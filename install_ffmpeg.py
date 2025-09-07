"""
Instalador automático de FFmpeg para Windows
"""

import os
import sys
import subprocess
import requests
import zipfile
import shutil
from pathlib import Path

def check_ffmpeg():
    """Verificar si FFmpeg está instalado"""
    try:
        result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ FFmpeg ya está instalado")
            return True
    except FileNotFoundError:
        pass
    
    print("❌ FFmpeg no encontrado")
    return False

def download_ffmpeg():
    """Descargar FFmpeg para Windows"""
    print("📥 Descargando FFmpeg...")
    
    # URL de descarga de FFmpeg precompilado para Windows
    url = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
    
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        with open("ffmpeg.zip", "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print("✅ FFmpeg descargado")
        return True
        
    except Exception as e:
        print(f"❌ Error descargando FFmpeg: {e}")
        return False

def install_ffmpeg():
    """Instalar FFmpeg en el sistema"""
    print("🔧 Instalando FFmpeg...")
    
    try:
        # Crear directorio para FFmpeg
        ffmpeg_dir = Path("C:/ffmpeg")
        ffmpeg_dir.mkdir(exist_ok=True)
        
        # Extraer archivo
        with zipfile.ZipFile("ffmpeg.zip", 'r') as zip_ref:
            zip_ref.extractall("temp_ffmpeg")
        
        # Encontrar el directorio extraído
        temp_dirs = list(Path("temp_ffmpeg").glob("ffmpeg-*"))
        if not temp_dirs:
            print("❌ Error: No se encontró el directorio de FFmpeg")
            return False
        
        source_dir = temp_dirs[0]
        
        # Copiar archivos
        if (source_dir / "bin").exists():
            shutil.copytree(source_dir / "bin", ffmpeg_dir / "bin", dirs_exist_ok=True)
            print("✅ FFmpeg instalado en C:/ffmpeg/bin")
        else:
            print("❌ Error: No se encontró el directorio bin")
            return False
        
        # Limpiar archivos temporales
        os.remove("ffmpeg.zip")
        shutil.rmtree("temp_ffmpeg")
        
        return True
        
    except Exception as e:
        print(f"❌ Error instalando FFmpeg: {e}")
        return False

def add_to_path():
    """Agregar FFmpeg al PATH del sistema"""
    print("🔧 Configurando PATH...")
    
    ffmpeg_path = "C:\\ffmpeg\\bin"
    
    try:
        # Obtener PATH actual
        current_path = os.environ.get('PATH', '')
        
        if ffmpeg_path not in current_path:
            # Agregar al PATH de la sesión actual
            os.environ['PATH'] = f"{ffmpeg_path};{current_path}"
            print(f"✅ FFmpeg agregado al PATH de la sesión")
            
            # Mostrar instrucciones para agregar permanentemente
            print("\n💡 IMPORTANTE: Para hacer esto permanente:")
            print("1. Presiona Win + R, escribe 'sysdm.cpl' y presiona Enter")
            print("2. Ve a la pestaña 'Avanzado' → 'Variables de entorno'")
            print("3. En 'Variables del sistema', busca 'Path' y haz clic en 'Editar'")
            print("4. Haz clic en 'Nuevo' y agrega: C:\\ffmpeg\\bin")
            print("5. Haz clic en 'Aceptar' en todas las ventanas")
            
        return True
        
    except Exception as e:
        print(f"❌ Error configurando PATH: {e}")
        return False

def verify_installation():
    """Verificar que la instalación fue exitosa"""
    print("\n🔍 Verificando instalación...")
    
    try:
        result = subprocess.run(['C:/ffmpeg/bin/ffmpeg.exe', '-version'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ FFmpeg instalado correctamente")
            version_line = result.stdout.split('\n')[0]
            print(f"📦 {version_line}")
            return True
        else:
            print("❌ Error verificando FFmpeg")
            return False
            
    except Exception as e:
        print(f"❌ Error en verificación: {e}")
        return False

def main():
    print("🎵 INSTALADOR DE FFMPEG PARA DABOT V2")
    print("=" * 40)
    
    # Verificar si ya está instalado
    if check_ffmpeg():
        print("FFmpeg ya está disponible en el sistema")
        return
    
    print("FFmpeg es necesario para reproducir música de YouTube")
    respuesta = input("¿Deseas instalarlo automáticamente? (s/n): ")
    
    if respuesta.lower() in ['s', 'si', 'y', 'yes']:
        # Instalar FFmpeg
        if download_ffmpeg():
            if install_ffmpeg():
                add_to_path()
                if verify_installation():
                    print("\n🚀 ¡INSTALACIÓN COMPLETADA!")
                    print("Ahora puedes usar los comandos de música del bot")
                    print("\nReinicia el bot para aplicar los cambios")
                else:
                    print("\n❌ La instalación falló en la verificación")
            else:
                print("\n❌ La instalación falló")
        else:
            print("\n❌ La descarga falló")
    else:
        print("\n💡 INSTALACIÓN MANUAL:")
        print("1. Ve a https://ffmpeg.org/download.html")
        print("2. Descarga FFmpeg para Windows")
        print("3. Extrae el archivo a C:\\ffmpeg")
        print("4. Agrega C:\\ffmpeg\\bin al PATH del sistema")

if __name__ == "__main__":
    main()
