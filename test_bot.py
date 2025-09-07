import nextcord
from nextcord.ext import commands
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = commands.Bot(command_prefix='!', intents=nextcord.Intents.all())

@bot.event
async def on_ready():
    print(f"✅ Bot conectado como {bot.user}")
    
    # Probar cargar un módulo nuevo
    try:
        import modules.auto_rules
        modules.auto_rules.setup(bot)
        print("✅ auto_rules cargado")
    except Exception as e:
        print(f"❌ Error con auto_rules: {e}")
    
    # Probar cargar otro módulo
    try:
        import modules.advanced_levels  
        modules.advanced_levels.setup(bot)
        print("✅ advanced_levels cargado")
    except Exception as e:
        print(f"❌ Error con advanced_levels: {e}")

if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    
    # Cargar variables de entorno
    load_dotenv()
    TOKEN = os.getenv('DISCORD_TOKEN')
    
    if not TOKEN:
        print("❌ Error: No se encontró DISCORD_TOKEN en el archivo .env")
        print("📝 Crea un archivo .env con: DISCORD_TOKEN=tu_token_aquí")
        input("Presiona Enter para salir...")
        exit(1)
    
    try:
        bot.run(TOKEN)
    except Exception as e:
        print(f"Error: {e}")