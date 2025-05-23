import time
import random as rd

def busca_local(n, k, pedidos, container, X, tempo_limite):
    soma_quantidades = [0 for _ in range(k)]
    for i in range(n):
        if X[i] != -1:
             soma_quantidades[X[i]] += pedidos[i][0]

    violacao = 0
    for v in range(k):
        if not (container[v][0] <= soma_quantidades[v] <= container[v][1]):
            violacao += 1

    def intervalo_mudanca(v):
        return container[v][0] - soma_quantidades[v], container[v][1] - soma_quantidades[v]

    def carga_valida(v):
        min_delta, max_delta = intervalo_mudanca(v)
        return min_delta * max_delta <= 0

    def podem_trocar(v1, v2):
        if carga_valida(v1) and carga_valida(v2):
            return False
        m1_min, m1_max = intervalo_mudanca(v1)
        m2_min, m2_max = intervalo_mudanca(v2)
        if m1_min * m2_max < 0 or m1_max * m2_min < 0:
            return True
        if (not carga_valida(v1) and carga_valida(v2)) or \
           (carga_valida(v1) and not carga_valida(v2)):
             if m1_min * (-m2_min) < 0 or m1_max * (-m2_max) < 0:
                  return True
        return False

    def escolher_container():
        candidatos = []
        for i in range(k):
            for j in range(i + 1, k):
                if podem_trocar(i, j):
                    candidatos.append((i, j))
        return rd.choice(candidatos) if candidatos else None


    def mudanca_aceitavel(v1, v2):
        r1_min, r1_max = intervalo_mudanca(v1)
        r2_min_inv, r2_max_inv = intervalo_mudanca(v2)
        r2_min, r2_max = -r2_max_inv, -r2_min_inv
        min_aceitavel = max(r1_min, r2_min)
        max_aceitavel = min(r1_max, r2_max)
        return (min_aceitavel, max_aceitavel) if min_aceitavel <= max_aceitavel else None

    pedidos.append([0, 0])

    def escolher_pedidos_para_troca(v1, v2, intervalo_aceit):
        if intervalo_aceit is None:
             return None
        min_mudanca, max_mudanca = intervalo_aceit
        candidatos_v1 = [n] + [o for o in range(n) if X[o] == v1]
        candidatos_v2 = [n] + [o for o in range(n) if X[o] == v2]
        for i in candidatos_v1:
            quant_i = pedidos[i][0]
            for j in candidatos_v2:
                if i == n and j == n: continue
                quant_j = pedidos[j][0]
                mudanca_liquida = quant_j - quant_i
                if min_mudanca <= mudanca_liquida <= max_mudanca:
                    return i, j, mudanca_liquida
        return None

    inicio_tempo = time.time()

    while True:
        if violacao == 0:
            break
        if time.time() - inicio_tempo >= tempo_limite:
            print("Tempo limite atingido. Interrompendo a execução...")
            break
        par_container = escolher_container()
        if par_container is None:
            break
        v1, v2 = par_container
        intervalo_aceit = mudanca_aceitavel(v1, v2)
        troca_escolhida = escolher_pedidos_para_troca(v1, v2, intervalo_aceit)
        if troca_escolhida is not None:
            pedido_i, pedido_j, mudanca_liq = troca_escolhida
            pre_v1_valido = carga_valida(v1)
            pre_v2_valido = carga_valida(v2)
            if pedido_i != n: X[pedido_i] = v2
            if pedido_j != n: X[pedido_j] = v1
            soma_quantidades[v1] += mudanca_liq
            soma_quantidades[v2] -= mudanca_liq
            if not pre_v1_valido and carga_valida(v1): violacao -= 1
            elif pre_v1_valido and not carga_valida(v1): violacao += 1
            if not pre_v2_valido and carga_valida(v2): violacao -= 1
            elif pre_v2_valido and not carga_valida(v2): violacao += 1

    pedidos.pop()

Pedidos = []
container = []

with open('Primeiro Exercício\input.txt', 'r') as f:
    n, k = map(int, f.readline().split())
    for _ in range(n):
        Pedidos.append(list(map(float, f.readline().split())))  
    for _ in range(k):
        container.append(list(map(float, f.readline().split())))

tempo_inicio = time.time()

tempo_limite = float(input("Digite o tempo limite de execução (em segundos): "))

pedidos_enumerados = sorted(enumerate(Pedidos), key=lambda x: x[1][0], reverse=True)
container_enumerados = sorted(enumerate(container), key=lambda x: x[1][0], reverse=True)

carga_atual = [0] * k
pedido_atendido = [False] * n
X = [-1] * n

for indice_container, container_atual in container_enumerados:
    for indice_pedido, pedido_atual in pedidos_enumerados:
        if not pedido_atendido[indice_pedido] and \
           carga_atual[indice_container] + pedido_atual[0] <= container_atual[1]:
            pedido_atendido[indice_pedido] = True
            carga_atual[indice_container] += pedido_atual[0]
            X[indice_pedido] = indice_container

busca_local(n, k, Pedidos, container, X, tempo_limite)

tempo_fim = time.time()

contagem_pedidos = 0
lucro_total = 0
for i in range(n):
    if X[i] != -1:
        contagem_pedidos += 1
        lucro_total += Pedidos[i][1]

print("Pedidos Atendidos:", contagem_pedidos)
print("Lucro Total:", lucro_total)
print("Tempo de Execução (s):", tempo_fim - tempo_inicio)
