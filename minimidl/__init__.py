"""MinimIDL: Modern Interface Definition Language.

A zero-cost abstraction tool that generates C++ interfaces, C wrappers,
and Swift bindings from a clean Interface Definition Language (IDL).
"""

__version__ = "0.1.0"
__author__ = "MinimIDL Contributors"

from minimidl.parser import parse_idl

__all__ = ["parse_idl"]
