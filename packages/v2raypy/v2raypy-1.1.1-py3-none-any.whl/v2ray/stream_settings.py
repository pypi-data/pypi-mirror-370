from typing import Dict, Self

from base import SettingsBase


class TcpStreamSettings(SettingsBase):
    def __init__(self, header_type='none', host=None, path=None):
        super().__init__()
        self.header_type = header_type
        self.host = host
        self.path = path

    @classmethod
    def from_dict(cls, config: Dict) -> Self:
        header = config.get('header')
        if not header:
            return cls()
        if header.get('type') == 'http' and header.get('request'):
            return cls(
                header_type=header.get('type'),
                host=','.join(header['request']['headers']['Host']),
                path=','.join(header['request']['path'])
            )
        return cls(header.get('type', 'none'), '', '')

    def to_dict(self):
        return {
            'header': {
                'type': self.header_type,
                **({
                       'request': {
                           'headers': {
                               'Host': [] if not self.host else self.host.split(',')
                           },
                           'path': ["/"] if not self.path else self.path.split(',')
                       }
                   } if self.header_type == 'http' else {}),
            }
        }


class WsStreamSettings(SettingsBase):
    def __init__(self,
                 path='/',
                 host='',
                 heartbeat_period=0
                 ):
        super().__init__()
        self.path = path
        self.host = host
        self.heartbeat_period = heartbeat_period

    @classmethod
    def from_dict(cls, config: Dict) -> Self:
        return cls(
            config.get('path', '/'),
            config.get('host', ''),
            config.get('heartbeatPeriod', 0),
        )

    def to_dict(self):
        return {
            'path': self.path,
            'host': self.host,
            'heartbeatPeriod': self.heartbeat_period,
        }


class GrpcStreamSettings(SettingsBase):
    def __init__(self,
                 service_name='',
                 authority='',
                 multi_mode=False,
                 ):
        super().__init__()
        self.service_name = service_name
        self.authority = authority
        self.multi_mode = multi_mode

    @classmethod
    def from_dict(cls, config: Dict) -> Self:
        return cls(
            config.get('serviceName', ''),
            config.get('authority', ''),
            config.get('multiMode', False),
        )

    def to_dict(self):
        return {
            'serviceName': self.service_name,
            'authority': self.authority,
            'multiMode': self.multi_mode,
        }


class KcpStreamSettings(SettingsBase):
    def __init__(self,
                 mtu=1350,
                 tti=50,
                 uplink_capacity=5,
                 downlink_capacity=20,
                 congestion=False,
                 read_buffer_size=2,
                 write_buffer_size=2,
                 header_type='none',
                 seed=''

                 ):
        super().__init__()
        self.mtu = mtu
        self.tti = tti
        self.uplink_capacity = uplink_capacity
        self.downlink_capacity = downlink_capacity
        self.congestion = congestion
        self.read_buffer_size = read_buffer_size
        self.write_buffer_size = write_buffer_size
        self.header_type = header_type
        self.seed = seed

    @classmethod
    def from_dict(cls, config: Dict) -> Self:
        return cls(
            config.get('mtu', 1350),
            config.get('tti', 50),
            config.get('uplinkCapacity', 5),
            config.get('downlinkCapacity', 20),
            config.get('congestion', False),
            config.get('readBufferSize', 2),
            config.get('writeBufferSize', 2),
            config['header']['type'] if config.get('header') else 'none',
            config.get('seed', ''),
        )

    def to_dict(self):
        return {
            'mtu': self.mtu,
            'tti': self.tti,
            'uplinkCapacity': self.uplink_capacity,
            'downlinkCapacity': self.downlink_capacity,
            'congestion': self.congestion,
            'readBufferSize': self.read_buffer_size,
            'writeBufferSize': self.write_buffer_size,
            'header': {
                'type': self.header_type,
            },
            'seed': self.seed,
        }


class HttpUpgradeStreamSettings(SettingsBase):
    def __init__(self,
                 path='/',
                 host='',
                 ):
        super().__init__()
        self.path = path
        self.host = host

    @classmethod
    def from_dict(cls, config: Dict) -> Self:
        return cls(
            config.get('path', '/'),
            config.get('host', ''),
        )

    def to_dict(self):
        return {
            'path': self.path,
            'host': self.host,
        }


class XHttpStreamSettings(SettingsBase):
    def __init__(self,
                 path='/',
                 host='',
                 mode='',
                 no_grpc_header=False,
                 sc_min_posts_interval_ms="30",
                 x_mux=None
                 ):
        super().__init__()
        if x_mux is None:
            x_mux = {
                'maxConcurrency': "16-32",
                'maxConnections': 0,
                'cMaxReuseTimes': 0,
                'hMaxRequestTimes': "600-900",
                'hMaxReusableSecs': "1800-3000",
                'hKeepAlivePeriod': 0,
            }
        self.path = path
        self.host = host
        self.mode = mode
        self.no_grpc_header = no_grpc_header
        self.sc_min_posts_interval_ms = sc_min_posts_interval_ms
        self.x_mux = x_mux

    @classmethod
    def from_dict(cls, config: Dict) -> Self:
        return cls(
            config.get('path', '/'),
            config.get('host', ''),
            config.get('mode', ''),
            config.get('noGRPCHeader', False),
            config.get('scMinPostsIntervalMs', "30"),
            config.get('xmux', None),
        )

    def to_dict(self):
        return {
            'path': self.path,
            'host': self.host,
            'mode': self.mode,
            'noGRPCHeader': self.no_grpc_header,
            'scMinPostsIntervalMs': self.sc_min_posts_interval_ms,
            'xmux': {
                'maxConcurrency': self.x_mux.get('maxConcurrency', "16-32"),
                'maxConnections': self.x_mux.get('maxConnections', 0),
                'cMaxReuseTimes': self.x_mux.get('cMaxReuseTimes', 0),
                'hMaxRequestTimes': self.x_mux.get('hMaxRequestTimes', "600-900"),
                'hMaxReusableSecs': self.x_mux.get('hMaxReusableSecs', "1800-3000"),
                'hKeepAlivePeriod': self.x_mux.get('hKeepAlivePeriod', 0),
            },
        }


class TlsStreamSettings(SettingsBase):
    def __init__(self,
                 server_name='',
                 alpn=None,
                 fingerprint='',
                 allow_insecure=False,
                 ):
        super().__init__()
        if alpn is None:
            alpn = []
        self.server_name = server_name
        self.alpn = alpn
        self.fingerprint = fingerprint
        self.allow_insecure = allow_insecure

    @classmethod
    def from_dict(cls, config: Dict) -> Self:
        return cls(
            config.get('serverName', ''),
            config.get('alpn', None),
            config.get('fingerprint', ''),
            config.get('allowInsecure', False),
        )

    def to_dict(self):
        return {
            'serverName': self.server_name,
            'alpn': self.alpn,
            'fingerprint': self.fingerprint,
            'allowInsecure': self.allow_insecure,
        }


class RealityStreamSettings(SettingsBase):
    def __init__(self,
                 public_key='',
                 fingerprint='',
                 server_name='',
                 short_id='',
                 spider_x='/'
                 ):
        super().__init__()
        self.public_key = public_key
        self.fingerprint = fingerprint
        self.server_name = server_name
        self.short_id = short_id
        self.spider_x = spider_x

    @classmethod
    def from_dict(cls, config: Dict) -> Self:
        return cls(
            config.get('publicKey', ''),
            config.get('fingerprint', ''),
            config.get('serverName', ''),
            config.get('shortId', ''),
            config.get('spiderX', '/'),
        )

    def to_dict(self):
        return {
            'publicKey': self.public_key,
            'fingerprint': self.fingerprint,
            'serverName': self.server_name,
            'shortId': self.short_id,
            'spiderX': self.spider_x,
        }


class SockoptStreamSettings(SettingsBase):
    def __init__(self,
                 dialer_proxy="",
                 tcp_fast_open=False,
                 tcp_keep_alive_interval=0,
                 tcp_mptcp=False,
                 penetrate=False,
                 address_port_strategy='none',
                 ):
        super().__init__()
        self.dialer_proxy = dialer_proxy
        self.tcp_fast_open = tcp_fast_open
        self.tcp_keep_alive_interval = tcp_keep_alive_interval
        self.tcp_mptcp = tcp_mptcp
        self.penetrate = penetrate
        self.address_port_strategy = address_port_strategy

    @classmethod
    def from_dict(cls, config: Dict) -> Self:
        if not config: return None;
        return cls(
            config.get('dialerProxy', ''),
            config.get('tcpFastOpen', False),
            config.get('tcpKeepAliveInterval', 0),
            config.get('tcpMptcp', False),
            config.get('penetrate', False),
            config.get('addressPortStrategy', 'none'),
        )

    def to_dict(self):
        return {
            'dialerProxy': self.dialer_proxy,
            'tcpFastOpen': self.tcp_fast_open,
            'tcpKeepAliveInterval': self.tcp_keep_alive_interval,
            'tcpMptcp': self.tcp_mptcp,
            'penetrate': self.penetrate,
            'addressPortStrategy': self.address_port_strategy,
        }


class Mux(SettingsBase):
    def __init__(self,
                 enable=False,
                 concurrency=8,
                 xudp_concurrency=16,
                 xudp_proxy_udp443="reject"
                 ):
        super().__init__()
        self.enable = enable
        self.concurrency = concurrency
        self.xudp_concurrency = xudp_concurrency
        self.xudp_proxy_udp443 = xudp_proxy_udp443

    @classmethod
    def from_dict(cls, config: Dict) -> Self:
        return cls(
            config.get('enable', False),
            config.get('concurrency', 8),
            config.get('xudpConcurrency', 16),
            config.get('xudpProxyUDP443', "reject"),
        )

    def to_dict(self):
        return {
            'enable': self.enable,
            'concurrency': self.concurrency,
            'xudpConcurrency': self.xudp_concurrency,
            'xudpProxyUDP443': self.xudp_proxy_udp443,
        }


class StreamSettings(SettingsBase):
    def __init__(self,
                 network='tcp',
                 security='none',
                 tls_settings=TlsStreamSettings(),
                 reality_settings=RealityStreamSettings(),
                 tcp_settings=TcpStreamSettings(),
                 kcp_settings=KcpStreamSettings(),
                 ws_settings=WsStreamSettings(),
                 grpc_settings=GrpcStreamSettings(),
                 httpupgrade_settings=HttpUpgradeStreamSettings(),
                 xhttp_settings=XHttpStreamSettings(),
                 sockopt=None
                 ):
        super().__init__()
        self.network = network
        self.security = security
        self.tls = tls_settings
        self.reality = reality_settings
        self.tcp = tcp_settings
        self.kcp = kcp_settings
        self.ws = ws_settings
        self.grpc = grpc_settings
        self.httpupgrade = httpupgrade_settings
        self.xhttp = xhttp_settings
        self.sockopt = sockopt

    @classmethod
    def from_dict(cls, config: Dict) -> Self:
        return cls(
            config.get('network', 'tcp'),
            config.get('security', 'none'),
            TlsStreamSettings.from_dict(config.get('tlsStreamSettings', {})),
            RealityStreamSettings.from_dict(config.get('realitySettings', {})),
            TcpStreamSettings.from_dict(config.get('tcpSettings', {})),
            KcpStreamSettings.from_dict(config.get('kcpSettings', {})),
            WsStreamSettings.from_dict(config.get('wsSettings', {})),
            GrpcStreamSettings.from_dict(config.get('grpcSettings', {})),
            HttpUpgradeStreamSettings.from_dict(config.get('httpupgradeSettings', {})),
            XHttpStreamSettings.from_dict(config.get('xhttpSettings', {})),
            SockoptStreamSettings.from_dict(config.get('sockopt', {})),
        )

    def to_dict(self):
        network = self.network
        return {
            'network': network,
            'security': self.security,
            **({'tlsSettings': self.tls.to_dict()} if self.security == 'tls' else {}),
            **({'realitySettings': self.reality.to_dict()} if self.security == 'reality' else {}),
            **({'tcpSettings': self.tcp.to_dict()} if network == 'tcp' else {}),
            **({'kcpSettings': self.tcp.to_dict()} if network == 'kcp' else {}),
            **({'wsSettings': self.tcp.to_dict()} if network == 'ws' else {}),
            **({'grpcSettings': self.tcp.to_dict()} if network == 'grpc' else {}),
            **({'httpupgradeSettings': self.tcp.to_dict()} if network == 'httpupgrade' else {}),
            **({'xhttpSettings': self.tcp.to_dict()} if network == 'xhttp' else {}),
            **({'sockopt': self.sockopt.to_dict()} if self.sockopt else {}),
        }
