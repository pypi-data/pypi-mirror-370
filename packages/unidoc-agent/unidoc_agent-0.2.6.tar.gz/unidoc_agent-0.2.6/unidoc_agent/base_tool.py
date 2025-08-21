from abc import ABC, abstractmethod
from typing import Union

class BaseTool(ABC):
    @abstractmethod
    def can_handle(self, file_path: str, mime_type: Union[str, None]) -> bool:
        pass

    @abstractmethod
    def extract_content(self, file_path: str) -> str:
        pass