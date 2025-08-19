"""Module containing kernel functions for use in Kernax."""

# This file is subject to the terms and conditions defined in
# file 'LICENSE.txt', which is part of this source code package.

import jax
import jax.numpy as jnp
from jaxtyping import Scalar

from kernax.types import JaxArray, KernelFn, SteinKernelFn


def IMQ(x: JaxArray, y: JaxArray, lengthscale: float) -> Scalar:
    """Inverse multi-quadratric kernel function.

    Args:
        x: Vector of dimension `d`
        y: Vector of dimension `d`
        lengthscale: Scalar lengthscale / bandwidth

    Returns:
        Value of the kernel function `k(x,y)`
    """
    return 1.0 / jnp.sqrt(1.0 + jnp.sum((x - y) ** 2) / lengthscale**2)


def Gaussian(x: JaxArray, y: JaxArray, lengthscale: float) -> Scalar:
    """Gaussian kernel function.

    Args:
        x: Vector of dimension `d`
        y: Vector of dimension `d`
        lengthscale: Scalar lengthscale / bandwidth

    Returns:
        Value of the kernel function `k(x,y)`
    """
    return jnp.exp(-0.5 * jnp.sum((x - y) ** 2) / lengthscale**2)


def Energy(x: JaxArray, y: JaxArray) -> Scalar:
    """Distance induced kernel function.

    Args:
        x: Vector of dimension `d`
        y: Vector of dimension `d`
        lengthscale: Scalar lengthscale / bandwidth

    Returns:
        Value of the kernel function `k(x,y)`
    """
    # return jnp.sqrt(jnp.sum(x**2)) + jnp.sqrt(jnp.sum(y**2)) - jnp.sqrt(jnp.sum((x-y)**2))
    return (
        jnp.sqrt(x @ x)
        + jnp.sqrt(y @ y)
        - jnp.sqrt(jnp.clip(x @ x + y @ y - 2 * x @ y, min=0))
    )


def SteinIMQ(
    x: JaxArray, sx: JaxArray, y: JaxArray, sy: JaxArray, lengthscale: float
) -> Scalar:
    """Langevin Stein kernel with the IMQ as the underlying kernel.

    Args:
        x: Vector of dimension `d`
        sx: Score functon evaluated at x, vector of dimension `d`
        y: Vector of dimension `d`
        sy: Score function evaluetaed at y, vector of dimension `d`
        lengthscale: Scalar lengthscale / bandwidth

    Returns:
        Value the Stein IMQ kernel `k_p(x,y)`
    """
    d = len(x)
    sqdist = jnp.sum((x - y) ** 2)
    qf = 1.0 / (1.0 + sqdist / lengthscale**2)
    t3 = jnp.dot(sx, sy) * jnp.sqrt(qf)
    t2 = (1.0 / lengthscale**2) * (d + jnp.dot(sx - sy, x - y)) * qf ** (3 / 2)
    t1 = (-3.0 / lengthscale**4) * sqdist * qf ** (5 / 2)
    return t1 + t2 + t3


def SteinGaussian(
    x: JaxArray, sx: JaxArray, y: JaxArray, sy: JaxArray, lengthscale: float
) -> Scalar:
    """Langevin Stein kernel with the Gaussian kernel as the underlying kernel.

    Args:
        x: Vector of dimension `d`
        sx: Score function evaluated at x, vector of dimension `d`
        y: Vector of dimension `d`
        sy: Score function evaluetaed at y, vector of dimension `d`
        lengthscale: Scalar lengthscale / bandwidth

    Returns:
        Value the Stein Gaussian kernel `k_p(x,y)`
    """
    d = len(x)
    sqdist = jnp.sum((x - y) ** 2)
    kxy = jnp.exp(-0.5 * sqdist / lengthscale**2)
    t1 = d / lengthscale**2 - sqdist / lengthscale**4
    t2 = jnp.dot(sx - sy, x - y) / lengthscale**2
    t3 = jnp.dot(sx, sy)
    return kxy * (t1 + t2 + t3)


def GetSteinFn(kernel_fn: KernelFn) -> SteinKernelFn:
    r"""Helper that builds the Stein kernel function `k_p(x,y)` given an arbitrary underlying kernel `k(x,y)`.

    The function signature is `kp_fn(x, sx, y, sy)`, where `x` and `y` are vectors of dimension `d`, and `sx` and `sy` are the score functions evaluated at `x` and `y`, respectively, both of dimension `d`.

    Args:
        kernel_fn: Callable kernel function of the form `(x,y) \mapsto k(x,y)`. Any hyperparameters such as the lengthscale should be fixed with `jax.tree_util.Partial`.

    Returns:
        A function that computes the Stein kernel `k_p(x,y)` given two vectors `x` and `y`, and their corresponding score functions `sx` and `sy`.
    """
    grad1_fn = jax.grad(kernel_fn, argnums=0)
    grad2_fn = jax.grad(kernel_fn, argnums=1)
    hessian_fn = jax.jacobian(grad2_fn, argnums=0)

    def kp_fn(x, sx, y, sy):
        return (
            jnp.dot(sx, sy) * kernel_fn(x, y)
            + jnp.dot(sx, grad2_fn(x, y))
            + jnp.dot(sy, grad1_fn(x, y))
            + jnp.trace(hessian_fn(x, y))
        )

    return kp_fn
