#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# parametric quantile mapping of temperature (normal distribution)
from auxiliary_functions import *

obs, sim = read_example_data()

sim_parametric_qm = ba_parametric_qm(sim, sim, obs)
plot_histogram(obs, sim_parametric_qm, "tas_hist_parametric_qm.png")
plot_qq(obs, sim_parametric_qm, "tas_qq_parametric_qm.png")