const { escapeHtml, write: writeExperience } = PortfolioUI;
const loadingState = document.getElementById("experience-loading");
const errorState = document.getElementById("experience-error");
const emptyState = document.getElementById("experience-empty");
const listContainer = document.getElementById("experience-list");
const countState = document.getElementById("experience-count");
const searchInput = document.getElementById("experience-search-input");
const experienceForm = document.getElementById("experience-form");
const experienceModal = document.getElementById("add-experience-modal");
let experiences = [];
let experienceAbortController;
let experienceSearchDebounceTimer;
let editingExperienceId = null;

function experienceEndpoint(id) {
    return DETAIL_EXPERIENCE_ENDPOINT.replace("00000000-0000-0000-0000-000000000000", encodeURIComponent(id));
}

function displayExperienceSection({ showLoading = false, showError = false, showEmpty = false, showList = false }) {
    loadingState.classList.toggle("hide", !showLoading);
    errorState.classList.toggle("hide", !showError);
    emptyState.classList.toggle("hide", !showEmpty);
    listContainer.classList.toggle("hide", !showList);
    listContainer.setAttribute("aria-busy", String(showLoading));
}

function buildExperienceElement(experience, expandedIds) {
    const details = document.createElement("details");
    details.className = "timeline-item";
    details.dataset.id = experience.id;
    details.open = expandedIds.has(experience.id);
    const manage = IS_SUPERUSER || IS_EDITOR
        ? `<div class="experience-actions"><button type="button" class="button button-secondary"
            data-action="edit" data-id="${escapeHtml(experience.id)}">Edit</button>
            ${IS_SUPERUSER ? `<button type="button" class="btn-danger-ghost" data-action="delete" data-id="${escapeHtml(experience.id)}">Delete</button>` : ""}</div>` : "";
    details.innerHTML = `<summary><span class="timeline-role">${escapeHtml(experience.title)}</span>
        <span class="timeline-period">${escapeHtml(experience.started_at.slice(0, 4))} &mdash;
        ${escapeHtml(experience.is_ongoing ? "Present" : experience.ended_at.slice(0, 4))}</span>
        <span class="chevron" aria-hidden="true">⌄</span></summary>
        <div class="timeline-body"><p class="experience-category">${escapeHtml(experience.category_display)}</p>
        <p>${escapeHtml(experience.location)}</p><p class="timeline-description">${escapeHtml(experience.description)}</p>${manage}</div>`;
    return details;
}

async function fetchExperiences() {
    experienceAbortController?.abort();
    const controller = new AbortController();
    experienceAbortController = controller;
    const expandedIds = new Set([...listContainer.querySelectorAll("details[open]")].map(item => item.dataset.id));
    const url = new URL(BASE_EXPERIENCES_ENDPOINT, location.origin);
    const category = document.querySelector("input[name='experience-filter']:checked")?.value || "all";
    if (searchInput.value.trim()) url.searchParams.set("title", searchInput.value.trim());
    if (category !== "all") url.searchParams.set("category", category);
    displayExperienceSection({ showLoading: true });
    countState.textContent = "";
    try {
        const response = await fetch(url, { headers: { Accept: "application/json" }, signal: controller.signal });
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        const data = await response.json();
        if (controller.signal.aborted) return;
        experiences = data;
        listContainer.replaceChildren(...experiences.map(item => buildExperienceElement(item, expandedIds)));
        countState.textContent = `${experiences.length} experience${experiences.length === 1 ? "" : "s"} found`;
        displayExperienceSection({ showList: experiences.length > 0, showEmpty: experiences.length === 0 });
    } catch (error) {
        if (error.name !== "AbortError") displayExperienceSection({ showError: true });
    }
}

function prepareExperienceForm(experience = null) {
    editingExperienceId = experience?.id || null;
    experienceForm.reset();
    for (const name of ["title", "category", "location", "started_at", "ended_at", "description"]) {
        if (experience) experienceForm.elements[name].value = experience[name] ?? "";
    }
    document.getElementById("add-experience-modal-title").textContent = experience ? "Edit Experience" : "Add Experience";
    experienceForm.querySelector("button[type=submit]").textContent = experience ? "Save changes" : "Add Experience";
}

listContainer.addEventListener("click", async event => {
    const button = event.target.closest("button[data-action]");
    if (!button || button.disabled) return;
    const experience = experiences.find(item => item.id === button.dataset.id);
    if (!experience) return;
    if (button.dataset.action === "edit") {
        prepareExperienceForm(experience); experienceModal.showModal(); return;
    }
    button.disabled = true;
    try {
        if (!await PortfolioUI.confirmDelete(experience.title)) return;
        await writeExperience(experienceEndpoint(experience.id), "DELETE");
        showToast("Success", "Experience deleted.", "success");
        await fetchExperiences();
    } catch (error) { showToast("Could not delete experience", error.message, "error"); }
    finally { button.disabled = false; }
});

if (experienceForm) {
    document.querySelector("[data-new-experience]")?.addEventListener("click", () => prepareExperienceForm());
    experienceForm.addEventListener("submit", async event => {
        event.preventDefault();
        const button = experienceForm.querySelector("button[type=submit]");
        if (button.disabled) return;
        button.disabled = true;
        try {
            const payload = Object.fromEntries(["title", "category", "location", "started_at", "ended_at", "description"]
                .map(name => [name, experienceForm.elements[name].value]));
            payload.ended_at ||= null;
            await writeExperience(editingExperienceId ? experienceEndpoint(editingExperienceId) : BASE_EXPERIENCES_ENDPOINT,
                editingExperienceId ? "PATCH" : "POST", payload);
            experienceModal.close();
            showToast("Success", editingExperienceId ? "Experience updated." : "Experience created.", "success");
            experienceForm.reset();
            await fetchExperiences();
        } catch (error) { showToast("Could not save experience", error.message, "error"); }
        finally { button.disabled = false; }
    });
}
searchInput.addEventListener("input", () => {
    clearTimeout(experienceSearchDebounceTimer);
    experienceSearchDebounceTimer = setTimeout(fetchExperiences, 300);
});
document.getElementById("experience-search-form").addEventListener("submit", event => {
    event.preventDefault(); clearTimeout(experienceSearchDebounceTimer); fetchExperiences();
});
document.querySelectorAll("input[name='experience-filter']").forEach(input => input.addEventListener("change", () => {
    clearTimeout(experienceSearchDebounceTimer); fetchExperiences();
}));
document.getElementById("experience-retry").addEventListener("click", fetchExperiences);
fetchExperiences();
