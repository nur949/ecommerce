(function () {
  const api = window.ZynvoApi;
  if (!api) return;

  const money = (value) => `\u09F3${value || '0.00'}`;
  const refreshIcons = () => {
    if (window.lucide) window.lucide.createIcons();
  };

  const debounce = (fn, wait = 300) => {
    let timer = null;
    return (...args) => {
      clearTimeout(timer);
      timer = setTimeout(() => fn(...args), wait);
    };
  };

  const toast = (message, type = 'success') => {
    if (!message) return;
    let region = document.getElementById('ajaxToastRegion');
    if (!region) {
      region = document.createElement('div');
      region.id = 'ajaxToastRegion';
      region.className = 'ajax-toast-region';
      region.setAttribute('aria-live', 'polite');
      region.setAttribute('aria-atomic', 'true');
      document.body.appendChild(region);
    }
    const item = document.createElement('div');
    item.className = `ajax-toast ajax-toast-${type}`;
    item.textContent = message;
    region.appendChild(item);
    requestAnimationFrame(() => item.classList.add('is-visible'));
    setTimeout(() => {
      item.classList.remove('is-visible');
      setTimeout(() => item.remove(), 220);
    }, 2600);
  };

  const setBusy = (node, busy = true) => {
    if (!node) return;
    node.classList.toggle('is-async-loading', busy);
    node.setAttribute('aria-busy', busy ? 'true' : 'false');
  };

  const withButtonLoading = async (button, task) => {
    const label = button?.innerHTML;
    if (button) {
      button.disabled = true;
      button.dataset.loading = 'true';
      button.innerHTML = '<span class="ajax-spinner"></span><span>Working...</span>';
    }
    try {
      return await task();
    } finally {
      if (button) {
        button.disabled = false;
        button.dataset.loading = 'false';
        button.innerHTML = label;
      }
      refreshIcons();
    }
  };

  const openMiniCart = () => {
    const panel = document.getElementById('miniCartPanel');
    const backdrop = document.getElementById('miniCartBackdrop');
    if (!panel) return;
    panel.classList.remove('d-none');
    backdrop?.classList.remove('d-none');
    requestAnimationFrame(() => {
      panel.classList.add('is-open');
      backdrop?.classList.add('is-open');
      panel.setAttribute('aria-hidden', 'false');
    });
  };

  const replaceMiniCart = (html) => {
    if (!html) return;
    const doc = new DOMParser().parseFromString(html, 'text/html');
    ['miniCartBackdrop', 'miniCartPanel'].forEach((id) => {
      const current = document.getElementById(id);
      const incoming = doc.getElementById(id);
      if (current && incoming) current.replaceWith(incoming);
    });
    refreshIcons();
  };

  const updateCartBadge = (count) => {
    document.querySelectorAll('.js-mini-cart-toggle').forEach((toggle) => {
      let badge = toggle.querySelector('.badge');
      if (count > 0) {
        if (!badge) {
          badge = document.createElement('span');
          badge.className = 'badge absolute -right-1 -top-1 flex h-5 min-w-[1.25rem] items-center justify-center rounded-full bg-ink px-1 text-[10px] font-bold text-white';
          toggle.appendChild(badge);
        }
        badge.textContent = String(count);
      } else {
        badge?.remove();
      }
    });
  };

  const updateWishlistBadge = (count) => {
    document.querySelectorAll('.js-wishlist-link').forEach((link) => {
      let badge = link.querySelector('.js-wishlist-badge');
      if (count > 0) {
        if (!badge) {
          badge = document.createElement('span');
          badge.className = 'js-wishlist-badge absolute -right-1 -top-1 flex h-5 min-w-[1.25rem] items-center justify-center rounded-full bg-ink px-1 text-[10px] font-bold text-white';
          link.appendChild(badge);
        }
        badge.textContent = String(count);
      } else {
        badge?.remove();
      }
    });
  };

  const updateCartSummary = (data) => {
    const totals = data.cart_totals || {};
    const setText = (selector, value) => {
      document.querySelectorAll(selector).forEach((node) => {
        node.textContent = value;
      });
    };
    setText('.cart-subtotal-value', money(totals.subtotal || data.cart_subtotal));
    setText('.cart-coupon-discount-value', `-${money(totals.coupon_discount)}`);
    setText('.cart-reward-discount-value', `-${money(totals.reward_discount)}`);
    setText('.cart-total-value', money(totals.total));
    setText('.cart-free-delivery-remaining', money(totals.free_delivery_remaining));
    document.querySelectorAll('.cart-free-delivery-message').forEach((node) => {
      const remaining = Number(totals.free_delivery_remaining || 0);
      node.innerHTML = remaining > 0
        ? `Add <strong class="cart-free-delivery-remaining">${money(totals.free_delivery_remaining)}</strong> more for free delivery.`
        : '<span class="cart-free-delivery-unlocked">You unlocked free delivery.</span>';
    });
  };

  const showEmptyCart = () => {
    const shell = document.querySelector('[data-cart-content]');
    if (!shell) return;
    shell.innerHTML = `
      <div class="commerce-panel px-6 py-20 text-center">
        <h2 class="text-3xl font-semibold text-ink">Your cart is empty</h2>
        <p class="mt-3 text-sm text-stone">Start adding products from the beauty catalog.</p>
        <a href="/shop/" class="commerce-btn-primary mt-7 px-6">Go to Shop</a>
      </div>
    `;
  };

  document.addEventListener('submit', (event) => {
    const form = event.target.closest('form.js-add-to-cart-ajax');
    if (!form) return;
    event.preventDefault();
    event.stopImmediatePropagation();
    const button = form.querySelector('[type="submit"]');
    withButtonLoading(button, async () => {
      const data = await api.form(form);
      replaceMiniCart(data.mini_cart_html);
      updateCartBadge(Number(data.cart_count || 0));
      openMiniCart();
      toast(data.message || 'Added to cart.');
    }).catch(() => toast('Could not add this item. Try again.', 'error'));
  }, true);

  document.addEventListener('change', (event) => {
    const input = event.target.closest('.cart-qty-input');
    if (!input) return;
    const form = input.closest('form.js-cart-update-form');
    if (!form) return;
    event.preventDefault();
    event.stopImmediatePropagation();
    const line = form.closest('.cart-line');
    setBusy(line, true);
    api.form(form).then((data) => {
      if (Number(data.item_quantity || 0) <= 0) {
        line?.remove();
      } else {
        input.value = String(data.item_quantity);
        const total = line?.querySelector('.cart-line-total');
        if (total) total.textContent = money(data.item_total);
      }
      replaceMiniCart(data.mini_cart_html);
      updateCartBadge(Number(data.cart_count || 0));
      updateCartSummary(data);
      if (Number(data.cart_count || 0) <= 0) showEmptyCart();
      toast('Cart updated.');
    }).catch(() => toast('Could not update cart.', 'error')).finally(() => setBusy(line, false));
  }, true);

  document.addEventListener('submit', (event) => {
    const form = event.target.closest('form.js-cart-remove-form');
    if (!form) return;
    event.preventDefault();
    event.stopImmediatePropagation();
    const line = form.closest('.cart-line');
    const button = form.querySelector('[type="submit"]');
    withButtonLoading(button, async () => {
      const data = await api.form(form);
      line?.remove();
      replaceMiniCart(data.mini_cart_html);
      updateCartBadge(Number(data.cart_count || 0));
      updateCartSummary(data);
      if (Number(data.cart_count || 0) <= 0) showEmptyCart();
      toast('Item removed from cart.');
    }).catch(() => toast('Could not remove item.', 'error'));
  }, true);

  document.addEventListener('submit', (event) => {
    const form = event.target.closest('form.js-wishlist-ajax');
    if (!form) return;
    event.preventDefault();
    event.stopImmediatePropagation();
    const button = form.querySelector('.js-wishlist-button');
    withButtonLoading(button, async () => {
      const data = await api.form(form);
      updateWishlistBadge(Number(data.wishlist_count || 0));
      const active = Boolean(data.is_wishlisted);
      button?.classList.toggle('is-active', active);
      button?.classList.toggle('text-rosewood', active);
      if (button) {
        const addLabel = button.dataset.addLabel || 'Save';
        const removeLabel = button.dataset.removeLabel || 'Saved';
        const icon = button.querySelector('svg') ? '<i data-lucide="heart" class="h-4 w-4"></i>' : '';
        button.innerHTML = icon || (active ? removeLabel : addLabel);
        if (icon && !button.classList.contains('w-full')) button.append(document.createTextNode(active ? removeLabel : addLabel));
      }
      if (data.add_url && data.remove_url) {
        form.action = active ? data.remove_url : data.add_url;
      }
      toast(data.message || 'Wishlist updated.');
    }).catch(() => toast('Could not update wishlist.', 'error'));
  }, true);

  const shopForm = document.getElementById('shopAjaxForm');
  const shopGrid = document.getElementById('shopProductGrid');
  const shopNav = document.getElementById('shopCategoryNav');
  const shopCount = document.getElementById('shopProductCount');
  const shopStatus = document.getElementById('shopResultsStatus');

  const buildShopUrl = (page = 1) => {
    const params = new URLSearchParams(new FormData(shopForm));
    [...params.keys()].forEach((key) => {
      if (!params.get(key)) params.delete(key);
    });
    if (page > 1) params.set('page', String(page));
    else params.delete('page');
    const query = params.toString();
    return `${shopForm.action}${query ? `?${query}` : ''}`;
  };

  const applyShopPayload = (data, append = false) => {
    if (shopNav && data.nav_html) shopNav.innerHTML = data.nav_html;
    if (append) {
      const doc = new DOMParser().parseFromString(data.html, 'text/html');
      const target = shopGrid.querySelector('#shopProductsGrid');
      doc.querySelectorAll('#shopProductsGrid > div').forEach((card) => target?.appendChild(card));
      shopGrid.querySelector('.js-load-more-products')?.remove();
      const nextButton = doc.querySelector('.js-load-more-products');
      if (nextButton) shopGrid.appendChild(nextButton);
    } else {
      shopGrid.innerHTML = data.html;
    }
    if (shopCount) shopCount.textContent = `${data.count} products`;
    if (shopStatus) shopStatus.textContent = '';
    refreshIcons();
  };

  const fetchShop = async ({page = 1, append = false, push = true} = {}) => {
    if (!shopForm || !shopGrid) return;
    const url = buildShopUrl(page);
    if (shopStatus) shopStatus.textContent = append ? 'Loading more products...' : 'Loading products...';
    setBusy(shopGrid, true);
    try {
      const data = await api.get(url);
      applyShopPayload(data, append);
      if (push && !append) window.history.pushState({shop: true, url}, '', url);
    } catch (_) {
      toast('Could not load products.', 'error');
    } finally {
      setBusy(shopGrid, false);
    }
  };

  if (shopForm && shopGrid) {
    const debouncedFetch = debounce(() => fetchShop({page: 1}), 320);

    document.addEventListener('input', (event) => {
      const input = event.target.closest('#shopAjaxForm input');
      if (!input) return;
      event.stopImmediatePropagation();
      debouncedFetch();
    }, true);

    document.addEventListener('change', (event) => {
      const field = event.target.closest('#shopAjaxForm select, #shopAjaxForm input');
      if (!field) return;
      event.stopImmediatePropagation();
      fetchShop({page: 1});
    }, true);

    document.addEventListener('submit', (event) => {
      if (event.target !== shopForm) return;
      event.preventDefault();
      event.stopImmediatePropagation();
      fetchShop({page: 1});
    }, true);

    document.addEventListener('click', (event) => {
      const button = event.target.closest('.js-load-more-products');
      if (!button) return;
      event.preventDefault();
      event.stopImmediatePropagation();
      withButtonLoading(button, () => fetchShop({page: Number(button.dataset.nextPage || 2), append: true, push: false}));
    }, true);

    window.addEventListener('popstate', () => {
      api.get(window.location.href).then((data) => applyShopPayload(data, false)).catch(() => window.location.reload());
    });
  }

  window.ZynvoUi = {
    toast,
    replaceMiniCart,
    updateCartBadge,
    updateWishlistBadge,
  };
}());
