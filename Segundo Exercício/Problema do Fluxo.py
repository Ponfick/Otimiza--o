import json
import math
import networkx as nx
import os

JSON_FILE = 'Segundo Exercício/cities.json'
SOURCE_CITY_NAME = 'Miami'
SINK_CITY_NAME = 'Seattle'
DISTANCE_THRESHOLD = 3.5

def euclidean_distance(lat1, lon1, lat2, lon2):
    try:
        lat1_f, lon1_f, lat2_f, lon2_f = map(float, [lat1, lon1, lat2, lon2])
        dist = math.sqrt((lat1_f - lat2_f)**2 + (lon1_f - lon2_f)**2)
        return dist
    except (ValueError, TypeError):
        return float('inf')

def get_population(city_info):
    try:
        pop_str = str(city_info.get('population', '0')).replace(',', '')
        return int(pop_str)
    except (ValueError, TypeError):
        return 0

if not os.path.exists(JSON_FILE):
    print(f"Erro: Arquivo '{JSON_FILE}' não encontrado no diretório atual: {os.getcwd()}")
    exit()

try:
    with open(JSON_FILE, 'r', encoding='utf-8') as f:
        all_cities_data = json.load(f)
except Exception as e:
    print(f"Erro ao ler ou decodificar o arquivo JSON '{JSON_FILE}': {e}")
    exit()

print(f"Carregados dados de {len(all_cities_data)} cidades.")

G_filtered = nx.DiGraph()
city_lookup = {}

print("Adicionando nós válidos ao grafo...")
valid_nodes_count = 0
for city_info in all_cities_data:
    city_name = city_info.get('city', 'Unknown').strip()
    if city_name and city_name != 'Unknown' and 'latitude' in city_info and 'longitude' in city_info:
        try:
            float(city_info['latitude'])
            float(city_info['longitude'])
            G_filtered.add_node(city_name)
            city_lookup[city_name] = city_info
            valid_nodes_count += 1
        except (ValueError, TypeError):
            continue

print(f"Adicionados {valid_nodes_count} nós válidos ao grafo.")

print(f"Adicionando arestas direcionadas (apenas se dist_euclid <= {DISTANCE_THRESHOLD})...")
edges_added = 0
nodes_in_graph = list(G_filtered.nodes())

for i in range(len(nodes_in_graph)):
    city1_name = nodes_in_graph[i]
    city1_data = city_lookup[city1_name]
    lat1 = city1_data['latitude']
    lon1 = city1_data['longitude']
    pop1 = get_population(city1_data)

    for j in range(i + 1, len(nodes_in_graph)):
        city2_name = nodes_in_graph[j]
        city2_data = city_lookup[city2_name]
        lat2 = city2_data['latitude']
        lon2 = city2_data['longitude']
        pop2 = get_population(city2_data)

        distance = euclidean_distance(lat1, lon1, lat2, lon2)

        if distance <= DISTANCE_THRESHOLD + 1e-9:
            if pop2 > 0:
                G_filtered.add_edge(city1_name, city2_name, capacity=pop2)
                edges_added += 1
            if pop1 > 0:
                G_filtered.add_edge(city2_name, city1_name, capacity=pop1)
                edges_added += 1

print(f"Adicionadas {edges_added} arestas direcionadas ao grafo filtrado.")
if edges_added == 0:
    print(f"Aviso: Nenhuma conexão encontrada com distância <= {DISTANCE_THRESHOLD}.")

source_exists = SOURCE_CITY_NAME in G_filtered
sink_exists = SINK_CITY_NAME in G_filtered

if not source_exists:
    print(f"Erro: Cidade de origem '{SOURCE_CITY_NAME}' não está nos nós válidos do grafo.")
    exit()
if not sink_exists:
    print(f"Erro: Cidade de destino '{SINK_CITY_NAME}' não está nos nós válidos do grafo.")
    exit()

print(f"\nCalculando o fluxo máximo de '{SOURCE_CITY_NAME}' para '{SINK_CITY_NAME}'...")
print(f"(Considerando APENAS conexões com distância Euclidiana <= {DISTANCE_THRESHOLD})")

try:
    flow_value, flow_dict = nx.maximum_flow(G_filtered, SOURCE_CITY_NAME, SINK_CITY_NAME)

    print("-" * 40)
    print(f"Fluxo Máximo Calculado (Rede Filtrada por Distância): {flow_value:,.0f}")
    print("-" * 40)

except nx.NetworkXUnfeasible:
    print(f"Erro: Não há caminho viável entre '{SOURCE_CITY_NAME}' e '{SINK_CITY_NAME}'")
    print(f"no grafo filtrado (nenhuma rota usa apenas conexões com dist <= {DISTANCE_THRESHOLD}).")
except nx.NetworkXError as e:
    print(f"Erro do NetworkX durante o cálculo do fluxo máximo: {e}")
except Exception as e:
    print(f"Ocorreu um erro inesperado durante o cálculo do fluxo: {e}")