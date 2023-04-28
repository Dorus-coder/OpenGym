from piascomms.internal_geometry.shape_manipulation.xml_request import AddPhysicalPlane, RequestFactory, RequestVolume
from pathlib import Path
from piascomms.client import Client, TranslateReply

# example_2 = Path(r"C:\Users\cursist\Dorus\OpenGym\recieved_data.xml")
# planes = PlaneData(example_2).list_of_planes

# request = AddPhysicalPlane(planes=planes,
#                            orientation='transverse',
#                            distance=-30,
#                            boundary_fr_1=5,
#                            boundary_fr_2=6,
#                            )

# data = request.to_xml_string()

ship_layout = RequestFactory()
ship_layout.request_type = "Export_ship_layout"
ship_layout_request_string = ship_layout.to_xml_string()

xml_path = Path("recieved_data.xml")

def recieve_data(xml_path: Path):
    client = Client()
    client.send_from_stream(ship_layout_request_string)
    reply = TranslateReply(client.cache_recieved_bytes)
    reply.to_line()
    with xml_path.open('w') as outfile:
        for line in reply.message.recieved_lines:
            outfile.write(line.data.strip())

recieve_data(xml_path)

