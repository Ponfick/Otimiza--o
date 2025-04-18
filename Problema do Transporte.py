import pulp

fabricas = ["Fabrica1", "Fabrica2", "Fabrica3"]
depositos = ["Deposito1", "Deposito2", "Deposito3"]

oferta = {"Fabrica1": 120, "Fabrica2": 80, "Fabrica3": 80}
demanda = {"Deposito1": 150, "Deposito2": 70, "Deposito3": 60}

custos = {
    ("Fabrica1", "Deposito1"): 8,  ("Fabrica1", "Deposito2"): 5,  ("Fabrica1", "Deposito3"): 6,
    ("Fabrica2", "Deposito1"): 15, ("Fabrica2", "Deposito2"): 10, ("Fabrica2", "Deposito3"): 12,
    ("Fabrica3", "Deposito1"): 3,  ("Fabrica3", "Deposito2"): 9,  ("Fabrica3", "Deposito3"): 10,
}

prob_transporte = pulp.LpProblem("Problema de Transporte", pulp.LpMinimize)

rotas = [(f, d) for f in fabricas for d in depositos]
transporte_vars = pulp.LpVariable.dicts("Transporte", rotas, lowBound=0, cat='Continuous')

prob_transporte += pulp.lpSum(custos[r] * transporte_vars[r] for r in rotas), "Custo Total Transporte"

for f in fabricas:
    prob_transporte += pulp.lpSum(transporte_vars[(f, d)] for d in depositos) <= oferta[f], f"Oferta_{f}"

for d in depositos:
    prob_transporte += pulp.lpSum(transporte_vars[(f, d)] for f in fabricas) >= demanda[d], f"Demanda_{d}"

prob_transporte.solve()

print(f"Status: {pulp.LpStatus[prob_transporte.status]}")

print("\nPlano de Transporte Ótimo:")
for r in rotas:
    val = transporte_vars[r].varValue
    if val > 1e-6:
        print(f"De {r[0]} para {r[1]}: {val:.2f} unidades")

print(f"\nCusto Mínimo de Transporte = {pulp.value(prob_transporte.objective):.2f}")