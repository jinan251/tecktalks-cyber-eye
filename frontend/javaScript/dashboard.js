console.log("DASHBOARD LOADED");

const token = localStorage.getItem("token");

async function loadDashboard() {

    try {
        const response = await fetch("http://127.0.0.1:8000/history?limit=100", {
            headers: {
                "Authorization": "Bearer " + token
            }
        });

        const data = await response.json();

        const scans = data.history || [];

        let total = scans.length;
        let safe = 0;
        let threats = 0;

        const today = new Date().toISOString().split("T")[0];
        let todayCount = 0;

        scans.forEach(scan => {

            if (scan.result === "safe") safe++;
            else if (scan.result === "phishing") threats++;

            if (scan.timestamp && scan.timestamp.startsWith(today)) {
                todayCount++;
            }
        });

        // Update UI
        document.querySelectorAll(".card p")[0].innerText = todayCount;
        document.querySelectorAll(".card p")[1].innerText = safe;
        document.querySelectorAll(".card p")[2].innerText = threats;

    } catch (error) {
        console.error("Dashboard error:", error);
    }
}

loadDashboard();