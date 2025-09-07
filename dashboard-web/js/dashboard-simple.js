/**
 * Dashboard JavaScript simplificado sin redirecciones
 * Para uso local con autenticación simplificada
 */

class SimpleDashboard {
    constructor() {
        this.isLoaded = false;
        this.apiBase = '/api';
    }

    async init() {
        console.log('Inicializando dashboard simplificado...');
        
        // No verificar autenticación - funciona en modo local
        this.isLoaded = true;
        
        // Cargar datos básicos
        await this.loadBasicData();
        
        // Configurar eventos
        this.setupEventListeners();
        
        console.log('Dashboard simplificado listo');
    }

    async loadBasicData() {
        try {
            // Intentar cargar estado del bot
            const response = await fetch(`${this.apiBase}/status`);
            if (response.ok) {
                const status = await response.json();
                this.updateBotStatus(status);
            }
        } catch (error) {
            console.log('API no disponible, usando datos por defecto');
            this.updateBotStatus({
                status: 'online',
                guilds: ['Servidor Local'],
                ping: Math.floor(Math.random() * 100) + 20
            });
        }
    }

    updateBotStatus(status) {
        // Actualizar indicador de estado
        const statusElement = document.getElementById('bot-status');
        if (statusElement) {
            statusElement.className = 'status-indicator online';
        }

        // Actualizar información en la interfaz
        const statusText = document.querySelector('.bot-status span');
        if (statusText) {
            statusText.textContent = 'Bot Online';
        }
    }

    setupEventListeners() {
        // Botón de actualizar
        const refreshBtn = document.getElementById('refresh-btn');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => {
                this.loadBasicData();
            });
        }

        // Toggle sidebar
        const sidebarToggle = document.getElementById('sidebar-toggle');
        if (sidebarToggle) {
            sidebarToggle.addEventListener('click', () => {
                document.querySelector('.sidebar').classList.toggle('mobile-open');
            });
        }

        // Logout - solo limpia datos locales
        const logoutBtn = document.getElementById('logout-btn');
        if (logoutBtn) {
            logoutBtn.addEventListener('click', (e) => {
                e.preventDefault();
                localStorage.removeItem('dabot_local_token');
                window.location.href = '/index.html';
            });
        }
    }

    // Funciones auxiliares para compatibilidad
    async fetchGuilds() {
        return [{ id: '1', name: 'Servidor Local', icon: null }];
    }

    async fetchBotStats() {
        return {
            guilds: 1,
            users: 100,
            commands: 25,
            uptime: Math.floor(Math.random() * 86400)
        };
    }
}

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM cargado, inicializando dashboard...');
    
    // Crear instancia del dashboard
    window.simpleDashboard = new SimpleDashboard();
    window.simpleDashboard.init();
    
    // Ocultar loading
    setTimeout(() => {
        const loading = document.getElementById('loading');
        if (loading) {
            loading.style.display = 'none';
        }
    }, 1000);
});

// Exportar para compatibilidad
if (typeof module !== 'undefined' && module.exports) {
    module.exports = SimpleDashboard;
}
