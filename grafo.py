from random import randint

class Grafo:

#*******************************************************************
#                      PRIMITIVAS DEL GRAFO
#*******************************************************************

    # Crea un nuevo Grafo
    # Post: se devolvió un Grafo vacío que es dirigido si se pasó True como parámetro, y no dirigido de lo contrario
    def __init__(self, dirigido = False):
        self.vertices = {}
        self.dirigido = dirigido

    # Le agrega un vértice al Grafo
    # Pre: el Grafo fue creado y el parámetro "v" es un elemento hasheable
    # Post: el Grafo tiene un nuevo vertice "v", en caso de que dicho vértice no estuviera en el Grafo
    def agregar_vertice(self, v):
        if v in self.vertices: return
        self.vertices[v] = {}

    # Le agrega una arista al Grafo
    # Pre: el Grafo fue creado y tanto "v" como "w" son vertices del Grafo.
    # Post: el Grafo tiene una nueva arista del peso pasado por parámetro de "v" a "w". Se devuelve False en caso de 
    # que "v" o "w" no pertenecieran al Grafo, y True en caso contrario. Si no se indicó un peso, este será 1
    def agregar_arista(self, v, w, peso = 1):
        if v not in self.vertices or w not in self.vertices: return False
        self.vertices[v][w] = peso
        if not self.dirigido:
            self.vertices[w][v] = peso
        return True

    # Indica si dos vertices son adyacentes o no
    # Pre: el Grafo fue creado y ambos vertices están en el Grafo
    # Post: se devolvió True si "w" era adyacente de "v" y False en el caso contrario
    def son_adyacentes(self, v, w):
        if w not in self.vertices[v]: return False
        return True

    # Borra un vertice del Grafo
    # Pre: el Grafo fue creado
    # Post: el vertice "v" ya no está en el Grafo y se devolvió True. Si "v" no estaba, se devolvió False
    def borrar_vertice(self, v):
        if v not in self.vertices: return False
        self.vertices.pop(v)
        for adyacentes in self.vertices.values():
            if v in adyacentes: adyacentes.pop(v)
        return True        

    # Borra un arista del Grafo
    # Pre: el Grafo fue creado; ambos vertices se encuentran en el Grafo y son adyacentes
    # Post: el vertice "w" ya no es adyacente del vertice "v" y se devolvió True si se borró la arista
    def borrar_arista(self, v, w):
        if not self.son_adyacentes(v, w): return False
        self.vertices[v].pop(w)
        if not self.dirigido:
            self.vertices[w].pop(v)
        return True

    # Dados dos vertices "v" y "w" devuelve el peso de la arista que los une
    # Pre: el Grafo fue creado, "v" y "w" están en el Grafo y  "w" es adyacente de "v"
    # Post: devolvió el peso de la arista de "v" a "w", o None en caso de que "w" no fuese adycacente de "v"
    def peso_arista(self, v, w):
        if not self.son_adyacentes(v, w): return None
        return self.vertices[v][w]

    # Devuelve una lista con todos los vertices del grafo
    # Pre: el grafo fue creado
    # Post: se devolvió una lista con todos los vertices contenidos en el Grafo
    def obtener_vertices(self):
        return list(self.vertices.keys())

    # Devuelve un vertice aleatorio
    # Pre: el Grafo fue creado
    # Post: se devolvió un vertice aleatorio del Grafo. Si este no tenía vertices devolvió None  
    def vertice_aleatorio(self):
        if len(self.vertices) == 0: return None
        n = randint(0, len(self.vertices) - 1)
        return list(self.vertices)[n]

    # Recibe un vertice e indica si este se encuentra en el grafo o no.
    # Pre: el Grafo fue creado
    # Post: se devolvió True si el vertice se encontraba en el grafo y False en caso contrario
    def vertice_pertenece(self, v):
        return v in self.vertices

    # Recibe un vertice y devuelve todos los vertices adyacentes de este
    # Pre: el Grafo fue creado y el vertice "v" se encuentra en él
    # Post: se devolvió una lista con todos los vertices adyacentes sw "v"
    def adyacentes(self, v):
        return list(self.vertices[v].keys())

    # Imprime el Grafo
    # Pre: el Grafo fue creado
    # Post: se imprimió una representacion de forma diccionario del Grafo
    def __str__(self) -> str:
        cadena = ""
        for vertice, adyacentes in self.vertices.items(): cadena += vertice + ": " + str(adyacentes) + "\n"
        return cadena

    # Devuelve la cantidad de vertices en el Grafo
    # Pre: el Grafo fue creado
    # Post: se devolvió el numero de vertices contenidos en el Grafo
    def __len__(self) -> int:
        return len(self.vertices)
