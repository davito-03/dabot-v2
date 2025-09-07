"""
Script para actualizar yt-dlp y resolver problemas de YouTube
"""

import subprocess
import sys
import os

def update_ytdlp():
    """Actualizar yt-dlp a la última versión"""
    try:
        print("🔄 Actualizando yt-dlp...")
        
        # Actualizar yt-dlp
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "--upgrade", "yt-dlp"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ yt-dlp actualizado correctamente")
            print("📦 Versión instalada:")
            
            # Verificar versión
            version_result = subprocess.run([
                sys.executable, "-c", "import yt_dlp; print(yt_dlp.version.__version__)"
            ], capture_output=True, text=True)
            
            if version_result.returncode == 0:
                print(f"   Versión: {version_result.stdout.strip()}")
            
        else:
            print(f"❌ Error actualizando yt-dlp: {result.stderr}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def test_youtube_access():
    """Probar acceso a YouTube"""
    try:
        print("\n🔍 Probando acceso a YouTube...")
        
        test_code = '''
import yt_dlp
import asyncio

async def test_search():
    try:
        ydl_opts = {
            "quiet": True,
            "no_warnings": True,
            "extract_flat": True,
            "default_search": "ytsearch1:",
            "skip_download": True
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info("test music", download=False)
            if "entries" in info and info["entries"]:
                print("✅ Búsqueda de YouTube funcional")
                return True
            else:
                print("❌ No se encontraron resultados")
                return False
                
    except Exception as e:
        print(f"❌ Error en búsqueda: {e}")
        return False

asyncio.run(test_search())
'''
        
        result = subprocess.run([
            sys.executable, "-c", test_code
        ], capture_output=True, text=True)
        
        print(result.stdout)
        if result.stderr:
            print(f"Errores: {result.stderr}")
            
    except Exception as e:
        print(f"❌ Error en prueba: {e}")

if __name__ == "__main__":
    print("🛠️ SOLUCIONADOR DE PROBLEMAS DE YOUTUBE")
    print("=" * 40)
    
    update_ytdlp()
    test_youtube_access()
    
    print("\n💡 CONSEJOS ADICIONALES:")
    print("1. Si persisten los errores, reinicia el bot")
    print("2. Los delays en las búsquedas ayudan a evitar bloqueos")
    print("3. El método de respaldo funciona con extracción simplificada")
    print("4. Considera usar una VPN si el problema persiste")
