"""
Búsqueda alternativa de YouTube usando requests y regex
"""

import re
import requests
import json
from urllib.parse import quote

def search_youtube_alternative(query, limit=5):
    """Búsqueda alternativa usando la página web de YouTube"""
    try:
        # Preparar la búsqueda
        search_query = quote(query)
        url = f"https://www.youtube.com/results?search_query={search_query}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            # Buscar datos JSON en la página
            pattern = r'var ytInitialData = ({.*?});'
            match = re.search(pattern, response.text)
            
            if match:
                data = json.loads(match.group(1))
                
                # Extraer resultados
                results = []
                try:
                    contents = data['contents']['twoColumnSearchResultsRenderer']['primaryContents']['sectionListRenderer']['contents'][0]['itemSectionRenderer']['contents']
                    
                    for item in contents[:limit]:
                        if 'videoRenderer' in item:
                            video = item['videoRenderer']
                            
                            # Extraer información básica
                            video_id = video.get('videoId', '')
                            title = video.get('title', {}).get('runs', [{}])[0].get('text', 'Título desconocido')
                            
                            # Extraer canal
                            channel = 'Desconocido'
                            if 'ownerText' in video:
                                channel = video['ownerText']['runs'][0]['text']
                            
                            # Extraer duración
                            duration_str = 'N/A'
                            if 'lengthText' in video:
                                duration_str = video['lengthText']['simpleText']
                            
                            # Extraer thumbnail
                            thumbnail = None
                            if 'thumbnail' in video and 'thumbnails' in video['thumbnail']:
                                thumbnail = video['thumbnail']['thumbnails'][-1]['url']
                            
                            results.append({
                                'title': title,
                                'url': f'https://www.youtube.com/watch?v={video_id}',
                                'duration': 0,
                                'duration_str': duration_str,
                                'uploader': channel,
                                'view_count': 'N/A',
                                'thumbnail': thumbnail
                            })
                
                except Exception as parse_error:
                    print(f"Error parseando resultados: {parse_error}")
                    return []
                
                return results
            else:
                print("No se encontró datos JSON en la página")
                return []
        else:
            print(f"Error HTTP: {response.status_code}")
            return []
            
    except Exception as e:
        print(f"Error en búsqueda alternativa: {e}")
        return []

def test_alternative_search():
    """Probar búsqueda alternativa"""
    print("Probando búsqueda alternativa...")
    
    results = search_youtube_alternative("imagine dragons", 3)
    
    if results:
        print(f"EXITO: Encontrados {len(results)} resultados")
        for i, result in enumerate(results, 1):
            print(f"{i}. {result['title']} - {result['uploader']}")
    else:
        print("ERROR: No se encontraron resultados")

if __name__ == "__main__":
    test_alternative_search()
