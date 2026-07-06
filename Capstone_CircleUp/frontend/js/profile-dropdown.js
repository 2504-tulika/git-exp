/**
 * profile-dropdown.js
 *
 * Handles all behaviour for the profile dropdown in the navbar.
 * The dropdown HTML structure lives in each page's HTML file — this
 * script only queries elements and manages state/interactions.
 * No HTML strings live in this file, by design.
 */

// ── State ──────────────────────────────────────────────────────
let _dropdownProfile = null;

// ── Init ───────────────────────────────────────────────────────

/**
 * Call this on DOMContentLoaded on every authenticated page.
 * Loads profile data and wires up the edit form submit handler.
 * Assumes the dropdown markup already exists in the page HTML.
 */
async function initProfileDropdown() {
  const mount = document.getElementById('profile-trigger-mount');
  if (!mount) return;

  await loadDropdownProfile();

  const editForm = document.getElementById('pd-edit-form');
  if (editForm) editForm.addEventListener('submit', saveProfileEdit);
}

// ── Load & Render ──────────────────────────────────────────────

async function loadDropdownProfile() {
  const cached = getUser();
  if (cached) renderDropdown(cached);

  const { data, ok } = await apiGetProfile();
  if (ok) {
    _dropdownProfile = data;
    setUser(data);
    renderDropdown(data);
  }
}

function renderDropdown(p) {
  const initials = p.name
    ? p.name.split(' ').map(w => w[0]).join('').toUpperCase().slice(0, 2)
    : '?';

  document.getElementById('pd-nav-avatar').textContent = initials;
  document.getElementById('pd-avatar').textContent     = initials;
  document.getElementById('pd-name').textContent       = p.name           || 'NA';
  document.getElementById('pd-email').textContent      = p.email          || 'NA';
  document.getElementById('pd-city').textContent       = p.city           || 'NA';
  document.getElementById('pd-phone').textContent      = p.phone          || 'NA';
  document.getElementById('pd-gender').textContent     = p.gender         || 'NA';
  document.getElementById('pd-social').textContent     = p.social_handle  || 'NA';
  document.getElementById('pd-bio').textContent        = p.bio            || 'NA';
}

// ── Toggle ─────────────────────────────────────────────────────

function toggleDropdown() {
  const dd = document.getElementById('profile-dropdown');
  const isOpen = dd.classList.contains('open');
  isOpen ? closeDropdown() : openDropdown();
}

function openDropdown() {
  document.getElementById('profile-dropdown').classList.add('open');
  document.getElementById('profile-overlay').classList.add('active');
}

function closeDropdown() {
  document.getElementById('profile-dropdown')?.classList.remove('open');
  document.getElementById('profile-overlay')?.classList.remove('active');
  cancelProfileEdit();
}

// ── Edit ───────────────────────────────────────────────────────

function startProfileEdit() {
  const p = _dropdownProfile || getUser() || {};

  document.getElementById('pd-edit-name').value   = p.name           || '';
  document.getElementById('pd-edit-city').value   = p.city           || '';
  document.getElementById('pd-edit-phone').value  = p.phone          || '';
  document.getElementById('pd-edit-social').value = p.social_handle  || '';
  document.getElementById('pd-edit-bio').value    = p.bio            || '';

  document.getElementById('pd-fields').style.display = 'none';
  document.getElementById('pd-edit-form').classList.add('visible');
}

function cancelProfileEdit() {
  const form   = document.getElementById('pd-edit-form');
  const fields = document.getElementById('pd-fields');
  if (!form || !fields) return;
  form.classList.remove('visible');
  fields.style.display = '';
}

async function saveProfileEdit(e) {
  e.preventDefault();

  const name   = document.getElementById('pd-edit-name').value.trim();
  const city   = document.getElementById('pd-edit-city').value.trim()   || null;
  const phone  = document.getElementById('pd-edit-phone').value.trim()  || null;
  const social = document.getElementById('pd-edit-social').value.trim() || null;
  const bio    = document.getElementById('pd-edit-bio').value.trim()    || null;

  if (!name) return;

  document.getElementById('pd-edit-form').classList.remove('visible');
  document.getElementById('pd-saving').classList.add('visible');

  const payload = { name };
  if (city)   payload.city          = city;
  if (phone)  payload.phone         = phone;
  if (social) payload.social_handle = social;
  if (bio)    payload.bio           = bio;

  const { data, ok } = await apiUpdateProfile(payload);

  document.getElementById('pd-saving').classList.remove('visible');
  document.getElementById('pd-fields').style.display = '';

  if (ok) {
    _dropdownProfile = data;
    setUser(data);
    renderDropdown(data);
    showDropdownToast('Profile updated!');
  } else {
    showDropdownToast('Update failed. Try again.', 'error');
  }
}

// ── Logout ─────────────────────────────────────────────────────

async function handleLogout() {
  await apiLogout();
  window.location.href = '../index.html';
}

// ── Toast ──────────────────────────────────────────────────────

function showDropdownToast(msg, type = 'success') {
  let container = document.getElementById('toast-container');
  if (!container) {
    container = document.createElement('div');
    container.id = 'toast-container';
    container.className = 'toast-container';
    document.body.appendChild(container);
  }
  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  toast.textContent = msg;
  container.appendChild(toast);
  setTimeout(() => toast.remove(), 3500);
}
