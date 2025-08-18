from abc import ABC, abstractmethod

from pydantic import BaseModel


class XmlEncodableModel(BaseModel, ABC):
    @property
    @abstractmethod
    def xml_tag_name(self) -> str:
        raise NotImplementedError
