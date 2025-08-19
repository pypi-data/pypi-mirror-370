"""Module for kernel quantization using maximum mean discrepancy."""

# This file is subject to the terms and conditions defined in
# file 'LICENSE.txt', which is part of this source code package.

import equinox as eqx
import jax
import jax.numpy as jnp

from kernax.types import JaxArray, KernelFn


class KernelHerding(eqx.Module):
    """Greedy MMD-based kernel quantization (herding-style thinning).

    Once instantiated, the module can be called with an integer `m` to
    select `m` representative samples from the input dataset.

    Args:
        x : The dataset of shape `(N, d)` to be subsampled.
        kernel_fn : Kernel function of the form ``k(x: (d,), y: (d,)) -> scalar``.
    """

    x: JaxArray
    kernel_fn: KernelFn = eqx.field(static=True)

    def __call__(self, m: int) -> JaxArray:
        """Return indices of a subset (size m) that greedily minimizes MMD.

        Args:
            m (int): Number of points to select (must be <= N).

        Returns:
            Indices of the selected points into `x`, array of shape `(m,)`.
        """
        x = self.x
        kernel_fn = self.kernel_fn

        def gram_matrix_fn(X: JaxArray, Y: JaxArray):
            return jax.vmap(lambda xx: jax.vmap(lambda yy: kernel_fn(xx, yy))(Y))(X)

        Kmat = gram_matrix_fn(x, x)

        k0_diag = jax.vmap(lambda xi: kernel_fn(xi, xi))
        k0 = k0_diag(x)
        k0_mean = jnp.mean(Kmat, axis=1)
        obj = k0 - 2.0 * k0_mean

        init = jnp.argmin(obj)
        kmap = jax.jit(jax.vmap(kernel_fn, (None, 0)))

        def thinning_step_fn(carry, _):
            idx_prev, obj_prev = carry
            ki = kmap(x[idx_prev], x)  # (n,)
            obj_new = obj_prev + 2.0 * ki - 2.0 * k0_mean
            new_idx = jnp.argmin(obj_new)
            return (new_idx, obj_new), new_idx

        (_, _), idx_tail = jax.lax.scan(thinning_step_fn, (init, obj), jnp.arange(1, m))
        return jnp.append(init, idx_tail)
