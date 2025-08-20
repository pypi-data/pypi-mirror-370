#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# bias adjustment of mean and variance test
from auxiliary_functions import *

obs, sim = read_example_data()
obs_mean = obs.mean()
sim_mean = sim.mean()
obs_std  = obs.std()
sim_std  = sim.std()

sim_ba_mean_and_var = ba_mean_and_var(sim, sim_mean, obs_mean, sim_std, obs_std)
print(obs_mean, sim_mean, sim_ba_mean_and_var.mean())
print(obs_std, sim_std, sim_ba_mean_and_var.std())
plot_histogram(obs, sim_ba_mean_and_var, "tas_hist_ba_mean_and_var.png")
plot_qq(obs, sim_ba_mean_and_var, "tas_qq_ba_mean_and_var.png")