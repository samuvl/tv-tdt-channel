#!/usr/bin/env python3
"""
Script para descargar y filtrar lista IPTV de España.
Genera una playlist M3U limpia solo con los canales que necesitas.
"""

import requests
import re
from datetime import datetime

SOURCE_URL = "https://iptv-org.github.io/iptv/countries/es.m3u"
OUTPUT_FILE = "lista_abuela.m3u"
CHANNELS_FILE = "channels_list.txt"
DEBUG_FILE = "debug_matching.txt"

def load_wanted_channels():
    """Lee channels_list.txt y retorna lista de canales deseados."""
    try:
        with open(CHANNELS_FILE, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Filtrar líneas vacías y comentarios
        channels = [line.strip() for line in lines 
                   if line.strip() and not line.strip().startswith('#')]
        return channels
    except FileNotFoundError:
        print(f"❌ ERROR: Archivo no encontrado: {CHANNELS_FILE}")
        print(f"   Crea {CHANNELS_FILE} con los nombres de canales que quieres")
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

def match_channel_strict(available_name, wanted_name):
    """
    Intenta hacer matching de forma inteligente:
    1. Primero match exacto
    2. Luego case-insensitive
    3. Luego búsqueda parcial (si el wanted está dentro del available)
    """
    avail = available_name.strip()
    want = wanted_name.strip()
    
    # Match exacto
    if avail == want:
        return True
    
    # Case-insensitive
    if avail.lower() == want.lower():
        return True
    
    # Búsqueda parcial: el nombre buscado está dentro del disponible
    # Ej: buscamos "Punt 3 Vall Uixó" y encontramos "Punt 3 Vall Uixó (1080p)" -> Match
    if want.lower() in avail.lower():
        return True
    
    # Búsqueda inversa (raro pero puede pasar)
    if avail.lower() in want.lower():
        return True
    
    return False

def build_custom_playlist(all_channels, wanted_channels):
    """Construye la playlist personalizada manteniendo el orden deseado."""
    playlist_lines = ["#EXTM3U"]
    found_channels = {}
    debug_matches = []
    
    print(f"🔍 Buscando {len(wanted_channels)} canales solicitados...\n")
    print(f"{'#':<3} {'Buscado':<40} {'Encontrado':<50} {'Estado':<15}")
    print("-" * 110)
    
    # Primer paso: mapear canales encontrados con los deseados
    for wanted in wanted_channels:
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
            found_channels[wanted] = best_match_data
            status = "✅ OK"
            print(f"{len(found_channels):<3} {wanted:<40} {best_match:<50} {status:<15}")
            debug_matches.append(f"✅ '{wanted}' -> '{best_match}'")
        else:
            status = "❌ NO ENCONTRADO"
            print(f"{'?':<3} {wanted:<40} {'-':<50} {status:<15}")
            debug_matches.append(f"❌ '{wanted}' -> NO ENCONTRADO")
    
    # Segundo paso: escribir en orden de preferencia
    print(f"\n" + "=" * 110)
    print(f"✅ Canales encontrados: {len(found_channels)}/{len(wanted_channels)}")
    print(f"=" * 110 + "\n")
    
    for wanted in wanted_channels:
        if wanted in found_channels:
            channel_data = found_channels[wanted]
            playlist_lines.append(channel_data['extinf'])
            playlist_lines.append(channel_data['url'])
    
    # Guardar debug log
    with open(DEBUG_FILE, 'w', encoding='utf-8') as f:
        f.write("DEBUG: Matching Results\n")
        f.write("=" * 60 + "\n\n")
        for line in debug_matches:
            f.write(line + "\n")
    
    return '\n'.join(playlist_lines)

def save_playlist(content):
    """Guarda la playlist en fichero."""
    try:
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # Contar líneas de canal (ignorando #EXTM3U y metadata)
        url_count = content.count('http')
        
        print(f"📁 Playlist guardada: {OUTPUT_FILE}")
        print(f"📊 Canales en la playlist: {url_count}\n")
        return True
    except IOError as e:
        print(f"❌ Error al guardar: {e}")
        return False

def main():
    """Función principal."""
    print("=" * 110)
    print("🎬 GENERADOR DE PLAYLIST IPTV PERSONALIZADO")
    print("=" * 110)
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # 1. Cargar canales deseados
    wanted_channels = load_wanted_channels()
    if not wanted_channels:
        return
    print(f"📋 Canales a buscar: {len(wanted_channels)}\n")
    
    # 2. Descargar fuente
    source_content = fetch_source_playlist()
    if not source_content:
        return
    
    # 3. Parsear
    all_channels = parse_m3u(source_content)
    print(f"📊 Canales totales en fuente: {len(all_channels)}\n")
    
    # 4. Filtrar y ordenar
    custom_playlist = build_custom_playlist(all_channels, wanted_channels)
    
    # 5. Guardar
    if save_playlist(custom_playlist):
        print("=" * 110)
        print("✅ PROCESO COMPLETADO")
        print("=" * 110)
        print(f"\n💡 Tip: Revisa {DEBUG_FILE} si algo no se encontró\n")
    else:
        print("\n❌ Error durante el guardado")

if __name__ == "__main__":
    main()
