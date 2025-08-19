"""Kernax package."""

# This file is subject to the terms and conditions defined in
# file 'LICENSE.txt', which is part of this source code package.

from .quantization import (
    KernelHerding,
)
from .thinning import (
    RegularizedSteinThinning,
    SteinThinning,
)

__all__ = [
    "SteinThinning",
    "RegularizedSteinThinning",
    "KernelHerding",
]
