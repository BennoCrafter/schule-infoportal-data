"""
Fetch data from schule-infoportal api
"""

import os

import dotenv
import requests
from requests.auth import HTTPBasicAuth

from src.models import News, Substitution

dotenv.load_dotenv()
login_username = os.getenv("LOGIN_USERNAME", "")
login_password = os.getenv("PASSWORD", "")

BASE_URL = "https://schule-infoportal-api.vercel.app/"


def fetch_data() -> tuple[list[Substitution], list[News]]:
    substitutions = requests.get(
        BASE_URL + "substitutions",
        auth=HTTPBasicAuth(login_username, login_password),
    ).json()

    news = requests.get(
        BASE_URL + "news",
        auth=HTTPBasicAuth(login_username, login_password),
    ).json()

    return [Substitution(**sub) for sub in substitutions], [News(**n) for n in news]


def update_data_cycle() -> None:
    substitutions, news = fetch_data()
