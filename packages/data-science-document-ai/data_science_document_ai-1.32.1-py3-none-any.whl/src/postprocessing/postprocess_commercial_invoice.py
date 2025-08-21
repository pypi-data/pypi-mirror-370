"""This module contains the postprocessing functions for the commercial invoice."""
from src.postprocessing.common import extract_string


def postprocessing_commercial_invoice(result, params, input_doc_type):
    """Apply postprocessing to the commercial invoice data."""
    # Get the global currency of the document
    global_currency = result.get("currency") or (
        extract_string(result.get("total_amount"))
        if result.get("total_amount")
        else None
    )

    sku_list = result.get(params["key_to_combine"].get(input_doc_type, [None])[0], [])

    # Loops over each sku
    for sku in sku_list:
        if sku.get("amount"):  # If the sku has an extracted amount
            # If currency is None, extract the currency either from the "amount" field or assign the global currency
            sku["currency"] = (
                sku.get("currency") or extract_string(sku["amount"]) or global_currency
            )

    result[params["key_to_combine"][input_doc_type][0]] = sku_list

    return result
