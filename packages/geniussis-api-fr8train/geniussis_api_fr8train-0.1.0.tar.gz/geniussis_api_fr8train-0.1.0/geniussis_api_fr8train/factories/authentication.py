from dotenv import load_dotenv
import os
import requests
from geniussis_api_fr8train.models.connection import Connection


def build_api_connector() -> Connection:
    load_dotenv(override=True)

    api_client_key = os.getenv("API_CLIENT_KEY")
    api_secret = os.getenv("API_SECRET")
    api_host = os.getenv("API_HOST")

    session = requests.Session()
    session.headers.update(
        {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
    )

    auth_payload = {"apiClientId": api_client_key, "apiClientSecret": api_secret}

    response = session.post(
        f"{api_host}/api/v1/Authentication/login", json=auth_payload
    )
    response.raise_for_status()
    data = response.json()

    if not data.get("success"):
        raise Exception(f"{data.get('errorCode')}: {data.get('message')}")

    return Connection(
        base_url=api_host,
        token=data.get("token"),
        session=session,
    )
