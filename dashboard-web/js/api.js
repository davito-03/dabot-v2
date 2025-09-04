/**
 * Cliente API para Da Bot
 * Comunicación con el bot en Local
 */

class DaBotAPI {
    constructor() {
        // URL base de la API (bot en Local)
        this.baseURL = 'http://localhost:8080/api';
        this.authToken = null;
        this.isAuthenticated = false;
        
        // Configuración por defecto
        this.defaultHeaders = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        };
        
        // Cargar token guardado
        this.loadAuthToken();
    }

    /**
     * Cargar token de autenticación guardado
     */
    loadAuthToken() {
        const token = localStorage.getItem('dabot_auth_token');
        if (token) {
            this.authToken = token;
            this.isAuthenticated = true;
            this.defaultHeaders['Authorization'] = `Bearer ${token}`;
        }
    }

    /**
     * Guardar token de autenticación
     */
    saveAuthToken(token) {
        this.authToken = token;
        this.isAuthenticated = true;
        this.defaultHeaders['Authorization'] = `Bearer ${token}`;
        localStorage.setItem('dabot_auth_token', token);
    }

    /**
     * Realizar petición HTTP genérica
     */
    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        
        const config = {
            headers: { ...this.defaultHeaders, ...(options.headers || {}) },
            ...options
        };

        try {
            console.log(`API Request: ${options.method || 'GET'} ${url}`);
            
            const response = await fetch(url, config);
            
            // Manejar diferentes tipos de respuesta
            let data;
            const contentType = response.headers.get('content-type');
            
            if (contentType && contentType.includes('application/json')) {
                data = await response.json();
            } else {
                data = await response.text();
            }

            if (!response.ok) {
                throw new Error(data.error || data.message || `HTTP ${response.status}: ${response.statusText}`);
            }

            console.log(`API Response:`, data);
            return data;

        } catch (error) {
            console.error('Error en petición API:', error);
            
            // Si el error es de autenticación, limpiar token
            if (error.message.includes('401') || error.message.includes('Unauthorized')) {
                this.logout();
            }
            
            throw error;
        }
    }

    /**
     * Peticiones GET
     */
    async get(endpoint) {
        return this.request(endpoint, { method: 'GET' });
    }

    /**
     * Peticiones POST
     */
    async post(endpoint, data = {}) {
        return this.request(endpoint, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }

    /**
     * Peticiones PUT
     */
    async put(endpoint, data = {}) {
        return this.request(endpoint, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    }

    /**
     * Peticiones DELETE
     */
    async delete(endpoint) {
        return this.request(endpoint, { method: 'DELETE' });
    }

    // ===== AUTENTICACIÓN =====

    /**
     * Autenticar con Discord access token
     */
    async authenticate(discordAccessToken) {
        try {
            const response = await this.post('/auth/discord', {
                access_token: discordAccessToken
            });
            
            this.saveAuthToken(response.access_token);
            return response;
            
        } catch (error) {
            console.error('Error en autenticación:', error);
            throw error;
        }
    }

    /**
     * Cerrar sesión
     */
    logout() {
        this.authToken = null;
        this.isAuthenticated = false;
        delete this.defaultHeaders['Authorization'];
        localStorage.removeItem('dabot_auth_token');
    }

    /**
     * Verificar si el token es válido
     */
    async verifyToken() {
        try {
            await this.get('/auth/verify');
            return true;
        } catch (error) {
            this.logout();
            return false;
        }
    }

    // ===== INFORMACIÓN DEL BOT =====

    /**
     * Obtener estadísticas del bot
     */
    async getBotStats() {
        return this.get('/bot/stats');
    }

    /**
     * Obtener información del bot
     */
    async getBotInfo() {
        return this.get('/bot/info');
    }

    /**
     * Obtener estado del bot
     */
    async getBotStatus() {
        return this.get('/bot/status');
    }

    // ===== SERVIDORES =====

    /**
     * Obtener servidores del usuario
     */
    async getUserGuilds() {
        return this.get('/guilds');
    }

    /**
     * Obtener información de un servidor específico
     */
    async getGuildInfo(guildId) {
        return this.get(`/guilds/${guildId}`);
    }

    /**
     * Obtener configuración de un servidor
     */
    async getGuildConfig(guildId) {
        return this.get(`/guilds/${guildId}/config`);
    }

    /**
     * Actualizar configuración de un servidor
     */
    async updateGuildConfig(guildId, config) {
        return this.put(`/guilds/${guildId}/config`, config);
    }

    // ===== MODERACIÓN =====

    /**
     * Obtener warnings de un usuario
     */
    async getUserWarnings(guildId, userId) {
        return this.get(`/guilds/${guildId}/warnings/${userId}`);
    }

    /**
     * Obtener todas las warnings de un servidor
     */
    async getGuildWarnings(guildId) {
        return this.get(`/guilds/${guildId}/warnings`);
    }

    /**
     * Añadir warning a un usuario
     */
    async addWarning(guildId, userId, reason) {
        return this.post(`/guilds/${guildId}/warnings/${userId}`, { reason });
    }

    /**
     * Remover warning de un usuario
     */
    async removeWarning(guildId, warningId) {
        return this.delete(`/guilds/${guildId}/warnings/${warningId}`);
    }

    // ===== TICKETS =====

    /**
     * Obtener todos los tickets
     */
    async getTickets(guildId) {
        return this.get(`/guilds/${guildId}/tickets`);
    }

    /**
     * Obtener información de un ticket específico
     */
    async getTicket(guildId, ticketId) {
        return this.get(`/guilds/${guildId}/tickets/${ticketId}`);
    }

    /**
     * Cerrar un ticket
     */
    async closeTicket(guildId, ticketId) {
        return this.post(`/guilds/${guildId}/tickets/${ticketId}/close`);
    }

    /**
     * Asignar staff a un ticket
     */
    async assignTicket(guildId, ticketId, staffId) {
        return this.post(`/guilds/${guildId}/tickets/${ticketId}/assign`, { staff_id: staffId });
    }

    /**
     * Añadir mensaje a un ticket
     */
    async addTicketMessage(guildId, ticketId, message) {
        return this.post(`/guilds/${guildId}/tickets/${ticketId}/messages`, { message });
    }

    // ===== ECONOMÍA =====

    /**
     * Obtener balance de un usuario
     */
    async getUserBalance(guildId, userId) {
        return this.get(`/guilds/${guildId}/economy/${userId}`);
    }

    /**
     * Obtener ranking de economía
     */
    async getEconomyLeaderboard(guildId, limit = 10) {
        return this.get(`/guilds/${guildId}/economy/leaderboard?limit=${limit}`);
    }

    /**
     * Transferir créditos entre usuarios
     */
    async transferCredits(guildId, fromUserId, toUserId, amount) {
        return this.post(`/guilds/${guildId}/economy/transfer`, {
            from_user_id: fromUserId,
            to_user_id: toUserId,
            amount: amount
        });
    }

    // ===== LOGS =====

    /**
     * Obtener logs del servidor
     */
    async getGuildLogs(guildId, limit = 50, offset = 0) {
        return this.get(`/guilds/${guildId}/logs?limit=${limit}&offset=${offset}`);
    }

    /**
     * Obtener logs por tipo
     */
    async getLogsByType(guildId, type, limit = 50) {
        return this.get(`/guilds/${guildId}/logs/${type}?limit=${limit}`);
    }

    // ===== VOICE MASTER =====

    /**
     * Obtener canales temporales activos
     */
    async getTempChannels(guildId) {
        return this.get(`/guilds/${guildId}/voicemaster/channels`);
    }

    /**
     * Obtener configuración de VoiceMaster
     */
    async getVoiceMasterConfig(guildId) {
        return this.get(`/guilds/${guildId}/voicemaster/config`);
    }

    /**
     * Actualizar configuración de VoiceMaster
     */
    async updateVoiceMasterConfig(guildId, config) {
        return this.put(`/guilds/${guildId}/voicemaster/config`, config);
    }

    // ===== MÚSICA =====

    /**
     * Obtener estado del reproductor de música
     */
    async getMusicStatus(guildId) {
        return this.get(`/guilds/${guildId}/music/status`);
    }

    /**
     * Obtener cola de reproducción
     */
    async getMusicQueue(guildId) {
        return this.get(`/guilds/${guildId}/music/queue`);
    }

    // ===== UTILIDADES =====

    /**
     * Probar conexión con la API
     */
    async ping() {
        try {
            const start = Date.now();
            await this.get('/ping');
            const end = Date.now();
            return { latency: end - start, status: 'ok' };
        } catch (error) {
            return { latency: -1, status: 'error', error: error.message };
        }
    }

    /**
     * Obtener información de un usuario de Discord
     */
    async getDiscordUser(userId) {
        return this.get(`/discord/users/${userId}`);
    }

    /**
     * Buscar miembros en un servidor
     */
    async searchGuildMembers(guildId, query) {
        return this.get(`/guilds/${guildId}/members/search?q=${encodeURIComponent(query)}`);
    }

    // ===== GESTIÓN DE ERRORES =====

    /**
     * Manejar errores de API de forma centralizada
     */
    handleError(error) {
        console.error('Error en API:', error);
        
        // Mostrar notificación al usuario
        this.showNotification('Error', error.message, 'error');
        
        // Si es error de autenticación, redirigir al login
        if (error.message.includes('401') || error.message.includes('Unauthorized')) {
            window.location.href = '/dabot/';
        }
    }

    /**
     * Mostrar notificación al usuario
     */
    showNotification(title, message, type = 'info') {
        // Crear elemento de notificación
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <h4>${title}</h4>
                <p>${message}</p>
            </div>
            <button class="notification-close">&times;</button>
        `;
        
        // Añadir estilos
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            padding: 1rem;
            max-width: 300px;
            z-index: 1000;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
            animation: slideIn 0.3s ease-out;
        `;
        
        // Añadir al DOM
        document.body.appendChild(notification);
        
        // Evento para cerrar
        const closeBtn = notification.querySelector('.notification-close');
        closeBtn.addEventListener('click', () => {
            notification.remove();
        });
        
        // Auto-remover después de 5 segundos
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 5000);
    }
}

// Crear instancia global
window.daBotAPI = new DaBotAPI();

// Exportar para uso en módulos
if (typeof module !== 'undefined' && module.exports) {
    module.exports = DaBotAPI;
}
