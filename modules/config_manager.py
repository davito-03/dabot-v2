import yaml
import os
import json
from typing import Dict, Any, List, Optional
import logging

# Importar el sistema de base de datos
try:
    from .server_manager import ServerConfigDB
    DB_AVAILABLE = True
except ImportError:
    DB_AVAILABLE = False
    logging.warning("Base de datos de servidor no disponible")

class ConfigManager:
    """
    Gestor de configuración para DaBot v2
    Carga y gestiona todas las configuraciones desde config.yaml y base de datos
    """
    
    def __init__(self, config_path: str = "config.yaml"):
        self.config_path = config_path
        self.config = {}
        self.defaults = {}
        
        # Inicializar base de datos de servidores si está disponible
        if DB_AVAILABLE:
            try:
                self.server_db = ServerConfigDB()
            except Exception as e:
                logging.error(f"Error inicializando base de datos: {e}")
                self.server_db = None
        else:
            self.server_db = None
        
        self.load_config()
        
    def load_config(self):
        """Carga la configuración desde el archivo YAML"""
        try:
            if not os.path.exists(self.config_path):
                self.create_default_config()
            
            with open(self.config_path, 'r', encoding='utf-8') as file:
                self.config = yaml.safe_load(file) or {}
                
            # Validar configuración crítica
            self._validate_critical_config()
            
            logging.info(f"✅ Configuración cargada desde {self.config_path}")
            
        except Exception as e:
            logging.error(f"❌ Error cargando configuración: {e}")
            self.config = self._get_emergency_config()
    
    def get(self, path: str, default=None, guild_id: str = None) -> Any:
        """
        Obtiene un valor de configuración usando notación de puntos
        Si se proporciona guild_id, busca primero en la base de datos del servidor
        Ejemplo: config.get('moderation.antispam.enabled', False, guild_id="123456789")
        """
        # Si hay guild_id y base de datos disponible, buscar configuración específica del servidor
        if guild_id and self.server_db:
            try:
                # Convertir path a formato de configuración de servidor
                server_setting = self._convert_path_to_server_setting(path)
                if server_setting:
                    server_value = self.server_db.get_setting(guild_id, server_setting)
                    if server_value is not None:
                        return server_value
            except Exception as e:
                logging.debug(f"Error obteniendo configuración de servidor: {e}")
        
        # Buscar en configuración global
        keys = path.split('.')
        value = self.config
        
        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default
    
    def _convert_path_to_server_setting(self, path: str) -> Optional[str]:
        """Convierte un path de configuración a formato de configuración de servidor"""
        conversions = {
            'moderation.enabled': 'moderation_enabled',
            'music.enabled': 'music_enabled',
            'fun.nsfw.enabled': 'nsfw_enabled',
            'welcome.enabled': 'welcome_enabled',
            'logging.enabled': 'logging_enabled',
            'general.prefix': 'prefix',
            'general.language': 'language',
            'moderation.anti_spam.enabled': 'automod_anti_spam',
            'moderation.anti_links.enabled': 'automod_anti_links',
            'moderation.anti_caps.enabled': 'automod_anti_caps',
            'moderation.bad_words.enabled': 'automod_bad_words'
        }
        return conversions.get(path)
    
    def set_server_config(self, guild_id: str, setting: str, value: Any) -> bool:
        """Establece una configuración específica para un servidor"""
        if not self.server_db:
            return False
        
        try:
            self.server_db.set_setting(guild_id, setting, str(value))
            return True
        except Exception as e:
            logging.error(f"Error estableciendo configuración de servidor: {e}")
            return False
    
    def get_server_channel(self, guild_id: str, channel_type: str) -> Optional[str]:
        """Obtiene el ID de un canal específico del servidor"""
        if not self.server_db:
            return None
        
        try:
            return self.server_db.get_channel(guild_id, channel_type)
        except Exception as e:
            logging.debug(f"Error obteniendo canal de servidor: {e}")
            return None
    
    def get_server_role(self, guild_id: str, role_type: str) -> Optional[str]:
        """Obtiene el ID de un rol específico del servidor"""
        if not self.server_db:
            return None
        
        try:
            return self.server_db.get_role(guild_id, role_type)
        except Exception as e:
            logging.debug(f"Error obteniendo rol de servidor: {e}")
            return None
    
    def set(self, path: str, value: Any):
        """
        Establece un valor de configuración usando notación de puntos
        """
        keys = path.split('.')
        config = self.config
        
        # Navegar hasta el penúltimo nivel
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]
        
        # Establecer el valor final
        config[keys[-1]] = value
    
    def save_config(self):
        """Guarda la configuración actual al archivo YAML"""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as file:
                yaml.dump(self.config, file, default_flow_style=False, 
                         allow_unicode=True, indent=2)
            logging.info("✅ Configuración guardada")
        except Exception as e:
            logging.error(f"❌ Error guardando configuración: {e}")
    
    def reload_config(self):
        """Recarga la configuración desde el archivo"""
        self.load_config()
    
    # === MÉTODOS DE ACCESO RÁPIDO ===
    
    def get_permission_level(self, user_id: str, role_ids: List[str] = None) -> int:
        """Obtiene el nivel de permisos de un usuario"""
        role_ids = role_ids or []
        
        # Verificar permisos de usuario específicos
        user_level = self.get(f'permissions.users.{user_id}', 0)
        
        # Verificar permisos de roles
        role_level = 0
        for role_id in role_ids:
            level = self.get(f'permissions.roles.{role_id}', 0)
            role_level = max(role_level, level)
        
        return max(user_level, role_level)
    
    def can_use_command(self, command: str, user_level: int) -> bool:
        """Verifica si un usuario puede usar un comando"""
        required_level = self.get(f'permissions.commands.{command}', 0)
        return user_level >= required_level
    
    def is_ignored_user(self, user_id: str, context: str = "logging") -> bool:
        """Verifica si un usuario está en la lista de ignorados"""
        ignored_list = self.get(f'{context}.ignored.users', [])
        return user_id in ignored_list
    
    def is_ignored_channel(self, channel_id: str, context: str = "logging") -> bool:
        """Verifica si un canal está en la lista de ignorados"""
        ignored_list = self.get(f'{context}.ignored.channels', [])
        return channel_id in ignored_list
    
    def is_ignored_role(self, role_ids: List[str], context: str = "logging") -> bool:
        """Verifica si algún rol está en la lista de ignorados"""
        ignored_list = self.get(f'{context}.ignored.roles', [])
        return any(role_id in ignored_list for role_id in role_ids)
    
    def get_automod_config(self) -> Dict[str, Any]:
        """Obtiene la configuración completa de automod"""
        return self.get('moderation', {})
    
    def get_levels_config(self) -> Dict[str, Any]:
        """Obtiene la configuración completa de niveles"""
        return self.get('levels', {})
    
    def get_music_config(self) -> Dict[str, Any]:
        """Obtiene la configuración completa de música"""
        return self.get('music', {})
    
    def get_welcome_config(self) -> Dict[str, Any]:
        """Obtiene la configuración completa de bienvenidas"""
        return self.get('welcome', {})
    
    def get_economy_config(self) -> Dict[str, Any]:
        """Obtiene la configuración completa de economía"""
        return self.get('economy', {})
    
    def get_tickets_config(self) -> Dict[str, Any]:
        """Obtiene la configuración completa de tickets"""
        return self.get('tickets', {})
    
    def get_filters_config(self) -> Dict[str, Any]:
        """Obtiene la configuración completa de filtros"""
        return self.get('filters', {})
    
    def get_voicemaster_config(self) -> Dict[str, Any]:
        """Obtiene la configuración completa de voicemaster"""
        return self.get('voicemaster', {})
    
    def get_appeals_config(self) -> Dict[str, Any]:
        """Obtiene la configuración completa de apelaciones"""
        return self.get('moderation.appeals', {})
    
    def get_logging_config(self) -> Dict[str, Any]:
        """Obtiene la configuración completa de logging"""
        return self.get('logging', {})
    
    def get_web_config(self) -> Dict[str, Any]:
        """Obtiene la configuración completa del dashboard web"""
        return self.get('web', {})
    
    # === MÉTODOS DE UTILIDAD ===
    
    def is_module_enabled(self, module: str) -> bool:
        """Verifica si un módulo está habilitado"""
        return self.get(f'{module}.enabled', False)
    
    def get_log_channel(self, log_type: str) -> Optional[str]:
        """Obtiene el canal de logs para un tipo específico"""
        return self.get(f'logging.channels.{log_type}')
    
    def get_currency_symbol(self) -> str:
        """Obtiene el símbolo de la moneda"""
        return self.get('economy.currency_symbol', '🪙')
    
    def get_currency_name(self) -> str:
        """Obtiene el nombre de la moneda"""
        return self.get('economy.currency_name', 'DaCoins')
    
    def get_prefix(self) -> str:
        """Obtiene el prefijo del bot"""
        return self.get('general.prefix', '!')
    
    def get_language(self) -> str:
        """Obtiene el idioma configurado"""
        return self.get('general.language', 'es-ES')
    
    def _validate_critical_config(self):
        """Valida configuraciones críticas"""
        critical_configs = [
            'general.language',
            'general.prefix',
            'permissions.users',
            'permissions.roles'
        ]
        
        for config_path in critical_configs:
            if self.get(config_path) is None:
                logging.warning(f"⚠️ Configuración crítica faltante: {config_path}")
    
    def _get_emergency_config(self) -> Dict[str, Any]:
        """Configuración de emergencia si falla la carga"""
        return {
            'general': {
                'language': 'es-ES',
                'prefix': '!',
                'status': 'online'
            },
            'permissions': {
                'users': {},
                'roles': {},
                'commands': {}
            }
        }
    
    def create_default_config(self):
        """Crea un archivo de configuración por defecto"""
        # Aquí iría el contenido por defecto si no existe el archivo
        logging.info("⚠️ Archivo de configuración no encontrado. Usando valores por defecto.")

# Instancia global del gestor de configuración
config = ConfigManager()

# Funciones de conveniencia para acceso rápido
def get_config(path: str, default=None):
    """Función rápida para obtener configuración"""
    return config.get(path, default)

def set_config(path: str, value):
    """Función rápida para establecer configuración"""
    return config.set(path, value)

def save_config():
    """Función rápida para guardar configuración"""
    return config.save_config()

def is_module_enabled(module: str) -> bool:
    """Función rápida para verificar si un módulo está habilitado"""
    return config.is_module_enabled(module)

def get_permission_level(user_id: str, role_ids: List[str] = None) -> int:
    """Función rápida para obtener nivel de permisos"""
    return config.get_permission_level(user_id, role_ids)

def can_use_command(command: str, user_level: int) -> bool:
    """Función rápida para verificar permisos de comando"""
    return config.can_use_command(command, user_level)

def reload_config():
    """Función rápida para recargar configuración"""
    config.reload_config()

# Decorador para comandos que requieren configuración específica
def require_module(module_name: str):
    """Decorador que verifica si un módulo está habilitado"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            if not is_module_enabled(module_name):
                return None  # O lanzar excepción
            return func(*args, **kwargs)
        return wrapper
    return decorator

# Decorador para verificar permisos
def require_permission(command_name: str):
    """Decorador que verifica permisos para comandos"""
    def decorator(func):
        async def wrapper(interaction, *args, **kwargs):
            try:
                user_roles = [str(role.id) for role in interaction.user.roles]
                user_level = get_permission_level(str(interaction.user.id), user_roles)
                
                if not can_use_command(command_name, user_level):
                    await interaction.response.send_message(
                        "❌ No tienes permisos para usar este comando.", 
                        ephemeral=True
                    )
                    return
                
                return await func(interaction, *args, **kwargs)
            except Exception as e:
                # Si hay error en permisos, permitir el comando (modo fallback)
                return await func(interaction, *args, **kwargs)
        return wrapper
    return decorator
