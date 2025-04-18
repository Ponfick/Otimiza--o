import pulp

itens = ["Item_A", "Item_B", "Item_C", "Item_D"]
valores = {"Item_A": 60, "Item_B": 100, "Item_C": 120, "Item_D": 80}
pesos = {"Item_A": 10, "Item_B": 20, "Item_C": 30, "Item_D": 15}
capacidade_maxima = 50

prob_mochila = pulp.LpProblem("Problema da Mochila", pulp.LpMaximize)

x = pulp.LpVariable.dicts("Escolher", itens, cat='Binary')

prob_mochila += pulp.lpSum(valores[i] * x[i] for i in itens), "Valor Total"

prob_mochila += pulp.lpSum(pesos[i] * x[i] for i in itens) <= capacidade_maxima, "Limite Peso"

prob_mochila.solve()

print("Status:", pulp.LpStatus[prob_mochila.status])
print("Itens selecionados:")
for i in itens:
    if x[i].value() == 1:
        print(f"- {i}")
print("Valor total:", pulp.value(prob_mochila.objective))