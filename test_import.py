#!/usr/bin/env python3
"""Quick test to verify the import fix"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

try:
    from algorithm.comparing_algorithms.artificial_bee_colony import ABC
    print("✓ ABC imported successfully!")
    print(f"  ABC class: {ABC}")
    print(f"  ABC base class: {ABC.__bases__}")
except ImportError as e:
    print(f"✗ Import error: {e}")
except Exception as e:
    print(f"✗ Error: {e}")
