import ast
import inspect
import sys
from pathlib import Path
from types import ModuleType
from typing import Any, Mapping, get_args, get_origin, get_type_hints

from .annotation_constraints import AnnotateCallsTransformer
from .utils import _, assumption, normalize_constraint

# More permissive canonical type to match function/class representations
CANONICAL = Mapping[str, Any]


def constrain_this_module():
    """Rewrites the current module in-place with annotation constraints."""
    frame = inspect.currentframe()
    if frame is None or frame.f_back is None:
        raise RuntimeError("Could not find caller frame")
    caller_globals = frame.f_back.f_globals

    if "_" not in caller_globals:
        caller_globals["_"] = _
    # Inject zvic.utils.assumption into caller's globals if not already present
    if "assumption" not in caller_globals:
        caller_globals["assumption"] = assumption

    # Prevent recursion: only transform if not already transformed
    if caller_globals.get("__zvic_transformed__", False):
        return
    caller_globals["__zvic_transformed__"] = True
    filename = caller_globals["__file__"]
    with open(filename, "r", encoding="utf-8") as f:
        source = f.read()

    assert source.startswith(
        "from __future__ import annotations"
    ) and sys.version_info < (3, 13), (
        f"ZVIC requires 'from __future__ import annotations' in {filename} for advanced annotation constraints on Python < 3.13. Please add it at the top of your module."
    )
    tree = ast.parse(source, filename=filename)
    transformer = AnnotateCallsTransformer()
    new_tree = transformer.visit(tree)
    ast.fix_missing_locations(new_tree)
    code = compile(new_tree, filename, "exec")
    exec(code, caller_globals)
    return ast.unparse(new_tree)


def load_module(path: Path, module_name: str) -> ModuleType:
    original_source = path.read_text(encoding="utf-8")
    tree = ast.parse(original_source, filename=str(path))

    transformer = AnnotateCallsTransformer()
    transformed_tree = transformer.visit(tree)
    transformed_tree: ast.Module = transformer.visit_Module(transformed_tree)  # type: ignore
    ast.fix_missing_locations(transformed_tree)
    assert assumption(transformed_tree, ast.Module)
    code = compile(transformed_tree, str(path), "exec")

    mod = ModuleType(module_name)
    mod.__dict__["__file__"] = str(path)
    exec(code, mod.__dict__)

    setattr(mod, "__original_source__", original_source)

    canonical = canonicalize(mod)
    setattr(mod, "_zvic_canonical", canonical)
    assert assumption(mod, ModuleType)
    return mod


def canonicalize(obj: Any) -> CANONICAL:
    """
    Canonicalize any object using the type normalization layer.
    For a module, returns a dict mapping names to canonicalized signatures/types.
    For a function or class, returns its canonical signature/type.
    For other objects, returns their normalized type.
    """
    if isinstance(obj, ModuleType):
        # Only include user-defined functions and classes (exclude built-ins, imports, and typing helpers)
        result: CANONICAL = {}
        for attr_name, attr in vars(obj).items():
            if attr_name == "Annotated":
                continue
            # If it's a function, represent as a dict with a single '__call__' field
            if (
                inspect.isfunction(attr)
                and getattr(attr, "__module__", None) == obj.__name__
            ):
                result[attr_name] = {"__call__": canonical_signature(attr)}
            # If it's a class, represent as its methods and __call__
            elif (
                inspect.isclass(attr)
                and getattr(attr, "__module__", None) == obj.__name__
            ):
                result[attr_name] = canonicalize(attr)
        return result
    elif inspect.isclass(obj):
        result: CANONICAL = {}
        # If the class is callable (has a custom __call__), represent it by its __call__
        call_method = obj.__dict__.get("__call__")
        if call_method and inspect.isfunction(call_method):
            result["__call__"] = canonical_signature(call_method)
        # Also include other user-defined methods (excluding __call__ and dunder methods)
        for name, member in vars(obj).items():
            if name.startswith("__") and name != "__call__":
                continue
            if name == "__call__":
                continue
            if inspect.isfunction(member):
                result[name] = canonical_signature(member)
            elif isinstance(member, staticmethod):
                result[name] = canonical_signature(member.__func__)
            elif isinstance(member, classmethod):
                result[name] = canonical_signature(member.__func__)
        return result
    elif callable(obj):
        # For any other callable (including functions), represent as a dict with a single '__call__' field
        call_method = getattr(obj, "__call__", None)
        result: CANONICAL = {}
        if call_method and inspect.ismethod(call_method):
            result["__call__"] = canonical_signature(call_method)
        elif call_method and inspect.isfunction(call_method):
            result["__call__"] = canonical_signature(call_method)
        else:
            result["__call__"] = canonical_signature(obj)
        return result
    else:
        return canonical_signature(obj)


def canonical_signature(func: Any, name: str | None = None) -> CANONICAL:
    sig = inspect.signature(func)

    def strip_typing_prefix(s: str) -> str:
        return s.replace("typing.", "") if s.startswith("typing.") else s

    positional_only: list[dict[str, Any]] = []
    positional_or_keyword: list[dict[str, Any]] = []
    keyword_only: list[dict[str, Any]] = []
    # Use runtime type hints for robust Annotated extraction
    try:
        type_hints = get_type_hints(func, include_extras=True)
    except Exception:
        type_hints = {}
    for param in sig.parameters.values():
        param_info = {}
        ann = type_hints.get(param.name, param.annotation)
        origin = get_origin(ann)
        args = get_args(ann)
        if origin is not None and origin.__name__ == "Annotated" and len(args) >= 2:
            base_type = args[0]
            if hasattr(base_type, "__name__"):
                param_info["type"] = base_type.__name__
            else:
                param_info["type"] = strip_typing_prefix(str(base_type))
            param_info["constraint"] = normalize_constraint(str(args[1]))
        elif ann != inspect.Signature.empty:
            if hasattr(ann, "__module__") and ann.__module__ == "typing":
                param_info["type"] = strip_typing_prefix(str(ann))
            elif hasattr(ann, "__name__"):
                param_info["type"] = ann.__name__
            else:
                param_info["type"] = str(ann)
        else:
            param_info["type"] = None
        if param.kind in (
            inspect.Parameter.POSITIONAL_OR_KEYWORD,
            inspect.Parameter.KEYWORD_ONLY,
        ):
            param_info["name"] = param.name
        if param.default != inspect.Signature.empty:
            param_info["default"] = param.default
        if param.kind == inspect.Parameter.POSITIONAL_ONLY:
            positional_only.append(param_info)
        elif param.kind == inspect.Parameter.POSITIONAL_OR_KEYWORD:
            positional_or_keyword.append(param_info)
        elif param.kind == inspect.Parameter.KEYWORD_ONLY:
            keyword_only.append(param_info)
    # Remove 'type' field if it is None
    for plist in (positional_only, positional_or_keyword, keyword_only):
        for p in plist:
            if "type" in p and p["type"] is None:
                del p["type"]
    keyword_only = sorted(keyword_only, key=lambda p: p["name"])
    params: dict[str, list[dict[str, Any]]] = {
        "positional_only": positional_only,
        "positional_or_keyword": positional_or_keyword,
        "keyword_only": keyword_only,
    }
    # Handle return type using runtime type hints
    try:
        return_ann = type_hints.get("return", sig.return_annotation)
    except Exception:
        return_ann = sig.return_annotation
    return_info = {}
    origin = get_origin(return_ann)
    args = get_args(return_ann)
    if origin is not None and origin.__name__ == "Annotated" and len(args) >= 2:
        base_type = args[0]
        if hasattr(base_type, "__name__"):
            return_info["type"] = base_type.__name__
        else:
            return_info["type"] = strip_typing_prefix(str(base_type))
        return_info["constraint"] = normalize_constraint(str(args[1]))
    elif return_ann != inspect.Signature.empty:
        if hasattr(return_ann, "__module__") and return_ann.__module__ == "typing":
            return_info["type"] = strip_typing_prefix(str(return_ann))
        elif hasattr(return_ann, "__name__"):
            return_info["type"] = return_ann.__name__
        else:
            return_info["type"] = str(return_ann)
    else:
        return_info["type"] = None
    if return_info.get("type") == "None":
        return_info["type"] = None
    # Remove 'type' field from return if it is None
    if "type" in return_info and return_info["type"] is None:
        del return_info["type"]
    return {
        "params": params,
        "return": return_info,
    }


def pprint_recursive(obj, indent=0):
    prefix = " " * indent
    if isinstance(obj, dict):
        for k, v in obj.items():
            print(f"{prefix}{k}:")
            pprint_recursive(v, indent + 2)
    elif isinstance(obj, (list, tuple, set)):
        for v in obj:
            if isinstance(v, dict):
                print(f"{prefix}-")
                pprint_recursive(v, indent + 2)
            else:
                print(f"{prefix}- {v}")
    else:
        print(f"{prefix}{obj}")
