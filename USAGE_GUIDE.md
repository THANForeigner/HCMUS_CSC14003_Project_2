# Main Function Usage Guide

## Quick Start

### Run with default input (input-01.txt):
```bash
cd d:\1_Study\Project\HCMUS_CSC14003_Project_2
python src/main.py
```

### Run with specific puzzle (e.g., input-05.txt):
```bash
python src/main.py 05
```

---

## Input File Format

**File: `inputs/input-{id}.txt`**

Example for a 4×4 puzzle:
```
4                          ← Grid size
2 0 3 4                    ← Initial grid row 1 (0 = empty)
3 4 0 1                    ← Initial grid row 2
2 0 4 3                    ← Initial grid row 3
4 3 1 0                    ← Initial grid row 4
1 0 -1 0                   ← Horizontal constraints row 1
0 0 0 0                    ← Horizontal constraints row 2
0 1 0 0                    ← Horizontal constraints row 3
-1 0 0 0                   ← Horizontal constraints row 4
0 1 0 0                    ← Vertical constraints (between rows 1-2)
0 0 -1 0                   ← Vertical constraints (between rows 2-3)
-1 0 0 0                   ← Vertical constraints (between rows 3-4)
```

### Constraint Values:
- **Horizontal**: `1` = left < right, `-1` = left > right, `0` = no constraint
- **Vertical**: `1` = top < bottom, `-1` = top > bottom, `0` = no constraint

---

## Output File Format

**File: `outputs/output-{id}.txt`**

Example output for the above puzzle (with constraints displayed):
```
2 < 3   4   1
v
1   2 > 3   4

4   1   2   3
^
3   4   1 < 2
```

### How to Read Output:
- **Numbers**: Solution values (1 to n)
- **Between cells** (horizontal): `<` (left < right) or `>` (left > right) or space (no constraint)
- **Between rows** (vertical): `^` (top < bottom) or `v` (top > bottom) or space (no constraint)

---

## Function Details

### 1. `read_input(input_file)`
Reads puzzle input from file.

**Parameters:**
- `input_file`: Path to input file

**Returns:**
- `size`: Grid size (n)
- `grid`: List of lists with initial values
- `constraint`: [h_constraints, v_constraints]

**Example:**
```python
from main import read_input
size, grid, constraint = read_input("inputs/input-01.txt")
print(f"Puzzle size: {size}x{size}")
```

---

### 2. `format_output(solution, h_constraints, v_constraints)`
Converts solution numpy array to formatted string with constraint symbols.

**Parameters:**
- `solution`: numpy array (n×n) with solution values
- `h_constraints`: Horizontal constraints (n×(n-1))
- `v_constraints`: Vertical constraints ((n-1)×n)

**Returns:**
- Formatted string representation

**Example:**
```python
import numpy as np
from main import format_output

solution = np.array([[2, 1, 3, 4], [3, 4, 2, 1], ...])
h_constraints = [[1, 0, -1], [0, 0, 0], ...]
v_constraints = [[0, 1, 0, 0], [0, 0, -1, 0], ...]

formatted = format_output(solution, h_constraints, v_constraints)
print(formatted)
```

---

### 3. `write_output(output_file, solution, h_constraints, v_constraints)`
Writes formatted solution to output file.

**Parameters:**
- `output_file`: Path to output file
- `solution`: numpy array with solution
- `h_constraints`: Horizontal constraints
- `v_constraints`: Vertical constraints

**Returns:**
- None (writes to file)

**Example:**
```python
from main import write_output
write_output("outputs/output-01.txt", solution, h_constraints, v_constraints)
```

---

### 4. `main()`
Main function that orchestrates the entire solving process.

**What it does:**
1. Parses command-line arguments (puzzle ID)
2. Reads input from `inputs/input-{id}.txt`
3. Creates ABC solver instance
4. Runs ABC algorithm
5. Formats solution
6. Writes to `outputs/output-{id}.txt`

**Command-line Usage:**
```bash
python src/main.py [puzzle_id]
```

**Arguments:**
- `puzzle_id`: (optional) Puzzle ID number (default: "01")

**Output:**
- Console: Progress messages and results
- File: Formatted solution in `outputs/output-{id}.txt`

---

## Complete Example Workflow

### Step 1: Prepare Input
Create `inputs/input-01.txt`:
```
4
2 0 3 4
3 4 0 1
2 0 4 3
4 3 1 0
1 0 -1 0
0 0 0 0
0 1 0 0
-1 0 0 0
0 1 0 0
0 0 -1 0
-1 0 0 0
```

### Step 2: Run Solver
```bash
cd d:\1_Study\Project\HCMUS_CSC14003_Project_2
python src/main.py 01
```

### Step 3: Console Output
```
Reading puzzle from d:\...\inputs\input-01.txt
Puzzle size: 4x4
Initial grid:
[[2 0 3 4]
 [3 4 0 1]
 [2 0 4 3]
 [4 3 1 0]]

Solving with Artificial Bee Colony algorithm...

Best fitness achieved: 0.9167
Solution:
[[2 1 3 4]
 [3 4 2 1]
 [2 3 4 1]
 [4 2 1 3]]

Writing solution to d:\...\outputs\output-01.txt
Done!
```

### Step 4: Check Output
File: `outputs/output-01.txt`
```
2 < 3   4   1
v
1   2 > 3   4

4   1   2   3
^
3   4   1 < 2
```

---

## Error Handling

### Common Errors:

**File not found:**
```
FileNotFoundError: inputs/input-99.txt
```
→ Create the input file first

**Invalid format:**
```
ValueError: invalid literal for int()
```
→ Check input file format (numbers separated by spaces)

**ABC solver not found:**
```
ModuleNotFoundError: No module named 'algorithm'
```
→ Run from correct directory or adjust Python path

---

## Tips

✅ **Always keep input format consistent** (grid size, grid, h-constraints, v-constraints)  
✅ **Use matching puzzle IDs** (input-01.txt → output-01.txt)  
✅ **Check that empty cells are marked with 0**  
✅ **Verify constraint arrays have correct dimensions** (h: n×(n-1), v: (n-1)×n)
