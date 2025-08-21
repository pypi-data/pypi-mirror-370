"""compatibility.types.py

Everything we need to check for compatibility between types of a single parameter or return value.
"""

import collections.abc
import contextlib
import inspect
import logging
from typing import Any, get_args, get_origin

from .exception import SignatureIncompatible


def is_any_or_missing(t: Any) -> bool:
    return (
        t is None
        or t == {"type": "any"}
        or t == {"type": "object"}
        or t == {}
        or t == "any"
        or t == inspect._empty
    )


def get_class_str(d: Any) -> str | None:
    if isinstance(d, dict) and "class" in d:
        val: Any = d["class"]
        if val is not None:
            return val if isinstance(val, str) else str(val)
    return d if isinstance(d, str) else None


def is_subtype(sub: Any, sup: Any) -> bool:
    if is_any_or_missing(sub) or is_any_or_missing(sup):
        return True
    if sub == sup:
        return True
    # Accept class objects directly
    if isinstance(sub, type) and isinstance(sup, type):
        with contextlib.suppress(Exception):
            if issubclass(sub, sup):
                return True
        # Cross-module: compare by class name and walk MROs
        sub_mro = list(getattr(sub, "__mro__", []))
        sup_name = getattr(sup, "__name__", None)
        if sup_name and any(getattr(c, "__name__", None) == sup_name for c in sub_mro):
            return True
    # Fallback: resolve strings via globals
    sub_cls: str | None = get_class_str(sub)
    sup_cls: str | None = get_class_str(sup)
    if sub_cls is not None and sup_cls is not None:
        with contextlib.suppress(Exception):
            sub_type: Any = globals().get(sub_cls)
            sup_type: Any = globals().get(sup_cls)
            if isinstance(sub_type, type) and isinstance(sup_type, type):
                with contextlib.suppress(Exception):
                    if issubclass(sub_type, sup_type):
                        return True
                # Cross-module fallback
                sub_mro = list(getattr(sub_type, "__mro__", []))
                if sup_cls and any(
                    getattr(c, "__name__", None) == sup_cls for c in sub_mro
                ):
                    return True
    return False


def is_supertype(sup: Any, sub: Any) -> bool:
    if is_any_or_missing(sub) or is_any_or_missing(sup):
        return True
    if sup == sub:
        return True
    sup_cls: str | None = get_class_str(sup)
    sub_cls: str | None = get_class_str(sub)
    if sup_cls is not None and sub_cls is not None:
        with contextlib.suppress(Exception):
            sup_type: Any = eval(sup_cls)
            sub_type: Any = eval(sub_cls)
            return issubclass(sub_type, sup_type)
    return False


def is_type_compatible(a, b) -> bool:
    # Unwrap typing.Annotated types to their base type for both a and b
    def unwrap_annotated(t):
        origin = get_origin(t)
        if origin is not None and origin.__name__ == "Annotated":
            args = get_args(t)
            if args:
                return unwrap_annotated(args[0])
        return t

    a = unwrap_annotated(a)
    b = unwrap_annotated(b)
    logging.getLogger(__name__).debug(
        f"Comparing types: a={a!r} (type={type(a)}), b={b!r} (type={type(b)})"
    )
    # T8: Adjacent types | A: uint8 → B: uint16 | ✗ | Behavioral differences matter
    # If both are types, not primitive, not subtypes, and not equal, fail
    if (
        isinstance(a, type)
        and isinstance(b, type)
        and a != b
        and not issubclass(b, a)
        and not issubclass(a, b)
        and a.__name__.startswith("uint")
        and b.__name__.startswith("uint")
    ):
        raise SignatureIncompatible(
            message="Adjacent types (e.g., uint8 vs uint16) are not compatible.",
            context={"A_type": a, "B_type": b},
            suggestion="Use explicit conversion or match types exactly.",
        )
    # T6: Implicit conversion | A: int → B: float | ✗ | No explicit subtype relationship
    primitive_types = {int, float, str, bool}
    if (
        isinstance(a, type)
        and isinstance(b, type)
        and a in primitive_types
        and b in primitive_types
        and a != b
        and not issubclass(b, a)
        and not issubclass(a, b)
    ):
        logging.getLogger(__name__).debug(
            f"Primitive type incompatibility detected: a={a}, b={b}"
        )
        raise SignatureIncompatible(
            message="Implicit conversion between primitive types is not allowed.",
            context={"A_type": a, "B_type": b},
            suggestion="Use explicit conversion or ensure types match exactly.",
        )
    # T0: Untyped/Any → Specific type | A: Any → B: int | ✗ | Type constraint added
    if is_any_or_missing(a) and not is_any_or_missing(b):
        raise SignatureIncompatible(
            message="Untyped/Any parameter cannot be narrowed to a specific type without breaking compatibility.",
            context={"A_type": a, "B_type": b},
            suggestion="Start with a narrow type and explicitely go from there as baseline. There is nothing we can do from here.",
        )
    if is_any_or_missing(b):
        return True
    # | T1 | Same type | A: int → B: int | ✓ | Exact match
    if a == b:
        return True
    # | T2 | Base → Derived (narrowing) | A: Animal → B: Cat | ✗ | New function requires specific subtype
    logging.getLogger(__name__).debug(
        f"a={a!r} b={b!r} a_type={type(a)} b_type={type(b)}"
    )
    try:
        logging.getLogger(__name__).debug(
            f"a.__module__={getattr(a, '__module__', None)!r} b.__module__={getattr(b, '__module__', None)!r}"
        )
    except Exception as e:
        logging.getLogger(__name__).debug(f"T2 DEBUG: error getting __module__: {e}")
    logging.getLogger(__name__).debug(
        f"is_subtype(b, a)={is_subtype(b, a)} is_subtype(a, b)={is_subtype(a, b)}"
    )
    # Disallow narrowing: base → derived (A: Animal → B: Cat)
    if (
        isinstance(a, type)
        and isinstance(b, type)
        and a != b
        and is_subtype(a, b)  # a is subclass of b (derived → base, widening) is OK
        and not is_subtype(b, a)  # b is not subclass of a (so not narrowing)
    ):
        return True
    # If b is subclass of a and not equal, that's narrowing (base → derived), disallow
    if is_subtype(b, a) and a != b:
        raise SignatureIncompatible(
            message="Cannot narrow parameter type from base to derived (contravariant narrowing).",
            context={"A_type": a, "B_type": b},
            suggestion="Relax the target type to the base type or use a union type to allow all valid inputs.",
        )
    # If neither is a subtype of the other, but both are ABCs or unrelated, allow if not narrowing
    if (
        isinstance(a, type)
        and isinstance(b, type)
        and a != b
        and not is_subtype(a, b)
        and not is_subtype(b, a)
    ):
        # Allow if both are ABCs or unrelated (e.g., Integral → Real), as per T7
        import numbers

        abc_types = (numbers.Integral, numbers.Real, numbers.Number)
        # Accept if both are ABCs and a is a subclass of b (contravariant acceptance)
        with contextlib.suppress(Exception):
            if issubclass(a, abc_types) and issubclass(b, abc_types):
                if issubclass(a, b):
                    return True
                # Allow if a's MRO contains a class with the same name as b or any of b's ancestors (for ABCs across modules)
                b_names = {
                    getattr(cls, "__name__", None) for cls in getattr(b, "__mro__", [])
                }
                a_mro_names = {
                    getattr(cls, "__name__", None) for cls in getattr(a, "__mro__", [])
                }
                if b_names & a_mro_names:
                    return True
        # Otherwise, incompatible
        raise SignatureIncompatible(
            message="Incompatible parameter types: neither is a subtype of the other (narrowing not allowed).",
            context={"A_type": a, "B_type": b},
            suggestion="Ensure the target type is the same or a supertype of the source type.",
        )

    # T3: Interface → Concrete | A: Sized → B: list | ✗ | Implementation restricts valid inputs
    # If A is an ABC/protocol/interface and B is a concrete type, and B is not a subtype of A, fail
    if (
        isinstance(a, type)
        and hasattr(collections.abc, a.__name__)
        and isinstance(b, type)
        and not issubclass(b, a)
    ):
        raise SignatureIncompatible(
            message="Interface/ABC cannot be replaced by a concrete type unless it is a subtype.",
            context={"A_type": a, "B_type": b},
            suggestion="Use a protocol or ABC as the target type, or ensure the concrete type is a valid subtype.",
        )

    # | T3 | Interface → Concrete | A: Sized → B: list | ✗ | Implementation restricts valid inputs
    # | T4 | Type → Wider union | A: int → B: int|str | ✓ | Accepts original type + more
    # | T5 | Required → Optional | A: int → B: int|None | ✓ | Original callers already pass required type
    # | T6 | Implicit conversion | A: int → B: float | ✗ | No explicit subtype relationship
    # | T7 | ABC hierarchy | A: Integral → B: Real | ✓ | Explicit subtyping via ABCs
    # | T8 | Adjacent types | A: uint8 → B: uint16 | ✗ | Behavioral differences matter
    # | T9 | Derived → Base (widening) | A: Cat → B: Animal | ✓ | Contravariant parameter acceptance
    # | T10 | Container invariance | A: list[int] → B: list[str] | ✗ | Generic parameters invariant
    # | T11 | Container contravariance | A: list[Dog] → B: list[Animal] | ✓ | List of Dog is compatible with list of Animal

    # Handle union types (e.g., int|str)
    if isinstance(b, str) and "|" in b:
        b_types = [t.strip() for t in b.split("|")]
        # Accept if a_type matches any type in the union or is subtype
        for bt in b_types:
            if is_type_compatible(a, bt):
                return True
        # Optionals: None in union
        return a == "None" and "None" in b_types
    # Optionals: e.g., int|None
    if isinstance(b, str) and b.endswith("|None"):
        base_type = b[:-5]
        if is_type_compatible(a, base_type) or a == "None":
            return True

    # Container types: e.g., list[int], dict[str, int]
    import types

    def parse_container(t):
        # Handle Python 3.9+ generics (e.g., list[int])
        if isinstance(t, types.GenericAlias):
            base = t.__origin__
            args = t.__args__
            return base, args
        # Handle string-based generics (legacy)
        if not isinstance(t, str) or "[" not in t or not t.endswith("]"):
            return t, None
        base, inner = t.split("[", 1)
        inner = inner[:-1]
        parts = []
        depth = 0
        buf = ""
        for c in inner:
            if c == "," and depth == 0:
                parts.append(buf.strip())
                buf = ""
            else:
                if c == "[":
                    depth += 1
                elif c == "]":
                    depth -= 1
                buf += c
        if buf:
            parts.append(buf.strip())
        return base.strip(), parts

    a_base, a_args = parse_container(a)
    b_base, b_args = parse_container(b)
    # T10: Container invariance (list[int] vs list[str])
    if a_args and b_args:
        if a_base != b_base or len(a_args) != len(b_args):
            raise SignatureIncompatible(
                message="Container types must match exactly (invariant).",
                context={"A_type": a, "B_type": b},
                suggestion="Ensure container base types and all type arguments match exactly.",
            )
        for aa, ba in zip(a_args, b_args):
            if not is_type_compatible(aa, ba):
                raise SignatureIncompatible(
                    message="Container type arguments must match exactly (invariant).",
                    context={"A_type": aa, "B_type": ba},
                    suggestion="Ensure all container type arguments match exactly.",
                )
        return True
    # T11: Container contravariance (list[Dog] vs list[Animal])
    # Accept if a_args and b_args, and each a_arg is subtype of b_arg
    if a_args and b_args and (a_base == b_base and len(a_args) == len(b_args)):
        for aa, ba in zip(a_args, b_args):
            if not (is_type_compatible(aa, ba) or is_subtype(aa, ba)):
                return False
        return True

    return True
