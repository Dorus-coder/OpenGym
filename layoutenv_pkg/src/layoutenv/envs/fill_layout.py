from piascomms.internal_geometry.shape_manipulation.xml_request import AddPhysicalPlane
from piascomms.utils import observation_space
from piascomms.layout_properties import PlaneData
from pathlib import Path
from piascomms.client import Client
import numpy as np
from empty_layout import EmptyLayout, MessageBox
import subprocess
from time import sleep
from utils import request_layout, boundary_vertice

ing = 0.5

example_2 = Path(r"C:\Users\cursist\Dorus\OpenGym\recieved_data.xml")
planes = PlaneData(example_2).list_of_planes

empty_layout = EmptyLayout()
empty_layout.destination = Path(r"C:\Users\cursist\Dorus\ThesisResearch\PiasExampleFiles\full_layout")
empty_layout.query_user_empty_layout()

layout_module = r"C:\Users\cursist\Dorus\OpenGym\envs\temp.bat"
process = subprocess.Popen(layout_module)
c = Client()
while not c.server_check():
    print('loading.....')
sleep(1)

frames_and_decks = [("Frame", -20, 5 , 6), ("Frame", -40, 5 , 6), ("Deck", -1.5, 1, 2), ("Frame", -50, 5 , 6), ("Frame", -60, 5 , 6), ("Frame", -70, 5 , 6), ("Frame", -80, 5 , 6), ("Frame", -90, 5 , 6), ("Deck", -0.75, 1, 2)]

vertices_db_planes = [(5, 2, 0, 0, 2), (5, 7, 0, 0, 2), (9, 7, 0, 0, 2), (9, 2, 0, 0, 2), (5, 2, 0, 0, 2)]
vertices_sides = [(6, 1, 0, 0, 2), (2, 9, 0, 0, 2)]

boundary_vertices_db = boundary_vertice(vertices_db_planes)
boundary_vertices_side = boundary_vertice(vertices_sides)
  
for plane in frames_and_decks:
    request = AddPhysicalPlane(planes, *plane)
    data = request.to_xml_string()
    client = Client()
    client.send_from_stream(data)
    sleep(ing)

for d in np.arange(5, 5.75, 0.25):
    request = AddPhysicalPlane(planes, 
                               orientation="Longitudinal bulkhead",
                               distance=d,
                               boundary_fr_1=1,
                               boundary_fr_2=2)
    request.boundary_contour_vertices = boundary_vertices_side
    data = request.to_xml_string()
    client = Client()
    client.send_from_stream(data)
    sleep(ing)
    request = AddPhysicalPlane(planes, 
                               orientation="Longitudinal bulkhead",
                               distance=d*-1,
                               boundary_fr_1=1,
                               boundary_fr_2=2)
    request.boundary_contour_vertices = boundary_vertices_side
    data = request.to_xml_string()
    client = Client()
    client.send_from_stream(data)
    sleep(ing)

for d in np.arange(-4, 4, 0.4):
    request = AddPhysicalPlane(planes=planes,
                            orientation="Longitudinal bulkhead",
                            distance=d,
                            boundary_fr_1=1,
                            boundary_fr_2=2,
                            )
    request.boundary_contour_vertices = boundary_vertices_db

    data = request.to_xml_string()
    client = Client()
    client.send_from_stream(data)
    sleep(ing)


request_layout()

mes = MessageBox('layout module')
mes.warning('layout module is closed when the script ends.')