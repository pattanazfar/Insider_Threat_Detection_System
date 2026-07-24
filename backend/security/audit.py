import logging

audit_logger = logging.getLogger("insider_threat_api.audit")


def log_security_event(action: str, actor: str, target: str) -> None:
    """Emit a structured, minimal audit event without secrets or request bodies."""
    audit_logger.info("security_event action=%s actor=%s target=%s", action, actor, target)
