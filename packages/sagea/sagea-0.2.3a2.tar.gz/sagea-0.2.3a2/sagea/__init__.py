#!/use/bin/env python
# coding=utf-8
# @Author  : Shuhao Liu
# @Time    : 2025/6/13 10:28 
# @File    : __init__.py.py

from ._version import __version__
import os


def check_version():
    os.system("pip index versions sagea --pre")


from sagea.pysrc.data_class.__SHC__ import SHC
from sagea.pysrc.data_class.__GRD__ import GRD

from sagea.pysrc.error_assessment.tch.TCH import tch

from sagea.pysrc.load_file.LoadL2SH import load_SHC
from sagea.pysrc.load_file.LoadCov import load_CovMatrix as load_SHCov
from sagea.pysrc.load_file.LoadL2LowDeg import load_low_degs as load_SHLowDegs
from sagea.pysrc.load_file.LoadSHP import load_shp

from sagea.pysrc.auxiliary.MathTool import MathTool
from sagea.pysrc.auxiliary.TimeTool import TimeTool
from sagea.pysrc.auxiliary.FileTool import FileTool
import sagea.pysrc.auxiliary.Preference as Preference

from sagea.pysrc.data_collection.collect_auxiliary import collect_auxiliary as collect_auxiliary_data
