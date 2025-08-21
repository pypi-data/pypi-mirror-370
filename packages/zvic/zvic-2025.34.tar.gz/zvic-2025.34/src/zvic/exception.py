# Custom exceptions for ZVIC
# LLM/agent-friendly, RFC 7807-compatible error base class and hierarchy.


class ZVICError(Exception):
    """
    Base error for ZVIC, RFC 7807 compatible, LLM/agent-friendly.
    """

    error_id = None
    type = None
    severity = "error"
    error_namespace = "ZVIC"

    def __init__(
        self,
        message=None,
        context=None,
        recovery_actions=None,
        error_id=None,
        severity=None,
        error_namespace=None,
        zvic_version=None,
        timestamp=None,
        **kwargs,
    ):
        super().__init__(message)
        self.message = message
        self.context = context or {}
        self.recovery_actions = recovery_actions or []
        self.error_id = error_id or self.error_id
        self.severity = severity or self.severity
        self.error_namespace = error_namespace or self.error_namespace
        self.zvic_version = zvic_version
        self.timestamp = timestamp
        for k, v in kwargs.items():
            setattr(self, k, v)

    def to_json(self):
        import json

        return json.dumps(
            {
                "error_id": self.error_id,
                "type": self.__class__.__name__,
                "severity": self.severity,
                "message": self.message,
                "context": self.context,
                "recovery_actions": self.recovery_actions,
                "error_namespace": self.error_namespace,
                "zvic_version": self.zvic_version,
                "timestamp": self.timestamp,
            },
            default=str,
        )

    def __str__(self):
        if self.recovery_actions:
            return (
                f"{self.message} \nSuggestions how to recover: {self.recovery_actions}"
            )
        return str(self.message)

    def __repr__(self):
        return f"<{self.__class__.__name__} id={self.error_id} severity={self.severity} message={self.message!r}>"


# --- ZVIC-specific errors ---


class SignatureIncompatible(ZVICError):
    """
    Raised when two function signatures/types/constraints are not compatible per ZVIC rules.
    """

    error_id = "ZV1001"
    type = "SignatureCompatibilityError"
    error_namespace = "ZVIC_COMPAT"
    severity = "error"

    def __init__(self, message=None, context=None, **kwargs):
        # Add more detailed context for LLMs
        detailed_context = context or {}
        spec_id = None
        if detailed_context:
            spec_id = detailed_context.get("spec_id")
            detailed_context["llm_hint"] = (
                "Review the spec08 matrix for the reported spec_id. "
                "Compare parameter kinds, names, order, and types. "
                "If type compatibility failed, check for unions, optionals, and container invariance/contravariance. "
                "If constraints failed, compare constraint expressions and ranges (C0a–C4). "
                "Provide a step-by-step reasoning for why the signatures/types/constraints are incompatible."
            )
        # Use spec_id as error_id if present
        error_id = f"Z-{spec_id}" if spec_id else self.error_id
        recovery_actions = [
            "Check parameter kinds (positional-only, PK, keyword-only) and their order per spec08.",
            "Compare parameter names and required/optional status exactly as in the spec matrix.",
            "For type errors, analyze if the types are compatible (subtype, union, optional, container).",
            "For container types, check invariance/contravariance rules (e.g., list[int] vs list[str]).",
            "For constraints, compare constraint expressions and ranges (C0a–C4).",
            "If using an LLM, ask for a step-by-step explanation of the incompatibility and possible fixes.",
            "Suggest concrete code changes to make B compatible with A, or vice versa, based on the spec08 scenario.",
            "If unsure, output the full context and ask for a compatibility matrix walkthrough.",
        ]
        super().__init__(
            message=message or "Signature/type/constraint compatibility failed.",
            context=detailed_context,
            recovery_actions=recovery_actions,
            error_id=error_id,
            severity=self.severity,
            error_namespace=self.error_namespace,
            **kwargs,
        )


# Add more ZVIC-specific errors as needed
