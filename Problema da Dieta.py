import pulp


custos        = [   35,     30,     60,     50,     27,     22   ]
vitamina_A    = [    1,      0,      2,      2,      1,      2   ] 
vitamina_C    = [    0,      1,      3,      1,      3,      2   ] 
min_vit_A     = 9
min_vit_C     = 19
num_ingredientes = 6


prob_dieta = pulp.LpProblem("Problema da Dieta", pulp.LpMinimize)

nomes_ingr = [f"Ingrediente_{i+1}" for i in range(num_ingredientes)]
x = pulp.LpVariable.dicts("Qtd", nomes_ingr, lowBound=0, cat='Continuous') 


prob_dieta += pulp.lpSum(custos[i] * x[nomes_ingr[i]] for i in range(num_ingredientes)), "Custo Total"


prob_dieta += pulp.lpSum(vitamina_A[i] * x[nomes_ingr[i]] for i in range(num_ingredientes)) >= min_vit_A, "Minimo Vitamina A"
prob_dieta += pulp.lpSum(vitamina_C[i] * x[nomes_ingr[i]] for i in range(num_ingredientes)) >= min_vit_C, "Minimo Vitamina C"


prob_dieta.solve()

print(f"Status: {pulp.LpStatus[prob_dieta.status]}")


print("Composição ótima da dieta:")
for v in prob_dieta.variables():
    if v.varValue > 0: 
        print(f"{v.name} = {v.varValue:.2f} unidades")

print(f"Custo Mínimo = {pulp.value(prob_dieta.objective):.2f}")