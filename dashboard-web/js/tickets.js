/**
 * Sistema de Tickets para Da Bot Dashboard
 * davito.es/dabot/tickets
 */

class TicketManager {
    constructor() {
        this.selectedGuild = null;
        this.tickets = [];
        this.selectedTicket = null;
        this.refreshInterval = null;
        this.filters = {
            status: 'all',
            priority: 'all',
            assigned: 'all'
        };
        
        // Referencias DOM
        this.elements = {
            guildSelect: null,
            ticketsContainer: null,
            ticketDetails: null,
            filterButtons: null,
            searchInput: null
        };
        
        this.init();
    }

    /**
     * Inicializar gestor de tickets
     */
    async init() {
        console.log('Inicializando gestor de tickets...');
        
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
        
        // Iniciar actualización automática
        this.startAutoRefresh();
        
        console.log('Gestor de tickets inicializado');
    }

    /**
     * Configurar referencias DOM
     */
    setupDOMElements() {
        this.elements.guildSelect = document.getElementById('guild-select');
        this.elements.ticketsContainer = document.getElementById('tickets-container');
        this.elements.ticketDetails = document.getElementById('ticket-details');
        this.elements.filterButtons = document.querySelectorAll('.filter-btn');
        this.elements.searchInput = document.getElementById('ticket-search');
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

        // Filtros
        this.elements.filterButtons.forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.setFilter(e.target.dataset.filter, e.target.dataset.value);
            });
        });

        // Búsqueda
        if (this.elements.searchInput) {
            this.elements.searchInput.addEventListener('input', (e) => {
                this.searchTickets(e.target.value);
            });
        }

        // Botones de acción
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('ticket-item')) {
                this.selectTicket(e.target.dataset.ticketId);
            }
            
            if (e.target.classList.contains('close-ticket-btn')) {
                this.closeTicket(e.target.dataset.ticketId);
            }
            
            if (e.target.classList.contains('assign-ticket-btn')) {
                this.showAssignModal(e.target.dataset.ticketId);
            }
            
            if (e.target.classList.contains('refresh-btn')) {
                this.refreshTickets();
            }
        });

        // Modal de asignación
        const assignModal = document.getElementById('assign-modal');
        const assignForm = document.getElementById('assign-form');
        
        if (assignForm) {
            assignForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.assignTicket();
            });
        }

        // Envío de mensajes
        const messageForm = document.getElementById('message-form');
        if (messageForm) {
            messageForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.sendMessage();
            });
        }
    }

    /**
     * Cargar datos iniciales
     */
    async loadInitialData() {
        try {
            this.showLoading(true);
            
            // Cargar servidores del usuario
            await this.loadUserGuilds();
            
            // Cargar servidor guardado
            const savedGuild = localStorage.getItem('selected_guild');
            if (savedGuild) {
                await this.selectGuild(savedGuild);
            }
            
        } catch (error) {
            console.error('Error cargando datos iniciales:', error);
            this.showError('Error cargando datos de tickets');
        } finally {
            this.showLoading(false);
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
            throw error;
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
            this.elements.guildSelect.appendChild(option);
        });
    }

    /**
     * Seleccionar servidor
     */
    async selectGuild(guildId) {
        if (!guildId) {
            this.selectedGuild = null;
            this.clearTickets();
            return;
        }

        try {
            this.showLoading(true);
            
            this.selectedGuild = guildId;
            localStorage.setItem('selected_guild', guildId);
            
            // Cargar tickets del servidor
            await this.loadTickets(guildId);
            
        } catch (error) {
            console.error('Error seleccionando servidor:', error);
            this.showError('Error cargando tickets del servidor');
        } finally {
            this.showLoading(false);
        }
    }

    /**
     * Cargar tickets del servidor
     */
    async loadTickets(guildId) {
        try {
            const tickets = await window.daBotAPI.getTickets(guildId);
            this.tickets = tickets;
            this.renderTickets();
            
            // Actualizar estadísticas
            this.updateTicketStats();
            
        } catch (error) {
            console.error('Error cargando tickets:', error);
            throw error;
        }
    }

    /**
     * Renderizar lista de tickets
     */
    renderTickets() {
        if (!this.elements.ticketsContainer) return;

        const filteredTickets = this.getFilteredTickets();
        
        if (filteredTickets.length === 0) {
            this.elements.ticketsContainer.innerHTML = `
                <div class="no-tickets">
                    <i class="icon-inbox"></i>
                    <h3>No hay tickets</h3>
                    <p>No se encontraron tickets que coincidan con los filtros.</p>
                </div>
            `;
            return;
        }

        this.elements.ticketsContainer.innerHTML = filteredTickets.map(ticket => 
            this.renderTicketItem(ticket)
        ).join('');
    }

    /**
     * Renderizar item de ticket
     */
    renderTicketItem(ticket) {
        const statusClass = this.getStatusClass(ticket.status);
        const priorityClass = this.getPriorityClass(ticket.priority);
        const timeAgo = this.formatRelativeTime(ticket.created_at);
        
        return `
            <div class="ticket-item ${statusClass}" data-ticket-id="${ticket.id}">
                <div class="ticket-header">
                    <div class="ticket-info">
                        <h4>#${ticket.id} - ${ticket.subject}</h4>
                        <div class="ticket-meta">
                            <span class="ticket-user">
                                <i class="icon-user"></i>
                                ${ticket.user.username}
                            </span>
                            <span class="ticket-time">
                                <i class="icon-clock"></i>
                                ${timeAgo}
                            </span>
                        </div>
                    </div>
                    <div class="ticket-badges">
                        <span class="badge badge-status ${statusClass}">
                            ${this.getStatusText(ticket.status)}
                        </span>
                        <span class="badge badge-priority ${priorityClass}">
                            ${this.getPriorityText(ticket.priority)}
                        </span>
                    </div>
                </div>
                
                <div class="ticket-preview">
                    <p>${ticket.content.substring(0, 150)}${ticket.content.length > 150 ? '...' : ''}</p>
                </div>
                
                <div class="ticket-footer">
                    <div class="ticket-assigned">
                        ${ticket.assigned_to ? `
                            <span class="assigned-to">
                                <i class="icon-user-check"></i>
                                Asignado a ${ticket.assigned_to.username}
                            </span>
                        ` : `
                            <span class="unassigned">
                                <i class="icon-user-x"></i>
                                Sin asignar
                            </span>
                        `}
                    </div>
                    
                    <div class="ticket-actions">
                        <button class="btn btn-sm btn-secondary assign-ticket-btn" 
                                data-ticket-id="${ticket.id}">
                            <i class="icon-user-plus"></i>
                            Asignar
                        </button>
                        
                        ${ticket.status === 'open' ? `
                            <button class="btn btn-sm btn-danger close-ticket-btn" 
                                    data-ticket-id="${ticket.id}">
                                <i class="icon-x"></i>
                                Cerrar
                            </button>
                        ` : ''}
                    </div>
                </div>
            </div>
        `;
    }

    /**
     * Obtener tickets filtrados
     */
    getFilteredTickets() {
        let filtered = [...this.tickets];
        
        // Filtrar por estado
        if (this.filters.status !== 'all') {
            filtered = filtered.filter(ticket => ticket.status === this.filters.status);
        }
        
        // Filtrar por prioridad
        if (this.filters.priority !== 'all') {
            filtered = filtered.filter(ticket => ticket.priority === this.filters.priority);
        }
        
        // Filtrar por asignación
        if (this.filters.assigned !== 'all') {
            if (this.filters.assigned === 'assigned') {
                filtered = filtered.filter(ticket => ticket.assigned_to);
            } else {
                filtered = filtered.filter(ticket => !ticket.assigned_to);
            }
        }
        
        // Ordenar por fecha (más recientes primero)
        filtered.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
        
        return filtered;
    }

    /**
     * Establecer filtro
     */
    setFilter(filterType, value) {
        this.filters[filterType] = value;
        
        // Actualizar botones activos
        this.updateFilterButtons(filterType, value);
        
        // Re-renderizar tickets
        this.renderTickets();
    }

    /**
     * Actualizar botones de filtro
     */
    updateFilterButtons(filterType, value) {
        const filterGroup = document.querySelector(`[data-filter-group="${filterType}"]`);
        if (filterGroup) {
            const buttons = filterGroup.querySelectorAll('.filter-btn');
            buttons.forEach(btn => {
                btn.classList.remove('active');
                if (btn.dataset.value === value) {
                    btn.classList.add('active');
                }
            });
        }
    }

    /**
     * Buscar tickets
     */
    searchTickets(query) {
        if (!query.trim()) {
            this.renderTickets();
            return;
        }
        
        const searchTerms = query.toLowerCase().split(' ');
        const filtered = this.tickets.filter(ticket => {
            const searchText = `
                ${ticket.subject} 
                ${ticket.content} 
                ${ticket.user.username}
                #${ticket.id}
            `.toLowerCase();
            
            return searchTerms.every(term => searchText.includes(term));
        });
        
        this.renderFilteredTickets(filtered);
    }

    /**
     * Renderizar tickets filtrados por búsqueda
     */
    renderFilteredTickets(tickets) {
        if (!this.elements.ticketsContainer) return;

        if (tickets.length === 0) {
            this.elements.ticketsContainer.innerHTML = `
                <div class="no-tickets">
                    <i class="icon-search"></i>
                    <h3>Sin resultados</h3>
                    <p>No se encontraron tickets que coincidan con la búsqueda.</p>
                </div>
            `;
            return;
        }

        this.elements.ticketsContainer.innerHTML = tickets.map(ticket => 
            this.renderTicketItem(ticket)
        ).join('');
    }

    /**
     * Seleccionar ticket para mostrar detalles
     */
    async selectTicket(ticketId) {
        try {
            this.showTicketLoading(true);
            
            const ticket = await window.daBotAPI.getTicket(this.selectedGuild, ticketId);
            this.selectedTicket = ticket;
            
            this.renderTicketDetails(ticket);
            
            // Marcar como seleccionado en la lista
            document.querySelectorAll('.ticket-item').forEach(item => {
                item.classList.remove('selected');
            });
            
            const selectedItem = document.querySelector(`[data-ticket-id="${ticketId}"]`);
            if (selectedItem) {
                selectedItem.classList.add('selected');
            }
            
        } catch (error) {
            console.error('Error cargando detalles del ticket:', error);
            this.showError('Error cargando detalles del ticket');
        } finally {
            this.showTicketLoading(false);
        }
    }

    /**
     * Renderizar detalles del ticket
     */
    renderTicketDetails(ticket) {
        if (!this.elements.ticketDetails) return;

        const statusClass = this.getStatusClass(ticket.status);
        const priorityClass = this.getPriorityClass(ticket.priority);
        
        this.elements.ticketDetails.innerHTML = `
            <div class="ticket-details-header">
                <div class="ticket-title">
                    <h2>#${ticket.id} - ${ticket.subject}</h2>
                    <div class="ticket-badges">
                        <span class="badge badge-status ${statusClass}">
                            ${this.getStatusText(ticket.status)}
                        </span>
                        <span class="badge badge-priority ${priorityClass}">
                            ${this.getPriorityText(ticket.priority)}
                        </span>
                    </div>
                </div>
                
                <div class="ticket-actions">
                    ${ticket.status === 'open' ? `
                        <button class="btn btn-danger close-ticket-btn" data-ticket-id="${ticket.id}">
                            <i class="icon-x"></i>
                            Cerrar Ticket
                        </button>
                    ` : ''}
                    
                    <button class="btn btn-secondary assign-ticket-btn" data-ticket-id="${ticket.id}">
                        <i class="icon-user-plus"></i>
                        ${ticket.assigned_to ? 'Reasignar' : 'Asignar'}
                    </button>
                </div>
            </div>
            
            <div class="ticket-info-grid">
                <div class="info-item">
                    <label>Usuario:</label>
                    <div class="user-info">
                        <img src="https://cdn.discordapp.com/avatars/${ticket.user.id}/${ticket.user.avatar}.png" 
                             alt="${ticket.user.username}" class="user-avatar-sm">
                        <span>${ticket.user.username}#${ticket.user.discriminator}</span>
                    </div>
                </div>
                
                <div class="info-item">
                    <label>Creado:</label>
                    <span>${this.formatDateTime(ticket.created_at)}</span>
                </div>
                
                <div class="info-item">
                    <label>Asignado a:</label>
                    <span>${ticket.assigned_to ? 
                        `${ticket.assigned_to.username}#${ticket.assigned_to.discriminator}` : 
                        'Sin asignar'
                    }</span>
                </div>
                
                <div class="info-item">
                    <label>Última actividad:</label>
                    <span>${this.formatRelativeTime(ticket.updated_at)}</span>
                </div>
            </div>
            
            <div class="ticket-messages">
                <h3>Conversación</h3>
                <div class="messages-container" id="messages-container">
                    ${this.renderTicketMessages(ticket.messages || [])}
                </div>
                
                ${ticket.status === 'open' ? `
                    <form id="message-form" class="message-form">
                        <div class="form-group">
                            <textarea id="message-input" placeholder="Escribe tu respuesta..." required></textarea>
                        </div>
                        <div class="form-actions">
                            <button type="submit" class="btn btn-primary">
                                <i class="icon-send"></i>
                                Enviar Mensaje
                            </button>
                        </div>
                    </form>
                ` : ''}
            </div>
        `;
    }

    /**
     * Renderizar mensajes del ticket
     */
    renderTicketMessages(messages) {
        if (!messages.length) {
            return '<p class="no-messages">No hay mensajes en este ticket.</p>';
        }
        
        return messages.map(message => `
            <div class="message ${message.author.bot ? 'staff-message' : 'user-message'}">
                <div class="message-header">
                    <div class="message-author">
                        <img src="https://cdn.discordapp.com/avatars/${message.author.id}/${message.author.avatar}.png" 
                             alt="${message.author.username}" class="author-avatar">
                        <span class="author-name">${message.author.username}</span>
                        ${message.author.bot ? '<span class="staff-badge">Staff</span>' : ''}
                    </div>
                    <span class="message-time">${this.formatDateTime(message.timestamp)}</span>
                </div>
                <div class="message-content">
                    <p>${this.formatMessageContent(message.content)}</p>
                    ${message.attachments ? this.renderAttachments(message.attachments) : ''}
                </div>
            </div>
        `).join('');
    }

    /**
     * Cerrar ticket
     */
    async closeTicket(ticketId) {
        const confirmed = confirm('¿Estás seguro de que quieres cerrar este ticket?');
        if (!confirmed) return;
        
        try {
            await window.daBotAPI.closeTicket(this.selectedGuild, ticketId);
            
            // Actualizar tickets
            await this.refreshTickets();
            
            this.showSuccess('Ticket cerrado correctamente');
            
        } catch (error) {
            console.error('Error cerrando ticket:', error);
            this.showError('Error al cerrar el ticket');
        }
    }

    /**
     * Mostrar modal de asignación
     */
    showAssignModal(ticketId) {
        // Implementar modal de asignación
        console.log('Mostrar modal de asignación para ticket:', ticketId);
    }

    /**
     * Asignar ticket
     */
    async assignTicket() {
        // Implementar asignación de ticket
        console.log('Asignar ticket');
    }

    /**
     * Enviar mensaje
     */
    async sendMessage() {
        const messageInput = document.getElementById('message-input');
        if (!messageInput || !this.selectedTicket) return;
        
        const message = messageInput.value.trim();
        if (!message) return;
        
        try {
            await window.daBotAPI.addTicketMessage(
                this.selectedGuild, 
                this.selectedTicket.id, 
                message
            );
            
            messageInput.value = '';
            
            // Recargar detalles del ticket
            await this.selectTicket(this.selectedTicket.id);
            
            this.showSuccess('Mensaje enviado');
            
        } catch (error) {
            console.error('Error enviando mensaje:', error);
            this.showError('Error al enviar el mensaje');
        }
    }

    /**
     * Actualizar estadísticas de tickets
     */
    updateTicketStats() {
        const stats = {
            total: this.tickets.length,
            open: this.tickets.filter(t => t.status === 'open').length,
            pending: this.tickets.filter(t => t.status === 'pending').length,
            closed: this.tickets.filter(t => t.status === 'closed').length,
            unassigned: this.tickets.filter(t => !t.assigned_to).length
        };
        
        // Actualizar elementos de estadísticas
        Object.keys(stats).forEach(key => {
            const element = document.getElementById(`${key}-tickets`);
            if (element) {
                element.textContent = stats[key];
            }
        });
    }

    /**
     * Refrescar tickets
     */
    async refreshTickets() {
        if (this.selectedGuild) {
            await this.loadTickets(this.selectedGuild);
        }
    }

    /**
     * Iniciar actualización automática
     */
    startAutoRefresh() {
        this.refreshInterval = setInterval(() => {
            if (this.selectedGuild) {
                this.refreshTickets();
            }
        }, 30000); // 30 segundos
    }

    /**
     * Limpiar tickets
     */
    clearTickets() {
        this.tickets = [];
        this.selectedTicket = null;
        
        if (this.elements.ticketsContainer) {
            this.elements.ticketsContainer.innerHTML = `
                <div class="no-guild">
                    <i class="icon-server"></i>
                    <h3>Selecciona un servidor</h3>
                    <p>Elige un servidor para ver sus tickets.</p>
                </div>
            `;
        }
        
        if (this.elements.ticketDetails) {
            this.elements.ticketDetails.innerHTML = '';
        }
    }

    // ===== UTILIDADES =====

    getStatusClass(status) {
        const classes = {
            'open': 'status-open',
            'pending': 'status-pending', 
            'closed': 'status-closed'
        };
        return classes[status] || 'status-unknown';
    }

    getStatusText(status) {
        const texts = {
            'open': 'Abierto',
            'pending': 'Pendiente',
            'closed': 'Cerrado'
        };
        return texts[status] || 'Desconocido';
    }

    getPriorityClass(priority) {
        const classes = {
            'low': 'priority-low',
            'medium': 'priority-medium',
            'high': 'priority-high',
            'urgent': 'priority-urgent'
        };
        return classes[priority] || 'priority-medium';
    }

    getPriorityText(priority) {
        const texts = {
            'low': 'Baja',
            'medium': 'Media',
            'high': 'Alta',
            'urgent': 'Urgente'
        };
        return texts[priority] || 'Media';
    }

    formatDateTime(timestamp) {
        return new Date(timestamp).toLocaleString('es-ES');
    }

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

    formatMessageContent(content) {
        // Básico formateo de mensaje (escapar HTML, convertir enlaces, etc.)
        return content.replace(/</g, '&lt;').replace(/>/g, '&gt;');
    }

    renderAttachments(attachments) {
        if (!attachments.length) return '';
        
        return `
            <div class="message-attachments">
                ${attachments.map(att => `
                    <a href="${att.url}" target="_blank" class="attachment">
                        <i class="icon-paperclip"></i>
                        ${att.filename}
                    </a>
                `).join('')}
            </div>
        `;
    }

    showLoading(show) {
        const loader = document.getElementById('tickets-loading');
        if (loader) {
            loader.style.display = show ? 'flex' : 'none';
        }
    }

    showTicketLoading(show) {
        const loader = document.getElementById('ticket-details-loading');
        if (loader) {
            loader.style.display = show ? 'flex' : 'none';
        }
    }

    showError(message) {
        console.error(message);
        // Implementar notificación de error
    }

    showSuccess(message) {
        console.log(message);
        // Implementar notificación de éxito
    }
}

// Inicializar cuando se carga la página
document.addEventListener('DOMContentLoaded', () => {
    window.ticketManager = new TicketManager();
});

// Limpiar al salir
window.addEventListener('beforeunload', () => {
    if (window.ticketManager && window.ticketManager.refreshInterval) {
        clearInterval(window.ticketManager.refreshInterval);
    }
});
