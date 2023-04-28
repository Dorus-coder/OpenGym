from time import sleep
from piascomms.internal_geometry.shape_manipulation.xml_request import RequestFactory, AddPhysicalPlane


def build_plane(plane, list_of_planes):
    ing_time = 0.5
    if plane.plane_equation.component_a == 1.0:
        print(plane.name)
        request = AddPhysicalPlane(planes=list_of_planes, 
                        orientation="Frame", 
                        distance=plane.plane_equation.component_d.reference_value[0].distance,
                        boundary_fr_1=5,
                        boundary_fr_2=6,
                        )
        send(request)
        sleep(ing_time)
        
    elif plane.plane_equation.component_b == -1.0 or plane.plane_equation.component_b == 1.0:
        print(plane.name)
        request = AddPhysicalPlane(planes=list_of_planes, 
                        orientation="Longitudinal bulkhead", 
                        distance=plane.plane_equation.component_d.reference_value[0].distance,
                        boundary_fr_1=1,
                        boundary_fr_2=2,
                        )
        send(request)
        sleep(ing_time)

    elif plane.plane_equation.component_c == 1.0:
        print(plane.name)
        request = AddPhysicalPlane(planes=list_of_planes,
                        orientation="Deck",
                        distance=plane.plane_equation.component_d.reference_value[0].distance,
                        boundary_fr_1=1,
                        boundary_fr_2=2)
        send(request)
        sleep(ing_time)