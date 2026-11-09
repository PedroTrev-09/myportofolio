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
const pendingExperienceIds = new Set();
const savingControls = new Map();

function setExperienceSaving(saving) {
    experienceForm.setAttribute("aria-busy", String(saving));
    if (saving) {
        experienceModal.querySelectorAll("input, select, textarea, button").forEach(control => {
            savingControls.set(control, control.disabled);
            control.disabled = true;
        });
    } else {
        savingControls.forEach((disabled, control) => { control.disabled = disabled; });
        savingControls.clear();
    }
    experienceForm.querySelector("button[type=submit]").textContent = saving ? "Saving…"
        : editingExperienceId ? "Save changes" : "Add Experience";
}

experienceModal?.addEventListener("cancel", event => {
    if (experienceForm.getAttribute("aria-busy") === "true") event.preventDefault();
});

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
    const star = IS_AUTHENTICATED
        ? `<button type="button" class="button-star${experience.is_starred ? " is-starred" : ""}"
            data-action="star" data-id="${escapeHtml(experience.id)}" aria-pressed="${experience.is_starred}"
            title="${escapeHtml(experience.starred_by_names || "Be the first to star this experience")}">
            <span aria-hidden="true">★</span> ${experience.is_starred ? "Unstar" : "Star"}
            <span class="star-count">${escapeHtml(experience.star_count)}</span></button>`
        : `<a class="button-star" href="${escapeHtml(LOGIN_URL)}?next=${encodeURIComponent(location.pathname)}">Login to star <span class="star-count">${escapeHtml(experience.star_count)}</span></a>`;
    const manage = IS_SUPERUSER || IS_EDITOR
        ? `<button type="button" class="button button-secondary"
            data-action="edit" data-id="${escapeHtml(experience.id)}">Edit</button>
            ${IS_SUPERUSER ? `<button type="button" class="btn-danger-ghost" data-action="delete" data-id="${escapeHtml(experience.id)}">Delete</button>` : ""}` : "";
    details.innerHTML = `<summary><span class="timeline-role">${escapeHtml(experience.title)}</span>
        <span class="timeline-period">${escapeHtml(experience.started_at.slice(0, 4))} &mdash;
        ${escapeHtml(experience.is_ongoing ? "Present" : experience.ended_at.slice(0, 4))}</span>
        <span class="chevron" aria-hidden="true">⌄</span></summary>
        <div class="timeline-body"><p class="experience-category">${escapeHtml(experience.category_display)}</p>
        <p>${escapeHtml(experience.location)}</p><p class="timeline-description">${escapeHtml(experience.description)}</p><div class="experience-actions">${star}${manage}</div></div>`;
    if (pendingExperienceIds.has(experience.id)) {
        details.querySelectorAll("button[data-action]").forEach(button => { button.disabled = true; });
    }
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
    // Bookmarkable state: retain search/category without a document navigation.
    const pageUrl = new URL(location.href);
    for (const name of ["title", "category"]) {
        if (url.searchParams.has(name)) pageUrl.searchParams.set(name, url.searchParams.get(name));
        else pageUrl.searchParams.delete(name);
    }
    history.replaceState(null, "", pageUrl);
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
    PortfolioUI.clearFormErrors(experienceForm);
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
    if (!experience || pendingExperienceIds.has(experience.id)) return;
    if (button.dataset.action === "edit") {
        prepareExperienceForm(experience); experienceModal.showModal(); return;
    }
    const action = button.dataset.action;
    if (!["star", "delete"].includes(action)) return;
    pendingExperienceIds.add(experience.id);
    button.disabled = true;
    try {
        const isStar = button.dataset.action === "star";
        if (!isStar && !await PortfolioUI.confirmDelete(experience.title)) return;
        const url = isStar ? STAR_EXPERIENCE_ENDPOINT.replace("00000000-0000-0000-0000-000000000000", encodeURIComponent(experience.id)) : experienceEndpoint(experience.id);
        await writeExperience(url, isStar ? "POST" : "DELETE");
        showToast("Success", isStar ? "Star updated." : "Experience deleted.", "success");
        await fetchExperiences();
    } catch (error) { showToast("Request failed", error.message, "error"); }
    finally {
        pendingExperienceIds.delete(experience.id);
        button.disabled = false;
        listContainer.querySelectorAll("button[data-action]").forEach(control => {
            if (control.dataset.id === experience.id) control.disabled = false;
        });
        if (document.activeElement === document.body) {
            const replacement = [...listContainer.querySelectorAll("button[data-action]")]
                .find(control => control.dataset.id === experience.id && control.dataset.action === action);
            (replacement || searchInput).focus({ preventScroll: true });
        }
    }
});

if (experienceForm) {
    document.querySelector("[data-new-experience]")?.addEventListener("click", () => prepareExperienceForm());
    experienceForm.addEventListener("submit", async event => {
        event.preventDefault();
        const button = experienceForm.querySelector("button[type=submit]");
        if (button.disabled) return;
        PortfolioUI.clearFormErrors(experienceForm);
        const payload = Object.fromEntries(["title", "category", "location", "started_at", "ended_at", "description"]
                .map(name => [name, experienceForm.elements[name].value]));
        payload.ended_at ||= null;
        setExperienceSaving(true);
        try {
            await writeExperience(editingExperienceId ? experienceEndpoint(editingExperienceId) : BASE_EXPERIENCES_ENDPOINT,
                editingExperienceId ? "PATCH" : "POST", payload);
            experienceModal.close();
            showToast("Success", editingExperienceId ? "Experience updated." : "Experience created.", "success");
            experienceForm.reset();
            await fetchExperiences();
        } catch (error) {
            setExperienceSaving(false);
            PortfolioUI.showFormErrors(experienceForm, error);
            showToast("Could not save experience", error.message, "error");
        } finally { setExperienceSaving(false); }
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
document.getElementById("experience-clear-filters").addEventListener("click", () => {
    clearTimeout(experienceSearchDebounceTimer);
    searchInput.value = "";
    document.getElementById("experience-filter-all").checked = true;
    fetchExperiences();
    searchInput.focus();
});
document.getElementById("experience-retry").addEventListener("click", fetchExperiences);
fetchExperiences();
