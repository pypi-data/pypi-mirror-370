#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# bias adjustment of mean
from auxiliary_functions import *

obs, sim = read_example_data()
obs_mean = obs.mean()
sim_mean = sim.mean()
sim_ba_mean = ba_mean(sim, sim_mean, obs_mean)
print(obs_mean,sim_mean,sim_ba_mean.mean())
plot_histogram(obs, sim_ba_mean, "tas_hist_ba_mean.png")
plot_qq(obs, sim_ba_mean, "tas_qq_ba_mean.png")