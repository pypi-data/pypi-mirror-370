import os

_execution_context = None


def get_execution_id():
    global _execution_context
    if _execution_context is None:
        try:
            # File injected in steps
            import __craft_internal_execution_context  # type: ignore

            _execution_context = __craft_internal_execution_context
        except ImportError:
            _execution_context = False
    if _execution_context:
        try:
            return _execution_context.current_execution_id.get()
        except LookupError:
            pass
    return os.environ.get("CRAFT_AI_EXECUTION_ID")
