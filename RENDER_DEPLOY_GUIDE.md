# 🚀 Guía Rápida de Deploy en Render

## ⚡ Opción 1: Manual Setup (MÁS RECOMENDADO)

### **🎯 La forma más confiable de evitar errores:**

1. **Crear Nuevo Web Service**
   - Ve a [Render Dashboard](https://dashboard.render.com)
   - **New +** → **Web Service**
   - Conecta: `https://github.com/davito-03/dabot-v2.git`

2. **Configuración Simple**
   ```
   Name: dabot-v2
   Runtime: Python 3
   Build Command: pip install --upgrade pip && pip install nextcord==2.6.0 python-dotenv==1.0.1 aiohttp==3.9.5 requests==2.31.0 PyNaCl==1.5.0
   Start Command: python bot.py
   ```

3. **Variables de Entorno**
   ```
   DISCORD_TOKEN=tu_token_aqui
   WEB_PORT=10000
   WEB_HOST=0.0.0.0
   ENVIRONMENT=production
   ```

4. **Health Check**
   ```
   Health Check Path: /health
   ```

---

## � Opción 2: Con requirements-minimal.txt

### **Si prefieres usar archivo de requirements:**

**Build Command:**
```bash
pip install --upgrade pip && pip install -r requirements-minimal.txt
```

---

## 🐳 Opción 3: Docker (Solo si las otras fallan)

### **Configuración Docker:**
```
Dockerfile Path: ./Dockerfile
Docker Context: ./
Port: 8080
```

El Dockerfile tiene fallback automático a requirements mínimos.

---

## ❌ **Si sigues teniendo errores:**

### **Deploy Ultra-Simple:**
1. **Build Command:**
   ```bash
   pip install nextcord python-dotenv aiohttp requests
   ```

2. **Start Command:**
   ```bash
   python bot.py
   ```

3. **Variables mínimas:**
   ```
   DISCORD_TOKEN=tu_token
   ```

---

## � **Troubleshooting por Error:**

### **Error: requirements-render.txt failed**
✅ **Usa requirements-minimal.txt o build command manual**

### **Error: Docker build failed**  
✅ **Usa Web Service sin Docker (Opción 1)**

### **Error: Health check failing**
✅ **El bot incluye servidor web automático en puerto 10000**

---

## 🎯 **Método Recomendado Final:**

**La Opción 1 (Manual Setup) es la más confiable porque:**
- ✅ No depende de archivos requirements complejos
- ✅ Instala solo las dependencias esenciales
- ✅ Menos puntos de fallo
- ✅ Build más rápido
