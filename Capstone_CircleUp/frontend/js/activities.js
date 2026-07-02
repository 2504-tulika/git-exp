/**
 * activities.js
 * Handles the activities discovery page — fetching, filtering, rendering, and pagination.
 */

// State
let _currentSkip  = 0;
const PAGE_SIZE   = 12;
let _hasMore      = false;
let _currentFilters = {
  category: '',
  location: '',
  date: '',
  sort: 'date_asc',
};

// Init

function initActivities() {
  _bindFilterEvents();
  fetchActivities(true);
}

// Filter Events

function _bindFilterEvents() {
  // Fetch on category or sort change immediately
  document.getElementById('filter-category').addEventListener('change', () => {
    _applyFilters();
  });

  document.getElementById('filter-sort').addEventListener('change', () => {
    _applyFilters();
  });

  // Debounce location input so we don't fire on every keystroke
  let _locationTimer = null;
  document.getElementById('filter-location').addEventListener('input', () => {
    clearTimeout(_locationTimer);
    _locationTimer = setTimeout(_applyFilters, 400);
  });

  // Fetch on date change
  document.getElementById('filter-date').addEventListener('change', () => {
    _applyFilters();
  });

  // Clear filters button
  document.getElementById('clear-filters').addEventListener('click', clearFilters);
}

function _applyFilters() {
  _currentFilters = {
    category: document.getElementById('filter-category').value,
    location: document.getElementById('filter-location').value.trim(),
    date:     document.getElementById('filter-date').value,
    sort:     document.getElementById('filter-sort').value,
  };
  fetchActivities(true);
}

function clearFilters() {
  document.getElementById('filter-category').value = '';
  document.getElementById('filter-location').value = '';
  document.getElementById('filter-date').value     = '';
  document.getElementById('filter-sort').value     = 'date_asc';
  _currentFilters = { category: '', location: '', date: '', sort: 'date_asc' };
  fetchActivities(true);
}

// Fetch

async function fetchActivities(reset = false) {
  if (reset) {
    _currentSkip = 0;
    document.getElementById('activities-grid').style.display  = 'none';
    document.getElementById('activities-empty').style.display = 'none';
    document.getElementById('load-more-wrap').style.display   = 'none';
    document.getElementById('activities-loading').style.display = '';
  }

  const params = new URLSearchParams();
  if (_currentFilters.category) params.set('category', _currentFilters.category);
  if (_currentFilters.location) params.set('location', _currentFilters.location);
  if (_currentFilters.date)     params.set('date',     _currentFilters.date);
  params.set('sort',  _currentFilters.sort);
  params.set('skip',  _currentSkip);
  params.set('limit', PAGE_SIZE);

  const { data, ok } = await apiGetActivities({
  category: _currentFilters.category,
  location: _currentFilters.location,
  date:     _currentFilters.date,
  sort:     _currentFilters.sort,
  skip:     _currentSkip,
  limit:    PAGE_SIZE,
  });

  document.getElementById('activities-loading').style.display = 'none';

  if (!ok) {
    showActivitiesToast('Failed to load activities. Please try again.', 'error');
    return;
  }

  const activities = data;
  _hasMore = activities.length === PAGE_SIZE;

  if (reset) {
    if (activities.length === 0) {
      document.getElementById('activities-empty').style.display = 'block';
      return;
    }
    document.getElementById('activities-grid').innerHTML = '';
  }

  document.getElementById('activities-grid').style.display = '';
  activities.forEach(a => {
    document.getElementById('activities-grid').appendChild(_buildCard(a));
  });

  _currentSkip += activities.length;

  document.getElementById('load-more-wrap').style.display = _hasMore ? 'block' : 'none';
}

// Load More

async function loadMore() {
  const btn = document.getElementById('load-more-btn');
  btn.textContent = 'Loading...';
  btn.disabled = true;
  await fetchActivities(false);
  btn.textContent = 'Load more';
  btn.disabled = false;
}

// Card Builder

function _buildCard(a) {
  const card = document.createElement('div');
  card.className = `activity-card${a.status === 'cancelled' ? ' cancelled' : ''}`;

  // Format date nicely
  const dateStr = new Date(a.activity_date + 'T00:00:00').toLocaleDateString('en-IN', {
    weekday: 'short', day: 'numeric', month: 'short', year: 'numeric'
  });

  // Format time nicely
  const [h, m] = a.activity_time.split(':');
  const hour = parseInt(h);
  const timeStr = `${hour > 12 ? hour - 12 : hour || 12}:${m} ${hour >= 12 ? 'PM' : 'AM'}`;

  card.innerHTML = `
    <div class="activity-card-top">
      <span class="activity-card-category">${_capitalize(a.category)}</span>
      <span class="badge badge-${a.status}">${_statusLabel(a.status)}</span>
    </div>
    <div class="activity-card-title">${_escape(a.title)}</div>
    <div class="activity-card-meta">
      <div class="activity-card-meta-row">
        <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/>
        </svg>
        ${_escape(a.location)}
      </div>
      <div class="activity-card-meta-row">
        <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/>
        </svg>
        ${dateStr} · ${timeStr}
      </div>
    </div>
    <div class="activity-card-footer">
      <span class="activity-card-participants">
        ${a.max_participants} spots max
      </span>
    </div>
  `;

  // All cards are clickable — navigate to detail page
  card.addEventListener('click', () => {
    window.location.href = `activity-detail.html?id=${a.id}`;
  });

  return card;
}

// Helpers

function _statusLabel(status) {
  const labels = {
    open:      'Open',
    full:      'Full',
    cancelled: 'Cancelled',
    completed: 'Completed',
  };
  return labels[status] || status;
}

function _capitalize(str) {
  if (!str) return '';
  return str.charAt(0).toUpperCase() + str.slice(1);
}

function _escape(str) {
  if (!str) return '';
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

function showActivitiesToast(msg, type = 'success') {
  let container = document.getElementById('toast-container');
  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  toast.textContent = msg;
  container.appendChild(toast);
  setTimeout(() => toast.remove(), 3500);
}