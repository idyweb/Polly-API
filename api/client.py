import requests
from typing import Any, Dict, List, Optional, TypedDict


class PollsFetchError(Exception):
    pass


class OptionOut(TypedDict):
    id: int
    text: str
    poll_id: int


class PollOut(TypedDict):
    id: int
    question: str
    created_at: str  # ISO date-time
    owner_id: int
    options: List[OptionOut]


def fetch_polls(
    skip: int = 0,
    limit: int = 10,
    base_url: str = "http://localhost:8000",
    timeout: float = 10.0,
    session: Optional[requests.Session] = None,
) -> List[PollOut]:
    """Fetch paginated polls.

    Parameters:
        skip: Number of items to skip (query param `skip`).
        limit: Max number of items to return (query param `limit`).
        base_url: API base URL, default is http://localhost:8000.
        timeout: Request timeout in seconds.
        session: Optional requests.Session to reuse connections.

    Returns:
        List of polls matching the `PollOut` schema.
    """
    http = session or requests
    url = f"{base_url.rstrip('/')}/polls"
    params = {"skip": skip, "limit": limit}

    resp = http.get(url, params=params, timeout=timeout)

    if resp.status_code == 200:
        data: List[Dict[str, Any]] = resp.json()
        return data  # type: ignore[return-value]

    try:
        resp.raise_for_status()
    except requests.HTTPError as e:
        text = (resp.text or "").strip()
        raise PollsFetchError(f"GET /polls failed ({resp.status_code}): {text or str(e)}") from e
    raise PollsFetchError(f"Unexpected status code {resp.status_code}")



class VotingError(Exception):
    pass


class VoteOut(TypedDict):
    id: int
    user_id: int
    option_id: int
    created_at: str  # ISO date-time


def cast_vote(
    poll_id: int,
    option_id: int,
    base_url: str = "http://localhost:8000",
    timeout: float = 10.0,
    session: Optional[requests.Session] = None,
    bearer_token: Optional[str] = None,
) -> VoteOut:
    """Cast a vote on a poll.

    Parameters:
        poll_id: The target poll ID (path param).
        option_id: The chosen option ID (JSON body `option_id`).
        base_url: API base URL, default is http://localhost:8000.
        timeout: Request timeout in seconds.
        session: Optional requests.Session to reuse connections.
        bearer_token: JWT access token for Authorization header.

    Returns:
        The created vote matching the `VoteOut` schema.
    """
    http = session or requests
    url = f"{base_url.rstrip('/')}/polls/{poll_id}/vote"
    headers: Dict[str, str] = {}
    if bearer_token:
        headers["Authorization"] = f"Bearer {bearer_token}"

    resp = http.post(url, json={"option_id": option_id}, headers=headers or None, timeout=timeout)

    if resp.status_code == 200:
        return resp.json()

    try:
        resp.raise_for_status()
    except requests.HTTPError as e:
        text = (resp.text or "").strip()
        raise VotingError(f"POST /polls/{poll_id}/vote failed ({resp.status_code}): {text or str(e)}") from e
    raise VotingError(f"Unexpected status code {resp.status_code}")


class PollResultsFetchError(Exception):
    pass


class PollResultItem(TypedDict):
    option_id: int
    text: str
    vote_count: int


class PollResults(TypedDict):
    poll_id: int
    question: str
    results: List[PollResultItem]


def get_poll_results(
    poll_id: int,
    base_url: str = "http://localhost:8000",
    timeout: float = 10.0,
    session: Optional[requests.Session] = None,
) -> PollResults:
    """Retrieve aggregated results for a poll.

    Parameters:
        poll_id: The target poll ID (path param).
        base_url: API base URL, default is http://localhost:8000.
        timeout: Request timeout in seconds.
        session: Optional requests.Session to reuse connections.

    Returns:
        Results object matching the `PollResults` schema.
    """
    http = session or requests
    url = f"{base_url.rstrip('/')}/polls/{poll_id}/results"

    resp = http.get(url, timeout=timeout)

    if resp.status_code == 200:
        return resp.json()

    try:
        resp.raise_for_status()
    except requests.HTTPError as e:
        text = (resp.text or "").strip()
        raise PollResultsFetchError(
            f"GET /polls/{poll_id}/results failed ({resp.status_code}): {text or str(e)}"
        ) from e
    raise PollResultsFetchError(f"Unexpected status code {resp.status_code}")

