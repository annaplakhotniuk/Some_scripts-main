import subprocess
from scapy.all import *

#need install dependencies ---- pip install scapy



class NetWork():
    

    def __init__(self):
        sg0: str = "kv0.cloud.boosteroid.com"
        sg1: str = "kv1.cloud.boosteroid.com"
        

        self.ip_addr: dict = {
            "185.2.108.5": "185.2.108.6",
            "185.2.108.6": "185.2.108.5"
        }
        self.blocked_ip_var: str = "185.2.108.6"
        self.unblocked_ip_var: str = "185.2.108.5"
        self.target_ip:str = "192.168.0.106"
        self.network_interface: str = "enp3s0"
        self._counter: int = 0
        self.numbers_of_switches: int = 0
        

    def packet_handler(self, packet, switch_limit: int = 2):
        stop_handling = False
        if packet.haslayer(IP) and packet.haslayer(UDP):
            ip_src = packet[IP].src
            ip_dst = packet[IP].dst
            udp_srcport = packet[UDP].sport
            udp_dstport = packet[UDP].dport
            udp_payload = packet[UDP].payload

            # Check if the destination IP is in the blocked/unblocked IP list
            
            for hostname, unblocked in self.ip_addr.items():
                if ip_src == hostname:
                    self._counter += 1
                    print(f"Counter is: {self._counter}")
                    if self._counter == 20:
                        print("Reset counter")
                        # Try block
                        if not self.check_iptables_stdout(ip_src):
                            self.numbers_of_switches += 1
                            print(f"Try block on {ip_src}")
                            self.reset_all_iptable_rules()
                            self.block_ip(ip_src)  # Block IP using iptables
                        elif self.check_iptables_stdout(ip_src):
                            self.numbers_of_switches += 1
                            print(f"Try block: IP: {ip_src} exists in Iptables -> Reset rules for Blocked IP -> Block IP: {unblocked}")
                            self.reset_all_iptable_rules()
                            self.block_ip(unblocked)
                        self._counter = 0

                if self.numbers_of_switches == switch_limit:
                    print(f"The switch limit of {switch_limit} has been reached!")
                    stop_handling = True
                    break                      
                           
            # Print packet details
            print(f"numbers of switches is: {self.numbers_of_switches}")
            print(f"Source IP: {ip_src}")
            #print(f"Destination IP: {ip_dst}")
            #print(f"UDP Source Port: {udp_srcport}")
            #print(f"UDP Destination Port: {udp_dstport}")
            #print(f"UDP Payload: {udp_payload}")
            print("----------------------------------------")
            time.sleep(1)
            if stop_handling:
                return

    def check_iptables_stdout(self, ip) -> bool:        
        command = ['sudo', 'iptables', '-n', '-L']
        result = subprocess.run(command, capture_output=True, text=True)
        output = result.stdout
        lines = output.splitlines()

        for line in lines:
            if ip in line:                
                return True
            
        return False   
               

    def reset_all_iptable_rules(self):        
        command = ['iptables', '-F']
        result = subprocess.run(command, capture_output=True, text=True)
        output = result.stdout
        print(f"RESET ALL RULES {output}")        

    def block_ip(self, ip):
        ckeck: bool = self.check_iptables_stdout(ip)
        if ckeck is True:
            print(f"Method block_ip: ip-{ip} already exist in Iptables list")
        else:
            print(f"Method 'block_ip':{ip}")
            subprocess.run(['iptables', '-A', 'INPUT', '-s', ip, '-p', 'udp', '-j', 'DROP'], check=True)

    def unblock_ip(self, ip):
        ckeck: bool = self.check_iptables_stdout(ip)
        if ckeck is False:
            print(f"Method unblock_ip: rule for ip-{ip} is not exist")       
        else:
            print(f"Method 'unblock_ip':{ip}")
            try:
                subprocess.run(['iptables', '-D', 'INPUT', '-s', ip, '-p', 'udp', '-j', 'DROP'], check=True)
            except subprocess.CalledProcessError as e:
                print(f"An error occurred while unblocking IP: {ip}")
                print(f"Error message: {e}")

    def start_capture(self):        
        sniff(iface=self.network_interface, filter="udp", prn=self.packet_handler)


network = NetWork()
network.reset_all_iptable_rules()
network.start_capture()

"""import subprocess
import platform
from scapy.all import *


class NetWork():
    def __init__(self):
        self.ip_addr = {
            "185.2.108.5": "185.2.108.6",
            "185.2.108.6": "185.2.108.5"
        }
        self.blocked_ip_var = "185.2.108.6"
        self.unblocked_ip_var = "185.2.108.5"
        self.target_ip = "192.168.0.106"
        self.network_interface = "enp3s0"
        self._counter = 0
        self.numbers_of_switches = 0

    def packet_handler(self, packet, switch_limit=2):
        stop_handling = False
        if packet.haslayer(IP) and packet.haslayer(UDP):
            ip_src = packet[IP].src
            ip_dst = packet[IP].dst
            udp_srcport = packet[UDP].sport
            udp_dstport = packet[UDP].dport
            udp_payload = packet[UDP].payload

            # Check if the source IP is in the blocked/unblocked IP list
            for hostname, unblocked in self.ip_addr.items():
                if ip_src == hostname:
                    self._counter += 1
                    print(f"Counter is: {self._counter}")
                    if self._counter == 20:
                        print("Reset counter")
                        # Try block
                        if not self.check_iptables_stdout(ip_src):
                            self.numbers_of_switches += 1
                            print(f"Try block on {ip_src}")
                            self.reset_all_iptable_rules()
                            self.block_ip(ip_src)  # Block IP
                        elif self.check_iptables_stdout(ip_src):
                            self.numbers_of_switches += 1
                            print(f"Try block: IP: {ip_src} exists in Iptables -> Reset rules for Blocked IP -> Block IP: {unblocked}")
                            self.reset_all_iptable_rules()
                            self.block_ip(unblocked)
                        self._counter = 0

                if self.numbers_of_switches == switch_limit:
                    print(f"The switch limit of {switch_limit} has been reached!")
                    stop_handling = True
                    break

            # Print packet details
            print(f"Number of switches: {self.numbers_of_switches}")
            print(f"Source IP: {ip_src}")
            print(f"Destination IP: {ip_dst}")
            print(f"UDP Source Port: {udp_srcport}")
            print(f"UDP Destination Port: {udp_dstport}")
            print(f"UDP Payload: {udp_payload}")
            print("----------------------------------------")
            time.sleep(1)
            if stop_handling:
                return

    def check_iptables_stdout(self, ip):
        system = platform.system()
        if system == 'Linux':
            command = ['sudo', 'iptables', '-n', '-L']
        elif system == 'Windows':
            command = ['netsh', 'advfirewall', 'firewall', 'show', 'rule', 'name=all']
        elif system == 'Darwin':
            command = ['pfctl', '-s', 'rules']
        else:
            print(f"Unsupported operating system: {system}")
            return False

        result = subprocess.run(command, capture_output=True, text=True)
        output = result.stdout
        lines = output.splitlines()

        for line in lines:
            if ip in line:
                return True

        return False

    def reset_all_iptable_rules(self):
        system = platform.system()
        if system == 'Linux':
            command = ['iptables', '-F']
        elif system == 'Windows':
            command = ['netsh', 'advfirewall', 'reset']
        elif system == 'Darwin':
            command = ['pfctl', '-F', 'all']
        else:
            print(f"Unsupported operating system: {system}")
            return

        result = subprocess.run(command, capture_output=True, text=True)
        output = result.stdout
        print(f"RESET ALL RULES {output}")

    def block_ip(self, ip):
        system = platform.system()
        if system == 'Linux':
            command = ['iptables', '-A', 'INPUT', '-s', ip, '-p', 'udp', '-j', 'DROP']
        elif system == 'Windows':
            command = ['netsh', 'advfirewall', 'firewall', 'add', 'rule', 'name="Block IP"', 'dir=in', 'interface=any', 'action=block', 'remoteip=any', f'localip={ip}']
        elif system == 'Darwin':
            command = ['pfctl', '-a', 'com.apple/250.AppFirewall', '-s', 'anchorrules']
        else:
            print(f"Unsupported operating system: {system}")
            return

        subprocess.run(command, check=True)

    def unblock_ip(self, ip):
        system = platform.system()
        if system == 'Linux':
            command = ['iptables', '-D', 'INPUT', '-s', ip, '-p', 'udp', '-j', 'DROP']
        elif system == 'Windows':
            command = ['netsh', 'advfirewall', 'firewall', 'delete', 'rule', 'name="Block IP"', 'dir=in', f'localip={ip}']
        elif system == 'Darwin':
            command = ['pfctl', '-a', 'com.apple/250.AppFirewall', '-s', 'anchorrules']
        else:
            print(f"Unsupported operating system: {system}")
            return

        subprocess.run(command, check=True)

    def start_capture(self):
        sniff(iface=self.network_interface, filter="udp", prn=self.packet_handler)


network = NetWork()
network.reset_all_iptable_rules()
network.start_capture()"""