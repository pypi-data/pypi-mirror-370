import ctypes
import threading
import ipaddress
import time
import platform
import os
import subprocess
import re
from tqdm import tqdm
from typing import List, Dict, Optional



class ArpScanner:
	def __init__(self, show_progress: bool = True, engine: str = "system", interface: Optional[str] = None):
		"""
		engine: 'auto' | 'system' | 'scapy'
		- system: use OS tools/APIs (Windows SendARP; Linux/macOS ip/arp/arping)
		- scapy: use raw ARP via scapy.srp (requires admin/root and Npcap on Windows)
		- auto: prefer scapy when available and likely permitted; otherwise fallback to system
		"""
		self.show_progress = show_progress
		self.engine = engine
		self.interface = interface
		self.results: Dict[str, str] = {}
		self.results_lock = threading.Lock()

	def _run_cmd(self, args: List[str], timeout: float = 2.0) -> str:
		try:
			out = subprocess.check_output(args, stderr=subprocess.STDOUT, timeout=timeout)
			return out.decode('utf-8', errors='ignore')
		except Exception:
			return ""

	def _get_mac_windows(self, ip: str) -> Optional[str]:
		try:
			iphlpapi = ctypes.windll.iphlpapi
			inet_addr = ctypes.windll.ws2_32.inet_addr
			SendARP = iphlpapi.SendARP
			dest_ip = inet_addr(ip.encode('utf-8'))
			mac_addr = ctypes.create_string_buffer(6)
			mac_addr_len = ctypes.c_ulong(6)
			res = SendARP(dest_ip, 0, ctypes.byref(mac_addr), ctypes.byref(mac_addr_len))
			if res == 0:
				return ':'.join('%02x' % b for b in mac_addr.raw[:6])
		except Exception:
			pass
		return None

	def _parse_mac(self, text: str) -> Optional[str]:
		m = re.search(r"([0-9A-Fa-f]{2}(:|-)){5}[0-9A-Fa-f]{2}", text)
		return m.group(0).replace('-', ':').lower() if m else None

	def _get_mac_linux(self, ip: str) -> Optional[str]:
		# 1) Try ip neigh
		txt = self._run_cmd(["ip", "neigh", "show", ip])
		mac = self._parse_mac(txt)
		if mac:
			return mac
		# 2) Try to nudge ARP: ping once then read again
		ping_out = self._run_cmd(["ping", "-c", "1", "-W", "1", ip], timeout=1.5)
		txt = self._run_cmd(["ip", "neigh", "show", ip])
		mac = self._parse_mac(txt)
		if mac:
			return mac
		# 3) Fallback to arp -n
		txt = self._run_cmd(["arp", "-n", ip])
		mac = self._parse_mac(txt)
		if mac:
			return mac
		# 4) Best-effort arping (may require sudo on some systems); try both -w/-W variants
		arping_out = self._run_cmd(["arping", "-c", "1", "-w", "1", ip], timeout=2.0)
		txt = self._run_cmd(["ip", "neigh", "show", ip]) or self._run_cmd(["arp", "-n", ip])
		mac = self._parse_mac(txt)
		if mac:
			return mac
		# Gentle hinting for missing tools (no exceptions, just informative when verbose env is on)
		if os.getenv('IPSCAN_DEBUG', '0') == '1':
			missing = []
			if not ping_out:
				missing.append('ping')
			if not arping_out:
				missing.append('arping')
			if missing:
				print(f"[ipscan] Hint: tools not found or no output: {', '.join(missing)}. Install iproute2/net-tools/arping as needed.")
		return None

	def _get_mac_macos(self, ip: str) -> Optional[str]:
		# macOS: use arp -n directly; if empty, ping once to populate cache
		txt = self._run_cmd(["arp", "-n", ip])
		mac = self._parse_mac(txt)
		if mac:
			return mac
		# Ping once; macOS ping doesn't support -W as Linux; keep short count
		ping_out = self._run_cmd(["ping", "-c", "1", ip], timeout=1.5)
		txt = self._run_cmd(["arp", "-n", ip])
		mac = self._parse_mac(txt)
		if mac:
			return mac
		if os.getenv('IPSCAN_DEBUG', '0') == '1' and not ping_out:
			print("[ipscan] Hint: 'ping' produced no output; ensure it is available and accessible.")
		return None

	def get_mac(self, ip: str) -> Optional[str]:
		osname = platform.system().lower()
		if osname == 'windows':
			return self._get_mac_windows(ip)
		if osname == 'linux':
			return self._get_mac_linux(ip)
		if osname == 'darwin':
			return self._get_mac_macos(ip)
		# Unknown OS: best-effort using arp -n
		txt = self._run_cmd(["arp", "-n", ip])
		return self._parse_mac(txt)

	def _can_use_scapy(self) -> bool:
		try:
			import scapy.all as scapy  # noqa: F401
			# On Linux/macOS, sending raw frames usually needs root
			if os.name != 'nt' and hasattr(os, 'geteuid') and os.geteuid() != 0:
				return False
			return True
		except Exception:
			return False

	def _scan_with_scapy(self, ip_list: List[str]) -> Dict[str, str]:
		"""Use scapy to broadcast ARP requests for the given IPs in one or few batches."""
		try:
			from scapy.all import ARP, Ether, srp, conf  # type: ignore
		except Exception:
			return {}
		# Select interface if provided
		if self.interface:
			conf.iface = self.interface
		# Scapy accepts a comma-separated range/list in ARP pdst
		pdst = ",".join(ip_list)
		pkt = Ether(dst="ff:ff:ff:ff:ff:ff")/ARP(pdst=pdst)
		try:
			ans, _ = srp(pkt, timeout=1.5, inter=0, verbose=0)
		except PermissionError:
			return {}
		except Exception:
			return {}
		out: Dict[str, str] = {}
		for _, rcv in ans:
			ip = getattr(rcv, 'psrc', None)
			mac = getattr(rcv, 'hwsrc', None)
			if ip and mac:
				out[str(ip)] = str(mac).lower()
		return out

	def scan_ip(self, ip: str, pbar: Optional[tqdm] = None) -> None:
		mac = self.get_mac(ip)
		if mac and mac != "00:00:00:00:00:00":
			with self.results_lock:
				self.results[ip] = mac
		if pbar:
			pbar.update(1)

	def scan_range(self, start_ip: str, end_ip: str) -> Dict[str, str]:
		self.results.clear()
		ip_list = [
			str(ipaddress.IPv4Address(ip))
			for ip in range(
				int(ipaddress.IPv4Address(start_ip)), int(ipaddress.IPv4Address(end_ip)) + 1
			)
		]

		# Try scapy fast-path if requested/available
		if self.engine in ("scapy", "auto") and self._can_use_scapy():
			res = self._scan_with_scapy(ip_list)
			if res or self.engine == "scapy":
				self.results.update(res)
				return self.results.copy()

		# Progress bar description: Chinese|English
		pbar = (
			tqdm(total=len(ip_list), desc="ARP掃描|ARP Scan", ncols=80)
			if self.show_progress
			else None
		)

		threads: List[threading.Thread] = []
		for ip in ip_list:
			t = threading.Thread(target=self.scan_ip, args=(ip, pbar))
			t.start()
			threads.append(t)

		for t in threads:
			t.join()

		if pbar:
			pbar.close()

		return self.results.copy()

	def scan_list(self, ip_list: List[str]) -> Dict[str, str]:
		self.results.clear()

		# Try scapy fast-path if requested/available
		if self.engine in ("scapy", "auto") and self._can_use_scapy():
			res = self._scan_with_scapy(ip_list)
			if res or self.engine == "scapy":
				self.results.update(res)
				return self.results.copy()

		# Progress bar description: Chinese|English
		pbar = (
			tqdm(total=len(ip_list), desc="ARP掃描|ARP Scan", ncols=80)
			if self.show_progress
			else None
		)

		threads: List[threading.Thread] = []
		for ip in ip_list:
			t = threading.Thread(target=self.scan_ip, args=(ip, pbar))
			t.start()
			threads.append(t)

		for t in threads:
			t.join()

		if pbar:
			pbar.close()

		return self.results.copy()


def arp_range(start_ip: str, end_ip: str, show_progress: bool = True, engine: str = "system", interface: Optional[str] = None) -> Dict[str, str]:
	return ArpScanner(show_progress=show_progress, engine=engine, interface=interface).scan_range(start_ip, end_ip)


def arp_list(ip_list: List[str], show_progress: bool = True, engine: str = "system", interface: Optional[str] = None) -> Dict[str, str]:
	return ArpScanner(show_progress=show_progress, engine=engine, interface=interface).scan_list(ip_list)


def main():
	start_ip = input('請輸入起始 IP 地址|Start IP: ').strip()
	end_ip = input('請輸入結束 IP 地址|End IP: ').strip()

	# Optional engine selection
	default_engine = os.getenv('IPSCAN_ARP_ENGINE', 'system').strip().lower() or 'system'
	engine_in = input(f"選擇引擎 system/scapy/auto (預設 {default_engine})|Engine system/scapy/auto (default {default_engine}): ").strip().lower()
	engine = engine_in if engine_in in ('system', 'scapy', 'auto') else default_engine

	# Optional interface (primarily for scapy)
	iface = os.getenv('IPSCAN_ARP_IFACE', '').strip()
	iface_in = input(f"網卡介面（可空）|Interface (optional) [{iface}]: ").strip()
	interface = iface_in or iface or None

	start_time = time.time()
	print(f"開始掃描從 {start_ip} 到 {end_ip} 的 IP 地址...|Starting scan from {start_ip} to {end_ip}...")

	host_results = arp_range(start_ip, end_ip, engine=engine, interface=interface)

	print("正在收集最後的回應...|Collecting final replies...")
	time.sleep(1)

	total_time = time.time() - start_time
	ip_count = int(ipaddress.IPv4Address(end_ip)) - int(ipaddress.IPv4Address(start_ip)) + 1

	print("掃描結束|Scan completed")
	print(f"總共掃描了 {ip_count} 個 IP 地址|Total scanned: {ip_count}")
	print(f"總耗時: {total_time:.2f} 秒|Total time: {total_time:.2f} s")
	print(f"平均每個 IP 耗時: {total_time/ip_count:.4f} 秒|Avg per IP: {total_time/ip_count:.6f} s")

	if host_results:
		print(f"\n📋 在線主機列表 ({len(host_results)} 個)|Online hosts: ({len(host_results)})")
		print("-" * 50)
		for ip in sorted(host_results, key=lambda x: ipaddress.IPv4Address(x)):
			print(f"  {ip:<15} -> {host_results[ip]}|MAC")
	else:
		print("\n❌ 沒有發現在線主機|No online hosts found")

