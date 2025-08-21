"""
The module defines an InheritanceDict, which is a dictionary, but for lookups where the key is a
type, it will walk over the Method Resolution Order (MRO) looking for a value.
"""


class InheritanceDict(dict):
    """
    A dictionary that for type lookups, will walk over the Method Resolution Order (MRO) of that
    type, to find the value for the most specific superclass (including the class itself) of that
    type.
    """

    def __getitem__(self, key):
        """
        Return the value associated with a key, resolving class inheritance for type keys.

        If `key` is a class (a `type`), this looks up values for each class in the key's
        method resolution order (MRO) and returns the first found mapping value.
        If `key` is not a class, it is used directly as the lookup key.

        Parameters:
            key: The lookup key. If a `type`, the MRO (key.__mro__) is searched in order;
            otherwise `key` itself is used.

        Returns:
            The mapped value for the first matching key.

        Raises:
            KeyError: If no matching key is found.
        """
        if isinstance(key, type):
            items = key.__mro__
        else:
            items = (key,)
        for item in items:
            try:
                return super().__getitem__(item)
            except KeyError:
                pass
        raise KeyError(key)

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default
