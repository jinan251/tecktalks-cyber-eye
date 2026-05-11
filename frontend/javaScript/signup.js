console.log("SIGNUP JS LOADED");

// =========================
// FORM
// =========================

const form = document.querySelector(".form");
const signupBtn = document.querySelector(".btn");

const fullNameInput =
    document.querySelector("input[placeholder='Full Name']");

const emailInput =
    document.querySelector("input[type='email']");

const phoneInput =
    document.querySelector("input[placeholder='Phone Number']");

const passwordInput =
    document.querySelectorAll("input[type='password']")[0];

const confirmPasswordInput =
    document.querySelectorAll("input[type='password']")[1];

// =========================
// VERIFY
// =========================

const verifyBox = document.getElementById("verifyBox");
const verifyBtn = document.getElementById("verifyBtn");
const verifyInput = document.getElementById("verificationCode");
const verifyMessage = document.getElementById("verifyError");

// =========================
// ERROR UI
// =========================

const errorMessage = document.getElementById("errorMessage");

// =========================
// TEMP EMAIL
// =========================

let tempEmail = "";

// =========================
// SHOW MESSAGE
// =========================

function showError(msg) {
    errorMessage.style.display = "block";
    errorMessage.style.color = "#ff4d4d";
    errorMessage.innerText = msg;
}

function showSuccess(msg) {
    errorMessage.style.display = "block";
    errorMessage.style.color = "#00ff88";
    errorMessage.innerText = msg;
}

// =========================
// EYE TOGGLE
// =========================

document.querySelectorAll(".password-wrapper").forEach(wrapper => {

    const input = wrapper.querySelector("input");
    const toggle = wrapper.querySelector(".toggle-password");

    const eyeOpen = wrapper.querySelector(".eye-open");
    const eyeClosed = wrapper.querySelector(".eye-closed");

    toggle.addEventListener("click", () => {

        const hidden = input.type === "password";

        input.type = hidden ? "text" : "password";

        eyeOpen.style.display = hidden ? "none" : "block";
        eyeClosed.style.display = hidden ? "block" : "none";

    });

});

// =========================
// LIVE PASSWORD RULES
// =========================

passwordInput.addEventListener("input", () => {

    const value = passwordInput.value;

    updateRule("rule-length", value.length >= 8);
    updateRule("rule-uppercase", /[A-Z]/.test(value));
    updateRule("rule-number", /[0-9]/.test(value));
    updateRule("rule-special", /[^A-Za-z0-9]/.test(value));

});

function updateRule(id, valid) {

    const element = document.getElementById(id);

    if (!element) return;

    if (valid) {
        element.classList.add("valid");
    } else {
        element.classList.remove("valid");
    }

}

// =========================
// SIGNUP
// =========================

form.addEventListener("submit", async function (e) {

    e.preventDefault();

    const fullName = fullNameInput.value.trim();
    const email = emailInput.value.trim();
    const phone = phoneInput.value.trim();

    const password = passwordInput.value;
    const confirmPassword = confirmPasswordInput.value;

    if (!fullName || !email || !phone ||
        !password || !confirmPassword) {

        showError("All fields are required");
        return;
    }

    if (password !== confirmPassword) {
        showError("Passwords do not match");
        return;
    }

    signupBtn.disabled = true;
    signupBtn.innerText = "Sending verification...";

    try {

        const response = await fetch(
            "http://127.0.0.1:8000/signup",
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    username: fullName,
                    email: email,
                    phone: phone,
                    password: password
                })
            }
        );

        const data = await response.json();

        console.log(data);

        if (response.ok) {

            tempEmail = email;

            verifyBox.style.display = "block";

            showSuccess(
                "Verification code sent successfully"
            );

        } else {

            showError(data.detail || "Signup failed");

        }

    } catch (error) {

        console.log(error);

        showError("Server error");

    }

    signupBtn.disabled = false;
    signupBtn.innerText = "Sign Up";

});

// =========================
// VERIFY EMAIL
// =========================

verifyBtn.addEventListener("click", async () => {

    const code = verifyInput.value.trim();

    if (!code) {

        verifyMessage.innerText =
            "Please enter verification code";

        verifyMessage.style.color = "red";

        return;
    }

    try {

        const response = await fetch(
            "http://127.0.0.1:8000/verify-email",
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    email: tempEmail,
                    otp_code: code
                })
            }
        );

        const data = await response.json();

        console.log(data);

        if (response.ok) {

            localStorage.setItem(
                "token",
                data.access_token
            );

            verifyMessage.innerText =
                "Account verified successfully ✔";

            verifyMessage.style.color = "#00ff88";

            setTimeout(() => {
                window.location.href =
                    "dashboard.html";
            }, 1500);

        } else {

            verifyMessage.innerText =
                data.detail || "Invalid code";

            verifyMessage.style.color = "red";

        }

    } catch (error) {

        console.log(error);

        verifyMessage.innerText =
            "Server error";

        verifyMessage.style.color = "red";

    }

});