import logging
from inspect import Signature

from .exception import SignatureIncompatible
from .utils import Scenario, prepare_params, prepare_scenario


def are_params_compatible(a_sig: Signature, b_sig: Signature) -> bool:
    """
    Compatibility logic using match/case for parameter kind scenarios.
    """
    a = prepare_params(a_sig)
    b = prepare_params(b_sig)
    scenario = prepare_scenario(a, a_sig, b, b_sig)

    match scenario:
        # |AP4|	*args + **kwargs|	A(a, b, /) → B(*args, **kwargs)   |	✓
        case Scenario(b_has_varargs=True, b_has_varkw=True):
            return True

        # AP1: A has only positional (posonly + *args), B has *args and no PK or KO (always compatible)
        case Scenario(
            a_pos_or_kw_required=0,
            a_pos_or_kw=0,
            a_kwonly_required=0,
            a_kwonly=0,
            b_kwonly_required=0,
            b_kwonly=0,
            b_has_varargs=True,
            b_has_varkw=False,
        ):
            return True

        # |PK5| Fewer required PK args in B, and not enough optional to compensate | A(a, b) -> B(a) | ✗
        case Scenario(
            a_pos_or_kw_required=a_req,
            b_pos_or_kw_required=b_req,
            b_pos_or_kw=b_total,
            b_has_varargs=False,
            b_has_varkw=False,
        ) if b_req < a_req and b_total < a_req:
            raise SignatureIncompatible(
                message="B has fewer required positional-or-keyword parameters than A, and not enough optional to compensate",
                context={"A": str(a_sig), "B": str(b_sig)},
            )

        # |PK6| B has fewer total PK parameters than A | A(a, b, c=1) -> B(a, b) | ✗
        case Scenario(
            a_pos_or_kw=a_total,
            b_pos_or_kw=b_total,
            b_has_varargs=False,
            b_has_varkw=False,
        ) if b_total < a_total:
            raise SignatureIncompatible(
                message="B has fewer total positional-or-keyword parameters than A",
                context={"A": str(a_sig), "B": str(b_sig)},
            )

        # | P2| Additional required args in B             | A(a, b,/) -> B(x, y, z,/) | ✗
        case Scenario(
            a_posonly_required=a_po,
            a_pos_or_kw_required=a_pk,
            a_kwonly_required=a_ko,
            b_posonly_required=b_po,
            b_pos_or_kw_required=b_pk,
            b_kwonly_required=b_ko,
        ) if (b_po + b_pk + b_ko) > (a_po + a_pk + a_ko):
            logging.getLogger(__name__).debug(
                f"Global required param check failed: a_required={a_po + a_pk + a_ko}, b_required={b_po + b_pk + b_ko}"
            )
            raise SignatureIncompatible(
                message="B has more required parameters than A",
                context={"A": str(a_sig), "B": str(b_sig)},
            )

        # PO→PK case
        case Scenario(
            a_posonly_required=a_req,
            b_posonly_required=b_req,
            a_posonly=a_total,
            b_posonly=b_total,
            b_pos_or_kw_required=b_pk_req,
            b_pos_or_kw=b_pk_total,
            b_has_varargs=b_has_args,
            b_has_varkw=b_has_kwargs,
        ) if b_req < a_req and b_total <= a_total:
            # |AP8|	Fixed params match A_max|	A(a, b, /) → B(x, y)     |	✓      | 2 ≤ 2 + 2 ≥ 2
            if (
                a_req > 0
                and b_req == 0
                and b_pk_req == a_req
                and b_pk_total == a_total
                and b_total == 0
                and not b_has_kwargs
                and not b_has_args
            ):
                return True
            # |AP9|	Optional params + **kwargs|	A(a, b, /) → B(x, y=1, **kwargs)      |	✓  | 1 ≤ 2 + 2 ≥ 2
            if a_req > 0 and b_req == 0 and b_pk_total >= a_total and b_has_kwargs:
                return True
            # |AP10| PO->PK with *args: A(a, b, /) → B(*args, k=5) | ✓
            if a_req > 0 and b_req == 0 and b_has_args:
                a_kwonly_required = scenario.a_kwonly_required
                b_kwonly_required = scenario.b_kwonly_required
                if b_kwonly_required == 0 or b_kwonly_required == a_kwonly_required:
                    return True
                else:
                    raise SignatureIncompatible(
                        message="B has extra required keyword-only parameters that A does not have (AP10 edge)",
                        context={"A": str(a_sig), "B": str(b_sig)},
                    )
            # | P3| Fewer required args in B, but no optional to compensate | A(a,b,/) -> B(x,/)        | ✗
            raise SignatureIncompatible(
                message="B has fewer required positional-only parameters than A, or transition from PO to PK is not allowed (complex edge)",
                context={"A": str(a_sig), "B": str(b_sig)},
            )

        # | P5| Fewer optional args in B                  | A(a,b=1,/) -> B(x,/)      | ✗
        case Scenario(
            a_posonly_required=a_req,
            a_posonly=a_total,
            b_posonly_required=b_req,
            b_posonly=b_total,
            b_has_varargs=False,
            b_has_varkw=False,
        ) if (b_total - b_req) < (a_total - a_req):
            raise SignatureIncompatible(
                message="B has fewer optional positional-only parameters than A",
                context={"A": str(a_sig), "B": str(b_sig)},
            )

        # PK names case: raise if names differ, regardless of required count
        case Scenario(
            a_pos_or_kw=a_pk_total,
            b_pos_or_kw_required=b_pk_req,
            b_pos_or_kw=b_pk_total,
            b_has_varargs=False,
            b_has_varkw=False,
        ) if a_pk_total == b_pk_total and a_pk_total > 0:
            a_names = [p["name"] for p in prepare_params(a_sig).pos_or_kw]
            b_names = [p["name"] for p in prepare_params(b_sig).pos_or_kw]
            if a_names != b_names:
                raise SignatureIncompatible(
                    message="PK parameter names differ",
                    context={"A": str(a_sig), "B": str(b_sig)},
                )

        # KW names case: raise if names differ, regardless of required count
        case Scenario(
            a_kwonly=a_ko_total,
            b_kwonly=b_ko_total,
            b_has_varargs=False,
            b_has_varkw=False,
        ) if a_ko_total == b_ko_total and a_ko_total > 0:
            a_names = sorted(p["name"] for p in prepare_params(a_sig).kwonly)
            b_names = sorted(p["name"] for p in prepare_params(b_sig).kwonly)
            if a_names != b_names:
                raise SignatureIncompatible(
                    message="Keyword-only parameter names differ",
                    context={"A": str(a_sig), "B": str(b_sig)},
                )

        # |K6| B has fewer total keyword-only parameters than A
        case Scenario(
            a_kwonly=a_total,
            b_kwonly=b_total,
            b_has_varargs=False,
            b_has_varkw=False,
        ) if b_total < a_total:
            raise SignatureIncompatible(
                message="B has fewer total keyword-only parameters than A",
                context={"A": str(a_sig), "B": str(b_sig)},
            )

        # PK6: B has fewer total PK parameters than A
        case Scenario(
            a_pos_or_kw=a_total,
            b_pos_or_kw=b_total,
            b_has_varargs=False,
            b_has_varkw=False,
        ) if b_total < a_total:
            raise SignatureIncompatible(
                message="B has fewer total positional-or-keyword parameters than A",
                context={"A": str(a_sig), "B": str(b_sig)},
            )

        # PK, B has fewer required
        case Scenario(
            a_pos_or_kw_required=a_req,
            b_pos_or_kw_required=b_req,
            b_has_varargs=False,
            b_has_varkw=False,
        ) if b_req < a_req:
            raise SignatureIncompatible(
                message="B has fewer required positional-or-keyword parameters than A",
                context={"A": str(a_sig), "B": str(b_sig)},
            )

        # PK, B has fewer optional
        case Scenario(
            a_pos_or_kw_required=a_req,
            a_pos_or_kw=a_total,
            b_pos_or_kw_required=b_req,
            b_pos_or_kw=b_total,
            b_has_varargs=False,
            b_has_varkw=False,
        ) if (b_total - b_req) < (a_total - a_req):
            raise SignatureIncompatible(
                message="B has fewer optional positional-or-keyword parameters than A",
                context={"A": str(a_sig), "B": str(b_sig)},
            )

        # |K5| Fewer required args in B                  | A(*, a, b) -> B(*, a)         | ✗
        case Scenario(
            a_kwonly_required=a_req,
            a_kwonly=a_total,
            b_kwonly_required=b_req,
            b_kwonly=b_total,
            b_has_varargs=False,
            b_has_varkw=False,
        ) if b_req < a_req and b_total < a_total:
            raise SignatureIncompatible(
                message="B has fewer optional keyword-only parameters than A",
                context={"A": str(a_sig), "B": str(b_sig)},
            )

        # XP1: Positional-only for both, same required and total
        case Scenario(
            a_posonly_required=a_req,
            a_posonly=a_total,
            b_posonly_required=b_req,
            b_posonly=b_total,
            b_has_varargs=False,
            b_has_varkw=False,
        ) if a_req == b_req and a_total == b_total:
            return True

        # KW, B has more optional
        case Scenario(
            a_kwonly_required=a_req,
            a_kwonly=a_total,
            b_kwonly_required=b_req,
            b_kwonly=b_total,
            b_has_varargs=False,
            b_has_varkw=False,
        ) if (b_total - b_req) > (a_total - a_req):
            return True

        # Positional-only, B has more optional (P4, compatible)
        case Scenario(
            a_posonly_required=a_req,
            a_posonly=a_total,
            b_posonly_required=b_req,
            b_posonly=b_total,
            b_has_varargs=False,
            b_has_varkw=False,
        ) if b_total > a_total and b_req <= a_req:
            return True

        # Positional-only for both, same required and total (P1, compatible)
        case Scenario(
            a_posonly_required=a_req,
            a_posonly=a_total,
            b_posonly_required=b_req,
            b_posonly=b_total,
            b_has_varargs=False,
            b_has_varkw=False,
        ) if a_req == b_req and a_total == b_total:
            return True

        # PK, B has more optional
        case Scenario(
            a_pos_or_kw_required=a_req,
            a_pos_or_kw=a_total,
            b_pos_or_kw_required=b_req,
            b_pos_or_kw=b_total,
            b_has_varargs=False,
            b_has_varkw=False,
        ) if (b_total - b_req) > (a_total - a_req):
            return True

        # KW, B has more optional
        case Scenario(
            a_kwonly_required=a_req,
            a_kwonly=a_total,
            b_kwonly_required=b_req,
            b_kwonly=b_total,
            b_has_varargs=False,
            b_has_varkw=False,
        ) if (b_total - b_req) > (a_total - a_req):
            return True

        # B is empty
        case Scenario(
            b_posonly_required=0,
            b_posonly=0,
            b_pos_or_kw_required=0,
            b_pos_or_kw=0,
            b_kwonly_required=0,
            b_kwonly=0,
            b_has_varargs=False,
            b_has_varkw=False,
        ):
            return True

        # PK, B has more optional
        case Scenario(
            a_pos_or_kw_required=a_req,
            a_pos_or_kw=a_total,
            b_pos_or_kw_required=b_req,
            b_pos_or_kw=b_total,
            b_has_varargs=False,
            b_has_varkw=False,
        ) if (b_total - b_req) > (a_total - a_req):
            return True

        # KO-kwargs case
        case Scenario(
            a_posonly_required=0,
            a_pos_or_kw_required=0,
            b_posonly_required=0,
            b_pos_or_kw_required=0,
            b_has_varargs=False,
            b_has_varkw=True,
        ):
            return True

        # args&kwargs case
        case Scenario(
            a_posonly_required=a_po,
            a_pos_or_kw_required=a_pk,
            a_kwonly_required=a_ko,
            b_posonly_required=b_po,
            b_pos_or_kw_required=b_pk,
            b_kwonly_required=b_ko,
            b_has_varargs=varargs,
            b_has_varkw=varkw,
        ) if varargs or varkw:
            # If A has only optional parameters, B is compatible
            if a_po + a_pk + a_ko == 0:
                return True
            # Otherwise, B must have at least as many required positional-only, PK, and KW-only params as A
            if b_po + b_pk + b_ko < a_po + a_pk + a_ko:
                raise SignatureIncompatible(
                    message="B cannot satisfy all required parameters of A, even with *args/**kwargs",
                    context={"A": str(a_sig), "B": str(b_sig)},
                )
            return True

        # Fallback
        case _:
            raise AssertionError("Unhandled Scenario??")
    return False
