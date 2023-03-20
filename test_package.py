
from piascomms.internal_geometry.shape_manipulation.xml_request import AddPhysicalPlane, RequestFactory, RequestVolume
from piascomms.utils import observation_space
from piascomms.internal_geometry.shape_manipulation.xml2dataclasses.physical_planes import physical_planes_from_xml
from piascomms.compartments import CompartmentData
from pathlib import Path
from piascomms.client import Client, TranslateReply, RecievedMessage
example_2 = Path(r"C:\Users\cursist\Dorus\ThesisResearch\PiasExampleFiles\example_2\goa1.fromLayout.xml")
planes = physical_planes_from_xml(example_2).physical_planes.physical_plane

request = AddPhysicalPlane(planes=planes,
                           orientation='transverse',
                           distance=-30,
                           boundary_fr_1=5,
                           boundary_fr_2=6,
                           )

data = request.to_xml_string()

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
        outfile.write(line.data.strip())

print(observation_space(xml_path))
