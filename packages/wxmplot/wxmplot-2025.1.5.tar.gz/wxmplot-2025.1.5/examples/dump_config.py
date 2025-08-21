#!/usr/bin/python
import numpy as np
import wxmplot.interactive as wi
import json

x = np.linspace(0.0, 20.0, 201)
disp = wi.plot(x, np.sin(x)/(x+1), ylabel='response',  xlabel='T (sec)')
cnf = disp.panel.conf

print("Line 1 ", cnf.get_mpline(0))


out = cnf.get_config()

#
#
# for attr in ('added_texts', 'auto_margins', 'axes_style',
#              'data_deriv', 'data_expr', 'draggable_legend', 'facecolor',
#              'framecolor', 'gridcolor', 'hidewith_legend', 'legend_loc',
#              'legend_onaxis', 'linecolors', 'margins', 'mpl_legend', 'ntrace',
#              'plot_type', 'scatter_mask', 'scatter_normalcolor',
#              'scatter_normaledge', 'scatter_selectcolor', 'scatter_selectedge',
#              'scatter_size', 'show_grid', 'show_legend', 'show_legend_frame',
#              'textcolor', 'title', 'viewpad', 'with_data_process',
#              'xlabel', 'xscale', 'y2label', 'ylabel', 'yscale', 'zoom_lims',
#              'zoom_style'):
#
#     out[attr] = getattr(cnf, attr)
#
# ntrace = int(out['ntrace'])
#
# for attr in ('fills', 'traces'):
#     val = getattr(cnf, attr)
#     if attr == 'traces':
#          val = cnf.get_traces()
#     out[attr] = val[:ntrace+1]
#
#

conf = {'axes_style': 'open',
        'xlabel': 'New X',
        'traces': [{'color': '#440044', 'style': 'solid',
                    'linewidth': 3.5, 'zorder': 5, 'fill': False,
                    'label': 'x111', 'drawstyle': 'default', 'alpha': 1,
                    'markersize': 5, 'marker': '+', 'markercolor': 'black'}]}


cnf.load_config(conf)
disp.panel.canvas.draw()
