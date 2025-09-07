/**
 * Sistema de autenticación local simplificado
 * Para uso con el dashboard local del bot
 */

class LocalAuth {
    constructor() {
        this.isAuthenticated = false;
        this.user = null;
        this.guilds = [];
        this.token = null;
    }

    /**
     * Inicializar autenticación
     */
    async init() {
        console.log('Inicializando autenticación local...');
        
        // Verificar si hay token guardado
        const savedToken = localStorage.getItem('dabot_local_token');
        if (savedToken) {
            this.token = savedToken;
            await this.verifyToken();
        }
        
        return this.isAuthenticated;
    }

    /**
     * Verificar si hay autenticación
     */
    checkAuth() {
        return this.isAuthenticated && this.user;
    }

    /**
     * Autenticación automática con el bot
     */
    async authenticateWithBot() {
        try {
            console.log('Autenticando con el bot local...');
            
            const response = await fetch('/api/auth/local', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                throw new Error(`Error ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();
            
            if (data.success) {
                this.isAuthenticated = true;
                this.user = data.user;
                this.guilds = data.guilds;
                this.token = data.token;
                
                // Guardar token
                localStorage.setItem('dabot_local_token', this.token);
                
                console.log('Autenticación exitosa:', this.user);
                this.updateUI();
                
                return true;
            } else {
                throw new Error(data.error || 'Error en autenticación');
            }
            
        } catch (error) {
            console.error('Error en autenticación:', error);
            this.showError('Error al conectar con el bot: ' + error.message);
            return false;
        }
    }

    /**
     * Verificar token guardado
     */
    async verifyToken() {
        try {
            const response = await fetch('/api/auth/info', {
                headers: {
                    'Authorization': `Bearer ${this.token}`
                }
            });

            if (response.ok) {
                const data = await response.json();
                if (data.authenticated) {
                    this.isAuthenticated = true;
                    this.user = {
                        id: data.bot.id,
                        username: data.bot.name,
                        avatar: data.bot.avatar,
                        is_bot: true,
                        local_auth: true
                    };
                    
                    // Obtener guilds
                    await this.loadGuilds();
                    
                    console.log('Token válido, usuario autenticado');
                    this.updateUI();
                    return true;
                }
            }
            
            // Token inválido, limpiar
            this.logout();
            return false;
            
        } catch (error) {
            console.error('Error verificando token:', error);
            this.logout();
            return false;
        }
    }

    /**
     * Cargar lista de guilds
     */
    async loadGuilds() {
        try {
            const response = await fetch('/api/guilds', {
                headers: {
                    'Authorization': `Bearer ${this.token}`
                }
            });

            if (response.ok) {
                this.guilds = await response.json();
            }
        } catch (error) {
            console.error('Error cargando guilds:', error);
        }
    }

    /**
     * Cerrar sesión
     */
    logout() {
        this.isAuthenticated = false;
        this.user = null;
        this.guilds = [];
        this.token = null;
        
        // Limpiar almacenamiento local
        localStorage.removeItem('dabot_local_token');
        
        console.log('Sesión cerrada');
        this.updateUI();
    }

    /**
     * Obtener URL de avatar
     */
    getAvatarUrl() {
        if (!this.user || !this.user.avatar) {
            return '/assets/images/default-avatar.png';
        }
        return this.user.avatar;
    }

    /**
     * Actualizar interfaz de usuario
     */
    updateUI() {
        const authButtons = document.querySelectorAll('.auth-button');
        const loginButton = document.getElementById('loginButton');
        const userInfo = document.getElementById('userInfo');
        const userAvatar = document.getElementById('userAvatar');
        const userName = document.getElementById('userName');
        const dashboardButton = document.getElementById('dashboardButton');

        if (this.isAuthenticated && this.user) {
            // Usuario autenticado
            authButtons.forEach(btn => {
                if (btn.textContent.includes('Iniciar')) {
                    btn.style.display = 'none';
                }
            });

            if (loginButton) {
                loginButton.style.display = 'none';
            }

            if (dashboardButton) {
                dashboardButton.style.display = 'inline-block';
            }

            if (userInfo) {
                userInfo.style.display = 'flex';
            }

            if (userAvatar && this.user.avatar) {
                userAvatar.src = this.user.avatar;
                userAvatar.style.display = 'block';
            }

            if (userName) {
                userName.textContent = this.user.username;
            }

            // Mostrar información del bot
            const botInfo = document.getElementById('botInfo');
            if (botInfo) {
                botInfo.innerHTML = `
                    <div class="bot-status">
                        <span class="status-indicator online"></span>
                        <span>Bot conectado: ${this.user.username}</span>
                        <span class="guild-count">${this.guilds.length} servidores</span>
                    </div>
                `;
                botInfo.style.display = 'block';
            }

        } else {
            // Usuario no autenticado
            authButtons.forEach(btn => {
                if (btn.textContent.includes('Iniciar')) {
                    btn.style.display = 'inline-block';
                }
            });

            if (loginButton) {
                loginButton.style.display = 'inline-block';
            }

            if (dashboardButton) {
                dashboardButton.style.display = 'none';
            }

            if (userInfo) {
                userInfo.style.display = 'none';
            }

            const botInfo = document.getElementById('botInfo');
            if (botInfo) {
                botInfo.innerHTML = `
                    <div class="bot-status">
                        <span class="status-indicator offline"></span>
                        <span>Conectando con el bot...</span>
                    </div>
                `;
            }
        }
    }

    /**
     * Mostrar error
     */
    showError(message) {
        console.error('Auth Error:', message);
        
        // Crear notificación de error
        const errorDiv = document.createElement('div');
        errorDiv.className = 'auth-error';
        errorDiv.innerHTML = `
            <div class="error-content">
                <span class="error-icon">⚠️</span>
                <span class="error-message">${message}</span>
                <button class="error-close" onclick="this.parentElement.parentElement.remove()">×</button>
            </div>
        `;
        
        // Agregar estilos si no existen
        if (!document.getElementById('auth-error-styles')) {
            const styles = document.createElement('style');
            styles.id = 'auth-error-styles';
            styles.textContent = `
                .auth-error {
                    position: fixed;
                    top: 20px;
                    right: 20px;
                    background: #ff4757;
                    color: white;
                    padding: 15px;
                    border-radius: 8px;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.2);
                    z-index: 1000;
                    animation: slideIn 0.3s ease;
                }
                .error-content {
                    display: flex;
                    align-items: center;
                    gap: 10px;
                }
                .error-close {
                    background: none;
                    border: none;
                    color: white;
                    font-size: 18px;
                    cursor: pointer;
                    padding: 0;
                    margin-left: 10px;
                }
                @keyframes slideIn {
                    from { transform: translateX(100%); opacity: 0; }
                    to { transform: translateX(0); opacity: 1; }
                }
                .status-indicator {
                    display: inline-block;
                    width: 8px;
                    height: 8px;
                    border-radius: 50%;
                    margin-right: 8px;
                }
                .status-indicator.online {
                    background: #2ed573;
                }
                .status-indicator.offline {
                    background: #ff4757;
                }
                .bot-status {
                    display: flex;
                    align-items: center;
                    gap: 10px;
                    font-size: 14px;
                    color: #666;
                }
                .guild-count {
                    background: #f1f2f6;
                    padding: 2px 8px;
                    border-radius: 12px;
                    font-size: 12px;
                }
            `;
            document.head.appendChild(styles);
        }
        
        document.body.appendChild(errorDiv);
        
        // Auto-remover después de 5 segundos
        setTimeout(() => {
            if (errorDiv.parentElement) {
                errorDiv.remove();
            }
        }, 5000);
    }
}

// Crear instancia global
window.localAuth = new LocalAuth();

// Auto-inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', async () => {
    console.log('DOM cargado, inicializando autenticación...');
    
    const isAuthenticated = await window.localAuth.init();
    
    if (!isAuthenticated) {
        // Intentar autenticación automática
        await window.localAuth.authenticateWithBot();
    }
});
