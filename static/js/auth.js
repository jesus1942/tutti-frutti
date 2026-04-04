/**
 * Sistema de autenticación para Tutti Frutti
 * Gestiona login, registro y perfil de usuario
 */

// Estado de autenticación
const authState = {
    isLoggedIn: false,
    user: null,
    token: null
};

// Funciones de autenticación simuladas
function login(email, password) {
    // Simulación de autenticación exitosa
    authState.isLoggedIn = true;
    authState.user = {
        username: email.split('@')[0],
        email: email
    };
    authState.token = 'simulated_jwt_token';
    
    // Guardar en localStorage
    localStorage.setItem('tuttiFrutiAuth', JSON.stringify({
        user: authState.user,
        token: authState.token
    }));
    
    showToast('Inicio de sesión exitoso', 'success');
    return true;
}

function register(username, email, password) {
    // Simulación de registro exitoso
    authState.isLoggedIn = true;
    authState.user = {
        username: username,
        email: email
    };
    authState.token = 'simulated_jwt_token';
    
    // Guardar en localStorage
    localStorage.setItem('tuttiFrutiAuth', JSON.stringify({
        user: authState.user,
        token: authState.token
    }));
    
    showToast('Registro exitoso', 'success');
    return true;
}

function logout() {
    authState.isLoggedIn = false;
    authState.user = null;
    authState.token = null;
    
    // Eliminar de localStorage
    localStorage.removeItem('tuttiFrutiAuth');
    
    showToast('Sesión cerrada', 'info');
}

// Función para mostrar notificaciones
function showToast(message, type = 'info', duration = 3000) {
    const toastContainer = document.getElementById('toast-container') || 
                          createToastContainer();
    
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `<p>${message}</p><button class="toast-close">&times;</button>`;
    
    // Manejar cierre manual
    toast.querySelector('.toast-close').addEventListener('click', () => {
        toast.remove();
    });
    
    toastContainer.appendChild(toast);
    
    // Remover automáticamente después de 'duration' ms
    if (duration > 0) {
        setTimeout(() => {
            toast.classList.add('toast-hiding');
            setTimeout(() => toast.remove(), 500);
        }, duration);
    }
}

function createToastContainer() {
    const container = document.createElement('div');
    container.id = 'toast-container';
    document.body.appendChild(container);
    return container;
}

// Cargar estado de autenticación guardado
function loadSavedAuth() {
    const savedAuth = localStorage.getItem('tuttiFrutiAuth');
    if (savedAuth) {
        try {
            const parsed = JSON.parse(savedAuth);
            authState.isLoggedIn = true;
            authState.user = parsed.user;
            authState.token = parsed.token;
        } catch (e) {
            console.error('Error parsing saved auth:', e);
            localStorage.removeItem('tuttiFrutiAuth');
        }
    }
}

// Inicializar cuando se cargue el documento
document.addEventListener('DOMContentLoaded', function() {
    loadSavedAuth();
});

// Exportar funciones para uso global
window.auth = {
    login,
    register,
    logout,
    isLoggedIn: () => authState.isLoggedIn,
    getCurrentUser: () => authState.user,
    getToken: () => authState.token,
    showToast
};
