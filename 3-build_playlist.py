#!/usr/bin/env python3
"""
Script para descargar y filtrar lista IPTV de España.
Genera playlist M3U con numeración TDT estándar.
Compatible con Samsung QLED TV: SS IPTV, Smart IPTV, IPTV Smarters Pro

Características:
- Numeración automática según orden en channels_list.txt
- Group-title personalizable
- Prefijos numéricos para forzar orden en apps que ordenan alfabéticamente
- URLs limpias sin corchetes
- Nombres de canales limpios sin resoluciones (720p, 1080p, etc.)
"""

import requests
import re
from datetime import datetime


# ============================================================================
# CONFIGURACIÓN
# ============================================================================
SOURCE_URL = "https://iptv-org.github.io/iptv/countries/es.m3u"
OUTPUT_FILE = "lista_channels.m3u"
CHANNELS_FILE = "2-channels_list.txt"
DEBUG_FILE = "3.1-build_playlist_debug.txt"

# Configuración de group-title
# Opciones: "unique", "custom", "original", "none"
GROUP_TITLE_MODE = "unique"
UNIQUE_GROUP_NAME = "TDT España"

# Prefijos numéricos en nombres (para forzar orden alfabético)
# True = "001. La 1", False = "La 1"
ADD_NUMERIC_PREFIX = True

# Limpiar resoluciones del nombre (720p, 1080p, etc.)
# True = "La 1", False = "La 1 (720p)"
CLEAN_CHANNEL_NAMES = True


# ============================================================================
# FUNCIONES
# ============================================================================

def load_wanted_channels():
    """
    Lee channels_list.txt y retorna lista de canales deseados.
    El ORDEN del archivo determina la NUMERACIÓN en la TDT simulada.
    """
    try:
        with open(CHANNELS_FILE, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        channels = [line.strip() for line in lines 
                   if line.strip() and not line.strip().startswith('#')]
        return channels
    except FileNotFoundError:
        print(f"❌ ERROR: Archivo no encontrado: {CHANNELS_FILE}")
        print(f"   Crea {CHANNELS_FILE} con los nombres de canales en orden TDT")
        return []


def fetch_source_playlist():
    """Descarga la lista oficial de España."""
    print(f"📥 Descargando lista desde: {SOURCE_URL}")
    try:
        response = requests.get(SOURCE_URL, timeout=15)
        response.raise_for_status()
        print("✅ Lista descargada correctamente\n")
        return response.text
    except requests.RequestException as e:
        print(f"❌ Error al descargar: {e}\n")
        return None


def parse_m3u(content):
    """Parsea el contenido M3U y retorna lista de canales."""
    channels = []
    lines = content.split('\n')
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        if line.startswith('#EXTINF'):
            extinf_line = line
            if i + 1 < len(lines):
                url_line = lines[i + 1].strip()
                if url_line and url_line.startswith('http'):
                    channels.append({
                        'extinf': extinf_line,
                        'url': url_line,
                        'name': extract_channel_name(extinf_line)
                    })
                    i += 2
                else:
                    i += 1
            else:
                i += 1
        else:
            i += 1
    
    return channels


def extract_channel_name(extinf_line):
    """Extrae el nombre del canal de la línea EXTINF."""
    if ',' in extinf_line:
        name = extinf_line.split(',', 1)[1].strip()
        return name
    return ""


def clean_channel_name(channel_name):
    """
    Limpia el nombre del canal eliminando resoluciones y etiquetas.
    
    Ejemplos:
    - "La 1 (720p)" → "La 1"
    - "Antena 3 (1080p)" → "Antena 3"
    - "Tele Safor (720p) [Not 24/7]" → "Tele Safor"
    - "La 1 UHD (2160p)" → "La 1 UHD"
    """
    if not CLEAN_CHANNEL_NAMES:
        return channel_name
    
    # Eliminar patrones comunes:
    # - (720p), (1080p), (2160p), (576p), (1280p), etc.
    # - [Not 24/7], [Geo-blocked], etc.
    # - Espacios extra
    
    # Eliminar resoluciones entre paréntesis
    cleaned = re.sub(r'\s*\(\d+p\)', '', channel_name)
    
    # Eliminar etiquetas entre corchetes
    cleaned = re.sub(r'\s*\[.*?\]', '', cleaned)
    
    # Eliminar espacios extra y trimear
    cleaned = ' '.join(cleaned.split())
    
    return cleaned.strip()


def clean_url(url):
    """
    Limpia la URL para asegurar formato correcto M3U.
    Remueve corchetes markdown y espacios extra.
    """
    url = url.strip()
    if url.startswith('[') and url.endswith(']'):
        url = url[1:-1]
    url = url.replace('[', '').replace(']', '')
    url = url.strip()
    return url


def add_channel_number_to_extinf(extinf_line, channel_number):
    """
    Agrega tvg-chno (número de canal) a la línea EXTINF.
    El atributo tvg-chno es reconocido por apps IPTV para ordenar canales.
    """
    # Buscar si ya existe tvg-chno y eliminarlo
    extinf_line = re.sub(r'tvg-chno="[^"]*"\s*', '', extinf_line)
    
    # Insertar tvg-chno justo después de #EXTINF:-1
    if extinf_line.startswith('#EXTINF:-1'):
        extinf_line = extinf_line.replace(
            '#EXTINF:-1 ',
            f'#EXTINF:-1 tvg-chno="{channel_number}" ',
            1
        )
        if '#EXTINF:-1 tvg-chno=' not in extinf_line:
            extinf_line = extinf_line.replace(
                '#EXTINF:-1',
                f'#EXTINF:-1 tvg-chno="{channel_number}" ',
                1
            )
    
    return extinf_line


def add_channel_prefix_to_name(extinf_line, channel_number):
    """
    Agrega número de canal al principio del nombre para forzar orden alfabético.
    Ej: "La 1" → "001. La 1"
    
    Esto garantiza que incluso si la app ordena alfabéticamente,
    los canales aparezcan en el orden correcto.
    """
    if not ADD_NUMERIC_PREFIX:
        return extinf_line
    
    if ',' in extinf_line:
        parts = extinf_line.split(',', 1)
        channel_name = parts[1].strip()
        # Agregar prefijo con padding de 3 dígitos (soporta hasta 999 canales)
        new_name = f"{channel_number:03d}. {channel_name}"
        extinf_line = f"{parts[0]},{new_name}"
    
    return extinf_line


def clean_extinf_channel_name(extinf_line):
    """
    Limpia el nombre del canal dentro de la línea EXTINF.
    Elimina resoluciones y etiquetas del nombre después de la coma.
    """
    if not CLEAN_CHANNEL_NAMES:
        return extinf_line
    
    if ',' in extinf_line:
        parts = extinf_line.split(',', 1)
        channel_name = parts[1].strip()
        cleaned_name = clean_channel_name(channel_name)
        extinf_line = f"{parts[0]},{cleaned_name}"
    
    return extinf_line


def normalize_group_title(extinf_line, channel_number=None, mode=None, custom_name=None):
    """
    Normaliza el group-title según configuración.
    
    Modos:
    - "unique": Todos los canales en un grupo
    - "custom": Grupos personalizados por rango de canales
    - "original": Mantiene el original
    - "none": Sin group-title
    """
    if mode is None:
        mode = GROUP_TITLE_MODE
    if custom_name is None:
        custom_name = UNIQUE_GROUP_NAME
    
    if mode == "original":
        return extinf_line
    
    if mode == "none":
        return re.sub(r'group-title="[^"]*"\s*', '', extinf_line)
    
    # Eliminar group-title existente
    extinf_line = re.sub(r'group-title="[^"]*"\s*', '', extinf_line)
    
    # Determinar nuevo group-title
    if mode == "unique":
        new_group = custom_name
    elif mode == "custom":
        # Grupos personalizados según numeración
        if channel_number <= 8:
            new_group = "Nacionales"
        elif channel_number <= 18:
            new_group = "Entretenimiento"
        elif channel_number <= 33:
            new_group = "Autonómicos"
        else:
            new_group = "Temáticos"
    else:
        new_group = custom_name
    
    # Agregar nuevo group-title
    if ',' in extinf_line:
        parts = extinf_line.split(',', 1)
        extinf_line = f'{parts[0]} group-title="{new_group}",{parts[1]}'
    
    return extinf_line


def match_channel_strict(available_name, wanted_name):
    """
    Intenta hacer matching de forma inteligente:
    1. Primero match exacto
    2. Luego case-insensitive
    3. Luego búsqueda parcial (ignorando resoluciones)
    """
    avail = available_name.strip()
    want = wanted_name.strip()
    
    # Match exacto
    if avail == want:
        return True
    
    # Case-insensitive
    if avail.lower() == want.lower():
        return True
    
    # Búsqueda parcial
    if want.lower() in avail.lower():
        return True
    
    # Búsqueda inversa
    if avail.lower() in want.lower():
        return True
    
    # Matching sin resoluciones (más flexible)
    avail_clean = clean_channel_name(avail).lower()
    want_clean = clean_channel_name(want).lower()
    
    if avail_clean == want_clean:
        return True
    
    return False


def build_custom_playlist(all_channels, wanted_channels):
    """
    Construye la playlist personalizada con numeración TDT.
    El orden en channels_list.txt determina el número de canal.
    """
    playlist_lines = ["#EXTM3U"]
    found_channels = {}
    debug_matches = []
    
    print(f"🔍 Buscando {len(wanted_channels)} canales solicitados...\n")
    print(f"{'Nº':<4} {'Buscado':<40} {'Encontrado':<50} {'Estado':<15}")
    print("-" * 115)
    
    # Primer paso: mapear canales encontrados con numeración
    for idx, wanted in enumerate(wanted_channels, start=1):
        best_match = None
        best_match_data = None
        
        for channel_data in all_channels:
            channel_name = channel_data['name']
            
            if match_channel_strict(channel_name, wanted):
                # Si hay múltiples matches, prefiere el más corto (más específico)
                if best_match is None or len(channel_name) < len(best_match):
                    best_match = channel_name
                    best_match_data = channel_data
        
        if best_match_data:
            found_channels[wanted] = {
                'data': best_match_data,
                'number': idx
            }
            status = "✅ OK"
            print(f"{idx:<4} {wanted:<40} {best_match:<50} {status:<15}")
            debug_matches.append(f"Canal {idx}: ✅ '{wanted}' -> '{best_match}'")
        else:
            status = "❌ NO ENCONTRADO"
            print(f"{idx:<4} {wanted:<40} {'-':<50} {status:<15}")
            debug_matches.append(f"Canal {idx}: ❌ '{wanted}' -> NO ENCONTRADO")
    
    # Segundo paso: escribir en orden con todas las transformaciones
    print(f"\n" + "=" * 115)
    print(f"✅ Canales encontrados: {len(found_channels)}/{len(wanted_channels)}")
    print(f"=" * 115 + "\n")
    
    for wanted in wanted_channels:
        if wanted in found_channels:
            channel_info = found_channels[wanted]
            channel_data = channel_info['data']
            channel_number = channel_info['number']
            
            # 1. Agregar número de canal (tvg-chno)
            extinf_with_number = add_channel_number_to_extinf(
                channel_data['extinf'],
                channel_number
            )
            
            # 2. Limpiar nombre del canal (eliminar resoluciones)
            extinf_cleaned = clean_extinf_channel_name(extinf_with_number)
            
            # 3. Agregar prefijo numérico al nombre (001., 002., etc.)
            extinf_with_prefix = add_channel_prefix_to_name(
                extinf_cleaned,
                channel_number
            )
            
            # 4. Normalizar group-title
            extinf_final = normalize_group_title(
                extinf_with_prefix,
                channel_number
            )
            
            # 5. Agregar línea EXTINF y URL limpia
            playlist_lines.append(extinf_final)
            clean_channel_url = clean_url(channel_data['url'])
            playlist_lines.append(clean_channel_url)
    
    # Guardar debug log
    with open(DEBUG_FILE, 'w', encoding='utf-8') as f:
        f.write(f"DEBUG: Matching Results con Numeración TDT\n")
        f.write(f"Configuración:\n")
        f.write(f"  - GROUP_TITLE_MODE: {GROUP_TITLE_MODE}\n")
        f.write(f"  - UNIQUE_GROUP_NAME: {UNIQUE_GROUP_NAME}\n")
        f.write(f"  - ADD_NUMERIC_PREFIX: {ADD_NUMERIC_PREFIX}\n")
        f.write(f"  - CLEAN_CHANNEL_NAMES: {CLEAN_CHANNEL_NAMES}\n")
        f.write("=" * 70 + "\n\n")
        for line in debug_matches:
            f.write(line + "\n")
        f.write("\n" + "=" * 70 + "\n")
        f.write(f"💡 El orden en {CHANNELS_FILE} determina la numeración\n")
        f.write(f"   Canal 1 = primera línea, Canal 2 = segunda línea, etc.\n")
    
    return '\n'.join(playlist_lines)


def save_playlist(content):
    """Guarda la playlist en fichero."""
    try:
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            f.write(content)
        
        url_count = content.count('http')
        
        print(f"📁 Playlist guardada: {OUTPUT_FILE}")
        print(f"📊 Canales en la playlist: {url_count}")
        print(f"\n📺 CONFIGURACIÓN:")
        print(f"   ✅ Numeración TDT automática (tvg-chno)")
        print(f"   ✅ Prefijos numéricos: {'SÍ' if ADD_NUMERIC_PREFIX else 'NO'}")
        print(f"   ✅ Nombres limpios: {'SÍ (sin resoluciones)' if CLEAN_CHANNEL_NAMES else 'NO'}")
        print(f"   ✅ Group-title: {GROUP_TITLE_MODE.upper()}")
        if GROUP_TITLE_MODE == "unique":
            print(f"   📂 Grupo único: '{UNIQUE_GROUP_NAME}'")
        print(f"\n🎯 ORDEN:")
        print(f"   Canal 1 = {CHANNELS_FILE} línea 1")
        print(f"   Canal 2 = {CHANNELS_FILE} línea 2")
        print(f"   Canal N = {CHANNELS_FILE} línea N\n")
        return True
    except IOError as e:
        print(f"❌ Error al guardar: {e}")
        return False


def main():
    """Función principal."""
    print("=" * 115)
    print("🎬 GENERADOR DE PLAYLIST IPTV - NUMERACIÓN TDT PARA SAMSUNG QLED TV")
    print("=" * 115)
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # 1. Cargar canales deseados (el orden importa!)
    wanted_channels = load_wanted_channels()
    if not wanted_channels:
        return
    print(f"📋 Canales a buscar: {len(wanted_channels)}")
    print(f"💡 El ORDEN en {CHANNELS_FILE} determina la numeración TDT")
    print(f"🏷️  Modo group-title: {GROUP_TITLE_MODE}")
    print(f"🔢 Prefijos numéricos: {'ACTIVADOS' if ADD_NUMERIC_PREFIX else 'DESACTIVADOS'}")
    print(f"🧹 Limpiar nombres: {'ACTIVADO' if CLEAN_CHANNEL_NAMES else 'DESACTIVADO'}\n")
    
    # 2. Descargar fuente
    source_content = fetch_source_playlist()
    if not source_content:
        return
    
    # 3. Parsear
    all_channels = parse_m3u(source_content)
    print(f"📊 Canales totales en fuente: {len(all_channels)}\n")
    
    # 4. Filtrar, ordenar y numerar
    custom_playlist = build_custom_playlist(all_channels, wanted_channels)
    
    # 5. Guardar
    if save_playlist(custom_playlist):
        print("=" * 115)
        print("✅ PROCESO COMPLETADO - LISTA TDT LIMPIA Y NUMERADA")
        print("=" * 115)
        print(f"\n💡 Tip: Revisa {DEBUG_FILE} si algo no se encontró")
        print(f"\n📱 SIGUIENTE PASO:")
        print(f"   1. Verifica el orden: head -20 {OUTPUT_FILE}")
        print(f"   2. Prueba en navegador: test_iptv_player.html")
        print(f"   3. Sube a GitHub: git add {OUTPUT_FILE} && git commit -m 'Update' && git push")
        print(f"   4. En Samsung TV: ELIMINA playlist antigua y añade URL raw actualizada")
        print(f"   5. Los canales aparecerán como: 001. La 1, 002. La 2, 003. Antena 3, etc.\n")
    else:
        print("\n❌ Error durante el guardado")


if __name__ == "__main__":
    main()
