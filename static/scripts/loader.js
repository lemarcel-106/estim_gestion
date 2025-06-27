function showSpinner() {
    if (document.getElementById("admin-spinner")) return;
    const spinner = document.createElement("div");
    spinner.id = "admin-spinner";
    spinner.innerHTML = `
        <div class="spinner-overlay">
            <div class="spinner"></div>
        </div>
    `;
    document.body.appendChild(spinner);
}

function hideSpinner() {
    const spinner = document.getElementById("admin-spinner");
    if (spinner) spinner.remove();
}

document.addEventListener("DOMContentLoaded", function () {
    showSpinner();
});

window.addEventListener("load", function () {
    hideSpinner();
});

document.addEventListener("submit", function (e) {
    if (e.target.tagName === "FORM") {
        showSpinner();
    }
}, true);


// Si l'utilisateur quitte la page (autre onglet, réduit la fenêtre, etc.)
document.addEventListener("visibilitychange", () => {
    if (document.hidden) {
        hideSpinner();
    }
});


