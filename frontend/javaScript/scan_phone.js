console.log("SCAN PHONE JS LOADED");

const phoneInput = document.getElementById("phone");
const countrySelect = document.getElementById("countrySelect");
const resultBox = document.getElementById("phoneResult");

// =========================
// LOAD COUNTRIES
// =========================
async function loadCountries() {
    try {
        const response = await fetch("http://127.0.0.1:8000/countries");
        const data = await response.json();

        data.forEach(country => {
            const option = document.createElement("option");
            option.value = country.code;
            option.innerText = `${country.name} (+${country.code})`;
            countrySelect.appendChild(option);
        });

    } catch (err) {
        console.error("Country load failed", err);
    }
}

loadCountries();

// =========================
// SCAN
// =========================
async function scanPhone() {

    const phone = phoneInput.value.trim();
    const countryCode = countrySelect.value;

    if (!countryCode) {
        resultBox.innerHTML = "<p style='color:red'>Please select a country</p>";
        return;
    }

    if (!phone || !countryCode) {
        resultBox.innerHTML = "<p style='color:red'>Please enter phone + country</p>";
        return;
    }

    resultBox.innerHTML = `
        <div class="loading-box">
            <div class="loader"></div>
            <p>Scanning...</p>
        </div>
    `;

    try {
        const response = await fetch("http://127.0.0.1:8000/scan-phone", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": "Bearer " + localStorage.getItem("token")
            },
            body: JSON.stringify({
                phone: phone,
                country_code: countryCode
            })
        });

        const data = await response.json();

        console.log("RESULT:", data);

        if (!data.final_status) {
            resultBox.innerHTML = "<p style='color:red'>Invalid response</p>";
            return;
        }

        const status = data.final_status.toUpperCase();

        let className = "unknown-result";

        if (data.final_status === "safe") className = "safe-result";
        if (data.final_status === "phishing") className = "phishing-result";
        if (data.final_status === "suspicious") className = "suspicious-result";

        resultBox.innerHTML = `
            <div class="phone-result-card ${className}">
                <h2>${status}</h2>
            </div>
        `;

    } catch (err) {
        console.error(err);
        resultBox.innerHTML = "<p style='color:red'>Server error</p>";
    }
}