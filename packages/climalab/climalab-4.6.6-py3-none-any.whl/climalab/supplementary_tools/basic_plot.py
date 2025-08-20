#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from matplotlib import pyplot
import numpy as np

fig = pyplot.figure( figsize = (4,4) )
ax  = fig.add_subplot(1,1,1)
ax.plot(np.arange(100), np.random.random(100))
ax.grid(True)
ax.set_xlabel("year")
ax.set_ylabel("random number")
ax.set_xlim((0,99))
ax.set_ylim((0.0, 1.0))
ax.set_title("Title of the plot")
fig.savefig("basic_plot.png")
pyplot.close(fig)