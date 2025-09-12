"""
Script de verificación completa de APIs y comandos de DaBot v2
Verifica todas las APIs externas y funcionalidades
"""

import asyncio
import aiohttp
import json
import sys
from datetime import datetime

class APITester:
    def __init__(self):
        self.results = []
        self.total_tests = 0
        self.passed_tests = 0
        
    async def test_api(self, name, url, expected_status=200, timeout=10):
        """Probar una API específica"""
        self.total_tests += 1
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=timeout)) as session:
                async with session.get(url) as response:
                    status = response.status
                    if status == expected_status:
                        print(f"✅ {name}: OK ({status})")
                        self.passed_tests += 1
                        self.results.append({"name": name, "status": "✅ PASS", "code": status})
                        return True
                    else:
                        print(f"❌ {name}: Failed ({status})")
                        self.results.append({"name": name, "status": "❌ FAIL", "code": status})
                        return False
        except Exception as e:
            print(f"❌ {name}: Error - {str(e)}")
            self.results.append({"name": name, "status": "❌ ERROR", "error": str(e)})
            return False
    
    async def run_all_tests(self):
        """Ejecutar todas las pruebas de APIs"""
        print("🚀 INICIANDO VERIFICACIÓN COMPLETA DE APIs\n")
        
        # APIs de animales
        print("🐾 ANIMAL APIs:")
        await self.test_api("Duck API", "https://random-d.uk/api/random")
        await self.test_api("Cat API", "https://api.thecatapi.com/v1/images/search")
        await self.test_api("Dog API", "https://dog.ceo/api/breeds/image/random")
        await self.test_api("Fox API", "https://randomfox.ca/floof/")
        
        print("\n🎭 INTERACTION APIs:")
        await self.test_api("Waifu Pics SFW", "https://api.waifu.pics/sfw/hug")
        await self.test_api("Waifu Pics Kiss", "https://api.waifu.pics/sfw/kiss")
        await self.test_api("Waifu Pics Pat", "https://api.waifu.pics/sfw/pat")
        
        print("\n🔞 NSFW APIs:")
        await self.test_api("Waifu NSFW", "https://api.waifu.pics/nsfw/waifu")
        await self.test_api("Neko NSFW", "https://api.waifu.pics/nsfw/neko")
        
        print("\n🎵 MUSIC APIs:")
        # YouTube no se puede probar directamente, pero podemos verificar conectividad
        await self.test_api("YouTube (connectivity)", "https://www.youtube.com", expected_status=200)
        
        print("\n🌐 UTILITY APIs:")
        await self.test_api("Discord API", "https://discord.com/api/v10/gateway")
        
        # Reportar resultados
        print(f"\n{'='*50}")
        print(f"📊 RESULTADOS FINALES:")
        print(f"✅ Tests pasados: {self.passed_tests}/{self.total_tests}")
        print(f"❌ Tests fallidos: {self.total_tests - self.passed_tests}/{self.total_tests}")
        print(f"📈 Tasa de éxito: {(self.passed_tests/self.total_tests)*100:.1f}%")
        
        if self.passed_tests == self.total_tests:
            print("🎉 TODAS LAS APIs FUNCIONAN CORRECTAMENTE")
        else:
            print("⚠️  ALGUNAS APIs TIENEN PROBLEMAS")
            
        return self.passed_tests == self.total_tests

async def verify_discord_token():
    """Verificar formato del token de Discord"""
    print("\n🔐 VERIFICANDO TOKEN DE DISCORD:")
    
    try:
        import os
        from dotenv import load_dotenv
        load_dotenv()
        
        token = os.getenv('DISCORD_TOKEN')
        if not token:
            print("❌ Token no encontrado en .env")
            return False
            
        # Verificar formato básico del token
        parts = token.split('.')
        if len(parts) != 3:
            print("❌ Formato de token inválido")
            return False
            
        print(f"✅ Token encontrado: {parts[0]}.{'*'*len(parts[1])}.{'*'*len(parts[2])}")
        print("ℹ️  Para verificar validez, ejecutar bot localmente")
        return True
        
    except Exception as e:
        print(f"❌ Error verificando token: {e}")
        return False

def verify_modules():
    """Verificar que todos los módulos estén presentes"""
    print("\n📦 VERIFICANDO MÓDULOS:")
    
    required_modules = [
        "modules.entertainment",
        "modules.moderation", 
        "modules.music",
        "modules.scheduled_tasks",
        "modules.keep_alive"
    ]
    
    all_ok = True
    for module in required_modules:
        try:
            __import__(module)
            print(f"✅ {module}")
        except ImportError as e:
            print(f"❌ {module}: {e}")
            all_ok = False
            
    return all_ok

async def main():
    """Función principal de verificación"""
    print(f"🔍 VERIFICACIÓN COMPLETA DABOT V2")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*50)
    
    # Verificar módulos
    modules_ok = verify_modules()
    
    # Verificar token
    token_ok = await verify_discord_token()
    
    # Verificar APIs
    tester = APITester()
    apis_ok = await tester.run_all_tests()
    
    # Resumen final
    print(f"\n{'='*50}")
    print("🎯 RESUMEN GENERAL:")
    print(f"📦 Módulos: {'✅ OK' if modules_ok else '❌ FAIL'}")
    print(f"🔐 Token: {'✅ OK' if token_ok else '❌ FAIL'}")
    print(f"🌐 APIs: {'✅ OK' if apis_ok else '❌ FAIL'}")
    
    if modules_ok and token_ok and apis_ok:
        print("\n🎉 ¡TODO ESTÁ FUNCIONANDO CORRECTAMENTE!")
        print("🚀 El bot debería funcionar sin problemas")
    else:
        print("\n⚠️  HAY PROBLEMAS QUE RESOLVER")
        if not token_ok:
            print("🔧 Revisar configuración del token de Discord")
        if not apis_ok:
            print("🔧 Algunas APIs externas pueden estar caídas")
            
    return modules_ok and token_ok and apis_ok

if __name__ == "__main__":
    try:
        result = asyncio.run(main())
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n⚠️  Verificación interrumpida por usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error durante verificación: {e}")
        sys.exit(1)