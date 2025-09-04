#!/usr/bin/env python3
"""
Test de importación de módulos
"""

import logging
import sys
import asyncio
import nextcord
from nextcord.ext import commands

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Crear bot de prueba
intents = nextcord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

async def test_modules():
    """Test individual de cada módulo"""
    
    modules_to_test = [
        ("Moderation", "modules.moderation", "Moderation"),
        ("Entertainment", "modules.entertainment", "Entertainment"),
        ("Music", "modules.music", "Music"),
        ("ScheduledTasks", "modules.scheduled_tasks", "ScheduledTasks"),
        ("HelpCommands", "modules.help_commands", "HelpCommands"),
        ("Warnings", "modules.warnings", "Warnings"),
        ("AntiSpam", "modules.anti_spam", "AntiSpam"),
        ("LoggingSystem", "modules.logging_system", "LoggingSystem"),
        ("Economy", "modules.economy", "Economy"),
        ("VoiceMaster", "modules.voicemaster", "VoiceMaster"),
        ("TicketSystem", "modules.ticket_system", "TicketSystem"),
        ("WebAPI", "modules.web_api", "WebAPI")
    ]
    
    for name, module_path, class_name in modules_to_test:
        try:
            # Importar módulo
            module = __import__(module_path, fromlist=[class_name])
            module_class = getattr(module, class_name)
            
            logger.info(f"✅ {name} importado correctamente")
            
            # Crear instancia
            instance = module_class(bot)
            
            if instance is None:
                logger.error(f"❌ {name} devuelve None!")
            else:
                logger.info(f"✅ {name} instanciado correctamente: {type(instance)}")
                
        except Exception as e:
            logger.error(f"❌ Error con {name}: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_modules())
