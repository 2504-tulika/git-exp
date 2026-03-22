'use strict';

// Product Data 
const PRODUCTS_DEFAULT = [
  { id:1,  name:'Rose Glow Vitamin C Serum',     category:'Skincare',  brand:'Lumière',   price:2499, stock:18, desc:'Brightening serum with 15% ascorbic acid.',      sku:'LMR-001', restock:5,  image:'' },
  { id:2,  name:'Velvet Matte Lipstick',          category:'Makeup',    brand:'NoirLab',   price:799,  stock:43, desc:'Long-lasting matte in 24 rich shades.',          sku:'NRL-002', restock:10, image:'' },
  { id:3,  name:'Midnight Bloom Parfum',          category:'Fragrance', brand:'Éclat',     price:5999, stock:9,  desc:'Oud, black rose and sandalwood.',                sku:'ECL-003', restock:3,  image:'' },
  { id:4,  name:'Argan Silk Hair Mask',           category:'Haircare',  brand:'SilkRoots', price:1299, stock:2,  desc:'Nourishing mask with argan oil and keratin.',    sku:'SLK-004', restock:5,  image:'' },
  { id:5,  name:'Crystal Dew Moisturiser',        category:'Skincare',  brand:'Lumière',   price:1899, stock:31, desc:'Lightweight gel moisturiser with hyaluronic acid.', sku:'LMR-005', restock:8, image:'' },
  { id:6,  name:'Satin Finish Foundation',        category:'Makeup',    brand:'NoirLab',   price:1599, stock:0,  desc:'Full-coverage foundation with SPF 25.',          sku:'NRL-006', restock:6,  image:'' },
  { id:7,  name:'Lavender Dream Body Oil',        category:'Wellness',  brand:'AuraBliss', price:999,  stock:15, desc:'Calming oil with lavender and chamomile.',       sku:'AUR-007', restock:5,  image:'' },
  { id:8,  name:'Peptide Eye Cream',              category:'Skincare',  brand:'Lumière',   price:3299, stock:7,  desc:'Triple-peptide technology for fine lines.',      sku:'LMR-008', restock:4,  image:'' },
  { id:9,  name:'Brow Sculptor Kit',              category:'Makeup',    brand:'NoirLab',   price:649,  stock:3,  desc:'Precision pencil and setting gel duo.',          sku:'NRL-009', restock:5,  image:'' },
  { id:10, name:'Citrus Burst Body Wash',         category:'Wellness',  brand:'AuraBliss', price:549,  stock:22, desc:'Energising gel with natural citrus extracts.',   sku:'AUR-010', restock:7,  image:'' },
  { id:11, name:'Amber Oud Eau de Parfum',        category:'Fragrance', brand:'Éclat',     price:7499, stock:0,  desc:'Oriental fragrance for lasting presence.',       sku:'ECL-011', restock:2,  image:'' },
  { id:12, name:'Castor Growth Hair Serum',       category:'Haircare',  brand:'SilkRoots', price:899,  stock:11, desc:'Scalp serum with cold-pressed castor oil.',      sku:'SLK-012', restock:5,  image:'' },
  { id:13, name:'Hyaluronic Glow Toner',          category:'Skincare',  brand:'Lumière',   price:1499, stock:4,  desc:'Plumping toner for deeper absorption.',          sku:'LMR-013', restock:6,  image:'' },
  { id:14, name:'Liquid Highlighter Drops',       category:'Makeup',    brand:'NoirLab',   price:1149, stock:19, desc:'Buildable glow drops for face and body.',        sku:'NRL-014', restock:5,  image:'' },
  { id:15, name:'Jasmine Neroli Eau de Toilette', category:'Fragrance', brand:'Éclat',     price:3999, stock:6,  desc:'Neroli, jasmine and white musk.',                sku:'ECL-015', restock:3,  image:'' },
];

// Category icons and colors
const ICONS = {
  Skincare:  'fa-droplet',
  Makeup:    'fa-wand-magic-sparkles',
  Fragrance: 'fa-wind',
  Haircare:  'fa-scissors',
  Wellness:  'fa-spa'
};

const COLORS = {
  Skincare:  '#3a9c8f',
  Makeup:    '#c9697a',
  Fragrance: '#8a6bc9',
  Haircare:  '#c9923a',
  Wellness:  '#4a9c6d'
};

const CATS = ['Skincare', 'Makeup', 'Fragrance', 'Haircare', 'Wellness'];

// Helper Functions

// Get element by ID
function el(id) {
  return document.getElementById(id);
}

// Set text content of an element
function setText(id, value) {
  const elem = el(id);
  if (elem) elem.textContent = value;
}

// Save data to localStorage
function save() {
  localStorage.setItem('nn_products', JSON.stringify(products));
  localStorage.setItem('nn_nextId', nextId);
  localStorage.setItem('nn_profile', JSON.stringify(profile));
}


async function init() {
  // Load saved data from localStorage
  const savedProducts = localStorage.getItem('nn_products');
  const savedId       = localStorage.getItem('nn_nextId');
  const savedProfile  = localStorage.getItem('nn_profile');

  if (savedProducts) products = JSON.parse(savedProducts);
  else products = JSON.parse(JSON.stringify(PRODUCTS_DEFAULT));

  if (savedId)      nextId  = parseInt(savedId);
  if (savedProfile) profile = JSON.parse(savedProfile);

  // Apply dark mode if saved
  if (localStorage.getItem('nn_dark') === '1') {
    document.documentElement.setAttribute('data-theme', 'dark');
    const toggle = el('darkToggle');
    if (toggle) toggle.checked = true;
  }

  loadProfile();
  setGreeting();
  buildNotifications();

  // Show loading spinner for a moment (simulates API fetch)
  await simulateLoad();

  renderAll();
  bindEvents();
}

// Show/hide loading spinner
function simulateLoad() {
  return new Promise(resolve => {
    el('loadingState').classList.remove('hidden');
    setTimeout(() => {
      el('loadingState').classList.add('hidden'); resolve();}, 900);
  });
}

// Update topbar and sidebar with profile info
function loadProfile() {
  const initials = (profile.name || 'A').split(' ').map(w => w[0]).join('').slice(0, 2).toUpperCase();

  ['ddAvatar', 'modalAvatar'].forEach(id => {
    const elem = el(id);
    if (elem) elem.textContent = initials;
  });

  // Update topbar admin button
  const topbarAv = el('adminPill')?.querySelector('.av');
  if (topbarAv) topbarAv.textContent = initials;

  setText('topbarName', profile.name);
  setText('topbarRole', profile.role);
  setText('ddName',     profile.name);
  setText('ddEmail',    profile.email);
  setText('ddName2',    profile.name);
}

// Render all sections
function renderAll() {
  renderDashboard();
  renderProducts();
  renderAnalytics();
  updateBadges();
}


// ---- Notifications ----

function buildNotifications() {
  notifications = [];

  const outOfStock = products.filter(p => p.stock === 0);
  const lowStock   = products.filter(p => p.stock > 0 && p.stock < 5);

  outOfStock.forEach(p => {
    notifications.push({
      type: 'danger', icon: 'fa-ban',
      title: 'Out of Stock',
      desc:  `${p.name} needs restocking immediately.`,
      time:  'Now', unread: true
    });
  });

  lowStock.forEach(p => {
    notifications.push({
      type: 'warn', icon: 'fa-triangle-exclamation',
      title: 'Low Stock Alert',
      desc:  `${p.name} — only ${p.stock} unit${p.stock > 1 ? 's' : ''} left.`,
      time:  'Today', unread: true
    });
  });

  if (!notifications.length) {
    notifications.push({
      type: 'success', icon: 'fa-circle-check',
      title: 'All Stocked!',
      desc:  'All products are well stocked.',
      time:  'Now', unread: false
    });
  }

  renderNotifications();
}

function renderNotifications() {
  const unreadCount = notifications.filter(n => n.unread).length;
  const badge       = el('notifBadge');
  if (badge) badge.textContent = unreadCount || '';

  const list = el('notifList');
  if (!list) return;

  list.innerHTML = notifications.map((notif, i) => `
    <li class="notif-item ${notif.unread ? 'unread' : ''}" onclick="markNotifRead(${i})">
      <div class="notif-icon ${notif.type}"><i class="fa-solid ${notif.icon}"></i></div>
      <div>
        <div class="notif-title">${notif.title}</div>
        <div class="notif-desc">${notif.desc}</div>
        <div class="notif-time">${notif.time}</div>
      </div>
    </li>
  `).join('');
}

function markNotifRead(index) {
  notifications[index].unread = false;
  renderNotifications();
}


// Navigations (Page) 

function navigateTo(page) {
  // Hide all pages
  document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));

  // Remove active from all nav items
  document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));

  // Show selected page
  el('page-' + page)?.classList.add('active');

  // Mark correct nav item as active
  document.querySelector(`.nav-item[data-page="${page}"]`)?.classList.add('active');

  setText('NNPage', page.charAt(0).toUpperCase() + page.slice(1).replace('-', ' '));

  if (page === 'products')  renderProducts(); //if needed refresh
  if (page === 'analytics') renderAnalytics();

  // Close sidebar on mobile
  if (window.innerWidth < 768) {
    document.body.classList.remove('sidebar-open');
  }
}

function renderDashboard() {
  const total = products.length;
  const value = products.reduce((sum, p) => sum + p.price * p.stock, 0);
  const low   = products.filter(p => p.stock > 0 && p.stock < 5).length;
  const out   = products.filter(p => p.stock === 0).length;

  // Update KPI cards
  setText('statTotal',      total);
  setText('statValue',      '₹' + fmt(value));
  setText('statLowStock',   low);
  setText('statOutOfStock', out);

  // Update sidebar stats
  setText('sideTotal', total);
  setText('sideLow',   low);
  setText('sideOut',   out);

  // Animate the low/out of stock KPI bars
  const lowFill = el('kpiLowBar')?.querySelector('.kpi-fill');
  const outFill = el('kpiOutBar')?.querySelector('.kpi-fill');
  if (lowFill) lowFill.style.width = total ? (low / total * 100) + '%' : '0%';
  if (outFill) outFill.style.width = total ? (out / total * 100) + '%' : '0%';

  renderCategoryBars();
  renderTopValue('dashTopValue', 5);
  renderRecentProducts();
  renderDashAlerts();
}

// Category horizontal bar chart
function renderCategoryBars() {
  const counts = {};
  CATS.forEach(c => counts[c] = 0);
  products.forEach(p => {
    if (counts[p.category] !== undefined) counts[p.category]++;
  });

  const max = Math.max(...Object.values(counts), 1);
  const container = el('catBars');
  if (!container) return;

  container.innerHTML = CATS.map(cat => `
    <div>
      <div class="cbar-top">
        <span class="cbar-name" style="color:${COLORS[cat]}">
          <i class="fa-solid ${ICONS[cat]}"></i> ${cat}
        </span>
        <span class="cbar-count">${counts[cat]} items</span>
      </div>
      <div class="bar-track">
        <div class="bar-fill" style="width:${(counts[cat] / max) * 100}%; background:${COLORS[cat]}"></div>
      </div>
    </div>
  `).join('');
}