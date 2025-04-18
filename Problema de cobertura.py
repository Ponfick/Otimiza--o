import json
import math
# import networkx as nx # Não estritamente necessário aqui
import pulp
import os
import time

# --- Configuration ---
JSON_FILE = 'cities.json'
# Distância Euclidiana máxima (em graus lat/lon) para uma cidade cobrir outra
DISTANCE_THRESHOLD = 2.5
# Tolerância para comparação de ponto flutuante
TOLERANCE = 1e-9
# --- End Configuration ---

def euclidean_distance(lat1, lon1, lat2, lon2):
    """
    Calculates the simple Euclidean distance based on raw latitude and
    longitude degrees. Returns float('inf') on error.
    """
    try:
        lat1_f, lon1_f, lat2_f, lon2_f = map(float, [lat1, lon1, lat2, lon2])
        dist = math.sqrt((lat1_f - lat2_f)**2 + (lon1_f - lon2_f)**2)
        return dist
    except (ValueError, TypeError):
        return float('inf') # Retorna infinito para garantir que falhe no teste <= threshold

# --- 1. Load Data & Identify Cities ---
start_time = time.time()
if not os.path.exists(JSON_FILE):
    print(f"Erro: Arquivo '{JSON_FILE}' não encontrado.")
    exit()

try:
    with open(JSON_FILE, 'r', encoding='utf-8') as f:
        all_cities_data = json.load(f)
except Exception as e:
    print(f"Erro ao ler ou decodificar o arquivo JSON '{JSON_FILE}': {e}")
    exit()

# Filtra cidades com nome e coordenadas válidas.
# Essas cidades são tanto os locais potenciais para escolas
# quanto as cidades que precisam ser cobertas.
cities_data = {} # Dict: city_name -> {'lat': lat, 'lon': lon}
print("1. Identificando cidades válidas...")
for city_info in all_cities_data:
    city_name = city_info.get('city', 'Unknown').strip()
    if not city_name or city_name == 'Unknown': continue
    try:
        lat = float(city_info['latitude'])
        lon = float(city_info['longitude'])
        cities_data[city_name] = {'lat': lat, 'lon': lon}
    except (ValueError, TypeError, KeyError):
        continue # Pula cidades com dados inválidos/ausentes

if not cities_data:
    print("Erro: Nenhuma cidade válida com coordenadas encontrada no arquivo.")
    exit()

potential_school_locations = list(cities_data.keys())
cities_requiring_coverage = list(cities_data.keys()) # Todas as cidades válidas precisam ser cobertas

print(f"   Encontradas {len(cities_data)} cidades válidas.")
print(f"   Tempo decorrido: {time.time() - start_time:.2f}s")

# --- 2. Precompute Coverage Relationships ---
# Para cada cidade 'i' (que precisa ser coberta), encontrar o conjunto N(i)
# de cidades 'j' (locais potenciais de escolas) que podem cobri-la.
# N(i) = {j | distance(i, j) <= DISTANCE_THRESHOLD}
coverage_map = {city_i: [] for city_i in cities_requiring_coverage}
print(f"\n2. Calculando cobertura (dist <= {DISTANCE_THRESHOLD})...")
calculation_start_time = time.time()

num_calcs = 0
for city_i_name in cities_requiring_coverage:
    city_i_data = cities_data[city_i_name]
    lat_i, lon_i = city_i_data['lat'], city_i_data['lon']

    for city_j_name in potential_school_locations: # 'j' é onde a escola pode estar
        city_j_data = cities_data[city_j_name]
        lat_j, lon_j = city_j_data['lat'], city_j_data['lon']

        distance = euclidean_distance(lat_i, lon_i, lat_j, lon_j)
        num_calcs += 1

        # Se a escola em 'j' cobre a cidade 'i'
        if distance <= DISTANCE_THRESHOLD + TOLERANCE:
            coverage_map[city_i_name].append(city_j_name)

print(f"   Cálculos de distância realizados: {num_calcs}")
print(f"   Tempo decorrido nesta etapa: {time.time() - calculation_start_time:.2f}s")


# Verifica se alguma cidade ficou sem cobertura possível
uncoverable_cities = []
for city_name, covering_cities in coverage_map.items():
    if not covering_cities:
        uncoverable_cities.append(city_name)

if uncoverable_cities:
    print(f"\nAviso: {len(uncoverable_cities)} cidades não podem ser cobertas por nenhuma localidade")
    print(f"       (incluindo elas mesmas) com a distância <= {DISTANCE_THRESHOLD}:")
    print(f"       Exemplos: {', '.join(uncoverable_cities[:10])}{'...' if len(uncoverable_cities) > 10 else ''}")

    # Remove cidades incobertas da lista de cidades que precisam de cobertura
    original_count = len(cities_requiring_coverage)
    cities_requiring_coverage = [city for city in cities_requiring_coverage if city not in uncoverable_cities]
    print(f"   --> Estas cidades serão ignoradas. Tentando cobrir as {len(cities_requiring_coverage)} cidades restantes.")
    if not cities_requiring_coverage:
         print("\nNenhuma cidade restante que precise e possa ser coberta. Encerrando.")
         exit()


# --- 3. Set up ILP Model (Set Covering) ---
print("\n3. Configurando o modelo de Otimização Linear Inteira...")
model_setup_start_time = time.time()

# Cria o problema de minimização
prob_cobertura = pulp.LpProblem("Cobertura_Escolas_Pais", pulp.LpMinimize)

# Cria as variáveis binárias: x_j = 1 se construir escola em j, 0 caso contrário
# Usar nomes válidos para variáveis PuLP (sem espaços, etc.)
var_names = {city: f"Escola_{i}" for i, city in enumerate(potential_school_locations)}
x = pulp.LpVariable.dicts("Construir", potential_school_locations, cat='Binary')

# Função Objetivo: Minimizar o número total de escolas construídas
prob_cobertura += pulp.lpSum(x[j] for j in potential_school_locations), "Numero_Total_Escolas"

# Restrições: Cada cidade 'i' (que pode ser coberta) deve ser coberta por >= 1 escola
constraints_added = 0
for city_i_name in cities_requiring_coverage:
    # Obtém a lista de cidades 'j' que podem cobrir 'i'
    potential_covers = coverage_map.get(city_i_name, [])
    # Se houver alguma cidade que pode cobrir 'i', adiciona a restrição
    if potential_covers:
         constraint_name = f"Cobrir_{city_i_name[:20].replace(' ','_').replace('-','_').replace('.','')}" # Nome curto e válido
         prob_cobertura += pulp.lpSum(x[j] for j in potential_covers) >= 1, constraint_name
         constraints_added += 1

print(f"   Variáveis binárias criadas: {len(potential_school_locations)}")
print(f"   Restrições de cobertura adicionadas: {constraints_added}")
print(f"   Tempo decorrido nesta etapa: {time.time() - model_setup_start_time:.2f}s")


# --- 4. Solve the ILP ---
print("\n4. Resolvendo o problema de otimização (pode levar tempo)...")
solver_start_time = time.time()
# Você pode especificar um solver ou aumentar o tempo limite se necessário
# Ex: prob_cobertura.solve(pulp.PULP_CBC_CMD(timeLimit=600, msg=True))
status = prob_cobertura.solve()
print(f"   Tempo de resolução: {time.time() - solver_start_time:.2f}s")

# --- 5. Output Results ---
print("-" * 40)
print(f"Status da Solução: {pulp.LpStatus[status]}")

if status == pulp.LpStatusOptimal:
    min_escolas = int(round(pulp.value(prob_cobertura.objective))) # Arredonda para inteiro
    print(f"Número Mínimo de Escolas Necessárias: {min_escolas}")

    print("\nCidades selecionadas para construir escolas:")
    locais_escolas = []
    for j in potential_school_locations:
        if x[j].varValue is not None and x[j].varValue > 0.5: # Checa se a variável é ~= 1
            locais_escolas.append(j)

    # Ordena e imprime a lista
    locais_escolas.sort()
    for local in locais_escolas:
        print(f"- {local}")

    print(f"\nTotal: {len(locais_escolas)} locais selecionados.")
    if len(locais_escolas) != min_escolas:
         print(f"Aviso: Contagem de locais ({len(locais_escolas)}) difere do objetivo ({min_escolas}). Verifique arredondamento ou solução.")

    # Verificação opcional da cobertura (pode ser lenta se houver muitas cidades)
    # print("\nVerificando cobertura da solução...")
    # ... (código de verificação como no pensamento anterior) ...


elif status == pulp.LpStatusInfeasible:
    print("O problema é inviável. Não foi possível encontrar um conjunto de escolas")
    print("que cubra todas as cidades requeridas com as regras de distância dadas.")
    if uncoverable_cities:
         print("(Lembre-se que algumas cidades já foram identificadas como impossíveis de cobrir.)")
else:
    print("Não foi possível encontrar uma solução ótima garantida.")
    print("O status foi:", pulp.LpStatus[status])
    print("(Pode ser inviável, ilimitado, ou o solver pode ter atingido um limite de tempo/memória).")

print("-" * 40)
print(f"Tempo total de execução: {time.time() - start_time:.2f}s")