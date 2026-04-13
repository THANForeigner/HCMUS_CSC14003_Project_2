# Plan: Futoshiki gaming app (src\gui)

## Goal
Create a playable Futoshiki GUI app under src\gui that can:
- Generate and present random valid puzzles (with adjustable size/difficulty)
- Let the user attempt to solve puzzles with a responsive UI
- Demonstrate the solving algorithm(s) implemented in src/algorithm (step tracing or animated solve)
- Show solver statistics (nodes generated/expanded, time)

## Current codebase snapshot
- Project uses Python + flet for GUI (src/main.py uses flet and imports gui.home_page and gui.puzzle_page).
- Algorithm module exists (src/algorithm/futoshiki_solver.py) with solver base classes and state utilities.
- io_handler.py contains input parsing and output formatting utilities.

## High-level approach
1. Reuse existing flet-based app structure: implement UI pages/components under src/gui (home_page.py, puzzle_page.py already present as stubs).
2. Implement a "PuzzleManager" responsible for generating random puzzles and validating them. Keep generation deterministic for tests (seed option).
3. Integrate solver classes from src/algorithm: provide a SolverController that accepts a puzzle, runs the solver (sync or step-by-step) and exposes stats and step traces to the UI.
4. UI features: puzzle grid widget with cell editing, inequality display, controls to generate new puzzle, start/pause/step solver, speed slider, and export/save.
5. Tests: unit tests for PuzzleManager (generation/validation) and SolverController (correctness/stats). Minimal GUI smoke tests where possible.

## Todos (high-level)
- gui-structure: Create pages/components to host game (home_page, puzzle_page, grid widget, controls).
- random-puzzle: Implement PuzzleManager with random generator, seeding, difficulty parameter, and validation utilities.
- solver-integration: Add SolverController to run algorithm, capture step traces, and provide pause/step/auto-run APIs.
- solution-checker: Implement solution checker using z3 to verify uniqueness and validate user-submitted solutions.
- visualization: Render inequalities and solver steps in the grid with animation support and speed control.
- ui-controls: Add controls for new puzzle, size/difficulty selection, solver start/pause/step, and stats display.
- tests: Add unit tests for PuzzleManager, SolverController & solution_checker and simple integration test for solver producing valid solutions.

## Files to add/modify (planned)
- src/gui/home_page.py (update to include entry controls: size/difficulty, start random puzzle)
- src/gui/puzzle_page.py (main puzzle UI + solver controls)
- src/gui/grid_widget.py (new: renders grid + inequalities, cell editing, highlights)
- src/gui/solver_controller.py (new: runs solver, exposes API and step traces)
- src/gui/puzzle_manager.py (new: generator + validator)
- src/gui/solution_checker.py (new: uses z3 to formally verify uniqueness and validate candidate solutions)
- tests/test_puzzle_manager.py, tests/test_solver_controller.py, tests/test_solution_checker.py

## Design decisions / constraints
- Use existing flet UI approach used by src/main.py; avoid introducing new GUI frameworks.
- Puzzle generator should produce puzzles with a unique solution where feasible; initial version may generate full valid solution then remove numbers while respecting inequalities.
- Add a solution_checker component (src/gui/solution_checker.py) that uses the z3 SMT solver to perform formal uniqueness checks and to validate user-submitted solutions. Include z3 in requirements (e.g., `z3-solver` package).
- Solver integration will prioritize step-by-step interactive demo (user-driven stepping). A full-run mode that returns final solution and stats will remain available.
- Keep heavy computation off the UI event loop where possible (use Python threads or async calls with careful flet integration).

## Acceptance criteria
- App can generate a random 5x5 puzzle and display it in the puzzle page.
- Solver can solve that puzzle and UI displays the final solution and stats.
- User can run solver in step mode and see cell assignments animated.
- Unit tests for PuzzleManager and SolverController exist and pass locally.

## Risks / Unknowns / Questions
- How strict should the generator be about uniqueness of solutions? (affects generator complexity and time)
- Solver demo style chosen: Step-by-step interactive (user selected). This decision influences UI controls (step/pause) and SolverController API.

## Implementation phases
1. Phase 1 (scaffold): Add grid_widget stub, basic puzzle_page UI, and connect new-puzzle control to PuzzleManager generating a solved board (no removals yet).
2. Phase 2 (generator): Implement removal logic to make playable puzzles and validate uniqueness (best-effort). Add unit tests.
3. Phase 3 (solver): Integrate SolverController with existing algorithm base, implement full-run and step-trace modes. Add stats reporting.
4. Phase 4 (polish): Animation, controls (pause/step/speed), save/load, tests and small performance tweaks.

