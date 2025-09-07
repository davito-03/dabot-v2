"""
Instalador rápido de FFmpeg usando múltiples métodos
"""

import subprocess
import sys
import os

def check_ffmpeg():
    """Verificar si FFmpeg está disponible"""
    try:
        result = subprocess.run(['ffmpeg', '-version'], capture_output=True)
        return result.returncode == 0
    except FileNotFoundError:
        return False

def install_with_chocolatey():
    """Instalar usando Chocolatey"""
    try:
        print("🍫 Intentando instalar con Chocolatey...")
        result = subprocess.run(['choco', 'install', 'ffmpeg', '-y'], 
                              capture_output=True, text=True)
        return result.returncode == 0
    except FileNotFoundError:
        print("❌ Chocolatey no está instalado")
        return False

def install_with_winget():
    """Instalar usando Winget"""
    try:
        print("📦 Intentando instalar con Winget...")
        result = subprocess.run(['winget', 'install', 'ffmpeg'], 
                              capture_output=True, text=True)
        return result.returncode == 0
    except FileNotFoundError:
        print("❌ Winget no está disponible")
        return False

def install_with_scoop():
    """Instalar usando Scoop"""
    try:
        print("🪣 Intentando instalar con Scoop...")
        result = subprocess.run(['scoop', 'install', 'ffmpeg'], 
                              capture_output=True, text=True)
        return result.returncode == 0
    except FileNotFoundError:
        print("❌ Scoop no está instalado")
        return False

def main():
    print("🎵 INSTALADOR RÁPIDO DE FFMPEG")
    print("=" * 30)
    
    if check_ffmpeg():
        print("✅ FFmpeg ya está instalado")
        return
    
    print("❌ FFmpeg no encontrado. Intentando instalación automática...")
    
    # Intentar diferentes métodos
    methods = [
        ("Chocolatey", install_with_chocolatey),
        ("Winget", install_with_winget),
        ("Scoop", install_with_scoop)
    ]
    
    for name, method in methods:
        if method():
            print(f"✅ FFmpeg instalado con {name}")
            print("🔄 Reinicia la terminal y el bot")
            return
    
    print("\n❌ No se pudo instalar automáticamente")
    print("\n📋 INSTRUCCIONES MANUALES:")
    print("1. Ejecuta: python install_ffmpeg.py")
    print("2. O descarga desde: https://ffmpeg.org/download.html")
    print("3. Extrae a C:\\ffmpeg y agrega C:\\ffmpeg\\bin al PATH")

if __name__ == "__main__":
    main()
