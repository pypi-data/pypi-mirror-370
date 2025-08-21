# Testing/demo-ing all of the functions that need to be run directly on NCI

import os

from DAESIM_preprocess.ozwald_8day import ozwald_8day
from DAESIM_preprocess.ozwald_daily import ozwald_daily
from DAESIM_preprocess.silo_daily import silo_daily

# Create a tmpdir and outdir in this repo for testing
if not os.path.exists('tmpdir'):
    os.mkdir('tmpdir')
if not os.path.exists('outdir'):
    os.mkdir('outdir')


# Basic tests
ds = ozwald_daily(variables=['Uavg'], lat=-34.3890427, lon=148.469499, buffer=0.01, start_year="2020", end_year="2020", outdir="outdir", stub="TEST", tmpdir="tmpdir", thredds=False, save_netcdf=True, plot=True)
assert set(ds.coords) == {'time', 'latitude', 'longitude'}  
assert set(ds.data_vars) == {'Uavg'}
assert os.path.exists("outdir/TEST_ozwald_daily_Uavg.nc")
assert os.path.exists("outdir/TEST_ozwald_daily_Uavg.png")

ds = ozwald_8day(variables=["Ssoil"], lat=-34.3890427, lon=148.469499, buffer=0.01, start_year="2020", end_year="2020", outdir="outdir", stub="TEST", tmpdir=None, thredds=False, save_netcdf=True, plot=True)
assert set(ds.coords) == {'time', 'latitude', 'longitude'}  
assert set(ds.data_vars) == {"Ssoil"}
assert os.path.exists("outdir/TEST_ozwald_8day.nc")
assert os.path.exists("outdir/TEST_ozwald_8day.png")

ds = silo_daily(variables=["radiation"], lat=-34.3890427, lon=148.469499, buffer=0.1, start_year="2020", end_year="2020", outdir="outdir", stub="TEST", tmpdir="/g/data/xe2/datasets/Climate_SILO", thredds=None, save_netcdf=True, plot=True)
assert set(ds.coords) == {'time', 'lat', 'lon'}  
assert set(ds.data_vars) == {'radiation'}
assert os.path.exists("outdir/TEST_silo_daily.nc")
assert os.path.exists("outdir/TEST_silo_daily.png")


# More comprehensive tests for OzWald daily: All variables, 3x buffers, all years, with or without netcdf & plotting
ds = ozwald_daily(variables=["Tmax", "Tmin"], lat=-34.3890427, lon=148.469499, buffer=0.01, start_year="2020", end_year="2021", outdir="outdir", stub="TEST", tmpdir="tmpdir", thredds=False, save_netcdf=True, plot=True)
assert set(ds.coords) == {'time', 'latitude', 'longitude'}  
assert set(ds.data_vars) == {"Tmax", "Tmin"}

ds = ozwald_daily(variables=["Pg"], lat=-34.3890427, lon=148.469499, buffer=0.01, start_year="2020", end_year="2020", outdir="outdir", stub="TEST", tmpdir="tmpdir", thredds=False, save_netcdf=True, plot=True)
assert set(ds.coords) == {'time', 'latitude', 'longitude'}  
assert set(ds.data_vars) == {"Pg"}

ds = ozwald_daily(variables=["Uavg", "VPeff"], lat=-34.3890427, lon=148.469499, buffer=0, start_year="2020", end_year="2020", outdir="outdir", stub="TEST", tmpdir="tmpdir", thredds=False, save_netcdf=True, plot=True)
assert set(ds.coords) == {'time', 'latitude', 'longitude'}  

ds = ozwald_daily(variables=["Ueff", "kTavg", "kTeff"], lat=-34.3890427, lon=148.469499, buffer=0.01, start_year="2020", end_year="2020", outdir="outdir", stub="TEST", tmpdir="tmpdir", thredds=False, save_netcdf=True, plot=True)
assert set(ds.coords) == {'time', 'latitude', 'longitude'}  
assert set(ds.data_vars) == {"Ueff", "kTavg", "kTeff"}

ds = ozwald_daily(variables=["Ueff"], lat=-34.3890427, lon=148.469499, buffer=0, start_year="2020", end_year="2020", outdir="outdir", stub="TEST", tmpdir="tmpdir", thredds=False, save_netcdf=True, plot=True)
assert set(ds.coords) == {'time', 'latitude', 'longitude'}  

ds = ozwald_daily(variables=["Ueff"], lat=-34.3890427, lon=148.469499, buffer=0.01, start_year="2000", end_year="2030", outdir="outdir", stub="TEST", tmpdir="tmpdir", thredds=False, save_netcdf=True, plot=True)
assert set(ds.coords) == {'time', 'latitude', 'longitude'}  

if os.path.exists("outdir/TEST_ozwald_daily_Ueff.nc"):
    os.remove("outdir/TEST_ozwald_daily_Ueff.nc")
ds = ozwald_daily(variables=["Ueff"], lat=-34.3890427, lon=148.469499, buffer=0.1, start_year="2020", end_year="2020", outdir="outdir", stub="TEST", tmpdir="tmpdir", thredds=False, save_netcdf=False, plot=True)
assert set(ds.coords) == {'time', 'latitude', 'longitude'}  
assert not os.path.exists("outdir/TEST_ozwald_daily_Ueff.nc")

if os.path.exists("outdir/TEST_ozwald_daily_Ueff.png"):
    os.remove("outdir/TEST_ozwald_daily_Ueff.png")
ds = ozwald_daily(variables=["Ueff"], lat=-34.3890427, lon=148.469499, buffer=0.1, start_year="2020", end_year="2020", outdir="outdir", stub="TEST", tmpdir="tmpdir", thredds=False, save_netcdf=True, plot=False)
assert set(ds.coords) == {'time', 'latitude', 'longitude'}  
assert not os.path.exists("TEST_ozwald_daily_Ueff.png")

# Should also test (and handle) larger buffer sizes, and locations outside Australia


# More comprehensive tests for ozwald_8day: All variables, 2x buffers, all years, with or without netcdf & plotting
ds = ozwald_8day(variables=["Ssoil"], lat=-34.3890427, lon=148.469499, buffer=0.01, start_year="2020", end_year="2021", outdir="outdir", stub="TEST", tmpdir=None, thredds=False, save_netcdf=True, plot=True)
assert set(ds.coords) == {'time', 'latitude', 'longitude'}  

ds = ozwald_8day(variables=["Ssoil"], lat=-34.3890427, lon=148.469499, buffer=0, start_year="2020", end_year="2020", outdir="outdir", stub="TEST", tmpdir=None, thredds=False, save_netcdf=True, plot=True)
assert set(ds.coords) == {'time', 'latitude', 'longitude'}  

ds = ozwald_8day(variables=["Ssoil"], lat=-34.3890427, lon=148.469499, buffer=0.01, start_year="2000", end_year="2030", outdir="outdir", stub="TEST", tmpdir=None, thredds=False, save_netcdf=True, plot=True)
assert set(ds.coords) == {'time', 'latitude', 'longitude'}  

if os.path.exists("outdir/TEST_ozwald_8day.nc"):
    os.remove("outdir/TEST_ozwald_8day.nc")
ds = ozwald_8day(variables=["Ssoil"], lat=-34.3890427, lon=148.469499, buffer=0.01, start_year="2020", end_year="2020", outdir="outdir", stub="TEST", tmpdir=None, thredds=False, save_netcdf=False, plot=True)
assert set(ds.coords) == {'time', 'latitude', 'longitude'}  
assert not os.path.exists("outdir/TEST_ozwald_8day.nc")

ds = ozwald_8day(variables=["BS", "EVI", "FMC", "GPP", "LAI", "NDVI", "NPV", "OW", "PV", "Qtot", "SN", "Ssoil"], lat=-34.3890427, lon=148.469499, buffer=0.01, start_year="2020", end_year="2020", outdir="outdir", stub="TEST", tmpdir=None, thredds=False, save_netcdf=True, plot=True)
assert set(ds.coords) == {'time', 'latitude', 'longitude'}  
assert set(ds.data_vars) == {"BS", "EVI", "FMC", "GPP", "LAI", "NDVI", "NPV", "OW", "PV", "Qtot", "SN", "Ssoil"}


# More comprehensive tests for SILO: all variables, multiple years
ds = silo_daily(variables=["min_temp"], lat=-34.3890427, lon=148.469499, buffer=0.1, start_year="2000", end_year="2030", outdir="outdir", stub="TEST", tmpdir="/g/data/xe2/datasets/Climate_SILO", thredds=None, save_netcdf=True, plot=True)
assert set(ds.coords) == {'time', 'lat', 'lon'}  
assert set(ds.data_vars) == {'min_temp'}

ds = silo_daily(variables=["monthly_rain"], lat=-34.3890427, lon=148.469499, buffer=0.1, start_year="2020", end_year="2020", outdir="outdir", stub="TEST", tmpdir="/g/data/xe2/datasets/Climate_SILO", thredds=None, save_netcdf=True, plot=True)
assert set(ds.coords) == {'time', 'lat', 'lon'}  
assert set(ds.data_vars) == {'monthly_rain'}

ds = silo_daily(variables=['daily_rain', 'min_temp', "max_temp", "et_morton_actual", "et_morton_potential"], lat=-34.3890427, lon=148.469499, buffer=0.1, start_year="2020", end_year="2020", outdir="outdir", stub="TEST", tmpdir="/g/data/xe2/datasets/Climate_SILO", thredds=None, save_netcdf=True, plot=True)
assert set(ds.coords) == {'time', 'lat', 'lon'}  
assert set(ds.data_vars) == {'daily_rain', 'min_temp', "max_temp", "et_morton_actual", "et_morton_potential"}

ds = silo_daily(variables=["vp", "vp_deficit", "evap_pan", "evap_syn", "evap_morton_lake"], lat=-34.3890427, lon=148.469499, buffer=0.1, start_year="2020", end_year="2020", outdir="outdir", stub="TEST", tmpdir="/g/data/xe2/datasets/Climate_SILO", thredds=None, save_netcdf=True, plot=True)
assert set(ds.coords) == {'time', 'lat', 'lon'}  
assert set(ds.data_vars) == {"vp", "vp_deficit", "evap_pan", "evap_syn", "evap_morton_lake"}

ds = silo_daily(variables=["rh_tmax", "rh_tmin", "et_short_crop", "et_tall_crop", "et_morton_wet", "mslp"], lat=-34.3890427, lon=148.469499, buffer=0.1, start_year="2020", end_year="2020", outdir="outdir", stub="TEST", tmpdir="/g/data/xe2/datasets/Climate_SILO", thredds=None, save_netcdf=True, plot=True)
assert set(ds.coords) == {'time', 'lat', 'lon'}  
assert set(ds.data_vars) == {"rh_tmax", "rh_tmin", "et_short_crop", "et_tall_crop", "et_morton_wet", "mslp"}