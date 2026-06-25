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
        "twist-doble_o_nada-desc": "Completá todo y sumás un bonus; si dejás un casillero vacío o inválido, la ronda vale cero."
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
        "twist-doble_o_nada-desc": "Fill everything for a bonus; leave a blank or invalid cell and the round scores zero."
    }
};

// Idioma actual
let currentLang = 'es';

// Función para cambiar el idioma
function setLanguage(lang) {
    if (translations[lang]) {
        currentLang = lang;
        localStorage.setItem('tuttiFrutiLang', lang);
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
}

// Inicializar al cargar el documento
document.addEventListener('DOMContentLoaded', () => {
    // Cargar idioma guardado o usar el predeterminado
    const savedLang = localStorage.getItem('tuttiFrutiLang') || navigator.language.substring(0, 2);
    
    // Comprobar si el idioma está disponible, de lo contrario usar español
    if (translations[savedLang]) {
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
