from mininet.topo import Topo

class Base_Topo( Topo ):
    "Simple Base Topology for SCC365"

    def __init__(self):
        "Create Topology"
        Topo.__init__(self)

        # Add Hosts
        host_a = self.addHost('h1')
        host_b = self.addHost('h2')
        host_c = self.addHost('h3')
        host_d = self.addHost('h4')

        # Add Switch
        switch_a = self.addSwitch('s1')

        # Add Links
        self.addLink(host_a, switch_a)
        self.addLink(host_b, switch_a)
        self.addLink(host_c, switch_a)
        self.addLink(host_d, switch_a)

topos = { 'base-topo': (lambda: Base_Topo())}
