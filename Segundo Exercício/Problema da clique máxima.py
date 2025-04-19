import json
import math
import networkx as nx
import os
import time

JSON_FILE = 'Segunda Questão\cities.json'
DISTANCE_THRESHOLD = 3.5
TOLERANCE = 1e-9

def euclidean_distance(lat1, lon1, lat2, lon2):
    try:
        lat1_f, lon1_f, lat2_f, lon2_f = map(float, [lat1, lon1, lat2, lon2])
        dist = math.sqrt((lat1_f - lat2_f)**2 + (lon1_f - lon2_f)**2)
        return dist
    except (ValueError, TypeError):
        return float('inf')

start_time = time.time()
print("--- Problema da Clique Máxima (usando cities.json) ---")

print(f"\n1. Lendo dados de '{JSON_FILE}'...")
if not os.path.exists(JSON_FILE):
    print(f"Erro: Arquivo '{JSON_FILE}' não encontrado.")
    exit()

try:
    with open(JSON_FILE, 'r', encoding='utf-8') as f:
        all_cities_data = json.load(f)
except Exception as e:
    print(f"Erro ao ler ou decodificar o arquivo JSON '{JSON_FILE}': {e}")
    exit()

cities_data = {}
for city_info in all_cities_data:
    city_name = city_info.get('city', 'Unknown').strip()
    if not city_name or city_name == 'Unknown': continue
    try:
        lat = float(city_info['latitude'])
        lon = float(city_info['longitude'])
        cities_data[city_name] = {'lat': lat, 'lon': lon}
    except (ValueError, TypeError, KeyError):
        continue

if not cities_data:
    print("Erro: Nenhuma cidade válida com coordenadas encontrada no arquivo.")
    exit()
print(f"   Encontradas {len(cities_data)} cidades válidas.")
print(f"   Tempo de leitura: {time.time() - start_time:.2f}s")

G = nx.Graph()
print(f"\n2. Construindo grafo (arestas se dist <= {DISTANCE_THRESHOLD})...")
build_start_time = time.time()

G.add_nodes_from(cities_data.keys())

edges_added = 0
nodes_in_graph = list(G.nodes())

for i in range(len(nodes_in_graph)):
    city1_name = nodes_in_graph[i]
    city1_data = cities_data[city1_name]
    lat1, lon1 = city1_data['lat'], city1_data['lon']

    for j in range(i + 1, len(nodes_in_graph)):
        city2_name = nodes_in_graph[j]
        city2_data = cities_data[city2_name]
        lat2, lon2 = city2_data['lat'], city2_data['lon']

        distance = euclidean_distance(lat1, lon1, lat2, lon2)

        if distance <= DISTANCE_THRESHOLD + TOLERANCE:
            G.add_edge(city1_name, city2_name)
            edges_added += 1

print(f"   Grafo construído com {G.number_of_nodes()} nós e {G.number_of_edges()} arestas.")
print(f"   Tempo de construção: {time.time() - build_start_time:.2f}s")
if G.number_of_edges() == 0:
    print("   Aviso: Nenhuma aresta foi criada com este limiar. Cliques terão tamanho máximo 1.")

print("\n3. Encontrando a(s) clique(s) máxima(s) (pode levar tempo)...")
clique_find_start_time = time.time()

max_clique_size = 0
max_cliques_found = []

if G.number_of_nodes() > 0:
    try:
        all_maximal_cliques_iterator = nx.find_cliques(G)

        processed_cliques_count = 0
        for current_clique in all_maximal_cliques_iterator:
            current_size = len(current_clique)
            processed_cliques_count += 1

            if current_size > max_clique_size:
                max_clique_size = current_size
                max_cliques_found = [current_clique]
            elif current_size == max_clique_size:
                max_cliques_found.append(current_clique)

        if G.number_of_edges() == 0 and G.number_of_nodes() > 0:
             max_clique_size = 1
             max_cliques_found = [[node] for node in list(G.nodes())[:min(5, G.number_of_nodes())]]

    except Exception as e:
        print(f"Erro ao executar nx.find_cliques: {e}")
        max_clique_size = -1
else:
    print("   Grafo está vazio. Nenhuma clique para encontrar.")
    max_clique_size = 0

print(f"   Tempo de busca da clique: {time.time() - clique_find_start_time:.2f}s")

print("-" * 50)
if max_clique_size > 0:
    print(f"Tamanho da Clique Máxima Encontrada: {max_clique_size} cidades")
    print(f"   (Um grupo de {max_clique_size} cidades onde TODAS estão a uma distância <= {DISTANCE_THRESHOLD} umas das outras)")

    num_found = len(max_cliques_found)
    print(f"\nEncontrada(s) {num_found} clique(s) com este tamanho máximo:")

    max_cliques_to_show = 5
    for i, clique in enumerate(max_cliques_found):
        if i >= max_cliques_to_show:
             print(f"\n... e mais {num_found - max_cliques_to_show} clique(s) de tamanho máximo.")
             break

        clique.sort()
        print(f"\nClique Máxima #{i+1}:")

        if len(clique) > 12:
             cols=3
             padding = max(len(c) for c in clique) + 3 if clique else 20
             col_len = (len(clique) + cols - 1) // cols
             for r in range(col_len):
                  line = "  "
                  for c in range(cols):
                       idx = r + c*col_len
                       if idx < len(clique):
                            line += f"{clique[idx]:<{padding}}"
                  print(line)
        elif len(clique) > 1:
             print("  " + ", ".join(clique))
        else:
             print(f"  {clique[0]}")

elif max_clique_size == 0 and G.number_of_nodes() > 0:
     print("Nenhuma clique com mais de 1 nó encontrada.")
     print(f"(Provavelmente não há cidades com distância <= {DISTANCE_THRESHOLD} entre si)")
elif max_clique_size == 0 and G.number_of_nodes() == 0:
     print("Grafo vazio, nenhuma clique encontrada.")
elif max_clique_size < 0:
     print("Não foi possível determinar a clique máxima devido a um erro anterior.")

print("-" * 50)
print(f"Tempo total de execução: {time.time() - start_time:.2f}s")