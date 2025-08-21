"""This module contains the functions to extract data from an Excel file."""
# flake8: noqa: E402
import logging

logger = logging.getLogger(__name__)

import asyncio
import json

import numpy as np
import pandas as pd

from src.llm import prompt_excel_extraction
from src.utils import generate_schema_structure, get_excel_sheets


async def extract_data_from_sheet(params, sheet_name, sheet, response_schema):
    logger.info(f"Processing sheet: {sheet_name}")
    excel_content = pd.DataFrame(sheet.values)
    # Convert to Markdown format for the LLM model
    worksheet = (
        "This is from a excel. Pay attention to the cell position:\n"
        + excel_content.replace(np.nan, "").to_markdown(index=False, headers=[])
    )

    # Prompt for the LLM JSON
    prompt_docai = prompt_excel_extraction(worksheet)

    try:
        result = await params["LlmClient"].get_unified_json_genai(
            prompt_docai,
            response_schema=response_schema,
        )
    except Exception as e:
        result = {}
        logger.error(f"Error extracting data from LLM: {e}")

    return sheet_name, result


async def extract_data_from_excel(
    params,
    input_doc_type,
    file_content,
    schema_client,
    mime_type,
):
    """Extract data from the Excel file.

    Args:
        params (dict): Parameters for the data extraction process.
        input_doc_type (str): The type of the document.
        file_content (bytes): The content of the Excel file to process.
        schema_client (DocumentSchemaClient): Client for the Document AI schema.
        mime_type (str): The MIME type of the file.

    Returns:
        formatted_data (list): A list of dictionaries containing the extracted data.
        result (list): The extracted data from the document.
        model_id (str): The ID of the model used for extraction.

    """
    # Generate the response structure
    response_schema = generate_schema_structure(params, input_doc_type)

    # Load the Excel file and get ONLY the "visible" sheet names
    sheets, workbook = get_excel_sheets(file_content, mime_type)

    # Excel files may contain multiple sheets. Extract data from each sheet
    sheet_extract_tasks = [
        extract_data_from_sheet(
            params, sheet_name, workbook[sheet_name], response_schema
        )
        for sheet_name in sheets
    ]
    extracted_data = {k: v for k, v in await asyncio.gather(*sheet_extract_tasks)}

    stored_data = json.dumps(extracted_data)

    return extracted_data, stored_data, params["gemini_params"]["model_id"]
