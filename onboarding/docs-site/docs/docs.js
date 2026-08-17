// NIB Docs, small interactions: anchor links, scrollspy
(function () {
  // 1. Add # anchor pseudo-links to every h2/h3/h4 with an id
  document.querySelectorAll('.doc-main h2[id], .doc-main h3[id], .doc-main h4[id]').forEach(function (h) {
    var a = document.createElement('a');
    a.className = 'doc-anchor';
    a.href = '#' + h.id;
    a.setAttribute('aria-label', 'Link to ' + h.textContent.trim());
    a.textContent = '#';
    a.addEventListener('click', function (e) {
      // Update URL hash & copy to clipboard
      var url = location.origin + location.pathname + '#' + h.id;
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(url).catch(function () {});
      }
    });
    h.appendChild(a);
  });

  // 2. Scrollspy, highlight current section in sidebar
  var sidebarLinks = Array.from(document.querySelectorAll('.doc-sidebar__list a[href^="#"]'));
  if (!sidebarLinks.length) return;
  var headings = sidebarLinks.map(function (a) {
    var id = a.getAttribute('href').slice(1);
    return { id: id, el: document.getElementById(id), link: a };
  }).filter(function (x) { return x.el; });

  function onScroll() {
    var y = window.scrollY + 120;
    var active = headings[0];
    for (var i = 0; i < headings.length; i++) {
      if (headings[i].el.offsetTop <= y) active = headings[i];
    }
    sidebarLinks.forEach(function (a) { a.classList.remove('is-active'); });
    if (active) active.link.classList.add('is-active');
  }
  var ticking = false;
  window.addEventListener('scroll', function () {
    if (!ticking) {
      window.requestAnimationFrame(function () { onScroll(); ticking = false; });
      ticking = true;
    }
  });
  onScroll();
})();
