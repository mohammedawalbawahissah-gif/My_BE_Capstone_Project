document.addEventListener("DOMContentLoaded", function () {

    // Function to handle alerts fading out
    handleAlerts();

    // Function to update referral statuses with their respective classes
    updateReferralStatuses();

    // Function to handle the blinking of emergency-active cards
    handleEmergencyCards();

    // Function to update the live clock on the page
    startLiveClock();

});

// Function to fade out and remove alerts after 4 seconds
function handleAlerts() {
    document.querySelectorAll(".alert").forEach(alert => {
        setTimeout(() => {
            alert.style.transition = "opacity 0.6s";
            alert.style.opacity = "0";

            setTimeout(() => alert.remove(), 600);
        }, 4000);
    });
}

// Function to update the referral status based on text content
function updateReferralStatuses() {
    document.querySelectorAll(".referral-status").forEach(cell => {
        const text = cell.innerText.trim().toLowerCase();

        // Remove all status classes first
        cell.classList.remove(
            "pending",
            "accepted",
            "transit",
            "completed",
            "cancelled"
        );

        // Add the appropriate class based on the text
        if (text.includes("pending")) cell.classList.add("pending");
        else if (text.includes("accepted")) cell.classList.add("accepted");
        else if (text.includes("transit")) cell.classList.add("transit");
        else if (text.includes("completed")) cell.classList.add("completed");
        else if (text.includes("cancelled")) cell.classList.add("cancelled");
    });
}

// Function to handle blinking of emergency-active cards
function handleEmergencyCards() {
    document.querySelectorAll(".emergency-active").forEach(card => {
        setInterval(() => {
            card.classList.toggle("emergency-blink");
        }, 800);
    });
}

// Function to start the live clock
function startLiveClock() {
    const clock = document.getElementById("liveClock");

    if (clock) {
        function updateClock() {
            clock.innerText = new Date().toLocaleString();
        }

        setInterval(updateClock, 1000);
        updateClock();
    }
}

// Function to filter rows in a table based on input
function filterTable(inputId, tableId) {
    const input = document.getElementById(inputId);
    const table = document.getElementById(tableId);

    if (!input || !table) return;

    const filter = input.value.toLowerCase();
    const rows = table.getElementsByTagName("tr");

    for (let i = 1; i < rows.length; i++) {
        const text = rows[i].innerText.toLowerCase();
        rows[i].style.display = text.includes(filter) ? "" : "none";
    }
}

// Function to confirm actions with a custom message
function confirmAction(message = "Are you sure?") {
    return confirm(message);
}

// Function to display a toast notification
function showToast(message, type = "success") {
    const toast = document.createElement("div");

    toast.className = `alert alert-${type}`;
    toast.innerText = message;

    Object.assign(toast.style, {
        position: "fixed",
        bottom: "20px",
        right: "20px",
        zIndex: "9999",
        transition: "opacity 0.5s"
    });

    document.body.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = "0";

        setTimeout(() => toast.remove(), 500);
    }, 3000);
}