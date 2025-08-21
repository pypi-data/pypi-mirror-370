"""
annotation_constraints.py

Implements the AST transformation described in spec-07-Annotation-Constraints.md:
Rewrites any Call inside a type annotation as Annotated[BaseType, MetaExpr].
"""

import ast


class AnnotateCallsTransformer(ast.NodeTransformer):
    """
    AST transformer that rewrites any Call inside a type annotation as
    Annotated[BaseType, MetaExpr], as described in ZVIC spec-07.
    """

    def __init__(self):
        super().__init__()
        self.need_imports = False

    def visit_FunctionDef(self, node: ast.FunctionDef):
        # Track constraints for this function
        constraints = []
        # Transform argument- and return-annotations
        for arg in node.args.args + node.args.kwonlyargs:
            orig_ann = arg.annotation
            if orig_ann:
                new_ann = self._transform_ann(orig_ann)
                # If annotation is Annotated with a constraint, extract it
                param_type = None
                if (
                    isinstance(new_ann, ast.Subscript)
                    and getattr(new_ann.value, "id", None) == "Annotated"
                ):
                    # Extract type and constraint
                    if (
                        isinstance(new_ann.slice, ast.Tuple)
                        and len(new_ann.slice.elts) == 2
                    ):
                        base_type_node = new_ann.slice.elts[0]
                        constraint_node = new_ann.slice.elts[1]
                        # Try to get type name from base_type_node
                        if isinstance(base_type_node, ast.Name):
                            param_type = base_type_node.id
                        elif isinstance(base_type_node, ast.Attribute):
                            param_type = ast.unparse(base_type_node)
                        constraint = (
                            constraint_node.value
                            if isinstance(constraint_node, ast.Constant)
                            else None
                        )
                        if constraint:
                            param_constraint = str(constraint).replace("_", arg.arg)
                            # Only update the AST constant for outer collection-level
                            # calls (e.g., list[...] (len(_) == 3)). Detect this
                            # when the original annotation was a Call whose func is
                            # a Subscript. For element-level calls like int(...)
                            # keep '_' in the annotation text.
                            try:
                                if (
                                    isinstance(orig_ann, ast.Call)
                                    and isinstance(orig_ann.func, ast.Subscript)
                                    and isinstance(new_ann.slice, ast.Tuple)
                                    and len(new_ann.slice.elts) == 2
                                ):
                                    new_ann.slice.elts[1] = ast.Constant(
                                        value=param_constraint
                                    )
                            except Exception:
                                pass
                            constraints.append((arg.arg, param_type, param_constraint))
                arg.annotation = ast.copy_location(new_ann, arg.annotation)
        return_constraint = None
        return_type = None
        if node.returns:
            new_ret = self._transform_ann(node.returns)
            # Extract return type and constraint if Annotated
            if (
                isinstance(new_ret, ast.Subscript)
                and getattr(new_ret.value, "id", None) == "Annotated"
                and isinstance(new_ret.slice, ast.Tuple)
                and len(new_ret.slice.elts) == 2
            ):
                base_type_node = new_ret.slice.elts[0]
                if isinstance(base_type_node, ast.Name):
                    return_type = base_type_node.id
                elif isinstance(base_type_node, ast.Attribute):
                    return_type = ast.unparse(base_type_node)
                if (
                    isinstance(new_ret.slice.elts[1], ast.Constant)
                    and new_ret.slice.elts[1].value
                ):
                    if constraint := new_ret.slice.elts[1].value:
                        return_constraint = str(constraint)
            else:
                # Not Annotated, just a type
                if isinstance(new_ret, ast.Name):
                    return_type = new_ret.id
                elif isinstance(new_ret, ast.Attribute):
                    return_type = ast.unparse(new_ret)
            node.returns = ast.copy_location(new_ret, node.returns)
        # Insert assert statements for constraints if __debug__ is True
        if constraints:
            # Compose a PEP 316 docstring for CrossHair
            doc_lines = [
                f"pre: {constraint}" for param_name, _, constraint in constraints
            ]
            if return_constraint:
                doc_lines.append(f"post: {return_constraint}")
            docstring = "\n".join(doc_lines) if doc_lines else None
            # Only insert assertions if __debug__ is True at transformation time
            type_asserts = []
            constraint_asserts = []
            if __debug__:
                type_asserts = [
                    ast.Assert(
                        test=ast.Call(
                            func=ast.Name(id="assumption", ctx=ast.Load()),
                            args=[
                                ast.Name(id=param_name, ctx=ast.Load()),
                                ast.Name(id=param_type, ctx=ast.Load()),
                            ],
                            keywords=[],
                        ),
                        msg=ast.JoinedStr(
                            values=[
                                ast.Constant(
                                    value=f"Type assertion failed for {param_name}: expected {param_type}, got value="
                                ),
                                ast.FormattedValue(
                                    value=ast.Name(id=param_name, ctx=ast.Load()),
                                    conversion=-1,
                                ),
                            ]
                        ),
                    )
                    for param_name, param_type, _ in constraints
                    if param_type
                ]
                constraint_asserts = [
                    ast.Assert(
                        test=ast.parse(str(constraint), mode="eval").body,
                        msg=ast.JoinedStr(
                            values=[
                                ast.Constant(
                                    value=f"'{constraint}' not satisfied for {param_name}="
                                ),
                                ast.FormattedValue(
                                    value=ast.Name(id=param_name, ctx=ast.Load()),
                                    conversion=-1,
                                ),
                            ]
                        ),
                    )
                    for param_name, _, constraint in constraints
                ]
            # Compose new body: docstring (as true docstring), type asserts, constraint asserts, then rest
            new_body = []
            if docstring:
                # Insert as true docstring (first statement, string literal)
                new_body.append(ast.Expr(value=ast.Constant(value=docstring)))
            # Remove any old docstring
            orig_body = node.body
            if (
                orig_body
                and isinstance(orig_body[0], ast.Expr)
                and isinstance(orig_body[0].value, ast.Constant)
                and isinstance(orig_body[0].value.value, str)
            ):
                orig_body = orig_body[1:]
            new_body.extend(type_asserts)
            new_body.extend(constraint_asserts)
            new_body.extend(orig_body)
            node.body = new_body

        if return_constraint or return_type:
            # Replace _ with a unique variable name
            ret_var = "__return__"
            constraint_expr_str = (
                return_constraint.replace("_", ret_var) if return_constraint else None
            )

            # Recursively transform all return statements in the function body
            class ReturnTransformer(ast.NodeTransformer):
                def visit_Return(self, node):
                    # Assign return value to ret_var
                    assign_value = (
                        node.value
                        if node.value is not None
                        else ast.Constant(value=None)
                    )
                    assign = ast.Assign(
                        targets=[ast.Name(id=ret_var, ctx=ast.Store())],
                        value=assign_value,
                    )
                    asserts = []
                    # Type assertion for return value
                    if return_type and __debug__:
                        asserts.append(
                            ast.Assert(
                                test=ast.Call(
                                    func=ast.Name(id="assumption", ctx=ast.Load()),
                                    args=[
                                        ast.Name(id=ret_var, ctx=ast.Load()),
                                        ast.Name(id=return_type, ctx=ast.Load()),
                                    ],
                                    keywords=[],
                                ),
                                msg=ast.JoinedStr(
                                    values=[
                                        ast.Constant(
                                            value=f"Return type assertion failed: expected {return_type}, got value="
                                        ),
                                        ast.FormattedValue(
                                            value=ast.Name(id=ret_var, ctx=ast.Load()),
                                            conversion=-1,
                                        ),
                                    ]
                                ),
                            )
                        )
                    # Constraint assertion for return value
                    if return_constraint and __debug__:
                        expr_ast = ast.parse(str(constraint_expr_str), mode="eval")
                        asserts.append(
                            ast.Assert(
                                test=expr_ast.body,
                                msg=ast.JoinedStr(
                                    values=[
                                        ast.Constant(
                                            value=f"Return constraint '{return_constraint}' not satisfied (_ = "
                                        ),
                                        ast.FormattedValue(
                                            value=ast.Name(id=ret_var, ctx=ast.Load()),
                                            conversion=-1,
                                        ),
                                        ast.Constant(value=", actual value: "),
                                        ast.FormattedValue(
                                            value=ast.Name(id=ret_var, ctx=ast.Load()),
                                            conversion=-1,
                                        ),
                                        ast.Constant(value=")"),
                                    ]
                                ),
                            )
                        )
                    # Only insert return assertions if __debug__ is True at transformation time
                    if __debug__:
                        return [
                            assign,
                            *asserts,
                            ast.Return(value=ast.Name(id=ret_var, ctx=ast.Load())),
                        ]
                    else:
                        return [node]

            # ast.Module requires 'type_ignores' in newer Python versions
            node.body = (
                ReturnTransformer()
                .visit(ast.Module(body=node.body, type_ignores=[]))
                .body
            )
        return node

    def _transform_ann(self, ann: ast.AST) -> ast.expr:
        """
        Recursively transforms annotation AST nodes. Always returns ast.expr or raises TypeError.
        """
        # Prevent infinite recursion: if already Annotated, do not transform again
        if (
            isinstance(ann, ast.Subscript)
            and getattr(ann.value, "id", None) == "Annotated"
        ):
            return ann
        # If annotation is a Call (e.g., int(_ < x)), always rewrite to Annotated with constraint as string
        if isinstance(ann, ast.Call):
            # Transform the function (base) as it may itself contain Calls
            # (e.g., list[int(...)]). Also transform arguments and keywords.
            base = self._transform_ann(ann.func)
            ann.args = [self._transform_ann(arg) for arg in ann.args]
            for kw in ann.keywords:
                if hasattr(kw, "value"):
                    kw.value = self._transform_ann(kw.value)
            # Extract the full argument string (including keywords)
            try:
                # Build the constraint expression from the Call node's
                # arguments and keywords. This avoids slicing the unparsed
                # text which is error-prone for nested calls.
                arg_parts = [ast.unparse(a) for a in ann.args]
                kw_parts = [
                    f"{kw.arg}={ast.unparse(kw.value)}" for kw in ann.keywords if kw.arg
                ]
                parts = arg_parts + kw_parts
                constraint = ", ".join(parts)
            except Exception:
                constraint = ""
            self.need_imports = True
            # Always wrap the base in Annotated, with constraint as string
            new_annotated = ast.Subscript(
                value=ast.Name(id="Annotated", ctx=ast.Load()),
                slice=ast.Tuple(
                    elts=[base, ast.Constant(value=constraint)], ctx=ast.Load()
                ),
                ctx=ast.Load(),
            )
            return ast.copy_location(new_annotated, ann)
        if isinstance(ann, ast.Subscript):
            new_value = self._transform_ann(ann.value)
            new_slice = self._transform_ann(ann.slice)
            new_sub = ast.Subscript(
                value=new_value,
                slice=new_slice,
                ctx=ann.ctx,
            )
            return ast.copy_location(new_sub, ann)
        # If it's a Tuple of types (e.g. Tuple[A,B])
        if isinstance(ann, ast.Tuple):
            new_elts = [self._transform_ann(e) for e in ann.elts]
            new_tuple = ast.Tuple(elts=new_elts, ctx=ann.ctx)
            return ast.copy_location(new_tuple, ann)
        # Everything else untouched
        if isinstance(ann, ast.expr):
            return ann
        raise TypeError(f"Annotation node is not an ast.expr: {ann!r}")

    def visit_Module(self, node: ast.Module) -> ast.Module:
        new_node = self.generic_visit(node)
        assert isinstance(new_node, ast.Module), (
            "Expected ast.Module after generic_visit"
        )
        # Ensure 'from __future__ import annotations' is the first line
        has_future_annotations = any(
            isinstance(stmt, ast.ImportFrom)
            and stmt.module == "__future__"
            and any(alias.name == "annotations" for alias in stmt.names)
            for stmt in new_node.body
        )
        if not has_future_annotations:
            imp_future = ast.ImportFrom(
                module="__future__",
                names=[ast.alias(name="annotations", asname=None)],
                level=0,
            )
            new_node.body.insert(0, imp_future)
        # Insert 'from zvic import assumption' after __future__ import
        has_assumption_import = any(
            isinstance(stmt, ast.ImportFrom)
            and stmt.module == "zvic"
            and any(alias.name == "assumption" for alias in stmt.names)
            for stmt in new_node.body
        )
        # Find the last __future__ import
        insert_at = 0
        for idx, stmt in enumerate(new_node.body):
            if isinstance(stmt, ast.ImportFrom) and stmt.module == "__future__":
                insert_at = idx + 1
        if not has_assumption_import:
            imp_assumption = ast.ImportFrom(
                module="zvic",
                names=[ast.alias(name="assumption", asname=None)],
                level=0,
            )
            new_node.body.insert(insert_at, imp_assumption)
        # Inject Annotated import if needed
        if self.need_imports:
            imp_annotated = ast.ImportFrom(
                module="typing",
                names=[ast.alias(name="Annotated", asname=None)],
                level=0,
            )
            new_node.body.insert(insert_at, imp_annotated)
        return new_node


def apply_annotation_constraints(source: str) -> str:
    """
    Applies the AnnotateCallsTransformer to the given Python source code string.
    Returns the transformed source as a string.
    """
    tree = ast.parse(source)
    transformer = AnnotateCallsTransformer()
    new_tree = transformer.visit(tree)
    ast.fix_missing_locations(new_tree)
    return ast.unparse(new_tree)
