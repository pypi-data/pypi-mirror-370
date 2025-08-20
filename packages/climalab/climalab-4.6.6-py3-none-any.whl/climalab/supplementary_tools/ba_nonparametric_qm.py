#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# non-parametric quantile mapping test

from auxiliary_functions import *
obs, sim = read_example_data()
sim_ba_nonparametric_qm = ba_nonparametric_qm(sim, sim, obs)

plot_histogram(obs, sim_ba_nonparametric_qm, "tas_hist_nonparametric_qm.png")
plot_qq(obs, sim_ba_nonparametric_qm, "tas_qq_nonparametric_qm.png")