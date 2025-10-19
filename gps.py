"""
gps.py

Aplicación GPS que permite calcular rutas en el callejero de Madrid.
"""

import networkx as nx
import matplotlib.pyplot as plt
import osmnx as ox
import pandas as pd
from callejero import (
    carga_callejero,
    carga_grafo,
    procesa_grafo,
    busca_direccion,
    MAX_SPEEDS
)
from grafo_pesado import camino_minimo
from math import degrees, acos, sqrt

KMH_TO_MPS = 3.6  # Conversión de km/h a m/s

def calcula_peso_longitud(G: nx.Graph, u, v) -> float:
    """Calcula el peso de una arista basado en su longitud."""
    return G[u][v].get("length", 0)


def calcula_peso_tiempo(G: nx.Graph, u, v) -> float:
    """Calcula el peso de una arista basado en el tiempo estimado de viaje.
       Se tienen en cuenta los distintos casos hallados en el fichero madrid.graphml:
       Para maxspeed puede ser:
            - Solo un entero
            - Una lista de enteros. Nos hemos quedado con el primero (el más pequeño, velocidad mínima).
            - Hay solo una instancia en la que esta escrito de esta forma: 50|30. En este caso salta una adevertencia, y se utiliza la velocidad 50 km/h.
       Para highway puede ser:
            - Solo un string
            - Una lista de strings. Nos hemos quedado con la primera. 
    """

    longitud = G[u][v].get("length", 0) # longitud de la arista

    # Obtener el tipo de carretera (highway) y manejar listas
    raw_highway = G[u][v].get("highway", "")

    if isinstance(raw_highway, list):
        # Tomar el primer tipo de carretera si es una lista
        highway = raw_highway[0] if raw_highway else ""
    else:
        highway = raw_highway

    # Obtener maxspeed considerando el tipo de carretera
    velocidad_maxima = G[u][v].get("maxspeed", MAX_SPEEDS.get(highway, 50))

    # Manejar maxspeed como lista o string
    if isinstance(velocidad_maxima, list):
        try:
            velocidad_maxima = min(float(speed.split()[0]) if isinstance(speed, str) else float(speed) for speed in velocidad_maxima)
        except Exception:
            print(f"Advertencia: Lista de maxspeed inválida en la arista ({u}, {v}): {velocidad_maxima}")
            velocidad_maxima = 50  # Valor predeterminado
    elif isinstance(velocidad_maxima, str):
        try:
            velocidad_maxima = float(velocidad_maxima.split()[0])
        except ValueError:
            print(f"Advertencia: maxspeed inválido en la arista ({u}, {v}): {velocidad_maxima}")
            velocidad_maxima = 50
    else:
        try:
            velocidad_maxima = float(velocidad_maxima)
        except Exception:
            print(f"Advertencia: maxspeed inválido en la arista ({u}, {v}): {velocidad_maxima}")
            velocidad_maxima = 50

    # Calcular tiempo basado en longitud y velocidad maxima
    return float(longitud) / (velocidad_maxima / KMH_TO_MPS)


def calcula_peso_tiempo_esperado(G: nx.Graph, u, v) -> float:
    """Calcula el peso de una arista considerando tiempos de semáforo."""
    tiempo_base = calcula_peso_tiempo(G, u, v)
    prob_parada = 0.8
    tiempo_semáforo = 30
    return tiempo_base + prob_parada * tiempo_semáforo


def encuentra_nodo_mas_cercano(G: nx.Graph, lat: float, lon: float) -> object:
    """Encuentra el nodo más cercano a unas coordenadas."""
    menor_distancia = float("inf")
    nodo_cercano = None

    # Iterar todos los nodos y encontrar el que este mas cerca de la latituda y longitud dad.
    for nodo, data in G.nodes(data=True):
        distancia = ((data["y"] - lat) ** 2 + (data["x"] - lon) ** 2) ** 0.5
        if distancia < menor_distancia:
            menor_distancia = distancia
            nodo_cercano = nodo

    return nodo_cercano


def calcular_angulo_y_giro(p1: tuple, p2: tuple, p3: tuple, umbral_angulo=5):
    """
    Calcula el ángulo y determina si es un giro a la izquierda, derecha o movimiento recto.
    """

    # Vectores p1 -> p2 y p2 -> p3
    v1 = (p2[0] - p1[0], p2[1] - p1[1])
    v2 = (p3[0] - p2[0], p3[1] - p2[1])

    # Producto escalar y normas
    producto_escalar = v1[0] * v2[0] + v1[1] * v2[1]
    norma_v1 = sqrt(v1[0]**2 + v1[1]**2)
    norma_v2 = sqrt(v2[0]**2 + v2[1]**2)

    if norma_v1 == 0 or norma_v2 == 0:
        return "continúe recto"

    # Calcular el ángulo en grados
    cos_theta = producto_escalar / (norma_v1 * norma_v2)
    cos_theta = max(-1, min(1, cos_theta))  # Asegurar que esté en el rango [-1, 1]
    angulo = degrees(acos(cos_theta))

    # Producto cruzado para determinar el sentido del giro
    producto_cruzado = v1[0] * v2[1] - v1[1] * v2[0]

    # Decidir el tipo de giro
    if angulo < umbral_angulo:
        return "continúe recto"
    elif producto_cruzado > 0:
        return "gire a la izquierda"
    else:
        return "gire a la derecha"



def genera_instrucciones(G: nx.Graph, ruta: list) -> list:
    """
    Genera instrucciones detalladas para navegar por una ruta.
    
    Args:
        G (nx.Graph): Grafo con nodos y aristas que representan la red vial.
        ruta (list): Lista de nodos que componen la ruta.
    
    Returns:
        list: Lista de instrucciones de navegación.
    """
    instrucciones = []
    distancia_acumulada = 0
    calle_actual = None

    for i in range(len(ruta) - 1):
        u, v = ruta[i], ruta[i + 1]
        calle_siguiente = G[u][v].get("name", "vía desconocida")
        if isinstance(calle_siguiente, list):  # Si hay múltiples nombres, tomamos el último.
            calle_siguiente = calle_siguiente[-1]
        distancia = G[u][v].get("length", 0)

        # Primera iteración: establecer calle_actual
        if calle_actual is None:
            calle_actual = calle_siguiente
            distancia_acumulada += distancia
            continue

        # Si la calle cambia, ver si hay giro y hacia que direccion
        if calle_actual != calle_siguiente:
            instrucciones.append(f"Continúe por {calle_actual} durante {int(distancia_acumulada)} metros.")

            # Calcular giro si hay un tercer nodo
            if i + 1 < len(ruta) - 1:
                p1 = (G.nodes[ruta[i - 1]]['x'], G.nodes[ruta[i - 1]]['y']) if i > 0 else (0, 0)
                p2 = (G.nodes[u]['x'], G.nodes[u]['y'])
                p3 = (G.nodes[v]['x'], G.nodes[v]['y'])
                giro = calcular_angulo_y_giro(p1, p2, p3)
                instrucciones.append(f"{giro} hacia {calle_siguiente}.")

            # Reiniciar acumulador
            calle_actual = calle_siguiente
            distancia_acumulada = distancia
        else:
            # Si seguimos en la misma calle, acumular distancia
            distancia_acumulada += distancia

    # Instrucción final para la última calle
    if calle_actual:
        instrucciones.append(f"Continúe por {calle_actual} durante {int(distancia_acumulada)} metros hasta su destino.")

    return instrucciones


def resalta_ruta(G: nx.Graph, ruta: list):
    """Dibuja el grafo resaltando la ruta utilizando OSMnx.
       Hemos ajustado los colores de los nodos y las aristas, al igual que su intensidad (alpha) para mejor visualización.
    """

    print("Pintando el mapa con la ruta resaltada. Esto puede llevar unos segundos...")
    print("Para ver la ruta mejor, tocar la lupa arriba la izquierda y hacer un cuadrilátero incluyendo el camino rojo.")

    pos = {nodo: (datos['x'], datos['y']) for nodo, datos in G.nodes(data=True) if 'x' in datos and 'y' in datos}

    # Dibujar el grafo completo en gris
    plt.figure(figsize=(12, 8))
    nx.draw_networkx_nodes(G, pos, node_size=0.1, node_color='lightgray')
    nx.draw_networkx_edges(G, pos, edge_color='lightgray', width=0.5, alpha=0.3)

    # Extraer las aristas de la ruta
    ruta_edges = [(ruta[i], ruta[i + 1]) for i in range(len(ruta) - 1)]
    nx.draw_networkx_edges(G, pos, edgelist=ruta_edges, edge_color='red', width=1.5)
    plt.title("Mapa de Madrid con ruta resaltada")
    plt.axis('off')
    plt.show()






def obtener_coordenadas(direccion: str, callejero: pd.DataFrame):
    """Obtiene las coordenadas de una dirección en el callejero."""
    try:
        return busca_direccion(direccion, callejero)
    except Exception as e:
        print(f"Error al buscar la dirección '{direccion}': {e}")
        print("Sugerencia: Use el formato 'Calle de Nombre, Número'. Ejemplo: 'Calle de Alcalá, 25'")
        return None


def calcular_y_mostrar_ruta(grafo, origen, destino, peso_funcion):
    """Calcula la ruta entre dos nodos y muestra las instrucciones y visualización."""
    try:
        # Calcular ruta segun la opcion elegida (varía peso_funcion)
        ruta = camino_minimo(grafo, peso_funcion, origen, destino)
        print("Ruta calculada exitosamente.")
        
        # Generar instrucciones para el usuario (lista de strings)
        instrucciones = genera_instrucciones(grafo, ruta)
        print("\nInstrucciones para la ruta:")
        for instruccion in instrucciones:
            print("-", instruccion)
        print()

        # Pintar el mapa con la ruta resaltada 
        resalta_ruta(grafo, ruta)
    except Exception as e:
        print(f"Error al calcular la ruta: {e}")


def main():
    """Programa principal"""

    print("Cargando datos...")
    callejero = carga_callejero()
    grafo = procesa_grafo(carga_grafo())
    print("Datos cargados correctamente. Puede empezar a planificar su ruta.")

    while True:
        origen_input = input("Ingrese la dirección de origen (o presione Enter para salir): ")
        if not origen_input:
            break

        lat_lon_origen = obtener_coordenadas(origen_input, callejero)
        if not lat_lon_origen:
            continue

        destino_input = input("Ingrese la dirección de destino (o presione Enter para salir): ")
        if not destino_input:
            break

        lat_lon_destino = obtener_coordenadas(destino_input, callejero)
        if not lat_lon_destino:
            continue
            
        # Nodos en el grafo mas cercanos a las longitudes y latitudes encontradas en callejero
        origen = encuentra_nodo_mas_cercano(grafo, *lat_lon_origen)
        destino = encuentra_nodo_mas_cercano(grafo, *lat_lon_destino)

        print("Seleccione el modo de cálculo:")
        print("1. Ruta más corta (distancia)")
        print("2. Ruta más rápida (tiempo)")
        print("3. Ruta más rápida con semáforos (tiempo esperado)")
        modo = input("Ingrese una opción (1/2/3): ")

        peso_funcion = {"1": calcula_peso_longitud, "2": calcula_peso_tiempo, "3": calcula_peso_tiempo_esperado}.get(modo)
        if not peso_funcion:
            print("Opción no válida. Intente nuevamente.")
            continue

        calcular_y_mostrar_ruta(grafo, origen, destino, peso_funcion)

    print("Gracias por usar nuestro GPS, ¡Nos vemos en tu próximo viaje!")

if __name__ == "__main__":
   main()
