"""This module contains the functions to process PDF files using Document AI."""
import re

from google.cloud import documentai

from src.io import delete_folder_from_bucket, logger, upload_pdf_to_bucket
from src.utils import cache_on_disk


async def _process_pdf_w_docai(image_content, client, processor_name):
    """Process the PDF using Document AI.

    Args:
        image_content (bytes): The content of the PDF file as bytes.
        client: The Document AI client.
        processor_name (str): The name of the processor to be used.
                            e.g.: projects/{project_id}/locations/{location}/processor/{processor_id}

    Returns:
        The processed document.
    """
    # Load binary data
    raw_document = documentai.RawDocument(
        content=image_content, mime_type="application/pdf"
    )

    # Configure the process request
    request = documentai.ProcessRequest(
        name=processor_name,
        raw_document=raw_document,  # field_mask=field_mask
    )
    result = await cache_on_disk(client.process_document, request=request)

    return result.document


async def _batch_process_pdf_w_docai(
    params, image_content, client, processor_name, timeout=1200
):
    """Process the PDF using Document AI Batch Process API.

    Args:
        image_content (bytes): The content of the PDF file as bytes.
        client: The Document AI client.
        processor_name (str): The name of the processor to be used.
                            e.g.: projects/{project_id}/locations/{location}/processor/{processor_id}
        timeout (int, optional): The timeout in seconds. Defaults to 1200.

    Returns:
        The processed document.
    """
    # Upload the PDF to GCS bucket
    gcs_input_uri, storage_client = upload_pdf_to_bucket(
        params, image_content, "temp.pdf"
    )

    gcs_document = documentai.GcsDocument(
        gcs_uri=gcs_input_uri, mime_type="application/pdf"
    )
    # Load GCS Input URI into a List of document files
    input_config = documentai.BatchDocumentsInputConfig(
        gcs_documents=documentai.GcsDocuments(documents=[gcs_document])
    )

    # Cloud Storage URI for the Output Directory
    # This must end with a trailing forward slash `/`
    destination_uri = f"gs://{params['doc_ai_bucket_batch_output']}/"  # noqa
    gcs_output_config = documentai.DocumentOutputConfig.GcsOutputConfig(
        gcs_uri=destination_uri, field_mask="entities"
    )

    # Where to write results
    output_config = documentai.DocumentOutputConfig(gcs_output_config=gcs_output_config)

    # The full resource name of the processor
    request = documentai.BatchProcessRequest(
        name=processor_name,
        input_documents=input_config,
        document_output_config=output_config,
    )

    # BatchProcess returns a Long Running Operation (LRO)
    logger.info("Processing document in batch mode...")
    operation = await client.batch_process_documents(request)

    try:
        # Wait for the operation to finish
        logger.info(f"Waiting for operation {operation.operation.name} to complete...")
        await operation.result(timeout=timeout)
    # Catch exception when operation doesn't finish before timeout
    except Exception as e:
        logger.error(e)

    # Once the operation is complete,
    # get output document information from operation metadata
    metadata = documentai.BatchProcessMetadata(operation.metadata)

    if metadata.state != documentai.BatchProcessMetadata.State.SUCCEEDED:
        raise ValueError(f"Batch Process Failed: {metadata.state}")

    # One process per Input Document
    for process in metadata.individual_process_statuses:
        # The Cloud Storage API requires the bucket name and URI prefix separately
        matches = re.match(r"gs://(.*?)/(.*)", process.output_gcs_destination)
        if not matches:
            logger.warning(
                "Could not parse output GCS destination:",
                process.output_gcs_destination,
            )
            continue

        output_bucket, output_prefix = matches.groups()

        # Get List of Document Objects from the Output Bucket
        output_blobs = storage_client.list_blobs(output_bucket, prefix=output_prefix)

        # Document AI may output multiple JSON files per source file
        # Selecting only the first output file as of now. No particular reason
        for blob in output_blobs:
            # Document AI should only output JSON files to GCS
            if ".json" not in blob.name:
                logger.warning(
                    f"Skipping non-supported file: {blob.name} - Mimetype: {blob.content_type}"
                )
                continue

            # Download JSON File as bytes object and convert to Document Object
            result_document = documentai.Document.from_json(
                blob.download_as_bytes(), ignore_unknown_fields=True
            )

            # Delete the temporary file and the output file from the bucket
            delete_folder_from_bucket(
                params, params["doc_ai_bucket_batch_input"], "temp.pdf"
            )
            delete_folder_from_bucket(params, output_bucket, output_prefix)
            logger.info("Batch Process Completed!")

            return result_document
