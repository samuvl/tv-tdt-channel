# TV TDT Channel - Generador de Playlist IPTV España

Un proyecto Python para descargar, filtrar y generar playlists IPTV compatibles con Smart TVs Samsung (SS IPTV, Smart IPTV, IPTV Smarters Pro) con numeración estándar TDT de España.

## 🎯 Objetivo

Este proyecto nace de la necesidad de crear una lista de canales personalizada para una TV Samsung QLED de una persona mayor, que quiere acceder fácilmente a los canales principales de la TDT española con una numeración clara y ordenada. El resultado es un archivo `lista_channels.m3u` personalizado con los canales que desees en el orden y numeración que prefieras.

## 🔧 Requisitos

- **Python 3.6+**
- **requests** - Para descargar la fuente oficial

Instala dependencias:
```bash
pip install requests
```

## 📋 Descripción General

El proyecto sigue un flujo de 4 pasos:

```
1. Descubrir canales disponibles
         ↓
2. Crear lista de canales deseados
         ↓
3. Construir la playlist M3U
         ↓
4. Probar en un reproductor IPTV
         ↓
📺 lista_channels.m3u (RESULTADO FINAL)
```

## 🔄 Flujo Detallado

### Paso 1: Descubrir Canales Disponibles
**Archivo:** `1-discovery_channels.py`

Este script descarga la lista oficial de canales TDT de España desde la fuente IPTV comunitaria y muestra todos los canales disponibles con sus metadatos (nombre, grupo, resolución, URL).

**Fuente de datos:** [IPTV-ORG](https://iptv-org.github.io/iptv/countries/es.m3u) - Playlist comunitaria actualizada de canales IPTV España

```bash
python 1-discovery_channels.py
```

**Salida:** `1.1-discovery_channels_result.txt` - Lista de todos los canales disponibles

**Uso:** Ejecuta este script cuando quieras ver QUÉ canales existen en la fuente oficial para decidir cuáles incluir en tu playlist.

---

### Paso 2: Crear Lista de Canales Deseados
**Archivo:** `2-channels_list.txt`

Archivo de configuración donde defines:
- ✅ **Qué canales quieres** (uno por línea)
- 📊 **En qué orden** (línea 1 = Canal 001, línea 2 = Canal 002, etc.)

**Estructura:**
```
La 1 (720p)
La 2 (1080p)
Antena 3 (1080p)
Cuatro (1080p)
...
```

**Notas importantes:**
- El nombre debe coincidir EXACTAMENTE con uno de la fuente (verifica en `1.1-discovery_channels_result.txt`)
- El ORDEN determina la NUMERACIÓN en la playlist TDT simulada
- Puedes incluir resoluciones en el nombre, se limpiarán automáticamente si lo deseas (configurable)

**Archivo de backup:** `2.1-channels_list_backup.txt` - Este archivo contiene los posibles canales que querías incluyendo, ordenados por categorías (TDT, cine, deportes, etc.). Úsalo como referencia para seleccionar los canales que desees en `2-channels_list.txt`

---

### Paso 3: Construir la Playlist M3U
**Archivo:** `3-build_playlist.py`

Script principal que:
1. ✅ Descarga la lista oficial de España
2. 🔍 Filtra solo los canales que están en `2-channels_list.txt`
3. 📝 Genera la playlist M3U con:
   - Numeración automática (001, 002, 003, etc.)
   - Nombres limpios (opcional: elimina resoluciones)
   - Prefijos numéricos (opcional: para forzar orden alfabético)
   - Group-title personalizable
4. 💾 Exporta a `lista_channels.m3u`

**Ejecución:**
```bash
python 3-build_playlist.py
```

**Configuración** (dentro del script):
```python
# Modo de group-title
GROUP_TITLE_MODE = "unique"  # "unique", "custom", "original", "none"
UNIQUE_GROUP_NAME = "TDT España"

# Añadir prefijos numéricos
ADD_NUMERIC_PREFIX = True    # "001. La 1", "002. La 2", etc.

# Limpiar resoluciones
CLEAN_CHANNEL_NAMES = True   # "La 1" en lugar de "La 1 (720p)"
```

**Salida:** `lista_channels.m3u` - Tu playlist IPTV personalizada

**Debug:** `3.1-build_playlist_debug.txt` - Información detallada de qué se procesó y si hay errores

---

### Paso 4: Probar en Reproductor IPTV
**Archivo:** `4-test_iptv_player.html`

Una interfaz HTML simple para probar la playlist generada sin necesidad de un TV.

**Uso en navegador:**
1. Abre el archivo en tu navegador
2. Carga `lista_channels.m3u` 
3. Prueba que todos los canales carguen correctamente

**Uso en VLC Player:**

Si prefieres usar VLC Player para reproducir la playlist:

1. Abre VLC Player
2. Ve a **Media** → **Abrir archivo**
3. Selecciona `lista_channels.m3u`
4. Se abrirá la lista de reproducción con todos tus canales
5. Haz doble clic en cualquier canal para reproducirlo
6. Usa las flechas o el menú de reproducción para cambiar de canal

**Ventajas de VLC:**
- ✅ Reproductor profesional y confiable
- ✅ Funciona en Windows, Mac y Linux
- ✅ Interfaz familiar y fácil de usar
- ✅ Perfecto para personas mayores

Esta es una herramienta útil para verificar que la playlist está bien formada antes de usarla en tu TV.

---

## 🚀 Cómo Usar (Guía Rápida)

### Primera vez:
```bash
# 1. Ver qué canales están disponibles
python 1-discovery_channels.py

# 2. Editar 2-channels_list.txt con tus canales deseados
# (Abre con tu editor de texto favorito)

# 3. Generar la playlist
python 3-build_playlist.py

# 4. Probar (opcional)
# Abre 4-test_iptv_player.html en el navegador
```

### Actualizaciones:
Si quieres cambiar el orden o los canales:
1. Edita `2-channels_list.txt`
2. Ejecuta `python 3-build_playlist.py`
3. Copia `lista_channels.m3u` a tu TV

---

## 📄 Archivos del Proyecto

| Archivo | Tipo | Descripción |
|---------|------|-------------|
| `1-discovery_channels.py` | Script | Descubre canales disponibles en la fuente |
| `1.1-discovery_channels_result.txt` | Salida | Lista de canales encontrados |
| `2-channels_list.txt` | Configuración | Canales que quieres y su orden |
| `2.1-channels_list_backup.txt` | Backup | Copia de seguridad de la configuración |
| `3-build_playlist.py` | Script | Genera la playlist M3U personalizada |
| `3.1-build_playlist_debug.txt` | Debug | Información de proceso y errores |
| `4-test_iptv_player.html` | Herramienta | Prueba la playlist en el navegador |
| `lista_channels.m3u` | **RESULTADO** | **Tu playlist IPTV final** |
| `README.MD` | Documentación | Este archivo |

---

## 💡 Características

✅ **Numeración automática** - Asigna números 001-999 según el orden de `2-channels_list.txt`

✅ **Compatible con Smart TVs Samsung** - Probado con:
- SS IPTV
- Smart IPTV
- IPTV Smarters Pro

✅ **Compatible con otros reproductores:**
- VLC Player
- Navegadores web

✅ **Nombres limpios** - Opcional: elimina resoluciones (720p, 1080p) de los nombres

✅ **Prefijos numéricos** - Fuerza el orden correcto en apps que ordenan alfabéticamente

✅ **Group-title personalizable** - Agrupa todos en "TDT España" o mantén grupos originales

✅ **Flexible** - Incluye solo los canales que quieras, en el orden que desees

---

## 🔧 Requisitos

- **Python 3.6+**
- **requests** - Para descargar la fuente oficial

Instala dependencias:
```bash
pip install requests
```

---

## 📝 Formato M3U

La playlist generada sigue el estándar M3U:

```
#EXTM3U
#EXTINF:-1 tvg-name="La 1" tvg-logo="..." group-title="TDT España",001. La 1
https://...url...
#EXTINF:-1 tvg-name="La 2" tvg-logo="..." group-title="TDT España",002. La 2
https://...url...
```

---

## 🌐 Fuentes Utilizadas

- **IPTV-ORG** (`https://iptv-org.github.io/`) - Playlist comunitaria y actualizada de canales IPTV España

---

## 📌 Notas Importantes

1. **El orden importa** - El orden en `2-channels_list.txt` determina la numeración final
2. **Nombres exactos** - Los nombres deben coincidir EXACTAMENTE con los de la fuente
3. **Actualización de URLs** - Las URLs de los streams pueden cambiar. Si dejan de funcionar, vuelve a ejecutar `1-discovery_channels.py` y `3-build_playlist.py`
4. **Uso legal** - Los canales TDT son emisión legal en España. Este proyecto es solo un filtro/reorganizador

---

## 🤝 GitHub Actions - CI/CD Pipeline

Este repositorio incluye un pipeline automatizado con GitHub Actions que valida y genera la playlist automáticamente.

### ¿Qué hace el pipeline?

El workflow automático se ejecuta cuando:
- Haces push a cambios en `2-channels_list.txt`
- Haces push a cambios en `3-build_playlist.py`
- Ejecutas manualmente el workflow desde GitHub

**Proceso automático:**
1. ✅ Descarga la lista oficial de canales
2. 🔍 Valida que todos los canales en `2-channels_list.txt` existan en la fuente
3. 📝 Genera automáticamente `lista_channels.m3u`
4. 📊 Crea un reporte de debug en `3.1-build_playlist_debug.txt`
5. 💾 Commit automático con los archivos generados

### Cómo usar GitHub Actions desde la web

1. **Ir a la pestaña Actions**
   - En tu repositorio de GitHub, haz clic en la pestaña **Actions**

2. **Seleccionar el workflow**
   - Verás el workflow "Build IPTV Playlist"
   - Haz clic en él

3. **Ejecutar manualmente (Manual Trigger)**
   - En el lado derecho verás un botón **"Run workflow"**
   - Haz clic en él para generar la playlist al instante
   - Selecciona la rama (normalmente `main`)

4. **Ver el resultado**
   - El workflow se ejecutará automáticamente
   - Puedes ver el progreso en tiempo real
   - Una vez finalizado, verás un ✅ si fue exitoso o un ❌ si hay errores

5. **Descargar el resultado**
   - Los archivos generados se guardan automáticamente en el repositorio
   - Puedes descargar `lista_channels.m3u` directamente desde GitHub
   - En la rama `main`, entra en el archivo y descárgalo

### Ventajas del pipeline

✅ **Automatizado** - No necesitas ejecutar scripts localmente

✅ **Validación** - Verifica automáticamente que los nombres sean correctos

✅ **Historial** - Puedes ver todos los cambios en el historial de Actions

✅ **Fácil de usar** - Interfaz gráfica en GitHub, sin terminal

✅ **Commits automáticos** - Guarda los cambios automáticamente

### Workflow típico con GitHub Actions

1. Edita `2-channels_list.txt` directamente en GitHub
2. Haz commit desde la web de GitHub
3. El pipeline se ejecuta automáticamente
4. Tu `lista_channels.m3u` se genera automáticamente
5. Descarga el archivo desde GitHub

---

## 📄 Licencia

Proyecto personal para uso con canales TDT públicos de España.

---

## 📞 Troubleshooting

### "Canal no encontrado"
→ Verifica el nombre exacto en `1.1-discovery_channels_result.txt`

### "Algunas URLs no funcionan"
→ Las fuentes pueden cambiar. Ejecuta nuevamente `1-discovery_channels.py` y `3-build_playlist.py`

### "La playlist se ve desordenada en mi TV"
→ Activa `ADD_NUMERIC_PREFIX = True` en `3-build_playlist.py`

### "Veo resoluciones en los nombres (720p, 1080p)"
→ Activa `CLEAN_CHANNEL_NAMES = True` en `3-build_playlist.py`

---

**Versión:** 1.0
**Última actualización:** 2026
