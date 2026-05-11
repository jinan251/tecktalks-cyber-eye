console.log("LOGIN JS LOADED");

const form = document.querySelector(".form");
const loginBtn = document.getElementById("loginBtn");
const btnText = document.getElementById("btnText");
const errorBox = document.getElementById("errorMessage");

// =========================
// PASSWORD INPUT (SAFE)
// =========================

const passwordInput = document.querySelector(".form input[type='password']");

// password rules (ONLY if exist)
const ruleLength = document.getElementById("rule-length");
const ruleUpper = document.getElementById("rule-uppercase");
const ruleNumber = document.getElementById("rule-number");
const ruleSpecial = document.getElementById("rule-special");

// =========================
// EYE TOGGLE (SAFE VERSION)
// =========================

document.addEventListener("DOMContentLoaded", function () {

    document.querySelectorAll(".password-wrapper").forEach(wrapper => {

        const input = wrapper.querySelector("input");
        const toggle = wrapper.querySelector(".toggle-password");
        const eyeOpen = wrapper.querySelector(".eye-open");
        const eyeClosed = wrapper.querySelector(".eye-closed");

        if (!input || !toggle) return;

        toggle.addEventListener("click", () => {

            const isHidden = input.type === "password";

            input.type = isHidden ? "text" : "password";

            if (eyeOpen && eyeClosed) {
                eyeOpen.style.display = isHidden ? "none" : "block";
                eyeClosed.style.display = isHidden ? "block" : "none";
            }

        });

    });

});

// =========================
// LIVE PASSWORD CHECK (ONLY IF EXISTS)
// =========================

if (passwordInput) {

    passwordInput.addEventListener("input", function () {
        const value = passwordInput.value;

        if (ruleLength) updateRule(ruleLength, value.length >= 8);
        if (ruleUpper) updateRule(ruleUpper, /[A-Z]/.test(value));
        if (ruleNumber) updateRule(ruleNumber, /[0-9]/.test(value));
        if (ruleSpecial) updateRule(ruleSpecial, /[^A-Za-z0-9]/.test(value));
    });

}

function updateRule(element, isValid) {
    element.classList.remove("valid");
    if (isValid) {
        element.classList.add("valid");
    }
}

// =========================
// FORM SUBMIT
// =========================

form.addEventListener("submit", async function (e) {
    e.preventDefault();

    const email = document.querySelector("input[type='email']").value.trim();
    const password = passwordInput.value;

    hideError();

    if (!validateEmail(email)) {
        return showError("Please enter a valid email address");
    }

    if (!validatePassword(password)) {
        return showError("Password must meet all requirements");
    }

    loginBtn.disabled = true;
    btnText.innerHTML = "Loading...";

    try {
        const response = await fetch("http://127.0.0.1:8000/login", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email, password })
        });

        const data = await response.json();

        if (data.message === "Login successful") {
            localStorage.setItem("token", data.data.access_token);
            window.location.href = "dashboard.html";
        } else {
            showError("Invalid email or password");
        }

    } catch (error) {
        showError("Server error, please try again later");
    }

    loginBtn.disabled = false;
    btnText.innerHTML = "Login";
});

// =========================
// VALIDATION
// =========================

function validateEmail(email) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

function validatePassword(password) {
    return (
        password.length >= 8 &&
        /[A-Z]/.test(password) &&
        /[0-9]/.test(password) &&
        /[^A-Za-z0-9]/.test(password)
    );
}

// =========================
// ERROR UI
// =========================

function showError(msg) {
    if (!errorBox) return;

    errorBox.innerText = msg;
    errorBox.style.display = "block";

    setTimeout(() => hideError(), 3000);
}

function hideError() {
    if (!errorBox) return;
    errorBox.style.display = "none";
}