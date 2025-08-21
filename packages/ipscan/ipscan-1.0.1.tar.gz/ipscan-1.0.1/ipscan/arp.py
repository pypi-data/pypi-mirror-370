import ctypes
import threading
import ipaddress
import time
from tqdm import tqdm
from typing import List, Dict, Optional

class ArpScanner:
    def __init__(self, show_progress: bool = True):
        self.show_progress = show_progress
        self.results = {}
        self.results_lock = threading.Lock()
    
    def get_mac(self, ip: str) -> Optional[str]:
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
            return None
        except Exception:
            return None
    
    def scan_ip(self, ip: str, pbar: Optional[tqdm] = None) -> None:
        mac = self.get_mac(ip)
        if mac and mac != "00:00:00:00:00:00":
            with self.results_lock:
                self.results[ip] = mac
        if pbar:
            pbar.update(1)
    
    def scan_range(self, start_ip: str, end_ip: str) -> Dict[str, str]:
        self.results.clear()
        ip_list = [str(ipaddress.IPv4Address(ip)) for ip in range(int(ipaddress.IPv4Address(start_ip)), int(ipaddress.IPv4Address(end_ip)) + 1)]
        
        pbar = tqdm(total=len(ip_list), desc="ARP掃描", ncols=80) if self.show_progress else None
        
        threads = []
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
        pbar = tqdm(total=len(ip_list), desc="ARP掃描", ncols=80) if self.show_progress else None
        
        threads = []
        for ip in ip_list:
            t = threading.Thread(target=self.scan_ip, args=(ip, pbar))
            threads.append(t)
            t.start()
        
        for t in threads:
            t.join()
        
        if pbar:
            pbar.close()
        
        return self.results.copy()

def arp_range(start_ip: str, end_ip: str, show_progress: bool = True) -> Dict[str, str]:
    return ArpScanner(show_progress=show_progress).scan_range(start_ip, end_ip)

def arp_list(ip_list: List[str], show_progress: bool = True) -> Dict[str, str]:
    return ArpScanner(show_progress=show_progress).scan_list(ip_list)

def main():
    start_ip = input('請輸入起始IP地址: ')
    end_ip = input('請輸入結束IP地址: ')
    
    start_time = time.time()
    print(f"開始掃描從 {start_ip} 到 {end_ip} 的IP地址...")
    
    host_results = arp_range(start_ip, end_ip)
    
    print("正在收集最後的reply")
    time.sleep(1)
    
    total_time = time.time() - start_time
    ip_count = int(ipaddress.IPv4Address(end_ip)) - int(ipaddress.IPv4Address(start_ip)) + 1
    
    print("掃描結束")
    print(f"總共掃描了 {ip_count} 個IP地址")
    print(f"總耗時: {total_time:.2f} 秒")
    print(f"平均每個IP耗時: {total_time/ip_count:.4f} 秒")
    
    if host_results:
        print(f"\n📋 在線主機列表 ({len(host_results)} 個):")
        print("-" * 50)
        for ip in sorted(host_results, key=lambda x: ipaddress.IPv4Address(x)):
            print(f"  {ip:<15} -> {host_results[ip]}")
    else:
        print("\n❌ 沒有發現在線主機")

if __name__ == '__main__':
    main() 