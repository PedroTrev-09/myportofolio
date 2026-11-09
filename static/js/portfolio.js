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
    confirmDelete(title) {
        const dialog = document.getElementById("delete-confirmation");
        if (dialog.open) return Promise.resolve(false);
        dialog.querySelector("strong").textContent = title;
        dialog.returnValue = "";
        return new Promise(resolve => {
            dialog.querySelector("form").onsubmit = event => {
                event.preventDefault(); dialog.close("delete");
            };
            dialog.addEventListener("close", () => resolve(dialog.returnValue === "delete"), { once: true });
            dialog.showModal();
        });
    },
    clearFormErrors(form) {
        form.querySelectorAll("[data-api-error]").forEach(node => node.remove());
        form.querySelectorAll("[aria-invalid]").forEach(control => {
            control.removeAttribute("aria-invalid");
            const ids = (control.getAttribute("aria-describedby") || "").split(" ")
                .filter(id => id && !id.endsWith("-api-error"));
            if (ids.length) control.setAttribute("aria-describedby", ids.join(" "));
            else control.removeAttribute("aria-describedby");
        });
        const feedback = form.querySelector("[data-form-feedback]");
        if (feedback) { feedback.hidden = true; feedback.textContent = ""; }
    },
    showFormErrors(form, error) {
        PortfolioUI.clearFormErrors(form);
        let firstInvalid;
        for (const [name, messages] of Object.entries(error.fields || {})) {
            const control = form.elements.namedItem(name);
            if (!control || !control.closest) continue;
            const hint = document.createElement("p");
            hint.className = "form-error";
            hint.id = `${form.id}-${name}-api-error`;
            hint.dataset.apiError = "";
            hint.textContent = Array.isArray(messages) ? messages.join(" ") : String(messages);
            control.setAttribute("aria-invalid", "true");
            const ids = control.getAttribute("aria-describedby");
            control.setAttribute("aria-describedby", [ids, hint.id].filter(Boolean).join(" "));
            control.insertAdjacentElement("afterend", hint);
            firstInvalid ||= control;
        }
        const feedback = form.querySelector("[data-form-feedback]");
        if (feedback) {
            feedback.hidden = false;
            feedback.textContent = firstInvalid ? "Please check the highlighted fields." : error.message;
        }
        (firstInvalid || feedback)?.focus();
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
            const error = new Error(messages.join(" ") || `Request failed (HTTP ${response.status}).`);
            error.status = response.status;
            error.fields = response.status === 400 ? data : {};
            throw error;
        }
        return data;
    },
};
