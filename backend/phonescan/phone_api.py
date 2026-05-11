import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("ABSTRACT_API_KEY")

def get_phone_info(phone_number: str):
    url = "https://phonevalidation.abstractapi.com/v1/"

    params = {
        "api_key": API_KEY,
        "phone": phone_number
    }

    try:
        response = requests.get(url, params=params, timeout=10)

        if response.status_code != 200:
            return {"error": f"HTTP {response.status_code}"}
        
        data = response.json()

        if not isinstance(data, dict):
            return {"error": "Invalid response format"}

        return data

    except requests.RequestException as e:
        return {"error": str(e)}