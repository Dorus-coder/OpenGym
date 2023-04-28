import numpy as np
from dataclasses import dataclass, field
from typing import Union


class BuildDamageCases:
    def __init__(self, observed_compartments: dict, floodable_length: float):
        self.observation_space = observed_compartments
        self.p_factors = [0.001, 0.005, 0.025, 0.105, 0.3401, 0.3401, 0.105, 0.025, 0.005, 0.001]
        self.max_floodable_length = floodable_length

    @property
    def damage_cases(self) -> dict:
        cases = {i: [] for i in range(0, 9)}
        for compartment, properties in self.observation_space.items():
            for case, compartments in cases.items():
                upper = (0.1 + 0.1*int(case)) * self.max_floodable_length
                lower = (0.0 + 0.1*int(case)) * self.max_floodable_length
                if lower < properties.get('centroid_z') < upper :
                    compartments.append(compartment)
                    break
        return cases 



if __name__ == "__main__":
    from piascomms.utils import observation_space
    from pathlib import Path

    observation = observation_space(xml_path=Path("recieved_data.xml"))

    b = BuildDamageCases(observed_compartments=observation, floodable_length=100)
    cases = b.damage_cases
    for case, compartments in cases.items():
        print(f"case # {case}")
        for idx, comp in enumerate(compartments):
            print('\t', idx,  comp)
