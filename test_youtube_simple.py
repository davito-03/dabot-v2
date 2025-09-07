"""
Prueba simple de YouTube con yt-dlp
"""

import yt_dlp

def test_youtube():
    print("Probando busqueda en YouTube...")
    
    try:
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': True,
            'default_search': 'ytsearch1:',
            'skip_download': True,
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info("imagine dragons", download=False)
            
            if 'entries' in info and info['entries']:
                print("EXITO: Busqueda funcional")
                print(f"Encontrado: {info['entries'][0]['title']}")
                return True
            else:
                print("ERROR: No se encontraron resultados")
                return False
                
    except Exception as e:
        print(f"ERROR: {str(e)}")
        return False

if __name__ == "__main__":
    test_youtube()
