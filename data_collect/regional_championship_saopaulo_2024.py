import requests
from bs4 import BeautifulSoup
import pandas as pd

# URL del torneo
url = 'https://labs.limitlesstcg.com/0009/standings'

# Realizar la solicitud HTTP
headers = {'User-Agent': 'Mozilla/5.0'}
response = requests.get(url, headers=headers)

# Verificar que la solicitud fue exitosa
if response.status_code != 200:
    print(f"Error al acceder a la página: {response.status_code}")
    exit()

# Parsear el contenido HTML
soup = BeautifulSoup(response.content, 'html.parser')

# Buscar todas las filas de la tabla
rows = soup.find_all('tr', class_='day2 topcut')
rows = rows + soup.find_all('tr', class_='day2')

# Lista para almacenar los datos
data = []

# Recorrer cada fila
for row in rows:
    cols = row.find_all('td')
    if len(cols) < 8:
        continue

    # Extraer datos básicos
    position = cols[0].get_text(strip=True)
    name = cols[1].get_text(strip=True)
    points = cols[3].get_text(strip=True)
    record = cols[4].get_text(strip=True)
    opw = cols[5].get_text(strip=True)
    oopw = cols[6].get_text(strip=True)

    # Extraer nombres de Pokémon del atributo alt en las imágenes dentro del deck
    pokemon_imgs = cols[7].find_all('img')
    pokemons = [img['alt'] for img in pokemon_imgs if img.has_attr('alt')]

    data.append({
        'Posición': position,
        'Jugador': name,
        'Puntos': points,
        'Record': record,
        'OPW%': opw,
        'OOPW%': oopw,
        'Pokémon del Deck': ', '.join(pokemons)
    })

# Crear el DataFrame
df = pd.DataFrame(data)

# Guardar en CSV
df.to_csv('estadisticas_pokemon_2024_saopaulo.csv', index=False, encoding='utf-8')

print("Scraping completado. Archivo guardado como 'estadisticas_pokemon_2024_saopaulo.csv'")
