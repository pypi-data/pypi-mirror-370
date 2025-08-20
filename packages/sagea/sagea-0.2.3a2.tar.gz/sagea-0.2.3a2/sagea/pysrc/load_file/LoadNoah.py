import datetime

import numpy as np
from netCDF4 import Dataset

from sagea.pysrc.auxiliary import FileTool
from sagea.pysrc.auxiliary.MathTool import MathTool
from sagea.pysrc.data_class.__GRD__ import GRD


class LoadNOAH21:
    def __init__(self):
        self.nc = None
        self.keys = None

    def setFile(self, file):
        self.nc = Dataset(file)
        self.keys = self.nc.variables.keys()
        return self

    def get2dData(self, key, full_lat=False):
        assert key in self.keys, 'no such key'
        data = np.array(self.nc.variables[key])[0]
        xyz = []
        for i in range(len(data)):
            for j in range(len((data[i]))):
                lat = int(i - 90) + 30
                lon = j - 180
                xyz.append([lon, lat, data[i][j]])
        xyz = np.array(xyz)
        grid, lat, lon = MathTool.xyz2grd(xyz)

        if full_lat:
            lat = np.arange(-90 + 0.5, 90 + 0.5, 1)

        return grid, lat, lon


def load_GLDAS_TWS(filepath, full_lat=True, components: iter = None):
    """
    The GLDAS/Noah soil moisture (SM), snow water equivalent (SWE), and plant canopy water storage (PCSW) are jointly
    used to calculate the TWS variations. doi: 10.1155/2019/3874742
    :param filepath: path + filename.nc of NOAH
    :param full_lat:
    :param components: iter of strings, defaults to []
    :return: 1*1 degree TWS map [m]
    """
    if components is None:
        components = ["SoilMoi0_10cm_inst", "SoilMoi10_40cm_inst", "SoilMoi40_100cm_inst", "SoilMoi100_200cm_inst",
                      "CanopInt_inst", "SWE_inst"]

    nc = LoadNOAH21().setFile(filepath)
    total, lat, lon = None, None, None
    for i in range(len(components)):
        this_component = components[i]

        if total is None:
            total, lat, lon = nc.get2dData(this_component, full_lat=full_lat)
        else:
            total += nc.get2dData(this_component, full_lat=full_lat)[0]

    assert total is not None

    return total / 1000, lat, lon
