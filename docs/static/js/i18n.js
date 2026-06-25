/**
 * Sistema de internacionalización para Tutti Frutti
 */

// Traducciones disponibles
const translations = {
    // Español (idioma predeterminado)
    es: {
        "welcome": "¡Bienvenido al Tutti Frutti!",
        "your-name": "Tu nombre:",
        "room-id": "ID de la sala:",
        "create-or-join": "Crea una nueva o únete a una existente",
        "join-room": "Unirse a la Sala",
        "login": "Iniciar Sesión",
        "register": "Registrarse",
        "waiting-room": "Sala de Espera",
        "room-id-label": "ID de la Sala:",
        "copy": "Copiar",
        "ready-to-play": "Estoy listo para jugar",
        "category": "Categoría",
        "answer": "Respuesta",
        "stop-button": "¡STOP!",
        "validate-continue": "Validar y Continuar",
        "scores": "Puntuaciones",
        "player": "Jugador",
        "points": "Puntos",
        "next-round": "Siguiente Ronda",
        "end-game": "Finalizar Juego",
        "review-title": "Revisión de Respuestas",
        "letter-label": "Letra:",
        "deck-title": "Mazo de categorías",
        "deck-hint": "El admin elige qué categorías se juegan.",
        "twists-toggle": "Rondas con giro (sorpresa por ronda)",
        "spin-title": "Sorteo de la letra",
        "spin-preparing": "Preparando la rueda...",
        "spin-auto": "La rueda gira sola: letra completamente aleatoria.",
        "spin-your-turn": "Te toca tirar la rueda.",
        "spin-thrower": "Tira la rueda: {name}.",
        "spin-auto-running": "Sorteo automático en curso.",
        "spin-wait-thrower": "Esperando al tirador.",
        "spin-button": "Tirar la rueda",
        "spin-revealed": "Salió la letra.",
        "fair-summary": "Sorteo verificable (a prueba de trampa)",
        "fair-note": "El servidor fija un hash antes de que se gire. El tirador aporta su giro sin conocer la semilla. Nadie puede forzar la letra.",
        "fair-commit-label": "Compromiso (hash):",
        "fair-server-label": "Semilla del servidor:",
        "fair-server-hidden": "oculta hasta el revelado",
        "fair-client-label": "Aporte del tirador:",
        "fair-result-label": "Resultado:",
        "fair-ok": "Verificado: el hash coincide y la letra se deriva sin trampa.",
        "fair-bad": "Atención: la verificación no coincide.",
        "fair-novalid": "No se pudo verificar en este navegador.",
        "twist-tag": "Ronda con giro",
        "impugnar-hint": "Si una respuesta te parece inválida, tocala para impugnarla. La sala vota y la mayoría decide.",
        "impugnar": "Impugnar",
        "approve": "Aprobar",
        "challenge-by": "Impugnada por {name}",
        "vote-valid": "Vale ({n})",
        "vote-invalid": "No vale ({n})",
        "you": "Vos",
        "empty": "vacío",
        "deck-clasico": "Clásico",
        "deck-clasico-desc": "El de toda la vida.",
        "deck-express": "Exprés",
        "deck-express-desc": "Pocas categorías, partidas rápidas.",
        "deck-mundo": "Vuelta al mundo",
        "deck-mundo-desc": "Geografía y cultura general.",
        "deck-cine": "Cine y series",
        "deck-cine-desc": "Pantalla grande y maratón.",
        "deck-escuela": "Escuela",
        "deck-escuela-desc": "Para jugar en el aula.",
        "twist-normal": "Ronda normal",
        "twist-normal-desc": "Sin modificadores. A jugar.",
        "twist-relampago": "Relámpago",
        "twist-relampago-desc": "Tiempo reducido: pensá rápido.",
        "twist-precision": "Precisión",
        "twist-precision-desc": "Las respuestas repetidas no suman puntos.",
        "twist-doble_o_nada": "Doble o nada",
        "twist-doble_o_nada-desc": "Completá todo y sumás un bonus; si dejás un casillero vacío o inválido, la ronda vale cero.",
        "rooms-title": "Salas activas",
        "refresh": "Actualizar",
        "back": "Volver",
        "enter": "Entrar",
        "enter-name-first": "Primero escribí tu nombre para entrar a la sala.",
        "rooms-hint": "Tocá una sala para entrar (poné tu nombre primero). Si no hay ninguna, dejá el ID vacío y creá una nueva.",
        "rooms-empty": "No hay salas activas todavía. ¡Creá la primera dejando el ID vacío!",
        "rooms-error": "No se pudo cargar la lista (el servidor puede estar despertando). Tocá “Actualizar”.",
        "status-waiting": "esperando",
        "status-playing": "jugando",
        "status-reviewing": "revisando",
        "status-finished": "terminada",
        "letter-word": "letra",
        "player-one": "jugador",
        "player-many": "jugadores",
        "dashboard-title": "Tabla de posiciones",
        "dash-loading": "Cargando tablero…",
        "dash-error": "No se pudo cargar el tablero (el servidor puede estar despertando). Probá de nuevo en unos segundos.",
        "dash-empty": "Todavía no hay puntajes. ¡Jueguen una partida para estrenar el tablero!",
        "th-rank": "Puesto",
        "th-player": "Jugador",
        "th-points": "Puntos",
        "th-ok": "Aciertos",
        "th-err": "Errores",
        "th-dup": "Duplicadas",
        "th-acc": "Precisión",
        "th-act": "Actividad",
        "totals-players": "jugadores",
        "totals-games": "partidas",
        "totals-rooms": "salas activas",
        "dash-foot": "Ranking por puntos. Aciertos: respuestas válidas. Errores: vacías o inválidas. Duplicadas: repetidas con otro jugador. Precisión: porcentaje de aciertos. Actividad: partidas jugadas."
    },

    // Inglés
    en: {
        "welcome": "Welcome to Tutti Frutti!",
        "your-name": "Your name:",
        "room-id": "Room ID:",
        "create-or-join": "Create a new one or join existing",
        "join-room": "Join Room",
        "login": "Login",
        "register": "Register",
        "waiting-room": "Waiting Room",
        "room-id-label": "Room ID:",
        "copy": "Copy",
        "ready-to-play": "I'm ready to play",
        "category": "Category",
        "answer": "Answer",
        "stop-button": "STOP!",
        "validate-continue": "Validate and Continue",
        "scores": "Scores",
        "player": "Player",
        "points": "Points",
        "next-round": "Next Round",
        "end-game": "End Game",
        "review-title": "Answer Review",
        "letter-label": "Letter:",
        "deck-title": "Category deck",
        "deck-hint": "The host picks which categories are played.",
        "twists-toggle": "Twist rounds (per-round surprise)",
        "spin-title": "Letter draw",
        "spin-preparing": "Getting the wheel ready...",
        "spin-auto": "The wheel spins on its own: fully random letter.",
        "spin-your-turn": "It's your turn to spin the wheel.",
        "spin-thrower": "{name} spins the wheel.",
        "spin-auto-running": "Automatic draw in progress.",
        "spin-wait-thrower": "Waiting for the spinner.",
        "spin-button": "Spin the wheel",
        "spin-revealed": "The letter is out.",
        "fair-summary": "Verifiable draw (cheat-proof)",
        "fair-note": "The server locks a hash before the spin. The spinner adds their spin without knowing the seed. Nobody can force the letter.",
        "fair-commit-label": "Commitment (hash):",
        "fair-server-label": "Server seed:",
        "fair-server-hidden": "hidden until reveal",
        "fair-client-label": "Spinner contribution:",
        "fair-result-label": "Result:",
        "fair-ok": "Verified: the hash matches and the letter derives with no cheating.",
        "fair-bad": "Warning: verification does not match.",
        "fair-novalid": "Could not verify in this browser.",
        "twist-tag": "Twist round",
        "impugnar-hint": "If an answer looks invalid, tap it to challenge it. The room votes and the majority decides.",
        "impugnar": "Challenge",
        "approve": "Approve",
        "challenge-by": "Challenged by {name}",
        "vote-valid": "Counts ({n})",
        "vote-invalid": "Doesn't count ({n})",
        "you": "You",
        "empty": "empty",
        "deck-clasico": "Classic",
        "deck-clasico-desc": "The all-time classic.",
        "deck-express": "Express",
        "deck-express-desc": "Few categories, fast rounds.",
        "deck-mundo": "Around the world",
        "deck-mundo-desc": "Geography and general knowledge.",
        "deck-cine": "Movies & series",
        "deck-cine-desc": "Big screen and binge-watching.",
        "deck-escuela": "School",
        "deck-escuela-desc": "To play in the classroom.",
        "twist-normal": "Normal round",
        "twist-normal-desc": "No modifiers. Let's play.",
        "twist-relampago": "Lightning",
        "twist-relampago-desc": "Less time: think fast.",
        "twist-precision": "Precision",
        "twist-precision-desc": "Repeated answers score nothing.",
        "twist-doble_o_nada": "Double or nothing",
        "twist-doble_o_nada-desc": "Fill everything for a bonus; leave a blank or invalid cell and the round scores zero.",
        "rooms-title": "Active rooms",
        "refresh": "Refresh",
        "back": "Back",
        "enter": "Join",
        "enter-name-first": "Enter your name first to join the room.",
        "rooms-hint": "Tap a room to join (enter your name first). If there are none, leave the ID empty and create a new one.",
        "rooms-empty": "No active rooms yet. Create the first one by leaving the ID empty!",
        "rooms-error": "Couldn't load the list (the server may be waking up). Tap “Refresh”.",
        "status-waiting": "waiting",
        "status-playing": "playing",
        "status-reviewing": "reviewing",
        "status-finished": "finished",
        "letter-word": "letter",
        "player-one": "player",
        "player-many": "players",
        "dashboard-title": "Leaderboard",
        "dash-loading": "Loading leaderboard…",
        "dash-error": "Couldn't load the leaderboard (the server may be waking up). Try again in a few seconds.",
        "dash-empty": "No scores yet. Play a game to kick off the leaderboard!",
        "th-rank": "Rank",
        "th-player": "Player",
        "th-points": "Points",
        "th-ok": "Correct",
        "th-err": "Errors",
        "th-dup": "Duplicates",
        "th-acc": "Accuracy",
        "th-act": "Activity",
        "totals-players": "players",
        "totals-games": "games",
        "totals-rooms": "active rooms",
        "dash-foot": "Ranked by points. Correct: valid answers. Errors: empty or invalid. Duplicates: repeated with another player. Accuracy: percentage of correct answers. Activity: games played."
    },

    // Italiano
    it: {
        "welcome": "Benvenuto a Tutti Frutti!",
        "your-name": "Il tuo nome:",
        "room-id": "ID della stanza:",
        "create-or-join": "Creane una nuova o unisciti a una esistente",
        "join-room": "Entra nella stanza",
        "login": "Accedi",
        "register": "Registrati",
        "waiting-room": "Sala d'attesa",
        "room-id-label": "ID della stanza:",
        "copy": "Copia",
        "ready-to-play": "Sono pronto a giocare",
        "category": "Categoria",
        "answer": "Risposta",
        "stop-button": "STOP!",
        "validate-continue": "Convalida e continua",
        "scores": "Punteggi",
        "player": "Giocatore",
        "points": "Punti",
        "next-round": "Round successivo",
        "end-game": "Termina partita",
        "review-title": "Revisione delle risposte",
        "letter-label": "Lettera:",
        "deck-title": "Mazzo di categorie",
        "deck-hint": "L'amministratore sceglie quali categorie si giocano.",
        "twists-toggle": "Round con variante (sorpresa a ogni round)",
        "spin-title": "Estrazione della lettera",
        "spin-preparing": "Preparazione della ruota...",
        "spin-auto": "La ruota gira da sola: lettera completamente casuale.",
        "spin-your-turn": "Tocca a te girare la ruota.",
        "spin-thrower": "Gira la ruota: {name}.",
        "spin-auto-running": "Estrazione automatica in corso.",
        "spin-wait-thrower": "In attesa di chi gira.",
        "spin-button": "Gira la ruota",
        "spin-revealed": "È uscita la lettera.",
        "fair-summary": "Estrazione verificabile (a prova di imbroglio)",
        "fair-note": "Il server fissa un hash prima del giro. Chi gira aggiunge il suo contributo senza conoscere il seme. Nessuno può forzare la lettera.",
        "fair-commit-label": "Impegno (hash):",
        "fair-server-label": "Seme del server:",
        "fair-server-hidden": "nascosto fino alla rivelazione",
        "fair-client-label": "Contributo di chi gira:",
        "fair-result-label": "Risultato:",
        "fair-ok": "Verificato: l'hash coincide e la lettera deriva senza imbrogli.",
        "fair-bad": "Attenzione: la verifica non coincide.",
        "fair-novalid": "Impossibile verificare in questo browser.",
        "twist-tag": "Round con variante",
        "impugnar-hint": "Se una risposta ti sembra non valida, toccala per contestarla. La stanza vota e decide la maggioranza.",
        "impugnar": "Contesta",
        "approve": "Approva",
        "challenge-by": "Contestata da {name}",
        "vote-valid": "Vale ({n})",
        "vote-invalid": "Non vale ({n})",
        "you": "Tu",
        "empty": "vuoto",
        "deck-clasico": "Classico",
        "deck-clasico-desc": "Quello di sempre.",
        "deck-express": "Express",
        "deck-express-desc": "Poche categorie, partite veloci.",
        "deck-mundo": "Giro del mondo",
        "deck-mundo-desc": "Geografia e cultura generale.",
        "deck-cine": "Cinema e serie",
        "deck-cine-desc": "Grande schermo e maratone.",
        "deck-escuela": "Scuola",
        "deck-escuela-desc": "Per giocare in classe.",
        "twist-normal": "Round normale",
        "twist-normal-desc": "Nessun modificatore. Si gioca.",
        "twist-relampago": "Lampo",
        "twist-relampago-desc": "Meno tempo: pensa in fretta.",
        "twist-precision": "Precisione",
        "twist-precision-desc": "Le risposte ripetute non danno punti.",
        "twist-doble_o_nada": "Doppio o niente",
        "twist-doble_o_nada-desc": "Completa tutto per un bonus; se lasci una casella vuota o non valida, il round vale zero.",
        "rooms-title": "Stanze attive",
        "refresh": "Aggiorna",
        "back": "Indietro",
        "enter": "Entra",
        "enter-name-first": "Inserisci prima il tuo nome per entrare nella stanza.",
        "rooms-hint": "Tocca una stanza per entrare (inserisci prima il tuo nome). Se non ce ne sono, lascia vuoto l'ID e creane una nuova.",
        "rooms-empty": "Ancora nessuna stanza attiva. Crea la prima lasciando vuoto l'ID!",
        "rooms-error": "Impossibile caricare l'elenco (il server potrebbe essersi svegliando). Tocca “Aggiorna”.",
        "status-waiting": "in attesa",
        "status-playing": "in gioco",
        "status-reviewing": "revisione",
        "status-finished": "terminata",
        "letter-word": "lettera",
        "player-one": "giocatore",
        "player-many": "giocatori",
        "dashboard-title": "Classifica",
        "dash-loading": "Caricamento classifica…",
        "dash-error": "Impossibile caricare la classifica (il server potrebbe essersi svegliando). Riprova tra qualche secondo.",
        "dash-empty": "Ancora nessun punteggio. Giocate una partita per inaugurare la classifica!",
        "th-rank": "Posizione",
        "th-player": "Giocatore",
        "th-points": "Punti",
        "th-ok": "Esatte",
        "th-err": "Errori",
        "th-dup": "Duplicate",
        "th-acc": "Precisione",
        "th-act": "Attività",
        "totals-players": "giocatori",
        "totals-games": "partite",
        "totals-rooms": "stanze attive",
        "dash-foot": "Classifica per punti. Esatte: risposte valide. Errori: vuote o non valide. Duplicate: ripetute con un altro giocatore. Precisione: percentuale di risposte esatte. Attività: partite giocate."
    },

    // Portugués
    pt: {
        "welcome": "Bem-vindo ao Tutti Frutti!",
        "your-name": "Seu nome:",
        "room-id": "ID da sala:",
        "create-or-join": "Crie uma nova ou entre em uma existente",
        "join-room": "Entrar na sala",
        "login": "Entrar",
        "register": "Cadastrar",
        "waiting-room": "Sala de espera",
        "room-id-label": "ID da sala:",
        "copy": "Copiar",
        "ready-to-play": "Estou pronto para jogar",
        "category": "Categoria",
        "answer": "Resposta",
        "stop-button": "STOP!",
        "validate-continue": "Validar e continuar",
        "scores": "Pontuações",
        "player": "Jogador",
        "points": "Pontos",
        "next-round": "Próxima rodada",
        "end-game": "Encerrar jogo",
        "review-title": "Revisão das respostas",
        "letter-label": "Letra:",
        "deck-title": "Baralho de categorias",
        "deck-hint": "O administrador escolhe quais categorias se jogam.",
        "twists-toggle": "Rodadas com twist (surpresa por rodada)",
        "spin-title": "Sorteio da letra",
        "spin-preparing": "Preparando a roleta...",
        "spin-auto": "A roleta gira sozinha: letra totalmente aleatória.",
        "spin-your-turn": "É a sua vez de girar a roleta.",
        "spin-thrower": "Gira a roleta: {name}.",
        "spin-auto-running": "Sorteio automático em andamento.",
        "spin-wait-thrower": "Aguardando quem gira.",
        "spin-button": "Girar a roleta",
        "spin-revealed": "Saiu a letra.",
        "fair-summary": "Sorteio verificável (à prova de trapaça)",
        "fair-note": "O servidor fixa um hash antes do giro. Quem gira adiciona seu giro sem conhecer a semente. Ninguém pode forçar a letra.",
        "fair-commit-label": "Compromisso (hash):",
        "fair-server-label": "Semente do servidor:",
        "fair-server-hidden": "oculta até a revelação",
        "fair-client-label": "Contribuição de quem gira:",
        "fair-result-label": "Resultado:",
        "fair-ok": "Verificado: o hash coincide e a letra é derivada sem trapaça.",
        "fair-bad": "Atenção: a verificação não coincide.",
        "fair-novalid": "Não foi possível verificar neste navegador.",
        "twist-tag": "Rodada com twist",
        "impugnar-hint": "Se uma resposta parecer inválida, toque para contestá-la. A sala vota e a maioria decide.",
        "impugnar": "Contestar",
        "approve": "Aprovar",
        "challenge-by": "Contestada por {name}",
        "vote-valid": "Vale ({n})",
        "vote-invalid": "Não vale ({n})",
        "you": "Você",
        "empty": "vazio",
        "deck-clasico": "Clássico",
        "deck-clasico-desc": "O de sempre.",
        "deck-express": "Express",
        "deck-express-desc": "Poucas categorias, partidas rápidas.",
        "deck-mundo": "Volta ao mundo",
        "deck-mundo-desc": "Geografia e cultura geral.",
        "deck-cine": "Cinema e séries",
        "deck-cine-desc": "Telona e maratona.",
        "deck-escuela": "Escola",
        "deck-escuela-desc": "Para jogar na sala de aula.",
        "twist-normal": "Rodada normal",
        "twist-normal-desc": "Sem modificadores. Bora jogar.",
        "twist-relampago": "Relâmpago",
        "twist-relampago-desc": "Menos tempo: pense rápido.",
        "twist-precision": "Precisão",
        "twist-precision-desc": "Respostas repetidas não somam pontos.",
        "twist-doble_o_nada": "Tudo ou nada",
        "twist-doble_o_nada-desc": "Complete tudo e ganhe um bônus; se deixar uma casa vazia ou inválida, a rodada vale zero.",
        "rooms-title": "Salas ativas",
        "refresh": "Atualizar",
        "back": "Voltar",
        "enter": "Entrar",
        "enter-name-first": "Coloque seu nome primeiro para entrar na sala.",
        "rooms-hint": "Toque numa sala para entrar (coloque seu nome primeiro). Se não houver nenhuma, deixe o ID vazio e crie uma nova.",
        "rooms-empty": "Ainda não há salas ativas. Crie a primeira deixando o ID vazio!",
        "rooms-error": "Não foi possível carregar a lista (o servidor pode estar acordando). Toque em “Atualizar”.",
        "status-waiting": "esperando",
        "status-playing": "jogando",
        "status-reviewing": "revisando",
        "status-finished": "encerrada",
        "letter-word": "letra",
        "player-one": "jogador",
        "player-many": "jogadores",
        "dashboard-title": "Classificação",
        "dash-loading": "Carregando classificação…",
        "dash-error": "Não foi possível carregar a classificação (o servidor pode estar acordando). Tente de novo em alguns segundos.",
        "dash-empty": "Ainda não há pontuações. Joguem uma partida para estrear a classificação!",
        "th-rank": "Posição",
        "th-player": "Jogador",
        "th-points": "Pontos",
        "th-ok": "Acertos",
        "th-err": "Erros",
        "th-dup": "Duplicadas",
        "th-acc": "Precisão",
        "th-act": "Atividade",
        "totals-players": "jogadores",
        "totals-games": "partidas",
        "totals-rooms": "salas ativas",
        "dash-foot": "Classificação por pontos. Acertos: respostas válidas. Erros: vazias ou inválidas. Duplicadas: repetidas com outro jogador. Precisão: porcentagem de acertos. Atividade: partidas jogadas."
    }
};

// Idioma actual
let currentLang = 'es';

// Función para cambiar el idioma
function setLanguage(lang) {
    if (translations[lang]) {
        currentLang = lang;
        localStorage.setItem('tuttiFrutiLang', lang);
        document.documentElement.lang = lang;
        updateUILanguage();
        return true;
    }
    return false;
}

// Función para traducir texto
function translate(key) {
    return translations[currentLang][key] || translations['es'][key] || key;
}

// Actualizar idioma en la interfaz
function updateUILanguage() {
    // Actualizar elementos con atributo data-i18n
    document.querySelectorAll('[data-i18n]').forEach(element => {
        const key = element.getAttribute('data-i18n');
        if (key) {
            element.textContent = translate(key);
        }
    });

    // Actualizar placeholders con atributo data-i18n-placeholder
    document.querySelectorAll('[data-i18n-placeholder]').forEach(element => {
        const key = element.getAttribute('data-i18n-placeholder');
        if (key) {
            element.placeholder = translate(key);
        }
    });

    // Marcar el botón de idioma activo.
    document.querySelectorAll('.lang-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.lang === currentLang);
    });

    // Volver a dibujar el contenido dinámico del juego (rueda, revisión, etc.).
    if (typeof window.refreshGameUI === 'function') {
        window.refreshGameUI();
    }

    // Volver a dibujar el contenido dinámico de inicio (lobby de salas y tablero).
    if (typeof window.onLanguageChange === 'function') {
        window.onLanguageChange();
    }
}

// Inicializar al cargar el documento
document.addEventListener('DOMContentLoaded', () => {
    // Idioma guardado; por defecto español hasta que se elija otro.
    const savedLang = localStorage.getItem('tuttiFrutiLang');

    if (savedLang && translations[savedLang]) {
        setLanguage(savedLang);
    } else {
        setLanguage('es');
    }

    // Agregar eventos a los botones de idioma
    document.querySelectorAll('.lang-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const lang = btn.dataset.lang;
            setLanguage(lang);
        });
    });
});

// Exportar funciones para usar en otros scripts
window.i18n = {
    translate,
    setLanguage,
    getCurrentLang: () => currentLang
};
