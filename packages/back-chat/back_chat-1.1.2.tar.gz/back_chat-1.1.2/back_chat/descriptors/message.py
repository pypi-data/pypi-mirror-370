from enum import Enum


class MessageType(Enum):
    """
    Enumeration of possible message types used in the application.
    Each member represents a distinct category or kind of message.
    """
    MESSAGE: str = 'message'
    CONNECT: str = 'connect'
    DISCONNECT: str = 'disconnect'
    NOTICE: str = 'notice'
    WARNING: str = 'warning'
    CONNECTION: str = 'connection'
    ALARM: str = 'alarm'
    CONFIGURATION: str = 'configuration'


class MessageMode:
    """
    Descriptor class that manages attribute access for message mode fields.

    This descriptor validates that the assigned value is a valid member of
    the MessageType enum, storing its string value internally.

    Usage:
        When used as a class attribute, it enforces that only MessageType enum
        values can be assigned to that attribute.
    """

    def __init__(self, name=None):
        """
        Initializes the descriptor instance.

        :param name: The name of the attribute this descriptor manages.
        """
        self.name = name

    def __get__(self, instance, owner):
        """
        Descriptor getter method.

        If accessed on the class, returns the descriptor itself.
        If accessed on an instance, returns the stored attribute value.

        :param instance: The instance of the class where the descriptor is
        used.
        :param owner: The class owning the descriptor.
        :return: The current stored value of the attribute.
        """
        if instance is None:
            return self
        return instance.__dict__[self.name]

    def __set__(self, instance, value):
        """
        Descriptor setter method.

        Validates that the value assigned is either a MessageType enum member
        or a valid string representing a MessageType member.

        Raises a ValueError if the value is invalid.

        :param instance: The instance of the class where the descriptor is
        used.
        :param value: The new value to assign to the attribute.
        """
        if isinstance(value, MessageType):
            value = value.value  # Convert enum to its string value
        if value not in MessageType:
            raise ValueError(f"Invalid value: {value}. "
                             f"Must be in {MessageType.__name__}")
        instance.__dict__[self.name] = value

    def __set_name__(self, owner, name):
        """
        Automatically called at class creation to inform the descriptor
        of the attribute name it is assigned to.

        :param owner: The owner class where the descriptor is used.
        :param name: The attribute name.
        """
        self.name = name
