import types
from tablegen.handlers import BUCK_EXT
from . import patch_inputs

def test_buck_ext_coeff_prompt(monkeypatch):
    # Feed A, rho, C, D
    patch_inputs(monkeypatch, "1000", "0.3", "10", "0.1")
    args = types.SimpleNamespace(
        pairs=["Na-O"],
        table_name="buck_ext.table",
        plot=False,
        cutoff=10.0,
        data_points=50
    )
    handler = BUCK_EXT(args)
    assert len(handler.COEFFS) == 1

