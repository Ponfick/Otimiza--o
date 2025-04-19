import pulp

max_folha_1 = 200
max_folha_2 = 90

padroes_data = {
    1: {'folha': 1, 'corpos': 1, 'tampas': 7},
    2: {'folha': 2, 'corpos': 2, 'tampas': 3},
    3: {'folha': 1, 'corpos': 0, 'tampas': 9},
    4: {'folha': 1, 'corpos': 4, 'tampas': 4}
}
indices_padroes = list(padroes_data.keys())

receita_lata = 50
custo_corpo_nao_usado = 50
custo_tampa_produzida = 3

prob_padroes = pulp.LpProblem("Problema_Padroes_Latinhas_v2", pulp.LpMaximize)

x = pulp.LpVariable.dicts("Usar_Padrao", indices_padroes, lowBound=0, cat='Integer')
N_cans = pulp.LpVariable("Latas_Completas", lowBound=0, cat='Integer')

prob_padroes += 100*N_cans - 71*x[1] - 109*x[2] - 27*x[3] - 212*x[4], "Lucro_Total"

folha1_usada = pulp.lpSum(x[p] for p in indices_padroes if padroes_data[p]['folha'] == 1)
prob_padroes += folha1_usada <= max_folha_1, "Limite_Folha_1"

folha2_usada = pulp.lpSum(x[p] for p in indices_padroes if padroes_data[p]['folha'] == 2)
prob_padroes += folha2_usada <= max_folha_2, "Limite_Folha_2"

total_corpos_expr = pulp.lpSum(padroes_data[p]['corpos'] * x[p] for p in indices_padroes)
prob_padroes += N_cans - total_corpos_expr <= 0, "Limite_Corpos"

total_tampas_expr = pulp.lpSum(padroes_data[p]['tampas'] * x[p] for p in indices_padroes)
prob_padroes += N_cans - total_tampas_expr <= 0, "Limite_Tampas"

print("Resolvendo o problema de otimização...")
status = prob_padroes.solve()

print("-" * 70)
print(f"Status da Solução: {pulp.LpStatus[status]}")

if status == pulp.LpStatusOptimal:
    print("\nSolução Ótima Encontrada:")
    lucro_calculado = pulp.value(prob_padroes.objective)
    print(f"Lucro Máximo: {lucro_calculado:.2f}")
    latas_produzidas = N_cans.varValue
    print(f"Número de Latas Completas a Produzir: {latas_produzidas:.0f}")

    print("\nNúmero de vezes para usar cada padrão:")
    total_corpos_prod = 0
    total_tampas_prod = 0
    folhas1_usadas_calc = 0
    folhas2_usadas_calc = 0
    for p in indices_padroes:
        num_usos = x[p].varValue
        print(f"  Padrão {p}: {num_usos:.0f} vezes")
        total_corpos_prod += padroes_data[p]['corpos'] * num_usos
        total_tampas_prod += padroes_data[p]['tampas'] * num_usos
        if padroes_data[p]['folha'] == 1:
            folhas1_usadas_calc += num_usos
        elif padroes_data[p]['folha'] == 2:
            folhas2_usadas_calc += num_usos

    print("\nRecursos Utilizados:")
    print(f"  Folhas Tipo 1: {folhas1_usadas_calc:.0f} / {max_folha_1}")
    print(f"  Folhas Tipo 2: {folhas2_usadas_calc:.0f} / {max_folha_2}")

    print("\nProdução e Sobras:")
    print(f"  Total Corpos Produzidos: {total_corpos_prod:.0f}")
    print(f"  Total Tampas Produzidas: {total_tampas_prod:.0f}")
    corpos_nao_usados = total_corpos_prod - latas_produzidas
    tampas_excesso = total_tampas_prod - latas_produzidas
    print(f"  Corpos Não Utilizados (custo {custo_corpo_nao_usado}): {corpos_nao_usados:.0f}")
    print(f"  Tampas em Excesso: {tampas_excesso:.0f}")
    print(f"  (Custo do Excesso de {custo_corpo_nao_usado * corpos_nao_usados:.0f} por copos e {3 * tampas_excesso:.0f} por tapas)")

    lucro_verif = receita_lata * latas_produzidas \
                  - custo_corpo_nao_usado * corpos_nao_usados \
                  - custo_tampa_produzida * total_tampas_prod
    print(f"\nVerificação do Lucro: {lucro_verif:.2f}")
    if abs(lucro_verif - lucro_calculado) > 0.01:
        print("Aviso: Lucro verificado difere ligeiramente do objetivo calculado pelo solver.")

else:
    print("Não foi possível encontrar uma solução ótima.")
    print("Status:", pulp.LpStatus[status])

print("-" * 70)