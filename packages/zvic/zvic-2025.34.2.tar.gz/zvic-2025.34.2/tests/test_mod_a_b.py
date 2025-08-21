from pathlib import Path

import zvic.main

a_mod = zvic.main.load_module(Path("stuff/mod_a1.py"), "mod_a1")
b_mod = zvic.main.load_module(Path("stuff/mod_b1.py"), "mod_b1")

try:
    result = zvic.main.is_compatible(a_mod, b_mod)
    print(f"mod_b1 is compatible with mod_a1: {result}")
except Exception as e:
    print(e)
