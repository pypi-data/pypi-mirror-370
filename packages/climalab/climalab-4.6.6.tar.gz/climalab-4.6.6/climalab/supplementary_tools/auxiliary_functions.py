#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jan 30 19:53:04 2022

@author: jon ander

Downloaded from http://www.pik-potsdam.de/~menz/IKI-Oasis/capacity_building/scripts/.
This program is intended to use AS A GUIDE, NOT AS A MODULE.
All scripts belong to Potsdam Institude for Climate Impact Research.
"""

# auxiliary functions for the course

def read_single_data(fname, variable = "tas"):
    # reads a single netcdf file and returns:
    #    dates, lat, lon, data
    from netCDF4 import Dataset
    from cftime import num2date
    
    nc = Dataset(fname)
    time = nc.variables["time"][:]
    lat  = nc.variables["lat"][:]
    lon  = nc.variables["lon"][:]
    data = nc.variables[variable][:]
    units = nc.variables["time"].units
    calendar = nc.variables["time"].calendar
    dates = num2date(time, units, calendar)
    nc.close()
    
    return (dates, lat, lon, data)
    
def create_lineplot(xlabel = "year", ylabel = "Temperature"):
    from matplotlib import pyplot 
    fig = pyplot.figure( figsize = (8,8) )
    ax  = fig.add_subplot(1,1,1)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    return (fig, ax)

def save_plot(fig, fname_out):
    from matplotlib import pyplot
    fig.savefig(fname_out, dpi = 300)
    pyplot.close(fig)
    
def create_mapplot():
    from matplotlib import pyplot
    import cartopy.crs as ccrs
    import cartopy.feature as cfeature

    fig = pyplot.figure( figsize = (4,4) )
    proj = ccrs.PlateCarree()
    ax = fig.add_subplot(1,1,1, projection = proj)

    coastline = cfeature.COASTLINE.with_scale("50m")
    borders   = cfeature.BORDERS.with_scale("50m")

    ax.add_feature(coastline)
    ax.add_feature(borders)

    ax.set_extent([116,127,6,19])
    
    return (fig, ax)

def get_yindex(years, year_start = 1979, year_stop = 2000):
    return [year >= year_start and year <= year_stop for year in years]

def read_example_data():
    ilon, ilat = 12, 20
    obs_dates, obs_lat, obs_lon, obs_data = read_single_data(r"C:\Users\chris\Desktop\capacity_building\data\prepared\philippines\day\observation\tas_day_EWEMBI_19790101-20131231.nc")
    sim_dates, sim_lat, sim_lon, sim_data = read_single_data(r"C:\Users\chris\Desktop\capacity_building\data\prepared\philippines\day\gcm\tas_day_MPI-ESM-LR_historical_r1i1p1_19000101-20051231.nc")
    
    obs_years = [date.year for date in obs_dates]
    sim_years = [date.year for date in sim_dates]
    obs_yindex = get_yindex(obs_years)
    sim_yindex = get_yindex(sim_years)
    
    obs_data_select = obs_data[obs_yindex,ilat,ilon] - 273.15
    sim_data_select = sim_data[sim_yindex,ilat,ilon] - 273.15
    
    return (obs_data_select, sim_data_select)

def plot_histogram(obs, sim, fname_out):
    import numpy as np
    bin_width = 0.5
    bins = np.arange(19,32,bin_width)
    fig, ax = create_lineplot(xlabel = "Temperature in °C", ylabel = "Frequency")
    ax.hist(obs, bins = bins, density = True, color = "black", alpha = 0.5)
    ax.hist(sim, bins = bins, density = True, color = "red",   alpha = 0.5)
    
    ax.axvline(obs.mean(), color = "black", lw = 2)
    ax.axvline(sim.mean(), color = "red",   lw = 2)
    save_plot(fig, fname_out)
    
def plot_qq(obs, sim, fname_out):
    import numpy as np
    fig, ax = create_lineplot(xlabel = "Simulated Temperature in °C",
                              ylabel = "Observed Temperature in °C")
    quantiles = np.arange(0,101,1)
    obs_percentiles = np.percentile(obs, q = quantiles)
    sim_percentiles = np.percentile(sim, q = quantiles)
    
    ax.scatter(sim_percentiles, obs_percentiles, color = "purple", zorder = 2)
    ax.plot((0,50),(0,50), color = "black", zorder = 1)
    
    ax.set_xlim((19,32))
    ax.set_ylim((19,32))
    save_plot(fig, fname_out)
    
def ba_mean(sim, sim_mean, obs_mean):
    return sim - sim_mean + obs_mean

def ba_mean_and_var(sim, sim_mean, obs_mean, sim_std, obs_std):
    return (sim - sim_mean) * (obs_std/sim_std) + obs_mean

def ba_nonparametric_qm(sim, sim_ref, obs_ref, order = 1):
    import numpy as np
    from scipy.interpolate import InterpolatedUnivariateSpline
    
    bins = np.linspace(0,100,1000)
    
    bin_obs_ref = np.percentile(obs_ref, q = bins)
    bin_sim_ref = np.percentile(sim_ref, q = bins)
    
    g = InterpolatedUnivariateSpline(bin_sim_ref, bin_obs_ref, k = order)
    
    return g(sim)

def ba_parametric_qm(sim, sim_ref, obs_ref):
    from scipy import stats
    dist_obs_ref_mean, dist_obs_ref_std = stats.norm.fit(obs_ref)
    dist_sim_ref_mean, dist_sim_ref_std = stats.norm.fit(sim_ref)
    
    F_sim = stats.norm.cdf(sim, dist_sim_ref_mean, dist_sim_ref_std)
    
    return stats.norm.ppf(F_sim, dist_obs_ref_mean, dist_obs_ref_std)

