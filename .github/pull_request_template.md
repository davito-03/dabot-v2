---
name: 🚀 Pull Request Template
about: Plantilla estándar para pull requests
---

## 📋 Descripción
**Descripción breve y clara de los cambios realizados**

Explica en 1-2 párrafos qué hace este PR y por qué es necesario.

## 🎯 Tipo de Cambio
**¿Qué tipo de cambio es este PR?**
- [ ] 🐛 **Bug fix** (cambio que soluciona un issue)
- [ ] ✨ **Nueva característica** (cambio que agrega funcionalidad)
- [ ] 💥 **Breaking change** (cambio que rompe compatibilidad)
- [ ] 🔧 **Refactoring** (cambio que no arregla bugs ni agrega features)
- [ ] 📚 **Documentación** (cambios solo en documentación)
- [ ] 🧪 **Tests** (agregar o corregir tests)
- [ ] 🎨 **Style** (formateo, espacios, etc.)
- [ ] ⚡ **Performance** (mejoras de rendimiento)
- [ ] 🏗️ **Chore** (mantenimiento, dependencias, etc.)

## 🔗 Issues Relacionados
**Conecta este PR con issues relevantes**
- Fixes #(numero_de_issue)
- Closes #(numero_de_issue)
- Relacionado con #(numero_de_issue)

## 🧪 Testing
**¿Cómo has probado tus cambios?**

### ✅ Tests Realizados
- [ ] He probado mis cambios localmente
- [ ] He ejecutado la suite de tests existente
- [ ] He agregado nuevos tests para mi código
- [ ] He probado en diferentes entornos (Windows/Linux)
- [ ] He probado con diferentes configuraciones

### 🔍 Casos de Prueba
```bash
# Comandos específicos probados
/comando_nuevo parámetro1 parámetro2
/comando_modificado --opción

# Escenarios probados
- Usuario sin permisos
- Usuario con permisos admin
- Servidor pequeño vs grande
- etc.
```

### 📊 Resultados de Tests
```
Pega aquí los resultados de pytest o los tests que hayas ejecutado
```

## 📸 Screenshots/Demos
**Si hay cambios visuales o nuevas funcionalidades:**

### 🖼️ Antes
<!-- Screenshot del comportamiento anterior -->

### 🖼️ Después  
<!-- Screenshot del nuevo comportamiento -->

### 🎥 Demo (opcional)
<!-- GIF o video demostrando la nueva funcionalidad -->

## 📝 Cambios Realizados
**Lista detallada de cambios:**

### 📁 Archivos Modificados
- `modules/entertainment.py` - Agregado sistema de logros
- `bot.py` - Corregido manejo de errores en comandos
- `requirements.txt` - Actualizada versión de nextcord
- `README.md` - Documentada nueva característica

### 🆕 Archivos Nuevos
- `modules/achievements.py` - Sistema de logros
- `tests/test_achievements.py` - Tests para logros
- `data/achievements.json` - Configuración de logros

### 🗑️ Archivos Eliminados
- `modules/deprecated_feature.py` - Funcionalidad obsoleta

## 🔧 Detalles Técnicos
**Información técnica relevante:**

### 🛠️ Implementación
- **Patrón de diseño usado**: [Factory, Observer, etc.]
- **Base de datos**: [Cambios en esquema, nuevas tablas]
- **APIs externas**: [Nuevas integraciones]
- **Performance**: [Optimizaciones realizadas]

### ⚠️ Breaking Changes
**Si hay cambios que rompen compatibilidad:**
- Comando `/viejo_comando` eliminado → usar `/nuevo_comando`
- Configuración `config.old_setting` deprecada → usar `config.new_setting`
- API endpoint `/api/v1/old` removido → usar `/api/v2/new`

### 🔄 Migración
**Pasos necesarios para actualizar:**
```bash
# Comandos para migrar datos
python migrate.py --from-version=1.9 --to-version=2.0
```

## 📋 Checklist
**Verifica antes de enviar el PR:**

### 🧪 Testing
- [ ] Todos los tests existentes pasan
- [ ] He agregado tests para nuevas funcionalidades
- [ ] He probado edge cases y errores
- [ ] No hay warnings en el código

### 📚 Documentación
- [ ] He actualizado el README si es necesario
- [ ] He actualizado el CHANGELOG.md
- [ ] He agregado docstrings a funciones nuevas
- [ ] He actualizado comentarios relevantes

### 🎨 Código
- [ ] Mi código sigue los estándares del proyecto
- [ ] He ejecutado linting (flake8, black)
- [ ] No hay código comentado o debug prints
- [ ] He optimizado imports con isort

### 🔒 Seguridad
- [ ] No he expuesto tokens o información sensible
- [ ] He validado inputs de usuarios
- [ ] He considerado aspectos de seguridad
- [ ] No hay vulnerabilidades conocidas

### 🐛 Compatibilidad
- [ ] Funciona en Python 3.11+
- [ ] Compatible con Windows y Linux
- [ ] No rompe funcionalidades existentes
- [ ] Mantiene backward compatibility (si aplica)

## 🚀 Deploy/Release
**Información sobre deployment:**

### 📦 Dependencias Nuevas
```txt
# Nuevas dependencias agregadas a requirements.txt
nueva_libreria==1.2.3
otra_dependencia>=2.0.0
```

### ⚙️ Variables de Entorno
```bash
# Nuevas variables necesarias en .env
NUEVA_API_KEY=tu_api_key_aqui
FEATURE_ENABLED=true
```

### 🗄️ Base de Datos
- [ ] Requiere migración de base de datos
- [ ] Backup recomendado antes de aplicar
- [ ] Scripts de migración incluidos

### ☁️ Infraestructura
- [ ] Requiere cambios en configuración de servidor
- [ ] Nuevos puertos/servicios necesarios
- [ ] Cambios en Docker/render.yaml

## 🎯 Plan de Rollback
**En caso de problemas después del deploy:**
```bash
# Comandos para revertir cambios
git revert <commit-hash>
python rollback.py --to-version=previous
```

## 📊 Métricas/Performance
**Impacto en rendimiento (si aplica):**
- **Memoria**: +/- X MB
- **CPU**: +/- X% de uso
- **Tiempo de respuesta**: +/- X ms
- **Tamaño de base de datos**: +/- X MB

## 🤝 Revisores Sugeridos
**Personas que deberían revisar este PR:**
- @davito-03 (owner)
- @reviewer1 (experto en música)
- @reviewer2 (experto en moderación)

**Razón específica para cada revisor:**
- Cambios en arquitectura core
- Modificaciones en sistema de música
- Nuevas funcionalidades de moderación

## 💬 Notas Adicionales
**Información adicional para los revisores:**

### 🤔 Decisiones de Diseño
- **Por qué elegí X sobre Y**: [Explicación]
- **Trade-offs considerados**: [Lista]
- **Alternativas evaluadas**: [Opciones descartadas]

### ⚠️ Áreas de Atención
- **Revisar especialmente**: [Secciones específicas]
- **Posibles problemas**: [Conocidos pero aceptables]
- **Feedback buscado**: [Tipo de feedback que necesitas]

### 🔮 Trabajo Futuro
- **TODOs pendientes**: [Para futuros PRs]
- **Mejoras planeadas**: [Optimizaciones futuras]
- **Features relacionadas**: [Que vendrán después]

---

**¿Primera vez contribuyendo?** ¡Gracias! 🎉 
Lee nuestra [guía de contribución](CONTRIBUTING.md) si tienes dudas.

**¿Necesitas ayuda?** 
Menciona a @davito-03 o comenta en este PR.

**Recuerda:** Los PRs se revisan generalmente en 24-48 horas. ¡Gracias por tu paciencia! ⏰
