import dataclasses
from typing import *

from overloadable import overloadable

__all__ = ["makeprop"]


@dataclasses.dataclass
class makeprop:
    var: Optional[str] = None
    hasdeleter: bool = False
    deletervalue: object = None

    @overloadable
    def __init__(self: Self, *args: Any, **kwargs: Any) -> bool:
        "This function works as dispatcher."
        return "delete" in kwargs.keys()

    @__init__.overload(False)
    def __init__(self: Self, var: Optional[str] = None) -> None:
        "This magic method sets up the current instance."
        return self.__init_1(var)

    @__init__.overload(True)
    def __init__(self: Self, var: Optional[str] = None, *, delete: object) -> None:
        "This magic method sets up the current instance."
        return self.__init_1(var, hasdeleter=True, deletervalue=delete)

    def __init_1(
        self,
        var: Optional[str] = None,
        /,
        hasdeleter: bool = False,
        deletervalue: object = None,
    ) -> None:
        "This method is the common ending of both versions of __init__."
        if var is None:
            self.var = None
        else:
            self.var = str(var)
        self.hasdeleter: bool = hasdeleter
        self.deletervalue: object = deletervalue

    def __call__(self: Self, func: Callable) -> property:
        "This magic method implements calling the current instance."
        if self.var is None:
            var = "_%s" % func.__name__
        else:
            var = self.var
        deletervalue = self.deletervalue

        kwargs: dict = dict(doc=func.__doc__)

        def fget(_self):
            return getattr(_self, var)

        kwargs["fget"] = fget

        def fset(_self, value) -> None:
            setattr(_self, var, func(_self, value))

        kwargs["fset"] = fset

        if self.hasdeleter:

            def fdel(_self) -> None:
                setattr(_self, var, func(_self, deletervalue))

            kwargs["fdel"] = fdel

        ans: property = property(**kwargs)
        return ans
