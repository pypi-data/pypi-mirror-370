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

This script contains a program to split rate (ac and dc *_params.csv) files
'''

import argparse
import ccfit2.relaxation as rx
import ccfit2.gui as gui
import ccfit2.utils as ut
import pandas as pd
import numpy as np
import copy
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import os


def plot_rates(dataset: rx.TDataset | rx.HDataset) -> tuple[plt.Figure, plt.Axes]: # noqa
    '''
    Plots experimental relaxation rate vs field/temperature and
    displays on screen.

    Parameters
    ----------
    dataset: TDataset | HDataset
        Dataset to plot

    Returns
    -------
    plt.Figure
        Matplotlib figure object
    plt.Axes
        Matplotlib axis object

    Raises
    ------
    ValueError
        If dataset type is not HDataset or TDataset
    '''

    # Create figure and axes
    fig, ax = plt.subplots(
        1,
        1,
        figsize=(6, 6.5),
        num='Relaxation profile'
    )

    if isinstance(dataset, rx.HDataset):
        ax.set_xlabel(r'Field (Oe)')
    elif isinstance(dataset, rx.TDataset):
        ax.set_xlabel(r'Temperature (K)')
    else:
        raise ValueError('Dataset Type is Unsupported')

    # Add uncertainties as errorbars
    if len(dataset.rate_pm):
        it = 0
        for dv, ra, rpm in zip(dataset.dep_vars, dataset.rates, dataset.rate_pm.T): # noqa
            ax.errorbar(
                dv,
                ra,
                yerr=[[rpm[0]], [rpm[1]]],
                marker='o',
                lw=0,
                elinewidth=1.5,
                fillstyle='none',
                color='black',
                picker=True
            )
            it += 1
    else:
        for dv, ra in zip(dataset.dep_vars, dataset.rates):
            ax.plot(
                dv,
                ra,
                marker='o',
                lw=0,
                fillstyle='none',
                color='black',
                picker=True
            )

    if dataset.IDEP_VAR_NAMES[0] == 'Field':
        if any(val < np.finfo(float).eps for val in dataset.dep_vars):
            ax.set_xscale(
                'symlog',
                linthresh=gui.calc_linthresh(dataset.dep_vars),
                linscale=gui.calc_linscale(dataset.dep_vars)
            )
        else:
            ax.set_xscale('log')
    else:
        ax.set_xscale('log')
    ax.set_yscale('log')

    ax.set_ylabel(r'Rate (s$^\mathregular{-1}$)')

    if len(dataset.lograte_pm):
        all_data = [
            np.log10(dataset.rates) + dataset.lograte_pm
        ]
        all_data += [
            np.log10(dataset.rates) - dataset.lograte_pm
        ]
    else:
        all_data = [
            np.log10(dataset.rates)
        ]
        all_data += [
            np.log10(dataset.rates)
        ]

    gui.format_rate_x_y_axes(
        ax,
        dataset.rates,
        dataset.dep_vars,
        np.abs(dataset.rate_pm),
        x_type=dataset.IDEP_VAR_NAMES[0].lower()
    )

    # Set x tick formatting
    gui.set_rate_xtick_formatting(
        ax,
        dataset.dep_vars,
        x_type=dataset.IDEP_VAR_NAMES[0].lower()
    )

    return fig, ax


def main():
    parser = argparse.ArgumentParser(
        description=(
            'This script allows you to interactively split a ccfit2'
            '_params.csv file containing a two-tau AC or DC model into '
            'two _params.csv files'
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        'file_name',
        type=str,
        help='ccfit2 params.csv file from AC or DC'
    )

    parser.add_argument(
        '--x_var',
        type=str,
        help='Independent variable T or H',
        choices=['T', 'H'],
        default='T'
    )

    uargs = parser.parse_args()

    # Load data as pandas df
    data = pd.read_csv(
        uargs.file_name,
        comment='#',
        skipinitialspace=True,
        delimiter=','
    )

    # Combine data into a single set of tau values

    data_1 = copy.copy(data)
    data_1.drop(
        columns=[
            '<ln(tau2)> (ln(s))',
            'sigma_ln(tau2) (ln(s))',
            'fit_upper_ln(tau2) (ln(s))',
            'fit_lower_ln(tau2) (ln(s))'
        ],
        inplace=True
    )
    data_1.rename(
        columns={
            '<ln(tau1)> (ln(s))': '<ln(tau)> (ln(s))',
            'sigma_ln(tau1) (ln(s))': 'sigma_ln(tau) (ln(s))',
            'fit_upper_ln(tau1) (ln(s))': 'fit_upper_ln(tau) (ln(s))',
            'fit_lower_ln(tau1) (ln(s))': 'fit_lower_ln(tau) (ln(s))'
        },
        inplace=True
    )
    data_2 = copy.copy(data)
    data_2.rename(
        columns={
            '<ln(tau2)> (ln(s))': '<ln(tau)> (ln(s))',
            'sigma_ln(tau2) (ln(s))': 'sigma_ln(tau) (ln(s))',
            'fit_upper_ln(tau2) (ln(s))': 'fit_upper_ln(tau) (ln(s))',
            'fit_lower_ln(tau2) (ln(s))': 'fit_lower_ln(tau) (ln(s))'
        },
        inplace=True
    )
    data_2.drop(
        columns=[
            '<ln(tau1)> (ln(s))',
            'sigma_ln(tau1) (ln(s))',
            'fit_upper_ln(tau1) (ln(s))',
            'fit_lower_ln(tau1) (ln(s))'
        ],
        inplace=True
    )

    keep = [
        'T (K)',
        'H (Oe)',
        '<ln(tau)> (ln(s))',
        'sigma_ln(tau) (ln(s))',
        'fit_upper_ln(tau) (ln(s))',
        'fit_lower_ln(tau) (ln(s))'
    ]
    data_1 = data_1[keep]
    data_2 = data_2[keep]
    final = pd.concat(
        [data_1, data_2],
        ignore_index=True
    ).sort_values('T (K)').reset_index(drop=True)

    if uargs.x_var == 'T':
        # Create relaxation dataset object
        data = rx.TDataset.from_raw(
            final['T (K)'],
            final['<ln(tau)> (ln(s))'],
            final['sigma_ln(tau) (ln(s))'],
            final['fit_upper_ln(tau) (ln(s))'],
            final['fit_lower_ln(tau) (ln(s))']
        )
    elif uargs.x_var == 'H':
        # Create relaxation dataset object
        data = rx.HDataset.from_raw(
            final['H (Oe)'],
            final['<ln(tau)> (ln(s))'],
            final['sigma_ln(tau) (ln(s))'],
            final['fit_upper_ln(tau) (ln(s))'],
            final['fit_lower_ln(tau) (ln(s))']
        )

    # Plot datapoints, each as its own line
    fig, ax = plot_rates(data)

    # add label to each line
    for it, line in enumerate(ax.lines):
        line._label = it

    def onclick(event, store):
        '''
        Callback for mouse click.
        If a point is clicked, then update the group
        '''

        if isinstance(event.artist, Line2D):
            store[int(event.artist.get_label())].switch(event.artist)

        plt.draw()

        return

    store = [Toggle(it) for it in range(len(final['T (K)']))]

    # Connect mouse click to callback
    fig.canvas.mpl_connect(
        'pick_event',
        lambda event: onclick(event, store)
    )
    suptitle = 'Click points to change markers and assign to group'
    suptitle += '\n Circle = Group 1'
    suptitle += '\n Cross = Group 2'
    suptitle += '\n Square = Groups 1 & 2'
    plt.suptitle(suptitle, fontsize=11)
    fig.subplots_adjust(hspace=0.08, wspace=.08)

    plt.show()

    # Create new csv files for each group of points
    one_indices = [st.index for st in store if st.group in [0, 2]]
    two_indices = [st.index for st in store if st.group in [1, 2]]

    _head = os.path.splitext(uargs.file_name)[0]

    final.loc[one_indices].to_csv(
        f'{_head}_1.csv',
        index=False,
        float_format='%.18e',
    )
    final.loc[two_indices].to_csv(
        f'{_head}_2.csv',
        index=False,
        float_format='%.18e',
    )
    ut.cprint(
        f'ccfit2 parameter .csv files written to \n{_head}_1.csv\n{_head}_2.csv', # noqa
        'blue'
    )


class Toggle():
    '''
    Helper class for interactive_t_select
    '''

    def __init__(self, index):

        self.group = 0
        self.index = index

    def switch(self, artist):

        self.group += 1
        if self.group > 2:
            self.group = 0

        if self.group == 0:
            artist.set_marker('o')
        elif self.group == 1:
            artist.set_marker('x')
        else:
            artist.set_marker('s')

        plt.draw()

        return
