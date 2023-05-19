from piascomms.internal_geometry.shape_manipulation.xml_request import RequestFactory
from piascomms.internal_geometry.shape_manipulation.xml2dataclasses.physical_planes import BoundaryContourVertices 
from piascomms.client import Client, TranslateReply
from piascomms.internal_geometry.shape_manipulation.xml_request import RemovePhysicalPlane, AddPhysicalPlane
from typing import List
from pathlib import Path
from collections import namedtuple
from ..utils.list_man import send
from ..utils.rl_env_func import normalized_to_discrete
from ..utils.conversions import rescale_actions
import numpy as np
import layoutenv.logger_module as logger_mod
import __main__



logger = logger_mod.get_logger_from_config(__main__.__name__)

def add_physical_plane(action: np.array, planes_list: list):
    PlaneInfo = namedtuple("PlaneInfo", ["orientation", "upper_limit", "boundary_vertices"])
    plane_info = {0: PlaneInfo("Longitudinal bulkhead", 11.5 / 2, [(2, 5), (1, 5), (1, 6), (2, 6), (2, 5)]),
            1: PlaneInfo("Frame", 96, [(5, 4), (5, 3), (6, 3), (5, 4)]),
            2: PlaneInfo("Deck", 10, [(1, 4), (2, 4), (2, 3), (1, 3), (1, 4)])}
    
    discrete_action = normalized_to_discrete(action[0])
    upper = plane_info[discrete_action].upper_limit

    position = rescale_actions(action[1], 0, upper)

    request = AddPhysicalPlane(planes_list,
                                plane_info[discrete_action].orientation, 
                                -position,
                                plane_info[discrete_action].boundary_vertices)

    # ensure longitudinal bulkheads are symmetrical along the center plane
    if plane_info[discrete_action][0] == "Longitudinal bulkhead" and action[1] != -1:
        request_symmetry = AddPhysicalPlane(planes_list, 
                                    plane_info[discrete_action].orientation, 
                                    position,
                                    plane_info[discrete_action].boundary_vertices)
        send(request_symmetry)

    logger.info(f"LayoutEnv._add_physical_plane, arg: {plane_info[discrete_action].orientation}: {action}, scaled: {discrete_action},{position}, bounds: 0, {plane_info[discrete_action].upper_limit}, vertices: {plane_info[discrete_action].boundary_vertices}")
    send(request)

def required_index(subdivision_length: float):
    r_0 = 1 - 128 / (subdivision_length + 152)
    if subdivision_length > 100:
        return r_0
    elif subdivision_length > 80:
        return 1 - 1 / (1 + subdivision_length / 100 * r_0 / (1- r_0))

def boundary_vertice(vertices: List[tuple]):
    """
    Arg: 
        vertices (List[tuple]): [(id 1, id 2, guid 1, guid 2, excluded), ...]
    Return:
        BoundaryCountourVertices 
    """
    boundary_class = BoundaryContourVertices.BoundaryContourVertice
    boundary_list = []
    for vertice in vertices:
        boundary_list.append(boundary_class(*vertice))
    return BoundaryContourVertices(boundary_contour_vertice=boundary_list)

def request_layout():
    ship_layout = RequestFactory()
    ship_layout.request_type = "Export_ship_layout"
    ship_layout_request_string = ship_layout.to_xml_string()

    client = Client()
    client.send_from_stream(ship_layout_request_string)
    reply = TranslateReply(client.cache_recieved_bytes)
    reply.to_line()

    xml_path = Path("recieved_data.xml")
    with xml_path.open('w') as outfile:
        for line in reply.message.recieved_lines:
            outfile.write(line.data)

def planes_of_type(plane_type: str, planes_list: list) -> dict:
    """
    Arg:
        plane_type (str): orientation of the plane
        planes_list (list): list of planes with planes properties.
    Return:
        (dict): dictionary with plane names as keys and position as values.
    """
    return {plane.name: plane.plane_equation.component_d.reference_value[0].distance for plane in planes_list if plane.name[0] == plane_type[0]}


def removed_planes(start: list, current: list):
    """Compare two list and return the entries that do not match the current list
    """
    for plane in start:
        if plane in current:
            continue
        else:
            yield plane





