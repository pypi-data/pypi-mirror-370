import importlib
import pytest


def mark_setfit():
    def decorator(func):
        func = pytest.mark.pytorch(func)
        func = pytest.mark.skipif(importlib.util.find_spec('setfit') is not None,
                                  reason='preconditions for dependency test not met')(func)
        return func
    return decorator
