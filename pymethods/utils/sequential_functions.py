class SequentialFunction:
    def __init__(self, *args) -> None:
        """__init__

        Composes a function from an iterable of functions

        Args:
            args: a tuple containing the functions to map

        Returns:
            None: [description]
        """
        self.functions = args

    def __call__(self, obj: object) -> object:
        """__call__

        Applies the composite function onto the object

        Args:
            obj (object):

        Returns:
            object:
        """
        for method in self.functions:
            obj = method(obj)
        return obj
