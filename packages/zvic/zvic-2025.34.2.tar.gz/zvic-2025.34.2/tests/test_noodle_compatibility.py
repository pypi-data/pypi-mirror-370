# type: ignore

from pathlib import Path

import pytest

from zvic import load_module
from zvic.compatibility import is_compatible
from zvic.compatibility_params import SignatureIncompatible

mod_a_path = Path(__file__).parent / "stuff" / "mod_a.py"
mod_b_path = Path(__file__).parent / "stuff" / "mod_b.py"

mod_a = load_module(mod_a_path, "mod_a")
mod_b = load_module(mod_b_path, "mod_b")


def test_noodle_compatibility():
    with pytest.raises(SignatureIncompatible):
        is_compatible(mod_a.Noodle, mod_b.Noodle)
