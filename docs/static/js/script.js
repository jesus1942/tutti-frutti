function createInitialGameState() {
    return {
        gameId: '',
        playerName: '',
        websocket: null,
        // Solo pasa a true cuando el jugador entra a una sala (WebSocket abierto).
        // Evita que el refresco inicial de la interfaz salte a la sala de espera
        // antes de que el jugador escriba su nombre y se una.
        joined: false,
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
        validationDetails: {},
        submittedThisRound: false,
        // Sorteo de la letra y modos de juego.
        currentThrower: null,
        wheel: {},
        twist: {},
        deck: 'clasico',
        decks: [],
        twistsEnabled: true,
        challenges: {},
        activeTimer: 60
    };
}

window.gameState = createInitialGameState();

let countdownInterval = null;
let uiFrame = null;

const screens = {
    welcome: document.getElementById('welcome-screen'),
    waiting: document.getElementById('waiting-room'),
    spin: document.getElementById('spin-screen'),
    game: document.getElementById('game-screen'),
    review: document.getElementById('review-screen'),
    scores: document.getElementById('scores-screen'),
    dashboard: document.getElementById('dashboard-screen')
};

// Clave para animar la rueda una sola vez por tirada.
let lastWheelKey = '';
let wheelSpinStarted = false;

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
    gameState.validationDetails = data.validation_details ?? gameState.validationDetails;
    gameState.currentThrower = data.current_thrower !== undefined ? data.current_thrower : gameState.currentThrower;
    gameState.wheel = data.wheel ?? gameState.wheel;
    gameState.twist = data.twist ?? gameState.twist;
    gameState.deck = data.deck ?? gameState.deck;
    gameState.decks = data.decks ?? gameState.decks;
    gameState.twistsEnabled = data.twists_enabled !== undefined ? data.twists_enabled : gameState.twistsEnabled;
    gameState.challenges = data.challenges ?? gameState.challenges;
    gameState.activeTimer = data.active_timer ?? gameState.activeTimer;
    gameState.isAdmin = gameState.playerName === gameState.admin;

    if (gameState.status !== 'reviewing') {
        gameState.challenges = data.challenges ?? {};
    }

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
    renderDeckPanel();
    renderSpin();
    renderTwistBanner('twist-banner-game');
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

    const deckLabel = (gameState.decks.find(d => d.id === gameState.deck) || {}).label || gameState.deck;
    adminPanel.innerHTML = `
        <h3>Opciones de Administrador</h3>
        <p><strong>Mazo:</strong> ${escapeHtml(deckLabel)}</p>
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

    const botName = gameState.botName;

    players.forEach(player => {
        const block = document.createElement('div');
        block.className = 'review-block';

        const rows = gameState.categories.map(category => {
            const answer = gameState.answers[player]?.[category] || '';
            const points = gameState.validatedAnswers[player]?.[category];
            const reason = gameState.validationReasons[player]?.[category];
            const scoreText = typeof points === 'number' ? `${points} pts` : 'Pendiente';
            const reasonText = reason ? ` · ${reason}` : '';

            const key = `${player}|${category}`;
            const challenge = gameState.challenges?.[key];
            let challengeMarkup = '';

            if (challenge) {
                const votes = Object.values(challenge.votes || {});
                const invalid = votes.filter(v => v === 'invalid').length;
                const valid = votes.filter(v => v === 'valid').length;
                const myVote = challenge.votes?.[gameState.playerName];
                challengeMarkup = `
                    <div class="challenge-box">
                        <span class="challenge-label">${escapeHtml(t('challenge-by', { name: challenge.opened_by || '' }))}</span>
                        <div class="challenge-vote">
                            <button type="button" class="vote-btn ${myVote === 'valid' ? 'is-picked' : ''}" data-challenge-action="valid" data-target="${escapeHtml(player)}" data-category="${escapeHtml(category)}">${escapeHtml(t('vote-valid', { n: valid }))}</button>
                            <button type="button" class="vote-btn ${myVote === 'invalid' ? 'is-picked' : ''}" data-challenge-action="invalid" data-target="${escapeHtml(player)}" data-category="${escapeHtml(category)}">${escapeHtml(t('vote-invalid', { n: invalid }))}</button>
                        </div>
                    </div>`;
            } else if (answer && player !== gameState.playerName && player !== botName) {
                challengeMarkup = `<button type="button" class="impugnar-btn" data-challenge-action="open" data-target="${escapeHtml(player)}" data-category="${escapeHtml(category)}">${escapeHtml(t('impugnar'))}</button>`;
            }

            let approveMarkup = '';
            if (gameState.isAdmin && answer && typeof reason === 'string'
                && reason.indexOf('a revisar') === 0 && points === 0) {
                approveMarkup = `<button type="button" class="approve-btn" data-approve-target="${escapeHtml(player)}" data-approve-category="${escapeHtml(category)}">${escapeHtml(t('approve'))}</button>`;
            }

            const answerText = answer ? escapeHtml(answer) : `<em>${escapeHtml(t('empty'))}</em>`;
            return `<li>
                <div class="review-row">
                    <span><strong>${escapeHtml(category)}:</strong> ${answerText} <span class="review-score">(${scoreText}${escapeHtml(reasonText)})</span></span>
                    ${approveMarkup}
                    ${challengeMarkup}
                </div>
            </li>`;
        }).join('');

        const selfTag = player === gameState.playerName ? `<span class="review-self">${escapeHtml(t('you'))}</span>` : '';
        block.innerHTML = `<h4>${escapeHtml(player)} ${selfTag}</h4><ul>${rows}</ul>`;
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
    // Mientras el jugador no se haya unido a una sala, la navegacion de pantallas
    // la maneja el flujo de bienvenida. Sin esta guarda, el primer refresco de la
    // interfaz (por ejemplo al aplicar el idioma) mandaria a la sala de espera con
    // el estado por defecto 'waiting' antes de que el jugador entre.
    if (!gameState.joined) {
        return;
    }

    switch (gameState.status) {
        case 'waiting':
            window.showScreen('waiting');
            break;
        case 'spinning':
            window.showScreen('spin');
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

// --- Mazos tematicos --------------------------------------------------------

function renderDeckPanel() {
    const panel = document.getElementById('deck-panel');
    const options = document.getElementById('deck-options');
    if (!panel || !options) return;

    if (gameState.status !== 'waiting' || !Array.isArray(gameState.decks) || !gameState.decks.length) {
        panel.style.display = 'none';
        return;
    }
    panel.style.display = 'block';

    options.innerHTML = '';
    gameState.decks.forEach(deck => {
        const btn = document.createElement('button');
        btn.type = 'button';
        btn.className = `deck-chip ${deck.id === gameState.deck ? 'is-active' : ''}`;
        btn.dataset.deck = deck.id;
        btn.disabled = !gameState.isAdmin;
        btn.innerHTML = `<span class="deck-chip-name">${escapeHtml(deckLabel(deck))}</span><span class="deck-chip-desc">${escapeHtml(deckDescription(deck))}</span>`;
        options.appendChild(btn);
    });

    const twistsCheckbox = document.getElementById('twists-checkbox');
    if (twistsCheckbox) {
        twistsCheckbox.checked = Boolean(gameState.twistsEnabled);
        twistsCheckbox.disabled = !gameState.isAdmin;
    }
}

function handleTwistsToggle(event) {
    if (!gameState.isAdmin || !socketReady()) return;
    gameState.websocket.send(JSON.stringify({ type: 'toggle_twists', enabled: event.target.checked }));
}

function handleDeckClick(event) {
    const chip = event.target.closest('.deck-chip');
    if (!chip || !gameState.isAdmin || !socketReady()) return;
    gameState.websocket.send(JSON.stringify({ type: 'set_deck', deck: chip.dataset.deck }));
}

// --- Rueda de la letra (sorteo justo verificable) ---------------------------

function polarPoint(cx, cy, radius, angleDeg) {
    const theta = (angleDeg * Math.PI) / 180;
    return { x: cx + radius * Math.sin(theta), y: cy - radius * Math.cos(theta) };
}

function buildWheel(pool) {
    const rotor = document.getElementById('wheel-rotor');
    if (!rotor) return;

    const signature = pool.join('');
    if (rotor.dataset.signature === signature) return;
    rotor.dataset.signature = signature;
    rotor.innerHTML = '';

    const cx = 160;
    const cy = 160;
    const radius = 150;
    const slice = 360 / pool.length;
    const svgNs = 'http://www.w3.org/2000/svg';

    pool.forEach((letter, index) => {
        const start = index * slice;
        const end = start + slice;
        const p0 = polarPoint(cx, cy, radius, start);
        const p1 = polarPoint(cx, cy, radius, end);
        const path = document.createElementNS(svgNs, 'path');
        path.setAttribute('d', `M ${cx} ${cy} L ${p0.x.toFixed(2)} ${p0.y.toFixed(2)} A ${radius} ${radius} 0 0 1 ${p1.x.toFixed(2)} ${p1.y.toFixed(2)} Z`);
        path.setAttribute('class', index % 2 === 0 ? 'wheel-slice slice-a' : 'wheel-slice slice-b');
        rotor.appendChild(path);

        const label = polarPoint(cx, cy, radius * 0.72, start + slice / 2);
        const text = document.createElementNS(svgNs, 'text');
        text.setAttribute('x', label.x.toFixed(2));
        text.setAttribute('y', label.y.toFixed(2));
        text.setAttribute('class', 'wheel-letter');
        text.setAttribute('text-anchor', 'middle');
        text.setAttribute('dominant-baseline', 'central');
        text.textContent = letter;
        rotor.appendChild(text);
    });
}

function animateWheelTo(letter, pool) {
    const rotor = document.getElementById('wheel-rotor');
    if (!rotor) return;
    const index = pool.indexOf(letter);
    if (index < 0) return;
    const slice = 360 / pool.length;
    const center = index * slice + slice / 2;
    const target = 360 * 6 - center;
    // Forzar reflow para reiniciar la transicion desde 0.
    rotor.style.transition = 'none';
    rotor.style.transform = 'rotate(0deg)';
    void rotor.getBoundingClientRect();
    rotor.style.transition = 'transform 3s cubic-bezier(0.16, 1, 0.3, 1)';
    rotor.style.transform = `rotate(${target}deg)`;
}

function renderSpin() {
    if (gameState.status !== 'spinning') {
        lastWheelKey = '';
        wheelSpinStarted = false;
        return;
    }

    const wheel = gameState.wheel || {};
    const pool = Array.isArray(wheel.allowed_letters) && wheel.allowed_letters.length
        ? wheel.allowed_letters
        : 'ABCDEFGHIJLMNOPRSTUV'.split('');
    buildWheel(pool);

    renderTwistBanner('twist-banner');

    const subtitle = document.getElementById('spin-subtitle');
    const spinBtn = document.getElementById('spin-btn');
    const spinWait = document.getElementById('spin-wait');
    const center = document.getElementById('wheel-center');
    const isThrower = !wheel.auto && gameState.playerName === wheel.thrower;

    const wheelKey = `${wheel.commit || ''}:${wheel.status || ''}`;

    if (wheel.status === 'committed') {
        if (center) center.textContent = '?';
        if (subtitle) {
            subtitle.textContent = wheel.auto
                ? t('spin-auto')
                : (isThrower ? t('spin-your-turn') : t('spin-thrower', { name: wheel.thrower || '' }));
        }
        if (spinBtn) {
            spinBtn.style.display = isThrower ? 'inline-block' : 'none';
            spinBtn.disabled = false;
        }
        if (spinWait) {
            spinWait.textContent = wheel.auto
                ? t('spin-auto-running')
                : (isThrower ? '' : t('spin-wait-thrower'));
        }
        lastWheelKey = wheelKey;
        wheelSpinStarted = false;
    } else if (wheel.status === 'revealed') {
        if (spinBtn) spinBtn.style.display = 'none';
        if (subtitle) subtitle.textContent = t('spin-revealed');
        if (spinWait) spinWait.textContent = '';

        if (lastWheelKey !== wheelKey || !wheelSpinStarted) {
            wheelSpinStarted = true;
            lastWheelKey = wheelKey;
            animateWheelTo(wheel.letter, pool);
            window.setTimeout(() => {
                const centerNow = document.getElementById('wheel-center');
                if (centerNow) centerNow.textContent = wheel.letter || '?';
            }, 2600);
        }
        updateFairPanel(wheel, pool);
    }
}

function renderTwistBanner(elId) {
    const banner = document.getElementById(elId);
    if (!banner) return;
    const twist = gameState.twist || {};
    if (!twist.label || twist.id === 'normal') {
        banner.textContent = '';
        banner.style.display = 'none';
        return;
    }
    const label = twistText(twist.id) || twist.label || '';
    const description = twistText(twist.id, '-desc') || twist.description || '';
    banner.style.display = 'block';
    banner.innerHTML = `<span class="twist-tag">${escapeHtml(t('twist-tag'))}</span> <strong>${escapeHtml(label)}</strong> — ${escapeHtml(description)}`;
}

async function sha256Hex(text) {
    const data = new TextEncoder().encode(text);
    const buffer = await crypto.subtle.digest('SHA-256', data);
    return Array.from(new Uint8Array(buffer)).map(b => b.toString(16).padStart(2, '0')).join('');
}

function randomHex(bytes) {
    const arr = new Uint8Array(bytes);
    crypto.getRandomValues(arr);
    return Array.from(arr).map(b => b.toString(16).padStart(2, '0')).join('');
}

async function updateFairPanel(wheel, pool) {
    const commitEl = document.getElementById('fair-commit');
    const serverEl = document.getElementById('fair-server');
    const clientEl = document.getElementById('fair-client');
    const resultEl = document.getElementById('fair-result');
    const verdictEl = document.getElementById('fair-verdict');
    if (commitEl) commitEl.textContent = (wheel.commit || '-').slice(0, 24) + '...';
    if (serverEl) serverEl.textContent = wheel.server_seed || '-';
    if (clientEl) clientEl.textContent = wheel.client_seed || '-';
    if (resultEl) resultEl.textContent = wheel.letter || '-';

    if (!verdictEl || !wheel.server_seed || !wheel.client_seed) return;
    try {
        const commitCheck = await sha256Hex(wheel.server_seed);
        const digest = await sha256Hex(`${wheel.server_seed}:${wheel.client_seed}`);
        const index = parseInt(digest.slice(0, 8), 16) % pool.length;
        const expected = pool[index];
        const ok = commitCheck === wheel.commit && expected === wheel.letter;
        verdictEl.textContent = ok ? t('fair-ok') : t('fair-bad');
        verdictEl.className = `fair-verdict ${ok ? 'ok' : 'bad'}`;
    } catch (error) {
        verdictEl.textContent = t('fair-novalid');
    }
}

function handleSpinClick() {
    const wheel = gameState.wheel || {};
    if (wheel.auto || gameState.playerName !== wheel.thrower || !socketReady()) return;
    const spinBtn = document.getElementById('spin-btn');
    if (spinBtn) spinBtn.disabled = true;
    gameState.websocket.send(JSON.stringify({ type: 'spin_wheel', client_seed: randomHex(8) }));
}

// --- Impugnaciones ----------------------------------------------------------

function handleChallengeAction(event) {
    const approveBtn = event.target.closest('.approve-btn');
    if (approveBtn && socketReady()) {
        gameState.websocket.send(JSON.stringify({
            type: 'approve_answer',
            target: approveBtn.dataset.approveTarget,
            category: approveBtn.dataset.approveCategory
        }));
        return;
    }

    const button = event.target.closest('[data-challenge-action]');
    if (!button || !socketReady()) return;
    const action = button.dataset.challengeAction;
    const target = button.dataset.target;
    const category = button.dataset.category;

    if (action === 'open') {
        gameState.websocket.send(JSON.stringify({ type: 'challenge_answer', target, category }));
    } else if (action === 'valid' || action === 'invalid') {
        gameState.websocket.send(JSON.stringify({ type: 'vote_challenge', target, category, vote: action }));
    }
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

// --- Helpers de traducción --------------------------------------------------

function t(key, params) {
    let text = (window.i18n && window.i18n.translate) ? window.i18n.translate(key) : key;
    if (params) {
        Object.keys(params).forEach(name => {
            text = text.replaceAll(`{${name}}`, params[name]);
        });
    }
    return text;
}

function deckLabel(deck) {
    const key = `deck-${deck.id}`;
    const translated = t(key);
    return translated === key ? deck.label : translated;
}

function deckDescription(deck) {
    const key = `deck-${deck.id}-desc`;
    const translated = t(key);
    return translated === key ? (deck.description || '') : translated;
}

function twistText(id, suffix) {
    const key = `twist-${id}${suffix || ''}`;
    const translated = t(key);
    return translated === key ? '' : translated;
}

// Permite que el cambio de idioma vuelva a dibujar el contenido dinámico.
window.refreshGameUI = function refreshGameUI() {
    if (typeof scheduleUIRefresh === 'function') {
        scheduleUIRefresh();
    }
};

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

// --- Lobby de salas activas -------------------------------------------------

function joinRoomById(roomId) {
    const playerNameInput = document.getElementById('player-name');
    const playerName = playerNameInput ? playerNameInput.value.trim() : '';
    if (!playerName) {
        window.auth.showToast(t('enter-name-first'), 'error');
        if (playerNameInput) playerNameInput.focus();
        return;
    }
    const gameIdInput = document.getElementById('game-id');
    if (gameIdInput) gameIdInput.value = roomId;
    const playVsBotInput = document.getElementById('play-vs-bot');
    window.connectToGame(roomId, playerName, { botEnabled: Boolean(playVsBotInput?.checked) });
}

function renderRooms(rooms) {
    const list = document.getElementById('rooms-list');
    if (!list) return;

    if (!rooms || rooms.length === 0) {
        list.innerHTML = `<li class="rooms-empty">${escapeHtml(t('rooms-empty'))}</li>`;
        return;
    }

    list.innerHTML = rooms.map((room) => {
        const names = (room.players || []).map(escapeHtml).join(', ');
        let extra = '';
        if (room.status === 'playing' || room.status === 'reviewing') {
            extra = ` &middot; R${room.round || 0}/${room.max_rounds || 0}`;
            if (room.current_letter) extra += ` &middot; ${escapeHtml(t('letter-word'))} ${escapeHtml(room.current_letter)}`;
        }
        const bot = room.bot_enabled ? ' <span class="room-bot">+ CPU</span>' : '';
        const playersWord = room.player_count === 1 ? t('player-one') : t('player-many');
        return `
            <li class="room-card">
                <div class="room-card-main">
                    <div class="room-card-head">
                        <span class="room-id">${escapeHtml(room.id)}</span>
                        <span class="room-status status-${escapeHtml(room.status)}">${escapeHtml(t('status-' + room.status))}${extra}</span>
                    </div>
                    <div class="room-players"><span class="room-count">${room.player_count} ${escapeHtml(playersWord)}:</span> ${names}${bot}</div>
                </div>
                <button class="btn mini-btn room-join" type="button" data-room="${escapeHtml(room.id)}">${escapeHtml(t('enter'))}</button>
            </li>`;
    }).join('');
}

let lobbyRefreshing = false;
async function refreshLobby() {
    const list = document.getElementById('rooms-list');
    if (!list || lobbyRefreshing) return;
    lobbyRefreshing = true;
    try {
        const base = window.tuttiConfig?.backendUrl || '';
        const res = await fetch(`${base}/rooms`, { cache: 'no-store' });
        if (!res.ok) throw new Error(`status ${res.status}`);
        const data = await res.json();
        renderRooms(data.rooms || []);
    } catch (e) {
        list.innerHTML = `<li class="rooms-empty">${escapeHtml(t('rooms-error'))}</li>`;
    } finally {
        lobbyRefreshing = false;
    }
}

function startLobbyPolling() {
    refreshLobby();
    if (window._lobbyTimer) clearInterval(window._lobbyTimer);
    window._lobbyTimer = setInterval(() => {
        const welcome = document.getElementById('welcome-screen');
        if (welcome && welcome.classList.contains('active')) {
            refreshLobby();
        }
    }, 6000);
}

// --- Tablero de posiciones --------------------------------------------------

async function openDashboard() {
    window.showScreen('dashboard');
    const body = document.getElementById('dashboard-body');
    if (body) body.innerHTML = `<p class="dash-loading">${escapeHtml(t('dash-loading'))}</p>`;
    try {
        const base = window.tuttiConfig?.backendUrl || '';
        const res = await fetch(`${base}/dashboard`, { cache: 'no-store' });
        if (!res.ok) throw new Error(`status ${res.status}`);
        renderDashboard(await res.json());
    } catch (e) {
        if (body) body.innerHTML = `<p class="dash-loading">${escapeHtml(t('dash-error'))}</p>`;
    }
}

function renderDashboard(data) {
    const body = document.getElementById('dashboard-body');
    if (!body) return;

    const top = data.top || [];
    const totals = data.totals || {};

    const totalsHtml = `
        <div class="dash-totals">
            <span><strong>${totals.total_players || 0}</strong> ${escapeHtml(t('totals-players'))}</span>
            <span><strong>${totals.total_games || 0}</strong> ${escapeHtml(t('totals-games'))}</span>
            <span><strong>${totals.active_rooms || 0}</strong> ${escapeHtml(t('totals-rooms'))}</span>
        </div>`;

    if (top.length === 0) {
        body.innerHTML = totalsHtml + `<p class="dash-loading">${escapeHtml(t('dash-empty'))}</p>`;
        return;
    }

    const maxGames = Math.max(...top.map((x) => x.games_played || 0), 1);
    const rows = top.map((p, i) => {
        const activity = Math.round(100 * (p.games_played || 0) / maxGames);
        return `
            <tr class="dash-row rank-${i + 1}">
                <td class="dash-rank">${i + 1}&ordm;</td>
                <td class="dash-name">${escapeHtml(p.name)}</td>
                <td class="dash-points">${p.points}</td>
                <td class="dash-ok">${p.aciertos}</td>
                <td class="dash-err">${p.errores}</td>
                <td class="dash-dup">${p.duplicaciones}</td>
                <td class="dash-acc">${p.accuracy}%</td>
                <td class="dash-act"><span class="act-bar"><span style="width:${activity}%"></span></span><small>${p.games_played}</small></td>
            </tr>`;
    }).join('');

    body.innerHTML = totalsHtml + `
        <div class="dash-table-wrap">
            <table class="dash-table">
                <thead>
                    <tr>
                        <th>${escapeHtml(t('th-rank'))}</th><th>${escapeHtml(t('th-player'))}</th><th>${escapeHtml(t('th-points'))}</th>
                        <th>${escapeHtml(t('th-ok'))}</th>
                        <th>${escapeHtml(t('th-err'))}</th>
                        <th>${escapeHtml(t('th-dup'))}</th>
                        <th>${escapeHtml(t('th-acc'))}</th>
                        <th>${escapeHtml(t('th-act'))}</th>
                    </tr>
                </thead>
                <tbody>${rows}</tbody>
            </table>
        </div>
        <p class="dash-foot">${escapeHtml(t('dash-foot'))}</p>`;
}

// Redibuja el contenido dinámico de inicio cuando se cambia el idioma.
window.onLanguageChange = function () {
    const welcome = document.getElementById('welcome-screen');
    if (welcome && welcome.classList.contains('active')) refreshLobby();
    const dash = document.getElementById('dashboard-screen');
    if (dash && dash.classList.contains('active')) openDashboard();
};

document.addEventListener('DOMContentLoaded', () => {
    const joinForm = document.getElementById('join-form');
    const answersForm = document.getElementById('answers-form');
    const readyCheckbox = document.getElementById('ready-checkbox');
    const validateBtn = document.getElementById('validate-btn');
    const nextRoundBtn = document.getElementById('next-round-btn');
    const endGameBtn = document.getElementById('end-game-btn');
    const backToHomeBtn = document.getElementById('back-to-home-btn');
    const copyRoomIdBtn = document.getElementById('copy-room-id');

    const spinBtn = document.getElementById('spin-btn');
    const deckOptions = document.getElementById('deck-options');
    const twistsCheckbox = document.getElementById('twists-checkbox');
    const allAnswers = document.getElementById('all-answers-container');

    if (joinForm) joinForm.addEventListener('submit', handleJoinGame);
    if (answersForm) answersForm.addEventListener('submit', handleAnswersSubmit);
    if (spinBtn) spinBtn.addEventListener('click', handleSpinClick);
    if (deckOptions) deckOptions.addEventListener('click', handleDeckClick);
    if (twistsCheckbox) twistsCheckbox.addEventListener('change', handleTwistsToggle);
    if (allAnswers) allAnswers.addEventListener('click', handleChallengeAction);
    if (readyCheckbox) readyCheckbox.addEventListener('change', handleReadyChange);
    if (validateBtn) validateBtn.addEventListener('click', handleValidateContinue);
    if (nextRoundBtn) nextRoundBtn.addEventListener('click', handleValidateContinue);
    if (endGameBtn) endGameBtn.addEventListener('click', handleEndGame);
    if (backToHomeBtn) backToHomeBtn.addEventListener('click', handleBackToHome);
    if (copyRoomIdBtn) copyRoomIdBtn.addEventListener('click', handleCopyRoomId);

    const refreshRoomsBtn = document.getElementById('refresh-rooms');
    const roomsList = document.getElementById('rooms-list');
    const openDashboardBtn = document.getElementById('open-dashboard');
    const dashboardBackBtn = document.getElementById('dashboard-back');
    const dashboardRefreshBtn = document.getElementById('dashboard-refresh');
    if (openDashboardBtn) openDashboardBtn.addEventListener('click', openDashboard);
    if (dashboardRefreshBtn) dashboardRefreshBtn.addEventListener('click', openDashboard);
    if (dashboardBackBtn) dashboardBackBtn.addEventListener('click', () => window.showScreen('welcome'));
    if (refreshRoomsBtn) refreshRoomsBtn.addEventListener('click', refreshLobby);
    if (roomsList) {
        roomsList.addEventListener('click', (event) => {
            const joinBtn = event.target.closest('.room-join');
            if (joinBtn && joinBtn.dataset.room) {
                joinRoomById(joinBtn.dataset.room);
            }
        });
    }

    syncBackendLinks();
    renderBackendStatus();
    window.showScreen('welcome');
    startLobbyPolling();
});
