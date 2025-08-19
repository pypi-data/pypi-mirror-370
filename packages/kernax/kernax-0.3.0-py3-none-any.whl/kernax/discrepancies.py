"""Module for discrepancy measures."""

# This file is subject to the terms and conditions defined in
# file 'LICENSE.txt', which is part of this source code package.

from typing import Callable, Optional

import jax
import jax.numpy as jnp
import numpy as np
from jaxtyping import Scalar

from kernax.kernels import IMQ, Energy, GetSteinFn
from kernax.types import JaxArray
from kernax.utils import median_heuristic


def MMD(x: JaxArray, y: JaxArray) -> Scalar:
    """Implements the V-estimator the maximum mean discrepancy.

    Args:
        x (JaxArray): Sample matrix of size `(n, d)`.
        y (JaxArray): Sample matrix of size `(m, d)`.

    Returns:
        JaxArray: The V-estimator of the maximum mean discrepancy.
    """
    kxx = jax.vmap(lambda x1: jax.vmap(lambda y1: Energy(x1, y1))(x))(x)
    kyy = jax.vmap(lambda x1: jax.vmap(lambda y1: Energy(x1, y1))(y))(y)
    kxy = jax.vmap(lambda x1: jax.vmap(lambda y1: Energy(x1, y1))(x))(y)
    mmd = (
        (1.0 / x.shape[0] ** 2) * kxx.sum()
        + (1.0 / y.shape[0] ** 2) * kyy.sum()
        - (2.0 / (x.shape[0] * y.shape[0])) * kxy.sum()
    )
    return jnp.sqrt(mmd)


def KSD(x: JaxArray, sx: JaxArray, kernel_fn: Optional[Callable] = None) -> Scalar:
    """Implements the V-estimator of kernelized Stein discrepancy.

    This function is not jittable yet.

    Args:
        x (JaxArray): Sample matrix of size `(n, d)`.
        sx (JaxArray): Score function evaluated at x, matrix of size `(n, d)`.
        kernel_fn (Optional[Callable]): Kernel function that takes two inputs and returns a scalar. If None, the IMQ kernel is used with a lengthscale determined by the median heuristic.

    Returns:
        JaxArray: The V-estimator of the kernelized Stein discrepancy.
    """
    if kernel_fn is None:
        lengthscale = jnp.array(median_heuristic(np.asarray(x)))
        kernel_fn = jax.tree_util.Partial(IMQ, lengthscale=lengthscale)

    kp_fn = GetSteinFn(kernel_fn)
    kp = jax.vmap(lambda a, b: jax.vmap(lambda c, d: kp_fn(a, b, c, d))(x, sx))(x, sx)
    ksd = jnp.sqrt(jnp.sum(kp)) / x.shape[0]
    return ksd
