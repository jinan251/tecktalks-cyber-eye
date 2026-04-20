import gradio as gr

def scan_link(link):
    """
    A placeholder function to simulate link scanning for phishing.
    In a real application, this would involve more sophisticated checks.
    """
    if "phishing" in link.lower() or "malicious" in link.lower():
        return "Warning: This link might be phishing!"
    elif "safe" in link.lower() or "google.com" in link.lower():
        return "This link appears safe."
    else:
        return "Scanning complete: Unable to determine phishing status with current simple logic. (Placeholder)"

# Create the Gradio interface
iface = gr.Interface(
    fn=scan_link,
    inputs=gr.Textbox(lines=2, placeholder="Enter a URL to scan..."),
    outputs="text",
    title="URL Scanner for Fishing Safety",
    description="Paste a URL below and click 'Submit' to check if it's potentially a phishing link."
)

# Launch the interface
# The `share=True` option generates a public, shareable link (valid for 72 hours)
# which is useful when running in Colab.
iface.launch(debug=True)