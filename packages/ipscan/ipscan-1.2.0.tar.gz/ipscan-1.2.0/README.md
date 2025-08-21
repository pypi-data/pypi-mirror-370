<p align="center">
    <img src="assets/banner.svg" alt="ipscan banner" width="100%" />
</p>

<div align="center">

# ipscan

Fast IP scanner — multithreaded Ping and ARP for Windows

[![PyPI version](https://img.shields.io/pypi/v/ipscan?logo=pypi&label=PyPI)](https://pypi.org/project/ipscan/) 
![Python](https://img.shields.io/pypi/pyversions/ipscan?logo=python) 
![OS](https://img.shields.io/badge/OS-Windows-blue?logo=windows) 
![License](https://img.shields.io/github/license/Wing9897/ipscan?color=success)

Language:
[English](README.md) · [繁體中文](README.zh-TW.md) · [简体中文](README.zh-CN.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Deutsch](README.de.md) · [Français](README.fr.md) · [Italiano](README.it.md) · [Español](README.es.md) · [Português BR](README.pt-BR.md) · [Русский](README.ru.md)

</div>

---

## Table of contents

- Quick start
- Features
- CLI tools
- Python API
- Performance notes
- Requirements
- Contributing

---

## Quick start

Install from PyPI:

```bash
pip install ipscan
```

Optional: enable raw ARP engine with scapy support

```bash
pip install "ipscan[arp]"
```

### CLI

```bash
fping           # High-speed continuous ping (interactive)
sping           # Simple range ping scan
sarp            # ARP range scan
```

### Python API

Ping scan:

```python
from ipscan import ping_range, PingScanner

online_hosts = ping_range("192.168.1.1", "192.168.1.254")

scanner = PingScanner(timeout=1.0)
results = scanner.scan_range("10.0.0.1", "10.0.0.100")
```

ARP scan:

```python
from ipscan import arp_range, ArpScanner

host_info = arp_range("192.168.1.1", "192.168.1.254")
for ip, mac in host_info.items():
        print(f"{ip} -> {mac}")

scanner = ArpScanner()
results = scanner.scan_range("10.0.0.1", "10.0.0.100")
```

## Features

- Multithreaded scanning for high speed
- Ping and ARP scans with simple API
- Progress bar and clean output
- Tiny dependency footprint

### ARP engines

- system (default):
    - Windows: WinAPI SendARP
    - Linux/macOS: ip neigh / arp -n, with a one-off ping or arping to populate cache
- scapy: raw ARP broadcast via scapy (fast, requires admin/root and Npcap on Windows)
- auto: use scapy when available/allowed, else fallback to system

Select engine in code:

```python
from ipscan import arp_range
hosts = arp_range("192.168.1.1","192.168.1.254", engine="scapy", interface="eth0")
```

CLI will also prompt for engine/interface; you can set environment variables:

- IPSCAN_ARP_ENGINE=system|scapy|auto
- IPSCAN_ARP_IFACE=eth0

## Performance notes

- Ping: scans /24 in a few seconds on typical hardware
- ARP: very fast on local networks

## Requirements

- Python 3.7+
- Windows / Linux / macOS supported; on Linux/macOS, ARP uses system tools (ip/arp/arping)
 - For scapy engine: root/admin (Linux/macOS) or Npcap (Windows)

## Contributing

Issues and PRs are welcome. If you like this project, consider starring it.

---

<div align="center">
Made with ❤️ for network tinkerers.
</div>
