// UTILS.JS — Shared helper functions

// DATE & TIME FORMATTING

// converts "2026-12-01T10:00:00" to "01 Dec 2026, 10:00 AM"
function formatDateTime(dateString) {
    if (!dateString) return "N/A";

    const date = new Date(dateString);
    const options = {
        day: "2-digit",
        month: "short",
        year: "numeric",
        hour: "2-digit",
        minute: "2-digit",
        hour12: true
    };
    return date.toLocaleString("en-IN", options);
}

// returns just the date part — "01 Dec 2026"
function formatDate(dateString) {
    if (!dateString) return "N/A";

    const date = new Date(dateString);
    return date.toLocaleDateString("en-IN", {
        day: "2-digit",
        month: "short",
        year: "numeric"
    });
}

// returns just the time — "10:00 AM"
function formatTime(dateString) {
    if (!dateString) return "N/A";

    const date = new Date(dateString);
    return date.toLocaleTimeString("en-IN", {
        hour: "2-digit",
        minute: "2-digit",
        hour12: true
    });
}

// checks if an event date is in the past
function isPastEvent(dateString) {
    return new Date(dateString) < new Date();
}

// converts datetime-local input value to ISO format for API
// input gives "2026-12-01T10:00" — API needs "2026-12-01T10:00:00"
function toISOFormat(datetimeLocalValue) {
    if (!datetimeLocalValue) return null;
    return datetimeLocalValue + ":00";
}

// converts ISO date to datetime-local input format
// API gives "2026-12-01T10:00:00" — input needs "2026-12-01T10:00"
function toDatetimeLocal(isoString) {
    if (!isoString) return "";
    return isoString.substring(0, 16);
}


// CURRENCY FORMATTING

// formats 999 to "₹999.00"
function formatCurrency(amount) {
    if (amount === null || amount === undefined) return "₹0.00";
    return "₹" + parseFloat(amount).toFixed(2);
}


// ALERT / MESSAGE DISPLAY

// shows an alert box by its element id
// type = "error" | "success" | "info"
function showAlert(elementId, message, type = "error") {
    const alertBox = document.getElementById(elementId);
    if (!alertBox) return;

    alertBox.className = "alert alert-" + type;
    alertBox.textContent = message;
    alertBox.style.display = "block";

    // auto hide after 5 seconds
    setTimeout(function () {
        hideAlert(elementId);
    }, 5000);
}

function hideAlert(elementId) {
    const alertBox = document.getElementById(elementId);
    if (alertBox) {
        alertBox.style.display = "none";
    }
}


// LOADER SHOW / HIDE

function showLoader(elementId) {
    const loader = document.getElementById(elementId);
    if (loader) loader.style.display = "block";
}

function hideLoader(elementId) {
    const loader = document.getElementById(elementId);
    if (loader) loader.style.display = "none";
}


// BUTTON LOADING STATE

// disables button and shows loading text while API call runs
function setButtonLoading(buttonId, loadingText = "Please wait...") {
    const btn = document.getElementById(buttonId);
    if (!btn) return;
    btn.disabled = true;
    btn.dataset.originalText = btn.textContent;
    btn.textContent = loadingText;
}

// restores button back to normal after API call
function resetButton(buttonId) {
    const btn = document.getElementById(buttonId);
    if (!btn) return;
    btn.disabled = false;
    btn.textContent = btn.dataset.originalText || "Submit";
}


// STATUS BADGE

// returns the HTML for a colored status badge
function getBadgeHTML(status) {
    const map = {
        "ACTIVE":               "badge-active",
        "CANCELLED":            "badge-cancelled",
        "CONFIRMED":            "badge-confirmed",
        "CANCELLED_BY_ORGANIZER": "badge-cancelled-organizer"
    };

    const cssClass = map[status] || "badge-active";
    const label = status.replace(/_/g, " ");
    return `<span class="badge ${cssClass}">${label}</span>`;
}


// URL PARAMS

// gets a query param from URL
// e.g. getParam("id") from "event-details.html?id=3" returns "3"
function getParam(name) {
    const params = new URLSearchParams(window.location.search);
    return params.get(name);
}


// FORM VALIDATION HELPERS

// checks password against SRS rules:
// 8-12 chars, at least 1 uppercase, 1 special character
function validatePassword(password) {
    const regex = /^(?=.*[A-Z])(?=.*[@#$%^&+=!])(?=\S+$).{8,12}$/;
    return regex.test(password);
}

// returns strength level of password — "weak" | "medium" | "strong"
function getPasswordStrength(password) {
    if (password.length < 6) return "weak";

    let score = 0;
    if (password.length >= 8) score++;
    if (/[A-Z]/.test(password)) score++;
    if (/[0-9]/.test(password)) score++;
    if (/[@#$%^&+=!]/.test(password)) score++;

    if (score <= 2) return "weak";
    if (score === 3) return "medium";
    return "strong";
}

// checks if a string is a valid email
function validateEmail(email) {
    const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return regex.test(email);
}


// EMPTY STATE HTML

// returns a nice empty state block when no data found
function getEmptyStateHTML(title, message, buttonText = null, buttonOnclick = null) {
    const buttonHTML = buttonText
        ? `<button class="btn btn-primary" onclick="${buttonOnclick}">${buttonText}</button>`
        : "";

    return `
        <div class="empty-state">
            <h3>${title}</h3>
            <p>${message}</p>
            ${buttonHTML}
        </div>
    `;
}