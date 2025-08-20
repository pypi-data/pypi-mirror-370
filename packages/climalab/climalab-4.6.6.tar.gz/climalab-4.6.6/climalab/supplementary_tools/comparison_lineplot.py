#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
**Goal**

Create a lineplot of temperature observations and gcm simulations
of the Manila grid box
"""

import auxiliary_functions

ilon, ilat = 14, 19
# reading observations
obs_dates, obs_lat, obs_lon, obs_data = read_single_data(r"C:\Users\chris\Desktop\capacity_building\data\prepared\philippines\yr\observation\tas_yr_EWEMBI_19790101-20131231.nc", variable = "tas")
sim_dates, sim_lat, sim_lon, sim_data = read_single_data(r"C:\Users\chris\Desktop\capacity_building\data\prepared\philippines\yr\gcm\tas_yr_MPI-ESM-LR_historical_r1i1p1_19000101-20051231.nc", variable = "tas")

obs_years = [date.year for date in obs_dates]
sim_years = [date.year for date in sim_dates]

fig, ax = create_lineplot(xlabel = "year", ylabel = "Temperature in °C")
ax.plot(obs_years, obs_data[:,ilat,ilon] - 273.15, color = "black")
ax.plot(sim_years, sim_data[:,ilat,ilon] - 273.15, color = "red")
ax.grid(True)
ax.set_xlim((1979,2005))
fig.show()
# save_plot(fig, "comparison_lineplot.png")