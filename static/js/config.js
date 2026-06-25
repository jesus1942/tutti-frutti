(function initTuttiConfig() {
    const queryParams = new URLSearchParams(window.location.search);
    const queryBackend = queryParams.get('backend');
    const explicitConfig = window.TUTTI_CONFIG || {};
    const storedBackend = window.localStorage.getItem('tutti_backend_url');

    // Backend desplegado en Render. Se usa por defecto cuando el frontend es
    // estatico (GitHub Pages o archivo local) y no se indico otro backend.
    const DEFAULT_BACKEND = 'https://tutti-frutti-backend.onrender.com';

    const normalizeBaseUrl = (value) => {
        if (!value) return '';
        return value.trim().replace(/\/+$/, '');
    };

    const isStaticHost = window.location.hostname.endsWith('github.io')
        || window.location.protocol === 'file:';

    const backendUrl = normalizeBaseUrl(
        queryBackend
        || explicitConfig.backendUrl
        || storedBackend
        || (isStaticHost ? DEFAULT_BACKEND : '')
    );

    if (queryBackend) {
        window.localStorage.setItem('tutti_backend_url', backendUrl);
    }

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';

    const wsBase = backendUrl
        ? backendUrl.replace(/^http:/, 'ws:').replace(/^https:/, 'wss:')
        : (isStaticHost ? '' : `${protocol}//${window.location.host}`);

    const adminUrl = backendUrl
        ? `${backendUrl}/admin`
        : (isStaticHost ? '' : '/admin');

    window.tuttiConfig = {
        backendUrl,
        wsBase,
        adminUrl,
        isStaticHost,
        requiresBackend: Boolean(isStaticHost && !backendUrl)
    };
})();
