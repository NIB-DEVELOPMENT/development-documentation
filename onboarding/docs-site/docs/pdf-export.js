// NIB Docs — programmatic PDF export
// Click the ↓ PDF button → renders the doc to JPEG pages and assembles a real PDF using html2canvas + jsPDF.
// No browser print dialog involved. Triggers a direct download.

(function () {
  let loading = null;

  async function loadOnce() {
    if (loading) return loading;
    loading = (async () => {
      await injectScript('https://cdn.jsdelivr.net/npm/html2canvas@1.4.1/dist/html2canvas.min.js');
      await injectScript('https://cdn.jsdelivr.net/npm/jspdf@2.5.1/dist/jspdf.umd.min.js');
    })();
    return loading;
  }

  function injectScript(src) {
    return new Promise((res, rej) => {
      const s = document.createElement('script');
      s.src = src; s.onload = res; s.onerror = rej;
      document.head.appendChild(s);
    });
  }

  // Capture the current doc's main column at A4 ratio, paginate, and trigger download.
  async function exportPDF(filename) {
    const btn = document.querySelector('.doc-topbar__pdf');
    const originalText = btn ? btn.innerHTML : '';
    if (btn) { btn.style.pointerEvents = 'none'; btn.innerHTML = 'Building…'; }
    try {
      await loadOnce();

      // Snapshot & hide chrome so it doesn't appear in the PDF
      const sidebar = document.querySelector('.doc-sidebar');
      const topbar  = document.querySelector('.doc-topbar');
      const footer  = document.querySelector('.doc-footer');
      const layout  = document.querySelector('.doc-layout');
      const main    = document.querySelector('.doc-main');
      const savedDisplays = {
        sidebar: sidebar ? sidebar.style.display : '',
        topbar:  topbar  ? topbar.style.display  : '',
        footer:  footer  ? footer.style.display  : '',
        layoutCss: layout ? layout.style.cssText : '',
        mainCss:   main   ? main.style.cssText   : '',
      };
      if (sidebar) sidebar.style.display = 'none';
      if (topbar)  topbar.style.display  = 'none';
      if (footer)  footer.style.display  = 'none';
      if (layout)  layout.style.cssText  = 'display:block;max-width:none;padding:0;margin:0';
      if (main) {
        main.style.cssText = 'max-width:none;margin:0 auto;padding:24px 36px;width:auto;';
      }

      // Wait for layout + fonts
      if (document.fonts && document.fonts.ready) { try { await document.fonts.ready; } catch (e) {} }
      await new Promise(r => setTimeout(r, 250));

      const { jsPDF } = window.jspdf;
      const pdf = new jsPDF({ unit: 'pt', format: 'a4', orientation: 'portrait', compress: true });
      const pageW = pdf.internal.pageSize.getWidth();   // 595
      const pageH = pdf.internal.pageSize.getHeight();  // 842
      const scrollW = document.body.scrollWidth;
      const scrollH = document.body.scrollHeight;
      const pxPerPage = (pageH / pageW) * scrollW;
      const numPages = Math.ceil(scrollH / pxPerPage);

      for (let p = 0; p < numPages; p++) {
        if (btn) btn.innerHTML = 'Page ' + (p + 1) + '/' + numPages;
        const yStart = p * pxPerPage;
        const pageHeightPx = Math.min(pxPerPage, scrollH - yStart);
        const canvas = await window.html2canvas(document.body, {
          x: 0, y: yStart,
          width: scrollW, height: pageHeightPx,
          windowWidth: scrollW, windowHeight: scrollH,
          scale: 1.5, backgroundColor: '#ffffff', logging: false,
        });
        const imgData = canvas.toDataURL('image/jpeg', 0.85);
        if (p > 0) pdf.addPage();
        const drawH = pageHeightPx / scrollW * pageW;
        pdf.addImage(imgData, 'JPEG', 0, 0, pageW, drawH, undefined, 'FAST');
      }

      // Restore chrome
      if (sidebar) sidebar.style.display = savedDisplays.sidebar;
      if (topbar)  topbar.style.display  = savedDisplays.topbar;
      if (footer)  footer.style.display  = savedDisplays.footer;
      if (layout)  layout.style.cssText  = savedDisplays.layoutCss;
      if (main)    main.style.cssText    = savedDisplays.mainCss;

      pdf.save(filename);
    } catch (e) {
      alert('PDF generation failed: ' + e.message);
      console.error(e);
    } finally {
      if (btn) { btn.style.pointerEvents = ''; btn.innerHTML = originalText; }
    }
  }

  window.exportPDF = exportPDF;
})();
