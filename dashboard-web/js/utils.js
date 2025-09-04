/**
 * Utilidades comunes para Da Bot Dashboard
 * davito.es/dabot
 */

// ===== UTILIDADES GENERALES =====

/**
 * Formatear números grandes
 */
function formatNumber(num) {
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
function formatRelativeTime(timestamp) {
    const now = new Date();
    const time = new Date(timestamp);
    const diff = now - time;
    
    const seconds = Math.floor(diff / 1000);
    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(diff / 3600000);
    const days = Math.floor(diff / 86400000);
    const weeks = Math.floor(diff / (86400000 * 7));
    const months = Math.floor(diff / (86400000 * 30));
    
    if (months > 0) {
        return `hace ${months} mes${months > 1 ? 'es' : ''}`;
    } else if (weeks > 0) {
        return `hace ${weeks} semana${weeks > 1 ? 's' : ''}`;
    } else if (days > 0) {
        return `hace ${days} día${days > 1 ? 's' : ''}`;
    } else if (hours > 0) {
        return `hace ${hours} hora${hours > 1 ? 's' : ''}`;
    } else if (minutes > 0) {
        return `hace ${minutes} minuto${minutes > 1 ? 's' : ''}`;
    } else if (seconds > 30) {
        return `hace ${seconds} segundo${seconds > 1 ? 's' : ''}`;
    } else {
        return 'hace un momento';
    }
}

/**
 * Formatear fecha y hora
 */
function formatDateTime(timestamp, options = {}) {
    const defaultOptions = {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    };
    
    const formatOptions = { ...defaultOptions, ...options };
    return new Date(timestamp).toLocaleDateString('es-ES', formatOptions);
}

/**
 * Formatear duración en segundos
 */
function formatDuration(seconds) {
    const days = Math.floor(seconds / 86400);
    const hours = Math.floor((seconds % 86400) / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = Math.floor(seconds % 60);
    
    const parts = [];
    
    if (days > 0) parts.push(`${days}d`);
    if (hours > 0) parts.push(`${hours}h`);
    if (minutes > 0) parts.push(`${minutes}m`);
    if (secs > 0 || parts.length === 0) parts.push(`${secs}s`);
    
    return parts.join(' ');
}

/**
 * Truncar texto
 */
function truncateText(text, maxLength, suffix = '...') {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength - suffix.length) + suffix;
}

/**
 * Escapar HTML
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

/**
 * Generar color aleatorio basado en texto
 */
function generateColorFromText(text) {
    let hash = 0;
    for (let i = 0; i < text.length; i++) {
        hash = text.charCodeAt(i) + ((hash << 5) - hash);
    }
    
    const hue = Math.abs(hash) % 360;
    return `hsl(${hue}, 70%, 60%)`;
}

// ===== SISTEMA DE NOTIFICACIONES =====

class NotificationSystem {
    constructor() {
        this.container = null;
        this.notifications = [];
        this.createContainer();
    }

    createContainer() {
        this.container = document.createElement('div');
        this.container.id = 'notification-container';
        this.container.className = 'notification-container';
        this.container.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 10000;
            max-width: 400px;
        `;
        document.body.appendChild(this.container);
    }

    show(title, message, type = 'info', duration = 5000) {
        const notification = this.createNotification(title, message, type);
        this.container.appendChild(notification);
        this.notifications.push(notification);

        // Animación de entrada
        setTimeout(() => {
            notification.classList.add('show');
        }, 10);

        // Auto-remover
        if (duration > 0) {
            setTimeout(() => {
                this.remove(notification);
            }, duration);
        }

        return notification;
    }

    createNotification(title, message, type) {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        
        const icon = this.getIcon(type);
        
        notification.innerHTML = `
            <div class="notification-icon">
                <i class="icon-${icon}"></i>
            </div>
            <div class="notification-content">
                <h4>${title}</h4>
                <p>${message}</p>
            </div>
            <button class="notification-close" onclick="notifications.remove(this.parentElement)">
                <i class="icon-x"></i>
            </button>
        `;

        return notification;
    }

    getIcon(type) {
        const icons = {
            'success': 'check-circle',
            'error': 'alert-circle',
            'warning': 'alert-triangle',
            'info': 'info'
        };
        return icons[type] || 'info';
    }

    remove(notification) {
        notification.classList.add('removing');
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
            const index = this.notifications.indexOf(notification);
            if (index > -1) {
                this.notifications.splice(index, 1);
            }
        }, 300);
    }

    success(title, message) {
        return this.show(title, message, 'success');
    }

    error(title, message) {
        return this.show(title, message, 'error');
    }

    warning(title, message) {
        return this.show(title, message, 'warning');
    }

    info(title, message) {
        return this.show(title, message, 'info');
    }
}

// ===== SISTEMA DE MODALES =====

class ModalSystem {
    constructor() {
        this.activeModal = null;
        this.setupEventListeners();
    }

    setupEventListeners() {
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('modal-backdrop')) {
                this.close();
            }
            
            if (e.target.classList.contains('modal-close')) {
                this.close();
            }
        });

        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.activeModal) {
                this.close();
            }
        });
    }

    create(content, options = {}) {
        const modal = document.createElement('div');
        modal.className = 'modal-backdrop';
        
        const modalDialog = document.createElement('div');
        modalDialog.className = `modal-dialog ${options.size || 'medium'}`;
        
        modalDialog.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h3>${options.title || 'Modal'}</h3>
                    <button class="modal-close">
                        <i class="icon-x"></i>
                    </button>
                </div>
                <div class="modal-body">
                    ${content}
                </div>
                ${options.footer ? `
                    <div class="modal-footer">
                        ${options.footer}
                    </div>
                ` : ''}
            </div>
        `;
        
        modal.appendChild(modalDialog);
        return modal;
    }

    show(content, options = {}) {
        this.close(); // Cerrar modal anterior si existe
        
        this.activeModal = this.create(content, options);
        document.body.appendChild(this.activeModal);
        
        setTimeout(() => {
            this.activeModal.classList.add('show');
        }, 10);
        
        return this.activeModal;
    }

    close() {
        if (this.activeModal) {
            this.activeModal.classList.add('hiding');
            setTimeout(() => {
                if (this.activeModal && this.activeModal.parentNode) {
                    this.activeModal.parentNode.removeChild(this.activeModal);
                }
                this.activeModal = null;
            }, 300);
        }
    }

    confirm(title, message, onConfirm, onCancel) {
        const content = `
            <p>${message}</p>
        `;
        
        const footer = `
            <button class="btn btn-secondary" onclick="modals.close(); ${onCancel ? onCancel.toString() + '()' : ''}">
                Cancelar
            </button>
            <button class="btn btn-danger" onclick="modals.close(); (${onConfirm.toString()})()">
                Confirmar
            </button>
        `;
        
        return this.show(content, { title, footer });
    }
}

// ===== UTILIDADES DE TABLA =====

class TableUtils {
    static sortTable(table, columnIndex, direction = 'asc') {
        const tbody = table.querySelector('tbody');
        const rows = Array.from(tbody.querySelectorAll('tr'));
        
        rows.sort((a, b) => {
            const aVal = a.cells[columnIndex].textContent.trim();
            const bVal = b.cells[columnIndex].textContent.trim();
            
            // Intentar convertir a números
            const aNum = parseFloat(aVal);
            const bNum = parseFloat(bVal);
            
            if (!isNaN(aNum) && !isNaN(bNum)) {
                return direction === 'asc' ? aNum - bNum : bNum - aNum;
            } else {
                return direction === 'asc' ? 
                    aVal.localeCompare(bVal) : 
                    bVal.localeCompare(aVal);
            }
        });
        
        tbody.innerHTML = '';
        rows.forEach(row => tbody.appendChild(row));
    }

    static filterTable(table, searchTerm) {
        const tbody = table.querySelector('tbody');
        const rows = tbody.querySelectorAll('tr');
        
        rows.forEach(row => {
            const text = row.textContent.toLowerCase();
            const matches = text.includes(searchTerm.toLowerCase());
            row.style.display = matches ? '' : 'none';
        });
    }

    static exportTableToCSV(table, filename = 'data.csv') {
        const rows = table.querySelectorAll('tr');
        const csvContent = Array.from(rows).map(row => {
            const cells = row.querySelectorAll('th, td');
            return Array.from(cells).map(cell => 
                `"${cell.textContent.replace(/"/g, '""')}"`
            ).join(',');
        }).join('\n');
        
        const blob = new Blob([csvContent], { type: 'text/csv' });
        const url = URL.createObjectURL(blob);
        
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }
}

// ===== VALIDACIÓN DE FORMULARIOS =====

class FormValidator {
    constructor(form) {
        this.form = form;
        this.errors = {};
        this.setupValidation();
    }

    setupValidation() {
        this.form.addEventListener('submit', (e) => {
            e.preventDefault();
            if (this.validate()) {
                this.onValidSubmit();
            }
        });

        // Validación en tiempo real
        this.form.addEventListener('input', (e) => {
            this.validateField(e.target);
        });
    }

    validate() {
        this.errors = {};
        
        const fields = this.form.querySelectorAll('input, textarea, select');
        fields.forEach(field => this.validateField(field));
        
        this.showErrors();
        return Object.keys(this.errors).length === 0;
    }

    validateField(field) {
        const name = field.name || field.id;
        if (!name) return;

        const value = field.value.trim();
        const rules = this.getFieldRules(field);
        
        delete this.errors[name];

        for (const rule of rules) {
            const error = this.applyRule(value, rule, field);
            if (error) {
                this.errors[name] = error;
                break;
            }
        }

        this.updateFieldDisplay(field);
    }

    getFieldRules(field) {
        const rules = [];
        
        if (field.required) {
            rules.push({ type: 'required' });
        }
        
        if (field.type === 'email') {
            rules.push({ type: 'email' });
        }
        
        if (field.minLength) {
            rules.push({ type: 'minLength', value: field.minLength });
        }
        
        if (field.maxLength) {
            rules.push({ type: 'maxLength', value: field.maxLength });
        }
        
        if (field.pattern) {
            rules.push({ type: 'pattern', value: field.pattern });
        }
        
        return rules;
    }

    applyRule(value, rule, field) {
        switch (rule.type) {
            case 'required':
                return value === '' ? 'Este campo es obligatorio' : null;
                
            case 'email':
                const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
                return !emailRegex.test(value) ? 'Email inválido' : null;
                
            case 'minLength':
                return value.length < rule.value ? 
                    `Mínimo ${rule.value} caracteres` : null;
                
            case 'maxLength':
                return value.length > rule.value ? 
                    `Máximo ${rule.value} caracteres` : null;
                
            case 'pattern':
                const regex = new RegExp(rule.value);
                return !regex.test(value) ? 'Formato inválido' : null;
                
            default:
                return null;
        }
    }

    updateFieldDisplay(field) {
        const name = field.name || field.id;
        const errorElement = this.form.querySelector(`[data-error="${name}"]`);
        
        if (this.errors[name]) {
            field.classList.add('error');
            if (errorElement) {
                errorElement.textContent = this.errors[name];
                errorElement.style.display = 'block';
            }
        } else {
            field.classList.remove('error');
            if (errorElement) {
                errorElement.style.display = 'none';
            }
        }
    }

    showErrors() {
        Object.keys(this.errors).forEach(name => {
            const field = this.form.querySelector(`[name="${name}"], #${name}`);
            if (field) {
                this.updateFieldDisplay(field);
            }
        });
    }

    onValidSubmit() {
        // Override en clases derivadas
        console.log('Formulario válido');
    }
}

// ===== UTILIDADES DE STORAGE =====

class StorageUtils {
    static set(key, value, expiration = null) {
        const data = {
            value,
            timestamp: Date.now(),
            expiration
        };
        localStorage.setItem(key, JSON.stringify(data));
    }

    static get(key, defaultValue = null) {
        try {
            const item = localStorage.getItem(key);
            if (!item) return defaultValue;
            
            const data = JSON.parse(item);
            
            // Verificar expiración
            if (data.expiration && Date.now() > data.expiration) {
                localStorage.removeItem(key);
                return defaultValue;
            }
            
            return data.value;
        } catch (error) {
            console.error('Error al leer storage:', error);
            return defaultValue;
        }
    }

    static remove(key) {
        localStorage.removeItem(key);
    }

    static clear() {
        localStorage.clear();
    }

    static setSession(key, value) {
        sessionStorage.setItem(key, JSON.stringify(value));
    }

    static getSession(key, defaultValue = null) {
        try {
            const item = sessionStorage.getItem(key);
            return item ? JSON.parse(item) : defaultValue;
        } catch (error) {
            console.error('Error al leer session storage:', error);
            return defaultValue;
        }
    }
}

// ===== INSTANCIAS GLOBALES =====

// Crear instancias globales
window.notifications = new NotificationSystem();
window.modals = new ModalSystem();

// Exportar utilidades
window.DaBotUtils = {
    formatNumber,
    formatRelativeTime,
    formatDateTime,
    formatDuration,
    truncateText,
    escapeHtml,
    generateColorFromText,
    TableUtils,
    FormValidator,
    StorageUtils
};

// ===== FUNCIONES DE NAVEGACIÓN =====

/**
 * Cambiar página activa en la navegación
 */
function setActivePage(pageName) {
    // Remover clase activa de todos los elementos
    document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.remove('active');
    });
    
    // Añadir clase activa al elemento correspondiente
    const activeItem = document.querySelector(`[data-page="${pageName}"]`);
    if (activeItem) {
        activeItem.closest('.nav-item').classList.add('active');
    }
    
    // Guardar página activa
    StorageUtils.set('active_page', pageName);
}

/**
 * Inicializar navegación
 */
function initNavigation() {
    // Obtener página activa guardada
    const activePage = StorageUtils.get('active_page');
    if (activePage) {
        setActivePage(activePage);
    }
    
    // Configurar eventos de navegación
    document.addEventListener('click', (e) => {
        const navLink = e.target.closest('[data-page]');
        if (navLink) {
            const page = navLink.dataset.page;
            setActivePage(page);
        }
    });
}

// ===== INICIALIZACIÓN =====

document.addEventListener('DOMContentLoaded', () => {
    // Inicializar navegación
    initNavigation();
    
    // Configurar tooltips
    const tooltips = document.querySelectorAll('[data-tooltip]');
    tooltips.forEach(element => {
        element.addEventListener('mouseenter', showTooltip);
        element.addEventListener('mouseleave', hideTooltip);
    });
    
    // Configurar tabs
    const tabs = document.querySelectorAll('[data-tab]');
    tabs.forEach(tab => {
        tab.addEventListener('click', () => switchTab(tab.dataset.tab));
    });
    
    console.log('Utilidades de Da Bot inicializadas');
});

// ===== FUNCIONES AUXILIARES =====

function showTooltip(e) {
    const tooltip = document.createElement('div');
    tooltip.className = 'tooltip';
    tooltip.textContent = e.target.dataset.tooltip;
    
    document.body.appendChild(tooltip);
    
    const rect = e.target.getBoundingClientRect();
    tooltip.style.left = rect.left + rect.width / 2 - tooltip.offsetWidth / 2 + 'px';
    tooltip.style.top = rect.top - tooltip.offsetHeight - 5 + 'px';
    
    e.target._tooltip = tooltip;
}

function hideTooltip(e) {
    if (e.target._tooltip) {
        e.target._tooltip.remove();
        delete e.target._tooltip;
    }
}

function switchTab(tabId) {
    // Ocultar todos los contenidos de tabs
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });
    
    // Remover clase activa de todos los tabs
    document.querySelectorAll('[data-tab]').forEach(tab => {
        tab.classList.remove('active');
    });
    
    // Mostrar contenido seleccionado
    const targetContent = document.getElementById(tabId);
    if (targetContent) {
        targetContent.classList.add('active');
    }
    
    // Activar tab seleccionado
    const targetTab = document.querySelector(`[data-tab="${tabId}"]`);
    if (targetTab) {
        targetTab.classList.add('active');
    }
}
