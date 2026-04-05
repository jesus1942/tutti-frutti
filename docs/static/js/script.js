function createInitialGameState() {
    return {
        gameId: '',
        playerName: '',
        websocket: null,
        status: 'waiting',
        players: {},
        currentLetter: '',
        rounds: 0,
        maxRounds: 5,
        categories: [],
        timer: 60,
        timeLeft: 60,
        answers: {},
        scores: {},
        roundScores: {},
        transitioningToRound: false,
        botEnabled: false,
        botName: 'CPU Austral',
        admin: '',
        stopMode: 'individual',
        autoValidate: true,
        isAdmin: false,
        lastWinner: null,
        chatMessages: [],
        validatedAnswers: {},
        validationReasons: {},
        submittedThisRound: false
    };
}

window.gameState = createInitialGameState();

let countdownInterval = null;
let uiFrame = null;

const screens = {
    welcome: document.getElementById('welcome-screen'),
    waiting: document.getElementById('waiting-room'),
    game: document.getElementById('game-screen'),
    review: document.getElementById('review-screen'),
    scores: document.getElementById('scores-screen')
};

window.showScreen = function(screenName) {
    Object.values(screens).forEach(screen => {
        if (screen) {
            screen.classList.remove('active');
        }
    });

    if (screens[screenName]) {
        screens[screenName].classList.add('active');
    }
};

window.updateGameState = function(data) {
    const previousStatus = gameState.status;

    gameState.status = data.status || gameState.status;
    gameState.players = data.players ?? gameState.players;
    gameState.currentLetter = data.current_letter ?? gameState.currentLetter;
    gameState.rounds = data.rounds ?? gameState.rounds;
    gameState.maxRounds = data.max_rounds ?? gameState.maxRounds;
    gameState.categories = data.categories ?? gameState.categories;
    gameState.timer = data.timer ?? gameState.timer;
    gameState.timeLeft = data.time_left ?? gameState.timeLeft;
    gameState.answers = data.answers ?? gameState.answers;
    gameState.scores = data.scores ?? gameState.scores;
    gameState.roundScores = data.round_scores ?? gameState.roundScores;
    gameState.transitioningToRound = Boolean(data.transitioning_to_round);
    gameState.botEnabled = Boolean(data.bot_enabled);
    gameState.botName = data.bot_name ?? gameState.botName;
    gameState.admin = data.admin ?? gameState.admin;
    gameState.stopMode = data.stop_mode ?? gameState.stopMode;
    gameState.autoValidate = data.auto_validate !== undefined ? data.auto_validate : gameState.autoValidate;
    gameState.lastWinner = data.last_winner ?? gameState.lastWinner;
    gameState.chatMessages = data.chat_messages ?? gameState.chatMessages;
    gameState.validatedAnswers = data.validated_answers ?? gameState.validatedAnswers;
    gameState.validationReasons = data.validation_reasons ?? gameState.validationReasons;
    gameState.isAdmin = gameState.playerName === gameState.admin;

    if (previousStatus !== gameState.status && gameState.status === 'playing') {
        gameState.submittedThisRound = false;
        renderCategoryInputs();
    }

    scheduleUIRefresh();
};

function scheduleUIRefresh() {
    if (uiFrame !== null) {
        return;
    }

    uiFrame = window.requestAnimationFrame(() => {
        uiFrame = null;
        updateUI();
    });
}

function updateUI() {
    updatePlayerList();
    updateRoundInfo();
    updateAdminPanel();
    syncCategoryInputs();
    renderReview();
    renderScores();
    syncReadyCheckbox();
    updateActionButtons();
    syncScreen();
    syncTimer();
}

function updateRoundInfo() {
    const roundNumber = document.getElementById('round-number');
    const maxRoundsDisplay = document.getElementById('max-rounds');
    const currentLetterDisplay = document.getElementById('current-letter');
    const reviewLetter = document.getElementById('review-letter');
    const timeLeft = document.getElementById('time-left');

    if (roundNumber) roundNumber.textContent = String(gameState.rounds + 1);
    if (maxRoundsDisplay) maxRoundsDisplay.textContent = String(gameState.maxRounds);
    if (currentLetterDisplay) currentLetterDisplay.textContent = gameState.currentLetter || '-';
    if (reviewLetter) reviewLetter.textContent = gameState.currentLetter || '-';
    if (timeLeft) timeLeft.textContent = String(Math.max(0, gameState.timeLeft));
}

function updatePlayerList() {
    const playerList = document.getElementById('player-list');
    if (!playerList) return;

    playerList.innerHTML = '';

    Object.entries(gameState.players).forEach(([name, data]) => {
        const li = document.createElement('li');
        li.className = `player-card ${data.connected ? 'is-connected' : 'is-disconnected'}`;

        const isMe = name === gameState.playerName;
        const roleBadge = name === gameState.admin
            ? '<span class="player-badge role-admin">Admin</span>'
            : '';
        const botBadge = name === gameState.botName
            ? '<span class="player-badge role-bot">CPU</span>'
            : '';
        const selfBadge = isMe
            ? '<span class="player-badge role-self">Vos</span>'
            : '';
        const readyBadge = data.connected
            ? `<span class="player-badge ${data.ready ? 'state-ready' : 'state-waiting'}">${data.ready ? 'Listo' : 'Esperando'}</span>`
            : '<span class="player-badge state-offline">Desconectado</span>';

        li.innerHTML = `
            <div class="player-main">
                <div class="player-name-row">
                    <span class="player-name">${escapeHtml(name)}</span>
                    <div class="player-badges">
                        ${selfBadge}
                        ${roleBadge}
                        ${botBadge}
                    </div>
                </div>
                <div class="player-meta">
                    ${readyBadge}
                </div>
            </div>
        `;
        playerList.appendChild(li);
    });
}

function updateAdminPanel() {
    const adminPanel = document.getElementById('admin-controls');
    if (!adminPanel) return;

    if (!gameState.isAdmin) {
        adminPanel.style.display = 'none';
        return;
    }

    adminPanel.style.display = 'block';

    const winnerMarkup = gameState.lastWinner
        ? `<p><strong>Último ganador:</strong> ${gameState.lastWinner.name} (${gameState.lastWinner.score} pts)</p>`
        : '';

    adminPanel.innerHTML = `
        <h3>Opciones de Administrador</h3>
        <p><strong>Modo STOP:</strong> ${gameState.stopMode}</p>
        <p><strong>Validación:</strong> ${gameState.autoValidate ? 'Automática' : 'Manual'}</p>
        <p><strong>Tiempo por ronda:</strong> ${gameState.timer}s</p>
        <p><strong>Modo CPU:</strong> ${gameState.botEnabled ? 'Activado' : 'Desactivado'}</p>
        ${winnerMarkup}
    `;
}

function renderCategoryInputs() {
    const container = document.getElementById('categories-container');
    if (!container) return;
    container.innerHTML = '';

    gameState.categories.forEach(category => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${category}</td>
            <td>
                <input
                    type="text"
                    class="category-input"
                    name="${category}"
                    data-category="${category}"
                    value=""
                    autocomplete="off"
                >
            </td>
        `;
        container.appendChild(tr);
    });

    syncCategoryInputs();
}

function syncCategoryInputs() {
    const container = document.getElementById('categories-container');
    if (!container) return;

    const existingInputs = Array.from(container.querySelectorAll('input[data-category]'));
    const currentCategories = existingInputs.map(input => input.dataset.category);
    const categoriesChanged = currentCategories.length !== gameState.categories.length
        || currentCategories.some((category, index) => category !== gameState.categories[index]);

    if (categoriesChanged) {
        renderCategoryInputs();
        return;
    }

    const shouldDisable = gameState.status !== 'playing' || gameState.submittedThisRound;
    existingInputs.forEach(input => {
        input.disabled = shouldDisable;
    });
}

function renderReview() {
    const container = document.getElementById('all-answers-container');
    if (!container) return;

    container.innerHTML = '';

    const players = Object.keys(gameState.answers);
    if (!players.length) {
        container.innerHTML = '<p>Aún no hay respuestas para revisar.</p>';
        return;
    }

    players.forEach(player => {
        const block = document.createElement('div');
        block.className = 'review-block';

        const rows = gameState.categories.map(category => {
            const answer = gameState.answers[player]?.[category] || '';
            const points = gameState.validatedAnswers[player]?.[category];
            const reason = gameState.validationReasons[player]?.[category];
            const scoreText = typeof points === 'number' ? `${points} pts` : 'Pendiente';
            const reasonText = reason ? ` · ${reason}` : '';
            return `<li><strong>${category}:</strong> ${escapeHtml(answer)} <span>(${scoreText}${reasonText})</span></li>`;
        }).join('');

        block.innerHTML = `<h4>${player}</h4><ul>${rows}</ul>`;
        container.appendChild(block);
    });
}

function renderScores() {
    const container = document.getElementById('scores-container');
    const highlight = document.getElementById('score-highlight');
    const podium = document.getElementById('score-podium');
    if (!container || !highlight || !podium) return;

    container.innerHTML = '';
    highlight.innerHTML = '';
    podium.innerHTML = '';

    const orderedScores = Object.entries(gameState.scores)
        .sort((a, b) => b[1] - a[1]);

    if (!orderedScores.length) {
        highlight.innerHTML = '<div class="score-highlight-card">Todavía no hay puntajes cargados.</div>';
        return;
    }

    const [leaderName, leaderPoints] = orderedScores[0];
    const distributedPoints = orderedScores.reduce((sum, [, points]) => sum + points, 0);
    highlight.innerHTML = `
        <div class="score-highlight-card">
            <div class="score-orbit">
                <span class="score-orbit-ring ring-a"></span>
                <span class="score-orbit-ring ring-b"></span>
                <span class="score-orbit-core"></span>
            </div>
            <div class="score-highlight-copy">
                <div class="score-highlight-label">Comandando la órbita</div>
                <div class="score-highlight-main">
                    <span class="score-highlight-name">${escapeHtml(leaderName)}</span>
                    <span class="score-highlight-points">${leaderPoints} pts</span>
                </div>
                <div class="score-highlight-meta">
                    <span>${orderedScores.length} jugadores</span>
                    <span>${distributedPoints} puntos distribuidos</span>
                </div>
            </div>
        </div>
    `;

    orderedScores.slice(0, 3).forEach(([player, points], index) => {
        const medal = getMedalLabel(index);
        const card = document.createElement('div');
        card.className = `podium-card podium-tier-${index + 1} medal-${medal.toLowerCase()} ${player === gameState.playerName ? 'is-self' : ''}`;
        card.innerHTML = `
            <div class="podium-topline">Posición ${index + 1}</div>
            <div class="podium-medal">${medal}</div>
            <div class="podium-player">${escapeHtml(player)}</div>
            <div class="podium-points">${points} pts</div>
            <div class="podium-ring"></div>
        `;
        podium.appendChild(card);
    });

    orderedScores.forEach(([player, points], index) => {
        const medal = getMedalLabel(index);
        const rounds = [];
        for (let round = 1; round <= gameState.maxRounds; round += 1) {
            const roundValue = gameState.roundScores[player]?.[String(round)];
            if (typeof roundValue === 'number') {
                rounds.push(`<span class="round-chip">R${round} <strong>${roundValue}</strong></span>`);
            }
        }

        const row = document.createElement('div');
        row.className = 'score-row';
        if (player === gameState.playerName) {
            row.classList.add('score-row-self');
        }
        row.innerHTML = `
            <div class="score-row-index">${index + 1}</div>
            <div class="score-row-body">
                <div class="score-row-top">
                    <span class="score-row-name">${escapeHtml(player)}</span>
                    <span class="score-row-medal medal-${medal.toLowerCase()}">${medal}</span>
                </div>
                <div class="score-row-rounds">${rounds.length ? rounds.join('') : '<span class="round-chip is-empty">Sin ronda cerrada</span>'}</div>
            </div>
            <div class="score-row-total">
                <span class="score-row-points">${points}</span>
                <span class="score-row-unit">pts</span>
            </div>
        `;
        container.appendChild(row);
    });
}

function getMedalLabel(index) {
    if (index === 0) return 'Oro';
    if (index === 1) return 'Plata';
    if (index === 2) return 'Bronce';
    return '-';
}

function syncReadyCheckbox() {
    const readyCheckbox = document.getElementById('ready-checkbox');
    if (!readyCheckbox) return;

    const me = gameState.players[gameState.playerName];
    readyCheckbox.checked = Boolean(me?.ready);
    readyCheckbox.disabled = gameState.status !== 'waiting';
}

function updateActionButtons() {
    const validateBtn = document.getElementById('validate-btn');
    const nextRoundBtn = document.getElementById('next-round-btn');
    const endGameBtn = document.getElementById('end-game-btn');
    const backToHomeBtn = document.getElementById('back-to-home-btn');

    if (validateBtn) {
        validateBtn.style.display = gameState.isAdmin && gameState.status === 'reviewing' ? 'inline-block' : 'none';
    }

    if (nextRoundBtn) {
        nextRoundBtn.style.display = gameState.isAdmin && gameState.status === 'scores' ? 'inline-block' : 'none';
        nextRoundBtn.disabled = gameState.transitioningToRound;
        nextRoundBtn.textContent = gameState.transitioningToRound ? 'Sincronizando...' : 'Siguiente Ronda';
    }

    if (endGameBtn) {
        endGameBtn.style.display = gameState.isAdmin && ['scores', 'reviewing', 'playing'].includes(gameState.status)
            ? 'inline-block'
            : 'none';
    }

    if (backToHomeBtn) {
        backToHomeBtn.style.display = ['finished', 'scores', 'waiting'].includes(gameState.status)
            ? 'inline-block'
            : 'none';
    }
}

function syncScreen() {
    switch (gameState.status) {
        case 'waiting':
            window.showScreen('waiting');
            break;
        case 'playing':
            window.showScreen('game');
            break;
        case 'reviewing':
            window.showScreen('review');
            break;
        case 'scores':
        case 'finished':
            window.showScreen('scores');
            break;
        default:
            window.showScreen('welcome');
            break;
    }
}

function syncTimer() {
    clearInterval(countdownInterval);

    if (gameState.status !== 'playing') {
        return;
    }

    const timeLeft = document.getElementById('time-left');
    if (timeLeft) {
        timeLeft.textContent = String(Math.max(0, gameState.timeLeft));
    }

    countdownInterval = setInterval(() => {
        gameState.timeLeft = Math.max(0, gameState.timeLeft - 1);
        if (timeLeft) {
            timeLeft.textContent = String(gameState.timeLeft);
        }

        if (gameState.timeLeft === 0) {
            clearInterval(countdownInterval);
            submitAnswers(false);
        }
    }, 1000);
}

function handleJoinGame(event) {
    event.preventDefault();

    const playerNameInput = document.getElementById('player-name');
    const gameIdInput = document.getElementById('game-id');
    const playVsBotInput = document.getElementById('play-vs-bot');
    if (!playerNameInput || !gameIdInput) return;

    const playerName = playerNameInput.value.trim();
    let gameId = gameIdInput.value.trim();

    if (!playerName) {
        window.auth.showToast('Por favor, ingresa tu nombre.', 'error');
        return;
    }

    if (!gameId) {
        gameId = Math.random().toString(36).substring(2, 8).toUpperCase();
    }

    window.connectToGame(gameId, playerName, {
        botEnabled: Boolean(playVsBotInput?.checked)
    });
}

function readCurrentAnswers() {
    const inputs = document.querySelectorAll('#categories-container input');
    const answers = {};

    inputs.forEach(input => {
        answers[input.name] = input.value.trim();
    });

    return answers;
}

function submitAnswers(stopPressed) {
    if (gameState.submittedThisRound || !socketReady()) {
        return;
    }

    const answers = readCurrentAnswers();
    gameState.submittedThisRound = true;

    gameState.websocket.send(JSON.stringify({
        type: 'submit_answers',
        answers,
        stop_pressed: stopPressed
    }));

    renderCategoryInputs();
    window.auth.showToast(stopPressed ? 'Respuestas enviadas. ¡STOP!' : 'Tiempo terminado. Respuestas enviadas.', 'info');
}

function handleAnswersSubmit(event) {
    event.preventDefault();
    submitAnswers(true);
}

function handleReadyChange(event) {
    if (!socketReady()) return;

    gameState.websocket.send(JSON.stringify({
        type: 'ready',
        ready: event.target.checked
    }));
}

function handleValidateContinue() {
    if (!gameState.isAdmin || !socketReady()) return;

    gameState.websocket.send(JSON.stringify({
        type: 'continue_game'
    }));
}

function handleEndGame() {
    if (!gameState.isAdmin || !socketReady()) return;

    gameState.websocket.send(JSON.stringify({
        type: 'end_game'
    }));
}

function resetLocalSession(options = {}) {
    const previousPlayerName = options.keepPlayerName ? gameState.playerName : '';
    const previousBackendWinner = gameState.lastWinner;
    Object.assign(gameState, createInitialGameState());
    gameState.playerName = previousPlayerName;
    gameState.lastWinner = previousBackendWinner;
    clearInterval(countdownInterval);
    countdownInterval = null;

    const roomIdDisplay = document.getElementById('room-id-display');
    if (roomIdDisplay) {
        roomIdDisplay.textContent = '';
    }

    const answersContainer = document.getElementById('categories-container');
    if (answersContainer) {
        answersContainer.innerHTML = '';
    }

    const reviewContainer = document.getElementById('all-answers-container');
    if (reviewContainer) {
        reviewContainer.innerHTML = '';
    }

    const scoresContainer = document.getElementById('scores-container');
    if (scoresContainer) {
        scoresContainer.innerHTML = '';
    }

    const scoreHighlight = document.getElementById('score-highlight');
    if (scoreHighlight) {
        scoreHighlight.innerHTML = '';
    }

    const scorePodium = document.getElementById('score-podium');
    if (scorePodium) {
        scorePodium.innerHTML = '';
    }

    const readyCheckbox = document.getElementById('ready-checkbox');
    if (readyCheckbox) {
        readyCheckbox.checked = false;
    }

    window.showScreen('welcome');
}

function leaveCurrentGame(options = {}) {
    const socket = gameState.websocket;
    if (socket && socket.readyState === WebSocket.OPEN) {
        socket._intentionalClose = true;
        socket.close(1000, 'Saliendo de la sala');
    }

    resetLocalSession({ keepPlayerName: true });

    if (!options.silent) {
        window.auth.showToast('Sesión cerrada. Ya podés crear o unirte a otra sala.', 'success');
    }
}

window.resetLocalSession = resetLocalSession;
window.leaveCurrentGame = leaveCurrentGame;

function handleCopyRoomId() {
    const roomId = gameState.gameId;
    if (!roomId) return;

    navigator.clipboard.writeText(roomId)
        .then(() => window.auth.showToast('ID de sala copiado.', 'success'))
        .catch(() => window.auth.showToast('No se pudo copiar el ID.', 'error'));
}

function handleBackToHome() {
    leaveCurrentGame();
}

function socketReady() {
    return gameState.websocket && gameState.websocket.readyState === WebSocket.OPEN;
}

function escapeHtml(value) {
    return value
        .replaceAll('&', '&amp;')
        .replaceAll('<', '&lt;')
        .replaceAll('>', '&gt;')
        .replaceAll('"', '&quot;');
}

function syncBackendLinks() {
    const adminLink = document.getElementById('admin-link');
    if (!adminLink) return;

    if (window.tuttiConfig?.adminUrl) {
        adminLink.href = window.tuttiConfig.adminUrl;
        adminLink.style.pointerEvents = 'auto';
        adminLink.style.opacity = '1';
        return;
    }

    adminLink.removeAttribute('href');
    adminLink.style.pointerEvents = 'none';
    adminLink.style.opacity = '0.6';
}

function renderBackendStatus() {
    const status = document.getElementById('backend-status');
    if (!status) return;

    if (window.tuttiConfig?.requiresBackend) {
        status.style.display = 'block';
        status.innerHTML = 'Esta versión estática necesita un backend. Abrila con <code>?backend=https://tu-backend</code>.';
        return;
    }

    if (window.tuttiConfig?.backendUrl) {
        status.style.display = 'block';
        status.textContent = `Backend conectado: ${window.tuttiConfig.backendUrl}`;
        return;
    }

    status.style.display = 'none';
}

document.addEventListener('DOMContentLoaded', () => {
    const joinForm = document.getElementById('join-form');
    const answersForm = document.getElementById('answers-form');
    const readyCheckbox = document.getElementById('ready-checkbox');
    const validateBtn = document.getElementById('validate-btn');
    const nextRoundBtn = document.getElementById('next-round-btn');
    const endGameBtn = document.getElementById('end-game-btn');
    const backToHomeBtn = document.getElementById('back-to-home-btn');
    const copyRoomIdBtn = document.getElementById('copy-room-id');

    if (joinForm) joinForm.addEventListener('submit', handleJoinGame);
    if (answersForm) answersForm.addEventListener('submit', handleAnswersSubmit);
    if (readyCheckbox) readyCheckbox.addEventListener('change', handleReadyChange);
    if (validateBtn) validateBtn.addEventListener('click', handleValidateContinue);
    if (nextRoundBtn) nextRoundBtn.addEventListener('click', handleValidateContinue);
    if (endGameBtn) endGameBtn.addEventListener('click', handleEndGame);
    if (backToHomeBtn) backToHomeBtn.addEventListener('click', handleBackToHome);
    if (copyRoomIdBtn) copyRoomIdBtn.addEventListener('click', handleCopyRoomId);

    syncBackendLinks();
    renderBackendStatus();
    window.showScreen('welcome');
});
