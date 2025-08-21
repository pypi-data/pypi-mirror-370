"""This module contains the postprocessing functions for the partner invoice."""
from concurrent.futures import ThreadPoolExecutor

from fuzzywuzzy import fuzz

from src.io import logger


def postprocessing_partner_invoice(partner_invoice):
    """Apply postprocessing to the partner invoice data."""
    # Flatten the invoice amount
    for amount in partner_invoice.get("invoiceAmount", {}):
        if isinstance(amount, list):
            amount = amount[0]
        if isinstance(amount, dict):
            partner_invoice.update(amount)
            break

    # Remove invoiceAmount - comes from DocAI
    if partner_invoice.get("invoiceAmount") is not None:
        partner_invoice.pop("invoiceAmount")

    # Remove containers - comes from DocAI
    # TODO: we can distribute containers to line items based on location proximity
    if partner_invoice.get("containers") is not None:
        partner_invoice.pop("containers")

    # Ensure only one item for optional multiple fields
    optional_multiple_list = [
        "dueDate",
        "eta",
        "etd",
        "fortoEntity",
        "hblNumber",
        "reverseChargeSentence",
    ]
    for k, v in partner_invoice.items():
        if (k in optional_multiple_list) and isinstance(v, list):
            partner_invoice[k] = v[0]

    # Update keys
    key_updates = {
        "pod": "portOfDischarge",
        "pol": "portOfLoading",
        "name": "lineItemDescription",
        "unit": "quantity",
    }

    def update_keys(d, key_updates):
        """
        Recursively updates keys in a dictionary according to a mapping provided in key_updates.

        d: The original dictionary
        key_updates: A dictionary mapping old key names to new key names

        return A new dictionary with updated key names
        """
        if isinstance(d, dict):
            return {
                key_updates.get(k, k): update_keys(v, key_updates) for k, v in d.items()
            }
        elif isinstance(d, list):
            return [update_keys(item, key_updates) for item in d]
        else:
            return d

    updated_data = update_keys(partner_invoice, key_updates)
    return updated_data


def post_process_bundeskasse(aggregated_data):
    """Post-process the Bundeskasse invoice data."""
    # Check if the Credit note number starts with ATS and classify it to Credit Note else Invoice
    invoice_type = (
        "bundeskasseCreditNote"
        if aggregated_data.get("creditNoteInvoiceNumber", {})
        .get("documentValue", "")
        .startswith("ATS")
        else "bundeskasseInvoice"
    )

    aggregated_data["documentType"] = {
        "documentValue": invoice_type,
        "formattedValue": invoice_type,
    }

    # Predefine mappings for tax codes
    tax_type_mappings = {
        "A0000": "Zölle (ohne EGKS-Zölle, Ausgleichs-, Antidumping- und Zusatzzölle, Zölle auf Agrarwaren) (ZOLLEU)",
        "B0000": "Einfuhrumsatzsteuer(EUSt)",
        "A3000": "Endgültige Antidumpingzölle(ANTIDUMPEU)",
    }

    line_items = aggregated_data.get("lineItem", [])
    is_recipient_forto = False  # Check if Forto account is in any line item

    # Process each line item
    for line_item in line_items:
        tax_type = line_item.get("taxType")
        if tax_type:
            # Map the tax type to the corresponding value
            line_item["name"]["formattedValue"] = tax_type_mappings.get(
                tax_type.get("documentValue"), line_item["name"]["documentValue"]
            )

        # Check if the deferredDutyPayer is forto
        deferredDutyPayer = line_item.get("deferredDutyPayer", {})
        lower = deferredDutyPayer.get("documentValue", "").lower()
        if any(key in lower for key in ["de789147263644738", "forto"]):
            is_recipient_forto = True

    update_recipient_and_vendor(aggregated_data, is_recipient_forto)


def update_recipient_and_vendor(aggregated_data, is_recipient_forto):
    """Update the recipient and vendor information in the aggregated data."""
    # Check if the "recipientName" and "recipientAddress" keys exist
    keys_to_init = ["recipientName", "recipientAddress", "vendorName", "vendorAddress"]
    for key in keys_to_init:
        aggregated_data.setdefault(key, {"formattedValue": "", "documentValue": ""})

    if is_recipient_forto:
        # Update the aggregated data with the recipient information
        aggregated_data["recipientName"][
            "formattedValue"
        ] = "Forto Logistics SE & Co KG"
        aggregated_data["recipientAddress"][
            "formattedValue"
        ] = "Schönhauser Allee 9, 10119 Berlin, Germany"

    # Update the vendor details always to Bundeskasse Trier
    aggregated_data["vendorName"]["formattedValue"] = "Bundeskasse Trier"
    aggregated_data["vendorAddress"][
        "formattedValue"
    ] = "Dasbachstraße 15, 54292 Trier, Germany"


def process_partner_invoice(params, aggregated_data, embed_manager, document_type_code):
    """Process the partner invoice data."""
    # Post process containerNumber.
    # TODO: Remove this block of code after migrating to LLM completely and update the placeholder in the prompt library
    if "containerNumber" in aggregated_data and isinstance(
        aggregated_data["containerNumber"], dict
    ):
        container_number = aggregated_data.get("containerNumber", {}).get(
            "formattedValue", None
        )
        if container_number:
            aggregated_data["containerNumber"] = (
                [
                    {
                        "documentValue": aggregated_data.get("containerNumber", {}).get(
                            "documentValue", ""
                        ),
                        "formattedValue": ctr_number,
                    }
                    for ctr_number in container_number
                ]
                if isinstance(container_number, list)
                else [
                    {
                        "documentValue": aggregated_data.get("containerNumber", {}).get(
                            "documentValue", ""
                        ),
                        "formattedValue": container_number,
                    }
                ]
            )

    if document_type_code == "bundeskasse":
        post_process_bundeskasse(aggregated_data)
        return

    line_items = aggregated_data.get("lineItem", [])
    # Add debug logging
    logger.info(f"Processing partnerInvoice with {len(line_items)} line items")

    reverse_charge = None
    reverse_charge_info = aggregated_data.get("reverseChargeSentence")

    # Check if reverseChargeSentence exists and has the expected structure
    if isinstance(reverse_charge_info, dict):
        # Get the reverse charge sentence and Check if the reverse charge sentence is present
        rev_charge_sentence = reverse_charge_info.get("formattedValue", "")
        reverse_charge_value = if_reverse_charge_sentence(rev_charge_sentence, params)

        # Assign the reverse charge value to the aggregated data
        reverse_charge_info["formattedValue"] = reverse_charge_value
        reverse_charge = aggregated_data.pop("reverseChargeSentence", None)

    # Process each line item
    for line_item in line_items:
        if line_item.get("lineItemDescription", None) is not None:
            line_item["itemCode"] = associate_forto_item_code(
                embed_manager,
                line_item["lineItemDescription"]["formattedValue"],
                params,
            )

        if reverse_charge:
            # Distribute reverseChargeSentence to all line items
            line_item["reverseChargeSentence"] = reverse_charge


def compute_score(args):
    """Compute the fuzzy matching score between a new line item and a key."""
    new_lineitem, key = args
    return key, fuzz.ratio(new_lineitem, key)


def get_fuzzy_match_score(target: str, sentences: list, threshold: int):
    """Get the best fuzzy match for a target string from a list of candidates.

    Args:
        target (str): The string to match.
        sentences (list): List of strings to match against.
        threshold (int): Minimum score threshold to consider a match.

    Returns:
        tuple: (best_match, score) if above threshold, else (None, 0)
    """
    # Use multiprocessing to find the best match
    with ThreadPoolExecutor() as executor:
        results = executor.map(compute_score, [(target, s) for s in sentences])

    # Find the best match and score
    best_match, best_score = max(results, key=lambda x: x[1], default=(None, 0))

    # return best_match, best_score
    # If the best match score is above a threshold (e.g., 80), return it
    if best_score >= threshold:
        return best_match, True

    return None, False


def if_reverse_charge_sentence(sentence: str, params):
    """Check if the reverse charge sentence is present in the line item."""
    reverse_charge_sentences = params["lookup_data"]["reverse_charge_sentences"]
    threshold = params["fuzzy_threshold_reverse_charge"]

    # Check if ("ARTICLE 144", "ART. 144") in the sentence
    if "ARTICLE 144" in sentence or "ART 144" in sentence:
        return False

    # Check if the sentence is similar to any of the reverse charge sentences
    _, is_reverse_charge = get_fuzzy_match_score(
        sentence, reverse_charge_sentences, threshold
    )

    return is_reverse_charge


def find_matching_lineitem(new_lineitem: str, kvp_dict: dict, threshold=90):
    """Find the best matching line item from the key-value pair dictionary using fuzzy matching.

    Args:
        new_lineitem (str): The new line item to be matched.
        kvp_dict (dict): The key-value pair dictionary with 'Processed Lineitem' as key and 'Forto SLI' as value.
        threshold (int): Minimum score threshold to consider a match.
    Returns:
        str: The best matching 'Forto SLI' value from the dictionary.
    """
    new_lineitem = new_lineitem.upper()

    # Check if the new line item is already in the dictionary
    if new_lineitem in kvp_dict:
        return kvp_dict[new_lineitem]

    # Get the best fuzzy match score for the extracted line item
    best_match, _ = get_fuzzy_match_score(
        new_lineitem, list(kvp_dict.keys()), threshold
    )

    return kvp_dict.get(best_match, None)


def associate_forto_item_code(embed_manager, input_string, params):
    """
    Finds a match for the input string using fuzzy matching first, then embedding fallback.

    1. Tries to find a fuzzy match for input_string against the keys in
       mapping_data using RapidFuzz, requiring a score >= fuzzy_threshold.
    2. If found, returns the corresponding value from mapping_data.
    3. If not found above threshold, calls the embedding_fallback function.

    Args:
        input_string: The string to find a match for.
        embed_manager: The embedding manager instance to use for fallback.
        params: Parameters containing the lookup data and fuzzy threshold.

    Returns:
        The matched value (from fuzzy match or embedding), or None if no match found.
    """
    # Get the Forto item code using fuzzy matching
    forto_item_code = find_matching_lineitem(
        new_lineitem=input_string,
        kvp_dict=params["lookup_data"]["item_code"],  # TODO: Parse the KVP dictionary
        threshold=params["fuzzy_threshold_item_code"],
    )

    if forto_item_code is None:
        # 2. Fallback to embedding function if no good fuzzy match
        embeddings_dict = embed_manager.embeddings_dict
        forto_item_code = embed_manager._find_most_similar_option(
            input_string, *embeddings_dict["item_codes_label"]
        )

    result = {"documentValue": input_string, "formattedValue": forto_item_code}
    return result
