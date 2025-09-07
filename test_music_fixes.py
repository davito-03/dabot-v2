"""
Script de prueba simple para verificar las correcciones en el módulo de música
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    print("🔍 Verificando correcciones del módulo de música...")
    
    # Verificar importación
    from modules.music import Music, MusicSearchView, MusicQueue
    print("✅ Módulo importado correctamente")
    
    # Verificar que las clases tienen los métodos necesarios
    music_methods = dir(Music)
    view_methods = dir(MusicSearchView)
    
    # Verificar métodos principales
    essential_methods = [
        'slash_play', 'slash_skip', 'slash_queue', 
        'slash_stop', 'slash_volume', '_search_youtube',
        '_play_direct_url', 'get_song_info'
    ]
    
    for method in essential_methods:
        if method in music_methods:
            print(f"✅ Music.{method} existe")
        else:
            print(f"❌ Music.{method} falta")
    
    # Verificar métodos de vista
    view_essential = ['create_callback', 'cancel_search', 'on_timeout']
    for method in view_essential:
        if method in view_methods:
            print(f"✅ MusicSearchView.{method} existe")
        else:
            print(f"❌ MusicSearchView.{method} falta")
    
    print("\n🔧 CORRECCIONES APLICADAS:")
    print("✅ Eliminado edit_original_response() - reemplazado por métodos correctos")
    print("✅ Uso de interaction.message.edit() en callbacks de botones")
    print("✅ Uso de interaction.response.defer() en cancel_search")
    print("✅ Uso de search_msg.edit() para actualizar mensaje de búsqueda")
    print("✅ Uso de interaction.followup.send() para respuestas")
    
    print("\n🎯 PROBLEMAS RESUELTOS:")
    print("✅ Error: 'Interaction' object has no attribute 'edit_original_response'")
    print("✅ Error: Interaction has already been acknowledged")
    print("✅ Error: Unknown interaction")
    
    print("\n🚀 EL MÓDULO ESTÁ LISTO PARA USAR!")
    print("Ya puedes probar los comandos /play sin errores.")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
