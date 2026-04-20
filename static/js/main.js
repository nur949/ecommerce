document.addEventListener('DOMContentLoaded', () => {
  const csrfToken = document.querySelector('input[name="csrfmiddlewaretoken"]')?.value || '';
  const refreshIcons = () => {
    if (window.lucide) window.lucide.createIcons();
  };

  if (window.Swiper) {
    document.querySelectorAll('[data-hero-slider]').forEach((slider) => {
      if (slider.swiper) return;
      new window.Swiper(slider, {
        loop: slider.querySelectorAll('.swiper-slide').length > 1,
        speed: 850,
        effect: 'fade',
        fadeEffect: {crossFade: true},
        autoplay: {
          delay: 5200,
          disableOnInteraction: false,
        },
        pagination: {
          el: slider.querySelector('.swiper-pagination'),
          clickable: true,
        },
        navigation: {
          prevEl: slider.querySelector('.hero-slider-prev'),
          nextEl: slider.querySelector('.hero-slider-next'),
        },
      });
    });
  }

  const miniCartPanel = document.getElementById('miniCartPanel');
  const miniCartBackdrop = document.getElementById('miniCartBackdrop');
  const miniCartToggles = () => document.querySelectorAll('.js-mini-cart-toggle');

  const openMiniCart = () => {
    if (!miniCartPanel) return;
    miniCartPanel.classList.remove('d-none');
    miniCartBackdrop?.classList.remove('d-none');
    requestAnimationFrame(() => {
      miniCartPanel.classList.add('is-open');
      miniCartBackdrop?.classList.add('is-open');
    });
  };
  const closeMiniCart = () => {
    if (!miniCartPanel) return;
    miniCartPanel.classList.remove('is-open');
    miniCartBackdrop?.classList.remove('is-open');
    setTimeout(() => {
      miniCartPanel.classList.add('d-none');
      miniCartBackdrop?.classList.add('d-none');
    }, 220);
  };

  const replaceMiniCart = (html) => {
    if (!html || !miniCartPanel) return;
    const doc = new DOMParser().parseFromString(html, 'text/html');
    const incoming = doc.getElementById('miniCartPanel');
    if (!incoming) return;
    miniCartPanel.innerHTML = incoming.innerHTML;
    refreshIcons();
  };

  const updateMiniCartBadge = (count) => {
    miniCartToggles().forEach((toggle) => {
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

  const money = (value) => `\u09F3${value || '0.00'}`;

  const updateCartSummary = (data) => {
    const totals = data?.cart_totals || {};
    const setText = (selector, value) => {
      const node = document.querySelector(selector);
      if (node) node.textContent = value;
    };
    setText('.cart-subtotal-value', money(totals.subtotal || data?.cart_subtotal));
    setText('.cart-coupon-discount-value', `-${money(totals.coupon_discount)}`);
    setText('.cart-reward-discount-value', `-${money(totals.reward_discount)}`);
    setText('.cart-total-value', money(totals.total));
    setText('.cart-free-delivery-remaining', money(totals.free_delivery_remaining));
  };

  miniCartToggles().forEach((btn) => btn.addEventListener('click', (e) => {
    if (!miniCartPanel) return;
    e.preventDefault();
    if (miniCartPanel?.classList.contains('is-open')) closeMiniCart();
    else openMiniCart();
  }));
  miniCartBackdrop?.addEventListener('click', closeMiniCart);
  document.addEventListener('click', (e) => {
    if (e.target.closest('#miniCartClose')) closeMiniCart();
  });
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      closeMiniCart();
      closeSearchOverlay();
      closeMobileNav();
      setMegaMenuOpen(false);
    }
  });

  const notify = (message) => {
    if (!message) return;
    let box = document.getElementById('cartNotice');
    if (!box) {
      box = document.createElement('div');
      box.id = 'cartNotice';
      box.className = 'cart-notice';
      document.body.appendChild(box);
    }
    box.textContent = message;
    box.classList.add('is-visible');
    clearTimeout(box.timer);
    box.timer = setTimeout(() => box.classList.remove('is-visible'), 2000);
  };

  document.addEventListener('submit', async (e) => {
    const form = e.target.closest('form.js-add-to-cart-ajax');
    if (!form) return;
    e.preventDefault();
    const button = form.querySelector("button[type='submit']");
    const formData = new FormData(form);
    if (button) button.disabled = true;
    try {
      const res = await fetch(form.action, {
        method: 'POST',
        headers: {'X-Requested-With': 'XMLHttpRequest'},
        credentials: 'same-origin',
        body: formData,
      });
      const data = await res.json();
      if (!data.ok) throw new Error();
      replaceMiniCart(data.mini_cart_html);
      updateMiniCartBadge(Number(data.cart_count || 0));
      openMiniCart();
      notify(data.message || 'Added to cart.');
    } catch (_) {
      form.submit();
    } finally {
      if (button) button.disabled = false;
    }
  });

  document.addEventListener('change', async (e) => {
    const input = e.target.closest('.cart-qty-input');
    if (!input) return;
    const form = input.closest('form.js-cart-update-form');
    if (!form) return;
    const line = form.closest('.cart-line');
    try {
      const res = await fetch(form.action, {
        method: 'POST',
        headers: {'X-Requested-With': 'XMLHttpRequest'},
        credentials: 'same-origin',
        body: new FormData(form),
      });
      const data = await res.json();
      if (!data.ok) throw new Error();
      if (Number(data.item_quantity || 0) <= 0) {
        line?.remove();
      } else {
        input.value = String(data.item_quantity);
        line?.querySelector('.cart-line-total') && (line.querySelector('.cart-line-total').textContent = money(data.item_total));
      }
      replaceMiniCart(data.mini_cart_html);
      updateMiniCartBadge(Number(data.cart_count || 0));
      updateCartSummary(data);
    } catch (_) {
      form.submit();
    }
  });

  document.addEventListener('submit', async (e) => {
    const form = e.target.closest('form.js-cart-remove-form');
    if (!form) return;
    e.preventDefault();
    const line = form.closest('.cart-line');
    try {
      const res = await fetch(form.action, {
        method: 'POST',
        headers: {'X-Requested-With': 'XMLHttpRequest'},
        credentials: 'same-origin',
        body: new FormData(form),
      });
      const data = await res.json();
      if (!data.ok) throw new Error();
      line?.remove();
      replaceMiniCart(data.mini_cart_html);
      updateMiniCartBadge(Number(data.cart_count || 0));
      updateCartSummary(data);
      notify('Item removed from cart.');
      if (Number(data.cart_count || 0) <= 0) window.location.reload();
    } catch (_) {
      form.submit();
    }
  });

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

  document.addEventListener('submit', async (e) => {
    const form = e.target.closest('form.js-wishlist-ajax');
    if (!form) return;
    e.preventDefault();
    try {
      const res = await fetch(form.action, {
        method: 'POST',
        headers: {'X-Requested-With': 'XMLHttpRequest'},
        credentials: 'same-origin',
        body: new FormData(form),
      });
      const data = await res.json();
      if (!data.ok) throw new Error();
      updateWishlistBadge(Number(data.wishlist_count || 0));
      notify(data.message || 'Wishlist updated.');
      window.location.reload();
    } catch (_) {
      form.submit();
    }
  });

  const shopForm = document.getElementById('shopAjaxForm');
  const shopGrid = document.getElementById('shopProductGrid');
  const shopNav = document.getElementById('shopCategoryNav');
  const shopCount = document.getElementById('shopProductCount');
  const status = document.getElementById('shopResultsStatus');
  let nextPage = null;
  let loadingMore = false;

  const fetchShop = async (append = false, page = 1) => {
    if (!shopForm || !shopGrid) return;
    const params = new URLSearchParams(new FormData(shopForm));
    params.set('page', String(page));
    status && (status.textContent = 'Loading products...');
    const res = await fetch(`${shopForm.action}?${params.toString()}`, {
      headers: {'X-Requested-With': 'XMLHttpRequest'},
      credentials: 'same-origin',
    });
    const data = await res.json();
    if (!data.ok) return;
    if (shopNav && data.nav_html) {
      shopNav.innerHTML = data.nav_html;
    }
    if (append) {
      const doc = new DOMParser().parseFromString(data.html, 'text/html');
      const cards = doc.querySelectorAll('#shopProductsGrid > div');
      const container = shopGrid.querySelector('#shopProductsGrid');
      cards.forEach((card) => container?.appendChild(card));
      const moreBtn = shopGrid.querySelector('.js-load-more-products');
      if (moreBtn) moreBtn.remove();
      const incomingMore = doc.querySelector('.js-load-more-products');
      if (incomingMore) shopGrid.appendChild(incomingMore);
    } else {
      shopGrid.innerHTML = data.html;
    }
    shopCount && (shopCount.textContent = `${data.count} products`);
    nextPage = data.next_page;
    status && (status.textContent = '');
    refreshIcons();
  };

  if (shopForm && shopGrid) {
    ['change', 'input'].forEach((eventName) => {
      shopForm.addEventListener(eventName, (e) => {
        const target = e.target;
        if (!(target instanceof HTMLInputElement || target instanceof HTMLSelectElement)) return;
        if (target.name === 'q' && eventName === 'input') return;
        fetchShop(false, 1);
      });
    });
    const searchInput = document.getElementById('shopSearch');
    let searchTimer = null;
    searchInput?.addEventListener('input', () => {
      clearTimeout(searchTimer);
      searchTimer = setTimeout(() => fetchShop(false, 1), 350);
    });
    shopForm.addEventListener('submit', (e) => {
      e.preventDefault();
      fetchShop(false, 1);
    });
    document.addEventListener('click', async (e) => {
      const btn = e.target.closest('.js-load-more-products');
      if (!btn || loadingMore) return;
      loadingMore = true;
      btn.disabled = true;
      const page = Number(btn.dataset.nextPage || nextPage || 2);
      await fetchShop(true, page);
      loadingMore = false;
    });
  }

  const mobileToggle = document.getElementById('mobileNavToggle');
  const mobilePanel = document.getElementById('mobileNavPanel');
  const closeMobileNav = () => {
    mobilePanel?.classList.add('hidden');
    mobilePanel?.classList.remove('is-open');
    mobileToggle?.setAttribute('aria-expanded', 'false');
    mobileCategoriesPanel?.classList.add('hidden');
    mobileCategoriesToggle?.setAttribute('aria-expanded', 'false');
  };
  mobileToggle?.addEventListener('click', () => {
    const open = mobilePanel?.classList.contains('hidden');
    mobilePanel?.classList.toggle('hidden', !open);
    mobilePanel?.classList.toggle('is-open', !!open);
    mobileToggle.setAttribute('aria-expanded', open ? 'true' : 'false');
  });

  const megaMenuWrap = document.getElementById('megaMenuWrap');
  const megaMenuToggle = document.getElementById('megaMenuToggle');
  const megaMenuPanel = document.getElementById('megaMenuPanel');
  const megaCategoriesList = document.getElementById('megaCategoriesList');
  const mobileCategoriesToggle = document.getElementById('mobileCategoriesToggle');
  const mobileCategoriesPanel = document.getElementById('mobileCategoriesPanel');
  const mobileCategoriesList = document.getElementById('mobileCategoriesList');
  let categoriesLoaded = false;
  let categoriesLoading = false;

  const escapeHtml = (value) => String(value || '').replace(/[&<>"']/g, (char) => ({
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#39;',
  }[char]));

  const renderDesktopCategories = (items) => {
    if (!megaCategoriesList) return;
    megaCategoriesList.innerHTML = items.map((category) => {
      const children = (category.children || []).map((child) => (
        `<a href="/category/${encodeURIComponent(child.slug)}/" class="text-sm text-stone transition hover:text-rosewood">${escapeHtml(child.name)}</a>`
      )).join('');
      return `
        <div>
          <a href="/category/${encodeURIComponent(category.slug)}/" class="text-sm font-bold uppercase tracking-[0.16em] text-ink">${escapeHtml(category.name)}</a>
          <div class="mt-3 grid gap-2">
            ${children || '<span class="text-sm text-stone">No sub-categories</span>'}
          </div>
        </div>
      `;
    }).join('');
  };

  const renderMobileCategories = (items) => {
    if (!mobileCategoriesList) return;
    mobileCategoriesList.innerHTML = items.map((category) => {
      const children = (category.children || []).map((child) => (
        `<a href="/category/${encodeURIComponent(child.slug)}/" class="ml-3 rounded-xl px-3 py-2 text-sm text-stone transition hover:bg-white hover:text-rosewood">${escapeHtml(child.name)}</a>`
      )).join('');
      return `
        <div class="grid gap-1">
          <a href="/category/${encodeURIComponent(category.slug)}/" class="rounded-xl px-3 py-2 text-sm font-semibold text-ink transition hover:bg-white hover:text-rosewood">${escapeHtml(category.name)}</a>
          ${children}
        </div>
      `;
    }).join('');
  };

  const loadCategories = async () => {
    if (categoriesLoaded || categoriesLoading) return;
    const apiUrl = megaCategoriesList?.dataset.url || mobileCategoriesList?.dataset.url;
    if (!apiUrl) return;
    categoriesLoading = true;
    try {
      const res = await fetch(apiUrl, {credentials: 'same-origin'});
      const data = await res.json();
      if (!data.ok) throw new Error('Category load failed');
      const items = data.results || [];
      if (!items.length) {
        if (megaCategoriesList) megaCategoriesList.innerHTML = '<div class="text-sm text-stone">No categories found.</div>';
        if (mobileCategoriesList) mobileCategoriesList.innerHTML = '<div class="text-sm text-stone">No categories found.</div>';
        categoriesLoaded = true;
        return;
      }
      renderDesktopCategories(items);
      renderMobileCategories(items);
      categoriesLoaded = true;
      refreshIcons();
    } catch (_) {
      if (megaCategoriesList) megaCategoriesList.innerHTML = '<div class="text-sm text-red-600">Failed to load categories.</div>';
      if (mobileCategoriesList) mobileCategoriesList.innerHTML = '<div class="text-sm text-red-600">Failed to load categories.</div>';
    } finally {
      categoriesLoading = false;
    }
  };

  const setMegaMenuOpen = (open) => {
    if (!megaMenuPanel || !megaMenuToggle) return;
    megaMenuPanel.classList.toggle('pointer-events-none', !open);
    megaMenuPanel.classList.toggle('pointer-events-auto', open);
    megaMenuPanel.classList.toggle('opacity-0', !open);
    megaMenuPanel.classList.toggle('opacity-100', open);
    megaMenuToggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    if (open) loadCategories();
  };

  megaMenuWrap?.addEventListener('mouseenter', () => loadCategories());
  megaMenuToggle?.addEventListener('focus', () => loadCategories());
  megaMenuToggle?.addEventListener('click', (e) => {
    e.preventDefault();
    const isOpen = megaMenuToggle.getAttribute('aria-expanded') === 'true';
    setMegaMenuOpen(!isOpen);
  });
  document.addEventListener('click', (e) => {
    if (!megaMenuWrap?.contains(e.target)) setMegaMenuOpen(false);
  });

  mobileCategoriesToggle?.addEventListener('click', () => {
    const open = mobileCategoriesPanel?.classList.contains('hidden');
    mobileCategoriesPanel?.classList.toggle('hidden', !open);
    mobileCategoriesToggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    if (open) loadCategories();
  });

  const searchOverlay = document.getElementById('searchOverlay');
  const searchToggle = document.getElementById('searchOverlayToggle');
  const mobileSearchToggle = document.getElementById('mobileSearchToggle');
  const searchClose = document.getElementById('searchOverlayClose');
  const searchInput = document.getElementById('instantSearchInput');
  const searchSuggestions = document.getElementById('instantSearchSuggestions');
  const recentWrap = document.getElementById('recentSearches');
  const recentKey = 'beauty_recent_searches_v1';
  const getRecent = () => {
    try {
      return JSON.parse(localStorage.getItem(recentKey) || '[]');
    } catch (_) {
      return [];
    }
  };
  const setRecent = (values) => localStorage.setItem(recentKey, JSON.stringify(values.slice(0, 6)));
  const renderRecent = () => {
    if (!recentWrap) return;
    const items = getRecent();
    recentWrap.innerHTML = '';
    items.forEach((term) => {
      const button = document.createElement('button');
      button.type = 'button';
      button.className = 'rounded-full border border-black/10 bg-white px-3 py-1 text-xs text-ink';
      button.textContent = term;
      button.addEventListener('click', () => {
        if (searchInput) searchInput.value = term;
        window.location.href = `/shop/?q=${encodeURIComponent(term)}`;
      });
      recentWrap.appendChild(button);
    });
  };
  const openSearchOverlay = () => {
    searchOverlay?.classList.remove('hidden');
    renderRecent();
    searchInput?.focus();
  };
  const closeSearchOverlay = () => searchOverlay?.classList.add('hidden');
  searchToggle?.addEventListener('click', openSearchOverlay);
  mobileSearchToggle?.addEventListener('click', () => {
    closeMobileNav();
    openSearchOverlay();
  });
  searchClose?.addEventListener('click', closeSearchOverlay);
  searchOverlay?.addEventListener('click', (e) => {
    if (e.target === searchOverlay) closeSearchOverlay();
  });

  let suggestTimer = null;
  searchInput?.addEventListener('input', () => {
    clearTimeout(suggestTimer);
    suggestTimer = setTimeout(async () => {
      const q = (searchInput.value || '').trim();
      if (!q || !searchSuggestions) {
        if (searchSuggestions) searchSuggestions.innerHTML = '';
        return;
      }
      const res = await fetch(`/api/search/suggest/?q=${encodeURIComponent(q)}`, {credentials: 'same-origin'});
      const data = await res.json();
      searchSuggestions.innerHTML = '';
      (data.results || []).forEach((item) => {
        const link = document.createElement('a');
        link.href = item.url;
        link.className = 'block rounded-[12px] border border-black/10 px-3 py-2 hover:bg-[#f8fafc]';
        link.innerHTML = `<div class="text-sm font-semibold text-ink">${item.label}</div><div class="text-xs text-stone">${item.subtext || ''}</div>`;
        link.addEventListener('click', () => {
          const recent = [q, ...getRecent().filter((v) => v !== q)];
          setRecent(recent);
        });
        searchSuggestions.appendChild(link);
      });
    }, 220);
  });

  searchInput?.closest('form')?.addEventListener('submit', () => {
    const q = (searchInput.value || '').trim();
    if (!q) return;
    setRecent([q, ...getRecent().filter((v) => v !== q)]);
  });

  const detailImage = document.querySelector('.detail-main-image');
  document.querySelectorAll('.detail-thumb').forEach((thumb) => {
    thumb.addEventListener('click', () => {
      if (!detailImage) return;
      detailImage.src = thumb.src;
      document.querySelectorAll('.detail-thumb').forEach((node) => node.classList.remove('active-thumb'));
      thumb.classList.add('active-thumb');
    });
  });

  const qtyInput = document.querySelector('.js-detail-quantity');
  const detailPrice = document.getElementById('detailPrice');
  const detailTotalPrice = document.getElementById('detailTotalPrice');
  const detailSku = document.getElementById('detailSku');
  const variantInput = document.getElementById('variantIdInput');
  const updateDetailTotal = () => {
    if (!detailPrice || !detailTotalPrice || !qtyInput) return;
    const unitPrice = Number(detailPrice.dataset.currentPrice || detailPrice.dataset.basePrice || 0);
    const quantity = Math.max(Number(qtyInput.value || 1), 1);
    detailTotalPrice.textContent = money((unitPrice * quantity).toFixed(2));
  };
  document.querySelectorAll('.js-qty-button').forEach((btn) => {
    btn.addEventListener('click', () => {
      if (!qtyInput) return;
      const step = Number(btn.dataset.step || 0);
      const max = Number(qtyInput.max || 999);
      const next = Math.min(Math.max(Number(qtyInput.value || 1) + step, 1), max);
      qtyInput.value = String(next);
      updateDetailTotal();
    });
  });
  qtyInput?.addEventListener('input', () => {
    const max = Number(qtyInput.max || 999);
    const value = Math.min(Math.max(Number(qtyInput.value || 1), 1), max);
    qtyInput.value = String(value);
    updateDetailTotal();
  });
  document.querySelectorAll('.js-variant-option').forEach((option) => {
    option.addEventListener('click', () => {
      document.querySelectorAll('.js-variant-option').forEach((node) => node.classList.remove('active'));
      option.classList.add('active');
      if (variantInput) variantInput.value = option.dataset.variantId || '';
      const stockLabel = document.getElementById('variantStockLabel');
      const stock = Number(option.dataset.stock || 0);
      if (stockLabel) {
        stockLabel.textContent = stock > 0 ? `${stock} available` : 'Out of stock';
        stockLabel.classList.toggle('text-danger', stock <= 0);
        stockLabel.classList.toggle('text-success', stock > 0);
      }
      const addButton = document.getElementById('addToCartButton');
      if (addButton) {
        addButton.disabled = stock <= 0;
        addButton.textContent = stock > 0 ? 'Add to Cart' : 'Out of Stock';
      }
      if (qtyInput) {
        qtyInput.max = String(Math.max(stock, 1));
        qtyInput.value = String(Math.min(Math.max(Number(qtyInput.value || 1), 1), Math.max(stock, 1)));
      }
      if (detailSku) detailSku.textContent = option.dataset.sku || detailSku.textContent;
      if (detailPrice && option.dataset.price) {
        detailPrice.dataset.currentPrice = option.dataset.price;
        detailPrice.textContent = money(option.dataset.price);
      }
      updateDetailTotal();
    });
  });
  if (detailPrice && !detailPrice.dataset.currentPrice) {
    detailPrice.dataset.currentPrice = detailPrice.dataset.basePrice || '0.00';
  }
  updateDetailTotal();

  const productSlug = window.location.pathname.split('/').filter(Boolean).slice(-1)[0];
  if (window.location.pathname.includes('/product/') && productSlug) {
    setInterval(async () => {
      try {
        const res = await fetch(`/api/products/${productSlug}/availability/`, {credentials: 'same-origin'});
        if (!res.ok) return;
        const data = await res.json();
        const addButton = document.getElementById('addToCartButton');
        const stockLabel = document.getElementById('variantStockLabel');
        if (addButton) addButton.disabled = !data.product.is_orderable;
        if (stockLabel && !document.querySelector('.js-variant-option.active')) {
          stockLabel.textContent = data.product.in_stock ? `${data.product.stock} available` : 'Out of stock';
        }
      } catch (_) {}
    }, 30000);
  }

  refreshIcons();
});
