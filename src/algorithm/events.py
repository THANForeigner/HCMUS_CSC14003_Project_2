# Step event helpers for visualizer
# Represent a step as a 4-tuple: (action, row, col, value)
# action: 'check' | 'assign' | 'backtrack' | 'final'

from typing import Tuple

Step = Tuple[str, int, int, int]


def make_step(action: str, r: int, c: int, value: int) -> Step:
    return (action, r, c, value)
