#!/usr/bin/env python
# -*- coding: utf-8 -*-
# written by Christoph Federrath, 2023-2025

import numpy as np
import argparse
import cfpack as cfp
from cfpack.defaults import *


# === test for cfpack.fit ===
def test_fit(n=21):
    def func1(x, p):
        y = 0*x + p
        return y
    def func2(x, p0, p1):
        y = p0*x + p1
        return y
    # some x data
    xdat = cfp.get_1d_coords(cmin=-10., cmax=10., ndim=n, cell_centred=False)
    # constant func 1
    print("=== Fit (constant with y errors):", color="magenta")
    ydat = np.array([3.5]*n)
    yerr = np.array([1.0]*n)
    weights = 1/yerr
    fitres = cfp.fit(func1, xdat, ydat, weights=weights)
    fitres = cfp.fit(func1, xdat, ydat, weights=weights, scale_covar=False)
    fitres = cfp.fit(func1, xdat, ydat, yerr=yerr)
    # linear func 2
    print("=== Fit (linear func with y errors):", color="magenta")
    ydat = func2(xdat, 0.5, 1.5)
    yerr = ydat*0 + 0.5 + cfp.generate_random_gaussian_numbers(n=n, mu=0, sigma=0.05, seed=None)
    fitres_w = cfp.fit(func2, xdat, ydat, weights=1/yerr, scale_covar=False)
    fitres_e = cfp.fit(func2, xdat, ydat, yerr=yerr)
    cfp.plot(ydat, xdat, yerr=[yerr,yerr], linestyle=None, marker='o', label="data with y errors")
    cfp.plot(func2(xdat, *fitres_w.popt), xdat, label="fit with weights")
    cfp.plot(func2(xdat, *fitres_e.popt), xdat, label="fit with y errors")
    print("=== Fit (linear func with x errors):", color="magenta")
    ydat = func2(xdat, 0.5, 3.0)
    xerr = xdat*0 + 1.0 + cfp.generate_random_gaussian_numbers(n=n, mu=0, sigma=0.1, seed=None)
    cfp.plot(ydat, xdat, xerr=[xerr,xerr], linestyle=None, marker='o', label="data with x errors")
    fitres_e = cfp.fit(func2, xdat, ydat, xerr=xerr)
    cfp.plot(func2(xdat, *fitres_e.popt), xdat, label="fit with x errors")
    print("=== Fit (linear func with x and y errors):", color="magenta")
    ydat = func2(xdat, 0.5, 4.5)
    cfp.plot(ydat, xdat, xerr=[xerr,xerr], yerr=[yerr,yerr], linestyle=None, marker='o', label="data with x and y errors")
    fitres_e = cfp.fit(func2, xdat, ydat, xerr=xerr, yerr=yerr)
    cfp.plot(func2(xdat, *fitres_e.popt), xdat, label="fit with x and y errors")
    cfp.plot(show=True)
    stop()


# === test for cfpack.plot_map ===
def test_plot_map(N=500):
    x, y = np.meshgrid(np.linspace(-1,1,N), np.linspace(-1,1,N))
    map = np.sqrt(x**2 + y**2)
    cfp.plot_map(map, xlim=[0,1], ylim=[0,1], save='test_map_imshow.pdf')
    edges = cfp.get_1d_coords(cmin=0, cmax=1, ndim=N+1, cell_centred=False)
    cfp.plot_map(map, xedges=edges, yedges=edges, aspect_data='equal', save='test_map_pcolormesh.pdf')
    stop()


# === test for cfpack.plot_map ===
def plot_multi_panel():
    o1 = cfp.plot(x=[1,2,3], y=[1,2,3], label="1st")
    o1 = cfp.plot(x=[1,2,3], y=[3,2,1], label="2nd", xlabel="", ylabel="y top", save="tmp1.pdf")
    cfp.plot_multi_panel(o1.ax(), save="tmp1_mp.pdf")

    o2 = cfp.plot(x=[1,2,3], y=[2,2,2], label="3rd", xlabel="", ylabel="", save="tmp2.pdf")

    figure_axes = [o1.ax(), o2.ax()]
    cfp.plot_multi_panel(figure_axes, show=False, save="tmp_mp.pdf")

    exit()

    o3 = cfp.plot(x=[1,2,3], y=[300,200,100], label="4th", xlabel="x bottom left", ylabel="y bottom", save="tmp3.pdf")

    o4 = cfp.plot(x=[1,2,3], y=[3,2,1], label="5th", xlabel="x bottom right", ylabel="", save="tmp4.pdf", show=False)
    o4 = cfp.plot(x=[1,2,3], y=[3,2,1], label="5th", xlabel="x bottom right", ylabel="", save="tmp4.png")
    cfp.plot_multi_panel(o4.ax(), save="tmp4_mp.pdf")
    cfp.plot_multi_panel(o4.ax(), save="tmp4_mp.png")

    figure_axes = [o1.ax(), o2.ax(), o3.ax(), o4.ax()]
    cfp.plot_multi_panel(figure_axes, show=False, save="tmp_mp.pdf")
    stop()

# === test for cfpack.get_spectrum ===
def test_get_spectrum():
    # Tukey window function
    def apply_tukey_window_nd(arr, alpha=0.1):
        from scipy.signal.windows import tukey
        window = np.ones_like(arr, dtype=float)
        for axis, size in enumerate(arr.shape):
            w = tukey(size, alpha)
            shape = [1] * arr.ndim
            shape[axis] = size
            window *= w.reshape(shape)
        return arr * window
    # create 1D test data
    dat = np.sin(np.linspace(0,1,100)*np.pi) + 1
    cfp.plot(dat, save="test_spect_dat.pdf")
    # get spectrum of test data
    po = cfp. get_spectrum(dat)
    cfp.plot(x=po['k'], y=po['P_tot'], save='test_spect_dat_PS.pdf')
    # apply Tukey window
    dat_win = apply_tukey_window_nd(dat, alpha=0.5)
    cfp.plot(dat_win, save="test_spect_dat_windowed.pdf")
    # get power spectrum of windowed data
    po = cfp. get_spectrum(dat_win)
    cfp.plot(x=po['k'], y=po['P_tot'], save='test_spect_dat_windowed_PS.pdf')
    # get power spectrum by using windowing
    po = cfp. get_spectrum(dat, window=True)
    cfp.plot(x=po['k'], y=po['P_tot'], save='test_spect_dat_PS_computed_with_kw_window.pdf')


# ===== the following applies in case we are running this in script mode =====
if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Test suite for cfpack.')
    subparsers = parser.add_subparsers(title='subcommands', dest='subcommand', description='valid subcommands',
                                        help='additional help', required=True)
    # sub parser for 'fit' sub-command
    parser_fit = subparsers.add_parser('fit')
    # sub parser for 'plot_map' sub-command
    parser_plot_map = subparsers.add_parser('plot_map')
    parser_plot_map.add_argument("-N", type=int, help="number of cells N to create an N x N test map (default: %(default)s)", default=256)
    # sub parser for 'plot_multi_panel' sub-command
    parser_plot_multi_panel = subparsers.add_parser('plot_multi_panel')
    # sub parser for 'get_spectrum' sub-command
    parser_fit = subparsers.add_parser('get_spectrum')

    args = parser.parse_args()

    if args.subcommand == 'fit':
        test_fit()

    if args.subcommand == 'plot_map':
        test_plot_map(N=args.N)

    if args.subcommand == 'plot_multi_panel':
        plot_multi_panel()

    if args.subcommand == 'get_spectrum':
        test_get_spectrum()
