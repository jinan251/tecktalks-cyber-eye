from fastapi import FastAPI #creates the api application
from models import URLRequest #for the type of the input 
from detection import detect_link #for the function 
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

@app.post("/scan-link")
def scan_link(request: URLRequest):
    result = detect_link(request.url)

    
    save_scan(request.url, result) #function that save the url and result in the database    

    return {
        "url": request.url,
        "result": result
    }