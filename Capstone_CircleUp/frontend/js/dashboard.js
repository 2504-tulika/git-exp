/**
 * dashboard.js
 *
 * Handles the CircleUp dashboard — fetches stats, user activities,
 * toggles tabs, and manages dashboard actions like activity cancellation.
 */
// State

let _dashboardData = null;
let _currentTab = 'created'; // 'created', 'joined', 'requested', 'rejected'
async function initDashboard() {
    const user = getUser();
    if (user && user.name) {
        document.getElementById('welcome-title').textContent = `Welcome back, ${user.name}!`;
    }
    await fetchDashboardData();
}

async function fetchDashboardData() {
    document.getElementById('dashboard-grid').style.display = 'none';
    document.getElementById('dashboard-empty').style.display = 'none';
    document.getElementById('dashboard-loading').style.display = 'grid';
    const { data, ok } = await apiGetMyActivities();
    document.getElementById('dashboard-loading').style.display = 'none';
    if (!ok) {
        showDashboardToast('Failed to load dashboard data. Please try again.', 'error');
        return;
    }
    _dashboardData = data;
    // Render Stats
    document.getElementById('stats-created').textContent = data.stats.created;
    document.getElementById('stats-joined').textContent = data.stats.joined;
    document.getElementById('stats-pending').textContent = data.stats.pending;
    document.getElementById('stats-completed').textContent = data.stats.completed;
    // Render Current Tab
    renderTabContent();
}

function switchTab(tabName) {
    if (_currentTab === tabName) return;
    _currentTab = tabName;
    // Update active tab buttons styling
    const tabs = ['created', 'joined', 'requested', 'rejected'];
    tabs.forEach(t => {
        const btn = document.getElementById(`tab-btn-${t}`);
        if (btn) {
            if (t === tabName) {
                btn.classList.add('active');
            } else {
                btn.classList.remove('active');
            }
        }
    });
    renderTabContent();
}

function renderTabContent() {
    const grid = document.getElementById('dashboard-grid');
    const emptyState = document.getElementById('dashboard-empty');
    grid.innerHTML = '';
    grid.style.display = 'none';
    emptyState.style.display = 'none';
    if (!_dashboardData) return;
    // Map client tabs to backend keys
    const tabMapping = {
        created: 'created',
        joined: 'joined',
        requested: 'pending',
        rejected: 'rejected'
    };
    const apiKey = tabMapping[_currentTab];
    const list = _dashboardData[apiKey] || [];
    if (list.length === 0) {
        // Customize empty state messages
        const emptyDetails = {
            created: {
                title: 'No activities created yet',
                desc: 'Organise something exciting! Tap "Create Activity" to get started.'
            },
            joined: {
                title: 'No joined activities',
                desc: 'Browse activities, send requests to join, and once approved they will appear here.'
            },
            requested: {
                title: 'No requests pending',
                desc: 'You do not have any active join requests waiting for organizer approval.'
            },
            rejected: {
                title: 'No rejected requests',
                desc: 'All clear! You have no rejected participation requests.'
            }
        };
        const details = emptyDetails[_currentTab];
        document.getElementById('empty-title').textContent = details.title;
        document.getElementById('empty-desc').textContent = details.desc;
        emptyState.style.display = 'block';
        return;
    }

    // Render cards
    list.forEach(a => {
        grid.appendChild(_buildDashboardCard(a));
    });
    grid.style.display = 'grid';
}

function _buildDashboardCard(a) {
    const card = document.createElement('div');
    card.className = `activity-card${a.status === 'cancelled' ? ' cancelled' : ''}`;
    card.style.cursor = 'default'; // Let only buttons be clickable
    // Format date nicely
    const dateStr = new Date(a.activity_date + 'T00:00:00').toLocaleDateString('en-IN', {
        weekday: 'short', day: 'numeric', month: 'short', year: 'numeric'
    });
    // Format time nicely
    const [h, m] = a.activity_time.split(':');
    const hour = parseInt(h);
    const timeStr = `${hour > 12 ? hour - 12 : hour || 12}:${m} ${hour >= 12 ? 'PM' : 'AM'}`;
    // Build card inner HTML
    card.innerHTML = `
    <div class="activity-card-top">
      <span class="activity-card-category">${_capitalize(a.category)}</span>
      <span class="badge badge-${a.status}">${_statusLabel(a.status)}</span>
    </div>
    <div class="activity-card-title" style="margin-top: 12px; margin-bottom: 8px;">${_escape(a.title)}</div>
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
    <div class="activity-card-footer" style="margin-top: auto; padding-top: 16px; border-top: 1px solid var(--border); display: flex; flex-direction: column; gap: 12px;">
      <span class="activity-card-participants" style="font-size: 0.8125rem;">
        ${a.max_participants} spots max
      </span>
      <div class="card-actions-wrapper" style="display:flex; justify-content:flex-end; gap:8px;">
        <button class="btn btn-secondary btn-sm" onclick="navigateToDetail(${a.id})">View Details</button>
        ${_currentTab === 'created' && a.status !== 'cancelled' && a.status !== 'completed'
            ? `<button class="btn btn-danger btn-sm" onclick="cancelDashboardActivity(${a.id})">Cancel</button>`
            : ''
        }
      </div>
    </div>
  `;
    return card;
}


function navigateToDetail(id) {
    window.location.href = `activity-detail.html?id=${id}`;
}
async function cancelDashboardActivity(activityId) {
    if (!confirm('Are you sure you want to cancel this activity? This cannot be undone.')) {
        return;
    }
    const { ok, data } = await apiCancelActivity(activityId);
    if (ok) {
        showDashboardToast('Activity cancelled successfully.');
        await fetchDashboardData();
    } else {
        showDashboardToast(data.detail || 'Failed to cancel activity.', 'error');
    }
}


// Helpers
function _statusLabel(status) {
    const labels = {
        open: 'Open',
        full: 'Full',
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

function showDashboardToast(msg, type = 'success') {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = msg;
    container.appendChild(toast);
    setTimeout(() => toast.remove(), 3500);
}