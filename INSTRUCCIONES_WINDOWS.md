# 🚀 ARGO v9.0 - Instrucciones para Windows

## ✅ El Problema que Tuviste

Intentaste ejecutar `python -m streamlit run app/ui.py` y te dio error:
```
No module named streamlit
```

**Causa:** Las dependencias NO están instaladas en tu entorno virtual.

---

## 📋 Instalación en Windows (3 Pasos)

### Paso 1: Instalar Dependencias

En tu PowerShell/CMD con el entorno virtual activado (`.venv`):

```powershell
# Asegúrate de estar en la carpeta ARGO
cd C:\Users\crdegoycoechea\ARGO

# Activa el entorno virtual (si no está activado)
.venv\Scripts\activate

# Instala TODAS las dependencias
pip install -r requirements.txt
```

**IMPORTANTE:** El archivo `requirements.txt` contiene:
- streamlit==1.40.1
- langchain==0.3.7
- openai==1.54.0
- anthropic==0.39.0
- chromadb==0.5.20
- pandas==2.2.3
- Y muchas más...

### Paso 2: Configurar Variables de Entorno

Crea un archivo `.env` en la raíz del proyecto:

```powershell
# Copia el ejemplo
copy .env.example .env

# Edita con Notepad
notepad .env
```

Agrega tu API key de OpenAI:
```
OPENAI_API_KEY=sk-tu-key-aqui
ANTHROPIC_API_KEY=sk-ant-tu-key-aqui  # (opcional)
```

### Paso 3: Iniciar ARGO

```powershell
# Opción 1: Ejecutar directamente
python -m streamlit run app/ui.py

# Opción 2: Usando python simple
streamlit run app/ui.py
```

---

## 🔧 Solución Rápida (Si Ya Instalaste Antes)

Si ya hiciste `pip install` de muchas cosas (como vi en tu captura), pero falta streamlit:

```powershell
pip install streamlit==1.40.1
python -m streamlit run app/ui.py
```

---

## 📁 Estructura del Proyecto

```
ARGO/
├── app/
│   ├── ui.py              ← Archivo principal de Streamlit
│   └── panels/            ← Paneles de la UI
├── core/
│   ├── bootstrap.py       ← Inicialización
│   ├── model_router.py    ← Router de LLMs
│   ├── rag_engine.py      ← Motor RAG
│   └── ...
├── tools/
│   ├── extractors.py      ← Procesamiento de docs
│   ├── google_drive_sync.py
│   └── ...
├── config/
│   └── settings.yaml      ← Configuración central
├── requirements.txt       ← ¡ESTE archivo es crucial!
├── .env.example           ← Plantilla de variables
└── install.sh             ← Script para Linux/Mac
```

---

## ❓ Verificar Instalación

```powershell
# Ver qué paquetes tienes instalados
pip list

# Verificar streamlit específicamente
pip show streamlit

# Debería mostrar: Version: 1.40.1
```

---

## 🐛 Problemas Comunes

### Error: "No module named streamlit"
**Solución:** `pip install -r requirements.txt`

### Error: "No module named langchain"
**Solución:** `pip install -r requirements.txt`

### Error: Scripts .sh no funcionan en Windows
**Solución:** No uses `install.sh` ni `start.sh`. Usa los comandos de PowerShell arriba.

### Error: "python: command not found"
**Solución:** Usa `py` en lugar de `python`:
```powershell
py -m streamlit run app/ui.py
```

---

## 🎯 Verificación Final

Ejecuta esto para verificar que todo está bien:

```powershell
# Test de importación
python -c "from core.bootstrap import initialize_argo; print('✅ ARGO OK')"

# Si funciona, inicia la UI
streamlit run app/ui.py
```

---

## 📊 Lo Que Verás

Cuando ARGO inicie correctamente:
1. Se abrirá tu navegador en `http://localhost:8501`
2. Verás la interfaz de ARGO con:
   - Panel de consultas
   - Gestión de biblioteca
   - Analytics
   - Configuración

---

## 🆘 Ayuda Adicional

Si tienes problemas:
1. Verifica que el entorno virtual esté activado (debería decir `(.venv)` en tu prompt)
2. Verifica que Python sea 3.9-3.12: `python --version`
3. Reinstala dependencias: `pip install -r requirements.txt --force-reinstall`

---

**¡El proyecto está COMPLETO y funcional! Solo faltaba instalar las dependencias.** 🎉
