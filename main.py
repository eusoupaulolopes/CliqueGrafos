import glob
import os
from Tools import helper
import networkx as nx
import sys
from contextlib import contextmanager
import _thread
import threading

class TimeoutException(Exception):
    pass

@contextmanager
def tempo_limite(seconds):
    timer = threading.Timer(seconds, lambda: _thread.interrupt_main())
    timer.start()
    try:
        yield
    except KeyboardInterrupt:
        raise TimeoutException()
    finally:
        timer.cancel()

def ler_base(base):
    arestas = []
    with open (base, 'r') as file:
        for line in file:
            if line.startswith('p'): #Propriedades do Grafo
                p, nome, num_vertices, num_arestas = line.split()
                print('{} {} {}'.format(nome, num_vertices, num_arestas))
            elif line.startswith('e'): # Adicionando cada par de vertices adjacentes na lista de arestas
                _, vertice_1, vertice_2 = line.split()
                arestas.append((vertice_1, vertice_2))
            else: 
                continue
        return nx.Graph(arestas)

def ordenar_nodes(graph):
    return [node[0] for node in sorted(nx.degree(graph), key=lambda x: x[1], reverse = True)]

def cromatico_guloso(graph):
    cores_possiveis = iter(range(0, len(graph)))
    cores_mapa = {}
    cores_usadas = set()
    node_list = ordenar_nodes(graph)
    #mapeamos a primeira cor com o node de maior grau
    cores_mapa[node_list.pop(0)] = next(cores_possiveis)
    cores_usadas = {cor for cor in cores_mapa.values()}
    #Enquanto existir nodes para colorir
    while len(node_list) != 0:
        no = node_list.pop(0)
        cores_vizinhas = {cores_mapa[vizinho] for vizinho in
                            list(filter(lambda x: x in cores_mapa, graph.neighbors(no)))}
        if len(cores_vizinhas) == len(cores_usadas):
            cor = next(cores_possiveis)
            cores_usadas.add(cor)
            cores_mapa[no] = cor
        else:
            cores_mapa[no] = next(iter(cores_usadas - cores_vizinhas))
    return len(cores_usadas)
    

def clique_guloso(graph):
    """
        Localizando uma clique através de heuristica gulosa.
    """
    K = set()
    node_list = ordenar_nodes(graph)
    while len(node_list) != 0:
       vizinhos = list(graph.neighbors(node_list[0]))
       K.add(node_list[0])
       node_list = list(filter(lambda x: x in vizinhos, node_list))
    return K

def branching(graph, tamanho_maximo_atual):
    graph1, graph2 = graph.copy(), graph.copy()
    maior_grau = len(graph) -1 
    # Lista ordenada das tupas (node, node_grau)
    nodes_list = [node for node in sorted(nx.degree(graph), key=lambda x: x[1], reverse =True)]
    nodes_parcialmente_conectados = list(filter(
        lambda x: x[1] != maior_grau, nodes_list
    ))

    #Sem nodes que não estão parcialmente conectados com o node de maior grau
    graph1.remove_node(nodes_parcialmente_conectados[0][0])
    
    # Sem nodes que não estao ligados ao node  conectado parcial de maior grau
    graph2.remove_nodes_from(
        graph.nodes() - graph.neighbors(nodes_parcialmente_conectados[0][0]) - {nodes_parcialmente_conectados[0][0]}
    )
    
    return graph1,graph2

def bb_max_clique(graph):
    max_clique = clique_guloso(graph)
    num_cromatico = cromatico_guloso(graph)
    if len(max_clique) == num_cromatico:
        return max_clique
    else:
        grafo1, grafo2 = branching(graph, len(max_clique))
        return max(bb_max_clique(grafo1), bb_max_clique(grafo2), key=lambda x: len(x))
    

def main():
    args = helper.arguments()
    try:
        graph = ler_base(args.base)
        max_clq = bb_max_clique(graph)
        print('\nClique Maxima', max_clq)
        print("tamanho: ", len(max_clq))
    except FileNotFoundError as exp:
        print ("Arquivo não localizado!")
    
if __name__ == '__main__':
    main()


