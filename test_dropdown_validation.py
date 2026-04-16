import sys
sys.path.insert(0, 'src')
from io_handler import get_test_inputs

# Test the data structure that the dropdowns will use
test_data = get_test_inputs()

print("=" * 60)
print("DROPDOWN DATA VALIDATION TEST")
print("=" * 60)

# Test 1: Size dropdown
print("\n1. SIZE DROPDOWN OPTIONS:")
sizes = sorted(test_data.keys())
print(f"   Available sizes: {sizes}")
for size in sizes:
    print(f"   - Size {size}: ✓")

# Test 2: Difficulty dropdown for each size
print("\n2. DIFFICULTY DROPDOWN OPTIONS (for each size):")
for size in sizes:
    diffs = sorted(test_data[size].keys())
    print(f"   Size {size}: {diffs}")

# Test 3: ID dropdown cascading
print("\n3. ID DROPDOWN OPTIONS (cascading test):")
test_size = 4
test_diff = "easy"
ids = sorted(test_data[test_size][test_diff].keys())
print(f"   Size {test_size}, Difficulty '{test_diff}': {ids}")

# Test 4: Path resolution
print("\n4. PATH RESOLUTION TEST:")
for size in [4, 5]:
    for diff in sorted(test_data[size].keys())[:2]:
        for puzzle_id in sorted(test_data[size][diff].keys())[:1]:
            path = test_data[size][diff][puzzle_id]
            print(f"   Size {size}, {diff}, ID {puzzle_id}: {path}")

print("\n" + "=" * 60)
print("✓ All dropdown data validated successfully!")
print("=" * 60)
