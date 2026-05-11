console.log("PROFILE JS LOADED");

const token = localStorage.getItem("token");

async function loadProfile() {

    try {
        const response = await fetch("http://127.0.0.1:8000/profile", {
            headers: {
                "Authorization": "Bearer " + token
            }
        });

        const data = await response.json();

        console.log("PROFILE DATA:", data);

        // Fill UI dynamically
        document.querySelector("h2").innerText = "👤 " + (data.username || "User");

        const profileCard = document.querySelector(".profile-card");

        profileCard.innerHTML = `
            <h2>👤 ${data.username}</h2>

            <p><strong>Email:</strong> ${data.email}</p>

            <hr>

            <p><strong>Total Scans:</strong> ${data.stats.total_scans}</p>
            <p><strong>Threats Detected:</strong> ${data.stats.phishing_found}</p>

            <hr>

            <p class="status safe">
                Account Status: Secure
            </p>
        `;

    } catch (error) {
        console.error("Profile error:", error);
    }
}

loadProfile();