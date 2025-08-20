# 1. Introduction

The level-2 time-variable gravity fields obtained from Gravity Recovery and Climate Experiment (GRACE) and its
Follow-On (GRACE-FO) mission are widely used in multi-discipline geo-science studies. However, the post-processing of
those gravity fields to obtain a desired signal is rather challenging for users that are not familiar with the level-2
products. In addition, the error assessment/quantification of those derived signals, which is of increasing demand in
science application, is still a challenging issue even among the professional GRACE(-FO) users. In this effort, the
common post-processing steps and the assessment of complicated error (uncertainty) of GRACE(-FO), are integrated into an
open-source, cross-platform and Python-based toolbox called SAGEA (SAtellite Gravity Error Assessment). With diverse
options, SAGEA provides flexibility to generate signal along with the full error from level-2 products, so that any
non-expert user can easily obtain advanced experience of GRACE(-FO) processing. Please contact Shuhao Liu (
liushuhao@hust.edu.cn) and Fan Yang (fany@plan.aau.dk) for more information.

When referencing this work, please cite:
> Liu, S., Yang, F., & Forootan, E. (2025). SAGEA: A toolbox for comprehensive error assessment of GRACE and GRACE-FO
> based mass changes. Computers & Geosciences, 196, 105825. https://doi.org/10.1016/j.cageo.2024.105825

# 2. Installation

```
pip install sagea
```

# 3. Usages

## Load files

### Load standard SH files

To load standard SH Files, use following codes:

```
shc, dates_begin, dates_end = sagea.load_SHC(filepath, key: str, lmax: int, read_rows:iterable, get_dates: bool = True)

shc = sagea.load_SHC(filepath, key: str, lmax: int, read_rows:iterable, get_dates: bool = False)

"""
param filepath: path of standard SH file, or iterable of paths
param key: str, usually "GRCOF2", "gfc", or blank string ""
param lmax: int
param read_rows: iter[int], to identify: degree index, order index, Clm, Slm
param get_dates: bool

return:
	if get_dates is True:
		SHC instance, list[datetime.date,], list[datetime.date,]
  else:
  	SHC instance
"""
```

### Load SH low-degree files

to load SH low-degrees file, use following codes:

```
sh_low_degs = sagea.load_SHLow(filepath, dates:list[datetime.date])

"""
param filepath: path of standard SH file, or iterable of paths

return:
	dict, for example:
	{
    "c10": np.ndarray[value,],
    "c10_dev": np.ndarray[value,],
	}
"""

```

Note: supports official TN-XX files for now (version 0.1.0)

### Load shape files

to load shp files, use following codes:

```
load_shp = sagea.LoadShp(filepath)
grid_basin = load_shp.get_GRD(grid_space=grid_space)  # return GRD instance
shc_basin = load_shp.get_SHC(lmax)  # return SHC instance
names = load_shp.get_attr(identity_name)  # get attributes defined in file

"""
Recommend using shp file that stores polygon information
"""
```

### Others

`sagea` provide additional scripts to load GLDAS Noah2.1 models:

```
grid_value, lat, lon = sagea.load_GLDAS_TWS(filepath, full_lat, components)
"""
param filepath:
param full_lat: bool, if True: ruturn a full global distribution
param components: list[str], identifying which components to load, defaults to 
	["SoilMoi0_10cm_inst", "SoilMoi10_40cm_inst", "SoilMoi40_100cm_inst", "SoilMoi100_200cm_inst", "CanopInt_inst", "SWE_inst"]

return: gridded value: 2d np.ndarray, latitudes: 1d np.ndarray, longtudes: 1d np.ndarray
"""
```

## SHC

### attributes

```
"""
A SHC instance stores one set or multiple sets of spherical harmonic coefficients (SHCs).
Use this codes to generate a SHC instance:
"""
shc = sagea.SHC(c, s, normalization, physical_dimension)
"""
:param c:
        if s is not None:
            harmonic coefficients c in 2-dimension (l,m), or a series (q,l,m);
        else:
            1-dimension array sorted by degree [c00, s11, c10, c11, s22, s21, ...]
            or 1-dimension array sorted by degree [[c00, s11, c10, c11, s22, s21, ...],[...]]

:param s: harmonic coefficients s in 2-dimension (l,m), or a series (q,l,m),
        or None.

:param __normalization: in preference.SHNormalization, defaults to .full.

:param __physical_dimension: in preference.PhysicalDimensions, defaults to .Dimensionless.
"""
```

in short, there are four ways to input `c` and `s`:

1. both `c` and `s` are 2-dimension `np.ndarray` with indices (l: degree, m: order), indicating one set of coefficients.
2. both `c` and `s` are 3-dimension `np.ndarray`` with indices (q:num, l: degree, m: order), indicating multiple sets of
   coefficients.
3. `s` is None, and `c` is 1-demension `np.ndarray` that indicates one set, and the sequence should be:
   `[c(0,0), s(1,1), c(1,0), c(1,1), s(2,2), s(2,1), ...]`
4. `s` is None, and `c` is 2-demension `np.ndarray` that indicates multiple sets, and the sequence should be:
   `[ [c(0,0), s(1,1), c(1,0), c(1,1), s(2,2), s(2,1), ...], ...]`

Attribute `SHC.__normalization` indicates the normalization of the SHCs in `sagea.Preference.SHNormalization`.

Attribute `SHC.__physical_dimension` indicates the physical dimension of the SHCs in `Preference.PhysicalDimensions`.

To get the basic and statistical information (such as max degree, degree-RMS, etc.), use following commands:

```
dimension = shc.get_physical_dimension()
# return physical dimension that shc indicates in type of sagea.Preference.PhysicalDimension, containing:
#  PhysicalDimension.Geopotential, in physical dimensionless
#  PhysicalDimension.EWH in unit [m]
#  PhysicalDimension.Pressure in unit [Pa]
#  PhysicalDimension.Density in unit [kg/m2]
#  PhysicalDimension.Geoid in unit [m]
#  PhysicalDimension.Gravity in unit [gal]
#  PhysicalDimension.HorizontalDisplacementEast in unit [m]
#  PhysicalDimension.HorizontalDisplacementNorth in unit [m]
#  PhysicalDimension.VerticalDisplacement in unit [m]

lmax = shc.get_lmax()
# return the max degree/order that shc indicates, in type of int.

rms = shc.get_degree_rms()
# retuen the degree rms, in 2-d np.ndarray, indicating indices (num, degree).

rss = shc.get_degree_rss()
# retuen the degree rss, in 2-d np.ndarray, indicating indices (num, degree).

crss = shc.get_cumulative_degree_rss()
# retuen the cumulative degree rss, in 2-d np.ndarray, indicating indices (num, degree).

std = shc.get_std()
# retuen the std of (multiple-set) shc, in type of SHC.

flag = shc.is_series()
# return True if shc indicates multiple sets of SHCs
```

### Addition and subtraction

SHC instance supports the addition and subtraction with following codes:

```
shc1 + shc2
shc1.add(shc2, lbegin, lend)

shc_sub1 = shc1 - shc2
shc1.subtract(shc2, lbegin, lend)

"""
lebgin and lend are given in int, to indicate which degree to start adding/subtracting, and up to which.
"""
```

### Indexing and Assignment

SHC instance supports two ways of indexing:

```
"""use int or slice to get sub-series or coefficients in a new SHC instance."""
shc_sub1 = shc[1]
shc_sub2 = shc[2:3]

"""use str to get series coefficients of certain degree and order."""
"""note that the (re) pattern should be r'[cs]\d+,\d+'."""
c2_0_series = shc["c2,0"]
s10_8_series = shc["s10,8"]

"""set new values with another SHC instance"""
shc[2:3] = shc_new


"""set new values with another series"""
shc["c2,0"] = c20_new
```

### `SHC().de_background()`

```
shc.debackground(shc_background)
"""
param: background, SHC or None, defaults to None.

deduct a given single-set shc_background for each set of shc if shc_background is not None,
or deduct the average of itself if shc_background is None.
"""
```

### `SHC().convert_type()`

- to convert the physical dimension of SHC instance, use following codes:

```
shc.convert_type(to_type: sagea.Preference.PhysicalDimension)
"""
param to_type: in type of sagea.Preference.PhysicalDimension.

convert the coefficients based on load theories into other equavilent physical dimension.
"""
```

### `SHC().replace()`

- to replace low-degree coefficients (deg-1, c20, c30), use following codes:

```
shc.replace_low_deg(index:str, new:np.ndarray or SHC)
"""
param index: str, like 'c2,0', 's1,1'
param new: 1d np.ndarray or SHC instance, with the same length of self.
"""
```

### `SHC().filter()`

- to filter the coefficients, use following codes:

```
shc.filter(method, param)
"""
filter coefficients with given method and param.
param mathod: sagea.Preference.SHCFilterType or sagea.Preference.SHCDecorrelationType.
param param: tuple, with requiements of different types of filters.

The details of method and param requirements are as follow:

if method == SHCDecorrelationType.SHCDecorrelationType.PnMm:
	param = (n, m)
	
if method == SHCDecorrelationType.SHCDecorrelationType.SlideWindowSwenson2006:
	param = (n, m, min_window_length)
	
if method == SHCDecorrelationType.SHCDecorrelationType.SlideWindowStable:
	param = (n, m, min_window_length, a, k)

if method == SHCFilterType.Gaussian:
	param = (r: int,),
  r indicates the radius [km].
	
if method == SHCFilterType.SHCFilterType.Fan:
	param = (r1: int, r2: int),
  r1, r2 indicate the radii [km].

if method == SHCFilterType.SHCFilterType.AnisotropicGaussianHan:
	param = (r1: int, r2: int, m0: int),
  r1, r2 indicate the radii [km], m0 indicates the truncation of order.

if method == SHCFilterType.SHCFilterType.DDK:
	param = (n,),
  n indicates the DDK index, optional 1-8
"""
```

Note: for the first use of DDK filter, auxiliary data would be automatically downloaded.

### `SHC().to_GRD()`

- to apply harmonic synthesis to project the SHCs onto the spatial gridded value, use following codes:

```
grd = shc_gsm.to_GRD(grid_space)
"""
pure harmonic synthesis
param grid_space: indicate the uniform spacing of grids [degree]

"""
```

## GRD

## attributes

```
"""
A GRD instance stores one set or multiple sets of global gridded value.
Use this codes to generate a GRD instance:
"""
grd = sagea.GRD(value, lat, lon, option=1, physical_dimension: Preference.PhysicalDimension = None)
"""
To create a GRID object,
one needs to specify the data (grid) and corresponding latitude range (lat) and longitude range (lon).
:param grid: 2d- or 3d-array gridded signal, index ([num] ,lat, lon)
:param lat: 1d-array, co-latitude in [rad] if option=0 else latitude in [degree]
:param lon: 1d-array, longitude in [rad] if option=0 else longitude in [degree]
:param option: set 0 if input colat and lon are in [rad]
:param physical_dimension: in type of sagea.Preference.PhysicalDimension
"""
```

The input parameters will form the following attributes respectively:

`.value`: 3-dimension `numpy.ndarray` that describes multiple sets of SHCs in shape of `(n, nlat, nlon)`, where `n`
represents the number of sets, `nlat` and `nlon` represents the latitudes and the longitudes of grids.

`.lat`: 1-dimension `numpy.ndarray` that describes the geometry latitudes in unit degree.

`.lon`: 1-dimension `numpy.ndarray` that describes the geometry longitude in unit degree.

`.__physical_dimension`: in type of `sagea.Preference.PhysicalDimension`

### `GRD().filter()`

```
grd.filter(method, param)
"""
filter gridded value with given method and param.
param mathod: sagea.Preference.SHCFilterType or sagea.Preference.SHCDecorrelationType.
param param: tuple, with requiements of different types of filters.

The details of method and param requirements are as follow:

if method == SHCDecorrelationType.GridFilterType.VGC:
	param = (r_min, r_max, sigma2, varying_way).
	r_min: minimum radius [km] at pole (lat 90),
	r_max: minimum radius [km] at equator (lat 0),
	sigma2: indicates anisotropy, optional 0-1, ana less sigma2 leads to stronger anisotropy,
	varying_way: indicates how radius varies along latitudes, in type of Preference.VaryRadiusWay
```

### `GRD().leakage()`

- to apply a leakage correction on given basin mask, use following codes:

```
grid.leakage(method: Preference.LeakageMethod, basin: np.ndarray, filter_type, filter_param: tuple, lmax: int,  # necessary params
model:3-d array,  # extra params for model-driven methods
prefilter_type, prefilter_param,  # extra params for iterative
scale_type, shc_unfiltered,  # extra params for scaling and scaling_grid
basin_conservation: np.ndarray, fm_iter_times: int, log: bool  # extra params for forward modeling
)

"""
notes:
params filter_type and filter_param should be the same with previous filter config.
param basin should be 2d-array indicating the regional mask (1 inside and 0 elsewhere).
param model should be the same shape with grid.value.
param basin_conservation should be 2d-array mask to maintain the gloabal mass conservation (ocean, for example).
"""
```

### `GRD().seismic()`

- to apply a seismic correction, use following codes:

```
grd.seismic(dates: list[datetime.date,], events: dict)
"""
notes:
param dates should be the same length with grids.
param events should be dict in structure like:
	{
    'Tohoku-Oki': {'teq': [2011.191], 'tau': [0.32], 'lat_range': [30.0, 45.5], 'lon_range': [130.0, 151.5]},
    'Sumatra': {'teq': [2004.98, 2012.58], 'tau': [0.32, 0.32], 'lat_range': [-10.0, 9.5], 'lon_range': [84.0, 103.5]},
    ...
	}
"""
```

### `GRD().de_sliasing()`

- to fit and deduct long-term aliasing signals, use following codes:

```
grd. de_aliasing(dates_ave, s2: bool, p1: bool, s1=: bool, k2=: bool, k1=: bool)
```

### `GRD().regional_extraction()`

- to integral in basin and get the summed or averaged signals, use following codes:

```
grd.regional_extraction(grid_region, average: bool)
"""
notes:
grid_region should be 2d-array indicating the region (1 inside and 0 elsewhere)
average=True means that the summed result (TWS, for example) is divided by the area to obtain the average (EWH, for example)
"""
```

### Save results

- to save grd results, use following codes:

```
grd.to_file(path: pathlib.Path, filepath: pathlib.Path, filetype=None, rewrite=False, time_dim: list[datetime.date,], description:str=None)

"""
notes:
filename of path should include file suffix, for now ".nc", ".npz" and ".hdf5" are supported.
param time_dim should be the same length with grids.
"""
```
