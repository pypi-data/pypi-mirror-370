#!/usr/bin/env python
# -*- coding: utf-8 -*-
# written by Christoph Federrath, 2019-2025

import numpy as np
np.set_printoptions(linewidth=200) # increase the numpy printing linewidth a bit

from . import constants as const # physical constants

# so we can call stop() to drop a script into interactive mode
try:
    from ipdb import set_trace as stop # interactive python debugger
except:
    from pdb import set_trace as stop # python debugger

# === setup default cfpack plot styles ===
def import_matplotlibrc(fontscale=None):
    from . import matplotlibrc # set default plotting style
    if fontscale is not None:
        from matplotlib import rcParams
        rcParams['font.size'] *= fontscale
        rcParams['legend.fontsize'] *= fontscale

# === START get_frame ===
# returns an object with the file and function name from which it is called
def get_frame():
    from inspect import currentframe, getouterframes
    from os import path
    class ret:
        def __init__(self, file_, func_):
            self.file = file_
            self.func = func_
            self.signature = file_+": "+func_+": "
    frame = currentframe()
    outer_frames = getouterframes(frame)
    if len(outer_frames) < 2: return ret("-?-", "-?-")
    # caller frame
    caller = outer_frames[1]
    file = path.basename(caller.filename)
    func = caller.function
    return ret(file, func)
# === END get_frame ===

# === START print ===
# custom print() function override to show caller (module and function) information before actual print string,
# plus options colourised output
def print(*args, error=False, warn=False, highlight=False, color="",
          input=False, no_prefix=False, newline=True, mpi=None, **kwargs):
    from builtins import print as builtin_print, input as builtin_input
    from inspect import currentframe, getouterframes
    from colorama import Fore, Style
    curframe = currentframe()
    calframe = getouterframes(curframe, 2)
    filename = calframe[1][1] # get file name
    ind = filename.rfind('/')+1 # remove leading path from filename
    filename = filename[ind:]
    funcname = calframe[1][3] # get function name
    prefix = filename+": "+funcname+": "
    ind = prefix.find("<module>: ") # remove '<module>: ' from prefix
    if ind < 0: ind = len(prefix)
    prefix = prefix[:ind]
    # handle MPI printing cases
    from sys import modules
    if 'mpi4py.MPI' in modules:
        from mpi import myPE
    else:
        myPE = 0
    if mpi is None:
        if myPE != 0: return # default is that only the master rank prints
    else:
        if isinstance(mpi, int) and not isinstance(mpi, bool):
            if mpi != myPE: return # if this is not the requested MPI rank for printing
        prefix += "["+str(myPE)+"] " # prepend MPI rank
    if not no_prefix: builtin_print(prefix, end="")
    message = "" # default message (can also be 'ERROR: ' or 'WARNING: ')
    color_str = getattr(Fore, color.upper(), Fore.RESET)
    if highlight:
        color_str = f"{Fore.GREEN}"
        if type(highlight)==int:
            if highlight==1: color_str = f"{Fore.GREEN}"
            if highlight==2: color_str = f"{Fore.CYAN}"
            if highlight==3: color_str = f"{Fore.MAGENTA}"
    if warn:
        message = "WARNING: "
        color_str = f"{Fore.YELLOW}"
    if error:
        message = "ERROR: "
        color_str = f"{Fore.RED}"
    post_str = ""
    if input: # in case we want to stop here and let the user press key to proceed
        post_str = " Press Enter to proceed..."
    # print
    builtin_print(color_str+message, end="") # print in colour and message, if requested
    builtin_print(*args, **kwargs, end="") # print the actual stuff
    builtin_print(post_str, end="") # print a post string, if requested
    if color_str != "": builtin_print(f"{Style.RESET_ALL}", end="") # reset, in case we used ANSI for colouring text
    if newline: end = None
    else: end = ""
    builtin_print("", end=end, flush=True) # print final line ending, and flush output
    if input: builtin_input() # this will ask for user press key...
    # error handling (exit or stop the code)
    if error:
        if type(error)==str:
            if error == "stop":
                builtin_print(f"{Fore.RED}Type 'n' to return to function call and inspect.{Style.RESET_ALL} ", flush=True)
                return stop()
        exit() # exit on error
    return # return if everything is normal
# === END print ===

# === START legend_formatter ===
# Can be passed to plot() to place and customize individual legend items.
# For each plot item (line, symbol, etc) that requires a custom legend,
# initialise new lf = cfp.legend_formatter(pos=(x,y), ...) and pass into cfp.plot(legend_formatter=lf)
class legend_formatter:
    def __init__(self, pos=(0.5, 0.5), loc='center left', textpad=0.1, length=1.25, fontsize=None):
        self.pos = pos # custom placement (normalised coordinates)
        self.loc = loc # relative position
        self.textpad = textpad # pad between symbol/line and text label
        self.length = length # length of the symbol/line section
        self.fontsize = fontsize
# === END legend_formatter ===

# === START plot ===
def plot(y=None, x=None, yerr=None, xerr=None, type=None, xlabel='x', ylabel='y', label=None,
         linestyle=None, linewidth=None, marker=None, text=None, shaded_err=None,
         aspect_data=None, aspect_box=None, normalised_coords=False, bar_width=1.0,
         xlog=False, ylog=False, xlim=None, ylim=None, legend_loc='upper left', legend_formatter=None,
         axes_format=[None,None], axes_pos=None, ax=None, show=False, pause=None, save=None, *args, **kwargs):
    import builtins
    import matplotlib.pyplot as plt
    import matplotlib.ticker as ticker
    from matplotlib.legend import Legend
    if ax is None:
        ax_provided = False
        ax = plt.gca() # get current axis
    else:
        ax_provided = True
        plt.sca(ax) # set current axis to ax, so we can easily keep plotting onto the same ax in subsequent calls
    if isinstance(x, list): x = np.array(x)
    if isinstance(y, list): y = np.array(y)
    if normalised_coords: # set transform to accept normalised coordinates (can be helpful for text placement)
        if "transform" not in kwargs: # check if user had already set 'transform' in **kwargs
            kwargs["transform"] = ax.transAxes # if not, set it here
    if linestyle == 'long dashed': linestyle = (0,(5,5))
    if y is not None:
        if x is None: x = np.arange(len(y)) # in this case, we just use the array indices as the x axis values
        # create a stand-alone text label (useful to combine with normalised_coords=True)
        if text is not None:
            ax.text(x, y, text, *args, **kwargs)
        else:
            if type == 'pdf' or type == 'histogram' or type == 'hist' or type == 'bars':
                if len(x) == 1 or len(x) != len(y)+1: # catch input error
                    print("x must contain bin edges for type='"+type+"'", error=True)
                if linestyle is None: linestyle="" # turn line off unless user specifies
                edges = x # bin edges
                x = (x[1:]+x[:-1]) / 2.0 # bin mid points
                if type == 'bars':
                    width = (edges[1:]-edges[:-1]) * bar_width # bar widths
                    ax.bar(x, height=y, width=width, label=label, *args, **kwargs)
                else:
                    ax.stairs(y, edges=edges, label=label, *args, **kwargs)
            if type == 'scatter':
                linestyle = "None"
                if marker is None: marker = 'o'
            xerr_bars = None; yerr_bars = None
            if shaded_err is None: # only plot error bars, if shaded error region is not requested
                if xerr is not None: xerr_bars = np.abs(xerr)
                if yerr is not None: yerr_bars = np.abs(yerr)
            if type == 'scatter':
                ax.scatter(x, y, marker=marker, linestyle=linestyle, linewidth=linewidth, label=label, *args, **kwargs)
            else:
                ax.errorbar(x, y, xerr=xerr_bars, yerr=yerr_bars, marker=marker, linestyle=linestyle, linewidth=linewidth, label=label, *args, **kwargs)
            if shaded_err is not None: # yerr must have shape (2,N), containing the lower and upper errors for each of the N data points
                if isinstance(shaded_err, list): # user provided a list with [color, alpha]
                    color_err = shaded_err[0]
                    alpha_err = shaded_err[1]
                else:
                    color_err = plt.gca().lines[-1].get_color()
                    alpha_err = 0.5
                ax.fill_between(x, y-np.abs(yerr[0]), y+np.abs(yerr[1]), color=color_err, alpha=alpha_err, linewidth=0.0, label=label)
        # create a stand-alone legend item for more control
        if legend_formatter is not None:
            handles, labels = ax.get_legend_handles_labels()
            last_handle, last_label = handles[-1], labels[-1]
            if builtins.type(legend_formatter) != builtins.type(legend_formatter):
                print('legend_formatter must be of type cfpack.legend_formatter', error=True)
            # add the new legend
            leg = ax.legend(
                handles=[last_handle], # select only the last plotted item
                labels=[last_label], # label
                bbox_to_anchor=legend_formatter.pos, # custom placement (normalised coordinates)
                loc=legend_formatter.loc, # relative position
                handletextpad=legend_formatter.textpad,
                handlelength=legend_formatter.length,
                fontsize=legend_formatter.fontsize,
            )
            ax.add_artist(leg)
    if show or save or ax_provided:
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        if xlim is not None: plt.xlim(xlim)
        if ylim is not None: plt.ylim(ylim)
        if xlog: ax.set_xscale('log')
        if ylog: ax.set_yscale('log')
        if axes_format[0] is not None: ax.xaxis.set_major_formatter(ticker.StrMethodFormatter(axes_format[0]))
        if axes_format[1] is not None: ax.yaxis.set_major_formatter(ticker.StrMethodFormatter(axes_format[1]))
        if aspect_data is not None: ax.set_aspect(aspect_data)
        if aspect_box is not None: ax.set_box_aspect(aspect_box)
        if axes_pos is not None: ax.set_position(axes_pos)
        # auto creation of legend handles and labels (first check if user has not already created legends manually)
        user_legend_present = False
        for artist in ax.get_children(): # find any existing legends
            if isinstance(artist, Legend):
                user_legend_present = True
        if not user_legend_present:
            legend_handles, legend_labels = ax.get_legend_handles_labels()
            if legend_handles or legend_labels:
                legend_labels = np.array(legend_labels)
                unique_labels = np.unique(legend_labels)
                new_handles = [[] for _ in range(len(unique_labels))]
                for iul, ul in enumerate(unique_labels):
                    for ill, ll in enumerate(legend_labels):
                        if ll == ul: new_handles[iul].append(legend_handles[ill])
                    new_handles[iul] = tuple(new_handles[iul])
                new_labels = unique_labels.tolist()
                ax.legend(new_handles, new_labels, loc=legend_loc, *args, **kwargs)
    ret = show_or_save_plot(ax, show=show, pause=pause, save=save) # now show or save the finished figure, and destroy it afterwards
    return ret
# === END plot ===

# === START plot_map ===
# function to plot a map (of a 2D numpy array)
def plot_map(image=None, xedges=None, yedges=None, dims=None, vmin=None, vmax=None, log=False,
             symlog=False, symlog_linthresh=1, symlog_linscale=0.01,
             norm=None, colorbar=True, cmap='magma', cmap_label=None, xlabel=None, ylabel=None, xlog=False, ylog=False,
             xlim=None, ylim=None, axes_format=[None,None], axes_pos=None, aspect_data='auto', aspect_box=None, dpi=200,
             ax=None, show=False, pause=None, save=None, *args, **kwargs):
    import matplotlib.pyplot as plt
    import matplotlib.colors as colors
    import matplotlib.ticker as ticker
    from mpl_toolkits.axes_grid1 import make_axes_locatable
    if ax is None: ax = plt.gca()
    cax = None
    if image is not None:
        if dims is not None: image = congrid(image, (dims[0], dims[1])) # re-sample image
        # define how to normalise colours
        if norm is None:
            norm = colors.Normalize(vmin=vmin, vmax=vmax)
            if log: norm = colors.LogNorm(vmin=vmin, vmax=vmax)
            if symlog: norm = colors.SymLogNorm(vmin=vmin, vmax=vmax, linthresh=symlog_linthresh, linscale=symlog_linscale)
        # define the coordinates of the map
        shape = np.array(image.shape)
        xrange = [0.5, shape[0]+0.5]
        yrange = [0.5, shape[1]+0.5]
        if xlim is not None:
            xrange = [xlim[0], xlim[1]]
        else:
            if xedges is not None:
                xrange = [xedges.min(), xedges.max()]
        if ylim is not None:
            yrange = [ylim[0], ylim[1]]
        else:
            if yedges is not None:
                yrange = [yedges.min(), yedges.max()]
        plt.xlim(xrange)
        plt.ylim(yrange)
        if xlog:
            ax.set_xscale('log')
            if min(xrange) <= 0: # handle symlog case
                linthresh = 1
                if xedges is not None:
                    # get the positive value of the number closest to zero
                    linthresh = min([-xedges[xedges<0].max(), xedges[xedges>0].min()])
                ax.set_xscale('symlog', linthresh=linthresh, linscale=symlog_linscale)
        if ylog:
            ax.set_yscale('log')
            if min(yrange) <= 0: # handle symlog case
                linthresh = 1
                if yedges is not None:
                    # get the positive value of the number closest to zero
                    linthresh = min([-yedges[yedges<0].max(), yedges[yedges>0].min()])
                ax.set_yscale('symlog', linthresh=linthresh, linscale=symlog_linscale)
        if axes_format[0] is not None: ax.xaxis.set_major_formatter(ticker.StrMethodFormatter(axes_format[0]))
        if axes_format[1] is not None: ax.yaxis.set_major_formatter(ticker.StrMethodFormatter(axes_format[1]))
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        have_regular_grid_to_plot = False
        if xedges is not None and yedges is not None:
            x_edges, y_edges = np.meshgrid(xedges, yedges, indexing='ij')
        else:
            x_edges, y_edges = get_2d_coords([xrange[0], yrange[0]], [xrange[1], yrange[1]], shape+1, cell_centred=False)
            if aspect_data == "auto" and xlim is None and ylim is None:
                ax.set_aspect((yrange[1]-yrange[0])/(xrange[1]-xrange[0]))
            if not xlog and not ylog:
                have_regular_grid_to_plot = True
        # plot map
        if not have_regular_grid_to_plot:
            map_obj = ax.pcolormesh(x_edges, y_edges, image, cmap=cmap, norm=norm, *args, **kwargs)
        else: # use the faster, but much less flexible imshow (doesn't work with xlog or ylog or when xedges or yedges are user defined)
            map_obj = ax.imshow(image.T, extent=[x_edges.min(), x_edges.max(), y_edges.min(), y_edges.max()], cmap=cmap, norm=norm,
                                origin='lower', interpolation='none', *args, **kwargs)
        # add colorbar
        if colorbar:
            divider = make_axes_locatable(ax)
            cax = divider.append_axes("right", size="5%", pad=0.05)
            cb = plt.colorbar(map_obj, cax=cax, label=cmap_label, pad=0.01, aspect=25)
            if not log: cb.ax.minorticks_on()
            cb.ax.yaxis.set_offset_position('left')
        if aspect_data != "auto": ax.set_aspect(aspect_data)
        if aspect_box is not None: ax.set_box_aspect(aspect_box)
        if axes_pos is not None: ax.set_position(axes_pos)
        plt.gcf().set_dpi(dpi)
        plt.tight_layout(pad=0.0)
    ret = show_or_save_plot([ax, cax], show=show, pause=pause, save=save) # now show or save the finished figure, and destroy it afterwards
    return ret
# === END plot_map ===

# === function that plots a standalone colorbar (can be useful for making a colorbar sharded by multiple panels in a publication figure) ===
# 'extend' can be "neither", "both", "min", "max"
# 'panels' scales the colorbar to spread across multiple panels
# 'orientation' can be "vertical", "horizontal"
def plot_colorbar(cmap=None, label=None, vmin=None, vmax=None, log=False, symlog=False, symlog_linthresh=1, norm=None, format=None,
                  aspect=28, extend="neither", panels=1, orientation="vertical", swap=False, ax=None, show=False, pause=None, save=None):
    import matplotlib.pyplot as plt
    import matplotlib.colorbar as cbar
    import matplotlib.ticker as ticker
    import matplotlib.colors as colors
    aspect_default = 28 # default aspect ratio
    if vmin is None: vmin = 0.0 # set vmin
    if vmax is None: vmax = 1.0 # set vmax
    # define how to normalise colors if not provided already
    if norm is None:
        norm = colors.Normalize(vmin=vmin, vmax=vmax) # linear color scale
        if log: # log color scale
            if vmin <= 0: vmin = 1e-99 # override negative or zero lower bound
            norm = colors.LogNorm(vmin=vmin, vmax=vmax)
        if symlog: # symlog color scale
            norm = colors.SymLogNorm(vmin=vmin, vmax=vmax, linthresh=symlog_linthresh)
    # define figure canvas
    figsize_for_cb = plt.gcf().get_size_inches()
    if orientation == "vertical":   figsize_for_cb[1] *= panels # extend figure size for multiple plot panels
    if orientation == "horizontal": figsize_for_cb[0] *= panels # extend figure size for multiple plot panels
    plt.gcf().set_size_inches(figsize_for_cb) # set canvas size
    width = 0.025*aspect_default/aspect
    height = 0.9
    xpos = 0.50
    ypos = 0.05
    if orientation == "horizontal": # flip width and height for horizontal colorbar
        width_saved = width
        width = height
        height = width_saved
        xpos = 0.05
        ypos = 0.50
    if ax is None: ax = plt.gcf().add_axes([xpos, ypos, width, height]) # colorbar axis
    cb = cbar.ColorbarBase(ax, cmap=cmap, norm=norm, orientation=orientation, extend=extend, label=label) # draw colorbar
    # adjust tick axis settings
    if not log: cb.ax.minorticks_on()
    if orientation == "vertical":
        cb_axis = cb.ax.yaxis
        label_and_tick_position = "right"
        if swap: label_and_tick_position = "left"
    if orientation == "horizontal":
        cb_axis = cb.ax.xaxis
        label_and_tick_position = "top"
        if swap: label_and_tick_position = "bottom"
    cb_axis.set_label_position(label_and_tick_position)
    cb_axis.set_ticks_position(label_and_tick_position)
    #cb_axis.set_offset_position(label_and_tick_position)
    if format is not None: cb_axis.set_major_formatter(ticker.StrMethodFormatter(format))
    ret = show_or_save_plot(ax, show=show, pause=pause, save=save) # now show or save the finished figure, and destroy it afterwards
    return ret
#=== END plot_colorbar ===

#=== START plot_multi_panel ===
# combines several plots created with cfpack.plot() into a multi-panel figure
def plot_multi_panel(figure_axes, nrows=None, ncols=None, width_panel=0.8, height_panel=0.8, col_sep=0.15, row_sep=0.15,
                     remove_old_fig=True, verbose=False, show=False, pause=None, save=None):
    import matplotlib.pyplot as plt
    # check for list
    if not isinstance(figure_axes, list): figure_axes = [figure_axes]
    print("Number of panels: "+str(len(figure_axes)))
    if nrows is None and ncols is None:
        nrows = int(np.floor(np.sqrt(len(figure_axes))))
        ncols = int(np.ceil(len(figure_axes)/nrows))
        print("Automatically set nrows, ncols = "+str(nrows)+", "+str(ncols))
    # create output figure
    panel_figsize = figure_axes[0].figure.get_size_inches()
    figsize = (panel_figsize[0]*ncols, panel_figsize[1]*nrows)
    fig = plt.figure(figsize=figsize)
    # loop over each sub-figure (axes), i.e., each panel
    for iax, ax in enumerate(figure_axes):
        old_fig = ax.figure # get a reference to the old figure so we can close it below
        ax.remove() # remove the axis from its original figure
        ax.figure = fig # set the pointer from the sub-panel axis to the new figure
        fig.add_axes(ax) # add the sub-panel axis
        # get sub-panel column and row index
        irow = iax // ncols
        icol = iax % ncols
        # set sub-panel position based on panel col and row index, separators, width and height
        x0 = icol + col_sep
        y0 = (nrows-1-irow)+row_sep
        position = [x0, y0, width_panel, height_panel]
        if verbose: print(icol, irow, position)
        ax.set_position(position)
        # close the old axis and figure
        if remove_old_fig: plt.close(old_fig)
    ret = show_or_save_plot(plt.gca(), show=show, pause=pause, save=save) # now show or save the finished figure, and destroy it afterwards
    return ret
#=== END plot_multi_panel ===

# === START show_or_save_plot ===
# internal plot helper function
def show_or_save_plot(figax=None, show=None, pause=None, save=None):
    import matplotlib.pyplot as plt
    import tempfile, dill
    if show or save:
        if figax is not None:
            # pickle figure axis to temporary file (so we can restore it, e.g., for plot_multi_panel(...))
            tmpfile = tempfile.NamedTemporaryFile(delete=False)
            with open(tmpfile.name, 'wb') as fid: dill.dump(figax, fid)
        else:
            figax = plt.gca()
        if save: # save to file
            plt.savefig(save, bbox_inches='tight')
            print(save+' written.', color='magenta')
        if show: # show in window
            block = None
            if pause: block = False
            plt.show(block=block)
            if pause:
                plt.draw()
                plt.pause(pause)
        plt.clf(); plt.cla(); plt.close() # clear figure after use
    class ret: # class object to be returned (contains ax()-function to get the axis of the plot)
        def ax():
            ret_ax = figax # set to normal axis object by default (in case the user has not issued a show or save)
            try: # restore the axis of this plot from the temporary file if show or save was used
                with open(tmpfile.name, 'rb') as fid: ret_ax = dill.load(fid)
            except Exception:
                pass
            return ret_ax
        def fig():
            ret_fig = plt.gcf() # returns fig object
            return ret_fig
        def plt():
            ret_plt = plt # returns plt object
            return ret_plt
    return ret
# === END show_or_save_plot ===

# === START rgba2data ===
# Given a RGBA colour image (2D array) plotted with a colourbar 'cmap', and vmin/vmax values on the colourbar.
# Return the interpolated data values in the RGBA colour image.
# Adopted from http://stackoverflow.com/questions/3720840/how-to-reverse-color-map-image-to-scalar-values/3722674#3722674
def rgba2data(rgba_image, cmap_name, cmap_vmin, cmap_vmax):
    import matplotlib.pyplot as plt
    import scipy.cluster.vq as scv
    # get cmap
    cmap = plt.get_cmap(cmap_name)
    gradient = cmap(np.linspace(0.0, 1.0, 100))
    # Reshape rgba_image with all the 4-tuples in a long list.
    rgba_image_2 = rgba_image.reshape((rgba_image.shape[0]*rgba_image.shape[1], rgba_image.shape[2]))
    # Use vector quantization to shift the values in rgba_image_2 to the nearest point in the code book (gradient).
    code, _ = scv.vq(rgba_image_2, gradient)
    # 'code' is an array of length rgba_image_2, holding the code book index for each observation (rgba_image_2 are the "observations").
    # Scale values so they are from 0 to 1.
    values = code.astype('float') / gradient.shape[0]
    # Reshape values back to original size of rgba_image
    values = values.reshape(rgba_image.shape[0], rgba_image.shape[1])
    values = values[::-1]
    # Finally, scale output values to cmap range.
    values = cmap_vmin + values * (cmap_vmax - cmap_vmin)
    return values
# === END rgba2data ===

# === START fit ===
# Supported fit_method 'ls': least squares via lmfit, 'mcmc' via emcee
# - params can be a dict with the parameter name(s) and a list specifying [min, start, max]
# - Method for parameter error estimate (based on random sampling with n_random_draws=1000):
#     perr_method='statistical': statistical error estimate based on sampling from data errors provided (xerr and/or yerr)
#     perr_method='systematic' : systematic error estimate based on sampling dat_frac_for_systematic_perr=0.3 of the original data
def fit(func, xdat, ydat, xerr=None, yerr=None, perr_method='statistical', n_random_draws=1000, dat_frac_for_systematic_perr=0.3,
        weights=None, scale_covar=True, params=None, fit_method='ls', plot_fit=False, mcmc_walkers=32, mcmc_steps=2000,
        verbose=1, *args, **kwargs):
    if fit_method not in ['ls', 'mcmc']: print("fit_method = '"+fit_method+"' not supported.", error=True)
    from lmfit import Model
    model = Model(func) # get lmfit model object
    # set up parameters
    lmfit_params = model.make_params() # make lmfit default params
    n_free_params = len(lmfit_params)
    if params is not None: # user provided parameter bounds and initial values
        for pname in params:
            if pname not in model.param_names: print("parameter key error: '"+pname+"'", error=True)
            plist = params[pname]
            if None in plist: # if a parameter is not allowed to vary (it's not free, instead it's fixed)
                model.set_param_hint(pname, value=plist[1], vary=False)
                n_free_params -= 1 # reduce the number of free parameters
            else: model.set_param_hint(pname, min=plist[0], value=plist[1], max=plist[2]) # set bounds for this parameter from [min, val, max]
    else: # try and find some reasonable initial guesses for the fit parameters
        if verbose: print("trying to find initial parameter guesses...", color="yellow")
        # genetic algorithm to come up with initial fit parameter values
        def generate_initial_params(n_params):
            from scipy.optimize import differential_evolution
            # function for genetic algorithm to minimize (sum of squared error)
            def sum_of_squared_error(parameterTuple):
                from warnings import filterwarnings
                filterwarnings("ignore") # do not print warnings by genetic algorithm
                val = func(xdat, *parameterTuple)
                return np.sum((ydat - val)**2)
            # min and max used for bounds
            maxXY = np.max([np.max(xdat), np.max(ydat)])
            parameterBounds = [[-maxXY, maxXY]]*n_params
            result = differential_evolution(sum_of_squared_error, parameterBounds, seed=140281)
            return result.x
        # get initial parameter value guesses and put them in
        initial_params = generate_initial_params(len(model.param_names))
        for ip, pname in enumerate(model.param_names):
            model.set_param_hint(pname, value=initial_params[ip])
    # re-create fit parameter settings after parameter bounds or initial guesses have been determined
    lmfit_params = model.make_params() # update lmfit params
    # get initial parameter info
    if verbose > 1:
        for pname in lmfit_params:
            print("parameters (start): ", lmfit_params[pname])
    # dealing with weights or errors (1-sigma data errors in x and/or y)
    if weights is not None and ((xerr is not None) or (yerr is not None)):
        print("cannot use weights when either xerr or yerr is present", error=True)
    # function to compute and return parameter statistics (median, std, error range, and parameter samples)
    def get_param_stats(fit_result, samples):
        # prepare for return class
        ret_popt = [] # parameter best value
        ret_pstd = [] # parameter standard deviation
        ret_perr = [] # parameter error range (lower and upper)
        ret_psamples = [] # parameter sampling list
        for ip in range(n_free_params):
            median = np.percentile(samples[:,ip], 50)
            percentile_16 = np.percentile(samples[:,ip], 16)
            percentile_84 = np.percentile(samples[:,ip], 84)
            ret_popt.append(median) # parameter median
            ret_pstd.append(np.std(samples[:,ip])) # standard deviation
            ret_perr.append(np.array([percentile_16-median, percentile_84-median])) # percentile distances from median
            ret_psamples.append(samples[:,ip]) # parameter samples
        return ret_popt, ret_pstd, ret_perr, ret_psamples
    # MCMC fitting
    if fit_method == 'mcmc':
        if verbose: print("Doing MCMC fitting...", color="green")
        import emcee
        independent_vars_dict = {model.independent_vars[0]:xdat} # set independent variable
        emcee_kws = dict(nwalkers=mcmc_walkers, steps=mcmc_steps, burn=mcmc_steps//4, thin=1, progress=True)
        fit_result = model.fit(data=ydat, params=lmfit_params, weights=weights, method='emcee', fit_kws=emcee_kws, *args, **kwargs, **independent_vars_dict)
        ret_lmfit_result = fit_result # for return class below
        sampler = fit_result.sampler
        # estimate auto-correlation time
        try:
            tau = sampler.get_autocorr_time(tol=0) # estimate auto-correlation time
            burnin = int(2 * np.max(tau)) # set burn-in to 2 times the maximum auto-correlation time
            thin = int(0.5 * np.min(tau)) # thinning to avoid correlated samples
            if verbose: print(f"Auto-correlation time: {tau}", color="cyan")
            if verbose: print(f"Estimated burn-in steps: {burnin}", color="cyan")
            if verbose: print(f"Thinning interval: {thin}", color="cyan")
        except emcee.autocorr.AutocorrError:
            print("Chains are too short to estimate autocorrelation time reliably.", color="yellow")
            burnin = emcee_kws["steps"] // 4 # fallback to arbitrary choice
            thin = 1
        # get the parameter samples from the chains
        samples = sampler.get_chain(discard=burnin, thin=thin, flat=True) # discard burn-in and thin
        # extract fit parameters
        ret_popt, ret_pstd, ret_perr, ret_psamples = get_param_stats(fit_result, samples)
        if plot_fit:
            # check convergence visually
            import matplotlib.pyplot as plt
            fig, axes = plt.subplots(nrows=n_free_params, ncols=1, figsize=(6, n_free_params*4), sharex=True)
            for ip in range(n_free_params):
                samples_tot_p = sampler.get_chain()[:, :, ip]
                for iw in range(emcee_kws["nwalkers"]):
                    plot(ax=axes[ip], y=samples_tot_p[:, iw], linewidth=1, alpha=0.5, xlabel="MCMC step number", ylabel=model.param_names[ip])
                color = "black"
                plot(x=[burnin,burnin], y=[samples_tot_p.min(),samples_tot_p.max()], color=color, linestyle="dotted") # mark burnin step
                med = ret_popt[ip]; p16 = med+ret_perr[ip][0]; p84 = med+ret_perr[ip][1] # parameter median, 16th and 84th percentile
                plot(x=[burnin,emcee_kws["steps"]], y=[med,med], color=color) # plot median
                plot(x=[burnin,emcee_kws["steps"]], y=[p16,p16], color=color, linestyle="dashed") # plot 16th percentile
                plot(x=[burnin,emcee_kws["steps"]], y=[p84,p84], color=color, linestyle="dashed") # plot 84th percentile
            show_or_save_plot(show=True)
    # Least-squares fitting
    if fit_method == 'ls':
        print("Doing least-squares fitting...", color="green")
        if xerr is not None or yerr is not None or perr_method == "systematic":
            ret_lmfit_result = None
            popts = [] # list of parameter samples
            if perr_method == "statistical":
                print("Performing statistical error estimate with "+str(n_random_draws)+" sampling fits, based on data errors provided...", highlight=True)
                # draw from Gaussian random distribution
                if xerr is not None:
                    xtry = np.array([generate_random_gaussian_numbers(n=n_random_draws, mu=xdat[i], sigma=xerr[i], seed=None) for i in range(len(xdat))])
                if yerr is not None:
                    ytry = np.array([generate_random_gaussian_numbers(n=n_random_draws, mu=ydat[i], sigma=yerr[i], seed=None) for i in range(len(ydat))])
                # for each random sample, fit and record the best-fit parameter(s) in popts
                for i in range(n_random_draws):
                    if xerr is not None:
                        x = xtry[:,i]
                    else:
                        x = xdat
                    if yerr is not None:
                        y = ytry[:,i]
                    else:
                        y = ydat
                    independent_vars_dict = {model.independent_vars[0]:x} # set independent variable
                    fit_result = model.fit(data=y, params=lmfit_params, weights=None, *args, **kwargs, **independent_vars_dict)
                    popt = []
                    for pname in fit_result.params:
                        popt.append(fit_result.params[pname].value)
                    popts.append(popt)
            if perr_method == "systematic":
                from random import seed, randrange
                n_dat_frac = max([n_free_params+1, int(np.ceil(max([0,min([dat_frac_for_systematic_perr,1])])*len(xdat)))]) # take only a fraction of the original data size (minimally, the number of parameters + 1)
                n_dat_toss = len(xdat) - n_dat_frac # number of data elements to drop
                print("Performing systematic error estimate with "+str(n_random_draws)+" sampling fits, based on random subsets of "+str(n_dat_frac/len(xdat)*100)+
                    "% of the original data, which are "+str(n_dat_frac)+" of total "+str(len(xdat))+" datapoints (note that minimum number of datapoints is the number of free parameters + 1 = "+
                    str(n_free_params+1)+").", highlight=True)
                for i in range(n_random_draws):
                    x = np.copy(xdat) # copy original x data
                    y = np.copy(ydat) # copy original y data
                    for i in range(n_dat_toss): # now randomly remove indices
                        seed(None) # set the random seed; if None, random uses the system time
                        ind = randrange(len(x))
                        x = np.delete(x, ind)
                        y = np.delete(y, ind)
                    independent_vars_dict = {model.independent_vars[0]:x} # set independent variable
                    fit_result = model.fit(data=y, params=lmfit_params, weights=None, *args, **kwargs, **independent_vars_dict)
                    popt = []
                    for pname in fit_result.params:
                        popt.append(fit_result.params[pname].value)
                    popts.append(popt)

            # prepare return values (median, standard deviation, 16th to 84th percentile, and complete list of popts)
            if len(popts) > 0:
                popts = np.array(popts)
                ret_popt, ret_pstd, ret_perr, ret_psamples = get_param_stats(fit_result, popts)

        else: # do a normal weighted or unweighted fit
            weights_info_str = "without"
            if weights is not None: weights_info_str = "with"
            print("Performing normal fit "+weights_info_str+" weights...", highlight=True)
            if weights is not None and scale_covar:
                print("Assuming good fit for reporting parameter errors. "+
                        "Consider setting 'scale_covar=False' if you believe the fit is not of good quality.", warn=True)
            # do the fit
            independent_vars_dict = {model.independent_vars[0]:xdat} # set independent variable
            fit_result = model.fit(data=ydat, params=lmfit_params, weights=weights, scale_covar=scale_covar, *args, **kwargs, **independent_vars_dict)
            ret_lmfit_result = fit_result # for return class below
            # prepare return values
            ret_popt, ret_pstd, ret_perr, ret_psamples = [[],[],[],[]]
            for ip, pname in enumerate(fit_result.params):
                ret_popt.append(fit_result.params[pname].value)
                ret_pstd.append(fit_result.params[pname].stderr)
                if ret_pstd[-1] is not None:
                    ret_perr.append(np.array([-fit_result.params[pname].stderr, fit_result.params[pname].stderr]))
                else:
                    ret_perr.append(None)
                ret_psamples.append(None)
    class ret: # class object to be returned
        lmfit_result = ret_lmfit_result # lmfit object
        pnames = model.param_names # parameter names (list)
        popt = np.array(ret_popt) # parameter best-fit values (np.array: shape (nparams))
        pstd = np.array(ret_pstd) # parameter standard deviation values (np.array: shape (nparams))
        perr = np.array(ret_perr) # parameter errors; upper and lower value (np.array: shape (nparams, 2))
        psamples = np.array(ret_psamples) # parameter samples in case of MCMC or LS uncertainty sampling (np.array: shape (nparams, nsamples))
        if fit_method == 'mcmc':
            mcmc_sampler = sampler
            mcmc_tau = tau
            mcmc_burnin = burnin
            mcmc_thin = thin
    if verbose:
        for ip, pname in enumerate(ret.pnames):
            print("fit parameters: ", pname+" = ", ret.popt[ip], ret.perr[ip], highlight=True)
    if plot_fit:
        # do corner plots if did sampling (either through MCMC or LS uncertainty sampling)
        if len(ret.psamples.shape) == 2:
            import corner
            fig = corner.corner(ret.psamples.T, labels=model.param_names, show_titles=True)
            show_or_save_plot(show=True)
        # plot the data and the fit
        plot(x=xdat, y=ydat, xerr=xerr, yerr=yerr, linestyle="", marker="o", label="data")
        xfit = np.linspace(np.min(xdat), np.max(xdat), 500)
        plot(x=xfit, y=func(xfit, *ret.popt), label="fit")
        plot(show=True)
    return ret
# === END fit ===

# === START logspace ===
# similar to numpy.logspace, but takes the non-log values of start and stop, i.e., as they appear in the output
def logspace(start, stop, *args, return_centre=False, **kwargs):
    base = kwargs.get('base', 10.0)
    if start <= 0 or stop <= 0: print("start and stop must be > 0 for logspace", error=True)
    log_start = np.log(start) / np.log(base)
    log_stop = np.log(stop) / np.log(base)
    ret = np.logspace(log_start, log_stop, *args, **kwargs)
    if return_centre: # centre values between [start, stop]
        tmp = np.log(ret)/np.log(base)
        ret = base**((tmp[:-1]+tmp[1:])/2)
    return ret
# === END logspace ===

# === START sym log space ===
# lin_thresh can be list of 2 elements to control [min, max] for linear range
def symlogspace(start, stop, num=100, base=10.0, lin_thresh=1e-2, num_lin=3, return_centre=False):
    if start >= stop: print("start must be < stop", error=True)
    if num < num_lin: print("num must be > num_lin; input values are num, num_lin: ", num, num_lin, error=True)
    # handle lin_thresh and error checking
    lt = np.array([lin_thresh]).flatten()
    if len(lt) == 1: lt = np.array([-lt[0], lt[0]]) # symmetric linear range
    if lt[0] >= 0 or lt[1] <= 0: print("lin_thresh must be > 0 (1-element input) or [<0, >0] (2-element input)", error=True)
    if start > lt[0] or stop < lt[1]:
        error_msg = "[start,end] must be [<,>] [-lin_thresh,lin_thresh] (1-element input) or [<lin_thresh[0],>lin_thresh[1]] (2-element input)"
        print(error_msg+"; input values are start, stop, lin_thresh: ", start, stop, lin_thresh, error=True)
    # number of points in each region
    num_log = num - num_lin
    neg_log_range = np.log(start/lt[0])/np.log(base)
    pos_log_range = np.log(stop/lt[1])/np.log(base)
    num_neg = int(np.floor(neg_log_range/(neg_log_range+pos_log_range)*num_log))
    num_pos = num_log - num_neg
    # negative log region
    neg = -logspace(-lt[0], -start, num=num_neg+1, base=base, return_centre=return_centre)[::-1]
    if not return_centre: neg = neg[:-1]
    # linear region
    if num_lin > 0:
        lin = np.linspace(lt[0], lt[1], num=num_lin)
        if return_centre: lin = (lin[1:]-lin[:-1])/2
    else: lin = np.array([])
    # positive log region
    pos = logspace(lt[1], stop, num=num_pos+1, base=base, return_centre=return_centre)
    if not return_centre: pos = pos[1:]
    # concatenate for return
    ret = np.concatenate([neg, lin, pos])
    return ret
# === END sym log space ===

# === START get_hostname ===
def get_hostname():
    from socket import getfqdn
    hostname = getfqdn()
    return hostname
# === END get_hostname ===

# === Decorator to print the runtime of the decorated function ===
def timer_decorator(func):
    from functools import wraps
    @wraps(func)
    def timer_decorator_wrapper(*args, **kwargs):
        from time import perf_counter
        start_time = perf_counter() # start time
        value = func(*args, **kwargs) # call the actual function that we are decorating with @timer
        end_time = perf_counter() # end time
        run_time = end_time - start_time # compute time difference
        print(f"finished {func.__name__!r} in {run_time:.4f} seconds")
        return value
    return timer_decorator_wrapper

# === Decorator to print the function signature and return value ===
def debug_decorator(func):
    from functools import wraps
    @wraps(func)
    def debug_decorator_wrapper(*args, **kwargs):
        args_repr = [repr(a) for a in args] # get nice string representation of args
        kwargs_repr = [f"{k}={v!r}" for k, v in kwargs.items()] # get nice string representation of keyword args
        signature = ", ".join(args_repr + kwargs_repr) # join them, so we see how the function was called
        print(f"calling {func.__name__}({signature})")
        value = func(*args, **kwargs)
        print(f"{func.__name__!r} returned {value!r}") # print the return value of the function
        return value
    return debug_decorator_wrapper

# === timer class to time different parts of code execution (named timers) ===
class timer:
    from datetime import datetime
    # ============= __init__ =============
    def __init__(self, name="", quiet=True):
        self.name = name # used to label the instance of timer (if needed)
        self.quiet = quiet # suppress time starting output
        self.start_time = None
        self.stop_time = None
        self.dt = None
        self.start()
    def start(self):
        self.start_time = self.datetime.now()
        if not self.quiet: print("timer('"+self.name+"'): start time = "+str(self.start_time))
    def stop(self):
        self.stop_time = self.datetime.now()
        if not self.quiet: print("timer('"+self.name+"'): stop time = "+str(self.stop_time))
    def get_dt(self):
        # check whether stop() was called; if not, call it here
        if self.stop_time is None: self.stop()
        # compute time difference in seconds
        self.dt = self.stop_time-self.start_time
    def report(self):
        self.stop()
        if self.dt is None: self.get_dt()
        print("=== timer('"+self.name+"'): start = "+str(self.start_time)+", stop = "+str(self.stop_time)+", runtime = "+str(self.dt), highlight=1, no_prefix=True)

# === class to monitor loop progress ===
class monitor:
    from datetime import datetime
    # ============= __init__ =============
    def __init__(self, loop_size, signature=""):
        self.loop_size = loop_size
        self.signature = signature # label
        self.report_status = 0.01
        self.start_time = self.datetime.now()
    def report(self, loop_index):
        def get_dt():
            return int((self.datetime.now()-self.start_time).total_seconds()*100)/100
        reported = False
        frac_done = (loop_index+1) / self.loop_size
        if (frac_done >= 0.01) and (self.report_status==0.01):
            print(self.signature+"...  1% done in "+str(get_dt())+"s...")
            self.report_status = 0.10
            reported = True
        if (frac_done >= 0.10) and (self.report_status==0.10):
            print(self.signature+"... 10% done in "+str(get_dt())+"s...")
            self.report_status = 1.00
            reported = True
        if (frac_done >= 1.00) and (self.report_status==1.00):
            print(self.signature+"...100% done in "+str(get_dt())+"s...")
            reported = True
        return reported

# === executes a shell command: input string 'cmd'
def run_shell_command(cmd, quiet=False, print_only=False, capture=False, **kargs):
    from subprocess import run
    from os import environ
    from sys import modules
    if 'mpi4py.MPI' in modules:
        if cmd.startswith(("mpirun", "mpiexec", "srun")):
            print('Calling an external MPI program may fail because mpi4py might interfere.', warn=True)
    if (not quiet) or print_only:
        if 'color' not in kargs.keys():
            kargs['color'] = 'magenta' # set default colour for shell command print
        print(cmd, **kargs)
    if (not print_only):
        sp_result = run(cmd, capture_output=capture, text=True, shell=True, env=environ.copy())
        return sp_result

# === START check_for_overwrite ===
def check_for_overwrite(filename):
    from os.path import isfile
    if isfile(filename):
        inp = input("Warning: file '"+filename+"' exisits; press 'p' to overwrite...")
        if inp != 'p': exit()
# === END check_for_overwrite ===

# === function returning all sub-directories, including hidden dirs ===
def get_dirs(dirname='.', include_base_dir=False, strip=False, verbose=1):
    from os import scandir
    # define recursive func
    def recursive_call(dirname='.', verbose=1):
        dirs = [f.path for f in scandir(dirname) if f.is_dir()]
        for dirname in list(dirs):
            if verbose > 1: print("adding sub-directories: ", dirs, highlight=3)
            dirs.extend(recursive_call(dirname, verbose=verbose))
        return dirs
    # call recursive func to get all sub-dirs
    dirs = recursive_call(dirname=dirname, verbose=verbose)
    if include_base_dir: dirs = ['.'] + dirs
    dirs = [x+'/' for x in dirs] # add trailing /
    if strip: dirs = [x[2:] for x in dirs]
    return dirs

# === function to search for a string pattern in each line of a file
# and return that line; or return a list of all the lines that match the search_str ===
def find_line_in_file(filename, search_str, debug=True):
    ret = []
    with open(filename, 'r') as f:
        for line in f:
            if line.find(search_str)!=-1:
                if debug==True: print(filename+": found line   : "+line.rstrip())
                ret.append(line)
    if len(ret)==1:
        ret = ret[0]
    return ret

# === function to search for a string pattern at the start of a line in a file, and to replace that line ===
def replace_line_in_file(filename, search_str, new_line, search_str_position=0, debug=True):
    from tempfile import mkstemp
    from shutil import move
    from os import remove as os_remove, chmod as os_chmod, close as os_close
    fd, tempfile = mkstemp()
    with open(tempfile, 'w') as ftemp:
        with open(filename, 'r') as f:
            for line in f:
                # find search str
                found = False
                if search_str_position is None: # search str match anywhere on line
                    if line.find(search_str) >= 0: found = True
                else: # search str match exactly at position
                    if line.find(search_str)==search_str_position: found = True
                # replace
                if found:
                    if debug==True: print(filename+": found line   : "+line.rstrip())
                    line = new_line+"\n"
                    if debug==True: print(filename+": replaced with: "+line.rstrip())
                # add lines to temporary output file
                if not found or new_line != "": ftemp.write(line)
    os_remove(filename)
    move(tempfile, filename)
    os_chmod(filename, 0o644)
    os_close(fd) # close file descriptor

# === function to add a line to a file ===
# === if position="end": append line to end of file ===
# === if position="beg": add line to beginning of file ===
def add_line_to_file(filename, add_line, position="end", debug=True):
    from tempfile import mkstemp
    from shutil import move
    from os import remove as os_remove, chmod as os_chmod, close as os_close
    fd, tempfile = mkstemp()
    if position == "end":
        open_flag = 'a'
    else:
        open_flag = 'w'
    with open(tempfile, open_flag) as ftemp:
        line = add_line+"\n"
        ftemp.write(line) # add the new line
        if debug==True: print(filename+": added line: "+line.rstrip())
        if position == "beg": # add previous lines (in case of position="beg")
            with open(filename, 'r') as f:
                for line in f:
                    ftemp.write(line)
    os_remove(filename)
    move(tempfile, filename)
    os_chmod(filename, 0o644)
    os_close(fd) # close file descriptor

# generates a numpy array with n uniformly distributed random numbers based on min and max
def generate_random_uniform_numbers(n=100, min=0.0, max=1.0, seed=None):
    from random import seed as random_seed, uniform as random_uniform
    random_seed(seed) # set the random seed; if None, random uses the system time
    random_numbers = [random_uniform(min, max) for _ in range(n)]
    return np.array(random_numbers)

# generates a numpy array with n Gaussian distributed random numbers based on mean mu and standard devitation sigma
def generate_random_gaussian_numbers(n=100, mu=0.0, sigma=1.0, seed=None):
    from random import seed as random_seed, gauss as random_gauss
    random_seed(seed) # set the random seed; if None, random uses the system time
    random_numbers = [random_gauss(mu, sigma) for _ in range(n)]
    return np.array(random_numbers)

# === return mean, stddev, skewness, kurtosis of input time series f(t) by integrating over t ===
def get_moments_from_time_series(time, func, ts=None, te=None):
    if ts is None: ts = np.nanmin(time) # start of t (lower limit of integral)
    if te is None: te = np.nanmax(time) # end of t (upper limit of integral)
    ind = (time >= ts) & (time <= te) # select relevant range
    tl = time[ind]
    ret = {"mean": np.nan, "std": np.nan, "skew": 0.0, "kurt": 0.0, "min": np.nan, "max": np.nan} # init return dict
    fl = func[ind]
    # get middle values and dx
    fmid = ( fl[:-1] + fl[1:] ) / 2.0
    dt = tl[1:] - tl[:-1]
    # get min/max
    ret["min"] = np.nanmin(fmid)
    ret["max"] = np.nanmax(fmid)
    # integrate to get moments and from that compute mean, stddev, skew, kurt
    norm = np.nansum(dt)
    if norm > 0:
        ret["mean"] = np.nansum(fmid*dt) / norm
        ret["std"]  = np.sqrt(np.nansum((fmid-ret["mean"])**2*dt) / norm)
        if ret["std"] > 0:
            ret["skew"] = np.nansum(fmid*((fmid-ret["mean"])/ret["std"])**3*dt) / norm
            ret["kurt"] = np.nansum(fmid*((fmid-ret["mean"])/ret["std"])**4*dt) / norm - 3.0 # excess kurtosis
    return ret

# === return mean, stddev, skewness, kurtosis of input distribution PDF(x) by integrating over x ===
def get_moments(x, pdf=None, xs=None, xe=None):
    if xs is None: xs = np.nanmin(x) # start of x (lower limit of integral)
    if xe is None: xe = np.nanmax(x) # end of x (upper limit of integral)
    ind = (x >= xs) & (x <= xe) # select relevant range
    xl = x[ind]
    ret = {"mean": np.nan, "std": np.nan, "skew": 0.0, "kurt": 0.0, "min": np.nan, "max": np.nan} # init return dict
    if pdf is None:
        from scipy.stats import skew, kurtosis
        ret["mean"] = np.nanmean(xl.flatten())
        ret["std"]  = np.nanstd(xl.flatten())
        ret["skew"] = skew(xl.flatten(), nan_policy='omit')
        ret["kurt"] = kurtosis(xl.flatten(), nan_policy='omit')
        ret["min"] = np.nanmin(xl.flatten())
        ret["max"] = np.nanmax(xl.flatten())
    else:
        yl = pdf[ind]
        # get middle values and dx
        xmid = ( xl[:-1] + xl[1:] ) / 2.0
        ymid = ( yl[:-1] + yl[1:] ) / 2.0
        dx = xl[1:] - xl[:-1]
        # integrate to get moments and from that compute mean, stddev, skew, kurt
        norm = np.nansum(ymid*dx)
        if norm > 0:
            ret["mean"] = np.nansum(ymid*xmid*dx) / norm
            ret["std"]  = np.sqrt(np.nansum(ymid*(xmid-ret["mean"])**2*dx) / norm)
            if ret["std"] > 0:
                ret["skew"] = np.nansum(ymid*((xmid-ret["mean"])/ret["std"])**3*dx) / norm
                ret["kurt"] = np.nansum(ymid*((xmid-ret["mean"])/ret["std"])**4*dx) / norm - 3.0 # excess kurtosis
    return ret

# === START get_pdf ===
# get the PDF of data and return centred bin values
def get_pdf(data, range=None, bins=200):
    pdf, bin_edges = np.histogram(data, range=None, density=True, bins=bins)
    bin_centres = ( bin_edges[1:] + bin_edges[:-1] ) / 2.0
    class ret:
        def __init__(self, pdf_, bin_edges_, bin_centres_):
            self.pdf = pdf_
            self.bin_edges = bin_edges_
            self.bin_centres = bin_centres_
    return ret(pdf, bin_edges, bin_centres)
# === END get_pdf ===

# === bin data with bin_values (same size as data) into bins (number or array of bin edges) ===
def get_binned_stats(data, bin_values, bins=None, statistic='mean', **kwargs):
    from scipy.stats import binned_statistic
    if bins is None: bins = 100
    binned_stats = binned_statistic(bin_values.flatten(), data.flatten(), bins=bins, statistic=statistic)
    return binned_stats.statistic, binned_stats.bin_edges

# === bin data with 2 bin_values (each with the same size as data) into 2D bins (number or array of bin edges) ===
def get_binned_stats_2d(data, bin_values_1, bin_values_2, bins=None, statistic='sum', **kwargs):
    from scipy.stats import binned_statistic_2d
    if bins is None: bins = 100
    binned_stats = binned_statistic_2d(bin_values_1.flatten(), bin_values_2.flatten(), data.flatten(), bins=bins, statistic=statistic)
    return binned_stats.statistic, binned_stats.x_edge, binned_stats.y_edge

# === START get_spectrum ===
# Computes the Fourier (k-space) spectrum of 'data_in' with ncmp components in axis=0.
# E.g., for a 64^3 dataset and 3 vector components, data.shape must be (3, 64, 64, 64).
# E.g., for a 32^2 dataset with only 1 component, data.shape must be (32, 32).
# Note that if 'data_in' is 2D or 3D, then the indices are in order data_in[x,[y,[z]]].
# Binning can be 'spherical' (default ->1D) or 'cylindrical' (->2D).
# If binning='cylindrical' (only for 3D input): r_cyl^2=x^2+y^2 -> k_perp; z_cyl=z -> k_para.
# If sum=True, then bininng uses 'sum' instead of 'mean' and integral_factor = 1.
# Results should be similar with either sum=True or sum=False.
# If return_ft_data=True, it also returns the full Fourier-transformed dataset.
# If mirror, applying mirroring of original data - only use in case of non-periodic datasets
# If window, apply a Tukey window (window can be a float between 0 and 1; higher means stronger windowing; default 0.1)
# Use verbose=0 to switch off any status prints from this function.
def get_spectrum(data_in, ncmp=1, binning='spherical', sum=False, return_ft_data=False, mirror=False, window=False, verbose=1):
    # check binning type
    supported_binning = ["spherical", "cylindrical"]
    if binning not in supported_binning:
        print("binning='"+binning+"' not supported; binning must be any of ", supported_binning, error=True)
    # check statistic type
    if sum:
        statistic = 'sum'
        normalise = False
    else:
        statistic = 'mean'
        normalise = True
    # make copy
    data = np.copy(data_in)
    if (ncmp == 1) and (data.shape[0] > 1):
        data = np.array([data]) # add an extra (fake) index, so we can index as if there were components
    # Tukey window
    if window:
        if type(window) == float: alpha = window
        else:                     alpha = 0.1
        def apply_tukey_window_nd(arr, alpha=alpha):
            from scipy.signal.windows import tukey
            window = np.ones_like(arr, dtype=float)
            for axis, size in enumerate(arr.shape):
                win = tukey(size, alpha)
                shape = [1] * arr.ndim
                shape[axis] = size
                window *= win.reshape(shape)
            return arr * window
        for d in range(ncmp):
            data[d] = apply_tukey_window_nd(data[d])
    # mirroring to create a periodic array
    if mirror:
        # mirrors original array to make a periodic array with twice the size in all dimensions
        def periodic_mirror(arr):
            result = arr
            for axis in range(arr.ndim):
                mirrored = np.flip(result, axis=axis)
                result = np.concatenate([result, mirrored], axis=axis)
            return result
        data_mirrored = []
        for d in range(ncmp):
            data_mirrored.append(periodic_mirror(data[d]))
        data_mirrored = np.array(data_mirrored) # used in FT below
    num = np.array(data[0].shape) # number of points in data
    ndim = len(num) # number of dimensions
    if binning == 'cylindrical': # error checking
        if ndim != 3:
            print("Parallel-perpendicular binning currently only works for 3D datasets!", error=True)
        if (num[0] != num[1]) or (num[0] != num[2]):
            print("Parallel-perpendicular binning currently only works for cubic datasets!", error=True)
    # print info about real-space field
    mean_sq = 0.0
    std_sq = 0.0
    for d in range(ncmp):
        mean_sq += data[d].mean()**2
        std_sq += np.std(data[d])**2
    if verbose: print("data mean squared = "+eform(mean_sq)+", data std squared = "+eform(std_sq))
    # construct wave numbers and bins
    ks = -(num//2) # k start
    ke = np.array([num[d]//2+(num[d]%2-1) for d in range(ndim)]) # k end
    k = get_coords(ks, ke, num, cell_centred=False) # get k vector with k=0 in the center
    if binning == 'cylindrical':
        k_perp = k[0:2] # split the k array into perpendicular and parallel components
        k_para = k[2] # the z axis is the parallel direction
    if ndim == 1: k_abs = np.abs(k) # length of k vector
    if ndim  > 1: k_abs = np.sqrt((k**2).sum(axis=0)) # length of k vector
    if binning == 'cylindrical': # construct absolute k_perp and k_para for binning below
        k_abs_perp = np.sqrt((k_perp**2).sum(axis=0))
        k_abs_para = np.abs(k_para)
    bins = np.arange(np.max(ke)+2) - 0.5 # k bins for 1D spectrum
    # do Fourier transformation
    def fourier_transform(arr):
        arr_ft = []
        for d in range(ncmp):
            arr_ft.append(np.fft.fftn(arr[d].T, norm='forward')) # FFT (note that we transpose before FFT, to get arr[x,[y,[z]]] -> arr[[[z],y],x])
            arr_ft[d] = np.fft.fftshift(arr_ft[d]).T # shift k=0 to center and transpose back, so we have arr_ft[kx,[ky,[kz]]]
            if mirror:
                # get shape of original array (after mirroring, the number of elements in each ndim has doubled)
                original_shape = np.array(arr[d].shape) / 2
                # now select every 2nd k-mode, taking care of the offsets, so we hit k=0 in the middle and get the even k modes of the mirrored FT
                starts = [0 if s % 2 == 0 else 1 for s in original_shape]
                slices = tuple(slice(start, None, 2) for start in starts)
                arr_ft[d] = arr_ft[d][slices]
        return np.array(arr_ft)
    if not mirror: data_ft = fourier_transform(data)
    else:          data_ft = fourier_transform(data_mirrored)
    # get total power
    power_tot = (np.abs(data_ft)**2).sum(axis=0)
    P0 = power_tot[k_abs==0][0] # extract k=0 value of power spectrum
    norm = power_tot.sum()-P0 # integral over all k!=0
    if verbose: print("           P(k=0) = "+eform(P0)+",      total power = "+eform(norm))
    # bin in k shells
    if binning == 'spherical':
        spect_tot, bins = get_binned_stats(power_tot, k_abs, bins=bins, statistic=statistic)
        bin_centers = bins[:-1]+0.5
        if statistic == "mean":
            integral_factor = bin_centers**(ndim-1)
            if ndim > 1: integral_factor *= np.pi*2*(ndim-1)
    if binning == 'cylindrical':
        spect_tot, bins_perp, bins_para = get_binned_stats_2d(power_tot, k_abs_perp, k_abs_para, bins=[bins,bins], statistic=statistic)
        bin_centers_perp = bins_perp[:-1]+0.5
        bin_centers_para = bins_para[:-1]+0.5
        # construct 2D array with k values
        k2d = get_2d_coords(cmin=[bin_centers_perp[0],bin_centers_para[0]], cmax=[bin_centers_perp[-1],bin_centers_para[-1]], ndim=[len(bin_centers_perp),len(bin_centers_para)], cell_centred=False)
        bin_centers = np.sqrt((k2d**2).sum(axis=0))
        if statistic == "mean":
            integral_factor = 2*2**np.pi*k2d[0] # 2 pi k_perp is the circumference when integrating over phi, and the additional factor 2 is because we fold k_para
            integral_factor[0,:] = 1.0 # set the entire k_perp = 0 axis to an integral factor of 1, so we don't destroy the power on that axis when multiplying below
    # integral factor and normalisation if needed
    if statistic == "sum": integral_factor = np.ones(spect_tot.shape)
    spect_tot[bin_centers!=0] *= integral_factor[bin_centers!=0] # k=0 stays
    if normalise: spect_tot[bin_centers!=0] = spect_tot[bin_centers!=0] / spect_tot[bin_centers!=0].sum() * norm # normalise
    # construct return dict (more added below)
    if binning == 'spherical':
        ret = {'k': bin_centers, 'P_tot': spect_tot}
    if binning == 'cylindrical':
        # integrate over k_para -> P_perp and integrate over k_perp -> P_para
        spect_tot[bin_centers==0] = 0.0 # temporarily set P(k=0)=0 for easier summation
        spect_tot_perp = np.sum(spect_tot, axis=1)
        spect_tot_para = np.sum(spect_tot, axis=0)
        spect_tot[bin_centers==0] = P0 # restore P(k=0)
        ret = {'k': bin_centers, 'P_tot': spect_tot, 'k_perp': bin_centers_perp, 'k_para': bin_centers_para, 'P_tot_perp': spect_tot_perp, 'P_tot_para': spect_tot_para}
    # # Helmholtz decomposition
    if ncmp > 1: # there is more than 1 component
        power_lgt = np.zeros(num, dtype=complex)
        if ndim == 1: power_lgt += k*data_ft[0] # 1D case: scalar product (k is a 1D array and we only use x-component data for the longitudinal power)
        if ndim >= 2: # 2D and 3D cases: scalar product (get power along k); if ndim < ncmp (i.e., 2.5D), the z-component does not enter the scalar product
            for d in range(ndim): power_lgt += k[d]*data_ft[d] # scalar product
        power_lgt = np.abs(power_lgt/np.maximum(k_abs,1e-99))**2
        power_trv = power_tot - power_lgt
        power_trv[k_abs==0] = 0.0 # remove k=0 mode from decomposed spectra
        norm_lgt = power_lgt.sum(); norm_trv = power_trv.sum()
        if verbose:
            print("longitudinal (lgt) power = "+eform(norm_lgt)+", relative to total: "+str(norm_lgt/norm))
            print("  transverse (trv) power = "+eform(norm_trv)+", relative to total: "+str(norm_trv/norm))
        if binning == 'spherical':
            spect_lgt, bins = get_binned_stats(power_lgt, k_abs, bins=bins, statistic=statistic)
            spect_trv, bins = get_binned_stats(power_trv, k_abs, bins=bins, statistic=statistic)
        if binning == 'cylindrical':
            spect_lgt, bins_perp, bins_para = get_binned_stats_2d(power_lgt, k_abs_perp, k_abs_para, bins=[bins,bins], statistic=statistic)
            spect_trv, bins_perp, bins_para = get_binned_stats_2d(power_trv, k_abs_perp, k_abs_para, bins=[bins,bins], statistic=statistic)
        spect_lgt[bin_centers!=0] *= integral_factor[bin_centers!=0] # k=0 stays
        spect_trv[bin_centers!=0] *= integral_factor[bin_centers!=0] # k=0 stays
        if normalise: spect_lgt[bin_centers!=0] = spect_lgt[bin_centers!=0] / spect_lgt[bin_centers!=0].sum() * norm_lgt # normalise
        if normalise: spect_trv[bin_centers!=0] = spect_trv[bin_centers!=0] / spect_trv[bin_centers!=0].sum() * norm_trv # normalise
        ret['P_lgt'] = spect_lgt
        ret['P_trv'] = spect_trv
    if return_ft_data: ret['Power_tot'] = power_tot # if the user wants to have the Fourier-transformed data (power) returned
    return ret # return dict with power spectrum data
# === END get_spectrum ===

# === return a KDE'd version of 'data' ===
def get_kde_sample(data, n=1000, seed=1, show=False):
    from scipy.stats import gaussian_kde
    kernel = gaussian_kde(data)
    data_resampled = kernel.resample(size=n, seed=seed)
    if show:
        import matplotlib.pyplot as plt
        pdf_obj = get_pdf(data)
        pdf_original = pdf_obj.pdf
        pdf_obj = get_pdf(data_resampled)
        pdf_resampled = pdf_obj.pdf
        x = pdf_obj.bin_center
        plot(x=x, y=pdf_original, label='original')
        plot(x=x, y=kernel.pdf(x), label='KDE')
        plot(x=x, y=pdf_resampled, label='resampled')
        plot(show=True)
    return data_resampled

# === START round ===
# return x rounded to nfigs significant figures
def round(xin, nfigs=3, str_ret=False):
    x = np.array(xin) # convert to array in case of list input
    # Calculate the order of magnitude of x with special treatment if x=0
    idx = x != 0
    order_of_magnitude = np.zeros(x.shape)
    order_of_magnitude[idx] = np.floor(np.log10(np.abs(x[idx])))
    # Scale the number to the desired precision, round it, then scale it back
    scaled_x = np.round(x / 10**order_of_magnitude, nfigs-1)
    rounded_x = np.round(scaled_x * 10**nfigs).astype(int) / 10**(nfigs-order_of_magnitude)
    # in case the user requested a string to be returned
    if not str_ret:
        return rounded_x # return rounded value
    else:
        # helper function that converts float to string with appropriate significant-figure formatting
        def to_str(rx):
            parts = str(rx).split('e') # split into scale part and exp part
            scale_part = parts[0]
            negative_x = False
            if scale_part[0] == "-": # check if the value is negative
                negative_x = True
                scale_part = scale_part[1:] # strip the minus from the start
            if scale_part.find('.') == -1: # if round number, add trailing '.0'
                scale_part += '.0'
            dot_separated = scale_part.split('.') # separate where the . is
            offset = 2
            if dot_separated[0] == '0':
                offset += 1
            # in case the requested number of nfigs is > the intrinsic nfigs of x
            if len(scale_part)-offset < nfigs:
                scale_part += "0"*(nfigs-(len(scale_part)-offset)-1) # add trailing zeros
            if len(dot_separated[0]) >= nfigs: # special treatment
                scale_part = dot_separated[0]
            # put string back together
            if negative_x: # add leading minus sign if needed
                scale_part = "-"+scale_part
            rx_str = scale_part
            if len(parts) == 2:
                rx_str += "e"+parts[1] # re-attach the exp part
            return rx_str
        # construct return object, depending on array/list or float input
        if isinstance(rounded_x, np.ndarray):
            rounded_x_str = [to_str(rx) for rx in rounded_x]
        else:
            rounded_x_str = to_str(rounded_x)
        return rounded_x_str
# === END round ===

# === START round_with_error ===
# round a value and its error (uncertainty) to given nfigs significant figures
def round_with_error(val, val_err, nfigs=2):
    # prepare function for scalar or array input and copy into ret
    ret_val = np.array(val)
    ret_val_err = np.array(val_err)
    if ret_val.shape != ret_val_err.shape:
        print("input value and associated error must have the same shape", error=True)
    scalar_input = False
    if ret_val.ndim == 0:
        ret_val = ret_val[None] # makes x 1D
        ret_val_err = ret_val_err[None] # makes x 1D
        scalar_input = True
    # iterate over each element in ret
    for i, val_err in enumerate(np.nditer(ret_val_err)):
        n = int(np.log10(val_err)) # displacement from ones place
        if val_err >= 1: n += 1
        scale = 10**(nfigs - n)
        ret_val[i] = np.round(ret_val[i] * scale) / scale
        ret_val_err[i] = np.round(val_err * scale) / scale
    # strip dimension if input was scalar and return
    if scalar_input: return np.squeeze(ret_val), np.squeeze(ret_val_err)
    return ret_val, ret_val_err
# === END round_with_error ===

# === START eform ===
# return x in E-format
def eform(x, prec=10, print_leading_plus=False):
    import decimal
    def eform_scalar(x):
        xx = decimal.Decimal(float(x))
        tup = xx.as_tuple()
        xx = xx.quantize(decimal.Decimal("1E{0}".format(len(tup[1])+tup[2]-prec-1)), decimal.ROUND_HALF_UP)
        tup = xx.as_tuple()
        exp = xx.adjusted()
        sign = '-' if tup.sign else '+' if print_leading_plus else ''
        dec = ''.join(str(i) for i in tup[1][1:prec+1])
        if prec > 0:
            return '{sign}{int}.{dec}E{exp:+03d}'.format(sign=sign, int=tup[1][0], dec=dec, exp=exp)
        elif prec == 0:
            return '{sign}{int}E{exp:+03d}'.format(sign=sign, int=tup[1][0], exp=exp)
        else:
            return None
    # prepare function for scalar or array input and copy into ret
    ret = np.array(x).astype(str)
    scalar_input = False
    if ret.ndim == 0:
        ret = ret[None] # makes x 1D
        scalar_input = True
    # iterate over each element in ret
    for i, val in enumerate(np.nditer(ret)):
        ret[i] = eform_scalar(val)
    # strip dimension if input was scalar and return
    if scalar_input: return str(np.squeeze(ret))
    return ret
# === END eform ===

# escape latex
def tex_escape(text):
    from re import compile, escape
    conv = {
        '&': r'\&',
        '%': r'\%',
        '$': r'\$',
        '#': r'\#',
        '_': r'\_',
        '{': r'\{',
        '}': r'\}',
        '~': r'\textasciitilde{}',
        '^': r'\^{}',
        '\\': r'\textbackslash{}',
        '<': r'\textless{}',
        '>': r'\textgreater{}',
    }
    regex = compile('|'.join(escape(str(key)) for key in sorted(conv.keys(), key = lambda item: - len(item))))
    return regex.sub(lambda match: conv[match.group()], text)

# === read an ASCII file ===
# === select plain=True, to read each line into a list ===
def read_ascii(filename, astropy_read=True, read_header=True, quiet=False, max_num_lines=1e7, plain=False, *args, **kwargs):
    if plain:
        with open(filename) as file:
            lines = [line.rstrip() for line in file]
        return lines
    # ASCII table reading
    from astropy.io.ascii import read as astropy_ascii_read
    from astropy.table import Table
    if not quiet: print("reading data in '"+filename+"'...")
    if astropy_read: # simple, but slow
        tab = astropy_ascii_read(filename, *args, **kwargs)
    else: # manually reading and parsing the file; much faster
        with open(filename, 'r') as f:
            if read_header: header = np.array(f.readline().split()) # read header (first line)
            err = [] # error container
            dat = np.empty((int(max_num_lines),len(header))) # init output data table
            il = 0 # index to append line to output table
            for line in f: # loop through all lines in file
                try: dat[il] = np.asarray(line.split(), dtype=float); il += 1 # fill table with floats
                except: err.append(line) # append to error container
        dat = dat[:il] # resize table to correct size
        tab = Table() # make astropy table
        for i in range(len(dat[0])):
            tab[header[i]] = dat[:,i] # insert columns
    if not quiet: print("File '"+filename+"' read; (nrow,ncol) = ({:d},{:d}).".format(len(tab), len(tab.columns)))
    return tab

# === write an ASCII file ===
# === select plain=True, to write list (dat) with lines to file ===
def write_ascii(filename, dat, format='fixed_width', delimiter="", comment=False, quiet=False, plain=False, *args, **kwargs):
    if plain:
        with open(filename, 'w') as file:
            for line in dat:
                file.write(f"{line}\n")
    else:
        from astropy.io.ascii import write as astropy_ascii_write
        astropy_ascii_write(dat, filename, overwrite=True, format=format, delimiter=delimiter, comment=comment, *args, **kwargs)
        if not quiet: print("Table written with (nrow, ncol) = ({:d},{:d}).".format(len(dat), len(dat.columns)))
    if not quiet: print("File '"+filename+"' written.")

# smoothing/filtering data
def smooth(x, y, window_npts=11, order=3):
    from scipy.signal import savgol_filter
    xy_filtered = savgol_filter((x, y), window_npts, order)
    return xy_filtered[0], xy_filtered[1]

# === scale factor from redshift ===
def scale_factor(redshift):
    return 1.0 / (1.0 + redshift)

# === for given redshift, convert co-moving quantity q with physical unit 'qtype' to proper quantity (use inverse=True) for prop -> co-mov ===
def comov2proper(q, redshift=None, qtype=None, inverse=False):
    if redshift is None or redshift == 0: return q
    if qtype is None: return q
    a = scale_factor(redshift) # get the scale factor
    if inverse: a = 1/a        #for the inverse transformation case (proper to comoving)
    if qtype.find('size') != -1 or qtype.find('len') != -1 or qtype.find('vel') != -1:
        return q * a # length or velocity
    if qtype.find('dens') != -1 or qtype.find('pden') != -1:
        return q / a**3 # any mass density
    if qtype.find('pres') != -1:
        return q / a # pressure
    if qtype.find('temp') != -1 or qtype.find('ener') != -1 or qtype.find('gpot') != -1:
        return q * a**2 # temperature or energy (specific or non-specific) or gravitational potential

# === Larmor radius ===
def r_larmor(B, v, m=const.m_p, q=const.ec):
    return m * v / (q * B)

# === Larmor time (time to gyrate once) ===
def t_larmor(B, m=const.m_p, q=const.ec):
    return 2 * np.pi * m / (q * B)

def tff(rho):
    return np.sqrt(3.0*np.pi/(32.0*const.g_n*rho))

# === return Jeans length ===
def lJ(rho, c_s):
    return np.sqrt(np.pi*c_s**2/(const.g_n*rho))

# === return Jeans mass ===
def MJ(rho, c_s):
    return rho * 4.0*np.pi/3.0*(lJ(rho, c_s)/2.0)**3

def sink_dens_thresh(r_sink, c_s):
    return np.pi * c_s**2 / (4.0 * const.g_n * r_sink**2)

# === return mass ===
def mass(rho, L, spherical=False):
    ret = 0.0
    if spherical:
        ret = 4.0*np.pi/3.0 * rho * (L/2.0)**3
    else:
        ret = rho * L**3
    return ret

# === return virial parameter (spherical uniform-density approximation) ===
def alpha_vir(rho, L, sigma_v, spherical=False):
    return 5.0 * sigma_v**2 * L / (6.0 * const.g_n * mass(rho, L, spherical))

# === return sigma_s(Mach, b, beta) ===
def sigma_s(Mach, b=0.4, beta=1e99):
    beta_factor = beta / (beta + 1.0)
    sigma_s = np.sqrt(np.log(1.0 + b**2*Mach**2*beta_factor))
    return sigma_s

# === return sigma from input mean and mean-square ===
def get_sigma(mean, ms):
    diff = np.array(ms - mean**2)
    ind = np.where(diff < 0)[0]
    if diff.size > 0: diff[ind] = 0.0 # in case there is numeric rounding to near zero, we return 0
    return np.sqrt(diff)

# === return density Rankine-Hugoniot shock jump condition- ===
def shock_jump_rho(Mach, gamma=5.0/3.0):
    return (gamma+1) / (gamma-1+2/Mach**2)

# === return pressure Rankine-Hugoniot shock jump condition- ===
def shock_jump_p(Mach, gamma=5.0/3.0):
    return (1-gamma+2*gamma*Mach**2) / (gamma+1)

# === return temperature Rankine-Hugoniot shock jump condition- ===
def shock_jump_T(Mach, gamma=5.0/3.0):
    return shock_jump_p(Mach,gamma) / shock_jump_rho(Mach,gamma)

# === START polytropic_eos ===
# piecewise polytropic equation of state (polytropic EOS): pres = Konst*dens^Gamma
def polytropic_eos(dens, mu=2.3):
    class ret:
        def __init__(self, ):
            # density and polytropic Gamma ranges (Masunaga & Inutsuka 2000)
            self.dens = dens
            self.mu = mu
            self.dens_thresh = [0.0, 2.50e-16, 3.84e-13, 3.84e-8, 3.84e-3] # density threshold to define denisty regimes
            self.Gamma = [1.0, 1.1, 1.4, 1.1, 5/3] # polytropic Gamma
            self.Konst = [(0.2e5)**2] # polytropic constant
            for i in range(1, 5):
                self.Konst.append(self.Konst[i-1]*self.dens_thresh[i]**(self.Gamma[i-1]-self.Gamma[i]))
            # loop through piecewise ranges to find the requested density regime
            for i in range(5):
                if self.dens >= self.dens_thresh[i]:
                    self.pres = self.Konst[i] * self.dens**self.Gamma[i] # pressure
                    self.cs = np.sqrt(self.Gamma[i]*self.pres/self.dens) # sound speed
                    self.temp = self.pres / (self.dens/self.mu/const.m_p) / const.k_b # temperature
                    break
    return ret()
# === END polytropic_eos ===

# === START get_1d_coords ===
# return cell-centered coordinates | . | . |
#                               xmin       xmax
# or face-centred if keyword cell_centred=False
def get_1d_coords(cmin=0, cmax=1, ndim=10, cell_centred=True):
    if cell_centred:
        d = (cmax-cmin) / float(ndim)
        offset = d/2
    else:
        d = (cmax-cmin) / float(ndim-1)
        offset = 0.0
    return np.linspace(cmin+offset, cmax-offset, num=ndim)
# === END get_1d_coords ===

# === START get_2d_coords ===
def get_2d_coords(cmin=[0,0], cmax=[1,1], ndim=[10,10], cell_centred=True):
    cmin = np.array(cmin)
    cmax = np.array(cmax)
    ndim = np.array(ndim)
    if cmin.ndim != 1: cmin = [cmin,cmin]
    if cmax.ndim != 1: cmax = [cmax,cmax]
    if ndim.ndim != 1: ndim = [ndim,ndim]
    c0 = get_1d_coords(cmin=cmin[0], cmax=cmax[0], ndim=ndim[0], cell_centred=cell_centred)
    c1 = get_1d_coords(cmin=cmin[1], cmax=cmax[1], ndim=ndim[1], cell_centred=cell_centred)
    return np.array(np.meshgrid(c0, c1, indexing='ij'))
# === END get_2d_coords ===

# === START get_3d_coords ===
def get_3d_coords(cmin=[0,0,0], cmax=[1,1,1], ndim=[10,10,10], cell_centred=True):
    cmin = np.array(cmin)
    cmax = np.array(cmax)
    ndim = np.array(ndim)
    if cmin.ndim != 1: cmin = [cmin,cmin,cmin]
    if cmax.ndim != 1: cmax = [cmax,cmax,cmax]
    if ndim.ndim != 1: ndim = [ndim,ndim,ndim]
    c0 = get_1d_coords(cmin=cmin[0], cmax=cmax[0], ndim=ndim[0], cell_centred=cell_centred)
    c1 = get_1d_coords(cmin=cmin[1], cmax=cmax[1], ndim=ndim[1], cell_centred=cell_centred)
    c2 = get_1d_coords(cmin=cmin[2], cmax=cmax[2], ndim=ndim[2], cell_centred=cell_centred)
    return np.array(np.meshgrid(c0, c1, c2, indexing='ij'))
# === END get_3d_coords ===

# === START get_coords ===
# this function takes lists or arrays as inputs,
# determining the dimensionality of the requested coordinates from the dimensionality of the inputs;
# for example, if cmin=[0,0], cmin=[1,1], ndim=[10,10], this function returns 2D corrdinates with 10 points in x=y=[0,1]
def get_coords(cmin, cmax, ndim, cell_centred=True):
    if (type(cmin) != list) and (type(cmin) != np.ndarray): print("need list or nump array inputs", error=True)
    cmin = np.array(cmin)
    cmax = np.array(cmax)
    ndim = np.array(ndim)
    if (cmin.shape != cmax.shape) or (cmax.shape != cmax.shape):
        print("Error: cmin, cmax, ndim, all must have the same shape.", error=True)
    if ndim.shape[0] == 1: return np.array(get_1d_coords(cmin[0], cmax[0], ndim[0], cell_centred))
    if ndim.shape[0] == 2: return np.array(get_2d_coords(cmin, cmax, ndim, cell_centred))
    if ndim.shape[0] == 3: return np.array(get_3d_coords(cmin, cmax, ndim, cell_centred))
# === END get_coords ===

# START gauss_smooth ===
# Smoothing of n-dimensional array 'input_data' with Gaussian kernel.
# Kernel sigma or FWHM in pixel units (optionally provided per dimension).
# Support for NaN pixels in input_data.
def gauss_smooth(input_data, sigma=None, fwhm=None, mode='wrap', truncate=3.0, verbose=1):
    from scipy.ndimage import gaussian_filter, generic_filter
    # check inputs
    if sigma is None and fwhm is None:
        print("Either sigma or fwhm must be specified for Gaussian smoothing.", error=True)
    if sigma is not None and fwhm is not None:
        print("Cannot set both sigma or fwhm; specify either sigma or fwhm for Gaussian smoothing.", error=True)
    # work out the input sigma for the scipy smoothing function
    sigma_in = None
    if sigma is not None:
        sigma_in = np.array(sigma)
    if fwhm is not None:
        sigma_in = np.array(fwhm) / (2.0*np.sqrt(2.0*np.log(2.0))) # convert FWHM to sigma
    # extend dimensions of input sigma if needed
    if sigma_in.ndim != input_data.ndim-1:
        tmp = np.zeros(input_data.ndim)
        tmp[:] = sigma_in
        sigma_in = tmp
    # check if there are NaNs in the input_data array
    if np.isnan(input_data).sum() == 0:
        # if no NaNs present, call scipy gaussian filter
        smoothed_data = gaussian_filter(input_data, sigma=sigma_in, order=0, mode=mode, truncate=truncate)
    else: # we have NaNs in input_data array
        if verbose: print("Data array contains NaN; using generic_filter for Gaussian smoothing...", warn=True)
        # generic filter function
        def nan_gaussian_filter(arr_in, size, gauss_weights):
            # reshape array
            arr = arr_in.reshape(size)
            # mask out NaN values
            valid_mask = ~np.isnan(arr)
            if valid_mask.sum() == 0: # all values are NaN
                return np.nan
            # apply Gaussian weights to valid values
            weighted_sum = np.sum(gauss_weights[valid_mask]*arr[valid_mask])
            weights_sum  = np.sum(gauss_weights[valid_mask])
            return weighted_sum / weights_sum
        # apply Gaussian smoothing while treating NaNs
        size = (2*np.ceil(truncate*sigma_in)+1).astype(int) # sub-shape on which filter operates (i.e., truncated at truncate*sigma)
        # create Gaussian weights based on distance from center
        center = np.array(size) // 2
        slices = tuple(slice(0, s) for s in size)
        coords = np.mgrid[slices] # coordinates
        distance_squared_divided_by_sigma_squared = np.sum((r-c)**2/s**2 for r, c, s in zip(coords, center, sigma_in))
        gauss_weights = np.exp(-0.5*distance_squared_divided_by_sigma_squared)
        smoothed_data = generic_filter(input_data, nan_gaussian_filter, size=size, mode=mode, extra_arguments=(size, gauss_weights))
    return smoothed_data
# END gauss_smooth ===

# === START rebin ===
# similar to IDL rebin
def rebin(inarray, outshape):
    inshape = inarray.shape # get shape of input array
    dims = len(inshape) # get dimensionality
    # turn outshape into list if necessary
    if not isinstance(outshape, list) and not isinstance(outshape, tuple):
        outshape = [outshape]
    # check consistency in dimensionality
    if len(outshape) != dims:
        print("outshape must have the same dimensionality as the input array ("+str(dims)+"D)!", error=True)
    shape = []
    for dim in range(dims):
        if outshape[dim] > inshape[dim]: # only compression of the array is supported at the moment
            print("outshape must be <= inshape", error=True)
        if (inshape[dim]%outshape[dim] != 0): # integer multiples check
            print("rebin only works for integer multiples of input and output dimensions", error=True)
        shape.append([outshape[dim], inshape[dim]//outshape[dim]]) # create shape for reshaping inarray
    shape = np.array(shape).flatten() # flatten shape
    ret = inarray.reshape(shape) # reshape inarray
    for dim in range(dims):
        ret = ret.mean(axis=-dim-1) # average (compression) of relevant reshaped dimension
    return ret
# === END rebin ===

# === START congrid ===
# similar to IDL congrid
def congrid(inarray, outshape, method="linear"):
    from scipy.interpolate import RegularGridInterpolator
    inshape = inarray.shape # get shape of input array
    dims = len(inshape) # get dimensionality
    # turn outshape into list if necessary
    if not isinstance(outshape, list) and not isinstance(outshape, tuple):
        outshape = [outshape]
    # check consistency in dimensionality
    if len(outshape) != dims:
        print("outshape must have the same dimensionality as the input array ("+str(dims)+"D)!", error=True)
    # create inarray coordinates list
    coords_list = []
    for dim in range(dims):
        coords_1d = get_coords(cmin=[0.0], cmax=[1.0], ndim=[inshape[dim]], cell_centred=True)
        coords_list.append(coords_1d)
    # create a clean array in case there are NaNs
    inarray_clean = np.copy(inarray)
    ind_bad = np.isnan(inarray)
    if np.any(ind_bad):
        print("NaN values encountered. Setting them to 0 as a workaround...", warn=True)
        inarray_clean[ind_bad] = 0.0
    # define interpolation function with scipy.interpolate.RegularGridInterpolator
    f = RegularGridInterpolator(np.array(coords_list), inarray_clean.astype('float'), method=method, bounds_error=False, fill_value=None)
    # define output coordinates
    coords_nd = get_coords(cmin=[0.0]*dims, cmax=[1.0]*dims, ndim=outshape, cell_centred=True)
    ret = f(coords_nd.T).T # evaluate f at output coordindates
    return ret
# === END congrid ===

# ===== the following applies in case we are running this in script mode =====
if __name__ == "__main__":
    stop()
