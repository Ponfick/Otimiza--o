import pulp
import json
import os
import time

print("--- Resolvedor para Problema de Facilidades (lendo JSON) ---")


INPUT_JSON_FILE = 'Segundo Exercício\\facility_data.json'


start_time = time.time()

print(f"\n1. Lendo dados do problema do arquivo '{INPUT_JSON_FILE}'...")

if not os.path.exists(INPUT_JSON_FILE):
    print(f"Erro: Arquivo de dados '{INPUT_JSON_FILE}' não encontrado.")
    print("Execute primeiro o script 'generate_facility_data.py' para criar o arquivo.")
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
    potenciais_centros = problem_data["potential_facilities"]
    clientes = problem_data["customers"]
    custos_instalacao = problem_data["installation_costs"]
    custos_atendimento = problem_data["service_costs"]

    if not all([potenciais_centros, clientes, custos_instalacao, custos_atendimento]):
         raise ValueError("Estrutura de dados incompleta no JSON.")

    print(f"   > Dados carregados para {len(potenciais_centros)} centros e {len(clientes)} clientes.")

except KeyError as e:
    print(f"Erro: Chave esperada não encontrada no arquivo JSON: {e}")
    exit()
except ValueError as e:
     print(f"Erro: Problema com os dados lidos do JSON: {e}")
     exit()

print(f"   Tempo de leitura dos dados: {time.time() - start_time:.2f}s")


print("\n2. Configurando o modelo de otimização...")
model_setup_start_time = time.time()

prob_facilidades = pulp.LpProblem("Localizacao_Facilidades_from_JSON", pulp.LpMinimize)

y = pulp.LpVariable.dicts("Abrir_Centro", potenciais_centros, cat='Binary')

x = pulp.LpVariable.dicts("Atender", (potenciais_centros, clientes), cat='Binary')

custo_total_instalacao = pulp.lpSum(custos_instalacao[i] * y[i] for i in potenciais_centros)
custo_total_atendimento = pulp.lpSum(custos_atendimento[i][j] * x[i][j] for i in potenciais_centros for j in clientes)

prob_facilidades += custo_total_instalacao + custo_total_atendimento, "Custo_Total_Minimo"

for j in clientes:
    prob_facilidades += pulp.lpSum(x[i][j] for i in potenciais_centros) == 1, f"Req_Atendimento_Cli_{j}"

for i in potenciais_centros:
    for j in clientes:
        if i in custos_atendimento and j in custos_atendimento[i]:
             prob_facilidades += x[i][j] <= y[i], f"Vinculo_Aberto_Atende_{i}_{j}"
        else:
            print(f"Aviso: Custo de atendimento ausente para {i} -> {j}. Ignorando vínculo para este par.")


print(f"   Modelo configurado.")
print(f"   Tempo de configuração do modelo: {time.time() - model_setup_start_time:.2f}s")


print("\n3. Resolvendo o problema...")
solver_start_time = time.time()
status = prob_facilidades.solve()
print(f"   Tempo de resolução: {time.time() - solver_start_time:.2f}s")


print("-" * 50)
print(f"Status da Solução: {pulp.LpStatus[status]}")

if status == pulp.LpStatusOptimal:
    custo_minimo = pulp.value(prob_facilidades.objective)
    print(f"\nCusto Total Mínimo Encontrado: {custo_minimo:.2f}")

    print("\nCentros que devem ser ABERTOS:")
    centros_abertos = []
    custo_instalacao_solucao = 0
    for i in potenciais_centros:
        if y[i].varValue is not None and y[i].varValue > 0.9: 
            print(f"- {i} (Custo de Instalação: {custos_instalacao[i]})")
            centros_abertos.append(i)
            custo_instalacao_solucao += custos_instalacao[i]
    if not centros_abertos:
         print("   Nenhum centro selecionado para abrir.")
    print(f" --> Custo Total de Instalação: {custo_instalacao_solucao:.2f}")


    print("\nAtendimento aos Clientes:")
    custo_atendimento_solucao = 0
    for j in clientes:
        atendido = False
        for i in potenciais_centros:
            if x[i][j].varValue is not None and x[i][j].varValue > 0.9: 
                if i in custos_atendimento and j in custos_atendimento[i]:
                    custo_ij = custos_atendimento[i][j]
                    print(f"- {j} será atendido por {i} (Custo: {custo_ij})")
                    custo_atendimento_solucao += custo_ij
                    atendido = True
                    break
                else:
                    print(f"!!! ERRO: Solução indica atender {j} por {i}, mas custo c_ij não encontrado nos dados!")
                    atendido = True
                    break
        if not atendido:
             print(f"!!! ATENÇÃO: Cliente {j} não foi atribuído a nenhum centro na solução (verificar!)")

    print(f" --> Custo Total de Atendimento: {custo_atendimento_solucao:.2f}")

    custo_total_verificado = custo_instalacao_solucao + custo_atendimento_solucao
    print("\nVerificação do Custo Total da Solução:")
    print(f"  Instalação ({custo_instalacao_solucao:.2f}) + Atendimento ({custo_atendimento_solucao:.2f}) = {custo_total_verificado:.2f}")
    if abs(custo_total_verificado - custo_minimo) > 0.01:
        print("  Aviso: Custo verificado difere ligeiramente do objetivo do solver.")

elif status == pulp.LpStatusInfeasible:
    print("\nNão foi possível encontrar uma solução viável para este problema com os dados fornecidos.")
else:
    print("\nA solução ótima não foi encontrada. Status:", pulp.LpStatus[status])

print("-" * 50)
print(f"Tempo total de execução: {time.time() - start_time:.2f}s")