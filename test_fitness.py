"""Test script to verify calculate_fitness and find_all_errors functions"""

# Example grid
grid = [
    [1, 2, 3, 4],
    [3, 4, 2, 1],
    [2, 1, 4, 3],
    [4, 3, 1, 2]
]

# Horizontal constraints (4x3)
h_constraints = [
    [1, 0, -1],
    [0, 0, 0],
    [0, 1, 0],
    [-1, 0, 0]
]

# Vertical constraints (3x4)
v_constraints = [
    [0, 1, 0, 0],
    [0, 0, -1, 0],
    [-1, 0, 0, 0]
]

constraint = [h_constraints, v_constraints]


class ABC:
    """Mock ABC class with fitness functions"""
    
    def find_all_errors(self, grid, constraint):
        """
        Find all constraint violations in the grid.
        """
        h_constraints = constraint[0]
        v_constraints = constraint[1]
        errors = []
        n = len(grid)
        
        # Check horizontal constraints
        for row in range(n):
            for col in range(n - 1):
                if h_constraints[row][col] != 0:
                    left_val = grid[row][col]
                    right_val = grid[row][col + 1]
                    constraint_val = h_constraints[row][col]
                    
                    # Only check if both cells are filled
                    if left_val != 0 and right_val != 0:
                        if constraint_val == 1 and left_val >= right_val:
                            errors.append({
                                'type': 'horizontal',
                                'row': row,
                                'col': col,
                                'expected': '<',
                                'actual': '>=',
                                'left_val': left_val,
                                'right_val': right_val
                            })
                        elif constraint_val == -1 and left_val <= right_val:
                            errors.append({
                                'type': 'horizontal',
                                'row': row,
                                'col': col,
                                'expected': '>',
                                'actual': '<=',
                                'left_val': left_val,
                                'right_val': right_val
                            })
        
        # Check vertical constraints
        for row in range(n - 1):
            for col in range(n):
                if v_constraints[row][col] != 0:
                    top_val = grid[row][col]
                    bottom_val = grid[row + 1][col]
                    constraint_val = v_constraints[row][col]
                    
                    # Only check if both cells are filled
                    if top_val != 0 and bottom_val != 0:
                        if constraint_val == 1 and top_val >= bottom_val:
                            errors.append({
                                'type': 'vertical',
                                'row': row,
                                'col': col,
                                'expected': '<',
                                'actual': '>=',
                                'top_val': top_val,
                                'bottom_val': bottom_val
                            })
                        elif constraint_val == -1 and top_val <= bottom_val:
                            errors.append({
                                'type': 'vertical',
                                'row': row,
                                'col': col,
                                'expected': '>',
                                'actual': '<=',
                                'top_val': top_val,
                                'bottom_val': bottom_val
                            })
        
        return errors
        
    def calculate_fitness(self, pop, constraint):
        """
        Calculate fitness score for each grid in population.
        """
        h_constraints = constraint[0]
        v_constraints = constraint[1]
        
        # Count total constraints
        total_h_constraints = sum(1 for row in h_constraints for c in row if c != 0)
        total_v_constraints = sum(1 for row in v_constraints for c in row if c != 0)
        total_constraints = total_h_constraints + total_v_constraints
        
        if total_constraints == 0:
            return [1.0] * len(pop)
        
        fitness_scores = []
        for grid in pop:
            errors = self.find_all_errors(grid, constraint)
            satisfied_constraints = total_constraints - len(errors)
            fitness = satisfied_constraints / total_constraints
            fitness_scores.append(fitness)
        
        return fitness_scores


if __name__ == "__main__":
    abc = ABC()
    
    print("=" * 60)
    print("Testing with example grid:")
    print("=" * 60)
    print("\nGrid:")
    for row in grid:
        print(row)
    
    print("\n\nHorizontal constraints (4x3):")
    for row in h_constraints:
        print(row)
    
    print("\n\nVertical constraints (3x4):")
    for row in v_constraints:
        print(row)
    
    # Test find_all_errors
    errors = abc.find_all_errors(grid, constraint)
    print(f"\n\nTotal constraints: {sum(1 for row in h_constraints for c in row if c != 0) + sum(1 for row in v_constraints for c in row if c != 0)}")
    print(f"Errors found: {len(errors)}")
    
    if errors:
        print("\nConstraint violations:")
        for i, error in enumerate(errors, 1):
            print(f"  {i}. {error}")
    else:
        print("No constraint violations found!")
    
    # Test calculate_fitness
    fitness_scores = abc.calculate_fitness([grid], constraint)
    print(f"\n\nFitness score: {fitness_scores[0]:.4f}")
    print(f"Fitness percentage: {fitness_scores[0] * 100:.2f}%")
    
    print("\n" + "=" * 60)
    print("Test complete!")
    print("=" * 60)
