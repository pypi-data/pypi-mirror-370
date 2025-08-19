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

This module contains functions and objects for working with AC susceptibility
data
'''

from abc import ABC, abstractmethod
import numpy as np
from numpy.typing import ArrayLike, NDArray
from math import isnan
from scipy.optimize import least_squares, curve_fit, OptimizeWarning
from scipy.special import digamma, polygamma
import sys
import matplotlib.pyplot as plt
from matplotlib.ticker import AutoMinorLocator, FuncFormatter, NullFormatter, NullLocator, LogLocator # noqa
from matplotlib import colormaps as cmaps
from matplotlib.widgets import RadioButtons
import copy
from qtpy import QtWidgets
import warnings
import datetime


from . import gui
from . import utils as ut
from . import stats
from .__version__ import __version__


#: Supported AC Headers - One of each MUST be found in the input file.
#:
#:  Note - These differ between magnetometers\
#:
#:  These keys are the arguments to the Measurement constructor, but their
#:  order does not matter
HEADERS_SUPPORTED: dict[str, list[str]] = {
    'dc_field': [
        'Field (Oe)',
        'field (Oe)',
        'Magnetic Field (Oe)',
        'magnetic field (Oe)'
    ],
    'temperature': [
        'Temperature (K)',
        'temperature (K)'
    ],
    'real_sus': [
        'm\' (emu)',
        'AC X\'  (emu/Oe)',
        'AC X\' (emu/Oe)',
        'M\' (emu)',
        'AC X\' (emu/Oe)'
    ],
    'imag_sus': [
        'm" (emu)',
        'AC X" (emu/Oe)',
        'AC X\'\' (emu/Oe)',
        'M\'\' (emu)',
        'AC X” (emu/Oe)'
    ],
    'ac_freq': [
        'Wave Frequency (Hz)',
        'AC Frequency (Hz)',
        'Frequency (Hz)'
    ],
    'ac_field': [
        'Drive Amplitude (Oe)',
        'AC Drive (Oe)',
        'Amplitude (Oe)'
    ]
}

#: Supported AC ERROR Headers - One of each MUST be found in the input file.
#:
#:  Note - These differ between magnetometers
#:
#:  Order does not matter
ERROR_HEADERS_SUPPORTED: dict[str, list[str]] = {
    'real_sus_err': [
        'm\' Scan Std Dev',
        'AC X\' Std Err. (emu/Oe)',
        'AC X\' Std Err. (emu)'
    ],
    'imag_sus_err': [
        'm" Scan Std Dev',
        'AC X\'\' Std Err. (emu/Oe)',
        'AC X\'\' Std Err. (emu)'
    ]
}

# Generic ac magnetometer file header names
HEADERS_GENERIC = list(HEADERS_SUPPORTED.keys())
ERROR_HEADERS_GENERIC = list(ERROR_HEADERS_SUPPORTED.keys())


class Model(ABC):
    '''
    Abstract class on which all models of AC susceptibility are based

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
        Mathmode (i.e. $$, latex ) versions of PARNAMES.\n
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
        Bounds for each parameter of model\n
        keys: parameter name\n
        values: [upper, lower]\n
        used by scipy least_squares\n
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
        Calculates expectation value of ln(tau) for this model using a given\n
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
        Calculates upper and lower bounds of ln(tau) from uncertainty\n
        in fitted parameters, rather than from ln(tau) distribution,\n
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
        Calculates standard deviation of ln(tau) from a given set of\n
        parameter values
        '''
        raise NotImplementedError

    @abstractmethod
    def model(parameters: dict[str, float], ac_freq_ang: list[float]
              ) -> tuple[list[float], list[float]]:
        '''
        Computes model function of ac suceptibility

        Parameters
        ----------
        parameters: dict[str, float]
            keys are PARNAMES, values are float values
        ac_freq_ang: list[float]
            angular ac frequencies at which model will be evaluated

        Returns
        -------
        list[float]
            real susceptibility
        list[float]
            imaginary susceptibility

        '''
        raise NotImplementedError

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
                'Missing fit/fix parameters in {} Model'.format(self.NAME)
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

        # Fit status and temperature
        self._fit_status = False
        self._temperature = None

        # Fit standard deviation
        self._fit_stdev = {
            var: None
            for var in self.fit_vars.keys()
        }

        # Flat threshold
        self._flat_thresh = 1E-06

        # DC Field
        self._dc_field = None

        # Expectation value and standard deviation of ln(tau)
        self._lntau_expect = None
        self._lntau_stdev = None
        # and upper and lower bounds of ln(tau) from uncertainty
        # in fitted parameters, rather than from ln(tau) distribution.
        self._lntau_fit_ul = None

        return

    @property
    def fit_status(self) -> bool:
        '''
        True if fit successful, else False
        '''
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
    def flat_thresh(self) -> float:
        '''
        Threshold for fit of susceptibility data to X''= m * nu + b
        When root sum of squared differences between X''_flat and X''_exp
        is below flat_thresh, the fit is marked as failed.
        '''
        return self._flat_thresh

    @flat_thresh.setter
    def flat_thresh(self, value):
        if isinstance(value, (np.floating, float, int)):
            self._flat_thresh = float(value)
        else:
            raise TypeError
        return

    @property
    def dc_field(self) -> float:
        '''DC field of fit'''
        return self._dc_field

    @dc_field.setter
    def dc_field(self, value):
        if isinstance(value, (np.floating, float, int)):
            self._dc_field = float(value)
        else:
            raise TypeError
        return

    @property
    def lntau_expect(self) -> float:
        '''
        Expectation value of ln(tau)
        '''
        # If not calculated yet, then calculate
        if self._lntau_expect is None:
            self.lntau_expect = self._calc_lntau_expect()
        return self._lntau_expect

    @lntau_expect.setter
    def lntau_expect(self, value):
        if isinstance(value, (np.floating, float, int)):
            self._lntau_expect = float(value)
        else:
            raise TypeError
        return

    @property
    def lntau_stdev(self) -> float:
        '''
        Standard deviation of ln(tau) - analytical expression from distribution
        '''
        # If not calculated yet, then calculate
        if self._lntau_stdev is None:
            self.lntau_stdev = self._calc_lntau_stdev()
        return self._lntau_stdev

    @lntau_stdev.setter
    def lntau_stdev(self, value):
        if isinstance(value, (np.floating, float, int)):
            self._lntau_stdev = float(value)
        else:
            raise TypeError
        return

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
        if isinstance(value, list):
            self._lntau_fit_ul = value
        else:
            raise TypeError
        return

    @classmethod
    def residuals(cls, parameters: dict[str, float], ac_freq_ang: list[float],
                  true_real_sus: list[float],
                  true_imag_sus: list[float]) -> list[float]:
        '''
        Calculates difference between true susceptibility and trial
        susceptibility calculated using model

        Parameters
        ----------
        parameters: dict[str, float]
            parameters used in model function\n
            keys are PARNAMES, values are float values
        ac_freq_ang: list[float]
            Angular AC Frequencies
        true_real_sus: list[float]
            true (experimental) values of real part of susceptibility
        true_imag_sus: list[float]
            true (experimental) values of imaginary part of susceptibility

        Returns
        -------
        list[float]
            vector of residuals, real, then imaginary
        '''
        [trial_real_sus, trial_imag_sus] = cls.model(
            parameters, ac_freq_ang
        )
        resid_re = trial_real_sus - true_real_sus
        resid_im = trial_imag_sus - true_imag_sus

        return np.concatenate((resid_re, resid_im)).tolist()

    @classmethod
    def residual_from_float_list(cls, new_vals: list[float],
                                 fit_vars: dict[str, float],
                                 fix_vars: dict[str, float],
                                 ac_freq_ang: list[float],
                                 true_real_sus: list[float],
                                 true_imag_sus: list[float]) -> list[float]:
        '''
        Wrapper for `residuals` method, takes new values from fitting routine
        which provides list[float], to construct new fit_vals dict, then
        runs `residuals` method.

        Parameters
        ----------
        new_vals: list[float]
            New values provided by fit routine, order matches fit_vars.keys()
        fit_vars: dict[str, float]
            Parameter to fit in model function\n
            keys are PARNAMES, values are initial guesses
        fix_vars: dict[str, float]
            Parameter which remain fixed in model function\n
            keys are PARNAMES, values are float values
        ac_freq_ang: list[float]
            Angular AC Frequencies
        true_real_sus: list[float]
            true (experimental) values of real part of susceptibility
        true_imag_sus: list[float]
            true (experimental) values of imaginary part of susceptibility

        Returns
        -------
        list[float]
            Residuals, real, then imaginary
        '''

        # Swap fit values for new values from fit routine
        new_fit_vars = {
            name: guess
            for guess, name in zip(new_vals, fit_vars.keys())
        }

        # And make combined dict of fit and fixed
        # variable names (keys) and values
        all_vars = {**fix_vars, **new_fit_vars}

        return cls.residuals(all_vars, ac_freq_ang, true_real_sus, true_imag_sus) # noqa

    @ut.strip_guess
    def fit_to(self, experiment: 'Experiment',
               no_discard: bool = False, verbose: bool = True) -> None:
        '''
        Fits model to susceptibility data

        Parameters
        ----------
        experiment: Experiment
            Experiment to which a model will be fitted
        no_discard: bool, default False
            If True, do not discard any fits
        verbose: bool, default True
            If False, supresses terminal output
        '''
        # update dimensions here
        # Get starting guesses
        guess = [val for val in self.fit_vars.values()]

        # Get bounds for variables to be fitted
        bounds = np.array([
            self.BOUNDS[name]
            for name in self.fit_vars.keys()
        ]).T

        ac_freq_ang = 2. * np.pi * experiment.ac_freqs

        curr_fit = least_squares(
            fun=self.residual_from_float_list,
            args=(
                self.fit_vars,
                self.fix_vars,
                ac_freq_ang,
                experiment.real_sus,
                experiment.imag_sus
            ),
            x0=guess,
            bounds=bounds
        )

        self.temperature = experiment.rep_temperature
        self.dc_field = experiment.rep_dc_field

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
                    (
                        f'\n At {self.dc_field} Oe'
                        f' and {self.temperature: 6.2f} K fit failed'
                        ' - Too many iterations -> point discarded.'
                    ),
                    'black_yellowbg'
                )
            self.fit_stdev = {
                label: np.nan
                for label in self.fit_vars.keys()
            }
            self.fit_status = False
        # Discard fit if resulting tau isnt within limits of frequency
        elif self.discard(self.final_var_values, ac_freq_ang) and not no_discard: # noqa
            if verbose:
                message = '\n At {: 6.1f} Oe and {: 6.2f} K'.format(
                    self.dc_field, self.temperature
                )
                message += ', no peak measured -> point discarded.'
                ut.cprint(message, 'black_yellowbg')
            self.final_var_values = {
                name: np.nan
                for name in self.final_var_values.keys()
            }
            self.fit_stdev = {
                label: np.nan
                for label in self.fit_vars.keys()
            }
            self.fit_status = False
        elif self.flat(ac_freq_ang, experiment.imag_sus, self.flat_thresh) and not no_discard: # noqa
            if verbose:
                message = '\n At {: 6.1f} Oe and {: 6.2f} K'.format(
                    self.dc_field, self.temperature
                )
                message += ', data is flat -> point discarded.'
                ut.cprint(message, 'black_yellowbg')
            self.final_var_values = {
                name: np.nan
                for name in self.final_var_values.keys()
            }
            self.fit_stdev = {
                label: np.nan
                for label in self.fit_vars.keys()
            }
            self.fit_status = False
        elif any([np.isnan(val) or val is None for val in ut.flatten_recursive(self.lntau_fit_ul)]): # noqa
            if verbose:
                message = '\n At {: 6.1f} Oe and {: 6.2f} K '.format(
                    self.dc_field, self.temperature
                )
                ut.cprint(
                    (
                        'upper and lower bounds of <ln(tau)>'
                        ' cannot be calculated -> point discarded.'
                    ),
                    'black_yellowbg'
                )
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
                        (
                            f'Warning: At {self.dc_field: 6.1f} Oe'
                            f' and {self.temperature: 6.2f} K'
                            f' Jacobian is degenerate for {par}'
                        ),
                        'black_yellowbg'
                    )
                    ut.cprint(
                        (
                            'Standard deviation cannot be found,'
                            ' and is set to zero',
                        ),
                        'black_yellowbg'
                    )

        return

    @staticmethod
    def discard(params: dict[str, float], ac_freq_ang: list[float]) -> bool:
        '''
        Decides whether fits should be discarded based on following criteria

        1. tau^-1 < smallest ac frequency

        2. tau^-1 > largest ac frequency

        Parameters
        ----------
        fit_param: dict[str, float]
            keys are PARNAMES, values are fitted parameter values
        ac_freq_ang: list[float]
            Angular ac frequencies

        Returns
        -------
        bool
            True if point should be discarded, else False
        '''

        to_discard = False

        if 1. / (params['tau']) < np.min(ac_freq_ang):
            to_discard = True
        elif 1. / (params['tau']) > np.max(ac_freq_ang):
            to_discard = True

        return to_discard

    @staticmethod
    def flat(ac_freq_ang: ArrayLike, imag_sus: ArrayLike,
             threshold: float) -> bool:
        '''
        Threshold for fit of susceptibility data to X''= m * nu + b
        When root sum of squared differences between X''_flat and X''_exp
        is below flat_thresh, the fit is marked as failed.

        Parameters
        ----------
        ac_freq_ang: array_like
            Angular AC Frequency of each measurement
        imag_sus: array_like
            Imaginary component of susceptibility of each measurement
        threshold: float
            Threshold for data to be marked as flat

        Returns
        -------
        bool
            True if point is flat and should be discarded, else False
        '''

        ac_freq_ang = np.asarray(ac_freq_ang)
        imag_sus = np.asarray(imag_sus)

        is_flat = False

        warnings.filterwarnings('ignore', category=OptimizeWarning)
        linear_popt, _ = curve_fit(
            lambda a, x, b: a * x + b,
            ac_freq_ang,
            imag_sus
        )
        warnings.filterwarnings('default', category=OptimizeWarning)
        error = np.square(
            linear_popt[0] * ac_freq_ang + linear_popt[1] - imag_sus
        )

        if np.sqrt(np.sum(error)) < threshold:
            is_flat = True

        return is_flat

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


class DebyeModel(Model):
    '''
    Debye Model of AC Susceptibility

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
    flat_thresh: float
        Threshold for fit of susceptibility data to X''= m * nu + b\n
        Used in fit_to()\n
        When root sum of squared differences between X''_flat and X''_exp\n
        is below flat_thresh, the fit is marked as failed.
    fit_status: bool
        True if fit successful, else false
    '''

    #: Model Name
    NAME = 'Debye'

    #: Display name for interactive buttons
    DISP_NAME = copy.copy(NAME)

    #: Model Parameter name strings
    PARNAMES = [
        'tau', 'chi_S', 'chi_T'
    ]

    #: Model Parameter bounds
    BOUNDS = {
        'tau': [0., np.inf],
        'chi_S': [0., np.inf],
        'chi_T': [0., np.inf]
    }

    #: Model Parameter mathmode name strings
    VARNAMES_MM = {
        'tau': r'$\tau$',
        'lntau_expect': r'$\langle \ln \tau \rangle$',
        'lntau_stdev': r'$\sigma_{\ln \tau}$',
        'chi_S': r'$\chi_\mathregular{S}$',
        'chi_T': r'$\chi_\mathregular{T}$',
    }

    UNITS = {
        'tau': r's',
        'chi_S': r'cm^3 mol^-1',
        'chi_T': r'cm^3 mol^-1',
    }

    UNITS_MM = {
        'tau': r'$\mathregular{s}$',
        'chi_S': r'\mathregular{cm}^\mathregular{3} \mathregular{mol}^\mathregular{-1}$', # noqa
        'chi_T': r'\mathregular{cm}^\mathregular{3} \mathregular{mol}^\mathregular{-1}$', # noqa
    }

    @staticmethod
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

        # Make copy, any str values will be replaced
        new_param_dict = copy.copy(param_dict)

        # Mean of two lowest frequencies
        mean_low_freq = np.mean(np.sort(experiment.ac_freqs)[:2])

        guessdict = {
            # Mean of smallest ac angular frequencies
            'tau': 1. / (2. * np.pi * mean_low_freq),
            # Smallest real susceptibility
            'chi_S': np.max([np.min(experiment.real_sus), 0.]),
            # Range of real susceptibilities
            'chi_T': np.max(experiment.real_sus) - np.min(experiment.real_sus)
        }

        # Replace 'guess' with relevant guess
        for var, val in param_dict.items():
            if isinstance(val, str) and val.lower() == 'guess':
                new_param_dict[var] = guessdict[var]

        return new_param_dict

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
        ------
        ValueError
            If required model parameters in self.final_var_values are undefined
        '''

        tau = self.final_var_values['tau']

        if None in [tau]:
            _error = '\n Error: Cannot calculate ln(tau) expectation value '
            _error += 'tau is undefined!'
            raise ValueError(_error)

        return self.calc_lntau_expect(tau)

    @staticmethod
    def calc_lntau_expect(tau: ArrayLike) -> float | NDArray:
        '''
        Calculates expectation value of ln(tau)

        Parameters
        ----------
        tau: array_like
            Relaxation time tau used in Debye model

        Returns
        -------
        float | ndarray of floats
            <ln(tau)> value(s) in ln(seconds)
        '''

        return np.log(tau)

    def _calc_lntau_fit_ul(self) -> list[float]:
        '''
        Calculates upper and lower bounds of ln(tau) from uncertainty\n
        in fitted parameters, rather than from ln(tau) distribution.

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

        tau = self.final_var_values['tau']

        if 'tau' in self.fit_stdev:
            tau_std = self.fit_stdev['tau']
        else:
            tau_std = 0.

        if tau is None:
            _error = '\n Error: Cannot calculate ln(tau) bounds '
            _error += 'tau is undefined!'
            raise ValueError(_error)
        elif tau_std is None:
            _error = '\n Error: Cannot calculate ln(tau) bounds '
            _error += 'tau standard deviation is undefined!'
            raise ValueError(_error)

        return self.calc_lntau_fit_ul(tau, tau_std)

    @staticmethod
    def calc_lntau_fit_ul(tau: ArrayLike,
                          tau_std: ArrayLike) -> list[float]:
        '''
        Calculates upper and lower bounds of ln(tau) from uncertainty\n
        in fitted parameters, rather than from ln(tau) distribution.

        Parameters
        ----------
        tau: array_like
            Relaxation time tau used in Debye model
        tau_std: array_like
            Standard deviation of tau, can be zero
        Returns
        -------
        list[float]
            lower and upper bounds of ln(tau) from fit uncertainty in fitted
            parameters (upper > lower)
        '''
        tau = np.asarray(tau)
        tau_std = np.asarray(tau_std)

        warnings.filterwarnings('ignore', 'invalid value encountered in log')
        bounds = np.array([np.log(tau + tau_std), np.log(tau - tau_std)]).T

        bounds = np.sort(bounds, axis=-1)

        warnings.filterwarnings('default', 'invalid value encountered in log')

        return bounds.T.tolist()

    def _calc_lntau_stdev(self) -> float:
        '''
        Calculates standard deviation of ln(tau)

        Parameters
        ----------
        None

        Returns
        -------
        float
            0. as no standard deviation is associated with this model
        '''

        return self.calc_lntau_stdev()

    @staticmethod
    def calc_lntau_stdev() -> float:
        '''
        Calculates standard deviation of ln(tau)

        Parameters
        ----------
        None

        Returns
        -------
        float
            0. as no standard deviation is associated with this model
        '''

        return 0.

    @staticmethod
    def model(parameters: dict[str, float],
              ac_freq_ang: list[float]) -> tuple[list[float], list[float]]:
        '''
        Computes Debye model function of ac suceptibility

        Parameters
        ----------
        parameters: dict[str, float],
            Keys are class.PARNAMES, values are float values
        ac_freq_ang: list[float]
            angular ac frequencies at which model will be evaluated

        Returns
        -------
        list[float]
            real susceptibility
        list[float]
            imaginary susceptibility

        '''

        tau = parameters['tau']
        chi_S = parameters['chi_S']
        chi_T = parameters['chi_T']

        upper = chi_T - chi_S
        lower = 1 + (1j * ac_freq_ang * tau)

        func = chi_S + (upper / lower)

        real = np.real(func)
        imag = -np.imag(func)

        return real.tolist(), imag.tolist()


class GeneralisedDebyeModel(Model):
    '''
    Generalised Debye Model of AC Susceptibility

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
    flat_thresh: float
        Threshold for fit of susceptibility data to X''= m * nu + b\n
        Used in fit_to()\n
        When root sum of squared differences between X''_flat and X''_exp\n
        is below flat_thresh, the fit is marked as failed.
    fit_status: bool
        True if fit successful, else false
    '''

    #: Model Name
    NAME = 'Generalised Debye'

    #: Display name for interactive buttons
    DISP_NAME = copy.copy(NAME)

    #: Model Parameter name strings
    PARNAMES = [
        'tau', 'chi_S', 'chi_T', 'alpha'
    ]

    #: Model parameter bounds
    BOUNDS = {
        'tau': [0., np.inf],
        'chi_S': [0., np.inf],
        'chi_T': [0., np.inf],
        'alpha': [0., 1.],
    }

    #: Model Parameter mathmode name strings
    VARNAMES_MM = {
        'tau': r'$\tau$',
        'lntau_expect': r'$\langle \ln \tau \rangle$',
        'lntau_stdev': r'$\sigma_{\ln \tau}$',
        'chi_S': r'$\chi_\mathregular{S}$',
        'chi_T': r'$\chi_\mathregular{T}$',
        'alpha': r'$\alpha$',
    }

    UNITS = {
        'tau': r's',
        'chi_S': r'cm^3 mol^-1',
        'chi_T': r'cm^3 mol^-1',
        'alpha': r'',
    }

    UNITS_MM = {
        'tau': r'$\mathregular{s}$',
        'chi_S': r'\mathregular{cm}^\mathregular{3} \mathregular{mol}^\mathregular{-1}$', # noqa
        'chi_T': r'\mathregular{cm}^\mathregular{3} \mathregular{mol}^\mathregular{-1}$', # noqa
        'alpha': r'',
    }

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
        ------
        ValueError
            If required model parameters in self.final_var_values are undefined
        '''

        tau = self.final_var_values['tau']

        if None in [tau]:
            _error = '\n Error: Cannot calculate ln(tau) expectation value '
            _error += 'tau is undefined!'
            raise ValueError(_error)

        return self.calc_lntau_expect(tau)

    @staticmethod
    def calc_lntau_expect(tau: ArrayLike) -> float | NDArray:
        '''
        Calculates expectation value of ln(tau)

        Parameters
        ----------
        tau: array_like
            Relaxation time tau used in Generalised Debye model

        Returns
        -------
        float | NDArray
            <ln(tau)> value(s) in ln(seconds)
        '''
        return np.log(tau)

    def _calc_lntau_fit_ul(self) -> list[float]:
        '''
        Calculates upper and lower bounds of ln(tau) from uncertainty\n
        in fitted parameters, rather than from ln(tau) distribution.

        Parameters
        ----------
        None

        Returns
        -------
        list[float]
            lower and upper bounds of ln(tau) from fit uncertainty in fitted\n
            parameters (upper > lower)

        Raises
        ------
        ValueError
            If required model parameters in self.final_var_values
            or self.fit_stdev are undefined
        '''

        tau = self.final_var_values['tau']

        if 'tau' in self.fit_stdev:
            tau_std = self.fit_stdev['tau']
        else:
            tau_std = 0.

        if tau is None:
            _error = '\n Error: Cannot calculate ln(tau) bounds '
            _error += 'tau is undefined!'
            raise ValueError(_error)
        elif tau_std is None:
            _error = '\n Error: Cannot calculate ln(tau) bounds '
            _error += 'tau standard deviation is undefined!'
            raise ValueError(_error)

        return self.calc_lntau_fit_ul(tau, tau_std)

    @staticmethod
    def calc_lntau_fit_ul(tau: ArrayLike,
                          tau_std: ArrayLike) -> list[float | NDArray]:
        '''
        Calculates upper and lower bounds of ln(tau) from uncertainty\n
        in fitted parameters, rather than from ln(tau) distribution.

        Parameters
        ----------
        tau: array_like
            Relaxation time tau used in Generalised Debye model
        tau_std: array_like
            Standard deviation of tau, can be zero
        Returns
        -------
        list[float | ndarray of floats]
            lower and upper bounds of ln(tau) from fit uncertainty in fitted\n
            parameters (upper > lower)
        '''

        tau = np.asarray(tau)
        tau_std = np.asarray(tau_std)

        warnings.filterwarnings('ignore', 'invalid value encountered in log')

        bounds = np.array([np.log(tau + tau_std), np.log(tau - tau_std)]).T

        bounds = np.sort(bounds, axis=-1)

        warnings.filterwarnings('default', 'invalid value encountered in log')

        return bounds.T.tolist()

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
        ------
        ValueError
            If required model parameters in self.final_var_values are undefined
        '''

        alpha = self.final_var_values['alpha']

        if alpha is None:
            _error = '\n Error: Cannot calculate ln(tau) standard deviation '
            _error += 'alpha is undefined!'
            raise ValueError(_error)

        return self.calc_lntau_stdev(alpha)

    @staticmethod
    def calc_lntau_stdev(alpha: float) -> float:
        '''
        Calculates standard deviation of ln(tau)

        Parameters
        ----------
        alpha: float
            Alpha value from Generalised Debye Model

        Returns
        -------
        float
            Standard deviation of ln(tau) in ln(seconds)
        '''

        stdev = np.sqrt((1. / (1 - alpha)**2 - 1.) * np.pi**2 / 3.)
        return stdev

    @staticmethod
    def model(parameters: dict[str, float],
              ac_freq_ang: list[float]) -> tuple[list[float], list[float]]:
        '''
        Computes Generalised Debye model function of ac suceptibility

        Parameters
        ----------
        parameters: dict[str, float],
            Keys are class.PARNAMES, values are float values
        ac_freq_ang: list[float]
            angular ac frequencies at which model will be evaluated

        Returns
        -------
        list[float]
            real susceptibility
        list[float]
            imaginary susceptibility
        '''

        tau = parameters['tau']
        chi_S = parameters['chi_S']
        chi_T = parameters['chi_T']
        alpha = parameters['alpha']

        upper = chi_T - chi_S
        lower = 1 + (1j * ac_freq_ang * tau)**(1 - alpha)

        func = chi_S + (upper / lower)

        real = np.real(func)
        imag = -np.imag(func)

        return real.tolist(), imag.tolist()

    @staticmethod
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

        # Make copy, any str values will be replaced
        new_param_dict = copy.copy(param_dict)

        # Mean of two lowest frequencies
        mean_low_freq = np.mean(np.sort(experiment.ac_freqs)[:2])

        guessdict = {
            # Mean of smallest ac angular frequencies
            'tau': 1. / (2. * np.pi * mean_low_freq),
            # Smallest real susceptibility
            'chi_S': np.max([np.min(experiment.real_sus), 0.]),
            # Range of real susceptibilities
            'chi_T': np.max(experiment.real_sus) - np.min(experiment.real_sus),
            'alpha': 0.1
        }

        # Replace 'guess' with relevant guess
        for var, val in param_dict.items():
            if isinstance(val, str) and val.lower() == 'guess':
                new_param_dict[var] = guessdict[var]

        return new_param_dict


class HavriliakNegamiModel(Model):
    '''
    Havriliak-Negami Model of AC Susceptibility

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
    flat_thresh: float
        Threshold for fit of susceptibility data to X''= m * nu + b\n
        Used in fit_to()\n
        When root sum of squared differences between X''_flat and X''_exp\n
        is below flat_thresh, the fit is marked as failed.
    fit_status: bool
        True if fit successful, else false
    '''
    #: Model Name
    NAME = 'Havriliak-Negami'

    #: Display name for interactive buttons
    DISP_NAME = copy.copy(NAME)

    #: Model Parameter name strings
    PARNAMES = [
        'tau', 'chi_S', 'chi_T', 'alpha', 'gamma'
    ]

    #: Model paramater bounds
    BOUNDS = {
        'tau': [0., np.inf],
        'chi_S': [0., np.inf],
        'chi_T': [0., np.inf],
        'alpha': [0., 1.],
        'gamma': [0., np.inf]
    }

    #: Model Parameter mathmode name strings
    VARNAMES_MM = {
        'tau': r'$\tau$',
        'lntau_expect': r'$\langle \ln \tau \rangle$',
        'lntau_stdev': r'$\sigma_{\ln \tau}$',
        'chi_S': r'$\chi_\mathregular{S}$',
        'chi_T': r'$\chi_\mathregular{T}$',
        'alpha': r'$\alpha$',
        'gamma': r'$\gamma$',
    }

    UNITS = {
        'tau': r's',
        'chi_S': r'cm^3 mol^-1',
        'chi_T': r'cm^3 mol^-1',
        'alpha': r'',
        'gamma': r'',
    }

    UNITS_MM = {
        'tau': r'$\mathregular{s}$',
        'chi_S': r'\mathregular{cm}^\mathregular{3} \mathregular{mol}^\mathregular{-1}$', # noqa
        'chi_T': r'\mathregular{cm}^\mathregular{3} \mathregular{mol}^\mathregular{-1}$', # noqa
        'alpha': r'',
        'gamma': r'',
    }

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
        ------
        ValueError
            If required model parameters in self.final_var_values are undefined
        '''

        tau = self.final_var_values['tau']
        alpha = self.final_var_values['alpha']
        gamma = self.final_var_values['gamma']

        if None in [tau, alpha, gamma]:
            _error = '\n Error: Cannot calculate ln(tau) expectation value '
            _error += 'tau, alpha, or gamma is undefined!'
            raise ValueError(_error)

        return self.calc_lntau_expect(tau, alpha, gamma)

    @staticmethod
    def calc_lntau_expect(tau: ArrayLike, alpha: ArrayLike,
                          gamma: ArrayLike) -> float | NDArray:
        '''
        Calculates expectation value of ln(tau)

        Parameters
        ----------
        tau: array_like
            Relaxation time tau used in Havriliak-Negami Model
        alpha: array_like
            Alpha value used in Havriliak-Negami Model
        gamma: array_like
            Gamma value used in Havriliak-Negami Model

        Returns
        -------
        float | ndarray of floats
            <ln(tau)> value(s) in ln(seconds)
        '''
        warnings.filterwarnings('ignore', 'invalid value encountered in log')
        value = np.log(tau) + (np.euler_gamma + digamma(gamma)) / (1 - alpha)
        warnings.filterwarnings('default', 'invalid value encountered in log')
        return value

    def _calc_lntau_fit_ul(self) -> list[float]:
        '''
        Calculates upper and lower bounds of ln(tau) from uncertainty\n
        in fitted parameters, rather than from ln(tau) distribution.

        Parameters
        ----------
        None

        Returns
        -------
        list[float]
            lower and upper bounds of ln(tau) from fit uncertainty in fitted\n
            parameters (upper > lower)

        Raises
        ------
        ValueError
            If required model parameters in self.final_var_values
            or self.fit_stdev are undefined
        '''

        tau = self.final_var_values['tau']
        alpha = self.final_var_values['alpha']
        gamma = self.final_var_values['gamma']

        if 'tau' in self.fit_stdev:
            tau_std = self.fit_stdev['tau']
        else:
            tau_std = 0.

        if 'alpha' in self.fit_stdev:
            alpha_std = self.fit_stdev['alpha']
        else:
            alpha_std = 0.

        if 'gamma' in self.fit_stdev:
            gamma_std = self.fit_stdev['gamma']
        else:
            gamma_std = 0.

        if None in [tau, alpha, gamma]:
            _error = '\n Error: Cannot calculate ln(tau) bounds '
            _error += 'tau, alpha, or gamma is undefined!'
            raise ValueError(_error)
        elif None in [tau_std, alpha_std, gamma_std]:
            _error = '\n Error: Cannot calculate  ln(tau) bounds '
            _error += 'tau, alpha, or gamma standard deviation is undefined!'
            raise ValueError(_error)

        bounds = self.calc_lntau_fit_ul(
            tau, alpha, gamma, tau_std, alpha_std, gamma_std
        )

        return bounds

    @staticmethod
    def calc_lntau_fit_ul(tau: ArrayLike, alpha: ArrayLike, gamma: ArrayLike,
                          tau_std: ArrayLike, alpha_std: ArrayLike,
                          gamma_std: ArrayLike) -> list[float | NDArray]:
        '''
        Calculates upper and lower bounds of ln(tau) from uncertainty\n
        in fitted parameters, rather than from ln(tau) distribution.

        Parameters
        ----------
        tau: array_like
            Relaxation time tau used in Havriliak-Negami Model
        alpha: array_like
            Alpha value used in Havriliak-Negami Model
        gamma: array_like
            Gamma value used in Havriliak-Negami Model
        tau_std: array_like
            Standard deviation of relaxation time tau used in\n
            Havriliak-Negami Model, can be zero
        alpha_std: array_like
            Standard deviation of alpha value used in Havriliak-Negami Model,\n
            can be zero
        gamma_std: array_like
            Standard deviation of gamma value used in Havriliak-Negami Model,\n
            can be zero
        Returns
        -------
        list[float] | ndarray of floats
            lower and upper bounds of ln(tau) from fit uncertainty in fitted\n
            parameters [lower, upper]
        '''

        tau = np.asarray(tau)
        tau_std = np.asarray(tau_std)
        gamma = np.asarray(gamma)
        gamma_std = np.asarray(gamma_std)
        alpha = np.asarray(alpha)
        alpha_std = np.asarray(alpha_std)

        if 0 <= gamma <= 1:

            upper = HavriliakNegamiModel.calc_lntau_expect(
                tau + tau_std,
                alpha - alpha_std,
                gamma + gamma_std
            )

            lower = HavriliakNegamiModel.calc_lntau_expect(
                tau - tau_std,
                alpha + alpha_std,
                gamma - gamma_std
            )

        elif gamma > 1:
            upper = HavriliakNegamiModel.calc_lntau_expect(
                tau + tau_std,
                alpha - alpha_std,
                gamma + gamma_std
            )

            lower = HavriliakNegamiModel.calc_lntau_expect(
                tau - tau_std,
                alpha + alpha_std,
                gamma - gamma_std
            )

        bounds = np.array([upper, lower]).T

        bounds = np.sort(bounds, axis=-1)

        return bounds.T.tolist()

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
        ------
        ValueError
            If required model parameters in self.final_var_values are undefined
        '''

        alpha = self.final_var_values['alpha']
        gamma = self.final_var_values['gamma']

        if None in [alpha, gamma]:
            _error = 'Error: Cannot calculate ln(tau) standard deviation'
            _error += 'alpha and/or gamma undefined!'
            raise ValueError(_error)

        return self.calc_lntau_stdev(alpha, gamma)

    @staticmethod
    def calc_lntau_stdev(alpha: ArrayLike,
                         gamma: ArrayLike) -> float | NDArray:
        '''
        Calculates standard deviation of ln(tau)

        Parameters
        ----------
        alpha: array_like
            Alpha value used in Havriliak-Negami Model
        gamma: array_like
            Gamma value used in Havriliak-Negami Model

        Returns
        -------
        float | ndarray of floats
            Standard deviation of ln(tau) in ln(seconds)
        '''

        variance = polygamma(1, gamma) / (1 - alpha)**2
        variance += np.pi**2 / (6 * (1 - alpha)**2)
        variance -= np.pi**2 / 3

        return np.sqrt(variance)

    @staticmethod
    def model(parameters: dict[str, float],
              ac_freq_ang: list[float]) -> tuple[list[float], list[float]]:
        '''
        Computes Havriliak-Negami model function of ac suceptibility

        Parameters
        ----------
        parameters: dict[str, float],
            Keys are class.PARNAMES, values are float values
        ac_freq_ang: list[float]
            angular ac frequencies at which model will be evaluated

        Returns
        -------
        list[float]
            real susceptibility
        list[float]
            imaginary susceptibility
        '''

        tau = parameters['tau']
        chi_S = parameters['chi_S']
        chi_T = parameters['chi_T']
        alpha = parameters['alpha']
        gamma = parameters['gamma']

        upper = chi_T - chi_S
        lower = (1 + (1j * ac_freq_ang * tau)**(1 - alpha))**gamma

        func = chi_S + (upper / lower)

        real = np.real(func)
        imag = -np.imag(func)

        return real.tolist(), imag.tolist()

    @staticmethod
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

        # Make copy, any str values will be replaced
        new_param_dict = copy.copy(param_dict)

        # Mean of two lowest frequencies
        mean_low_freq = np.mean(np.sort(experiment.ac_freqs)[:2])

        guessdict = {
            # Mean of smallest ac angular frequencies
            'tau': 1. / (2. * np.pi * mean_low_freq),
            # Smallest real susceptibility
            'chi_S': np.max([np.min(experiment.real_sus), 0.]),
            # Range of real susceptibilities
            'chi_T': np.max(experiment.real_sus) - np.min(experiment.real_sus),
            'alpha': 0.1,
            'gamma': 0.9
        }

        # Replace 'guess' with relevant guess
        for var, val in param_dict.items():
            if isinstance(val, str) and val.lower() == 'guess':
                new_param_dict[var] = guessdict[var]

        return new_param_dict

    @classmethod
    def residual_from_float_list(cls, new_vals: list[float],
                                 fit_vars: dict[str, float],
                                 fix_vars: dict[str, float],
                                 ac_freq_ang: list[float],
                                 true_real_sus: list[float],
                                 true_imag_sus: list[float]) -> list[float]:
        '''
        Reimplementation for coupled bounds required for this model

        Wrapper for `residuals` method, takes new values from fitting routine
        which provides list[float], to construct new fit_vals dict, then
        runs `residuals` method.

        Parameters
        ----------

        fit_vars: dict[str, float]
            Parameter to fit in model function\n
            keys are PARNAMES, values are initial guesses
        fix_vars: dict[str, float]
            Parameters which remain fixed in model function\n
            keys are PARNAMES, values are float values
        ac_freq_ang: list[float]
            Angular AC Frequencies
        true_real_sus: list[float]
            true (experimental) values of real part of susceptibility
        true_imag_sus: list[float]
            true (experimental) values of imaginary part of susceptibility

        Returns
        -------
        list[float]
            Residuals, real, then imaginary
        '''

        # Swap fit values for new values from fit routine
        new_fit_vars = {
            name: guess
            for guess, name in zip(new_vals, fit_vars.keys())
        }

        # And make combined dict of fit and fixed
        # variable names (keys) and values
        all_vars = {**fix_vars, **new_fit_vars}

        residuals = np.array(cls.residuals(
            all_vars, ac_freq_ang, true_real_sus, true_imag_sus
        ))

        # Enforce gamma * alpha < 1 by inflating residual if outside range
        if ((1 - all_vars['alpha']) * all_vars['gamma']) > 1.:
            residuals *= 2

        return residuals.tolist()


class ColeDavidsonModel(Model):
    '''
    Cole-Davidson Model of AC Susceptibility

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
    flat_thresh: float
        Threshold for fit of susceptibility data to X''= m * nu + b\n
        Used in fit_to()\n
        When root sum of squared differences between X''_flat and X''_exp\n
        is below flat_thresh, the fit is marked as failed.
    fit_status: bool
        True if fit successful, else false
    '''
    #: Model Name
    NAME = 'Cole-Davidson'

    #: Display name for interactive buttons
    DISP_NAME = copy.copy(NAME)

    #: Model Parameter name strings
    PARNAMES = [
        'tau', 'chi_S', 'chi_T', 'gamma'
    ]

    #: Model paramater bounds
    BOUNDS = {
        'tau': [0., np.inf],
        'chi_S': [0., np.inf],
        'chi_T': [0., np.inf],
        'gamma': [0., 1]
    }

    #: Model Parameter mathmode name strings
    VARNAMES_MM = {
        'tau': r'$\tau$',
        'lntau_expect': r'$\langle \ln \tau \rangle$',
        'lntau_stdev': r'$\sigma_{\ln \tau}$',
        'chi_S': r'$\chi_\mathregular{S}$',
        'chi_T': r'$\chi_\mathregular{T}$',
        'gamma': r'$\gamma$',
    }

    UNITS = {
        'tau': r's',
        'chi_S': r'cm^3 mol^-1',
        'chi_T': r'cm^3 mol^-1',
        'gamma': r'',
    }

    UNITS_MM = {
        'tau': r'$\mathregular{s}$',
        'chi_S': r'\mathregular{cm}^\mathregular{3} \mathregular{mol}^\mathregular{-1}$', # noqa
        'chi_T': r'\mathregular{cm}^\mathregular{3} \mathregular{mol}^\mathregular{-1}$', # noqa
        'gamma': r'',
    }

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
        ------
        ValueError
            If required model parameters in self.final_var_values are undefined
        '''

        tau = self.final_var_values['tau']
        gamma = self.final_var_values['gamma']

        if None in [tau, gamma]:
            _error = '\n Error: Cannot calculate ln(tau) expectation value '
            _error += 'tau or gamma is undefined!'
            raise ValueError(_error)

        return self.calc_lntau_expect(tau, gamma)

    @staticmethod
    def calc_lntau_expect(tau: ArrayLike,
                          gamma: ArrayLike) -> float | NDArray:
        '''
        Calculates expectation value of ln(tau)

        Parameters
        ----------
        tau: array_like
            Relaxation time value for Cole-Davidson Model
        gamma: array_like
            Gamma value for Cole-Davidson Model

        Returns
        -------
        float | ndarray of floats
            <ln(tau)> value(s) in ln(seconds)
        '''

        warnings.filterwarnings('ignore', 'invalid value encountered in log')
        value = np.log(tau) + np.euler_gamma + digamma(gamma)
        warnings.filterwarnings('default', 'invalid value encountered in log')
        return value

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

        tau = self.final_var_values['tau']
        gamma = self.final_var_values['gamma']

        if 'tau' in self.fit_stdev:
            tau_std = self.fit_stdev['tau']
        else:
            tau_std = 0.

        if 'gamma' in self.fit_stdev:
            gamma_std = self.fit_stdev['gamma']
        else:
            gamma_std = 0.

        if None in [tau, gamma]:
            _error = '\n Error: Cannot calculate ln(tau) bounds '
            _error += 'tau or gamma is undefined!'
            raise ValueError(_error)

        if None in [tau_std, gamma_std]:
            _error = '\n Error: Cannot calculate ln(tau) bounds '
            _error += 'tau or gamma standard deviation is undefined!'
            raise ValueError(_error)

        bounds = self.calc_lntau_fit_ul(tau, gamma, tau_std, gamma_std)

        return bounds

    @staticmethod
    def calc_lntau_fit_ul(tau: ArrayLike, gamma: ArrayLike, tau_std: ArrayLike,
                          gamma_std: ArrayLike) -> list[float | NDArray]:
        '''
        Calculates upper and lower bounds of ln(tau) from fit uncertainty
        in fitted parameters

        Parameters
        ----------
        tau: array_like
            Relaxation time value for Cole-Davidson Model
        gamma: array_like
            Gamma value for Cole-Davidson Model
        tau_std: array_like
            Standard deviation of relaxation time tau used in\n
            Cole-Davidson Model, can be zero
        gamma_std: array_like
            Standard deviation of gamma value used in Cole-Davidson Model,\n
            can be zero

        Returns
        -------
        list[float | ndarray of floats]
            upper and lower bounds of ln(tau) from fit uncertainty in fitted
            parameters (upper > lower)
        '''

        tau = np.asarray(tau)
        tau_std = np.asarray(tau_std)
        gamma = np.asarray(gamma)
        gamma_std = np.asarray(gamma_std)

        upper = ColeDavidsonModel.calc_lntau_expect(
            tau + tau_std,
            gamma + gamma_std
        )

        lower = ColeDavidsonModel.calc_lntau_expect(
            tau - tau_std,
            gamma - gamma_std
        )

        bounds = np.array([upper, lower]).T

        bounds = np.sort(bounds, axis=-1)

        return bounds.T.tolist()

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
        ------
        ValueError
            If required model parameters in self.final_var_values are undefined
        '''

        gamma = self.final_var_values['gamma']

        if None in [gamma]:
            _error = 'Error: Cannot calculate ln(tau) standard deviation'
            _error += 'gamma is undefined!'
            raise ValueError(_error)

        return self.calc_lntau_stdev(gamma)

    @staticmethod
    def calc_lntau_stdev(gamma: float) -> float:
        '''
        Calculates standard deviation of ln(tau)

        Parameters
        ----------
        gamma: float
        Gamma value for Cole-Davidson Model

        Returns
        -------
        float
            Standard deviation of ln(tau) in ln(seconds)
        '''
        variance = polygamma(1, gamma)
        variance -= np.pi**2 / 6

        return np.sqrt(variance)

    @staticmethod
    def model(parameters: dict[str, float],
              ac_freq_ang: list[float]) -> tuple[list[float], list[float]]:
        '''
        Computes Cole-Davidson model function of ac suceptibility

        Parameters
        ----------
        parameters: dict[str, float],
            Keys are class.PARNAMES, values are float values
        ac_freq_ang: list[float]
            angular ac frequencies at which model will be evaluated

        Returns
        -------
        list[float]
            real susceptibility
        list[float]
            imaginary susceptibility
        '''

        tau = parameters['tau']
        chi_S = parameters['chi_S']
        chi_T = parameters['chi_T']
        gamma = parameters['gamma']

        upper = chi_T - chi_S
        lower = (1 + (1j * ac_freq_ang * tau))**gamma

        func = chi_S + (upper / lower)

        real = np.real(func)
        imag = -np.imag(func)

        return real.tolist(), imag.tolist()

    @staticmethod
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

        # Make copy, any str values will be replaced
        new_param_dict = copy.copy(param_dict)

        # Mean of two lowest frequencies
        mean_low_freq = np.mean(np.sort(experiment.ac_freqs)[:2])

        guessdict = {
            # Mean of smallest ac angular frequencies
            'tau': 1. / (2. * np.pi * mean_low_freq),
            # Smallest real susceptibility
            'chi_S': np.max([np.min(experiment.real_sus), 0.]),
            # Range of real susceptibilities
            'chi_T': np.max(experiment.real_sus) - np.min(experiment.real_sus),
            'gamma': 0.9
        }

        # Replace 'guess' with relevant guess
        for var, val in param_dict.items():
            if isinstance(val, str) and val.lower() == 'guess':
                new_param_dict[var] = guessdict[var]

        return new_param_dict

    @classmethod
    def residual_from_float_list(cls, new_vals: list[float],
                                 fit_vars: dict[str, float],
                                 fix_vars: dict[str, float],
                                 ac_freq_ang: list[float],
                                 true_real_sus: list[float],
                                 true_imag_sus: list[float]) -> list[float]:
        '''
        Reimplementation for coupled bounds required for this model

        Wrapper for `residuals` method, takes new values from fitting routine
        which provides list[float], to construct new fit_vals dict, then
        runs `residuals` method.

        Parameters
        ----------

        fit_vars: dict[str, float]
            Parameter to fit in model function\n
            keys are PARNAMES, values are initial guesses
        fix_vars: dict[str, float]
            Parameters which remain fixed in model function\n
            keys are PARNAMES, values are float values
        ac_freq_ang: list[float]
            Angular AC Frequencies
        true_real_sus: list[float]
            true (experimental) values of real part of susceptibility
        true_imag_sus: list[float]
            true (experimental) values of imaginary part of susceptibility

        Returns
        -------
        list[float]
            Residuals, real, then imaginary
        '''

        # Swap fit values for new values from fit routine
        new_fit_vars = {
            name: guess
            for guess, name in zip(new_vals, fit_vars.keys())
        }

        # And make combined dict of fit and fixed
        # variable names (keys) and values
        all_vars = {**fix_vars, **new_fit_vars}

        residuals = np.array(cls.residuals(
            all_vars, ac_freq_ang, true_real_sus, true_imag_sus
        ))

        return residuals.tolist()


class DoubleGDebyeModel(Model):
    '''
    Double Generalised Debye Model of AC Susceptibility

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
    flat_thresh: float
        Threshold for fit of susceptibility data to X''= m * nu + b\n
        Used in fit_to()\n
        When root sum of squared differences between X''_flat and X''_exp\n
        is below flat_thresh, the fit is marked as failed.
    fit_status: bool
        True if fit successful, else false
    '''
    #: Model Name
    NAME = 'Double Generalised Debye'

    #: Display name for interactive buttons
    DISP_NAME = copy.copy(NAME)

    #: Model Parameter name strings
    PARNAMES = [
        'tau1', 'alpha1', 'D_chi1', 'tau2', 'alpha2', 'D_chi2', 'chi_total'
    ]

    #: Model Parameter bounds
    BOUNDS = {
        'tau1': [0., np.inf],
        'alpha1': [0., 1],
        'D_chi1': [0., np.inf],
        'tau2': [0., np.inf],
        'alpha2': [0., 1],
        'D_chi2': [0., np.inf],
        'chi_total': [0., np.inf],
    }

    #: Model Parameter mathmode name strings
    VARNAMES_MM = {
        'tau1': r'$\tau_\mathregular{1}$',
        'alpha1': r'$\alpha_\mathregular{1}$',
        'D_chi1': r'$\Delta\chi_\mathregular{1}$',
        'tau2': r'$\tau_\mathregular{2}$',
        'alpha2': r'$\alpha_\mathregular{2}$',
        'D_chi2': r'$\Delta\chi_\mathregular{2}$',
        'chi_total': r'$\chi_\mathregular{Total}$'
    }

    UNITS = {
        'tau1': r's',
        'tau2': r's',
        'D_chi1': r'cm^3 mol^-1',
        'D_chi2': r'cm^3 mol^-1',
        'alpha1': r'',
        'alpha2': r'',
        'chi_total': r'cm^3 mol^-1'
    }

    UNITS_MM = {
        'tau1': r'$\mathregular{s}$',
        'tau2': r'$\mathregular{s}$',
        'D_chi1': r'\mathregular{cm}^\mathregular{3} \mathregular{mol}^\mathregular{-1}$', # noqa
        'D_chi2': r'\mathregular{cm}^\mathregular{3} \mathregular{mol}^\mathregular{-1}$', # noqa
        'alpha1': r'',
        'alpha2': r'',
        'chi_total': r'\mathregular{cm}^\mathregular{3} \mathregular{mol}^\mathregular{-1}$', # noqa
    }

    def __init__(self, fit_vars: dict[str, float | str],
                 fix_vars: dict[str, float | str], experiment: 'Experiment'):

        # Initialise attributes required by Model superclass to default values
        super().__init__(fit_vars, fix_vars, experiment)

        # Set as list of None, since here they have multiple values one
        # for tau1, one for tau2
        self._lntau_expect = [None, None]
        self._lntau_fit_ul = [None, None]
        self._lntau_stdev = [None, None]

        return

    # Redefined for list
    @property
    def lntau_expect(self) -> list[float]:
        '''
        Expectation value of ln(tau)
        '''
        # If not calculated yet, then calculate
        if None in self._lntau_expect:
            self.lntau_expect = self._calc_lntau_expect()
        return self._lntau_expect

    @lntau_expect.setter
    def lntau_expect(self, value):
        if isinstance(value, list):
            self._lntau_expect = value
        else:
            raise TypeError
        return

    # Redefined for list
    @property
    def lntau_fit_ul(self) -> list[list[float]]:
        '''
        Expectation value of ln(tau)
        '''
        # If not calculated yet, then calculate
        if None in self._lntau_fit_ul:
            self._lntau_fit_ul = self._calc_lntau_fit_ul()
        return self._lntau_fit_ul

    @lntau_fit_ul.setter
    def lntau_fit_ul(self, value):
        if isinstance(value, list):
            self._lntau_fit_ul = value
        else:
            raise TypeError
        return

    # Redefined for list
    @property
    def lntau_stdev(self) -> list[float]:
        '''
        Standard deviation of ln(tau)
        '''
        # If not calculated yet, then calculate
        if None in self._lntau_stdev:
            self.lntau_stdev = self._calc_lntau_stdev()
        return self._lntau_stdev

    @lntau_stdev.setter
    def lntau_stdev(self, value):
        if isinstance(value, list):
            self._lntau_stdev = value
        else:
            raise TypeError
        return

    @staticmethod
    def model(parameters: dict[str, float],
              ac_freq_ang: list[float]) -> tuple[list[float], list[float]]:
        '''
        Computes model function of ac suceptibility for double
        generalised debye

        Parameters
        ----------
        parameters: dict[str, float],
            Keys are class.PARNAMES, values are float value
        ac_freq_ang: list[float]
            angular ac frequencies at which model will be evaluated

        Returns
        -------
        list[float]
            real susceptibility
        list[float]
            imaginary susceptibility

        '''
        tau1 = parameters['tau1']
        delta_chi1 = parameters['D_chi1']
        alpha1 = parameters['alpha1']
        tau2 = parameters['tau2']
        delta_chi2 = parameters['D_chi2']
        alpha2 = parameters['alpha2']
        chi_total = parameters['chi_total']

        func = chi_total
        func += delta_chi1 / (
            1 + np.power((ac_freq_ang * tau1 * 1j), (1. - alpha1))
        )
        func += delta_chi2 / (
            1 + np.power((ac_freq_ang * tau2 * 1j), (1. - alpha2))
        )

        return np.real(func).tolist(), np.abs(np.imag(func)).tolist()

    @staticmethod
    def discard(params: dict[str, float], ac_freq_ang: list[float]) -> bool:
        '''
        Decides whether fits should be discarded based on following criteria

        1. tau^-1 < smallest ac frequency

        2. tau^-1 > largest ac frequency

        where both tau_1 and tau_2 (corresponding to the two peaks) are
        checked

        Parameters
        ----------
        fit_param: dict[str, float]
            keys are PARNAMES, values are fitted parameter values
        ac_freq_ang: list[float]
            Angular ac frequencies

        Returns
        -------
        bool
            True if point should be discarded, else False
        '''

        to_discard = False

        if 1. / (params['tau1']) < np.min(ac_freq_ang):
            to_discard = True
        elif 1. / (params['tau1']) > np.max(ac_freq_ang):
            to_discard = True
        elif 1. / (params['tau2']) < np.min(ac_freq_ang):
            to_discard = True
        elif 1. / (params['tau2']) > np.max(ac_freq_ang):
            to_discard = True
        return to_discard

    @staticmethod
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

        # Make copy, any str values will be replaced
        new_param_dict = copy.copy(param_dict)

        '''
        Let x = largest frequency at turning point of imaginary susceptibility
                with largest abs value

        Parameters and guesses are

        tau_1 - inverse of frequency for turning point with 2nd largest
                imaginary susceptibility

        D_chi_1 - 2/3 * range of real susceptibility

        alpha_1 - 0.1

        tau_2 - inverse of frequency for turning point with largest
                imaginary susceptibility

        D_chi_2 - 1/3 * range of real susceptibility

        alpha_2 - 0.01

        chi_total - minimum real susceptibility
        '''

        # Calculate gradient of imaginary susceptibility and retrieve indexes
        # where there is a change of sign.
        dimag_sus = np.gradient(experiment.imag_sus)
        zero_crossings_freq = np.where(np.diff(np.sign(dimag_sus)))

        # Get frequency for turning point with largest imaginary
        # susceptibility
        imag_sus_cross = experiment.imag_sus[zero_crossings_freq]
        indices = np.argsort(-imag_sus_cross)
        ac_freq_cross = experiment.ac_freqs[zero_crossings_freq]
        ac_freq_cross = [ac_freq_cross[ind] for ind in indices]

        if len(ac_freq_cross[:2]):
            crossing_freq_largest = max(ac_freq_cross[:2])
            crossing_freq_2nd_largest = min(ac_freq_cross[:2])
        else:
            crossing_freq_largest = 10.
            crossing_freq_2nd_largest = 100.

        range_real = np.max(experiment.real_sus) - np.min(
            experiment.real_sus
        )

        guessdict = {
            'tau1': 1. / (2. * np.pi * crossing_freq_2nd_largest),
            'alpha1': 0.1,
            'D_chi1': 2. * range_real / 3.,
            'tau2': 1. / (2. * np.pi * crossing_freq_largest),
            'alpha2': 0.01,
            'D_chi2': range_real / 3.,
            'chi_total': np.max([np.min(experiment.real_sus), 0.])
        }

        # Replace 'guess' with relevant guess
        for var, val in param_dict.items():
            if isinstance(val, str) and val.lower() == 'guess':
                new_param_dict[var] = guessdict[var]

        return new_param_dict

    def _calc_lntau_expect(self) -> list[float]:
        '''
        Calculates expectation value of ln(tau) for tau1 and tau2

        Parameters
        ----------
        None

        Returns
        -------
        list[float]
            <ln(tau)> value in ln(seconds) for tau1 and tau2

        Raises
        ------
        ValueError
            If required model parameters in self.final_var_values are undefined
        '''

        tau1 = self.final_var_values['tau1']
        tau2 = self.final_var_values['tau2']

        if None in [tau1, tau2]:
            _error = 'Error: Cannot calculate ln(tau) expectation value '
            _error += 'tau1 and/or tau2 are undefined!'
            raise ValueError(_error)

        return self.calc_lntau_expect(tau1, tau2)

    @staticmethod
    def calc_lntau_expect(tau1: ArrayLike,
                          tau2: ArrayLike) -> list[float | NDArray]:
        '''
        Calculates expectation value of ln(tau) for tau1 and tau2

        Parameters
        ----------
        tau1: array_like
            First tau value from Double Generalised Debye Model
        tau2: array_like
            Second tau value from Double Generalised Debye Model

        Returns
        -------
        list[float | ndarray of floats]
            <ln(tau)> value(s) in ln(seconds) for tau1 and tau2
        '''

        return [np.log(tau1), np.log(tau2)]

    def _calc_lntau_fit_ul(self) -> list[list[float]]:
        '''
        Calculates upper and lower bounds of ln(tau) from fit uncertainty
        in fitted parameters

        Parameters
        ----------
        None

        Returns
        -------
        list[list[float]]
            upper and lower bounds of ln(tau1) from fit uncertainty in fitted\n
            parameters, then for ln(tau2) (in both cases upper > lower)

        Raises
        ------
        ValueError
            If required model parameters in self.final_var_values\n
            or self.fit_stdev are undefined
        '''

        tau1 = self.final_var_values['tau1']
        tau2 = self.final_var_values['tau2']

        if 'tau1' in self.fit_stdev:
            tau1_std = self.fit_stdev['tau1']
        else:
            tau1_std = 0.

        if 'tau2' in self.fit_stdev:
            tau2_std = self.fit_stdev['tau2']
        else:
            tau2_std = 0.

        if None in [tau1, tau2]:
            _error = 'Error: Cannot calculate ln(tau) bounds '
            _error += 'tau1 and/or tau2 are undefined!'
            raise ValueError(_error)
        elif None in [tau1_std, tau2_std]:
            _error = 'Error: Cannot calculate ln(tau) bounds '
            _error += 'standard deviation of tau1 and/or tau2  are undefined!'
            raise ValueError(_error)

        bounds = self.calc_lntau_fit_ul(tau1, tau2, tau1_std, tau2_std)

        return bounds

    @staticmethod
    def calc_lntau_fit_ul(tau1: ArrayLike, tau2: ArrayLike,
                          tau1_std: ArrayLike,
                          tau2_std: ArrayLike) -> list[list[float | NDArray]]:
        '''
        Calculates upper and lower bounds of ln(tau) from fit uncertainty\n
        in fitted parameters

        Parameters
        ----------
        tau1: array_like
            First tau value from Double Generalised Debye Model
        tau2: array_like
            Second tau value from Double Generalised Debye Model
        tau1_std: array_like
            Standard deviation of first tau value from Double Generalised\n
            Debye Model
        tau2_std: array_like
            Standard deviation of second tau value from Double Generalised\n
            Debye Model

        Returns
        -------
        list[list[float | ndarray of floats]]
            upper and lower bounds of ln(tau1) from fit uncertainty in fitted\n
            parameters, then for ln(tau2) (in both cases upper > lower)
        '''

        tau1 = np.asarray(tau1)
        tau1_std = np.asarray(tau1_std)
        tau2 = np.asarray(tau2)
        tau2_std = np.asarray(tau2_std)

        warnings.filterwarnings('ignore', 'invalid value encountered in log')
        bounds1 = np.array(
            [np.log(tau1 + tau1_std), np.log(tau1 - tau1_std)]
        ).T
        bounds2 = np.array(
            [np.log(tau2 + tau2_std), np.log(tau2 - tau2_std)]
        ).T

        warnings.filterwarnings('default', 'invalid value encountered in log')

        bounds1 = np.sort(bounds1, axis=-1)
        bounds2 = np.sort(bounds2, axis=-1)

        return [bounds1.T.tolist(), bounds2.T.tolist()]

    def _calc_lntau_stdev(self) -> list[float]:
        '''
        Calculates standard deviation of ln(tau) for tau1 and tau2

        Parameters
        ----------
        None

        Returns
        -------
        list[float]
            lntau standard deviation for tau1 and tau2

        Raises
        ------
        ValueError
            If required model parameters in self.final_var_values are undefined
        '''

        alpha1 = self.final_var_values['alpha1']
        alpha2 = self.final_var_values['alpha2']

        if None in [alpha1, alpha2]:
            _error = 'Error: Cannot calculate ln(tau) standard deviation '
            _error += 'alpha1 and/or alpha2 undefined!'
            raise ValueError(_error)

        two_bounds = self.calc_lntau_stdev(alpha1, alpha2)
        return two_bounds

    @staticmethod
    def calc_lntau_stdev(alpha1: float, alpha2: float) -> list[float]:
        '''
        Calculates standard deviation of ln(tau) for tau1 and tau2

        Parameters
        ----------
        alpha1: float
            First alpha value of Double Generalised Debye Model
        alpha2: float
            Second alpha value of Double Generalised Debye Model

        Returns
        -------
        list[float]
            lntau standard deviation for tau1 and tau2
        '''

        sd1 = np.sqrt(((1. / (1. - alpha1)**2) - 1.) * np.pi**2 / 3.)
        sd2 = np.sqrt(((1. / (1. - alpha2)**2) - 1.) * np.pi**2 / 3.)

        return [sd1, sd2]


class DoubleGDebyeEqualChiModel(Model):
    '''
    Double Generalised Debye Model (with equal chi) of AC Susceptibility

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
    flat_thresh: float
        Threshold for fit of susceptibility data to X''= m * nu + b\n
        Used in fit_to()\n
        When root sum of squared differences between X''_flat and X''_exp\n
        is below flat_thresh, the fit is marked as failed.
    fit_status: bool
        True if fit successful, else false
    '''
    #: Model Name
    NAME = 'Double Generalised Debye Equal Chi'

    #: Display name for interactive buttons
    DISP_NAME = 'Double Generalised Debye\n (Equal χ, Equal α)'

    #: Model Parameter name strings
    PARNAMES = [
        'tau1', 'tau2', 'alpha', 'chi_S', 'chi_T'
    ]

    #: Model Parameter bounds
    BOUNDS = {
        'tau1': [0., np.inf],
        'tau2': [0., np.inf],
        'alpha': [0., 1],
        'chi_S': [0., np.inf],
        'chi_T': [0., np.inf]
    }

    #: Model Parameter mathmode name strings
    VARNAMES_MM = {
        'tau1': r'$\tau_\mathregular{1}$',
        'tau2': r'$\tau_\mathregular{2}$',
        'alpha': r'$\alpha$',
        'chi_S': r'$\chi_\mathregular{S}$',
        'chi_T': r'$\chi_\mathregular{T}$'
    }

    UNITS = {
        'tau1': r's',
        'tau2': r's',
        'chi_S': r'cm^3 mol^-1',
        'chi_T': r'cm^3 mol^-1',
        'alpha': r''
    }

    UNITS_MM = {
        'tau1': r'$\mathregular{s}$',
        'tau2': r'$\mathregular{s}$',
        'chi_S': r'\mathregular{cm}^\mathregular{3} \mathregular{mol}^\mathregular{-1}$', # noqa
        'chi_T': r'\mathregular{cm}^\mathregular{3} \mathregular{mol}^\mathregular{-1}$', # noqa
        'alpha': r'',
    }

    def __init__(self, fit_vars: dict[str, float | str],
                 fix_vars: dict[str, float | str], experiment: 'Experiment'):

        # Initialise attributes required by Model superclass to default values
        super().__init__(fit_vars, fix_vars, experiment)

        # Set as list of None, since here they have multiple values one
        # for tau1, one for tau2
        self._lntau_expect = [None, None]
        self._lntau_fit_ul = [None, None]
        self._lntau_stdev = [None, None]

        return

    # Redefined for list
    @property
    def lntau_expect(self) -> list[float]:
        '''
        Expectation value of ln(tau)
        '''
        # If not calculated yet, then calculate
        if None in self._lntau_expect:
            self.lntau_expect = self._calc_lntau_expect()
        return self._lntau_expect

    @lntau_expect.setter
    def lntau_expect(self, value):
        if isinstance(value, list):
            self._lntau_expect = value
        else:
            raise TypeError
        return

    # Redefined for list
    @property
    def lntau_fit_ul(self) -> list[list[float]]:
        '''
        Expectation value of ln(tau)
        '''
        # If not calculated yet, then calculate
        if None in self._lntau_fit_ul:
            self._lntau_fit_ul = self._calc_lntau_fit_ul()
        return self._lntau_fit_ul

    @lntau_fit_ul.setter
    def lntau_fit_ul(self, value):
        if isinstance(value, list):
            self._lntau_fit_ul = value
        else:
            raise TypeError
        return

    # Redefined for list
    @property
    def lntau_stdev(self) -> list[float]:
        '''
        Standard deviation of ln(tau)
        '''
        # If not calculated yet, then calculate
        if None in self._lntau_stdev:
            self.lntau_stdev = self._calc_lntau_stdev()
        return self._lntau_stdev

    @lntau_stdev.setter
    def lntau_stdev(self, value):
        if isinstance(value, list):
            self._lntau_stdev = value
        else:
            raise TypeError
        return

    @staticmethod
    def model(parameters: dict[str, float],
              ac_freq_ang: list[float]) -> tuple[list[float], list[float]]:
        '''
        Computes model function of ac suceptibility for double
        generalised debye model with equal ratio of DChi for the two
        species

        Parameters
        ----------
        parameters: dict[str, float],
            Keys are class.PARNAMES, values are float value
        ac_freq_ang: list[float]
            angular ac frequencies at which model will be evaluated

        Returns
        -------
        list[float]
            real susceptibility
        list[float]
            imaginary susceptibility

        '''
        tau1 = parameters['tau1']
        tau2 = parameters['tau2']
        alpha = parameters['alpha']
        chi_s = parameters['chi_S']
        chi_t = parameters['chi_T']

        func = abs(chi_s)
        func += 0.5 * (chi_t - chi_s) / (
            1 + np.power((ac_freq_ang * tau1 * 1j), (1. - alpha))
        )
        func += 0.5 * (chi_t - chi_s) / (
            1 + np.power((ac_freq_ang * tau2 * 1j), (1. - alpha))
        )

        return np.real(func).tolist(), np.abs(np.imag(func)).tolist()

    @staticmethod
    def discard(params: dict[str, float], ac_freq_ang: list[float]) -> bool:
        '''
        Decides whether fits should be discarded based on following criteria

        1. tau^-1 < smallest ac frequency

        2. tau^-1 > largest ac frequency

        where both tau_1 and tau_2 (corresponding to the two peaks) are
        checked

        Parameters
        ----------
        fit_param: dict[str, float]
            keys are PARNAMES, values are fitted parameter values
        ac_freq_ang: list[float]
            Angular ac frequencies

        Returns
        -------
        bool
            True if point should be discarded, else False
        '''

        to_discard = False

        if 1. / (params['tau1']) < np.min(ac_freq_ang):
            to_discard = True
        elif 1. / (params['tau1']) > np.max(ac_freq_ang):
            to_discard = True
        elif 1. / (params['tau2']) < np.min(ac_freq_ang):
            to_discard = True
        elif 1. / (params['tau2']) > np.max(ac_freq_ang):
            to_discard = True
        return to_discard

    @staticmethod
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

        # Make copy, any str values will be replaced
        new_param_dict = copy.copy(param_dict)

        '''
        Let x = largest frequency at turning point of imaginary susceptibility
                with largest abs value

        Parameters and guesses are

        tau_1 - inverse of frequency for turning point with 2nd largest
                imaginary susceptibility

        D_chi_1 - 2/3 * range of real susceptibility

        alpha_1 - 0.1

        tau_2 - inverse of frequency for turning point with largest
                imaginary susceptibility

        D_chi_2 - 1/3 * range of real susceptibility

        alpha_2 - 0.01

        chi_total - minimum real susceptibility
        '''

        # Calculate gradient of imaginary susceptibility and retrieve indexes
        # where there is a change of sign.
        dimag_sus = np.gradient(experiment.imag_sus)
        zero_crossings_freq = np.where(np.diff(np.sign(dimag_sus)))

        # Get frequency for turning point with largest imaginary
        # susceptibility
        imag_sus_cross = experiment.imag_sus[zero_crossings_freq]
        indices = np.argsort(-imag_sus_cross)
        ac_freq_cross = experiment.ac_freqs[zero_crossings_freq]
        ac_freq_cross = [ac_freq_cross[ind] for ind in indices]

        crossing_freq_largest = max(ac_freq_cross[:2])
        crossing_freq_2nd_largest = min(ac_freq_cross[:2])

        guessdict = {
            'tau1': 1. / (2. * np.pi * crossing_freq_2nd_largest),
            'tau2': 1. / (2. * np.pi * crossing_freq_largest),
            # Smallest real susceptibility
            'chi_S': np.max([np.min(experiment.real_sus), 0.]),
            # Range of real susceptibilities
            'chi_T': np.max(experiment.real_sus) - np.min(experiment.real_sus),
            'alpha': 0.1
        }

        # Replace 'guess' with relevant guess
        for var, val in param_dict.items():
            if isinstance(val, str) and val.lower() == 'guess':
                new_param_dict[var] = guessdict[var]

        return new_param_dict

    def _calc_lntau_expect(self) -> list[float]:
        '''
        Calculates expectation value of ln(tau) for tau1 and tau2

        Parameters
        ----------
        None

        Returns
        -------
        list[float]
            <ln(tau)> value in ln(seconds) for tau1 and tau2

        Raises
        ------
        ValueError
            If required model parameters in self.final_var_values are undefined
        '''

        tau1 = self.final_var_values['tau1']
        tau2 = self.final_var_values['tau2']

        if None in [tau1, tau2]:
            _error = 'Error: Cannot calculate ln(tau) expectation value '
            _error += 'tau1 and/or tau2 are undefined!'
            raise ValueError(_error)

        return self.calc_lntau_expect(tau1, tau2)

    @staticmethod
    def calc_lntau_expect(tau1: ArrayLike,
                          tau2: ArrayLike) -> list[float | NDArray]:
        '''
        Calculates expectation value of ln(tau) for tau1 and tau2

        Parameters
        ----------
        tau1: array_like
            First tau value from Double Generalised Debye Model
        tau2: array_like
            Second tau value from Double Generalised Debye Model

        Returns
        -------
        list[float | ndarray of floats]
            <ln(tau)> value(s) in ln(seconds) for tau1 and tau2
        '''

        return [np.log(tau1), np.log(tau2)]

    def _calc_lntau_fit_ul(self) -> list[list[float]]:
        '''
        Calculates upper and lower bounds of ln(tau) from fit uncertainty
        in fitted parameters

        Parameters
        ----------
        None

        Returns
        -------
        list[list[float]]
            upper and lower bounds of ln(tau1) from fit uncertainty in fitted\n
            parameters, then for ln(tau2) (in both cases upper > lower)

        Raises
        ------
        ValueError
            If required model parameters in self.final_var_values\n
            or self.fit_stdev are undefined
        '''

        tau1 = self.final_var_values['tau1']
        tau2 = self.final_var_values['tau2']

        if 'tau1' in self.fit_stdev:
            tau1_std = self.fit_stdev['tau1']
        else:
            tau1_std = 0.

        if 'tau2' in self.fit_stdev:
            tau2_std = self.fit_stdev['tau2']
        else:
            tau2_std = 0.

        if None in [tau1, tau2]:
            _error = 'Error: Cannot calculate ln(tau) bounds '
            _error += 'tau1 and/or tau2 are undefined!'
            raise ValueError(_error)
        elif None in [tau1_std, tau2_std]:
            _error = 'Error: Cannot calculate ln(tau) bounds '
            _error += 'standard deviation of tau1 and/or tau2  are undefined!'
            raise ValueError(_error)

        bounds = self.calc_lntau_fit_ul(tau1, tau2, tau1_std, tau2_std)

        return bounds

    @staticmethod
    def calc_lntau_fit_ul(tau1: ArrayLike, tau2: ArrayLike,
                          tau1_std: ArrayLike,
                          tau2_std: ArrayLike) -> list[list[float | NDArray]]:
        '''
        Calculates upper and lower bounds of ln(tau) from fit uncertainty\n
        in fitted parameters

        Parameters
        ----------
        tau1: array_like
            First tau value from Double Generalised Debye Model
        tau2: array_like
            Second tau value from Double Generalised Debye Model
        tau1_std: array_like
            Standard deviation of first tau value from Double Generalised\n
            Debye Model
        tau2_std: array_like
            Standard deviation of second tau value from Double Generalised\n
            Debye Model

        Returns
        -------
        list[list[float | ndarray of floats]]
            upper and lower bounds of ln(tau1) from fit uncertainty in fitted\n
            parameters, then for ln(tau2) (in both cases upper > lower)
        '''

        tau1 = np.asarray(tau1)
        tau1_std = np.asarray(tau1_std)
        tau2 = np.asarray(tau2)
        tau2_std = np.asarray(tau2_std)

        warnings.filterwarnings('ignore', 'invalid value encountered in log')
        bounds1 = np.array(
            [np.log(tau1 + tau1_std), np.log(tau1 - tau1_std)]
        ).T
        bounds2 = np.array(
            [np.log(tau2 + tau2_std), np.log(tau2 - tau2_std)]
        ).T
        warnings.filterwarnings('default', 'invalid value encountered in log')

        bounds1 = np.sort(bounds1, axis=-1)
        bounds2 = np.sort(bounds2, axis=-1)

        return [bounds1.T.tolist(), bounds2.T.tolist()]

    def _calc_lntau_stdev(self) -> list[float]:
        '''
        Calculates standard deviation of ln(tau) for tau1 and tau2\n
        Since alpha is the same for both, the standard deviation of each\n
        is equal

        Parameters
        ----------
        None

        Returns
        -------
        list[float]
            lntau standard deviation for tau1 and tau2

        Raises
        ------
        ValueError
            If required model parameters in self.final_var_values are undefined
        '''

        alpha = self.final_var_values['alpha']

        if None in [alpha]:
            _error = 'Error: Cannot calculate ln(tau) standard deviation '
            _error += 'alpha undefined!'
            raise ValueError(_error)

        two_bounds = self.calc_lntau_stdev(alpha)
        return two_bounds

    @staticmethod
    def calc_lntau_stdev(alpha: float) -> list[float]:
        '''
        Calculates standard deviation of ln(tau) for tau1 and tau2\n
        Since alpha is the same for both, the standard deviation of each\n
        is equal

        Parameters
        ----------
        alpha: float
            Alpha value of Double Generalised Debye Model

        Returns
        -------
        list[float]
            lntau standard deviation for tau1 and tau2
        '''

        sd1 = np.sqrt(((1. / (1. - alpha)**2) - 1.) * np.pi**2 / 3.)
        sd2 = np.sqrt(((1. / (1. - alpha)**2) - 1.) * np.pi**2 / 3.)

        return [sd1, sd2]


class Measurement():
    '''
    Stores data for a single AC Susceptibility measurement at a
    given temperature, given applied dc field, and given ac frequency

    Parameters
    ----------
    dc_field: float
        Applied dc field (Oe)
    temperature: float
        Temperature of datapoint (K)
    real_sus: float
        real part of susceptibility (cm3 mol-1)
    imag_sus: float
        imaginary part of susceptibility (cm3 mol-1)
    ac_freq: float
        linear ac frequency of datapoint (s-1)
    ac_field: float
        ac field (Oe)

    Attributes
    ----------
    dc_field: float
        Applied dc field (Oe)
    temperature: float
        Temperature of datapoint (K)
    ac_freq: float
        linear ac frequency of datapoint (s-1)
    real_sus: float
        real part of susceptibility (cm3 mol-1) for datapoint
    imag_sus: float
        imaginary part of susceptibility (cm3 mol-1) for datapoint
    ac_field: float
        ac field (Oe)
    rep_temperature: float
        Representative temperature assigned to this datapoint (K)
    rep_dc_field: float
        Representative dc field assigned to this datapoint (Oe)
    '''

    def __init__(self, dc_field: float, temperature: float, real_sus: float,
                 imag_sus: float, ac_freq: float, ac_field: float):

        self.dc_field = dc_field
        self.temperature = temperature
        self.real_sus = real_sus
        self.imag_sus = imag_sus
        self.ac_freq = ac_freq
        self.ac_field = ac_field

        self._rep_temperature = None
        self._rep_dc_field = None

        return

    @property
    def rep_temperature(self):
        return self._rep_temperature

    @rep_temperature.setter
    def rep_temperature(self, value: float):
        if isinstance(value, (np.floating, float, int)):
            self._rep_temperature = float(value)
        else:
            raise TypeError
        return

    @property
    def rep_dc_field(self):
        return self._rep_dc_field

    @rep_dc_field.setter
    def rep_dc_field(self, value: float):
        if isinstance(value, (np.floating, float, int)):
            self._rep_dc_field = float(value)
        else:
            raise TypeError
        return

    @staticmethod
    def condition_positive(s: str) -> float:
        '''
        For a given string containing a float,
        attempts to convert to float, and checks if
        positive.\n\n

        If positive and floatable, returns value.\n
        Else, returns np.nan

        Parameters
        ----------
        s: str
            string to check
        Returns
        -------
        float
            Float, or np.nan if conditions not met
        '''
        try:
            s = float(s.strip())
            if s < 0:
                # print(
                #   f'Negative Susceptibility {s} emu, skipping'
                # )
                s = np.nan
        except (TypeError, ValueError):
            s = np.nan

        return s

    @classmethod
    def from_file(cls, file: str, mass: float, mw: float,
                  data_header: str = '[Data]',
                  check_error: bool = True,
                  encoding: str = 'find') -> list['Measurement']:
        '''
        Extracts ac susceptibility data from magnetometer output file and
        returns list of Measurements, one for each valid datapoint.\n
        Incomplete lines are ignored.\n
        Susceptibilities which become positive when std error is added
        are included and all others are ignored.\n
        Negative temperatures are ignored.\n
        Mass and MW are required for conversion from.\n
        emu(per Oe) to cm^3 mol^-1

        Parameters
        ----------
        file: str
            Name of magnetometer output file
        mass: float
            Mass of sample in mg
        mw: float
            Molecular weight of sample in g mol^-1
        data_header: str, default '[Data]'
            Contents of line which specifies the beginning of the data block
            in input file.\n
            Default is to find line containing '[Data]'
        check_error: bool, default True
            If True, susceptibilities are compared to Error, and those
            values that become positive when error is added are retained.
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

        data_index, header_indices, header_names = ut.parse_mag_file(
            file,
            HEADERS_SUPPORTED,
            data_header,
            encoding=encoding
        )

        # Columns to extract from file
        cols = {
            gen: header_indices[gen] for gen in HEADERS_GENERIC
        }

        # Convert strings to floats, if not possible then mark as nan
        converters = {
            it: lambda s: (float(s.strip() or np.nan)) for it in cols.values()
        }

        # Get file headers and names for error columns
        error_indices, _ = ut.parse_headers(
            file, data_index, ERROR_HEADERS_SUPPORTED
        )

        # If no error headers found, then enforce positive susceptibility
        if any([ev == -1 for ev in error_indices.values()]):
            converters[header_indices['real_sus']] = cls.condition_positive
            converters[header_indices['imag_sus']] = cls.condition_positive

        # Enforce positive temperature
        converters[header_indices['temperature']] = cls.condition_positive

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

        # If errors specified, remove susceptibilities which are not
        # positive within error
        if not any([ev == -1 for ev in error_indices.values()]) and check_error: # noqa

            # Columns to extract from file
            err_cols = {
                gen: error_indices[gen] for gen in ERROR_HEADERS_GENERIC
            }
            # Convert strings to floats, if not possible then mark as nan
            err_converters = {
                it: lambda s: (float(s.strip() or np.nan))
                for it in err_cols.values()
            }

            # Read required columns of file
            err_data = np.loadtxt(
                file,
                skiprows=data_index + 1,
                delimiter=',',
                converters=err_converters,
                usecols=err_cols.values(),
                encoding=encoding
            )

            real_err_col = list(err_cols.keys()).index('real_sus_err')
            imag_err_col = list(err_cols.keys()).index('imag_sus_err')
            real_susc_col = list(cols.keys()).index('real_sus')
            imag_susc_col = list(cols.keys()).index('imag_sus')

            data = [
                drow for drow, erow in zip(data, err_data)
                if drow[real_susc_col] + erow[real_err_col] > 0. and drow[imag_susc_col] + erow[imag_err_col] > 0. # noqa
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

        # Change of units of input susceptibility to cm^3mol^(-1)
        # and apply correction for ac drive field if needed
        if '(emu/Oe)' in header_names['imag_sus']:
            for mm in measurements:
                mm.real_sus *= mw / (mass / 1000.)
                mm.imag_sus *= mw / (mass / 1000.)
        else:
            for mm in measurements:
                mm.real_sus *= mw / (mm.ac_field * mass / 1000.)
                mm.imag_sus *= mw / (mm.ac_field * mass / 1000.)

        return measurements


class Experiment():
    '''
    Stores data for multiple AC Susceptibility measurements at a
    given temperature, given applied dc field, and multiple ac frequencies

    Parameters
    ----------
    rep_temperature: float
        Representative temperature for this experiment e.g. mean of all
        datapoints (Measurements) (K)
    raw_temperatures: array_like
        Raw temperature values for each datapoint (Measurements)
        in experiment (K)
    real_sus: array_like
        real part of susceptibility (cm3 mol-1) for each datapoint
    imag_sus: array_like
        imaginary part of susceptibility (cm3 mol-1) for each datapoint
    ac_freqs: array_like
        linear ac frequency (s-1) for each datapoint
    rep_dc_field: float
        Representative DC field for this experiment e.g. mean of all
        datapoints (Measurements) (Oe)
    dc_fields: float
        Applied dc field strength (Oe) for each datapoint
    ac_fields: array_like
        AC field value (Oe) for each datapoint

    Attributes
    ----------
    rep_temperature: float
        Representative temperature for this experiment e.g. mean of all
        datapoints (measurements) (K)
    raw_temperatures: ndarray of floats
        Raw temperature values for each datapoint (Measurement)
        in experiment (K)
    real_sus: ndarray of floats
        real part of susceptibility (cm3 mol-1) for each datapoint
    imag_sus: ndarray of floats
        imaginary part of susceptibility (cm3 mol-1) for each datapoint
    ac_freqs: ndarray of floats
        linear ac frequency (s-1) for each datapoint
    rep_dc_field: float
        Representative DC field for this experiment e.g. mean of all
        datapoints (Oe)
    dc_fields: float
        Applied dc field strength for each datapoint (Oe)
    ac_fields: ndarray of floats
        AC field value (Oe) for each datapoint
    '''

    def __init__(self, rep_temperature: float,
                 raw_temperatures: ArrayLike, real_sus: ArrayLike,
                 imag_sus: ArrayLike, ac_freqs: ArrayLike,
                 rep_dc_field: float, dc_fields: ArrayLike,
                 ac_fields: ArrayLike):

        self.rep_temperature = rep_temperature
        self.raw_temperatures = raw_temperatures
        self.real_sus = np.asarray(real_sus)
        self.imag_sus = np.asarray(imag_sus)
        self.ac_freqs = np.asarray(ac_freqs)
        self.rep_dc_field = rep_dc_field
        self.dc_fields = np.asarray(dc_fields)
        self.ac_fields = np.asarray(ac_fields)

        return

    @classmethod
    def from_file(cls, file: str, mass: float, mw: float,
                  data_header: str = '[Data]',
                  temp_thresh: float = 0.1,
                  field_thresh: float = 1,
                  x_var: str = 'T') -> list[list['Experiment']]:
        '''
        Extracts ac susceptibility data from magnetometer output file and
        returns list of Experiments.

        Combines Measurement.from_file and Experiment.from_measurements

        Incomplete lines and negative values of susceptibility are ignored
        Mass and MW are required for conversion from
        emu(per Oe) to cm^3 mol^-1

        Parameters
        ----------
        file: str
            Name of magnetometer output file
        data_header: str, default '[Data]'
            Contents of line which specifies the beginning of the data block
            in input file default is to find line containing '[Data]'
        mass: float
            Mass of sample in mg
        mw: float
            Molecular weight of sample in g mol^-1
        temp_thresh: float, default 0.1 K
            Threshold used to discriminate between temperatures (K)
        field_thresh: float, default 1 Oe
            Threshold used to discriminate between dc field values (Oe)
        x_var: str, default {'T', 'H'}
            Independent variable that relaxation time is being measured over,
            temperature or field.

        Returns
        -------
        list[list[Experiment]]
            Each element is a list of Experiments at the same DC field/
            temperature sorted low to high DC field/temperature strength.

            Within each sublist the elements are single experiments
            which are each a set of measurements with the same temperature
            and DC field strength.

            The sublists are sorted low to high mean temperature/DC field.
        '''

        mm = Measurement.from_file(
            file=file,
            mass=mass,
            mw=mw,
            data_header=data_header
        )

        all_exp = cls.from_measurements(
            measurements=mm,
            temp_thresh=temp_thresh,
            field_thresh=field_thresh,
            x_var=x_var
        )

        return all_exp

    @classmethod
    def from_measurements(cls,
                          measurements: list[Measurement],
                          temp_thresh: float = 0.1,
                          field_thresh: float = 1,
                          x_var: str = 'T') -> list[list['Experiment']]:
        '''
        Creates a list of lists of Experiment objects from a list of\n
        Individual measurement objects. Experiments are defined as a set of\n
        Measurements with the same temperature and DC field strength.\n\n

        Measurements are sorted by dc field and temperature,\n
        with the order determined by x_var, then ac frequency.

        Parameters
        ----------
        measurement: list[Measurement]
            Measurements at various temperatures and DC fields
        temp_thresh: float, default 0.1 K
            Threshold used to discriminate between temperatures (K)
        field_thresh: float, default 1 Oe
            Threshold used to discriminate between dc field values (Oe)
        x_var: str, default {'T', 'H'}
            Independent variable that relaxation time is being measured over,
            temperature or field.

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
            # Sort measurements by dc field then temperature
            measurements.sort(key=lambda k: (k.dc_field, k.temperature))
            mean_fields, split_ind = ut.find_mean_values(
                    [
                        measurement.dc_field
                        for measurement in measurements
                    ],
                    thresh=field_thresh
                )

            # Set each measurement's representative field, here the mean
            for measurement, mean_field in zip(measurements, mean_fields):
                measurement.rep_dc_field = mean_field

            # Re-sort using mean dc field
            measurements.sort(key=lambda k: (k.rep_dc_field, k.temperature))

            # And split based on changing dc field values
            measurements: list[list[Measurement]] = [
                mm.tolist() for mm in np.split(
                    measurements, split_ind
                )
            ]

            experiments = []

            # Within a given dc field, split by temperature
            for sf_measurements in measurements:

                mean_temps, split_ind = ut.find_mean_values(
                    [
                        measurement.temperature
                        for measurement in sf_measurements
                    ],
                    thresh=temp_thresh
                )

                # Set each measurement's representative temperature,
                # here the mean
                for measurement, mean_temp in zip(sf_measurements, mean_temps):
                    measurement.rep_temperature = mean_temp

                # sort measurements by temperature then ac frequency
                sf_measurements.sort(
                    key=lambda k: (k.rep_temperature, k.ac_freq)
                )

                # Generate list of experiments, one per each temperature
                # at this current dc field
                _exps = [
                    cls._from_mmlist(_mms)
                    for _mms in np.split(sf_measurements, split_ind)
                ]

                # and append to list of all experiments
                experiments.append(_exps)

        elif x_var == 'H':

            # Sort measurements by temperature then field
            measurements.sort(key=lambda k: (k.temperature, k.dc_field))
            mean_temps, split_ind = ut.find_mean_values(
                    [
                        measurement.temperature
                        for measurement in measurements
                    ],
                    thresh=temp_thresh
                )

            # Set each measurement's representative temperature, here the mean
            for measurement, mean_temp in zip(measurements, mean_temps):
                measurement.rep_temperature = mean_temp

            # Re-sort using mean temperature
            measurements.sort(key=lambda k: (k.rep_temperature, k.dc_field))

            # And split based on changing temperature values
            measurements: list[list[Measurement]] = [
                mm.tolist() for mm in np.split(
                    measurements, split_ind
                )
            ]

            experiments = []

            # Within a given temperature, split by dc field
            for sf_measurements in measurements:

                mean_fields, split_ind = ut.find_mean_values(
                    [
                        measurement.dc_field
                        for measurement in sf_measurements
                    ],
                    thresh=field_thresh
                )

                # Set each measurement's representative field,
                # here the mean
                for measurement, mean_field in zip(sf_measurements, mean_fields): # noqa
                    measurement.rep_dc_field = mean_field

                # sort measurements by temperature then ac frequency
                sf_measurements.sort(
                    key=lambda k: (k.rep_dc_field, k.ac_freq)
                )

                # Generate list of experiments, one per each field
                # at this current temperature
                _exps = [
                    cls._from_mmlist(_mms)
                    for _mms in np.split(sf_measurements, split_ind)
                ]

                # and append to list of all experiments
                experiments.append(_exps)

        else:
            raise ValueError(f'Unknown x_var "{x_var}" specified')

        return experiments

    @classmethod
    def _from_mmlist(cls, measurements: list[Measurement]) -> 'Experiment':
        '''
        Creates a single Experiment from a list of measurements with no\n
        sorting or splitting

        Parameters
        ----------
        measurements: list[Measurement]
            Measurements to convert to Experiment

        Returns
        -------
        Experiment
        '''

        _rt = [
            mm.rep_temperature
            for mm in measurements
        ]

        _t = [
            mm.temperature
            for mm in measurements
        ]

        _dc = [
            mm.dc_field
            for mm in measurements
        ]

        _rdc = [
            mm.rep_dc_field
            for mm in measurements
        ]

        _rs = [
            mm.real_sus
            for mm in measurements
        ]

        _is = [
            mm.imag_sus
            for mm in measurements
        ]

        _acfi = [
            mm.ac_field
            for mm in measurements
        ]

        _acfr = [
            mm.ac_freq
            for mm in measurements
        ]

        _exp = Experiment(
            _rt[0], _t, _rs, _is, _acfr, _rdc[0], _dc, _acfi
        )

        return _exp


def save_ac_magnetometer_file(experiments: list[Experiment] | Experiment,
                              file_name: str = 'ac_data.out',
                              verbose: bool = False,
                              extra_comment: str = '') -> None:
    '''
    Saves the data contained in a list of Experiments to
    a magnetometer-style file that can be read by ccfit2

    Parameters
    ----------
    experiments: list[Experiment] | Experiment
        List of AC Experiments to include, or single Experiment
    file_name: str, 'ac_data.out'
        Name of output file
    verbose: bool, default True
        If True, file location is written to terminal
    extra_comment: str, optional
        Extra comments to add to file after ccfit2 version line
        Must include comment character # for each new line

    Returns
    -------
    None
    '''

    if isinstance(experiments, Experiment):
        experiments = [experiments]

    # Make header
    header = [
        'Field (Oe)',
        'Temperature (K)',
        'Frequency (Hz)',
        'AC X\' (emu/Oe)',
        'AC X" (emu/Oe)',
        'Drive Amplitude (Oe)'
    ]
    header = ','.join(header)

    # Make comment
    comment = (
        f'#This file was generated with ccfit2 v{__version__}'
        ' on {}\n'.format(
            datetime.datetime.now().strftime('%H:%M:%S %d-%m-%Y ')
        )
    )

    if len(extra_comment):
        comment += extra_comment

    comment += '\n[Data]\n'

    # Assemble output array
    _out = [
        np.array([
            experiment.dc_fields,
            experiment.raw_temperatures,
            experiment.ac_freqs,
            experiment.real_sus,
            experiment.imag_sus,
            experiment.ac_fields
        ])
        for experiment in experiments
    ]

    _out = np.hstack(_out).T

    # Save file
    np.savetxt(
        file_name,
        _out,
        header=header,
        delimiter=',',
        encoding='utf-8',
        comments=comment,
    )

    if verbose:
        ut.cprint(
            f'\n Magnetometer file written to \n {file_name}\n',
            'cyan'
        )

    return


def plot_susceptibility(experiments: list[Experiment] | Experiment,
                        save: bool = True, show: bool = True,
                        x_var: str = 'T',
                        save_name: str = 'susceptibility.png',
                        window_title: str = 'AC susceptibility',
                        verbose: bool = True) -> tuple[plt.Figure, list[plt.Axes]]: # noqa
    '''
    Creates plot of in- and out-of-phase raw susceptibilities as matplotlib
    figure.

    Parameters
    ----------
    experiments: list[Experiment] | Experiment
        AC experiments
    save: bool, default True
        If True, saves plot to file
    show: bool, default True
        If True, shows plot on screen
    x_var: str, default {'T', 'H'}
        Controls datapoint colour specification according to either \n
        temperature (T) or DC field (H)
    save_name: str, default 'susceptibility.png'
        If save is True, will save plot to this file name
    window_title: str, default 'AC susceptibility'
        Title of figure window, not of plot
    verbose: bool, default True
        If True, plot file location is written to terminal

    Returns
    -------
    plt.Figure
        Matplotlib figure object
    list[plt.Axes]
        Matplotlib axis objects, first contains real susceptibility, second
        contains imaginary

    Raises
    ------
    ValueError
        If x_var is not T or H
    '''

    if isinstance(experiments, Experiment):
        experiments = [experiments]

    fig, (ax1, ax2) = plt.subplots(
        2,
        1,
        sharex='none',
        sharey='none',
        figsize=(7., 4.5),
        num=window_title
    )  # 8.27, 11.69 A4
    fig.subplots_adjust(hspace=.5, wspace=.02)

    ratio = np.linspace(0, 1, len(experiments))
    colors = cmaps['jet'].resampled(len(experiments))

    # Experimental data
    for eit, experiment in enumerate(experiments):
        if x_var == 'T':
            label_name = '{:.2f} K'.format(experiment.rep_temperature)
        elif x_var == 'H':
            label_name = '{:.1f} Oe'.format(experiment.rep_dc_field)
        else:
            raise ValueError(f'Unknown x_var "{x_var}" specified')

        # Real
        ax1.semilogx(
            experiment.ac_freqs,
            experiment.real_sus,
            '-o',
            markersize=4,
            fillstyle='none',
            label=label_name,
            color=colors(ratio[eit])
        )
        # Imaginary
        ax2.semilogx(
            experiment.ac_freqs,
            experiment.imag_sus,
            '-o',
            markersize=4,
            fillstyle='none',
            color=colors(ratio[eit])
        )

    ax1.set_xticklabels([])
    ax1.set_ylabel(
        r'$\chi^{\prime}$  (cm$^\mathregular{3}$ mol$^\mathregular{-1}$)'
    )
    # Get rid of the frames of susceptibility plots
    for axis in [ax1, ax2]:
        axis.spines['top'].set_visible(False)
        axis.spines['right'].set_visible(False)

    # Add minor ticks
    for axis in [ax1, ax2]:
        axis.xaxis.set_major_formatter(
            FuncFormatter(lambda y, _: '{:g}'.format(y))
        )
        axis.xaxis.set_minor_locator(
            LogLocator(base=10, subs='auto', numticks=999)
        )
        axis.yaxis.set_minor_locator(AutoMinorLocator())

    # Get rid of the x-labels of real susceptibility
    ax1.set_xticklabels([])
    ax1.set_ylabel(
        r'$\chi^{\prime}$  (cm$^\mathregular{3}$ mol$^\mathregular{-1}$)'
    )
    ax2.set_xlabel('Wave Frequency (Hz)')
    ax2.set_ylabel(
        r'$\chi^{\prime\prime}$ (cm$^\mathregular{3}$ mol$^\mathregular{-1}$)'
    )

    # Disable X' x-tick labels
    # sometimes they still show up even if ax1 and ax2 have sharex=True
    plt.setp(ax1.get_xticklabels(), visible=False)

    fig.legend(
        frameon=False,
        loc=7
    )

    fig.tight_layout(rect=[0, 0, 0.85, 1])

    if save:
        fig.savefig(save_name, dpi=400)
        if verbose:
            ut.cprint(
                f'\n Susceptibility plot saved to \n {save_name}\n',
                'cyan'
            )
    if show:
        plt.show()

    return fig, [ax1, ax2]


def plot_colecole(experiments: list[Experiment] | Experiment,
                  save: bool = False, show: bool = True,
                  x_var: str = 'T',
                  save_name: str = 'cole_cole.png',
                  window_title: str = 'Cole-Cole Plot',
                  verbose: bool = True) -> tuple[plt.Figure, list[plt.Axes]]:
    '''
    Creates Cole-Cole plot as matplotlib figure

    Parameters
    ----------
    experiments: list[Experiment] | Experiment
        AC experiments
    save: bool, default False
        If true, saves plot to file as png
    show: bool, default True
        If True, shows plot on screen
    x_var: str, default {'T', 'H'}
        Controls datapoint colour specification according to either \n
        temperature (T) or DC field (H)
    save_name: str, default 'cole_cole.png'
        If save is True, will save plot to this file name
    window_title: str, default 'Cole-Cole Plot'
        Title of figure window, not of plot
    verbose: bool, default True
        If True, plot file location is written to terminal

    Returns
    -------
    plt.Figure
        Matplotlib figure object
    plt.Axes
        Matplotlib axis object

    Raises
    ------
    ValueError
        If x_var is not T or H
    '''

    if isinstance(experiments, Experiment):
        experiments = [experiments]

    fig, ax = plt.subplots(
        1,
        1,
        sharex='none',
        sharey='none',
        figsize=(7.1, 4.8),
        num=window_title
    )
    fig.subplots_adjust(hspace=.02, wspace=.02)

    ratio = np.linspace(0, 1, len(experiments))
    colors = cmaps['jet'].resampled(len(experiments))

    # Experimental data
    for eit, experiment in enumerate(experiments):
        if x_var == 'T':
            label_name = '{:.2f} K'.format(experiment.rep_temperature)
        elif x_var == 'H':
            label_name = '{:.1f} Oe'.format(experiment.rep_dc_field)
        else:
            raise ValueError(f'Unknown x_var "{x_var}" specified')

        # Plot Cole-Cole
        ax.plot(
            experiment.real_sus,
            experiment.imag_sus,
            '-o',
            markersize=4,
            fillstyle='none',
            label=label_name,
            color=colors(ratio[eit])
        )

    fig.legend(
        frameon=False,
        loc=7
    )

    # Remove frames
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    # Set labels for the axes
    ax.set_xlabel(
        r'$\chi^{\prime}$  (cm$^\mathregular{3}$ mol$^\mathregular{-1}$)'
    )
    ax.set_ylabel(
        r'$\chi^{\prime\prime}$ (cm$^\mathregular{3}$ mol$^\mathregular{-1}$)'
    )

    fig.tight_layout(rect=[0, 0, 0.85, 1])

    # Set minor ticks
    ax.xaxis.set_minor_locator(AutoMinorLocator())
    ax.yaxis.set_minor_locator(AutoMinorLocator())

    if save:
        fig.savefig(save_name, dpi=400)
        if verbose:
            ut.cprint(
                f'\n Cole-Cole plot saved to \n {save_name}\n',
                'cyan'
            )

    if show:
        plt.show()

    return fig, ax


def interactive_t_select(experiments: list[Experiment],
                         on: bool = False) -> list[Experiment]:
    '''
    Creates interactive figure which allows user to select which temperatures
    they would like to fit by clicking on the plots, and then returns a new
    list of experiments.

    Parameters
    ----------
    experiments: list[Experiment]
        Experiments, ordered  low to high temperature
    on: bool, default False
        If True, set all experiments as enabled from beginning, else
        set all experiments as disabled from beginning

    Returns
    -------
    list[Experiment]
        Same as before, with user-specified entries removed

    Raises
    ------
    ValueError
        If only one experiment provided
    '''

    if len(experiments) == 1:
        raise ValueError('Cannot interactively select a single experiment')

    unique_temps = np.unique(
        [experiment.rep_temperature for experiment in experiments]
    )

    n_temps = unique_temps.size

    label_on = 'x'

    if n_temps == 1:
        n_cols = 1
    elif n_temps < 5:
        n_cols = 2
    elif n_temps < 10:
        n_cols = 3
    elif n_temps < 17:
        n_cols = 4
    elif n_temps < 25:
        n_cols = 6
        label_on = 'y'
    elif n_temps < 43:
        n_cols = 7
        label_on = 'y'
    elif n_temps < 56:
        n_cols = 8
        label_on = 'y'
    elif n_temps < 64:
        n_cols = 9
        label_on = 'y'
    else:
        n_cols = 10
        label_on = 'y'

    n_rows = int(np.ceil(n_temps / n_cols))

    width = 7. / 3. * n_rows
    if width > 7:
        width = 7.
    height = width * 1.

    if n_cols > 6:
        width = 1.5 * height

    # Show each data set individually for identification of peaks
    fig, axs = plt.subplots(
        n_rows,
        n_cols,
        sharex='none',
        sharey='none',
        figsize=(width, height),
        num='Select temperatures to fit',
    )

    suptitle = r'$\chi^{{,,}}$ vs wave frequency under {:2.1f} Oe field'.format( # noqa
        experiments[0].rep_dc_field
    )

    suptitle += '\n Select (click) the temperatures to fit (make green)'
    suptitle += ' then close this window.'

    plt.suptitle(suptitle, fontsize=11)

    for experiment, ax in zip(experiments, axs.flatten()):
        ax.semilogx(
            experiment.ac_freqs,
            experiment.imag_sus,
            marker='o',
            markeredgewidth=1,
            markeredgecolor='b',
            markerfacecolor='w',
            markersize=5,
            c='b',
            lw=.5
        )

        if label_on == 'y':
            ax.set_ylabel('{:.2f} K'.format(experiment.rep_temperature))
        elif label_on == 'x':
            ax.set_xlabel('{:.2f} K'.format(experiment.rep_temperature))

        ax.xaxis.set_minor_formatter(NullFormatter())
        ax.yaxis.set_minor_formatter(NullFormatter())
        ax.xaxis.set_major_formatter(NullFormatter())
        ax.yaxis.set_major_formatter(NullFormatter())
        ax.yaxis.set_major_locator(NullLocator())

        ax.set_box_aspect(aspect=1)
    fig.subplots_adjust(hspace=0.08, wspace=.08)

    # Remove empty axes
    for _ in range(axs.size - n_temps):
        fig.delaxes(axs.flatten()[-1])
        axs = np.delete(axs, -1)

    colors = {
        True: 'Green',
        False: 'White'
    }
    for ax in axs.flatten():
        ax.set_facecolor(colors[on])

    fig.tight_layout()

    # Store object, one per temperature
    stores = [Toggle(temp, on) for temp in unique_temps]

    def onclick(event, axs_to_store):
        '''
        Callback for mouse click.
        If an axis is clicked, then switch the corresponding store
        object and the axis' color
        '''
        if event.inaxes is not None:
            axs_to_store[event.inaxes].switch(event.inaxes)
        return

    axs_to_store = {
        ax: store
        for ax, store in zip(axs.flatten(), stores)
    }

    # Connect mouse click to callback
    cid = fig.canvas.mpl_connect(
        'button_press_event',
        lambda event: onclick(event, axs_to_store)
    )

    ut.cprint(
        (
            '\n Click the temperatures you want to fit (green),'
            ' then close this figure.\n'
        ),
        'green'
    )

    plt.show()

    experiments = [
        experiment
        for experiment, store in zip(experiments, stores)
        if store.on
    ]

    fig.canvas.mpl_disconnect(cid)

    if not len(experiments):
        ut.cprint('\n Error: No data selected.\n', 'red')
        sys.exit(1)

    return experiments


def interactive_h_select(experiments: list[Experiment],
                         on: bool = False) -> list[Experiment]:
    '''
    Creates interactive figure which allows user to select which fields
    they would like to fit by clicking on the plots, and then returns a new
    list of experiments.

    Parameters
    ----------
    experiments: list[Experiment]
        Experiments, ordered  low to high temperature
    on: bool, default False
        If True, set all experiments as enabled from beginning, else
        set all experiments as disabled from beginning

    Returns
    -------
    list[Experiment]
        Same as before, with user-specified entries removed

    Raises
    ------
    ValueError
        If only one experiment provided
    '''

    if len(experiments) == 1:
        raise ValueError('Cannot interactively select a single experiment')

    unique_fields = np.unique(
        [experiment.rep_dc_field for experiment in experiments]
    )

    n_fields = unique_fields.size

    label_on = 'x'

    if n_fields == 1:
        n_cols = 1
    elif n_fields < 5:
        n_cols = 2
    elif n_fields < 10:
        n_cols = 3
    elif n_fields < 17:
        n_cols = 4
    elif n_fields < 25:
        n_cols = 6
        label_on = 'y'
    elif n_fields < 43:
        n_cols = 7
        label_on = 'y'
    elif n_fields < 56:
        n_cols = 8
        label_on = 'y'
    elif n_fields < 64:
        n_cols = 9
        label_on = 'y'
    else:
        n_cols = 10
        label_on = 'y'

    n_rows = int(np.ceil(n_fields / n_cols))

    width = 7. / 3. * n_rows
    if width > 7:
        width = 7.
    height = width * 1.

    if n_cols > 6:
        width = 1.5 * height

    # Show each data set individually for identification of peaks
    fig, axs = plt.subplots(
        n_rows,
        n_cols,
        sharex='none',
        sharey='none',
        figsize=(width, height),
        num='Select fields to fit',
    )

    suptitle = r'$\chi^{{,,}}$ vs wave frequency at {:2.1f} K'.format(
        experiments[0].rep_temperature
    )

    suptitle += '\n Select (click) the fields to fit (make green)'
    suptitle += ' then close this window.'

    plt.suptitle(suptitle, fontsize=11)

    for experiment, ax in zip(experiments, axs.flatten()):
        ax.semilogx(
            experiment.ac_freqs,
            experiment.imag_sus,
            marker='o',
            markeredgewidth=1,
            markeredgecolor='b',
            markerfacecolor='w',
            markersize=5,
            c='b',
            lw=.5
        )

        if label_on == 'y':
            ax.set_ylabel('{:.2f} Oe'.format(experiment.rep_dc_field))
        elif label_on == 'x':
            ax.set_xlabel('{:.2f} Oe'.format(experiment.rep_dc_field))

        ax.xaxis.set_minor_formatter(NullFormatter())
        ax.yaxis.set_minor_formatter(NullFormatter())
        ax.xaxis.set_major_formatter(NullFormatter())
        ax.yaxis.set_major_formatter(NullFormatter())
        ax.yaxis.set_major_locator(NullLocator())

        ax.set_box_aspect(aspect=1)
    fig.subplots_adjust(hspace=0.08, wspace=.08)

    # Remove empty axes
    for _ in range(axs.size - n_fields):
        fig.delaxes(axs.flatten()[-1])
        axs = np.delete(axs, -1)

    colors = {
        True: 'Green',
        False: 'White'
    }
    for ax in axs.flatten():
        ax.set_facecolor(colors[on])

    fig.tight_layout()

    # Store object, one per temperature
    stores = [Toggle(field, on) for field in unique_fields]

    def onclick(event, axs_to_store):
        '''
        Callback for mouse click.
        If an axis is clicked, then switch the corresponding store
        object and the axis' color
        '''
        if event.inaxes is not None:
            axs_to_store[event.inaxes].switch(event.inaxes)
        return

    axs_to_store = {
        ax: store
        for ax, store in zip(axs.flatten(), stores)
    }

    # Connect mouse click to callback
    cid = fig.canvas.mpl_connect(
        'button_press_event',
        lambda event: onclick(event, axs_to_store)
    )

    ut.cprint(
        '\n Click the fields you want to fit (green), then close this figure.\n', # noqa
        'green'
    )

    plt.show()

    experiments = [
        experiment
        for experiment, store in zip(experiments, stores)
        if store.on
    ]

    fig.canvas.mpl_disconnect(cid)

    if not len(experiments):
        ut.cprint('\n Error: No data selected.\n', 'red')
        sys.exit(1)

    return experiments


class Toggle():
    '''
    Helper class for interactive_t_select
    '''

    def __init__(self, temperature, on):

        self.on = on
        self.temperature = temperature

    def switch(self, ax):

        if self.on:
            self.on = False
            ax.set_facecolor('White')
        else:
            self.on = True
            ax.set_facecolor('Green')

        plt.draw()

        return


def interactive_ac_model_select(experiments: list[Experiment],
                                x_var: str = 'T') -> Model:
    '''
    Creates cole cole plot of experimental data at a given field
    with radiobuttons specifying which model the user wants to fit with.

    Parameters
    ----------
    experiments: list[Experiment]
        experiments to plot
    x_var: str, default {'T', 'H'}
        Controls datapoint colour specification according to either \n
        temperature (T) or DC field (H)

    Returns
    -------
    Model
        Model class (uninstantiated) selected by user

    Raises
    ------
    ValueError
        If x_var is not T or H
    '''

    if x_var == 'T':
        temperatures = [
            experiment.rep_temperature for experiment in experiments
        ]
        field = experiments[0].rep_dc_field
        colors = cmaps['coolwarm'].resampled(len(temperatures))
    elif x_var == 'H':
        temperature = experiments[0].rep_temperature
        fields = [
            experiment.rep_dc_field for experiment in experiments
        ]
        colors = cmaps['coolwarm'].resampled(len(fields))
    else:
        raise ValueError(f'Unknown x_var "{x_var}" specified')

    fig, (ax, ax2) = plt.subplots(
        1,
        2,
        sharex='none',
        sharey='none',
        figsize=(8.25, 6.),
        num='Select AC Susceptibility Model',
        gridspec_kw={'width_ratios': [10, 1]}
    )
    if x_var == 'T':
        supt = 'Cole-Cole plot at {:4.1f} Oe.'.format(field)
        ratio = np.linspace(0, 1, len(temperatures))
    elif x_var == 'H':
        supt = 'Cole-Cole plot at {:.2f} K.'.format(temperature)
        ratio = np.linspace(0, 1, len(fields))
    else:
        raise ValueError(f'Unknown x_var "{x_var}" specified')

    supt += '\nSelect model by clicking the circle -->'
    fig.suptitle(supt, fontsize=10)

    # Plot cole-cole for each temperature
    for it, experiment in enumerate(experiments):
        if x_var == 'T':
            if (it in [0, len(temperatures) - 1] or it % 4 == 0):
                _label = '{:.2f} K'.format(experiment.rep_temperature)
            else:
                _label = ''

        elif x_var == 'H':
            if (it in [0, len(fields) - 1] or it % 4 == 0):
                _label = '{:4.1f} Oe'.format(experiment.rep_dc_field)
            else:
                _label = ''
        else:
            raise ValueError(f'Unknown x_var "{x_var}" specified')

        ax.plot(
            experiment.real_sus,
            experiment.imag_sus,
            'o',
            color=colors(ratio[it]),
            label=_label
        )

    ax.legend(
        loc=0, fontsize='small', numpoints=1, ncol=2, frameon=False
    )
    ax.set_xlabel(
        r'$\chi^{\prime}$  (cm$^\mathregular{3}$ mol$^\mathregular{-1}$)'
    )
    ax.set_ylabel(
        r'$\chi^{\prime\prime}$ (cm$^\mathregular{3}$ mol$^\mathregular{-1}$)'
    )

    ax.xaxis.set_minor_locator(AutoMinorLocator())
    ax.yaxis.set_minor_locator(AutoMinorLocator())

    print('\n Select the model function:')
    print('\n  Debye             -> Single relaxation process.')
    print('\n  Generalised Debye -> Single relaxation process with a distribution of τ.') # noqa
    print('\n  Havriliak-Negami  -> Single relaxation process with an asymmetric distribution of τ.') # noqa
    print('\n  Cole-Davidson     -> Single relaxation process with an upper cutoff in the distribution of τ.') # noqa
    print('\n  Double Gen. Debye   -> Two distinct relaxation processes, each with a distribution of τ.') # noqa
    print('\n  Double Gen. Debye (Equal χ)   -> Two distinct relaxation processes with equal χ and α, but different τ.') # noqa

    supported_models = {
        DebyeModel.DISP_NAME: DebyeModel,
        GeneralisedDebyeModel.DISP_NAME: GeneralisedDebyeModel,
        HavriliakNegamiModel.DISP_NAME: HavriliakNegamiModel,
        ColeDavidsonModel.DISP_NAME: ColeDavidsonModel,
        DoubleGDebyeModel.DISP_NAME: DoubleGDebyeModel,
        DoubleGDebyeEqualChiModel.DISP_NAME: DoubleGDebyeEqualChiModel
    }

    # Create radiobuttons
    radio = RadioButtons(
        ax2,
        labels=[
            f' {name}'
            for name in supported_models.keys()
        ],
        radio_props={
            's': 100.,
            'facecolor': 'blue'
        }
    )

    # Set initial facecolor of buttons as white
    # this becomes blue when clicked
    radio._buttons.set_facecolor(
        [
            [0, 0, 0, 0] for _ in range(len(supported_models))
        ]
    )

    def callback(label, store):
        label = label.lstrip()
        store['model'] = supported_models[label]
        plt.close()
        fig.canvas.stop_event_loop()
        ut.cprint('\n {} has been selected\n'.format(label), 'green')
        return

    modstore = {
        'model': None
    }

    radio.on_clicked(
        lambda label: callback(label, modstore)
    )

    # Connect mouse click to callback
    cid = fig.canvas.mpl_connect(
        'close_event',
        lambda _: fig.canvas.stop_event_loop()
    )

    ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_visible(False)
    ax2.spines['left'].set_visible(False)
    ax2.spines['bottom'].set_visible(False)

    fig.tight_layout()

    plt.show()
    fig.canvas.mpl_disconnect(cid)
    plt.ioff()

    if modstore['model'] is None:
        ut.cprint('\n Error: No Model Selected', 'red')
        sys.exit(1)

    return modstore['model']


def plot_fitted_colecole(experiments: list[Experiment] | Experiment,
                         models: list[Model] | Model, save: bool = False,
                         show: bool = True, x_var: str = 'T',
                         save_name: str = 'fitted_cole_cole.png',
                         verbose: bool = True) -> None:
    '''
    Creates Cole-Cole plot as matplotlib figure for models and experiments.\n

    Datapoints are coloured according to values of temperature or field.

    Parameters
    ----------
    experiments: list[Experiment] | Experiment
        Experiments to which a model was successfully fitted
    models: list[Model] | Model
        Models, one per Experiment
    save: bool, default False
        If true, saves plot to file as png
    show: bool, default True
        If True, shows plot on screen
    x_var: str, default {'T', 'H'}
        Controls datapoint colour specification according to either \n
        temperature (T) or DC field (H)
    save_name: str, default 'fitted_cole_cole.png'
        If save is True, will save plot to this file name
    verbose: bool, default True
        If True, plot file location is written to terminal

    Returns
    -------
    None
    '''

    if isinstance(models, Model):
        models = [models]

    if isinstance(experiments, Experiment):
        experiments = [experiments]

    fig, axes = plt.subplots(
        2,
        1,
        sharex='none',
        sharey='none',
        figsize=(5.1, 4.8),
        gridspec_kw={'height_ratios': [0.03, 0.9]},
        num='Cole-Cole Fit'
    )
    fig.subplots_adjust(hspace=.02, wspace=.02)

    _plot_fitted_colecole(experiments, models, fig, axes, x_var=x_var)

    if save:
        fig.savefig(save_name, dpi=400)
        if verbose:
            ut.cprint(
                f'\n Fitted Cole-Cole plot saved to \n {save_name}\n',
                'cyan'
            )

    if show:
        plt.show()

    return


def qt_plot_fitted_colecole(app: QtWidgets.QApplication,
                            experiments: list[Experiment] | Experiment,
                            models: list[Model] | Model,
                            save: bool = True, show: bool = True,
                            x_var: str = 'T',
                            save_name: str = 'fitted_cole_cole.png',
                            verbose: bool = True) -> None:
    '''
    Plots fitted and experimental Cole-Cole data in qt window using matplotlib

    Parameters
    ----------
    app: QtWidgets.QApplication
        Application used by current program
        Create with `app=QtWidgets.QApplication([])`
    experiments: list[Experiment] | Experiment
        Experiments, to which a model was successfully fitted
    models: list[Model] | Model
        Models, one per Experiment
    save: bool, default True
        If true, saves plot to file as png
    show: bool, default True
        If True, shows plot on screen
    x_var: str, default {'T', 'H'}
        Controls datapoint colour specification according to either \n
        temperature (T) or DC field (H)
    save_name: str, default 'fitted_cole_cole.png'
        If save is True, will save plot to this file name
    verbose: bool, default True
        If True, plot file location is written to terminal

    Returns
    -------
    None
    '''

    if isinstance(models, Model):
        models = [models]

    if isinstance(experiments, Experiment):
        experiments = [experiments]

    window = gui.MatplotlibWindow(
        mpl_canvas=gui.ColeColeCanvas, width=4.8, height=5.1
    )

    _plot_fitted_colecole(
        experiments, models, window.sc.fig, window.sc.ax, x_var=x_var
        )

    window.sc.fig.subplots_adjust(hspace=.02, wspace=.02)

    if save:
        window.sc.fig.savefig(save_name, dpi=400)
        if verbose:
            ut.cprint(
                f'\n Fitted Cole-Cole plot saved to \n {save_name}\n',
                'cyan'
            )

    if show:
        window.show()
        # Call twice else it wont work!
        window.sc.fig.tight_layout()
        window.sc.fig.tight_layout()
        app.exec_()

    return


def _plot_fitted_colecole(experiments: list[Experiment],
                          models: list[Model], fig: plt.Figure,
                          axes: list[plt.Axes], x_var: str = 'T') -> None:
    '''
    Plots fitted and experimental Cole-Cole data on given figure and axis

    Parameters
    ----------
    experiments: list[Experiment]
        Experiments, to which a model was successfully fitted
    models: list[Model]
        Models, one per Experiment
    plt.Figure
        Matplotlib figure object
    axes: list[plt.Axis]
        Two matplotlib axis objects, first is colorbar, second is plot
    x_var: str, default {'T', 'H'}
        Controls datapoint colour specification according to either \n
        temperature (T) or DC field (H)

    Returns
    -------
    None

    Raises
    ------
    ValueError
        If x_var is not T or H
    '''

    if x_var == 'T':
        fitted_vals = [
            model.temperature for model in models if model.fit_status
        ]
        colors = cmaps['coolwarm'].resampled(len(fitted_vals))
    elif x_var == 'H':
        fitted_vals = [
            model.dc_field for model in models if model.fit_status
        ]
        colors = cmaps['coolwarm'].resampled(len(fitted_vals))
    else:
        raise ValueError(f'Unknown x_var "{x_var}" specified')

    ratio = np.linspace(0, 1, np.sum(
        [model.fit_status for model in models])
    )
    # colors = cmaps['coolwarm'].resampled(len(fitted_temps))

    # Experimental data
    count = -1
    for experiment, model in zip(experiments, models):

        # label name
        if x_var == 'T':
            labelname = '{:.2f} K'.format(model.temperature)
        elif x_var == 'H':
            labelname = '{:.1f} K'.format(model.dc_field)
        else:
            raise ValueError(f'Unknown x_var "{x_var}" specified')

        if not model.fit_status:
            continue

        count += 1

        # Plot Cole-Cole
        axes[1].plot(
            experiment.real_sus,
            experiment.imag_sus,
            'o',
            markersize=4,
            fillstyle='none',
            label=labelname,
            color=colors(ratio[count])
        )

        # Convert linear to angular frequency
        freq_grid = np.logspace(
            np.log10(np.min(experiment.ac_freqs * 2. * np.pi)),
            np.log10(np.max(experiment.ac_freqs * 2. * np.pi)),
            100
        )

        # Get model values at provided frequencies
        [chips, chipps] = model.model(model.final_var_values, freq_grid)

        axes[1].plot(
            chips,
            chipps,
            '-',
            color=colors(ratio[count]),
            lw=1
        )

    gui.create_ac_temp_colorbar(
        axes[0], fig, fitted_vals, colors, x_var
        )

    # Put the x-labels of the colourbar on top
    axes[0].xaxis.set_ticks_position('top')

    # Add minor ticks
    axes[1].xaxis.set_minor_locator(AutoMinorLocator())
    axes[1].yaxis.set_minor_locator(AutoMinorLocator())

    # Remove frames
    axes[1].spines['top'].set_visible(False)
    axes[1].spines['right'].set_visible(False)

    # Set labels for the axes
    axes[1].set_xlabel(
        r'$\chi^{\prime}$  (cm$^\mathregular{3}$ mol$^\mathregular{-1}$)'
    )
    axes[1].set_ylabel(
        r'$\chi^{\prime\prime}$ (cm$^\mathregular{3}$ mol$^\mathregular{-1}$)'
    )

    fig.tight_layout()

    return


def plot_single_fitted_cole_cole(experiment: Experiment,
                                 model: Model, save: bool = False,
                                 show: bool = True,
                                 save_name: str = 'single_fitted_cole_cole.png', # noqa
                                 verbose: bool = True) -> None:
    '''
    Plots fitted and experimental Cole-Cole data for a single
    experiment

    Parameters
    ----------
    experiments: Experiment
        Experiments, to which a model was successfully fitted
    models: Model
        Models, one per Experiment
    plt.Figure
        Matplotlib figure object
    axes: list[plt.Axis]
        Two matplotlib axis objects, first is colorbar, second is plot
    save: bool, default False
        If true, saves plot to file as png
    show: bool, default True
        If True, shows plot on screen
    save_name: str, default 'fitted_cole_cole.png'
        If save is True, will save plot to this file name
    verbose: bool, default True
        If True, plot file location is written to terminal

    Returns
    -------
    None
    '''

    fig, ax = plt.subplots(
        1,
        1,
        figsize=(5.1, 4.8),
        num='Cole-Cole at {:.5f} K and {:.5f} Oe with fit'.format(
            experiment.rep_temperature,
            experiment.rep_dc_field
        )
    )

    # Plot Cole-Cole
    ax.plot(
        experiment.real_sus,
        experiment.imag_sus,
        'o',
        markersize=4,
        fillstyle='none',
        label='Experiment',
        color='k'
    )

    # Plot model if fit successful
    if model.fit_status:
        # Convert linear to angular frequency
        freq_grid = np.logspace(
            np.log10(np.min(experiment.ac_freqs * 2. * np.pi)),
            np.log10(np.max(experiment.ac_freqs * 2. * np.pi)),
            100
        )

        # Get model values at provided frequencies
        [chips, chipps] = model.model(model.final_var_values, freq_grid)

        ax.plot(
            chips,
            chipps,
            '-',
            color='k',
            label=f'{model.DISP_NAME} model',
            lw=1
        )

    ax.legend(frameon=False)

    # Remove frames
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    # Set labels for the axes
    ax.set_xlabel(
        r'$\chi^{\prime}$  (cm$^\mathregular{3}$ mol$^\mathregular{-1}$)'
    )
    ax.set_ylabel(
        r'$\chi^{\prime\prime}$ (cm$^\mathregular{3}$ mol$^\mathregular{-1}$)'
    )

    # Set minor ticks
    ax.xaxis.set_minor_locator(AutoMinorLocator())
    ax.yaxis.set_minor_locator(AutoMinorLocator())

    fig.tight_layout()

    if save:
        fig.savefig(save_name, dpi=400)
        if verbose:
            ut.cprint(
                f'\n Fitted Cole-Cole plot saved to \n {save_name}\n',
                'cyan'
            )

    if show:
        plt.show()

    return


def plot_fitted_susceptibility(experiments: list[Experiment] | Experiment,
                               models: list[Model] | Model, save: bool = True,
                               show: bool = True, x_var: str = 'T',
                               save_name: str = 'fitted_susceptibility.png',
                               verbose: bool = True) -> None:
    '''

    Creates plot of in- and out-of-phase susceptibilities
    as matplotlib figure for models and experiments

    Parameters
    ----------
    experiments: list[Experiment] | Experiment
        Experiments, to which a model was successfully fitted
    models: list[Model] | Model
        Models, one per Experiment
    save: bool, default True
        If true, saves plot to file as png
    show: bool, default True
        If True, shows plot on screen
    x_var: str, default {'T', 'H'}
        Controls datapoint colour specification according to either \n
        temperature (T) or DC field (H)
    save_name: str, default 'fitted_susceptibility.png'
        If save is True, will save plot to this file name
    verbose: bool, default True
        If True, plot file location is written to terminal

    Returns
    -------
    None
    '''

    if isinstance(models, Model):
        models = [models]

    if isinstance(experiments, Experiment):
        experiments = [experiments]

    fig = plt.figure(
        figsize=(6.5, 4.5),
        num='AC Susceptibility Fit'
    )
    spec = fig.add_gridspec(3, 1, height_ratios=[0.05, 1, 1])
    ax1 = fig.add_subplot(spec[0, 0])
    ax2 = fig.add_subplot(spec[1, 0])
    ax3 = fig.add_subplot(spec[2, 0], sharex=ax2)

    axes = [ax1, ax2, ax3]

    fig.subplots_adjust(hspace=.05, wspace=.02)

    _plot_fitted_susceptibility(experiments, models, fig, axes, x_var=x_var)

    if save:
        fig.savefig(save_name, dpi=400)
        if verbose:
            ut.cprint(
                f'\n Fitted Susceptibility plot saved to \n {save_name}\n',
                'cyan'
            )
    if show:
        plt.show()

    return


def qt_plot_fitted_susceptibility(app: QtWidgets.QApplication,
                                  experiments: list[Experiment] | Experiment,
                                  models: list[Model] | Model,
                                  save: bool = True, show: bool = True,
                                  x_var: str = 'T',
                                  save_name: str = 'fitted_susceptibility.png',
                                  verbose: bool = True) -> None:
    '''

    Plots experimental and model in- and out-of-phase susceptibility data
    in qt window using matplotlib

    Parameters
    ----------
    app: QtWidgets.QApplication
        Application used by current program
        Create with `app=QtWidgets.QApplication([])`
    experiments: list[Experiment] | Experiment
        Experiments, to which a model was successfully fitted
    models: list[Model] | Model
        Models, one per Experiment
    save: bool, default True
        If true, saves plot to file as png
    show: bool, default True
        If True, shows plot on screen
    x_var: str, default {'T', 'H'}
        Controls datapoint colour specification according to either \n
        temperature (T) or DC field (H)
    save_name: str, default 'fitted_susceptibility.png'
        If save is True, will save plot to this file name
    verbose: bool, default True
        If True, plot file location is written to terminal

    Returns
    -------
    None
    '''

    if isinstance(models, Model):
        models = [models]

    if isinstance(experiments, Experiment):
        experiments = [experiments]

    window = gui.MatplotlibWindow(
        mpl_canvas=gui.SusceptibilityCanvas, height=4.5, width=6.5)
    window.setWindowTitle('Fitted AC Susceptibility')

    window.sc.fig.subplots_adjust(hspace=.05, wspace=.02)

    _plot_fitted_susceptibility(
        experiments, models, window.sc.fig, window.sc.ax, x_var=x_var
    )

    if save:
        window.sc.fig.savefig(save_name, dpi=400)
        if verbose:
            ut.cprint(
                f'\n Fitted Susceptibility plot saved to \n {save_name}\n',
                'cyan'
            )

    if show:
        window.show()
        # Call twice else it wont work!
        window.sc.fig.tight_layout()
        window.sc.fig.tight_layout()
        app.exec_()

    return


def _plot_fitted_susceptibility(experiments: list[Experiment],
                                models: list[Model], fig: plt.Figure,
                                axes: plt.Axes, x_var: str = 'T') -> None:
    '''
    Plots experimental and model in- and out-of-phase susceptibility data
    on given figure and axes

    Parameters
    ----------
    experiments: list[Experiment]
        Experiments, to which a model was successfully fitted
    models: list[Model]
        Models, one per Experiment
    plt.Figure
        Matplotlib figure object
    axes: list[plt.Axis]
        Three matplotlib axis objects\n
        First is colorbar, second is real susc, third is imag susc
    x_var: str, default {'T', 'H'}
        Controls datapoint colour specification according to either \n
        temperature (T) or DC field (H)

    Returns
    -------
    None

    Raises
    ------
    ValueError
        If x_var is not T or H
    '''

    if x_var == 'T':
        fitted_vals = [
            model.temperature for model in models if model.fit_status
        ]
        colors = cmaps['coolwarm'].resampled(len(fitted_vals))
    elif x_var == 'H':
        fitted_vals = [
            model.dc_field for model in models if model.fit_status
        ]
        colors = cmaps['coolwarm'].resampled(len(fitted_vals))
    else:
        raise ValueError(f'Unknown x_var "{x_var}" specified')

    ratio = np.linspace(0, 1, np.sum(
        [model.fit_status for model in models])
    )

    # colors = cmaps['coolwarm'].resampled(len(fitted_temps))

    # Experimental data
    count = -1
    for experiment, model in zip(experiments, models):

        if not model.fit_status:
            continue

        count += 1

        # Plots will be in linear frequency to compare to experiment
        freq_grid = np.logspace(
            np.log10(np.min(experiment.ac_freqs)),
            np.log10(np.max(experiment.ac_freqs)),
            100
        )

        # Get model values at provided frequencies
        # Model takes angular frequencies
        [chips, chipps] = model.model(
            model.final_var_values,
            freq_grid * 2 * np.pi
        )
        # label name
        if x_var == 'T':
            labelname = '{:.2f} K'.format(model.temperature)
        elif x_var == 'H':
            labelname = '{:.1f} K'.format(model.dc_field)
        else:
            raise ValueError(f'Unknown x_var "{x_var}" specified')

        # Real
        axes[1].semilogx(
            experiment.ac_freqs,
            experiment.real_sus,
            'o',
            markersize=4,
            fillstyle='none',
            label=labelname,
            color=colors(ratio[count])
        )
        axes[1].semilogx(
            freq_grid,
            chips,
            '-',
            color=colors(ratio[count]),
            lw=1
        )
        # Imaginary
        axes[2].semilogx(
            experiment.ac_freqs,
            experiment.imag_sus,
            'o',
            markersize=4,
            fillstyle='none',
            label=labelname,
            color=colors(ratio[count])
        )
        axes[2].semilogx(
            freq_grid,
            chipps,
            '-',
            color=colors(ratio[count]),
            lw=1
        )

    gui.create_ac_temp_colorbar(
        axes[0], fig, fitted_vals, colors, x_var
        )

    # Add minor ticks to y axis
    # and set x tick format as decimal, not powers of 10
    for axis in axes[1:]:
        axis.yaxis.set_minor_locator(AutoMinorLocator())
        axis.xaxis.set_minor_locator(
            LogLocator(base=10, subs='auto', numticks=999)
        )
        axis.xaxis.set_major_formatter(
            FuncFormatter(lambda y, _: '{:g}'.format(y))
        )

    axes[0].xaxis.set_ticks_position('top')
    axes[0].xaxis.set_label_position('top')

    # Get rid of the frames of susceptibility plots
    for axis in [axes[1], axes[2]]:
        axis.spines['top'].set_visible(False)
        axis.spines['right'].set_visible(False)

    # Get rid of the x-labels of real susceptibility
    axes[1].set_ylabel(
        r'$\chi^{\prime}$  (cm$^\mathregular{3}$ mol$^\mathregular{-1}$)'
    )
    axes[2].set_xlabel('Wave Frequency (Hz)')
    axes[2].set_ylabel(
        r'$\chi^{\prime\prime}$ (cm$^\mathregular{3}$ mol$^\mathregular{-1}$)'
    )

    # Disable X' x-tick labels
    # sometimes they still show up even if axes[0] and axes[1] have sharex=True
    plt.setp(axes[1].get_xticklabels(), visible=False)

    return


def plot_single_fitted_susceptibility(experiment: Experiment,
                                      model: Model, save: bool = False,
                                      show: bool = True,
                                      save_name: str = 'single_fitted_cole_cole.png', # noqa
                                      verbose: bool = True) -> None:
    '''
    Plots fitted and experimental susceptibility data for a single
    experiment

    Parameters
    ----------
    experiments: Experiment
        Experiments, to which a model was successfully fitted
    models: Model
        Models, one per Experiment
    plt.Figure
        Matplotlib figure object
    axes: list[plt.Axis]
        Two matplotlib axis objects, first is colorbar, second is plot
    save: bool, default False
        If true, saves plot to file as png
    show: bool, default True
        If True, shows plot on screen
    save_name: str, default 'fitted_cole_cole.png'
        If save is True, will save plot to this file name
    verbose: bool, default True
        If True, plot file location is written to terminal

    Returns
    -------
    None
    '''

    fig, [ax1, ax2] = plt.subplots(
        2,
        1,
        figsize=(6.5, 4.5),
        num='AC susceptibility at {:.5f} K and {:.5f} Oe with fit'.format(
            experiment.rep_temperature,
            experiment.rep_dc_field
        ),
        sharex=True
    )

    # Plot experiment
    # Real
    ax1.semilogx(
        experiment.ac_freqs,
        experiment.real_sus,
        'o',
        markersize=4,
        fillstyle='none',
        color='black',
        label='Experiment'
    )
    # Imaginary
    ax2.semilogx(
        experiment.ac_freqs,
        experiment.imag_sus,
        'o',
        markersize=4,
        fillstyle='none',
        color='black',
        label='Experiment'
    )

    # Plot model if fit successful
    if model.fit_status:
        # Plots will be in linear frequency to compare to experiment
        freq_grid = np.logspace(
            np.log10(np.min(experiment.ac_freqs)),
            np.log10(np.max(experiment.ac_freqs)),
            100
        )

        # Get model values at provided frequencies
        # Model takes angular frequencies
        [chips, chipps] = model.model(
            model.final_var_values,
            freq_grid * 2 * np.pi
        )
        # Real
        ax1.semilogx(
            freq_grid,
            chips,
            lw=1,
            color='k',
            label=f'{model.DISP_NAME} model'
        )
        # Imaginary
        ax2.semilogx(
            freq_grid,
            chipps,
            lw=1,
            color='k',
            label=f'{model.DISP_NAME} model'
        )

    ax1.legend(frameon=False)

    # Get rid of the frames of susceptibility plots
    for axis in [ax1, ax2]:
        axis.spines['top'].set_visible(False)
        axis.spines['right'].set_visible(False)

    # Get rid of the x-labels of real susceptibility
    ax1.set_ylabel(
        r'$\chi^{\prime}$  (cm$^\mathregular{3}$ mol$^\mathregular{-1}$)'
    )
    ax2.set_xlabel('Wave Frequency (Hz)')
    ax2.set_ylabel(
        r'$\chi^{\prime\prime}$ (cm$^\mathregular{3}$ mol$^\mathregular{-1}$)'
    )

    # Add minor ticks to y axis
    # and set x tick format as decimal, not powers of 10
    for axis in [ax1, ax2]:
        axis.yaxis.set_minor_locator(AutoMinorLocator())
        axis.xaxis.set_minor_locator(
            LogLocator(base=10, subs='auto', numticks=999)
        )
        axis.xaxis.set_major_formatter(
            FuncFormatter(lambda y, _: '{:g}'.format(y))
        )

    if save:
        fig.savefig(save_name, dpi=400)
        if verbose:
            ut.cprint(
                f'\n Fitted Susceptibility plot saved to \n {save_name}\n',
                'cyan'
            )

    if show:
        plt.show()

    return


def write_model_data(experiments: list[Experiment], models: list[Model],
                     file_name: str = 'ac_model_data.csv',
                     verbose: bool = True,
                     delimiter: str = ',',
                     extra_comment: str = '') -> None:
    '''
    Creates a csv file containing χ' and χ'' calculated using the model
    function with fitted parameters. Temperatures for which a fit was
    not possible are not included.

    Parameters
    ----------
    experiments: list[Experiment]
        Experiments, to which a model was successfully fitted
    models: list[Model]
        Models, one per Experiment
    file_name: str, default 'ac_model_data.csv'
        Name of output file
    verbose: bool, default True
        If True, file location is written to terminal
    delimiter: str, default ','
        Delimiter used in .csv file, usually either ',' or ';'
    extra_comment: str, optional
        Extra comments to add to file after ccfit2 version line
        Must include comment character # for each new line

    Returns
    -------
    None

    Raises
    ------
    ValueError
        If output array is empty
    '''

    # Make header
    header = [
        'Temperature (K)',
        'Field (oe)'
        'Linear Wave Frequency (s^-1)',
        'chi\' (cm^{3} mol^{-1})',
        'chi\'\' (cm^{3} mol^{-1})'
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
    # susceptibility using model parameters
    for model, experiment in zip(models, experiments):

        if not model.fit_status:
            continue

        freq_grid = np.logspace(
            np.log10(np.min(experiment.ac_freqs)),
            np.log10(np.max(experiment.ac_freqs)),
            100
        )

        # Get model values at provided frequencies
        [chips, chipps] = model.model(
            model.final_var_values, freq_grid * 2 * np.pi
        )

        _temps = [model.temperature] * len(chips)
        _fields = [model.dc_field] * len(chips)

        _out.append(np.array([_temps, _fields, freq_grid, chips, chipps]))

    if not len(_out):
        raise ValueError(
            'Output array contains no data, no models could be computed'
        )

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
            (
                '\n AC Model χ\' and χ\'\' vs linear '
                f'frequency written to \n {file_name}\n'
            ),
            'cyan'
        )

    return


def write_model_params(models: list[Model],
                       file_name: str = 'ac_model_params.csv',
                       verbose: bool = True, delimiter: str = ',',
                       extra_comment: str = '') -> None:
    '''
    Writes fitted and fixed parameters of a set of models to csv file.\n
    Assumes models are all of the same type, e.g. all Debye

    Parameters
    ----------
    models: list[Model]
        Models, one per temperature, must all be same type
    file_name: str, default 'ac_model_params.csv'
        Name of output file
    verbose: bool, default True
        If True, file location is written to terminal
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
    if all({isinstance(model, DoubleGDebyeEqualChiModel) for model in models}):
        model_type = DoubleGDebyeEqualChiModel
    elif all({isinstance(model, DoubleGDebyeModel) for model in models}):
        model_type = DoubleGDebyeModel
    else:
        model_type = None

    # Make header
    header = [
        'T (K)',
        'H (Oe)',
    ]
    # Fitted parameters
    for name in models[0].fit_vars.keys():
        header.append(f'{name} ({models[0].UNITS[name]})')
        header.append(f'{name}-s-dev ({models[0].UNITS[name]})')

    # Fixed parameters
    for name in models[0].fix_vars.keys():
        header.append(f'{name} ({models[0].UNITS[name]})')

    # Model-dependent headers
    if model_type in [DoubleGDebyeEqualChiModel, DoubleGDebyeModel]:
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

        for name in model.fit_vars.keys():
            _tmp += [
                model.final_var_values[name],
                model.fit_stdev[name]
            ]

        for value in model.fix_vars.values():
            _tmp.append(value)

        if model_type in [DoubleGDebyeEqualChiModel, DoubleGDebyeModel]:
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
        comments=comment
    )

    if verbose:
        ut.cprint(
            f'\n AC Model parameters written to \n {file_name}\n',
            'cyan'
        )
    return
