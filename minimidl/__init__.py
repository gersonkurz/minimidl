"""MinimIDL: Modern Interface Definition Language.

A zero-cost abstraction tool that generates C++ interfaces, C wrappers,
and Swift bindings from a clean Interface Definition Language (IDL).
"""

__version__ = "0.1.0"
__author__ = "MinimIDL Contributors"

from minimidl.ast import IDLFile, load_ast, save_ast
from minimidl.parser import parse_idl, parse_idl_file

__all__ = ["parse_idl", "parse_idl_file", "IDLFile", "save_ast", "load_ast"]
