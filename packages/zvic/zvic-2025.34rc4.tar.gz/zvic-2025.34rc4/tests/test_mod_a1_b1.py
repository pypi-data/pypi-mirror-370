# type: ignore

from pathlib import Path

import pytest

from zvic import load_module
from zvic.compatibility import is_compatible
from zvic.compatibility_params import SignatureIncompatible

mod_a1_path = Path(__file__).parent / "stuff" / "mod_a1.py"
mod_b1_path = Path(__file__).parent / "stuff" / "mod_b1.py"

mod_a1 = load_module(mod_a1_path, "mod_a1")
mod_b1 = load_module(mod_b1_path, "mod_b1")


def test_inherit_a_foo():
    with pytest.raises(SignatureIncompatible):
        is_compatible(mod_a1.InheritA.foo, mod_b1.InheritA.foo)
