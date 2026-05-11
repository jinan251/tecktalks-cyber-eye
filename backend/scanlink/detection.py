from urllib.parse import urlparse
import re
import math


# =========================
# Helpers
# =========================
def entropy(s):
    if not s:
        return 0
    prob = [float(s.count(c)) / len(s) for c in dict.fromkeys(list(s))]
    return -sum(p * math.log2(p) for p in prob)


# =========================
# MAIN DETECTOR
# =========================
def detect_link(url, domain_age=None):
    url = url.lower().strip()
    parsed = urlparse(url)

    hostname = parsed.hostname or ""
    path = parsed.path or ""
    full_url = url

    score = 0

    # =========================
    # TRUSTED DOMAINS (HARD SAFE)
    # =========================
    trusted_domains = [
        "google.com",
        "microsoft.com",
        "github.com",
        "amazon.com",
        "facebook.com",
        "apple.com"
    ]

    if any(hostname == d or hostname.endswith("." + d) for d in trusted_domains):
        return "safe"

    # =========================
    # IP / LOCAL NETWORK
    # =========================
    if re.match(r"^https?://\d{1,3}(\.\d{1,3}){3}(/|$)", full_url):
        score += 5

    if hostname.startswith("127.") or "localhost" in hostname:
        score += 5

    # =========================
    # SHORTENERS (HIGH RISK)
    # =========================
    shorteners = ["bit.ly", "tinyurl.com", "t.co", "is.gd"]
    if any(s in hostname for s in shorteners):
        score += 5

    # =========================
    # BRAND SPOOFING (IMPORTANT FIX)
    # =========================
    brands = ["google", "microsoft", "amazon", "paypal", "facebook"]

    for brand in brands:
        if brand in hostname:
            # fake brand subdomain attack
            if not any(hostname.endswith(d) for d in trusted_domains):
                score += 5

            # strong spoof pattern
            if re.search(rf"{brand}[-_.]?[a-z0-9]+", hostname):
                score += 4

    # =========================
    # PHISHING KEYWORDS
    # =========================
    phishing_keywords = [
        "login", "secure", "verify", "account",
        "password", "update", "confirm", "signin"
    ]

    if any(k in hostname for k in phishing_keywords):
        score += 2

    if any(k in path for k in phishing_keywords):
        score += 2

    # =========================
    # SUSPICIOUS TLDs
    # =========================
    bad_tlds = [".xyz", ".click", ".top", ".site", ".online", ".shop", ".ru"]
    if any(hostname.endswith(tld) for tld in bad_tlds):
        score += 4

    # =========================
    # STRUCTURE SIGNALS
    # =========================
    if "@" in full_url:
        score += 4

    if parsed.scheme == "http":
        score += 1

    if len(full_url) > 120:
        score += 1

    if hostname.count(".") >= 4:
        score += 2

    if entropy(hostname) > 4.3:
        score += 2

    # =========================
    # FINAL DECISION (STABLE THRESHOLDS)
    # =========================
    if score >= 10:
        return "phishing"
    elif score >= 6:
        return "suspicious"
    else:
        return "safe"