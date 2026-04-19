from fastapi import FastAPI #creates the api application
from models import URLRequest #for the type of the input 
from detection import detect_link #for the function 
from google_safe import check_google_safe
from fastapi.middleware.cors import CORSMiddleware
from database import save_scan #for using the function from the database

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#@app.post("/scan-link")
#def scan_link(request: URLRequest):
    #result = detect_link(request.url)

    
    #save_scan(request.url, result) #function that save the url and result in the database    

    #return {
       # "url": request.url,
       # "result": result
   # }

@app.post("/scan-link")
def scan_link(request: URLRequest):

    url = request.url

    # 1. Heuristic detection
    heuristic_result = detect_link(url)

    # 2. Google Safe Browsing detection
    google_result = check_google_safe(url)

    # 3. Final decision logic (fusion)
    if google_result == "phishing":
        final_result = "phishing"

    elif heuristic_result == "phishing":
        final_result = "phishing"

    elif heuristic_result == "suspicious" or google_result == "unknown":
        final_result = "suspicious"

    else:
        final_result = "safe"

    # 4. Save into database
    save_scan(url, final_result)

    # 5. Return response
    return {
        "url": url,
        "heuristic_result": heuristic_result,
        "google_result": google_result,
        "final_result": final_result
    }