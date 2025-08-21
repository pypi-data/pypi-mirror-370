"""Config constant params for data science project(s)."""

project_parameters = {
    # Project constants
    "project_name": "document-ai",
    "project_hash": "ceb0ac54",
    # Google related parameters
    "g_ai_project_name": "forto-data-science-production",
    "g_ai_project_id": "738250249861",
    "g_api_endpoint": "eu-documentai.googleapis.com",
    "g_location": "eu",
    "g_region": "europe-west1",
    # Google Cloud Storage
    "doc_ai_bucket_project_name": "forto-data-science-production",
    "doc_ai_bucket_name": "ds-document-capture",
    "doc_ai_bucket_batch_input": "ds-batch-process-docs",
    "doc_ai_bucket_batch_output": "ds-batch-process-output",
    # Paths
    "folder_data": "data",
    # Fuzzy lookup
    "g_model_fuzzy_lookup_folder": "fuzzy_lookup",
    "item_code_lookup": "line_item_kvp_table.json",
    "invoice_classification_lookup": "invoice_classification.json",
    "reverse_charge_sentence_lookup": "reverse_charge_sentences.json",
    # Fuzzy logic params
    "fuzzy_threshold_item_code": 70,
    "fuzzy_threshold_reverse_charge": 80,
    "fuzzy_threshold_invoice_classification": 70,
    # Big Query
    "g_ai_gbq_db_schema": "document_ai",
    "g_ai_gbq_db_table_out": "document_ai_api_calls_v1",
    "excluded_endpoints": ["/healthz", "/", "/metrics", "/healthz/"],
    # models metadata (confidence),
    "g_model_data_folder": "models",
    "local_model_data_folder": "data",
    "model_selector": {
        "stable": {
            "bookingConfirmation": 1,
            "packingList": 0,
            "commercialInvoice": 0,
            "finalMbL": 0,
            "draftMbl": 0,
            "arrivalNotice": 0,
            "shippingInstruction": 0,
            "customsAssessment": 0,
            "deliveryOrder": 0,
            "partnerInvoice": 0,
            "customsInvoice": 0,
            "bundeskasse": 0,
        },
        "beta": {
            "bookingConfirmation": 0,
        },
    },
    # this is the model selector for the model to be used from the model_config.yaml
    # file based on the environment, 0 mean the first model in the list
    # LLM model parameters
    "gemini_params": {
        "temperature": 0,
        "maxOutputTokens": 65536,
        "top_p": 0.8,
        "top_k": 40,
        "seed": 42,
        "model_id": "gemini-2.5-pro",
    },
    # Key to combine the LLM results with the Doc Ai results
    "key_to_combine": {
        "bookingConfirmation": ["transportLegs"],
        "finalMbL": ["containers"],
        "draftMbl": ["containers"],
        "customsAssessment": ["containers"],
        "packingList": ["skuData"],
        "commercialInvoice": ["skus"],
        "shippingInstruction": ["containers"],
        "partnerInvoice": ["lineItem"],
        "customsInvoice": ["lineItem"],
        "bundeskasse": ["lineItem"],
    },
}

# Hardcoded rules for data points formatting that can't be based on label name alone
formatting_rules = {
    "bookingConfirmation": {"pickUpTerminal": "depot", "gateInTerminal": "terminal"},
    "deliveryOrder": {"pickUpTerminal": "terminal", "EmptyContainerDepot": "depot"},
}
