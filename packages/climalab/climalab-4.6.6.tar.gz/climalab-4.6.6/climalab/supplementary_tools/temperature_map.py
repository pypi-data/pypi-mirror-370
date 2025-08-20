#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Map of temperature of observation"""

import auxiliary_functions

obs_dates, obs_lat, obs_lon, obs_data = read_single_data(r"C:\Users\chris\Desktop\capacity_building\data\prepared\philippines\yr\observation\tas_yr_EWEMBI_19790101-20131231.nc", variable = "tas")

plot_data = obs_data.mean(axis = 0)

fig, ax = create_mapplot()
cm = ax.contourf(obs_lon, obs_lat, plot_data)
fig.colorbar(cm, ax = ax, label = "Temperature in K")
save_plot(fig, "temperature_map.png")