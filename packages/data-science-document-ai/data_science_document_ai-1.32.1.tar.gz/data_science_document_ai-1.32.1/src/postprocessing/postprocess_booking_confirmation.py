"""Postprocessing of the result of Booking  Confirmation model to match the data schema."""

transport_leg_features = [
    "eta",
    "etd",
    "portOfLoading",
    "vesselName",
    "voyage",
    "imoNumber",
    "portOfDischarge",
]

same_label_groups = [
    ["bookingNumber", "pickUpReference", "gateInReference"],
]


def filter_transport_legs(booking_confirmation):
    """Delete pre- and on- carriage legs.

    For now, we consider legs without vesselName or voyage as non transport leg which are ignored by Ops.
    If leg is deleted by Ops, order of other legs is changed and accuracy is not measured correctly.

    Args:
        booking_confirmation: list of predicted entities.

    Returns:
        bookingConfirmation: updated predicted entities.
    """
    filtered_legs = []
    legs_amount = len(booking_confirmation["transportLegs"])
    if legs_amount > 1:
        for i in range(legs_amount):
            if (booking_confirmation["transportLegs"][i].get("vesselName")
                    or booking_confirmation["transportLegs"][i].get("voyage")):
                filtered_legs.append(booking_confirmation["transportLegs"][i])
        booking_confirmation["transportLegs"] = filtered_legs
    return booking_confirmation


def apply_naive_predictions(booking_confirmation):
    """There are some labels that usually have the same value.

    E. G. portOfLoading2 = portOfDischarge1 and usually bookingNumber = pickUpReference = gateInReference.
    Doc AI is not perfect when two or more labels are the same. This function applies these assumptions.

    Args:
        booking_confirmation: list of predicted entities.

    Returns:
        bookingConfirmation: updated predicted entities.
    """
    for same_label_group in same_label_groups:
        value = None
        for label in same_label_group:
            if label in booking_confirmation:
                value = booking_confirmation[label]
            elif value:
                booking_confirmation[label] = value

    legs = len(booking_confirmation["transportLegs"])
    for i in range(legs - 1):
        if "portOfDischarge" in booking_confirmation["transportLegs"][i]:
            if "portOfLoading" not in booking_confirmation["transportLegs"][i + 1]:
                booking_confirmation["transportLegs"][i + 1][
                    "portOfLoading"
                ] = booking_confirmation["transportLegs"][i]["portOfDischarge"]
        else:
            if "portOfLoading" in booking_confirmation["transportLegs"][i + 1]:
                booking_confirmation["transportLegs"][i][
                    "portOfDischarge"
                ] = booking_confirmation["transportLegs"][i + 1]["portOfLoading"]

    return booking_confirmation


def postprocess_booking_confirmation(booking_confirmation):
    """Postprocessing aggregates transport legs into list and assign ids.

    Model returns transport legs components as 'eta1', 'etd2', 'vesselName3'...
    They are copied into 'transportLegs'[id]"{'eta', 'etd', 'vesselName'...}
    Original labels are deleted.

    Args:
        booking_confirmation: aggregated_data with formatted values from processor response
    Returns:
        bookingConfirmation with "transportLegs" list and without original transport legs components
    """
    if "transportLegs" not in booking_confirmation:
        legs = []
        delete_keys = set()
        for entity_type in booking_confirmation.keys():

            # support for old bookingConfirmation schema
            if entity_type in transport_leg_features:
                index = 1
                while index > len(legs):
                    legs.append({})
                legs[index - 1][entity_type] = booking_confirmation[entity_type]
                delete_keys.add(entity_type)
            else:

                # e.g. "eta1" = type_without_index:"eta" + index: 1, we won't have legs > 10
                type_without_index = entity_type[:-1]
                if type_without_index in transport_leg_features:
                    index = int(entity_type[-1])

                    # it is possible to encounter leg3 value before leg1 or leg2
                    while index > len(legs):
                        legs.append({})
                    legs[index - 1][type_without_index] = booking_confirmation[
                        entity_type
                    ]
                    delete_keys.add(entity_type)
        for delete_key in delete_keys:
            del booking_confirmation[delete_key]

        # this function only called for BookingConfirmations, empty list is preferred to no value
        booking_confirmation["transportLegs"] = legs

    booking_confirmation = apply_naive_predictions(booking_confirmation)
    booking_confirmation = filter_transport_legs(booking_confirmation)
    return booking_confirmation
