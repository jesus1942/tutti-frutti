(function initTuttiConfig() {
    const queryParams = new URLSearchParams(window.location.search);
    const queryBackend = queryParams.get('backend');
    const explicitConfig = window.TUTTI_CONFIG || {};
    const storedBackend = window.localStorage.getItem('tutti_backend_url');

    const normalizeBaseUrl = (value) => {
        if (!value) return '';
        return value.trim().replace(/\/+$/, '');
    };

    const backendUrl = normalizeBaseUrl(
        queryBackend || explicitConfig.backendUrl || storedBackend || ''
    );

    if (queryBackend) {
        window.localStorage.setItem('tutti_backend_url', backendUrl);
    }

    const isStaticHost = window.location.hostname.endsWith('github.io')
        || window.location.protocol === 'file:';

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
