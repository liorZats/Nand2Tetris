"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing


class SymbolTable:
    """A symbol table that associates names with information needed for Jack
    compilation: type, kind and running index. The symbol table has two nested
    scopes (class/subroutine).
    """
    TYPE = 0
    KIND = 1
    INDEX = 2

    def __init__(self) -> None:
        """Creates a new empty symbol table."""
        self.class_st = {}
        self.subroutine_st = {}
        self.kind_count = {
            "var": 0,
            "argument": 0,
            "field": 0,
            "static": 0
        }

    def start_subroutine(self) -> None:
        """Starts a new subroutine scope (i.e., resets the subroutine's 
        symbol table).
        """
        self.subroutine_st.clear()
        self.kind_count["var"] = 0
        self.kind_count["argument"] = 0

    def define(self, name: str, type: str, kind: str) -> None:
        """Defines a new identifier of a given name, type and kind and assigns 
        it a running index. "STATIC" and "FIELD" identifiers have a class scope, 
        while "ARG" and "VAR" identifiers have a subroutine scope.

        Args:
            name (str): the name of the new identifier.
            type (str): the type of the new identifier.
            kind (str): the kind of the new identifier, can be:
            "STATIC", "FIELD", "ARG", "VAR".
        """
        if kind in {'argument', 'var'}:
            self.subroutine_st[name] = (type, kind, self.kind_count[kind])
        else:  # 'STATIC' or 'FIELD'
            self.class_st[name] = (type, kind, self.kind_count[kind])
        self.kind_count[kind] += 1

    def var_count(self, kind: str) -> int:
        """
        Args:
            kind (str): can be "STATIC", "FIELD", "ARG", "VAR".

        Returns:
            int: the number of variables of the given kind already defined in 
            the current scope.
        """
        return self.kind_count[kind]

    def val_from_st(self, name: str, val_type: int):
        """

        Args:
            name: name of an identifier.
            val_type: KIND/TYPE/INDEX

        Returns:

        """
        if name in self.subroutine_st.keys():
            return self.subroutine_st[name][val_type]
        elif name in self.class_st.keys():
            return self.class_st[name][val_type]
        else:
            return None

    def kind_of(self, name: str) -> str:
        """
        Args:
            name (str): name of an identifier.

        Returns:
            str: the kind of the named identifier in the current scope, or None
            if the identifier is unknown in the current scope.
        """
        return self.val_from_st(name, self.KIND)

    def type_of(self, name: str) -> str:
        """
        Args:
            name (str):  name of an identifier.

        Returns:
            str: the type of the named identifier in the current scope.
        """
        return self.val_from_st(name, self.TYPE)

    def index_of(self, name: str) -> int:
        """
        Args:
            name (str):  name of an identifier.

        Returns:
            int: the index assigned to the named identifier.
        """
        return self.val_from_st(name, self.INDEX)

    def is_in(self, name: str):
        return name in self.subroutine_st.keys() or name in self.class_st.keys()
