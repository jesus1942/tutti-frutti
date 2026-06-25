// Configuración para WebSocket
const SERVER_URL = window.tuttiConfig?.wsBase || '';

// Render (plan free) duerme el servicio tras inactividad y puede tardar hasta
// ~1 minuto en despertar. Por eso reintentamos la conexión durante ese lapso
// en lugar de cortar a los pocos segundos.
const CONNECT_BUDGET_MS = 70000;   // tiempo total que insistimos en conectar
const PER_ATTEMPT_MS = 9000;       // espera máxima por intento individual
const RETRY_GAP_MS = 2500;         // pausa entre reintentos

console.log("Configuración del WebSocket:", SERVER_URL || 'sin backend configurado');

/**
 * Función para conectar a una sala de juego mediante WebSocket.
 * Tolera el "cold start" de Render reintentando hasta CONNECT_BUDGET_MS.
 */
function connectToGame(gameId, playerName, options = {}) {
    if (!SERVER_URL) {
        window.auth.showToast(
            'Falta configurar el backend del juego. Agrega ?backend=https://tu-backend o define window.TUTTI_CONFIG.backendUrl.',
            'error',
            6000
        );
        return null;
    }

    if (window.gameState?.websocket) {
        const existingSocket = window.gameState.websocket;
        if (existingSocket.readyState === WebSocket.OPEN || existingSocket.readyState === WebSocket.CONNECTING) {
            existingSocket._intentionalClose = true;
            existingSocket.close(1000, 'Reiniciando sesión');
        }
    }

    if (typeof window.resetLocalSession === 'function') {
        window.resetLocalSession({ keepPlayerName: false });
    }

    // Codificar parámetros para evitar problemas con caracteres especiales
    const encodedGameId = encodeURIComponent(gameId);
    const encodedPlayerName = encodeURIComponent(playerName);
    const socketUrl = `${SERVER_URL}/ws/${encodedGameId}/${encodedPlayerName}`;
    const httpBase = window.tuttiConfig?.backendUrl;

    const deadline = Date.now() + CONNECT_BUDGET_MS;
    let attempt = 0;
    let wakingMsgShown = false;

    // "Golpe" HTTP para empezar a despertar el servicio cuanto antes (best effort).
    if (httpBase) {
        try {
            fetch(`${httpBase}/?wake=${Date.now()}`, { mode: 'no-cors', cache: 'no-store' }).catch(() => {});
        } catch (e) { /* ignorar */ }
    }

    window.auth.showToast(`Conectando a sala ${gameId}...`, 'info');

    const scheduleRetry = () => {
        if (Date.now() < deadline) {
            if (!wakingMsgShown) {
                wakingMsgShown = true;
                window.auth.showToast(
                    'Despertando el servidor (la primera vez puede tardar hasta 1 minuto)...',
                    'info',
                    9000
                );
            }
            setTimeout(attemptConnect, RETRY_GAP_MS);
        } else {
            window.auth.showToast(
                'No se pudo conectar al servidor. Esperá unos segundos y volvé a intentar.',
                'error',
                8000
            );
        }
    };

    function attemptConnect() {
        attempt += 1;
        console.log(`Intentando conectar a: ${socketUrl} (intento ${attempt})`);

        let settled = false;
        let socket;
        try {
            socket = new WebSocket(socketUrl);
        } catch (error) {
            console.error('Error al crear el WebSocket:', error);
            scheduleRetry();
            return;
        }

        const perAttemptTimeout = setTimeout(() => {
            if (!settled && socket.readyState !== WebSocket.OPEN) {
                socket._intentionalClose = true;   // evitar que onclose dispare otro retry
                try { socket.close(); } catch (e) { /* ignorar */ }
                scheduleRetry();
            }
        }, PER_ATTEMPT_MS);

        // Evento: conexión establecida
        socket.onopen = () => {
            settled = true;
            clearTimeout(perAttemptTimeout);
            console.log('Conexion establecida correctamente');
            window.auth.showToast(`¡Conexión establecida! Bienvenido a la sala ${gameId}`, 'success');

            window.gameState.websocket = socket;
            window.gameState.joined = true;
            window.gameState.gameId = gameId;
            window.gameState.playerName = playerName;

            window.showScreen('waiting');
            const roomIdDisplay = document.getElementById('room-id-display');
            if (roomIdDisplay) {
                roomIdDisplay.textContent = gameId;
            }

            if (options.botEnabled) {
                socket.send(JSON.stringify({
                    type: 'toggle_bot',
                    enabled: true
                }));
            }
        };

        // Evento: recepción de mensajes
        socket.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                console.log('Mensaje recibido:', data);
                window.updateGameState(data);
            } catch (error) {
                console.error('Error al procesar mensaje:', error);
            }
        };

        // Evento: cierre de conexión
        socket.onclose = (event) => {
            console.log(`Desconectado del servidor. Código: ${event.code}`);
            if (window.gameState.websocket === socket) {
                window.gameState.websocket = null;
            }

            if (socket._intentionalClose) {
                return;
            }

            // Cierre antes de abrir => el servidor seguramente sigue despertando: reintentar.
            if (!settled) {
                clearTimeout(perAttemptTimeout);
                scheduleRetry();
                return;
            }

            window.auth.showToast('La conexión con el servidor se ha cerrado.', 'error');
        };

        // Evento: error de conexión (dejamos que onclose decida el reintento)
        socket.onerror = (error) => {
            console.error('Error en la conexión WebSocket:', error);
        };
    }

    attemptConnect();
    return null;
}

// Exponer la función globalmente
window.connectToGame = connectToGame;
