console.log("HISTORY JS LOADED");

const historyContainer = document.querySelector(".history-container");

async function loadHistory() {
    try {
        const response = await fetch("http://127.0.0.1:8000/history", {
            headers: {
                "Authorization": "Bearer " + localStorage.getItem("token")
            }
        });

        const data = await response.json();

        console.log("HISTORY DATA:", data);

        historyContainer.innerHTML = "";

        data.history.forEach(scan => {

            let statusClass = "";

            if (scan.result === "safe") statusClass = "safe";
            else if (scan.result === "phishing") statusClass = "danger";
            else statusClass = "unknown";

            historyContainer.innerHTML += `
                <div class="history-card ${statusClass}">
                    <p><strong>Type:</strong> ${scan.type}</p>
                    <p><strong>Value:</strong> ${scan.input_value}</p>
                    <p><strong>Date:</strong> ${new Date(scan.timestamp).toLocaleString()}</p>
                    <p><strong>Result:</strong> ${scan.result.toUpperCase()}</p>
                </div>
            `;
        });

    } catch (error) {
        console.error("History error:", error);
        historyContainer.innerHTML = "<p style='color:red'>Failed to load history</p>";
    }
}

loadHistory();