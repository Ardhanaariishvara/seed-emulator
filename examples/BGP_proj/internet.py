from seedemu import Emulator, Base, Routing, Ebgp, Ibgp, Ospf, WebService, DomainNameService, \
    OpenVpnRemoteAccessProvider, PeerRelationship, Docker, DomainNameCachingService, Binding, Filter, Platform
from seedemu.utilities import Makers

emu = Emulator()
base = Base()
routing = Routing()
ebgp = Ebgp()
ibgp = Ibgp()
ospf = Ospf()
web = WebService()
dns = DomainNameService()
ovpn = OpenVpnRemoteAccessProvider()
ldns = DomainNameCachingService()

ix100 = base.createInternetExchange(100)
ix200 = base.createInternetExchange(200)
ix203 = base.createInternetExchange(203)
ix204 = base.createInternetExchange(204)
ix205 = base.createInternetExchange(205)
ix206 = base.createInternetExchange(206)

Makers.makeTransitAs(base, 2, [100, 200, 203], [(100, 200), (100, 203)])
Makers.makeTransitAs(base, 3, [203, 204, 205], [(203, 204), (203, 205), (204, 205)])
Makers.makeTransitAs(base, 4, [100, 200, 203, 205], [(200, 203), (100, 205)])

Makers.makeTransitAs(base, 10, [100, 200], [(100, 200)])
Makers.makeTransitAs(base, 11, [204, 206], [(204, 206)])

Makers.makeStubAs(emu, base, 101, 100, [web, None, None, None, None, None])
Makers.makeStubAs(emu, base, 102, 100, [None])
Makers.makeStubAs(emu, base, 110, 206, [web, None])
Makers.makeStubAs(emu, base, 111, 206, [web])
Makers.makeStubAs(emu, base, 112, 204, [])

as2 = base.getAutonomousSystem(2)
as2.createNetwork('net0')
as2.getRouter('r100').joinNetwork('net0')
as2.createHost('ns-as1-probably').joinNetwork('net0')

as112 = base.getAutonomousSystem(112)
as112.createHost('host_112').joinNetwork('net0', '10.112.0.112')
as112.getNetwork('net0').enableRemoteAccess(ovpn)

ebgp.addRsPeers(100, [2, 4])
ebgp.addRsPeers(200, [2, 4])
ebgp.addRsPeers(203, [2, 3, 4])
ebgp.addRsPeers(205, [3, 4])

ebgp.addPrivatePeerings(100, [2,4], [101, 102], PeerRelationship.Provider)
ebgp.addPrivatePeerings(206, [11], [110, 111], PeerRelationship.Provider)
ebgp.addPrivatePeerings(204, [3], [11], PeerRelationship.Provider)
ebgp.addPrivatePeerings(204, [11], [112], PeerRelationship.Peer)
ebgp.addPrivatePeerings(204, [3], [112], PeerRelationship.Provider)

base.getAutonomousSystem(112).createHost('web').joinNetwork('net0')
web.install('webtest')
emu.addBinding(Binding('webtest', filter=Filter(nodeName='web', asn=112)))

dns.install('a-root-server').addZone('.').setMaster()
dns.install('b-root-server').addZone('.')
dns.install('a-com-server').addZone('com.')
dns.install('a-edu-server').addZone('edu.')

dns.install('ns-example-com').addZone('example.com.')
dns.install('ns-google-com').addZone('google.com.')
dns.install('ns-example-edu').addZone('example.edu.')
dns.install('ns-as2').addZone('as2.com.')

dns.getZone('google.com.').addRecord('@ A 8.8.8.8').addRecord('www A 5.5.5.6')
dns.getZone('example.edu.').addRecord('@ A 2.2.2.2')
dns.getZone('as1.com.').addRecord('@ A 192.168.0.1').addRecord('@ TXT hello')

emu.addBinding(Binding('a-root-server', filter=Filter(asn=101)))
emu.addBinding(Binding('b-root-server', filter=Filter(asn=110)))
emu.addBinding(Binding('a-com-server', filter=Filter(asn=112)))
emu.addBinding(Binding('a-edu-server', filter=Filter(asn=112)))
emu.addBinding(Binding('ns-example-com', filter=Filter(asn=101)))
emu.addBinding(Binding('ns-example-edu', filter=Filter(asn=101)))
emu.addBinding(Binding('ns-google-com', filter=Filter(asn=101)))
emu.addBinding(Binding('ns-as2', filter=Filter(asn=2)))

# ldns.install('global-dns-1')
# base.getAutonomousSystem(101).createHost('local-dns').joinNetwork('net0', '10.101.0.53')
# base.getAutonomousSystem(102).setNameServers(['10.101.0.53'])
# emu.addBinding(Binding('global-dns-1', filter=Filter(asn=101, nodeName='local-dns')))

emu.addLayer(base)
emu.addLayer(routing)
emu.addLayer(ebgp)
emu.addLayer(ibgp)
emu.addLayer(ospf)
emu.addLayer(web)
emu.addLayer(dns)
emu.addLayer(ldns)

emu.render()
docker = Docker(internetMapEnabled=True, platform=Platform.AMD64)
emu.compile(Docker(), './output')