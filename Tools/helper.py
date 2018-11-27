def arguments():
    import argparse
    parser = argparse.ArgumentParser(
        description='Programa para encontrar a clique maxima de um grafo.')
    parser.add_argument('--base', type=str, required=False,
                        help='Nome da base de dados no formato DIMAC')
    parser.add_argument('--all', type=bool, required=False, default=False,
                        help='Roda o algoritmo para todas as bases em \\samples\\*.col')
    return parser.parse_args()