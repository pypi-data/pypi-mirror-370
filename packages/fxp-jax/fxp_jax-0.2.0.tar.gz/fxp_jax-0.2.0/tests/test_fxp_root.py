import jax
import jax.numpy as jnp
from jax import random

from fxp_jax import fxp_root

import pytest

# Increase precision to 64 bit
jax.config.update("jax_enable_x64", True)

@pytest.mark.parametrize("N, accelerator", [
    (1000, "None"),
    (1000, "SQUAREM"),
]) 

def test_FixedPointRoot(N: int, accelerator: str):

    a = random.uniform(random.PRNGKey(111), (N,1))
    b = random.uniform(random.PRNGKey(112), (1,1))

    def fun(x: jnp.ndarray) -> tuple[jnp.ndarray, jnp.ndarray]:
        y = a + x @ b
        return y, y - x

    fxp = fxp_root(
        fun,
    )
    result = fxp.solve(guess=jnp.zeros_like(a), accelerator=accelerator)

    assert jnp.allclose(result.x, fxp.fun(result.x)[0]), f"Error: {jnp.linalg.norm(fxp.fun(result.x)[1])}"