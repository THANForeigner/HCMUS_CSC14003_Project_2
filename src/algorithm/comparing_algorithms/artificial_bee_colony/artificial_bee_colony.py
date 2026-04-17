import numpy as np
import random
from copy import deepcopy
from ...futoshiki_solver import FutoshikiSolver

class ABC(FutoshikiSolver):
    def __init__(self, size, grid, constraint, swarm_size=-1, limit=-1, max_iteration=-1):
        super().__init__(size, grid, constraint)
        self.grid = np.array(grid, dtype=np.int32)
        self.constraint = [np.array(constraint[0], dtype=np.int32), 
                          np.array(constraint[1], dtype=np.int32)]
        
        self.swarm_size = 100 if swarm_size == -1 else swarm_size
        self.food_size = int(self.swarm_size / 2)
        self.trial_limit = 10 if limit == -1 else limit
        self.max_iteration = 1000 if max_iteration == -1 else max_iteration
        
        self.food_sources = self.generate_random_states()
        self.fitness = np.array(self.calculate_fitness(self.food_sources, self.constraint), dtype=np.float32)
        self.trials = np.zeros(self.food_size, dtype=np.int32)
        self.best_solution = None
        self.best_fitness = 0.0
        
    def generate_state(self, size, grid):
        """Generate a random state by filling empty cells with random values"""
        new_state = grid.copy()
        empty_mask = new_state == 0
        new_state[empty_mask] = np.random.randint(1, size + 1, np.sum(empty_mask))
        return new_state
        
    def generate_random_states(self, n_states=None):
        """Generate n random states"""
        if n_states is None:
            n_states = self.food_size
        
        grid_array = np.array([self.generate_state(self.size, self.grid) 
                              for _ in range(n_states)], dtype=np.int32)
        return grid_array
    
    def find_all_errors(self, grid, constraint):
        h_constraints = constraint[0]
        v_constraints = constraint[1]
        errors = 0
        n = grid.shape[0]
        
        # Check for duplicate numbers in rows
        for row in range(n):
            row_values = grid[row]
            non_zero_values = row_values[row_values != 0]
            unique_count = len(np.unique(non_zero_values))
            total_count = len(non_zero_values)
            if unique_count < total_count:
                errors += total_count - unique_count
        
        # Check for duplicate numbers in columns
        for col in range(n):
            col_values = grid[:, col]
            non_zero_values = col_values[col_values != 0]
            unique_count = len(np.unique(non_zero_values))
            total_count = len(non_zero_values)
            if unique_count < total_count:
                errors += total_count - unique_count
        
        # Check horizontal constraints
        for row in range(n):
            for col in range(n - 1):
                if h_constraints[row, col] != 0:
                    left_val = grid[row, col]
                    right_val = grid[row, col + 1]
                    constraint_val = h_constraints[row, col]
                    
                    if left_val != 0 and right_val != 0:
                        if constraint_val == 1 and left_val >= right_val:
                            errors += 1
                        elif constraint_val == -1 and left_val <= right_val:
                            errors += 1
        
        # Check vertical constraints
        for row in range(n - 1):
            for col in range(n):
                if v_constraints[row, col] != 0:
                    top_val = grid[row, col]
                    bottom_val = grid[row + 1, col]
                    constraint_val = v_constraints[row, col]
                    
                    if top_val != 0 and bottom_val != 0:
                        if constraint_val == 1 and top_val >= bottom_val:
                            errors += 1
                        elif constraint_val == -1 and top_val <= bottom_val:
                            errors += 1
        
        return errors
        
    def calculate_fitness(self, pop, constraint):
        h_constraints = constraint[0]
        v_constraints = constraint[1]
        
        # Count total constraints
        total_h_constraints = np.count_nonzero(h_constraints)
        total_v_constraints = np.count_nonzero(v_constraints)
        total_constraints = total_h_constraints + total_v_constraints
        
        if total_constraints == 0:
            return np.ones(len(pop), dtype=np.float32)
        
        fitness_scores = np.zeros(len(pop), dtype=np.float32)
        
        for i, grid in enumerate(pop):
            errors = self.find_all_errors(grid, constraint)
            satisfied_constraints = total_constraints - errors
            fitness_scores[i] = satisfied_constraints / total_constraints
        
        return fitness_scores
        
    def solve(self):
        for iteration in range(self.max_iteration):
            self.nodes_expanded += 1
            # Phase 1: Employed Bees
            # Each employed bee explores neighborhood of its food source
            partners_idx = np.array([random.choice([idx for idx in range(self.food_size) if idx != i]) 
                                   for i in range(self.food_size)])
            partners = self.food_sources[partners_idx]
            
            # Randomly select cells to modify
            j = np.random.randint(0, self.size * self.size, self.food_size)
            phi = np.random.uniform(-1, 1, self.food_size)
            
            new_sources = self.food_sources.copy()
            
            for i in range(self.food_size):
                row, col = divmod(j[i], self.size)
                
                # Skip if cell is fixed (original grid value)
                if self.grid[row, col] != 0:
                    continue
                
                curr_val = self.food_sources[i, row, col]
                part_val = partners[i, row, col]
                
                # Generate new value using velocity and sigmoid probability
                velocity = curr_val + phi[i] * (curr_val - part_val)
                prob = 1.0 / (1.0 + np.exp(-velocity / self.size))
                
                if np.random.random() < prob:
                    new_val = np.random.randint(1, self.size + 1)
                    new_sources[i, row, col] = new_val
            
            new_fitness = self.calculate_fitness(new_sources, self.constraint)
            self.nodes_generated += len(new_sources)
            
            # Greedy selection: update if better fitness
            improved = new_fitness > self.fitness
            self.food_sources[improved] = new_sources[improved]
            self.fitness[improved] = new_fitness[improved]
            self.trials[improved] = 0
            self.trials[~improved] += 1
            
            # Phase 2: Onlooker Bees
            # Select food sources based on fitness probability
            sum_fit = np.sum(self.fitness)
            if sum_fit > 0:
                prob_onlooker = self.fitness / sum_fit
            else:
                prob_onlooker = np.ones(self.food_size) / self.food_size
            
            selected_indices = np.random.choice(self.food_size, size=self.food_size, p=prob_onlooker)
            
            onlooker_partners_idx = np.array([random.choice([idx for idx in range(self.food_size) 
                                                            if idx != s_idx]) 
                                            for s_idx in selected_indices])
            
            j_on = np.random.randint(0, self.size * self.size, self.food_size)
            phi_on = np.random.uniform(-1, 1, self.food_size)
            
            new_onlooker_sources = self.food_sources[selected_indices].copy()
            
            for i, s_idx in enumerate(selected_indices):
                row, col = divmod(j_on[i], self.size)
                
                if self.grid[row, col] != 0:
                    continue
                
                curr_val = self.food_sources[s_idx, row, col]
                part_val = self.food_sources[onlooker_partners_idx[i], row, col]
                
                velocity = curr_val + phi_on[i] * (curr_val - part_val)
                prob = 1.0 / (1.0 + np.exp(-velocity / self.size))
                
                if np.random.random() < prob:
                    new_val = np.random.randint(1, self.size + 1)
                    new_onlooker_sources[i, row, col] = new_val
            
            new_on_fitness = self.calculate_fitness(new_onlooker_sources, self.constraint)
            self.nodes_generated += len(new_onlooker_sources)
            
            # Update food sources and trials
            for i, s_idx in enumerate(selected_indices):
                if new_on_fitness[i] > self.fitness[s_idx]:
                    self.food_sources[s_idx] = new_onlooker_sources[i]
                    self.fitness[s_idx] = new_on_fitness[i]
                    self.trials[s_idx] = 0
                else:
                    self.trials[s_idx] += 1
            
            # Phase 3: Scout Bees
            # Replace abandoned food sources with new random solutions
            abandoned = self.trials > self.trial_limit
            num_abandoned = np.sum(abandoned)
            
            if num_abandoned > 0:
                for idx in np.where(abandoned)[0]:
                    self.food_sources[idx] = self.generate_state(self.size, self.grid)
                
                abandoned_fitness = self.calculate_fitness(self.food_sources[abandoned], self.constraint)
                self.nodes_generated += len(abandoned_fitness)
                self.fitness[abandoned] = abandoned_fitness
                self.trials[abandoned] = 0
            
            # Update best solution
            best_idx = np.argmax(self.fitness)
            if self.fitness[best_idx] > self.best_fitness:
                self.best_fitness = self.fitness[best_idx]
                self.best_solution = self.food_sources[best_idx].copy()
        
        return self.best_solution
