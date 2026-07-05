const API_BASE = 'http://localhost:8000/api/v1';

// Token Management 

function getToken() {
  return localStorage.getItem('access_token');
}

function setToken(token) {
  localStorage.setItem('access_token', token);
}

function getUser() {
  const user = localStorage.getItem('user');
  return user ? JSON.parse(user) : null;
}

function setUser(user) {
  localStorage.setItem('user', JSON.stringify(user));
}

function clearSession() {
  localStorage.removeItem('access_token');
  localStorage.removeItem('user');
}

function isLoggedIn() {
  return !!getToken();
}

// Core Request Handler

/**
 * Makes an API request.
 * Automatically attaches Authorization header if token exists.
 * Returns { data, ok, status } — never throws.
 */
async function request(method, endpoint, body = null, auth = true) {
  const headers = { 'Content-Type': 'application/json' };

  if (auth) {
    const token = getToken();
    if (token) headers['Authorization'] = `Bearer ${token}`;
  }

  const options = { method, headers };
  if (body) options.body = JSON.stringify(body);

  try {
    const res = await fetch(`${API_BASE}${endpoint}`, options);
    if (res.status === 401 && auth) {
    clearSession();
    window.location.href = '../pages/auth.html#login';
    return;
    }
    const data = await res.json();
    return { data, ok: res.ok, status: res.status };
  } 
  catch (err) {
    return {
      data: { detail: 'Network error. Please check your connection.' },
      ok: false,
      status: 0,
    };
  }
}

// Auth API

async function apiRegister(payload) {
  return request('POST', '/auth/register', payload, false);
}

async function apiLogin(email, password) {
  return request('POST', '/auth/login', { email, password }, false);
}

async function apiLogout() {
  await request('POST', '/auth/logout');
  clearSession();
}

// User API

async function apiGetProfile() {
  return request('GET', '/users/me');
}

async function apiUpdateProfile(payload) {
  return request('PUT', '/users/me', payload);
}

// Activities API

async function apiGetActivities(filters = {}) {
  const params = new URLSearchParams();
  if (filters.category) params.append('category', filters.category);
  if (filters.location) params.append('location', filters.location);
  if (filters.date)     params.append('date', filters.date);
  if (filters.sort)     params.append('sort', filters.sort);
  const query = params.toString();
  return request('GET', `/activities${query ? '?' + query : ''}`);
}

async function apiGetActivity(id) {
  return request('GET', `/activities/${id}`);
}

async function apiCreateActivity(payload) {
  return request('POST', '/activities', payload);
}

async function apiUpdateActivity(id, payload) {
  return request('PUT', `/activities/${id}`, payload);
}

async function apiCancelActivity(id) {
  return request('DELETE', `/activities/${id}`);
}

// Participation API

async function apiRequestParticipation(activityId) {
  return request('POST', `/activities/${activityId}/requests`);
}

async function apiGetActivityRequests(activityId) {
  return request('GET', `/activities/${activityId}/requests`);
}

async function apiUpdateRequestStatus(activityId, requestId, status) {
  return request('PUT', `/activities/${activityId}/requests/${requestId}`, { status });
}

async function apiGetMyActivities() {
  return request('GET', '/users/me/activities');
}