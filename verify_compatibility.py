#!/usr/bin/env python3
"""
Script de verificación de compatibilidad para DaBot v2
Verifica que todas las dependencias sean compatibles con Python 3.12
"""

import sys
import subprocess
import pkg_resources
from packaging import version

def check_python_version():
    """Verifica la versión de Python"""
    print("🐍 Verificando versión de Python...")
    current_version = sys.version_info
    print(f"   Versión actual: {current_version.major}.{current_version.minor}.{current_version.micro}")
    
    if current_version < (3, 11):
        print("❌ Python 3.11+ es requerido")
        return False
    elif current_version >= (3, 12):
        print("✅ Python 3.12+ - Completamente compatible")
        return True
    else:
        print("⚠️  Python 3.11 - Compatible pero se recomienda 3.12+")
        return True

def check_dependencies():
    """Verifica que las dependencias estén instaladas correctamente"""
    print("\n📦 Verificando dependencias...")
    
    required_packages = [
        "nextcord>=2.6.0",
        "yt-dlp>=2024.8.6",
        "PyNaCl>=1.5.0",
        "python-dotenv>=1.0.1",
        "aiohttp>=3.9.0",
        "requests>=2.31.0",
        "pillow>=10.0.1"
    ]
    
    all_good = True
    for package in required_packages:
        try:
            pkg_resources.require(package)
            print(f"   ✅ {package}")
        except pkg_resources.DistributionNotFound:
            print(f"   ❌ {package} - No instalado")
            all_good = False
        except pkg_resources.VersionConflict as e:
            print(f"   ⚠️  {package} - Conflicto de versión: {e}")
            all_good = False
    
    return all_good

def check_nextcord_compatibility():
    """Verifica compatibilidad específica de nextcord"""
    print("\n🤖 Verificando compatibilidad de nextcord...")
    
    try:
        import nextcord
        print(f"   ✅ nextcord {nextcord.__version__} instalado")
        
        # Verificar que la versión sea compatible
        if version.parse(nextcord.__version__) >= version.parse("2.6.0"):
            print("   ✅ Versión compatible con Python 3.11+")
            return True
        else:
            print("   ❌ Versión muy antigua, actualizar a 2.6.0+")
            return False
            
    except ImportError:
        print("   ❌ nextcord no está instalado")
        return False

def check_render_compatibility():
    """Verifica archivos necesarios para Render"""
    print("\n☁️ Verificando configuración para Render...")
    
    files_to_check = [
        "requirements-render.txt",
        "runtime.txt", 
        "render.yaml",
        "Dockerfile"
    ]
    
    all_good = True
    for file in files_to_check:
        try:
            with open(file, 'r') as f:
                print(f"   ✅ {file} encontrado")
        except FileNotFoundError:
            print(f"   ❌ {file} no encontrado")
            all_good = False
    
    return all_good

def main():
    """Función principal"""
    print("🔍 VERIFICACIÓN DE COMPATIBILIDAD - DaBot v2")
    print("=" * 50)
    
    checks = [
        ("Python Version", check_python_version),
        ("Dependencies", check_dependencies), 
        ("Nextcord", check_nextcord_compatibility),
        ("Render Config", check_render_compatibility)
    ]
    
    all_passed = True
    for name, check_func in checks:
        try:
            if not check_func():
                all_passed = False
        except Exception as e:
            print(f"   ❌ Error en {name}: {e}")
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 ¡TODAS LAS VERIFICACIONES PASARON!")
        print("✅ El bot está listo para deploy en Render")
    else:
        print("❌ ALGUNAS VERIFICACIONES FALLARON")
        print("🔧 Revisa los errores arriba y corrígelos antes del deploy")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
