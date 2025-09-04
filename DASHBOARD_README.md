# Dashboard Web para DaBot v2
# Configurado para davito.es/dabot en Hostalia

## 📁 Estructura del proyecto web (para subir por FTP)

```
dabot/                          # carpeta principal en davito.es/dabot
├── index.html                  # página principal
├── login.html                  # página de login
├── dashboard.html              # panel principal
├── tickets.html                # gestión de tickets
├── config.html                 # configuración del bot
├── css/
│   ├── style.css              # estilos principales
│   ├── dashboard.css          # estilos del dashboard
│   └── components.css         # componentes reutilizables
├── js/
│   ├── app.js                 # aplicación principal
│   ├── api.js                 # conexión con el bot
│   ├── auth.js                # autenticación discord
│   ├── dashboard.js           # lógica del dashboard
│   └── tickets.js             # gestión de tickets
├── assets/
│   ├── images/
│   │   ├── logo.png
│   │   └── discord-logo.png
│   └── icons/
│       ├── bot.svg
│       └── settings.svg
└── .htaccess                   # configuración para hostalia
```

## 🌐 URL Final: **https://davito.es/dabot**

## 📋 Instrucciones de deployment en Hostalia:

### 1. **Preparar archivos localmente**
```bash
# crear carpeta del dashboard
mkdir dashboard-web
cd dashboard-web
# aquí van todos los archivos que te voy a crear
```

### 2. **Subir por FTP a Hostalia**
```
Servidor FTP: ftp.davito.es (o el que te dé Hostalia)
Usuario: tu_usuario_hostalia
Contraseña: tu_contraseña_hostalia

Ruta de destino: /public_html/dabot/
```

### 3. **Configurar en el bot**
```python
# en modules/web_api.py
"allowed_origins": [
    "https://davito.es",
    "https://www.davito.es"
]
```

## 🔧 Configuración específica para Hostalia:

### archivo .htaccess (para el directorio /dabot/)
```apache
RewriteEngine On

# Habilitar CORS para la API del bot
Header always set Access-Control-Allow-Origin "https://tu-bot-render.onrender.com"
Header always set Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS"
Header always set Access-Control-Allow-Headers "Content-Type, Authorization"

# Redirecciones para SPA
RewriteCond %{REQUEST_FILENAME} !-f
RewriteCond %{REQUEST_FILENAME} !-d
RewriteRule ^(.*)$ index.html [QSA,L]

# Cache para recursos estáticos
<filesMatch "\.(css|js|png|jpg|gif|ico|svg)$">
    ExpiresActive On
    ExpiresDefault "access plus 1 month"
</filesMatch>

# Comprimir archivos
<IfModule mod_deflate.c>
    AddOutputFilterByType DEFLATE text/plain
    AddOutputFilterByType DEFLATE text/html
    AddOutputFilterByType DEFLATE text/xml
    AddOutputFilterByType DEFLATE text/css
    AddOutputFilterByType DEFLATE application/xml
    AddOutputFilterByType DEFLATE application/xhtml+xml
    AddOutputFilterByType DEFLATE application/rss+xml
    AddOutputFilterByType DEFLATE application/javascript
    AddOutputFilterByType DEFLATE application/x-javascript
</IfModule>
```

## 📱 Archivos del dashboard:

### index.html (página principal)
```html
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DaBot Dashboard - davito.es</title>
    <meta name="description" content="Panel de control para DaBot v2 - Bot multipropósito de Discord">
    <link rel="stylesheet" href="css/style.css">
    <link rel="stylesheet" href="css/dashboard.css">
    <link rel="icon" type="image/png" href="assets/images/logo.png">
</head>
<body>
    <div id="app">
        <header class="header">
            <div class="container">
                <div class="nav-brand">
                    <img src="assets/images/logo.png" alt="DaBot" class="logo">
                    <h1>DaBot Dashboard</h1>
                </div>
                <nav class="nav-menu" id="nav-menu">
                    <a href="#home" class="nav-link active">Inicio</a>
                    <a href="#features" class="nav-link">Características</a>
                    <a href="#login" class="nav-link" id="login-btn">Iniciar Sesión</a>
                </nav>
            </div>
        </header>

        <main class="main">
            <section id="home" class="hero">
                <div class="container">
                    <h2>Gestiona tu servidor de Discord</h2>
                    <p>Panel completo para configurar y controlar DaBot v2</p>
                    <button class="btn btn-primary" id="get-started">Comenzar</button>
                </div>
            </section>

            <section id="features" class="features">
                <div class="container">
                    <h3>Características del Dashboard</h3>
                    <div class="features-grid">
                        <div class="feature-card">
                            <div class="feature-icon">🎫</div>
                            <h4>Gestión de Tickets</h4>
                            <p>Administra tickets de soporte directamente desde la web</p>
                        </div>
                        <div class="feature-card">
                            <div class="feature-icon">🛡️</div>
                            <h4>Moderación</h4>
                            <p>Herramientas avanzadas de moderación y configuración</p>
                        </div>
                        <div class="feature-card">
                            <div class="feature-icon">📊</div>
                            <h4>Estadísticas</h4>
                            <p>Métricas detalladas de tu servidor en tiempo real</p>
                        </div>
                        <div class="feature-card">
                            <div class="feature-icon">⚙️</div>
                            <h4>Configuración</h4>
                            <p>Personaliza todos los módulos del bot fácilmente</p>
                        </div>
                    </div>
                </div>
            </section>
        </main>

        <footer class="footer">
            <div class="container">
                <p>&copy; 2024 DaBot v2 - Desarrollado por <strong>davito</strong></p>
                <p>Hospedado en <a href="https://davito.es">davito.es</a></p>
            </div>
        </footer>
    </div>

    <script src="js/auth.js"></script>
    <script src="js/app.js"></script>
</body>
</html>
```

### js/api.js (conexión con el bot en Render)
```javascript
/**
 * Cliente API para DaBot v2
 * Conecta con el bot en Render.com
 */
class DaBotAPI {
    constructor() {
        // URL del bot en Render (cambiar por tu URL real)
        this.baseURL = 'https://tu-dabot-v2.onrender.com/api';
        this.token = localStorage.getItem('dabot_auth_token');
    }

    /**
     * Realizar petición HTTP a la API
     */
    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        
        const config = {
            ...options,
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            }
        };

        // Agregar token de autorización si existe
        if (this.token) {
            config.headers['Authorization'] = `Bearer ${this.token}`;
        }

        try {
            const response = await fetch(url, config);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('Error en API:', error);
            throw error;
        }
    }

    /**
     * Autenticación con Discord
     */
    async authenticate(discordToken) {
        const response = await this.request('/auth/discord', {
            method: 'POST',
            body: JSON.stringify({ access_token: discordToken })
        });
        
        if (response.token) {
            this.token = response.token;
            localStorage.setItem('dabot_auth_token', this.token);
        }
        
        return response;
    }

    /**
     * Obtener estado del bot
     */
    async getStatus() {
        return this.request('/status');
    }

    /**
     * Obtener servidores del usuario
     */
    async getGuilds() {
        return this.request('/guilds');
    }

    /**
     * Obtener información de un servidor
     */
    async getGuildInfo(guildId) {
        return this.request(`/guilds/${guildId}`);
    }

    /**
     * Obtener tickets
     */
    async getTickets() {
        return this.request('/tickets');
    }

    /**
     * Obtener ticket específico
     */
    async getTicket(ticketId) {
        return this.request(`/tickets/${ticketId}`);
    }

    /**
     * Cerrar ticket
     */
    async closeTicket(ticketId, reason = 'Cerrado desde dashboard') {
        return this.request(`/tickets/${ticketId}/close`, {
            method: 'POST',
            body: JSON.stringify({ reason })
        });
    }

    /**
     * Asignar ticket
     */
    async assignTicket(ticketId, staffId) {
        return this.request(`/tickets/${ticketId}/assign`, {
            method: 'POST',
            body: JSON.stringify({ staff_id: staffId })
        });
    }

    /**
     * Obtener estadísticas de economía
     */
    async getEconomyStats(guildId) {
        return this.request(`/economy/${guildId}`);
    }

    /**
     * Obtener warnings
     */
    async getWarnings(guildId) {
        return this.request(`/warnings/${guildId}`);
    }

    /**
     * Realizar acción de moderación
     */
    async moderationAction(guildId, action, data) {
        return this.request(`/moderation/${guildId}/action`, {
            method: 'POST',
            body: JSON.stringify({ action, ...data })
        });
    }

    /**
     * Cerrar sesión
     */
    logout() {
        this.token = null;
        localStorage.removeItem('dabot_auth_token');
        localStorage.removeItem('discord_user');
    }
}

// Instancia global de la API
window.daBotAPI = new DaBotAPI();
```

## 🔐 Configuración de Discord OAuth2:

### En Discord Developer Portal:
```
Application Name: DaBot v2 Dashboard
Redirect URIs: 
- https://davito.es/dabot/auth
- https://davito.es/dabot/
OAuth2 URL Generator:
- Scopes: identify, guilds
- Redirect: https://davito.es/dabot/auth
```

## 🚀 Pasos para deployment:

### 1. **Crear archivos localmente**
Te voy a crear todos los archivos necesarios

### 2. **Configurar FTP en FileZilla (o cliente FTP)**
```
Host: ftp.davito.es
Usuario: tu_usuario
Contraseña: tu_contraseña
Puerto: 21
Protocolo: FTP
```

### 3. **Subir archivos**
```
Local: /dashboard-web/*
Remoto: /public_html/dabot/
```

### 4. **Actualizar bot en Render**
```python
# En modules/web_api.py
"allowed_origins": [
    "https://davito.es",
    "https://www.davito.es"
]
```

¿Quieres que continúe creando todos los archivos HTML, CSS y JavaScript para el dashboard completo?
