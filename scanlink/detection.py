from urllib.parse import urlparse
import re
import math


# Helper: entropy

def entropy(s):
    if not s:
        return 0
    prob = [float(s.count(c)) / len(s) for c in dict.fromkeys(list(s))]
    return -sum(p * math.log2(p) for p in prob)


# Helper: similarity (typosquat detection)

def similarity(a, b):
    return sum(1 for i, j in zip(a, b) if i != j) + abs(len(a) - len(b))


# Main detector

def detect_link(url, domain_age=None):
    url = url.lower()
    parsed = urlparse(url)
    hostname = parsed.hostname or ""
    path = parsed.path or ""

    score = 0

    parts = hostname.split(".")
    subdomain = parts[0] if parts else ""

    
    #  STRONG SIGNALS
    

    if "@" in url:
        score += 3

    if re.match(r"http[s]?://\d{1,3}(\.\d{1,3}){3}(/|$)", url):
        score += 3

    
    #  STRUCTURE SIGNALS
    

    if parsed.scheme == "http":
        score += 1

    if len(url) > 100:
        score += 2

    if url.count("-") > 3:
        score += 1

    if "%" in url:
        score += 1

    if re.search(r"(.)\1{3,}", url):
        score += 1

    if hostname.count(".") >= 3:
        score += 1

    if entropy(hostname) > 4:
        score += 1

    
    # KEYWORDS
    

    high_risk_words = ["login", "password", "secure", "verify", "update", "confirm", "auth", "check"]
    bait_words = ["free", "win", "prize", "reward", "claim"]

    if any(word in url for word in high_risk_words):
        score += 2

    if any(word in url for word in bait_words):
        score += 2

    if any(word in url for word in bait_words) and len(hostname.split(".")) <= 2:
        score += 2

   
    #BRAND IMPERSONATION + TYPOSQUATTING
  

    trusted_brands = ["paypal", "google", "facebook", "amazon", "microsoft", "bank"]

    for brand in trusted_brands:

        if brand in url and brand not in hostname:
            score += 3

        if similarity(hostname, brand) <= 2 and brand not in hostname:
            score += 4

        if brand in hostname and brand not in parts[-2]:
            score += 4

    
    #SUSPICIOUS TLDs
    

    bad_tlds = [".xyz", ".click", ".top", ".site", ".online", ".shop"]

    if any(hostname.endswith(tld) for tld in bad_tlds):
        score += 2

        if entropy(subdomain) > 3.5:
            score += 3

    
    #TRUSTED PLATFORM ABUSE
    

    trusted_platforms = ["wixstudio.com", "github.io", "sites.google.com"]

    if any(tp in hostname for tp in trusted_platforms):
        score += 3

    if any(tp in hostname for tp in trusted_platforms) and any(word in url for word in high_risk_words):
        score += 3

   
    #  STRUCTURE PHISHING PATTERNS
    

    suspicious_patterns = ["account", "security", "verify", "update", "login", "check"]

    if any(p in url for p in suspicious_patterns):
        score += 2

    login_paths = ["login", "auth", "signin", "verify", "account", "secure"]

    if any(p in path for p in login_paths):
        score += 3

    
    #  DANGEROUS FILES
    

    if any(url.endswith(ext) for ext in [".exe", ".zip", ".bat", ".sh"]):
        score += 2

    
    #  URL SHORTENER DETECTION
    

    shorteners = ["bit.ly", "t.co", "tinyurl.com", "is.gd", "goo.gl", "ow.ly", "x.co"]

    if any(short in hostname for short in shorteners):
        score += 4

   

    
    #  QUERY STRING ABUSE
    

    if parsed.query:
        score += 2

   
    #  NEW ADDED PATTERNS (FINAL ADDITION BLOCK)
   

    if url.count("http") > 1:
        score += 5

    if "ipfs" in hostname or "dweb.link" in hostname:
        score += 4

    cloud_hosts = ["web.core.windows.net", "amazonaws.com", "firebaseapp.com", "netlify.app", "vercel.app"]
    if any(h in hostname for h in cloud_hosts):
        score += 3

    if entropy(hostname) > 3.8 and hostname.count(".") == 1:
        score += 3

    if re.search(r"(micros|paypa|faceb|googl)[a-z0-9]{2,}", hostname):
        score += 4

    if re.search(r"(login|signin|verify|account|secure)", path) and len(path) > 20:
        score += 2

    if hostname.count(".") >= 4:
        score += 3

    if any(r in hostname for r in shorteners):
        score += 4

    if re.search(r"(amazon|paypal|microsoft|bank).*(login|secure|verify)", hostname):
        score += 4

    extra_bad_tlds = [".cfd", ".mobi", ".xyz", ".click", ".top", ".site", ".online", ".shop"]
    if any(hostname.endswith(tld) for tld in extra_bad_tlds):
        if entropy(subdomain) > 3:
            score += 3

    trusted_impersonation = ["netflix", "amazon", "microsoft", "paypal", "instagram"]
    if any(t in hostname for t in trusted_impersonation):
        if not any(t in parts[-2] for t in trusted_impersonation):
            score += 4


    # NEW: ADVANCED BRAND FUZZING / IMPERSONATION FIX (ADDED INSIDE FUNCTION)
    

    for brand in ["amazon", "paypal", "google", "facebook", "microsoft"]:

        if brand[:3] in hostname and brand not in hostname:
            score += 3

        if re.search(rf"{brand}[a-z0-9]+", hostname):
            score += 3

        normalized = hostname.replace("0", "o").replace("1", "l")
        if brand in normalized and brand not in hostname:
            score += 2

   
    #  FINAL DECISION
    

    if score >= 6:
        return "phishing"
    elif score >= 3:
        return "suspicious"
    else:
        return "safe"