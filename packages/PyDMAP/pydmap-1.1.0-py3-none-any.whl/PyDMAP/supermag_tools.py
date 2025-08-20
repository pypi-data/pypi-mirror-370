"""
Tools and example tests showing how to access SuperMAG DataMap files.

Basics:
  fname = ...
  mydmap, err = PyDMAP.read_datamap(fname1)

Fetching from AWS S3:
  s3uri = "s3://..."
  mydmap, err = stream_dmap_from_s3(s3uri)

Selecting Stations by Lat/Lon:
  station_ids, station_indices = get_stations_in_box(mydmap, -90, 90, 0, 360)

Plotting:
  all_stations_heatmap(mydmap)

  station_code = get_all_stations(mydmap)[0] # e.g. the 1st in its list
  timeseries = plot_station_timeseries(mydmap, station_code)

  timeseries = plot_station_timeseries(mydmap, station_code,
                    lat_min=-90, lat_max=90, lon_min=-180, lon_max=180)

Note we include conversion from dict of numpy arrays to a pandas DataFrame:
  df = supermag_tools.pydmap_to_dataframe(mydmap)

You can then easily do xarray and NetCDF:
  import xarray
  xr = xarray.Dataset.from_dataframe(df)
  fname_nc = re.sub(r'.dmap','.nc',fname)
  xr.to_netcdf(fname_nc, format='NETCDF4')

You can also save as CDF:
  import df_to_cdf
  fname_cdf = re.sub(r'.dmap','.cdf',fname)
  df_to_cdf.df_to_cdf(df, fname_cdf)

"""

import io
import os
import re
import numpy as np
import pandas as pd
import PyDMAP as dmap
import matplotlib.pyplot as plt
try:
    import df_to_cdf
except:
    print("DataFrame to CDF not enabled, please install/find df_to_cdf.py")
try:
    import boto3
    from botocore import UNSIGNED
    from botocore.client import Config
except:
    print("S3 read not enabled, please install boto3, botocore")

setA = {
    "id": "grdvec.id",
    "north": "grdvec.vec.val.north",
    "east": "grdvec.vec.val.east",
    "vertical": "grdvec.vec.val.vertical",
    "lat": "grdvec.vec.lat",
    "lon": "grdvec.vec.lon"
}
setB = {
    "id": "id",
    "north": "N",
    "east": "E",
    "vertical": "Z",
    "lat": "glat",
    "lon": "glon"
}
            
    
def plot_station_timeseries(
    mydmap,
    station_code,
    components=["north", "east", "vertical"],
    lat_min=-90,
    lat_max=90,
    lon_min=-180,
    lon_max=180,
    plot=True,
):
    """
    Using the pydmap numpy array, plots the time series for a station,
    optionally verifying/subselecting only those in the lat/lon box.
    Specify a 3-letter station code (e.g., "NEW"),
    Choose the component ("north", "east", "vertical"),
    Set your lat/lon bounding box,
    Automatically extract, filter, and plot that station’s time series (if it lies within the bounds).
    """

    myset = setA if 'grdvec.id' in mydmap.keys() else setB
    # Validate component
    comp_map = {
        "north": myset["north"],
        "east": myset["east"],
        "vertical": myset["vertical"],
    }
    if isinstance(components, str):
        components = [components]
    components = [c for c in components if c in comp_map.keys()]

    # Extract static metadata from t=0
    id0 = mydmap[myset["id"]][0]
    lat0 = np.array(mydmap[myset["lat"]][0])
    lon0 = np.array(mydmap[myset["lon"]][0])

    # Step 1: Match code to full index
    matches = np.where(id0 == station_code)[0]
    if len(matches) == 0:
        print(f"No match for station {station_code}")
        return
    full_index = matches[0]

    # Step 2: Check lat/lon bounds
    if not (
        lat_min <= lat0[full_index] <= lat_max
        and lon_min <= lon0[full_index] <= lon_max
    ):
        print(f"Station {station_code} is outside the lat/lon box.")
        return None

    # Step 3: Extract component data (list of arrays, one per time)
    series = {}
    for comp in components:

        comp_all = mydmap[comp_map[comp]]
        time = pd.to_datetime(mydmap["time.epoch"], unit="s")

        # Step 4: Build time series with fallback for missing times
        series[comp] = [
            v[full_index] if full_index < len(v) else np.nan for v in comp_all
        ]

        if plot:
            # Step 5: Plot
            plt.figure(figsize=(10, 4))
            plt.plot(time, series[comp], label=f"{comp.title()} @ {station_code}")
            plt.xlabel("Time")
            plt.ylabel("nT")
            plt.title(f"{comp.title()} Component at Station {station_code}")
            plt.grid(True)
            plt.tight_layout()
            plt.show()

    return series


def test_plot_station_timeseries(mydmap,station=None):
    if station == None:
        stationlist = get_all_stations(mydmap)
        station = stationlist[0]
    ignore = plot_station_timeseries(mydmap, station)
    return True

def all_stations_heatmap(mydmap, components=["north", "east", "vertical"]):
    """Plots all supermag stations as a heat map, using pydmap numpy array"""

    myset = setA if 'grdvec.id' in mydmap.keys() else setB
    comp_map = {
        "north": myset["north"],
        "east": myset["east"],
        "vertical": myset["vertical"],
    }
    if isinstance(components, str):
        components = [components]
    components = [c for c in components if c in comp_map.keys()]
    for comp in components:
        compdata = mydmap[comp_map[comp]]
        max_stations = max(len(vec) for vec in compdata)
        n_times = len(compdata)

        # Fill a masked array (or NaN) for irregular station counts
        compdata_matrix = np.full((n_times, max_stations), np.nan)

        for i, vec in enumerate(compdata):
            compdata_matrix[i, : len(vec)] = vec

        # Plot it
        plt.imshow(
            compdata_matrix.T,
            aspect="auto",
            origin="lower",
            extent=[0, n_times, 0, max_stations],
        )
        plt.xlabel("Time Index")
        plt.ylabel("Station Index")
        plt.title(f"{comp} Component Across All Stations")
        plt.colorbar(label="nT")
        plt.show()


def test_all_stations_heatmap(mydmap):
    all_stations_heatmap(mydmap)
    return True

def get_all_stations(mydmap):
    """ From the datamap object, return the list of all stations contained
    in that dataset
    """
    myset = setA if 'grdvec.id' in mydmap.keys() else setB
    return mydmap[myset["id"]][0]

def get_stations_in_box(mydmap, lat_min, lat_max, lon_min, lon_max):
    """Returns list of stations and their ids from the pydmap numpy array
    that are in the given lat/lon box
    """
    myset = setA if 'grdvec.id' in mydmap.keys() else setB
    ids = mydmap[myset["id"]]  # List of station IDs
    lats = mydmap[myset["lat"]]  # List of lat arrays (1 per time step)
    lons = mydmap[myset["lon"]]  # Same shape as lat
    # Assume station ordering is stable — take first time step as representative
    lat0 = lats[0]  # array of shape (N,)
    lon0 = lons[0]
    id0 = ids[0]  # should be list/array of strings or IDs
    lat0 = np.array(lat0)
    lon0 = np.array(lon0)
    station_mask = (
        (lat0 >= lat_min) & (lat0 <= lat_max) & (lon0 >= lon_min) & (lon0 <= lon_max)
    )
    station_indices = np.where(station_mask)[0]
    station_ids = np.array(id0)[station_indices]
    return station_ids, station_indices


def test_get_stations_in_box(mydmap):
    lat_min, lat_max = -20, 20 # 40, 70  # example
    lon_min, lon_max = 50, 100
    ids, indices = get_stations_in_box(mydmap, lat_min, lat_max, lon_min, lon_max)
    print(f"\tFound {len(ids)} stations in box {lat_min}-{lat_max},{lon_min}-{lon_max}")
    return True, ids, indices

def time_series_for_stations(mydmap, station_indices):
    """Returns the 3 vector elements from the pydmap numpy array for the
    given stations.
    Requires the station indices, which you can get from either
    get_stations_in_box() or get_id_in_dmap() or get_all_stations()
    """
    myset = setA if 'grdvec.id' in mydmap.keys() else setB
    north_all = mydmap[myset["north"]]
    east_all = mydmap[myset["east"]]
    vertical_all = mydmap[myset["vertical"]]
    time = mydmap["time.epoch"]

    north_selected = [
        [vec[i] if i < len(vec) else np.nan for i in station_indices]
        for vec in north_all
    ]
    east_selected = [
        [vec[i] if i < len(vec) else np.nan for i in station_indices]
        for vec in east_all
    ]
    vertical_selected = [
        [vec[i] if i < len(vec) else np.nan for i in station_indices]
        for vec in vertical_all
    ]
    north_selected = np.array(north_selected)  # shape: [T, N_selected]
    east_selected = np.array(east_selected)
    vertical_selected = np.array(vertical_selected)
    return north_selected, east_selected, vertical_selected


def test_time_series_for_stations(mydmap):
    lat_min, lat_max = 40, 70  # example
    lon_min, lon_max = -100, -50
    ids, indices = get_stations_in_box(mydmap, lat_min, lat_max, lon_min, lon_max)
    n, e, v = time_series_for_stations(mydmap, indices)
    return True

def get_id_in_dmap(mydmap, station_code):
    """ Search on a given station code and find its index in the
    full station list from the pydmap numpy array, such that you can
    then fetch the data for that index
    """
    myset = setA if 'grdvec.id' in mydmap.keys() else setB
    id0 = mydmap[myset["id"]][0]  # List of station IDs
    matches = np.where(id0 == station_code)[0]
    if len(matches) == 0:
        print(f"No match for station {station_code}")
        return None
    full_index = matches[0]
    return full_index


def test_get_id_in_dmap(mydmap):
    print("\tFound sample ID for 'UPN',",get_id_in_dmap(mydmap, "UPN"))
    return True

def pydmap_to_dataframe(mydmap, lat_min=None, lat_max=None, lon_min=None, lon_max=None):
    """ Utility to convert pydmap numpy array to a pandas DataFrame
    The usual SuperMAG gridded vector collections such as
    '../sample_data/20141231.supermag.grdvec.60s.rev-0006.dmap'
    require some re-packing, whereas a single station file such as
    '../sample_data/2015_LRM.mag.60s.rev-0006.dmap' converts directly
    to a dataframe.
    """
    myset = setA if 'grdvec.id' in mydmap.keys() else setB
    if myset["id"] == "id":
        # single station not collection, so easier conversion
        return pd.DataFrame(mydmap)
    
    times = pd.to_datetime(mydmap["time.epoch"], unit="s")
    ids_all = mydmap[myset["id"]]
    lats_all = mydmap[myset["lat"]]
    lons_all = mydmap[myset["lon"]]
    Bx_all = mydmap[myset["north"]]
    By_all = mydmap[myset["east"]]
    Bz_all = mydmap[myset["vertical"]]

    records = []

    for t_idx, t in enumerate(times):
        ids = np.array(ids_all[t_idx])
        lats = np.array(lats_all[t_idx])
        lons = np.array(lons_all[t_idx])
        Bx = np.array(Bx_all[t_idx])
        By = np.array(By_all[t_idx])
        Bz = np.array(Bz_all[t_idx])

        # Apply optional bounding box filter
        if None not in (lat_min, lat_max, lon_min, lon_max):
            mask = (
                (lats >= lat_min)
                & (lats <= lat_max)
                & (lons >= lon_min)
                & (lons <= lon_max)
            )
        else:
            mask = np.full_like(lats, True, dtype=bool)

        for i in np.where(mask)[0]:
            records.append(
                {
                    "time": t,
                    "station_id": ids[i],
                    "lat": lats[i],
                    "lon": lons[i],
                    "north": Bx[i],
                    "east": By[i],
                    "vertical": Bz[i],
                }
            )

    df = pd.DataFrame(records)
    return df

def test_pydmap_to_dataframe(mydmap):
    # Without filtering (all stations)
    df_all = pydmap_to_dataframe(mydmap)

    # With bounding box
    df_filtered = pydmap_to_dataframe(
        mydmap, lat_min=40, lat_max=70, lon_min=-100, lon_max=-50
    )

    print("\tSample dataframe head:",df_filtered.head())
    return True

def stream_dmap_from_s3(s3uri):
    """
    Bundles together fetching a DataMap file in S3 (anon/no-key needed)
    and returns the dmap, or None if it fails
    """
    # S3 read specific bytes
    s3c = boto3.client('s3',config=Config(signature_version=UNSIGNED))
    mybucket = s3uri.split('/')[2]
    mykey = '/'.join(s3uri.split('/')[3:])
    #print(mybucket,mykey)
    obj = s3c.get_object(Bucket=mybucket,Key=mykey)
    rawdata=obj['Body'].read()
    bdata=io.BytesIO(rawdata)
    return dmap.read_datamap(bdata)
    #with open('2020020102.supermag.grdvec.01s.rev-0006.dmap','rb') as f:
    #    rawdata = f.read()

def test_stream_dmap_from_s3(s3uri=None):
    if s3uri == None:
        s3uri='s3://gov-nasa-hdrl-data1/contrib/jhuapl/supermag/mag.01s/global/2020/20200201/2020020102.supermag.grdvec.01s.rev-0006.dmap'
    mydmap, err = stream_dmap_from_s3(s3uri)

    if mydmap == None:
        print("Failed to read",s3uri)
        return False
    else:
        stationlist = get_all_stations(mydmap)
        #print(stationlist[0:3])
        for station in stationlist[0:3]:
            test_plot_station_timeseries(mydmap,station)
        return True

def test_df_to_cdf(fname=None):
    """ Additional test, not called in __main__ below
        Requires the df_to_cdf.py file
    """
    if fname == None:
        fname = "../sample_data/20141231.supermag.grdvec.60s.rev-0006.dmap"
    mydmap, err = dmap.read_datamap(fname)
    df = pydmap_to_dataframe(mydmap)
    fname2 = re.sub(r".dmap",".cdf",fname)
    df_to_cdf.df_to_cdf(df, fname2)

    
def test_all(fname=None, s3uri=None):
    if fname == None:
        fname = "../sample_data/20141231.supermag.grdvec.60s.rev-0006.dmap"
    if s3uri == None:
        s3uri='s3://gov-nasa-hdrl-data1/contrib/jhuapl/supermag/mag.01s/global/2020/20200201/2020020102.supermag.grdvec.01s.rev-0006.dmap'
    mydmap, err = dmap.read_datamap(fname)
    if mydmap == None:
        print("Error in dmap.read_datamap()")
    else:
        print("Success, dmap.read_datamap()")
    if test_plot_station_timeseries(mydmap):
        print("Success, test_plot_station_timeseries(mydmap)")
    else:
        print("Error in test_plot_station_timeseries(mydmap)")
    if test_all_stations_heatmap(mydmap):
        print("Success, test_all_stations_heatmap(mydmap)")
    else:
        print("Error in test_all_stations_heatmap(mydmap)")
    if test_get_stations_in_box(mydmap)[0]:
        print("Success, test_get_stations_in_box(mydmap)")
    else:
        print("Error in test_get_stations_in_box(mydmap)")
    if test_time_series_for_stations(mydmap):
        print("Success, test_time_series_for_stations(mydmap)")
    else:
        print("Error in test_time_series_for_stations(mydmap)")
    if test_get_id_in_dmap(mydmap):
        print("Success, test_get_id_in_dmap(mydmap)")
    else:
        print("Error in test_get_id_in_dmap(mydmap)")
    if test_pydmap_to_dataframe(mydmap):
        print("Success, test_pydmap_to_dataframe(mydmap)")
    else:
        print("Error in test_pydmap_to_dataframe(mydmap)")
    if test_stream_dmap_from_s3():
        print("Success, test_stream_dmap_from_s3(s3uri)")
    else:
        print("Error in test_stream_dmap_from_s3()")


if __name__ == "__main__":
    mydmap = test_all()
    #mydmap = test_all("2020020102.supermag.grdvec.01s.rev-0006 (1).dmap")
    #mydmap = test_all("2020020102.supermag.grdvec.01s.rev-0006.dmap")
    #mydmap = test_all("2020020102.supermag.grdvec.01s.rev-0006.dmap.2")
