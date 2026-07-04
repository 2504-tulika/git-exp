/**
 * activity-detail.js
 *
 * Handles the activity detail page — loads activity info, adapts the
 * UI based on whether the current user is the creator or a participant,
 * and manages request-to-join and approve/reject flows.
 */

// ── State ──────────────────────────────────────────────────────
let _activity    = null;
let _currentUser = null;
let _myRequest   = null;

// ── Init ───────────────────────────────────────────────────────

async function initActivityDetail() {
  // Get activity ID from URL
  const params     = new URLSearchParams(window.location.search);
  const activityId = params.get('id');

  if (!activityId) {
    window.location.href = 'activities.html';
    return;
  }

  // Load current user from cache
  _currentUser = getUser();

  // Fetch activity
  const { data, ok } = await apiGetActivity(activityId);

  document.getElementById('detail-loading').style.display = 'none';

  if (!ok) {
    showDetailToast('Failed to load activity.', 'error');
    return;
  }

  _activity = data;
  _renderActivity(data);
  document.getElementById('detail-content').style.display = 'block';

  // Decide which section to show: creator or participant
  const isCreator = _currentUser && _activity.creator_id === _currentUser.id;

  if (isCreator) {
    _initCreatorSection(activityId);
  } else {
    _initParticipantSection(activityId);
  }
}

// ── Render Activity ────────────────────────────────────────────

function _renderActivity(a) {
  // Category + title
  document.getElementById('detail-category').textContent = _capitalize(a.category);
  document.getElementById('detail-title').textContent    = a.title;

  // Status badge
  const badge = document.getElementById('detail-status-badge');
  badge.textContent = _statusLabel(a.status);
  badge.className   = `badge badge-${a.status}`;

  // Meta
  const dateStr = new Date(a.activity_date + 'T00:00:00').toLocaleDateString('en-IN', {
    weekday: 'long', day: 'numeric', month: 'long', year: 'numeric'
  });
  const [h, m] = a.activity_time.split(':');
  const hour   = parseInt(h);
  const timeStr = `${hour > 12 ? hour - 12 : hour || 12}:${m} ${hour >= 12 ? 'PM' : 'AM'}`;

  document.getElementById('detail-location').textContent     = a.location;
  document.getElementById('detail-date').textContent         = dateStr;
  document.getElementById('detail-time').textContent         = timeStr;
  document.getElementById('detail-participants').textContent = `${a.max_participants} spots max`;

  // Description
  document.getElementById('detail-description').textContent = a.description;

  // Organizer name — fetch from profile if needed
  // For now show ID; creator name will be loaded separately
  document.getElementById('detail-organizer-name').textContent =
    a.creator_name || `User #${a.creator_id}`;

  // Update page title
  document.title = `${a.title} — CircleUp`;
}

// ── Participant Section ────────────────────────────────────────

async function _initParticipantSection(activityId) {
  document.getElementById('participant-section').style.display = 'block';

  const status = _activity.status;

  // If activity is not open — show unavailable
  if (status === 'cancelled') {
    _showParticipantState('unavailable');
    document.getElementById('unavailable-title').textContent = 'Activity cancelled';
    document.getElementById('unavailable-desc').textContent  =
      'This activity has been cancelled by the organiser.';
    return;
  }

  if (status === 'completed') {
    _showParticipantState('unavailable');
    document.getElementById('unavailable-title').textContent = 'Activity completed';
    document.getElementById('unavailable-desc').textContent  =
      'This activity has already taken place.';
    return;
  }

  if (status === 'full') {
    _showParticipantState('unavailable');
    document.getElementById('unavailable-title').textContent = 'Activity full';
    document.getElementById('unavailable-desc').textContent  =
      'This activity has reached maximum capacity.';
    return;
  }

  // Check if the user already has a request for this activity
  const { data: myReq, ok: reqOk, status: reqStatus } = await apiGetMyRequest(activityId);

  // 404 = no request exists yet — show the join button
  if (reqStatus === 404) {
    _showParticipantState('join');
    return;
  }

  if (reqOk && myReq) {
    _myRequest = myReq;
    if (myReq.status === 'pending') {
      _showParticipantState('pending');
    } else if (myReq.status === 'approved') {
      _showParticipantState('approved');
      _loadOrganizerContact(activityId, myReq.id);
    } else if (myReq.status === 'rejected') {
      _showParticipantState('rejected');
    }
    return;
  }

  // Fallback — show join button
  _showParticipantState('join');
}

function _showParticipantState(state) {
  ['action-join', 'action-pending', 'action-approved',
   'action-rejected', 'action-unavailable'].forEach(id => {
    document.getElementById(id).style.display = 'none';
  });
  document.getElementById(`action-${state}`).style.display = 'block';
}

// ── Request to Join ────────────────────────────────────────────

async function requestToJoin() {
  const btn  = document.getElementById('join-btn');
  const text = document.getElementById('join-btn-text');
  const spin = document.getElementById('join-spinner');

  btn.disabled       = true;
  text.textContent   = 'Sending...';
  spin.style.display = 'inline-block';

  const { data, ok, status } = await apiRequestParticipation(_activity.id);

  spin.style.display = 'none';

  if (!ok) {
    btn.disabled     = false;
    text.textContent = 'Request to join';

    // 409 means already requested
    if (status === 409) {
      _showParticipantState('pending');
      return;
    }

    showDetailToast(data.detail || 'Failed to send request.', 'error');
    return;
  }

  _myRequest = data;
  _showParticipantState('pending');
  showDetailToast('Request sent! Waiting for the organiser to respond.');
}

// ── Creator Section ────────────────────────────────────────────

async function _initCreatorSection(activityId) {
  document.getElementById('creator-section').style.display = 'block';

  const { data, ok } = await apiGetActivityRequests(activityId);

  document.getElementById('requests-loading').style.display = 'none';

  if (!ok) {
    showDetailToast('Failed to load requests.', 'error');
    return;
  }

  if (data.length === 0) {
    document.getElementById('requests-empty').style.display = 'block';
    return;
  }

  const list = document.getElementById('requests-list');
  list.style.display = 'block';
  data.forEach(req => list.appendChild(_buildRequestRow(req)));
}

function _buildRequestRow(req) {
  const row = document.createElement('div');
  row.className = 'request-row';
  row.id = `request-row-${req.id}`;

  const isPending = req.status === 'pending';

  row.innerHTML = `
    <div class="request-user">
      <div class="request-user-name">${req.user_name || `User #${req.user_id}`}</div>
      ${req.status !== 'pending'
        ? `<div class="request-user-contact">
            ${req.status === 'approved'
              ? `Phone: <strong id="contact-phone-${req.id}">loading...</strong>`
              : '<span style="color:var(--rejected)">Rejected</span>'}
           </div>`
        : ''}
    </div>
    <div class="request-actions">
      ${isPending
        ? `<button class="btn btn-primary btn-sm" onclick="approveRequest(${req.id})">Approve</button>
           <button class="btn btn-danger btn-sm" onclick="rejectRequest(${req.id})">Reject</button>`
        : `<span class="badge badge-${req.status}">${_statusLabel(req.status)}</span>`}
    </div>
  `;

  // If already approved, load contact info
  if (req.status === 'approved') {
    _loadContactForRequest(req.id);
  }

  return row;
}

async function approveRequest(requestId) {
  await _updateRequest(requestId, 'approved');
}

async function rejectRequest(requestId) {
  await _updateRequest(requestId, 'rejected');
}

async function _updateRequest(requestId, newStatus) {
  const { data, ok } = await apiUpdateRequestStatus(
    _activity.id, requestId, newStatus
  );

  if (!ok) {
    showDetailToast(data.detail || 'Failed to update request.', 'error');
    return;
  }

  // Rebuild just that row
  const row = document.getElementById(`request-row-${requestId}`);
  if (row) {
    const newRow = _buildRequestRow(data);
    row.replaceWith(newRow);
  }

  // If activity became full, update the badge
  if (data.status === 'approved') {
    const { data: updatedActivity } = await apiGetActivity(_activity.id);
    if (updatedActivity) {
      _activity = updatedActivity;
      const badge = document.getElementById('detail-status-badge');
      badge.textContent = _statusLabel(updatedActivity.status);
      badge.className   = `badge badge-${updatedActivity.status}`;
    }
  }

  showDetailToast(
    newStatus === 'approved' ? 'Request approved!' : 'Request rejected.'
  );
}

async function _loadOrganizerContact(activityId, requestId) {
  const { data, ok } = await apiGetApprovedContact(activityId, requestId);
  if (ok) {
    if (data.creator_phone) {
      document.getElementById('organizer-phone').textContent = data.creator_phone;
    } else {
      document.getElementById('organizer-phone-row').style.display = 'none';
    }
    if (data.creator_social) {
      document.getElementById('organizer-social').textContent = data.creator_social;
    } else {
      document.getElementById('organizer-social-row').style.display = 'none';
    }
  }
}

async function _loadContactForRequest(requestId) {
  const { data, ok } = await apiGetApprovedContact(_activity.id, requestId);
  if (ok && data.participant_phone) {
    const el = document.getElementById(`contact-phone-${requestId}`);
    if (el) el.textContent = data.participant_phone;
  }
}

// ── Helpers ────────────────────────────────────────────────────

function _statusLabel(status) {
  const labels = {
    open:      'Open',
    full:      'Full',
    cancelled: 'Cancelled',
    completed: 'Completed',
    pending:   'Pending',
    approved:  'Approved',
    rejected:  'Rejected',
  };
  return labels[status] || status;
}

function _capitalize(str) {
  if (!str) return '';
  return str.charAt(0).toUpperCase() + str.slice(1);
}

function showDetailToast(msg, type = 'success') {
  const container = document.getElementById('toast-container');
  const toast     = document.createElement('div');
  toast.className = `toast toast-${type}`;
  toast.textContent = msg;
  container.appendChild(toast);
  setTimeout(() => toast.remove(), 3500);
}