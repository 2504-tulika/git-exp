// ========================================
// API.JS — All backend API calls
// ========================================

const BASE_URL = "http://localhost:8081/api";

async function apiRequest(endpoint, method = "GET", body = null, requiresAuth = true) {
    const headers = { "Content-Type": "application/json" };

    if (requiresAuth) {
        const token = localStorage.getItem("token");
        if (token) headers["Authorization"] = "Bearer " + token;
    }

    const options = { method, headers };
    if (body) options.body = JSON.stringify(body);

    const response = await fetch(BASE_URL + endpoint, options);
    const status   = response.status;

    // handle empty responses (e.g. 204 No Content)
    const text = await response.text();
    if (!text) return { _status: status };

    const data = JSON.parse(text);

    // arrays need special wrapping so _status doesn't corrupt them
    if (Array.isArray(data)) {
        return { _isArray: true, _data: data, _status: status };
    }

    data._status = status;
    return data;
}


// ========================================
// USER SERVICE
// ========================================

async function registerUser(name, email, password, phone, role) {
    return await apiRequest("/users/register", "POST",
        { name, email, password, phone, role }, false);
}

async function loginUser(email, password) {
    return await apiRequest("/users/login", "POST",
        { email, password }, false);
}


// ========================================
// EVENT SERVICE
// ========================================

async function getAllEvents() {
    return await apiRequest("/events", "GET", null, true);
}

async function getEventById(eventId) {
    return await apiRequest("/events/" + eventId, "GET", null, true);
}

async function createEvent(eventData) {
    return await apiRequest("/events/create", "POST", eventData, true);
}

async function getMyEvents() {
    return await apiRequest("/events/my-events", "GET", null, true);
}

async function updateEvent(eventId, eventData) {
    return await apiRequest("/events/" + eventId, "PUT", eventData, true);
}

async function updateEventCapacity(eventId, newTotalSeats) {
    return await apiRequest("/events/" + eventId + "/capacity", "PUT",
        { newTotalSeats }, true);
}

async function cancelEvent(eventId) {
    return await apiRequest("/events/" + eventId + "/cancel", "PUT", null, true);
}


// ========================================
// BOOKING SERVICE
// ========================================

async function bookTickets(eventId, ticketsRequested) {
    return await apiRequest("/bookings", "POST",
        { eventId, ticketsRequested }, true);
}

async function cancelBooking(bookingId) {
    return await apiRequest("/bookings/" + bookingId + "/cancel", "PUT", null, true);
}

async function getMyBookings() {
    return await apiRequest("/bookings/my-bookings", "GET", null, true);
}

async function getBookingsForEvent(eventId) {
    return await apiRequest("/bookings/event/" + eventId, "GET", null, true);
}