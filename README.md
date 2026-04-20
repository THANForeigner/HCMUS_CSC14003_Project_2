#  [CSC14003] Demo project 2: FutoshikiSolving with FOL & Inference Algorithms - Group 9: Doryoku

A comprehensive Python application designed to solve and analyze **Futoshiki** puzzles (also known as "More or Less") using a wide variety of artificial intelligence and combinatorial algorithms. The project includes a full Graphical User Interface (GUI) to visualize the solving process and a benchmarking suite to compare algorithm performance.

---

## Features

- **Multiple Solving Algorithms**: From classic backtracking to advanced First-Order Logic (FOL) and metaheuristics.
- **Step-by-Step Visualization**: Watch algorithms solve puzzles in real-time via the GUI.
- **Performance Benchmarking**: Generate reports and plots on time complexity, memory usage, and node expansion.
- **Flexible Input**: Load puzzles from text files with customizable sizes and constraints.

## Supported Algorithms

The application implements the following techniques:

1. **Logic-Based (FOL)**:
   - Forward Chaining (with Backtracking)
   - Backward Chaining (SLD Resolution / Tabling)
   - Backward Chaining with AC-3 (Arc Consistency)
2. **Search & Constraint Satisfaction**:
   - A* Search (with MRV Heuristic)
   - A* Search with AC-3
   - Classic Backtracking & Brute Force
   - Dancing Links (DLX) / Exact Cover
3. **Metaheuristic Search algorithm**:
   - Genetic Algorithm (GA) with Adaptive Mutation
   - Artificial Bee Colony (ABC)

---

## Installation

### Prerequisites
- Python 3.10 or higher
- [Optional] `uv` for fast dependency management

### Setup
1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd hcmus-csc14003-project-2
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   *Note: Major dependencies include `numpy`, `PyQt6` (for GUI), and `matplotlib` (for plotting).*

---

## Usage

### 1. Running the GUI Application
Launch the main interface to solve puzzles interactively:
```bash
python src/main.py
```
From the GUI, you can:
- Select puzzle sizes (4x4 to 9x9).
- Choose different difficulty levels.
- Pick a specific algorithm and watch the "Step Player" visualize the search.

### 2. Running from Command Line
You can also run solvers directly using the `io_handler` (if supported by your script's CLI arguments):
```bash
python src/main.py --input inputs/input-01.txt --algorithm backtrack
```

---

## Testing & Benchmarking

### Test Data Generation
Generate test cases by crawling web data using Selenium:
```bash
python test/generate_test.py
```

### Running Algorithm Tests
Execute the test script to run algorithms across various puzzle sizes and difficulties. This will also generate performance plots in the `test/plot/` directory:
```bash
python test/test.py
```
This will output:
- **Time Comparison**: Execution time per algorithm.
- **Inferences/Nodes**: Efficiency of the search space.
- **Accuracy**: Verification that the solutions are valid.

---

## Project Structure
- `src/`: Core source code.
  - `algorithm/`: Implementation of all solving techniques.
  - `gui/`: PyQt6 windows, widgets, and state management.
  - `io_handler.py`: Logic for parsing `.txt` puzzle files.
- `inputs/`: Sample puzzle files.
- `test/`: Test scripts, log files, and performance visualizations.
- `requirements.txt`: Project dependencies.

---

## Puzzle Format
Input files follow this structure:
1. Grid size (N).
2. Initial grid values (0 for empty).
3. Horizontal constraints (represented as a matrix where `1` is `<`, `-1` is `>`, and `0` is none).
4. Vertical constraints.
