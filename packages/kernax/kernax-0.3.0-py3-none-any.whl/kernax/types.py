"""Custom types for Kernax."""

# This file is subject to the terms and conditions defined in
# file 'LICENSE.txt', which is part of this source code package.

from typing import Callable, TypeAlias

from jaxtyping import Array, Float, PRNGKeyArray, Scalar

# Public aliases
JaxArray: TypeAlias = Array
PRNGKey: TypeAlias = PRNGKeyArray

# Common callables
# log p(x): (n,d) -> (n,)
LogProbFn: TypeAlias = Callable[[Float[Array, "n d"]], Float[Array, "n"]]

# score(x): (n,d) -> (n,d)
ScoreFn: TypeAlias = Callable[[Float[Array, "n d"]], Float[Array, "n d"]]

# kernel(X, Y): (n,d),(m,d) -> (n,m)
KernelFn: TypeAlias = Callable[[Float[Array, "d"], Float[Array, "d"]], Scalar]

SteinKernelFn: TypeAlias = Callable[
    [
        Float[Array, "n d"],
        Float[Array, "n d"],
        Float[Array, "m d"],
        Float[Array, "m d"],
    ],
    JaxArray,
]
