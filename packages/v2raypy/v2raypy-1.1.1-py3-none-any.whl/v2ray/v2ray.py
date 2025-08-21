import base64
import json
from typing import Dict, Self
import re
from urllib.parse import urlparse, parse_qs, unquote, urlencode, urlunparse, quote

from base import SettingsBase
from stream_settings import StreamSettings, TcpStreamSettings, KcpStreamSettings, WsStreamSettings, GrpcStreamSettings, \
    HttpUpgradeStreamSettings, XHttpStreamSettings, TlsStreamSettings, Mux, RealityStreamSettings
from protocols_settings import Protocols, VmessSettings, VlessSettings, TrojanSettings, ShadowsocksSettings, Settings


class V2ray(SettingsBase):

    def __init__(self,
                 tag='',
                 protocol: Protocols = Protocols.VLESS,
                 settings=None,
                 stream_settings=StreamSettings(),
                 send_through=None,
                 mux=Mux()
                 ):
        super().__init__()
        self.tag = tag
        self.protocol = protocol
        self.settings = settings if settings else Settings.get_settings(protocol)
        self.stream = stream_settings
        self.send_through = send_through
        self.mux = mux

    @property
    def id(self):
        return self.settings.id

    @id.setter
    def id(self, value):
        self.settings.id = value

    @property
    def address(self):
        return self.settings.address

    @address.setter
    def address(self, value):
        self.settings.address = value

    @property
    def port(self):
        return self.settings.port

    @port.setter
    def port(self, value):
        self.settings.port = value

    def can_enable_stream(self):
        return self.protocol in [Protocols.VMess, Protocols.VLESS, Protocols.Trojan, Protocols.Shadowsocks]

    @classmethod
    def from_dict(cls, config: Dict) -> Self:
        return cls(
            config.get('tag', ''),
            config.get('protocol', Protocols.VLESS),
            Settings.from_dict(config.get('protocol', Protocols.VLESS), config.get('settings', {})),
            StreamSettings.from_dict(config.get('streamSettings', {})),
            config.get('sendThrough', None),
            Mux.from_dict(config.get('mux', {})),
        )

    def to_dict(self):
        stream = None
        if self.can_enable_stream():
            stream = self.stream.to_dict()
        else:
            if self.stream and self.stream.sockopt:
                stream = {'sockopt': self.stream.sockopt.to_dict()}
        return {
            'tag': self.tag,
            'protocol': self.protocol,
            'settings': self.settings.to_dict() if isinstance(self.settings, SettingsBase) else self.settings,
            'streamSettings': stream,
            **({'sendThrough': self.send_through} if self.send_through else {}),
            **({'mux': self.mux} if self.mux and self.mux.enable else {}),
        }

    @classmethod
    def from_link(cls, link):
        parts = link.split("://", 1)
        if len(parts) != 2:
            return None

        scheme = parts[0].lower()
        value = parts[1]

        try:
            protocol = Protocols(scheme) if scheme != 'ss' else scheme
        except ValueError:
            return None

        match protocol:
            case Protocols.VMess:
                return cls.from_vmess_link(json.loads(base64.urlsafe_b64decode(value).decode()))
            case Protocols.VLESS | Protocols.Trojan | 'ss':
                return cls.from_param_link(link)
            case _:
                return None

    @classmethod
    def from_vmess_link(cls, config):
        network = config.get('net', 'tcp')
        stream = StreamSettings(network, config.get('tls', 'none'))
        if network == 'tcp':
            stream.tcp = TcpStreamSettings(
                config.get('type', 'none'),
                config.get('host', ''),
                config.get('path', ''),
            )
        elif network == 'kcp':
            stream.kcp = KcpStreamSettings(
                header_type=config.get('type', 'none'),
                seed=config.get('path', ''),
            )
        elif network == 'ws':
            stream.ws = WsStreamSettings(
                config.get('path', '/'),
                config.get('host', '')
            )
        elif network == 'grpc':
            stream.grpc = GrpcStreamSettings(
                config.get('path', ''),
                config.get('authority', ''),
                config.get('type', 'single') == 'multi'
            )
        elif network == 'httpupgrade':
            stream.httpupgrade = HttpUpgradeStreamSettings(
                config.get('path', '/'),
                config.get('host', '')
            )
        elif network == 'xhttp':
            stream.xhttp = XHttpStreamSettings(
                config.get('path', '/'),
                config.get('host', ''),
                config.get('mode', '')
            )

        if config.get('tls') and config['tls'] == 'tls':
            stream.tls = TlsStreamSettings(
                config.get('sni', ''),
                config['alpn'].split(',') if config.get('alpn') else [],
                config.get('fp', ''),
                config.get('allowInsecure', False)
            )
        return cls(
            config['ps'],
            Protocols.VMess,
            VmessSettings(
                config.get('add'),
                int(config.get('port', 80)),
                config.get('id'),
                config.get('scy')
            ),
            stream
        )

    @classmethod
    def from_param_link(cls, link):
        url = urlparse(link)
        query_params = parse_qs(url.query)

        network = query_params.get('type', ['tcp'])[0]
        security = query_params.get('security', ['none'])[0]
        stream = StreamSettings(network, security)

        header_type = query_params.get('headerType', ['none'])[0]
        host = query_params.get('host', [''])[0]
        path = query_params.get('path', [''])[0]
        mode = query_params.get('mode', [''])[0]

        if network == 'tcp' or network == 'none':
            stream.tcp = TcpStreamSettings(header_type, host, path)
        elif network == 'kcp':
            stream.kcp = KcpStreamSettings(header_type=header_type, seed=path)
        elif network == 'ws':
            stream.ws = WsStreamSettings(path, host)
        elif network == 'grpc':
            stream.grpc = GrpcStreamSettings(
                query_params.get('serviceName', [''])[0],
                query_params.get('authority', [''])[0],
                mode == 'multi'
            )
        elif network == 'httpupgrade':
            stream.httpupgrade = HttpUpgradeStreamSettings(path, host)
        elif network == 'xhttp':
            stream.xhttp = XHttpStreamSettings(path, host, mode)

        if security == 'tls':
            fp = query_params.get('fp', ['none'])[0]
            alpn = query_params.get('alpn', [None])[0]
            allow_insecure = query_params.get('allowInsecure', [False])[0]
            sni = query_params.get('sni', [''])[0]
            stream.tls = TlsStreamSettings(sni, alpn and alpn.split(','), fp, allow_insecure == 1)

        if security == 'reality':
            pbk = query_params.get('pbk', [''])[0]
            fp = query_params.get('fp', [''])[0]
            sni = query_params.get('sni', [''])[0]
            sid = query_params.get('sid', [''])[0]
            spx = query_params.get('spx', [''])[0]
            stream.reality = RealityStreamSettings(pbk, fp, sni, sid, spx)

        regex = r'([^@]+)://([^@]+)@(.+):(\d+)(.*)$'
        match = re.match(regex, link)

        if not match:
            return None
        protocol, user_data, address, port = match.groups()[:4]
        port = int(port)
        if protocol == 'ss':
            protocol = 'shadowsocks'
            user_data = base64.urlsafe_b64decode(user_data).decode().split(':')

        try:
            protocol = Protocols(protocol)
        except ValueError:
            return None

        settings = None
        match protocol:
            case Protocols.VLESS:
                settings = VlessSettings(address, port, user_data, query_params.get('flow', [''])[0])
            case Protocols.Trojan:
                settings = TrojanSettings(address, port, user_data)
            case Protocols.Shadowsocks:
                method = user_data.pop(0)
                settings = ShadowsocksSettings(address, port, ':'.join(user_data), method, True)
            case _:
                return None
        remark = unquote(url.fragment)
        remark = remark if remark else f'out-{protocol.value}-{port}'
        return cls(remark, protocol, settings, stream)

    def gen_link(self, address='', port=None, force_tls='same', remark='', client=None, ):
        if client is None:
            client = {}
        port = port or self.settings.port
        address = address or self.settings.address
        remark = remark or self.tag
        match self.protocol:
            case Protocols.VMess:
                id = client.get('id', self.settings and self.settings.id)
                security = client.get('security', self.settings and self.settings.security)
                return self.gen_vmess_link(id, security, address, port, force_tls, remark)
            case Protocols.VLESS:
                id = client.get('id', self.settings and self.settings.id)
                return self.gen_vless_link(id, client.get('flow'), address, port, force_tls, remark)
            case Protocols.Shadowsocks:
                password = client.get('password', self.settings and self.settings.id)
                return self.gen_ss_link(password, address, port, force_tls, remark)
            case Protocols.Trojan:
                password = client.get('password', self.settings and self.settings.id)
                return self.gen_trojan_link(password, address, port, force_tls, remark)
            case _:
                return ''

    def gen_vmess_link(self, client_id, security, address='', port=None, force_tls='same', remark=''):
        if self.protocol != Protocols.VMess:
            return ''
        tls = self.stream.security if force_tls == 'same' else force_tls
        obj = {
            'v': 2,
            'ps': remark,
            'add': address,
            'port': port,
            'id': client_id,
            'scy': security,
            'net': self.stream.network,
            'tls': tls,
        }
        network = self.stream.network
        if network == 'tcp':
            tcp = self.stream.tcp
            obj['type'] = tcp.header_type
            if tcp.header_type == 'http':
                obj['path'] = tcp.path or ''
                if tcp.host:
                    obj['host'] = tcp.host
        elif network == 'kcp':
            kcp = self.stream.kcp
            obj['type'] = kcp.header_type
            obj['path'] = kcp.seed or ''
        elif network == 'ws':
            ws = self.stream.ws
            obj['path'] = ws.path
            if ws.host:
                obj['host'] = ws.host
        elif network == 'grpc':
            grpc = self.stream.grpc
            obj['path'] = grpc.service_name
            if grpc.authority:
                obj['authority'] = grpc.authority
            if grpc.multi_mode:
                obj['type'] = 'multi'
        elif network == 'httpupgrade':
            httpupgrade = self.stream.httpupgrade
            obj['path'] = httpupgrade.path
            if httpupgrade.host:
                obj['host'] = httpupgrade.host
        elif network == 'xhttp':
            xhttp = self.stream.xhttp
            obj['path'] = xhttp.path
            if xhttp.host:
                obj['host'] = xhttp.host
            obj['type'] = xhttp.mode

        if tls == 'tls':
            if self.stream.tls.server_name:
                obj['sni'] = self.stream.tls.server_name
            if self.stream.tls.fingerprint:
                obj['fp'] = self.stream.tls.fingerprint
            if self.stream.tls.alpn:
                obj['alpn'] = ','.join(self.stream.tls.alpn)
            if self.stream.tls.allow_insecure:
                obj['allowInsecure'] = self.stream.tls.allow_insecure

        return 'vmess://' + base64.urlsafe_b64encode(json.dumps(obj).encode()).decode()

    def _get_param_link_network_parameters(self):
        network = self.stream.network
        params = {'type': network}
        match network:
            case 'tcp':
                tcp = self.stream.tcp
                if tcp.header_type == 'http':
                    params['path'] = tcp.path or ''
                    if tcp.host:
                        params['host'] = tcp.host
                    params['headerType'] = 'http'
            case 'kcp':
                kcp = self.stream.kcp
                params['headerType'] = kcp.header_type
                params['seed'] = kcp.seed
            case 'ws':
                ws = self.stream.ws
                params['path'] = ws.path
                if ws.host:
                    params['host'] = ws.host
            case 'grpc':
                grpc = self.stream.grpc
                params['serviceName'] = grpc.service_name
                if grpc.authority:
                    params['authority'] = grpc.authority
                if grpc.multi_mode:
                    params['mode'] = 'multi'
            case 'httpupgrade':
                httpupgrade = self.stream.httpupgrade
                params['path'] = httpupgrade.path
                if httpupgrade.host:
                    params['host'] = httpupgrade.host
            case 'xhttp':
                xhttp = self.stream.xhttp
                params['path'] = xhttp.path
                if xhttp.host:
                    params['host'] = xhttp.host
                params['mode'] = xhttp.mode
            case _:
                return None
        return params

    def _get_param_link_tls_parameters(self):
        params = {'fp': self.stream.tls.fingerprint, 'alpn': ','.join(self.stream.tls.alpn)}
        if self.stream.tls.allow_insecure:
            params['allowInsecure'] = 1
        if self.stream.tls.server_name:
            params['sni'] = self.stream.tls.server_name
        return params

    def _get_param_link_reality_parameters(self):
        params = {'security': 'reality', 'pbk': self.stream.reality.public_key, 'fp': self.stream.reality.fingerprint}
        if self.stream.reality.server_name:
            params['sni'] = self.stream.reality.server_name
        if self.stream.reality.short_id:
            params['sni'] = self.stream.reality.short_id
        if self.stream.reality.spider_x:
            params['spx'] = self.stream.reality.spider_x
        return params

    def gen_vless_link(self, client_id, flow, address='', port=None, force_tls='same', remark=''):
        params = self._get_param_link_network_parameters()
        uuid = client_id
        security = self.stream.security if force_tls == 'same' else force_tls

        if security == 'tls':
            params['security'] = 'tls'
            if self.stream.security == 'tls':
                params.update(self._get_param_link_tls_parameters())
                if self.stream.network == 'tcp' and flow:
                    params['flow'] = flow
        elif security == 'reality':
            params.update(self._get_param_link_reality_parameters())
            if self.stream.network == 'tcp' and flow:
                params['flow'] = flow
        else:
            params['security'] = 'none'

        link = f'vless://{uuid}@{address}:{port}'
        url = list(urlparse(link))
        url[4] = urlencode(params)
        url[5] = quote(remark)
        url = urlunparse(url)
        return url

    def gen_ss_link(self, client_password, address='', port=None, force_tls='same', remark=''):
        params = self._get_param_link_network_parameters()
        settings = self.settings
        security = self.stream.security if force_tls == 'same' else force_tls

        if security == 'tls':
            params['security'] = 'tls'
            if self.stream.security == 'tls':
                params.update(self._get_param_link_tls_parameters())

        password = []
        if self.settings and self.settings.method[0:4] == "2022":
            password.append(settings.password)
        if self.settings and self.settings.method != '2022-blake3-chacha20-poly1305':
            password.append(client_password)
        user_info = f"{settings.method}:{':'.join(password)}"

        encoded_user_info = base64.urlsafe_b64encode(user_info.encode()).decode().rstrip('=')
        link = f'ss://{encoded_user_info}@{address}:{port}'
        url = list(urlparse(link))
        url[4] = urlencode(params)
        url[5] = quote(remark)
        url = urlunparse(url)
        return url

    def gen_trojan_link(self, client_password, address='', port=None, force_tls='same', remark=''):
        params = self._get_param_link_network_parameters()
        security = self.stream.security if force_tls == 'same' else force_tls

        if security == 'tls':
            params['security'] = 'tls'
            if self.stream.security == 'tls':
                params.update(self._get_param_link_tls_parameters())
        elif security == 'reality':
            return self._get_param_link_reality_parameters()
        else:
            params['security'] = 'none'

        link = f'trojan://{client_password}@{address}:{port}'
        url = list(urlparse(link))
        url[4] = urlencode(params)
        url[5] = quote(remark)
        url = urlunparse(url)
        return url
