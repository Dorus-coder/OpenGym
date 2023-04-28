from Simulator.survivability import Survivability
from Simulator.curves import GZ
from typing import  Dict


def required_index(subdivision_length: float):
    r_0 = 1 - 128 / (subdivision_length + 152)
    if subdivision_length > 100:
        return r_0
    elif subdivision_length > 80:
        return 1 - 1 / (1 + subdivision_length / 100 * r_0 / (1- r_0))
    
class BuildDamageCases:
    def __init__(self, observed_compartments: dict, floodable_length: float):
        self.observation_space = observed_compartments
        self.p_factors = [0.001, 0.005, 0.025, 0.105, 0.3401, 0.3401, 0.105, 0.025, 0.005, 0.001]
        self.max_floodable_length = floodable_length

    @property
    def damage_cases(self):
        cases = {i: [] for i in range(0, 9)}
        for compartment, properties in self.observation_space.items():
            z = properties.get('centroid_z')
            if z:
                for case, compartments in cases.items():
                    upper = (0.1 + 0.1*int(case)) * self.max_floodable_length
                    lower = (0.0 + 0.1*int(case)) * self.max_floodable_length
                    if lower < z < upper:
                        compartments.append(compartment)
                        break
        return cases 

    
class Damage:
    def __init__(self, filled_compartments: dict, damage_case: dict) -> None:
        self.filled_compartments = filled_compartments
        self.damage_case         = damage_case
        self.substract_existing_weight_from_added_weight()

    def substract_existing_weight_from_added_weight(self):
        for filled_compartment_name in self.filled_compartments.keys():
            if filled_compartment_name in self.damage_case.keys():
                self.damage_case[filled_compartment_name]['volume'] -= self.filled_compartments[filled_compartment_name]

    @property
    def added_weight(self):
        weight = 0
        for w in self.damage_case:
            weight =+ w['volume']
        return weight
    

class Simulator():
    def __init__(self, 
                 observation_space: dict, 
                 vcg: float, 
                 lightship_weight: float

                 ) -> None:
    
        self.observation_space = observation_space
        self.displacement      = lightship_weight
        self.vcg               = vcg
   

    def add_weight(self, compartments: Dict[str, dict]) -> float:
        for weight in compartments.values():
            self.displacement += weight['weight']

    def damage(self, damage_case: list):
        """
        This simulation doesn't account for the waterline and the weight of the damage compartment. Every damaged compartment will be full
        """
        for comp in damage_case:
            distance = self.observation_space[comp]['centroid_y'] - self.vcg
            self.vcg += self.transfer_center_of_gravity(weight=self.observation_space[comp]['volume'], distance=distance)
            self.displacement += self.observation_space[comp]['volume']

    def transfer_center_of_gravity(self, weight: float, distance: float, added_weight: bool = True):
        corr = 10 # correction to let some damage cases fail
        if added_weight:
            return ((weight * (distance + corr)) / (self.displacement + weight))
        else:
            return ((weight * distance) / (self.displacement))

    def transverse_moment(self, damage_cases: list):
        """
        transverse moment due to damaged compartments
        """
        trans_mom = 0
        for name, comp in self.observation_space.items():
            if name in damage_cases:
                trans_mom += comp['volume'] * comp['centroid_x']
        return trans_mom

    @property
    def trans_stability(self):
        return GZ(displacement=self.displacement, vcg=self.vcg)
    
    @property
    def gz_curve(self):
        return self.trans_stability.plot_gz_curve()
    
    def survivability(self):
        return Survivability(gz_max=self.trans_stability.gz_max,
                                 range=self.trans_stability.positve_gz_range,
                                 angle_equilibrium=0,
                                 )
    @property
    def probability_of_survival(self):
        return self.survivability().final()

if __name__ == "__main__":

    depl = 1677
    new_depl = 300
    delta = new_depl - depl

    sim_in = Simulator({}, 3.677, depl)
    print(f"{sim_in.transfer_center_of_gravity(delta, 1.6)}") 
    
