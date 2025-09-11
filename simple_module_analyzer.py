"""
Análisis simplificado de módulos
"""

import os
import re

def analyze_modules():
    modules_dir = "modules"
    modules = []
    
    print("📋 ANÁLISIS DE MÓDULOS DE DABOT V2")
    print("=" * 50)
    
    for filename in os.listdir(modules_dir):
        if filename.endswith('.py') and not filename.startswith('__'):
            filepath = os.path.join(modules_dir, filename)
            
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Contar líneas
                lines = len(content.split('\n'))
                
                # Contar comandos slash
                slash_commands = len(re.findall(r'@nextcord\.slash_command|@slash_command', content))
                
                # Buscar clases
                classes = re.findall(r'class\s+(\w+)', content)
                
                # Categorizar por nombre
                category = categorize_module(filename)
                
                modules.append({
                    'filename': filename,
                    'lines': lines,
                    'commands': slash_commands,
                    'classes': len(classes),
                    'category': category,
                    'size_kb': len(content) / 1024
                })
                
            except Exception as e:
                print(f"❌ Error analizando {filename}: {e}")
    
    # Ordenar por líneas
    modules.sort(key=lambda x: x['lines'], reverse=True)
    
    # Mostrar estadísticas
    print(f"\n📊 ESTADÍSTICAS GENERALES:")
    print(f"   • Total módulos: {len(modules)}")
    print(f"   • Total líneas: {sum(m['lines'] for m in modules)}")
    print(f"   • Total comandos: {sum(m['commands'] for m in modules)}")
    print(f"   • Tamaño total: {sum(m['size_kb'] for m in modules):.1f} KB")
    
    # Top 15 módulos más grandes
    print(f"\n📈 TOP 15 MÓDULOS MÁS GRANDES:")
    for i, module in enumerate(modules[:15]):
        print(f"   {i+1:2d}. {module['filename']:<35} {module['lines']:4d} líneas {module['commands']:2d} cmds [{module['category']}]")
    
    # Agrupar por categorías
    categories = {}
    for module in modules:
        cat = module['category']
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(module)
    
    print(f"\n🗂️ MÓDULOS POR CATEGORÍA:")
    for category, mods in categories.items():
        print(f"\n   📁 {category} ({len(mods)} módulos):")
        for mod in mods:
            print(f"      • {mod['filename']:<30} {mod['lines']:3d} líneas")
    
    # Identificar redundancias obvias
    print(f"\n⚠️ POSIBLES REDUNDANCIAS:")
    redundancies = find_redundancies(modules)
    for redundancy in redundancies:
        print(f"   • {redundancy}")
    
    print(f"\n💡 SUGERENCIAS DE CONSOLIDACIÓN:")
    print_consolidation_suggestions(categories)

def categorize_module(filename):
    name = filename.lower()
    
    if any(word in name for word in ['mod', 'admin', 'warn', 'ban', 'appeal']):
        return "MODERATION"
    elif any(word in name for word in ['entertainment', 'fun', 'meme', 'game', 'animal']):
        return "ENTERTAINMENT"
    elif any(word in name for word in ['economy', 'money', 'shop']):
        return "ECONOMY"
    elif any(word in name for word in ['music', 'audio']):
        return "MUSIC"
    elif any(word in name for word in ['level', 'xp']):
        return "LEVELS"
    elif any(word in name for word in ['setup', 'config', 'server']):
        return "SETUP"
    elif any(word in name for word in ['ticket', 'support']):
        return "TICKETS"
    elif any(word in name for word in ['log', 'audit']):
        return "LOGGING"
    elif any(word in name for word in ['nsfw', 'adult']):
        return "NSFW"
    elif any(word in name for word in ['help', 'command']):
        return "HELP"
    elif any(word in name for word in ['voice', 'vc']):
        return "VOICE"
    else:
        return "UTILITY"

def find_redundancies(modules):
    redundancies = []
    
    # Buscar módulos con nombres similares
    names = [m['filename'] for m in modules]
    
    for i, name1 in enumerate(names):
        for name2 in names[i+1:]:
            base1 = name1.replace('.py', '').replace('_new', '').replace('_old', '')
            base2 = name2.replace('.py', '').replace('_new', '').replace('_old', '')
            
            if base1 == base2:
                redundancies.append(f"{name1} y {name2} (mismo nombre base)")
            elif base1 in base2 or base2 in base1:
                redundancies.append(f"{name1} y {name2} (nombres similares)")
    
    return redundancies

def print_consolidation_suggestions(categories):
    suggestions = {
        "MODERATION": "Consolidar en 'moderation_system.py' - incluir bans, warns, appeals, roles",
        "ENTERTAINMENT": "Consolidar en 'entertainment_hub.py' - incluir memes, juegos, diversión",
        "MUSIC": "Mantener separado si hay múltiples versiones, elegir la mejor",
        "LEVELS": "Consolidar en 'level_system.py' - unificar todos los sistemas de niveles",
        "SETUP": "Consolidar en 'server_setup.py' - incluir todas las configuraciones",
        "LOGGING": "Consolidar en 'logging_system.py' - unificar logs y auditoría",
        "HELP": "Consolidar en 'help_system.py' - unificar toda la documentación"
    }
    
    for category, mods in categories.items():
        if len(mods) > 2:  # Solo sugerir si hay más de 2 módulos
            if category in suggestions:
                print(f"   🔧 {category}: {suggestions[category]}")
            else:
                print(f"   🔧 {category}: Consolidar {len(mods)} módulos en uno")

if __name__ == "__main__":
    analyze_modules()
