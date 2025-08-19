<!--intro-start-->
# Kernel-based MCMC post-processing algorithms

Kernax is a small package that implements kernel-based post-processing and subsampling algorithms for MCMC output. It currently provides three algorithms:

* The vanilla Stein thinning algorithm, proposed by M. Riabiz et al. in [Optimal thinning of MCMC output](https://academic.oup.com/jrsssb/article-abstract/84/4/1059/7073269)
* The regularized Stein thinning algorithm, proposed by C. Bénard et al. in [Kernel Stein Discrepancy thinning: a theoretical perspective of pathologies and a practical fix with regularization](https://proceedings.neurips.cc/paper_files/paper/2023/hash/9a8eb202c060b7d81f5889631cbcd47e-Abstract-Conference.html).
* A greedy maximum mean discrepancy (MMD) subsampling algorithm (see, e.g., [Optimal quantisation of probability measures using maximum mean discrepancy](http://proceedings.mlr.press/v130/teymur21a.html)).
<!--intro-end-->

# Documentation

Full documentation is available on [Read the Docs](https://kernax.readthedocs.io/en/latest/?kernax=latest).

<!--quick-start-->
# Quick start

Example usage of Stein thinning on a Gaussian sample:

```python
import jax
import jax.numpy as jnp
from jax.scipy.stats import multivariate_normal
from kernax.utils import median_heuristic
from kernax import SteinThinning

rng_key = jax.random.PRNGKey(0)
x = jax.random.normal(rng_key, (1000,2))

def logprob_fn(x):
    return multivariate_normal.logpdf(x, mean=jnp.zeros(2), cov=jnp.eye(2))
score_fn = jax.grad(logprob_fn)
score_values = jax.vmap(score_fn, 0)(x)

lengthscale = jnp.array([median_heuristic(x)])
stein_fn = SteinThinning(x, score_values, lengthscale)
indices = stein_fn(100)
```

To use the regularized variant, add a few lines:

```python
from kernax.utils import laplace_log_p_softplus
from kernax import RegularizedSteinThinning

log_p = jax.vmap(score_fn, 0)(x)
laplace_log_p_values = laplace_log_p_softplus(x, score_fn)

reg_stein_fn = RegularizedSteinThinning(x, log_p, score_values, laplace_log_p_values, lengthscale)
indices = reg_stein_fn(100)
```
<!--quick-start-end-->

<!--installation-start-->
# Install guide

## As a user

A Python wheel is available on [PyPi](https://pypi.org/project/kernax/). Install Kernax into your Python environment with:

```console
pip install kernax
```

## As a developper

We recommand using [uv](https://docs.astral.sh/uv/getting-started/installation/). Clone the repository, then run:
```bash
uv sync
```

This creates a virtual environment for developing Kernax. If you’re not familiar with `uv`, have a look at their [Getting started](https://docs.astral.sh/uv/getting-started/) guide.
<!--installation-end-->

<!--paper-experiments-start-->
# Paper experiments

This repository implements the regularized Stein thinning algorithm introduced in [Kernel Stein Discrepancy thinning: a theoretical perspective of pathologies and a practical fix with regularization](https://proceedings.neurips.cc/paper_files/paper/2023/hash/9a8eb202c060b7d81f5889631cbcd47e-Abstract-Conference.html).

If you use this library, please consider citing:
```bibtex
@article{benard2023kernel,
  title={Kernel Stein Discrepancy thinning: a theoretical perspective of pathologies and a practical fix with regularization},
  author={B{\'e}nard, Cl{\'e}ment and Staber, Brian and Da Veiga, S{\'e}bastien},
  journal={arXiv preprint arXiv:2301.13528},
  year={2023}
}
```

All numerical experiments presented in the [paper](https://proceedings.neurips.cc/paper_files/paper/2023/hash/9a8eb202c060b7d81f5889631cbcd47e-Abstract-Conference.html) can be reproduced using the scripts in the `example/` folder.

In particular:

* Figures 1–3: `example/mog_randn.py`
* Section 4 and Appendix 1:
    * Gaussian mixture: `example/mog4_mcmc/` and `example/mog4_mcmc_dim/`
    * Mixture of banana-shaped distributions: `example/mobt2_mcmc/` and `example/mobt2_mcmc_dim/`
    * Bayesian logistic regression: `example/logistic_regression.py`
* Supplementary material:
    * Figure 2: `example/mog_weight_weights.py`
    * Figure 6: `example/mog4_mcmc_lambda`
<!--paper-experiments-end-->