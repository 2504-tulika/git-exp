/**
 * create-activity.js
 *
 * Handles the create activity form — validation, submission,
 * and redirect to the new activity's detail page on success.
 */
function initCreateActivity() {
  // Set minimum date to today so users can't pick past dates
  const dateInput = document.getElementById('ca-date');
  const today = new Date().toISOString().split('T')[0];
  dateInput.min = today;
  document.getElementById('create-form').addEventListener('submit', handleCreateSubmit);
  // Bind live preview events
  _bindPreviewEvents();
}
function _bindPreviewEvents() {
  const fields = ['ca-title', 'ca-category', 'ca-location', 'ca-date', 'ca-time', 'ca-max'];
  fields.forEach(id => {
    document.getElementById(id).addEventListener('input', _updatePreview);
    document.getElementById(id).addEventListener('change', _updatePreview);
  });
}
function _updatePreview() {
  const title = document.getElementById('ca-title').value.trim();
  const category = document.getElementById('ca-category').value;
  const location = document.getElementById('ca-location').value.trim();
  const dateVal = document.getElementById('ca-date').value;
  const timeVal = document.getElementById('ca-time').value;
  const max = document.getElementById('ca-max').value;
  // Title
  document.getElementById('prev-title').textContent = title || 'Your Activity Title';
  // Category
  const catEl = document.getElementById('prev-category');
  if (category) {
    catEl.textContent = category.charAt(0).toUpperCase() + category.slice(1);
  } else {
    catEl.textContent = 'Sports';
  }
  // Location
  document.getElementById('prev-location').textContent = location || 'Enter location';
  // Date & Time
  if (dateVal || timeVal) {
    let dateStr = '';
    if (dateVal) {
      dateStr = new Date(dateVal + 'T00:00:00').toLocaleDateString('en-IN', {
        weekday: 'short', day: 'numeric', month: 'short', year: 'numeric'
      });
    } else {
      dateStr = 'Date';
    }
    let timeStr = '';
    if (timeVal) {
      const [h, m] = timeVal.split(':');
      const hour = parseInt(h);
      timeStr = `${hour > 12 ? hour - 12 : hour || 12}:${m} ${hour >= 12 ? 'PM' : 'AM'}`;
    } else {
      timeStr = 'Time';
    }
    document.getElementById('prev-datetime').textContent = `${dateStr} · ${timeStr}`;
  } else {
    document.getElementById('prev-datetime').textContent = 'Choose date & time';
  }
  // Capacity
  if (max) {
    document.getElementById('prev-capacity').textContent = `${max} spots max`;
  } else {
    document.getElementById('prev-capacity').textContent = '— spots max';
  }
}
async function handleCreateSubmit(e) {
  e.preventDefault();
  clearCreateErrors();
  document.getElementById('create-alert').style.display = 'none';
  // Read values
  const title       = document.getElementById('ca-title').value.trim();
  const description = document.getElementById('ca-description').value.trim() || null;
  const category    = document.getElementById('ca-category').value;
  const location    = document.getElementById('ca-location').value.trim();
  const date        = document.getElementById('ca-date').value;
  const time        = document.getElementById('ca-time').value;
  const max         = document.getElementById('ca-max').value;
  // Client-side validation
  let valid = true;
  if (!title) {
    showCreateError('ca-title', 'Title is required.');
    valid = false;
  }
  if (!category) {
    showCreateError('ca-category', 'Please select a category.');
    valid = false;
  }
  if (!location) {
    showCreateError('ca-location', 'Location is required.');
    valid = false;
  }
  if (!date) {
    showCreateError('ca-date', 'Date is required.');
    valid = false;
  }
  if (!time) {
    showCreateError('ca-time', 'Time is required.');
    valid = false;
  }
  if (!max || parseInt(max) < 1) {
    showCreateError('ca-max', 'Enter a valid number of participants (at least 1).');
    valid = false;
  }
  if (!valid) return;
  setCreateLoading(true);
  const payload = {
    title,
    category,
    location,
    activity_date: date,
    activity_time: time + ':00',  // backend expects HH:MM:SS
    max_participants: parseInt(max),
  };
  if (description) payload.description = description;
  const { data, ok } = await apiCreateActivity(payload);
  if (!ok) {
    setCreateLoading(false);
    // Map field-level validation errors from FastAPI
    if (Array.isArray(data.detail)) {
      data.detail.forEach(err => {
        const field = err.loc[err.loc.length - 1];
        const fieldMap = {
          title:            'ca-title',
          description:      'ca-description',
          category:         'ca-category',
          location:         'ca-location',
          activity_date:    'ca-date',
          activity_time:    'ca-time',
          max_participants: 'ca-max',
        };
        const mappedId = fieldMap[field];
        if (mappedId) showCreateError(mappedId, err.msg.replace('Value error, ', ''));
      });
    } else {
      document.getElementById('create-alert-msg').textContent =
        data.detail || 'Failed to create activity. Please try again.';
      document.getElementById('create-alert').style.display = 'flex';
    }
    return;
  }
  // Success — navigate to the new activity's detail page
  showCreateToast('Activity created!');
  setTimeout(() => {
    window.location.href = `activity-detail.html?id=${data.id}`;
  }, 800);
}
// ── Helpers ────────────────────────────────────────────────────
function setCreateLoading(loading) {
  const btn  = document.getElementById('create-btn');
  const text = document.getElementById('create-btn-text');
  const spin = document.getElementById('create-spinner');
  btn.disabled       = loading;
  text.textContent   = loading ? 'Creating...' : 'Create activity';
  spin.style.display = loading ? 'inline-block' : 'none';
}
function showCreateError(id, msg) {
  const errEl   = document.getElementById(`${id}-error`);
  const inputEl = document.getElementById(id);
  if (!errEl || !inputEl) return;
  errEl.textContent    = msg;
  errEl.style.display  = 'flex';
  inputEl.classList.add('error');
}
function clearCreateErrors() {
  ['ca-title', 'ca-description', 'ca-category', 'ca-location',
   'ca-date', 'ca-time', 'ca-max'].forEach(id => {
    const errEl   = document.getElementById(`${id}-error`);
    const inputEl = document.getElementById(id);
    if (errEl)   errEl.style.display = 'none';
    if (inputEl) inputEl.classList.remove('error');
  });
}
function showCreateToast(msg, type = 'success') {
  const container = document.getElementById('toast-container');
  const toast     = document.createElement('div');
  toast.className = `toast toast-${type}`;
  toast.textContent = msg;
  container.appendChild(toast);
  setTimeout(() => toast.remove(), 3500);
}