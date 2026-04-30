import gradio as gr
import requests

BACKEND_URL = "http://127.0.0.1:8000"

# --- Functions (The Logic) ---

def login_user(email, password):
    try:
        response = requests.post(
    f"{BACKEND_URL}/login",
    json={
        "email": email.strip().lower(),
        "password": password
    }
)
        if response.status_code == 200:
            token = response.json().get("access_token")
            
            return f"✅ Welcome! Access Granted.", gr.update(visible=True), gr.update(visible=False), token
        else:
            return "❌ Login Failed: Check credentials.", gr.update(visible=False), gr.update(visible=True), ""
    except:
        return "⚠️ Error: Backend is offline!", gr.update(visible=False), gr.update(visible=True), ""
    
    
def signup_user(username, email, password):
    try:
        payload = {"username": username, "email": email, "password": password}
        response = requests.post(f"{BACKEND_URL}/signup", json=payload)
        if response.status_code == 200:
            # Logic: Show OTP input section and hide the main register button
            return "✅ User Created! Enter the 6-digit OTP from your email.", gr.update(visible=True), gr.update(visible=False)
        else:
            return f"❌ Signup Failed: {response.text}", gr.update(visible=False), gr.update(visible=True)
    except:
        return "⚠️ Error: Backend is offline!", gr.update(visible=False), gr.update(visible=True)

def verify_otp_logic(email, otp_code):
    try:
        payload = {
            "email": email.strip().lower(),
            "otp_code": otp_code.strip()
        }
        
        response = requests.post(f"{BACKEND_URL}/verify-email", json=payload)
        
        if response.status_code == 200:
            
            data = response.json()
            token = data.get("access_token", "") 
            
            
            return "✅ Verified! Welcome to CyberEye.", gr.update(visible=True), gr.update(visible=False), token
        else:
            error_detail = response.json().get("detail", "Invalid OTP.")
            
            return f"❌ {error_detail}", gr.update(visible=False), gr.update(visible=True), ""
    except Exception as e:
        return f"⚠️ Connection Error: {str(e)}", gr.update(visible=False), gr.update(visible=True), ""
    
def scan_link(input_text, input_type, token):
    try:
        if not token:
            return "❌ Error: No session found. Please login again."
            
        endpoint = "/scan-link" if input_type == "URL" else "/scan-phone"
        payload = {"url": input_text} if input_type == "URL" else {"phone": input_text}
        
        # add the token to the header
        headers = {"Authorization": f"Bearer {token}"}
        
        response = requests.post(f"{BACKEND_URL}{endpoint}", json=payload, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            result = data.get("final_result") or data.get("final_status")
            return f"🔍 Result: {result.upper()}"
        else:
            return f"❌ Error: {response.status_code} - {response.text}"
    except Exception as e:
        return f"⚠️ Connection Error: {str(e)}"
    
def navigate(screen):
    if screen == "login":
        return gr.update(visible=False), gr.update(visible=True), gr.update(visible=False)
    elif screen == "signup":
        return gr.update(visible=False), gr.update(visible=False), gr.update(visible=True)
    else:
        return gr.update(visible=True), gr.update(visible=False), gr.update(visible=False)

# --- Layout (The Design) ---

with gr.Blocks(title="🛡️ CyberEye Security Portal") as demo:
    gr.Markdown("# 🛡️ CyberEye Security System")

    auth_token = gr.State("") #added

    # 1. Home Screen
    with gr.Column(visible=True) as home_ui:
        gr.Markdown("### Welcome! Please choose an option to start:")
        with gr.Row():
            btn_goto_login = gr.Button("Login", variant="primary")
            btn_goto_signup = gr.Button("Sign Up")

    # 2. Login Screen
    with gr.Column(visible=False) as login_ui:
        gr.Markdown("## Login")
        user_in = gr.Textbox(label="Email")
        pass_in = gr.Textbox(label="Password", type="password")
        login_btn = gr.Button("Submit Login")
        back_home1 = gr.Button("← Back")
        login_status = gr.Markdown("")

    # 3. Signup Screen
    with gr.Column(visible=False) as signup_ui:
        gr.Markdown("## Create New Account")
        reg_user = gr.Textbox(label="Username")
        reg_email = gr.Textbox(label="Email")
        reg_pass = gr.Textbox(label="Password", type="password")
        signup_btn = gr.Button("Register", variant="primary")
        
        # OTP verification section
        with gr.Column(visible=False) as otp_ui:
            gr.Markdown("### 📧 Email Verification")
            otp_val = gr.Textbox(label="Enter 6-digit Code", placeholder="123456")
            verify_btn = gr.Button("Verify & Enter App", variant="primary")
            
        back_home2 = gr.Button("← Back")
        signup_status = gr.Markdown("")

    # 4. Scanner Screen
    with gr.Column(visible=False) as scanner_ui:
        gr.Markdown("---")
        gr.Markdown("### 🔍 Security Scanner Dashboard")
        input_type = gr.Radio(["URL", "Phone Number"], label="Scan Type", value="URL")
        data_input = gr.Textbox(label="Enter Link or Phone")
        scan_btn = gr.Button("Start Scan", variant="primary")
        output_text = gr.Textbox(label="Results")

    # --- Button Logic ---
    
    btn_goto_login.click(fn=lambda: navigate("login"), outputs=[home_ui, login_ui, signup_ui])
    btn_goto_signup.click(fn=lambda: navigate("signup"), outputs=[home_ui, login_ui, signup_ui])
    back_home1.click(fn=lambda: navigate("home"), outputs=[home_ui, login_ui, signup_ui])
    back_home2.click(fn=lambda: navigate("home"), outputs=[home_ui, login_ui, signup_ui])

    # Updated: Added auth_token to outputs to store the JWT after login
    login_btn.click(
        fn=login_user, 
        inputs=[user_in, pass_in], 
        outputs=[login_status, scanner_ui, login_ui, auth_token]
    )
    
    # Signup shows OTP UI
    signup_btn.click(fn=signup_user, inputs=[reg_user, reg_email, reg_pass], outputs=[signup_status, otp_ui, signup_btn])
    
    # Updated: Added auth_token to outputs to store the JWT after OTP verification
    verify_btn.click(
        fn=verify_otp_logic, 
        inputs=[reg_email, otp_val], 
        outputs=[signup_status, scanner_ui, signup_ui, auth_token]
    )
    
    # Updated: Added auth_token to inputs so the scan function can use the stored JWT
    scan_btn.click(
        fn=scan_link, 
        inputs=[data_input, input_type, auth_token], 
        outputs=output_text
    )
if __name__ == "__main__":
    demo.launch(debug=True)