# numpyro_schechter

**Schechter galaxy luminosity distribution for NumPyro**

<p align="center">
  <img src="https://raw.githubusercontent.com/alserene/numpyro_schechter/main/docs/assets/logo.png" alt="Schechter distribution logo for numpyro_schechter" width="300"/>
</p>

<p align="center">
  <a href="https://pypi.org/project/numpyro-schechter/">
    <img src="https://img.shields.io/pypi/pyversions/numpyro-schechter.svg" alt="Python Versions">
  </a>
  <a href="https://numpyro-schechter.readthedocs.io/en/latest/?badge=latest">
    <img src="https://readthedocs.org/projects/numpyro-schechter/badge/?version=latest" alt="Docs Status">
  </a>
  <a href="https://pypi.org/project/numpyro-schechter/">
    <img src="https://img.shields.io/pypi/v/numpyro-schechter.svg" alt="PyPI">
  </a>
  <a href="https://opensource.org/licenses/MIT">
    <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="MIT License">
  </a>
  <a href="https://github.com/alserene/numpyro_schechter/actions/workflows/tests.yml">
    <img src="https://github.com/alserene/numpyro_schechter/actions/workflows/tests.yml/badge.svg" alt="Tests">
  </a>
</p>

---

## Overview

`numpyro_schechter` provides NumPyro-compatible probability distributions for Bayesian inference with Schechter and double Schechter luminosity functions in absolute magnitude space.

Built for astronomers and statisticians, it includes a JAX-compatible, differentiable implementation of the upper incomplete gamma function, enabling stable and efficient modelling in probabilistic programming frameworks.

---

## Parameter Constraints

Due to the custom normalisation logic, some constraints apply:

- `alpha` must be real and non-integer.
- The valid range of `alpha + 1` depends on `alpha_domain_depth`. By default, `alpha_domain_depth=3`, which supports the domain `-3 < alpha + 1 < 3`.
- To model more extreme values of `alpha`, increase the `alpha_domain_depth` parameter (see below).
- The list of valid depths is fixed and can be queried programmatically:
  ```python
  from numpyro_schechter import SchechterMag
  SchechterMag.supported_depths()
  # -> [3, 4, 5, 6, 7, 8, 9, 10, 15, 20, 30]
  ```
- If you set `include_poisson_term=True`, the log-likelihood will also include a Poisson term for the total number counts, with expectation `N_exp = norm * volume`. The volume argument defaults to `1.0` but can be set to your survey volume.

---

## Installation

From PyPI:

```bash
pip install numpyro_schechter
```

From GitHub (latest development version):

```bash
pip install git+https://github.com/alserene/numpyro_schechter.git
```

---

## Usage

### Single Schechter Example

Here is a minimal example showing how to use the `SchechterMag` distribution:

```python
import jax.numpy as jnp
import numpyro
import numpyro.distributions as dist
from numpyro_schechter.distribution import SchechterMag

# Simulated observed magnitudes
mag_obs = jnp.linspace(-24, -18, 100)

def model(mag_obs):
    # Priors
    alpha = numpyro.sample("alpha", dist.Uniform(-3.0, 1.0))
    M_star = numpyro.sample("M_star", dist.Uniform(-24.0, -20.0))
    logphi = numpyro.sample("logphi", dist.Normal(-3.0, 1.0))

    # Custom likelihood using the SchechterMag distribution, fitting only
    # the shape. Adding include_poisson_term=True would include total counts.
    # See Double Schechter Example for fitting both shape and total count.
    schechter_dist = SchechterMag(alpha=alpha, M_star=M_star, logphi=logphi,
                                  mag_obs=mag_obs)
    
    # Manually inject log-likelihood of observed magnitudes.
    # Required because SchechterMag/DoubleSchechterMag are custom distributions.
    log_likelihood = jnp.sum(schechter_dist.log_prob(mag_obs))
    numpyro.factor("likelihood", log_likelihood)

# You can now run inference with NumPyro's MCMC
# e.g., numpyro.infer.MCMC(...).run(rng_key, model, mag_obs=...)

# Note: Sampling is not implemented for SchechterMag or DoubleSchechterMag;
# it is intended for use as a likelihood in inference.
```

### Double Schechter Example

The double Schechter function is the sum of two Schechter components, each with their own parameters 
$(\alpha, M^\*, \phi^\*)$, normalised together over the observed magnitude range:

$$
\phi_{\text{double}}(M) = 
\frac{\phi_1(M) + \phi_2(M)}{\phi_1^\* \Gamma_1 + \phi_2^\* \Gamma_2}
$$

where $\Gamma_i$ is the upper incomplete gamma function for component $i$.

```python
import jax.numpy as jnp
import numpyro
import numpyro.distributions as dist
from numpyro_schechter import DoubleSchechterMag

def double_schechter_model(mag_obs, volume):
    # Slopes
    alpha1 = numpyro.sample("alpha1", dist.TruncatedNormal(-0.3, 0.1, low=-1.5, high=0.5))
    alpha2 = numpyro.sample("alpha2", dist.TruncatedNormal(-1.3, 0.1, low=-2.5, high=-0.5))

    # Normalisations (log10 φ*)
    logphi1 = numpyro.sample("logphi1", dist.Normal(-2.5, 0.3))
    logphi2 = numpyro.sample("logphi2", dist.Normal(-3.0, 0.3))

    # Break magnitudes
    M_star1 = numpyro.sample("M_star1", dist.TruncatedNormal(-21.0, 0.5, low=-23.0, high=-19.0))
    M_star2 = numpyro.sample("M_star2", dist.TruncatedNormal(-21.5, 0.5, low=-23.5, high=-19.5))

    # Likelihood: includes both point term and Poisson count term to fit
    # both shape and total count. If include_poisson_term=True, then volume
    # is used to scale expected counts and defaults to 1.0.
    dbl_schechter_dist = DoubleSchechterMag(alpha1, M_star1, logphi1,
                                    alpha2, M_star2, logphi2,
                                    mag_obs=mag_obs,
                                    include_poisson_term=True,
                                    volume=volume)

    # Manually inject log-likelihood of observed magnitudes.
    # Required because SchechterMag/DoubleSchechterMag are custom distributions.
    log_likelihood = jnp.sum(dbl_schechter_dist.log_prob(mag_obs))
    numpyro.factor("likelihood", log_likelihood)

# --- Example MCMC runner (same approach can be used for SchechterMag)
# from numpyro.infer import MCMC, NUTS
# mcmc = MCMC(NUTS(double_schechter_model), num_warmup=1000, num_samples=2000)
# mcmc.run(rng_key, mag_obs=your_magnitude_array, volume=your_survey_volume)
# samples = mcmc.get_samples()

```

For detailed usage and API documentation, please visit the [Documentation](https://numpyro-schechter.readthedocs.io/).

---

## Development

If you want to contribute or develop locally:

```bash
git clone https://github.com/alserene/numpyro_schechter.git
cd numpyro_schechter
poetry install
poetry run pytest
```

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file.

---

## Contact

Created by
 - Alice — [aserene@swin.edu.au](mailto:aserene@swin.edu.au)
 - Aryan - [aryanbansal@swin.edu.au](mailto:aryanbansal@swin.edu.au)
 - Edward - [entaylor@swin.edu.au](mailto:entaylor@swin.edu.au)

---

*Happy modelling!*
