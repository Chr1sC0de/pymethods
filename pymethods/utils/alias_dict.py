from typing import Iterable, Hashable
import sys


class AliasDict(dict):
    def __init__(self, alias_names: Iterable[Hashable], obj: object) -> None:
        """AliasDict

        Create a dictionary of pointers to an object

        Args:
            alias_names (Iterable[Hashable]): keys to be used,
                assumed to be immutable i.e. hashable
            obj (object): object the keys must point to
        """

        self.obj = obj
        for arg in alias_names:
            self.register_key(arg)

    def register_key(self, key: Hashable) -> None:
        """register_key

        Registers a new key in the dictionary. Speed up lookup of strings
        by interning its values https://en.wikipedia.org/wiki/String_interning
        this is done by storing only a single copy of each distinc string value

        Args:
            key (Hashable): hashable object to
                register as new key
        """
        if isinstance(key, str):
            key = sys.intern(key)
        self[key] = self.obj
