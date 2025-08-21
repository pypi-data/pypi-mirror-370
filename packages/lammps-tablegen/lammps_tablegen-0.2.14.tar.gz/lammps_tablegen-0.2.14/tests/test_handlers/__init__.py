# Shared helpers for handler tests
from itertools import cycle

def patch_inputs(monkeypatch, *values):
    """Monkey-patch builtins.input with a finite list of answers."""
    answers = iter(values)
    monkeypatch.setattr("builtins.input", lambda _: next(answers))

