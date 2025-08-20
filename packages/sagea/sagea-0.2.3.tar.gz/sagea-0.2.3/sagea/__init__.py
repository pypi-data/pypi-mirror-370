#!/use/bin/env python
# coding=utf-8
# @Author  : Shuhao Liu
# @Time    : 2025/6/13 10:28 
# @File    : __init__.py.py

from ._version import __version__
import os


def check_version():
    os.system("pip index versions sagea --pre")


from .pysrc.data_class.__SHC__ import SHC
from .pysrc.data_class.__GRD__ import GRD

from .pysrc.error_assessment.tch.TCH import tch

from .pysrc.load_file.LoadL2SH import load_SHC
from .pysrc.load_file.LoadCov import load_CovMatrix as load_SHCov
from .pysrc.load_file.LoadL2LowDeg import load_low_degs as load_SHLowDegs
from .pysrc.load_file.LoadSHP import load_shp

from .pysrc.auxiliary.MathTool import MathTool
from .pysrc.auxiliary.TimeTool import TimeTool
from .pysrc.auxiliary.FileTool import FileTool
from .pysrc.auxiliary import Preference

from .pysrc.data_collection.collect_auxiliary import collect_auxiliary as collect_auxiliary_data
