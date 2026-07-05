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
  ['reg-name', 'reg-email', 'reg-password', 'reg-phone', 'reg-gender',
   'reg-city', 'reg-bio', 'reg-social'].forEach(clearFieldError);
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

// ── Validation Helpers ─────────────────────────────────────────

function isValidEmail(email) {
  // Must have text @ text . text — basic format check
  return /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(email);
}

function isGmailEmail(email) {
  return email.toLowerCase().endsWith('@gmail.com');
}

function getPasswordErrors(password) {
  const errors = [];
  if (password.length < 8)              errors.push('at least 8 characters');
  if (!/[A-Z]/.test(password))          errors.push('one uppercase letter');
  if (!/[a-z]/.test(password))          errors.push('one lowercase letter');
  if (!/[0-9]/.test(password))          errors.push('one number');
  if (!/[^A-Za-z0-9]/.test(password))   errors.push('one special character');
  return errors;
}

// ── Login Form ─────────────────────────────────────────────────

document.getElementById('login-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  clearAlert();
  clearAllErrors();

  const email    = document.getElementById('login-email').value.trim();
  const password = document.getElementById('login-password').value;

  let valid = true;

  // Email validations
  if (!email) {
    showFieldError('login-email', 'Email address is required.');
    valid = false;
  } else if (!isValidEmail(email)) {
    showFieldError('login-email', 'Enter a valid email address');
    valid = false;
  }

  // Password validations
  if (!password) {
    showFieldError('login-password', 'Password is required.');
    valid = false;
  } else if (password.length < 8) {
    showFieldError('login-password', 'Password must be at least 8 characters.');
    valid = false;
  }

  if (!valid) return;

  setLoginLoading(true);

  const { data, ok } = await apiLogin(email, password);

  if (!ok) {
    const msg = typeof data.detail === 'string'
      ? data.detail
      : 'Invalid email or password.';

    // Route server error to the right field if possible
    const lower = msg.toLowerCase();
    if (lower.includes('email') || lower.includes('not found') || lower.includes('user')) {
      showFieldError('login-email', msg);
    } else if (lower.includes('password') || lower.includes('incorrect') || lower.includes('wrong')) {
      showFieldError('login-password', msg);
    } else {
      // Generic — show under password as that's the last field
      showFieldError('login-password', 'Incorrect email or password. Please try again.');
    }
    setLoginLoading(false);
    return;
  }

  setToken(data.access_token);
  setUser(data.user);

  showToast('Welcome back!');
  setTimeout(() => navigateTo('activities.html'), 800);
});

// ── Register Form ──────────────────────────────────────────────

document.getElementById('register-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  clearAlert();
  clearAllErrors();

  const name     = document.getElementById('reg-name').value.trim();
  const email    = document.getElementById('reg-email').value.trim();
  const password = document.getElementById('reg-password').value;
  const phone    = document.getElementById('reg-phone').value.trim();
  const gender   = document.getElementById('reg-gender').value;
  const city     = document.getElementById('reg-city').value.trim() || null;
  const bio      = document.getElementById('reg-bio').value.trim() || null;
  const social   = document.getElementById('reg-social').value.trim() || null;

  let valid = true;

  if (!name || name.length < 2) {
    showFieldError('reg-name', !name ? 'Full name is required.' : 'Name must be at least 2 characters.');
    valid = false;
  }

  if (!email) {
    showFieldError('reg-email', 'Email address is required.');
    valid = false;
  } else if (!isValidEmail(email)) {
    showFieldError('reg-email', 'Enter a valid email address.');
    valid = false;
  } else if (!isGmailEmail(email)) {
    showFieldError('reg-email', 'Only Gmail addresses are accepted.');
    valid = false;
  }

  if (!password) {
    showFieldError('reg-password', 'Password is required.');
    valid = false;
  } else {
    const pwErrors = getPasswordErrors(password);
    if (pwErrors.length > 0) {
      showFieldError('reg-password', `Password must have ${pwErrors.join(', ')}.`);
      valid = false;
    }
  }

  if (!phone) {
    showFieldError('reg-phone', 'Phone number is required.');
    valid = false;
  } else if (!/^\d{10}$/.test(phone)) {
    showFieldError('reg-phone', 'Enter a valid 10-digit phone number.');
    valid = false;
  }

  if (!gender) {
    showFieldError('reg-gender', 'Please select your gender.');
    valid = false;
  }

  if (!valid) return;

  setRegisterLoading(true);

  const payload = { name, email, password, phone, gender };
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
          gender:        'reg-gender',
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

// ── Real-time Validation (on blur + input) ─────────────────────

document.addEventListener('DOMContentLoaded', () => {

  // Clear on input (existing behaviour)
  ['reg-name','reg-email','reg-password','reg-phone',
   'reg-gender','reg-city','reg-bio','reg-social'].forEach(id => {
    const el = document.getElementById(id);
    if (el) el.addEventListener('input', () => clearFieldError(id));
    if (el) el.addEventListener('change', () => clearFieldError(id));
  });

  ['login-email','login-password'].forEach(id => {
    const el = document.getElementById(id);
    if (el) el.addEventListener('input', () => clearFieldError(id));
  });

  // ── Login: validate on blur (when user leaves the field) ──────

  document.getElementById('login-email').addEventListener('blur', () => {
    const val = document.getElementById('login-email').value.trim();
    if (!val) return; // don't nag on empty until submit
    if (!isValidEmail(val)) {
      showFieldError('login-email', 'Enter a valid email address');
    }
  });

  document.getElementById('login-password').addEventListener('blur', () => {
    const val = document.getElementById('login-password').value;
    if (!val) return;
    if (val.length < 8) {
      showFieldError('login-password', 'Password must be at least 8 characters.');
    }
  });

  // ── Register: validate on blur ────────────────────────────────

  document.getElementById('reg-name').addEventListener('blur', () => {
    const val = document.getElementById('reg-name').value.trim();
    if (!val) return;
    if (val.length < 2) showFieldError('reg-name', 'Name must be at least 2 characters.');
  });

  document.getElementById('reg-email').addEventListener('blur', () => {
    const val = document.getElementById('reg-email').value.trim();
    if (!val) return;
    if (!isValidEmail(val)) {
      showFieldError('reg-email', 'Enter a valid email address.');
    } else if (!isGmailEmail(val)) {
      showFieldError('reg-email', 'Only Gmail addresses are accepted.');
    }
  });

  document.getElementById('reg-password').addEventListener('blur', () => {
    const val = document.getElementById('reg-password').value;
    if (!val) return;
    const errors = getPasswordErrors(val);
    if (errors.length > 0) {
      showFieldError('reg-password', `Password must have ${errors.join(', ')}.`);
    }
  });

  // Live password strength as user types
  document.getElementById('reg-password').addEventListener('input', () => {
    const val = document.getElementById('reg-password').value;
    if (!val) { clearFieldError('reg-password'); return; }
    const errors = getPasswordErrors(val);
    if (errors.length === 0) {
      clearFieldError('reg-password');
      // Show a subtle success hint
      const errEl = document.getElementById('reg-password-error');
      errEl.textContent = '✓ Strong password';
      errEl.style.display = 'flex';
      errEl.style.color = 'var(--success)';
    } else if (val.length >= 4) {
      // Only show errors after they've typed a bit
      showFieldError('reg-password', `Still needs: ${errors.join(', ')}.`);
      document.getElementById('reg-password-error').style.color = 'var(--error)';
    }
  });

  document.getElementById('reg-phone').addEventListener('blur', () => {
    const val = document.getElementById('reg-phone').value.trim();
    if (!val) return;
    if (!/^\d{10}$/.test(val)) {
      showFieldError('reg-phone', 'Enter a valid 10-digit phone number.');
    }
  });
});