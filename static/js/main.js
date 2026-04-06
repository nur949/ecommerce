document.addEventListener('DOMContentLoaded', function () {
  const toggle = document.getElementById('miniCartToggle');
  const panel = document.getElementById('miniCartPanel');

  if (toggle && panel) {
    toggle.addEventListener('click', function () {
      const isHidden = panel.classList.contains('d-none');
      panel.classList.toggle('d-none');
      toggle.setAttribute('aria-expanded', String(isHidden));
    });
    document.addEventListener('click', function (event) {
      if (!panel.contains(event.target) && !toggle.contains(event.target)) {
        panel.classList.add('d-none');
        toggle.setAttribute('aria-expanded', 'false');
      }
    });
  }

  const mainImage = document.querySelector('.detail-main-image');
  document.querySelectorAll('.detail-thumb').forEach(function (thumb) {
    thumb.addEventListener('click', function () {
      if (mainImage && thumb.getAttribute('src')) {
        mainImage.setAttribute('src', thumb.getAttribute('src'));
        document.querySelectorAll('.detail-thumb').forEach(function (t) { t.classList.remove('active-thumb'); });
        thumb.classList.add('active-thumb');
      }
    });
  });

  const builderList = document.getElementById('sortableSections');
  const builderInput = document.getElementById('sectionOrderInput');
  if (builderList && builderInput) {
    let dragItem = null;
    const syncOrder = () => {
      const keys = [...builderList.querySelectorAll('.builder-item')].map((item) => item.dataset.key);
      builderInput.value = JSON.stringify(keys);
    };
    syncOrder();
    builderList.querySelectorAll('.builder-item').forEach((item) => {
      item.addEventListener('dragstart', () => {
        dragItem = item;
        item.classList.add('dragging');
      });
      item.addEventListener('dragend', () => {
        item.classList.remove('dragging');
        syncOrder();
      });
      item.addEventListener('dragover', (event) => {
        event.preventDefault();
        const current = event.currentTarget;
        if (dragItem && dragItem !== current) {
          const rect = current.getBoundingClientRect();
          const after = (event.clientY - rect.top) > rect.height / 2;
          if (after) {
            current.after(dragItem);
          } else {
            current.before(dragItem);
          }
        }
      });
    });
  }
});
