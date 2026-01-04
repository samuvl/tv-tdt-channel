#!/usr/bin/env python3
"""
Script para DESCUBRIR y LISTAR todos los canales disponibles en la fuente.
Úsalo para saber QUÉ nombres poner en channels_list.txt
"""

import requests
from collections import defaultdict

SOURCE_URL = "https://iptv-org.github.io/iptv/countries/es.m3u"

def fetch_source_playlist():
    """Descarga la lista oficial de España."""
    print(f"📥 Descargando lista desde: {SOURCE_URL}\n")
    try:
        response = requests.get(SOURCE_URL, timeout=10)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"❌ Error: {e}")
        return None

def parse_m3u(content):
    """Parsea el contenido M3U y extrae metadatos."""
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
                    # Extraer metadatos
                    channel_data = parse_extinf(extinf_line)
                    channel_data['url'] = url_line
                    channels.append(channel_data)
                    i += 2
                else:
                    i += 1
            else:
                i += 1
        else:
            i += 1
    
    return channels

def parse_extinf(extinf_line):
    """Extrae los metadatos de una línea EXTINF."""
    data = {
        'name': '',
        'tvg_id': '',
        'tvg_name': '',
        'group': '',
        'logo': ''
    }
    
    # Extraer nombre (después de la última coma)
    if ',' in extinf_line:
        data['name'] = extinf_line.split(',', 1)[1].strip()
    
    # Extraer atributos (regex opcional, pero aquí usamos split simple)
    # Formato: tvg-id="..." tvg-name="..." group-title="..." logo="..."
    if 'tvg-id=' in extinf_line:
        start = extinf_line.find('tvg-id="') + len('tvg-id="')
        end = extinf_line.find('"', start)
        data['tvg_id'] = extinf_line[start:end]
    
    if 'tvg-name=' in extinf_line:
        start = extinf_line.find('tvg-name="') + len('tvg-name="')
        end = extinf_line.find('"', start)
        data['tvg_name'] = extinf_line[start:end]
    
    if 'group-title=' in extinf_line:
        start = extinf_line.find('group-title="') + len('group-title="')
        end = extinf_line.find('"', start)
        data['group'] = extinf_line[start:end]
    
    return data

def main():
    """Función principal."""
    print("=" * 80)
    print("🔍 DESCUBRIDOR DE CANALES IPTV - ESPAÑA")
    print("=" * 80)
    
    # Descargar
    source_content = fetch_source_playlist()
    if not source_content:
        return
    
    # Parsear
    print("⏳ Analizando canales...\n")
    channels = parse_m3u(source_content)
    print(f"📊 Total de canales encontrados: {len(channels)}\n")
    
    # Agrupar por categoría (group-title)
    by_group = defaultdict(list)
    for ch in channels:
        group = ch['group'] if ch['group'] else 'Sin categoría'
        by_group[group].append(ch)
    
    # Mostrar por grupo
    for group in sorted(by_group.keys()):
        print(f"\n{'='*80}")
        print(f"📺 GRUPO: {group}")
        print(f"{'='*80}")
        print(f"{'# Nombre del Canal':<50} {'TVG-ID':<20}")
        print("-" * 80)
        
        for i, ch in enumerate(sorted(by_group[group], key=lambda x: x['name']), 1):
            name = ch['name'][:48]  # Truncar si es muy largo
            tvg_id = ch['tvg_id'][:18]
            print(f"{i:2}. {name:<48} {tvg_id:<20}")
    
    # Crear fichero de referencia
    output_file = "1.1-discovery_channels_result.txt"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("CANALES DISPONIBLES EN ESPAÑA (iptv-org)\n")
        f.write(f"Actualizado: 2026-01-04\n")
        f.write(f"Total: {len(channels)} canales\n\n")
        f.write("INSTRUCCIONES:\n")
        f.write("1. Busca el canal que quieres en esta lista\n")
        f.write("2. Copia el nombre EXACTO (columna 'Nombre del Canal')\n")
        f.write("3. Pégalo en channels_list.txt\n\n")
        
        for group in sorted(by_group.keys()):
            f.write(f"\n{'='*80}\n")
            f.write(f"GRUPO: {group}\n")
            f.write(f"{'='*80}\n")
            for ch in sorted(by_group[group], key=lambda x: x['name']):
                f.write(f"  • {ch['name']}\n")
    
    print(f"\n\n✅ Lista de referencia guardada en: {output_file}")
    print(f"📖 Abre este fichero para copiar nombres exactos a channels_list.txt\n")

if __name__ == "__main__":
    main()
