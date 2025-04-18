import pulp

fazendas = ["Fazenda1", "Fazenda2", "Fazenda3"]
culturas = ["Milho", "Arroz", "Feijao"]

area_fazenda = {"Fazenda1": 400, "Fazenda2": 650, "Fazenda3": 350}
agua_fazenda = {"Fazenda1": 1800, "Fazenda2": 2200, "Fazenda3": 950}

area_max_cultura = {"Milho": 660, "Arroz": 880, "Feijao": 400}
agua_por_area = {"Milho": 5.5, "Arroz": 4, "Feijao": 3.5}
lucro_por_area = {"Milho": 5000, "Arroz": 4000, "Feijao": 1800}

prob_plantio = pulp.LpProblem("Problema do Plantio", pulp.LpMaximize)

plantio_vars = pulp.LpVariable.dicts("Area", (fazendas, culturas), lowBound=0, cat='Continuous')

prob_plantio += pulp.lpSum(lucro_por_area[c] * plantio_vars[f][c] for f in fazendas for c in culturas), "Lucro Total"

for f in fazendas:
    prob_plantio += pulp.lpSum(plantio_vars[f][c] for c in culturas) <= area_fazenda[f], f"Area_{f}"

for f in fazendas:
    prob_plantio += pulp.lpSum(agua_por_area[c] * plantio_vars[f][c] for c in culturas) <= agua_fazenda[f], f"Agua_{f}"

for c in culturas:
    prob_plantio += pulp.lpSum(plantio_vars[f][c] for f in fazendas) <= area_max_cultura[c], f"AreaMax_{c}"

prob_plantio += pulp.lpSum(plantio_vars["Fazenda1"][c] for c in culturas) * area_fazenda["Fazenda2"] == \
                pulp.lpSum(plantio_vars["Fazenda2"][c] for c in culturas) * area_fazenda["Fazenda1"], "Proporcao_F1_F2"

prob_plantio += pulp.lpSum(plantio_vars["Fazenda2"][c] for c in culturas) * area_fazenda["Fazenda3"] == \
                pulp.lpSum(plantio_vars["Fazenda3"][c] for c in culturas) * area_fazenda["Fazenda2"], "Proporcao_F2_F3"

prob_plantio.solve()

print(f"Status: {pulp.LpStatus[prob_plantio.status]}")

print("Plano de Plantio Ótimo (em acres):")
total_area_cultivada = {f: 0 for f in fazendas}
for f in fazendas:
    print(f"--- Fazenda: {f} ---")
    for c in culturas:
        val = plantio_vars[f][c].varValue
        if val > 1e-6:
            print(f"  {c}: {val:.2f}")
            total_area_cultivada[f] += val

print("\nVerificação da Proporção:")
for f in fazendas:
    prop = (total_area_cultivada[f] / area_fazenda[f]) * 100 if area_fazenda[f] > 0 else 0
    print(f"Fazenda {f}: {total_area_cultivada[f]:.2f} / {area_fazenda[f]} acres cultivados ({prop:.2f}%)")

print(f"\nLucro Máximo Total = R$ {pulp.value(prob_plantio.objective):.2f}")