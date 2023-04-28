from collections import namedtuple

PlaneInfo = namedtuple("PlaneInfo", ["orientation", "upper_limit", "boundary_vertices"])


plane_info = {0: PlaneInfo("Longitudinal bulkhead", 11.5 / 2, [(2, 5), (1, 5), (1, 6), (2, 5)]),
              1: PlaneInfo("Frame", 96, [(5, 4), (5, 3), (6, 3), (5, 4)]),
              2: PlaneInfo("Deck", 10, [(1, 4), (2, 4), (2, 3), (1, 4)])}

print(PlaneInfo.__doc__)