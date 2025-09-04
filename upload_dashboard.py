#!/usr/bin/env python3
"""
Script para subir dashboard a Hostalia via FTP
Para uso en davito.es/dabot
"""

import ftplib
import os
from pathlib import Path

def upload_dashboard():
    """Subir dashboard a Hostalia FTP"""
    
    # Configuración FTP (CAMBIAR CON TUS DATOS)
    FTP_HOST = "ftp.hostalia.com"  # O tu host FTP específico
    FTP_USER = "tu_usuario_ftp"    # Tu usuario FTP
    FTP_PASS = "tu_password_ftp"   # Tu contraseña FTP
    REMOTE_DIR = "/public_html/dabot"  # Carpeta destino en el servidor
    
    # Directorio local del dashboard
    LOCAL_DIR = "dashboard-web"
    
    try:
        print("🔗 Conectando a FTP...")
        ftp = ftplib.FTP(FTP_HOST)
        ftp.login(FTP_USER, FTP_PASS)
        
        # Crear directorio remoto si no existe
        try:
            ftp.mkd(REMOTE_DIR)
        except:
            pass  # El directorio ya existe
        
        ftp.cwd(REMOTE_DIR)
        
        print(f"📁 Subiendo archivos de {LOCAL_DIR}...")
        
        # Subir todos los archivos
        for root, dirs, files in os.walk(LOCAL_DIR):
            # Crear directorios en el servidor
            for directory in dirs:
                local_dir = os.path.join(root, directory)
                remote_dir = local_dir.replace(LOCAL_DIR, "").replace("\\", "/").lstrip("/")
                
                if remote_dir:
                    try:
                        ftp.mkd(remote_dir)
                        print(f"📂 Directorio creado: {remote_dir}")
                    except:
                        pass  # Directorio ya existe
            
            # Subir archivos
            for file in files:
                local_file = os.path.join(root, file)
                remote_file = local_file.replace(LOCAL_DIR, "").replace("\\", "/").lstrip("/")
                
                with open(local_file, 'rb') as f:
                    ftp.storbinary(f"STOR {remote_file}", f)
                print(f"📄 Subido: {remote_file}")
        
        ftp.quit()
        print("✅ Dashboard subido exitosamente!")
        print("🌐 Disponible en: https://davito.es/dabot")
        
    except Exception as e:
        print(f"❌ Error subiendo dashboard: {e}")
        print("🔧 Verifica tus credenciales FTP y conexión")

if __name__ == "__main__":
    print("🚀 SUBIDA DE DASHBOARD A HOSTALIA")
    print("=" * 40)
    
    # Verificar que existe el directorio
    if not os.path.exists("dashboard-web"):
        print("❌ No se encuentra el directorio dashboard-web")
        exit(1)
    
    # Instrucciones
    print("📋 ANTES DE EJECUTAR:")
    print("1. Edita este archivo con tus credenciales FTP")
    print("2. Asegúrate de tener acceso FTP a tu hosting")
    print("3. Verifica la carpeta destino (/public_html/dabot)")
    print()
    
    respuesta = input("¿Continuar con la subida? (s/n): ")
    if respuesta.lower() == 's':
        upload_dashboard()
    else:
        print("❌ Subida cancelada")
