__version__ = "1.2.1"
__author__ = "Wing"
__email__ = "tomt99688@gmail.com"

# New canonical module names
from .sping import PingScanner, ping_range, ping_list
from .sarp import ArpScanner, arp_range, arp_list

__all__ = [
    'PingScanner', 'ping_range', 'ping_list',
    'ArpScanner', 'arp_range', 'arp_list',
    '__version__', '__author__', '__email__'
] 