const { escapeHtml, safeImage, write: writeProject } = PortfolioUI;
const loadingState = document.getElementById("loading");
const errorState = document.getElementById("error");
const emptyState = document.getElementById("empty");
const gridContainer = document.getElementById("grid");
const searchInput = document.getElementById("search-input");
const projectForm = document.getElementById("project-form");
const projectModal = document.getElementById("add-project-modal");
let projectsAbortController;
let searchDebounceTimer;
let projects = [];
let editingProjectId = null;

function projectEndpoint(pattern, id) {
    return pattern.replace("00000000-0000-0000-0000-000000000000", encodeURIComponent(id));
}

function displayPageSection({ showLoading = false, showError = false, showEmpty = false, showGrid = false }) {
    loadingState.classList.toggle("hide", !showLoading);
    errorState.classList.toggle("hide", !showError);
    emptyState.classList.toggle("hide", !showEmpty);
    gridContainer.classList.toggle("hide", !showGrid);
    gridContainer.setAttribute("aria-busy", String(showLoading));
}

function buildProjectCardElement(project) {
    const article = document.createElement("article");
    article.className = "project-card";
    article.dataset.category = project.category;
    const image = safeImage(project.image_url);
    const tags = project.tags.split(",").map(tag => tag.trim()).filter(Boolean)
        .map(tag => `<li>${escapeHtml(tag)}</li>`).join("");
    const star = IS_AUTHENTICATED
        ? `<button type="button" class="button-star${project.is_starred ? " is-starred" : ""}"
            data-action="star" data-id="${escapeHtml(project.id)}" aria-pressed="${project.is_starred}"
            title="${escapeHtml(project.starred_by_names || "Be the first to star this project")}">
            <span aria-hidden="true">★</span> ${project.is_starred ? "Unstar" : "Star"}
            <span class="star-count">${escapeHtml(project.star_count)}</span></button>`
        : `<a class="button-star" href="${escapeHtml(LOGIN_URL)}?next=${encodeURIComponent(location.pathname)}">Login to star <span class="star-count">${escapeHtml(project.star_count)}</span></a>`;
    const manage = IS_SUPERUSER
        ? `<button type="button" class="button button-secondary" data-action="edit" data-id="${escapeHtml(project.id)}">Edit</button>
           <button type="button" class="btn-danger-ghost" data-action="delete" data-id="${escapeHtml(project.id)}">Delete</button>` : "";
    article.innerHTML = `${image ? `<img src="${escapeHtml(image)}" alt="${escapeHtml(project.title)}" class="project-img" loading="lazy">` : ""}
        <div class="project-body"><h3><button type="button" class="stretched-link project-title-button"
            data-action="detail" data-id="${escapeHtml(project.id)}" aria-haspopup="dialog">${escapeHtml(project.title)}</button></h3>
        <p>${escapeHtml(project.short_description)}</p><ul class="tag-list">${tags}</ul>
        <div class="project-card-actions"><div class="project-actions">${star}${manage}</div></div></div>`;
    return article;
}

function applyCategoryFilter() {
    if (loadingState.classList.contains("hide") && errorState.classList.contains("hide")) {
        const category = document.querySelector("input[name='project-filter']:checked")?.value || "all";
        const visible = projects.filter(project => category === "all" || project.category.toLowerCase() === category);
        gridContainer.replaceChildren(...visible.map(buildProjectCardElement));
        displayPageSection({ showGrid: visible.length > 0, showEmpty: visible.length === 0 });
    }
}

async function fetchProjects(searchQuery = searchInput.value.trim()) {
    projectsAbortController?.abort();
    const controller = new AbortController();
    projectsAbortController = controller;
    displayPageSection({ showLoading: true });
    try {
        const url = new URL(BASE_PROJECTS_ENDPOINT, location.origin);
        if (searchQuery) url.searchParams.set("title", searchQuery);
        const response = await fetch(url, { headers: { Accept: "application/json" }, signal: controller.signal });
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        const data = await response.json();
        if (controller.signal.aborted) return;
        projects = data;
        displayPageSection({ showGrid: projects.length > 0, showEmpty: projects.length === 0 });
        applyCategoryFilter();
    } catch (error) {
        if (error.name !== "AbortError") displayPageSection({ showError: true });
    }
}

function prepareProjectForm(project = null) {
    editingProjectId = project?.id || null;
    projectForm.reset();
    for (const name of ["title", "category", "image_url", "short_description", "full_description", "tags"]) {
        if (project) projectForm.elements[name].value = project[name];
    }
    document.getElementById("add-project-modal-title").textContent = project ? "Edit Project" : "Add Project";
    projectForm.querySelector("button[type=submit]").textContent = project ? "Save changes" : "Add Project";
}

gridContainer.addEventListener("click", async event => {
    const button = event.target.closest("button[data-action]");
    if (!button || button.disabled) return;
    const project = projects.find(item => item.id === button.dataset.id);
    if (!project) return;
    const action = button.dataset.action;
    if (action === "detail") {
        const dialog = document.getElementById("project-detail-modal");
        document.getElementById("project-detail-title").textContent = project.title;
        document.getElementById("project-detail-description").textContent = project.full_description;
        const image = document.getElementById("project-detail-image");
        const src = safeImage(project.image_url);
        image.hidden = !src;
        image.removeAttribute("src");
        if (src) image.src = src;
        image.alt = project.title;
        dialog.showModal();
        return;
    }
    if (action === "edit") { prepareProjectForm(project); projectModal.showModal(); return; }
    // Disable before confirmation too: a double click cannot start a second toggle/delete.
    button.disabled = true;
    try {
        if (action === "delete" && !await PortfolioUI.confirmDelete(project.title)) return;
        const pattern = action === "star" ? STAR_PROJECT_ENDPOINT : DETAIL_PROJECT_ENDPOINT;
        await writeProject(projectEndpoint(pattern, project.id), action === "star" ? "POST" : "DELETE");
        showToast("Success", action === "star" ? "Star updated." : "Project deleted.", "success");
        await fetchProjects();
    } catch (error) { showToast("Request failed", error.message, "error"); }
    finally { button.disabled = false; }
});

if (projectForm) {
    document.querySelector("[data-new-project]").addEventListener("click", () => prepareProjectForm());
    projectForm.addEventListener("submit", async event => {
        event.preventDefault();
        const button = projectForm.querySelector("button[type=submit]");
        if (button.disabled) return;
        button.disabled = true;
        try {
            const payload = Object.fromEntries(["title", "category", "image_url", "short_description", "full_description", "tags"]
                .map(name => [name, projectForm.elements[name].value]));
            await writeProject(editingProjectId ? projectEndpoint(DETAIL_PROJECT_ENDPOINT, editingProjectId) : BASE_PROJECTS_ENDPOINT,
                editingProjectId ? "PATCH" : "POST", payload);
            projectModal.close();
            showToast("Success", editingProjectId ? "Project updated." : "Project created.", "success");
            projectForm.reset();
            await fetchProjects();
        } catch (error) { showToast("Could not save project", error.message, "error"); }
        finally { button.disabled = false; }
    });
}

searchInput.addEventListener("input", () => {
    clearTimeout(searchDebounceTimer);
    searchDebounceTimer = setTimeout(() => fetchProjects(), 300);
});
document.getElementById("project-search-form").addEventListener("submit", event => {
    event.preventDefault(); clearTimeout(searchDebounceTimer); fetchProjects();
});
document.querySelectorAll("input[name='project-filter']").forEach(input => input.addEventListener("change", applyCategoryFilter));
document.getElementById("project-retry").addEventListener("click", () => fetchProjects());
fetchProjects();
