import random
N_TEAMS = 20           # Número de equipes (deve ser par)
POPULATION_SIZE = 200   # Tamanho da população
MAX_GENERATIONS = 1000   # Número de gerações
MUTATION_PROBABILITY = 0.05 # Probabilidade de mutação 
MAX_CONSECUTIVE_GAMES = 3 # Máximo de jogos consecutivos em casa/fora

def swap_sequence(seq):
    """Inverte uma sequência de jogos (0s para 1s e vice-versa)."""
    return [1 - gene for gene in seq]

def is_valid_sequence(seq):
    """Verifica se uma sequência viola a regra de jogos consecutivos."""
    if len(seq) <= MAX_CONSECUTIVE_GAMES:
        return True
    for i in range(len(seq) - MAX_CONSECUTIVE_GAMES):
        if all(seq[j] == seq[i] for j in range(i, i + MAX_CONSECUTIVE_GAMES + 1)):
            return False
    return True

def create_random_travel_sequence(n_weeks):
    """Cria uma sequência de viagens válida para a primeira metade do torneio."""
    while True:
        seq_half = [random.randint(0, 1) for _ in range(n_weeks)]
        full_seq = seq_half + swap_sequence(seq_half)
        if is_valid_sequence(full_seq):
            return seq_half

def create_individual():
    """Cria um indivíduo (Tabela A) completo e válido."""
    n_first_half_weeks = N_TEAMS - 1
    first_half_teams = [create_random_travel_sequence(n_first_half_weeks) for _ in range(N_TEAMS // 2)]
    second_half_teams = [swap_sequence(seq) for seq in first_half_teams]
    return first_half_teams + second_half_teams

def calculate_fitness(individual):
    """Calcula o número total de viagens (fitness) de um indivíduo."""
    total_travels = 0
    for team_seq in individual:
        team_travels = 0
        if team_seq[0] == 1:
            team_travels += 1
        for i in range(len(team_seq) - 1):
            if team_seq[i] == 0 and team_seq[i+1] == 1:
                team_travels += 1
        total_travels += team_travels
    return total_travels

# --- Operadores Genéticos ---

def tournament_selection(population_with_fitness, k=3):
    """Seleciona um indivíduo usando o método de torneio."""
    tournament_contenders = random.sample(population_with_fitness, k)
    tournament_contenders.sort(key=lambda x: x[1])
    return tournament_contenders[0][0]

def crossover(parent1, parent2):
    """Executa o crossover de um ponto para cada sequência de time."""
    n_first_half_weeks = N_TEAMS - 1
    n_first_half_teams = N_TEAMS // 2
    child_first_half = []

    for i in range(n_first_half_teams):
        # Evita erro se n_first_half_weeks for 1
        if n_first_half_weeks > 1:
            crossover_point = random.randint(1, n_first_half_weeks - 1)
        else:
            crossover_point = 1
            
        child_seq = parent1[i][:crossover_point] + parent2[i][crossover_point:]
        child_first_half.append(child_seq)

    child_second_half = [swap_sequence(seq) for seq in child_first_half]
    return child_first_half + child_second_half
    
def mutate(individual):
    if random.random() > MUTATION_PROBABILITY:
        return individual

    mutated_ind = [list(row) for row in individual]
    team_idx = random.randrange(N_TEAMS // 2) # Muta apenas na primeira metade

    n_weeks = N_TEAMS - 1
    if n_weeks < 2: return individual # Não é possível trocar

    # Sorteia dois índices diferentes para trocar
    week_idx1, week_idx2 = random.sample(range(n_weeks), 2)

    # Faz a troca na primeira metade
    seq_half = mutated_ind[team_idx]
    seq_half[week_idx1], seq_half[week_idx2] = seq_half[week_idx2], seq_half[week_idx1]

    # Verifica se a nova sequência completa é válida
    if is_valid_sequence(seq_half + swap_sequence(seq_half)):
        # Se for válida, atualiza a segunda metade (o espelho)
        mutated_ind[team_idx + (N_TEAMS // 2)] = swap_sequence(seq_half)
        return mutated_ind

    # Se a mutação gerou um indivíduo inválido, retorna o original
    return individual

# --- Função Principal ---

def main():
    """Orquestra a execução do algoritmo genético."""
    print("Programa iniciado. Preparando para criar a população...")
    
    # 1. Inicialização
    population = [create_individual() for _ in range(POPULATION_SIZE)]
    
    print("População inicial criada com sucesso!")
    print(f"Iniciando o Algoritmo Genético para {N_TEAMS} equipes...")
    print(f"Tamanho da População: {POPULATION_SIZE}, Gerações: {MAX_GENERATIONS}\n")

    for gen in range(MAX_GENERATIONS):
        best_fitness_overall = float('inf')
        new_population = []
        # 2. Avaliação
        population_with_fitness = [(ind, calculate_fitness(ind)) for ind in population]
        
        # 3. Seleção 
        population_with_fitness.sort(key=lambda x: x[1])
        
        # Guarda o melhor de todos os tempos
        if population_with_fitness[0][1] < best_fitness_overall:
            best_fitness_overall = population_with_fitness[0][1]

        elites = [population_with_fitness[0][0], population_with_fitness[1][0]]
        
        # 4. Geração da Nova População
        while len(new_population) < POPULATION_SIZE:
            parent1 = tournament_selection(population_with_fitness)
            parent2 = tournament_selection(population_with_fitness)
            
            # Tenta gerar um filho válido
            for _ in range(10): # Loop para garantir que os operadores gerem um filho válido
                child_half = crossover(parent1, parent2)[:N_TEAMS // 2]
                # Verifica se o filho gerado é válido
                is_valid_after_crossover = True
                for seq_half in child_half:
                    if not is_valid_sequence(seq_half + swap_sequence(seq_half)):
                        is_valid_after_crossover = False
                        break
                
                if is_valid_after_crossover:
                    # Aplica mutação apenas se o crossover foi válido
                    full_child = child_half + [swap_sequence(s) for s in child_half]
                    mutated_child = mutate(full_child) # ou swap_mutate(full_child)
                    new_population.append(mutated_child)
                    break # Filho válido criado, sai do loop de tentativas
        
                population = new_population

                
        current_best_fitness = population_with_fitness[0][1]
        print(f"Geração {gen+1: >4}: Melhor da Geração = {current_best_fitness} | Melhor de Todos = {best_fitness_overall}")

        
        # 5. Crossover e Mutação
        while len(new_population) < POPULATION_SIZE:
            # CORREÇÃO: Usa torneio para selecionar pais da população inteira
            parent1 = tournament_selection(population_with_fitness)
            parent2 = tournament_selection(population_with_fitness)
            
            child = crossover(parent1, parent2)
            child = mutate(child)
            
            # Garante que o filho gerado é válido antes de adicionar
            is_child_valid = all(is_valid_sequence(seq + swap_sequence(seq)) for seq in child)
            if is_child_valid:
                new_population.append(child)

            population = new_population

            if (gen + 1) % 10 == 0:
                best_fitness = population_with_fitness[0][1]
                print(f"Geração {gen+1}: Melhor Fitness (Total de Viagens) = {best_fitness}")

    # --- Resultados Finais ---
    final_population_with_fitness = [(ind, calculate_fitness(ind)) for ind in population]
    final_population_with_fitness.sort(key=lambda x: x[1])
    best_solution_a_half = final_population_with_fitness[0][0]
    best_fitness = final_population_with_fitness[0][1]

    best_solution_a_full = [seq + swap_sequence(seq) for seq in best_solution_a_half]

    print("\n--- Otimização Concluída ---")
    print(f"Melhor resultado encontrado (mínimo de viagens): {best_fitness}")
    
    print("\nMelhor Tabela de Viagens (Tabela A) encontrada:")
    print(" " * 4 + "".join([f"W{j+1:<3}" for j in range(2 * (N_TEAMS - 1))]))
    for i, seq in enumerate(best_solution_a_full):
        print(f"T{i+1:<3}" + "".join([f"{gene:<3}" for gene in seq]))

if __name__ == "__main__":
    main()