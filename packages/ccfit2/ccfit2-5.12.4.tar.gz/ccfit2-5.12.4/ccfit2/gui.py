'''
            ccfit2

        Copyright (C) 2024

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

This module contains gui helper functions
'''
# Import shim for qt
import qtpy # noqa
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from matplotlib.colorbar import Colorbar
import matplotlib.colors as mpl_col
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import matplotlib.gridspec as gridspec
from matplotlib.ticker import NullFormatter, FormatStrFormatter, LogLocator, \
                              SymmetricalLogLocator, FuncFormatter # noqa

import numpy as np
import numpy.typing as npt

import pyqtgraph as pg

# Default values for interactive parameter widgets of relaxation.FitWindow
widget_defaults = {
    'Orbach': {
        'u_eff': {
            'min': 0.,
            'max': 3000.,
            'valinit': 1500.,
            'step': 1,
            'decimals': 2
        },
        'A': {
            'min': -30.,
            'max': 30.,
            'valinit': -11.,
            'step': 0.01,
            'decimals': 3
        }
    },
    'Raman': {
        'R': {
            'min': -60.,
            'max': 60.,
            'valinit': -6.,
            'step': 0.01,
            'decimals': 3
        },
        'n': {
            'min': 0,
            'max': 30.,
            'valinit': 3.,
            'step': 0.01,
            'decimals': 3
        }
    },
    'PPDRaman': {
        'w': {
            'min': 0.,
            'max': 3000.,
            'valinit': 10.,
            'step': 1,
            'decimals': 3
        },
        'R': {
            'min': -60.,
            'max': 60.,
            'valinit': 4,
            'step': 0.01,
            'decimals': 3
        },
    },
    'FTD-PPDRaman-I': {
        'w': {
            'min': 0.,
            'max': 3000.,
            'valinit': 10.,
            'step': 1,
            'decimals': 3
        },
        'R': {
            'min': -60.,
            'max': 60.,
            'valinit': 4.,
            'step': 0.01,
            'decimals': 3
        },
    },
    'QTM': {
        'Q': {
            'min': -6.,
            'max': 6.,
            'valinit': 1.,
            'step': 0.01,
            'decimals': 4
        }
    },
    'Direct': {
        'D': {
            'min': -6.,
            'max': 6.,
            'valinit': -2,
            'step': 0.01,
            'decimals': 4
        }
    },
    'FD-QTM': {
        'Q': {
            'min': -30.,
            'max': 30.,
            'valinit': 1,
            'step': 0.01,
            'decimals': 4
        },
        'Q_H': {
            'min': -30.,
            'max': 30.,
            'valinit': -8,
            'step': 0.01,
            'decimals': 4
        },
        'p': {
            'min': -30.,
            'max': 30.,
            'valinit': 2,
            'step': 0.01,
            'decimals': 4
        }
    },
    'Raman-II': {
        'C': {
            'min': -30.,
            'max': 30.,
            'valinit': -14,
            'step': 0.01,
            'decimals': 4
        },
        'm': {
            'min': -30.,
            'max': 30.,
            'valinit': 4,
            'step': 0.01,
            'decimals': 4
        }
    },
    'Constant': {
        'Ct': {
            'min': -30.,
            'max': 10.,
            'valinit': -4,
            'step': 0.01,
            'decimals': 4
        }
    },
    'Brons-Van-Vleck * Raman-II': {
        'e': {
            'min': -30.,
            'max': 30.,
            'valinit': -5,
            'step': 0.01,
            'decimals': 4
        },
        'f': {
            'min': -30.,
            'max': 30.,
            'valinit': -5,
            'step': 0.01,
            'decimals': 4
        },
        'C': {
            'min': -30.,
            'max': 30.,
            'valinit': -4,
            'step': 0.01,
            'decimals': 4
        },
        'm': {
            'min': -30.,
            'max': 30.,
            'valinit': 4,
            'step': 0.01,
            'decimals': 4
        },
    },
    'Brons-Van-Vleck * Constant': {
        'e': {
            'min': -30.,
            'max': 30.,
            'valinit': -5,
            'step': 0.01,
            'decimals': 4
        },
        'f': {
            'min': -30.,
            'max': 30.,
            'valinit': -5,
            'step': 0.01,
            'decimals': 4
        },
        'Ct': {
            'min': -30.,
            'max': 30.,
            'valinit': -4,
            'step': 0.01,
            'decimals': 4
        }
    }
}


def min_max_ticks_with_zero(values: list[float],
                            nticks: int) -> tuple[list[float], float]:
    '''
    Calculates tick positions including zero given a specified number of
    ticks either size of zero

    Parameters
    ----------
    values: list[float]
        Values plotted on this axis e.g. y-values or x-values
    n_ticks: int
        Number of ticks to produce either side of zero.
        i.e. total number of ticks is 2*n_ticks + 1

    Returns
    -------
    list[float]
        Tick positions
    float
        Maximum tick value
    '''

    # Extra tick for zero
    nticks += 1

    lowticks = np.linspace(-np.max(np.abs(values)), 0, nticks)
    highticks = np.linspace(np.max(np.abs(values)), 0, nticks)
    ticks = np.append(np.append(lowticks[:-1], [0.0]), np.flip(highticks[:-1]))

    return ticks, np.max(np.abs(values))


def calc_y_rate_lims(rates: list[float],
                     rate_err: list[float] = []) -> tuple[float, float]:
    '''
    Defines rate plot y limits as 10^integer

    Parameters
    ----------
    rates: list[float]
        Relaxation rates in s^-1
    rate_err: list[float], default []
        Error on rate, upper then lower\n
        Shape (n_rates, 2)

    Returns
    -------
    float
        Upper tick position
    float
        Lower tick position
    '''
    # Define limits of y axis
    # Upper limit from rounding up to nearest power of 10
    # Lower from rounding down to nearest power of 10

    if isinstance(rate_err, list):
        rate_err = np.asarray(rate_err)

    if not len(rate_err):
        rate_err = np.zeros([2, len(rates)])
    y_lower = 10**np.floor(
        np.log10(
            np.nanmin(
                [rates, rates + rate_err[1, :], rates - rate_err[0, :]]
            )
        )
    )
    y_upper = 10**np.ceil(
        np.log10(
            np.nanmax(
                [rates, rates + rate_err[1, :], rates - rate_err[0, :]]
            )
        )
    )

    if np.isnan(y_lower):
        y_lower = y_upper / 10
    if np.isnan(y_upper):
        y_upper = y_lower / 10

    return y_lower, y_upper


def calc_linthresh(x_vals: npt.ArrayLike) -> float:
    '''
    Calculates linthresh for symlog scale using field values.
    Valid only for rate/time versus field plots

    Parameters
    ----------
    x_vals: array_like
        Field values in Oe

    Returns
    -------
    float
        linthresh for symlog scale
    '''

    x_vals = np.asarray(x_vals)

    # Using first value greater than machine eps calculate new threshold
    it = np.argmin(x_vals[np.where(x_vals > np.finfo(float).eps)])
    linthresh = 10**np.floor(
        np.log10(x_vals[np.where(x_vals > np.finfo(float).eps)][it])
    )

    return linthresh


def calc_linscale(x_vals: npt.ArrayLike) -> float:
    '''
    Calculates how much space the linear region takes up on the symlog axis
    Defined here as reciprocal of number of decades spanned by data + 1
    where the +1 accounts for the zero point itself, considered as its own
    decade

    Parameters
    ----------
    x_vals: array_like[float]
        X values

    Returns
    -------
    float
        Width of linear region
    '''

    nz_x_vals = np.log10(x_vals[np.nonzero(x_vals)])
    decs = [np.floor(val) for val in nz_x_vals]

    n_dec = np.max(decs) - np.min(decs) + 1

    return 1 / n_dec


def format_rate_x_y_axes(ax: plt.Axes, rates: list[float],
                         x_vals: list[float],
                         rate_err: list[float] = [],
                         x_type: str = 'temperature') -> None:
    '''
    Wrapper for calc_y_rate_lims and set_rate_xtick_formatting
    Formats both axes of a rate vs T or H plot

    Parameters
    ----------
    ax: plt.Axes
        Axis to modify
    rates: list[float]
        Relaxation rates in s^-1
    x_vals: list[float]
        x values of plot (T or H)
    rate_err: list[float], default []
        Error on rates, upper then lower one per rate.\n
        Shape (n_rates, 2)
    x_type: str, {'field', 'temperature'}
        Type of data, temperature (T) or field (H)

    Returns
    -------
    None
    '''

    y_lower, y_upper = calc_y_rate_lims(rates, rate_err)

    ax.set_ylim([y_lower, y_upper])

    set_rate_xtick_formatting(ax, x_vals, x_type=x_type)

    ax.yaxis.set_minor_locator(LogLocator(base=10, subs='auto'))

    return


def set_rate_xtick_formatting(ax: plt.Axes, x_vals: list[float],
                              x_type: str = 'temperature') -> None:
    '''
    Sets x-tick formatting for rate plot. Enables minor tick labels if <1.1
    order of magnitude spanned by ticks

    Parameters
    ----------
    ax: plt.Axes
        Axis to modify
    x_vals: list[float]
        x values of plot (T or H)
    x_type: str, {'field', 'temperature'}
        Type of data, temperature (T) or field (H)

    Returns
    -------
    None
    '''

    if x_type == 'field':

        # Major ticks
        # Let matplotlib decide decimal values, but stop it
        # converting them to 10^val notation
        ax.xaxis.set_major_formatter(
            FuncFormatter(lambda y, _: '{:g}'.format(y))
        )
        # Disable minor tick labels
        ax.xaxis.set_minor_formatter(NullFormatter())
        # and set minor tick locations
        ax.xaxis.set_minor_locator(
            SymmetricalLogLocator(
                base=10,
                subs=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                linthresh=calc_linthresh(x_vals)
            )
        )
    elif x_type == 'temperature':
        x_vals = np.log10(x_vals)
        # Major ticks
        ax.xaxis.set_major_formatter(FormatStrFormatter('%.0f'))
        # Minor ticks
        if np.max(x_vals) - np.min(x_vals) > 1.05:
            # No minor ticks if > 1 and a bit decades spanned by temperature
            ax.xaxis.set_minor_formatter(NullFormatter())
        else:
            # Add minor tick labels when range is small
            # i.e. only just crosses a decade
            # and make tick lengths equal to major ticks
            ax.xaxis.set_minor_formatter(FormatStrFormatter('%.0f'))
            ax.tick_params('x', length=3.5, width=1, which='major')
            ax.tick_params('x', length=3.5, width=1, which='minor')

    return


def convert_log_ticks_to_lin(ax: pg.graphicsItems.AxisItem.AxisItem,
                             logx_vals: list[float],
                             shift: float = 0.) -> None:
    '''
    Converts logarithmic tick values to linear and adds to pyqtgraph axis

    Shift kwarg applies a shift to the ticks, and is neccessary when the data
    has been shifted to accommodate a x_value of 0 (e.g. Field = 0)

    Parameters
    ----------
    ax: pg.graphicsItems.AxisItem.AxisItem
        Axis to modify
    logx_vals: list[float]
        x values in logspace
    shift: float, default 0.
        Shift to apply tp ticks

    Returns
    -------
    None
    '''

    # Determine size of this item in pixels
    bounds = ax.mapRectFromParent(ax.geometry())
    span = (bounds.topLeft(), bounds.topRight())
    points = list(map(ax.mapToDevice, span))

    lengthInPixels = pg.Point(points[1] - points[0]).length()
    if lengthInPixels == 0:
        return

    # Determine major / minor / subminor axis ticks
    tick_tuple = ax.tickValues(ax.range[0], ax.range[1], lengthInPixels)

    minor_ticks = []
    intermediate_ticks = []

    if len(tick_tuple) >= 1:
        major_tick_vals = tick_tuple[0][1]
        major_ticks = [
            (level + shift, '{:.0f}'.format(10**level))
            for level in major_tick_vals
        ]

    if len(tick_tuple) >= 2:
        minor_tick_vals = tick_tuple[-1][1]

        if np.max(logx_vals) - np.min(logx_vals) < 1.1:
            minor_ticks = [
                (level + shift, '{:.0f}'.format(10**level))
                for level in minor_tick_vals
            ]
        else:
            minor_ticks = [
                (level + shift, '')
                for level in minor_tick_vals
            ]

    if len(tick_tuple) >= 3:
        inter_tick_vals = tick_tuple[1][1]
        intermediate_ticks = [
            (level + shift, '{:.0f}'.format(10**level))
            for level in inter_tick_vals
        ]

    # Add 0 tick at zero if zero value is present in log10(x_vals)
    if any(val == 0 for val in logx_vals):
        # but not if a tick is already at zero
        if not any(val[0] == 0. for val in major_ticks):
            major_ticks.append((0., '0'))

    ax.setTicks([major_ticks, intermediate_ticks, minor_ticks])

    return


def create_ac_temp_colorbar(ax: plt.Axes, fig: plt.Figure,
                            vals: list[float],
                            colors: mpl_col.Colormap,
                            x_var: str = 'T') -> Colorbar:
    '''
    Creates colorbar for temperatures in AC plotting

    Parameters
    ----------

    ax: plt.Axes
        Axis to which colorbar is added
    fig: plt.Figure
        Figure to which colorbar is added
    vals: list[float]
        Temperatures in Kelvin or Fields in Oersted
    colors: matplotlib.colors.Colormap
        Colormap used in plot
    x_var: str, default 'T'.
        Independent variable that relaxation time is being measured over,
        temperature or field. Raises an error if T or H not selected.
    Returns
    -------
    matplotlib.colorbar.Colorbar
        Matplotlib colorbar object

    Raises
    ------
    ValueError
        If no temperatures specified
    ValueError
        If x_var is not T or H
    '''

    n_vals = len(vals)

    if n_vals == 0:
        raise ValueError('Cannot create colorbar for zero temperatures')

    # Make colourbar
    # Indexing starts at zero and ends at num_temps
    norm = mpl_col.BoundaryNorm(
        np.arange(0, n_vals + 1),
        ncolors=colors.N
    )

    # Scalar mappable converts colourmap numbers into an image of colours
    sm = cm.ScalarMappable(cmap=colors, norm=norm)

    colorbar_ticks = np.arange(1, n_vals + 1) - 0.5
    colorbar_labels = get_temp_colourbar_ticks(vals=vals)

    cbar = fig.colorbar(
        sm,
        ticks=colorbar_ticks,
        orientation='horizontal',
        format='%.1f',
        cax=ax
    )

    ax.set_xticklabels(
        colorbar_labels,
        rotation=0,
        fontsize='smaller'
    )

    ax.minorticks_off()

    if x_var == 'T':
        title = 'T (K)'
    elif x_var == 'H':
        title = 'H (Oe)'
    else:
        raise ValueError('Error: T or H not selected for --x_var')

    # Set colourbar label - technically title - above bar
    cbar.ax.set_title(title, fontsize='smaller')

    return cbar


def get_temp_colourbar_ticks(vals: list[float],) -> list[float]:
    '''
    Creates ticks for a temperature/field colourbar.

    If there are fewer than 9 data points, give tick to all temperatures/fields

    If there are between 9 and 17, slice every 3 or 4 points depending on
    even-odd.

    If there are more than 17, slice every 5 or 6 points depending on
    even-odd.

    Parameters
    ----------
    vals: list[float]
        Temperatures in Kelvin or Fields in Oersted

    Returns
    -------
    list[float]
        Colourbar tick positions
    '''

    n_vals = len(vals)

    ticks = ['{:.1f}'.format(tp) for tp in vals]

    if n_vals <= 8:
        step = 1
    elif 9 <= n_vals <= 17:
        if n_vals % 2 == 0:
            step = 3
        else:
            step = 4
    else:
        if n_vals % 2 == 0:
            step = n_vals // 5
        else:
            step = n_vals // 4

    # Swap numbers for blanks, and ensure start and end are present
    ticks = [ti if not it % step else '' for (it, ti) in enumerate(ticks)]
    ticks[0] = '{:.1f}'.format(vals[0])
    ticks[-1] = '{:.1f}'.format(vals[-1])

    # Remove adjacent labels at end
    if n_vals > 8 and ticks[-2] != '':
        ticks[-2] = ''

    return ticks


class SusceptibilityCanvas(FigureCanvasQTAgg):
    '''
    Figure and axes for AC Susceptibility plots
    '''

    def __init__(self, width, height, dpi=100, parent=None):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.gs = gridspec.GridSpec(3, 1, height_ratios=[0.05, 1, 1])
        self.ax = [
            self.fig.add_subplot(self.gs[0]),
            self.fig.add_subplot(self.gs[1]),
            self.fig.add_subplot(self.gs[2])
        ]
        super(SusceptibilityCanvas, self).__init__(self.fig)


class ColeColeCanvas(FigureCanvasQTAgg):
    '''
    Figure and axes for AC Cole-Cole plots
    '''

    def __init__(self, width, height, dpi=100, parent=None):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.gs = gridspec.GridSpec(2, 1, height_ratios=[0.03, 0.9])
        self.ax = [
            self.fig.add_subplot(self.gs[0]),
            self.fig.add_subplot(self.gs[1])
        ]
        super(ColeColeCanvas, self).__init__(self.fig)
