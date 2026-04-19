document.addEventListener('DOMContentLoaded', function () {
  const getMiniCartElements = () => ({
    toggle: document.getElementById('miniCartToggle'),
    panel: document.getElementById('miniCartPanel'),
    backdrop: document.getElementById('miniCartBackdrop'),
  });

  const finishCloseMiniCart = () => {
    const { panel, backdrop } = getMiniCartElements();
    if (panel && !panel.classList.contains('is-open')) {
      panel.classList.add('d-none');
      panel.setAttribute('aria-hidden', 'true');
    }
    if (backdrop && !backdrop.classList.contains('is-open')) {
      backdrop.classList.add('d-none');
    }
    document.body.classList.remove('mini-cart-active');
  };

  const closeMiniCart = () => {
    const { toggle, panel, backdrop } = getMiniCartElements();
    if (!panel) return;
    panel.classList.remove('is-open');
    panel.setAttribute('aria-hidden', 'true');
    if (backdrop) {
      backdrop.classList.remove('is-open');
    }
    if (toggle) {
      toggle.setAttribute('aria-expanded', 'false');
    }
    window.setTimeout(finishCloseMiniCart, 240);
  };

  const openMiniCart = () => {
    const { toggle, panel, backdrop } = getMiniCartElements();
    if (!toggle || !panel) return;
    panel.classList.remove('d-none');
    panel.setAttribute('aria-hidden', 'false');
    if (backdrop) {
      backdrop.classList.remove('d-none');
      requestAnimationFrame(() => backdrop.classList.add('is-open'));
    }
    requestAnimationFrame(() => panel.classList.add('is-open'));
    toggle.setAttribute('aria-expanded', 'true');
    document.body.classList.add('mini-cart-active');
  };

  const showCartNotice = (message) => {
    if (!message) return;
    let notice = document.getElementById('cartNotice');
    if (!notice) {
      notice = document.createElement('div');
      notice.id = 'cartNotice';
      notice.className = 'cart-notice';
      notice.setAttribute('role', 'status');
      document.body.appendChild(notice);
    }
    notice.textContent = message;
    notice.classList.add('is-visible');
    window.clearTimeout(notice.hideTimer);
    notice.hideTimer = window.setTimeout(() => {
      notice.classList.remove('is-visible');
    }, 2200);
  };

  const updateMiniCartBadge = (count) => {
    const { toggle } = getMiniCartElements();
    if (!toggle) return;

    let badge = toggle.querySelector('.badge');
    if (count > 0) {
      if (!badge) {
        badge = document.createElement('span');
        badge.className = 'badge bg-danger position-absolute top-0 start-100 translate-middle rounded-pill';
        toggle.appendChild(badge);
      }
      badge.textContent = String(count);
    } else if (badge) {
      badge.remove();
    }
  };

  const replaceMiniCartPanelFromHtml = (html) => {
    const { panel } = getMiniCartElements();
    if (!panel || !html) return;

    const parser = new DOMParser();
    const doc = parser.parseFromString(html, 'text/html');
    const incomingPanel = doc.getElementById('miniCartPanel');
    if (!incomingPanel) return;

    panel.innerHTML = incomingPanel.innerHTML;
  };

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
  const backdrop = document.getElementById('miniCartBackdrop');

  if (toggle && panel) {
    toggle.addEventListener('click', function (event) {
      event.preventDefault();
      const isOpen = panel.classList.contains('is-open');
      if (isOpen) {
        closeMiniCart();
      } else {
        openMiniCart();
      }
    });
    if (backdrop) {
      backdrop.addEventListener('click', closeMiniCart);
    }
    document.addEventListener('click', function (event) {
      const closeBtn = event.target.closest('#miniCartClose');
      if (closeBtn) {
        closeMiniCart();
      }
    });
    document.addEventListener('keydown', function (event) {
      if (event.key === 'Escape') {
        closeMiniCart();
      }
    });
  }

  document.addEventListener('submit', async (event) => {
    const form = event.target.closest('form.js-add-to-cart-ajax');
    if (!form) return;
    event.preventDefault();
    const submitter = event.submitter || form.querySelector("button[type='submit']");
    const formData = new FormData(form);
    if (submitter && submitter.name) {
      formData.set(submitter.name, submitter.value);
    }
    const button = submitter && submitter.matches("button[type='submit']") ? submitter : form.querySelector("button[type='submit']");
    const originalText = button ? button.textContent : '';
    const nextUrl = String(formData.get('next') || '');
    if (button) {
      button.disabled = true;
      button.textContent = 'Adding...';
    }

    try {
      const response = await fetch(form.action, {
        method: 'POST',
        headers: {
          'X-Requested-With': 'XMLHttpRequest',
        },
        credentials: 'same-origin',
        body: formData,
      });

      if (!response.ok) throw new Error('Request failed');
      const data = await response.json();
      if (!data.ok) throw new Error('Invalid response');

      replaceMiniCartPanelFromHtml(data.mini_cart_html);
      updateMiniCartBadge(Number(data.cart_count || 0));
      showCartNotice(data.message || 'Added to cart.');
      if (nextUrl.includes('/checkout')) {
        window.location.href = nextUrl;
        return;
      }
      openMiniCart();
    } catch (error) {
      form.submit();
    } finally {
      if (button) {
        button.disabled = false;
        button.textContent = originalText;
      }
    }
  });

  const shopForm = document.getElementById('shopAjaxForm');
  const shopGrid = document.getElementById('shopProductGrid');
  const shopCount = document.getElementById('shopProductCount');
  const shopStatus = document.getElementById('shopResultsStatus');
  const shopSearch = document.getElementById('shopSearch');
  const shopSort = document.getElementById('shopSort');

  if (shopForm && shopGrid) {
    const categoryInput = shopForm.querySelector("input[name='category']");
    const saleInput = shopForm.querySelector("input[name='sale']");
    let shopTimer = null;
    let activeController = null;

    const setShopLoading = (isLoading) => {
      shopGrid.classList.toggle('is-loading', isLoading);
      if (shopStatus) {
        shopStatus.textContent = isLoading ? 'Loading products...' : '';
      }
    };

    const buildShopUrl = () => {
      const formData = new FormData(shopForm);
      const params = new URLSearchParams();
      formData.forEach((value, key) => {
        const nextValue = String(value || '').trim();
        if (nextValue) {
          params.set(key, nextValue);
        }
      });
      return `${shopForm.action}?${params.toString()}`;
    };

    const loadShopProducts = async (pushState = true) => {
      const url = buildShopUrl();
      if (activeController) {
        activeController.abort();
      }
      activeController = new AbortController();
      setShopLoading(true);

      try {
        const response = await fetch(url, {
          headers: {
            'X-Requested-With': 'XMLHttpRequest',
          },
          credentials: 'same-origin',
          signal: activeController.signal,
        });
        if (!response.ok) throw new Error('Shop request failed');
        const data = await response.json();
        if (!data.ok) throw new Error('Invalid shop payload');
        shopGrid.innerHTML = data.html;
        if (shopCount) {
          shopCount.textContent = `${Number(data.count || 0)} products`;
        }
        if (pushState) {
          window.history.pushState({}, '', url);
        }
      } catch (error) {
        if (error.name !== 'AbortError') {
          window.location.href = url;
        }
      } finally {
        setShopLoading(false);
      }
    };

    shopForm.addEventListener('submit', (event) => {
      event.preventDefault();
      loadShopProducts();
    });

    if (shopSort) {
      shopSort.addEventListener('change', () => loadShopProducts());
    }

    if (shopSearch) {
      shopSearch.addEventListener('input', () => {
        clearTimeout(shopTimer);
        shopTimer = setTimeout(() => loadShopProducts(), 400);
      });
    }

    document.querySelectorAll('.filter-list a[data-category]').forEach((link) => {
      link.addEventListener('click', (event) => {
        event.preventDefault();
        if (categoryInput) {
          categoryInput.value = link.dataset.category || '';
        }
        if (saleInput && link.href.includes('sale=1')) {
          saleInput.value = '1';
        }
        document.querySelectorAll('.filter-list a[data-category]').forEach((item) => item.classList.remove('active'));
        link.classList.add('active');
        loadShopProducts();
      });
    });

    window.addEventListener('popstate', () => {
      window.location.reload();
    });
  }

  const updateCartSubtotalUI = (subtotal) => {
    const subtotalEl = document.querySelector('.cart-subtotal-value');
    if (!subtotalEl) return;

    const current = (subtotalEl.textContent || '').trim();
    const prefixMatch = current.match(/^[^\d]*/);
    const prefix = prefixMatch ? prefixMatch[0] : '';
    subtotalEl.textContent = `${prefix}${subtotal}`;
  };

  const runCartUpdateAjax = async (form) => {
    const formData = new FormData(form);
    const itemKey = String(formData.get('item_key') || '');
    const response = await fetch(form.action, {
      method: 'POST',
      headers: {
        'X-Requested-With': 'XMLHttpRequest',
      },
      credentials: 'same-origin',
      body: formData,
    });

    if (!response.ok) throw new Error('Cart update failed');
    const data = await response.json();
    if (!data.ok) throw new Error('Invalid cart update payload');

    const line = document.querySelector(`.cart-line[data-item-key="${itemKey}"]`);
    if (line) {
      const lineTotalEl = line.querySelector('.cart-line-total');
      if (lineTotalEl) {
        const current = (lineTotalEl.textContent || '').trim();
        const prefixMatch = current.match(/^[^\d]*/);
        const prefix = prefixMatch ? prefixMatch[0] : '';
        lineTotalEl.textContent = `${prefix}${data.item_total}`;
      }
    }

    updateCartSubtotalUI(data.cart_subtotal);
    replaceMiniCartPanelFromHtml(data.mini_cart_html);
    updateMiniCartBadge(Number(data.cart_count || 0));
  };

  const cartUpdateForms = document.querySelectorAll('form.js-cart-update-form');
  cartUpdateForms.forEach((form) => {
    const quantityInput = form.querySelector("input[name='quantity']");
    if (!quantityInput) return;

    let debounceTimer = null;
    let lastValue = quantityInput.value;
    const submitIfChanged = async () => {
      const nextValue = quantityInput.value;
      if (nextValue === lastValue) return;
      lastValue = nextValue;
      try {
        await runCartUpdateAjax(form);
      } catch (error) {
        form.submit();
      }
    };

    form.addEventListener('submit', async (event) => {
      event.preventDefault();
      try {
        await runCartUpdateAjax(form);
      } catch (error) {
        form.submit();
      }
    });

    quantityInput.addEventListener('input', () => {
      clearTimeout(debounceTimer);
      debounceTimer = setTimeout(submitIfChanged, 550);
    });

    quantityInput.addEventListener('change', () => {
      clearTimeout(debounceTimer);
      submitIfChanged();
    });
  });

  document.querySelectorAll('.js-cart-remove-link').forEach((removeLink) => {
    removeLink.addEventListener('click', async (event) => {
      event.preventDefault();
      const itemKey = removeLink.dataset.itemKey;
      if (!itemKey) return;

      try {
        const response = await fetch(removeLink.href, {
          method: 'GET',
          headers: {
            'X-Requested-With': 'XMLHttpRequest',
          },
          credentials: 'same-origin',
        });
        if (!response.ok) throw new Error('Remove failed');
        const data = await response.json();
        if (!data.ok) throw new Error('Invalid remove payload');

        const line = document.querySelector(`.cart-line[data-item-key="${itemKey}"]`);
        if (line) {
          line.remove();
        }

        updateCartSubtotalUI(data.cart_subtotal);
        replaceMiniCartPanelFromHtml(data.mini_cart_html);
        updateMiniCartBadge(Number(data.cart_count || 0));

        const remaining = document.querySelectorAll('.cart-line[data-item-key]');
        if (!remaining.length) {
          window.location.reload();
        }
      } catch (error) {
        window.location.href = removeLink.href;
      }
    });
  });

  document.querySelectorAll('form.js-no-empty-submit').forEach((form) => {
    form.addEventListener('submit', (event) => {
      let firstInvalid = null;
      form.querySelectorAll("input[type='text'][name], textarea[name]").forEach((input) => {
        if (!input.hasAttribute('required')) return;
        const value = (input.value || '').trim();
        input.value = value;
        if (!value && !firstInvalid) {
          firstInvalid = input;
        }
      });
      if (firstInvalid) {
        event.preventDefault();
        firstInvalid.focus();
      }
    });
  });

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

  const variantInput = document.getElementById('variantIdInput');
  const variantPrice = document.getElementById('detailPrice');
  const variantStockLabel = document.getElementById('variantStockLabel');
  const addToCartButton = document.getElementById('addToCartButton');
  if (variantInput && variantPrice && addToCartButton) {
    document.querySelectorAll('.js-variant-option').forEach((option) => {
      option.addEventListener('click', () => {
        const nextId = option.dataset.variantId || '';
        const nextPrice = option.dataset.price || variantPrice.textContent.replace(/[^\d.]/g, '');
        const nextStock = Number(option.dataset.stock || 0);

        variantInput.value = nextId;
        variantPrice.textContent = `৳${nextPrice}`;
        if (variantStockLabel) {
          variantStockLabel.textContent = nextStock > 0 ? `${nextStock} available` : 'Out of stock';
          variantStockLabel.classList.toggle('text-success', nextStock > 0);
          variantStockLabel.classList.toggle('text-danger', nextStock <= 0);
        }
        addToCartButton.disabled = nextStock <= 0;
        addToCartButton.textContent = nextStock > 0 ? 'Add to Cart' : 'Out of Stock';
        document.querySelectorAll('.js-variant-option').forEach((item) => {
          item.classList.remove('active');
          item.setAttribute('aria-pressed', 'false');
        });
        option.classList.add('active');
        option.setAttribute('aria-pressed', 'true');
      });
    });
  }

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
