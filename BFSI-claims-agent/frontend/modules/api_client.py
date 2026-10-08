import json
import os
import re

import requests
import streamlit as st

API_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:8000")


class ApiError(Exception):
    """
    Raised for any non-2xx response. 
    """
    def __init__(self, status_code, detail):
        self.status_code = status_code
        self.detail = detail
        super().__init__(f"{status_code}: {detail}")


def _auth_headers():
    """Bearer header from the token in session state, or no auth header at all if not logged in."""
    headers = {}
    token = st.session_state.get("access_token")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def _format_validation_error(error):
    """
    Turn one Pydantic validation error dict into a plain sentence.
    """
    location = [str(part) for part in error.get("loc", []) if part != "body"]
    field_name = location[-1] if location else "Input"
    label = re.sub(r"\bid\b", "ID", field_name.replace("_", " ").capitalize())

    error_type = error.get("type", "")
    message = error.get("msg", "is invalid")
    context = error.get("ctx") or {}

    if error_type == "missing":
        formatted = f"{label} is required."
    elif error_type == "string_too_short":
        min_length = context.get("min_length", 1)
        if min_length <= 1:
            formatted = f"{label} is required."
        else:
            formatted = f"{label} must be at least {min_length} characters."
    elif message.startswith("Value error, "):
        formatted = message[len("Value error, "):].rstrip(".") + "."
    else:
        formatted = f"{label}: {message.rstrip('.')}."
    return formatted


def _format_error_detail(detail):
    if isinstance(detail, str):
        formatted = detail
    elif isinstance(detail, list):
        messages = [_format_validation_error(item) for item in detail if isinstance(item, dict)]
        formatted = " ".join(messages) if messages else str(detail)
    else:
        formatted = str(detail)
    return formatted


def _extract_error_detail(response):
    """
    Pull the "detail" out of an error response without assuming the body is JSON."""
    try:
        body = response.json()
    except ValueError:
        return response.text or f"The request failed (status {response.status_code})."

    if isinstance(body, dict) and "detail" in body:
        return body["detail"]
    return response.text or f"The request failed (status {response.status_code})."


def _request(method, path, json_body=None, requires_auth=True):
    """
    Make one request to the backend and return its parsed JSON body.
    """
    url = f"{API_BASE_URL}{path}"
    headers = _auth_headers() if requires_auth else {}

    try:
        response = requests.request(method, url, json=json_body, headers=headers, timeout=120)
    except requests.exceptions.RequestException as exc:
        raise ApiError(0, f"Could not reach the backend at {API_BASE_URL}: {exc}")

    if response.status_code >= 400:
        detail = _format_error_detail(_extract_error_detail(response))
        raise ApiError(response.status_code, detail)

    result = response.json() if response.content else None
    return result


def signup(customer_id, password):
    body = {"customer_id": customer_id, "password": password}
    user = _request("POST", "/auth/signup", json_body=body, requires_auth=False)
    return user


def login(customer_id, password):
    """Returns the raw token response dict ({"access_token": ..., "token_type": ...})."""
    body = {"customer_id": customer_id, "password": password}
    token_response = _request("POST", "/auth/login", json_body=body, requires_auth=False)
    return token_response


def list_my_policies():
    policies = _request("GET", "/claims/policies/mine")
    return policies


def submit_claim(policy_id, claim_type, incident_description, incident_date, claim_amount=None):
    """incident_date must already be an ISO date string, e.g. "2026-08-10"."""
    body = {
        "policy_id": policy_id,
        "claim_type": claim_type,
        "incident_description": incident_description,
        "incident_date": incident_date,
        "claim_amount": claim_amount,
    }
    claim = _request("POST", "/claims/submit", json_body=body)
    return claim


def submit_claim_stream(policy_id, claim_type, incident_description, incident_date, claim_amount=None):
    """
    Like submit_claim, but yields progress events as the backend works:
        {"type": "step", "step": "coverage", "status": "running" | "done"}  (several)
        {"type": "final", "claim": {...}}                                   (last)
    Raises ApiError for a rejected request (checked before the stream starts)
    or if the backend reports a failure part-way through.
    """
    body = {
        "policy_id": policy_id,
        "claim_type": claim_type,
        "incident_description": incident_description,
        "incident_date": incident_date,
        "claim_amount": claim_amount,
    }
    url = f"{API_BASE_URL}/claims/submit/stream"

    try:
        # (connect timeout, max wait between two events) -- not a limit on the whole review.
        response = requests.post(url, json=body, headers=_auth_headers(), stream=True, timeout=(10, 180))
    except requests.exceptions.RequestException as exc:
        raise ApiError(0, f"Could not reach the backend at {API_BASE_URL}: {exc}")

    try:
        if response.status_code >= 400:
            raise ApiError(response.status_code, _format_error_detail(_extract_error_detail(response)))

        for raw_line in response.iter_lines(chunk_size=64):
            if not raw_line:
                continue
            event = json.loads(raw_line.decode("utf-8"))
            if event.get("type") == "error":
                raise ApiError(500, event.get("detail", "Something went wrong while processing your claim."))
            yield event
    except requests.exceptions.RequestException as exc:
        raise ApiError(0, f"The connection to the backend was interrupted: {exc}")
    finally:
        response.close()


def list_my_claims():
    claims = _request("GET", "/claims/mine")
    return claims


def get_claim(claim_id):
    claim = _request("GET", f"/claims/{claim_id}")
    return claim

def send_chat_message(claim_id, message):
    """Ask a follow-up question about one claim; returns the assistant's reply text."""
    body = {"message": message}
    response = _request("POST", f"/claims/{claim_id}/chat", json_body=body)
    return response["reply"]


def get_chat_history(claim_id):
    """Earlier messages for one claim's chat, as [{"role", "content"}, ...]."""
    return _request("GET", f"/claims/{claim_id}/chat")


def get_policies_chat_history():
    """Earlier messages in the Policies-tab chat."""
    return _request("GET", "/policies/chat")


def send_policies_chat_message(message):
    """Ask about any of the customer's policies; returns the assistant's reply text."""
    body = {"message": message}
    response = _request("POST", "/policies/chat", json_body=body)
    return response["reply"]