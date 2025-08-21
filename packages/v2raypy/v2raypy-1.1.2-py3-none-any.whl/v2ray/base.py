from abc import ABC, abstractmethod
from typing import Dict, Self, Optional


class V2rayBase(ABC):

    @classmethod
    @abstractmethod
    def from_dict(cls, config: Dict) -> Self:
        return cls

    @abstractmethod
    def to_dict(self):
        raise NotImplementedError


class SettingsBase(V2rayBase, ABC):
    @staticmethod
    def to_v2_headers(headers, arr=True):
        v2headers = {}
        for header in headers:
            name = header.get('name')
            value = header.get('value')
            if not name or not value:
                continue
            if not name in v2headers:
                v2headers[name] = [value] if arr else value
            else:
                if arr:
                    v2headers[name].append(value)
                else:
                    v2headers[name] = value

        return v2headers

    pass


class ProtocolSettingsBase(SettingsBase, ABC):
    def __init__(self,
                 address: Optional[str] = None,
                 port: Optional[int] = None
                 ):
        self.address = address
        self.port = port

    @property
    @abstractmethod
    def id(self):
        raise NotImplementedError

    @id.setter
    @abstractmethod
    def id(self, value):
        raise NotImplementedError
