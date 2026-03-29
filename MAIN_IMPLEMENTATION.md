# Main Function Implementation Summary

## Files Created/Modified

### Core Implementation
- **`src/main.py`** - Main module with I/O functions

### Documentation
- **`IO_FORMAT.md`** - Input/Output file format specification
- **`USAGE_GUIDE.md`** - Complete usage guide with examples
- **`GENERATE_STATES_EXPLANATION.md`** - Explanation of state generation
- **`test_io.py`** - I/O testing script

### Input/Output
- **`inputs/input-01.txt`** - Sample input file (created)
- **`outputs/`** - Directory for output files (auto-created)

---

## Functions Implemented

### 1. **`read_input(input_file)`**
**Purpose**: Parse Futoshiki puzzle from input file

**Input Format**:
```
Line 1:       Grid size (n)
Lines 2-n+1:  Initial grid (n×n) with 0 = empty cells
Lines n+2-2n: Horizontal constraints (n×(n-1))
              1 = left<right, -1 = left>right, 0 = no constraint
Lines 2n+1-3n-1: Vertical constraints ((n-1)×n)
                 1 = top<bottom, -1 = top>bottom, 0 = no constraint
```

**Returns**: `(size, grid, constraint)`
- `size`: Integer grid dimension
- `grid`: List of lists with initial puzzle values
- `constraint`: [h_constraints, v_constraints] lists

---

### 2. **`format_output(solution, h_constraints, v_constraints)`**
**Purpose**: Convert solution to human-readable format with constraint symbols

**How it works**:
- Places solution values in the grid
- Inserts `<`, `>`, or spaces between horizontal cells
- Inserts `^`, `v`, or spaces between vertical rows

**Output Example**:
```
2 < 3   4   1
v
1   2 > 3   4

4   1   2   3
^
3   4   1 < 2
```

**Symbols**:
- `<`: left < right (horizontal) or top < bottom (vertical)
- `>`: left > right (horizontal only)
- `v`: top > bottom (vertical only)
- `^`: top < bottom (vertical only)
- Space: No constraint

**Returns**: Formatted string

---

### 3. **`write_output(output_file, solution, h_constraints, v_constraints)`**
**Purpose**: Save formatted solution to file

**Process**:
1. Call `format_output()` to create formatted string
2. Open output file for writing
3. Write formatted string to file

**Parameters**:
- `output_file`: Path to output file (Path or str)
- `solution`: numpy array (n×n)
- `h_constraints`: Horizontal constraints
- `v_constraints`: Vertical constraints

**Returns**: None

---

### 4. **`main()`**
**Purpose**: Main orchestrator function

**Process**:
1. Parse command-line arguments (puzzle ID, default "01")
2. Construct input/output file paths
3. Create output directory if needed
4. Read puzzle from input file
5. Instantiate ABC solver with parameters
6. Run `solver.solve()` to get solution
7. Format and write solution to output file

**Command-line Usage**:
```bash
python src/main.py [puzzle_id]
```

**Example**:
```bash
# Solve input-01.txt → output-01.txt
python src/main.py 01

# Solve input-05.txt → output-05.txt
python src/main.py 05

# Default: input-01.txt → output-01.txt
python src/main.py
```

**Output**:
- Prints progress to console
- Creates/updates `outputs/output-{id}.txt`

---

## How It All Works Together

```
inputs/input-01.txt
        ↓
   [read_input]
        ↓
   (size, grid, constraint)
        ↓
   [ABC solver instance]
        ↓
   solver.solve()
        ↓
   solution (numpy array)
        ↓
   [format_output]
        ↓
   Formatted string with constraint symbols
        ↓
   [write_output]
        ↓
outputs/output-01.txt
```

---

## Example Session

### Command:
```bash
python src/main.py 01
```

### Console Output:
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

### File Created: `outputs/output-01.txt`
```
2 < 3   4   1
v
1   2 > 3   4

4   1   2   3
^
3   4   1 < 2
```

---

## Key Features

✅ **Modular Design**: Separate functions for reading, formatting, writing  
✅ **Flexible IDs**: Works with any puzzle ID (01, 02, 03, etc.)  
✅ **Error Handling**: Creates output directory automatically  
✅ **Clear Output**: Constraint symbols make solution easy to verify  
✅ **Well Documented**: Docstrings and comments explain each step  
✅ **Integration Ready**: Works seamlessly with ABC solver  

---

## Testing

Run the test script:
```bash
python test_io.py
```

This will:
- Test `format_output()` function
- Create sample output file
- Verify input reading
- Create sample input file if missing

---

## File Structure
```
project/
├── inputs/
│   └── input-01.txt          (input files)
│   └── input-02.txt
│   └── ...
├── outputs/                  (auto-created)
│   └── output-01.txt         (generated solution files)
│   └── output-02.txt
│   └── ...
├── src/
│   ├── main.py               (main module)
│   ├── algorithm/
│   │   └── comparing_algorithms/
│   │       └── artificial_bee_colony.py
│   └── ...
└── Documentation/
    ├── IO_FORMAT.md
    ├── USAGE_GUIDE.md
    └── ...
```
