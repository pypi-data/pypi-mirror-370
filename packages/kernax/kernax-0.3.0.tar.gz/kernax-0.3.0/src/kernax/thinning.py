"""Module for Stein thinning algorithms using Langevin Stein operator and IMQ kernel."""

# This file is subject to the terms and conditions defined in
# file 'LICENSE.txt', which is part of this source code package.

from typing import Optional

import equinox as eqx
import jax
import jax.numpy as jnp
import numpy as np
from jaxtyping import ArrayLike

from kernax import kernels
from kernax.types import JaxArray, KernelFn
from kernax.utils import median_heuristic


class SteinThinning(eqx.Module):
    """Greedy Stein thinning with the Langevin Stein operator and IMQ kernel.

    Once instantiated, the module can be called with an integer ``m`` to select
    ``m`` representative indices from the dataset by greedily minimizing the
    Stein objective (Riabiz et al., 2022).

    Args:
        x (JaxArray): Samples to thin of shape `(N, d)`.
        score_p (JaxArray): Scores of the target log-density evaluated at ``x`` (i.e., ``∇_x log p(x)``) of shape `(N, d)`.
        lengthscale (float, optional): IMQ kernel lengthscale. If ``None``, uses the median heuristic on ``x``.
        stein_kernel (Callable, optional): A Stein kernel function with signature ``stein_kernel(xi, si, xj, sj, *, lengthscale) -> scalar``. Defaults to :func:`kernax.kernels.SteinIMQ`.
    """

    x: JaxArray
    score_p: JaxArray
    lengthscale: Optional[ArrayLike] = None
    stein_kernel: KernelFn = eqx.field(static=True, default=kernels.SteinIMQ)

    def __call__(self, m: int) -> JaxArray:
        """Select a subset of size ``m`` via greedy Stein thinning.

        Args:
            m (int): Number of points to select (must be <= N).

        Returns:
            indices (JaxArray): Indices of the selected points into ``x``, of shape `(m,)`.
        """
        x, s = self.x, self.score_p
        n: int = x.shape[0]
        m = int(jnp.clip(m, 1, n))

        lengthscale = (
            jnp.asarray(self.lengthscale)
            if self.lengthscale is not None
            else jnp.asarray(median_heuristic(np.asarray(x)))
        )

        stein_fn = jax.tree_util.Partial(self.stein_kernel, lengthscale=lengthscale)

        kpmap = jax.vmap(stein_fn, in_axes=(None, None, 0, 0))

        def step(carry, _):
            obj, idx_prev = carry
            ki = kpmap(x[idx_prev], s[idx_prev], x, s)
            obj += 2.0 * ki
            new_idx = jnp.argmin(obj)
            return (obj, new_idx), new_idx

        init_obj = jax.vmap(lambda xi, si: stein_fn(xi, si, xi, si), (0, 0))(x, s)
        init_idx = jnp.argmin(init_obj)

        (_, _), idx_tail = jax.lax.scan(step, (init_obj, init_idx), jnp.arange(1, m))
        return jnp.append(init_idx, idx_tail)


class RegularizedSteinThinning(eqx.Module):
    """Regularized Stein thinning with the Langevin Stein operator and IMQ kernel.

    Adds an entropy-style regularization term based on the target log-density.

    Args:
        x (JaxArray): Samples to thin of shape `(N, d)`.
        log_p (JaxArray): Target log-density evaluated at ``x`` of shape `(N,)`.
        score_p (JaxArray): Scores of the target log-density at ``x`` (i.e., ``∇_x log p(x)``), of shape `(N, d)`.
        laplace_log_p (JaxArray): Laplacian of the log-density at ``x``, of shape `(N,)`.
        lengthscale (float, optional): IMQ kernel lengthscale. If ``None``, uses the median heuristic on ``x``.
        stein_kernel (Callable, optional): A Stein kernel function with signature ``stein_kernel(xi, si, xj, sj, *, lengthscale) -> scalar``. Defaults to :func:`kernax.kernels.SteinIMQ`.
    """

    x: JaxArray
    log_p: JaxArray
    score_p: JaxArray
    laplace_log_p: JaxArray
    lengthscale: Optional[ArrayLike] = None
    stein_kernel: KernelFn = eqx.field(static=True, default=kernels.SteinIMQ)

    def __call__(self, m: int, weight_entropy: Optional[float] = None) -> JaxArray:
        """Select a subset of size ``m`` via regularized Stein thinning.

        Args:
            m (int): Number of points to select (must be <= N).
            weight_entropy (float, optional): Strength of the entropy regularization. Defaults to ``1.0 / m``.

        Returns:
            indices (JaxArray): Indices of the selected points into ``x``, of shape (m,).
        """
        x, s, logp, lap = self.x, self.score_p, self.log_p, self.laplace_log_p
        n = x.shape[0]
        m = int(jnp.clip(m, 1, n))
        weight_entropy = (
            (1.0 / float(m)) if (weight_entropy is None) else float(weight_entropy)
        )

        lengthscale = (
            jnp.asarray(self.lengthscale)
            if self.lengthscale is not None
            else jnp.asarray(median_heuristic(np.asarray(x)))
        )

        stein_fn = jax.tree_util.Partial(self.stein_kernel, lengthscale=lengthscale)
        kpmap = jax.vmap(stein_fn, in_axes=(None, None, 0, 0))

        def step(carry, _):
            obj, idx_prev = carry
            ki = kpmap(x[idx_prev], s[idx_prev], x, s)
            obj += 2.0 * ki - weight_entropy * logp
            new_idx = jnp.argmin(obj)
            return (obj, new_idx), new_idx

        init_diag = jax.vmap(lambda xi, si: stein_fn(xi, si, xi, si))(x, s)
        init_obj = init_diag + lap - weight_entropy * logp

        init_idx = jnp.argmin(init_obj)
        (_, _), idx_tail = jax.lax.scan(step, (init_obj, init_idx), jnp.arange(1, m))
        return jnp.append(init_idx, idx_tail)
