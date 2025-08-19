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

This module contains functions and objects for working with waveform data
'''

from . import utils as ut
from . import dc
from . import ac

import numpy as np
import numpy.typing as npt
import matplotlib.pyplot as plt
from matplotlib.ticker import AutoMinorLocator, LogLocator
from math import isnan
from scipy import signal


#: Supported Waveform Headers - One of each MUST be found in the input file.
#:
#:  Note - These differ between magnetometers\
#:
#:  These keys are the arguments to the Measurement constructor, but their
#:  order does not matter
HEADERS_SUPPORTED: dict[str, list[str]] = {
    'dc_field': [
        'Magnetic Field (Oe)',
        'Field (Oe)'
    ],
    'temperature': [
        'Temperature (K)'
    ],
    'time': [
        'Time Stamp (sec)'
    ],
    'moment': [
        'Moment (emu)',
    ],
    'moment_err': [
        'M. Std. Err. (emu)',
    ]
}

# Generic dc magnetometer file header names
HEADERS_GENERIC = list(HEADERS_SUPPORTED.keys())


class Measurement(dc.Measurement):
    '''
    Stores data for a single Waveform measurement at a
    given temperature and applied field

    Parameters
    ----------
    dc_field : float
        Applied dc field (Oe)
    temperature : float
        Temperature of datapoint (K)
    moment : float
        Magnetisation of datapoint (emu)
    time : float
        Time of datapoint (s)

    Attributes
    ----------
    dc_field : float
        Applied dc field (Oe)
    temperature : float
        Temperature of datapoint (K)
    moment : float
        Magnetic moment of datapoint (emu)
    time : float
        Time of datapoint (s)
    rep_temperature : float
        Representative temperature assigned to this datapoint (K)
    rep_dc_field : float
        Representative dc field assigned to this datapoint (Oe)
    '''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @classmethod
    def from_file(cls, file: str,
                  data_header: str = '[Data]',
                  verbose: bool = True,
                  encoding: str = 'find') -> list['Measurement']:
        '''
        Extracts waveform data from magnetometer output file and
        returns list of datapoints, one for each valid measurement
        Incomplete lines are ignored

        Parameters
        ----------
        file : str
            Name of magnetometer output file
        data_header : str default '[Data]'
            Contents of line which specifies the beginning of the data block
            in input file default is to find line containing '[Data]'
        verbose: bool, default True
            If True, issues parsing measurements are written to terminal
        encoding: str, default 'find'
            Encoding to use when opening file

        Returns
        -------
        list
            Measurement objects, each specifying a single datapoint
            List has the same order as the magnetometer file
        '''

        # Find encoding of input file
        if encoding == 'find':
            encoding = ut.detect_encoding(file)

        data_index, header_indices, _ = ut.parse_mag_file(
            file,
            header_dict=HEADERS_SUPPORTED,
            data_header=data_header,
            encoding=encoding
        )

        # Columns to extract from file
        cols = {
            gen: header_indices[gen] for gen in HEADERS_GENERIC
        }

        # Convert strings to floats, if not possible then mark as NaN
        converters = {
            it: lambda s: (float(s.strip() or np.nan)) for it in cols.values()
        }

        # Read required columns of file
        data = np.loadtxt(
            file,
            skiprows=data_index + 1,
            delimiter=',',
            converters=converters,
            usecols=cols.values(),
            encoding=encoding
        )

        # Remove missing entries that have been marked as nan
        data = [
            row for row in data
            if not any(isnan(val) for val in row)
        ]

        # Keep moments smaller than their error (remove noisy data)
        # and keep only the field values which fall outside window
        mom_col = list(cols.keys()).index('moment')
        err_col = list(cols.keys()).index('moment_err')

        data = np.array([
            np.delete(row, err_col) for row in data
            if row[err_col] / row[mom_col] <= 0.3
        ])

        # Convert array of floats into list of Measurement objects, one per
        # line
        # Remove positional nature of Measurement constructor args by using
        # kwargs through dict
        measurements = [
            cls(**{
                col: val
                for col, val in zip(cols, row)
            })
            for row in data
            if not any(isnan(val) for val in row)
        ]

        if not len(measurements) and verbose:
            _msg = '\n Error: Cannot parse measurements from file {}'.format(
                file
            )
            ut.cprint(_msg, 'red')

        return measurements


class Experiment(dc.Experiment):
    '''
    Stores data for multiple waveform measurements at a
    given temperature and oscillating dc field frequency

    Parameters
    ----------
    rep_temperature: float
        Representative temperature of experiment (K) e.g. mean
    rep_dc_field : float
        Representative dc field assigned to this experiment (Oe)
    raw_temperatures: array_like
        Raw temperatures of experiment, one per measurement (K)
    times : array_like
        Time value, one per measurement (s)
    moments : array_like
        Measured moment, one value per measurement (emu)
    dc_fields : array_like
        Applied dc field in Oe, one value per measurement (Oe)

    Attributes
    ----------
    rep_temperature: float
        Representative temperature of experiment e.g. mean (K)
    raw_temperatures: ndarray of floats
        Raw temperatures of experiment, one per measurement (K)
    times : ndarray of floats
        Time value, one per measurement (s)
    moments : ndarray of floats
        Measured moment, one value per measurement (emu)
    dc_fields : ndarray of floats
        Applied dc field in Oe, one value per measurement (Oe)
    rep_dc_field : float
        Representative dc field assigned to this experiment (Oe)
    '''

    @classmethod
    def from_measurements(cls,
                          measurements: list[Measurement],
                          field_window: list[float] = [-1, 1],
                          temp_thresh: float = .1) -> list[list['Experiment']]:
        '''
        Creates list of Experiment objects from a list of individual
        Measurement objects. An experiment is defined as a set of measurements
        which have the same temperature and DC Field period.

        Parameters
        ----------
        measurement: list[Measurement]
            Measurements at various times but same temperatures and
            dc field period.
        field_window: list[float], default [-1, 1]
            Range of values at which DC Field is sampled to determine
            different DC field periods (Oe)
        temp_thresh: float, default 0.1 K
            Threshold used to discriminate between temperatures (K)

        Returns
        -------
        list[list[Experiment]]
            Experiments, first dimension is temperature, second dimension\n
            is time.
        '''

        # Sort measurements by temperature then time
        measurements = sorted(
            measurements,
            key=lambda k: (k.temperature, k.time)
        )

        # Find mean temperature values
        mean_temperatures, split_ind = ut.find_mean_values(
            [
                measurement.temperature
                for measurement in measurements
            ],
            thresh=temp_thresh
        )

        # Set each measurement's representative temperature, here the mean
        for mm, mt in zip(measurements, mean_temperatures):
            mm.rep_temperature = mt

        # Re-sort using mean temperatures
        measurements = sorted(
            measurements,
            key=lambda k: (k.rep_temperature, k.time)
        )

        # Split by mean temperature
        measurements: list[list[Measurement]] = np.split(
            measurements,
            split_ind
        )

        field_window = np.sort(field_window)

        exp = []

        # Clean up measurements and then
        # split into experiments based on dc field
        # oscillation frequency
        for mm in measurements:

            fields = np.array([
                m.dc_field
                for m in mm
            ])

            # Select points to keep
            # These fall outside of the field window
            # and are where the field remains constant relative
            # to the either the next point (forward in time)
            # or previous point (backwards in time)
            mask = np.where(
                (
                    (fields < field_window[0]) ^ (fields > field_window[1])
                ) * ut.alldiff(fields)
            )[0]

            times = np.array([
                m.time
                for m in mm
            ])[mask]

            moments = np.array([
                m.moment
                for m in mm
            ])[mask]

            temperatures = np.array([
                m.temperature
                for m in mm
            ])[mask]

            fields = fields[mask]

            # Now separate frequency blocks

            # Get indices of positive and negative field datapoints
            pvals = np.arange(len(times))[np.where(fields > field_window[1])]
            nvals = np.arange(len(times))[np.where(fields < field_window[0])]

            # Calculate difference in indices
            pvals_diff = np.diff(pvals, append=pvals[-1])
            nvals_diff = np.diff(nvals, append=nvals[-1])

            # Jumps in index number correspond to peak (positive) or
            # trough (negative)
            # Use peak finder to locate
            pos_pt_start_end = signal.find_peaks(
                pvals_diff
            )[0]

            neg_pt_start_end = signal.find_peaks(
                nvals_diff
            )[0]

            # Take difference in start and end indices of peaks/troughs
            # and delete differences < 10 since these are spurious
            # Assume a peak or trough will have >10 points at sat. field
            pval_peaks_diff = np.diff(
                pvals_diff[pos_pt_start_end],
                append=pvals_diff[pos_pt_start_end][-1]
            )
            pval_peaks_diff[np.where(pval_peaks_diff < 10)] = 0

            nval_peaks_diff = np.diff(
                nvals_diff[neg_pt_start_end],
                append=nvals_diff[neg_pt_start_end][-1]
            )
            nval_peaks_diff[np.where(nval_peaks_diff < 10)] = 0

            # Then find the peaks in the above difference
            # these peaks define the start and end of a frequency block
            pos_fb_start_end = signal.find_peaks(
                pval_peaks_diff
            )[0]

            neg_fb_start_end = signal.find_peaks(
                nval_peaks_diff
            )[0]

            # Generate list of start indices of the blocks
            # in the index scheme of the experimental data
            start_indices = np.arange(
                len(times)
            )[pvals][pos_pt_start_end + 1][pos_fb_start_end]
            # add on first datapoint index as start of first block
            start_indices = np.insert(start_indices, 0, 0)

            # Generate list of end indices of the blocks
            # in the index scheme of the experimental data
            end_indices = np.arange(
                len(times)
            )[nvals][neg_pt_start_end][neg_fb_start_end + 1]
            # add on last datapoint index as end of last block
            end_indices = np.insert(
                end_indices, len(end_indices), len(times) - 1
            )

            # Split this temperature's data at start and end indices
            # and generate experiments
            _exp = [
                cls(
                    mm[0].rep_temperature,
                    0.,
                    temperatures[start: end + 1],
                    times[start: end + 1] - times[start: end + 1][0],
                    moments[start: end + 1],
                    fields[start: end + 1]
                )
                for start, end in zip(start_indices, end_indices)
            ]
            # Append to list of experiments at all temperatures
            exp.append(_exp)

            debug = False
            if debug:
                fig, ax1 = plt.subplots(1, 1, sharex=True, sharey=True)
                ax1.plot(times, fields)
                ax1.plot(
                    times[pvals][pos_pt_start_end + 1],
                    fields[pvals][pos_pt_start_end + 1],
                    lw=0,
                    marker='x',
                    color='r'
                )
                ax1.plot(
                    times[start_indices],
                    fields[start_indices],
                    lw=0,
                    marker='o', color='g', markersize=10)

                ax1.plot(
                    times[nvals][neg_pt_start_end],
                    fields[nvals][neg_pt_start_end],
                    lw=0,
                    marker='x',
                    color='r'
                )
                ax1.plot(
                    times[end_indices],
                    fields[end_indices],
                    lw=0,
                    marker='o',
                    color='g',
                    markersize=10
                )
                plt.show()

        return exp

    @classmethod
    def from_files(cls, file_names: list[str],
                   data_header: str = '[Data]',
                   field_window: list[float] = [-1, 1],
                   temp_thresh: float = .1) -> list[list['Experiment']]:
        '''
        Creates list of Experiment objects from a list of files\n
        Assumes each file contains 1 and only 1 DC field frequency.\n
        An experiment is defined as a set of datapoints\n
        which have the same temperature and DC Field period.

        Parameters
        ----------
        file_names: list[str]
            Files from which data is loaded.\n
            ASSUMES 1 DC Frequency per file!
        data_header: str, default '[Data]'
            Contents of line which specifies the beginning of the data block
            in input file.\n
            Default is to find line containing '[Data]'
        field_window: list[float], default [-1, 1]
            Range of values at which DC Field is sampled to determine
            different DC field periods (Oe)
        temp_thresh: float, default 0.1 K
            Threshold used to discriminate between temperatures (K)

        Returns
        -------
        list[list[Experiment]]
            Experiments, first dimension is temperature, second dimension\n
            is time.
        '''

        exp: list['Experiment'] = []

        if isinstance(file_names, str):
            file_names = [file_names]

        for file_name in file_names:

            _measurements = Measurement.from_file(
                file_name,
                data_header=data_header
            )

            # Sort measurements by temperature then time
            _measurements = sorted(
                _measurements,
                key=lambda k: (k.temperature, k.time)
            )

            # Find mean temperature values
            mean_temperatures, split_ind = ut.find_mean_values(
                [
                    mm.temperature
                    for mm in _measurements
                ],
                thresh=temp_thresh
            )

            # Set each measurement's representative temperature, here the mean
            for mm, mt in zip(_measurements, mean_temperatures):
                mm.rep_temperature = mt

            # Re-sort using mean temperatures
            _measurements = sorted(
                _measurements,
                key=lambda k: (k.rep_temperature, k.time)
            )

            # Split by mean temperature
            _measurements: list[list[Measurement]] = np.split(
                _measurements,
                split_ind
            )

            field_window = np.sort(field_window)

            # Clean up measurements and then
            # split into experiments based on dc field
            # oscillation frequency
            for mm in _measurements:

                fields = np.array([
                    m.dc_field
                    for m in mm
                ])

                # Select points to keep
                # These fall outside of the field window
                # and are where the field remains constant relative
                # to the either the next point (forward in time)
                # or previous point (backwards in time)
                mask = np.where(
                    (
                        (fields < field_window[0]) ^ (fields > field_window[1])
                    ) * ut.alldiff(fields)
                )[0]

                times = np.array([
                    m.time
                    for m in mm
                ])[mask]

                moments = np.array([
                    m.moment
                    for m in mm
                ])[mask]

                temperatures = np.array([
                    m.temperature
                    for m in mm
                ])[mask]

                fields = fields[mask]

                # Append to list of experiments at all temperatures
                exp.append(
                    cls(
                        mm[0].rep_temperature,
                        0.,
                        temperatures,
                        times - times[0],
                        moments,
                        fields
                    )
                )

        if len(exp) > 1:

            # Sort by temperature
            exp = sorted(
                exp,
                key=lambda k: k.rep_temperature
            )

            # Find mean temperature values
            _, split_ind = ut.find_mean_values(
                [
                    e.rep_temperature
                    for e in exp
                ],
                thresh=temp_thresh
            )

            # and split into sublists grouped by mean temperature
            exp: list[list[Experiment]] = np.split(
                exp,
                split_ind
            )
            exp = [
                ex.tolist()
                for ex in exp
            ]
        else:
            exp = [exp]

        return exp


class FTExperiment():

    '''
    Contains result of Fourier Transforming an Experiment.

    Parameters
    ----------
    ft_fields: array_like
        Fourier Transform of DC Fields
    ft_moments: array_like
        Fourier Transform of Magnetic Moments
    ft_freqs: array_like
        Frequencies associated with above fourier transformation
    temperature: float
        Temperature associated with this Experiment
    period: float
        Period associated with the oscillating DC field

    Attributes
    ----------
    ft_fields: ndarray of floats
        Fourier Transform of DC Fields, ordered by low to high frequency
    ft_moments: ndarray of floats
        Fourier Transform of Magnetic Moments, ordered by low to high
        frequency
    ft_freqs: ndarray of floats
        Frequencies associated with above fourier transformation, ordered
        low to high
    temperature: float
        Temperature associated with this Experiment
    period: float
        Period associated with the oscillating DC field
    '''

    def __init__(self, ft_fields: npt.NDArray, ft_moments: npt.NDArray,
                 ft_freqs: npt.NDArray, temperature: float,
                 period: float) -> None:

        order = np.argsort(ft_freqs)

        self.ft_fields = np.asarray(ft_fields)[order]
        self.ft_moments = np.asarray(ft_moments)[order]
        self.ft_freqs = np.asarray(ft_freqs)[order]
        self.temperature = temperature
        self.period = period

        pass

    @classmethod
    def from_experiment(cls, experiment: Experiment) -> 'FTExperiment':
        '''
        Fourier Transforms waveform Experiment to give FTExperiment object
        containing fourier transform data

        Parameters
        ----------
        experiment: Experiment
            Waveform Experiment object which will be fourier transformed

        Returns
        -------
        FTExperiment
            FTExperiment object containing fft data
        '''

        # Calculate the sample spacing (inverse of sampling rate).
        # Sampling rate is defined as npoints/measurement_time.
        spacing = experiment.times[-1] / len(experiment.times)

        # Retreive the associated frequencies.
        ft_freqs = np.fft.fftfreq(len(experiment.times), d=spacing)

        # Calculate the Fourier transform of field and moment
        ft_fields = np.fft.fft(experiment.dc_fields)
        ft_moments = np.fft.fft(experiment.moments)

        # Calculate period
        # take fundamental of fourier transformed field
        period = 1. / np.abs(ft_freqs[np.argmax(np.abs(ft_fields))])

        result = cls(
            ft_fields, ft_moments, ft_freqs, experiment.rep_temperature, period
        )

        return result

    @staticmethod
    def create_ac_experiment(ft_experiments: list['FTExperiment'],
                             experiments: list[Experiment],
                             mass: float, mw: float) -> ac.Experiment:
        '''
        Creates ac.Experiment using a list of Fourier Transform results

        Parameters
        ----------
        ft_experiments: list[FTExperiment]
            Fourier transform data, each constituting a single
            datapoint in an AC susceptiblity experiment
        exepriments: list[Experiments]
            Waveform experiments which accompany ft_experiments, order must
            match
        mass: float
            Mass of sample, used to convert real and imaginary susceptibility
            from emu/Oe to cm3 mol^{-1}\n
            Set to None for no conversion
        mw: float
            Molecular weight of sample, used to convert real and imaginary
            susceptibility from emu/Oe to cm3 mol^{-1}\n
            Set to None for no conversion

        Returns
        -------
        ac.Experiment
            ccfit2.ac.Experiment object for this set of AC Susceptibility data
        '''

        ac_freqs = []
        real_sus = []
        imag_sus = []

        for ft_exp in ft_experiments:

            # Find largest FT field index
            idx_field = np.argmax(np.abs(ft_exp.ft_fields))
            ac_freqs.append(np.abs(ft_exp.ft_freqs[idx_field]))

            # Calculate susceptibility as M/H at maximum (emu/Oe)
            chi = np.abs(ft_exp.ft_moments[idx_field])
            chi /= np.abs(ft_exp.ft_fields[idx_field])

            # Calculate the phase angle (rad) of the ratio between field and
            # moment spectra at their fundamental frequency.
            # It is the ratio because any function of the type:
            # Acos(X) + Bsin(X) = Ccos(X + phasefactor)
            # This phasefactor angle is determined by the ratio of A/B
            phi = calculate_phase(
                ft_exp.ft_fields[idx_field], ft_exp.ft_moments[idx_field]
            )

            # Calculate real and imaginary susceptibility components
            real_sus.append(abs(chi * np.cos(phi)))
            imag_sus.append(abs(chi * np.sin(phi)))

        real_sus = np.array(real_sus)
        imag_sus = np.array(imag_sus)
        ac_freqs = np.array(ac_freqs)

        # Convert real and imaginary susceptibility from (emu/Oe)
        # to cm^3mol^(-1)
        if None not in (mw, mass):
            real_sus *= mw / (mass / 1000.)
            imag_sus *= mw / (mass / 1000.)

        # Collect temperature data
        temperatures = np.array(
            [ft_exp.temperature for ft_exp in ft_experiments]
        )
        mean_temp = np.mean(temperatures)

        ac_fields = np.array([
            calculate_ac_field(exp)
            for exp in experiments
        ])

        # Sort all data by ac frequency, low to high
        order = np.argsort(ac_freqs)

        # Create AC experiment using waveform susceptibility data
        ac_experiment = ac.Experiment(
            mean_temp,
            temperatures[order],
            real_sus[order],
            imag_sus[order],
            ac_freqs[order],
            0.,
            np.zeros(len(temperatures)),
            ac_fields[order]
        )

        return ac_experiment


def calculate_ac_field(experiment: Experiment):
    '''
    Calculates the ac field of single waveform experiment

    Parameters
    ----------
    experiment: Experiment
        Waveform experiment object

    Returns
    -------
    float
        ac field
    '''

    # low to high field values
    sorted_fields = np.sort(experiment.dc_fields)

    n_fields = len(sorted_fields)

    # Take upper and lower 50%
    low = np.mean(sorted_fields[:n_fields // 2])
    high = np.mean(sorted_fields[n_fields // 2:])

    # and average them to get the ac field
    acf = abs((high - low) / 2.)

    return acf


def calculate_phase(ft_field: float, ft_moment: float):
    '''
    Calculates phase between fourier tranformed dc field and moment values

    Parameters
    ----------
    ft_field: float
        Fourier Transformed dc field value
    ft_moment: float
        Fourier Transformed moment value

    Returns
    -------
    float
        Phase in radians
    '''

    phase = abs(
        np.angle(
            ft_field / ft_moment,
            deg=False
        )
    )

    return phase


def plot_ft(ft_result: FTExperiment, save: bool = True, show: bool = True,
            save_name: str = 'FT_waveform.png',
            window_title: str = 'Fourier Transformed Data',
            verbose: bool = True) -> tuple[plt.Figure, list[plt.Axes]]:
    '''
    Plot fourier transform data for a given Waveform dataset

    Parameters
    ----------
    ft_result: FTExperiment
        Fts
    save: bool, default True
        If True, saves plot to file
    show: bool, default True
        If True, shows plot on screen
    save_name: str, default 'FT_waveform.png'
        If save is True, will save plot to this file name
    window_title: str, default 'Fourier Transformed Data'
        Title of figure window, not of plot
    verbose: bool, default True
        If True, plot file location is written to terminal

    Returns
    -------
    plt.Figure
        Matplotlib figure object
    list[plt.Axes]
        Matplotlib axis objects, first contains FT of field, second
        contains FT of moment
    '''

    fig, ax1 = plt.subplots(1, 1, num=window_title)

    ax2 = ax1.twinx()

    _plot_ft(ft_result, ax1, ax2)

    fig.tight_layout()

    if save:
        fig.savefig(save_name, dpi=400)
        if verbose:
            ut.cprint(
                f'\n Fourier Transform plot saved to \n {save_name}\n',
                'cyan'
            )
    if show:
        plt.show()

    return fig, [ax1, ax2]


def _plot_ft(ft_result: FTExperiment, ax1: plt.axes, ax2: plt.axes):
    '''
    Plot moment and field vs time for a given Waveform dataset
    onto a given pair of axis

    Parameters
    ----------
    ax1: plt.axes
        Axis on which field vs time data is plotted
    ax2: plt.axes
        Axis on which moment vs time data is plotted
    ft_result: FTExperiment
        Experimental data

    Returns
    -------
    None
    '''

    # Plot the data.
    ax1.plot(ft_result.ft_freqs, np.abs(ft_result.ft_fields), color='k')
    ax2.plot(
        ft_result.ft_freqs, np.abs(ft_result.ft_moments), color='tab:blue'
    )

    ax1.set_ylabel(r'|FT$^\mathregular{D}$ (H)|')
    ax2.set_ylabel(r'|FT$^\mathregular{D}$ (M)|')

    ax1.yaxis.label.set_color('k')
    ax2.yaxis.label.set_color('tab:blue')

    ax1.set_xscale('log')

    ax1.set_xlabel('Frequency (Hz)')

    # Set minor ticks
    for ax in [ax1, ax2]:
        ax.yaxis.set_minor_locator(AutoMinorLocator())
        ax.xaxis.set_minor_locator(LogLocator(base=10, subs='auto'))

    return


def plot_moment_and_field(experiment: Experiment, save: bool = True,
                          show: bool = True, save_name: str = 'waveform.png',
                          window_title: str = 'Waveform Data',
                          verbose: bool = True) -> tuple[plt.Figure, list[plt.Axes]]: # noqa
    '''
    Plot moment and field vs time for a given Waveform dataset

    Parameters
    ----------
    experiment: Experiment
        Experimental data
    save: bool, default True
        If True, saves plot to file
    show: bool, default True
        If True, shows plot on screen
    save_name: str, default 'waveform.png'
        If save is True, will save plot to this file name
    window_title: str, default 'Waveform Data'
        Title of figure window, not of plot
    verbose: bool, default True
        If True, plot file location is written to terminal

    Returns
    -------
    plt.Figure
        Matplotlib figure object
    list[plt.Axes]
        Matplotlib axis objects, first is moment vs time,
        and second is field vs time, third is FT of field vs freq, fourth
        contains FT of moment vs freq
    '''

    fig, ax1 = plt.subplots(num=window_title)

    # Create axis for field vs time
    ax2 = ax1.twinx()

    # Plot data
    _plot_moment_and_field(experiment, ax1, ax2)

    fig.tight_layout()

    if save:
        fig.savefig(save_name, dpi=400)
        if verbose:
            ut.cprint(
                f'\n Moment and field vs time plot saved to \n {save_name}\n',
                'cyan'
            )
    if show:
        plt.show()

    return fig, [ax1, ax2]


def _plot_moment_and_field(experiment: Experiment,
                           ax1: plt.axes, ax2: plt.axes) -> list[plt.Axes]:
    '''
    Plot moment and field vs time for a given Waveform dataset
    onto a given pair of axis

    Parameters
    ----------
    ax1: plt.axes
        Axis on which field vs time data is plotted
    ax2: plt.axes
        Axis on which moment vs time data is plotted
    experiment: Experiment
        Experimental data

    Returns
    -------
    None
    '''

    # Plot the field and moment data
    ax1.plot(
        experiment.times - experiment.times[0],
        experiment.dc_fields,
        color='k'
    )
    ax2.plot(
        experiment.times - experiment.times[0],
        experiment.moments,
        color='tab:blue'
    )

    ax1.set_ylabel(r'Field (Oe)')
    ax2.set_ylabel(r'Moment (emu)')

    ax1.yaxis.label.set_color('k')
    ax2.yaxis.label.set_color('tab:blue')

    ax1.set_xlabel('Time (s)')

    # Set minor ticks
    for ax in [ax1, ax2]:
        ax.yaxis.set_minor_locator(AutoMinorLocator())
        ax.xaxis.set_minor_locator(AutoMinorLocator())

    return [ax1, ax2]


def plot_mf_ft(ft_result: FTExperiment, experiment: Experiment,
               save: bool = True, show: bool = True,
               save_name: str = 'waveform.png',
               window_title: str = 'Waveform Data',
               verbose: bool = True) -> tuple[plt.Figure, list[plt.Axes]]:
    '''
    Plot moment and field vs time, along with their fourier transforms
    vs frequency for a given Waveform dataset

    Parameters
    ----------
    ft_result: FTExperiment
        Fourier Transform result object which accompanies experiment
    experiment: Experiment
        Experimental data
    save: bool, default True
        If True, saves plot to file
    show: bool, default True
        If True, shows plot on screen
    save_name: str, default 'waveform.png'
        If save is True, will save plot to this file name
    window_title: str, default 'Waveform Data'
        Title of figure window, not of plot
    verbose: bool, default True
        If True, plot file location is written to terminal

    Returns
    -------
    plt.Figure
        Matplotlib figure object
    list[plt.Axes]
        Matplotlib axis objects, first is moment vs time,
        and second is field vs time, third is FT of field vs freq, fourth
        contains FT of moment vs freq
    '''

    fig, [ax1, ax3] = plt.subplots(2, 1, num=window_title)

    ax2 = ax1.twinx()
    ax4 = ax3.twinx()

    _plot_moment_and_field(experiment, ax1, ax2)
    _plot_ft(ft_result, ax3, ax4)

    fig.tight_layout()

    if save:
        fig.savefig(save_name, dpi=400)
        if verbose:
            ut.cprint(
                f'\n Moment, Field, and FT plot saved to \n {save_name}\n',
                'cyan'
            )
    if show:
        plt.show()

    return fig, [ax1, ax2, ax3, ax4]


def plot_raw_moment_field(experiments: list[Experiment],
                          save: bool = False,
                          show: bool = True, save_name: str = 'raw_waveform.png', # noqa
                          window_title: str = 'Raw Waveform Data',
                          verbose: bool = True) -> tuple[plt.Figure, list[plt.Axes]]: # noqa
    '''
    Plot moment and field vs time from a list of experiments

    Parameters
    ----------
    experiments: list[Experiment]
        Experiments to plot
    save: bool, default False
        If True, saves plot to file
    show: bool, default True
        If True, shows plot on screen
    save_name: str, default 'raw_waveform.png'
        If save is True, will save plot to this file name
    window_title: str, default 'Raw Waveform Data'
        Title of figure window, not of plot
    verbose: bool, default True
        If True, plot file location is written to terminal

    Returns
    -------
    plt.Figure
        Matplotlib figure object
    list[plt.Axes]
        Matplotlib axis objects, first is moment vs time,
        and second is field vs time
    '''

    fig, ax1 = plt.subplots(1, 1, num=window_title)
    ax2 = ax1.twinx()

    times = np.concatenate([
        experiment.times
        for experiment in experiments
    ])

    fields = np.concatenate([
        experiment.dc_fields
        for experiment in experiments
    ])

    moments = np.concatenate([
        experiment.moments
        for experiment in experiments
    ])

    torder = np.argsort(times)
    times = times[torder]
    moments = moments[torder]
    fields = fields[torder]

    times -= times[0]

    # Plot the field and moment data
    ax1.plot(
        times,
        fields,
        color='k',
        lw=0.5,
        marker='x'
    )
    ax2.plot(
        times,
        moments,
        color='tab:blue',
        lw=0.5,
        marker='+'
    )

    ax1.set_ylabel(r'Field (Oe)')
    ax2.set_ylabel(r'Moment (emu)')

    ax1.yaxis.label.set_color('k')
    ax2.yaxis.label.set_color('tab:blue')

    ax1.set_xlabel('Time (s)')

    # Set minor ticks
    for ax in [ax1, ax2]:
        ax.yaxis.set_minor_locator(AutoMinorLocator())
        ax.xaxis.set_minor_locator(AutoMinorLocator())

    fig.tight_layout()

    if save:
        fig.savefig(save_name, dpi=400)
        if verbose:
            ut.cprint(
                f'\n Raw Moment and Field vs time plot saved to \n {save_name}\n', # noqa
                'cyan'
            )
    if show:
        plt.show()

    return fig, [ax1, ax2]
