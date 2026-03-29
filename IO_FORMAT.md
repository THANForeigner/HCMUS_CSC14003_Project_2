# Futoshiki Puzzle I/O Format

## Input File Format (`input-id.txt`)

### Structure:
```
Line 1:        Grid size (n)
Lines 2-n+1:   Initial grid (n x n) with 0 = empty cell
Lines n+2-2n+1: Horizontal constraints (n x n-1)
               1 = left < right, -1 = left > right, 0 = no constraint
Lines 2n+2-3n: Vertical constraints (n-1 x n)
               1 = top < bottom, -1 = top > bottom, 0 = no constraint
```

### Example Input (4x4 puzzle):
```
4                          <- Grid size = 4
2 0 3 4                    <- Row 1: has 2 fixed, 3 fixed, others empty
3 4 0 1                    <- Row 2: has 3, 4, 1 fixed
2 0 4 3                    <- Row 3: has 2, 4, 3 fixed
4 3 1 0                    <- Row 4: has 4, 3, 1 fixed
1 0 -1 0                   <- Horizontal constraints for row 1
0 0 0 0                    <- Horizontal constraints for row 2
0 1 0 0                    <- Horizontal constraints for row 3
-1 0 0 0                   <- Horizontal constraints for row 4
0 1 0 0                    <- Vertical constraints between rows 1-2
0 0 -1 0                   <- Vertical constraints between rows 2-3
-1 0 0 0                   <- Vertical constraints between rows 3-4
```

### Constraint Meaning:
| Value | Meaning (Horizontal) | Meaning (Vertical) |
|-------|----------------------|--------------------|
| `1`   | Left < Right         | Top < Bottom       |
| `-1`  | Left > Right         | Top > Bottom       |
| `0`   | No constraint        | No constraint      |

---

## Output File Format (`output-id.txt`)

### Structure:
- Solution grid with constraint symbols displayed between cells
- Cells separated by `<`, `>`, or spaces (3 chars wide)
- Between rows, vertical constraints shown as `^`, `v`, or spaces

### Example Output:
```
2 < 3   4   1     <- Row 1: 2 (< 3) space (4) space (1)
v                 <- Vertical constraint: top < bottom
1   2 > 3   4     <- Row 2: 1 space (2 > 3) space (4)
  
4   1   2   3     <- Row 3: (4) space (1) space (2) space (3)
^                 <- Vertical constraint: top < bottom
3   4   1 < 2     <- Row 4: (3) space (4) space (1 < 2)
```

### Constraint Symbols:
| Symbol | Meaning |
|--------|---------|
| `<`    | Left < Right (horizontal) or Top < Bottom (vertical) |
| `>`    | Left > Right (horizontal) |
| `v`    | Top > Bottom (vertical) |
| `^`    | Top < Bottom (vertical) |
| Space  | No constraint |

---

## Usage

### Run from command line:
```bash
# Solve puzzle input-01.txt
python src/main.py 01

# Default puzzle (input-01.txt)
python src/main.py
```

### Input Files Location:
```
inputs/input-01.txt
inputs/input-02.txt
inputs/input-03.txt
...
```

### Output Files Location:
```
outputs/output-01.txt
outputs/output-02.txt
outputs/output-03.txt
...
```

### Main Function Flow:
1. **Read Input** → Parse puzzle from `input-{id}.txt`
2. **Solve** → Apply ABC algorithm to find solution
3. **Format** → Convert solution with constraint symbols
4. **Write Output** → Save formatted solution to `output-{id}.txt`

---

## Function Reference

### `read_input(input_file)`
- Reads puzzle from file
- Returns: `(size, grid, constraint)`

### `format_output(solution, h_constraints, v_constraints)`
- Converts solution array to formatted string
- Returns: Formatted string with constraints

### `write_output(output_file, solution, h_constraints, v_constraints)`
- Writes formatted solution to file
- No return value

### `main()`
- Orchestrates entire solve process
- Handles command-line arguments
- Prints progress information
