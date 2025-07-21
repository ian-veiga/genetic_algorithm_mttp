import random
N_TEAMS = 100  # Número de equipes (deve ser par) 
POPULATION_SIZE = 1000
MAX_GENERATIONS = 10000
MUTATION_PROBABILITY = 0.02
MAX_CONSECUTIVE_GAMES = 3 # Máximo de jogos consecutivos em casa/fora


def swap_sequence(seq):
    return [1 - gene for gene in seq]

def is_valid_sequence(seq):
    for i in range(len(seq) - MAX_CONSECUTIVE_GAMES):
        if all(seq[j] == seq[i] for j in range(i, i + MAX_CONSECUTIVE_GAMES + 1)):
            return False
    return True

def create_random_travel_sequence(n_weeks):
   
    while True:
        # Gera a primeira metade do torneio, a segunda é espelhada.
        # O torneio tem 2*(n-1) semanas, então a primeira metade tem n-1.
        seq_half = [random.randint(0, 1) for _ in range(n_weeks)]
        
        # Cria a segunda metade espelhada (não é necessário para a validação inicial)
        full_seq = seq_half + swap_sequence(seq_half)
        
        if is_valid_sequence(full_seq):
            return seq_half

def create_individual():
    """
    Cria um indivíduo (Tabela A) usando a metodologia de inicialização. 
    """
    n_first_half_weeks = N_TEAMS - 1
    
    # 1. Gera as primeiras n/2 sequências aleatoriamente.
    first_half_teams = [create_random_travel_sequence(n_first_half_weeks) for _ in range(N_TEAMS // 2)]
    
    # 2. Gera as n/2 restantes usando o método de troca. 
    second_half_teams = [swap_sequence(seq) for seq in first_half_teams]
    
    return first_half_teams + second_half_teams

def calculate_fitness(individual):
    """
    Calcula o número total de viagens para um indivíduo (Tabela A).
    O objetivo é minimizar este valor. 
    Uma viagem é contada quando há uma transição de casa (0) para fora (1).
    """
    total_travels = 0
    for team_seq in individual:
        team_travels = 0
        # Adiciona 1 se o primeiro jogo for fora. [cite: 42]
        if team_seq[0] == 1:
            team_travels += 1
        # Adiciona 1 para cada transição de casa para fora. [cite: 50]
        for i in range(len(team_seq) - 1):
            if team_seq[i] == 0 and team_seq[i+1] == 1:
                team_travels += 1
        total_travels += team_travels
    return total_travels

# --- 2. Operadores Genéticos ---

def selection(population_with_fitness):
    """
    Seleciona os dois melhores indivíduos (elitismo). 
    """
    population_with_fitness.sort(key=lambda x: x[1])
    return [population_with_fitness[0][0], population_with_fitness[1][0]]

def crossover(parent1, parent2):
    """
    Executa o crossover para criar um novo indivíduo. [cite: 126]
    """
    n_first_half_teams = N_TEAMS // 2
    child_first_half = []
    
    # Escolhe aleatoriamente as sequências dos pais para a primeira metade do filho. [cite: 128]
    for i in range(n_first_half_teams):
        child_first_half.append(random.choice([parent1[i], parent2[i]]))
        
    # As sequências restantes são geradas pelo método de troca. 
    child_second_half = [swap_sequence(seq) for seq in child_first_half]
    
    return child_first_half + child_second_half
    
def mutate(individual):
    """
    Executa a mutação em um indivíduo.
    """
    if random.random() > MUTATION_PROBABILITY:
        return individual

    mutated_ind = [list(row) for row in individual] # Cópia para mutação
    
    # Escolhe uma equipe e uma semana aleatórias
    team_idx = random.randrange(N_TEAMS)
    week_idx = random.randrange(N_TEAMS - 1)

    # Inverte o gene (0->1 ou 1->0)
    mutated_ind[team_idx][week_idx] = 1 - mutated_ind[team_idx][week_idx]
    
    # Altera a equipe trocada correspondente
    swapped_team_idx = (team_idx + N_TEAMS // 2) % N_TEAMS
    mutated_ind[swapped_team_idx][week_idx] = 1 - mutated_ind[swapped_team_idx][week_idx]
    
    # Verifica a validade da sequência completa (primeira e segunda metade)
    full_seq_mutated = mutated_ind[team_idx] + swap_sequence(mutated_ind[team_idx])
    full_seq_swapped = mutated_ind[swapped_team_idx] + swap_sequence(mutated_ind[swapped_team_idx])
    
    if is_valid_sequence(full_seq_mutated) and is_valid_sequence(full_seq_swapped):
        # CORREÇÃO: Retorna a lista de listas diretamente
        return mutated_ind
    else:
        # Se a mutação invalidar a sequência, retorna o original
        return individual



def generate_schedule_b(table_a):

    n = len(table_a)
    n_weeks = n - 1
    
    # Tabela B para a primeira metade do torneio
    table_b_half = [[0] * n_weeks for _ in range(n)]

    def solve(team_idx, week_idx):
        if team_idx == n:
            return True # Concluído

        next_week = (week_idx + 1) % n_weeks
        next_team = team_idx + 1 if next_week == 0 else team_idx

        if table_b_half[team_idx][week_idx] != 0:
            return solve(next_team, next_week)

        # Encontrar adversários possíveis
        possible_opponents = []
        for opponent in range(n):
            # Condições para um adversário válido 
            if opponent != team_idx and \
               table_b_half[opponent][week_idx] == 0 and \
               table_a[team_idx][week_idx] != table_a[opponent][week_idx]:
                
                # Verifica se já jogaram na primeira rodada
                has_played = False
                for w in range(n_weeks):
                    if table_b_half[team_idx][w] == opponent + 1:
                        has_played = True
                        break
                if not has_played:
                    possible_opponents.append(opponent)
        
        random.shuffle(possible_opponents)

        for opp in possible_opponents:
            table_b_half[team_idx][week_idx] = opp + 1
            table_b_half[opp][week_idx] = team_idx + 1
            
            if solve(next_team, next_week):
                return True
            
            # Backtrack
            table_b_half[team_idx][week_idx] = 0
            table_b_half[opp][week_idx] = 0
            
        return False

    if solve(0, 0):
        # Constrói a tabela completa (primeira e segunda metade)
        full_table_b = [[0] * (2 * n_weeks) for _ in range(n)]
        for i in range(n):
            for j in range(n_weeks):
                 full_table_b[i][j] = table_b_half[i][j]
                 # Segunda metade espelhada
                 full_table_b[i][j + n_weeks] = table_b_half[i][j]
        return full_table_b
    else:
        return None # Não foi possível encontrar um calendário válido

# --- 4. Execução Principal do Algoritmo Genético ---

def main():
    """
    Orquestra a execução do algoritmo genético.
    """
    # 1. Inicialização
    population = [create_individual() for _ in range(POPULATION_SIZE)]

    print(f"Iniciando o Algoritmo Genético para {N_TEAMS} equipes...")
    print(f"Tamanho da População: {POPULATION_SIZE}, Gerações: {MAX_GENERATIONS}\n")

    for gen in range(MAX_GENERATIONS):
        # 2. Avaliação de Aptidão
        population_with_fitness = [(ind, calculate_fitness(ind)) for ind in population]
        
        # 3. Seleção (Elitismo)
        elites = selection(population_with_fitness)
        
        # 4. Geração da nova população
        new_population = elites.copy()
        
        # 5. Crossover e Mutação
        # Gera os 2 indivíduos restantes
        while len(new_population) < POPULATION_SIZE:
            parent1, parent2 = random.sample(elites, 2)
            child = crossover(parent1, parent2)
            child = mutate(child)
            
            # Garante que o filho é válido antes de adicionar
            is_child_valid = all(is_valid_sequence(seq + swap_sequence(seq)) for seq in child)
            if is_child_valid:
                new_population.append(child)

        population = new_population

        if (gen + 1) % 10 == 0:
            best_fitness = min(p[1] for p in population_with_fitness)
            print(f"Geração {gen+1}: Melhor Fitness (Total de Viagens) = {best_fitness}")

    # --- Resultados Finais ---
    final_population_with_fitness = [(ind, calculate_fitness(ind)) for ind in population]
    final_population_with_fitness.sort(key=lambda x: x[1])
    best_solution_a_half = final_population_with_fitness[0][0]
    best_fitness = final_population_with_fitness[0][1]

    # Constrói a Tabela A completa
    best_solution_a_full = [seq + swap_sequence(seq) for seq in best_solution_a_half]

    print("\n--- Otimização Concluída ---")
    print(f"Melhor resultado encontrado (mínimo de viagens): {best_fitness}")
    
    print("\nMelhor Tabela de Viagens (Tabela A) encontrada:")
    print(" " * 4 + "".join([f"W{j+1:<3}" for j in range(2 * (N_TEAMS - 1))]))
    for i, seq in enumerate(best_solution_a_full):
        print(f"T{i+1:<3}" + "".join([f"{gene:<3}" for gene in seq]))

    print("\n--- Gerando Calendário de Jogos (Tabela B) ---")
    final_schedule_b = generate_schedule_b(best_solution_a_half)

    if final_schedule_b:
        print("\nCalendário de Jogos Final (Tabela B):")
        print(" " * 6 + "".join([f"W{j+1:<4}" for j in range(2 * (N_TEAMS - 1))]))
        for i, row in enumerate(final_schedule_b):
            print(f"Equipe {i+1:<2}" + "".join([f"{opp:<4}" for opp in row]))
    else:
        print("\nNão foi possível gerar um calendário válido para a Tabela A encontrada.")


if __name__ == "__main__":
    main()