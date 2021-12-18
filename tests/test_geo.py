import os
from copy import copy

import geopandas as gpd
import numpy as np
import rasterio as rio

from elapid import geo

# set the test raster data paths
directory_path, script_path = os.path.split(os.path.abspath(__file__))
data_path = os.path.join(directory_path, "data")
raster_1b = os.path.join(data_path, "test-raster-1band.tif")
raster_2b = os.path.join(data_path, "test-raster-2bands.tif")
raster_1b_offset = os.path.join(data_path, "test-raster-1band-offset.tif")
with rio.open(raster_1b, "r") as src:
    raster_1b_profile = copy(src.profile)

# set some crs variables
wkt = 'GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563,AUTHORITY["EPSG","7030"]],AUTHORITY["EPSG","6326"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.01745329251994328,AUTHORITY["EPSG","9122"]],AUTHORITY["EPSG","4326"]]'
proj4 = "+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs"
epsg_code = 4326
epsg_str = f"EPSG:{epsg_code}"


def test_xy_to_geoseries():
    lon, lat = (-120, 38)
    geoseries = geo.xy_to_geoseries(lon, lat, crs=epsg_str)
    assert geoseries.x[0] == lon
    assert geoseries.y[0] == lat


# TODO
def test_pseudoabsence_from_raster():
    pass


# TODO
def test_pseudoabsence_from_bias_file():
    pass


# TODO
def test_pseudoabsence_from_vector():
    pass


# TODO
def test_pseudoabsence_from_geoseries():
    pass


def test_parse_crs_string():
    assert geo.parse_crs_string(wkt) == "wkt"
    assert geo.parse_crs_string(proj4) == "proj4"
    assert geo.parse_crs_string(epsg_str) == "epsg"


def test_string_to_crs():
    crs = geo.string_to_crs(wkt)
    assert crs.to_epsg() == epsg_code

    crs = geo.string_to_crs(proj4)
    assert crs.to_epsg() == epsg_code

    crs = geo.string_to_crs(epsg_str)
    assert crs.to_epsg() == epsg_code


def test_crs_match():
    lon, lat = (-120, 38)
    geoseries = geo.xy_to_geoseries(lon, lat, crs=epsg_str)
    gpd_crs = geoseries.crs
    rio_crs = rio.crs.CRS.from_epsg(epsg_code)

    assert geo.crs_match(rio_crs, gpd_crs) is True
    assert geo.crs_match(gpd_crs, wkt) is True
    assert geo.crs_match(rio_crs, epsg_str) is True
    assert geo.crs_match(wkt, proj4) is True

    assert geo.crs_match(rio_crs, "epsg:32610") is False


# TODO
def test_raster_values_from_vector():
    pass


def test_raster_values_from_geoseries():
    # create a single point in the origin of the test data
    with rio.open(raster_1b, "r") as src:
        x, y = src.xy(0, 0)
        geoseries = geo.xy_to_geoseries(x, y, crs=src.crs)

    # test on one band input
    df = geo.raster_values_from_geoseries(geoseries, [raster_1b])
    b1 = df["band_1"].iloc[0]
    assert b1 == 0

    # test on two band input
    df = geo.raster_values_from_geoseries(geoseries, [raster_2b])
    b1 = df["band_1"].iloc[0]
    b2 = df["band_2"].iloc[0]
    assert b1 == 0
    assert b2 == 65280

    # test on multi-raster input
    df = geo.raster_values_from_geoseries(geoseries, [raster_1b, raster_2b])
    b1 = df["band_1"].iloc[0]
    b2 = df["band_2"].iloc[0]
    b3 = df["band_3"].iloc[0]
    assert b1 == 0
    assert b2 == 0
    assert b3 == 65280

    # test it works on lots of points
    n = 100
    df = geo.raster_values_from_geoseries(geoseries.repeat(n), [raster_1b])
    b1 = df["band_1"].iloc[n - 1]
    assert b1 == 0

    # test the slow read
    n = 10
    df = geo.raster_values_from_geoseries(geoseries.repeat(n), [raster_1b], iterate=True)
    b1 = df["band_1"].iloc[n - 1]
    assert b1 == 0