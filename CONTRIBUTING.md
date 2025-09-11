# 🤝 Contribuir a DaBot v2

¡Gracias por tu interés en contribuir a DaBot v2! Este documento te guiará a través del proceso de contribución.

## 📋 Tabla de Contenidos
- [🎯 Antes de Empezar](#-antes-de-empezar)
- [🛠️ Configuración del Entorno](#-configuración-del-entorno)
- [📝 Guías de Contribución](#-guías-de-contribución)
- [🐛 Reportar Bugs](#-reportar-bugs)
- [✨ Solicitar Características](#-solicitar-características)
- [🔧 Desarrollo](#-desarrollo)
- [📦 Pull Requests](#-pull-requests)
- [🎨 Estándares de Código](#-estándares-de-código)
- [📚 Documentación](#-documentación)
- [🆘 Necesitas Ayuda?](#-necesitas-ayuda)

## 🎯 Antes de Empezar

### 🤔 ¿Qué tipo de contribuciones buscamos?
- 🐛 **Correcciones de bugs**
- ✨ **Nuevas características**
- 📚 **Mejoras en documentación**
- 🔧 **Optimizaciones de rendimiento**
- 🧪 **Pruebas automatizadas**
- 🌐 **Traducciones**
- 🎨 **Mejoras de UI/UX**

### 🚫 Lo que NO aceptamos
- ❌ Cambios que rompan la compatibilidad sin justificación
- ❌ Código malicioso o con vulnerabilidades de seguridad
- ❌ Funcionalidades que violen los términos de Discord
- ❌ Contenido inapropiado o que viole las políticas

## 🛠️ Configuración del Entorno

### 📋 Requisitos Previos
```bash
# Software necesario
- Python 3.11 o superior
- Git
- Editor de código (recomendado: VS Code)
- Cuenta de GitHub
- Cuenta de Discord Developer
```

### 🚀 Configuración Inicial

1. **Fork del repositorio**
   ```bash
   # Ve a https://github.com/davito-03/dabot-v2 y haz fork
   ```

2. **Clonación local**
   ```bash
   git clone https://github.com/TU_USUARIO/dabot-v2.git
   cd dabot-v2
   ```

3. **Configuración del entorno virtual**
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate
   
   # Linux/macOS
   python3 -m venv venv
   source venv/bin/activate
   ```

4. **Instalación de dependencias**
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # Si existe
   ```

5. **Configuración del bot**
   ```bash
   # Copia el archivo de configuración
   cp .env.example .env
   
   # Edita .env con tus tokens y configuraciones
   notepad .env  # Windows
   nano .env     # Linux
   ```

6. **Configuración de pre-commit** (opcional pero recomendado)
   ```bash
   pip install pre-commit
   pre-commit install
   ```

## 📝 Guías de Contribución

### 🔍 Explorar el Proyecto
Antes de contribuir, familiarízate con:
- 📖 **README.md** - Información general del proyecto
- 📝 **CHANGELOG.md** - Historial de cambios
- 🗂️ **Estructura del proyecto** - Ver sección "Arquitectura"
- 🧪 **Tests existentes** - En el directorio `tests/`

### 🗂️ Estructura del Proyecto
```
dabot-v2/
├── 🤖 bot.py                 # Archivo principal del bot
├── 📋 requirements.txt       # Dependencias de Python
├── 🔧 .env.example          # Plantilla de configuración
├── 📚 README.md             # Documentación principal
├── 📝 CHANGELOG.md          # Historial de cambios
├── 🤝 CONTRIBUTING.md       # Esta guía
├── 📜 LICENSE               # Licencia MIT
├── 🐳 Dockerfile            # Containerización
├── ☁️ render.yaml           # Deploy en Render
├── 📦 modules/              # Módulos del bot
│   ├── 🎣 entertainment.py  # Sistema de pesca y juegos
│   ├── 🔨 moderation.py     # Sistema de moderación
│   ├── 🎵 music.py          # Sistema de música
│   └── ⏰ scheduled_tasks.py # Tareas programadas
├── 🗄️ data/                 # Bases de datos
├── 📊 logs/                 # Archivos de log
├── 🧪 tests/                # Pruebas automatizadas
└── 📖 docs/                 # Documentación adicional
```

## 🐛 Reportar Bugs

### 📝 Antes de Reportar
1. 🔍 **Busca** si el bug ya fue reportado
2. 🧪 **Reproduce** el error en la última versión
3. 📊 **Recopila** información del sistema
4. 📸 **Documenta** con capturas/logs

### 🎯 Plantilla de Bug Report
```markdown
## 🐛 Descripción del Bug
Descripción clara y concisa del problema.

## 🔄 Pasos para Reproducir
1. Ve a '...'
2. Ejecuta comando '...'
3. Observa el error

## ✅ Comportamiento Esperado
Qué debería suceder normalmente.

## 📸 Capturas/Logs
```logs
Pega aquí los logs relevantes
```

## 🖥️ Información del Sistema
- OS: [ej. Windows 11]
- Python: [ej. 3.11.4]
- Bot Version: [ej. v2.0.0]
- Discord.py Version: [ej. 2.3.2]

## 📋 Información Adicional
Cualquier otro detalle relevante.
```

## ✨ Solicitar Características

### 💡 Antes de Solicitar
1. 🔍 **Verifica** que no exista ya
2. 🤔 **Considera** si encaja con el proyecto
3. 💭 **Piensa** en la implementación
4. 📊 **Evalúa** el impacto en usuarios

### 🎯 Plantilla de Feature Request
```markdown
## ✨ Descripción de la Característica
Descripción clara de qué quieres que se agregue.

## 🎯 Problema que Soluciona
¿Qué problema específico resuelve esta característica?

## 💡 Solución Propuesta
Descripción clara de cómo implementarías la solución.

## 🔄 Alternativas Consideradas
Otras soluciones que consideraste.

## 📊 Impacto Esperado
¿Cómo beneficiaría esto a los usuarios?

## 🛠️ Implementación Técnica (opcional)
Ideas sobre cómo podría implementarse técnicamente.
```

## 🔧 Desarrollo

### 🌿 Flujo de Trabajo con Git

1. **Crear rama para la característica**
   ```bash
   git checkout -b feature/nueva-caracteristica
   # o
   git checkout -b fix/correccion-bug
   ```

2. **Desarrollo iterativo**
   ```bash
   # Hacer cambios
   git add .
   git commit -m "feat: agregar nueva característica"
   
   # Testear los cambios
   python -m pytest tests/
   python bot.py --test
   ```

3. **Mantener actualizada la rama**
   ```bash
   git fetch origin
   git rebase origin/main
   ```

### 🧪 Testing

#### 🔍 Ejecutar Pruebas
```bash
# Todas las pruebas
python -m pytest

# Pruebas específicas
python -m pytest tests/test_entertainment.py

# Con cobertura
python -m pytest --cov=modules tests/
```

#### ✍️ Escribir Pruebas
```python
# tests/test_nueva_funcionalidad.py
import pytest
from modules.entertainment import nueva_funcion

def test_nueva_funcion():
    """Prueba que nueva_funcion funcione correctamente."""
    resultado = nueva_funcion("input_test")
    assert resultado == "output_esperado"

@pytest.mark.asyncio
async def test_comando_async():
    """Prueba comando asíncrono."""
    # Tu código de prueba aquí
    pass
```

### 📊 Logging y Debugging

```python
import logging

# Configurar logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Usar en tu código
logger.debug("Información de debug")
logger.info("Información general")
logger.warning("Advertencia")
logger.error("Error ocurrido")
```

## 📦 Pull Requests

### ✅ Checklist antes del PR

- [ ] 🧪 **Tests** - Todas las pruebas pasan
- [ ] 📝 **Documentación** - Actualizada si es necesario
- [ ] 🎨 **Estilo** - Código sigue los estándares
- [ ] 🔍 **Lint** - Sin errores de linting
- [ ] 📋 **Changelog** - Entrada agregada si es necesario
- [ ] 🔄 **Rebase** - Rama actualizada con main
- [ ] 📸 **Screenshots** - Si hay cambios visuales

### 📝 Plantilla de Pull Request

```markdown
## 📋 Descripción
Descripción breve de los cambios realizados.

## 🎯 Tipo de Cambio
- [ ] 🐛 Bug fix
- [ ] ✨ Nueva característica
- [ ] 💥 Breaking change
- [ ] 📚 Documentación
- [ ] 🔧 Refactoring
- [ ] 🧪 Tests

## 🧪 Testing
- [ ] He probado mis cambios localmente
- [ ] He agregado tests para mi código
- [ ] Todas las pruebas existentes pasan

## 📸 Screenshots (si aplica)
Agrega capturas de pantalla para cambios visuales.

## 📋 Notas Adicionales
Información adicional para los revisores.
```

### 🔍 Proceso de Revisión

1. 🤖 **Checks Automáticos** - CI/CD debe pasar
2. 👥 **Revisión de Código** - Al menos 1 aprobación
3. 🧪 **Testing Manual** - Si es necesario
4. ✅ **Merge** - Squash and merge preferido

## 🎨 Estándares de Código

### 🐍 Estilo Python (PEP 8)

```python
# ✅ Bueno
def funcion_con_nombre_descriptivo(parametro_uno: str, parametro_dos: int) -> bool:
    """
    Función que hace algo específico.
    
    Args:
        parametro_uno: Descripción del parámetro
        parametro_dos: Descripción del parámetro
        
    Returns:
        bool: True si todo está bien
    """
    if parametro_uno and parametro_dos > 0:
        return True
    return False

# ❌ Malo
def func(p1,p2):
    if p1 and p2>0:return True
    return False
```

### 📝 Convenciones de Naming

```python
# Variables y funciones: snake_case
usuario_actual = "Juan"
def obtener_datos_usuario():
    pass

# Clases: PascalCase
class GestorBaseDatos:
    pass

# Constantes: UPPER_SNAKE_CASE
MAX_INTENTOS = 3
API_URL = "https://api.ejemplo.com"

# Módulos: lowercase
import modulo_utilidades
```

### 💬 Mensajes de Commit

Seguimos [Conventional Commits](https://www.conventionalcommits.org/):

```bash
# Formato
<tipo>[scope opcional]: <descripción>

# Ejemplos
feat(pesca): agregar nueva especie de pez legendario
fix(music): corregir error al pausar música
docs(readme): actualizar guía de instalación
refactor(db): optimizar consultas de base de datos
test(entertainment): agregar pruebas para sistema de pesca
chore(deps): actualizar dependencias de seguridad
```

#### 🏷️ Tipos de Commit
- **feat**: Nueva característica
- **fix**: Corrección de bug
- **docs**: Cambios en documentación
- **style**: Formateo, punto y coma faltante, etc.
- **refactor**: Refactoring de código
- **test**: Agregar o corregir tests
- **chore**: Mantenimiento (deps, build, etc.)
- **perf**: Mejoras de rendimiento
- **ci**: Cambios en CI/CD

### 🔧 Herramientas de Desarrollo

#### 📐 Linting y Formateo
```bash
# Black (formateo automático)
pip install black
black .

# Flake8 (linting)
pip install flake8
flake8 modules/ bot.py

# isort (organizar imports)
pip install isort
isort .

# mypy (type checking)
pip install mypy
mypy modules/ bot.py
```

#### ⚙️ Configuración VS Code (recomendada)

```json
// .vscode/settings.json
{
    "python.formatting.provider": "black",
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.linting.mypyEnabled": true,
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
        "source.organizeImports": true
    }
}
```

## 📚 Documentación

### 📝 Docstrings

```python
def pescar_pez(usuario_id: int, canal_id: int) -> dict:
    """
    Simula la pesca de un pez para un usuario.
    
    Esta función maneja toda la lógica de pesca incluyendo:
    - Verificación de cooldown
    - Cálculo de probabilidades
    - Actualización de estadísticas
    - Gestión de inventario
    
    Args:
        usuario_id (int): ID del usuario de Discord
        canal_id (int): ID del canal donde se ejecuta
        
    Returns:
        dict: Diccionario con información del pez pescado:
            - 'especie': Nombre de la especie
            - 'rareza': Nivel de rareza (1-4)
            - 'valor': Valor en monedas
            - 'peso': Peso del pez en kg
            
    Raises:
        CooldownError: Si el usuario está en cooldown
        DatabaseError: Si hay problema con la base de datos
        
    Examples:
        >>> resultado = pescar_pez(123456789, 987654321)
        >>> print(resultado['especie'])
        'Dorado'
    """
    pass
```

### 📖 Documentación de Comandos

```python
@bot.slash_command(
    name="pescar",
    description="🎣 Intenta pescar un pez en el lago virtual"
)
async def cmd_pescar(
    interaction: nextcord.Interaction,
    lugar: str = SlashOption(
        description="🌊 Lugar donde pescar",
        choices=["lago", "rio", "mar", "oceano"],
        default="lago"
    )
):
    """
    Comando de pesca que permite a los usuarios pescar diferentes especies.
    
    El comando incluye:
    - Sistema de cooldown (5 minutos)
    - 32 especies diferentes
    - 4 niveles de rareza
    - Economía integrada
    """
    pass
```

## 🆘 Necesitas Ayuda?

### 💬 Canales de Comunicación

- 🐛 **Issues de GitHub**: Para bugs y características
- 💬 **Discord**: [Servidor de soporte](https://discord.gg/tu-servidor)
- 📧 **Email**: contacto@dabot.com
- 📚 **Wiki**: [Wiki del proyecto](https://github.com/davito-03/dabot-v2/wiki)

### 🤝 Mentores y Revisores

- **@davito-03** - Desarrollador principal
- **@contributor1** - Especialista en música
- **@contributor2** - Especialista en moderación

### 📚 Recursos Útiles

#### 🔗 Enlaces Importantes
- 📖 [Discord.py Documentation](https://discordpy.readthedocs.io/)
- 🎮 [Discord Developer Portal](https://discord.com/developers/docs/)
- 🐍 [Python Style Guide (PEP 8)](https://pep8.org/)
- 🧪 [Pytest Documentation](https://docs.pytest.org/)
- 📝 [Conventional Commits](https://www.conventionalcommits.org/)

#### 🛠️ Herramientas de Desarrollo
- 💻 [Visual Studio Code](https://code.visualstudio.com/)
- 🐙 [GitHub Desktop](https://desktop.github.com/)
- 🐳 [Docker Desktop](https://www.docker.com/products/docker-desktop)
- 📊 [SQLite Browser](https://sqlitebrowser.org/)

### 🎓 Guías de Aprendizaje

#### 🐍 Para Desarrolladores Python Nuevos
1. 📚 [Python.org Tutorial](https://docs.python.org/3/tutorial/)
2. 🎮 [Discord Bot Tutorial](https://realpython.com/how-to-make-a-discord-bot-python/)
3. 🧪 [Testing with Pytest](https://realpython.com/pytest-python-testing/)

#### 🤖 Para Desarrollo de Bots Discord
1. 📖 [Discord.py Guía de Inicio](https://discordpy.readthedocs.io/en/stable/quickstart.html)
2. 🔧 [Nextcord Documentation](https://docs.nextcord.dev/)
3. 🎯 [Discord Bot Best Practices](https://github.com/meew0/discord-bot-best-practices)

---

## 🎉 ¡Gracias por Contribuir!

Tu contribución hace que DaBot v2 sea mejor para toda la comunidad. Cada línea de código, reporte de bug, sugerencia o mejora en documentación es valiosa.

### 🏆 Reconocimientos

Los contribuidores serán reconocidos en:
- 📜 **CONTRIBUTORS.md** - Lista de todos los contribuidores
- 🎖️ **README.md** - Contribuidores destacados
- 🏅 **Release Notes** - Contribuidores de cada versión
- 🌟 **Discord** - Rol especial de contribuidor

### 💝 Código de Conducta

Nos comprometemos a mantener un ambiente acogedor y libre de acoso. Por favor:

- 🤝 **Sé respetuoso** con todos los participantes
- 💬 **Usa lenguaje inclusivo** y profesional
- 🎯 **Enfócate en el código**, no en las personas
- 🤔 **Acepta críticas constructivas** con gracia
- 🚫 **No toleres acoso** ni comportamiento inapropiado

¡Esperamos trabajar contigo para hacer de DaBot v2 el mejor bot de Discord! 🚀
