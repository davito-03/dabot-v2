/**
 * Dashboard principal de Da Bot
 * davito.es/dabot
 */

class Dashboard {
    constructor() {
        this.selectedGuild = null;
        this.guildData = null;
        this.refreshInterval = null;
        this.charts = {};
        
        // Referencias a elementos DOM
        this.elements = {
            guildSelect: null,
            statsCards: null,
            loadingIndicator: null,
            errorDisplay: null
        };
        
        this.init();
    }

    /**
     * Inicializar dashboard
     */
    async init() {
        console.log('Inicializando dashboard...');
        
        // Verificar autenticación
        if (!window.discordAuth || !window.discordAuth.checkAuth()) {
            window.location.href = '/dabot/';
            return;
        }

        // Verificar token del bot
        const isValidToken = await window.daBotAPI.verifyToken();
        if (!isValidToken) {
            window.location.href = '/dabot/';
            return;
        }

        // Configurar elementos DOM
        this.setupDOMElements();
        
        // Cargar datos iniciales
        await this.loadInitialData();
        
        // Configurar eventos
        this.setupEventListeners();
        
        // Iniciar actualizaciones automáticas
        this.startAutoRefresh();
        
        console.log('Dashboard inicializado correctamente');
    }

    /**
     * Configurar referencias a elementos DOM
     */
    setupDOMElements() {
        this.elements.guildSelect = document.getElementById('guild-select');
        this.elements.statsCards = document.getElementById('stats-cards');
        this.elements.loadingIndicator = document.getElementById('loading');
        this.elements.errorDisplay = document.getElementById('error-display');
    }

    /**
     * Configurar event listeners
     */
    setupEventListeners() {
        // Selector de servidor
        if (this.elements.guildSelect) {
            this.elements.guildSelect.addEventListener('change', (e) => {
                this.selectGuild(e.target.value);
            });
        }

        // Botones de navegación
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('nav-btn')) {
                this.handleNavigation(e.target.dataset.section);
            }
        });

        // Botón de actualizar
        const refreshBtn = document.getElementById('refresh-btn');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => {
                this.refreshData();
            });
        }

        // Cerrar alertas
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('alert-close')) {
                e.target.parentElement.remove();
            }
        });
    }

    /**
     * Cargar datos iniciales
     */
    async loadInitialData() {
        try {
            this.showLoading(true);
            
            // Cargar estadísticas del bot
            await this.loadBotStats();
            
            // Cargar servidores del usuario
            await this.loadUserGuilds();
            
            // Cargar servidor guardado
            const savedGuild = localStorage.getItem('selected_guild');
            if (savedGuild) {
                this.selectGuild(savedGuild);
            }
            
        } catch (error) {
            console.error('Error cargando datos iniciales:', error);
            this.showError('Error cargando datos del dashboard');
        } finally {
            this.showLoading(false);
        }
    }

    /**
     * Cargar estadísticas del bot
     */
    async loadBotStats() {
        try {
            const stats = await window.daBotAPI.getBotStats();
            this.updateBotStatsDisplay(stats);
        } catch (error) {
            console.error('Error cargando estadísticas del bot:', error);
        }
    }

    /**
     * Cargar servidores del usuario
     */
    async loadUserGuilds() {
        try {
            const guilds = await window.daBotAPI.getUserGuilds();
            this.populateGuildSelect(guilds);
        } catch (error) {
            console.error('Error cargando servidores:', error);
            this.showError('Error cargando la lista de servidores');
        }
    }

    /**
     * Poblar selector de servidores
     */
    populateGuildSelect(guilds) {
        if (!this.elements.guildSelect) return;

        this.elements.guildSelect.innerHTML = '<option value="">Seleccionar servidor...</option>';
        
        guilds.forEach(guild => {
            const option = document.createElement('option');
            option.value = guild.id;
            option.textContent = guild.name;
            option.dataset.icon = guild.icon;
            this.elements.guildSelect.appendChild(option);
        });
    }

    /**
     * Seleccionar servidor
     */
    async selectGuild(guildId) {
        if (!guildId) {
            this.selectedGuild = null;
            this.clearGuildData();
            return;
        }

        try {
            this.showLoading(true);
            
            this.selectedGuild = guildId;
            localStorage.setItem('selected_guild', guildId);
            
            // Cargar datos del servidor
            await this.loadGuildData(guildId);
            
            // Actualizar interfaz
            this.updateGuildDisplay();
            
        } catch (error) {
            console.error('Error seleccionando servidor:', error);
            this.showError('Error cargando datos del servidor');
        } finally {
            this.showLoading(false);
        }
    }

    /**
     * Cargar datos del servidor
     */
    async loadGuildData(guildId) {
        try {
            // Cargar información básica
            const [guildInfo, guildConfig] = await Promise.all([
                window.daBotAPI.getGuildInfo(guildId),
                window.daBotAPI.getGuildConfig(guildId)
            ]);

            this.guildData = {
                info: guildInfo,
                config: guildConfig
            };

            // Cargar datos adicionales
            await this.loadAdditionalGuildData(guildId);
            
        } catch (error) {
            console.error('Error cargando datos del servidor:', error);
            throw error;
        }
    }

    /**
     * Cargar datos adicionales del servidor
     */
    async loadAdditionalGuildData(guildId) {
        try {
            const [warnings, tickets, economy, logs] = await Promise.allSettled([
                window.daBotAPI.getGuildWarnings(guildId),
                window.daBotAPI.getTickets(guildId),
                window.daBotAPI.getEconomyLeaderboard(guildId, 5),
                window.daBotAPI.getGuildLogs(guildId, 10)
            ]);

            // Procesar resultados
            this.guildData.warnings = warnings.status === 'fulfilled' ? warnings.value : [];
            this.guildData.tickets = tickets.status === 'fulfilled' ? tickets.value : [];
            this.guildData.economy = economy.status === 'fulfilled' ? economy.value : [];
            this.guildData.logs = logs.status === 'fulfilled' ? logs.value : [];
            
        } catch (error) {
            console.error('Error cargando datos adicionales:', error);
        }
    }

    /**
     * Actualizar display del bot
     */
    updateBotStatsDisplay(stats) {
        // Estadísticas globales
        this.updateStatCard('total-guilds', stats.guild_count || 0);
        this.updateStatCard('total-users', stats.user_count || 0);
        this.updateStatCard('commands-today', stats.commands_today || 0);
        this.updateStatCard('uptime', this.formatUptime(stats.uptime || 0));
        
        // Estado del bot
        const statusElement = document.getElementById('bot-status');
        if (statusElement) {
            statusElement.className = `status-indicator ${stats.status || 'offline'}`;
            statusElement.textContent = this.getStatusText(stats.status);
        }
    }

    /**
     * Actualizar display del servidor
     */
    updateGuildDisplay() {
        if (!this.guildData) return;

        const { info, config, warnings, tickets, economy, logs } = this.guildData;
        
        // Información básica del servidor
        this.updateGuildHeader(info);
        
        // Estadísticas del servidor
        this.updateGuildStats(info, warnings, tickets, economy);
        
        // Gráficos y datos
        this.updateCharts();
        
        // Actividad reciente
        this.updateRecentActivity(logs);
        
        // Mostrar secciones específicas del servidor
        this.showGuildSections();
    }

    /**
     * Actualizar cabecera del servidor
     */
    updateGuildHeader(guildInfo) {
        const header = document.getElementById('guild-header');
        if (!header) return;

        const iconUrl = guildInfo.icon 
            ? `https://cdn.discordapp.com/icons/${guildInfo.id}/${guildInfo.icon}.png`
            : '/dabot/assets/images/default-server.png';

        header.innerHTML = `
            <div class="guild-info">
                <img src="${iconUrl}" alt="${guildInfo.name}" class="guild-icon">
                <div class="guild-details">
                    <h2>${guildInfo.name}</h2>
                    <p>${guildInfo.member_count} miembros</p>
                </div>
            </div>
            <div class="guild-actions">
                <button class="btn btn-primary" onclick="dashboard.openGuildSettings()">
                    <i class="icon-settings"></i> Configurar
                </button>
            </div>
        `;
    }

    /**
     * Actualizar estadísticas del servidor
     */
    updateGuildStats(guildInfo, warnings, tickets, economy) {
        // Miembros
        this.updateStatCard('guild-members', guildInfo.member_count || 0);
        
        // Warnings activos
        const activeWarnings = warnings ? warnings.filter(w => w.active).length : 0;
        this.updateStatCard('active-warnings', activeWarnings);
        
        // Tickets abiertos
        const openTickets = tickets ? tickets.filter(t => t.status === 'open').length : 0;
        this.updateStatCard('open-tickets', openTickets);
        
        // Economía
        const totalCredits = economy ? economy.reduce((sum, user) => sum + user.balance, 0) : 0;
        this.updateStatCard('total-credits', this.formatNumber(totalCredits));
    }

    /**
     * Actualizar tarjeta de estadística
     */
    updateStatCard(cardId, value) {
        const card = document.getElementById(cardId);
        if (card) {
            const valueElement = card.querySelector('.stat-value');
            if (valueElement) {
                valueElement.textContent = value;
            }
        }
    }

    /**
     * Actualizar gráficos
     */
    updateCharts() {
        // Aquí se pueden añadir gráficos con Chart.js o similar
        console.log('Actualizando gráficos...');
    }

    /**
     * Actualizar actividad reciente
     */
    updateRecentActivity(logs) {
        const activityList = document.getElementById('recent-activity');
        if (!activityList || !logs) return;

        activityList.innerHTML = logs.slice(0, 5).map(log => `
            <div class="activity-item">
                <div class="activity-icon ${log.type}">
                    <i class="icon-${this.getLogIcon(log.type)}"></i>
                </div>
                <div class="activity-content">
                    <p>${log.message}</p>
                    <span class="activity-time">${this.formatRelativeTime(log.timestamp)}</span>
                </div>
            </div>
        `).join('');
    }

    /**
     * Mostrar secciones específicas del servidor
     */
    showGuildSections() {
        const sections = document.querySelectorAll('.guild-section');
        sections.forEach(section => {
            section.style.display = 'block';
        });
        
        const noGuildMessage = document.getElementById('no-guild-selected');
        if (noGuildMessage) {
            noGuildMessage.style.display = 'none';
        }
    }

    /**
     * Limpiar datos del servidor
     */
    clearGuildData() {
        this.guildData = null;
        
        const sections = document.querySelectorAll('.guild-section');
        sections.forEach(section => {
            section.style.display = 'none';
        });
        
        const noGuildMessage = document.getElementById('no-guild-selected');
        if (noGuildMessage) {
            noGuildMessage.style.display = 'block';
        }
        
        localStorage.removeItem('selected_guild');
    }

    /**
     * Actualizar datos
     */
    async refreshData() {
        if (this.selectedGuild) {
            await this.loadGuildData(this.selectedGuild);
            this.updateGuildDisplay();
        }
        await this.loadBotStats();
    }

    /**
     * Iniciar actualización automática
     */
    startAutoRefresh() {
        // Actualizar cada 30 segundos
        this.refreshInterval = setInterval(() => {
            this.refreshData();
        }, 30000);
    }

    /**
     * Detener actualización automática
     */
    stopAutoRefresh() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
            this.refreshInterval = null;
        }
    }

    /**
     * Manejar navegación
     */
    handleNavigation(section) {
        // Guardar sección activa
        localStorage.setItem('active_section', section);
        
        // Actualizar navegación activa
        document.querySelectorAll('.nav-item').forEach(item => {
            item.classList.remove('active');
        });
        
        const activeItem = document.querySelector(`[data-section="${section}"]`);
        if (activeItem) {
            activeItem.closest('.nav-item').classList.add('active');
        }
        
        // Redirigir a la página correspondiente
        switch (section) {
            case 'dashboard':
                // Ya estamos en dashboard
                break;
            case 'tickets':
                window.location.href = '/dabot/tickets.html';
                break;
            case 'moderation':
                window.location.href = '/dabot/moderation.html';
                break;
            case 'economy':
                window.location.href = '/dabot/economy.html';
                break;
            case 'settings':
                window.location.href = '/dabot/settings.html';
                break;
        }
    }

    /**
     * Abrir configuración del servidor
     */
    openGuildSettings() {
        if (this.selectedGuild) {
            window.location.href = `/dabot/settings.html?guild=${this.selectedGuild}`;
        }
    }

    /**
     * Mostrar/ocultar indicador de carga
     */
    showLoading(show) {
        if (this.elements.loadingIndicator) {
            this.elements.loadingIndicator.style.display = show ? 'flex' : 'none';
        }
    }

    /**
     * Mostrar error
     */
    showError(message) {
        const errorContainer = document.getElementById('error-container');
        if (errorContainer) {
            errorContainer.innerHTML = `
                <div class="alert alert-error">
                    <i class="icon-alert-circle"></i>
                    <span>${message}</span>
                    <button class="alert-close">&times;</button>
                </div>
            `;
        }
    }

    // ===== UTILIDADES =====

    /**
     * Formatear tiempo de actividad
     */
    formatUptime(seconds) {
        const days = Math.floor(seconds / 86400);
        const hours = Math.floor((seconds % 86400) / 3600);
        const minutes = Math.floor((seconds % 3600) / 60);
        
        if (days > 0) {
            return `${days}d ${hours}h`;
        } else if (hours > 0) {
            return `${hours}h ${minutes}m`;
        } else {
            return `${minutes}m`;
        }
    }

    /**
     * Formatear número
     */
    formatNumber(num) {
        if (num >= 1000000) {
            return (num / 1000000).toFixed(1) + 'M';
        } else if (num >= 1000) {
            return (num / 1000).toFixed(1) + 'K';
        }
        return num.toString();
    }

    /**
     * Formatear tiempo relativo
     */
    formatRelativeTime(timestamp) {
        const now = new Date();
        const time = new Date(timestamp);
        const diff = now - time;
        
        const minutes = Math.floor(diff / 60000);
        const hours = Math.floor(diff / 3600000);
        const days = Math.floor(diff / 86400000);
        
        if (days > 0) {
            return `hace ${days} día${days > 1 ? 's' : ''}`;
        } else if (hours > 0) {
            return `hace ${hours} hora${hours > 1 ? 's' : ''}`;
        } else if (minutes > 0) {
            return `hace ${minutes} minuto${minutes > 1 ? 's' : ''}`;
        } else {
            return 'hace un momento';
        }
    }

    /**
     * Obtener texto de estado
     */
    getStatusText(status) {
        const statusMap = {
            'online': 'En línea',
            'idle': 'Ausente',
            'dnd': 'No molestar',
            'offline': 'Desconectado'
        };
        return statusMap[status] || 'Desconocido';
    }

    /**
     * Obtener icono de log
     */
    getLogIcon(type) {
        const iconMap = {
            'warning': 'alert-triangle',
            'ban': 'shield-off',
            'kick': 'user-x',
            'mute': 'mic-off',
            'ticket': 'message-circle',
            'economy': 'dollar-sign'
        };
        return iconMap[type] || 'info';
    }
}

// Inicializar dashboard cuando se carga la página
document.addEventListener('DOMContentLoaded', () => {
    window.dashboard = new Dashboard();
});

// Limpiar al salir de la página
window.addEventListener('beforeunload', () => {
    if (window.dashboard) {
        window.dashboard.stopAutoRefresh();
    }
});
