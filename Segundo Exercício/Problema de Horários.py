import pulp

dias = range(1, 8) 
demanda_diaria = {
    1: 17, 2: 13, 3: 15, 4: 19, 5: 14, 6: 16, 7: 11
}


prob_horarios = pulp.LpProblem("Escalonamento Enfermeiras", pulp.LpMinimize)

x = pulp.LpVariable.dicts("Inicio_Dia_", dias, lowBound=0, cat='Integer')

prob_horarios += pulp.lpSum(x[i] for i in dias), "Total Enfermeiras"


for dia_atual in dias:
    indices_trabalhando = [(dia_atual - k - 1) % 7 + 1 for k in range(5)]
    prob_horarios += pulp.lpSum(x[i] for i in indices_trabalhando) >= demanda_diaria[dia_atual], f"Demanda_Dia_{dia_atual}"

prob_horarios.solve()

print("Status:", pulp.LpStatus[prob_horarios.status])
print("Número total de enfermeiras:", pulp.value(prob_horarios.objective))
for dia in dias:
    print(f"Enfermeiras começando no dia {dia}: {x[dia].varValue}")

print("Estrutura do problema de Escalonamento criada.")
print("Preencha 'demanda_diaria' e descomente a linha prob_horarios.solve() para executar.")