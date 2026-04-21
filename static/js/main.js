document.addEventListener('DOMContentLoaded', () => {
  if (window.lucide) {
    window.lucide.createIcons();
  }

  const refreshIcons = () => window.lucide && window.lucide.createIcons();

  const toastRegion = (() => {
    let region = document.querySelector('.ajax-toast-region');
    if (!region) {
      region = document.createElement('div');
      region.className = 'ajax-toast-region';
      document.body.appendChild(region);
    }
    return region;
  })();

  const notify = (message, isError = false) => {
    if (!message) return;
    const toast = document.createElement('div');
    toast.className = `ajax-toast${isError ? ' bg-red-600' : ''}`;
    toast.textContent = message;
    toastRegion.appendChild(toast);
    requestAnimationFrame(() => toast.classList.add('is-visible'));
    setTimeout(() => {
      toast.classList.remove('is-visible');
      setTimeout(() => toast.remove(), 300);
    }, 2200);
  };

  if (window.Swiper) {
    document.querySelectorAll('[data-hero-slider]').forEach((slider) => {
      if (slider.swiper) return;
      const thumbButtons = slider.parentElement?.querySelectorAll('[data-hero-thumb]') || [];
      const progressBar = slider.querySelector('.hero-progress-bar');
      const swiper = new window.Swiper(slider, {
        loop: slider.querySelectorAll('.swiper-slide').length > 1,
        speed: 700,
        autoplay: { delay: 4500, disableOnInteraction: false, pauseOnMouseEnter: true },
        pagination: { el: slider.querySelector('.swiper-pagination'), clickable: true },
        navigation: {
          nextEl: slider.querySelector('.hero-slider-next'),
          prevEl: slider.querySelector('.hero-slider-prev'),
        },
      });
      const updateHeroUi = () => {
        const total = Math.max(thumbButtons.length || swiper.slides.length - swiper.loopedSlides * 2, 1);
        const current = ((swiper.realIndex || 0) % total + total) % total;
        thumbButtons.forEach((button, index) => {
          button.classList.toggle('is-active', index === current);
        });
        if (progressBar) {
          progressBar.style.width = `${((current + 1) / total) * 100}%`;
        }
      };
      thumbButtons.forEach((button) => {
        button.addEventListener('click', () => {
          swiper.slideToLoop(Number(button.dataset.heroThumb || 0));
        });
      });
      swiper.on('slideChange', updateHeroUi);
      updateHeroUi();
    });
  }

  const accountMenuToggle = document.getElementById('accountMenuToggle');
  const accountMenuPanel = document.getElementById('accountMenuPanel');
  const accountMenuWrap = document.getElementById('accountMenuWrap');
  const setAccountMenu = (open) => {
    if (!accountMenuToggle || !accountMenuPanel) return;
    accountMenuToggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    accountMenuPanel.classList.toggle('pointer-events-none', !open);
    accountMenuPanel.classList.toggle('pointer-events-auto', open);
    accountMenuPanel.classList.toggle('opacity-0', !open);
    accountMenuPanel.classList.toggle('opacity-100', open);
    accountMenuPanel.classList.toggle('translate-y-2', !open);
    accountMenuPanel.classList.toggle('translate-y-0', open);
  };
  accountMenuToggle?.addEventListener('click', (event) => {
    event.preventDefault();
    setAccountMenu(accountMenuToggle.getAttribute('aria-expanded') !== 'true');
  });
  document.addEventListener('click', (event) => {
    if (accountMenuWrap && !accountMenuWrap.contains(event.target)) setAccountMenu(false);
  });

  const megaToggle = document.getElementById('megaMenuToggle');
  const megaPanel = document.getElementById('megaMenuPanel');
  const megaWrap = megaToggle?.closest('.group');
  const setMegaMenu = (open) => {
    if (!megaToggle || !megaPanel) return;
    megaToggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    megaPanel.classList.toggle('pointer-events-none', !open);
    megaPanel.classList.toggle('pointer-events-auto', open);
    megaPanel.classList.toggle('opacity-0', !open);
    megaPanel.classList.toggle('opacity-100', open);
    megaPanel.classList.toggle('translate-y-2', !open);
    megaPanel.classList.toggle('translate-y-0', open);
  };
  megaToggle?.addEventListener('click', (event) => {
    event.preventDefault();
    setMegaMenu(megaToggle.getAttribute('aria-expanded') !== 'true');
  });
  document.addEventListener('click', (event) => {
    if (megaWrap && !megaWrap.contains(event.target)) setMegaMenu(false);
  });

  const mobileNavToggle = document.getElementById('mobileNavToggle');
  const mobileNavPanel = document.getElementById('mobileNavPanel');
  mobileNavToggle?.addEventListener('click', () => {
    mobileNavPanel?.classList.toggle('hidden');
  });

  const searchInput = document.getElementById('instantSearchInput');
  const searchSuggestions = document.getElementById('instantSearchSuggestions');
  let searchTimer = null;
  searchInput?.addEventListener('input', () => {
    clearTimeout(searchTimer);
    searchTimer = setTimeout(async () => {
      const q = (searchInput.value || '').trim();
      if (!searchSuggestions) return;
      if (!q) {
        searchSuggestions.innerHTML = '';
        searchSuggestions.classList.add('hidden');
        return;
      }
      try {
        const res = await fetch(`/api/search/suggest/?q=${encodeURIComponent(q)}`, { credentials: 'same-origin' });
        const data = await res.json();
        searchSuggestions.innerHTML = (data.results || []).map((item) => (
          `<a href="${item.url}" class="block rounded-lg px-3 py-2 transition hover:bg-slate-50">
            <div class="text-sm font-semibold text-slate-900">${item.label}</div>
            <div class="text-xs text-slate-500">${item.subtext || ''}</div>
          </a>`
        )).join('') || '<div class="px-3 py-2 text-sm text-slate-500">No suggestions found.</div>';
        searchSuggestions.classList.remove('hidden');
      } catch (_) {
        searchSuggestions.innerHTML = '<div class="px-3 py-2 text-sm text-red-500">Search unavailable.</div>';
        searchSuggestions.classList.remove('hidden');
      }
    }, 180);
  });
  document.addEventListener('click', (event) => {
    if (searchSuggestions && !searchSuggestions.contains(event.target) && event.target !== searchInput) {
      searchSuggestions.classList.add('hidden');
    }
  });
  document.getElementById('mobileSearchToggle')?.addEventListener('click', () => searchInput?.focus());

  const money = (value) => `\u09F3${value || '0.00'}`;

  const updateCartBadge = (count) => {
    document.querySelectorAll('a[href="/orders/cart/"]').forEach((toggle) => {
      let badge = toggle.querySelector('.badge');
      if (count > 0) {
        if (!badge) {
          badge = document.createElement('span');
          badge.className = 'badge absolute -right-1 -top-1 grid min-h-5 min-w-5 place-items-center rounded-full bg-primary px-1 text-[10px] font-bold text-white';
          toggle.appendChild(badge);
        }
        badge.textContent = String(count);
      } else {
        badge?.remove();
      }
    });
  };

  const updateCartSummary = (data) => {
    const totals = data?.cart_totals || {};
    const setText = (selector, value) => {
      document.querySelectorAll(selector).forEach((node) => { node.textContent = value; });
    };
    if (totals.subtotal || data?.cart_subtotal) setText('.cart-subtotal-value', money(totals.subtotal || data.cart_subtotal));
    if (typeof totals.coupon_discount !== 'undefined') setText('.cart-coupon-discount-value', `-${money(totals.coupon_discount)}`);
    if (typeof totals.reward_discount !== 'undefined') setText('.cart-reward-discount-value', `-${money(totals.reward_discount)}`);
    if (typeof totals.total !== 'undefined') setText('.cart-total-value', money(totals.total));
    if (typeof totals.free_delivery_remaining !== 'undefined') setText('.cart-free-delivery-remaining', money(totals.free_delivery_remaining));
  };

  document.addEventListener('submit', async (event) => {
    const form = event.target.closest('form.js-add-to-cart-ajax');
    if (!form) return;
    event.preventDefault();
    const button = form.querySelector("button[type='submit']");
    button && (button.disabled = true);
    try {
      const res = await fetch(form.action, {
        method: 'POST',
        headers: { 'X-Requested-With': 'XMLHttpRequest' },
        credentials: 'same-origin',
        body: new FormData(form),
      });
      const data = await res.json();
      if (!data.ok) throw new Error('cart add failed');
      updateCartBadge(Number(data.cart_count || 0));
      updateCartSummary(data);
      notify(data.message || 'Added to cart.');
    } catch (_) {
      form.submit();
    } finally {
      button && (button.disabled = false);
    }
  });

  document.addEventListener('change', async (event) => {
    const input = event.target.closest('.cart-qty-input');
    if (!input) return;
    const form = input.closest('form.js-cart-update-form');
    if (!form) return;
    try {
      const res = await fetch(form.action, {
        method: 'POST',
        headers: { 'X-Requested-With': 'XMLHttpRequest' },
        credentials: 'same-origin',
        body: new FormData(form),
      });
      const data = await res.json();
      if (!data.ok) throw new Error('cart update failed');
      const line = form.closest('.cart-line');
      if (Number(data.item_quantity || 0) <= 0) line?.remove();
      const totalNode = line?.querySelector('.cart-line-total');
      if (totalNode && data.item_total) totalNode.textContent = money(data.item_total);
      updateCartBadge(Number(data.cart_count || 0));
      updateCartSummary(data);
    } catch (_) {
      form.submit();
    }
  });

  document.addEventListener('submit', async (event) => {
    const form = event.target.closest('form.js-cart-remove-form');
    if (!form) return;
    event.preventDefault();
    try {
      const res = await fetch(form.action, {
        method: 'POST',
        headers: { 'X-Requested-With': 'XMLHttpRequest' },
        credentials: 'same-origin',
        body: new FormData(form),
      });
      const data = await res.json();
      if (!data.ok) throw new Error('cart remove failed');
      form.closest('.cart-line')?.remove();
      updateCartBadge(Number(data.cart_count || 0));
      updateCartSummary(data);
      notify('Item removed from cart.');
      if (Number(data.cart_count || 0) <= 0 && document.body.contains(document.querySelector('[data-cart-content]'))) {
        window.location.reload();
      }
    } catch (_) {
      form.submit();
    }
  });

  document.addEventListener('submit', async (event) => {
    const form = event.target.closest('form.js-wishlist-ajax');
    if (!form) return;
    event.preventDefault();
    try {
      const res = await fetch(form.action, {
        method: 'POST',
        headers: { 'X-Requested-With': 'XMLHttpRequest' },
        credentials: 'same-origin',
        body: new FormData(form),
      });
      const data = await res.json();
      if (!data.ok) throw new Error('wishlist failed');
      document.querySelectorAll('.js-wishlist-link').forEach((link) => {
        let badge = link.querySelector('.js-wishlist-badge');
        const count = Number(data.wishlist_count || 0);
        if (count > 0) {
          if (!badge) {
            badge = document.createElement('span');
            badge.className = 'js-wishlist-badge absolute -right-1 -top-1 grid min-h-5 min-w-5 place-items-center rounded-full bg-accent px-1 text-[10px] font-bold text-white';
            link.appendChild(badge);
          }
          badge.textContent = String(count);
        } else {
          badge?.remove();
        }
      });
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
  const shopStatus = document.getElementById('shopResultsStatus');

  const fetchShop = async (append = false, page = 1) => {
    if (!shopForm || !shopGrid) return;
    const params = new URLSearchParams(new FormData(shopForm));
    params.set('page', String(page));
    shopGrid.classList.add('is-loading');
    shopStatus && (shopStatus.textContent = 'Loading products...');
    try {
      const res = await fetch(`${shopForm.action}?${params.toString()}`, {
        headers: { 'X-Requested-With': 'XMLHttpRequest' },
        credentials: 'same-origin',
      });
      const data = await res.json();
      if (!data.ok) throw new Error('shop fetch failed');
      if (append) {
        const doc = new DOMParser().parseFromString(data.html, 'text/html');
        const incomingCards = doc.querySelectorAll('#shopProductsGrid > *');
        const target = shopGrid.querySelector('#shopProductsGrid');
        incomingCards.forEach((node) => target?.appendChild(node));
        shopGrid.querySelector('.js-load-more-products')?.remove();
        doc.querySelector('.js-load-more-products') && shopGrid.appendChild(doc.querySelector('.js-load-more-products'));
      } else {
        shopGrid.innerHTML = data.html;
      }
      if (shopNav && data.nav_html) shopNav.innerHTML = data.nav_html;
      if (shopCount) shopCount.textContent = `${data.count} products`;
      shopStatus && (shopStatus.textContent = '');
      refreshIcons();
    } finally {
      shopGrid.classList.remove('is-loading');
    }
  };

  if (shopForm && shopGrid) {
    shopForm.addEventListener('submit', (event) => {
      event.preventDefault();
      fetchShop(false, 1);
    });
    shopForm.addEventListener('change', (event) => {
      const target = event.target;
      if (target.matches('input, select')) fetchShop(false, 1);
    });
    let debounceTimer = null;
    document.getElementById('shopSearch')?.addEventListener('input', () => {
      clearTimeout(debounceTimer);
      debounceTimer = setTimeout(() => fetchShop(false, 1), 260);
    });
    document.addEventListener('click', (event) => {
      const button = event.target.closest('.js-load-more-products');
      if (!button) return;
      fetchShop(true, Number(button.dataset.nextPage || 2));
    });
  }

  const detailImage = document.querySelector('.detail-main-image');
  document.querySelectorAll('.detail-thumb').forEach((thumb) => {
    thumb.addEventListener('click', () => {
      const image = thumb.querySelector('img');
      if (!detailImage || !image) return;
      detailImage.src = image.src;
      document.querySelectorAll('.detail-thumb').forEach((node) => node.classList.remove('active-thumb', 'border-primary'));
      thumb.classList.add('active-thumb', 'border-primary');
    });
  });

  const qtyInput = document.querySelector('.js-detail-quantity');
  const detailPrice = document.getElementById('detailPrice');
  const detailTotalPrice = document.getElementById('detailTotalPrice');
  const mobileDetailTotal = document.getElementById('mobileDetailTotalPrice');
  const variantInput = document.getElementById('variantIdInput');
  const detailSku = document.getElementById('detailSku');
  const stockLabel = document.getElementById('variantStockLabel');
  const addToCartButton = document.getElementById('addToCartButton');

  const updateDetailTotal = () => {
    if (!qtyInput || !detailPrice || !detailTotalPrice) return;
    const unitPrice = Number(detailPrice.dataset.currentPrice || detailPrice.dataset.basePrice || 0);
    const quantity = Math.max(Number(qtyInput.value || 1), 1);
    const total = money((unitPrice * quantity).toFixed(2));
    detailTotalPrice.textContent = total;
    if (mobileDetailTotal) mobileDetailTotal.textContent = total;
  };

  document.querySelectorAll('.js-qty-button').forEach((button) => {
    button.addEventListener('click', () => {
      if (!qtyInput) return;
      const step = Number(button.dataset.step || 0);
      const max = Number(qtyInput.max || 99);
      const next = Math.min(Math.max(Number(qtyInput.value || 1) + step, 1), max);
      qtyInput.value = String(next);
      updateDetailTotal();
    });
  });
  qtyInput?.addEventListener('input', updateDetailTotal);

  document.querySelectorAll('.js-variant-option').forEach((button) => {
    button.addEventListener('click', () => {
      document.querySelectorAll('.js-variant-option').forEach((node) => node.classList.remove('active', 'border-primary', 'bg-primary', 'text-white'));
      button.classList.add('active', 'border-primary', 'bg-primary', 'text-white');
      if (variantInput) variantInput.value = button.dataset.variantId || '';
      if (detailPrice) {
        detailPrice.dataset.currentPrice = button.dataset.price || detailPrice.dataset.basePrice || '0.00';
        detailPrice.textContent = money(button.dataset.price || detailPrice.dataset.basePrice || '0.00');
      }
      if (detailSku) detailSku.textContent = button.dataset.sku || detailSku.textContent;
      const stock = Number(button.dataset.stock || 0);
      if (qtyInput) {
        qtyInput.max = String(Math.max(stock, 1));
        qtyInput.value = String(Math.min(Math.max(Number(qtyInput.value || 1), 1), Math.max(stock, 1)));
      }
      if (stockLabel) {
        stockLabel.textContent = stock > 0 ? 'In stock' : 'Out of stock';
        stockLabel.classList.toggle('text-success', stock > 0);
        stockLabel.classList.toggle('text-accent', stock <= 0);
      }
      if (addToCartButton) addToCartButton.disabled = stock <= 0;
      updateDetailTotal();
    });
  });
  updateDetailTotal();

  document.querySelectorAll('[data-countdown]').forEach((node) => {
    const target = new Date(node.dataset.countdown).getTime();
    if (Number.isNaN(target)) return;
    const updateCountdown = () => {
      const diff = Math.max(target - Date.now(), 0);
      const days = Math.floor(diff / 86400000);
      const hours = Math.floor((diff % 86400000) / 3600000);
      const minutes = Math.floor((diff % 3600000) / 60000);
      const seconds = Math.floor((diff % 60000) / 1000);
      node.querySelector('.countdown-days') && (node.querySelector('.countdown-days').textContent = String(days).padStart(2, '0'));
      node.querySelector('.countdown-hours') && (node.querySelector('.countdown-hours').textContent = String(hours).padStart(2, '0'));
      node.querySelector('.countdown-minutes') && (node.querySelector('.countdown-minutes').textContent = String(minutes).padStart(2, '0'));
      node.querySelector('.countdown-seconds') && (node.querySelector('.countdown-seconds').textContent = String(seconds).padStart(2, '0'));
    };
    updateCountdown();
    setInterval(updateCountdown, 1000);
  });

  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape') {
      setAccountMenu(false);
      setMegaMenu(false);
    }
  });
});
