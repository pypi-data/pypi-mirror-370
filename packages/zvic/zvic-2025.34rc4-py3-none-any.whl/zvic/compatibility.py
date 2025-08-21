import inspect
import logging
import types
from enum import Enum
from inspect import signature
from typing import Any, Callable, cast

from .compatibility_constraints import is_constraint_compatible
from .compatibility_params import are_params_compatible
from .compatibility_types import is_type_compatible
from .exception import SignatureIncompatible
from .utils import prepare_params


def is_compatible(a, b):
    """
    Recursively checks any given object for ZVIC compatibility - signature, types and constraints.
    """

    # If both are modules, treat their public interface as the set of all public attributes (callable and non-callable)
    if isinstance(a, types.ModuleType) and isinstance(b, types.ModuleType):

        def get_public_interface(mod):
            # If module defines __all__, that explicitly declares the public
            # interface; otherwise, fall back to the rule 'names not
            # starting with underscore'. Use vars(mod) to get the actual
            # attributes available.
            mod_vars = vars(mod)
            if "__all__" in mod_vars and isinstance(mod_vars["__all__"], (list, tuple)):
                return {
                    name: mod_vars[name]
                    for name in mod_vars["__all__"]
                    if name in mod_vars
                }
            return {
                name: member
                for name, member in mod_vars.items()
                if not name.startswith("_")
            }

        a_public = get_public_interface(a)
        b_public = get_public_interface(b)
        missing = set(a_public) - set(b_public)
        if missing:
            raise SignatureIncompatible(
                f"Public attributes missing in {b.__name__}: {sorted(missing)}"
            )
        # For callables, check signature compatibility
        logger = logging.getLogger(__name__)
        for name in sorted(a_public):
            if name in b_public:
                a_val = a_public[name]
                b_val = b_public[name]
                if (
                    inspect.isfunction(a_val)
                    or inspect.isclass(a_val)
                    or callable(a_val)
                ) and (
                    inspect.isfunction(b_val)
                    or inspect.isclass(b_val)
                    or callable(b_val)
                ):
                    logger.debug(f"Recursively comparing module callable: {name}")
                    is_compatible(a_val, b_val)
        return None
    # If both are classes, recursively check all user-defined methods
    if inspect.isclass(a) and inspect.isclass(b):

        def get_methods(cls):
            methods = {}
            for name, member in vars(cls).items():
                if (
                    inspect.isfunction(member)
                    or isinstance(member, (staticmethod, classmethod))
                ) and not (name.startswith("__") and name != "__init__"):
                    # Unwrap descriptors: staticmethod and classmethod store the
                    # underlying function in the __func__ attribute in the class
                    # dict. Use that so inspect.signature() receives a plain
                    # function object (callable) rather than the descriptor.
                    if isinstance(member, (staticmethod, classmethod)):
                        methods[name] = member.__func__
                    else:
                        methods[name] = member
            return methods

        a_methods = get_methods(a)
        b_methods = get_methods(b)
        # If both classes are Enum subclasses, ensure their members match
        # including order. Enum.__members__ is an ordered mapping of member
        # names in definition order.
        if issubclass(a, Enum) and issubclass(b, Enum):
            a_members = list(getattr(a, "__members__", {}).keys())
            b_members = list(getattr(b, "__members__", {}).keys())
            # Require that all members present in A also exist in B, but do
            # not enforce any specific ordering. B may add new members anywhere
            # in the definition order. For existing names, enforce value
            # stability so numeric/encoded values clients depend on don't
            # silently change.
            a_set = set(a_members)
            b_set = set(b_members)
            missing = a_set - b_set
            if missing:
                raise SignatureIncompatible(
                    f"Enum members missing in {b.__name__}: {sorted(missing)} (a={a_members}, b={b_members})"
                )
            a_map = getattr(a, "__members__", {})
            b_map = getattr(b, "__members__", {})
            for name in a_members:
                a_val = a_map[name].value
                b_val = b_map[name].value
                if a_val != b_val:
                    raise SignatureIncompatible(
                        f"Enum member value changed for {a.__name__}.{name}: a.value={a_val!r}, b.value={b_val!r}"
                    )
        # Always check __init__ if present in both
        logger = logging.getLogger(__name__)
        if hasattr(a, "__init__") and hasattr(b, "__init__"):
            logger.debug(f"Recursively comparing constructor: {a.__name__}.__init__")
            is_compatible(a.__init__, b.__init__)
        # Always check __call__ if present in both
        if (
            hasattr(a, "__call__")
            and hasattr(b, "__call__")
            and (
                a.__call__ is not object.__call__ and b.__call__ is not object.__call__
            )
        ):
            logger.debug(f"Recursively comparing callable: {a.__name__}.__call__")
            is_compatible(a.__call__, b.__call__)
        # Check for missing methods in B (excluding __init__)
        missing_methods = set(a_methods) - set(b_methods)
        if missing_methods:
            raise SignatureIncompatible(
                f"Methods missing in {b.__name__}: {sorted(missing_methods)}"
            )

        # Also check for missing public class attributes (constants, enum
        # members, etc.) that aren't methods. Treat names not starting with
        # an underscore as public.
        def get_public_attrs(cls):
            attrs = set()
            for name, member in vars(cls).items():
                if name.startswith("_"):
                    continue
                # skip methods we've already considered
                if name in a_methods:
                    continue
                attrs.add(name)
            return attrs

        a_attrs = get_public_attrs(a)
        b_attrs = get_public_attrs(b)
        missing_attrs = a_attrs - b_attrs
        if missing_attrs:
            raise SignatureIncompatible(
                f"Attributes missing in {b.__name__}: {sorted(missing_attrs)}"
            )
        # Recursively check all user-defined methods present in both (excluding __init__)
        common_methods = set(a_methods) & set(b_methods)
        for mname in sorted(common_methods):
            if mname == "__init__":
                continue
            a_m = a_methods[mname]
            b_m = b_methods[mname]
            logger.debug(f"Recursively comparing method: {a.__name__}.{mname}")
            is_compatible(a_m, b_m)
        return None

    logging.getLogger(__name__).debug(
        f"Comparing: a_func={a} ({getattr(a, '__qualname__', '')}), b_func={b} ({getattr(b, '__qualname__', '')})"
    )
    # Check for sync/async and generator/non-generator mismatch
    if inspect.isfunction(a) and inspect.isfunction(b):
        a_is_async = inspect.iscoroutinefunction(a)
        b_is_async = inspect.iscoroutinefunction(b)
        if a_is_async != b_is_async:
            raise SignatureIncompatible(
                f"Function async/sync mismatch: a is {'async' if a_is_async else 'sync'}, b is {'async' if b_is_async else 'sync'}"
            )
        a_is_gen = inspect.isgeneratorfunction(a)
        b_is_gen = inspect.isgeneratorfunction(b)
        if a_is_gen != b_is_gen:
            raise SignatureIncompatible(
                f"Function generator/non-generator mismatch: a is {'generator' if a_is_gen else 'regular'}, b is {'generator' if b_is_gen else 'regular'}"
            )

    def _safe_signature(obj: object):
        """Return inspect.signature(obj) while narrowing the type for static checkers.

        We cast to Callable[..., Any] because inspect.signature accepts callables
        and mypy/pyright complain when the static type includes e.g. ModuleType.
        """
        if isinstance(obj, types.ModuleType):
            # Modules should have been handled earlier; treat this as an error
            raise SignatureIncompatible(f"Cannot take signature of module: {obj!r}")
        return signature(cast(Callable[..., Any], obj))

    a_sig = _safe_signature(a)
    b_sig = _safe_signature(b)
    are_params_compatible(a_sig, b_sig)
    a_params = prepare_params(a_sig, a)
    b_params = prepare_params(b_sig, b)

    # Check positional-only
    for a_p, b_p in zip(a_params.posonly, b_params.posonly):
        is_type_compatible(a_p["type"], b_p["type"])
        is_constraint_compatible(a_p, b_p)

    # Check positional-or-keyword
    for a_p, b_p in zip(a_params.pos_or_kw, b_params.pos_or_kw):
        is_type_compatible(a_p["type"], b_p["type"])
        is_constraint_compatible(a_p, b_p)

    # Check keyword-only
    for a_p, b_p in zip(a_params.kwonly, b_params.kwonly):
        is_type_compatible(a_p["type"], b_p["type"])
        is_constraint_compatible(a_p, b_p)

    return None
