from typing import Dict

from seedemu import Graphable, Layer, PeerRelationship, Emulator, Node

PathSecFileTemplates: Dict[str, str] = {}

PathSecFileTemplates["bind_txt_record"] = """
{} TXT TRUE
"""

class PathSec(Layer, Graphable):
    """!
    @brief The new layer for pathsec in BGP
    """

    __neighbours: Dict[int, PeerRelationship]

    def __init__(self):
        super().__init__()
        self.__neighbours = {}
        self.addDependency('Ebgp', False, False)


    def __getNeighbours(self):
        self.get

    def configureDNSRecords(self, emulator: Emulator):
        reg = emulator.getRegistry()
        for neighbour in self.__neighbours.keys():
            node: Node = reg.get(neighbour)
            node.appendFile('/etc/bind/zones/', PathSecFileTemplates["bind_txt_record"].format())
