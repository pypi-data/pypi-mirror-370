import ast
import logging
import textwrap

from .exception import SignatureIncompatible


def is_constraint_compatible(a_param, b_param):
    """
    Returns True if constraints are compatible, else raises SignatureIncompatible.
    Assumes a_param and b_param are parameter dicts from prepare_params.
    """
    a_con = a_param.get("constraint")
    b_con = b_param.get("constraint")
    # If B has no constraint, it's permissive (covers both neither-has and only-A-has cases)
    if not b_con:
        return
    # If only B has a constraint (A does not), this is NOT compatible (B is more restrictive)
    if not a_con:
        raise SignatureIncompatible(
            f"B adds constraint for parameter {a_param.get('name')}: {b_con}"
        )
    # Both have constraints at this point; check whether B is at least as permissive as A.
    # We prefer to use the optional CrossHair analyser when available.
    # Build the small function to hand to CrossHair. Use an f-string for clarity.
    # Replace placeholder '_' with a variable name and escape any triple-double-quotes
    # so embedding into a triple-double-quoted docstring is safe.
    a_code = a_con.replace("_", "x").replace('"""', '\\"""')
    b_code = b_con.replace("_", "x").replace('"""', '\\"""')

    # Quick AST-based heuristic early: detect simple numeric narrowing (e.g. x < 20 -> x < 10)
    def _simple_narrowing(a_expr: str, b_expr: str) -> bool:
        try:
            a_node = ast.parse(a_expr, mode="eval").body
            b_node = ast.parse(b_expr, mode="eval").body
        except Exception:
            return False

        if not (isinstance(a_node, ast.Compare) and isinstance(b_node, ast.Compare)):
            return False
        if len(a_node.comparators) != 1 or len(b_node.comparators) != 1:
            return False
        if not (
            isinstance(a_node.left, ast.Name) and isinstance(b_node.left, ast.Name)
        ):
            return False
        if a_node.left.id != b_node.left.id:
            return False

        a_op = type(a_node.ops[0])
        b_op = type(b_node.ops[0])
        a_val = a_node.comparators[0]
        b_val = b_node.comparators[0]
        if not (isinstance(a_val, ast.Constant) and isinstance(b_val, ast.Constant)):
            return False
        if not (
            isinstance(a_val.value, (int, float))
            and isinstance(b_val.value, (int, float))
        ):
            return False

        a_num = a_val.value
        b_num = b_val.value

        if a_op is b_op:
            if a_op is ast.Lt or a_op is ast.LtE:
                return b_num < a_num
            if a_op is ast.Gt or a_op is ast.GtE:
                return b_num > a_num
        return False

    if _simple_narrowing(a_code, b_code):
        raise SignatureIncompatible(
            f"Constraint mismatch for parameter {a_param.get('name')}: {a_con} vs {b_con} (B is narrower and thus incompatible: some inputs that A accepts will not be accepted by B)"
        )
    func_code = textwrap.dedent(
        f"""\
        def _chk(x: int):
            \"""
            pre: {b_code}
            \"""
            assert not ({a_code})
            return True
        """
    )

    try:
        # Import the runner lazily so the module does not fail to import when
        # CrossHair support is not installed.
        from .crosshair_subprocess import run_crosshair_on_code

        crosshair_result = run_crosshair_on_code(func_code, "_chk")
        # crosshair_result: True => no counterexample found (OK)
        #                   False => counterexample found (B is narrower)
        #                   None => CrossHair could not analyse (treat as unknown)
        if crosshair_result is True:
            return
        if crosshair_result is False:
            raise SignatureIncompatible(
                f"Constraint mismatch for parameter {a_param.get('name')}: {a_con} vs {b_con} (B is narrower and thus incompatible: some inputs that A accepts will not be accepted by B)"
            )
        # If CrossHair returned None (unable to analyse), try a tiny AST-based
        # heuristic for simple numeric bounds like `x < 20` vs `x < 10`.
        if crosshair_result is None:

            def _simple_narrowing(a_expr: str, b_expr: str) -> bool:
                """Return True if b_expr is a strictly narrower numeric bound than a_expr.

                Only supports simple forms like `x < CONST` / `x <= CONST` / `x > CONST` / `x >= CONST`.
                """
                try:
                    a_node = ast.parse(a_expr, mode="eval").body
                    b_node = ast.parse(b_expr, mode="eval").body
                except Exception:
                    return False

                # Ensure both are simple Compare nodes with single comparator and a Name left
                if not (
                    isinstance(a_node, ast.Compare) and isinstance(b_node, ast.Compare)
                ):
                    return False
                if len(a_node.comparators) != 1 or len(b_node.comparators) != 1:
                    return False
                if not (
                    isinstance(a_node.left, ast.Name)
                    and isinstance(b_node.left, ast.Name)
                ):
                    return False
                # name must match variable used after replacement; we've been using 'x'
                if a_node.left.id != b_node.left.id:
                    return False

                a_op = type(a_node.ops[0])
                b_op = type(b_node.ops[0])
                a_val = a_node.comparators[0]
                b_val = b_node.comparators[0]
                if not (
                    isinstance(a_val, ast.Constant) and isinstance(b_val, ast.Constant)
                ):
                    return False
                if not (
                    isinstance(a_val.value, (int, float))
                    and isinstance(b_val.value, (int, float))
                ):
                    return False

                a_num = a_val.value
                b_num = b_val.value

                # Only handle same-operator numeric comparisons
                if a_op is b_op:
                    # For less-than styles, smaller RHS is narrower
                    if a_op is ast.Lt or a_op is ast.LtE:
                        return b_num < a_num
                    if a_op is ast.Gt or a_op is ast.GtE:
                        return b_num > a_num
                return False

            if _simple_narrowing(a_code, b_code):
                raise SignatureIncompatible(
                    f"Constraint mismatch for parameter {a_param.get('name')}: {a_con} vs {b_con} (B is narrower and thus incompatible: some inputs that A accepts will not be accepted by B)"
                )

        # Unknown to CrossHair and heuristic didn't detect narrowing; treat as permissive
        logging.getLogger(__name__).debug(
            "CrossHair could not analyse constraint for %s; treating as compatible: A=%r B=%r",
            a_param.get("name"),
            a_con,
            b_con,
        )
        return
    except Exception as e:
        # If CrossHair is not available or failed, log and treat constraints as permissive
        logging.getLogger(__name__).debug(
            "CrossHair unavailable or failed to run for constraint check (%s); treating as compatible: A=%r B=%r",
            e,
            a_con,
            b_con,
        )
        return
