import pathlib
from enum import Enum


class GeoConstants:
    density_earth = 5517  # unit[kg/m3]
    radius_earth = 6378136.3  # unit[m]
    GM = 3.9860044150E+14  # unit[m3/s2]

    """gas constant for dry air"""
    Rd = 287.00
    # Rd = 287.06

    '''gravity constant g defined by WMO'''
    g_wmo = 9.80665
    # g_wmo = 9.7

    ''' water density'''
    density_water = 1000.0
    # density_water = 1025.0


class Config:
    aux_data_dir = pathlib.Path(__file__).parent.parent.parent / "__data__"

    check_version = True


class SHNormalization(Enum):
    full = 1


class Dimension(Enum):
    Geopotential = 0  # SHC with Dimension value <=99 support convert_type() method
    EWH = 1
    Pressure = 2
    Density = 3
    Geoid = 4
    Gravity = 5
    HorizontalDisplacementEast = 6
    HorizontalDisplacementNorth = 7
    VerticalDisplacement = 8

    Dimensionless = 100
    DimensionlessMask = 101
    DimensionlessFactor = 102


class LoveNumberMethod(Enum):
    PREM = 1
    AOD04 = 2
    Wang = 3
    IERS = 4


class LoveNumberType(Enum):
    VerticalDisplacement = 1
    HorizontalDisplacement = 2
    GravitationalPotential = 3


class SHCFilterType(Enum):
    Gaussian = 1
    Fan = 2
    AnisotropicGaussianHan = 3
    DDK = 4
    VGC = 5


class SHCDecorrelationType(Enum):
    PnMm = 1
    SlideWindowSwenson2006 = 2
    SlideWindowStable = 3


class GeometricCorrectionAssumption(Enum):
    Sphere = 1
    Ellipsoid = 2
    ActualEarth = 3


class L2DataServer(Enum):
    GFZ = 1
    ITSG = 2


class L2ProductType(Enum):
    GSM = 1
    GAA = 2
    GAB = 3
    GAC = 4
    GAD = 5


class L2InstituteType(Enum):
    CSR = 1
    GFZ = 2
    JPL = 3
    COST_G = 4
    ITSG = 5


class L2Release(Enum):
    RL05 = 5
    RL06 = 6
    RL061 = 61
    RL062 = 62

    ITSGGrace2014 = 1002014
    ITSGGrace2016 = 1002016
    ITSGGrace2018 = 1002018
    ITSGGrace_operational = 2002018


class L2ProductMaxDegree(Enum):
    Degree60 = 60
    Degree90 = 90
    Degree96 = 96
    Degree120 = 120


class L2LowDegreeType(Enum):
    Deg1 = 1
    C20 = 2
    C30 = 3


class L2LowDegreeFileID(Enum):
    TN11 = 11
    TN13 = 13
    TN14 = 14


class Satellite(Enum):
    GRACE = 1
    GRACE_FO = 2


class GridFilterType(Enum):
    VGC = 1


class VaryRadiusWay(Enum):
    """for VGC filter"""
    sin = 1
    sin2 = 2


class LeakageMethod(Enum):
    Additive = 1
    Multiplicative = 2
    Scaling = 3
    ScalingGrid = 4
    Iterative = 5
    DataDriven = 6
    ForwardModeling = 7
    BufferZone = 8


class GIAModel(Enum):
    Caron2018 = 1
    Caron2019 = 2
    ICE6GC = 3
    ICE6GD = 4


class BasinName(Enum):
    Amazon = 1
    Amur = 2
    Antarctica = 3
    Aral = 4
    Brahmaputra = 5
    Caspian = 6
    Colorado = 7
    Congo = 8
    Danube = 9
    Dnieper = 10
    Euphrates = 11
    Eyre = 12
    Ganges = 13
    Greenland = 14
    Indus = 15
    Lena = 16
    Mackenzie = 17
    Mekong = 18
    Mississippi = 19
    Murray = 20
    Nelson = 21
    Niger = 22
    Nile = 23
    Ob = 24
    Okavango = 25
    Orange = 26
    Orinoco = 27
    Parana = 28
    Sahara = 29
    St_Lawrence = 30
    Tocantins = 31
    Yangtze = 32
    Yellow = 33
    Yenisey = 34
    Yukon = 35
    Zambeze = 36
    Ocean = 37


class EmpiricalDecorrelationType(Enum):
    PnMm = 1
    window_stable = 2
    window_Wahr2006 = 3
    window_Duan2009 = 4
