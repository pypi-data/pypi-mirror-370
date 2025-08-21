\
import importlib
import importlib.abc
import importlib.util
import sys
import types
from functools import wraps
from typing import Any, Optional

PHRASE = "I'm sorry Dave, I'm afraid I can't do that."

def _announce(*_args, **_kwargs):
    print(PHRASE)

def _wrap_callable(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        _announce()
        # Optional: raise instead
        # raise RuntimeError(PHRASE)
        return None
    return wrapper

class HALWrapper:
    """
    Generic wrapper: if the wrapped object is callable, calling it prints PHRASE.
    Attribute access is lazy-wrapped so methods/functions/classes also get blocked.
    """
    __slots__ = ("_obj",)

    def __init__(self, obj: Any):
        object.__setattr__(self, "_obj", obj)

    def __getattr__(self, name):
        target = getattr(self._obj, name)
        return hal_wrap(target)

    def __setattr__(self, name, value):
        setattr(self._obj, name, value)

    def __repr__(self):
        return f"<HALWrapper of {self._obj!r}>"

    def __call__(self, *args, **kwargs):
        if callable(self._obj):
            _announce()
            return None
        raise TypeError(f"'{type(self._obj).__name__}' object is not callable")

    def __getitem__(self, key):
        target = self._obj[key]
        return hal_wrap(target)

def hal_wrap(obj: Any):
    # Always return a wrapper so that any call eventually prints the phrase.
    # For non-callable objects, attribute access keeps wrapping deeper.
    return HALWrapper(obj)

class HALModuleProxy(types.ModuleType):
    """
    A module proxy that lazily wraps attributes so any callable you reach
    eventually prints PHRASE on call.
    """
    def __init__(self, real_mod: types.ModuleType):
        super().__init__(real_mod.__name__)
        object.__setattr__(self, "_real_mod", real_mod)
        # Preserve dunder attributes for nicer repr/dir
        self.__dict__.update({k: v for k, v in real_mod.__dict__.items()
                              if k.startswith("__") and k.endswith("__")})

    def __getattr__(self, name):
        target = getattr(self._real_mod, name)
        return hal_wrap(target)

    def __repr__(self):
        return f"<HALModuleProxy for {self._real_mod.__name__}>"

def import_as(modname: str) -> HALModuleProxy:
    """
    Import a real module, then return a proxied module that blocks calls.
    """
    real = importlib.import_module(modname)
    return HALModuleProxy(real)

# ---- Meta path hook (intercept future imports of selected names) ----

class _HALFinder(importlib.abc.MetaPathFinder, importlib.abc.Loader):
    def __init__(self, targets):
        self.targets = set(targets)
        self._original_specs = {}

    def find_spec(self, fullname, path, target=None):
        if fullname in self.targets:
            # Find the real spec first using other finders
            for finder in sys.meta_path:
                if finder is self:
                    continue
                if hasattr(finder, "find_spec"):
                    spec = finder.find_spec(fullname, path, target)
                else:
                    spec = None
                if spec is not None:
                    self._original_specs[fullname] = spec
                    # Return a spec that we will load
                    from importlib.machinery import ModuleSpec
                    return ModuleSpec(fullname, self)
        return None

    def create_module(self, spec):
        # Use default module creation
        return None

    def exec_module(self, module):
        # Avoid recursion by temporarily removing ourselves
        try:
            sys.meta_path.remove(self)
            real = importlib.import_module(module.__name__)
        finally:
            sys.meta_path.insert(0, self)
        proxy = HALModuleProxy(real)
        sys.modules[module.__name__] = proxy

_finder = None  # type: Optional[_HALFinder]

def install(*module_names: str):
    """
    Intercept imports of the given module names and return proxied modules.
    Example:
        install("numpy", "requests")
        import numpy as np   # np.somefunc(...) -> prints PHRASE
    """
    global _finder
    targets = set(module_names)
    if _finder is None:
        _finder = _HALFinder(targets)
        sys.meta_path.insert(0, _finder)
    else:
        _finder.targets.update(targets)

def uninstall(*module_names: str):
    """Remove names from interception; remove hook entirely if no targets left."""
    global _finder
    if _finder is None:
        return
    for n in module_names:
        _finder.targets.discard(n)
    if not _finder.targets:
        try:
            sys.meta_path.remove(_finder)
        except ValueError:
            pass
        _finder = None
