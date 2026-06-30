// Redirect if already logged in
if (isLoggedIn()) {
  window.location.href = 'activities.html';
}

// Tab Switching
function switchTab(tab) {
  const loginSection    = document.getElementById('section-login');
  const registerSection = document.getElementById('section-register');
  const loginTab        = document.getElementById('tab-login');
  const registerTab     = document.getElementById('tab-register');

  clearAlert();
  clearAllErrors();

  if (tab === 'login') {
    loginSection.classList.add('visible');
    registerSection.classList.remove('visible');
    loginTab.classList.add('active');
    registerTab.classList.remove('active');
    document.title = 'Sign In — CircleUp';
    history.replaceState(null, '', '#login');
  } else {
    registerSection.classList.add('visible');
    loginSection.classList.remove('visible');
    registerTab.classList.add('active');
    loginTab.classList.remove('active');
    document.title = 'Create Account — CircleUp';
    history.replaceState(null, '', '#register');
  }
}

// Check URL hash on load
if (window.location.hash === '#register') {
  switchTab('register');
}

// Alert Helpers
function showAlert(msg) {
  const el = document.getElementById('alert');
  document.getElementById('alert-msg').textContent = msg;
  el.style.display = 'flex';
}
function clearAlert() {
  document.getElementById('alert').style.display = 'none';
}

// Field Error Helpers
function showFieldError(id, msg) {
  const errEl   = document.getElementById(`${id}-error`);
  const inputEl = document.getElementById(id);
  if (!errEl || !inputEl) return;
  errEl.textContent = msg;
  errEl.style.display = 'flex';
  inputEl.classList.add('error');
}
function clearFieldError(id) {
  const errEl   = document.getElementById(`${id}-error`);
  const inputEl = document.getElementById(id);
  if (!errEl || !inputEl) return;
  errEl.style.display = 'none';
  inputEl.classList.remove('error');
}
function clearAllErrors() {
  ['login-email', 'login-password'].forEach(clearFieldError);
  ['reg-name', 'reg-email', 'reg-password',
   'reg-phone', 'reg-city', 'reg-bio', 'reg-social'].forEach(clearFieldError);
}

// Toast
function showToast(msg, type = 'success') {
  const container = document.getElementById('toast-container');
  const toast     = document.createElement('div');
  toast.className = `toast toast-${type}`;
  toast.textContent = msg;
  container.appendChild(toast);
  setTimeout(() => toast.remove(), 3500);
}

// Loading State
function setLoginLoading(loading) {
  const btn  = document.getElementById('login-btn');
  const text = document.getElementById('login-btn-text');
  const spin = document.getElementById('login-spinner');
  btn.disabled       = loading;
  text.textContent   = loading ? 'Signing in...' : 'Sign in';
  spin.style.display = loading ? 'inline-block' : 'none';
}
function setRegisterLoading(loading) {
  const btn  = document.getElementById('register-btn');
  const text = document.getElementById('register-btn-text');
  const spin = document.getElementById('register-spinner');
  btn.disabled       = loading;
  text.textContent   = loading ? 'Creating account...' : 'Create account';
  spin.style.display = loading ? 'inline-block' : 'none';
}

// Navigate with transition (bypasses the <a> handler since these are JS redirects)
function navigateTo(url) {
  document.body.classList.remove('visible');
  document.body.classList.add('leaving');
  setTimeout(() => { window.location.href = url; }, 340);
}

// Login Form
document.getElementById('login-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  clearAlert();
  clearAllErrors();

  const email    = document.getElementById('login-email').value.trim();
  const password = document.getElementById('login-password').value;

  let valid = true;
  if (!email)    { showFieldError('login-email',    'Email is required.');    valid = false; }
  if (!password) { showFieldError('login-password', 'Password is required.'); valid = false; }
  if (!valid) return;

  setLoginLoading(true);

  const { data, ok } = await apiLogin(email, password);

  if (!ok) {
    const msg = typeof data.detail === 'string'
      ? data.detail
      : 'Invalid email or password.';
    showAlert(msg);
    setLoginLoading(false);
    return;
  }

  setToken(data.access_token);
  setUser(data.user);

  showToast('Welcome back!');
  setTimeout(() => navigateTo('activities.html'), 800);
});

// Register Form
document.getElementById('register-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  clearAlert();
  clearAllErrors();

  const name     = document.getElementById('reg-name').value.trim();
  const email    = document.getElementById('reg-email').value.trim();
  const password = document.getElementById('reg-password').value;
  const phone    = document.getElementById('reg-phone').value.trim() || null;
  const city     = document.getElementById('reg-city').value.trim() || null;
  const bio      = document.getElementById('reg-bio').value.trim() || null;
  const social   = document.getElementById('reg-social').value.trim() || null;

  let valid = true;
  if (!name)     { showFieldError('reg-name',     'Name is required.');     valid = false; }
  if (!email)    { showFieldError('reg-email',    'Email is required.');    valid = false; }
  if (!password) { showFieldError('reg-password', 'Password is required.'); valid = false; }
  if (!valid) return;

  setRegisterLoading(true);

  const payload = { name, email, password };
  if (phone)  payload.phone         = phone;
  if (city)   payload.city          = city;
  if (bio)    payload.bio           = bio;
  if (social) payload.social_handle = social;

  const { data, ok } = await apiRegister(payload);

  if (!ok) {
    if (Array.isArray(data.detail)) {
      data.detail.forEach(err => {
        const field = err.loc[err.loc.length - 1];
        const fieldMap = {
          name:          'reg-name',
          email:         'reg-email',
          password:      'reg-password',
          phone:         'reg-phone',
          city:          'reg-city',
          bio:           'reg-bio',
          social_handle: 'reg-social',
        };
        const mappedId = fieldMap[field];
        if (mappedId) showFieldError(mappedId, err.msg.replace('Value error, ', ''));
      });
    } else {
    const msg = typeof data.detail === 'string'
      ? data.detail
      : 'Registration failed. Please try again.';
    showAlert(msg);
    }
    setRegisterLoading(false);
    return;
  }

  showToast('Account created! Signing you in...');

  // Auto-login after register
  const { data: loginData, ok: loginOk } = await apiLogin(email, password);

  if (loginOk) {
    setToken(loginData.access_token);
    setUser(loginData.user);
    setTimeout(() => navigateTo('activities.html'), 1000);
  } else {
    setTimeout(() => navigateTo('auth.html#login'), 1000);
  }
});
