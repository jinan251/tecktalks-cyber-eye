from fastapi import FastAPI #creates the api application
from models import URLRequest #for the type of the input 
from detection import detect_link #for the function 
from fastapi.middleware.cors import CORSMiddleware

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
    result = detect_link(request.url)

    return {
        "url": request.url,
        "result": result
    }