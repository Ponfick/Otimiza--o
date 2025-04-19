import json
import os
import networkx as nx
import time
import matplotlib.pyplot as plt

print("--- Resolvedor para Problema de Frequência (Coloração de Grafo) ---")

INPUT_JSON_FILE = 'Segunda Questão/frequency_data.json'
COLORING_STRATEGY = 'largest_first'
DRAW_GRAPH = True

start_time = time.time()

print(f"\n1. Lendo dados do problema do arquivo '{INPUT_JSON_FILE}'...")

if not os.path.exists(INPUT_JSON_FILE):
    print(f"Erro: Arquivo de dados '{INPUT_JSON_FILE}' não encontrado.")
    print("Execute primeiro o script 'generate_frequency_data.py' para criar o arquivo.")
    exit()

try:
    with open(INPUT_JSON_FILE, 'r', encoding='utf-8') as f:
        problem_data = json.load(f)
except json.JSONDecodeError:
    print(f"Erro: Falha ao decodificar o arquivo JSON '{INPUT_JSON_FILE}'. Verifique o formato.")
    exit()
except Exception as e:
    print(f"Erro ao ler o arquivo '{INPUT_JSON_FILE}': {e}")
    exit()

try:
    antennas = problem_data["antennas"]
    interferences = problem_data["interferences"]
    if not isinstance(antennas, list) or not isinstance(interferences, list):
         raise ValueError("Formato inválido para 'antennas' ou 'interferences' no JSON.")
    print(f"   > Dados carregados para {len(antennas)} antenas e {len(interferences)} interferências.")
except KeyError as e:
    print(f"Erro: Chave esperada não encontrada no arquivo JSON: {e}")
    exit()
except ValueError as e:
    print(f"Erro: Problema com os dados lidos do JSON: {e}")
    exit()

print(f"   Tempo de leitura: {time.time() - start_time:.2f}s")

print("\n2. Construindo o grafo de interferência...")
build_start_time = time.time()
G = nx.Graph()
G.add_nodes_from(antennas)

valid_edges = 0
invalid_pairs_count = 0
for pair in interferences:
    if isinstance(pair, list) and len(pair) == 2 and pair[0] in G and pair[1] in G:
        G.add_edge(pair[0], pair[1])
        valid_edges += 1
    else:
        invalid_pairs_count += 1

if invalid_pairs_count > 0:
     print(f"   Aviso: {invalid_pairs_count} pares de interferência inválidos foram ignorados.")
print(f"   Grafo construído com {G.number_of_nodes()} nós e {G.number_of_edges()} arestas.")
print(f"   Tempo de construção do grafo: {time.time() - build_start_time:.2f}s")

print(f"\n3. Encontrando uma atribuição de frequências (coloração válida)")
print(f"   Usando a estratégia heurística: '{COLORING_STRATEGY}'...")
coloring_start_time = time.time()
coloring = None
num_colors_used = -1

try:
    coloring = nx.coloring.greedy_color(G, strategy=COLORING_STRATEGY)
    if coloring:
        num_colors_used = max(coloring.values()) + 1
    else:
         num_colors_used = 0
    print(f"   Coloração/Atribuição encontrada em {time.time() - coloring_start_time:.2f}s.")

except Exception as e:
    print(f"\nErro ao tentar colorir/atribuir frequências ao grafo: {e}")

print("-" * 50)
if coloring is not None and num_colors_used >= 0:
    print(f"Atribuição de Frequências Válida Encontrada (Heurística)")
    print(f"Número de Frequências (Cores) Utilizadas: {num_colors_used}")

    print("\nFrequência (Cor*) atribuída a cada Antena:")
    print(" (* Cores são numeradas a partir de 1)")
    sorted_antennas = sorted(coloring.keys())
    output_lines = []
    max_name_len = 0
    for antenna in sorted_antennas:
        if len(antenna) > max_name_len: max_name_len = len(antenna)
        frequency_number = coloring[antenna] + 1
        output_lines.append(f"- {antenna}: Frequência {frequency_number}")

    if len(output_lines) > 15:
        cols = 2 if len(output_lines) < 40 else 3
        padding = max_name_len + 18
        col_len = (len(output_lines) + cols - 1) // cols
        for r in range(col_len):
            line = ""
            for c in range(cols):
                idx = r + c * col_len
                if idx < len(output_lines):
                    line += f"{output_lines[idx]:<{padding}}"
            print(line)
    else:
        for line in output_lines:
            print(line)

    if DRAW_GRAPH and G.number_of_nodes() > 0 and G.number_of_nodes() < 50:
        print("\n5. Desenhando o grafo colorido...")
        print("   (Pode ser necessário fechar a janela do gráfico para o script terminar)")
        try:
            import matplotlib.pyplot as plt
            pos = nx.spring_layout(G, seed=42)
            node_colors = [coloring[node] for node in G.nodes()]
            plt.figure(figsize=(12, 9))
            nx.draw(G, pos, with_labels=True, node_color=node_colors,
                    cmap=plt.cm.get_cmap('viridis', num_colors_used),
                    font_size=9, node_size=600, edge_color='gray')
            plt.title(f"Grafo de Interferência Colorido ({num_colors_used} cores/frequências)")
            plt.show()
        except ImportError:
             print("   Aviso: Biblioteca 'matplotlib' não encontrada. Para desenhar o grafo, instale com: pip install matplotlib")
        except Exception as e:
            print(f"   Erro ao tentar desenhar o grafo: {e}")
    elif DRAW_GRAPH:
         print("\n5. Desenho do grafo pulado (grafo muito grande ou vazio).")

else:
    print("Não foi possível encontrar uma atribuição de frequências válida para o grafo.")

print("-" * 50)
print(f"Tempo total de execução: {time.time() - start_time:.2f}s")