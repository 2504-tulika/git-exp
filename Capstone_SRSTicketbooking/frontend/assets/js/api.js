// ========================================
// API.JS — All backend API calls
// Base URL points to our Spring Boot server
// ========================================

const BASE_URL = "http://localhost:8081/api";

// ----------------------------------------
// HELPER — makes HTTP requests
// automatically attaches JWT token if present
// ----------------------------------------
async function apiRequest(endpoint, method = "GET", body = null, requiresAuth = true) {
    const headers = {
        "Content-Type": "application/json"
    };

    // attach token for protected endpoints
    if (requiresAuth) {
        const token = localStorage.getItem("token");
        if (token) {
            headers["Authorization"] = "Bearer " + token;
        }
    }

    const options = {
        method: method,
        headers: headers
    };

    if (body) {
        options.body = JSON.stringify(body);
    }

    const response = await fetch(BASE_URL + endpoint, options);
    const data = await response.json();

    // attach status code to response so callers can check it
    data._status = response.status;
    return data;
}


// ========================================
// USER SERVICE CALLS
// ========================================

// register a new user
async function registerUser(name, email, password, phone, role) {
    return await apiRequest("/users/register", "POST", {
        name, email, password, phone, role
    }, false);
}

// login and get JWT token
async function loginUser(email, password) {
    return await apiRequest("/users/login", "POST", {
        email, password
    }, false);
}


// ========================================
// EVENT SERVICE CALLS
// ========================================

// get all upcoming events (customer home page)
async function getAllEvents() {
    return await apiRequest("/events", "GET", null, true);
}

// get a single event's details
async function getEventById(eventId) {
    return await apiRequest("/events/" + eventId, "GET", null, true);
}

// organizer — create a new event
async function createEvent(eventData) {
    return await apiRequest("/events/create", "POST", eventData, true);
}

// organizer — get only their own events
async function getMyEvents() {
    return await apiRequest("/events/my-events", "GET", null, true);
}

// organizer — update event details
async function updateEvent(eventId, eventData) {
    return await apiRequest("/events/" + eventId, "PUT", eventData, true);
}

// organizer — update seat capacity only
async function updateEventCapacity(eventId, newTotalSeats) {
    return await apiRequest("/events/" + eventId + "/capacity", "PUT", {
        newTotalSeats
    }, true);
}

// organizer — cancel an event
async function cancelEvent(eventId) {
    return await apiRequest("/events/" + eventId + "/cancel", "PUT", null, true);
}


// ========================================
// BOOKING SERVICE CALLS
// ========================================

// customer — book tickets for an event
async function bookTickets(eventId, ticketsRequested) {
    return await apiRequest("/bookings", "POST", {
        eventId, ticketsRequested
    }, true);
}

// customer — cancel their own booking
async function cancelBooking(bookingId) {
    return await apiRequest("/bookings/" + bookingId + "/cancel", "PUT", null, true);
}

// customer — get their own booking history
async function getMyBookings() {
    return await apiRequest("/bookings/my-bookings", "GET", null, true);
}

// organizer — get all bookings for a specific event
async function getBookingsForEvent(eventId) {
    return await apiRequest("/bookings/event/" + eventId, "GET", null, true);
}