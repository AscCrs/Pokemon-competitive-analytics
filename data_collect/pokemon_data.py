import requests
import pandas as pd
from tqdm import tqdm
import time

# Diccionario con las generaciones y sus rangos de IDs
generaciones = {
    'Generación 1': (1, 151),
    'Generación 2': (152, 251),
    'Generación 3': (252, 386),
    'Generación 4': (387, 493),
    'Generación 5': (494, 649),
    'Generación 6': (650, 721),
    'Generación 7': (722, 809),
    'Generación 8': (810, 905),
    'Generación 9': (906, 1025)
}

def obtener_info_pokemon(id_pokemon):
    """Obtiene información de un Pokémon por su ID"""
    url = f"https://pokeapi.co/api/v2/pokemon/{id_pokemon}/"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        
        # Extraer información relevante
        pokemon_info = {
            'id': data['id'],
            'nombre': data['name'],
            'altura': data['height'] / 10,  # Convertir a metros
            'peso': data['weight'] / 10,    # Convertir a kg
            'tipos': [tipo['type']['name'] for tipo in data['types']],
            'stats': {stat['stat']['name']: stat['base_stat'] for stat in data['stats']},
            'habilidades': [habilidad['ability']['name'] for habilidad in data['abilities']],
            'movimientos': len(data['moves']),
            'imagen': data['sprites']['other']['official-artwork']['front_default']
        }
        return pokemon_info
    else:
        print(f"Error al obtener información del Pokémon {id_pokemon}")
        return None

def crear_dataframe_generacion(generacion, inicio, fin):
    """Crea un DataFrame con todos los Pokémon de una generación"""
    pokemones = []
    
    print(f"\nObteniendo información de la {generacion} (IDs {inicio}-{fin})...")
    
    for id_pokemon in tqdm(range(inicio, fin + 1), desc=generacion):
        info = obtener_info_pokemon(id_pokemon)
        if info:
            pokemones.append(info)
        time.sleep(0.1)  # Para no saturar la API
    
    # Crear DataFrame
    df = pd.DataFrame(pokemones)
    
    # Expandir los tipos en columnas separadas
    df['tipo_1'] = df['tipos'].apply(lambda x: x[0] if len(x) > 0 else None)
    df['tipo_2'] = df['tipos'].apply(lambda x: x[1] if len(x) > 1 else None)
    
    # Expandir los stats en columnas separadas
    stats_df = pd.json_normalize(df['stats'])
    df = pd.concat([df.drop(['stats', 'tipos'], axis=1), stats_df], axis=1)
    
    # Reordenar columnas
    column_order = ['id', 'nombre', 'tipo_1', 'tipo_2', 'altura', 'peso', 
                    'hp', 'attack', 'defense', 'special-attack', 
                    'special-defense', 'speed', 'movimientos', 
                    'habilidades', 'imagen']
    df = df[column_order]
    
    # Renombrar columnas de stats para mayor claridad
    df = df.rename(columns={
        'hp': 'HP',
        'attack': 'Ataque',
        'defense': 'Defensa',
        'special-attack': 'Ataque Especial',
        'special-defense': 'Defensa Especial',
        'speed': 'Velocidad'
    })
    
    return df

def guardar_dataframes(generaciones_df):
    """Guarda los DataFrames en archivos CSV y Excel"""
    with pd.ExcelWriter('pokemons_por_generacion.xlsx') as writer:
        for generacion, df in generaciones_df.items():
            # Guardar en Excel (una hoja por generación)
            df.to_excel(writer, sheet_name=generacion, index=False)
            
            # Guardar en CSV individual
            nombre_archivo = f"pokemon_{generacion.lower().replace(' ', '_')}.csv"
            df.to_csv(nombre_archivo, index=False, encoding='utf-8')
    
    print("\n¡Todos los datos han sido guardados exitosamente!")
    print("Archivos creados:")
    print("- pokemons_por_generacion.xlsx (contiene todas las generaciones)")
    for generacion in generaciones_df.keys():
        nombre_archivo = f"pokemon_{generacion.lower().replace(' ', '_')}.csv"
        print(f"- {nombre_archivo}")

def main():
    generaciones_df = {}
    
    for generacion, (inicio, fin) in generaciones.items():
        df = crear_dataframe_generacion(generacion, inicio, fin)
        generaciones_df[generacion] = df
    
    # Mostrar resumen
    print("\nResumen de Pokémon por generación:")
    for generacion, df in generaciones_df.items():
        print(f"{generacion}: {len(df)} Pokémon")
    
    # Guardar los datos
    guardar_dataframes(generaciones_df)

if __name__ == "__main__":
    main()