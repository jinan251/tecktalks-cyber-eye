from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
# Imports must match your existing folder/file names
from backend.models import URLRequest 
from backend.detection import detect_link 
from backend.google_safe import check_google_safe
from database.connection_to_backend import save_scan 

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/scan-link")
def scan_link(request: URLRequest):
    """Main endpoint to scan a URL using Heuristics and Google Safe Browsing"""
    url = request.url

    # 1. Heuristic detection
    heuristic_result = detect_link(url)

    # 2. Google Safe Browsing detection
    google_result = check_google_safe(url)

    # 3. Final decision logic (Fusion)
    if google_result == "phishing" or heuristic_result == "phishing":
        final_result = "phishing"
    elif heuristic_result == "suspicious":
        final_result = "suspicious"
    else:
        final_result = "safe"

    # 4. Save into database
    save_scan(url, final_result)

    return {
        "url": url,
        "heuristic_result": heuristic_result,
        "google_result": google_result,
        "final_result": final_result
    }