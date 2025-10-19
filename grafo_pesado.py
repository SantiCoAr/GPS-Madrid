from typing import List,Tuple,Dict,Callable,Union
import networkx as nx
import sys

import heapq #Librería para la creación de colas de prioridad

INFTY=sys.float_info.max #Distincia "infinita" entre nodos de un grafo

"""
En las siguientes funciones, las funciones de peso son funciones que reciben un grafo o digrafo y dos vértices y devuelven un real (su peso)
Por ejemplo, si las aristas del grafo contienen en sus datos un campo llamado 'valor', una posible función de peso sería:

def mi_peso(G:nx.Graph,u:object, v:object):
    return G[u][v]['valor']

y, en tal caso, para calcular Dijkstra con dicho parámetro haríamos

camino=dijkstra(G,mi_peso,origen, destino)


"""

def dijkstra(G:Union[nx.Graph, nx.DiGraph], peso:Union[Callable[[nx.Graph,object,object],float], Callable[[nx.DiGraph,object,object],float]], origen:object)-> Dict[object,object]:
    """ Calcula un Árbol de Caminos Mínimos para el grafo pesado partiendo
    del vértice "origen" usando el algoritmo de Dijkstra. Calcula únicamente
    el árbol de la componente conexa que contiene a "origen".
    
    Args:
        origen (object): vértice del grafo de origen
    Returns:
        Dict[object,object]: Devuelve un diccionario que indica, para cada vértice alcanzable
            desde "origen", qué vértice es su padre en el árbol de caminos mínimos.
    Raises:
        TypeError: Si origen no es "hashable".
    Example:
        Si G.dijksra(1)={2:1, 3:2, 4:1} entonces 1 es padre de 2 y de 4 y 2 es padre de 3.
        En particular, un camino mínimo desde 1 hasta 3 sería 1->2->3.
    """
    if not isinstance(origen, (str, int, tuple)):
        raise TypeError("El nodo origen debe ser hashable (str, int, tuple, etc.).")
    if origen not in G:
        raise ValueError("El vértice origen no está en el grafo.")
    
    padre = {v: None for v in G.nodes}
    visitado = {v: False for v in G.nodes}
    dist = {v: float('inf') for v in G.nodes}
    dist[origen] = 0
    cola = [(0, str(origen))]  # Convertimos el nodo a cadena para evitar errores de comparación
    
    while cola:
        d, v = heapq.heappop(cola)
        v = int(v) if v.isdigit() else v  # Convertimos de vuelta al tipo original
        if not visitado[v]:
            visitado[v] = True
            for u in G.neighbors(v):
                if dist[u] > dist[v] + peso(G, v, u):
                    dist[u] = dist[v] + peso(G, v, u)
                    padre[u] = v
                    heapq.heappush(cola, (dist[u], str(u)))  # Convertimos u a cadena para la cola
    
    return padre

def camino_minimo(G, peso, origen, destino):
    """
    Calcula el camino mínimo desde el vértice origen hasta el vértice
    destino utilizando el algoritmo de Dijkstra.
    
    Args:
        G (nx.Graph o nx.Digraph): Grafo dirigido o no dirigido.
        peso (Callable): Función que recibe un grafo y dos vértices, y devuelve el peso de la arista que los conecta.
        origen (object): Vértice del grafo de origen.
        destino (object): Vértice del grafo de destino.
    
    Returns:
        List[object]: Devuelve una lista con los vértices del camino más corto entre origen y destino.
                      El primer elemento es el origen y el último es el destino.
    
    Raises:
        TypeError: Si origen o destino no son "hashable".
        ValueError: Si no existe un camino entre origen y destino.
    """
    if not isinstance(origen, (str, int, tuple)) or not isinstance(destino, (str, int, tuple)):
        raise TypeError("Los nodos origen y destino deben ser hashables (str, int, tuple, etc.).")

    padre = dijkstra(G, peso, origen)
    if padre[destino] is None:
        raise ValueError("No existe un camino entre el origen y el destino.")
    
    camino = []
    actual = destino
    while actual is not None:
        camino.append(actual)
        actual = padre[actual]
    
    return camino[::-1]


def prim(G, peso):
    """
    Implementación del algoritmo de Prim para calcular el Árbol Abarcador Mínimo (MST).

    Args:
        G (nx.Graph): Grafo no dirigido ponderado.
        peso (Callable): Función que recibe el grafo y dos nodos, y devuelve el peso de la arista que los conecta.

    Returns:
        Dict[object, object]: Diccionario que indica, para cada nodo alcanzable desde el origen,
                              qué nodo es su padre en el Árbol Abarcador Mínimo.

    Raises:
        ValueError: Si el grafo no es conexo.
    """
    padre = {v: None for v in G.nodes}
    coste_minimo = {v: float('inf') for v in G.nodes}
    visitado = set()
    cola = []

    nodo_inicial = list(G.nodes)[0]
    coste_minimo[nodo_inicial] = 0
    heapq.heappush(cola, (0, str(nodo_inicial)))  

    while cola:
        _, v = heapq.heappop(cola)
        v = int(v) if v.isdigit() else v 

        if v in visitado:
            continue
        visitado.add(v)

        for vecino in G.neighbors(v):
            w_vx = peso(G, v, vecino)
            if vecino not in visitado and w_vx < coste_minimo[vecino]:
                coste_minimo[vecino] = w_vx
                padre[vecino] = v
                heapq.heappush(cola, (coste_minimo[vecino], str(vecino)))  

    if len(visitado) != len(G.nodes):
        raise ValueError("El grafo no es conexo. El MST no puede cubrir todos los nodos.")

    return padre

def kruskal(G, peso):
    """
    Implementación del algoritmo de Kruskal para calcular el Árbol Abarcador Mínimo (MST).

    Args:
        G (nx.Graph): Grafo no dirigido ponderado.
        peso (Callable): Función que recibe el grafo y dos nodos, y devuelve el peso de la arista que los conecta.

    Returns:
        List[Tuple[object, object]]: Lista de aristas en el MST.

    Raises:
        ValueError: Si el grafo no es conexo.
    """
    aristas = sorted(G.edges(data=True), key=lambda edge: peso(G, edge[0], edge[1]))
    componentes = {v: {v} for v in G.nodes}
    aristas_aam = []

    while aristas:
        u, v, datos = aristas.pop(0)
        if componentes[u] != componentes[v]:
            aristas_aam.append((u, v))
            nueva_componente = componentes[u] | componentes[v]
            for nodo in nueva_componente:
                componentes[nodo] = nueva_componente

    return aristas_aam