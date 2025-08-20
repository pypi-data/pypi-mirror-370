import json
from typing import List

from httpx import codes, Response

from heisenberg.exceptions import (
    UnauthorizedError,
    ForbiddenError,
    InvalidRequestError,
    InternalError,
)


def extract_response_error(response: Response):
    try:
        json_res = response.json()
        error = json_res["error"]
    except (json.JSONDecodeError, KeyError):
        error = response.text
    return error or response.text


def response_as_json(response: Response):
    try:
        json_response = response.json()
    except json.JSONDecodeError as e:
        raise InternalError(f"Failed to decode JSON response from agent service: {e}")
    return json_response


def raise_for_status(response: Response):
    if codes.is_success(response.status_code):
        return

    error = extract_response_error(response)
    if response.status_code == 401:
        raise UnauthorizedError(
            message=f"Provided env variable for HEISENBERG_TOKEN or HEISENBERG_API_KEY is not valid, error: {error}"
        )
    if response.status_code == 403:
        raise ForbiddenError(
            message=f"Your credentials cannot access to this tool or resource, error: {error}"
        )
    if response.status_code == 400:
        raise InvalidRequestError(
            message=f"The parameter of request is not valid, error: {error}"
        )
    if response.status_code == 429:
        raise InvalidRequestError(message=f"Request reached its limit, error: {error}")
    raise InternalError(message=error)


def parse_agent_list_response(json_data: dict) -> List[dict]:
    data = json_data.get("results")
    if not isinstance(data, list):
        raise InternalError(
            "Expected a list of agents, but received a non-list response."
        )

    parsed_agents = []
    for i, item in enumerate(data):
        if not isinstance(item, dict):
            continue
        reference_agent = item.get("reference_agent")
        if not isinstance(reference_agent, dict):
            raise InternalError("'reference_agent' is missing or not a dictionary")

        parsed_agents.append(
            {
                "id": item.get("id"),
                "name": item.get("name"),
                "description": item.get("description")
                + "\n"
                + reference_agent.get("description"),
                "initial_prompt": reference_agent.get("initial_prompt"),
            }
        )
    return parsed_agents
