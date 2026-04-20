import numpy as np
import random
from ...futoshiki_solver import futoshiki_solver

class GA(futoshiki_solver):
    def __init__(self, size, grid, constraint, pop_size=-1, mutation_rate=-1, 
                 crossover_rate=-1, elite_size=-1, tournament_size=-1, max_iteration=-1):
        super().__init__(size, grid, constraint)
        self.size = size
        self.grid = np.array(grid, dtype=np.int32)
        self.constraint = [np.array(constraint[0], dtype=np.int32), 
                          np.array(constraint[1], dtype=np.int32)]
        
        # GA hyperparameters
        self.pop_size = 200 if pop_size == -1 else pop_size
        self.mutation_rate = 0.15 if mutation_rate == -1 else mutation_rate
        self.crossover_rate = 0.85 if crossover_rate == -1 else crossover_rate
        self.elite_size = max(2, self.pop_size // 10) if elite_size == -1 else elite_size
        self.tournament_size = 5 if tournament_size == -1 else tournament_size
        self.max_iteration = 1000 if max_iteration == -1 else max_iteration
        
        # Precompute fixed cell mask (cells that are given in the puzzle)
        self.fixed_mask = self.grid != 0
        
        # Initialize population
        self.population = self.generate_random_states()
        self.fitness = np.array(self.calculate_fitness(self.population, self.constraint), dtype=np.float32)
        self.best_solution = None
        self.best_fitness = 0.0
        
    def generate_state(self, size, grid):
        """
        Create a random state but ensure each row is a permutation 
        of numbers from 1 to size (no duplicate rows).
        """
        new_state = grid.copy()
        all_numbers = np.arange(1, size + 1)

        for r in range(size):
            empty_cols = np.where(new_state[r] == 0)[0]
            if len(empty_cols) > 0:
                # Find numbers that haven't appeared in row r (already in fixed_mask)
                existing_numbers = new_state[r][new_state[r] > 0]
                missing_numbers = np.setdiff1d(all_numbers, existing_numbers)
                
                # Shuffle missing numbers and fill in
                np.random.shuffle(missing_numbers)
                new_state[r, empty_cols] = missing_numbers

        return new_state
        
    def generate_random_states(self, n_states=None):
        """Create initial population of n states with row optimization."""
        if n_states is None:
            n_states = self.pop_size
        
        # Create a list of states and convert to a numpy array once
        pop_list = [self.generate_state(self.size, self.grid) for _ in range(n_states)]
        return np.array(pop_list, dtype=np.int32)
    
    def find_all_errors(self, grid, constraint):
        """Count total violations. Assume rows are always correct."""
        h_constraints, v_constraints = constraint
        errors = 0
        n = self.size
        
        # Check for column duplicates
        for col in range(n):
            column = grid[:, col]
            errors += len(column) - len(np.unique(column))
        
        # Check horizontal constraints
        left_cells = grid[:, :-1]
        right_cells = grid[:, 1:]

        h_errors = np.sum((h_constraints == 1) & (left_cells >= right_cells)) + \
                   np.sum((h_constraints == -1) & (left_cells <= right_cells))
        errors += h_errors
        
        # Check vertical constraints
        top_cells = grid[:-1, :]
        bottom_cells = grid[1:, :]
    
        v_errors = np.sum((v_constraints == 1) & (top_cells >= bottom_cells)) + \
                   np.sum((v_constraints == -1) & (top_cells <= bottom_cells))
        errors += v_errors
        
        return errors
        
    def calculate_fitness(self, pop, constraint):
        """
        Calculate fitness. 
        Fitness = 1 / (1 + errors). 
        Score 1.0 is perfect, closer to 0 is worse.
        """
        fitness_scores = np.zeros(len(pop), dtype=np.float32)
        
        for i, grid in enumerate(pop):
            errors = self.find_all_errors(grid, constraint)
            
            # Use formula 1 / (1 + errors) to avoid division by 0 
            # and create a smoother evolution curve.
            fitness_scores[i] = 1.0 / (1.0 + errors)
            
        return fitness_scores
    
    def tournament_selection(self, k=None):
        """
        Select one individual via tournament selection.
        Randomly pick `k` individuals and return the one with the highest fitness.
        """
        if k is None:
            k = self.tournament_size
        
        candidates = np.random.choice(self.pop_size, size=k, replace=False)
        best_candidate = candidates[np.argmax(self.fitness[candidates])]
        return best_candidate
    
    def crossover(self, parent1, parent2):
        """
        Row-wise crossover: Exchange intact rows between parents.
        This is the best crossover to keep rows as correct permutations.
        """
        mask = np.random.randint(0, 2, size=self.size).astype(bool)

        child1 = np.where(mask[:, np.newaxis], parent1, parent2)
        child2 = np.where(mask[:, np.newaxis], parent2, parent1)
        
        return child1, child2
    
    def swap_mutation(self, individual):
        """Swap 2 random cells in a random row."""
        mutant = individual.copy()
        row = np.random.randint(0, self.size)
        non_fixed_cols = np.where(~self.fixed_mask[row])[0]
        
        if len(non_fixed_cols) >= 2:
            col1, col2 = np.random.choice(non_fixed_cols, size=2, replace=False)
            mutant[row, col1], mutant[row, col2] = mutant[row, col2], mutant[row, col1]
        
        return mutant
    
    def scramble_mutation(self, individual):
        """Scramble all non-fixed cells in a random row."""
        mutant = individual.copy()
        row = np.random.randint(0, self.size)
        non_fixed_cols = np.where(~self.fixed_mask[row])[0]
        
        if len(non_fixed_cols) >= 2:
            values = mutant[row, non_fixed_cols].copy()
            np.random.shuffle(values)
            mutant[row, non_fixed_cols] = values
        
        return mutant
    
    def mutate(self, individual):
        if np.random.random() > self.mutation_rate:
            return individual
        
        mutant = individual.copy()
        # "Strong" mutation: perform 1 to 3 changes
        for _ in range(np.random.randint(1, 4)):
            strategy = np.random.randint(0, 2)
            if strategy == 0:
                mutant = self.swap_mutation(mutant)
            else:
                mutant = self.scramble_mutation(mutant)
        return mutant
    
    def mutate_heavy(self, individual):
        """Very strong mutation: Scramble 3-5 rows at once."""
        mutant = individual.copy()
        # Randomly select the number of affected rows (about 1/2 of the board)
        num_rows = np.random.randint(3, 6)
        rows = np.random.choice(self.size, size=num_rows, replace=False)
        
        for r in rows:
            non_fixed = np.where(~self.fixed_mask[r])[0]
            if len(non_fixed) >= 2:
                # Scramble all empty cells in that row
                vals = mutant[r, non_fixed]
                np.random.shuffle(vals)
                mutant[r, non_fixed] = vals
        return mutant
    
    def solve(self):
        """
        Run Genetic Algorithm to solve Futoshiki.
        Add Adaptive Mutation mechanism to avoid local optima.
        """
        # Save initial mutation rate to reset when needed
        orig_mut_rate = self.mutation_rate
        stagnant_generations = 0

        # Track the global best
        best_idx = np.argmax(self.fitness)
        self.best_fitness = self.fitness[best_idx]
        self.best_solution = self.population[best_idx].copy()

        stagnant_generations = 0
        original_mutation_rate = self.mutation_rate

        
        
        for iteration in range(self.max_iteration):
            self.nodes_expanded += 1
            if self.best_fitness >= 1.0:
                break

            # If 50 generations find no better individual, increase mutation to break the trap

            if stagnant_generations > 50:
                # Level 1: Gradually increase temperature (Mutation rate)
                self.mutation_rate = min(0.5, self.mutation_rate + 0.05)
                
            if stagnant_generations > 150:
                # Level 2: Switch to heavy weapons (Heavy Mutation)
                current_mutate_fn = self.mutate_heavy

            # if stagnant_generations > 500:
            #     # Level 3: NEW BLOOD (Reset 90% of population)
            #     print(f"\n[Gen {iteration}] Stuck too long at {self.best_fitness:.4f}. Changing blood...")
            #     num_new = int(self.pop_size * 0.95)
            #     new_blood = self.generate_random_states(num_new)
            #     # Keep 5% old elite, replace 95% with new blood
            #     elite_indices = np.argsort(self.fitness)[-int(self.pop_size*0.1):]
            #     new_pop_list = [self.population[i].copy() for i in elite_indices]
            #     self.population = np.vstack([np.array(new_pop_list), new_blood])
                
            #     # Reset parameters to initial after changing blood
            #     self.mutation_rate = orig_mut_rate
            #     stagnant_generations = 0
            #     self.fitness = self.calculate_fitness(self.population, self.constraint)
            #     continue # Skip to next generation
            
            new_population = []
            
            elite_indices = np.argsort(self.fitness)[-self.elite_size:]
            for idx in elite_indices:
                new_population.append(self.population[idx].copy())
            
            while len(new_population) < self.pop_size:
                # Selection
                parent1_idx = self.tournament_selection()
                parent2_idx = self.tournament_selection()
                
                parent1 = self.population[parent1_idx]
                parent2 = self.population[parent2_idx]
                
                # Crossover
                if np.random.random() < self.crossover_rate:
                    child1, child2 = self.crossover(parent1, parent2)
                else:
                    child1 = parent1.copy()
                    child2 = parent2.copy()
                
                # Mutation
                child1 = self.mutate(child1)
                child2 = self.mutate(child2)
                
                new_population.append(child1)
                if len(new_population) < self.pop_size:
                    new_population.append(child2)
            
            self.population = np.array(new_population[:self.pop_size], dtype=np.int32)
            self.nodes_generated += len(self.population)
            self.fitness = self.calculate_fitness(self.population, self.constraint)
            
            gen_best_idx = np.argmax(self.fitness)
            if self.fitness[gen_best_idx] > self.best_fitness:
                self.best_fitness = self.fitness[gen_best_idx]
                self.best_solution = self.population[gen_best_idx].copy()
                stagnant_generations = 0 # Reset when progress is made
                self.mutation_rate = orig_mut_rate # Return to old level for exploitation
            else:
                stagnant_generations += 1

            # if iteration % 100 == 0:
            #     print(f"Gen {iteration}: Best Fitness = {self.best_fitness:.4f}")
        
        return self.best_solution
