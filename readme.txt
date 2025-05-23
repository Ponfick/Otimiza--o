Primeiro Exercicio
Implementação de uma Meta-heurística de Solução Unica para o Bin-Packing

O código tem por objetivo maximizar o lucro total dos pedidos atendidos, e espeitar as restrições de capacidade mínima e máxima dos containers.

O código usa uma abordagem em duas fases:
1. Construção de uma Solução Inicial (Algoritmo Guloso): Tenta atribuir pedidos aos containers de forma gulosa.
2. Melhoria da Solução (Busca Local): Tenta corrigir violações de capacidade na solução inicial, movendo pedidos entre containers.

Algoritmo Guloso
Atribuir pedidos aos containers sequencialmente para satisfazer o problema. Ele ordenar os pedidos e os containers para apoiar o processo de atribuição.
Tem a restrição de sempre obedecer ao limite superior de capacidade. E satisfazer o máximo possível dos limites inferiores de capacidade.
Ele ordenar os containers em ordem decrescente pelos limites inferiores de capacidade. E ordenar os pedidos em ordem decrescente por peso. Para cada container, ele verificar os pedidos na lista de pedidos. Se o limite inferior do container for satisfeito, ele passar para o próximo container.
Ele percorre cada container uma vez, e para cada container percorre todos os pedidos uma vez.

Busca Local - First Improvement
O código permite modificar o total de carga que pode ser trocado entre os containers. Com o limite de troca definido, primeiro ele checa se o container está com a carga total satisfeita, se não, ele checa aleatoriamente dois containers que são aptos para realizar a troca, e verifica se eles se beneficiam de uma troca, se eles ferem o limite de carga é aplicada uma penalidade.

Os critérios de parada são
Todas as restrições de capacidade são satisfeitas
Não há mais pares de containers que possam trocar pedidos.
O tempo limite fornecido pelo usuário é atingido.

O arquivo input.txt
A primira linha mosta 1000 50, onde 1000 é o numero de pedidos e 50 é o numero de containers
da linha 2 ate a 1001 são os pedidos
0.145763 93.0, sendo quantidade 0.145763, lucro 93
da linha 1002 são os containers
0.318644 0.688136, sendo a capacidade minima 0.318644, e capacidade maxima 0.688136

Segundo Exercicio

São codigos para resolver os problemas vistos em aula

Problema da Ração
Problema da Dieta
Problema do Plantio
Problema das Tintas
Problema do Transporte
Problema do Fluxo Máximo
Problema do Escalonamento de Horários
Problema de Cobertura
Problema da Mochila
Problema de Padrões
Problema das Facilidades
Problema de Frequência
Problema da clique máxima
