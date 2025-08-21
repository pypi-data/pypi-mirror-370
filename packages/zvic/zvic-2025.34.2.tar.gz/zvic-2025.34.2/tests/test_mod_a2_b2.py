# type: ignore

from pathlib import Path

import pytest

from zvic import load_module
from zvic.compatibility import is_compatible
from zvic.compatibility_params import SignatureIncompatible

mod_a2_path = Path(__file__).parent / "stuff" / "mod_a2.py"
mod_b2_path = Path(__file__).parent / "stuff" / "mod_b2.py"

mod_a2 = load_module(mod_a2_path, "mod_a2")
mod_b2 = load_module(mod_b2_path, "mod_b2")


def test_method_addition():
    # MyClassB_Add has an extra method 'baz' not present in MyClassA
    # Should be compatible (addition is allowed)
    is_compatible(mod_a2.MyClassA, mod_b2.MyClassB_Add)


def test_method_removal():
    # MyClassB_Remove is missing 'bar' present in MyClassA
    # Should be incompatible (removal is not allowed)
    with pytest.raises(SignatureIncompatible):
        is_compatible(mod_a2.MyClassA, mod_b2.MyClassB_Remove)
