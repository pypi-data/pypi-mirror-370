import jax.numpy as jnp
from jax.scipy.special import gammaln
from numpyro.distributions import Distribution, constraints, Poisson
from .math_utils import custom_gammaincc, schechter_mag, SUPPORTED_ALPHA_DOMAIN_DEPTHS, LN10_0p4


class SchechterMag(Distribution):
    """
    NumPyro-compatible distribution based on the single-component Schechter luminosity function in absolute magnitude space.

    This distribution models galaxy number densities using the Schechter parameterisation in magnitude space:
        φ(M) ∝ 10**[0.4(α + 1)(M* − M)] * exp[−10**(0.4(M* − M))]

    Parameters
    ----------
    alpha : float
        Faint-end slope of the Schechter function.
    M_star : float
        Characteristic magnitude (M*).
    logphi : float
        Logarithm (base 10) of the normalisation φ* (number density per unit volume per magnitude). 
        The internal `phi_star` is computed as 10**logphi. 
    mag_obs : array-like
        Observed magnitudes used for computing the likelihood.
    include_poisson_term : bool, optional
        If True, includes a Poisson likelihood term on the total observed counts to constrain φ*.
    volume : float, optional
        Survey volume, used to scale expected counts for the Poisson term.
        Volume is in the same units as `phi_star` (e.g., if `phi_star` is per Mpc³ per mag, 
        volume should be in Mpc³).
    alpha_domain_depth : int, optional
        Depth parameter for recurrence-based incomplete gamma calculation (default=3).

    Constraints
    -----------
    - `alpha` must be real and non-integer. By default, the valid domain for `alpha + 1` is (−3, 3), corresponding
      to `alpha_domain_depth=3`. To support broader domains, increase `alpha_domain_depth` (see note).
    - `mag_obs` must contain values such that `10**(0.4(M* − M)) > 0`.

    Notes
    -----
    - Normalisation is handled via a custom, recurrence-based computation of the upper incomplete gamma function,
      allowing support for automatic differentiation in JAX/NumPyro. To ensure compatibility with NUTS/HMC (which
      uses JAX's reverse-mode autodiff), only a fixed set of `alpha_domain_depth` values are supported. See
      `SchechterMag.supported_depths()` for available options (e.g., 3, 5, 10, 15).
    - If `include_poisson_term=True`, the log-likelihood includes:
          log L = Σ log(pdf_shape) + Poisson(N_obs | N_exp)
      where N_exp = volume * normalisation integral over observed magnitudes.
    """

    support = constraints.real

    @property
    def has_rsample(self) -> bool:
        return False
    
    @staticmethod
    def supported_depths():
        """
        Returns a list of supported values for `alpha_domain_depth`, corresponding to increasing valid alpha ranges.
        Larger `alpha_domain_depth` will see reduced performance due to the corresponding increase in recursions.
        """
        return SUPPORTED_ALPHA_DOMAIN_DEPTHS

    def __init__(self, alpha, M_star, logphi, mag_obs,
                 include_poisson_term=False,
                 volume=1.0,
                 alpha_domain_depth=3,
                 validate_args=None):
        # Store input parameters
        self.alpha = alpha
        self.M_star = M_star
        self.logphi = logphi
        self.phi_star = 10.0 ** logphi # convert log10(phi*) to phi*
        self.mag_obs = mag_obs
        self.alpha_domain_depth = alpha_domain_depth
        self.include_poisson_term = include_poisson_term
        self.N_obs = len(mag_obs)
        self.volume = volume

        # Magnitude range of the data
        M_min, M_max = jnp.min(mag_obs), jnp.max(mag_obs)

        # Precompute normalisation over observed magnitude range
        a = alpha + 1.0
        x_min = 10 ** (0.4 * (M_star - M_max)) # faint light
        x_max = 10 ** (0.4 * (M_star - M_min)) # bright light
        norm_shape = LN10_0p4 * self.phi_star * (custom_gammaincc(a, x_min, recur_depth=self.alpha_domain_depth) -
                                                 custom_gammaincc(a, x_max, recur_depth=self.alpha_domain_depth))
        self.norm = jnp.where(norm_shape > 0, norm_shape, jnp.inf) # avoid /0

        super().__init__(batch_shape=(), event_shape=(), validate_args=validate_args)

    def __str__(self):
        return (
            f"SchechterMag distribution\n"
            f"  alpha = {self.alpha}\n"
            f"  M_star = {self.M_star}\n"
            f"  logphi = {self.logphi}\n"
            f"  alpha_domain_depth = {self.alpha_domain_depth}"
        )

    def __repr__(self):
        return str(self)

    def log_prob(self, value):
        # Compute the Schechter PDF (shape only) at given magnitudes
        pdf_shape = LN10_0p4 * schechter_mag(self.phi_star, self.M_star, self.alpha, value) / self.norm
        logp_shape = jnp.log(pdf_shape + 1e-30) # avoid log(0)

        if self.include_poisson_term:
            # Expected total counts for the survey
            N_exp = self.norm * self.volume
            # Add Poisson term for total number counts
            log_poisson = Poisson(N_exp).log_prob(self.N_obs)
            return jnp.sum(logp_shape) + log_poisson
        else:
            # Shape-only likelihood
            return jnp.sum(logp_shape)

    def sample(self, key, sample_shape=()):
        raise NotImplementedError("Sampling not implemented for SchechterMag.")


class DoubleSchechterMag(Distribution):
    """
    NumPyro-compatible distribution based on the double-component Schechter luminosity function in absolute magnitude space.

    This distribution models galaxy number densities using the sum of two Schechter functions:
        φ(M) = φ1(M) + φ2(M)
    with each component of the form:
        φ_i(M) ∝ 10**[0.4(α_i + 1)(M*_i − M)] * exp[−10**(0.4(M*_i − M))]

    Parameters
    ----------
    alpha1, alpha2 : float
        Faint-end slopes of the two Schechter components.
    M_star1, M_star2 : float
        Characteristic magnitudes (M*) of the first and second components.
    logphi1, logphi2 : float
        Logarithm (base 10) of the normalisation φ*_i (number density per unit volume per magnitude)
        for the first and second Schechter components, respectively. Internally converted as
        phi_star_i = 10**logphi_i.
    mag_obs : array-like
        Observed magnitudes used for computing the likelihood.
    include_poisson_term : bool, optional
        If True, includes a Poisson likelihood term on the total observed counts to constrain φ*_i.
    volume : float, optional
        Survey volume, used to scale expected counts for the Poisson term.
        Volume is in the same units as `phi_star_i` (e.g., if `phi_star_i` is per Mpc³ per mag, 
        volume should be in Mpc³).
    alpha_domain_depth : int, optional
        Depth parameter for recurrence-based incomplete gamma calculation (default=3).

    Constraints
    -----------
    - `alpha1` and `alpha2` must be real and non-integer. By default, the valid domain for `alpha_i + 1` is (−3, 3), corresponding
      to `alpha_domain_depth=3`. To support broader domains, increase `alpha_domain_depth` (see note).
    - `mag_obs` must contain values such that `10**(0.4(M*_i − M)) > 0`.

    Notes
    -----
    - Normalisation is handled via a custom, recurrence-based computation of the upper incomplete gamma function,
      allowing support for automatic differentiation in JAX/NumPyro. To ensure compatibility with NUTS/HMC (which
      uses JAX's reverse-mode autodiff), only a fixed set of `alpha_domain_depth` values are supported. See
      `SchechterMag.supported_depths()` for available options (e.g., 3, 5, 10, 15).
    - If `include_poisson_term=True`, the log-likelihood includes:
          log L = Σ log(pdf_shape) + Poisson(N_obs | N_exp)
      where N_exp = volume * (normalisation1 + normalisation2) over observed magnitudes.
    """

    support = constraints.real

    @property
    def has_rsample(self):
        return False

    @staticmethod
    def supported_depths():
        """
        Returns a list of supported values for `alpha_domain_depth`, corresponding to increasing valid alpha ranges.
        Larger `alpha_domain_depth` will see reduced performance due to the corresponding increase in recursions.
        """
        return SUPPORTED_ALPHA_DOMAIN_DEPTHS

    def __init__(self,
                 alpha1, M_star1, logphi1,
                 alpha2, M_star2, logphi2,
                 mag_obs,
                 include_poisson_term=False,
                 volume=1.0,
                 alpha_domain_depth=3,
                 validate_args=None):
        # First Schechter component parameters
        self.alpha1 = alpha1
        self.M_star1 = M_star1
        self.logphi1 = logphi1
        self.phi_star1 = 10.0 ** logphi1

        # Second Schechter component parameters
        self.alpha2 = alpha2
        self.M_star2 = M_star2
        self.logphi2 = logphi2
        self.phi_star2 = 10.0 ** logphi2

        # Data and settings
        self.mag_obs = mag_obs
        self.alpha_domain_depth = alpha_domain_depth
        self.include_poisson_term = include_poisson_term
        self.N_obs = len(mag_obs)
        self.volume = volume

        # Magnitude range of the data
        M_min, M_max = jnp.min(mag_obs), jnp.max(mag_obs)

        # First component normalisation
        a1 = alpha1 + 1.0
        x1_min = 10 ** (0.4 * (M_star1 - M_max))
        x1_max = 10 ** (0.4 * (M_star1 - M_min))
        norm1 = self.phi_star1 * (
            custom_gammaincc(a1, x1_min, recur_depth=alpha_domain_depth) -
            custom_gammaincc(a1, x1_max, recur_depth=alpha_domain_depth)
        )

        # Second component normalisation
        a2 = alpha2 + 1.0
        x2_min = 10 ** (0.4 * (M_star2 - M_max))
        x2_max = 10 ** (0.4 * (M_star2 - M_min))
        norm2 = self.phi_star2 * (
            custom_gammaincc(a2, x2_min, recur_depth=alpha_domain_depth) -
            custom_gammaincc(a2, x2_max, recur_depth=alpha_domain_depth)
        )

        # Combined normalisation for both components
        self.norm = LN10_0p4 * (norm1 + norm2)
        self.norm = jnp.where(self.norm > 0, self.norm, jnp.inf) # avoid /0

        super().__init__(batch_shape=(), event_shape=(), validate_args=validate_args)
    
    def __str__(self):
        return (
            f"DoubleSchechterMag distribution\n"
            f"  alpha1={self.alpha1}, M_star1={self.M_star1}, logphi1={self.logphi1}\n"
            f"  alpha2={self.alpha2}, M_star2={self.M_star2}, logphi2={self.logphi2}\n"
            f"  alpha_domain_depth={self.alpha_domain_depth}"
        )

    def __repr__(self):
        return str(self)

    def log_prob(self, value):
        # Compute PDFs for each component and sum
        phi1 = schechter_mag(self.phi_star1, self.M_star1, self.alpha1, value)
        phi2 = schechter_mag(self.phi_star2, self.M_star2, self.alpha2, value)

        pdf_shape = LN10_0p4 * (phi1 + phi2) / self.norm
        logp_shape = jnp.log(pdf_shape + 1e-30) # avoid log(0)

        if self.include_poisson_term:
            # Expected total counts from both components
            N_exp = self.norm * self.volume
            # Add Poisson term for number counts
            log_poisson = Poisson(N_exp).log_prob(self.N_obs)
            return jnp.sum(logp_shape) + log_poisson
        else:
            # Shape-only likelihood
            return jnp.sum(logp_shape)

    def sample(self, key, sample_shape=()):
        raise NotImplementedError("Sampling not implemented for DoubleSchechterMag.")
