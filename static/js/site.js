const themeToggle = document.getElementById("theme-toggle");
const navToggle = document.getElementById("nav-toggle");
try { themeToggle.checked = localStorage.getItem("portfolio-theme") === "dark"; } catch { /* Storage may be unavailable. */ }
themeToggle.addEventListener("change", () => {
    try { localStorage.setItem("portfolio-theme", themeToggle.checked ? "dark" : "light"); } catch { /* Keep the switch usable. */ }
});
navToggle.addEventListener("change", () => navToggle.setAttribute("aria-expanded", String(navToggle.checked)));
document.addEventListener("keydown", event => {
    if (event.key === "Escape") { navToggle.checked = false; navToggle.setAttribute("aria-expanded", "false"); }
});
document.addEventListener("click", event => {
    if (!event.target.closest(".site-header, #nav-toggle")) {
        navToggle.checked = false; navToggle.setAttribute("aria-expanded", "false");
    }
});
document.querySelectorAll(".site-nav a").forEach(link => link.addEventListener("click", () => {
    navToggle.checked = false; navToggle.setAttribute("aria-expanded", "false");
}));
