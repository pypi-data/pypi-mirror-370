#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# first basic map plot

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

fig.show()