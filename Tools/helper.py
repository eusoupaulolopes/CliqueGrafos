def arguments():
    import argparse
    parser = argparse.ArgumentParser(
        description='Programa para encontrar a clique maxima de um grafo.')
    parser.add_argument('--base', type=str, required=False,
                        help='Nome da base de dados no formato DIMAC')
    parser.add_argument('--time', type=int, default=60,
                        help='Tempo limite de execucao')
    return parser.parse_args()