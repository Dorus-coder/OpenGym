import numpy as np


class Survivability:
    def __init__(self, gz_max: float, range: float ,angle_equilibrium ,type: str = 'cargo', space: str = "other") -> None:
        min_heel            = {'cargo': 25, 'passenger': 7}     # degree
        max_heel            = {'cargo': 30, 'passenger': 15}    # degree
        tgz_maximum         = {'other': 0.12, 'ro-ro': 0.2}     # meters
        t_range             = {'other': 16, 'ro-ro': 20}        # degrees

        self.tgz    = tgz_maximum.get(space)
        self.t_range        = t_range.get(space)
        self.min_angle_heel = min_heel.get(type)
        self.max_angle_heel = max_heel.get(type)
        
        if range < self.t_range:
            self.range = range
        else:
            self.range = self.t_range

        self.angle_e        = angle_equilibrium
        
        if gz_max < self.tgz:
            self.gz_max = gz_max
        else:
            self.gz_max = self.tgz
 
    @property               
    def factor_k(self):
        if self.angle_e <= self.min_angle_heel:
            return 1
        elif self.angle_e >= self.max_angle_heel:
            return 0
        else:
            return np.sqrt((self.max_angle_heel - self.angle_e) / (self.max_angle_heel - self.min_angle_heel))

    def final(self):
        return self.factor_k * (self.gz_max / self.tgz * self.range / self.t_range) ** 0.25

    def __str__(self):
        # import pprint
        return f"gz range: {self.range}\nmax GZ: {self.gz_max}\nangle of equilibrium: {self.angle_e}"
        # return pprint.pformat({'gz range:': self.range, "angle of equilibrium:": self.angle_e, "max GZ": self.gz_max})
        
if __name__ == "__main__":

    for gz in np.arange(0, 0.06, 0.02):
        for range in np.arange(0, 90, 5):
            for angle in np.arange(0, 30, 5):
                survival = Survivability(gz_max=gz, range=range ,angle_equilibrium=-0.24)
                print(F"{gz = }, {range = }, {angle = }")
                print(f"{survival.final() = }")
                print()


    survival = Survivability(gz_max=1.149, range=60 ,angle_equilibrium=0)
    print(f"{survival.final() = }")
    print(survival)