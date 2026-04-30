import requests
import os
import base64
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("VIRUSTOTAL_API_KEY")



def url_to_id(url):
    url_bytes = url.encode("utf-8")
    return base64.urlsafe_b64encode(url_bytes).decode().strip("=")



def check_virustotal(url):
    headers = {
        "x-apikey": API_KEY
    }

    try:
        url_id = url_to_id(url)

        response = requests.get(
            f"https://www.virustotal.com/api/v3/urls/{url_id}",
            headers=headers,
            timeout=10
        )

        if response.status_code != 200:
            return "unknown"

        data = response.json()

        stats = data.get("data", {}).get("attributes", {}).get("last_analysis_stats", {})

        malicious = stats.get("malicious", 0)
        suspicious = stats.get("suspicious", 0)

        if malicious > 0:
            return "phishing"
        elif suspicious > 0:
            return "suspicious"
        else:
            return "safe"

    except Exception as e:
        print("VirusTotal error:", e)
        return "unknown"