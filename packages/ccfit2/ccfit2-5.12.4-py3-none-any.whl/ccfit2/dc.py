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

This module contains functions and objects for working with DC magnetisation
decay data
'''

from math import isnan
import numpy as np
from numpy.typing import NDArray, ArrayLike
import matplotlib.pyplot as plt
from matplotlib.ticker import AutoMinorLocator
from scipy.optimize import least_squares
from abc import ABC, abstractmethod
import copy
import warnings
import datetime

from . import utils as ut
from . import stats
from .__version__ import __version__


#: Supported DC Headers - One of each MUST be found in the input file.
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
        'DC Moment Free Ctr (emu)',
        'DC Moment Fixed Ctr (emu)'
    ]
}

# Generic dc magnetometer file header names
HEADERS_GENERIC = list(HEADERS_SUPPORTED.keys())


class Measurement():
    '''
    Stores data for a single DC Decay measurement at a
    given temperature and applied field

    Parameters
    ----------
    dc_field: float
        Applied dc field (Oe)
    temperature: float
        Temperature of datapoint (K)
    moment: float
        Magnetic moment of datapoint (emu)
    time: float
        Time of datapoint (s)

    Attributes
    ----------
    dc_field: float
        Applied dc field (Oe)
    temperature: float
        Temperature of datapoint (K)
    moment: float
        Magnetic moment of datapoint (emu)
    time: float
        Time of datapoint (s)
    rep_temperature: float
        Representative temperature assigned to this datapoint (K)
    rep_dc_field: float
        Representative dc field assigned to this datapoint (Oe)
    '''

    def __init__(self, dc_field: float, temperature: float, time: float,
                 moment: float):
        self.dc_field = dc_field
        self.temperature = temperature
        self.time = time
        self.moment = moment
        self._rep_temperature = None
        self._rep_dc_field = None

    @property
    def rep_temperature(self):
        return self._rep_temperature

    @rep_temperature.setter
    def rep_temperature(self, value: float):
        self._rep_temperature = value
        return

    @property
    def rep_dc_field(self):
        return self._rep_dc_field

    @rep_dc_field.setter
    def rep_dc_field(self, value: float):
        self._rep_dc_field = value
        return

    @classmethod
    def from_file(cls, file: str, data_header: str = '[Data]',
                  verbose: bool = True,
                  encoding: str = 'find') -> list['Measurement']:
        '''
        Extracts dc data from magnetometer output file and
        returns list of datapoints, one for each valid measurement.\n
        Incomplete lines are ignored

        Parameters
        ----------
        file: str
            Name of magnetometer output file
        data_header: str default '[Data]'
            Contents of line which specifies the beginning of the data block
            in input file.\n
            Default is to find line containing '[Data]'
        verbose: bool, default True
            If True, issues parsing measurements are written to terminal
        encoding: str, default 'find'
            Encoding to use when opening file
        Returns
        -------
        list
            Measurement objects, one per temperature, per field\n
            List has the same order as the magnetometer file

        '''

        # Find encoding of input file
        if encoding == 'find':
            encoding = ut.detect_encoding(file)

        data_index, header_indices, _ = ut.parse_mag_file(
            file,
            HEADERS_SUPPORTED,
            data_header,
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


class Experiment():
    '''
    Stores data for multiple DC measurements at a
    given temperature, given applied dc field

    Parameters
    ----------
    rep_temperature: float
        Representative temperature of experiment (K)
        e.g. mean of all datapoints (Measurements)
    rep_dc_field: float
        Representative dc field assigned to this experiment (Oe)
        e.g. mean of all datapoints
    raw_temperatures: array_like
        Raw temperatures of experiment, one per datapoint (K)
    times: array_like
        Time value, one per datapoint (s)
    moments: array_like
        Measured moment, one value per datapoint (emu)
    dc_fields: array_like
        Applied dc field in Oe, one value per datapoint (Oe)

    Attributes
    ----------
    rep_temperature: float
        Representative temperature of experiment
        e.g. mean of all datapoints (Measurements)
    rep_dc_field: float
        Representative dc field assigned to this experiment (Oe)
        e.g. mean of all datapoints
    raw_temperatures: ndarray of floats
        Raw temperatures of experiment, one per datapoint (K)
    times: ndarray of floats
        Time value, one per datapoint (s)
    moments: ndarray of floats
        Measured moment, one value per datapoint (emu)
    dc_fields: ndarray of floats
        Applied dc field in Oe, one value per datapoint (Oe)
    meas_dc_fields: ndarray of floats
        Applied dc field measured by the instrument\n
        one value per datapoint (Oe)\n
        If not set, this will be the same as dc_fields\n
        But allows the user to calibrate dc_fields and still retain the\n
        actual measured values\n
    '''

    def __init__(self, rep_temperature: float, rep_dc_field: float,
                 raw_temperatures: ArrayLike,
                 times: ArrayLike, moments: ArrayLike,
                 dc_fields: ArrayLike):

        self.rep_temperature = rep_temperature
        self.rep_dc_field = rep_dc_field
        self.raw_temperatures = np.asarray(raw_temperatures)
        self.times = np.asarray(times)
        self.moments = np.asarray(moments)
        self.dc_fields = np.asarray(dc_fields)
        self._meas_dc_fields = np.copy(self.dc_fields)

        return

    @property
    def meas_dc_fields(self) -> NDArray:
        return self._meas_dc_fields

    @meas_dc_fields.setter
    def meas_dc_fields(self, value: ArrayLike):
        self._meas_dc_fields = np.asarray(value)
        return

    @classmethod
    def _from_single(cls, measurements: list[Measurement],
                     cut_moment: float = 0.01) -> 'Experiment':
        '''
        Creates experiment from single set of measurements

        Parameters
        ----------
        measurements: list[Measurement]
            Measurements constituting a single experiment
        cut_moment: float, default 0.01
            Specifies %% of initial moment\n
            Moments smaller than this will be discarded
        Returns
        -------
            Experiment
        '''

        # Remove moments less than cut_moment % of initial moment
        measurements = [
            mm
            for mm in measurements
            if mm.moment >= cut_moment * measurements[0].moment
        ]

        raw_temperatures = np.array([
            mm.temperature for mm in measurements
        ])

        moments = np.array([
            mm.moment for mm in measurements
        ])

        # Set start time to zero
        mintime = np.min([
            mm.time
            for mm in measurements
        ])

        # Set start time of these measurements as zero
        for mm in measurements:
            mm.time -= mintime

        times = np.array([
            mm.time for mm in measurements
        ])

        dc_fields = np.array([
            mm.dc_field for mm in measurements
        ])

        rep_temperature = measurements[0].rep_temperature
        rep_dc_field = measurements[0].rep_dc_field

        experiment = cls(
            rep_temperature,
            rep_dc_field,
            raw_temperatures,
            times,
            moments,
            dc_fields
        )

        return experiment

    @classmethod
    def from_measurements(cls, measurements: list[Measurement],
                          temp_thresh: float = 0.1,
                          field_thresh: float = 1,
                          x_var: str = 'T',
                          cut_moment: float = 0.01) -> list[list['Experiment']]: # noqa
        '''
        Creates a list of lists of Experiment objects from a list of\n
        Individual measurement objects. Experiments are defined as a set of\n
        Measurements with the same temperature and DC field strength.\n\n

        Measurements are sorted by dc field and temperature,\n
        with order determined by x_var, then time.

        Parameters
        ----------
        measurement: list[Measurement]
            Measurements at various temperatures and times
        temp_thresh: float, default 0.1 K
            Threshold used to discriminate between temperatures (K)
        field_thresh: float, default 1 Oe
            Threshold used to discriminate between dc field values (Oe)
        x_var: str, {'T', 'H'}}
            Independent variable that relaxation time is being measured over,
            temperature or field.
        cut_moment: float, default 0.01
            Specifies %% of initial moment\n
            Moments smaller than this will be discarded
            after splitting by field and temperature.

        Returns
        -------
        list[list[Experiment]]
            Each element is a list of Experiments at the same DC field/
            temperature sorted low to high DC field/temperature strength.

            Within each sublist the elements are single experiments
            which are each a set of measurements with the same temperature
            and DC field strength.

            The sublists are sorted low to high mean temperature/DC field.

            All sorting is dependent on choice of x_var

        Raises
        ------
        ValueError
            If x_var is not T or H
        '''
        if x_var == 'T':
            # Sort measurements by dc field, temperature, and time
            measurements.sort(
                key=lambda k: (k.dc_field, k.temperature, k.time)
            )

            # Find mean field values
            mean_fields, fsi = ut.find_mean_values(
                [
                    measurement.dc_field
                    for measurement in measurements
                ],
                thresh=field_thresh
            )

            # Set each measurement's representative dc field, here the mean
            for measurement, mean_field in zip(measurements, mean_fields):
                measurement.rep_dc_field = mean_field

            # Re-sort using mean field
            measurements.sort(
                key=lambda k: (k.rep_dc_field, k.temperature, k.time)
            )
            # Get indices which sort the above
            order = sorted(
                np.arange(len(measurements), dtype=int),
                key=lambda k: (
                    measurements[k].rep_dc_field,
                    measurements[k].temperature,
                    measurements[k].time
                )
            )
            # transfer field split points into new order
            fsi = np.array([order[fs] for fs in fsi], dtype=int)

            # Find mean temperature values
            mean_temperatures, tsi = ut.find_mean_values(
                [
                    measurement.temperature
                    for measurement in measurements
                ],
                thresh=temp_thresh
            )

            # Set each measurement's representative temperature, here the mean
            for m, mt in zip(measurements, mean_temperatures):
                m.rep_temperature = mt

            # Re-sort using mean dc field and mean temperature
            measurements.sort(
                key=lambda k: (k.rep_dc_field, k.rep_temperature, k.time)
            )
            # Get indices which sort the above
            order = sorted(
                np.arange(len(measurements), dtype=int),
                key=lambda k: (
                    measurements[k].rep_dc_field,
                    measurements[k].rep_temperature,
                    measurements[k].time
                )
            )
            # transfer temperature split points into new order
            tsi = np.array([order[ts] for ts in tsi], dtype=int)
            # transfer field split points into new order
            fsi = np.array([order[fs] for fs in fsi], dtype=int)

            # Split and field and temperature jumps
            split_ind = np.concatenate([tsi, fsi])
            # Remove duplicate split indices corresponding to field and
            # temperature jump
            split_ind = np.unique(split_ind)

            # If only one experiment, then no need to split, just
            # combine measurements into an experiment
            if not len(split_ind):
                experiments = [
                    cls._from_single(measurements, cut_moment=cut_moment)
                ]
            # >1 Experiment, then split up measurements from time jumps
            else:
                split_measurements: list[list[Measurement]] = np.split(
                    measurements,
                    split_ind
                )

                # and combine each set of measurements into an experiment
                experiments = [
                    cls._from_single(sm, cut_moment=cut_moment)
                    for sm in split_measurements
                ]

            # Group experiments by field
            mean_field, split_ind = ut.find_mean_values(
                [
                    experiment.rep_dc_field
                    for experiment in experiments
                ],
                thresh=field_thresh
            )

            all_experiments: list[list[Experiment],] = np.split(
                experiments,
                split_ind
            )

            all_experiments = np.asarray(all_experiments, dtype=object)

            # order by ascending field
            all_experiments = all_experiments[
                np.argsort(
                    [
                        experiments[0].rep_dc_field
                        for experiments in all_experiments
                    ]
                )
            ]
            # and order each iso-field set by ascending temperature
            _ordered = copy.copy(all_experiments)

            for it, experiments in enumerate(all_experiments):
                order = np.argsort(
                    [exp.rep_temperature for exp in experiments]
                )
                _ordered[it] = _ordered[it][order]

            all_experiments = _ordered.tolist()

        elif x_var == 'H':
            # Sort measurements by temperature, dc field, and time
            measurements = sorted(
                measurements,
                key=lambda k: (k.temperature, k.dc_field, k.time)
            )

            # Find mean temperature values
            mean_temperatures, tsi = ut.find_mean_values(
                [
                    measurement.temperature
                    for measurement in measurements
                ],
                thresh=temp_thresh
            )

            # Set each measurement's representative temperature, here the mean
            for measurement, mean_temperature in zip(measurements, mean_temperatures): # noqa
                measurement.rep_temperature = mean_temperature

            # Re-sort using mean temperature
            measurements = sorted(
                measurements,
                key=lambda k: (k.rep_temperature, k.dc_field,  k.time)
            )
            # Get indices which sort the above
            order = sorted(
                np.arange(len(measurements), dtype=int),
                key=lambda k: (
                    measurements[k].rep_temperature,
                    measurements[k].dc_field,
                    measurements[k].time
                )
            )
            # transfer temperature split points into new order
            tsi = np.array([order[ts] for ts in tsi], dtype=int)

            # Find mean field values
            mean_fields, fsi = ut.find_mean_values(
                [
                    measurement.dc_field
                    for measurement in measurements
                ],
                thresh=field_thresh
            )

            # Set each measurement's representative temperature, here the mean
            for m, mf in zip(measurements, mean_fields):
                m.rep_dc_field = mf

            # Re-sort using mean temperature and mean dc field
            measurements = sorted(
                measurements,
                key=lambda k: (k.rep_temperature, k.rep_dc_field, k.time)
            )
            # Get indices which sort the above
            order = sorted(
                np.arange(len(measurements), dtype=int),
                key=lambda k: (
                    measurements[k].rep_temperature,
                    measurements[k].rep_dc_field,
                    measurements[k].time
                )
            )
            # transfer field split points into new order
            fsi = np.array([order[fs] for fs in fsi], dtype=int)
            # transfer temperature split points into new order
            tsi = np.array([order[ts] for ts in tsi], dtype=int)

            # Split and field and temperature jumps
            split_ind = np.concatenate([fsi, tsi])
            # Remove duplicate split indices corresponding to field and
            # temperature jump
            split_ind = np.unique(split_ind)

            # If only one experiment, then no need to split, just
            # combine measurements into an experiment
            if not len(split_ind):
                experiments = [
                    cls._from_single(measurements, cut_moment=cut_moment)
                ]
            # >1 Experiment, then split up measurements from time jumps
            else:
                split_measurements: list[list[Measurement]] = np.split(
                    measurements,
                    split_ind
                )

                # and combine each set of measurements into an experiment
                experiments = [
                    cls._from_single(sm, cut_moment=cut_moment)
                    for sm in split_measurements
                ]

            # Group experiments by temperature
            mean_temperature, split_ind = ut.find_mean_values(
                [
                    experiment.rep_temperature
                    for experiment in experiments
                ],
                thresh=temp_thresh
            )

            all_experiments: list[list[Experiment]] = np.split(
                experiments,
                split_ind
            )

            all_experiments = np.asarray(all_experiments, dtype=object)

            # order by ascending temperature
            all_experiments = all_experiments[
                np.argsort(
                    [
                        experiments[0].rep_temperature
                        for experiments in all_experiments
                    ]
                )
            ]
            # and order each iso-temperature set by ascending field
            _ordered = copy.copy(all_experiments)

            for it, experiments in enumerate(all_experiments):
                order = np.argsort(
                    [exp.rep_dc_field for exp in experiments]
                )
                _ordered[it] = _ordered[it][order]

            all_experiments = _ordered.tolist()

        else:
            raise ValueError(f'Unknown x_var "{x_var}" specified')

        return all_experiments


class Model(ABC):
    '''
    Abstract class on which all models of DC magnetisation decays are based

    Parameters
    ----------
    fit_vars: dict[str, float]
        Parameter to fit in model function\n
        Keys are fit/fix parameter names (see class.PARNAMES)\n
        Values are either float (actual value) or the string 'guess'\n
        If 'guess' then a parameter value is guessed using experiment
    fix_vars: dict[str, float]
        Parameter which remain fixed in model function\n
        Keys are fit/fix parameter names (see class.PARNAMES)\n
        Values are either float (actual value) or the string 'guess'\n
        If 'guess' then a parameter value is guessed using experiment
    experiment: Experiment
        Experiment used to generate guess values for fit/fix parameters\n
        if 'guess' is specified as a value in either fit_vars or fix_vars
    '''

    @property
    @abstractmethod
    def NAME() -> str:
        'String name of model'
        raise NotImplementedError

    @property
    @abstractmethod
    def DISP_NAME() -> str:
        'Display name for interactive buttons'
        raise NotImplementedError

    @property
    @abstractmethod
    def PARNAMES() -> list[str]:
        'String names of parameters which can be fitted or fixed'
        raise NotImplementedError

    @property
    @abstractmethod
    def VARNAMES_MM() -> dict[str, str]:
        '''
        Mathmode (i.e. $$, latex ) versions of PARNAMES\n
        Keys are strings from PARNAMES plus any other variables which
        might be plotted (e.g. lntau_expect)\n
        Values are mathmode strings
        '''
        raise NotImplementedError

    @property
    @abstractmethod
    def UNITS() -> dict[str, str]:
        '''
        string names of units of PARNAMES\n
        Keys are strings from PARNAMES
        might be needed\n
        Values are unit name strings
        '''
        raise NotImplementedError

    @property
    @abstractmethod
    def UNITS_MM() -> dict[str, str]:
        '''
        Mathmode (i.e. $$, latex ) versions of UNITS\n
        Keys are strings from PARNAMES
        might be needed\n
        Values are unit name strings
        '''
        raise NotImplementedError

    @property
    @abstractmethod
    def BOUNDS() -> dict[str, list[float, float]]:
        '''
        Bounds for each parameter of model
        keys: parameter name
        values: [upper, lower]
        used by scipy least_squares
        '''
        raise NotImplementedError

    @abstractmethod
    def _calc_lntau_expect() -> float:
        '''
        Calculates expectation value of ln(tau) from class attributes
        '''
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def calc_lntau_expect() -> float:
        '''
        Calculates expectation value of ln(tau) for this model using a given
        set of parameter values
        '''
        raise NotImplementedError

    @abstractmethod
    def _calc_lntau_fit_ul() -> list[float]:
        '''
        Calculates upper and lower bounds of ln(tau) from uncertainty\n
        in fitted parameters, rather than from ln(tau) distribution.
        '''
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def calc_lntau_fit_ul() -> list[float]:
        '''
        Calculates upper and lower bounds of ln(tau) from uncertainty
        in fitted parameters, rather than from ln(tau) distribution,
        using a given set of parameter and standard deviation values
        '''
        raise NotImplementedError

    @abstractmethod
    def _calc_lntau_stdev() -> float:
        '''
        Calculates standard deviation of ln(tau) from class attributes
        '''
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def calc_lntau_stdev() -> float:
        '''
        Calculates standard deviation of ln(tau) from a given set of parameter
        values
        '''
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def model(parameters: dict[str, float], time: list[float]) -> list[float]:
        '''
        Evaluates model function of DC magnetisation decay
        using provided parameter and time values.

        Parameters
        ----------
        parameters: list[float]
            Parameters to use in model function
        time: list[float]
            Time values in seconds at which model function is evaluated

        Returns
        -------
        list[float]
            Moment as a function of time

        '''
        raise NotImplementedError

    @classmethod
    def residuals(cls, params: dict[str, float], time: list[float],
                  true_moment: list[float]) -> list[float]:
        '''
        Calculates difference between measured moment and
        trial moment from model

        Parameters
        ----------
        params: list[float]
            model parameter values
        time: list[float]
            time values in seconds at which model function is evaluated
        moment: list[float]
            true (experimental) values of magnetic moment

        Returns
        -------
        list[float]
            Residuals
        '''
        trial_moment = cls.model(params, time)

        residuals = trial_moment - true_moment
        return residuals

    def __init__(self, fit_vars: dict[str, float | str],
                 fix_vars: dict[str, float | str], experiment: 'Experiment'):

        # Replace any 'guess' strings with proper guesses
        self.fit_vars = self.set_initial_vals(fit_vars, experiment)
        self.fix_vars = self.set_initial_vals(fix_vars, experiment)

        # Check all PARNAMES are provided in fit+fix
        input_names = [
            name for name in {**self.fit_vars, **self.fix_vars}.keys()
        ]

        if any([req_name not in input_names for req_name in self.PARNAMES]):
            raise ValueError(
                'Missing fit/fix parameters in {} Model'.format(
                    self.NAME
                )
            )

        # Check for duplicates in fit and fix
        dupe = self.fit_vars.keys() & self.fix_vars.keys()
        if dupe:
            raise ValueError(
                f'Duplicate keys {dupe} provided to both fit and fix'
            )

        # Final model parameter values
        self._final_var_values = {
            var: None
            for var in self.PARNAMES
        }

        # Fit status, temperature, and field
        self._fit_status = False
        self._temperature = None
        self._dc_field = None
        self._meas_dc_field = None

        # Fit standard deviation
        self._fit_stdev = {
            var: None
            for var in self.fit_vars.keys()
        }

        # Expectation value and standard deviation of ln(tau)
        self._lntau_expect = None
        self._lntau_fit_ul = None
        self._lntau_stdev = None

        return

    @abstractmethod
    def set_initial_vals(param_dict: dict[str, str | float],
                         experiment: 'Experiment') -> dict[str, float]:
        '''
        Sets guess values for parameters if requested by user

        Parameters
        ----------
        param_dict: dict[str, str | float]
            Either fit_vars or fix_vars
            Keys are fit/fix parameter names (see class.PARNAMES)\n
            Values are either float (actual value) or the string 'guess'\n
            If 'guess' then a parameter value is guessed using experiment
        experiment: Experiment
            Used to set guess values if specified

        Returns
        -------
        dict[str, float]
            Keys are fit/fix parameter names (see class.PARNAMES)\n
            Values are float (actual value) which are initial values of\n
            parameter
        '''
        raise NotImplementedError

    @property
    def fit_status(self) -> bool:
        'True if fit successful, else False'
        return self._fit_status

    @fit_status.setter
    def fit_status(self, value):
        if isinstance(value, bool):
            self._fit_status = value
        else:
            raise TypeError
        return

    @property
    def temperature(self) -> float:
        '''
        Temperature of fit (K)
        '''
        return self._temperature

    @temperature.setter
    def temperature(self, value):
        if isinstance(value, (np.floating, float, int)):
            self._temperature = float(value)
        else:
            raise TypeError
        return

    @property
    def dc_field(self) -> float:
        '''
        DC Field of fit (Oe)
        '''
        return self._dc_field

    @dc_field.setter
    def dc_field(self, value):
        if isinstance(value, (np.floating, float, int)):
            self._dc_field = float(value)
        else:
            raise TypeError
        return

    @property
    def meas_dc_field(self) -> float:
        '''
        Measured DC Field of fit (Oe)
        '''
        return self._meas_dc_field

    @meas_dc_field.setter
    def meas_dc_field(self, value: float):
        if isinstance(value, (np.floating, float, int)):
            self._meas_dc_field = float(value)
        else:
            raise TypeError
        return

    @property
    def final_var_values(self) -> float:
        '''
        Final values of parameters, both fitted and fixed\n
        Keys are PARNAMES, values are float value of that parameter
        '''
        return self._final_var_values

    @final_var_values.setter
    def final_var_values(self, value):
        if isinstance(value, dict):
            self._final_var_values = value
        else:
            raise TypeError
        return

    @property
    def fit_stdev(self) -> dict[str, float]:
        '''
        Standard deviation on fitted parameters, from fitting routine\n
        Keys are PARNAMES, values are float value of that parameter\n
        Only the parameters in fit_vars will be present.
        '''
        return self._fit_stdev

    @fit_stdev.setter
    def fit_stdev(self, value):
        if isinstance(value, dict):
            self._fit_stdev = value
        else:
            raise TypeError
        return

    @property
    def fix_vars(self) -> dict[str, float]:
        '''
        Variables of model which are fixed.\n
        Keys are PARNAMES, values are float value of that parameter
        '''
        return self._fix_vars

    @fix_vars.setter
    def fix_vars(self, value):
        if isinstance(value, dict):
            if any([key not in self.PARNAMES for key in value.keys()]):
                raise KeyError('Unknown variable names provided to fix')
            self._fix_vars = value
        else:
            raise TypeError('fix must be dictionary')
        return

    @property
    def fit_vars(self) -> dict[str, float]:
        '''
        Variables of model which will be fitted.\n
        Keys are PARNAMES, values are floats corresponding to guess values\n
        passed to fitting routine.
        '''
        return self._fit_vars

    @fit_vars.setter
    def fit_vars(self, value):
        if isinstance(value, dict):
            if any([key not in self.PARNAMES for key in value.keys()]):
                raise KeyError('Unknown variable names provided to fit')
            self._fit_vars = value
        else:
            raise TypeError('Fit must be dictionary')
        return

    @property
    def lntau_stdev(self) -> float:
        'Standard deviation of ln(tau)'
        # If not calculated yet, then calculate
        if self._lntau_stdev is None:
            self.lntau_stdev = self._calc_lntau_stdev()
        return self._lntau_stdev

    @lntau_stdev.setter
    def lntau_stdev(self, value):
        self._lntau_stdev = value

    @property
    def lntau_fit_ul(self) -> list[float]:
        '''
        Upper and lower (1 sigma) limits of ln(tau) from fit uncertainty
        in fitted values
        '''
        # If not calculated yet, then calculate
        if self._lntau_fit_ul is None:
            self.lntau_fit_ul = self._calc_lntau_fit_ul()
        return self._lntau_fit_ul

    @lntau_fit_ul.setter
    def lntau_fit_ul(self, value):
        self._lntau_fit_ul = value

    @property
    def lntau_expect(self) -> float:
        'Expectation value of ln(tau)'
        # If not calculated yet, then calculate
        if self._lntau_expect is None:
            self.lntau_expect = self._calc_lntau_expect()
        return self._lntau_expect

    @lntau_expect.setter
    def lntau_expect(self, value):
        self._lntau_expect = value

    @classmethod
    def residual_from_float_list(cls, new_vals: list[float],
                                 fit_vars: dict[str, float],
                                 fix_vars: dict[str, float],
                                 time: list[float],
                                 moment: list[float]) -> list[float]:
        '''
        Wrapper for `residuals` method, takes new values from fitting routine
        which provides list[float], to construct new fit_vals dict, then
        runs `residuals` method.

        Parameters
        ----------

        fit_vars: dict[str, float]
            Parameter to fit in model function\n
            keys are PARNAMES, values are initial guesses used for fitting
        fix_vars: dict[str, float]
            Parameter which remain fixed in model function\n
            keys are PARNAMES, values are float values
        time: list[float]
            time values in seconds at which model function is evaluated
        moment: list[float]
            true (experimental) values of magnetic moment

        Returns
        -------
        list[float]
            Residuals
        '''

        # Swap fit values for new values from fit routine
        new_fit_vars = {
            name: guess
            for guess, name in zip(new_vals, fit_vars.keys())
        }

        # And make combined dict of fit and fixed
        # variable names (keys) and values
        all_vars = {**fix_vars, **new_fit_vars}

        return cls.residuals(all_vars, time, moment)

    @ut.strip_guess
    def fit_to(self, experiment: 'Experiment',
               verbose: bool = True) -> None:
        '''
        Fits model to Experiment

        Parameters
        ----------
        experiment: Experiment
            Experiment to which a model will be fitted
        verbose: bool, default True
            If True, prints information to terminal

        Returns
        -------
        None
        '''

        # Get starting guesses
        guess = [val for val in self.fit_vars.values()]

        # Get bounds for variables to be fitted
        bounds = np.array([
            self.BOUNDS[name]
            for name in self.fit_vars.keys()
        ]).T

        curr_fit = least_squares(
            self.residual_from_float_list,
            args=[
                self.fit_vars,
                self.fix_vars,
                experiment.times,
                experiment.moments
            ],
            x0=guess,
            bounds=bounds,
            max_nfev=200 * (len(guess) + 1),
            jac='3-point'
        )

        self.temperature = experiment.rep_temperature
        self.dc_field = experiment.dc_fields[-1]
        self.meas_dc_field = experiment.meas_dc_fields[-1]

        # Set final variable values
        # from fitted values
        curr_fit.x = abs(curr_fit.x)
        self.final_var_values = {
            name: value
            for name, value in zip(self.fit_vars.keys(), curr_fit.x)
        }

        # and fixed values
        for key, val in self.fix_vars.items():
            self.final_var_values[key] = val

        stdev, nonzero_sing = stats.svd_stdev(curr_fit)

        # Standard deviation error on the parameters
        self.fit_stdev = {
            label: val
            for label, val in zip(self.fit_vars.keys(), stdev)
        }

        if curr_fit.status == 0:
            if verbose:
                ut.cprint(
                    '\n Fit at {} K and {} Oe failed - Too many iterations'.format( # noqa
                        self.temperature, self.dc_field
                    ),
                    'black_yellowbg'
                )

            self.fit_stdev = {
                label: np.nan
                for label in self.fit_vars.keys()
            }
            self.fit_status = False
        elif any([np.isnan(val) or val is None for val in ut.flatten_recursive(self.lntau_fit_ul)]): # noqa
            if verbose:
                message = '\n At {: 6.1f} Oe and {: 6.2f} K'.format(
                    self.dc_field, self.temperature
                )
                message += ' upper and lower bounds of <ln(tau)> cannot be calculated -> point discarded.' # noqa
                ut.cprint(message, 'black_yellowbg')
            self.fit_status = False
            self.final_var_values = {
                name: np.nan
                for name in self.final_var_values.keys()
            }
            self.fit_stdev = {
                label: np.nan
                for label in self.fit_vars.keys()
            }
        else:
            self.fit_status = True

            # Report singular values=0 of Jacobian
            # and indicate that std_dev cannot be calculated
            for par, si in zip(self.fit_vars.keys(), nonzero_sing):
                if verbose and not si:
                    ut.cprint(
                        f'Warning: At {self.dc_field: 6.1f} Oe and {self.temperature: 6.2f} K Jacobian is degenerate for {par}', # noqa
                        'black_yellowbg'
                    )
                    ut.cprint(
                        'Standard deviation cannot be found, and is set to zero', # noqa
                        'black_yellowbg'
                    )

        return


class ExponentialModel(Model):
    '''
    Exponential Model of Magnetisation decay with stretching parameters

    Parameters
    ----------
    fit_vars: dict[str, float]
        Parameter to fit in model function\n
        Keys are fit/fix parameter names (see class.PARNAMES)\n
        Values are either float (actual value) or the string 'guess'\n
        If 'guess' then a parameter value is guessed using experiment
    fix_vars: dict[str, float]
        Parameter which remain fixed in model function\n
        Keys are fit/fix parameter names (see class.PARNAMES)\n
        Values are either float (actual value) or the string 'guess'\n
        If 'guess' then a parameter value is guessed using experiment
    experiment: Experiment
        Experiment used to generate guess values for fit/fix parameters\n
        if 'guess' is specified as a value in either fit_vars or fix_vars

    Attributes
    ----------
    fit_vars: dict[str, float]
        Parameter to fit in model function\n
        keys are PARNAMES, values are initial guesses used for fitting
    fix_vars: dict[str, float]
        Parameter which remain fixed in model function\n
        keys are PARNAMES, values are float values
    final_var_values: dict[str, float]
        Final values of models (fitted and fixed)
        keys are PARNAMES, values are float values
    fit_stdev: dict[str, float]
        Standard deviation on fitted parameters, from fitting routine\n
        Keys are PARNAMES, values are float value of that parameter\n
        Only the parameters in fit_vars will be present.
    temperature: float
        Representative temperature of fit (K)\n
        Taken from experiment.rep_temperature when fit_to() is called.
    dc_field: float
        DC Field of fit (Oe)
        Taken from experiment.rep_dc_field when fit_to() is called.
    lntau_expect: float
        Expectation value of ln(tau)
    lntau_stdev: float
        Standard deviation of ln(tau) calculated using analytical expression
    lntau_fit_ul: list[float]
        Upper and lower (1 sigma) limits of ln(tau) from fit uncertainty\n
        in fitted values
    fit_status: bool
        True if fit successful, else false
    meas_dc_field: float
        Measured DC Field of fit (Oe)\n
        If not set, this will be the same as dc_field\n
        But allows the user to calibrate dc_field and still retain the\n
        actual measured value\n
    '''

    #: Model name
    NAME = 'Exponential'

    #: Display name for interactive buttons
    DISP_NAME = copy.copy(NAME)

    #: Model Parameter name strings
    PARNAMES = [
        'tau*', 'beta', 'm_eq', 'm_0', 't_offset'
    ]

    #: Model Parameter bounds
    BOUNDS = {
        'tau*': [0., np.inf],
        'beta': [0., 1.],
        'm_eq': [-np.inf, np.inf],
        'm_0': [0, np.inf],
        't_offset': [0., np.inf]
    }

    #: Model Parameter mathmode name strings
    VARNAMES_MM = {
        'tau*': r'$\tau^*$',
        'lntau_expect': r'$\langle \ln \tau \rangle$',
        'lntau_stdev': r'$\sigma_{\ln \tau}$',
        'beta': r'$\beta$',
        'm_eq': r'$M_\mathregular{eq}$',
        'm_0': r'$M_0$',
        't_offset': r'$\mathregular{t}_\mathregular{offset}$'
    }

    #: Model Parameter Unit strings
    UNITS = {
        'tau*': 's',
        'beta': '',
        'm_eq': 'emu',
        'm_0': 'emu',
        't_offset': 's'
    }

    #: Model Parameter Unit mathmode strings
    UNITS_MM = {
        'tau*': r'$\mathregular{s}$',
        'beta': '',
        'm_eq': r'$\mathregular{emu}$',
        'm_0': r'$\mathregular{emu}$',
        't_offset': r'$\mathregular{s}$',
    }

    def __init__(self, fit_vars: dict[str, float | str],
                 fix_vars: dict[str, float | str], experiment: Experiment):

        # Initialise attributes required by Model superclass to default values
        super().__init__(fit_vars, fix_vars, experiment)

        return

    @staticmethod
    def set_initial_vals(param_dict: dict[str, str | float],
                         experiment: Experiment):
        '''
        Sets guess values for parameters if requested by user

        Parameters
        ----------
        param_dict: dict[str, str | float]
            Either fit_vars or fix_vars
            Keys are fit/fix parameter names (see class.PARNAMES)
            values are either float (actual value) or the string 'guess'\n
            If 'guess' then a parameter value is guessed using experiment
        experiment: Experiment
            Used to set guess values if specified

        Returns
        -------
        dict[str, float]
            Keys are fit/fix parameter names (see class.PARNAMES)
            values are float (actual value) which are initial values of
            parameter
        '''

        # Make copy, any str values will be replaced
        new_param_dict = copy.copy(param_dict)

        # Guesses
        guessdict = {
            'tau*': 100.,
            'm_eq': experiment.moments[-1],  # Final measured moment
            'm_0': experiment.moments[0],  # First measured moment
            'beta': 0.95,
            't_offset': 0.
        }

        # Replace 'guess' with relevant guess
        for var, val in param_dict.items():
            if isinstance(val, str) and val.lower() == 'guess':
                new_param_dict[var] = guessdict[var]

        return new_param_dict

    @staticmethod
    def model(parameters: dict[str, float], time: list[float]) -> list[float]:
        '''
        Evaluates exponential model function of DC magnetisation decay
        using provided parameter and time values.

        Parameters
        ----------
        parameters: dict[str, float]
            Parameters to use in model function, keys are given in
            ExponentialModel.PARNAMES
        time: list[float]
            time values in seconds at which model function is evaluated

        Returns
        -------
        list[float]
            moment as a function of time

        '''

        m_eq = parameters['m_eq']
        m_0 = parameters['m_0']
        beta = parameters['beta']
        tau_star = parameters['tau*']
        t_offset = parameters['t_offset']

        mom = m_eq
        mom += (m_0 - m_eq) * np.exp(-((time - t_offset) / tau_star)**beta)

        return mom

    def _calc_lntau_expect(self) -> float:
        '''
        Calculates expectation value of ln(tau)

        Parameters
        ----------
        None

        Returns
        -------
        float
            <ln(tau)> value in ln(seconds)

        Raises
        -----
        ValueError
            If required model parameters in self.final_var_values are undefined
        '''

        beta = self.final_var_values['beta']
        tau_star = self.final_var_values['tau*']

        if None in [beta, tau_star]:
            _error = 'Cannot calculate ln(tau) expectation value '
            _error += 'beta and/or tau* are undefined!'
            raise ValueError(_error)

        return self.calc_lntau_expect(tau_star, beta)

    @staticmethod
    def calc_lntau_expect(tau_star: ArrayLike,
                          beta: ArrayLike) -> float | NDArray:
        '''
        Calculates expectation value of ln(tau) from given parameters

        Parameters
        ----------
        tau_star: array_like
            tau* value from Exponential model
        beta: array_like
            beta value from Exponential model

        Returns
        -------
        float | ndarray of floats
            <ln(tau)> value in ln(seconds)
        '''

        return (1 - (1 / beta)) * np.euler_gamma + np.log(tau_star)

    def _calc_lntau_stdev(self) -> float:
        '''
        Calculates standard deviation of ln(tau)

        Parameters
        ----------
        None

        Returns
        -------
        float
            Standard deviation of ln(tau) in ln(seconds)

        Raises
        -----
        ValueError
            If required model parameters in self.final_var_values are undefined
        '''

        beta = self.final_var_values['beta']

        if beta is None:
            _error = 'Error: Cannot calculate ln(tau) standard deviation'
            _error += 'beta undefined!'
            raise ValueError(_error)

        return self.calc_lntau_stdev(beta)

    @staticmethod
    def calc_lntau_stdev(beta: ArrayLike) -> float | NDArray:
        '''
        Calculates standard deviation of ln(tau) from given parameters

        Parameters
        ----------
        beta: array_like
            beta value from Exponential model

        Returns
        -------
        float | ndarray of floats
            Standard deviation of ln(tau) in ln(seconds)
        '''

        return np.sqrt((1. / beta**2 - 1.) * np.pi**2 / 6.)

    def _calc_lntau_fit_ul(self) -> list[float]:
        '''
        Calculates upper and lower bounds of ln(tau) from fit uncertainty
        in fitted parameters

        Parameters
        ----------
        None

        Returns
        -------
        list[float]
            upper and lower bounds of ln(tau) from fit uncertainty in fitted
            parameters (upper > lower)

        Raises
        ------
        ValueError
            If required model parameters in self.final_var_values
            or self.fit_stdev are undefined
        '''

        tau_star = self.final_var_values['tau*']

        if 'tau*' in self.fit_stdev:
            tau_star_std = self.fit_stdev['tau*']
        else:
            tau_star_std = 0.

        beta = self.final_var_values['beta']

        if 'beta' in self.fit_stdev:
            beta_std = self.fit_stdev['beta']
        else:
            beta_std = 0.

        if None in [tau_star, beta]:
            _error = '\n Error: Cannot calculate ln(tau) bounds '
            _error += 'tau and/or beta is undefined!'
            raise ValueError(_error)
        elif None in [tau_star_std, beta_std]:
            _error = '\n Error: Cannot calculate ln(tau) bounds '
            _error += 'tau and/or beta standard deviation is undefined!'
            raise ValueError(_error)

        return self.calc_lntau_fit_ul(tau_star, beta, tau_star_std, beta_std)

    @staticmethod
    def calc_lntau_fit_ul(tau_star: ArrayLike, beta: ArrayLike,
                          tau_star_std: ArrayLike,
                          beta_std: ArrayLike) -> list[float | NDArray]:
        '''
        Calculates upper and lower bounds of ln(tau) from uncertainty\n
        in fitted parameters, rather than from ln(tau) distribution.

        Parameters
        ----------
        tau_star: array_like
            tau* value from Exponential model
        beta: array_like
            beta value from Exponential model
        tau_star_std: array_like
            Standard deviation of tau* value from Exponential model
        beta_star_std: array_like
            Standard deviation of beta value from Exponential model

        Returns
        -------
        list[float | ndarray of floats]
            upper and lower bounds of ln(tau) from fit uncertainty in fitted
            parameters (upper > lower)
        '''

        tau_star = np.asarray(tau_star)
        tau_star_std = np.asarray(tau_star_std)
        beta = np.asarray(beta)
        beta_std = np.asarray(beta_std)

        warnings.filterwarnings('ignore', 'invalid value encountered in log')

        upper = (1 - (1 / (beta - beta_std))) * np.euler_gamma + np.log(tau_star + tau_star_std) # noqa
        lower = (1 - (1 / (beta + beta_std))) * np.euler_gamma + np.log(tau_star - tau_star_std) # noqa

        warnings.filterwarnings('default', 'invalid value encountered in log')

        bounds = np.array([upper, lower]).T
        bounds = np.sort(bounds, axis=-1)

        return bounds.T.tolist()


class DoubleExponentialModel(Model):
    '''
    Double Exponential Model of Magnetisation decay

    Parameters
    ----------
    fit_vars: dict[str, float]
        Parameter to fit in model function\n
        Keys are fit/fix parameter names (see class.PARNAMES)\n
        Values are either float (actual value) or the string 'guess'\n
        If 'guess' then a parameter value is guessed using experiment
    fix_vars: dict[str, float]
        Parameter which remain fixed in model function\n
        Keys are fit/fix parameter names (see class.PARNAMES)\n
        Values are either float (actual value) or the string 'guess'\n
        If 'guess' then a parameter value is guessed using experiment
    experiment: Experiment
        Experiment used to generate guess values for fit/fix parameters\n
        if 'guess' is specified as a value in either fit_vars or fix_vars

    Attributes
    ----------
    fit_vars: dict[str, float]
        Parameter to fit in model function\n
        keys are PARNAMES, values are initial guesses used for fitting
    fix_vars: dict[str, float]
        Parameter which remain fixed in model function\n
        keys are PARNAMES, values are float values
    final_var_values: dict[str, float]
        Final values of models (fitted and fixed)
        keys are PARNAMES, values are float values
    fit_stdev: dict[str, float]
        Standard deviation on fitted parameters, from fitting routine\n
        Keys are PARNAMES, values are float value of that parameter\n
        Only the parameters in fit_vars will be present.
    temperature: float
        Representative temperature of fit (K)\n
        Taken from experiment.rep_temperature when fit_to() is called.
    dc_field: float
        DC Field of fit (Oe)
        Taken from experiment.rep_dc_field when fit_to() is called.
    fit_status: bool
        True if fit successful, else false
    meas_dc_field: float
        Measured DC Field of fit (Oe)\n
        If not set, this will be the same as dc_field\n
        But allows the user to calibrate dc_field and still retain the\n
        actual measured value\n
    '''

    #: Model Name
    NAME = 'Double Exponential'

    #: Display name for interactive buttons
    DISP_NAME = copy.copy(NAME)

    #: Model Parameter name strings
    PARNAMES = [
        'tau*1', 'tau*2', 'beta1', 'beta2', 'm_eq', 'm_0', 't_offset', 'frac'
    ]

    #: Model Parameter bounds
    BOUNDS = {
        'tau*1': [0., np.inf],
        'tau*2': [0., np.inf],
        'beta1': [0., 1.],
        'beta2': [0., 1.],
        'frac': [0., 1.],
        'm_eq': [-np.inf, np.inf],
        'm_0': [0., np.inf],
        't_offset': [0., np.inf]
    }

    #: Model Parameter mathmode name strings
    VARNAMES_MM = {
        'tau*1': r'$\tau_{1}^*$',
        'tau*2': r'$\tau_{2}^*$',
        'lntau_expect1': r'$\langle \ln \tau 1 \rangle$',
        'lntau_expect2': r'$\langle \ln \tau 2 \rangle$',
        'lntau_stdev1': r'$\sigma_{\ln \tau 1}$',
        'lntau_stdev2': r'$\sigma_{\ln \tau 2}$',
        'beta1': r'$\beta_{1}$',
        'beta2': r'$\beta_{2}$',
        'frac': r'Fraction',
        'm_eq': r'$M_\mathregular{eq}$',
        'm_0': r'$M_0$',
        't_offset': r'$\mathregular{t}_\mathregular{offset}$'
    }

    #: Model Parameter Unit strings
    UNITS = {
        'tau*1': 's',
        'tau*2': 's',
        'beta1': '',
        'beta2': '',
        'frac': '',
        'm_eq': 'emu',
        'm_0': 'emu',
        't_offset': 's'
    }

    #: Model Parameter Unit mathmode strings
    UNITS_MM = {
        'tau*1': r'$\mathregular{s}$',
        'tau*2': r'$\mathregular{s}$',
        'beta1': '',
        'beta2': '',
        'frac': '',
        'm_eq': r'$\mathregular{emu}$',
        'm_0': r'$\mathregular{emu}$',
        't_offset': r'$\mathregular{s}$',
    }

    # Redefined for list
    @property
    def lntau_stdev(self) -> list[float]:
        'Standard deviation of ln(tau)'
        # If not calculated yet, then calculate
        if None in self._lntau_stdev:
            self._lntau_stdev = self._calc_lntau_stdev()
        return self._lntau_stdev

    # Redefined for list
    @property
    def lntau_fit_ul(self) -> list[list[float]]:
        '''
        Upper and lower (1 sigma) limits of ln(tau) from fit uncertainty
        in fitted values
        '''
        # If not calculated yet, then calculate
        if None in self._lntau_fit_ul:
            self._lntau_fit_ul = self._calc_lntau_fit_ul()
        return self._lntau_fit_ul

    # Redefined for list
    @property
    def lntau_expect(self) -> list[float]:
        'Expectation value of ln(tau)'
        # If not calculated yet, then calculate
        if None in self._lntau_expect:
            self._lntau_expect = self._calc_lntau_expect()
        return self._lntau_expect

    def __init__(self, fit_vars: dict[str, float | str],
                 fix_vars: dict[str, float | str], experiment: Experiment):

        # Initialise attributes required by Model superclass to default values
        super().__init__(fit_vars, fix_vars, experiment)

        # Expectation value and standard deviation of ln(tau)
        self._lntau_expect = [None, None]
        self._lntau_fit_ul = [None, None]
        self._lntau_stdev = [None, None]

        return

    @staticmethod
    def set_initial_vals(param_dict: dict[str, str | float],
                         experiment: Experiment):
        '''
        Sets guess values for parameters if requested by user

        Parameters
        ----------
        param_dict: dict[str, str | float]
            Either fit_vars or fix_vars
            Keys are fit/fix parameter names (see class.PARNAMES)
            values are either float (actual value) or the string 'guess'\n
            If 'guess' then a parameter value is guessed using experiment
        experiment: Experiment
            Used to set guess values if specified

        Returns
        -------
        dict[str, float]
            Keys are fit/fix parameter names (see class.PARNAMES)
            values are float (actual value) which are initial values of
            parameter
        '''

        # Make copy, any str values will be replaced
        new_param_dict = copy.copy(param_dict)

        # Guesses
        guessdict = {
            'tau*1': 50.,
            'tau*2': 5000.,
            'm_eq': experiment.moments[-1],  # M_eq guess final measured moment
            'm_0': experiment.moments[0],  # M_0 is first measured moment
            'frac': 0.5,
            'beta1': 0.95,
            'beta2': 0.95,
            't_offset': 0.
        }

        # Replace 'guess' with relevant guess
        for var, val in param_dict.items():
            if isinstance(val, str) and val.lower() == 'guess':
                new_param_dict[var] = guessdict[var]

        return new_param_dict

    @staticmethod
    def model(parameters: dict[str, float], time: list[float]) -> list[float]:
        '''
        Evaluates exponential model function of DC magnetisation decay
        using provided parameter and time values.

        Parameters
        ----------
        parameters: dict[str, float]
            Parameters to use in model function, keys are given in
            ExponentialModel.PARNAMES
        time: list[float]
            time values in seconds at which model function is evaluated

        Returns
        -------
        list[float]
            Moment as a function of time

        '''

        m_eq = parameters['m_eq']
        m_0 = parameters['m_0']
        beta1 = parameters['beta1']
        beta2 = parameters['beta2']
        tau_star1 = parameters['tau*1']
        tau_star2 = parameters['tau*2']
        frac = parameters['frac']
        t_offset = parameters['t_offset']

        sef1 = np.exp(-((time - t_offset) / tau_star1)**beta1)
        sef2 = np.exp(-((time - t_offset) / tau_star2)**beta2)
        mom = m_eq + (m_0 - m_eq) * ((frac * sef1) + ((1 - frac) * sef2))

        return mom

    def _calc_lntau_expect(self) -> float:
        '''
        Calculates expectation value of ln(tau)

        Parameters
        ----------
        None

        Returns
        -------
        float
            <ln(tau)>1 and <ln(tau)2> values in ln(seconds)

        Raises
        -----
        ValueError
            If required model parameters in self.final_var_values are undefined
        '''

        beta1 = self.final_var_values['beta1']
        beta2 = self.final_var_values['beta2']
        tau_star1 = self.final_var_values['tau*1']
        tau_star2 = self.final_var_values['tau*2']

        if None in [beta1, beta2, tau_star1, tau_star2]:
            _error = 'Cannot calculate ln(tau) expectation value '
            _error += 'beta and/or tau* are undefined!'
            raise ValueError(_error)

        return self.calc_lntau_expect(tau_star1, tau_star2, beta1, beta2)

    @staticmethod
    def calc_lntau_expect(tau_star1: ArrayLike, tau_star2: ArrayLike,
                          beta1: ArrayLike,
                          beta2: ArrayLike) -> float | NDArray:
        '''
        Calculates expectation value of ln(tau)

        Parameters
        ----------
        tau_star1: array_like
            tau*1 value from Double Exponential model
        tau_star2: array_like
            tau*2 value from Double Exponential model
        beta1: array_like
            beta1 value from Double Exponential model
        beta2: array_like
            beta2 value from Double Exponential model

        Returns
        -------
        float | ndarray of floats
            <ln(tau)>1 and <ln(tau)2> values in ln(seconds)
        '''

        lntau1 = (1 - (1 / beta1)) * np.euler_gamma + np.log(tau_star1)
        lntau2 = (1 - (1 / beta2)) * np.euler_gamma + np.log(tau_star2)

        return [lntau1, lntau2]

    def _calc_lntau_stdev(self) -> list[float]:
        '''
        Calculates standard deviation of ln(tau1) and ln(tau2)

        Parameters
        ----------
        None

        Returns
        -------
        list[float]
            Standard deviation of ln(tau)1 and ln(tau)2 in ln(seconds)

        Raises
        -----
        ValueError
            If required model parameters in self.final_var_values are undefined
        '''

        beta1 = self.final_var_values['beta1']
        beta2 = self.final_var_values['beta2']

        if None in [beta1, beta2]:
            _error = 'Error: Cannot calculate ln(tau) standard deviation'
            _error += 'beta undefined!'
            raise ValueError(_error)

        return self.calc_lntau_stdev(beta1, beta2)

    @staticmethod
    def calc_lntau_stdev(beta1: ArrayLike,
                         beta2: ArrayLike) -> list[float | NDArray]:
        '''
        Calculates standard deviation of ln(tau1) and ln(tau2)

        Parameters
        ----------
        beta1: array_like
            beta1 value from Double Exponential model
        beta2: array_like
            beta2 value from Double Exponential model

        Returns
        -------
        list[float | ndarray of floats]
            Standard deviation of ln(tau)1 and ln(tau)2 in ln(seconds)
        '''

        sd1 = np.sqrt((1. / beta1**2 - 1.) * np.pi**2 / 6.)
        sd2 = np.sqrt((1. / beta2**2 - 1.) * np.pi**2 / 6.)

        return [sd1, sd2]

    def _calc_lntau_fit_ul(self) -> list[list[float]]:
        '''
        Calculates upper and lower bounds of ln(tau) from fit uncertainty\n
        in fitted parameters

        Parameters
        ----------
        None

        Returns
        -------
        list[float]
            upper and lower bounds of ln(tau)1\n
            and upper and lower bounds of ln(tau)2 from fit uncertainty in\n
            fitted parameters (upper > lower)

        Raises
        ------
        ValueError
            If required model parameters in self.final_var_values
            or self.fit_stdev are undefined
        '''

        tau_star1 = self.final_var_values['tau*1']

        if 'tau*1' in self.fit_stdev:
            tau_star1_std = self.fit_stdev['tau*1']
        else:
            tau_star1_std = 0.

        beta1 = self.final_var_values['beta1']

        if 'beta1' in self.fit_stdev:
            beta1_std = self.fit_stdev['beta1']
        else:
            beta1_std = 0.

        tau_star2 = self.final_var_values['tau*2']

        if 'tau*2' in self.fit_stdev:
            tau_star2_std = self.fit_stdev['tau*2']
        else:
            tau_star2_std = 0.

        beta2 = self.final_var_values['beta2']

        if 'beta2' in self.fit_stdev:
            beta2_std = self.fit_stdev['beta2']
        else:
            beta2_std = 0.

        if None in [tau_star1, tau_star2, beta1, beta2]:
            _error = 'Cannot calculate ln(tau) bounds'
            _error += 'beta and/or tau* are undefined!'
            raise ValueError(_error)
        elif None in [tau_star1_std, tau_star2_std, beta1_std, beta2_std]:
            _error = '\n Error: Cannot calculate ln(tau) bounds '
            _error += 'tau*1, tau*2, beta1, or beta2 standard '
            _error += 'deviation is undefined!'
            raise ValueError(_error)

        bounds = self.calc_lntau_fit_ul(
            tau_star1, tau_star2, beta1, beta2, tau_star1_std, tau_star2_std,
            beta1_std, beta2_std
        )

        return bounds

    @staticmethod
    def calc_lntau_fit_ul(tau_star1: ArrayLike, tau_star2: ArrayLike,
                          beta1: ArrayLike, beta2: ArrayLike,
                          tau_star1_std: ArrayLike, tau_star2_std: ArrayLike,
                          beta1_std: ArrayLike,
                          beta2_std: ArrayLike) -> list[list[float], list[float]]: # noqa
        '''
        Calculates upper and lower bounds of ln(tau) from fit uncertainty\n
        in fitted parameters

        Parameters
        ----------
        tau_star1: array_like
            tau*1 value from Double Exponential model
        tau_star2: array_like
            tau*2 value from Double Exponential model
        beta1: array_like
            beta1 value from Double Exponential model
        beta2: array_like
            beta2 value from Double Exponential model
        tau_star1_std: array_like
            Standard deviation of tau*1 value from Double Exponential model
        tau_star2_std: array_like
            Standard deviation of tau*2 value from Double Exponential model
        beta1_std: array_like
            Standard deviation of beta1 value from Double Exponential model
        beta2_std: array_like
            Standard deviation of beta2 value from Double Exponential model


        Returns
        -------
        list[list[float], list[float]]
            upper and lower bounds of ln(tau)1\n
            and upper and lower bounds of ln(tau)2 from fit uncertainty in\n
            fitted parameters (upper > lower)
        '''

        warnings.filterwarnings('ignore', 'invalid value encountered in log')

        upper1 = (1 - (1 / (beta1 - beta1_std))) * np.euler_gamma + np.log(tau_star1 + tau_star1_std) # noqa
        lower1 = (1 - (1 / (beta1 + beta1_std))) * np.euler_gamma + np.log(tau_star1 - tau_star1_std) # noqa

        upper2 = (1 - (1 / (beta2 - beta2_std))) * np.euler_gamma + np.log(tau_star2 + tau_star2_std) # noqa
        lower2 = (1 - (1 / (beta2 + beta2_std))) * np.euler_gamma + np.log(tau_star2 - tau_star2_std) # noqa

        warnings.filterwarnings('default', 'invalid value encountered in log')

        bounds1 = np.array([upper1, lower1]).T
        bounds2 = np.array([upper2, lower2]).T

        bounds1 = np.sort(bounds1, axis=-1)
        bounds2 = np.sort(bounds2, axis=-1)

        return [bounds1.T.tolist(), bounds2.T.tolist()]


def write_model_params(models: list[Model],
                       file_name: str = 'dc_model_params.csv',
                       verbose: bool = True, delimiter: str = ',',
                       extra_comment: str = '') -> None:
    '''
    Writes fitted parameters of a set of models to csv file.\n
    Assumes models are all of the same type, e.g. all Exponential

    Parameters
    ----------
    models: list[Model]
        Models, one per temperature, must all be same type
    file_name: str, default 'dc_model_params.csv'
        Name of output file
    verbose: bool, default True
        If True, file location is printed to terminal
    delimiter: str, default ','
        Delimiter used in .csv file, usually either ',' or ';'
    extra_comment: str, optional
        Extra comments to add to file after ccfit2 version line
        Must include comment character # for each new line

    Returns
    -------
    None
    '''

    # Get model type
    if all({isinstance(model, DoubleExponentialModel) for model in models}):
        model_type = DoubleExponentialModel
    else:
        model_type = None

    # Make header
    header = [
        'T (K)',
        'H (Oe)',
    ]

    if all([model.dc_field != model.meas_dc_field for model in models]):
        h_meas = True
        header.append('H_measured (Oe)')
    else:
        h_meas = False

    # Fitted parameters
    for name in models[0].fit_vars.keys():
        header.append(f'{name} ({models[0].UNITS[name]})')
        header.append(f'{name}-s-dev ({models[0].UNITS[name]})')

    # Fixed parameters
    for name in models[0].fix_vars.keys():
        header.append(f'{name} ({models[0].UNITS[name]})')

    # Model-dependent headers
    if model_type == DoubleExponentialModel:
        header += [
            '<ln(tau1)> (ln(s))',
            'sigma_ln(tau1) (ln(s))',
            'fit_upper_ln(tau1) (ln(s))',
            'fit_lower_ln(tau1) (ln(s))',
            '<ln(tau2)> (ln(s))',
            'sigma_ln(tau2) (ln(s))',
            'fit_upper_ln(tau2) (ln(s))',
            'fit_lower_ln(tau2) (ln(s))'
        ]
    else:
        header += [
            '<ln(tau)> (ln(s))',
            'sigma_ln(tau) (ln(s))',
            'fit_upper_ln(tau) (ln(s))',
            'fit_lower_ln(tau) (ln(s))'
        ]
    header = f'{delimiter} '.join(header)

    # Make comment
    comment = (
        f'#This file was generated with ccfit2 v{__version__}'
        ' on {}\n'.format(
            datetime.datetime.now().strftime('%H:%M:%S %d-%m-%Y ')
        )
    )

    if len(extra_comment):
        comment += extra_comment

    # Assemble output array
    _out = []

    for model in models:
        _tmp = []

        if not model.fit_status:
            continue

        _tmp = [model.temperature, model.dc_field]

        if h_meas:
            _tmp.append(model.meas_dc_field)

        for name in model.fit_vars.keys():
            _tmp += [
                model.final_var_values[name],
                model.fit_stdev[name]
            ]

        for value in model.fix_vars.values():
            _tmp.append(value)

        if model_type == DoubleExponentialModel:
            _tmp += [
                model.lntau_expect[0],
                model.lntau_stdev[0],
                model.lntau_fit_ul[0][0],
                model.lntau_fit_ul[0][1],
                model.lntau_expect[1],
                model.lntau_stdev[1],
                model.lntau_fit_ul[1][0],
                model.lntau_fit_ul[1][1]
            ]
        else:
            _tmp += [
                model.lntau_expect,
                model.lntau_stdev,
                model.lntau_fit_ul[0],
                model.lntau_fit_ul[1],
            ]

        _out.append(np.asarray(_tmp))

    _out = np.asarray(_out)

    # Save file
    np.savetxt(
        file_name,
        _out,
        header=header,
        delimiter=delimiter,
        encoding='utf-8',
        comments=comment,
    )

    if verbose:
        ut.cprint(
            f'\n DC Model parameters written to \n {file_name}\n',
            'cyan'
        )

    return


def write_model_data(experiments: list['Experiment'],
                     models: list['Model'],
                     file_name: str = 'dc_model_data.csv',
                     verbose: bool = True, delimiter: str = ',',
                     extra_comment: str = '') -> None:
    '''
    Creates csv file containing time, and moment using the model
    function with fitted and fixed parameters.
    Temperatures for which a fit was not possible are not included.

    Parameters
    ----------
    experiments: list[Experiment]
        List of experiments to which a model was fitted
    models: list[Model]
        List of models, one per experiment
    file_name: str, default 'dc_model_data.csv'
        Name of output file
    verbose: bool, default True
        If True, file location is printed to terminal
    delimiter: str, default ','
        Delimiter used in .csv file, usually either ',' or ';'
    extra_comment: str, optional
        Extra comments to add to file after ccfit2 version line
        Must include comment character # for each new line

    Returns
    -------
    None
    '''

    # Make header
    header = [
        'Temperature (K)',
        'Field (Oe)',
        'Time (s)',
        'Moment (emu)'
    ]
    header = f'{delimiter} '.join(header)

    # Make comment
    comment = (
        f'#This file was generated with ccfit2 v{__version__}'
        ' on {}\n'.format(
            datetime.datetime.now().strftime('%H:%M:%S %d-%m-%Y ')
        )
    )

    if len(extra_comment):
        comment += extra_comment

    # Assemble output array
    _out = []

    # For each experiment and its corresponding model, calculate
    # moment at experimental time values
    for model, experiment in zip(models, experiments):

        moments = model.model(
            model.final_var_values,
            experiment.times,
        )

        _temps = [model.temperature] * len(experiment.times)
        _fields = [model.dc_field] * len(experiment.times)

        _out.append(np.array([_temps, _fields, experiment.times, moments]))

    _out = np.hstack(_out).T

    # Save file
    np.savetxt(
        file_name,
        _out,
        header=header,
        delimiter=delimiter,
        encoding='utf-8',
        comments=comment
    )

    if verbose:
        ut.cprint(
            f'\n Model decays written to \n {file_name}\n',
            'cyan'
        )
    return


def plot_decays_and_fields(experiments: list[Experiment] | Experiment,
                           show: bool = True,
                           save: bool = False, iso_var: str = 'T',
                           save_name: str = 'decays_and_fields.png',
                           x_scale: str = 'linear', y_scale: str = 'linear',
                           verbose: bool = True) -> tuple[plt.Figure, list[plt.Axes]]: # noqa:
    '''
    Plots experimental decays as moment vs time and DC field vs time,
    as two separate plots on a single figure.\n

    Assumes all experiments are at either the same temperature or DC field\n
    as specified by iso_var.

    Parameters
    ----------
    experiment: list[Experiment]
        Experiments to plot, grouped by either temperature or DC field\n
        as specified by iso_var.
    show: bool, default True
        If True, shows plot on screen
    save: bool, default False
        If True, saves plot to file
    iso_var: str, {'T', 'H'}
        Iso-variable for title of plot, the value of which is
        (near) constant for all experiments\n
        If 'H', then title is 'H = {H} Oe'\n
        If 'T', then title is 'T = {T} K'
    save_name: str, default 'decays_and_fields.png'
        If save is True, saves plot to this file name
    x_scale: str {'linear', 'log'}
        Scale of x-axis
    y_scale: str {'linear', 'log'}
        Scale of y-axis
    verbose: bool, default True
        If True, plot file location is written to terminal

    Returns
    -------
    plt.Figure
        Matplotlib figure object
    list[plt.Axes]
        List of Matplotlib axis objects

    Raises
    ------
    ValueError
        If iso_var is not T or H
    '''

    fig, (ax1, ax2) = plt.subplots(1, 2, sharex=True, figsize=(10, 5))
    for experiment in experiments:

        experiment.times -= np.min(experiment.times)
        ax1.plot(
            experiment.times,
            experiment.moments,
            lw=2,
            marker='x',
            label='{:.2f} K'.format(experiment.rep_temperature)
        )
        ax2.plot(
            experiment.times,
            experiment.dc_fields,
            lw=2,
            marker='x',
            label='{:.2f} K'.format(experiment.rep_temperature)
        )

    ax1.set_xlabel('Time (s)')
    ax1.set_ylabel('Moment (emu)')
    ax2.set_xlabel('Time (s)')
    ax2.set_ylabel('DC Field (Oe)')

    if iso_var == 'T':
        fig.suptitle(
            'T = {:.2f} K'.format(
                experiments[0].rep_temperature
            ),
            fontsize='medium'
        )
    elif iso_var == 'H':
        fig.suptitle(
            'H = {:.0f} Oe'.format(
                experiments[0].rep_dc_field
            ),
            fontsize='medium'
        )
    else:
        raise ValueError(f'Unknown iso_var "{iso_var}" specified')

    ax1.set_xscale(x_scale)
    ax1.set_yscale(y_scale)

    if y_scale == 'linear':
        ax1.yaxis.set_minor_locator(AutoMinorLocator())
    if x_scale == 'linear':
        ax1.xaxis.set_minor_locator(AutoMinorLocator())

    ax2.xaxis.set_minor_locator(AutoMinorLocator())
    ax2.yaxis.set_minor_locator(AutoMinorLocator())

    fig.tight_layout()

    if save:
        plt.savefig(save_name, dpi=500)
        if verbose:
            ut.cprint(
                f'\n Decay plot saved to \n {save_name}\n',
                'cyan'
            )
    if show:
        plt.show()

    plt.close('all')

    return fig, [ax1, ax2]


def plot_decays(experiments: list[Experiment], show: bool = True,
                save: bool = False, save_name: str = 'decays.png',
                x_scale: str = 'linear', y_scale: str = 'linear',
                verbose: bool = True) -> tuple[plt.Figure, plt.Axes]:
    '''
    Plots a list of experimental decays (moment vs time) on one plot.

    Parameters
    ----------
    experiment: list[Experiment]
        Experiments to plot
    show: bool, default True
        If True, shows plot on screen
    save: bool, default False
        If True, saves plot to file
    save_name: str, default 'decays.png'
        If save is True, saves plot to this file name
    x_scale: str {'linear', 'log'}
        Scale of x-axis
    y_scale: str {'linear', 'log'}
        Scale of y-axis
    verbose: bool, default True
        If True, plot file location is written to terminal

    Returns
    -------
    plt.Figure
        Matplotlib figure object
    plt.Axes
        Matplotlib axis object
    '''

    fig, ax = plt.subplots(1, 1, figsize=(6, 5))
    for experiment in experiments:

        experiment.times -= np.min(experiment.times)
        ax.plot(
            experiment.times,
            experiment.moments,
            lw=2,
            marker='x',
            label='{:.2f} K'.format(experiment.rep_temperature)
        )

    ax.set_xlabel('Time (s)')
    ax.set_ylabel('Moment (emu)')

    if len(np.unique([e.rep_temperature for e in experiments])) > 1:
        ax.legend()
    else:
        fig.suptitle(
            'T = {:.2f} K'.format(
                experiments[0].rep_temperature
            ),
            fontsize='medium'
        )

    if y_scale == 'linear':
        ax.yaxis.set_minor_locator(AutoMinorLocator())
    if x_scale == 'linear':
        ax.xaxis.set_minor_locator(AutoMinorLocator())

    ax.set_xscale(x_scale)

    fig.tight_layout()

    if save:
        plt.savefig(save_name, dpi=500)
        if verbose:
            ut.cprint(
                f'\n Decay plot saved to \n {save_name}\n',
                'cyan'
            )
    if show:
        plt.show()

    plt.close('all')

    return fig, ax


def plot_decay(experiment: Experiment, show: bool = True,
               save: bool = False, save_name: str = 'decay.png',
               x_scale: str = 'linear', y_scale: str = 'linear',
               verbose: bool = True) -> tuple[plt.Figure, plt.Axes]:
    '''
    Plots an experimental decay (moment vs time) on one plot.

    Parameters
    ----------
    experiment: Experiment
        Experiment to plot
    show: bool, default True
        If True, shows plot on screen
    save: bool, default False
        If True, saves plot to file
    save_name: str, default 'decay.png'
        If save is True, saves plot to this file name
    x_scale: str {'linear', 'log'}
        Scale of x-axis
    y_scale: str {'linear', 'log'}
        Scale of y-axis
    verbose: bool, default True
        If True, plot file location is written to terminal

    Returns
    -------
    plt.Figure
        Matplotlib figure object
    plt.Axes
        Matplotlib axis object
    '''

    fig, ax = plt.subplots(1, 1, figsize=(6, 5))
    experiment.times -= np.min(experiment.times)
    ax.plot(
        experiment.times,
        experiment.moments,
        lw=2,
        marker='x',
        label='{:.2f} K'.format(experiment.rep_temperature)
    )

    ax.set_xlabel('Time (s)')
    ax.set_ylabel('Moment (emu)')

    if y_scale == 'linear':
        ax.yaxis.set_minor_locator(AutoMinorLocator())
    if x_scale == 'linear':
        ax.xaxis.set_minor_locator(AutoMinorLocator())

    ax.set_xscale(x_scale)

    fig.tight_layout()

    if save:
        plt.savefig(save_name, dpi=500)
        if verbose:
            ut.cprint(
                f'\n Decay plot saved to \n {save_name}\n',
                'cyan'
            )
    if show:
        plt.show()

    plt.close('all')

    return fig, ax


def plot_fitted_decay(experiment: Experiment, model: Model,
                      show: bool = True, save: bool = False,
                      save_name: str = 'fitted_decay.png',
                      show_params: bool = True,
                      x_scale: str = 'linear', y_scale: str = 'linear',
                      verbose: bool = True) -> tuple[plt.Figure, plt.Axes]:
    '''
    Plots experimental and fitted (model) decay together (moment vs time),
    displays on screen.

    Parameters
    ----------
    experiment: Experiment
        Experiment to plot
    model: Model
        Model (fitted) to plot
    show: bool, default True
        If True, shows plot on screen
    save: bool, default False
        If True, saves plot to file
    save_name: str, default 'fitted_decay.png'
        If save is True, saves plot to this file name
    show_params: bool, default True
        If True, shows fitted parameters on decay plots
    x_scale: str {'linear', 'log'}
        Scale of x-axis
    y_scale: str {'linear', 'log'}
        Scale of y-axis
    verbose: bool, default True
        If True, plot file location is written to terminal

    Returns
    -------
    plt.Figure
        Matplotlib figure object
    plt.Axes
        Matplotlib axis object
    '''

    if show_params:
        figsize = (4.5, 5)
    else:
        figsize = (4.5, 4)

    # Plot the figure.
    fig, ax = plt.subplots(
        1,
        1,
        sharex=True,
        sharey=True,
        figsize=figsize,
        num='Fitted DC Decay at {:.2f} K and {:.2f} Oe'.format(
            experiment.rep_temperature, experiment.dc_fields[-1]
        )
    )

    expression = ''

    for name in model.PARNAMES:
        if np.abs(model.final_var_values[name]) > 1E-8:
            # Meq format as x.yz x 10^a
            if name == 'm_eq':
                # Convert to scientific string, then split at E
                # to get mantissa and exponent separately
                _tmp = f'{model.final_var_values[name]:.4E}'
                _tmp = _tmp.split('E')
                _mant = float(_tmp[0])
                _exp = int(_tmp[1])
                expression += f'{model.VARNAMES_MM[name]} = {_mant:.4f}'
                expression += r' $\times \ \mathregular{10}'
                expression += r'^\mathregular{{{:d}}}$'.format(_exp)
                if 'm_eq' in model.fit_vars.keys():
                    expression += r' $\pm$'
                    _tmp = f'{model.fit_stdev[name]:.4E}'
                    _tmp = _tmp.split('E')
                    _mant = float(_tmp[0])
                    _exp = int(_tmp[1])
                    expression += f' {_mant:.4f}'
                    expression += r' $\times \ \mathregular{10}'
                    expression += r'^\mathregular{{{:d}}}$'.format(_exp)
            else:
                # All others format as float
                expression += '{} = {:.4f} '.format(
                    model.VARNAMES_MM[name],
                    model.final_var_values[name],
                )
                if name in model.fit_vars.keys():
                    expression += r'$\pm$'
                    expression += ' {:.4f}'.format(model.fit_stdev[name])
            expression += f' {model.UNITS_MM[name]} '
            expression += '\n'

    if show_params:
        ax.text(0.0, 1.02, s=expression, fontsize=10, transform=ax.transAxes)

    label_fit = 'Fit'

    ax.plot(
        experiment.times,
        experiment.moments,
        lw=0,
        marker='o',
        fillstyle='none',
        label='Experiment'
    )
    ax.plot(
        experiment.times,
        model.model(
            model.final_var_values,
            experiment.times,
        ),
        lw=1.5,
        label=label_fit
    )

    ax.legend(loc=0, fontsize='10', numpoints=1, ncol=1, frameon=False)
    ax.set_ylabel('Moment (emu)')
    ax.set_xlabel('Time (s)')

    ax.set_xscale(x_scale)
    ax.set_yscale(y_scale)

    if y_scale == 'linear':
        ax.yaxis.set_minor_locator(AutoMinorLocator())
    if x_scale == 'linear':
        ax.xaxis.set_minor_locator(AutoMinorLocator())

    fig.tight_layout()

    if save:
        plt.savefig(save_name, dpi=500)
        if verbose:
            ut.cprint(
                f'\n Fitted decay plot saved to \n {save_name}\n',
                'cyan'
            )
    if show:
        plt.show()

    plt.close()
    return fig, ax
