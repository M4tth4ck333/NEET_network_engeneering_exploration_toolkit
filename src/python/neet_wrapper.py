# src/python/neet_wrapper.py
import neet_core_py as nc

class NEET:
    def __init__(self):
        pass

    def discover_device(self, ip_address: str, hostname: str = "unknown"):
        device = nc.NetworkDevice(ip_address, hostname)
        print(f"Discovering device: {device.hostname} ({device.ip_address})")
        return device

    def scan_ports(self, device: nc.NetworkDevice):
        ports = device.discover_ports()
        print(f"Discovered ports for {device.ip_address}: {ports}")
        return ports

# Beispiel der Nutzung
if __name__ == "__main__":
    neet_tool = NEET()
    my_device = neet_tool.discover_device("192.168.1.1", "Router")
    neet_tool.scan_ports(my_device)