# Testing/demo-ing all of the main functions in DAESim_preprocess

print("Starting tests_local.py")

import os
import time

from DAESIM_preprocess.terrain_tiles import terrain_tiles
from DAESIM_preprocess.topography import topography
from DAESIM_preprocess.slga_soils import slga_soils
from DAESIM_preprocess.ozwald_8day import ozwald_8day
from DAESIM_preprocess.ozwald_daily import ozwald_daily
from DAESIM_preprocess.silo_daily import silo_daily
from DAESIM_preprocess.daesim_forcing import daesim_forcing, daesim_soils

# Create a tmpdir and outdir in this repo for testing
if not os.path.exists('tmpdir'):
    os.mkdir('tmpdir')
if not os.path.exists('outdir'):
    os.mkdir('outdir')

start = time.time()

# Basic tests for quickly checking all the API's
ds = ozwald_daily(variables=['Uavg'], lat=-34.3890427, lon=148.469499, buffer=0.01, start_year="2020", end_year="2020", outdir="outdir", stub="TEST", tmpdir="tmpdir", thredds=True, save_netcdf=True, plot=True)
assert set(ds.coords) == {'time', 'latitude', 'longitude'}  
assert set(ds.data_vars) == {'Uavg'}
assert os.path.exists("outdir/TEST_ozwald_daily_Uavg.nc")
assert os.path.exists("outdir/TEST_ozwald_daily_Uavg.png")

ds = ozwald_8day(variables=["Ssoil"], lat=-34.3890427, lon=148.469499, buffer=0.01, start_year="2020", end_year="2020", outdir="outdir", stub="TEST", tmpdir="tmpdir", thredds=True, save_netcdf=True, plot=True)
assert set(ds.coords) == {'time', 'latitude', 'longitude'}  
assert set(ds.data_vars) == {"Ssoil"}
assert os.path.exists("outdir/TEST_ozwald_8day.nc")
assert os.path.exists("outdir/TEST_ozwald_8day.png")

ds = terrain_tiles(lat=-34.3890427, lon=148.469499, buffer=0.005, outdir="outdir", stub="TEST", tmpdir="tmpdir", tile_level=14, interpolate=True)
assert set(ds.coords) == {'x', 'y'}  
assert set(ds.data_vars) == {'terrain'}
assert os.path.exists("tmpdir/TEST_terrain_original.tif")
assert os.path.exists("outdir/TEST_terrain.tif")

ds = topography(outdir="outdir", stub="TEST")
assert set(ds.coords) == {'x', 'y'} 
assert set(ds.data_vars) == {'terrain', 'dem_smooth', 'accumulation', 'aspect', 'slope', 'twi'}
assert os.path.exists("outdir/TEST_accumulation.tif")
assert os.path.exists("outdir/TEST_aspect.tif")
assert os.path.exists("outdir/TEST_slope.tif")
assert os.path.exists("outdir/TEST_twi.tif")
assert os.path.exists("outdir/TEST_topography.png")

slga_soils(variables=["Clay"], lat=-34.3890427, lon=148.469499, buffer=0.005, outdir="tmpdir", stub="TEST",  depths=["5-15cm"])
assert os.path.exists("tmpdir/TEST_Clay_5-15cm.tif")

ds = silo_daily(variables=["radiation"], lat=-34.3890427, lon=148.469499, buffer=0.1, start_year="2020", end_year="2020", outdir="outdir", stub="TEST", tmpdir="tmpdir", thredds=None, save_netcdf=True, plot=True)
assert set(ds.coords) == {'time', 'lat', 'lon'}  
assert set(ds.data_vars) == {'radiation'}
assert os.path.exists("outdir/TEST_silo_daily.nc")
assert os.path.exists("outdir/TEST_silo_daily.png")


# More comprehensive tests for ozwald_daily: All variables, 3x buffers, all years, with or without netcdf & plotting
ds = ozwald_daily(variables=["Tmax", "Tmin"], lat=-34.3890427, lon=148.469499, buffer=0.01, start_year="2020", end_year="2021", outdir="outdir", stub="TEST", tmpdir="tmpdir", thredds=True, save_netcdf=True, plot=True)
assert set(ds.coords) == {'time', 'latitude', 'longitude'}  
assert set(ds.data_vars) == {"Tmax", "Tmin"}

ds = ozwald_daily(variables=["Pg"], lat=-34.3890427, lon=148.469499, buffer=0.01, start_year="2020", end_year="2020", outdir="outdir", stub="TEST", tmpdir="tmpdir", thredds=True, save_netcdf=True, plot=True)
assert set(ds.coords) == {'time', 'latitude', 'longitude'}  
assert set(ds.data_vars) == {"Pg"}

ds = ozwald_daily(variables=["Uavg", "VPeff"], lat=-34.3890427, lon=148.469499, buffer=0, start_year="2020", end_year="2020", outdir="outdir", stub="TEST", tmpdir="tmpdir", thredds=True, save_netcdf=True, plot=True)
assert set(ds.coords) == {'time', 'latitude', 'longitude'}  

ds = ozwald_daily(variables=["Ueff", "kTavg", "kTeff"], lat=-34.3890427, lon=148.469499, buffer=0.01, start_year="2020", end_year="2020", outdir="outdir", stub="TEST", tmpdir="tmpdir", thredds=True, save_netcdf=True, plot=True)
assert set(ds.coords) == {'time', 'latitude', 'longitude'}  
assert set(ds.data_vars) == {"Ueff", "kTavg", "kTeff"}

ds = ozwald_daily(variables=["Ueff"], lat=-34.3890427, lon=148.469499, buffer=0, start_year="2020", end_year="2020", outdir="outdir", stub="TEST", tmpdir="tmpdir", thredds=True, save_netcdf=True, plot=True)
assert set(ds.coords) == {'time', 'latitude', 'longitude'}  

ds = ozwald_daily(variables=["Ueff"], lat=-34.3890427, lon=148.469499, buffer=0.01, start_year="2000", end_year="2030", outdir="outdir", stub="TEST", tmpdir="tmpdir", thredds=True, save_netcdf=True, plot=True)
assert set(ds.coords) == {'time', 'latitude', 'longitude'}  

if os.path.exists("outdir/TEST_ozwald_daily_Ueff.nc"):
    os.remove("outdir/TEST_ozwald_daily_Ueff.nc")
ds = ozwald_daily(variables=["Ueff"], lat=-34.3890427, lon=148.469499, buffer=0.1, start_year="2020", end_year="2020", outdir="outdir", stub="TEST", tmpdir="tmpdir", thredds=True, save_netcdf=False, plot=True)
assert set(ds.coords) == {'time', 'latitude', 'longitude'}  
assert not os.path.exists("outdir/TEST_ozwald_daily_Ueff.nc")

if os.path.exists("outdir/TEST_ozwald_daily_Ueff.png"):
    os.remove("outdir/TEST_ozwald_daily_Ueff.png")
ds = ozwald_daily(variables=["Ueff"], lat=-34.3890427, lon=148.469499, buffer=0.1, start_year="2020", end_year="2020", outdir="outdir", stub="TEST", tmpdir="tmpdir", thredds=True, save_netcdf=True, plot=False)
assert set(ds.coords) == {'time', 'latitude', 'longitude'}  
assert not os.path.exists("TEST_ozwald_daily_Ueff.png")

# Should also test (and handle) larger buffer sizes, and locations outside Australia


# More comprehensive tests for ozwald_8day: All variables, 2x buffers, multiple years, with or without netcdf & plotting
ds = ozwald_8day(variables=["Ssoil"], lat=-34.3890427, lon=148.469499, buffer=0.01, start_year="2020", end_year="2021", outdir="outdir", stub="TEST", tmpdir="tmpdir", thredds=True, save_netcdf=True, plot=True)
assert set(ds.coords) == {'time', 'latitude', 'longitude'}  

ds = ozwald_8day(variables=["Ssoil"], lat=-34.3890427, lon=148.469499, buffer=0, start_year="2020", end_year="2020", outdir="outdir", stub="TEST", tmpdir="tmpdir", thredds=True, save_netcdf=True, plot=True)
assert set(ds.coords) == {'time', 'latitude', 'longitude'}  

ds = ozwald_8day(variables=["Ssoil"], lat=-34.3890427, lon=148.469499, buffer=0.01, start_year="2020", end_year="2024", outdir="outdir", stub="TEST", tmpdir="tmpdir", thredds=True, save_netcdf=True, plot=True)
assert set(ds.coords) == {'time', 'latitude', 'longitude'}  

if os.path.exists("outdir/TEST_ozwald_8day.nc"):
    os.remove("outdir/TEST_ozwald_8day.nc")
ds = ozwald_8day(variables=["Ssoil"], lat=-34.3890427, lon=148.469499, buffer=0.01, start_year="2020", end_year="2020", outdir="outdir", stub="TEST", tmpdir="tmpdir", thredds=True, save_netcdf=False, plot=True)
assert set(ds.coords) == {'time', 'latitude', 'longitude'}  
assert not os.path.exists("outdir/TEST_ozwald_8day.nc")

ds = ozwald_8day(variables=["BS", "EVI", "FMC", "NPV"], lat=-34.3890427, lon=148.469499, buffer=0.01, start_year="2020", end_year="2020", outdir="outdir", stub="TEST", tmpdir="tmpdir", thredds=True, save_netcdf=True, plot=True)
assert set(ds.coords) == {'time', 'latitude', 'longitude'}  
assert set(ds.data_vars) == {"BS", "EVI", "FMC", "NPV"}

ds = ozwald_8day(variables=["OW", "PV",  "SN"], lat=-34.3890427, lon=148.469499, buffer=0.01, start_year="2020", end_year="2020", outdir="outdir", stub="TEST", tmpdir="tmpdir", thredds=True, save_netcdf=True, plot=True)
assert set(ds.coords) == {'time', 'latitude', 'longitude'}  
assert set(ds.data_vars) == {"OW", "PV", "SN"}

ds = ozwald_8day(variables=["GPP", "LAI", "NDVI", "Ssoil", "Qtot"], lat=-34.3890427, lon=148.469499, buffer=0.01, start_year="2020", end_year="2020", outdir="outdir", stub="TEST", tmpdir="tmpdir", thredds=True, save_netcdf=True, plot=True)
assert set(ds.coords) == {'time', 'latitude', 'longitude'}  
assert set(ds.data_vars) == {"GPP", "LAI", "NDVI", "Ssoil", "Qtot"}


# More comprehensive tests for terrain tiles: 3x buffers, 3x tile levels, with or without interpolation
ds = terrain_tiles(lat=-34.3890427, lon=148.469499, buffer=0, outdir="outdir", stub="TEST", tmpdir="tmpdir", tile_level=14, interpolate=True)
assert set(ds.coords) == {'x', 'y'}  
assert set(ds.data_vars) == {'terrain'}

ds = terrain_tiles(lat=-34.3890427, lon=148.469499, buffer=0.1, outdir="outdir", stub="TEST", tmpdir="tmpdir", tile_level=9, interpolate=True)
assert set(ds.coords) == {'x', 'y'}  
assert set(ds.data_vars) == {'terrain'}

ds = terrain_tiles(lat=-34.3890427, lon=148.469499, buffer=1, outdir="outdir", stub="TEST", tmpdir="tmpdir", tile_level=4, interpolate=True)
assert set(ds.coords) == {'x', 'y'}  
assert set(ds.data_vars) == {'terrain'}

if os.path.exists("outdir/TEST_terrain.tif"):
    os.remove("outdir/TEST_terrain.tif")
ds = terrain_tiles(lat=-34.3890427, lon=148.469499, buffer=0.005, outdir="outdir", stub="TEST", tmpdir="tmpdir", tile_level=14, interpolate=False)
assert not os.path.exists("outdir/TEST_terrain.tif")

ds = terrain_tiles(lat=-34.3890427, lon=148.469499, buffer=0.005, outdir="outdir", stub="TEST", tmpdir="tmpdir", tile_level=14, interpolate=True)
assert set(ds.coords) == {'x', 'y'}  
assert set(ds.data_vars) == {'terrain'}


# More comprehensive tests for topography: different sigma, with or without smoothing, savetifs, verbose, and plot
ds = topography(outdir="outdir", stub="TEST", smooth=False, sigma=10, ds=None, savetifs=True, verbose=True, plot=True)
assert set(ds.coords) == {'x', 'y'} 
assert set(ds.data_vars) == {'terrain', 'accumulation', 'aspect', 'slope', 'twi'}

ds = topography(outdir="outdir", stub="TEST", smooth=True, sigma=5, ds=None, savetifs=True, verbose=True, plot=True)
assert set(ds.coords) == {'x', 'y'} 
assert set(ds.data_vars) == {'terrain', 'dem_smooth', 'accumulation', 'aspect', 'slope', 'twi'}

if os.path.exists("outdir/TEST_accumulation.tif"):
    os.remove("outdir/TEST_accumulation.tif")
if os.path.exists("outdir/TEST_aspect.tif"):
    os.remove("outdir/TEST_aspect.tif")
if os.path.exists("outdir/TEST_slope.tif"):
    os.remove("outdir/TEST_slope.tif")
if os.path.exists("outdir/TEST_twi.tif"):
    os.remove("outdir/TEST_twi.tif")
ds = topography(outdir="outdir", stub="TEST", smooth=True, sigma=5, ds=None, savetifs=False, verbose=True, plot=True)
assert set(ds.coords) == {'x', 'y'} 
assert set(ds.data_vars) == {'terrain', 'dem_smooth', 'accumulation', 'aspect', 'slope', 'twi'}
assert not os.path.exists("outdir/TEST_accumulation.tif")
assert not os.path.exists("outdir/TEST_aspect.tif")
assert not os.path.exists("outdir/TEST_slope.tif")
assert not os.path.exists("outdir/TEST_twi.tif")

ds = topography(outdir="outdir", stub="TEST", smooth=True, sigma=5, ds=None, savetifs=True, verbose=False, plot=True)
assert set(ds.coords) == {'x', 'y'} 
assert set(ds.data_vars) == {'terrain', 'dem_smooth', 'accumulation', 'aspect', 'slope', 'twi'}

if os.path.exists("outdir/TEST_topography.png"):
    os.remove("outdir/TEST_topography.png")
ds = topography(outdir="outdir", stub="TEST", smooth=True, sigma=5, ds=None, savetifs=True, verbose=True, plot=False)
assert set(ds.coords) == {'x', 'y'} 
assert set(ds.data_vars) == {'terrain', 'dem_smooth', 'accumulation', 'aspect', 'slope', 'twi'}
assert not os.path.exists("outdir/TEST_topography.png")


# More comprehensive tests for slga soils: 2x buffers, all variables, all depths 
slga_soils(variables=["Clay"], lat=-34.3890427, lon=148.469499, buffer=0, outdir="tmpdir", stub="TEST",  depths=["5-15cm"])
assert os.path.exists("tmpdir/TEST_Clay_5-15cm.tif")

slga_soils(variables=["Clay"], lat=-34.3890427, lon=148.469499, buffer=0.005, outdir="tmpdir", stub="TEST",  depths=["5-15cm", "15-30cm", "30-60cm", "60-100cm"])
assert os.path.exists("tmpdir/TEST_Clay_5-15cm.tif")
assert os.path.exists("tmpdir/TEST_Clay_15-30cm.tif")
assert os.path.exists("tmpdir/TEST_Clay_30-60cm.tif")
assert os.path.exists("tmpdir/TEST_Clay_60-100cm.tif")

slga_soils(variables=["Clay", "Silt", "Sand", "pH_CaCl2", "Bulk_Density", "Available_Water_Capacity", "Effective_Cation_Exchange_Capacity",  "Total_Nitrogen", "Total_Phosphorus"], lat=-34.3890427, lon=148.469499, buffer=0.005, outdir="tmpdir", stub="TEST",  depths=["5-15cm"])
assert os.path.exists("tmpdir/TEST_Clay_5-15cm.tif")
assert os.path.exists("tmpdir/TEST_Silt_5-15cm.tif")
assert os.path.exists("tmpdir/TEST_Sand_5-15cm.tif")
assert os.path.exists("tmpdir/TEST_pH_CaCl2_5-15cm.tif")
assert os.path.exists("tmpdir/TEST_Bulk_Density_5-15cm.tif")
assert os.path.exists("tmpdir/TEST_Available_Water_Capacity_5-15cm.tif")
assert os.path.exists("tmpdir/TEST_Effective_Cation_Exchange_Capacity_5-15cm.tif")
assert os.path.exists("tmpdir/TEST_Total_Nitrogen_5-15cm.tif")
assert os.path.exists("tmpdir/TEST_Total_Phosphorus_5-15cm.tif")


# More comprehensive tests for SILO: multiple buffers, with or without saving netcdf and plotting 
# (not testing multiple variables or years locally because it takes too long)
ds = silo_daily(variables=["radiation"], lat=-34.3890427, lon=148.469499, buffer=0, start_year="2020", end_year="2020", outdir="outdir", stub="TEST", tmpdir="tmpdir", thredds=None, save_netcdf=True, plot=True)
assert set(ds.coords) == {'time', 'lat', 'lon'}  
assert set(ds.data_vars) == {'radiation'}

if os.path.exists("outdir/TEST_silo_daily.nc"):
    os.remove("outdir/TEST_silo_daily.nc")
ds = silo_daily(variables=["radiation"], lat=-34.3890427, lon=148.469499, buffer=0.01, start_year="2020", end_year="2020", outdir="outdir", stub="TEST", tmpdir="tmpdir", thredds=None, save_netcdf=False, plot=True)
assert not os.path.exists("outdir/TEST_silo_daily.nc")

if os.path.exists("outdir/TEST_silo_daily.png"):
    os.remove("outdir/TEST_silo_daily.png")
ds = silo_daily(variables=["radiation"], lat=-34.3890427, lon=148.469499, buffer=0.01, start_year="2020", end_year="2020", outdir="outdir", stub="TEST", tmpdir="tmpdir", thredds=None, save_netcdf=True, plot=False)
assert not os.path.exists("outdir/TEST_silo_daily.png")


# Testing creation of the daesim_forcing csv (Doing this last so the necessary files are all pre-downloaded)
df = daesim_forcing(outdir="outdir", stub="TEST")
assert set(df.columns) == {"Precipitation", "Runoff", "Minimum temperature", "Maximum temperature", "Soil moisture", "Vegetation growth", "Vegetation leaf area", "VPeff",	"Uavg", "SRAD"}
assert os.path.exists("outdir/TEST_DAESim_forcing.csv")

slga_soils(variables=["Clay", "Silt", "Sand", "pH_CaCl2", "Bulk_Density", "Available_Water_Capacity", "Effective_Cation_Exchange_Capacity",  "Total_Nitrogen", "Total_Phosphorus"], lat=-34.3890427, lon=148.469499, buffer=0.005, outdir="tmpdir", stub="TEST",  depths=["15-30cm"])
slga_soils(variables=["Clay", "Silt", "Sand", "pH_CaCl2", "Bulk_Density", "Available_Water_Capacity", "Effective_Cation_Exchange_Capacity",  "Total_Nitrogen", "Total_Phosphorus"], lat=-34.3890427, lon=148.469499, buffer=0.005, outdir="tmpdir", stub="TEST",  depths=["30-60cm"])
slga_soils(variables=["Clay", "Silt", "Sand", "pH_CaCl2", "Bulk_Density", "Available_Water_Capacity", "Effective_Cation_Exchange_Capacity",  "Total_Nitrogen", "Total_Phosphorus"], lat=-34.3890427, lon=148.469499, buffer=0.005, outdir="tmpdir", stub="TEST",  depths=["60-100cm"])

df = daesim_soils(outdir="outdir", stub="TEST", tmpdir="tmpdir")
assert os.path.exists("outdir/TEST_DAESim_Soils.csv")

# Testing no print statements when verbose is false
print("Re-running every command with verbose=False")
df = daesim_forcing(outdir="outdir", stub="TEST", verbose=False)
df = daesim_soils(outdir="outdir", stub="TEST", tmpdir="tmpdir", verbose=False)
ds = ozwald_daily(variables=['Uavg'], lat=-34.3890427, lon=148.469499, buffer=0.01, start_year="2020", end_year="2020", outdir="outdir", stub="TEST", tmpdir="tmpdir", thredds=True, save_netcdf=True, plot=True, verbose=False)
ds = ozwald_8day(variables=["Ssoil"], lat=-34.3890427, lon=148.469499, buffer=0.01, start_year="2020", end_year="2020", outdir="outdir", stub="TEST", tmpdir="tmpdir", thredds=True, save_netcdf=True, plot=True, verbose=False)
ds = terrain_tiles(lat=-34.3890427, lon=148.469499, buffer=0.005, outdir="outdir", stub="TEST", tmpdir="tmpdir", tile_level=14, interpolate=True, verbose=False)
ds = topography(outdir="outdir", stub="TEST", verbose=False)
slga_soils(variables=["Clay"], lat=-34.3890427, lon=148.469499, buffer=0.005, outdir="tmpdir", stub="TEST",  depths=["5-15cm"], verbose=False)
ds = silo_daily(variables=["radiation"], lat=-34.3890427, lon=148.469499, buffer=0.1, start_year="2020", end_year="2020", outdir="outdir", stub="TEST", tmpdir="tmpdir", thredds=None, save_netcdf=True, plot=True, verbose=False)
print("Finished Tests")

end = time.time()
print(f"Tests took {end - start} seconds to complete.")
