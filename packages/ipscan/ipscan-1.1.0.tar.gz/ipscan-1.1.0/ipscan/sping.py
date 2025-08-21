import ping3
import threading
import ipaddress
import time
from tqdm import tqdm
from typing import List, Set, Optional


class PingScanner:
	def __init__(self, timeout: float = 0.5, show_progress: bool = True):
		self.timeout = timeout
		self.show_progress = show_progress
		self.results: Set[str] = set()
		self.results_lock = threading.Lock()

	def ping_host(self, ip_address: str, pbar: Optional[tqdm] = None) -> None:
		try:
			response_time = ping3.ping(str(ip_address), timeout=self.timeout)
			if response_time is not None and response_time is not False:
				with self.results_lock:
					self.results.add(ip_address)
		except (ping3.errors.HostUnknown, ping3.errors.TimeExceeded):
			pass
		if pbar:
			pbar.update(1)

	def scan_range(self, start_ip: str, end_ip: str) -> Set[str]:
		self.results.clear()
		ip_addresses = [
			str(ipaddress.IPv4Address(ip))
			for ip in range(
				int(ipaddress.IPv4Address(start_ip)), int(ipaddress.IPv4Address(end_ip)) + 1
			)
		]

		# Progress bar description: Chinese|English
		pbar = (
			tqdm(total=len(ip_addresses), desc="Ping掃描|Ping Scan", ncols=80)
			if self.show_progress
			else None
		)

		threads: List[threading.Thread] = []
		for ip_address in ip_addresses:
			t = threading.Thread(target=self.ping_host, args=(ip_address, pbar))
			t.start()
			threads.append(t)

		for t in threads:
			t.join()

		if pbar:
			pbar.close()

		return self.results.copy()

	def scan_list(self, ip_list: List[str]) -> Set[str]:
		self.results.clear()

		# Progress bar description: Chinese|English
		pbar = (
			tqdm(total=len(ip_list), desc="Ping掃描|Ping Scan", ncols=80)
			if self.show_progress
			else None
		)

		threads: List[threading.Thread] = []
		for ip_address in ip_list:
			t = threading.Thread(target=self.ping_host, args=(ip_address, pbar))
			t.start()
			threads.append(t)

		for t in threads:
			t.join()

		if pbar:
			pbar.close()

		return self.results.copy()


def ping_range(start_ip: str, end_ip: str, timeout: float = 0.5, show_progress: bool = True) -> Set[str]:
	return PingScanner(timeout=timeout, show_progress=show_progress).scan_range(start_ip, end_ip)


def ping_list(ip_list: List[str], timeout: float = 0.5, show_progress: bool = True) -> Set[str]:
	return PingScanner(timeout=timeout, show_progress=show_progress).scan_list(ip_list)


def main():
	start_ip = input('請輸入起始 IP 地址|Start IP: ')
	end_ip = input('請輸入結束 IP 地址|End IP: ')

	start_time = time.time()
	print(f"開始掃描從 {start_ip} 到 {end_ip} 的 IP 地址...|Starting scan from {start_ip} to {end_ip}...")

	online_hosts = ping_range(start_ip, end_ip)

	total_time = time.time() - start_time
	ip_count = int(ipaddress.IPv4Address(end_ip)) - int(ipaddress.IPv4Address(start_ip)) + 1

	print("掃描結束|Scan completed")
	print(f"總共掃描了 {ip_count} 個 IP 地址|Total scanned: {ip_count}")
	print(f"總耗時: {total_time:.2f} 秒|Total time: {total_time:.2f} s")
	print(f"平均每個 IP 耗時: {total_time/ip_count:.4f} 秒|Avg per IP: {total_time/ip_count:.6f} s")

	if online_hosts:
		print(f"\n📋 在線主機列表 ({len(online_hosts)} 個)|Online hosts: ({len(online_hosts)})")
		print("-" * 50)
		for ip in sorted(online_hosts, key=lambda x: ipaddress.IPv4Address(x)):
			print(f"  {ip}")
	else:
		print("\n❌ 沒有發現在線主機|No online hosts found")


