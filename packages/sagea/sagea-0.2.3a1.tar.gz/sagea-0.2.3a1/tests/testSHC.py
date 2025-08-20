#!/use/bin/env python
# coding=utf-8
# @Author  : Shuhao Liu
# @Time    : 2025/6/13 12:53 
# @File    : testSHC.py
import copy
import os
import pathlib
import subprocess
from curses.ascii import isdigit

import matplotlib.pyplot as plt
import numpy as np
from tqdm import trange

import sagea
from sagea import MathTool

from scripts.PlotGrids import plot_grids


def demo():
    """demo program of GRACE post-processing"""
    lmax = 60
    grid_space = 1
    begin_year, end_year = 2002, 2015

    '''load files'''
    # load L2 GSM
    print("loading GSM files ...")
    gsm_path_list = []
    for year in range(begin_year, end_year + 1):
        gsm_dir = pathlib.Path(f"data/L2_SH_products/GSM/CSR/RL06/BA01/{year}")
        gsm_path_list += list(gsm_dir.iterdir())
    gsm_path_list.sort()
    shc_gsm, dates_begin, dates_end = sagea.load_SHC(gsm_path_list, key="GRCOF2", lmax=lmax, get_dates=True)
    dates_ave = sagea.TimeTool.get_average_dates(dates_begin, dates_end)

    # load basin
    print("loading Basin ...")
    # basin_path_shp = pathlib.Path("data/basin_mask/Shp/bas200k_shp")
    # load_shp = sagea.LoadShp(basin_path_shp)
    # grid_basin = load_shp.get_GRD(grid_space=grid_space)  # load basin mask (in GRID)
    # basin_mask = grid_basin.value[10]

    basin_path_sh = pathlib.Path("data/auxiliary/ocean360_grndline.sh")
    shc_basin = sagea.load_SHC(basin_path_sh, key=None, lmax=lmax, get_dates=False)
    grid_basin = shc_basin.to_GRD(grid_space=grid_space)
    grid_basin.limiter(threshold=0.5, beyond=1, below=0)
    basin_mask = grid_basin.value[0]

    # load L2 GAD
    print("loading GAD files ... ")
    gad_path_list = []
    for year in range(begin_year, end_year + 1):
        gad_dir = pathlib.Path(f"data/L2_SH_products/GAD/CSR/RL06/BC01/{year}")
        gad_path_list += list(gad_dir.iterdir())
    gad_path_list.sort()
    shc_gad = sagea.load_SHC(gad_path_list, key="GRCOF2", lmax=lmax, get_dates=False)

    # load L2 GAA
    print("loading GAA files ... ")
    gaa_path_list = []
    for year in range(begin_year, end_year + 1):
        gaa_dir = pathlib.Path(f"data/L2_SH_products/GAA/GFZ/RL06/BC01/{year}")
        gaa_path_list += list(gaa_dir.iterdir())
    gaa_path_list.sort()
    shc_gaa = sagea.load_SHC(gaa_path_list, key="GRCOF2", lmax=lmax, get_dates=False)

    # load low-degrees
    l2_low_deg_path_list = [
        pathlib.Path("data/L2_low_degrees/TN-13_GEOC_CSR_RL06.txt"),
        pathlib.Path("data/L2_low_degrees/TN-14_C30_C20_SLR_GSFC.txt"),
    ]
    sh_low_degs = sagea.load_SHLow(l2_low_deg_path_list)

    # load background model
    gif_48_sh_path = "data/auxiliary/GIF48.gfc"
    shc_gif48 = sagea.load_SHC(gif_48_sh_path, key="gfc", lmax=lmax, get_dates=False)

    # load GIA model
    gia_sh_path = "data/GIA/GIA.ICE-6G_D.txt"
    shc_gia_trend = sagea.load_SHC(gia_sh_path, key=None, lmax=lmax, get_dates=False)

    # laod Noah2.1 model
    # print("loading Noah2.1 files ... ")
    # grid_value_model = []
    # lat_noah, lon_noah = None, None
    # for i in trange(len(dates_ave)):
    #     year, month = dates_ave[i].year, dates_ave[i].month
    #     noah_file_name = f"GLDAS_NOAH10_M.A{str(year)}{str(month).rjust(2, '0')}.021.nc4"
    #     if year < 2019 or (year == 2019 and month <= 3):
    #         noah_file_name += ".SUB.nc4"
    #     noah_path = pathlib.Path("data/Noah2.1") / noah_file_name
    #     this_grd_value, lat_noah, lon_noah = sagea.load_GLDAS_TWS(filepath=noah_path)
    #     grid_value_model.append(this_grd_value)
    # grid_value_model = np.array(grid_value_model)
    # grid_value_model -= np.mean(grid_value_model, axis=0)
    # grd_noah = sagea.GRD(grid_value_model, lat_noah, lon_noah)

    '''begin processing'''
    # replace low-degree coefficients
    print("replacing low-degree coefficients ...")
    shc_gsm.replace_low_degs(
        dates_begin=dates_begin, dates_end=dates_end, low_deg=sh_low_degs,
        c10=True, c11=True, s11=True,
    )

    # subtract GIA
    print("subtracting low-degree coefficients ...")
    shc_gia_monthly = shc_gia_trend.linear_expand(dates_ave)
    shc_gia_monthly.de_background()
    shc_gsm -= shc_gia_monthly
    shc_gsm.de_background(shc_gif48)

    # add GAD
    print("subtracting low-degree coefficients ...")
    shc_gsm += shc_gad

    # subtract GMAM by GAA degree-0
    # print("GMAM correction ...")
    # shc_gsm.subtract(shc_gaa, lend=0)

    # geometric correction
    # print("geometric correction ...")
    # shc_gsm.geometric(assumption=sagea.Preference.GeometricCorrectionAssumption.Ellipsoid, log=True)

    # filtering
    print("filtering ...")
    shc_gsm_unfiltered = copy.deepcopy(shc_gsm)
    shc_gsm_unfiltered.convert_type(to_type=sagea.Preference.Dimension.EWH)

    filter_method, filter_param = sagea.Preference.SHCFilterType.DDK, (2,)
    shc_gsm.filter(method=filter_method, param=filter_param)
    # shc.filter(method=sagea.Preference.SHCFilterType.Gaussian, param=(300,))
    # shc.filter(method=sagea.Preference.SHCFilterType.Fan, param=(300, 500,))
    # shc.filter(method=sagea.Preference.SHCFilterType.AnisotropicGaussianHan, param=(300, 500, 30))

    # harmonic synthesis
    print("spectral-spatial convertion ...")
    shc_gsm.convert_type(to_type=sagea.Preference.Dimension.EWH)
    grd = shc_gsm.to_GRD(grid_space=grid_space)

    # seismic correction
    seismic_events = {
        'Tohoku-Oki': {'teq': [2011.191], 'tau': [0.32], 'lat_range': [30.0, 45.5], 'lon_range': [130.0, 151.5]},
        'Sumatra': {'teq': [2004.98, 2012.58], 'tau': [0.32, 0.32], 'lat_range': [-10.0, 9.5],
                    'lon_range': [84.0, 103.5]},
        'Maule': {'teq': [2010.158], 'tau': [0.32], 'lat_range': [-40.0, -30.5], 'lon_range': [-80.0, -60.5]},
        'Chile': {'teq': [2010.167], 'tau': [0.32], 'lat_range': [-41.0, -31.5], 'lon_range': [-83.0, -63.5]},
        'Nias': {'teq': [2005.238], 'tau': [0.32], 'lat_range': [-4.0, 9.5], 'lon_range': [84.0, 103.5]},
        'Bengkulu': {'teq': [2007.698], 'tau': [0.32], 'lat_range': [-8.0, 3.5], 'lon_range': [96.0, 107.5]},
        'Okhotsk': {'teq': [2013.394], 'tau': [0.32], 'lat_range': [45.0, 64.5], 'lon_range': [144.0, 175.5]}
    }
    grd.seismic(dates=dates_ave, events=seismic_events)

    ewh_uncorrected = grd.regional_extraction(basin_mask)

    # leakage correction
    # grd.leakage(
    #     method=sagea.Preference.LeakageMethod.DataDriven, basin=basin_mask,
    #     shc_unfiltered=shc_gsm_unfiltered,
    #     filter_type=filter_method, filter_param=filter_param,
    #     lmax=lmax,
    #     model=grd_noah
    # )

    # ewh_corrected = grd.regional_extraction(basin_mask)

    year_frac = sagea.TimeTool.convert_date_format(dates_ave, output_type=sagea.TimeTool.DateFormat.YearFraction)

    plt.plot(year_frac, ewh_uncorrected, label="uncorrected")
    # plt.plot(year_frac, ewh_corrected, label="corrected")

    plt.legend()

    plt.show()


def demo_iter():
    lmax = 60
    grid_space = 1
    begin_year, end_year = 2002, 2002

    '''load files'''
    # load L2 GSM
    print("loading GSM files ...")
    gsm_path_list = []
    for year in range(begin_year, end_year + 1):
        gsm_dir = pathlib.Path(f"data/L2_SH_products/GSM/CSR/RL06/BA01/{year}")
        gsm_path_list += list(gsm_dir.iterdir())
    gsm_path_list.sort()
    shc_gsm, dates_begin, dates_end = sagea.load_SHC(gsm_path_list, key="GRCOF2", lmax=lmax, get_dates=True)
    shc_gsm2 = copy.deepcopy(shc_gsm)
    shc_gsm2.value *= 2

    dates_ave = sagea.TimeTool.get_average_dates(dates_begin, dates_end)

    c20 = list(shc_gsm["c2,0"] + 1)
    shc_gsm["c2,0"] = c20

    print(shc_gsm["c2,0"])


def demo_leakage():
    noah_dir = pathlib.Path("data/Noah2.1/")
    noah_path_list = list(noah_dir.iterdir())
    noah_path_list.sort()

    mask = np.load("data/basin_mask/grids/Amazon_maskGrid.dat(360,720).npy")
    # mask = np.load("data/basin_mask/grids/land_maskGrid.dat(360,720).npy")
    lat, lon = sagea.MathTool.get_global_lat_lon_range(0.5)
    mask, lat, lon = sagea.MathTool.resample_global_mask(mask, lat, lon, target_resolution=1)

    noah_path_list = noah_path_list[:20]

    gldas_grid_value = []
    lat, lon = None, None
    for i in trange(len(noah_path_list), desc="loading GLDAS"):
        g, lat, lon = sagea.load_GLDAS_TWS(noah_path_list[i])
        gldas_grid_value.append(g)
    gldas_grid_value = np.array(gldas_grid_value)
    gldas_grid_value -= np.min(gldas_grid_value, axis=0)

    grd_gldas = sagea.GRD(gldas_grid_value, lat, lon)

    leak_in = grd_gldas.get_leakage(
        leak_type="in", mask=mask,
        filter_type=sagea.Preference.SHCFilterType.Gaussian,
        filter_params=(300,)
    )

    scale_basin = grd_gldas.get_leakage_scale(
        scale_type="basin", mask=mask,
        filter_type=sagea.Preference.SHCFilterType.Gaussian,
        filter_params=(300,)
    )
    print(scale_basin)

    scale_grid_value = grd_gldas.get_leakage_scale(
        scale_type="grid", mask=mask,
        filter_type=sagea.Preference.SHCFilterType.Gaussian,
        filter_params=(300,)
    )
    plot_grids(scale_grid_value > 1, grd_gldas.lat, grd_gldas.lon)

    grd_gldas.leakage_fm(
        mask=mask,
        filter_type=sagea.Preference.SHCFilterType.Gaussian,
        filter_params=(300,),
        lmax=60
    )
    plot_grids(grd_gldas.value[:3], grd_gldas.lat, grd_gldas.lon)

    # plt.plot(leak_in)
    # plt.show()


if __name__ == "__main__":
    demo_leakage()
