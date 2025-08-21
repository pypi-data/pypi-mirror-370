# v2raypy

**v2raypy** is a Python library for working with V2Ray configurations and links. It allows you to parse, generate, and manipulate V2Ray nodes (VLESS, VMess, Trojan, Shadowsocks) in both dictionary and link format.

---

## 📦 Installation

```bash
pip install v2raypy
```

---

## 🚀 Getting Started

### Importing

```python
from v2ray import V2ray
```

---

## 📚 Features

- Parse links into config objects: `from_link()`
- Parse dictionaries into config objects: `from_dict()`
- Generate configuration dictionaries: `to_dict()`
- Generate shareable V2Ray links: `gen_link()`

---

## 🧪 Usage Examples

### 1. Load from a V2Ray link

```python
link = "vless://<uuid>@example.com:443?security=tls&type=ws#MyServer"
v = V2ray.from_link(link)
```

### 2. Load from a Python dictionary

```python
config = {
    "tag": "my-vless-node",
    "protocol": "vless",
    "settings": {
        "address": "example.com",
        "port": 443,
        "uuid": "<uuid>"
    },
    "streamSettings": {
        "network": "ws",
        "security": "tls"
    }
}

v = V2ray.from_dict(config)
```

### 3. Export to dictionary

```python
conf_dict = v.to_dict()
```

### 4. Generate a new V2Ray share link

```python
link = v.gen_link()
print(link)
```

---

## 🌐 Supported Protocols

- **VLESS**
- **VMess**
- **Trojan**
- **Shadowsocks**

Each with full support for stream types like TCP, KCP, WebSocket, gRPC, HTTP Upgrade, XHTTP, and TLS/REALITY security layers.

---

## 🛠️ Advanced Configuration

You can manipulate advanced options such as:

- `Mux`
- `SendThrough`
- `StreamSettings` (including complex nested settings like TLS, WS headers, GRPC options)

---

## 📜 Acknowledgements

- [3X-UI](https://github.com/MHSanaei/3x-ui/) (License: **GPL-3.0**): _3x-ui is a user interface for managing and configuring V2Ray, XRay, and related protocols, with features such as a web-based dashboard and advanced configuration management. It simplifies the setup process and provides a graphical interface for managing server configurations, routing, and security settings._

