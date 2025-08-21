import jax
import jax.numpy as jnp
from jax import lax, jit
from jax.scipy.special import gamma, gammaincc
from jax._src.numpy.util import promote_args_inexact
from jax._src.typing import Array, ArrayLike

jax.config.update("jax_enable_x64", True)

SUPPORTED_ALPHA_DOMAIN_DEPTHS = [3, 4, 5, 6, 7, 8, 9, 10, 15, 20, 30]
LN10_0p4 = 0.4 * jnp.log(10.0)

def schechter_mag(phi_star, M_star, alpha, M):
    """
    Schechter density in magnitude space (unnormalised).
    """
    # M: absolute magnitude
    x = 10 ** (0.4 * (M_star - M))
    return (
        LN10_0p4
        * phi_star
        * x ** (alpha + 1)
        * jnp.exp(-x)
    )


def custom_gammaincc(s: ArrayLike, x: ArrayLike, recur_depth: int = 3) -> Array:
    """
    Computes Γ(s, x) using a recurrence-based method.

    Valid for real, non-integer s. The default supported domain for s is approximately (-3, 3), corresponding to `recur_depth=3`.
    Increase `recur_depth` to extend this range. Input `x` must be positive.

    Raises:
        ValueError: If `recur_depth` is not in the supported set.
    """
    s, x = promote_args_inexact("custom_gammaincc", s, x)
    if recur_depth not in _dispatch_table:
        raise ValueError(f"Unsupported recur_depth={recur_depth}. "
                         f"Must be one of {SUPPORTED_ALPHA_DOMAIN_DEPTHS}.")
    return _dispatch_table[recur_depth](s, x)


def s_positive(s: ArrayLike, x: ArrayLike) -> Array:
    """
    Regularised upper incomplete gamma function * Gamma(s)
    """
    return gamma(s) * gammaincc(s, x)


def compute_gamma(s: ArrayLike, x: ArrayLike, recur_depth: int) -> Array:
    def recur(gamma_val, s, x):
        return (gamma_val - x ** s * jnp.exp(-x)) / s

    def compute_recurrence(carry, _):
        gamma_val, s = carry
        new_s = s - 1
        gamma_val_new = lax.cond(
            jnp.isinf(gamma_val),
            lambda _: jnp.inf,
            lambda _: recur(gamma_val, new_s, x),
            operand=None
        )
        return (gamma_val_new, new_s), gamma_val_new

    s_start = s + recur_depth
    gamma_start = s_positive(s_start, x)

    initial_carry = (gamma_start, s_start)
    result, _ = lax.scan(compute_recurrence, initial_carry, None, length=recur_depth)
    return result[0]


_dispatch_table = {}

for depth in SUPPORTED_ALPHA_DOMAIN_DEPTHS:
    def _make_fn(recur_depth=depth):
        @jit
        def fn(s, x):
            return compute_gamma(s, x, recur_depth)
        return fn

    _dispatch_table[depth] = _make_fn()
