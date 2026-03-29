#!/usr/bin/env python3
"""Test script for I/O functions"""

import numpy as np
import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))
from main import read_input, format_output, write_output

# Test data
size = 4
grid = [
    [2, 0, 3, 4],
    [3, 4, 0, 1],
    [2, 0, 4, 3],
    [4, 3, 1, 0]
]

h_constraints = [
    [1, 0, -1],
    [0, 0, 0],
    [0, 1, 0],
    [-1, 0, 0]
]

v_constraints = [
    [0, 1, 0, 0],
    [0, 0, -1, 0],
    [-1, 0, 0, 0]
]

# Solution
solution = np.array([
    [2, 1, 3, 4],
    [3, 4, 2, 1],
    [2, 3, 4, 1],  # This is just an example, might not satisfy all constraints
    [4, 2, 1, 3]
])

print("=" * 60)
print("Testing format_output function")
print("=" * 60)

formatted = format_output(solution, h_constraints, v_constraints)
print("\nFormatted output:")
print(formatted)

print("\n" + "=" * 60)
print("Expected format (from your example):")
print("=" * 60)
print("""2 < 3   4   1
v
1   2 > 3   4

4   1   2   3
^
3   4   1 < 2""")

# Test write to file
output_path = Path(__file__).parent / "outputs" / "test-output.txt"
output_path.parent.mkdir(parents=True, exist_ok=True)

write_output(output_path, solution, h_constraints, v_constraints)
print(f"\n✓ Written to {output_path}")

# Test read from input
input_path = Path(__file__).parent / "inputs" / "input-01.txt"
if input_path.exists():
    print(f"\n✓ Input file exists: {input_path}")
    try:
        size, grid, constraint = read_input(input_path)
        print(f"  Size: {size}x{size}")
        print(f"  Grid: {np.array(grid)}")
        print(f"  H-constraints shape: {np.array(constraint[0]).shape}")
        print(f"  V-constraints shape: {np.array(constraint[1]).shape}")
    except Exception as e:
        print(f"  Error reading: {e}")
else:
    print(f"\n✗ Input file missing: {input_path}")
    print("  Creating sample input file...")
    
    with open(input_path, 'w') as f:
        f.write("4\n")
        f.write("2 0 3 4\n")
        f.write("3 4 0 1\n")
        f.write("2 0 4 3\n")
        f.write("4 3 1 0\n")
        f.write("1 0 -1 0\n")
        f.write("0 0 0 0\n")
        f.write("0 1 0 0\n")
        f.write("-1 0 0 0\n")
        f.write("0 1 0 0\n")
        f.write("0 0 -1 0\n")
        f.write("-1 0 0 0\n")
    
    print(f"  ✓ Created {input_path}")
    
    # Now test reading
    size, grid, constraint = read_input(input_path)
    print(f"  ✓ Read successfully")
    print(f"    Size: {size}x{size}")
    print(f"    Grid loaded: {np.array(grid).shape}")

print("\n" + "=" * 60)
print("✓ All tests completed!")
print("=" * 60)
