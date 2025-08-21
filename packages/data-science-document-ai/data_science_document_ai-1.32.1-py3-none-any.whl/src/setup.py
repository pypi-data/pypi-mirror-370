"""Contains project setup parameters and initialization functions."""
import argparse
import json

# import streamlit as st
import os
import random
import time
from pathlib import Path

import toml
import vertexai
import yaml
from google.api_core.client_options import ClientOptions
from google.cloud import documentai
from google.cloud import documentai_v1beta3 as docai_beta

from src.constants import project_parameters
from src.constants_sandbox import project_parameters_sandbox

# Parent repos are imported without .
from src.io import download_dir_from_bucket, get_storage_client, logger
from src.llm import LlmClient


def ulid(hash_project):
    """Create unique identifier every time it runs, with respect to the hash_project."""
    hash_time = f"{int(time.time() * 1e3): 012x}"  # noqa: E203
    hash_rand = f"{random.getrandbits(48): 012x}"  # noqa: E203
    hash_all = hash_time + hash_project + hash_rand
    return f"{hash_all[:8]}-{hash_all[8:12]}-{hash_all[12:16]}-{hash_all[16:20]}-{hash_all[20:32]}"


def get_docai_processor_client(params, async_=True):
    """
    Return a DocumentAI client and processor name.

    Args:
        api_endpoint (str, optional): The API endpoint to use. Defaults to None.
        client_processor_path_kwargs: Keyword arguments to pass to documentai.DocumentProcessorServiceClient.processor_path method  # noqa: E501

    Returns:
        tuple: A tuple containing a DocumentAI client and processor name.
    """
    opts = ClientOptions(api_endpoint=params.get("g_api_endpoint"))
    if async_:
        client = documentai.DocumentProcessorServiceAsyncClient(client_options=opts)
    else:
        client = documentai.DocumentProcessorServiceClient(client_options=opts)
    return client


def get_docai_schema_client(params, async_=True):
    """
    Return a DocumentAI client and processor name.

    Args:
        api_endpoint (str, optional): The API endpoint to use. Defaults to None.
        client_processor_path_kwargs: Keyword arguments to pass to documentai.DocumentProcessorServiceClient.processor_path method  # noqa: E501

    Returns:
        tuple: A tuple containing a DocumentAI client and processor name.
    """
    opts = ClientOptions(api_endpoint=params.get("g_api_endpoint"))
    if async_:
        client = docai_beta.DocumentServiceAsyncClient(client_options=opts)
    else:
        client = docai_beta.DocumentServiceClient(client_options=opts)
    return client


def parse_input():
    """Manage input parameters."""
    parser = argparse.ArgumentParser(description="", add_help=False)
    parser.add_argument(
        "--scope",
        type=str,
        dest="scope",
        required=False,
        help="Whether the function should 'upload' or 'download' documents",
    )
    parser.add_argument(
        "--document_name",
        type=str,
        dest="document_name",
        required=False,
        help="Category of the document (e.g., 'commercialInvoice', 'packingList')",
    )
    parser.add_argument(
        "--for_combinations",
        type=bool,
        default=False,
        dest="for_combinations",
        required=False,
        help="A flag to download documents into a special subfolder",
    )
    parser.add_argument(
        "--n_samples",
        type=int,
        default=50,
        dest="n_samples",
        required=False,
        help="A number of samples to download",
    )

    # Remove declared missing arguments (e.g. model_type)
    args = vars(parser.parse_args())
    args_no_null = {
        k: v.split(",") if isinstance(v, str) else v
        for k, v in args.items()
        if v is not None
    }
    return args_no_null


def setup_params(args=None):
    """
    Set up the application parameters.

    Args:
        args: Command-line arguments.

    Returns:
        params: Dictionary containing application parameters.
    """
    if args is None:
        args = {}

    # Get program call arguments
    params = args.copy()

    # Update parameters with constants
    params.update(project_parameters)

    cluster = os.getenv("CLUSTER", "").lower()
    # Update the parameters with the sandbox parameters if the cluster is not production and not ODE
    if cluster not in ("production", "ode"):
        params.update(project_parameters_sandbox)

    # Set up the bucket constants for ODE environment
    if cluster == "ode":
        ode_env_vars = {
            "doc_ai_bucket_project_name": "PROJECT_ID",
            "doc_ai_bucket_name": "BUCKET_NAME",
            "doc_ai_bucket_batch_input": "INPUT_BUCKET_NAME",
            "doc_ai_bucket_batch_output": "OUTPUT_BUCKET_NAME",
        }
        params.update(
            {key: os.getenv(env_var) for key, env_var in ode_env_vars.items()}
        )

    # print cluster info
    logger.info(f"Cluster: {os.getenv('CLUSTER')}")

    params["version"] = toml.load("pyproject.toml")["tool"]["poetry"]["version"]

    params["session_id"] = ulid(params["project_hash"])
    logger.info(f"Session id is: {params['session_id']}")
    logger.info(f"Caching is {os.getenv('CACHE', 'disabled')}")

    # Directories and paths
    os.makedirs(params["folder_data"], exist_ok=True)

    params = setup_docai_client_and_path(params)

    # Set up Vertex AI for text embeddings
    setup_vertexai(params)

    # Load models from YAML file
    current_dir = os.path.dirname(__file__)
    file_path = os.path.join(current_dir, "docai_processor_config.yaml")
    with open(file_path) as file:
        yaml_content = yaml.safe_load(file)
        assert params.keys() & yaml_content.keys() == set()
        params.update(yaml_content)

    # Get models meta data from cloud
    client = get_storage_client(params)
    bucket = client.bucket(params["doc_ai_bucket_name"])
    downloaded_meta = download_dir_from_bucket(
        bucket, params["g_model_data_folder"], Path(params["local_model_data_folder"])
    )
    if not downloaded_meta:
        logger.info(f"Could not load models metadata from cloud.")

    params["LlmClient"] = LlmClient(
        openai_key=os.getenv("OPENAI_KEY"), parameters=params["gemini_params"]
    )

    params["lookup_data"] = setup_lookup_data(params, bucket)

    return params


def setup_docai_client_and_path(params):
    """Set up the Document AI client and path for processing documents."""
    processor_client = get_docai_processor_client(params, async_=False)

    # Set up document ai processor names by listing all processors by prefix
    parent_path = processor_client.common_location_path(
        project=params["g_ai_project_id"], location=params["g_location"]
    )
    processor_list = processor_client.list_processors(parent=parent_path)

    # Set up the processor names
    params["data_extractor_processor_names"] = {
        processor.display_name.removeprefix("doc_cap_"): processor.name
        for processor in processor_list
        if processor.display_name.startswith("doc_cap_")
    }

    return params


def setup_vertexai(params):
    """Initialize the Vertex AI with the specified project and location."""
    vertexai.init(
        project=params["g_ai_project_name"],
        location=params["g_region"],
    )


def setup_lookup_data(params, bucket):
    """
    Loads JSON mapping data from given GCP Bucket.
    """
    data = dict()

    input_path_item_code = (
        f'{params["g_model_fuzzy_lookup_folder"]}/{params["item_code_lookup"]}'
    )
    input_path_invoice_classification = f'{params["g_model_fuzzy_lookup_folder"]}/{params["invoice_classification_lookup"]}'  # noqa: E501
    input_path_reverse_charge = f'{params["g_model_fuzzy_lookup_folder"]}/{params["reverse_charge_sentence_lookup"]}'

    def download_json_from_bucket(path):
        """Download JSON data from a specified path in a GCP bucket."""
        blob = bucket.blob(path)
        downloaded_data = blob.download_as_text(encoding="utf-8")
        return json.loads(downloaded_data)

    data["item_code"] = download_json_from_bucket(input_path_item_code)
    data["invoice_classification"] = download_json_from_bucket(
        input_path_invoice_classification
    )
    data["reverse_charge_sentences"] = download_json_from_bucket(
        input_path_reverse_charge
    )

    return data
