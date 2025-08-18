
import numpy as np
from dataclasses import dataclass, field
from typing import List, Dict



@dataclass(slots=True, frozen=True)
class ExpiryAttributes:
    expiry: float
    strikes: np.ndarray[float]
    n_strikes: int
    expiry_idx: int
    strike_idx_map: Dict[float, int]


def get_closest_n_strikes(center_strike, strike_arr, n):
    differences = np.abs(center_strike - strike_arr)
    sorted_indexes = np.argsort(differences)
    closest_indices = sorted_indexes[:n]
    closest_strikes = strike_arr[closest_indices]
    closest_strikes.sort()
    return closest_strikes, closest_indices, sorted_indexes[n:]
