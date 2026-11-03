// Native modal dialogs provide Escape, focus trapping and focus restoration.
document.addEventListener("click", event => {
    const close = event.target.closest("[data-dialog-close]");
    if (close) { close.closest("dialog")?.close(); return; }
    const opener = event.target.closest("[data-dialog-open]");
    if (opener) {
        const dialog = document.getElementById(opener.dataset.dialogOpen);
        if (dialog && !dialog.open) dialog.showModal();
        return;
    }
    const remove = event.target.closest("[data-delete-url]");
    if (remove) {
        const dialog = document.getElementById("delete-confirmation");
        dialog.querySelector("strong").textContent = remove.dataset.deleteTitle;
        dialog.querySelector("form").action = remove.dataset.deleteUrl;
        dialog.showModal();
    }
});
