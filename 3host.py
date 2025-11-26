from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import OVSSwitch, Controller
from mininet.cli import CLI
from mininet.log import setLogLevel
import time

class ThreeSwitchTopo(Topo):
    def build(self):
        # Switches
        s1 = self.addSwitch('s1')
        s2 = self.addSwitch('s2')
        s3 = self.addSwitch('s3')

        # Hosts
        h1 = self.addHost('h1', ip='10.0.0.1/8')
        h2 = self.addHost('h2', ip='10.0.0.2/8')
        h3 = self.addHost('h3', ip='10.0.0.3/8')
        server = self.addHost('server', ip='10.0.0.4/8')

        # Host connections
        self.addLink(h1, s1)
        self.addLink(h2, s2)
        self.addLink(h3, s3)
        self.addLink(server, s2)  # server on switch s2

        # Switch connections
        self.addLink(s1, s2)
        self.addLink(s2, s3)

def run():
    topo = ThreeSwitchTopo()
    net = Mininet(topo=topo, controller=Controller, switch=OVSSwitch)
    net.start()

    h1 = net.get('h1')
    h2 = net.get('h2')
    h3 = net.get('h3')
    server = net.get('server')

    # Print MAC + IP for hosts
    for host in [h1, h2, h3, server]:
        print(f"\n=== {host.name} interfaces ===")
        print(host.cmd('ifconfig -a'))
        print(f"=== {host.name} IP addresses ===")
        print(host.cmd('ip addr show'))

    # Ping all hosts (uses IP)
    print("\n=== Ping All Hosts ===")
    net.pingAll()

    # h1 -> server ping (using IP)
    print("\n=== Pinging server from h1 (via IP) ===")
    print(h1.cmd(f'ping -c 3 {server.IP()}'))

    # ARP table of h1
    print("\n=== ARP table of h1 ===")
    print(h1.cmd("ip neigh show"))

    # iperf TCP throughput h1 -> server
    print("\n=== Measuring TCP Throughput (h1 -> server) ===")
    print("Starting iperf server on server...")
    server.cmd("iperf -s &")
    time.sleep(1)
    print(h1.cmd(f'iperf -c {server.IP()}'))
    server.cmd("pkill -f iperf")

    # Allow manual commands
    print("\n=== Opening Mininet CLI ===")
    CLI(net)

    net.stop()

if __name__ == "__main__":
    setLogLevel('info')
    run()





from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import OVSSwitch, Controller
from mininet.cli import CLI
from mininet.log import setLogLevel

class ThreeSwitchTopo(Topo):
    def build(self):
        # Switches
        s1 = self.addSwitch('s1')
        s2 = self.addSwitch('s2')
        s3 = self.addSwitch('s3')

        # Hosts
        h1 = self.addHost('h1', ip='10.0.0.1/8')
        h2 = self.addHost('h2', ip='10.0.0.2/8')
        h3 = self.addHost('h3', ip='10.0.0.3/8')
        server = self.addHost('server', ip='10.0.0.4/8')

        # Links (hosts -> switches)
        self.addLink(h1, s1)
        self.addLink(h2, s2)
        self.addLink(h3, s3)
        self.addLink(server, s2)

        # Switch interconnections
        self.addLink(s1, s2)
        self.addLink(s2, s3)

def run():
    topo = ThreeSwitchTopo()
    net = Mininet(topo=topo, controller=Controller, switch=OVSSwitch)
    net.start()
    CLI(net)
    net.stop()

if __name__ == "__main__":
    setLogLevel('info')
    run()
