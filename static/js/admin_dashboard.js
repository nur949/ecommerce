(function () {
  const root = document.querySelector('.pro-dashboard[data-dashboard-endpoint]');
  if (!root) return;

  const endpoint = root.dataset.dashboardEndpoint;
  const currency = new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 });
  const number = new Intl.NumberFormat('en-US');
  const charts = {};
  let payload = null;

  const getCookie = (name) => {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
    return '';
  };

  const setText = (selector, value) => {
    const node = root.querySelector(selector);
    if (node) node.textContent = value;
  };

  const escapeHtml = (value) => String(value || '').replace(/[&<>"']/g, (char) => ({
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#39;',
  }[char]));

  const shortDate = (value) => {
    try {
      return new Intl.DateTimeFormat('en-US', { month: 'short', day: 'numeric' }).format(new Date(value));
    } catch (_) {
      return value;
    }
  };

  const renderKpis = (data) => {
    setText('[data-kpi="users"]', number.format(data.users || 0));
    setText('[data-kpi="orders"]', number.format(data.orders || 0));
    setText('[data-kpi="revenue"]', currency.format(data.revenue || 0));
    setText('[data-kpi="growth"]', `${Number(data.growth || 0).toFixed(1)}%`);
    setText('#dashboardUpdatedAt', `Updated ${shortDate(data.generated_at)}`);
  };

  const chartDefaults = () => {
    if (!window.Chart) return;
    window.Chart.defaults.color = '#94a3b8';
    window.Chart.defaults.borderColor = 'rgba(148, 163, 184, .14)';
    window.Chart.defaults.font.family = 'Inter, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif';
  };

  const buildGradient = (ctx, color) => {
    const gradient = ctx.createLinearGradient(0, 0, 0, 320);
    gradient.addColorStop(0, color);
    gradient.addColorStop(1, 'rgba(8, 11, 18, 0)');
    return gradient;
  };

  const createCharts = () => {
    if (!payload || !window.Chart) return;
    chartDefaults();
    const labels = payload.chart_data.labels.map(shortDate);

    const revenueCanvas = document.getElementById('revenueChart');
    if (revenueCanvas && !charts.revenue) {
      const ctx = revenueCanvas.getContext('2d');
      charts.revenue = new window.Chart(ctx, {
        type: 'line',
        data: {
          labels,
          datasets: [{
            label: 'Revenue',
            data: payload.chart_data.revenue,
            fill: true,
            tension: .38,
            pointRadius: 0,
            borderWidth: 2,
            borderColor: '#22c55e',
            backgroundColor: buildGradient(ctx, 'rgba(34, 197, 94, .24)'),
          }],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          interaction: { intersect: false, mode: 'index' },
          plugins: {
            legend: { display: false },
            tooltip: { callbacks: { label: (item) => currency.format(item.parsed.y || 0) } },
          },
          scales: {
            x: { grid: { display: false }, ticks: { maxTicksLimit: 7 } },
            y: { beginAtZero: true, ticks: { callback: (value) => currency.format(value) } },
          },
        },
      });
    }

    const ordersCanvas = document.getElementById('ordersChart');
    if (ordersCanvas && !charts.orders) {
      charts.orders = new window.Chart(ordersCanvas, {
        type: 'bar',
        data: {
          labels,
          datasets: [{
            label: 'Orders',
            data: payload.chart_data.orders,
            borderRadius: 6,
            backgroundColor: 'rgba(96, 165, 250, .78)',
            hoverBackgroundColor: '#60a5fa',
          }],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: { legend: { display: false } },
          scales: {
            x: { grid: { display: false }, ticks: { maxTicksLimit: 6 } },
            y: { beginAtZero: true, ticks: { precision: 0 } },
          },
        },
      });
    }

    const usersCanvas = document.getElementById('usersChart');
    if (usersCanvas && !charts.users) {
      const ctx = usersCanvas.getContext('2d');
      charts.users = new window.Chart(ctx, {
        type: 'line',
        data: {
          labels,
          datasets: [{
            label: 'Users',
            data: payload.chart_data.users,
            fill: true,
            tension: .42,
            pointRadius: 0,
            borderWidth: 2,
            borderColor: '#a78bfa',
            backgroundColor: buildGradient(ctx, 'rgba(167, 139, 250, .24)'),
          }],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: { legend: { display: false } },
          scales: {
            x: { grid: { display: false }, ticks: { maxTicksLimit: 6 } },
            y: { beginAtZero: true, ticks: { precision: 0 } },
          },
        },
      });
    }
  };

  const lazyCharts = () => {
    if (!('IntersectionObserver' in window)) {
      createCharts();
      return;
    }
    const observer = new IntersectionObserver((entries) => {
      if (entries.some((entry) => entry.isIntersecting)) {
        createCharts();
        observer.disconnect();
      }
    }, { rootMargin: '160px' });
    root.querySelectorAll('[data-chart-lazy]').forEach((node) => observer.observe(node));
  };

  const renderOrders = (orders) => {
    const node = document.getElementById('recentOrdersList');
    if (!node) return;
    node.innerHTML = (orders || []).map((order) => `
      <div class="pro-list-item">
        <div>
          <strong>${escapeHtml(order.order_number)}</strong>
          <span>${escapeHtml(order.customer)} · ${shortDate(order.created_at)}</span>
        </div>
        <div>
          <small>${currency.format(order.total || 0)}</small>
          <span class="pro-status ${escapeHtml(order.status)}">${escapeHtml(order.status)}</span>
        </div>
      </div>
    `).join('') || '<div class="pro-list-item"><strong>No orders yet</strong><span>New orders will appear here.</span></div>';
  };

  const renderUsers = (users) => {
    const node = document.getElementById('latestUsersList');
    if (!node) return;
    node.innerHTML = (users || []).map((user) => `
      <div class="pro-list-item">
        <div>
          <strong>${escapeHtml(user.name)}</strong>
          <span>${escapeHtml(user.email)}</span>
        </div>
        <small>${shortDate(user.created_at)}</small>
      </div>
    `).join('') || '<div class="pro-list-item"><strong>No users yet</strong><span>Registrations will appear here.</span></div>';
  };

  const renderLogs = (logs) => {
    const node = document.getElementById('adminLogsList');
    if (!node) return;
    node.innerHTML = (logs || []).map((log) => `
      <div class="pro-list-item">
        <div>
          <strong>${escapeHtml(log.action)} · ${escapeHtml(log.object)}</strong>
          <span>${escapeHtml(log.user)}</span>
        </div>
        <small>${shortDate(log.created_at)}</small>
      </div>
    `).join('') || '<div class="pro-list-item"><strong>No logs yet</strong><span>Admin actions will appear here.</span></div>';
  };

  const renderActivity = (data) => {
    renderOrders(data.activity && data.activity.recent_orders);
    renderUsers(data.activity && data.activity.latest_users);
    renderLogs(data.activity && data.activity.logs);
  };

  const showError = (message) => {
    const node = document.getElementById('dashboardError');
    if (!node) return;
    node.style.display = 'block';
    node.textContent = message;
  };

  const loadDashboard = async () => {
    try {
      const response = await fetch(endpoint, {
        method: 'GET',
        credentials: 'same-origin',
        headers: {
          'X-Requested-With': 'XMLHttpRequest',
          'X-CSRFToken': getCookie('csrftoken'),
        },
      });
      const data = await response.json();
      if (!response.ok || !data.ok) throw new Error(data.error || 'Dashboard stats unavailable.');
      payload = data;
      renderKpis(data);
      renderActivity(data);
      lazyCharts();
    } catch (error) {
      showError(error.message || 'Dashboard stats unavailable.');
    }
  };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', loadDashboard);
  } else {
    loadDashboard();
  }
})();
