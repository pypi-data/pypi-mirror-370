from dotenv import load_dotenv
from agilix_api_fr8train.models.connection import Connection
import os
import requests


def build_api_connection() -> Connection:
    load_dotenv(override=True)

    base_url = os.getenv("BASE_URL")
    username = os.getenv("USERNAME")
    password = os.getenv("PASSWORD")
    domain = os.getenv("DOMAIN")
    home_domain_id = int(os.getenv("HOME_DOMAIN_ID"))

    session = requests.Session()
    session.headers.update({
        "Content-Type": "application/json",
        "Accept": "application/json"
    })

    json_payload = {
        "request": {
            "cmd": "login3",
            "username": f"{domain}/{username}",
            "password": password
        }
    }

    response = session.post(base_url, json=json_payload)
    response.raise_for_status()
    login_data = response.json()

    login_token = login_data.get('response', {}).get('user', {}).get('token', None)

    if login_token is None:
        error_code = login_data.get('response', {}).get('code', "Generic Error")
        error_message = login_data.get('response', {}).get('message', "Generic Error")
        raise Exception(f"{error_code}: {error_message}")

    conn = Connection(
        base_url=base_url,
        session=session,
        token=login_token,
        home_domain_id=home_domain_id
    )

    return conn
