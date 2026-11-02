"""The orbit returned by refinement must be the orbit whose objective was evaluated."""
import importlib.util
from pathlib import Path

import numpy as np
import pytest


@pytest.mark.parametrize("start_e, optimum_e", [(-0.1, 0.0), (1.1, 0.99)])
def test_refine_returns_eccentricity_used_in_objective(start_e, optimum_e):
    spec = importlib.util.spec_from_file_location(
        "validation", Path(__file__).resolve().parents[1] / "scripts/check_transit_bootstrap.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    nb = module.notebook_functions()
    # A known minimum at the eccentricity boundary; keep SciPy's real optimiser.
    nb["chi2"] = lambda s, q: (q[0] - 1)**2 + (q[1] - optimum_e)**2 + q[2]**2
    q = nb["refine"](None, [1.0, start_e, 0.0])
    assert 0 <= q[1] <= 0.99
    np.testing.assert_allclose(q, [1, optimum_e, 0], atol=1e-7)
