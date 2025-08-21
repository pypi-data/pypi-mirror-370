import types
import pytest
from tablegen.handlers import SHIK

@pytest.fixture
def dummy_args(tmp_path):
    # Create a minimal LAMMPS "Atoms" style file to satisfy get_oxygen_charge
    atoms = tmp_path / "dummy.lmp"
    atoms.write_text("Header\nAtoms # charge\n\n1 1 0 0 0 0\n")
    return types.SimpleNamespace(
        structure_file=str(atoms),
        species=["Si", "O"],
        cutoff=10.0, wolf_cutoff=8.0, buck_cutoff=6.0,
        gamma=0.2, data_points=100, table_name="test.table",
        plot=False
    )

def test_shik_instantiates(monkeypatch, dummy_args):
    # Avoid parsing the real file – just stub the charge method.
    monkeypatch.setattr("tablegen.handlers.shik.SHIK.get_oxygen_charge",
                        lambda self, _: -1.0)
    handler = SHIK(dummy_args)
    assert handler.is_2b is True
    assert set(handler.SPECIES) == {"Si", "O"}

