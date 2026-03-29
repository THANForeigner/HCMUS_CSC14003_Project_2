# Understanding generate_random_states()

## What Does This Method Do?

It creates a **population of random puzzle states** for the Artificial Bee Colony algorithm.

## Visual Example

### Input (Original Puzzle):
```
Base grid (4x4):
1 0 3 4     (0 = empty cell to fill)
3 4 0 1
2 0 4 3
4 3 1 0
```

### Process with n_states=3:

#### Step 1: Create n_states copies
```python
population = np.tile(self.grid, (3, 1, 1))
```

Creates 3 identical copies:
```
State 0:  State 1:  State 2:
1 0 3 4   1 0 3 4   1 0 3 4
3 4 0 1   3 4 0 1   3 4 0 1
2 0 4 3   2 0 4 3   2 0 4 3
4 3 1 0   4 3 1 0   4 3 1 0
```

#### Step 2: Identify empty cells
```python
empty_cell_mask = population == 0
```

Marks all empty cells (True/False):
```
State 0:  State 1:  State 2:
F T F F   F T F F   F T F F
F F T F   F F T F   F F T F
F T F F   F T F F   F T F F
F F F T   F F F T   F F F T
```

Total empty cells: 3 states × 4 empty cells = **12 cells to fill**

#### Step 3: Fill with random values (1 to 4)
```python
num_empty_cells = np.sum(empty_cell_mask)  # = 12
random_values = np.random.randint(1, 5, 12)  # [2, 1, 3, 4, 2, 3, ...]
population[empty_cell_mask] = random_values
```

Result:
```
State 0:  State 1:  State 2:
1 2 3 4   1 4 3 4   1 3 3 4
3 4 1 1   3 4 3 1   3 4 2 1
2 3 4 3   2 1 4 3   2 2 4 3
4 3 1 2   4 3 1 4   4 3 1 1
```

### Output:
```python
Return: numpy array shape (3, 4, 4)
```

## Key Parameters Explained

| Parameter | Meaning |
|-----------|---------|
| `n_states` | How many different puzzle states to generate (default: food_size = 50) |
| `self.size` | Puzzle grid size (4 for 4×4) |
| `self.grid` | Original puzzle with fixed cells |

## Why This Design?

✅ **Vectorized**: All states filled at once (no loops) = faster  
✅ **Scalable**: Works for any puzzle size  
✅ **Fixed cells**: Original values (non-zero) are preserved  
✅ **Diversity**: Each state has different random values in empty cells  

## Performance Comparison

### Old Approach (with generate_state):
```python
# Loop through 50 times
for _ in range(50):
    state = generate_state()  # Copy + mask + fill
    grid_list.append(state)
# Result: List of arrays
```
⏱️ **Slower**: Repeated operations, Python loops

### New Approach (vectorized):
```python
# One NumPy operation on all 50 at once
population = np.tile(...)
population[mask] = values
# Result: Single 3D array
```
⏱️ **Faster**: Bulk NumPy operations, no loops
