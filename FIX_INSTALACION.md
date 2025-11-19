# 🔧 FIX: Error de Instalación - Conflicto de Dependencias

## ❌ Problema
```
ERROR: ResolutionImpossible
The user requested numpy==2.1.3
langchain 0.3.7 depends on numpy<2 and >=1.26.0
```

## ✅ Solución Rápida

### **Opción 1: Usar requirements_fixed.txt (RECOMENDADO)**

```bash
# 1. Descargar requirements_fixed.txt (está en outputs)

# 2. Reemplazar el archivo
cp requirements_fixed.txt requirements.txt

# 3. Instalar
pip install -r requirements.txt
```

### **Opción 2: Modificar manualmente**

Edita `requirements.txt` y cambia esta línea:

**ANTES:**
```
numpy==2.1.3
```

**DESPUÉS:**
```
numpy==1.26.4
```

Luego instala:
```bash
pip install -r requirements.txt
```

### **Opción 3: Instalar sin numpy primero**

```bash
# 1. Remover numpy del requirements temporalmente
grep -v "numpy" requirements.txt > requirements_temp.txt

# 2. Instalar todo lo demás
pip install -r requirements_temp.txt

# 3. Dejar que langchain instale su numpy compatible
# (ya está instalado con las dependencias de langchain)
```

---

## 🎯 Por qué ocurre

- **Langchain 0.3.7** requiere `numpy<2` (versiones 1.x)
- El `requirements.txt` original tenía `numpy==2.1.3`
- Python no puede instalar ambas versiones

---

## ✅ Versiones Correctas

```
numpy==1.26.4           ← Compatible con langchain
langchain==0.3.7        ← Requiere numpy < 2.0
pandas==2.2.3           ← Compatible con numpy 1.26
```

---

## 🚀 Verificar Instalación

Después de instalar, verifica:

```bash
python -c "import numpy; print(f'Numpy: {numpy.__version__}')"
python -c "import langchain; print(f'Langchain: {langchain.__version__}')"
python -c "import streamlit; print('Streamlit OK')"
```

**Output esperado:**
```
Numpy: 1.26.4
Langchain: 0.3.7
Streamlit OK
```

---

## 📥 Archivo Listo Para Descargar

El archivo `requirements_fixed.txt` está en tus outputs.

Descárgalo y úsalo en lugar del `requirements.txt` original.

---

## ⚡ Instalación Limpia (Recomendado)

Si quieres empezar limpio:

```bash
# 1. Crear entorno virtual nuevo
python -m venv venv
source venv/bin/activate  # Linux/Mac
# o
venv\Scripts\activate     # Windows

# 2. Actualizar pip
pip install --upgrade pip

# 3. Instalar con requirements corregido
pip install -r requirements_fixed.txt
```

---

## ✅ Después de Instalar

Prueba que todo funciona:

```bash
# Test rápido
python -c "from core.bootstrap import initialize_argo; print('Bootstrap OK')"

# Ejecutar UI
streamlit run app/ui.py
```

Si ves la interfaz de Streamlit, **todo está OK** ✅
