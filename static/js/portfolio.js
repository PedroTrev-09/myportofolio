// Shared helpers for portfolio AJAX pages. Render model text as text or escape it.
window.PortfolioUI = {
    escapeHtml(value) {
        return String(value ?? "").replaceAll("&", "&amp;").replaceAll("<", "&lt;")
            .replaceAll(">", "&gt;").replaceAll('"', "&quot;").replaceAll("'", "&#39;");
    },
    getCookie(name) {
        const prefix = `${name}=`;
        const cookie = document.cookie.split(";").map(value => value.trim())
            .find(value => value.startsWith(prefix));
        return cookie ? decodeURIComponent(cookie.slice(prefix.length)) : "";
    },
    safeImage(value) {
        try {
            const url = new URL(value, location.origin);
            return ["http:", "https:"].includes(url.protocol) ? url.href : "";
        } catch { return ""; }
    },
    async write(url, method, payload) {
        const response = await fetch(url, {
            method,
            headers: { Accept: "application/json", "Content-Type": "application/json",
                "X-CSRFToken": PortfolioUI.getCookie("csrftoken") },
            body: payload === undefined ? undefined : JSON.stringify(payload),
        });
        if (response.status === 204) return null;
        const data = await response.json().catch(() => ({}));
        if (!response.ok) {
            const messages = Object.values(data).flat().filter(value => typeof value === "string");
            throw new Error(messages.join(" ") || `Request failed (HTTP ${response.status}).`);
        }
        return data;
    },
};
