"""Utility functions for data science projects."""
import asyncio
import hashlib
import io  # type: ignore
import json
import os
import pickle
from datetime import datetime
from typing import Literal

import openpyxl
import pandas as pd
from google.cloud import documentai_v1beta3 as docu_ai_beta
from PyPDF2 import PdfReader, PdfWriter

from src.io import get_bq_client, get_storage_client, logger


def bq_logs(data_to_insert, params):
    """Insert logs into Google BigQuery.

    Args:
        data_to_insert (list): The data to insert into BigQuery.
        params (dict): The parameters dictionary.
    """
    # Get the BigQuery client
    bq_client, config = get_bq_client(params)
    # Get the table string
    table_string = f"{params['g_ai_project_name']}.{params['g_ai_gbq_db_schema']}.{params['g_ai_gbq_db_table_out']}"

    logger.info(f"Log table: {table_string}")
    # Insert the rows into the table
    insert_logs = bq_client.insert_rows_json(table_string, data_to_insert)

    # Check if there were any errors inserting the rows
    if not insert_logs:
        logger.info("New rows have been added.")
    else:
        logger.info("Errors occurred while inserting rows: ", insert_logs)


async def get_data_set_schema_from_docai(
    schema_client, project_id=None, location=None, processor_id=None, name=None
):
    """Get the existing processor schema.

    Args:
        schema_client (documentai_v1beta3.DocumentServiceClient): The schema client.
        project_id (str): The ID of the project.
        location (str): The location of the project.
        processor_id (str): The id of the processor.
        name (str, optional): The name of the dataset schema. Defaults to None.
        The format is "projects/{project_id}/locations/{location}/processors/{processor_id}/dataset/datasetSchema".

    Returns:
        documentai.DatasetSchema: The schema of the dataset.
    """
    # Check if the name is provided as per the format
    if name and not name.endswith("datasetSchema"):
        name = f"{name}/dataset/datasetSchema"

    # Initialize request argument(s)
    if name:
        request = docu_ai_beta.GetDatasetSchemaRequest(
            name=name, visible_fields_only=True
        )
    else:
        request = docu_ai_beta.GetDatasetSchemaRequest(
            name=schema_client.dataset_schema_path(project_id, location, processor_id),
            visible_fields_only=True,
        )

    # Make the request
    response = await schema_client.get_dataset_schema(request=request)

    return response.document_schema


def get_processor_name(
    params, input_doc_type, version: Literal["stable", "beta"] = "stable"
):
    """Access models based on the environment and isBetaTest."""
    g_ai_project_id = params["models_project_id"]

    doctype_models_list = params["model_config"][version][input_doc_type]
    selected_model_idx = params["model_selector"][version][input_doc_type]
    processor_id = doctype_models_list[selected_model_idx]["id"]

    processor_name = (
        f"projects/{g_ai_project_id}/locations/eu/processors/{processor_id}"
    )
    logger.info(f"Processor: {processor_name}")

    logger.info(f"Processor ID for {input_doc_type}: {processor_id}")

    return processor_name


async def validate_based_on_schema(params, extracted_raw_data, processor_name):
    """Validate the extracted data based on the schema."""
    # Get the schema of a processor and select only the entity types
    schema_response = get_data_set_schema(params, processor_name)
    # schema_response.document_schema.entity_types contains 2 elements:
    # One for entities at document level
    # One for entities at line item level
    schemas = schema_response.entity_types
    schema_header_fields = schemas[0].properties

    result = dict(extracted_raw_data)
    for data_field in schema_header_fields:
        if "once" in data_field.occurrence_type.name.lower():
            if data_field.name in result:
                result[data_field.name] = result[data_field.name][0]

    # Exclude the fields that are not in the schema.This is to avoid submitting additional fields from General AI to PAW
    result = {
        key: value
        for key, value in result.items()
        if key in [_entity.name for _entity in schema_header_fields]
    }

    return result


def store_json_in_gcs(
    params, document_id, json_data, folder_path="docai_entity_storage/"
):
    """Store a JSON object in a Google Cloud Storage bucket.

    Args:
        params (dict): The parameters dictionary.
        document_id (str): The document ID.
        json_data (dict): The JSON data to be stored.
        folder_path (str): The folder path in the GCS bucket. Default is "docai_entity_storage/".
    """
    try:
        storage_client = get_storage_client(params)
        bucket = storage_client.bucket(params.get("doc_ai_bucket_name"))
        full_object_name = folder_path + document_id
        blob = bucket.blob(full_object_name)
        blob.upload_from_string(json_data, content_type="application/json")

        logger.info(
            f"JSON object stored successfully in gs://{params.get('doc_ai_bucket_name')}/{full_object_name}"  # noqa
        )

    except Exception as e:
        logger.error(f"Error storing JSON object in GCS: {e}")


# Execute synchronous functions in the background
async def run_background_tasks(
    params,
    doc_id,
    docType,
    extracted_data,
    store_data,
    processor_version,
    mime_type,
):
    """
    Run background tasks asynchronously.

    Args:
        params (dict): The parameters dictionary.
        doc_id (str): The document ID.
        docType (str): The document type code.
        extracted_data (dict): The extracted data from the document.
        store_data: The data to store in GCS.
        processor_version: The processor version used to extract the data.
        mime_type: The MIME type of the document.

    Returns:
        None
    """
    loop = asyncio.get_running_loop()

    await loop.run_in_executor(None, store_json_in_gcs, params, doc_id, store_data)

    # Keep the page count as 1 for Excel files.
    page_count = 1
    # calculate the number of pages processed for PDFs
    try:
        if mime_type == "application/pdf":
            page_count = len(json.loads(store_data.encode("utf-8"))["pages"])
    except AttributeError:
        page_count = 0

    # Log the request in BigQuery
    await loop.run_in_executor(
        None,
        bq_logs,
        [
            {
                "session_id": params["session_id"],
                "upload_date": datetime.utcnow().isoformat(),
                "doc_id": doc_id,
                "documentTypeCode": docType,
                "status": "processed",
                "response": json.dumps(extracted_data),
                "processor_version": processor_version,
                "page_count": page_count,
                "mime_type": mime_type,
            }
        ],
        params,
    )


def get_excel_sheets(file_content, mime_type):
    """Get the sheet names from the Excel file.

    Args:
        file_content (bytes): The content of the Excel file.
        mime_type (str): The MIME type of the file.

    Returns:
        sheets (list): The list of sheet names.
        openpyxl.Workbook: The workbook
    """
    file_stream = io.BytesIO(file_content)
    if "spreadsheet" in mime_type:
        workbook = openpyxl.load_workbook(file_stream, data_only=True)
        sheets = [
            sheet_name
            for sheet_name in workbook.sheetnames
            if workbook[sheet_name].sheet_state == "visible"
        ]
    else:
        workbook = pd.read_excel(file_stream, sheet_name=None)
        # Select only the sheets that are not empty
        sheets = [sheet for sheet in workbook.keys() if not workbook[sheet].empty]

    return sheets, workbook


def generate_schema_structure(params, input_doc_type):
    """
    Generate the schema placeholder and the JSON response structure.

    Args:
        params (dict): Parameters dictionary.
        input_doc_type (str): Document type to select the appropriate schema.

    Returns:
        dict: The response schema structure.
    """
    # Get the processor name and the Doc Ai schema of the processor
    processor_name = get_processor_name(params, input_doc_type)
    schema = get_data_set_schema(params, processor_name)

    def build_schema(entity):
        return {
            "type": "OBJECT",
            "properties": {
                prop.name: {
                    "type": "string",
                    "nullable": True,
                    "description": prop.description,
                }
                for prop in entity.properties
            },
            "required": [
                prop.name
                for prop in entity.properties
                if "REQUIRED" in prop.occurrence_type.name
            ],
        }

    # Build the response schema structure for the header fields
    response_schema = build_schema(
        next(
            e
            for e in schema.entity_types
            if e.name == "custom_extraction_document_type"
        )
    )

    # Build the child schemas
    child_schemas = {
        entity.name: {"type": "ARRAY", "items": build_schema(entity)}
        for entity in schema.entity_types
        if entity.name != "custom_extraction_document_type"
    }

    # Attach child schemas to the parent schema
    response_schema["properties"].update(child_schemas)

    # TODO: expand or remove this workaround after testing
    if input_doc_type in ["finalMbL", "draftMbl"]:
        response_schema["properties"]["plug"] = {
            "description": "",
            "nullable": True,
            "type": "string",
        }

    return response_schema


def get_hash_of_data(data):
    """Generate a hash for data."""
    sha256_hash = hashlib.sha256()
    if data:
        if isinstance(data, bytes):
            sha256_hash.update(data)
        else:
            sha256_hash.update(str(data).encode("utf-8"))
        return sha256_hash.hexdigest()
    return None


async def cache_on_disk(func, **kwargs):
    """Cache function result if the arguments are the same. Enableable via environment variable CACHE."""
    if os.getenv("CACHE") != "enabled":
        return await func(**kwargs)
    os.makedirs("cache", exist_ok=True)
    func_name = func.__name__
    serialized_kwargs = {k: get_hash_of_data(v) for k, v in kwargs.items()}
    serialized_kwargs_str = json.dumps(serialized_kwargs, sort_keys=True)
    unique_key = get_hash_of_data(serialized_kwargs_str)
    cache_file = os.path.join("cache", f"{func_name}_{unique_key}.pkl")

    # Try retrieving cached result
    if os.path.exists(cache_file):
        with open(cache_file, "rb") as f:
            cached_data = f.read()
            return pickle.loads(cached_data)

    # Execute the function and cache the result
    result = await func(**kwargs)
    with open(cache_file, "wb") as f:
        f.write(pickle.dumps(result))
    return result


async def update_response_schema_from_docai(params, schema_client):
    params["docai_schema_dict"] = params.get("docai_schema_dict", {})
    for version in params["model_config"]:
        for input_doc_type in params["model_config"][version]:
            processor_name = get_processor_name(params, input_doc_type, version)
            # Get schema
            schema = await get_data_set_schema_from_docai(
                schema_client, name=processor_name
            )
            params["docai_schema_dict"].update({processor_name: schema})


def get_data_set_schema(params, processor_name):
    return params["docai_schema_dict"][processor_name]


def extract_top_pages(pdf_bytes, num_pages=4):
    """Extract the top pages from a PDF document."""
    reader = PdfReader(io.BytesIO(pdf_bytes))
    writer = PdfWriter()

    for page_num in range(min(num_pages, len(reader.pages))):
        writer.add_page(reader.pages[page_num])

    output = io.BytesIO()
    writer.write(output)

    return output.getvalue()
