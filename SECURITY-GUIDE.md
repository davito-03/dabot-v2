# 🔒 GUÍA DE SEGURIDAD: Proteger tu Repositorio GitHub

## 🚨 VERIFICACIÓN ACTUAL
- **Todos los commits** muestran "Davito" como autor
- **Repositorio**: davito-03/dabot-v2 
- **Acceso**: Privado (recomendado)

## 🛡️ MEDIDAS DE SEGURIDAD INMEDIATAS

### 1. **Verificar Colaboradores**
```bash
# En GitHub.com:
Repositorio → Settings → Manage access → Collaborators
```

### 2. **Revocar Tokens de Acceso**
```bash
GitHub → Settings → Developer settings → Personal access tokens
# Revocar todos los tokens sospechosos
```

### 3. **Cambiar Credenciales**
```bash
# Si usas HTTPS, cambiar contraseña GitHub
# Si usas SSH, regenerar keys
```

## 🔐 CONFIGURACIÓN BRANCH PROTECTION

### **En GitHub.com:**
1. **Repositorio → Settings → Branches**
2. **Add rule para 'main':**
   - ✅ Require pull request reviews
   - ✅ Dismiss stale reviews
   - ✅ Require review from CODEOWNERS
   - ✅ Restrict pushes to matching branches
   - ✅ Require status checks to pass

### **Crear archivo CODEOWNERS:**
```bash
# En raíz del proyecto
# Solo tú puedes aprobar cambios
* @davito-03
```

## 🔍 AUDITORÍA DE SEGURIDAD

### **Verificar Git Config Local:**
```bash
git config user.name
git config user.email
# Debe mostrar TUS datos
```

### **Verificar Historial Completo:**
```bash
git log --all --graph --pretty=format:"%h - %an (%ae) - %ad - %s" --date=short
```

### **Revisar Archivos Sensibles:**
```bash
# Verificar que no haya tokens expuestos
grep -r "token\|key\|secret" . --exclude-dir=.git --exclude-dir=__pycache__
```

## 🚀 COMANDOS DE LIMPIEZA

### **1. Forzar Push de tu Versión:**
```bash
git push --force-with-lease origin main
```

### **2. Limpiar Commits No Deseados (PELIGROSO):**
```bash
# Solo si encuentras commits maliciosos
git rebase -i HEAD~10  # Para últimos 10 commits
# Marcar como 'drop' los commits no deseados
```

### **3. Reescribir Historial (EXTREMO):**
```bash
# Si hay muchos commits comprometidos
git filter-branch --force --author-filter '
if [ "$GIT_COMMITTER_EMAIL" != "tu-email@gmail.com" ];
then
    skip_commit "$@";
fi' HEAD
```

## 📋 CHECKLIST DE SEGURIDAD

### **GitHub Settings:**
- [ ] Repositorio es PRIVADO
- [ ] Solo TÚ tienes acceso de escritura
- [ ] Branch protection activada
- [ ] CODEOWNERS configurado
- [ ] 2FA activado en tu cuenta

### **Local Git:**
- [ ] user.name correcto
- [ ] user.email correcto  
- [ ] SSH keys seguras
- [ ] .env en .gitignore

### **Código:**
- [ ] Sin tokens hardcodeados
- [ ] Variables sensibles en .env
- [ ] .env NO en el repositorio

## 🔄 CONFIGURACIÓN POST-LIMPIEZA

### **1. Configurar Git Correctamente:**
```bash
git config user.name "Davito"
git config user.email "tu-email@gmail.com"
```

### **2. Actualizar Remote (si es necesario):**
```bash
git remote set-url origin https://github.com/davito-03/dabot-v2.git
```

### **3. Hacer Push Limpio:**
```bash
git add .
git commit -m "🔒 Seguridad: Repositorio asegurado - Solo Davito"
git push origin main
```

## ⚠️ SI ENCUENTRAS COMMITS SOSPECHOSOS

### **Revertir Commit Específico:**
```bash
git revert <commit-hash>
git push origin main
```

### **Eliminar Commit del Historial:**
```bash
git reset --hard <commit-anterior-bueno>
git push --force origin main
```

## 📞 SOPORTE DE EMERGENCIA

Si encuentras actividad maliciosa:
1. **Cambiar contraseña GitHub INMEDIATAMENTE**
2. **Revocar TODOS los access tokens**
3. **Revisar logs de actividad en GitHub**
4. **Contactar soporte GitHub si es necesario**

---

**🛡️ Tu repositorio debe estar bajo TU control exclusivo.**
