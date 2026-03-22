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

// Top products by total value (price × stock)
function renderTopValue(containerId, limit) {
  const sorted = [...products]
    .map(p => ({ ...p, totalValue: p.price * p.stock }))
    .sort((a, b) => b.totalValue - a.totalValue)
    .slice(0, limit);

  const container = el(containerId);
  if (!container) return;

  container.innerHTML = sorted.map((p, i) => `
    <li class="mini-item">
      <div class="mini-rank ${['g1', 'g2', 'g3'][i] || ''}">${i + 1}</div>
      <div class="mini-icon" style="background:${COLORS[p.category]}22; color:${COLORS[p.category]}">
        <i class="fa-solid ${ICONS[p.category]}"></i>
      </div>
      <div>
        <div class="mini-name">${esc(p.name)}</div>
        <div class="mini-sub">${p.category} · Stock: ${p.stock}</div>
      </div>
      <span class="mini-val">₹${fmt(p.totalValue)}</span>
    </li>
  `).join('');
}

// Recently added products
function renderRecentProducts() {
  const container = el('recentList');
  if (!container) return;

  container.innerHTML = [...products].slice(-6).reverse().map(p => `
    <li class="mini-item">
      <div class="mini-icon" style="background:${COLORS[p.category]}22; color:${COLORS[p.category]}">
        <i class="fa-solid ${ICONS[p.category]}"></i>
      </div>
      <div>
        <div class="mini-name">${esc(p.name)}</div>
        <div class="mini-sub">${esc(p.brand || '')} · ${p.category}</div>
      </div>
      <span class="mini-val">₹${fmt(p.price)}</span>
    </li>
  `).join('');
}

// Dashboard stock alerts
function renderDashAlerts() {
  const alerts    = products.filter(p => p.stock < 5).sort((a, b) => a.stock - b.stock).slice(0, 5);
  const container = el('dashAlerts');
  if (!container) return;

  if (!alerts.length) {
    container.innerHTML = '<li style="padding:1rem; text-align:center; font-size:.8rem; color:var(--text-muted)"><i class="fa-solid fa-circle-check" style="color:var(--success)"></i> All stocked!</li>';
    return;
  }

  container.innerHTML = alerts.map(p => `
    <li class="alert-item">
      <span class="alert-dot ${p.stock === 0 ? 'danger' : 'warn'}"></span>
      <span class="alert-name">${esc(p.name)}</span>
      <span class="alert-pill ${p.stock === 0 ? 'danger' : 'warn'}">${p.stock === 0 ? 'Out' : p.stock + ' left'}</span>
    </li>
  `).join('');
}

// Products Page
function getFilteredProducts() {
  let list = [...products];

  // Text search
  if (searchQuery) {
    const query = searchQuery.toLowerCase();
    list = list.filter(p =>
      p.name.toLowerCase().includes(query) ||
      p.category.toLowerCase().includes(query) ||
      (p.brand || '').toLowerCase().includes(query) ||
      (p.sku || '').toLowerCase().includes(query)
    );
  }

  // Category filter
  if (activeCat !== 'all') {
    list = list.filter(p => p.category === activeCat);
  }

  // Stock filter
  if      (activeStock === 'instock') list = list.filter(p => p.stock > 4);
  else if (activeStock === 'low')     list = list.filter(p => p.stock > 0 && p.stock < 5);
  else if (activeStock === 'out')     list = list.filter(p => p.stock === 0);

  // Sorting
  if      (activeSort === 'price-asc')  list.sort((a, b) => a.price - b.price);
  else if (activeSort === 'price-desc') list.sort((a, b) => b.price - a.price);
  else if (activeSort === 'name-asc')   list.sort((a, b) => a.name.localeCompare(b.name));
  else if (activeSort === 'stock-asc')  list.sort((a, b) => a.stock - b.stock);
  else if (activeSort === 'value-desc') list.sort((a, b) => (b.price * b.stock) - (a.price * a.stock));

  return list;
}

function renderProducts() {
  const grid      = el('productGrid');
  const emptyMsg  = el('emptyState');
  if (!grid) return;

  const list = getFilteredProducts();

  // Update results count label
  setText('resultsLabel', `${list.length} item${list.length !== 1 ? 's' : ''} found`);

  if (!list.length) {
    grid.innerHTML = '';
    emptyMsg?.classList.remove('hidden');
    return;
  }

  emptyMsg?.classList.add('hidden');

  // Apply view mode classes
  grid.className = 'product-grid' + (isListMode ? ' list-mode' : '') + (isCompact ? ' compact' : '');

  grid.innerHTML = list.map((product, index) => buildProductCard(product, index)).join('');
}

// Build HTML for a single product card
function buildProductCard(p, index) {
  const stockClass = p.stock === 0 ? 'out' : p.stock < 5 ? 'low' : 'in';
  const stockLabel = p.stock === 0 ? 'Out of Stock' : p.stock < 5 ? `Low: ${p.stock}` : `Stock: ${p.stock}`;

  const ribbon = p.stock === 0
    ? '<span class="pcard-ribbon ribbon-out">Out</span>'
    : p.stock < 5
    ? '<span class="pcard-ribbon ribbon-low">Low</span>'
    : '';

  const imageHTML = p.image
    ? `<img src="${esc(p.image)}" alt="${esc(p.name)}" loading="lazy">`
    : `<div class="pcard-ph" style="background:${COLORS[p.category]}18">
         <i class="fa-solid ${ICONS[p.category]}" style="color:${COLORS[p.category]}; font-size:2rem; opacity:.7"></i>
       </div>`;

  return `
    <div class="product-card" data-id="${p.id}" style="--delay:${index * 0.04}s">
      <div class="pcard-img">
        ${imageHTML}
        ${ribbon}
        <div class="pcard-actions">
          <button class="pac-btn edit" onclick="openEdit(${p.id})" title="Edit"><i class="fa-solid fa-pen"></i></button>
          <button class="pac-btn del"  onclick="confirmDelete(${p.id})" title="Delete"><i class="fa-solid fa-trash"></i></button>
        </div>
      </div>
      <div class="pcard-body">
        <div class="pcard-cat">${esc(p.category)}</div>
        <div class="pcard-name">${esc(p.name)}</div>
        <div class="pcard-brand">${esc(p.brand || '')}${p.sku ? ' · ' + esc(p.sku) : ''}</div>
        ${p.desc ? `<p class="pcard-desc">${esc(p.desc)}</p>` : ''}
        <div class="pcard-foot">
          <span class="pcard-price">₹${fmt(p.price)}</span>
          <span class="stock-pill ${stockClass}">${stockLabel}</span>
        </div>
      </div>
    </div>
  `;
}

// Clear all active filters and reset products view
function clearFilters() {
  searchQuery = '';
  activeCat   = 'all';
  activeStock = 'all';
  el('searchInput').value = '';
  document.querySelectorAll('.chip').forEach(c => c.classList.remove('active'));
  document.querySelector('.chip[data-stock="all"]')?.classList.add('active');
  renderProducts();
}

// ---- Analytics Page ----

function renderAnalytics() {
  const total = products.length;
  const value = products.reduce((sum, p) => sum + p.price * p.stock, 0);
  const avg   = total ? products.reduce((sum, p) => sum + p.price, 0) / total : 0;

  // KPI summary row
  const kpiContainer = el('analyticsKpi');
  if (kpiContainer) {
    const kpis = [
      { icon: 'fa-boxes-stacked',      bg: 'var(--teal-light)',    color: 'var(--teal)',    label: 'Total Products',  value: total,             sub: CATS.filter(c => products.find(p => p.category === c)).length + ' categories' },
      { icon: 'fa-indian-rupee-sign',  bg: 'var(--primary-light)', color: 'var(--primary)', label: 'Inventory Value', value: '₹' + fmt(value),  sub: 'Price × Stock' },
      { icon: 'fa-chart-simple',       bg: 'var(--gold-light)',     color: 'var(--gold)',    label: 'Avg. Price',      value: '₹' + fmt(Math.round(avg)), sub: 'All products' },
    ];
    kpiContainer.innerHTML = kpis.map(k => `
      <div class="akpi">
        <div class="akpi-icon" style="background:${k.bg}; color:${k.color}">
          <i class="fa-solid ${k.icon}"></i>
        </div>
        <div>
          <div class="akpi-label">${k.label}</div>
          <div class="akpi-val">${k.value}</div>
          <div class="akpi-sub">${k.sub}</div>
        </div>
      </div>
    `).join('');
  }

  // Category performance cards
  const catContainer = el('catIntel');
  if (catContainer) {
    const maxCount = Math.max(...CATS.map(c => products.filter(p => p.category === c).length), 1);

    catContainer.innerHTML = CATS.map(cat => {
      const items     = products.filter(p => p.category === cat);
      const catValue  = items.reduce((sum, p) => sum + p.price * p.stock, 0);
      const count     = items.length;

      return `
        <div class="cat-intel-card">
          <div class="cic-icon" style="background:${COLORS[cat]}22; color:${COLORS[cat]}">
            <i class="fa-solid ${ICONS[cat]}"></i>
          </div>
          <div class="cic-name">${cat}</div>
          <div class="cic-count">${count}</div>
          <div class="cic-value">₹${fmt(catValue)} value</div>
          <div class="cic-bar bar-track">
            <div class="bar-fill" style="width:${(count / maxCount) * 100}%; background:${COLORS[cat]}"></div>
          </div>
        </div>
      `;
    }).join('');
  }

  // Top by value list
  renderTopValue('rankList', 8);

  // Stock alerts list
  const alerts       = products.filter(p => p.stock < 5).sort((a, b) => a.stock - b.stock).slice(0, 8);
  const alertContainer = el('alertList');
  setText('alertCount', alerts.length || '');

  if (alertContainer) {
    if (!alerts.length) {
      alertContainer.innerHTML = '<li style="padding:1.2rem; text-align:center; font-size:.81rem; color:var(--text-muted)"><i class="fa-solid fa-circle-check" style="color:var(--success)"></i> All products stocked!</li>';
    } else {
      alertContainer.innerHTML = alerts.map(p => `
        <li class="rank-item">
          <div class="rank-dot" style="background:${p.stock === 0 ? 'var(--danger)' : 'var(--amber)'}"></div>
          <span class="rank-name">${esc(p.name)}</span>
          <span class="rank-val" style="color:${p.stock === 0 ? 'var(--danger)' : 'var(--amber)'}">
            ${p.stock === 0 ? 'Out' : p.stock + ' left'}
          </span>
        </li>
      `).join('');
    }
  }

  // Price distribution bar chart
  const buckets = [
    { label: '₹0 – ₹500',       min: 0,    max: 500 },
    { label: '₹501 – ₹1,500',   min: 501,  max: 1500 },
    { label: '₹1,501 – ₹3,000', min: 1501, max: 3000 },
    { label: '₹3,001 – ₹7,000', min: 3001, max: 7000 },
    { label: '₹7,000+',         min: 7001, max: Infinity },
  ];

  const priceContainer = el('priceDist');
  if (priceContainer) {
    const maxCount = Math.max(...buckets.map(b => products.filter(p => p.price >= b.min && p.price <= b.max).length), 1);

    priceContainer.innerHTML = buckets.map(b => {
      const count = products.filter(p => p.price >= b.min && p.price <= b.max).length;
      return `
        <div class="pd-bucket">
          <div class="pd-label">${b.label}</div>
          <div class="pd-track">
            <div class="pd-fill" style="width:${(count / maxCount) * 100}%">${count}</div>
          </div>
        </div>
      `;
    }).join('');
  }
}


// ---- Add Product Form ----

function submitProduct() {
  const name     = el('fName').value.trim();
  const category = el('fCategory').value;
  const brand    = el('fBrand').value.trim();
  const price    = parseFloat(el('fPrice').value);
  const stock    = parseInt(el('fStock').value);
  const desc     = el('fDesc').value.trim();
  const image    = el('fImage').value.trim();
  const sku      = el('fSku').value.trim();
  const restock  = parseInt(el('fRestock').value) || 5;

  // Validation
  if (!name)                      { toast('Product name is required.', 'error'); return; }
  if (!category)                  { toast('Please select a category.', 'error'); return; }
  if (isNaN(price) || price < 0)  { toast('Enter a valid price.', 'error');     return; }
  if (isNaN(stock) || stock < 0)  { toast('Enter a valid stock quantity.', 'error'); return; }

  products.push({ id: nextId++, name, category, brand, price, stock, desc, image, sku, restock });

  save();
  buildNotifications();
  renderAll();
  clearForm();
  navigateTo('products');
  toast(`"${name}" added to inventory!`, 'success');
}

function clearForm() {
  ['fName', 'fBrand', 'fPrice', 'fStock', 'fDesc', 'fImage', 'fSku', 'fRestock'].forEach(id => {
    const elem = el(id);
    if (elem) elem.value = '';
  });
  el('fCategory').value = '';
  updatePreview();
}

// Update live preview card while typing
function updatePreview() {
  const name     = el('fName')?.value     || 'Product Name';
  const category = el('fCategory')?.value || 'Category';
  const brand    = el('fBrand')?.value    || 'Brand';
  const price    = parseFloat(el('fPrice')?.value) || 0;
  const stock    = parseInt(el('fStock')?.value)   || 0;
  const image    = el('fImage')?.value    || '';

  setText('prevName',  name);
  setText('prevCat',   category);
  setText('prevBrand', brand);
  setText('prevPrice', '₹' + fmt(price));

  const stockPill = el('prevStock');
  if (stockPill) {
    stockPill.className  = 'stock-pill ' + (stock === 0 ? 'out' : stock < 5 ? 'low' : 'in');
    stockPill.textContent = stock === 0 ? 'Out of Stock' : stock < 5 ? `Low: ${stock}` : `Stock: ${stock}`;
  }

  const previewImg = el('previewPh');
  if (previewImg) {
    previewImg.innerHTML = image
      ? `<img src="${esc(image)}" style="width:100%; height:100%; object-fit:cover">`
      : `<i class="fa-solid ${ICONS[category] || 'fa-image'}" style="color:${COLORS[category] || 'var(--border-dark)'}; font-size:2rem"></i>`;
  }
}


// ---- Edit Product ----

function openEdit(id) {
  const product = products.find(p => p.id === id);
  if (!product) return;

  el('editId').value       = id;
  el('editName').value     = product.name;
  el('editCategory').value = product.category;
  el('editBrand').value    = product.brand   || '';
  el('editPrice').value    = product.price;
  el('editStock').value    = product.stock;
  el('editDesc').value     = product.desc    || '';

  openModal('editModal');
}

function saveEdit() {
  const id       = parseInt(el('editId').value);
  const name     = el('editName').value.trim();
  const category = el('editCategory').value;
  const brand    = el('editBrand').value.trim();
  const price    = parseFloat(el('editPrice').value);
  const stock    = parseInt(el('editStock').value);
  const desc     = el('editDesc').value.trim();

  if (!name || isNaN(price) || isNaN(stock)) {
    toast('Please fill in all fields.', 'error');
    return;
  }

  const index = products.findIndex(p => p.id === id);
  if (index > -1) {
    products[index] = { ...products[index], name, category, brand, price, stock, desc };
    save();
    buildNotifications();
    renderAll();
    closeModal('editModal');
    toast('Product updated successfully!', 'success');
  }
}


// Delete Product 

function confirmDelete(id) {
  const product = products.find(p => p.id === id);
  if (!product) return;

  setText('confirmMsg', `Delete "${product.name}"? This cannot be undone.`);

  confirmCb = () => {
    products = products.filter(p => p.id !== id);
    save();
    buildNotifications();
    renderAll();
    toast('Product deleted.', 'warn');
  };

  openModal('confirmModal');
}

//Search Bar
function renderSearchDropdown(query) {
  const resultsBox = el('searchResults');
  if (!resultsBox) return;

  if (!query) {
    resultsBox.classList.remove('open');
    return;
  }

  const matches = products.filter(p =>
    p.name.toLowerCase().includes(query) ||
    (p.brand || '').toLowerCase().includes(query) ||
    p.category.toLowerCase().includes(query)
  ).slice(0, 6);

  if (!matches.length) {
    resultsBox.innerHTML = `<div class="sr-empty"><i class="fa-solid fa-magnifying-glass"></i> No results for "${esc(query)}"</div>`;
  } else {
    resultsBox.innerHTML = matches.map(p => `
      <div class="sr-item" onclick="searchGoTo(${p.id})">
        <div class="sr-icon" style="background:${COLORS[p.category]}22; color:${COLORS[p.category]}">
          <i class="fa-solid ${ICONS[p.category]}"></i>
        </div>
        <div>
          <div class="sr-name">${esc(p.name)}</div>
          <div class="sr-meta">${p.category} · ${p.brand || '—'} · Stock: ${p.stock}</div>
        </div>
        <span class="sr-price">₹${fmt(p.price)}</span>
      </div>
    `).join('');
  }

  resultsBox.classList.add('open');
}

// Jump to a product card from search
function searchGoTo(id) {
  el('searchResults').classList.remove('open');
  searchQuery = '';
  el('searchInput').value = '';
  activeCat   = 'all';
  activeStock = 'all';
  navigateTo('products');

  setTimeout(() => {
    const card = document.querySelector(`.product-card[data-id="${id}"]`);
    if (card) {
      card.scrollIntoView({ behavior: 'smooth', block: 'center' });
      card.style.outline = '2px solid var(--primary)';
      setTimeout(() => card.style.outline = '', 1800);
    }
  }, 300);
}


// Export CSV 

function exportCSV() {
  const header = ['ID', 'Name', 'Category', 'Brand', 'Price', 'Stock', 'SKU', 'Total Value'];
  const rows   = products.map(p => [
    p.id, `"${p.name}"`, p.category, `"${p.brand || ''}"`,
    p.price, p.stock, `"${p.sku || ''}"`, p.price * p.stock
  ]);

  const csv  = [header, ...rows].map(r => r.join(',')).join('\n');
  const blob = new Blob([csv], { type: 'text/csv' });
  const link = document.createElement('a');
  link.href     = URL.createObjectURL(blob);
  link.download = 'novanest-inventory.csv';
  link.click();
  URL.revokeObjectURL(link.href);

  toast('Exported as CSV!', 'success');
}


// Sidebar Badges

function updateBadges() {
  setText('badge-all', products.length);
  CATS.forEach(cat => {
    setText('badge-' + cat, products.filter(p => p.category === cat).length);
  });
}


// Modals 

function openModal(id) {
  el(id)?.classList.remove('hidden');
  document.body.style.overflow = 'hidden';
}

function closeModal(id) {
  el(id)?.classList.add('hidden');
  document.body.style.overflow = '';
}


// Dropdown Panels

function closeAllPanels() {
  ['notifPanel', 'settingsPanel', 'adminDropdown'].forEach(id => {
    el(id)?.classList.remove('open');
  });
  el('overlay')?.classList.remove('show');
  el('searchResults')?.classList.remove('open');
}

function togglePanel(id) {
  const panel    = el(id);
  const isOpen   = panel.classList.contains('open');
  closeAllPanels();
  if (!isOpen) {
    panel.classList.add('open');
    el('overlay').classList.add('show');
  }
}


// Notifications

function toast(message, type = '') {
  const icons = {
    success: 'fa-circle-check',
    error:   'fa-circle-xmark',
    warn:    'fa-triangle-exclamation',
    '':      'fa-circle-info'
  };

  const div = document.createElement('div');
  div.className = `toast ${type}`;
  div.innerHTML = `<i class="fa-solid ${icons[type] || icons['']}"></i> ${message}`;

  el('toastStack').appendChild(div);

  // Animate in
  requestAnimationFrame(() => {
    requestAnimationFrame(() => div.classList.add('show'));
  });

  // Remove after 3 seconds
  setTimeout(() => {
    div.classList.add('out');
    setTimeout(() => div.remove(), 300);
  }, 3000);
}
