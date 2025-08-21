# -*- coding: utf-8 -*-
import inspect
import functools

# Internal/private marker attribute names
_RUN_ON_FAILURE_ATTR = "__rof_wrapped__"
_IGNORE_RUN_FAILURE_ATTR = "__rof_ignore__"
_ORIGINAL_METHOD_ATTR = "__original__"


def _run_on_failure_decorator(method):
    """Decorator to wrap keyword methods with _run_on_failure support."""
    if getattr(method, _RUN_ON_FAILURE_ATTR, False):
        # Already decorated → skip re-wrapping
        return method

    @functools.wraps(method)
    def wrapper(*args, **kwargs):
        try:
            return method(*args, **kwargs)
        except Exception:
            self = args[0] if args else None
            if self and hasattr(self, "_run_on_failure"):
                self._run_on_failure()
            raise

    setattr(wrapper, _RUN_ON_FAILURE_ATTR, True)      # mark as decorated
    setattr(wrapper, _ORIGINAL_METHOD_ATTR, method)   # keep reference to original
    return wrapper


def ignore_on_fail(method):
    """Decorator to mark methods that should never be wrapped by run_on_failure."""
    setattr(method, _IGNORE_RUN_FAILURE_ATTR, True)
    return method


class KeywordGroupMetaClass(type):
    def __new__(cls, clsname, bases, attrs):
        for name, method in list(attrs.items()):
            if (
                not name.startswith('_')
                and inspect.isfunction(method)
                and not getattr(method, _IGNORE_RUN_FAILURE_ATTR, False)
                and not getattr(method, _RUN_ON_FAILURE_ATTR, False)
            ):
                attrs[name] = _run_on_failure_decorator(method)
        return super().__new__(cls, clsname, bases, attrs)


class KeywordGroup(metaclass=KeywordGroupMetaClass):

    def _invoke_original(self, method, *args, **kwargs):
        """
        Call the original (undecorated) implementation of a method.

        Accepts either:
          - method name (str), e.g. self._invoke_original("click", el)
          - bound method itself, e.g. self._invoke_original(self.click, el)

        Falls back to the current method if undecorated.
        Returns None if method not found at all.
        """
        if isinstance(method, str):
            method = getattr(self, method, None)
        if method is None:
            return None

        original = getattr(method, _ORIGINAL_METHOD_ATTR, method)
        return original(self, *args, **kwargs)
