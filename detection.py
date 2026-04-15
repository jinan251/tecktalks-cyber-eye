def detect_link(url):
    url = url.lower()

    if "@" in url:
        return "phishing"
    if "free" in url or "win" in url:
        return "phishing"
    if url.startswith("http://"):
        return "suspicious"

    return "safe"