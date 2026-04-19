import requests

API_KEY = "AIzaSyByZVKs8pXKRe3GnvzGf2SV53MyouNGcaU"

def check_google_safe(url):

    endpoint = f"https://safebrowsing.googleapis.com/v4/threatMatches:find?key={API_KEY}"

    payload = {
        "client": {
            "clientId": "cybereye",
            "clientVersion": "1.0"
        },
        "threatInfo": {
            "threatTypes": [
                "MALWARE",
                "SOCIAL_ENGINEERING",
                "UNWANTED_SOFTWARE"
            ],
            "platformTypes": ["ANY_PLATFORM"],
            "threatEntryTypes": ["URL"],
            "threatEntries": [
                {"url": url}
            ]
        }
    }

    try:
        response = requests.post(endpoint, json=payload)

        print("STATUS:", response.status_code)
        print("RESPONSE:", response.text)

        if response.status_code != 200:
            return "unknown"

        data = response.json()

        if data.get("matches"):
            return "phishing"

        return "safe"

    except Exception as e:
        print("Error:", e)
        return "unknown"