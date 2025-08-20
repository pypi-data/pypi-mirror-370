from abc import ABC, abstractmethod
from typing import Dict, Any


class Serializable(ABC):
    """
    Abstract base class for all OSSBOM models that need serialization.
    """

    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the object into a dictionary representation.
        :return: Dictionary representation of the object.
        """
        pass

    @classmethod
    @abstractmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Serializable":
        """
        Create an object instance from a dictionary.
        :param data: Dictionary representation of the object.
        :return: An instance of the class.
        """
        pass

    @classmethod
    @abstractmethod
    def create(cls, **kwargs) -> "Serializable":
        """
        Create an object instance from keyword arguments.
        :param kwargs: Keyword arguments to create the object.
        :return: An instance of the class.
        """
        pass
