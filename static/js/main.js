document.addEventListener('DOMContentLoaded', function () {
  const mobileNavToggle = document.getElementById('mobileNavToggle');
  const mobileNavPanel = document.getElementById('mobileNavPanel');
  const productsMegaItem = document.getElementById('productsMegaItem');
  const productsMegaToggle = productsMegaItem ? productsMegaItem.querySelector('.mobile-mega-toggle') : null;
  const closeProductsMega = () => {
    if (productsMegaItem && productsMegaToggle) {
      productsMegaItem.classList.remove('is-open');
      productsMegaToggle.setAttribute('aria-expanded', 'false');
    }
  };

  const closeMobileNav = () => {
    if (mobileNavToggle && mobileNavPanel) {
      mobileNavPanel.classList.remove('is-open');
      mobileNavToggle.classList.remove('is-open');
      mobileNavToggle.setAttribute('aria-expanded', 'false');
    }
    closeProductsMega();
  };

  if (mobileNavToggle && mobileNavPanel) {
    mobileNavToggle.addEventListener('click', function () {
      const nextState = !mobileNavPanel.classList.contains('is-open');
      mobileNavPanel.classList.toggle('is-open', nextState);
      mobileNavToggle.classList.toggle('is-open', nextState);
      mobileNavToggle.setAttribute('aria-expanded', String(nextState));
    });

    document.addEventListener('click', function (event) {
      if (!mobileNavPanel.contains(event.target) && !mobileNavToggle.contains(event.target)) {
        closeMobileNav();
      }
    });

    window.addEventListener('resize', function () {
      if (window.innerWidth >= 992) {
        closeMobileNav();
      }
    });
  }

  if (productsMegaItem && productsMegaToggle) {
    productsMegaToggle.addEventListener('click', function () {
      const nextState = !productsMegaItem.classList.contains('is-open');
      productsMegaItem.classList.toggle('is-open', nextState);
      productsMegaToggle.setAttribute('aria-expanded', String(nextState));
    });

    document.addEventListener('click', function (event) {
      if (!productsMegaItem.contains(event.target)) {
        closeProductsMega();
      }
    });

    window.addEventListener('resize', function () {
      if (window.innerWidth >= 992) {
        closeProductsMega();
      }
    });
  }

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
