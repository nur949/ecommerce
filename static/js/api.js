(function () {
  const getCookie = (name) => {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return decodeURIComponent(parts.pop().split(';').shift());
    return '';
  };

  const csrfToken = () => (
    document.querySelector('[name=csrfmiddlewaretoken]')?.value
    || document.querySelector('meta[name="csrf-token"]')?.content
    || getCookie('csrftoken')
  );

  const request = async (url, options = {}) => {
    const headers = new Headers(options.headers || {});
    headers.set('X-Requested-With', 'XMLHttpRequest');
    if (!headers.has('Accept')) headers.set('Accept', 'application/json');
    const method = (options.method || 'GET').toUpperCase();
    if (!['GET', 'HEAD', 'OPTIONS', 'TRACE'].includes(method) && !headers.has('X-CSRFToken')) {
      headers.set('X-CSRFToken', csrfToken());
    }

    const response = await fetch(url, {
      credentials: 'same-origin',
      ...options,
      headers,
    });
    const data = await response.json().catch(() => ({}));
    if (!response.ok || data.ok === false) {
      const error = new Error(data.error || data.message || 'Request failed.');
      error.status = response.status;
      error.data = data;
      throw error;
    }
    return data;
  };

  const form = (formNode) => request(formNode.action, {
    method: formNode.method || 'POST',
    body: new FormData(formNode),
  });

  const get = (url) => request(url);

  window.ZynvoApi = {
    csrfToken,
    form,
    get,
    request,
  };
}());
