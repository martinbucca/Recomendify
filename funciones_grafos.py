from grafo import Grafo
from collections import deque
import heapq
from random import randint

#*******************************************************************
#                     FUNCIONES AUXILIARES
#*******************************************************************

# Recibe un grafo, un diccionario con el padre de cada vertice en el camino, el vertice origen del camino y el destino 
# y devuelve una lista ordenada que representa el camino desde el origen hasta el final, donde el origen es el
# primer elemento de la lista y el destino el ultimo.
# Complejidad: O(C) (C es el costo del camino, es decir, la cantidad de aristas que recorre el camino pasado)
def reconstruir_camino(grafo, padre, origen, destino = None):
    if not padre: return None
    if not destino: destino = origen
    camino = []
    camino.append(destino)
    v = padre[destino]
    while v != origen:
        camino.insert(0, v)
        v = padre[v]
    camino.insert(0, v)
    return camino

#*******************************************************************
#                         CAMINO MÍNIMO
#*******************************************************************

# Recibe un grafo no pesado dos vertices "v" y "w" y devuelve un diccionario con los padres de cada vertice que esta
# en el camino minimo entre esos dos vertices, siendo "v" el origen y "w" el destino.
# Complejidad: O(V + E)
def camino_minimo_no_pesado(grafo, v, w):
    padre = {}
    visitados = set()
    visitados.add(v)
    q = deque()
    q.append(v)
    while len(q) != 0:
        x = q.popleft()
        for y in grafo.adyacentes(x):
            if y not in visitados:
                q.append(y)
                padre[y] = x
                if y == w: return padre
                visitados.add(y)
    return None

# Recibe un grafo no pesado, dos vertices "v" y "w"" y devuelve una lista con uno de los caminos mas cortos para ir 
# desde "v" hasta "w"
def camino_minimo(grafo, v, w):
    padre = camino_minimo_no_pesado(grafo, v, w)
    return reconstruir_camino(grafo, padre, v, w)

#*******************************************************************
#                     CICLO DE N VERTICES
#*******************************************************************

# Recibe un grafo, el origen del ciclo, el anterior del vertice actual, el largo del ciclo n, el largo del camino 
# actual, los vertices visitados actuales y un diccionario de los padres de los vertices visitados. Si se llego al 
# origen y el largo del camino es igual al pedido se devuelve una lista con el camino. Si no existe el ciclo de largo
# n pedido se devuelve False.
# Complejidad: O(V^n)
def _ciclo_largo_n(grafo, origen, anterior, n, saltos, visitados, padre):
    if saltos > n: return False
    for w in grafo.adyacentes(anterior): 
        if w == origen:
            if saltos == n:
                padre[origen] = anterior
                return reconstruir_camino(grafo, padre, origen)
        if w not in visitados:
            padre_copia = padre.copy()
            padre_copia[w] = anterior
            visitados_copia = visitados.copy()
            visitados_copia.add(w)
            camino = _ciclo_largo_n(grafo, origen, w, n, saltos+1, visitados_copia, padre_copia)
            if not camino: continue
            return camino
    return False

# Devuelve una lista con el ciclo de largo n que vuelve al vertice origen. De no existir devuelve False
def ciclo_de_largo_n(grafo, origen, n):
    if n < 1: return False
    visitados = set()
    visitados.add(origen)
    padre = {}
    padre[origen] = None
    camino = _ciclo_largo_n(grafo, origen, origen, n, 1, visitados, padre)
    return camino

#*******************************************************************
#                       TODOS EN RANGO N
#*******************************************************************

# Recibe un grafo un vertice y la distancia en saltos n que deben estar los vertices desados del vertice v y devuelve
# la cantidad de vertices que se encuentran a esa distancia n
# Complejidad: O(V + E)
def cantidad_de_rango_n(grafo, v, n):
    distancias = {}
    distancias[v] = 0
    q = deque()
    q.append(v)
    while len(q) != 0:
        x = q.popleft()
        if distancias[x] > n: 
            continue
        for y in grafo.adyacentes(x):
            if y not in distancias:
                q.append(y)
                distancias[y] = distancias[x] + grafo.peso_arista(x, y)
    vertices_a_distancia_n = set()
    for vertice, distancia in distancias.items():
        if distancia == n: vertices_a_distancia_n.add(vertice)
    return len(vertices_a_distancia_n)

#*******************************************************************
#                     N VERTICES MAS IMPORTANTES
#*******************************************************************

# Recibe un grafo, un vertice v, un coeficiente de amortiguacion y un diccionario de pageranks de vertices en el grafo
# y devuelve el numero que representa la importancia del vertice dentro del grafo de acuerdo a la formula de pagerank
def page_rank_vertice(grafo, v, amortiguacion, page_ranks):
    sumatoria_ady = 0
    for w in grafo.adyacentes(v):
        sumatoria_ady += page_ranks.get(w, 0.1) / len(grafo.adyacentes(w))
    rank = (1 -  amortiguacion) / len(grafo) +  amortiguacion * sumatoria_ady
    return rank

# Recibe un grafo, un coeficiente de amortiguacion y un numero deseado de iteraciones para el algoritmo pageranks
# y devuelve un diccionario con los vertices de clave, y sus valores de importancia segun la formula de pagerank 
# como valor. El coeficioente de amortiguación representa la probabilidad de pasar de un vertice a otro en vez de
# solo buscarlo en una lista. A mayor cantidad de iteraciones, el algoritmo se vuelve más preciso, pero toma más 
# tiempo en terminar de ejecutarse
def page_ranks(grafo, amortiguacion, iteraciones):
    page_ranks = {}
    for i in range(iteraciones):
        for v in grafo.obtener_vertices():
            page_ranks[v] = page_rank_vertice(grafo, v, amortiguacion, page_ranks)
    return page_ranks

# Recibe un grafo, un coeficiente de amortiguacion, un numero deseado de iteraciones y la cantidad de elementos que 
# se quiere devolver y devuelve los n vertices mas importances del grafo segun el algoritmo pageranks
def n_vertices_mas_importantes(grafo, amortiguacion, iteraciones, n):
    if n > len(grafo): n = len(grafo)
    pr = page_ranks(grafo, amortiguacion, iteraciones)
    return heapq.nlargest(n, pr, key = pr.get)

#*******************************************************************
#                     RECOMENDACION/ VERTICES SIMILARES
#*******************************************************************

# Realiza un camino aleatorio desde el vertice "v", recorriendo "largo" cantidad de vertices. Le asigna un 1 al 
# vertice "v" como valor. Cada vez que el camino pasa de un vertice a otro, el vertice origen le transfiere al 
# siguiente un numero calculado como: su valor dividido la cantidad de adyacentes que tiene. Devuelve un diccionario
# de valores según el algoritmo para cada vertice cruzado en el recorrido
def page_rank_random_walk(grafo, v, valores, largo, recorridos):
    if recorridos == largo: return valores
    ady = grafo.adyacentes(v)
    if len(ady) == 0: return valores
    pos_aleatoria = randint(0, len(ady) - 1)
    proximo = ady[pos_aleatoria]
    transferencia = valores[v] / len(ady)
    valores[v] -= transferencia
    if proximo not in valores: valores[proximo] = 0
    valores[proximo] += transferencia
    recorridos += 1
    return page_rank_random_walk(grafo, proximo, valores, largo, recorridos)

# Recibe un grafo, una lista de vertices a los que se le quiere encontrar vertices similares, el largo de los 
# Random Walks y la cantidad de iteraciones que se desean hacer. Realiza esa cantidad de iteraciones aplicando el 
# algoritmo de Random Walks y devuelve el diccionario de los valores obtenidos. Los vértices con mayor valor 
# tendrán más afinidad a los vertices pasados por parámetro
def vertices_similares(grafo, vertices, largo, iteraciones):
    valores = {}
    for vertice in vertices: valores[vertice] = 1
    for i in range(iteraciones):
        for v in vertices:
            recorridos = 0
            page_rank_random_walk(grafo, v, valores, largo, recorridos)
    return valores