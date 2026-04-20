import gradio as gr
import requests

# The URL of your running FastAPI server
API_URL = "http://127.0.0.1:8000/scan-link"

def scan_link_real(link):
    """
    Sends the URL to the FastAPI backend and returns the final result.
    """
    try:
        # Send a POST request to the backend
        response = requests.post(API_URL, json={"url": link})
        
        if response.status_code == 200:
            data = response.json()
            # Extract results from the backend response
            final = data.get("final_result", "unknown")
            heuristic = data.get("heuristic_result", "unknown")
            google = data.get("google_result", "unknown")
            
            return f"Final Decision: {final.upper()}\n(Heuristic: {heuristic}, Google: {google})"
        else:
            return "Error: Backend is not responding correctly."
    except Exception as e:
        return f"Error: Make sure the Backend server is running! ({e})"

# Create the Gradio interface
iface = gr.Interface(
    fn=scan_link_real,
    inputs=gr.Textbox(lines=2, placeholder="Enter a URL to scan..."),
    outputs="text",
    title="CyberEye: Professional URL Scanner",
    description="This interface is now connected to your FastAPI Backend and SQLite Database."
)

if __name__ == "__main__":
    iface.launch()