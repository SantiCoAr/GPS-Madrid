"""
callejero.py

Matemática Discreta - IMAT
ICAI, Universidad Pontificia Comillas

Grupo: GPxxx
Integrantes:
    - XX
    - XX

Descripción:
Librería con herramientas y clases auxiliares necesarias para la representación de un callejero en un grafo.

Complétese esta descripción según las funcionalidades agregadas por el grupo.
"""

import osmnx as ox
import networkx as nx
import pandas as pd
import os
import re
import matplotlib.pyplot as plt
from typing import Tuple

STREET_FILE_NAME="direcciones.csv"

PLACE_NAME = "Madrid, Spain"
MAP_FILE_NAME="madrid.graphml"

MAX_SPEEDS={'living_street': '20',
 'residential': '30',
 'primary_link': '40',
 'unclassified': '40',
 'secondary_link': '40',
 'trunk_link': '40',
 'secondary': '50',
 'tertiary': '50',
 'primary': '50',
 'trunk': '50',
 'tertiary_link':'50',
 'busway': '50',
 'motorway_link': '70',
 'motorway': '100'}


class ServiceNotAvailableError(Exception):
    "Excepción que indica que la navegación no está disponible en este momento"
    pass


class AdressNotFoundError(Exception):
    "Excepción que indica que una dirección buscada no existe en la base de datos"
    pass


############## Parte 2 ##############

def convertir_coordenada(coordenada: str) -> float:
    """
    Convierte una cadena de texto que representa una coordenada geográfica
    en grados, minutos y segundos a un número en grados decimales.

    Args:
        coordenada (str): Cadena de texto de la forma "3º42’24.69”W".
    
    Returns:
        float: Coordenada convertida a grados decimales.
    """
    # Expresión regular para extraer grados, minutos, segundos y orientación
    patron = r"(\d+)°(\d+)'([\d.]+)(?:'') ([NSEW])"
    match = re.match(patron, coordenada)

    if not match:
        raise ValueError(f"Coordenada no válida: {coordenada}")

    # Extraer los componentes
    grados = int(match.group(1))
    minutos = int(match.group(2))
    segundos = float(match.group(3))
    orientacion = match.group(4)

    # Convertir a grados decimales
    decimal = grados + (minutos / 60) + (segundos / 3600)

    # Hacer negativo si la orientación es S o W
    if orientacion in ['S', 'W']:
        decimal *= -1

    return decimal


def carga_callejero() -> pd.DataFrame:
    """ Función que carga el callejero de Madrid, lo procesa y devuelve
    un DataFrame con los datos procesados
    
    Args: None
    Returns:
        Dict[object,object]: Devuelve un diccionario que indica, para cada vértice del
            grafo, qué vértice es su padre en el árbol abarcador mínimo.
    Raises:
        FileNotFoundError si el fichero csv con las direcciones no existe
    """
    try:
        # Ruta al fichero CSV
        file_path = "direcciones.csv"

        # Cargar las columnas necesarias del archivo CSV
        columns = ["VIA_CLASE", "VIA_PAR", "VIA_NOMBRE", "NUMERO", "LATITUD", "LONGITUD"]
        df = pd.read_csv(file_path, sep=";", encoding="latin1", usecols=columns)
        
        # Convertir coordenadas a grados decimales
        df["LATITUD"] = df["LATITUD"].apply(convertir_coordenada)
        df["LONGITUD"] = df["LONGITUD"].apply(convertir_coordenada)

        # Crear la columna DIRECCION con el objetivo de facilitar la busqueda de dirección de busca_direccion()
        df["DIRECCION"] = df.apply(
            lambda row: f"{row['VIA_CLASE']} {row['VIA_PAR']} {row['VIA_NOMBRE']}, {row['NUMERO']}".strip()
            if pd.notna(row["VIA_PAR"]) else
            f"{row['VIA_CLASE']} {row['VIA_NOMBRE']}, {row['NUMERO']}".strip(), 
            axis=1
        )

        return df

    except FileNotFoundError as e:
        raise FileNotFoundError("El fichero 'direcciones.csv' no existe. Por favor, verifique la ruta del archivo.") from e


def busca_direccion(direccion:str, callejero:pd.DataFrame) -> Tuple[float,float]:
    """ Función que busca una dirección, dada en el formato
        calle, numero
    en el DataFrame callejero de Madrid y devuelve el par (latitud, longitud) en grados de la
    ubicación geográfica de dicha dirección
    
    Args:
        direccion (str): Nombre completo de la calle con número, en formato "Calle, num"
        callejero (DataFrame): DataFrame con la información de las calles
    Returns:
        Tuple[float,float]: Par de float (latitud,longitud) de la dirección buscada, expresados en grados
    Raises:
        AdressNotFoundError: Si la dirección no existe en la base de datos
    Example:
        busca_direccion("Calle de Alberto Aguilera, 23", data)=(40.42998055555555,3.7112583333333333)
        busca_direccion("Calle de Alberto Aguilera, 25", data)=(40.43013055555555,3.7126916666666667)
    """
    # Normalizar la dirección (ignorar mayúsculas/minúsculas)
    # El usuario deberá poner la dirección completa con una coma antes del número
    direccion_normalizada = direccion.strip().upper()

    # Filtrar el DataFrame para encontrar la dirección
    filtro = callejero["DIRECCION"] == direccion_normalizada
    resultado = callejero[filtro]

    # Si no se encuentra la dirección, lanzar error
    if resultado.empty:
        raise AdressNotFoundError(
            f"La dirección '{direccion}' no se encontró en el callejero. "
            f"Asegúrese de escribirla en el formato exacto, como aparece en la columna DIRECCION, "
            f"por ejemplo: 'Calle de Nombre, Número'."
        )

    # Extraer latitud y longitud de la primera coincidencia
    latitud = resultado.iloc[0]["LATITUD"]
    longitud = resultado.iloc[0]["LONGITUD"]

    return latitud, longitud


############## Parte 4 ##############


def carga_grafo() -> nx.MultiDiGraph:
    """Función que recupera el quiver de calles de Madrid de OpenStreetMap.
    
    Args:
        None
    
    Returns:
        nx.MultiDiGraph: Quiver de las calles de Madrid.
    
    Raises:
        ServiceNotAvailableError: Si no es posible recuperar el grafo de OpenStreetMap.
    """
    fichero = 'madrid.graphml'
    try:
        if os.path.exists(fichero):
            print("Cargando grafo desde el archivo local...")
            grafo = ox.load_graphml(fichero)
            
        else:
            print("Descargando grafo de OpenStreetMap...")
            grafo = ox.graph_from_place("Madrid, Spain", network_type='drive')
            ox.save_graphml(grafo, fichero)
            
        # Descomentar línea para ver como se ve el grafo sin procesar
        # fig, ax = ox.plot_graph(grafo, node_size=0, edge_linewidth=0.5)
        return grafo
    except Exception as e:
        raise ServiceNotAvailableError(f"No se pudo recuperar el grafo: {str(e)}") from e


def procesa_grafo(multidigrafo: nx.MultiDiGraph) -> nx.DiGraph:
    """
    Función que convierte un MultiDiGraph en un DiGraph simplificado sin bucles,
    utilizando la función convert.to_digraph de OSMnx.

    Args:
        multidigrafo (nx.MultiDiGraph): Grafo dirigido con múltiples aristas (MultiDiGraph)
            obtenido de OpenStreetMap.

    Returns:
        nx.DiGraph: Grafo dirigido (DiGraph) simplificado, sin bucles ni aristas redundantes.
    """
    try:
        # Convertir a digrafo y eliminar bucles
        digrafo = ox.utils_graph.convert.to_digraph(multidigrafo)
        bucles = list(nx.selfloop_edges(digrafo)) 
        digrafo.remove_edges_from(bucles)  

        # print(f"Procesamiento completado: {len(bucles)} bucles eliminados.")

        return digrafo

    except Exception as e:
        raise RuntimeError(f"Error al procesar el grafo: {str(e)}") from e
