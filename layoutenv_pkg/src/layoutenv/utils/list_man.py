from piascomms.client import Client
from piascomms.internal_geometry.shape_manipulation.xml_request import RequestFactory, AddPhysicalPlane
import numpy as np



def find_nearest_idx(arr: list, value):
    array = np.array([arr])
    diff = np.absolute(array-value)
    return np.argmin(diff)

def send(request: AddPhysicalPlane) -> None:
    client = Client()
    client.send_from_stream(request.to_xml_string())