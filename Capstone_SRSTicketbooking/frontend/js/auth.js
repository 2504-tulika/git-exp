// AUTH.JS — Token management, session
// timeout, login/logout, route protection

// how long before we log the user out
// 30 minutes in milliseconds (as per SRS)
const SESSION_TIMEOUT = 30 * 60 * 1000;

// this will hold the timeout timer reference
let sessionTimer = null;


// SAVE & GET USER DATA FROM localStorage

// called after successful login
function saveUserSession(token, email, name, role) {
    localStorage.setItem("token", token);
    localStorage.setItem("userEmail", email);
    localStorage.setItem("userName", name);
    localStorage.setItem("userRole", role);
    localStorage.setItem("loginTime", Date.now());
}

function getToken() {
    return localStorage.getItem("token");
}

function getUserEmail() {
    return localStorage.getItem("userEmail");
}

function getUserName() {
    return localStorage.getItem("userName");
}

function getUserRole() {
    return localStorage.getItem("userRole");
}

function isLoggedIn() {
    return getToken() !== null;
}


// LOGOUT

function logout() {
    // clear everything from localStorage
    localStorage.removeItem("token");
    localStorage.removeItem("userEmail");
    localStorage.removeItem("userName");
    localStorage.removeItem("userRole");
    localStorage.removeItem("loginTime");

    // clear the session timer
    if (sessionTimer) {
        clearTimeout(sessionTimer);
        sessionTimer = null;
    }

    // find login.html relative to current page location
    const path = window.location.pathname;

    if (path.includes("/pages/customer/") || path.includes("/pages/organizer/")) {
        // two levels deep — pages/customer/ or pages/organizer/
        window.location.href = "../../login.html";
    } else if (path.includes("/pages/")) {
        // one level deep — pages/
        window.location.href = "../login.html";
    } else {
        // root level — login.html, register.html
        window.location.href = "login.html";
    }
}


// SESSION TIMEOUT — 30 min inactivity

// reset the timer every time user does something
function resetSessionTimer() {
    if (sessionTimer) {
        clearTimeout(sessionTimer);
    }

    sessionTimer = setTimeout(function () {
        alert("Your session has expired due to inactivity. Please login again.");
        logout();
    }, SESSION_TIMEOUT);
}

// attach listeners to detect user activity
function startSessionWatcher() {
    const events = ["mousemove", "keydown", "click", "scroll", "touchstart"];

    events.forEach(function (event) {
        document.addEventListener(event, resetSessionTimer, { passive: true });
    });

    // start the first timer
    resetSessionTimer();
}


// ROUTE PROTECTION
// call this at the top of every protected page

// for pages that need login — redirects to login if not logged in
function requireAuth() {
    if (!isLoggedIn()) {
        const path = window.location.pathname;

        if (path.includes("/pages/customer/") || path.includes("/pages/organizer/")) {
            window.location.href = "../../login.html";
        } else if (path.includes("/pages/")) {
            window.location.href = "../login.html";
        } else {
            window.location.href = "login.html";
        }
        return false;
    }
    startSessionWatcher();
    return true;
}

// for pages that need a specific role
function requireRole(role) {
    if (!requireAuth()) return false;

    if (getUserRole() !== role) {
        // redirect to correct dashboard based on actual role
        if (getUserRole() === "ORGANIZER") {
            window.location.href = "pages/organizer/dashboard.html";
        } else {
            window.location.href = "pages/customer/home.html";
        }
        return false;
    }
    return true;
}

// for login/register pages — redirect away if already logged in
function redirectIfLoggedIn() {
    if (isLoggedIn()) {
        if (getUserRole() === "ORGANIZER") {
            window.location.href = "pages/organizer/dashboard.html";
        } else {
            window.location.href = "pages/customer/home.html";
        }
    }
}


// NAVBAR — inject dynamically on all pages

// call this on every page to build the navbar
function buildNavbar(activePage) {
    const role = getUserRole();
    const name = getUserName();

    // links differ based on role
    let navLinks = "";

    if (role === "CUSTOMER") {
        navLinks = `
            <a href="home.html" class="${activePage === 'home' ? 'active' : ''}">Events</a>
            <a href="my-bookings.html" class="${activePage === 'bookings' ? 'active' : ''}">My Bookings</a>
        `;
    } else if (role === "ORGANIZER") {
        navLinks = `
            <a href="dashboard.html" class="${activePage === 'dashboard' ? 'active' : ''}">Dashboard</a>
            <a href="create-event.html" class="${activePage === 'create' ? 'active' : ''}">Create Event</a>
        `;
    }

    const navbarHTML = `
        <nav class="navbar">
            <div class="navbar-brand">Event<span>Hive</span></div>
            <div class="navbar-links">
                ${navLinks}
            </div>
            <div class="navbar-user">
                <span>👋 ${name || "User"}</span>
                <button class="btn btn-outline btn-sm" onclick="logout()">Logout</button>
            </div>
        </nav>
    `;

    // inject at the top of body
    document.body.insertAdjacentHTML("afterbegin", navbarHTML);
}