from __future__ import annotations

import math


def round_up_to_increment(value: float, increment: float) -> float:
    if increment <= 0:
        return value
    return math.ceil((value - 1e-12) / increment) * increment
