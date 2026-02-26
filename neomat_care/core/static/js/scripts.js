document.addEventListener("DOMContentLoaded", () => {

    console.log("Neomat Care System Loaded");

    // highlight current page
    const links = document.querySelectorAll("nav a");
    links.forEach(link => {
        if (link.href === window.location.href) {
            link.style.color = "#38bdf8";
            link.style.fontWeight = "bold";
        }
    });

    // confirm emergency referral
    const emergencyBtns = document.querySelectorAll(".btn-danger");

    emergencyBtns.forEach(btn => {
        btn.addEventListener("click", e => {
            if (!confirm("Send emergency referral?")) {
                e.preventDefault();
            }
        });
    });
});

