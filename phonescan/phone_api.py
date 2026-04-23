import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("0727412f42244882baebc0e20414136e")

def get_phone_info(phone_number: str):
    url = "https://phonevalidation.abstractapi.com/v1/"

    params = {
        "api_key": API_KEY,
        "phone": phone_number
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        return {"error": str(e)}