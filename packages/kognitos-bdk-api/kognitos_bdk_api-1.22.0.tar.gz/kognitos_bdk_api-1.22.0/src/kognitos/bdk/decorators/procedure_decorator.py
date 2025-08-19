import inspect
from functools import wraps
from inspect import Signature

from ..docstring import DocstringParser
from ..reflection import BookProcedureSignature
from ..reflection.factory import BookProcedureFactory


def procedure(name: str, **kwargs):
    override_connection_required = kwargs.get("connection_required", None)

    def decorator(fn):
        if not inspect.isfunction(fn):
            raise TypeError("The procedure decorator can only be applied to functions.")

        # parse procedure signature
        english_signature = BookProcedureSignature.from_english(name)

        # parse python signature
        python_signature = extract_python_signature(fn)

        # parse documentation
        if not fn.__doc__:
            raise ValueError("missing docstring")

        docstring = DocstringParser.parse(fn.__doc__)

        # construct book_procedure
        book_procedure = BookProcedureFactory.create(fn.__name__, english_signature, python_signature, docstring, override_connection_required)

        if not hasattr(fn, "__procedure__"):
            fn.__procedure__ = book_procedure

        if not hasattr(fn, "__signature__"):
            fn.__signature__ = python_signature

        if not hasattr(fn, "__text_signature__"):
            fn.__text_signature__ = english_signature

        return wraps(fn)(fn)

    def extract_python_signature(fn) -> Signature:
        return inspect.signature(fn, eval_str=True)

    return decorator
