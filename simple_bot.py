#!/usr/bin/env python3
"""
Bot básico simplificado para testing
"""

import asyncio
import logging
import os
import time
from datetime import datetime, time as time_obj
from dotenv import load_dotenv
import nextcord
from nextcord.ext import commands, tasks

# Cargar variables de entorno
load_dotenv()

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SimpleBot(commands.Bot):
    """Bot simplificado para testing"""
    
    def __init__(self):
        # Configurar intents
        intents = nextcord.Intents.default()
        intents.message_content = True
        intents.guilds = True
        intents.voice_states = True
        intents.members = True
        
        super().__init__(
            command_prefix='!',
            intents=intents,
            help_command=None,
            case_insensitive=True
        )
    
    async def on_ready(self):
        """Evento cuando el bot se conecta"""
        logger.info(f'{self.user} se ha conectado!')
        logger.info(f'Servidores: {len(self.guilds)}')
        
        # Sincronizar slash commands
        try:
            synced = await self.sync_all_application_commands()
            logger.info(f"Slash commands sincronizados: {len(synced) if synced else 'OK'}")
        except Exception as e:
            logger.error(f"Error sincronizando: {e}")

async def main():
    """Función principal"""
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        logger.error("Token no encontrado")
        return
    
    bot = SimpleBot()
    
    # Solo cargar módulos esenciales y que sabemos que funcionan
    essential_modules = [
        'music',
        'entertainment',
        'appeals',
        'config_commands'
    ]
    
    for module_name in essential_modules:
        try:
            logger.info(f"Cargando {module_name}...")
            
            module = __import__(f'modules.{module_name}', fromlist=['setup'])
            
            if hasattr(module, 'setup'):
                cog = module.setup(bot)
                if cog:
                    await bot.add_cog(cog)
                    logger.info(f"✅ {module_name} cargado")
                else:
                    logger.error(f"❌ {module_name} devolvió None")
            else:
                logger.error(f"❌ {module_name} sin función setup")
                
        except Exception as e:
            logger.error(f"❌ Error cargando {module_name}: {e}")
    
    logger.info("=== BOT INICIADO ===")
    
    try:
        await bot.start(token)
    except Exception as e:
        logger.error(f"Error ejecutando bot: {e}")
    finally:
        await bot.close()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot detenido")
    except Exception as e:
        logger.error(f"Error crítico: {e}")
