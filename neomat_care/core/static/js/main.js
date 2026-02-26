/* ========================================
   GLOBAL SYSTEM JAVASCRIPT
   Neonatal Emergency Referral System
======================================== */

/* =============================
   AUTO DISMISS ALERTS
============================= */
document.addEventListener("DOMContentLoaded", function () {

    const alerts = document.querySelectorAll(".alert");

    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.transition = "opacity 0.6s";
            alert.style.opacity = "0";
            setTimeout(() => alert.remove(), 600);
        }, 4000);
    });

});


/* =============================
   CONFIRM DELETE / ACTION
============================= */
function confirmAction(message="Are you sure?") {
    return confirm(message);
}


/* =============================
   REFERRAL STATUS COLOR AUTO TAG
============================= */
document.addEventListener("DOMContentLoaded", function () {

    const statusCells = document.querySelectorAll(".referral-status");

    statusCells.forEach(cell => {

        const text = cell.innerText.trim().toLowerCase();

        cell.classList.remove("pending","accepted","transit","completed","cancelled");

        if (text.includes("pending")) cell.classList.add("pending");
        else if (text.includes("accepted")) cell.classList.add("accepted");
        else if (text.includes("transit")) cell.classList.add("transit");
        else if (text.includes("completed")) cell.classList.add("completed");
        else if (text.includes("cancelled")) cell.classList.add("cancelled");

    });

});


/* =============================
   EMERGENCY FLASH EFFECT
============================= */
document.addEventListener("DOMContentLoaded", function () {

    const emergencyCards = document.querySelectorAll(".emergency-active");

    emergencyCards.forEach(card => {
        setInterval(() => {
            card.classList.toggle("emergency-blink");
        }, 800);
    });

});


/* =============================
   PATIENT SEARCH FILTER
============================= */
function filterTable(inputId, tableId) {

    const input = document.getElementById(inputId);
    const filter = input.value.toLowerCase();
    const table = document.getElementById(tableId);
    const rows = table.getElementsByTagName("tr");

    for (let i = 1; i < rows.length; i++) {
        const text = rows[i].innerText.toLowerCase();
        rows[i].style.display = text.includes(filter) ? "" : "none";
    }
}


/* =============================
   LIVE CLOCK (Dashboard)
============================= */
document.addEventListener("DOMContentLoaded", function () {

    const clock = document.getElementById("liveClock");

    if (!clock) return;

    function updateClock() {
        const now = new Date();
        clock.innerText = now.toLocaleString();
    }

    setInterval(updateClock, 1000);
    updateClock();

});


/* =============================
   SUCCESS TOAST MESSAGE
============================= */
function showToast(message, type="success") {

    const toast = document.createElement("div");
    toast.className = "alert alert-" + type;
    toast.innerText = message;

    document.body.appendChild(toast);

    toast.style.position = "fixed";
    toast.style.bottom = "20px";
    toast.style.right = "20px";
    toast.style.zIndex = "9999";

    setTimeout(() => {
        toast.style.opacity = "0";
        setTimeout(() => toast.remove(), 500);
    }, 3000);
}