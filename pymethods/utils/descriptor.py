from typing import Any


class Descriptor:
    """ Descriptor

    Base descriptor class
    """

    def __init__(self, name: str) -> None:
        """__init__

        method by which to get a property from an object.
        self.name is a property accessed by the descriptor
        during the get method

        Args:
            name (str): string of property to use

        Returns:
            None:
        """
        self.name = name

    def __get__(self, obj: object, objType: type) -> Any:
        """__get__

        get method i.e. obj.potatoe returns "potatoes". We will
        be defining a new method

        Args:
            obj (object): object with property defined in
                self.name
            objType (type): class of the obj
        Returns:
            Any: object property
        """
        return getattr(obj, self.name)

    def __set__(self, obj: object, value: Any) -> None:
        """__set__

        define the set method of the property whose
        name is defined in self.name

        Args:
            obj (object): object by which assignment is occuring
            value (Any): value to assign

        Returns:
            None:
        """
        setattr(obj, self.name, value)

    def __delete__(self, obj: object) -> None:
        delattr(obj, self.name)


class LockedDescriptor(Descriptor):
    def __set__(self, obj: object, value: Any) -> None:
        """NotSettable

        properties set from this class
        are locked and cannot be set

        Args:
            obj (object): assigned object
            value (Any): any value

        Raises:
            Exception: cannot be set error

        Returns:
            None:
        """

        raise Exception(f'property {self.name} is not settable')


class NoInputFunctionAlias(Descriptor):
    def __init__(self, name: str, store=False) -> None:
        """__init__

        method by which to get a property from an object.
        self.name is a property accessed by the descriptor
        during the get method

        Args:
            name (str): string of property to use
            store (bool): store the value of the output of the
                function so that it is not recomputed

        Returns:
            None:
        """
        self.store = store
        self.save_string = "_%s_" % name
        super().__init__(name)

    def __get__(self, obj: object, objType: type) -> Any:
        """__get__

        create an alias for a method which takes no input,
        essentially converting the method into a property.
        If store is set to true the value of the calculated
        function is stored as a private variable and is reused
        rather than recalculating the solution

        Args:
            obj (object): object with property defined in
                self.name
            objType (type): class of the obj

        Returns:
            Any: return of object method
        """
        if self.store:
            if hasattr(obj, self.save_string):
                return getattr(obj, self.save_string)
            else:
                value = getattr(obj, self.name)()
                setattr(obj, self.save_string, value)
        else:
            value = getattr(obj, self.name)()
        return value

    def __set__(self, obj: object, value: Any) -> None:
        """__set__

        define the set method of the property whose
        name is defined in self.name

        Args:
            obj (object): object by which assignment is occuring
            value (Any): value to assign

        Returns:
            None:
        """
        setattr(obj, self.save_string, value)

    def __delete__(self, obj: object) -> None:
        """__delete__

        delete the saved property and not the original function
        method

        Args:
            obj (object): [description]

        Returns:
            None: [description]
        """
        del obj.__dict__[self.save_string]
