from .simulator import Simulator, BuildDamageCases

WEIGHT = {'DB 4 SB': {'weight': 1.045, 'centroid_z': 1.16, 'centroid_x': 1.78, 'centroid_y': 34.856}, 'DB 4 BB': {'weight': 1.045, 'centroid_z': 1.16, 'centroid_x': -1.78, 'centroid_y': 34.856}}

def attained_index(observation: dict, vcg: float, lightship_weight: float, floodable_length: float) -> float:
    att_idx = 0 
    damage_case_factory = BuildDamageCases(observation, floodable_length)
    for no, damage_case in damage_case_factory.damage_cases.items():
        survivability = Simulator(observation, vcg, lightship_weight)
        survivability.add_weight(WEIGHT)
        survivability.damage(damage_case)
        att_idx += survivability.probability_of_survival * damage_case_factory.p_factors[no]
        print(f"{no = }, {survivability.probability_of_survival = }")
    return att_idx

if __name__ == "__main__":
    from pathlib import Path
    from piascomms.utils import observation_space

    obs = observation_space(xml_path=Path("recieved_data.xml"))
    print(obs)
    a = attained_index(obs, draft=3.438, vcg=3.677, lightship_weight=1667.445, floodable_length=99.95)
    print(f"{a = }")