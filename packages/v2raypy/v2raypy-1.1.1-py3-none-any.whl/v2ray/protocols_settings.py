from enum import Enum
from typing import Dict, Self, Optional

from base import ProtocolSettingsBase, SettingsBase


class Protocols(str, Enum):
    Freedom = "freedom"
    Blackhole = "blackhole"
    DNS = "dns"
    VMess = "vmess"
    VLESS = "vless"
    Trojan = "trojan"
    Shadowsocks = "shadowsocks"
    Socks = "socks"
    HTTP = "http"
    Wireguard = "wireguard"


class VmessSettings(ProtocolSettingsBase):
    def __init__(self,
                 address: Optional[str] = None,
                 port: Optional[int] = None,
                 uuid: Optional[str] = None,
                 security: Optional[str] = None
                 ):
        super().__init__(address, port)
        self.uuid = uuid
        self.security = security

    @property
    def id(self):
        return self.uuid

    @id.setter
    def id(self, value):
        self.uuid = value

    @classmethod
    def from_dict(cls, config: Dict) -> Self:
        vnext = config.get('vnext', [{}])[0]
        return cls(
            vnext.get('address', None),
            vnext.get('port', None),
            vnext.get('users', [{}])[0].get('id', None),
            vnext.get('users', [{}])[0].get('security', None),
        )

    def to_dict(self):
        return {
            'vnext': [{
                'address': self.address,
                'port': self.port,
                'users': [{
                    'id': self.uuid,
                    'security': self.security,
                }]
            }]
        }


class VlessSettings(ProtocolSettingsBase):
    def __init__(self,
                 address: Optional[str] = None,
                 port: Optional[int] = None,
                 uuid: Optional[str] = None,
                 flow: Optional[str] = None,
                 encryption: str = 'none'
                 ):
        super().__init__(address, port)
        self.uuid = uuid
        self.flow = flow
        self.encryption = encryption

    @property
    def id(self):
        return self.uuid

    @id.setter
    def id(self, value):
        self.uuid = value

    @classmethod
    def from_dict(cls, config: Dict) -> Self:
        vnext = config.get('vnext', [{}])[0]
        return cls(
            vnext.get('address', None),
            vnext.get('port', None),
            vnext.get('users', [{}])[0].get('id', None),
            vnext.get('users', [{}])[0].get('flow', None),
            vnext.get('users', [{}])[0].get('encryption', 'none'),
        )

    def to_dict(self):
        return {
            'vnext': [{
                'address': self.address,
                'port': self.port,
                'users': [{
                    'id': self.uuid,
                    'flow': self.flow,
                    'encryption': self.encryption,
                }]
            }]
        }


class TrojanSettings(ProtocolSettingsBase):
    def __init__(self,
                 address: Optional[str] = None,
                 port: Optional[int] = None,
                 password: Optional[str] = None
                 ):
        super().__init__(address, port)
        self.password = password

    @property
    def id(self):
        return self.password

    @id.setter
    def id(self, value):
        self.password = value

    @classmethod
    def from_dict(cls, config: Dict) -> Self:
        servers = config.get('servers', [{}])[0]
        return cls(
            servers.get('address', None),
            servers.get('port', None),
            servers.get('password', None),
        )

    def to_dict(self):
        return {
            'servers': [{
                'address': self.address,
                'port': self.port,
                'password': self.password,
            }]
        }


class ShadowsocksSettings(ProtocolSettingsBase):
    def __init__(self,
                 address: Optional[str] = None,
                 port: Optional[int] = None,
                 password: Optional[str] = None,
                 method: Optional[str] = None,
                 uot: Optional[bool] = None,
                 uot_version: Optional[int] = None):
        super().__init__(address, port)
        self.password = password
        self.method = method
        self.uot = uot
        self.uot_version = uot_version

    @property
    def id(self):
        return self.password

    @id.setter
    def id(self, value):
        self.password = value

    @classmethod
    def from_dict(cls, config: Dict) -> Self:
        servers = config.get('servers', [{}])[0]
        return cls(
            servers.get('address', None),
            servers.get('port', None),
            servers.get('password', None),
            servers.get('method', None),
            servers.get('uot', None),
            servers.get('UoTVersion', None),
        )

    def to_dict(self):
        return {
            'servers': [{
                'address': self.address,
                'port': self.port,
                'password': self.password,
                'uot': self.uot,
                'UoTVersion': self.uot_version,
            }]
        }


class Settings(SettingsBase):
    def __init__(self,
                 protocol):
        super().__init__()
        self.protocol = protocol

    @staticmethod
    def get_settings(protocol):
        try:
            protocol = Protocols(protocol)
        except ValueError:
            return None
        match protocol:
            case Protocols.VMess:
                return VmessSettings()
            case Protocols.VLESS:
                return VlessSettings()
            case Protocols.Trojan:
                return TrojanSettings()
            case Protocols.Shadowsocks:
                return ShadowsocksSettings()
            case _:
                return None

    @classmethod
    def from_dict(cls, protocol, config: Dict) -> Self:
        setting = cls.get_settings(protocol)
        if setting:
            return setting.from_dict(config)
        return None

    def to_dict(self):
        return {}
