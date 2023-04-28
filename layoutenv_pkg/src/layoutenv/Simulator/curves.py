import numpy as np
from pathlib import Path


class KNsin:
    def __init__(self, cross_curves_path: Path) -> None:
        self.cross_curves = cross_curves_path.open('r').readlines()
         

    def dataframe(self) -> dict:
        df = {}
        for line in self.cross_curves:
            if line == "\n":
                break
            temp_line = line.split()
            df[temp_line[0]] = [float(val) for val in temp_line[2:]]
        self.header = df.pop("NNNN")
        return df
    
    
    def __str__(self):
        import pprint
        return pprint.pformat(self.dataframe(), indent=2)       
    
    def find_kn(self, displacement: float):
        weights = [float(val) for val in self.dataframe().keys()]
        previous = weights[0]
        for idx, weight in enumerate(weights):
            if idx >= 1:
                previous = weights[idx -1]
            if weight == displacement:
                return self.dataframe().get(str(displacement))
            elif previous < displacement < weight:
                diff = (weight - displacement) / (weight - previous) 
                low = self.dataframe().get(str(int(previous)))
                high = self.dataframe().get(str(int(weight)))
                return [(high[i] - low[i]) * diff + low[i] for i in range(len(low))]
    

class GZ:
    def __init__(self, displacement: float, vcg: float) -> None:
        cross_curve     = KNsin(cross_curves_path=Path(r"C:\Users\cursist\Dorus\ThesisResearch\PiasExampleFiles\example_3\PiasExampleFiles\cross_curve_short_ps.txt"))
        kn = cross_curve.find_kn(displacement)
        if kn:
            self.kn_sin_phi = kn
        else:
            self.kn_sin_phi =  [0.0, 0.15, 0.8, 1.5, 2.0, 2.8, 3.2, 3.5]
        self.x_axis     = cross_curve.header
        self.vcg        = vcg

    @property
    def kg_sin_phi(self):
        RAD = 180 / np.pi
        return [self.vcg * np.sin(angle / RAD) for angle in self.x_axis]

    @property
    def righting_arm(self):
        return [kn_sin_phi - self.kg_sin_phi[idx] for idx, kn_sin_phi in enumerate(self.kn_sin_phi)]
    
    @property
    def gz_max(self):
        return max(self.righting_arm)
    
    @property
    def positve_gz_range(self):
        for value in self.righting_arm[1:]:
            if value < 0:
                return self.x_axis[self.righting_arm.index(value)]
            else:
                return max(self.x_axis)

    def plot_gz_curve(self, grid = True):
        import matplotlib.pyplot as plt
        plt.plot(self.x_axis, self.righting_arm)
        plt.vlines(x=30, ymin=0, ymax=self.righting_arm[4])
        plt.hlines(y=0, xmin=0, xmax=self.x_axis[-1], colors='k')
        plt.grid(visible=grid)
        plt.show()

    def __str__(self):
        from prettytable import PrettyTable
        tab = PrettyTable(self.x_axis)
        tab.add_rows([self.kn_sin_phi, self.kg_sin_phi, self.righting_arm])
        tab.add_column("Heeling angle", ["KN sin (phi)", "KG sin (phi)", "GZ (rigting arm)"])
        return tab.__repr__()

if __name__ == "__main__":

    gz = GZ(displacement=1700, vcg=3.974)

    print(gz)

