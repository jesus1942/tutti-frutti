// Configuración para WebSocket
const SERVER_URL = window.tuttiConfig?.wsBase || '';

console.log("Configuración del WebSocket:", SERVER_URL || 'sin backend configurado');

/**
 * Función para conectar a una sala de juego mediante WebSocket
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

    // Codificar parámetros para evitar problemas con caracteres especiales
    const encodedGameId = encodeURIComponent(gameId);
    const encodedPlayerName = encodeURIComponent(playerName);
    
    // Construir URL para el WebSocket
    const socketUrl = `${SERVER_URL}/ws/${encodedGameId}/${encodedPlayerName}`;
    
    console.log(`Intentando conectar a: ${socketUrl}`);
    window.auth.showToast(`Conectando a sala ${gameId}...`, 'info');
    
    try {
        // Crear conexión WebSocket
        const socket = new WebSocket(socketUrl);
        
        // Configurar timeout para detectar problemas de conexión
        const connectionTimeout = setTimeout(() => {
            if (socket.readyState !== WebSocket.OPEN) {
                console.error('Timeout de conexión WebSocket después de 5 segundos');
                window.auth.showToast('Error de conexión. Verifica que el servidor esté en ejecución.', 'error');
            }
        }, 5000);
        
        // Evento: conexión establecida
        socket.onopen = () => {
            console.log('✅ Conexión establecida correctamente');
            clearTimeout(connectionTimeout);
            window.auth.showToast(`¡Conexión establecida! Bienvenido a la sala ${gameId}`, 'success');
            
            // Actualizar estado del juego
            window.gameState.websocket = socket;
            window.gameState.gameId = gameId;
            window.gameState.playerName = playerName;
            
            // Mostrar sala de espera
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
            window.auth.showToast(`La conexión con el servidor se ha cerrado.`, 'error');
        };
        
        // Evento: error de conexión
        socket.onerror = (error) => {
            console.error('Error en la conexión WebSocket:', error);
            window.auth.showToast(`Error de conexión al servidor.`, 'error');
        };
        
        return socket;
    } catch (error) {
        console.error('Error al crear el WebSocket:', error);
        window.auth.showToast(`No se pudo crear la conexión WebSocket: ${error.message}`, 'error');
        return null;
    }
}

// Exponer la función globalmente
window.connectToGame = connectToGame;
