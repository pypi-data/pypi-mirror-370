import types
from tablegen.handlers import TRUNC3B
from . import patch_inputs

def test_trunc3b_coeff_prompt(monkeypatch):
    # Feed k, rho, theta0 (degrees)
    patch_inputs(monkeypatch, "50", "1.5", "109.5")
    args = types.SimpleNamespace(
        triplets=["O-Si-O"],
        table_name="trunc",
        cutoff=4.0,
        data_points=10
    )
    handler = TRUNC3B(args)
    assert handler.is_2b is False
    assert len(handler.COEFFS) == 1

