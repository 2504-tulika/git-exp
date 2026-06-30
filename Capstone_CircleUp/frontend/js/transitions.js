(function () {
  // Inject the transition stylesheet once
  const style = document.createElement('style');
  style.textContent = `
    body { opacity: 0; transition: opacity 320ms cubic-bezier(0.4,0,0.2,1); }
    body.visible { opacity: 1; }
    body.leaving { opacity: 0; }
  `;
  document.head.appendChild(style);

  // Fade in on load
  window.addEventListener('DOMContentLoaded', () => {
    requestAnimationFrame(() => {
      requestAnimationFrame(() => {
        document.body.classList.add('visible');
      });
    });
  });

  // Intercept internal navigation links
  document.addEventListener('click', (e) => {
    const a = e.target.closest('a[href]');
    if (!a) return;
    const href = a.getAttribute('href');
    // Only handle relative links, skip hash-only and external
    if (!href || href.startsWith('http') || href.startsWith('//') || href.startsWith('#')) return;
    e.preventDefault();
    document.body.classList.remove('visible');
    document.body.classList.add('leaving');
    setTimeout(() => { window.location.href = href; }, 340);
  });
})();
