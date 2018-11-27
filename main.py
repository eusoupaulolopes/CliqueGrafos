import glob
import os
from Tools import helper
import networkx as nx
import sys
import time

DIR = "samples\\"



def timeit(f):
    '''
    Mensura o tempo de execução
    '''
    def wrap(*args):
        time1 = time.time()
        ret = f(*args)
        time2 = time.time()
       
        return (ret, '{0:.3f} ms'.format((time2 - time1) * 1000.0))
    return wrap


def ler_samples():
    file_content = {}
    for file in os.listdir(DIR):
        if file.endswith( ".clq" ):
            try:    
                file_content[file] = ler_base(os.path.join(DIR+file))
            except FileNotFoundError as e:
                print("Caminho inválido para os arquivos")
                sys.exit(0)
    
    return file_content
        
def ler_base(base):
    arestas = []
    try:
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
    except FileNotFoundError as e:
        print("Caminho inválido para o arquivo: "+ base)
        sys.exit(0) 
    
    return nx.Graph(arestas)

def ordenar_nodes(graph):
    return [node[0] for node in sorted(nx.degree(graph), key=lambda x: x[1], reverse = True)]

def cromatico_guloso(graph):
    """
        Definindo número cromático guloso para um grafo

        0) Inicialmente o número máximo de cores é igual ao numero de nós no grafo
        1) cores do mapa é um dicionário vazio, <cores_usadas> esta vazio
        2) Pintamos o nó com maior grau com a primeira cor disponível, 
        3) Adicionamos as cores do mapa uma entrada com o nó pintado e a cor
        4) Retiramos o nó pintado da lista de nós
        5) Acrescentamos a cor usada em <cores_usadas>
        6) REPETICAO enquanto existir nós a serem pintados:
            6.1) Escolhemos/Retiramos o nó de maior grau da lista
            6.2) As cores dos vizinhos é um dicionário das definida pelas ja usadas  
            6.3) Se o tamanho das cores usadas for igual as cores vizinhas:
                6.3.1) Solicite uma nova cor e acrescente no mapa uma entrada {nó escolhido: proxima cor entre as cores possiveis}.
                6.3.2) itere o contador de cores usadas
            6.4) Caso contrário
                6.4.1) Adicione no mapa uma tupla no e (cores usadas - cores vizinhas)
        7) Retorne as cores_usadas


    """
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

def cromatico_welsh_powell(graph):
	
    #Ordenar os vértices 
	node_list = ordenar_nodes(graph)
    
    # C1 = ... Cn = {}
	col_val = {} 
    #Primeira cor ao nó de maior grau
	col_val[node_list.pop(0)] = 0 
	
    # Cores dos nós restantes 
    # i <- 1 até n
	for node in node_list:
        # Estrutura para guardar cores disponiveis
		available = [True] * len(graph.nodes()) 

		#Iterando sobre os nós vizinhos
		for adj_node in graph.neighbors(node): 
            # Se o nó já foi pintado com uma cor
			if adj_node in col_val.keys():
				col = col_val[adj_node]
				available[col] = False

		clr = 0
		for clr in range(len(available)):
            #Estrutura para iterar até aproxima cor disponivel
			if available[clr] == True:
				break
        #pinta o nó com a próxima cor disponivel
        
        #Ck = Ck U {Xi}
		col_val[node] = clr
	
	return len(col_val)

def clique_guloso(graph):
    """
        Localizando uma clique através de heuristica gulosa. Trazemos uma clique com maior grau possivel no grafo proposto
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


    #Filtrando os nós parcialmente conectados
    nodes_parcialmente_conectados = list(filter(
        lambda x: x[1] != maior_grau and x[1] <= maior_grau, nodes_list
    ))

    #Cortamos os nós parcialmente conectados
    graph1.remove_node(nodes_parcialmente_conectados[0][0])
    
    # Grafo resultante do Grafo base menos os nós vizinhos que estão parcialmente conectados entre eles
    graph2.remove_nodes_from(
        graph.nodes() - graph.neighbors(nodes_parcialmente_conectados[0][0]) - {nodes_parcialmente_conectados[0][0]}
    )
    
    return graph1, graph2


def bb_max_clique(graph):
    max_clique = clique_guloso(graph)
    num_cromatico = cromatico_welsh_powell(graph)
    #Caso atinjanmos o num_cormático atual temos o maximo clique
    if len(max_clique) == num_cromatico:
        return max_clique
    #Caso contrário, entramos um nível a mais nos branchs
    else:
        grafo1, grafo2 = branching(graph, len(max_clique))
        #Aqui o corte é feito, recursivamente apenas o clique maximal entre os dois branchs é eleito e o outro ramo é descartado
        return max(bb_max_clique(grafo1), bb_max_clique(grafo2), key=lambda x: len(x))

@timeit
def get_max_clique(graph):
    return bb_max_clique(graph)


def main():
    args = helper.arguments()
    if args.all:
        graph_dict = ler_samples()
        for key, graph in graph_dict.items():
            print("\nBASE: ", key)
            max_clq = get_max_clique(graph)
            with open('results.txt', 'a+') as results:
                results.write("#########################")
                results.write("\nBASE: {}\n".format(key))
                print('Clique Maxima: \n {} \nTamanho: {} Tempo Execucao: {}'.format(max_clq[0], len(max_clq[0]), max_clq[1]))
                results.write('Clique Maxima: {} \n Tamanho: {} \n Tempo Execucao: {}'.format(max_clq[0], len(max_clq[0]), max_clq[1]))
                results.write("\n#########################")
    else:
        graph = ler_base(args.base)
        max_clq = get_max_clique(graph)
        print('\nClique Maxima: \n {} \nTamanho: {} \n Tempo Execucao: {}'.format(max_clq[0], len(max_clq[0]), max_clq[1]))

if __name__ == '__main__':
    main()


