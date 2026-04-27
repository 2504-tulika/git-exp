// ========================================
// AUTH.JS — Token management, session
// timeout, login/logout, route protection
// ========================================

const SESSION_TIMEOUT = 30 * 60 * 1000;
let sessionTimer = null;


// ========================================
// SAVE & GET USER DATA
// ========================================

function saveUserSession(token, email, name, role) {
    localStorage.setItem("token", token);
    localStorage.setItem("userEmail", email);
    localStorage.setItem("userName", name);
    localStorage.setItem("userRole", role);
    localStorage.setItem("loginTime", Date.now());
}

function getToken()     { return localStorage.getItem("token"); }
function getUserEmail() { return localStorage.getItem("userEmail"); }
function getUserName()  { return localStorage.getItem("userName"); }
function getUserRole()  { return localStorage.getItem("userRole"); }
function isLoggedIn()   { return getToken() !== null; }


// ========================================
// PATH HELPERS
// works correctly from any folder depth
// ========================================

function getBasePath() {
    const path = window.location.pathname;

    // pages/customer/ or pages/organizer/ — two levels deep
    if (path.includes("/pages/customer/") || path.includes("/pages/organizer/")) {
        return "../../";
    }

    // root level — login.html, register.html
    return "";
}

function getCustomerHome() {
    return getBasePath() + "pages/customer/home.html";
}

function getOrganizerDashboard() {
    return getBasePath() + "pages/organizer/dashboard.html";
}

function getLoginPage() {
    return getBasePath() + "login.html";
}


// ========================================
// LOGOUT
// ========================================

function logout() {
    localStorage.removeItem("token");
    localStorage.removeItem("userEmail");
    localStorage.removeItem("userName");
    localStorage.removeItem("userRole");
    localStorage.removeItem("loginTime");

    if (sessionTimer) {
        clearTimeout(sessionTimer);
        sessionTimer = null;
    }

    window.location.href = getLoginPage();
}


// ========================================
// SESSION TIMEOUT
// ========================================

function resetSessionTimer() {
    if (sessionTimer) clearTimeout(sessionTimer);

    sessionTimer = setTimeout(function () {
        alert("Your session has expired due to inactivity. Please login again.");
        logout();
    }, SESSION_TIMEOUT);
}

function startSessionWatcher() {
    ["mousemove", "keydown", "click", "scroll", "touchstart"].forEach(function (evt) {
        document.addEventListener(evt, resetSessionTimer, { passive: true });
    });
    resetSessionTimer();
}


// ========================================
// ROUTE PROTECTION
// ========================================

function requireAuth() {
    if (!isLoggedIn()) {
        window.location.href = getLoginPage();
        return false;
    }
    startSessionWatcher();
    return true;
}

function requireRole(role) {
    if (!requireAuth()) return false;

    if (getUserRole() !== role) {
        // wrong role — send to their correct page
        if (getUserRole() === "ORGANIZER") {
            window.location.href = getOrganizerDashboard();
        } else {
            window.location.href = getCustomerHome();
        }
        return false;
    }
    return true;
}

// call on login.html and register.html
// sends logged in users away to their dashboard
function redirectIfLoggedIn() {
    if (!isLoggedIn()) return;

    if (getUserRole() === "ORGANIZER") {
        window.location.href = getOrganizerDashboard();
    } else {
        window.location.href = getCustomerHome();
    }
}


// ========================================
// NAVBAR
// ========================================

function buildNavbar(activePage) {
    const role = getUserRole();
    const name = getUserName();

    let navLinks = "";

    if (role === "CUSTOMER") {
        navLinks = `
            <a href="home.html"
               class="${activePage === 'home' ? 'active' : ''}">
               Events
            </a>
            <a href="my-bookings.html"
               class="${activePage === 'bookings' ? 'active' : ''}">
               My Bookings
            </a>
        `;
    } else if (role === "ORGANIZER") {
        navLinks = `
            <a href="dashboard.html"
               class="${activePage === 'dashboard' ? 'active' : ''}">
               Dashboard
            </a>
            <a href="create-event.html"
               class="${activePage === 'create' ? 'active' : ''}">
               Create Event
            </a>
        `;
    }

    const navbarHTML = `
        <nav class="navbar">
            <div class="navbar-brand">Event<span>Hive</span></div>
            <div class="navbar-links">${navLinks}</div>
            <div class="navbar-user">
                <span>👋 ${name || "User"}</span>
                <button class="btn btn-outline btn-sm"
                    onclick="logout()">Logout</button>
            </div>
        </nav>
    `;

    // safely inject navbar
    if (document.body) {
        document.body.insertAdjacentHTML("afterbegin", navbarHTML);
    } else {
        document.addEventListener("DOMContentLoaded", function () {
            document.body.insertAdjacentHTML("afterbegin", navbarHTML);
        });
    }
}