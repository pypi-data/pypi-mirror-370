import base64
from pickle import loads, dumps
from typing import Type
from copy import deepcopy


class SerializerMixin:

    def serialize(self) -> str:
        """
        Serialize an object to a string representation.
        
        Parameters
        ----------
        obj : Type
            The object to serialize.
        
        Returns
        -------
        str
            The serialized string representation of the object.
        """
        pickled = dumps(self)
        based = base64.b64encode(pickled).decode('utf-8')
        return based 

    @staticmethod
    def deserialize(String: str) -> Type:
        """
        Deserialize a string representation into an object.

        Parameters
        ----------
        String : str
            The string representation to deserialize.

        Returns
        -------
        SerializerMixin
            The deserialized object.
        """
        decoded = base64.b64decode(String.encode('utf-8'))
        obj = deepcopy(loads(decoded))
        return obj
    
