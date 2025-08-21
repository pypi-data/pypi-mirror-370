import types
from tablegen.handlers import BUCK
from . import patch_inputs

def test_buck_coeff_prompt(monkeypatch):
    # Feed A, rho, C once (only one unique pair)
    patch_inputs(monkeypatch, "1000", "0.3", "10")
    args = types.SimpleNamespace(
        pairs=["Si-O"],
        table_name="buck.table",
        plot=False,
        cutoff=10.0,
        data_points=50
    )
    handler = BUCK(args)
    assert len(handler.COEFFS) == 1

