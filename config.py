"""
configuración de deployment para render.com
por davito
"""

import os
from dotenv import load_dotenv

# cargar variables de entorno
load_dotenv()

# configuración de la base de datos
DATABASE_CONFIG = {
    'postgresql': {
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': int(os.getenv('DB_PORT', 5432)),
        'database': os.getenv('DB_NAME', 'dabot'),
        'user': os.getenv('DB_USER', 'dabot'),
        'password': os.getenv('DB_PASSWORD', '')
    }
}

# configuración del bot
BOT_CONFIG = {
    'token': os.getenv('DISCORD_TOKEN'),
    'prefix': '!',
    'description': 'dabot v2 - bot multipropósito por davito',
    'web_api_port': int(os.getenv('PORT', 8080)),
    'web_api_host': '0.0.0.0',
    'jwt_secret': os.getenv('JWT_SECRET', 'clave_super_secreta_davito_2024'),
    'web_api_token': os.getenv('WEB_API_TOKEN', 'token_api_davito_2024')
}

# configuración web
WEB_CONFIG = {
    'dashboard_url': os.getenv('DASHBOARD_URL', 'https://dashboard.davito.es'),
    'allowed_origins': [
        'https://dashboard.davito.es',
        'https://davito.es',
        'http://localhost:3000'  # para desarrollo
    ],
    'cors_enabled': True
}

# configuración de logs
LOGGING_CONFIG = {
    'level': os.getenv('LOG_LEVEL', 'INFO'),
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'file': 'logs/bot.log'
}

# configuración de render
RENDER_CONFIG = {
    'port': int(os.getenv('PORT', 8080)),
    'host': '0.0.0.0',
    'workers': int(os.getenv('WEB_CONCURRENCY', 1))
}
