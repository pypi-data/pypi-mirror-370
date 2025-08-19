"""Module containing utility functions for Kernax."""

# This file is subject to the terms and conditions defined in
# file 'LICENSE.txt', which is part of this source code package.

from typing import Callable

import jax
import jax.numpy as jnp
import numpy as np
from jaxtyping import Array, ArrayLike, Float
from numpy.typing import NDArray
from scipy.spatial.distance import pdist

from kernax.types import JaxArray, LogProbFn


def median_heuristic(x: NDArray[np.int32 | np.int64]):
    """Function that computes the median heuristic for the lengthscale parameter.

    Args:
        x: Sample matrix of size `(n, d)`

    Returns:
        Median heuristic value.
    """
    return np.median(pdist(x))


def laplace_log_p_hardplus(x: ArrayLike, logprob_fn: LogProbFn) -> JaxArray:
    """Function that computes the clipped laplacian of a log-probability for the provided sample matrix.

    Args:
        x: Sample matrix of size `(n, d)`
        logprob_fn: Callable log-probability function

    Returns:
        Values of the laplacian of log-probability, clipped to be non-negative.
    """
    x_: JaxArray = jnp.asarray(x)
    jacobian_fn: Callable[[Float[Array, "n d"]], Float[Array, "n n"]] = jax.jacfwd(
        jax.jacrev(logprob_fn)
    )
    jacobians = jax.vmap(jacobian_fn, 0)(x_)
    llp = jnp.nan_to_num(jnp.clip(jax.vmap(jnp.trace)(jacobians), min=0))
    return llp


def laplace_log_p_softplus(x: ArrayLike, logprob_fn: LogProbFn) -> JaxArray:
    """Function that computes the sum of positive second-order derivatives of the log-probability for the provided sample matrix.

    Args:
        x: Sample matrix of size `(n, d)`
        logprob_fn: Callable log-probability function

    Returns:
        Values of the laplacian of log-probability
    """
    x_: JaxArray = jnp.asarray(x)
    jacobian_fn: Callable[[Float[Array, "n d"]], Float[Array, "n n"]] = jax.jacfwd(
        jax.jacrev(logprob_fn)
    )
    jacobians = jnp.nan_to_num(jnp.clip(jax.vmap(jacobian_fn, 0)(x_), min=0))
    llp = jax.vmap(jnp.trace)(jacobians)
    return llp
