from piascomms.internal_geometry.shape_manipulation.xml_request import AddPhysicalPlane, RequestFactory, RequestVolume
from piascomms.internal_geometry.shape_manipulation.xml2dataclasses.physical_planes import PhysicalPlanes
from piascomms.layout_properties import PlaneData
from piascomms.client import Client
import numpy as np
from typing import List
import layoutenv.utils as lutils

def send(request: AddPhysicalPlane) -> None:
    data = request.to_xml_string()
    client = Client()
    client.send_from_stream(data)

def find_nearest_idx(arr: list, value):
    array = np.array([arr])
    diff = np.absolute(array-value)
    return np.argmin(diff)

class LayoutScript:
    def __init__(self, _planes: PlaneData) -> None:
        self.planes = _planes
        self.time = 0.5
        print(self.plane_names)

    @property
    def layout(self) -> List[PhysicalPlanes.PhysicalPlane]:
        return [plane for plane in self.planes.list_of_planes if plane.name[:8] != 'Uiterste']

    @property
    def plane_names(self) -> list:
        return [plane.name for plane in self.layout]
    
    def planes_of_type(self, plane_type: str) -> dict:
        return {plane.name: plane.plane_equation.component_d.reference_value for plane in self.planes.list_of_planes if plane.name[0] == plane_type[0]}

    def build_layout(self):
        for plane in self.layout:
             lutils.build_plane(plane, self.planes.list_of_planes)

    def remove_plane(self, action: tuple):
        """
        Arg:
            action (int): orientation = Discrete(3), position = box
 
        """
        plane_types = {0: "Longitudinal bulkhead", 1: "Frame", 2: "Deck"}
        plane_type = plane_types.get(action[0])
        planes = self.planes_of_type(plane_type)
        plane_to_delete = list(planes.keys())[find_nearest_idx(planes.values(), action[1])]
        self.layout.remove(plane_to_delete)
        
        

       
    

