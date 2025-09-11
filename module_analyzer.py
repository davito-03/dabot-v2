"""
Análisis y Auditoría de Módulos de DaBot v2
Identificación de redundancias y optimizaciones
"""

import os
import ast
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ModuleAnalyzer:
    def __init__(self):
        self.modules_dir = "modules"
        self.modules_info = {}
        self.redundancies = []
        self.consolidation_suggestions = []
        
    def analyze_modules(self):
        """Analizar todos los módulos del bot"""
        print("🔍 Analizando módulos del bot...\n")
        
        for filename in os.listdir(self.modules_dir):
            if filename.endswith('.py') and not filename.startswith('__'):
                self.analyze_module(filename)
        
        self.identify_redundancies()
        self.suggest_consolidations()
        self.print_report()
    
    def analyze_module(self, filename):
        """Analizar un módulo específico"""
        filepath = os.path.join(self.modules_dir, filename)
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Analizar AST para extraer información
            tree = ast.parse(content)
            
            module_info = {
                'filename': filename,
                'classes': [],
                'functions': [],
                'imports': [],
                'slash_commands': [],
                'size': len(content),
                'lines': len(content.split('\n'))
            }
            
            # Extraer información del AST
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    module_info['classes'].append(node.name)
                elif isinstance(node, ast.FunctionDef):
                    module_info['functions'].append(node.name)
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        module_info['imports'].append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        module_info['imports'].append(node.module)
            
            # Buscar comandos slash
            if '@nextcord.slash_command' in content or '@slash_command' in content:
                # Contar comandos slash aproximadamente
                module_info['slash_commands'] = content.count('@nextcord.slash_command') + content.count('@slash_command')
            
            self.modules_info[filename] = module_info
            
        except Exception as e:
            logger.error(f"Error analizando {filename}: {e}")
    
    def identify_redundancies(self):
        """Identificar módulos redundantes o similares"""
        print("🔍 Identificando redundancias...\n")
        
        # Buscar módulos con nombres similares
        module_names = list(self.modules_info.keys())
        
        for i, module1 in enumerate(module_names):
            for module2 in module_names[i+1:]:
                # Verificar similitudes en nombres
                name1 = module1.replace('.py', '').replace('_', '').lower()
                name2 = module2.replace('.py', '').replace('_', '').lower()
                
                if name1 in name2 or name2 in name1:
                    self.redundancies.append((module1, module2, "Nombres similares"))
                
                # Verificar clases similares
                classes1 = set(self.modules_info[module1]['classes'])
                classes2 = set(self.modules_info[module2]['classes'])
                
                if classes1.intersection(classes2):
                    self.redundancies.append((module1, module2, "Clases duplicadas"))
    
    def suggest_consolidations(self):
        """Sugerir consolidaciones de módulos"""
        print("💡 Generando sugerencias de consolidación...\n")
        
        # Agrupar por funcionalidad
        groups = {
            'CORE': [],           # Funcionalidades principales
            'MODERATION': [],     # Moderación y administración
            'ENTERTAINMENT': [],  # Entretenimiento y diversión
            'ECONOMY': [],        # Sistema económico
            'UTILITY': [],        # Utilidades y herramientas
            'SETUP': [],          # Configuración y setup
            'MUSIC': [],          # Sistema de música
            'LEVELS': [],         # Sistema de niveles
            'MISC': []            # Misceláneos
        }
        
        for filename, info in self.modules_info.items():
            name_lower = filename.lower()
            
            # Clasificar por nombre y contenido
            if any(word in name_lower for word in ['mod', 'admin', 'warn', 'ban', 'kick']):
                groups['MODERATION'].append(filename)
            elif any(word in name_lower for word in ['entertainment', 'fun', 'meme', 'game', 'joke']):
                groups['ENTERTAINMENT'].append(filename)
            elif any(word in name_lower for word in ['economy', 'money', 'coin', 'shop']):
                groups['ECONOMY'].append(filename)
            elif any(word in name_lower for word in ['music', 'audio', 'sound']):
                groups['MUSIC'].append(filename)
            elif any(word in name_lower for word in ['level', 'xp', 'experience']):
                groups['LEVELS'].append(filename)
            elif any(word in name_lower for word in ['setup', 'config', 'install']):
                groups['SETUP'].append(filename)
            elif any(word in name_lower for word in ['bot', 'core', 'main']):
                groups['CORE'].append(filename)
            elif any(word in name_lower for word in ['util', 'helper', 'tool']):
                groups['UTILITY'].append(filename)
            else:
                groups['MISC'].append(filename)
        
        # Generar sugerencias
        for group_name, modules in groups.items():
            if len(modules) > 3:  # Si hay más de 3 módulos en un grupo
                self.consolidation_suggestions.append({
                    'group': group_name,
                    'modules': modules,
                    'suggestion': f"Consolidar {len(modules)} módulos en un módulo unificado"
                })
    
    def print_report(self):
        """Imprimir reporte completo"""
        print("=" * 60)
        print("📊 REPORTE DE ANÁLISIS DE MÓDULOS")
        print("=" * 60)
        
        print(f"\n📁 Total de módulos analizados: {len(self.modules_info)}")
        
        # Estadísticas generales
        total_lines = sum(info['lines'] for info in self.modules_info.values())
        total_classes = sum(len(info['classes']) for info in self.modules_info.values())
        total_commands = sum(info['slash_commands'] for info in self.modules_info.values())
        
        print(f"📝 Total de líneas de código: {total_lines}")
        print(f"🏗️ Total de clases: {total_classes}")
        print(f"⚡ Total de comandos slash: {total_commands}")
        
        # Módulos más grandes
        print(f"\n📈 TOP 10 MÓDULOS MÁS GRANDES:")
        sorted_modules = sorted(self.modules_info.items(), key=lambda x: x[1]['lines'], reverse=True)
        for i, (filename, info) in enumerate(sorted_modules[:10]):
            print(f"   {i+1:2d}. {filename:<30} - {info['lines']:4d} líneas - {info['slash_commands']:2d} comandos")
        
        # Redundancias encontradas
        print(f"\n⚠️ REDUNDANCIAS ENCONTRADAS:")
        if self.redundancies:
            for module1, module2, reason in self.redundancies:
                print(f"   • {module1} ↔ {module2} - {reason}")
        else:
            print("   ✅ No se encontraron redundancias obvias")
        
        # Sugerencias de consolidación
        print(f"\n💡 SUGERENCIAS DE CONSOLIDACIÓN:")
        for suggestion in self.consolidation_suggestions:
            print(f"\n   🔶 {suggestion['group']}:")
            print(f"      {suggestion['suggestion']}")
            for module in suggestion['modules']:
                info = self.modules_info[module]
                print(f"      • {module:<25} - {info['lines']:3d} líneas - {info['slash_commands']:2d} cmds")
        
        print(f"\n" + "=" * 60)

if __name__ == "__main__":
    analyzer = ModuleAnalyzer()
    analyzer.analyze_modules()
