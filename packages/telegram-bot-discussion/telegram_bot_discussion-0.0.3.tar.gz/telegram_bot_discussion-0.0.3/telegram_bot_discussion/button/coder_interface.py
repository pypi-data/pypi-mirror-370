from abc import ABC, abstractmethod
from typing import Any, List, Tuple


class CoderInterface(ABC):
    _instance = None

    def check_signature(
        self,
        chat_id: int,
        signed_serialized_data: str,
        sender_id: int = None,
    ) -> bool:
        if sender_id is None:
            sender_id = chat_id
        signature, serialized_data = self.extract_signature_and_serialized_data(
            signed_serialized_data
        )
        if self.get_signature(chat_id, serialized_data, sender_id) == signature:
            return True
        return False

    @abstractmethod
    def deserialize(self, data: str) -> List[Any]: ...

    @abstractmethod
    def extract_signature_and_deserialized_data(
        self, signed_serialized_data: str
    ) -> Tuple[str, List[Any]]: ...

    @abstractmethod
    def extract_signature_and_serialized_data(
        self, signed_serialized_data: str
    ) -> Tuple[str, str]: ...

    @abstractmethod
    def get_signature(
        self, chat_id: int, serialized_data: str, sender_id: int
    ) -> str: ...

    @abstractmethod
    def serialize(self, *args: Any) -> str: ...

    @abstractmethod
    def sign(self, signature: str, serialized_data: str) -> str: ...

    def fetch_deserialized_data(self, signed_serialized_data: str) -> List[Any]:
        return self.extract_signature_and_deserialized_data(signed_serialized_data)[1]

    def fetch_serialized_data(self, signed_serialized_data: str) -> str:
        return self.extract_signature_and_serialized_data(signed_serialized_data)[1]

    def fetch_signature(self, signed_serialized_data: str) -> str:
        return self.extract_signature_and_deserialized_data(signed_serialized_data)[0]

    @classmethod
    def instance(cls, *args, **kwargs):
        if cls._instance == None:
            cls._instance = cls(*args, **kwargs)
        return cls._instance
