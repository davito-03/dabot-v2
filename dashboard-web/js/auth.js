/**
 * Sistema de autenticación con Discord OAuth2
 * Para davito.es/dabot
 */

class DiscordAuth {
    constructor() {
        // Configuración de Discord OAuth2
        this.clientId = '1413169797759238244'; // Tu Discord Application ID
    this.redirectUri = 'https://davito.es/dabot/auth.html';
    this.scope = 'identify guilds';
        
        // URLs
        this.discordAuthUrl = 'https://discord.com/api/oauth2/authorize';
        this.discordTokenUrl = 'https://discord.com/api/oauth2/token';
        this.discordApiUrl = 'https://discord.com/api';
        
        // Estado de autenticación
        this.isAuthenticated = false;
        this.user = null;
        this.accessToken = null;
        
        // Inicializar
        this.init();
    }

    /**
     * Inicializar sistema de autenticación
     */
    init() {
        // Verificar si hay token guardado
        const savedToken = localStorage.getItem('discord_access_token');
        const savedUser = localStorage.getItem('discord_user');
        
        if (savedToken && savedUser) {
            this.accessToken = savedToken;
            this.user = JSON.parse(savedUser);
            this.isAuthenticated = true;
        }
        
        // Manejar callback de Discord
        this.handleAuthCallback();
        
        // Configurar eventos
        this.setupEventListeners();
    }

    /**
     * Configurar event listeners
     */
    setupEventListeners() {
        // Botón de login
        const loginBtn = document.getElementById('login-btn');
        if (loginBtn) {
            loginBtn.addEventListener('click', () => this.login());
        }

        // Botón de logout
        const logoutBtn = document.getElementById('logout-btn');
        if (logoutBtn) {
            logoutBtn.addEventListener('click', () => this.logout());
        }

        // Botón "Comenzar"
        const getStartedBtn = document.getElementById('get-started');
        if (getStartedBtn) {
            getStartedBtn.addEventListener('click', () => {
                if (this.isAuthenticated) {
                    window.location.href = '/dabot/dashboard.html';
                } else {
                    this.login();
                }
            });
        }
    }

    /**
     * Generar URL de autenticación de Discord
     */
    getAuthUrl() {
        const params = new URLSearchParams({
            client_id: this.clientId,
            redirect_uri: this.redirectUri,
            response_type: 'token', // implicit grant for frontend-only
            scope: this.scope,
            state: this.generateState(),
            prompt: 'consent'
        });
        
        return `${this.discordAuthUrl}?${params.toString()}`;
    }

    /**
     * Generar estado aleatorio para seguridad
     */
    generateState() {
        const state = Math.random().toString(36).substring(2, 15);
        localStorage.setItem('discord_auth_state', state);
        return state;
    }

    /**
     * Verificar estado de autenticación
     */
    verifyState(state) {
        const savedState = localStorage.getItem('discord_auth_state');
        localStorage.removeItem('discord_auth_state');
        return state === savedState;
    }

    /**
     * Iniciar proceso de login
     */
    login() {
        console.log('Iniciando login con Discord...');
        window.location.href = this.getAuthUrl();
    }

    /**
     * Manejar callback de Discord OAuth2
     */
    async handleAuthCallback() {
    // Support both implicit grant (#access_token) and code flow (?code)
    const urlParams = new URLSearchParams(window.location.search);
    const hashParams = new URLSearchParams(window.location.hash.replace(/^#/, ''));
    const code = urlParams.get('code');
    const state = urlParams.get('state') || hashParams.get('state');
    const error = urlParams.get('error') || hashParams.get('error');
    const accessTokenFromHash = hashParams.get('access_token');

        if (error) {
            console.error('Error de autenticación:', error);
            this.showError('Error en la autenticación con Discord');
            return;
        }

        // Implicit grant: access_token is in the URL hash
        if (accessTokenFromHash && state) {
            if (!this.verifyState(state)) {
                console.error('Estado de autenticación inválido');
                this.showError('Error de seguridad en la autenticación');
                return;
            }

            try {
                this.accessToken = accessTokenFromHash;
                localStorage.setItem('discord_access_token', this.accessToken);
                await this.fetchUserInfo();
                await this.authenticateWithBot();

                // Limpiar el hash y redirigir al dashboard
                history.replaceState(null, '', window.location.pathname);
                window.location.href = '/dabot/dashboard.html';
            } catch (e) {
                console.error('Error en autenticación (implicit):', e);
                this.showError('Error al completar la autenticación');
            }
            return;
        }

        // Authorization code flow (not used now but kept for compatibility)
        if (code && state) {
            if (!this.verifyState(state)) {
                console.error('Estado de autenticación inválido');
                this.showError('Error de seguridad en la autenticación');
                return;
            }

            try {
                await this.exchangeCodeForToken(code);
                await this.fetchUserInfo();
                await this.authenticateWithBot();
                
                // Redirigir al dashboard
                window.location.href = '/dabot/dashboard.html';
                
            } catch (error) {
                console.error('Error en el proceso de autenticación:', error);
                this.showError('Error al completar la autenticación');
            }
        }
    }

    /**
     * Intercambiar código por token de acceso
     */
    async exchangeCodeForToken(code) {
        const data = {
            client_id: this.clientId,
            client_secret: 'TU_CLIENT_SECRET', // NOT USED on frontend; keep for backend reference
            grant_type: 'authorization_code',
            code: code,
            redirect_uri: this.redirectUri
        };

        // Nota: En producción, esto debe hacerse en el backend por seguridad
        const response = await fetch(this.discordTokenUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: new URLSearchParams(data)
        });

        if (!response.ok) {
            throw new Error('Error al obtener token de acceso');
        }

        const tokenData = await response.json();
        this.accessToken = tokenData.access_token;
        
        // Guardar token (en producción, considerar expiración)
        localStorage.setItem('discord_access_token', this.accessToken);
    }

    /**
     * Obtener información del usuario de Discord
     */
    async fetchUserInfo() {
        const response = await fetch(`${this.discordApiUrl}/users/@me`, {
            headers: {
                'Authorization': `Bearer ${this.accessToken}`
            }
        });

        if (!response.ok) {
            throw new Error('Error al obtener información del usuario');
        }

        this.user = await response.json();
        this.isAuthenticated = true;
        
        // Guardar información del usuario
        localStorage.setItem('discord_user', JSON.stringify(this.user));
        
        console.log('Usuario autenticado:', this.user);
    }

    /**
     * Autenticar con el bot y obtener JWT
     */
    async authenticateWithBot() {
        try {
            const response = await window.daBotAPI.authenticate(this.accessToken);
            console.log('Autenticado con el bot:', response);
            
            // Actualizar UI
            this.updateUI();
            
        } catch (error) {
            console.error('Error autenticando con el bot:', error);
            throw new Error('Error conectando con el bot');
        }
    }

    /**
     * Cerrar sesión
     */
    logout() {
        // Limpiar datos locales
        localStorage.removeItem('discord_access_token');
        localStorage.removeItem('discord_user');
        localStorage.removeItem('dabot_auth_token');
        
        // Reiniciar estado
        this.isAuthenticated = false;
        this.user = null;
        this.accessToken = null;
        
        // Cerrar sesión en API del bot
        if (window.daBotAPI) {
            window.daBotAPI.logout();
        }
        
        // Redirigir a inicio
        window.location.href = '/dabot/';
    }

    /**
     * Actualizar interfaz de usuario
     */
    updateUI() {
        const loginBtn = document.getElementById('login-btn');
        const userInfo = document.getElementById('user-info');
        const getStartedBtn = document.getElementById('get-started');

        if (this.isAuthenticated && this.user) {
            // Ocultar botón de login
            if (loginBtn) {
                loginBtn.style.display = 'none';
            }

            // Mostrar información del usuario
            if (userInfo) {
                userInfo.innerHTML = `
                    <div class="user-info">
                        <img src="https://cdn.discordapp.com/avatars/${this.user.id}/${this.user.avatar}.png" 
                             alt="${this.user.username}" class="user-avatar">
                        <div class="user-details">
                            <h4>${this.user.username}#${this.user.discriminator}</h4>
                            <p>Conectado</p>
                        </div>
                        <button id="logout-btn" class="btn btn-secondary">Salir</button>
                    </div>
                `;
                
                // Reconfigurar event listener para logout
                const logoutBtn = document.getElementById('logout-btn');
                if (logoutBtn) {
                    logoutBtn.addEventListener('click', () => this.logout());
                }
            }

            // Cambiar texto del botón "Comenzar"
            if (getStartedBtn) {
                getStartedBtn.textContent = 'Ir al Dashboard';
            }

        } else {
            // Mostrar botón de login
            if (loginBtn) {
                loginBtn.style.display = 'inline-flex';
                loginBtn.textContent = 'Iniciar Sesión';
            }

            // Ocultar información del usuario
            if (userInfo) {
                userInfo.innerHTML = '';
            }

            // Texto original del botón
            if (getStartedBtn) {
                getStartedBtn.textContent = 'Comenzar';
            }
        }
    }

    /**
     * Mostrar error al usuario
     */
    showError(message) {
        // Crear o mostrar elemento de error
        let errorElement = document.getElementById('auth-error');
        
        if (!errorElement) {
            errorElement = document.createElement('div');
            errorElement.id = 'auth-error';
            errorElement.className = 'alert alert-error';
            errorElement.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                background-color: var(--error-color);
                color: white;
                padding: 1rem 1.5rem;
                border-radius: 8px;
                z-index: 1000;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
            `;
            document.body.appendChild(errorElement);
        }
        
        errorElement.textContent = message;
        errorElement.style.display = 'block';
        
        // Ocultar después de 5 segundos
        setTimeout(() => {
            errorElement.style.display = 'none';
        }, 5000);
    }

    /**
     * Verificar si el usuario está autenticado
     */
    checkAuth() {
        return this.isAuthenticated;
    }

    /**
     * Obtener información del usuario
     */
    getUser() {
        return this.user;
    }

    /**
     * Obtener avatar del usuario
     */
    getUserAvatar() {
        if (!this.user || !this.user.avatar) {
            return 'assets/images/default-avatar.png';
        }
        
        return `https://cdn.discordapp.com/avatars/${this.user.id}/${this.user.avatar}.png`;
    }
}

// Inicializar sistema de autenticación cuando se carga la página
document.addEventListener('DOMContentLoaded', () => {
    window.discordAuth = new DiscordAuth();
    
    // Actualizar UI inicial
    setTimeout(() => {
        window.discordAuth.updateUI();
    }, 100);
});

// Exportar para uso global
window.DiscordAuth = DiscordAuth;
