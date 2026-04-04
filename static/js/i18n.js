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
        "end-game": "Finalizar Juego"
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
        "end-game": "End Game"
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
