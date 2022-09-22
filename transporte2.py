from pulp import *

# Lista das filiais
Filiais = ["A", "B", "C", "D", "E"]

# Lista com a a capacidade máxima de cada filial
supply = {"A": 175, "B": 175, "C": 175, "D": 175, "E": 175}

# Lista com a entrega mínima de cada filial
minimum = {"A": 25, "B": 30, "C": 30, "D": 35, "E": 25}

# Lista dos contratos
Contratos = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]

# Dicionário com a demanda mínima de fornecimento dos contratos
demand_1 = {
    "1": 100,
    "2": 65,
    "3": 100,
    "4": 70,
    "5": 120,
    "6": 60,
    "7": 75,
    "8": 100,
    "9": 95,
    "10": 85,
}

# Dicionário com a demanda mínima de fornecedores dos contratos
demand_2 = {
    "1": 3,
    "2": 2,
    "3": 3,
    "4": 2,
    "5": 3,
    "6": 2,
    "7": 2,
    "8": 3,
    "9": 3,
    "10": 3,
}

# Lista dos custos de tranporte
costs = [  # Contratos
    # 1 2 3 4 5
    [10, 15, 10, 15, 20, 20, 20, 40, 10, 30],   # A   Filiais
    [30, 15, 10, 20, 10, 20, 20, 30, 20, 30],   # B
    [20, 10, 5, 15, 10, 15, 15, 10, 5, 5],      # C
    [40, 25, 15, 20, 10, 30, 30, 10, 15, 10],   # D
    [30, 30, 25, 10, 5, 35, 35, 15, 5, 10],     # E
]

# Dicionário dos custos de transporte
costs = makeDict([Filiais, Contratos], costs, 0)

# Variável problema
prob = LpProblem("Beer Distribution Problem", LpMinimize)

# Lista de todos pares ordenados associados os possíveis caminhos de uma filial a um contrato
Routes = [(w, b) for w in Filiais for b in Contratos]

# Dicionários das variávies

# Variáveis contínuas, associadas a quantidade entregue por certa filial a certo contrato
vars_1 = LpVariable.dicts("Peso", (Filiais, Contratos), 0, None, LpContinuous)

# Variáveis binárias, associadas a existência ou não de entrega entre uma filial e um contrato
vars_2 = LpVariable.dicts("Rota", (Filiais, Contratos), cat = "Binary")


# Função custo
prob += (
    lpSum([vars_1[w][b] * costs[w][b] for (w, b) in Routes]),
    "Sum_of_Transporting_Costs",
)

# Condições associadas à capacidade máxima de cada filial
for w in Filiais:
    prob += (
        lpSum([vars_1[w][b] for b in Contratos]) <= supply[w],
        "Sum_of_Products_out_of_Warehouse_%s" % w,
    )

# Condições associadas à entrega mínima de cada filial
for (w,b) in Routes:
    prob += (
        vars_1[w][b] >= minimum[w] * vars_2[w][b],
        "Minimum_delivered_by_%s_to_%s" % (w, b),
    )

# Condições associadas à demanda de cada contrato (quantidade de produtos)
for b in Contratos:
    prob += (
        lpSum([vars_1[w][b] for w in Filiais]) >= demand_1[b],
        "Sum_of_Products_into_Bar%s" % b,
    )

# Condições associadas à demanda de cada contrato (quantidade de fornecedores)
for b in Contratos:
    prob += (
        lpSum([vars_2[w][b] for w in Filiais]) >= demand_2[b],
        "Num_supply_Bar%s" % b,
    )

# As informações do problema são escritas num arquivo .lp
prob.writeLP("BeerDistributionProblem.lp")

# Resolução do problema
prob.solve(PULP_CBC_CMD(msg=0))

# Status da solução 
print("Status:", LpStatus[prob.status])

# O valor de cada variável
for v in prob.variables():
    print(v.name, "=", v.varValue)

# O valor da função custo otimizada
print("Total Cost of Transportation = ", value(prob.objective))