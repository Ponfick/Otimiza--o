import pulp

produtos = ["SolventeA", "SolventeB", "SEC", "COR"]
tintas = ["SR", "SN"]

custo_produto = {"SolventeA": 1.5, "SolventeB": 1.0, "SEC": 4.0, "COR": 6.0}

comp_sec = {"SolventeA": 0.30, "SolventeB": 0.60, "SEC": 1.0, "COR": 0.0}
comp_cor = {"SolventeA": 0.70, "SolventeB": 0.40, "SEC": 0.0, "COR": 1.0}

demanda_tinta = {"SR": 1000, "SN": 250}
min_sec_req = {"SR": 0.25, "SN": 0.20}
min_cor_req = {"SR": 0.50, "SN": 0.50}

prob_tintas = pulp.LpProblem("Problema das Tintas", pulp.LpMinimize)

qtd_vars = pulp.LpVariable.dicts("Qtd", (produtos, tintas), lowBound=0, cat='Continuous')

prob_tintas += pulp.lpSum(custo_produto[p] * pulp.lpSum(qtd_vars[p][t] for t in tintas) for p in produtos), "Custo Total"

for t in tintas:
    prob_tintas += pulp.lpSum(qtd_vars[p][t] for p in produtos) == demanda_tinta[t], f"Volume_{t}"

for t in tintas:
    total_sec_em_t = pulp.lpSum(comp_sec[p] * qtd_vars[p][t] for p in produtos)
    min_sec_necessario = min_sec_req[t] * demanda_tinta[t]
    prob_tintas += total_sec_em_t >= min_sec_necessario, f"Min_SEC_{t}"

for t in tintas:
    total_cor_em_t = pulp.lpSum(comp_cor[p] * qtd_vars[p][t] for p in produtos)
    min_cor_necessario = min_cor_req[t] * demanda_tinta[t]
    prob_tintas += total_cor_em_t >= min_cor_necessario, f"Min_COR_{t}"

prob_tintas.solve()

print(f"Status: {pulp.LpStatus[prob_tintas.status]}")

print("\nQuantidades a comprar (em litros):")
total_por_produto = {p: 0 for p in produtos}
for t in tintas:
    print(f"--- Para Tinta {t} ---")
    for p in produtos:
        val = qtd_vars[p][t].varValue
        if val > 1e-6:
            print(f"  {p}: {val:.2f}")
            total_por_produto[p] += val

print("\n--- Total por Produto ---")
for p in produtos:
     if total_por_produto[p] > 1e-6:
        print(f"  {p}: {total_por_produto[p]:.2f}")

print(f"\nCusto Mínimo Total = R$ {pulp.value(prob_tintas.objective):.2f}")