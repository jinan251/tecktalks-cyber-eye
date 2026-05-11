async function scanLink() {

    // Get URL input
    const url = document.getElementById("url").value;

    // Get result div
    const resultBox = document.getElementById("result");

    // Check if input is empty
    if (!url) {
        resultBox.innerHTML = "Please enter a URL";
        return;
    }

    try {

        //get token first
        const token = localStorage.getItem("token");

        if (!token) {
                    resultBox.innerHTML = "Please login again (token missing)";
                    return;
                }

        resultBox.innerHTML = `
            <div class="loading-box">
                <div class="loader"></div>
                <p>Scanning URL...</p>
            </div>
        `;

        // Send request to backend
        const response = await fetch("http://127.0.0.1:8000/scan-link", {

            method: "POST",

            headers: {
                "Content-Type": "application/json",
                "Authorization": "Bearer " + token
            },

            body: JSON.stringify({
                url: url
            })

        });

        // Convert response to JSON
        const data = await response.json();

        // Display result
        let resultClass = "";

if (data.final_result === "safe") {
    resultClass = "safe-result";
}
else if (data.final_result === "phishing") {
    resultClass = "phishing-result";
}
else {
    resultClass = "suspicious-result";
}

resultBox.innerHTML = `
    <div class="result-card ${resultClass}">

        <h2 class="result-title">
            ${data.final_result.toUpperCase()}
        </h2>

    </div>
`;
    } catch (error) {

        console.error(error);

        resultBox.innerHTML = "Error connecting to backend";

    }
}