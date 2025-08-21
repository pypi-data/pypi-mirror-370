"""Interact with TMS."""
# flake8: noqa: E402

import logging

logger = logging.getLogger(__name__)

import os
from time import sleep

import requests


def set_tms_service_token():
    """Get bearer token from data-science service. Use for deployment batch-process."""
    data = {
        "grant_type": "client_credentials",
        "client_id": "data-science",
        "client_secret": os.environ["TMS_AUTH_CLIENT_SECRET"],
    }
    headers = {"contentType": "application/x-www-form-urlencoded"}
    url = f"https://auth.forto.{os.environ['TMS_DOMAIN']}/auth/realms/forto-eu/protocol/openid-connect/token"  # NOQA
    auth_response = requests.post(url, headers=headers, data=data)
    bearer_token = auth_response.json()
    os.environ["TMS_TOKEN"] = bearer_token["access_token"]
    return bearer_token


def get_tms_headers():
    """
    Return headers with TMS token for API requests.

    Returns:
    headers (dict): A dictionary containing the authorization header with the TMS token.
    """
    headers = {
        "authorization": f'Bearer {os.environ["TMS_TOKEN"]}',
    }
    return headers


def call_tms(request_function, *args, **kwargs):
    """
    Call the TMS API with the provided function and arguments.

    Args:
    request_function (function): The function to call.
    *args: Positional arguments to pass to the function.
    **kwargs: Keyword arguments to pass to the function.
    Returns:
    response (requests.Response): The response from the API call.
    """
    headers = get_tms_headers()
    sleep(0.02)
    logger.info(
        f"Calling TMS with {request_function.__name__.upper()} request: {args}{kwargs}"
    )
    response = request_function(*args, headers=headers, **kwargs)
    return response
