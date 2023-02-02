from grafo import Grafo
from funciones_grafos import *
import sys
from sys import stdin
from os.path import exists
import heapq

#*******************************************************************
#                     CONSTANTES GLOBALES
#*******************************************************************

# Posiciones del set de datos pasados por parámetro del programa
PROGRAMA = 0
ARCHIVO_CANCIONES = 1
ENTRADA = 2
CANT_PARAMETROS_CON_ARCHIVO_ENTRADAS = 3
CANT_PARAMETROS_MAX = 4

# Posiciones dentro del archivo de canciones
ID = 0
USER_ID = 1
TRACK_NAME = 2
ARTIST = 3
PLAYLIST_ID = 4
PLAYLIST_NAME = 5
GENRES = 6

# Comandos del programa
CAMINO = "camino"
IMPORTANTES = "mas_importantes"
RECOMENDACION = "recomendacion"
CICLO = "ciclo"
RANGO = "rango"

# Separador de los valores en el archivo de canciones
SEPARADOR_ARCHIVO = "\t"

# Separadores de las canciones y su autor en los Grafos
SEPARADOR_CANCIONES_GRAFO = " - "

# Posiciones y separadores en la entrada del usuario
POSICION_COMANDO = 0
POSICION_NUMERO_N_GENERAL = 1
POSICION_CANCION_GENERAL = 2

POSICION_TIPO_RECOMENDACION = 1
POSICION_NUMERO_N_RECOMENDACION = 2
POSICION_INICIO_CANCIONES_RECOMENDAR = 3

POSICION_ORIGEN_CAMINO = 1

SEPARADOR_CANCIONES_ENTRADA_USUARIO = ">>>>"
RECOMENDACION_TIPO_CANCION = "canciones"
RECOMENDACION_TIPO_USUARIO = "usuarios"

# Separador de las canciones, usuarios y playlists en las salidas del programa
SEPARADOR_CANCIONES_MAS_IMPORTANTES = "; "
SEPARADOR_CANCIONES_CICLO = " --> "
SEPARADOR_CAMINO_CANCIONES_A_PLAYLIST = " --> aparece en playlist --> "
SEPARADOR_CAMINO_PLAYLIST_A_USUARIO = " --> de --> "
SEPARADOR_CAMINO_PLAYLIST_A_CANCION = " --> donde aparece --> "
SEPARADOR_CAMINO_USUARIOS_A_PLAYLIST = " --> tiene una playlist --> "

# Mensajes de error
ARCHIVO_CANCIONES_INEXISTENTE = "El archivo de canciones es inaccesible"
ARCHIVO_ENTRADAS_INEXISTENTE = "El archivo de entradas es inaccesible"
CANT_PARAMETROS_INCORRECTA = "La cantidad de parámetros es incorrecta"

RECORRIDO_INEXISTENTE = "No se encontro recorrido"
CANCION_INEXISTENTE = "No se encontro la cancion"
NUMERO_N_INVALIDO = "Numero invalido"
CANCION_NO_VALIDA = "Tanto el origen como el destino deben ser canciones"

# Valores del algortimo PageRank que cuadran con los modelos usados en este programa:
PAGERANK_AMORTIGUACION = 0.5
PAGERANK_ITERACIONES = 15

# Valores del algoritmo de PageRank personalizado que le aplica a los Random Walks:
RANDOM_WALK_LARGO = 500
RANDOM_WALK_ITERACIONES = 150

# Recibe una lista con los parametros pasados al programa y devuelve True en caso de que sean validos.
# Imprime un mensaje de error y devuelve False en caso de que no sean validos y no se pueda seguir con el programa
def validar_parametros(lista_parametros):
    if not exists(lista_parametros[ARCHIVO_CANCIONES]):
        print(ARCHIVO_CANCIONES_INEXISTENTE)
        return False
    if len(lista_parametros) > CANT_PARAMETROS_MAX:
        print(CANT_PARAMETROS_INCORRECTA)
        return False
    if len(lista_parametros) == CANT_PARAMETROS_CON_ARCHIVO_ENTRADAS and not exists(lista_parametros[ENTRADA]):
        print(ARCHIVO_ENTRADAS_INEXISTENTE)
        return False
    return True

# Recibe una linea del archivo de datos y devuelve una lista donde cada elemento es un campo particular del archivo
def limpiar_linea_archivo(linea):
    entrada = linea.split(SEPARADOR_ARCHIVO)
    entrada[-1] = entrada[-1].rstrip()
    return entrada

# Recibe un grafo de usuarios y canciones bipartito, la lista de la entrada, un usuario y una cancion
# y le agrega al grafo un vertice usuario, otro vertice cancion y los relaciona entre si con una arista
# cuyo peso es el nombre de la playlist del usuario en la que se encuentra la cancion
def agregar_entrada_grafo_mixto(grafo, usuario, cancion, playlist):
    grafo.agregar_vertice(cancion)
    grafo.agregar_vertice(usuario)
    grafo.agregar_arista(cancion, usuario, playlist)

# Recibe un archivo de datos y devuelve un grafo bipartito que relaciona usuarios 
# y canciones que les gustan y un set con todos los usuarios del archivo
def procesar_archivo(ruta_archivo):
    with open(ruta_archivo, 'r') as archivo:
        next(archivo)
        usuarios = set()
        grafo_usuarios_canciones = Grafo()
        for linea in archivo:
            linea = limpiar_linea_archivo(linea)
            cancion = linea[TRACK_NAME] + SEPARADOR_CANCIONES_GRAFO + linea[ARTIST]
            usuario = linea[USER_ID]
            playlist = linea[PLAYLIST_NAME]
            usuarios.add(usuario)
            agregar_entrada_grafo_mixto(grafo_usuarios_canciones, usuario, cancion, playlist)
        return grafo_usuarios_canciones, usuarios

# Recibe una linea de entrada con dos canciones separadas por cierto/s caracter/es
# y devuelve una lista con cada cancion
def devolver_lista_canciones(lista_linea):
    lista_canciones = []
    cancion = ""
    for palabra in lista_linea:
        if palabra == SEPARADOR_CANCIONES_ENTRADA_USUARIO:
            lista_canciones.append(cancion[:-1])
            cancion = ""
        else: cancion += palabra + " "
    lista_canciones.append(cancion.rstrip())
    return lista_canciones

# Recibe un grafo y un camino y devuelve una cadena con el camino de una manera personalizada mostrando los usuarios, 
# las playists y las canciones que forman el camino
def construir_salida_camino(grafo, camino):
    salida = ""
    es_cancion = True
    for n in range(len(camino) - 1):
        playlist = grafo.peso_arista(camino[n], camino[n+1])
        if es_cancion:
            salida += camino[n] + SEPARADOR_CAMINO_CANCIONES_A_PLAYLIST
            if n != len(camino) - 1: salida += playlist + SEPARADOR_CAMINO_PLAYLIST_A_USUARIO
            es_cancion = False
        else:
            salida += camino[n] + SEPARADOR_CAMINO_USUARIOS_A_PLAYLIST + playlist + SEPARADOR_CAMINO_PLAYLIST_A_CANCION
            es_cancion = True
    salida += camino[-1]
    return salida

# Recibe un grafo que relaciona usuarios y las canciones que les gustan, la entrada del usuario y un set con los 
# usuarios e imprime el camino minimo para ir desde la primera cancion pasada en la entrada hasta la segunda. 
# Imprime un mensaje de error en caso de que alguna cancion no sea parte del grafo o no exista el camino entre 
# las canciones
def imprimir_camino_mas_corto(grafo_usuarios_canciones, entrada_usuario, usuarios):
    lista_canciones = devolver_lista_canciones(entrada_usuario[POSICION_ORIGEN_CAMINO:])
    for cancion in lista_canciones:
        if cancion in usuarios or not grafo_usuarios_canciones.vertice_pertenece(cancion):
            print(CANCION_NO_VALIDA)
            return
    camino = camino_minimo(grafo_usuarios_canciones, lista_canciones[0], lista_canciones[1])
    if not camino:
        print(RECORRIDO_INEXISTENTE)
        return
    print(construir_salida_camino(grafo_usuarios_canciones, camino))

# Recibe un numero n en forma de string y verifica que sea valido (positivo). Lo devuelve en caso de que sea valido.
# Imprime un mensaje de error en caso contrario
def procesar_numero_n(n_usuario):
    n = int(n_usuario)
    if n < 1: 
        print(NUMERO_N_INVALIDO)
        return False
    return n

# Recibe un diccionario con las canciones y sus valores de importancia segun page_rank y la entrada del usuario.
# Imprime las "n" canciones mas importantes
def imprimir_n_canciones_mas_importantes(page_rank, entrada_usuario):
    n = procesar_numero_n(entrada_usuario[POSICION_NUMERO_N_GENERAL])
    if not n: return
    lista_importantes = heapq.nlargest(n, page_rank, key = page_rank.get)
    print(SEPARADOR_CANCIONES_MAS_IMPORTANTES.join(lista_importantes))

# Recibe un grafo que relaciona usuarios y canciones que les gustan, la entrada del usuario y un set con todos
# los usuarios e imprime "n" usuarios/canciones para recomendar segun la entrada ingresada
def imprimir_n_recomendaciones(grafo_usuarios_canciones, entrada_usuario, usuarios):
    tipo_recomendacion = entrada_usuario[POSICION_TIPO_RECOMENDACION]
    n = procesar_numero_n(entrada_usuario[POSICION_NUMERO_N_RECOMENDACION])
    canciones = devolver_lista_canciones(entrada_usuario[POSICION_INICIO_CANCIONES_RECOMENDAR:])
    valores = vertices_similares(grafo_usuarios_canciones, canciones, RANDOM_WALK_LARGO, RANDOM_WALK_ITERACIONES)
    for cancion in canciones:
        # Saca de las recomendaciones las canciones que ya sabemos que le gustan a la persona (las que fueron pasadas)
        if cancion in valores: valores.pop(cancion)
    for vertice in list(valores.keys()):
        # Si la recomendacion es de canciones se eliminan de valores todos los vertices que sean usuarios
        if tipo_recomendacion == RECOMENDACION_TIPO_CANCION:
            if vertice in usuarios: valores.pop(vertice)
        # Si la recomendacion es de usuarios se eliminan todos los vertices que sean canciones             
        if tipo_recomendacion == RECOMENDACION_TIPO_USUARIO:
            if vertice not in usuarios: valores.pop(vertice)
    print(SEPARADOR_CANCIONES_MAS_IMPORTANTES.join(heapq.nlargest(n, valores, key = valores.get)))

# Recibe el Grafo con las canciones y la entrada del usuario en forma de lista y devuelve
# una cadena con el nombre de la cancion en caso de que esté en el Grafo. Imprime un mensaje de error 
# en caso contrario
def procesar_cancion(grafo_canciones, entrada_usuario):
    cancion = " ".join(entrada_usuario[POSICION_CANCION_GENERAL:])
    if not grafo_canciones.vertice_pertenece(cancion):
        print(CANCION_INEXISTENTE)
        return False
    return cancion

# Recibe el Grafo con las canciones y la entrada del usuario en forma de lista e imprime por pantalla de forma
# personalizada un ciclo de la longitud "n" recibida por parámetro que comienza desde la cancion
def imprimir_ciclo_n_canciones(grafo_canciones, entrada_usuario):
    cancion = procesar_cancion(grafo_canciones, entrada_usuario)
    n = procesar_numero_n(entrada_usuario[POSICION_NUMERO_N_GENERAL])
    if not cancion or not n: return
    ciclo = ciclo_de_largo_n(grafo_canciones, cancion, n)
    if not ciclo:
        print(RECORRIDO_INEXISTENTE)
        return
    salida = ""
    for indice, cancion in enumerate(ciclo):
        salida += cancion
        if indice != len(ciclo) - 1: salida += SEPARADOR_CANCIONES_CICLO 
    print(salida)

# Recibe un grafo que relaciona canciones que aparecen en playlists de un mismo usuario y la entrada del programa
# e imprime la cantidad de canciones que se encuenten a exactamente n saltos desde la cancion pasada en la entrada
def imprimir_canciones_rango_n(grafo_canciones, entrada_usuario):
    cancion = procesar_cancion(grafo_canciones, entrada_usuario)
    n = procesar_numero_n(entrada_usuario[POSICION_NUMERO_N_GENERAL])
    if not cancion or not n: return
    print(cantidad_de_rango_n(grafo_canciones, cancion, n))

# Recibe un grafo que relaciona usuarios y canciones que les gustan y un set con los usuarios y devuelve otro grafo
# que relaciona canciones que aparecen en playlists de un mismo usuario
def construir_grafo_canciones(grafo_usuarios_canciones, usuarios):
    grafo_canciones = Grafo()
    for vertice in grafo_usuarios_canciones.obtener_vertices():
        if vertice in usuarios:
            canciones_usuario_actual = set()
            for cancion in grafo_usuarios_canciones.adyacentes(vertice):
                grafo_canciones.agregar_vertice(cancion)
                for cancion_de_usuario in canciones_usuario_actual:
                    grafo_canciones.agregar_arista(cancion, cancion_de_usuario)
                canciones_usuario_actual.add(cancion)
    return grafo_canciones

# Recibe un grafo que relaciona usuarios y canciones que les gustan y un set con los usuarios y devuelve un diccionario
# con canciones como claves y su importancia como valores
def calcular_page_ranks(grafo_usuarios_canciones, usuarios):
    page_rank = page_ranks(grafo_usuarios_canciones, PAGERANK_AMORTIGUACION, PAGERANK_ITERACIONES)
    for vertice in list(page_rank.keys()):
        # si el vertice es un usuario lo saco del diccionario pageranks, solo interesan las canciones
        if vertice in usuarios: page_rank.pop(vertice)
    return page_rank

# Recibe un archivo con las entradas (o entrada stdin), un grafo que relaciona usuarios y canciones que les gustan,
# un grafo que relaciona canciones que aparecen en playlists de un mismo usuario o None si no existe, un diccionario
# con la importancia (pagerank) de cada vertice o None si todavia no fue creado, y un set de los usuarios. LLama a 
# las funciones correspondientes de cada comando ingresado en la entrada
def ejecutar_comandos(entrada, grafo_usuarios_canciones, grafo_canciones, page_rank, usuarios):
    for linea in entrada:
        linea = linea.rstrip()
        entrada_usuario = linea.split(" ")
        comando = entrada_usuario[POSICION_COMANDO]
        if comando == CAMINO: imprimir_camino_mas_corto(grafo_usuarios_canciones, entrada_usuario, usuarios)
        if comando == IMPORTANTES:
            # si todavia el page_rank de las canciones no fue creado (es None), lo creo
            if not page_rank: page_rank = calcular_page_ranks(grafo_usuarios_canciones, usuarios)
            imprimir_n_canciones_mas_importantes(page_rank, entrada_usuario)
        if comando == RECOMENDACION: imprimir_n_recomendaciones(grafo_usuarios_canciones, entrada_usuario, usuarios)
        if comando == CICLO or comando == RANGO:
            # si todavia no se creo el grafo que relaciona canciones si aparecen en playlists de un mismo usuario (es None), lo creo
            if not grafo_canciones: grafo_canciones = construir_grafo_canciones(grafo_usuarios_canciones, usuarios)
            if comando == CICLO: imprimir_ciclo_n_canciones(grafo_canciones, entrada_usuario)
            if comando == RANGO: imprimir_canciones_rango_n(grafo_canciones, entrada_usuario)

# Recibe la lista de parámetros que recibió el programa, el grafo de usuarios y canciones, el de solo canciones y el 
# diccionario de page_ranks, si estos ya fueron creados y un conjunto de los usuarios presentes en el Grafo.
# Abre el archivo o entrada correspondiente a los comandos a ser ejecutados por el usuario y llama a la funcion que
# los ejecuta
def abrir_entradas(lista_parametros, grafo_usuarios_canciones, grafo_canciones, page_rank, usuarios):
    if len(lista_parametros) == CANT_PARAMETROS_CON_ARCHIVO_ENTRADAS:
        archivo_entrada = lista_parametros[ENTRADA]
        with open(archivo_entrada, "r") as entrada:
            ejecutar_comandos(entrada, grafo_usuarios_canciones, grafo_canciones, page_rank, usuarios)
    else: 
        entrada = stdin
        ejecutar_comandos(entrada, grafo_usuarios_canciones, grafo_canciones, page_rank, usuarios)

# Función central del programa que recibe la lista de parámetros, extrae la ruta del archivo y lo procesa, y
# llama a la función que se dedica a realizar los comandos en la entrada del usuario
def recomendify(lista_parametros):
    ruta_archivo = lista_parametros[ARCHIVO_CANCIONES]
    grafo_usuarios_canciones, usuarios = procesar_archivo(ruta_archivo)
    abrir_entradas(lista_parametros, grafo_usuarios_canciones, None, None, usuarios)

# Valida los parámetros del programa y de ser correctos inicia el programa Recomendify
def main():
    parametros = sys.argv
    if not validar_parametros(parametros): return 1
    recomendify(parametros)
    return 0

main()