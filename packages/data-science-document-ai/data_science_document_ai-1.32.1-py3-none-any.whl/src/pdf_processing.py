"""Building engine to understand and process PDF files."""
# flake8: noqa: E402

import logging
import os

logger = logging.getLogger(__name__)

import asyncio
from collections import defaultdict

from fastapi import HTTPException
from google.cloud.documentai_v1 import Document as docaiv1_document

from src.docai import _batch_process_pdf_w_docai, _process_pdf_w_docai
from src.excel_processing import extract_data_from_excel
from src.postprocessing.common import format_all_entities, remove_none_values
from src.postprocessing.postprocess_booking_confirmation import (
    postprocess_booking_confirmation,
)
from src.postprocessing.postprocess_commercial_invoice import (
    postprocessing_commercial_invoice,
)
from src.postprocessing.postprocess_partner_invoice import (
    postprocessing_partner_invoice,
)
from src.prompts.prompt_library import prompt_library
from src.utils import (
    extract_top_pages,
    generate_schema_structure,
    get_processor_name,
    run_background_tasks,
    validate_based_on_schema,
)


async def process_file_w_docai(params, image_content, client, processor_name):
    """
    Process a file using Document AI.

    Args:
        params (dict): The project parameters.
        image_content (bytes): The file to be processed. It can be bytes object.
        client: The Document AI client.
        processor_name (str): The name of the processor to be used.

    Returns:
        The processed document.

    Raises:
        ValueError: If the file is neither a path nor a bytes object.
    """
    result = None

    try:
        logger.info("Processing document...")
        result = await _process_pdf_w_docai(image_content, client, processor_name)
    except Exception as e:
        if e.reason == "PAGE_LIMIT_EXCEEDED":
            logger.warning(
                "Document contains more than 15 pages! Processing in batch method..."
            )
            # Process the document in batch method (offline processing)
            try:
                result = await _batch_process_pdf_w_docai(
                    params, image_content, client, processor_name
                )
            except Exception as batch_e:
                logger.error(f"Error processing document {batch_e}.")

        else:
            logger.error(f"Error processing document {e}.")

    return result


async def extract_data_from_pdf_w_docai(
    params,
    input_doc_type,
    file_content,
    processor_client,
    isBetaTest,
):
    """Extract data from the PDF file."""
    version = "stable" if not isBetaTest else "beta"
    processor_name = get_processor_name(params, input_doc_type, version)

    if not processor_name:
        supported_doc_types = list(params["data_extractor_processor_names"].keys())
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported document type {input_doc_type}. Supported document types are: {supported_doc_types}",  # noqa: E501
        )

    result = await process_file_w_docai(
        params, file_content, processor_client, processor_name
    )

    # Create an entity object to store the result in gcs
    result_for_store = docaiv1_document.to_json(result)

    aggregated_data = defaultdict(list)

    # Extract entities from the result
    for entity in result.entities:
        value = (
            {child.type_: child.mention_text for child in entity.properties}
            if entity.properties
            else entity.mention_text
        )
        aggregated_data[entity.type_].append(value)

    # Select only 1 entity for Occurrence_Type= "once"
    aggregated_data = await validate_based_on_schema(
        params, aggregated_data, processor_name
    )

    # Call postprocessing for Multi Leg
    if (
        input_doc_type == "bookingConfirmation"
        or input_doc_type == "bookingConfirmation_test"
    ):
        aggregated_data = postprocess_booking_confirmation(aggregated_data)
        logger.info("Transport Legs assembled successfully")
    elif input_doc_type in ["partnerInvoice", "customsInvoice"]:
        aggregated_data = postprocessing_partner_invoice(aggregated_data)
        logger.info("Partner Invoice naming changed successfully")

    response = await processor_client.get_processor(name=processor_name)
    processor_version = response.default_processor_version.split("/")[-1]

    logger.info("Data Extraction completed successfully")
    logger.info(
        f"Processor & it's version used for current request: {response.display_name} - {processor_version}"
    )

    return aggregated_data, result_for_store, processor_version


async def identify_carrier(document, llm_client, prompt, response_schema):
    """Identify the carrier from the Booking Confirmation document."""

    result = await llm_client.ask_gemini(
        prompt=prompt,
        document=document,
        response_schema=response_schema,
        response_mime_type="text/x.enum",
    )

    if result:
        result = result.strip().lower()
    else:
        result = "other"
    return result


async def process_file_w_llm(params, file_content, input_doc_type, llm_client):
    """Process a document using a language model (gemini) to extract structured data.

    Args:
        params (dict): The project parameters.
        file_content (str): The content of the file to be processed.
        input_doc_type (str): The type of document, used to select the appropriate prompt from the prompt library.
        llm_client: The LLM client object.

    Returns:
        result (dict): The structured data extracted from the document, formatted as JSON.
    """
    # Bundeskasse invoices contains all the required information in the first 3 pages.
    file_content = (
        extract_top_pages(file_content, num_pages=5)
        if input_doc_type == "bundeskasse"
        else file_content
    )

    # convert file_content to required document
    document = llm_client.prepare_document_for_gemini(file_content)

    # get the schema placeholder from the Doc AI and generate the response structure
    response_schema = (
        prompt_library.library[input_doc_type]["other"]["placeholders"]
        if input_doc_type in ["partnerInvoice", "customsInvoice", "bundeskasse"]
        else generate_schema_structure(params, input_doc_type)
    )

    carrier = "other"
    if (
        "preprocessing" in prompt_library.library.keys()
        and "carrier" in prompt_library.library["preprocessing"].keys()
        and input_doc_type
        in prompt_library.library["preprocessing"]["carrier"]["placeholders"].keys()
    ):
        carrier_schema = prompt_library.library["preprocessing"]["carrier"][
            "placeholders"
        ][input_doc_type]

        carrier_prompt = prompt_library.library["preprocessing"]["carrier"]["prompt"]
        carrier_prompt = carrier_prompt.replace(
            "DOCUMENT_TYPE_PLACEHOLDER", input_doc_type
        )

        # identify carrier for customized prompting
        carrier = await identify_carrier(
            document, llm_client, carrier_prompt, carrier_schema
        )

    if input_doc_type == "bookingConfirmation":
        response_schema = prompt_library.library[input_doc_type][carrier][
            "placeholders"
        ]

    if (
        input_doc_type in prompt_library.library.keys()
        and carrier in prompt_library.library[input_doc_type].keys()
    ):
        # get the related prompt from predefined prompt library
        prompt = prompt_library.library[input_doc_type][carrier]["prompt"]

        # generate the result with LLM (gemini)
        result = await llm_client.get_unified_json_genai(
            prompt=prompt, document=document, response_schema=response_schema
        )
        return result
    return {}


async def extract_data_from_pdf_w_llm(params, input_doc_type, file_content, llm_client):
    """Extract data from the PDF file."""
    # Process the document using LLM
    result = await process_file_w_llm(params, file_content, input_doc_type, llm_client)

    # Add currency from the amount field
    if input_doc_type in ["commercialInvoice"]:
        result = postprocessing_commercial_invoice(result, params, input_doc_type)
    elif input_doc_type == "bookingConfirmation":
        result = postprocess_booking_confirmation(result)
    return result, llm_client.model_id


def combine_llm_results_w_doc_ai(
    doc_ai, llm, keys_to_combine: list = None, input_doc_type=None
):
    """
    Combine results from DocAI and LLM extractions.

    Args:
        doc_ai: result from DocAI
        llm: result from LLM
        keys_to_combine (list): specific keys to apply list merging logic (e.g., 'transportLegs' or 'containers')
        input_doc_type: document type

    Returns:
        combined result
    """
    result = doc_ai.copy()
    llm = remove_none_values(llm)
    if not llm:
        return result

    # Merge top-level keys
    result.update({k: v for k, v in llm.items() if k not in result})

    if (
        input_doc_type
        and input_doc_type in ["packingList", "commercialInvoice"]
        and keys_to_combine
    ):
        result.update(
            {key: llm.get(key) for key in keys_to_combine if key in llm.keys()}
        )
        return result

    # Handle specific key-based merging logic for multiple keys
    if keys_to_combine:
        for key in keys_to_combine:
            if key in llm.keys():
                # Merge the list of dictionaries
                # If the length of the LLM list is less than the Doc AI result, replace with the LLM list
                if len(llm[key]) < len(result[key]):
                    result[key] = llm[key]
                else:
                    # If the length of the LLM list is greater than or equal to the Doc AI result,
                    # add & merge the dictionaries
                    if isinstance(llm[key], list):
                        for i in range(len(llm[key])):
                            if i == len(result[key]):
                                result[key].append(llm[key][i])
                            else:
                                for sub_key in llm[key][i].keys():
                                    result[key][i][sub_key] = llm[key][i][sub_key]
    return result


async def extract_data_by_doctype(
    params,
    file_content,
    input_doc_type,
    processor_client,
    if_use_docai,
    if_use_llm,
    isBetaTest=False,
):
    # Select LLM client
    llm_client = params["LlmClient"]

    async def extract_w_docai():
        return await extract_data_from_pdf_w_docai(
            params=params,
            input_doc_type=input_doc_type,
            file_content=file_content,
            processor_client=processor_client,
            isBetaTest=isBetaTest,
        )

    async def extract_w_llm():
        return await extract_data_from_pdf_w_llm(
            params=params,
            input_doc_type=input_doc_type,
            file_content=file_content,
            llm_client=llm_client,
        )

    if if_use_docai and if_use_llm:
        results = await asyncio.gather(extract_w_docai(), extract_w_llm())
        (extracted_data_doc_ai, store_data, processor_version_doc_ai) = results[0]
        (extracted_data_llm, processor_version_llm) = results[1]

        # Combine the results from DocAI and LLM extractions
        logger.info("Combining the results from DocAI and LLM extractions...")
        extracted_data = combine_llm_results_w_doc_ai(
            extracted_data_doc_ai,
            extracted_data_llm,
            params["key_to_combine"][input_doc_type],
            input_doc_type,
        )
        processor_version = f"{processor_version_doc_ai}/{processor_version_llm}"
    elif if_use_docai:
        (extracted_data, store_data, processor_version) = await extract_w_docai()
    elif if_use_llm:
        (extracted_data, processor_version) = await extract_w_llm()
        store_data = extracted_data
    else:
        raise ValueError("Either if_use_docai or if_use_llm must be True.")
    return extracted_data, store_data, processor_version


async def data_extraction_manual_flow(
    params,
    file_content,
    mime_type,
    meta,
    processor_client,
    schema_client,
    embed_manager,
):
    """
    Process a PDF file and extract data from it.

    Args:
        params (dict): Parameters for the data extraction process.
        file_content (bytes): The content of the PDF file to process.
        mime_type (str): The MIME type of the document.
        meta (DocumentMeta): Metadata associated with the document.
        processor_client (DocumentProcessorClient): Client for the Document AI processor.
        schema_client (DocumentSchemaClient): Client for the Document AI schema.
        embed_manager (EmbeddingsManager): Manager for embeddings.

    Returns:
        dict: A dictionary containing the processed document information.

    Raises:
        Refer to reasons in 400 error response examples.
    """
    # Validate the file type
    if mime_type == "application/pdf":
        # bundeskasse is processed with LLM only
        if_use_docai = False if meta.documentTypeCode == "bundeskasse" else True
        if_use_llm = (
            True if meta.documentTypeCode in params["key_to_combine"].keys() else False
        )

        (
            extracted_data,
            store_data,
            processor_version,
        ) = await extract_data_by_doctype(
            params,
            file_content,
            meta.documentTypeCode,
            processor_client,
            if_use_docai=if_use_docai,
            if_use_llm=if_use_llm,
            isBetaTest=False,
        )

    elif "excel" in mime_type or "spreadsheet" in mime_type:
        # Extract data from the Excel file
        extracted_data, store_data, processor_version = await extract_data_from_excel(
            params=params,
            input_doc_type=meta.documentTypeCode,
            file_content=file_content,
            schema_client=schema_client,
            mime_type=mime_type,
        )

    else:
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Please upload a PDF or Excel file.",
        )
    # Create the result dictionary with the extracted data
    extracted_data = await format_all_entities(
        extracted_data, embed_manager, meta.documentTypeCode, params
    )
    result = {
        "id": meta.id,
        "documentTypeCode": meta.documentTypeCode,
        "data": extracted_data,
        "processor_version": processor_version,
    }

    # Schedule background tasks without using FastAPI's BackgroundTasks
    if os.getenv("CLUSTER") != "ode":  # skip data export to bigquery in ODE environment
        asyncio.create_task(
            run_background_tasks(
                params,
                meta.id,
                meta.documentTypeCode,
                extracted_data,
                store_data,
                processor_version,
                mime_type,
            )
        )
    return result
