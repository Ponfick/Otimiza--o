import pulp

prob_racao = pulp.LpProblem("Problema da Racao", pulp.LpMaximize)

x_amgs = pulp.LpVariable("Kg_AMGS", lowBound=0, cat='Continuous') 
x_re = pulp.LpVariable("Kg_RE", lowBound=0, cat='Continuous')   


prob_racao += 11 * x_amgs + 12 * x_re, "Lucro Total"

prob_racao += 5 * x_amgs + 2 * x_re <= 30000, "Limite Cereais"

prob_racao += 1 * x_amgs + 4 * x_re <= 10000, "Limite Carne"

prob_racao.solve()

print(f"Status: {pulp.LpStatus[prob_racao.status]}")

print("Produção ótima:")
for v in prob_racao.variables():
    print(f"{v.name} = {v.varValue:.2f} kg")

print(f"Lucro Máximo = R$ {pulp.value(prob_racao.objective):.2f}")