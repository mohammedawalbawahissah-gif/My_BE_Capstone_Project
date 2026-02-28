document.addEventListener("DOMContentLoaded", () => {

    // Log message when the system is loaded
    console.log("Neomat Care System Loaded");

    // Highlight the active navigation link
    highlightActiveNavLink();

    // Add confirmation for emergency referral action
    addEmergencyReferralConfirmation();
});

// Function to highlight the active navigation link
function highlightActiveNavLink() {
    document.querySelectorAll("nav a").forEach(link => {
        if (link.href === window.location.href) {
            link.classList.add("active-nav-link");
        }
    });
}

// Function to add confirmation before sending emergency referral
function addEmergencyReferralConfirmation() {
    document.querySelectorAll(".emergency-confirm").forEach(btn => {
        btn.addEventListener("click", function (e) {
            if (!confirm("Send emergency referral?")) {
                e.preventDefault();
            }
        });
    });
}