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
        
    # -------------------------------------------------------------------------
    # Initialization helpers
    # -------------------------------------------------------------------------
    def generate_state(self, size, grid):
        """
        Tạo một trạng thái ngẫu nhiên nhưng đảm bảo mỗi hàng là một hoán vị 
        của các số từ 1 đến size (không trùng lặp hàng).
        """
        new_state = grid.copy()
        all_numbers = np.arange(1, size + 1)

        for r in range(size):
            empty_cols = np.where(new_state[r] == 0)[0]
            if len(empty_cols) > 0:
                # Tìm các số chưa xuất hiện trong hàng r (đã có trong fixed_mask)
                existing_numbers = new_state[r][new_state[r] > 0]
                missing_numbers = np.setdiff1d(all_numbers, existing_numbers)
                
                # Xáo trộn các số còn thiếu và điền vào
                np.random.shuffle(missing_numbers)
                new_state[r, empty_cols] = missing_numbers

        return new_state
        
    def generate_random_states(self, n_states=None):
        """Tạo quần thể ban đầu gồm n trạng thái đã được tối ưu hàng."""
        if n_states is None:
            n_states = self.pop_size
        
        # Tạo danh sách các state và chuyển thành mảng numpy một lần duy nhất
        pop_list = [self.generate_state(self.size, self.grid) for _ in range(n_states)]
        return np.array(pop_list, dtype=np.int32)
    
    # -------------------------------------------------------------------------
    # Fitness evaluation
    # -------------------------------------------------------------------------
    def find_all_errors(self, grid, constraint):
        """Đếm tổng số lỗi vi phạm. Giả định hàng đã luôn đúng."""
        h_constraints, v_constraints = constraint
        errors = 0
        n = self.size
        
        # Kiểm tra trùng lập cột
        for col in range(n):
            column = grid[:, col]
            errors += len(column) - len(np.unique(column))
        
        # Kiểm tra ràng buộc ngang
        left_cells = grid[:, :-1]
        right_cells = grid[:, 1:]

        h_errors = np.sum((h_constraints == 1) & (left_cells >= right_cells)) + \
                   np.sum((h_constraints == -1) & (left_cells <= right_cells))
        errors += h_errors
        
        # Kiểm tra ràng buộc dọc
        top_cells = grid[:-1, :]
        bottom_cells = grid[1:, :]
    
        v_errors = np.sum((v_constraints == 1) & (top_cells >= bottom_cells)) + \
                   np.sum((v_constraints == -1) & (top_cells <= bottom_cells))
        errors += v_errors
        
        return errors
        
    def calculate_fitness(self, pop, constraint):
        """
        Tính toán độ thích nghi. 
        Fitness = 1 / (1 + errors). 
        Điểm 1.0 là hoàn hảo, càng gần 0 càng tệ.
        """
        fitness_scores = np.zeros(len(pop), dtype=np.float32)
        
        for i, grid in enumerate(pop):
            errors = self.find_all_errors(grid, constraint)
            
            # Sử dụng công thức 1 / (1 + errors) để tránh chia cho 0 
            # và tạo ra đường cong tiến hóa mượt mà hơn.
            fitness_scores[i] = 1.0 / (1.0 + errors)
            
        return fitness_scores
    
    # -------------------------------------------------------------------------
    # Selection
    # -------------------------------------------------------------------------
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
    
    # -------------------------------------------------------------------------
    # Crossover operators
    # -------------------------------------------------------------------------
    def crossover(self, parent1, parent2):
        """
        Row-wise crossover: Trao đổi các hàng nguyên vẹn giữa bố và mẹ.
        Đây là phép lai tốt nhất để giữ cho các hàng luôn là hoán vị đúng.
        """
        mask = np.random.randint(0, 2, size=self.size).astype(bool)

        child1 = np.where(mask[:, np.newaxis], parent1, parent2)
        child2 = np.where(mask[:, np.newaxis], parent2, parent1)
        
        return child1, child2
    
    # -------------------------------------------------------------------------
    # Mutation operators
    # -------------------------------------------------------------------------
    def swap_mutation(self, individual):
        """Hoán đổi 2 ô ngẫu nhiên trong một hàng ngẫu nhiên."""
        mutant = individual.copy()
        row = np.random.randint(0, self.size)
        non_fixed_cols = np.where(~self.fixed_mask[row])[0]
        
        if len(non_fixed_cols) >= 2:
            col1, col2 = np.random.choice(non_fixed_cols, size=2, replace=False)
            mutant[row, col1], mutant[row, col2] = mutant[row, col2], mutant[row, col1]
        
        return mutant
    
    def scramble_mutation(self, individual):
        """Xáo trộn tất cả các ô không cố định trong một hàng ngẫu nhiên."""
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
        # Đột biến "mạnh": thực hiện từ 1 đến 3 lần thay đổi
        for _ in range(np.random.randint(1, 4)):
            strategy = np.random.randint(0, 2)
            if strategy == 0:
                mutant = self.swap_mutation(mutant)
            else:
                mutant = self.scramble_mutation(mutant)
        return mutant
    
    def mutate_heavy(self, individual):
        """Đột biến cực mạnh: Xáo trộn 3-5 hàng cùng lúc."""
        mutant = individual.copy()
        # Chọn ngẫu nhiên số lượng hàng bị tác động (khoảng 1/2 bảng)
        num_rows = np.random.randint(3, 6)
        rows = np.random.choice(self.size, size=num_rows, replace=False)
        
        for r in rows:
            non_fixed = np.where(~self.fixed_mask[r])[0]
            if len(non_fixed) >= 2:
                # Xáo trộn (Scramble) toàn bộ ô trống trong hàng đó
                vals = mutant[r, non_fixed]
                np.random.shuffle(vals)
                mutant[r, non_fixed] = vals
        return mutant
    
    # -------------------------------------------------------------------------
    # Main GA loop
    # -------------------------------------------------------------------------
    def solve(self):
        """
        Chạy Giải thuật Di truyền để giải Futoshiki.
        Bổ sung cơ chế Adaptive Mutation để tránh kẹt ở tối ưu cục bộ.
        """
        # Lưu lại mutation ban đầu để reset khi cần
        orig_mut_rate = self.mutation_rate
        stagnant_generations = 0

        # Track the global best
        best_idx = np.argmax(self.fitness)
        self.best_fitness = self.fitness[best_idx]
        self.best_solution = self.population[best_idx].copy()

        stagnant_generations = 0
        original_mutation_rate = self.mutation_rate

        
        
        for iteration in range(self.max_iteration):
            if self.best_fitness >= 1.0:
                break

            # --- Tự động điều chỉnh Mutation Rate (Adaptive) ---
            # Nếu 50 thế hệ không tìm thấy cá thể tốt hơn, tăng đột biến để phá vỡ bẫy

            if stagnant_generations > 50:
                # Cấp 1: Tăng dần nhiệt độ (Mutation rate)
                self.mutation_rate = min(0.5, self.mutation_rate + 0.05)
                
            if stagnant_generations > 150:
                # Cấp 2: Đổi sang vũ khí hạng nặng (Heavy Mutation)
                current_mutate_fn = self.mutate_heavy

            # if stagnant_generations > 500:
            #     # Cấp 3: THAY MÁU (Reset 90% quần thể)
            #     print(f"\n[Gen {iteration}] Kẹt quá lâu ở {self.best_fitness:.4f}. Đang thay máu...")
            #     num_new = int(self.pop_size * 0.95)
            #     new_blood = self.generate_random_states(num_new)
            #     # Giữ lại 5% elite cũ, thay 95% bằng máu mới
            #     elite_indices = np.argsort(self.fitness)[-int(self.pop_size*0.1):]
            #     new_pop_list = [self.population[i].copy() for i in elite_indices]
            #     self.population = np.vstack([np.array(new_pop_list), new_blood])
                
            #     # Reset các thông số về ban đầu sau khi thay máu
            #     self.mutation_rate = orig_mut_rate
            #     stagnant_generations = 0
            #     self.fitness = self.calculate_fitness(self.population, self.constraint)
            #     continue # Nhảy sang thế hệ mới
            
            new_population = []
            
            # ----- Step 1: Elitism -----
            elite_indices = np.argsort(self.fitness)[-self.elite_size:]
            for idx in elite_indices:
                new_population.append(self.population[idx].copy())
            
            # ----- Steps 2-4: Selection, Crossover, Mutation -----
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
            
            # ----- Step 5: Replacement -----
            self.population = np.array(new_population[:self.pop_size], dtype=np.int32)
            self.fitness = self.calculate_fitness(self.population, self.constraint)
            
            # ----- Step 6: Update best -----
            gen_best_idx = np.argmax(self.fitness)
            if self.fitness[gen_best_idx] > self.best_fitness:
                self.best_fitness = self.fitness[gen_best_idx]
                self.best_solution = self.population[gen_best_idx].copy()
                stagnant_generations = 0 # Reset khi có tiến triển
                self.mutation_rate = orig_mut_rate # Trở về mức cũ để khai thác
            else:
                stagnant_generations += 1

            if iteration % 100 == 0:
                print(f"Gen {iteration}: Best Fitness = {self.best_fitness:.4f}")
        
        return self.best_solution
