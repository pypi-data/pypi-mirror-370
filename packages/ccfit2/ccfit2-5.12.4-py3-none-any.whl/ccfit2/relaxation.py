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

This module contains functions and objects for working with relaxation data
'''

from . import utils as ut
from . import gui
from . import ac
from . import dc
from . import stats
from .__version__ import __version__

import datetime
import numpy as np
from numpy.typing import ArrayLike, NDArray
from scipy.optimize import least_squares
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter, AutoMinorLocator
import matplotlib.colors as mcolors
from abc import ABC, abstractmethod
import copy
from functools import partial
from qtpy import QtWidgets, QtCore, QtGui
import pyqtgraph as pg
import pandas as pd


import warnings
warnings.filterwarnings('ignore', '.*GUI is implemented.*')
warnings.filterwarnings('ignore', 'invalid value encountered in power')
warnings.filterwarnings('ignore', 'invalid value encountered in multiply')
warnings.filterwarnings('ignore', 'invalid value encountered in log10')
warnings.filterwarnings('ignore', 'divide by zero encountered in log10')
warnings.filterwarnings('ignore', 'divide by zero encountered in power')
warnings.filterwarnings('ignore', 'divide by zero encountered in reciprocal')
warnings.filterwarnings('ignore', 'invalid value encountered in divide')
warnings.filterwarnings('ignore', 'overflow encountered in power')
warnings.filterwarnings('ignore', 'overflow encountered in scalar power')
warnings.filterwarnings('ignore', 'overflow encountered in multiply')
warnings.filterwarnings('ignore', 'overflow encountered in square')
warnings.filterwarnings('ignore', 'divide by zero encountered in divide')

pg.setConfigOption('foreground', 'k')


class Dataset(ABC):
    '''
    Abstract base class which contains experimental rates, rate bounds (+-)
    and independent variable on which the rate depends

    Parameters
    ----------
    rates: array_like
        Relaxation rates in seconds^-1
    dep_vars: array_like
        Values of independent variable of which the rate is a function\n
        e.g. Field, Temperature
    lograte_pm: array_like
        Plus-Minus of log10(rates) in logspace, assumed to be symmetric\n
        Not! log(rate_pm)

    Attributes
    ----------
    rates: ndarray of floats
        Relaxation rates in seconds^-1
    dep_vars: ndarray of floats
        Values of independent variable of which the rate is a function\n
        e.g. Field, Temperature
    lograte_pm: ndarray of floats
        Plus-minus of log10(rates) in logspace,
        assumed to be symmetric, size is (n_rates,1)\n
        Not! log(rate_pm)
    rate_pm: ndarray of floats
        Plus-minus of rates in linspace,
        will be asymmetric, size is (n_rates,2)\n
        not! 10**(lograte_pm)
    '''
    @property
    @abstractmethod
    def IDEP_VAR_NAMES() -> list[str]:
        'str names of independent variables with which rate varies e.g. Field'
        raise NotImplementedError

    @property
    @abstractmethod
    def IDEP_VAR_LABELS() -> list[str]:
        'str label of independent variables with which rate varies e.g. H'
        raise NotImplementedError

    @property
    @abstractmethod
    def IDEP_VAR_UNITS() -> list[str]:
        'str units of independent variables with which rate varies e.g. Oe'
        raise NotImplementedError

    def __init__(self, rates: ArrayLike, dep_vars: ArrayLike,
                 lograte_pm: ArrayLike = []):

        self.rates = np.asarray(rates, dtype=float)
        self.dep_vars = np.asarray(dep_vars, dtype=float)
        self.lograte_pm = np.asarray(lograte_pm, dtype=float)

        return

    @property
    def lograte_pm(self) -> NDArray:
        return self._lograte_pm

    @lograte_pm.setter
    def lograte_pm(self, value: ArrayLike):

        if isinstance(value, float):
            raise ValueError('lograte_pm must be list')
        elif len(np.shape(value)) != 1:
            raise ValueError('lograte_pm must be symmetric, i.e. (1, n_rates)')
        if not len(value):
            self._lograte_pm = []
            self.rate_pm = []
        else:
            # Use symmetric lograte_pm to obtain difference in rates in linear
            # space - n.b. these will be asymmetric
            self._lograte_pm = np.asarray(value, dtype=float)
            self.rate_pm = self.lograte_pm_to_pm(self.rates, self.lograte_pm)

            # Ensure that any values close to zero are set to zero
            # these may sometimes be negative
            self.rate_pm = np.array([
                [
                    0.0 if abs(val) < 1E-10 else val
                    for val in bound
                ]
                for bound in self.rate_pm
            ])

        return

    @classmethod
    def from_raw(cls, dep_vars: ArrayLike, lntaus: ArrayLike,
                 lntau_stdevs: ArrayLike = [],
                 lntau_fus: ArrayLike = [],
                 lntau_fls: ArrayLike = []) -> 'Dataset':
        '''
        Creates dataset from raw values of rates, dep_vars, ln standard
        deviation, and upper and lower lntau values

        Parameters
        ----------
        dep_vars: array_like
            Values of independent variable of which the rate is a function\n
            e.g. Field, Temperature
        lntaus: array_like
            ln(tau) values  (ln(seconds))
        lntau_stdevs: array_like, default []
            Standard deviation of ln(tau) (ln(seconds)).\n
            These are intrinsic to AC or DC model
        lntau_fus: array_like, default []
            Upper bound of fitted ln(tau) computed using uncertainties from
            fitted parameters
        lntau_fls: array_like, default []
            Lower bound of fitted ln(tau) computed using uncertainties from
            fitted parameters

        Returns
        -------
        Dataset
           Single Dataset, rate as function of dep_var
        '''

        dep_vars = np.asarray(dep_vars, dtype=float)
        lntaus = np.asarray(lntaus, dtype=float)
        lntau_stdevs = np.asarray(lntau_stdevs, dtype=float)
        lntau_fus = np.asarray(lntau_fus, dtype=float)
        lntau_fls = np.asarray(lntau_fls, dtype=float)

        taus = np.array([
            np.exp(lntime)
            for lntime in lntaus
        ])

        rates = [tau**-1 for tau in taus]

        # Upper and lower lntau using standard deviation
        # from distribution
        if len(lntau_stdevs):
            upper_tau = np.exp(lntaus + lntau_stdevs)
            lower_tau = np.exp(lntaus - lntau_stdevs)
            # If upper and lower bounds present, then take element wise
            # maximum of these to find max standard deviation
            # considering both stdev inherent to AC/DC model distribution,
            # and from fitting of AC/DC model parameters
            # or from upper lower bounds
            if len(lntau_fus):
                upper_tau = np.maximum(np.exp(lntau_fus), upper_tau)
            if len(lntau_fls):
                lower_tau = np.maximum(np.exp(lntau_fls), lower_tau)
        else:
            # If just bounds present, then use these
            if len(lntau_fus):
                upper_tau = np.exp(lntau_fus)
            if len(lntau_fls):
                lower_tau = np.exp(lntau_fls)

        if not len(lntau_fls) and not len(lntau_fus) and not len(lntau_stdevs):
            lograte_pm = []
        else:
            # Difference in rates in log space, used as standard deviation in
            # log(tau), required by fitting routine
            # THIS IS NOT!!!! log10(rate_ul_diff)
            # log(sigma(tau)) != sigma(log(tau))
            lograte_ul_diff = [
                np.log10(rates) - np.log10(upper_tau**-1),
                np.log10(lower_tau**-1) - np.log10(rates)
            ]

            # Take maximum of difference in rates in log space
            # If differences arise from model stdev then will be symmetric
            # in log space
            # but if from previous least squares will be asymmetric
            # so take largest and treat as symmetric
            lograte_pm = np.maximum(
                lograte_ul_diff[0],
                lograte_ul_diff[1]
            )

        return cls(rates, dep_vars, lograte_pm)

    @classmethod
    def from_ac_dc(cls, models: list[ac.Model | dc.Model]) -> 'Dataset':
        '''
        Creates Dataset from list of fitted AC or DC models

        Parameters
        ----------
        models: list[ac.Model]
            Models of AC or DC data, at least one in list must be\n
            successfully fitted (i.e. fit_status=True)\n
            Only models with a single relaxation time are supported.

        Returns
        -------
        list[Dataset]
            Datasets, each rate vs dep_vars

        Raises
        ------
        TypeError
            If any of the models are Double Tau Models
        '''
        double_tau_models = [
            ac.DoubleGDebyeEqualChiModel,
            ac.DoubleGDebyeModel,
            dc.DoubleExponentialModel
        ]

        ml1 = []

        for model in models:
            # Split double tau models into two single tau models
            if type(model) in double_tau_models:
                raise TypeError('Double Tau models are unsupported')
            else:
                ml1.append(model)

        # Process first set of models
        datasets = [
            cls.from_raw(
                *cls.extract_ac_dc_model(
                    ml1,
                    cls.IDEP_VAR_NAMES[0].lower()
                )
            )
        ]

        return datasets

    @classmethod
    def _from_ccfit2_files(cls, file_names: str | list[str]) -> 'Dataset':
        '''
        DEPRECATED - Use from_ccfit2_csv()
        Creates Dataset from ccfit2 AC/DC parameter file(s)

        Parameters
        ----------
        file_names: str | list[str]
            Filenames of ccfit2 AC/DC parameter file(s)

        Returns
        -------
        Dataset
            Single Dataset, rate vs independent variable

        Raises
        ------
        ValueError if either independent variable or lntau values\n
        cannot be found in file
        '''

        ut.cprint(
            'Using a legacy ccfit2 _params.out file\n',
            'black_yellowbg'
        )
        ut.cprint(
            'This functionality will be removed soon, convert your file to .csv !', # noqa
            'black_yellowbg'
        )

        if isinstance(file_names, str):
            file_names = [file_names]

        # Find encoding of input files
        encodings = [
            ut.detect_encoding(file)
            for file in file_names
        ]

        headers = {
            'lntaus': ['<ln(tau)>', '<ln(tau)> (ln(s))'],
            'lntau_stdevs': ['sigma_<ln(tau)>', 'sigma_<ln(tau)> (ln(s))', 'sigma_ln(tau)', 'sigma_ln(tau) (ln(s))'], # noqa
            'lntau_fus': ['fit_upper_ln(tau)', 'fit_upper_ln(tau) (ln(s))', 'fit_upper_<ln(tau)>', 'fit_upper_<ln(tau)> (ln(s))'], # noqa
            'lntau_fls': ['fit_lower_ln(tau)', 'fit_lower_ln(tau) (ln(s))', 'fit_lower_<ln(tau)>', 'fit_lower_<ln(tau)> (ln(s))'], # noqa
        }

        if cls.IDEP_VAR_NAMES[0] == 'Field':
            headers['fields'] = ['H', 'H (Oe)']
        elif cls.IDEP_VAR_NAMES[0] == 'Temperature':
            headers['temperatures'] = ['H', 'H (Oe)']
        else:
            raise ValueError('Unknown DEP_VAR_NAME in Dataset implementation')

        dep_vars, lntaus, lntau_stdevs, lntau_fls, lntau_fus = [], [], [], [], [] # noqa

        bounds = True

        for file, encoding in zip(file_names, encodings):

            # Get file headers
            header_indices, _ = ut.parse_headers(
                file, 0, headers, delim=None
            )

            if header_indices['fields'] == -1:
                raise ValueError(f'Cannot find fields in {file}')
            elif header_indices['lntaus'] == -1:
                raise ValueError(f'Cannot find <ln(tau)> in {file}')

            # Columns to extract from file
            cols = [header_indices[he] for he in headers.keys()]

            converters = {
                it: lambda s: (float(s.strip() or np.nan)) for it in cols
            }

            # Read required columns of file
            data = np.loadtxt(
                file,
                skiprows=1,
                converters=converters,
                usecols=cols,
                encoding=encoding
            )

            # If bound headers not found then turn off bounds for all files
            optional_indices = [
                header_indices['lntau_stdevs'],
                header_indices['lntau_fus'],
                header_indices['lntau_fls']
            ]
            if -1 not in optional_indices:
                lntau_stdevs += data[:, 2].tolist()
                lntau_fus += data[:, 3].tolist()
                lntau_fls += data[:, 4].tolist()
            else:
                bounds = False

            # Add to big lists
            dep_vars += data[:, 0].tolist()
            lntaus += data[:, 1].tolist()

        # Sort all data by field
        order = sorted(range(len(dep_vars)), key=lambda k: dep_vars[k])

        if bounds:
            # Create dataset from all data
            dataset = cls.from_raw(
                [dep_vars[o] for o in order],
                [lntaus[o] for o in order],
                [lntau_stdevs[o] for o in order],
                [lntau_fus[o] for o in order],
                [lntau_fls[o] for o in order]
            )

        else:
            dataset = cls(
                [np.exp(-lntaus[o]) for o in order],
                [dep_vars[o] for o in order]
            )

        return dataset

    @classmethod
    def from_ccfit2_csv(cls, file_names: str | list[str]) -> 'Dataset':
        '''
        Creates Dataset from ccfit2 AC/DC parameter csv file(s)

        Parameters
        ----------
        file_names: str | list[str]
            Filenames of ccfit2 AC/DC parameter file(s)

        Returns
        -------
        Dataset
            Single Dataset, rate vs independent variable

        Raises
        ------
        ValueError if either independent variable (T, H) or lntau values\n
        cannot be found in file
        '''

        if isinstance(file_names, str):
            file_names = [file_names]

        name_to_headers = {
            'lntaus': ['<ln(tau)>', '<ln(tau)> (ln(s))'],
            'lntau_stdevs': ['sigma_<ln(tau)>', 'sigma_<ln(tau)> (ln(s))', 'sigma_ln(tau)', 'sigma_ln(tau) (ln(s))'], # noqa
            'lntau_fus': ['fit_upper_ln(tau)', 'fit_upper_ln(tau) (ln(s))', 'fit_upper_<ln(tau)>', 'fit_upper_<ln(tau)> (ln(s))'], # noqa
            'lntau_fls': ['fit_lower_ln(tau)', 'fit_lower_ln(tau) (ln(s))', 'fit_lower_<ln(tau)>', 'fit_lower_<ln(tau)> (ln(s))'], # noqa
        }

        if cls.IDEP_VAR_NAMES[0] == 'Field':
            name_to_headers['dep_vars'] = ['H', 'H (Oe)']
        elif cls.IDEP_VAR_NAMES[0] == 'Temperature':
            name_to_headers['dep_vars'] = ['T', 'T (K)']
        else:
            raise ValueError('Unknown DEP_VAR_NAME in Dataset implementation')

        header_to_name = {
            val: key
            for key, vals in name_to_headers.items()
            for val in vals
        }

        dep_vars, lntaus, lntau_stdevs, lntau_fls, lntau_fus = [], [], [], [], [] # noqa

        both_bounds = True
        std_bound = False
        ul_bound = False

        for file in file_names:

            reader = pd.read_csv(
                file,
                sep=None,
                iterator=True,
                comment='#',
                engine='python',
                skipinitialspace=True,
                dtype=float
            )
            full_data = pd.concat(reader, ignore_index=True)
            full_data.reset_index(drop=True, inplace=True)

            # Replace headers with names
            full_data = full_data.rename(header_to_name, axis=1)
            # and remove unwanted columns
            full_data = full_data[
                full_data.columns.intersection(name_to_headers.keys())
            ]

            for name in ['dep_vars', 'lntaus']:
                if name not in full_data.columns:
                    if name == 'dep_vars':
                        raise ValueError(
                            f'Cannot find {cls.DEP_VAR_NAME} header in {file}'
                        )
                    else:
                        raise ValueError(
                            f'Cannot find {name} header in {file}'
                        )

            optional = ['lntau_stdevs', 'lntau_fus', 'lntau_fls']
            if any(name not in full_data.columns for name in optional):
                both_bounds = False
                if 'lntau_stdevs' in full_data.columns:
                    std_bound = True
                elif all(name not in full_data.columns for name in optional[1:]): # noqa
                    ul_bound = True

            # Add to big lists
            dep_vars += full_data['dep_vars'].to_list()
            lntaus += full_data['lntaus'].to_list()

            if both_bounds:
                lntau_stdevs += full_data['lntau_stdevs'].to_list()
                lntau_fls += full_data['lntau_fls'].to_list()
                lntau_fus += full_data['lntau_fus'].to_list()
            elif std_bound:
                lntau_stdevs += full_data['lntau_stdevs'].to_list()
            elif ul_bound:
                lntau_fls += full_data['lntau_fls'].to_list()
                lntau_fus += full_data['lntau_fus'].to_list()

        # Sort all data by field
        order = sorted(range(len(dep_vars)), key=lambda k: dep_vars[k])

        if both_bounds:
            # Create dataset from all data and compute bounds
            # from sigma and upper/lower data
            dataset = cls.from_raw(
                [dep_vars[o] for o in order],
                [lntaus[o] for o in order],
                lntau_stdevs=[lntau_stdevs[o] for o in order],
                lntau_fus=[lntau_fus[o] for o in order],
                lntau_fls=[lntau_fls[o] for o in order]
            )
        elif std_bound:
            # Create dataset from all data with sigma bounds
            dataset = cls.from_raw(
                [dep_vars[o] for o in order],
                [lntaus[o] for o in order],
                lntau_stdevs=[lntau_stdevs[o] for o in order],
            )
        elif ul_bound:
            # Create dataset from all data with upper lower bounds
            dataset = cls.from_raw(
                [dep_vars[o] for o in order],
                [lntaus[o] for o in order],
                lntau_fus=[lntau_fus[o] for o in order],
                lntau_fls=[lntau_fls[o] for o in order]
            )
        else:
            dataset = cls(
                [np.exp(-lntaus[o]) for o in order],
                [dep_vars[o] for o in order]
            )

        return dataset

    @classmethod
    def from_rate_files(cls, file_names: str | list[str]) -> 'Dataset':
        '''
        Creates Dataset from file(s) containingthe headers\n
        H or T, rate, <upper>, <lower>\n
        The last two are optional

        Parameters
        ----------
        file_names: str | list[str]
            Filenames of files to read

        Returns
        -------
        Dataset
            Single Dataset, H or T vs rate

        Raises
        ------
        ValueError if either fields/temperatures or lntau values cannot be
        found in file
        '''

        if isinstance(file_names, str):
            file_names = [file_names]

        # Find encoding of input files
        encodings = [
            ut.detect_encoding(file)
            for file in file_names
        ]

        headers = {
            'rate': ['rate'],
            'upper': ['upper'],
            'lower': ['lower']
        }

        if cls.IDEP_VAR_NAMES[0] == 'Field':
            headers['dep_vars'] = ['H', 'H (Oe)']
        elif cls.IDEP_VAR_NAMES[0] == 'Temperature':
            headers['dep_vars'] = ['T', 'T (K)']

        dep_vars, rates, upper, lower = [], [], [], []

        indices = []

        bounds = True

        for file, encoding in zip(file_names, encodings):

            # Get file headers
            header_indices, _ = ut.parse_headers(
                file, 0, headers, delim=None
            )

            indices.append(header_indices)

            if header_indices['dep_vars'] == -1:
                raise ValueError(f'Cannot find {cls.DEP_VAR_NAME} in {file}')
            elif header_indices['rate'] == -1:
                raise ValueError(f'Cannot find rates in {file}')

            converters = {
                it: lambda s: (float(s.strip() or np.nan))
                for it in sorted(header_indices.values())
            }

            # Columns to extract
            cols = sorted(
                [val for val in header_indices.values() if val != -1]
            )

            # Read required columns of file
            data = np.loadtxt(
                file,
                skiprows=1,
                converters=converters,
                usecols=cols,
                encoding=encoding
            )

            # Add to big lists
            dep_vars += data[:, header_indices['dep_vars']].tolist()
            rates += data[:, header_indices['rate']].tolist()

            # If either header not found, then skip
            if -1 not in [header_indices['upper'], header_indices['lower']]:
                upper += data[:, header_indices['upper']].tolist()
                lower += data[:, header_indices['lower']].tolist()
            else:
                bounds = False

        # Find low to high field order
        order = sorted(range(len(dep_vars)), key=lambda k: dep_vars[k])

        # Calculate lograte_pm as difference in logarithmic domain
        if bounds:
            lower_logdiff = np.log10(rates) - np.log10(lower)
            upper_logdiff = np.log10(upper) - np.log10(rates)
            lograte_pm = np.maximum(lower_logdiff, upper_logdiff)[order]
        else:
            lograte_pm = []

        # Create dataset from all data
        dataset = cls(
            [rates[o] for o in order],
            [dep_vars[o] for o in order],
            lograte_pm
        )

        return dataset

    @staticmethod
    def extract_ac_dc_model(models: list[ac.Model | dc.Model],
                            dep_var_name: str) -> tuple[list[float], list[float], list[float], list[float]]: # noqa
        '''
        Extracts, from AC.Model and DC.Model, the parameters required to
        generate a Dataset

        Parameters
        ----------
        models: list[ac.Model | dc.Model]
            AC or DC models, one per temperature and static field
        dep_var_name: str {'field', 'temperature'}
            independent variable to extract, either field or temperature

        Returns
        -------
        list[float]
            independent Variable Values\n
            either Field (Oe) or Temperature (K)
        list[float]
            ln(tau) values  in units of ln(seconds)
        list[float]
            Standard deviation of ln(tau) in units of ln(seconds)
            These are intrinsic to AC or DC model
        list[float]
            Upper bound of fitted ln(tau) computed using uncertainties from
            fitted parameters
        list[float]
            Lower bound of fitted ln(tau) computed using uncertainties from
            fitted parameters

        Raises
        ------
        ValueError
            If independent variable name is unknown
        '''

        # <ln(tau)>
        lntaus = [
            model.lntau_expect
            for model in models
            if model.fit_status
        ]

        # Standard deviation inherent to model distribution
        # This is sigma of lntau, so MUST be applied to lntau, not tau
        lntau_stdevs = [
            model.lntau_stdev
            for model in models
            if model.fit_status
        ]

        # Upper and lower bounds of ln(tau) from fit uncertainty
        # in fitted parameters
        lntau_fus = [
            model.lntau_fit_ul[0]
            for model in models
            if model.fit_status
        ]

        lntau_fls = [
            model.lntau_fit_ul[1]
            for model in models
            if model.fit_status
        ]

        if dep_var_name == 'field':
            dep_vars = [
                model.dc_field
                for model in models
                if model.fit_status
            ]
        elif dep_var_name == 'temperature':
            dep_vars = [
                model.temperature
                for model in models
                if model.fit_status
            ]
        else:
            raise ValueError('Unknown independent Variable')

        # Sort by independent variable, low to high
        order = sorted(range(len(dep_vars)), key=lambda k: dep_vars[k])
        dep_vars = [dep_vars[it] for it in order]
        lntaus = [lntaus[it] for it in order]
        lntau_stdevs = [lntau_stdevs[it] for it in order]
        lntau_fus = [lntau_fus[it] for it in order]
        lntau_fls = [lntau_fls[it] for it in order]

        return dep_vars, lntaus, lntau_stdevs, lntau_fus, lntau_fls

    @staticmethod
    def lograte_pm_to_pm(rates: ArrayLike,
                         lograte_pm: ArrayLike) -> NDArray:
        '''
        Converts symmetric log10 error of log10rates to asymmetric linear
        errors.

        Parameters
        ----------
        rates: array_like
            Rates in linear space in s^-1
        lograte_pm: array_like
            +-log10(rate), symmetric, same number of elements as rates

        Returns
        -------
        ndarray of floats
            (2, n_rates) list of upper and lower bounds in linear space
        '''

        rate_pm = np.array([
            rates - 10**(np.log10(rates) - lograte_pm),
            10**(np.log10(rates) + lograte_pm) - rates
        ])

        return rate_pm


class HDataset(Dataset):
    '''
    Contains experimental rates, rate bounds (+-) and fields

    Parameters
    ----------
    rates: array_like
        Relaxation rates in seconds^-1
    fields: array_like
        Field Values (Oe)
    lograte_pm: array_like
        Plus-Minus of log10(rates) in logspace, assumed to be symmetric\n
        Not! log(rate_pm)

    Attributes
    ----------
    rates: ndarray of floats
        Relaxation rates in seconds^-1
    dep_vars: ndarray of floats
        Field Values (Oe)
    fields: ndarray of floats
        Field Values (Oe) - linked to dep_vars
    lograte_pm: ndarray of floats
        Plus-minus of log10(rates) in logspace,
        assumed to be symmetric, size is (n_rates,1)\n
        Not! log(rate_pm)
    rate_pm: ndarray of floats
        Plus-minus of rates in linspace,
        will be asymmetric, size is (n_rates,2)\n
        not! 10**(lograte_pm)
    '''
    IDEP_VAR_NAMES = ['Field']
    IDEP_VAR_UNITS = ['Oe']
    IDEP_VAR_LABELS = ['H']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields = self.dep_vars
        return

    @property
    def fields(self):
        return self._fields

    @fields.setter
    def fields(self, value: ArrayLike):
        value = np.asarray(value, dtype=float)
        self._fields = value
        self._dep_vars = value
        return

    @property
    def dep_vars(self):
        return self._dep_vars

    @dep_vars.setter
    def dep_vars(self, value: ArrayLike):
        value = np.asarray(value, dtype=float)
        self._dep_vars = value
        self._fields = value
        return


class TDataset(Dataset):
    '''
    Contains experimental rates, rate bounds (+-) and temperatures

    Parameters
    ----------
    rates: array_like
        Relaxation rates in seconds^-1
    temperatures: array_like
        Temperature Values (K)
    lograte_pm: array_like
        Plus-Minus of log10(rates) in logspace, assumed to be symmetric\n
        Not! log(rate_pm)

    Attributes
    ----------
    rates: ndarray of floats
        Relaxation rates in seconds^-1
    temperatures: ndarray of floats
        Temperature Values (K)
    dep_vars: ndarray of floats
        Temperature Values (K) - linked to dep_vars
    lograte_pm: ndarray of floats
        Plus-minus of log10(rates) in logspace,
        assumed to be symmetric, size is (n_rates,1)\n
        Not! log(rate_pm)
    rate_pm: ndarray of floats
        Plus-minus of rates in linspace,
        will be asymmetric, size is (n_rates,2)\n
        not! 10**(lograte_pm)
    '''
    IDEP_VAR_NAMES = ['Temperature']
    IDEP_VAR_UNITS = ['K']
    IDEP_VAR_LABELS = ['T']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.temperatures = self.dep_vars
        return

    @property
    def temperatures(self):
        return self._temperatures

    @temperatures.setter
    def temperatures(self, value: ArrayLike):
        value = np.asarray(value, dtype=float)
        self._temperatures = value
        self._dep_vars = value
        return

    @property
    def dep_vars(self):
        return self._dep_vars

    @dep_vars.setter
    def dep_vars(self, value: ArrayLike):
        value = np.asarray(value, dtype=float)
        self._dep_vars = value
        self._temperatures = value
        return


class HTDataset(Dataset):
    '''
    Contains experimental rates, rate bounds (+-), fields and temperatures

    Parameters
    ----------
    rates: array_like
        Relaxation rates in seconds^-1
    fields: array_like
        Field Values (Oe)
    temperatures: array_like
        Temperature Values (K)
    lograte_pm: array_like
        Plus-Minus of log10(rates) in logspace, assumed to be symmetric\n
        Not! log(rate_pm)

    Attributes
    ----------
    rates: ndarray of floats
        Relaxation rates in seconds^-1
    fields: array_like
        Field Values (Oe)
    temperatures: array_like
        Temperature Values (K)
    lograte_pm: ndarray of floats
        Plus-minus of log10(rates) in logspace,
        assumed to be symmetric, size is (n_rates,1)\n
        Not! log(rate_pm)
    rate_pm: ndarray of floats
        Plus-minus of rates in linspace,
        will be asymmetric, size is (n_rates,2)\n
        not! 10**(lograte_pm)
    '''
    IDEP_VAR_NAMES = ['Field', 'Temperature']
    IDEP_VAR_UNITS = ['Oe', 'K']
    IDEP_VAR_LABELS = ['H', 'T']

    def __init__(self, rates: ArrayLike, fields: ArrayLike,
                 temperatures: ArrayLike, lograte_pm: ArrayLike = []):

        self.rates = np.asarray(rates, dtype=float)
        self.fields = np.asarray(fields, dtype=float)
        self.temperatures = np.asarray(temperatures, dtype=float)
        self.lograte_pm = np.asarray(lograte_pm, dtype=float)

        return

    @classmethod
    def from_raw(cls, fields: ArrayLike, temperatures: ArrayLike,
                 lntaus: ArrayLike, lntau_stdevs: ArrayLike = [],
                 lntau_fus: ArrayLike = [], lntau_fls: ArrayLike = []
                 ) -> 'HTDataset':
        '''
        Creates dataset from raw values of rates, fields, temperatures,
        ln standard deviation, and upper and lower lntau values

        Parameters
        ----------
        fields: array_like
            Applied Fields (Oe)
        temperatures: array_like
            Temperatures in units of Kelvin
        lntaus: array_like
            ln(tau) values  (ln(seconds))
        lntau_stdev: array_like, default []
            Standard deviation of ln(tau) (ln(seconds)).\n
            These are intrinsic to AC or DC model
        lntau_fus: array_like, default []
            Upper bound of fitted ln(tau) computed using uncertainties from
            fitted parameters
        lntau_fls: array_like, default []
            Lower bound of fitted ln(tau) computed using uncertainties from
            fitted parameters

        Returns
        -------
        HTDataset
           Single Dataset, rate vs H and T
        '''

        lntaus = np.array(lntaus)

        taus = np.array([
            np.exp(lntime)
            for lntime in lntaus
        ])

        rates = [tau**-1 for tau in taus]

        # Upper and lower lntau using standard deviation
        # from distribution
        if len(lntau_stdevs):
            upper_tau = np.exp(lntaus + lntau_stdevs)
            lower_tau = np.exp(lntaus - lntau_stdevs)
            # If upper and lower bounds present, then take element wise
            # maximum of these to find max standard deviation
            # considering both stdev inherent to AC/DC model distribution,
            # and from fitting of AC/DC model parameters
            # or from upper lower bounds
            if len(lntau_fus):
                upper_tau = np.maximum(np.exp(lntau_fus), upper_tau)
            if len(lntau_fls):
                lower_tau = np.maximum(np.exp(lntau_fls), lower_tau)
        else:
            # If just bounds present, then use these
            if len(lntau_fus):
                upper_tau = np.exp(lntau_fus)
            if len(lntau_fls):
                lower_tau = np.exp(lntau_fls)

        if not len(lntau_fls) and not len(lntau_fus) and not len(lntau_stdevs):
            lograte_pm = []
        else:
            # Difference in rates in log space, used as standard deviation in
            # log(tau), required by fitting routine
            # THIS IS NOT!!!! log10(rate_ul_diff)
            # log(sigma(tau)) != sigma(log(tau))
            lograte_ul_diff = [
                np.log10(rates) - np.log10(upper_tau**-1),
                np.log10(lower_tau**-1) - np.log10(rates)
            ]

            # Take maximum of difference in rates in log space
            # If differences arise from model stdev then will be symmetric
            # in log space
            # but if from previous least squares will be asymmetric
            # so take largest and treat as symmetric
            lograte_pm = np.maximum(
                lograte_ul_diff[0],
                lograte_ul_diff[1]
            )

        return cls(rates, fields, temperatures, lograte_pm)

    @classmethod
    def from_ccfit2_csv(cls, file_names: str | list[str]) -> 'HTDataset':
        '''
        Creates Dataset from ccfit2 AC/DC parameter csv file(s)

        Parameters
        ----------
        file_names: str | list[str]
            Filenames of ccfit2 AC/DC parameter file(s)

        Returns
        -------
        HDataset
            Single Dataset, rate vs H and T
        '''

        if isinstance(file_names, str):
            file_names = [file_names]

        name_to_headers = {
            'fields': ['H', 'H (Oe)'],
            'temps': ['T', 'T (K)'],
            'lntaus': ['<ln(tau)>', '<ln(tau)> (ln(s))'],
            'lntau_stdevs': ['sigma_<ln(tau)>', 'sigma_<ln(tau)> (ln(s))', 'sigma_ln(tau)', 'sigma_ln(tau) (ln(s))'], # noqa
            'lntau_fus': ['fit_upper_ln(tau)', 'fit_upper_ln(tau) (ln(s))', 'fit_upper_<ln(tau)>', 'fit_upper_<ln(tau)> (ln(s))'], # noqa
            'lntau_fls': ['fit_lower_ln(tau)', 'fit_lower_ln(tau) (ln(s))', 'fit_lower_<ln(tau)>', 'fit_lower_<ln(tau)> (ln(s))'], # noqa
        }

        header_to_name = {
            val: key
            for key, vals in name_to_headers.items()
            for val in vals
        }

        fields, temps, lntaus, lntau_stdevs, lntau_fls, lntau_fus = [], [], [], [], [], [] # noqa

        both_bounds = True
        std_bound = False
        ul_bound = False

        for file in file_names:

            reader = pd.read_csv(
                file,
                sep=None,
                iterator=True,
                comment='#',
                engine='python',
                skipinitialspace=True
            )
            full_data = pd.concat(reader, ignore_index=True)
            full_data.reset_index(drop=True, inplace=True)

            # Replace headers with names
            full_data = full_data.rename(header_to_name, axis=1)
            # and remove unwanted columns
            full_data = full_data[
                full_data.columns.intersection(name_to_headers.keys())
            ]

            for name in ['fields', 'temps', 'lntaus']:
                if name not in full_data.columns:
                    raise ValueError(f'Cannot find {name} header in {file}')

            optional = ['lntau_stdevs', 'lntau_fus', 'lntau_fls']
            if any(name not in full_data.columns for name in optional):
                both_bounds = False
                if 'lntau_stdevs' in full_data.columns:
                    std_bound = True
                elif all(name not in full_data.columns for name in optional[1:]): # noqa
                    ul_bound = True

            # Add to big lists
            fields += full_data['fields'].to_list()
            temps += full_data['temps'].to_list()
            lntaus += full_data['lntaus'].to_list()

            if both_bounds:
                lntau_stdevs += full_data['lntau_stdevs'].to_list()
                lntau_fls += full_data['lntau_fls'].to_list()
                lntau_fus += full_data['lntau_fus'].to_list()
            elif std_bound:
                lntau_stdevs += full_data['lntau_stdevs'].to_list()
            elif ul_bound:
                lntau_fls += full_data['lntau_fls'].to_list()
                lntau_fus += full_data['lntau_fus'].to_list()

        # Sort all data by field then temperature
        order = sorted(range(len(temps)), key=lambda k: [temps[k], fields[k]])

        if both_bounds:
            # Create dataset from all data and compute bounds
            # from sigma and upper/lower data
            dataset = cls.from_raw(
                [fields[o] for o in order],
                [temps[o] for o in order],
                [lntaus[o] for o in order],
                lntau_stdevs=[lntau_stdevs[o] for o in order],
                lntau_fus=[lntau_fus[o] for o in order],
                lntau_fls=[lntau_fls[o] for o in order]
            )
        elif std_bound:
            # Create dataset from all data with sigma bounds
            dataset = cls.from_raw(
                [fields[o] for o in order],
                [temps[o] for o in order],
                [lntaus[o] for o in order],
                lntau_stdevs=[lntau_stdevs[o] for o in order],
            )
        elif ul_bound:
            # Create dataset from all data with upper and lower bounds
            dataset = cls.from_raw(
                [fields[o] for o in order],
                [temps[o] for o in order],
                lntau_stdevs=[lntaus[o] for o in order],
                lntau_fus=[lntau_fus[o] for o in order],
                lntau_fls=[lntau_fls[o] for o in order]
            )
        else:
            dataset = cls(
                [np.exp(-lntaus[o]) for o in order],
                [fields[o] for o in order],
                [temps[o] for o in order]
            )

        return dataset

    @classmethod
    def from_rate_files(cls, file_names: str | list[str]) -> 'HTDataset':
        '''
        Creates Dataset from file(s) containing the headers\n
        H, T, rate, <upper>, <lower>\n
        The last two are optional

        Parameters
        ----------
        file_names: str | list[str]
            Filenames of files to read

        Returns
        -------
        TDataset
            Single Dataset, rate vs H and T
        '''

        if isinstance(file_names, str):
            file_names = [file_names]

        # Find encoding of input files
        encodings = [
            ut.detect_encoding(file)
            for file in file_names
        ]

        headers = {
            'fields': ['H'],
            'temps': ['T'],
            'rate': ['rate'],
            'upper': ['upper'],
            'lower': ['lower']
        }

        fields, temps, rates, upper, lower = [], [], [], [], []

        indices = []

        bounds = True

        for file, encoding in zip(file_names, encodings):

            # Get file headers
            header_indices, _ = ut.parse_headers(
                file, 0, headers, delim=None
            )

            indices.append(header_indices)

            if header_indices['fields'] == -1:
                raise ValueError(f'Cannot find fields in {file}')
            if header_indices['temps'] == -1:
                raise ValueError(f'Cannot find temperatures in {file}')
            elif header_indices['rate'] == -1:
                raise ValueError(f'Cannot find rates in {file}')

            # Columns to extract from file
            cols = [header_indices[he] for he in headers.keys()]

            converters = {
                it: lambda s: (float(s.strip() or np.nan)) for it in cols
            }

            # Read required columns of file
            data = np.loadtxt(
                file,
                skiprows=1,
                converters=converters,
                usecols=cols,
                encoding=encoding
            )

            # Add to big lists
            fields += data[:, 0].tolist()
            rates += data[:, 1].tolist()

            # If either header not found, then skip
            if -1 not in [header_indices['upper'], header_indices['lower']]:
                upper += data[:, 2].tolist()
                lower += data[:, 3].tolist()
            else:
                bounds = False

        # Sort by field (large loop) and temperature (small loop)
        order = sorted(range(len(temps)), key=lambda k: [temps[k], fields[k]])

        # Calculate lograte_pm as difference in logarithmic domain
        if bounds:
            lower_logdiff = np.log10(rates) - np.log10(lower)
            upper_logdiff = np.log10(upper) - np.log10(rates)
            lograte_pm = np.maximum(lower_logdiff, upper_logdiff)[order]
        else:
            lograte_pm = []

        # Create dataset from all data
        dataset = cls(rates[order], fields[order], temps[order], lograte_pm)

        return dataset

    @staticmethod
    def extract_ac_dc_model(models: list[ac.Model | dc.Model]) -> tuple[list[float], list[float], list[float], list[float], list[float]]: # noqa
        '''
        Extracts, from AC.Model and DC.Model, the parameters required to
        generate a HTDataset

        Parameters
        ----------
        models: list[ac.Model | dc.Model]
            AC or DC models, one per temperature and static field

        Returns
        -------
        list[float]
            Applied Field values in units of Oersted
        list[float]
            Temperatures in units of Kelvin
        list[float]
            ln(tau) values  in units of ln(seconds)
        list[float]
            Standard deviation of ln(tau) in units of ln(seconds)
            These are intrinsic to AC or DC model
        list[float]
            Upper bound of fitted ln(tau) computed using uncertainties from
            fitted parameters
        list[float]
            Lower bound of fitted ln(tau) computed using uncertainties from
            fitted parameters
        '''

        # <ln(tau)>
        lntaus = [
            model.lntau_expect
            for model in models
            if model.fit_status
        ]

        # Standard deviation inherent to model distribution
        # This is sigma of lntau, so MUST be applied to lntau, not tau
        lntau_stdevs = [
            model.lntau_stdev
            for model in models
            if model.fit_status
        ]

        # Upper and lower bounds of ln(tau) from fit uncertainty
        # in fitted parameters
        lntau_fus = [
            model.lntau_fit_ul[0]
            for model in models
            if model.fit_status
        ]

        lntau_fls = [
            model.lntau_fit_ul[1]
            for model in models
            if model.fit_status
        ]

        fields = [
            model.dc_field
            for model in models
            if model.fit_status
        ]

        temperatures = [
            model.temperature
            for model in models
            if model.fit_status
        ]

        # Sort by field and then temperature, low to high
        order = sorted(
            range(len(temperatures)),
            key=lambda k: [temperatures[k], fields[k]]
        )

        fields = [fields[o] for o in order]
        temperatures = [temperatures[o] for o in order]
        lntaus = [lntaus[o] for o in order]
        lntau_stdevs = [lntau_stdevs[o] for o in order]
        lntau_fus = [lntau_fus[o] for o in order]
        lntau_fls = [lntau_fls[o] for o in order]

        return fields, temperatures, lntaus, lntau_stdevs, lntau_fus, lntau_fls


class LogTauModel(ABC):
    '''
    Abstract class on which all phenomenological models of \n
    magnetic relaxation Log10(rate) are based

    Parameters
    ----------
    fit_vars: dict[str, float]
        Parameter to fit in model function\n
        Keys are fit/fix parameter names (see class.PARNAMES)\n
        Values are either float (actual value) or the string 'guess'\n
    fix_vars: dict[str, float]
        Parameter which remain fixed in model function\n
        Keys are fit/fix parameter names (see class.PARNAMES)\n
        Values are either float (actual value) or the string 'guess'\n
    '''

    @property
    @abstractmethod
    def NAME() -> str:
        'string name of model'
        raise NotImplementedError

    @property
    @abstractmethod
    def LNAME() -> str:
        'string name of model with Log() around it, e.g. Log(Orbach)'
        raise NotImplementedError

    @property
    @abstractmethod
    def IDEP_VAR_NAMES() -> list[str]:
        'str names of independent variables with which rate varies e.g. Field'
        raise NotImplementedError

    @property
    @abstractmethod
    def IDEP_VAR_LABELS() -> list[str]:
        'str label of independent variables with which rate varies e.g. H'
        raise NotImplementedError

    @property
    @abstractmethod
    def IDEP_VAR_UNITS() -> list[str]:
        'str units of independent variables with which rate varies e.g. Oe'
        raise NotImplementedError

    @property
    @abstractmethod
    def PARNAMES() -> list[str]:
        'string names of parameters which can be fitted or fixed'
        raise NotImplementedError

    @property
    @abstractmethod
    def VARNAMES_MM() -> dict[str, str]:
        '''
        Mathmode (i.e. $$, latex ) versions of PARNAMES\n
        Keys are strings from PARNAMES plus any other variables which
        might be needed\n
        Values are mathmode strings
        '''
        raise NotImplementedError

    @property
    @abstractmethod
    def VARNAMES_HTML() -> dict[str, str]:
        '''
        HTML versions of PARNAMES\n
        Keys are strings from PARNAMES plus any other variables which
        might be needed\n
        Values are mathmode strings
        '''
        raise NotImplementedError

    @property
    @abstractmethod
    def UNITS() -> dict[str, str]:
        '''
        string names of units of PARNAMES\n
        Keys are strings from PARNAMES plus any other variables which
        might be needed\n
        Values are unit name strings
        '''
        raise NotImplementedError

    @property
    @abstractmethod
    def UNITS_MM() -> dict[str, str]:
        '''
        Mathmode (i.e. $$, latex ) versions of UNITS\n
        Keys are strings from PARNAMES plus any other variables which
        might be needed\n
        Values are unit name strings
        '''
        raise NotImplementedError

    @property
    @abstractmethod
    def UNITS_HTML() -> dict[str, str]:
        '''
        HTML versions of UNITS\n
        Keys are strings from PARNAMES plus any other variables which
        might be needed\n
        Values are unit name strings
        '''
        raise NotImplementedError

    @property
    @abstractmethod
    def BOUNDS() -> dict[str, list[float, float]]:
        '''
        Bounds for each parameter of model\n
        Keys: parameter name\n
        Values: [upper, lower]\n
        used by scipy least_squares
        '''
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def model(parameters: dict[str, float],
              dep_vars: ArrayLike) -> NDArray:
        '''
        Evaluates model function of log(relaxation rate)
        using provided parameter and field values.

        Parameters
        ----------
        parameters: dict[str, float],
            Parameters to use in model function
        dep_vars: array_like
            inDependent variable values at which model function is evaluated

        Returns
        -------
        ndarray of floats
            log10(Relaxation rate) as a function of field

        '''
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def set_initial_vals(parameters: dict[str, str | float]) -> dict[str, float]: # noqa
        '''
        Sets guess values for parameters if requested by user

        Parameters
        ----------
        param_dict: dict[str, str | float]
            Either fit_vars or fix_vars
            Keys are fit/fix parameter names (see class.PARNAMES)
            values are either float (actual value) or the string 'guess'\n

        Returns
        -------
        dict[str, float]
            Keys are fit/fix parameter names (see class.PARNAMES)\n
            Values are float (actual value) which are initial values of
            parameter
        '''
        raise NotImplementedError

    def __init__(self, fit_vars: dict[str, float | str],
                 fix_vars: dict[str, float | str]):
        '''
        Set default values for mandatory attributes
        '''

        # Replace any 'guess' strings with proper guesses
        self.fit_vars = self.set_initial_vals(fit_vars)
        self.fix_vars = self.set_initial_vals(fix_vars)

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
        # fitted and fixed
        self._final_var_values = {
            var: None
            for var in self.PARNAMES
        }

        # Fit status and temperature
        self._fit_status = False

        # Fit standard deviation
        self._fit_stdev = {
            var: None
            for var in self.fit_vars.keys()
        }

        return

    @property
    def fit_status(self) -> bool:
        'True if fit successful, else False'
        return self._fit_status

    @fit_status.setter
    def fit_status(self, value: bool):
        if isinstance(value, bool):
            self._fit_status = value
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
        Variables of model which will are fixed.\n
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

    @classmethod
    def residuals(cls, params: dict[str, float], dep_vars: ArrayLike,
                  true_lograte: ArrayLike) -> NDArray:
        '''
        Calculates difference between measured log10(relaxation rate) and trial
        from model

        Parameters
        ----------
        params: array_like
            model parameter values
        dep_vars: array_like
            inDependent variable values at which model function is evaluated
        true_lograte: array_like
            true (experimental) values of log10(relaxation rate)

        Returns
        -------
        ndarray of floats
            Residuals
        '''

        # Calculate model log10(relaxation rate) using parameters
        trial_lograte = cls.model(params, dep_vars)

        residuals = trial_lograte - true_lograte

        return residuals

    @classmethod
    def residual_from_float_list(cls, new_vals: ArrayLike,
                                 fit_vars: dict[str, float],
                                 fix_vars: dict[str, float],
                                 dep_vars: ArrayLike,
                                 lograte: ArrayLike,
                                 sigma: ArrayLike = []) -> NDArray:
        '''
        Wrapper for `residuals` method, takes new values from scipy
        least_squares which provides list[float], to construct new
        fit_vars dict, then runs `residuals` method.

        Parameters
        ----------
        new_vals: array_like
            This iteration's fit parameter values provided by least_squares
            this has the same order at fit_vars.keys
        fit_vars: dict[str, float]
            Parameter to fit in model function\n
            keys are PARNAMES, values are initial guesses
        fix_vars: dict[str, float]
            Parameter which remain fixed in model function\n
            keys are PARNAMES, values are float values
        dep_vars: array_like
            inDependent variable values at which model function is evaluated
        lograte: array_like
            True (experimental) values of log10(relaxation rate)
        sigma: array_like
            Standard deviation of tau in logspace

        Returns
        -------
        ndarray of floats
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

        residuals = cls.residuals(all_vars, dep_vars, lograte)

        if len(sigma):
            residuals /= sigma

        return residuals

    @ut.strip_guess
    def fit_to(self, dataset: Dataset, verbose: bool = True) -> None:
        '''
        Fits model to Dataset

        Parameters
        ----------
        dataset: HDataset
            Dataset to which a model of rate vs independent variable will\n
            be fitted
        verbose: bool, default True
            If True, prints information to terminal

        Returns
        -------
        None

        Raises
        ------
        ValueError
            If Temperature dependent model provided when field data is to be\n
            fitted, and vice-versa
        '''

        if isinstance(dataset, HDataset) and isinstance(self.__class__, LogTauTModel): # noqa
            raise ValueError('Cannot fit T model to H Dataset')
        elif isinstance(dataset, TDataset) and isinstance(self.__class__, LogTauHModel): # noqa
            raise ValueError('Cannot fit H model to T Dataset')

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
                dataset.dep_vars,
                np.log10(dataset.rates),
                dataset.lograte_pm
            ],
            x0=guess,
            bounds=bounds
        )

        if curr_fit.status == 0:
            if verbose:
                ut.cprint(
                    '\n Fit failed - Too many iterations', 'black_yellowbg'
                )

            self.final_var_values = {
                name: value
                for name, value in zip(self.fit_vars, curr_fit.x)
            }
            self.fit_stdev = {
                label: np.nan
                for label in self.fit_vars.keys()
            }
            self.fit_status = False
        else:
            stdev, no_stdev = stats.svd_stdev(curr_fit)

            # Standard deviation error on the parameters
            self.fit_stdev = {
                label: val
                for label, val in zip(self.fit_vars.keys(), stdev)
            }

            self.fit_status = True

            # Report singular values=0 of Jacobian
            # and indicate that std_dev cannot be calculated
            for par, si in zip(self.fit_vars.keys(), no_stdev):
                if verbose and not si:
                    ut.cprint(
                        f'Warning: Jacobian is degenerate for {par}, standard deviation cannot be found, and is set to zero\n', # noqa
                        'black_yellowbg'
                    )

            # Set fitted values
            self.final_var_values = {
                name: value
                for name, value in zip(self.fit_vars.keys(), curr_fit.x)
            }
            # and fixed values
            for key, val in self.fix_vars.items():
                self.final_var_values[key] = val

        return


class LogTauHModel(LogTauModel):
    '''
    Abstract class on which all phenomenological models of \n
    field-dependent magnetic relaxation Log10(rate) are based

    Parameters
    ----------
    fit_vars: dict[str, float]
        Parameter to fit in model function\n
        Keys are fit/fix parameter names (see class.PARNAMES)\n
        Values are either float (actual value) or the string 'guess'\n
    fix_vars: dict[str, float]
        Parameter which remain fixed in model function\n
        Keys are fit/fix parameter names (see class.PARNAMES)\n
        Values are either float (actual value) or the string 'guess'\n

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
    fit_status: bool
        True if fit successful, else false
    '''
    IDEP_VAR_NAMES = ['Field']
    IDEP_VAR_UNITS = ['Oe']
    IDEP_VAR_LABELS = ['H']


class LogTauTModel(LogTauModel):
    '''
    Abstract class on which all phenomenological models of \n
    temperature-dependent magnetic relaxation Log10(rate) are based

    Parameters
    ----------
    fit_vars: dict[str, float]
        Parameter to fit in model function\n
        Keys are fit/fix parameter names (see class.PARNAMES)\n
        Values are either float (actual value) or the string 'guess'\n
        If 'guess' then a parameter value is guessed
    fix_vars: dict[str, float]
        Parameter which remain fixed in model function\n
        Keys are fit/fix parameter names (see class.PARNAMES)\n
        Values are either float (actual value) or the string 'guess'\n
        If 'guess' then a parameter value is guessed

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
    fit_status: bool
        True if fit successful, else false
    '''
    IDEP_VAR_NAMES = ['Temperature']
    IDEP_VAR_UNITS = ['K']
    IDEP_VAR_LABELS = ['T']


class LogTauHTModel(LogTauModel):
    '''
    Abstract class on which all phenomenological models of field- and \n
    temperature-dependent magnetic relaxation Log10(rate) are based

    Parameters
    ----------
    fit_vars: dict[str, float]
        Parameter to fit in model function\n
        Keys are fit/fix parameter names (see class.PARNAMES)\n
        Values are either float (actual value) or the string 'guess'\n
    fix_vars: dict[str, float]
        Parameter which remain fixed in model function\n
        Keys are fit/fix parameter names (see class.PARNAMES)\n
        Values are either float (actual value) or the string 'guess'\n

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
    fit_status: bool
        True if fit successful, else false
    '''

    IDEP_VAR_NAMES = ['Field', 'Temperature']
    IDEP_VAR_UNITS = ['Oe', 'K']
    IDEP_VAR_LABELS = ['H', 'T']

    @staticmethod
    @abstractmethod
    def model(parameters: dict[str, float], fields: ArrayLike,
              temperatures: ArrayLike) -> NDArray:
        '''
        Evaluates model function of log(relaxation rate)
        using provided parameter and field values.

        Parameters
        ----------
        parameters: dict[str, float],
            Parameters to use in model function
        fields: array_like
            DC field values (Oe) at which model function is evaluated
        temperatures
            Temperature values (K) at which model function is evaluated

        Returns
        -------
        ndarray of floats
            log10(Relaxation rate) as a function of field

        '''
        raise NotImplementedError

    @classmethod
    def residuals(cls, params: dict[str, float], fields: ArrayLike,
                  temperatures: ArrayLike,
                  true_lograte: ArrayLike) -> NDArray:
        '''
        Calculates difference between measured log10(relaxation rate) and trial
        from model

        Parameters
        ----------
        params: array_like
            model parameter values
        fields: array_like
            Fields (Oe) at which model function is evaluated
        temperatures: array_like
            Temperatures (K) at which model function is evaluated
        true_lograte: array_like
            true (experimental) values of log10(relaxation rate)

        Returns
        -------
        ndarray of floats
            Residuals
        '''

        # Calculate model log10(relaxation rate) using parameters
        trial_lograte = cls.model(params, fields, temperatures)

        residuals = trial_lograte - true_lograte

        return residuals

    @ut.strip_guess
    def fit_to(self, dataset: HTDataset, verbose: bool = True) -> None:
        '''
        Fits model to Dataset

        Parameters
        ----------
        dataset: HTDataset
            Dataset to which a model of rate vs field and temperature will be
            fit
        verbose: bool, default True
            If True, prints information to terminal

        Returns
        -------
        None
        '''

        if not isinstance(dataset, HTDataset): # noqa
            raise ValueError('Must use HTDataset with HT Models')

        # Get starting guesses
        guess = [val for val in self.fit_vars.values()]

        # Get bounds for variables to be fitted
        bounds = np.array([
            self.BOUNDS[name]
            for name in self.fit_vars.keys()
        ]).T

        dep_vars = [
            dataset.fields,
            dataset.temperatures
        ]

        curr_fit = least_squares(
            self.residual_from_float_list,
            args=[
                self.fit_vars,
                self.fix_vars,
                dep_vars,
                np.log10(dataset.rates),
                dataset.lograte_pm
            ],
            x0=guess,
            bounds=bounds
        )

        if curr_fit.status == 0:
            if verbose:
                ut.cprint(
                    '\n Fit failed - Too many iterations', 'black_yellowbg'
                )

            self.final_var_values = {
                name: value
                for name, value in zip(self.fit_vars, curr_fit.x)
            }
            self.fit_stdev = {
                label: np.nan
                for label in self.fit_vars.keys()
            }
            self.fit_status = False
        else:
            stdev, no_stdev = stats.svd_stdev(curr_fit)

            # Standard deviation error on the parameters
            self.fit_stdev = {
                label: val
                for label, val in zip(self.fit_vars.keys(), stdev)
            }

            self.fit_status = True

            # Report singular values=0 of Jacobian
            # and indicate that std_dev cannot be calculated
            for par, si in zip(self.fit_vars.keys(), no_stdev):
                if verbose and not si:
                    ut.cprint(
                        f'Warning: Jacobian is degenerate for {par}, standard deviation cannot be found, and is set to zero\n', # noqa
                        'black_yellowbg'
                    )

            # Set fitted values
            self.final_var_values = {
                name: value
                for name, value in zip(self.fit_vars.keys(), curr_fit.x)
            }
            # and fixed values
            for key, val in self.fix_vars.items():
                self.final_var_values[key] = val

        return


class MultiLogTauModel(ABC):
    '''
    Takes multiple LogTauModel objects and combines into a single object.\n
    Individual models can be accessed through the logmodels attribute.

    Parameters
    ----------
    fit_vars: list[dict[str, float | str]]
        List of fit dicts, with keys as PARNAMES of each LogTauHModel
        and values as either the string 'guess' or a float value
    fix_vars: list[dict[str, float | str]]
        List of fix dicts, with keys as PARNAMES of each LogTauHModel
        and values as either the string 'guess' or a float value
    logmodels: list[LogTauHModel]
        List of uninstantiated LogTauHModel objects

    Attributes
    ----------
    logmodels: list[LogTauTModel]
        List of instantiated LogTauTModel objects
    '''

    @property
    @abstractmethod
    def IDEP_VAR_NAMES() -> list[str]:
        'string name of independent variable with which rate varies e.g. Field'
        raise NotImplementedError

    @property
    @abstractmethod
    def IDEP_VAR_LABELS() -> list[str]:
        'string label of independent variables with which rate varies e.g. H'
        raise NotImplementedError

    @property
    @abstractmethod
    def IDEP_VAR_UNITS() -> list[str]:
        'string unit of independent variable with which rate varies e.g. Oe'
        raise NotImplementedError

    def __init__(self, logmodels: list[LogTauModel],
                 fit_vars: list[dict[str, float | str]],
                 fix_vars: list[dict[str, float | str]]) -> None:

        # Instantiate each logmodel and create list of instantiated logmodels
        self.logmodels = self.process_fitfix(fit_vars, fix_vars, logmodels)
        self._fit_status = False
        self._NAME = self.gen_name()

        return

    @property
    def NAME(self) -> str:
        '''
        Names of each LogTauModel in self.logmodels concatenated with +\n
        between models
        '''
        return self._NAME

    @NAME.setter
    def NAME(self, value) -> str:
        self._NAME = value
        return

    def gen_name(self):
        '''
        Generates concatenated names from self.logmodels, with + between\n
        model names
        '''
        name = [logmodel.NAME for logmodel in self.logmodels]
        name = ''.join(['{}+'.format(n) for n in name])[:-1]
        return name

    @property
    def fit_status(self) -> bool:
        'True if fit successful, else False'
        return self._fit_status

    @fit_status.setter
    def fit_status(self, value: bool):
        if isinstance(value, bool):
            self._fit_status = value
        else:
            raise TypeError
        return

    @staticmethod
    def process_fitfix(fit_vars: list[dict[str, float | str]],
                       fix_vars: list[dict[str, float | str]],
                       logmodels: list[LogTauHModel]) -> list[LogTauHModel]:
        '''
        Associates fit and fix dicts with a list of logmodels by instantiating
        each logmodel with the specified parameters

        Parameters
        ----------

        fit_vars: list[dict[str, float | str]]
            List of fit dicts, with keys as PARNAMES of each LogTauHModel
            and values as either the string 'guess' or a float value
        fix_vars: list[dict[str, float | str]]
            List of fix dicts, with keys as PARNAMES of each LogTauHModel
            and values as either the string 'guess' or a float value
        logmodels: list[LogTauHModel]
            List of uninstantiated LogTauHModel objects

        Returns
        -------
        list[LogTauHModel]
            Instantiated LogTauHModels with fit and fix dicts applied
        '''

        marked = [False] * len(fit_vars)

        instantiated_models = []

        for logmodel in logmodels:
            for it, (fitvar_set, fix_var_set) in enumerate(zip(fit_vars, fix_vars)): # noqa
                if marked[it]:
                    continue
                elif all([k in logmodel.PARNAMES for k in fitvar_set.keys()]): # noqa
                    if all([k in logmodel.PARNAMES for k in fix_var_set.keys()]) or not len(fix_var_set): # noqa
                        instantiated_models.append(
                            logmodel(fitvar_set, fix_var_set)
                        )
                        marked[it] = True

        if not len(instantiated_models):
            raise ValueError('No models could be instantiated!')

        return instantiated_models

    @classmethod
    def residual_from_float_list(cls, new_vals: ArrayLike,
                                 logmodels: list[LogTauHModel],
                                 dep_vars: ArrayLike,
                                 lograte: ArrayLike,
                                 sigma: ArrayLike = []) -> NDArray:
        '''
        Wrapper for `residuals` method, takes new values from fitting routine\n
        which provides list[float], to construct new fit_vars dict, then\n
        runs `residuals` method.

        Parameters
        ----------
        new_vals: array_like
            This iteration's fit parameter values provided by least_squares\n
            this has the same order as fit_vars.keys
        logmodels: list[LogTauHModel]
            Models to use
        dep_vars: array_like
            inDependent variable values at which model function is evaluated
        lograte: array_like
            True (experimental) values of log10(relaxation rate)
        sigma: array_like
            Standard deviation of tau in logspace

        Returns
        -------
        ndarray of floats
            Residuals
        '''

        # Swap fit values for new values from fit routine
        new_fit_vars = []

        it = 0
        for logmodel in logmodels:
            new_dict = {}
            for name in logmodel.fit_vars.keys():
                new_dict[name] = new_vals[it]
                it += 1
            new_fit_vars.append(new_dict)

        residuals = cls.residuals(
            logmodels, new_fit_vars, dep_vars, lograte
        )

        if len(sigma):
            residuals /= sigma

        return residuals

    @staticmethod
    def residuals(logmodels: list[LogTauHModel],
                  new_fit_vars: list[dict[str, float]],
                  dep_vars: ArrayLike,
                  true_lograte: ArrayLike) -> NDArray:
        '''
        Calculates difference between experimental log10(tau^-1)\n
        and log10(tau^-1) obtained from the sum of the provided logmodels\n
        using the provided fit variable values at provided fields

        Parameters
        ----------
        logmodels: list[LogTauHModel]
            LogTauHModels which will be evaluated
        new_fit_vars: list[dict[str, float]]
            fit dicts for each LogTauHModel, must have same order as logmodel\n
            if no vars to fit for that model, then empty dict is given
        dep_vars: array_like
            inDependent variable values at which model function is evaluated
        true_lograte: array_like
            Experimental Log10(rate)s

        Returns
        -------
        ndarray of floats
            Log10(rate)_trial - Log10(rate)_exp for each temperature
        '''

        # Calculate model log10(relaxation rate) using parameters
        # as sum of contributions from each process
        trial_lograte = np.zeros(len(dep_vars))

        for logmodel, fit_vars in zip(logmodels, new_fit_vars):
            all_vars = {**logmodel.fix_vars, **fit_vars}
            trial_lograte += 10**logmodel.model(all_vars, dep_vars)

        # sum in linear space, then take log
        trial_lograte = np.log10(trial_lograte)

        residuals = trial_lograte - true_lograte

        return residuals

    @ut.strip_guess
    def fit_to(self, dataset: HDataset | TDataset,
               verbose: bool = True) -> None:
        '''
        Fits model to Dataset

        Parameters
        ----------
        dataset: HDataset | TDataset
            Dataset to which a model of rate vs independent variable
            will be fitted
        verbose: bool, default True
            If True, prints information to terminal

        Returns
        -------
        None

        Raises
        ------
        ValueError
            If Temperature dependent model provided when field data is to be\n
            fitted, and vice-versa
        '''

        if isinstance(dataset, HDataset) and isinstance(self.__class__, MultiLogTauTModel): # noqa
            raise ValueError('Cannot fit T model to H Dataset')
        elif isinstance(dataset, TDataset) and isinstance(self.__class__, MultiLogTauHModel): # noqa
            raise ValueError('Cannot fit H model to T Dataset')

        # Initial guess is a list of fitvars values
        guess = [
            value for logmodel in self.logmodels
            for value in logmodel.fit_vars.values()
        ]

        bounds = np.array([
            logmodel.BOUNDS[name] for logmodel in self.logmodels
            for name in logmodel.fit_vars.keys()
        ]).T

        curr_fit = least_squares(
            self.residual_from_float_list,
            args=[
                self.logmodels,
                dataset.dep_vars,
                np.log10(dataset.rates),
                dataset.lograte_pm
            ],
            x0=guess,
            bounds=bounds,
            jac='3-point'
        )

        self.final_var_values = {}
        self.fit_stdev = {}

        if curr_fit.status == 0:
            if verbose:
                ut.cprint(
                    '\n Fit failed - Too many iterations',
                    'black_yellowbg'
                )

            n_fitted_pars = np.sum(
                [len(logmodel.fit_vars.keys()) for logmodel in self.logmodels]
            )

            stdev = [np.nan] * n_fitted_pars
            self.fit_status = False
        else:

            stdev, no_stdev = stats.svd_stdev(curr_fit)

            self.fit_status = True

        # Add parameters, status and stdev to each LogTauTModel
        # and to this object
        it = 0
        for logmodel in self.logmodels:

            # Name of fitted variables in this logmodel
            fit_var_names = logmodel.fit_vars.keys()
            # Number of parameters for this logmodel
            n_pars = len(fit_var_names)

            # Set each standard deviation
            _stdev = stdev[it: it + n_pars]
            logmodel.fit_stdev = {
                label: val
                for label, val in zip(
                    fit_var_names, _stdev
                )
            }
            for label, val in zip(fit_var_names, _stdev):
                self.fit_stdev[label] = val

            # Report singular values=0 of Jacobian
            # and indicate that std_dev cannot be calculated
            sings = no_stdev[it: it + n_pars]
            for par, si in zip(fit_var_names, sings):
                if verbose and not si:
                    ut.cprint(
                        f'Warning: Jacobian is degenerate for {par}, standard deviation cannot be found, and is set to zero\n', # noqa
                        'black_yellowbg'
                    )

            # Set final fitted values
            _vals = curr_fit.x[it: it + n_pars]
            logmodel.final_var_values = {
                name: value
                for name, value in zip(fit_var_names, _vals)
            }
            # and fixed values
            for name, value in logmodel.fix_vars.items():
                logmodel.final_var_values[name] = value
                self.final_var_values[name] = value

            for name, value in zip(fit_var_names, _vals):
                self.final_var_values[name] = value

            it += n_pars

        return


class MultiLogTauHModel(MultiLogTauModel):
    '''
    Takes multiple LogTauHModel objects and combines into a single object.\n
    Individual models can be accessed through the logmodels attribute.

    Parameters
    ----------
    logmodels: list[LogTauHModel]
        List of uninstantiated LogTauHModel objects
    fit_vars: list[dict[str, float | str]]
        List of fit dicts, with keys as PARNAMES of each LogTauHModel
        and values as either the string 'guess' or a float value
    fix_vars: list[dict[str, float | str]]
        List of fix dicts, with keys as PARNAMES of each LogTauHModel
        and values as either the string 'guess' or a float value

    Attributes
    ----------
    logmodels: list[LogTauTModel]
        List of instantiated LogTauTModel objects
    fit_status: bool
        True if fit successful, else false
    NAME: str
        Names of each LogTauHTModel concatenated
    '''
    IDEP_VAR_NAMES = ['Field']
    IDEP_VAR_UNITS = ['Oe']
    IDEP_VAR_LABELS = ['H']

    def __init__(self, logmodels: list[LogTauModel],
                 fit_vars: list[dict[str, float | str]],
                 fix_vars: list[dict[str, float | str]]) -> None:

        # Check for incorrect models
        for logmodel in logmodels:
            if not issubclass(logmodel, LogTauHModel):
                raise TypeError(
                    'Non-LogTauHModel passed to MultiLogTauHModel'
                )

        # and call parent
        super().__init__(
            logmodels=logmodels,
            fit_vars=fit_vars,
            fix_vars=fix_vars
        )


class MultiLogTauTModel(MultiLogTauModel):
    '''
    Takes multiple LogTauTModel objects and combines into a single object.\n
    Individual models can be accessed through the logmodels attribute.

    Parameters
    ----------
    logmodels: list[LogTauTModel]
        List of uninstantiated LogTauTModel objects
    fit_vars: list[dict[str, float | str]]
        List of fit dicts, with keys as PARNAMES of each LogTauTModel
        and values as either the string 'guess' or a float value
    fix_vars: list[dict[str, float | str]]
        List of fix dicts, with keys as PARNAMES of each LogTauTModel
        and values as either the string 'guess' or a float value

    Attributes
    ----------
    logmodels: list[LogTauTModel]
        List of instantiated LogTauTModel objects
    fit_status: bool
        True if fit successful, else false
    NAME: str
        Names of each LogTauTModel concatenated
    '''
    IDEP_VAR_NAMES = ['Temperature']
    IDEP_VAR_UNITS = ['K']
    IDEP_VAR_LABELS = ['T']

    def __init__(self, logmodels: list[LogTauModel],
                 fit_vars: list[dict[str, float | str]],
                 fix_vars: list[dict[str, float | str]]) -> None:

        # Check for incorrect models
        for logmodel in logmodels:
            if not issubclass(logmodel, LogTauTModel):
                print(isinstance(logmodel, LogTauTModel))
                raise TypeError(
                    'Non-LogTauTModel passed to MultiLogTauTModel'
                )

        # and call parent
        super().__init__(
            logmodels=logmodels,
            fit_vars=fit_vars,
            fix_vars=fix_vars
        )


class MultiLogTauHTModel(MultiLogTauModel):
    '''
    Takes multiple LogTauHTModel objects and combines into a single object.\n
    Individual models can be accessed through the logmodels attribute.

    Parameters
    ----------
    logmodels: list[LogTauHTModel]
        List of uninstantiated LogTauHTModel objects
    fit_vars: list[dict[str, float | str]]
        List of fit dicts, with keys as PARNAMES of each LogTauHTModel
        and values as either the string 'guess' or a float value
    fix_vars: list[dict[str, float | str]]
        List of fix dicts, with keys as PARNAMES of each LogTauHTModel
        and values as either the string 'guess' or a float value

    Attributes
    ----------
    logmodels: list[LogTauTModel]
        List of instantiated LogTauTModel objects
    fit_status: bool
        True if fit successful, else false
    NAME: str
        Names of each LogTauHTModel concatenated
    '''
    IDEP_VAR_NAMES = ['Field', 'Temperature']
    IDEP_VAR_UNITS = ['Oe', 'K']
    IDEP_VAR_LABELS = ['H', 'T']

    def __init__(self, logmodels: list[LogTauModel],
                 fit_vars: list[dict[str, float | str]],
                 fix_vars: list[dict[str, float | str]]) -> None:

        # Check for incorrect models
        for logmodel in logmodels:
            if not issubclass(logmodel, LogTauHTModel):
                raise TypeError(
                    'Non-LogTauHTModel passed to MultiLogTauHTModel'
                )

        # and call parent
        super().__init__(
            logmodels=logmodels,
            fit_vars=fit_vars,
            fix_vars=fix_vars
        )

    @staticmethod
    def residuals(logmodels: list[LogTauHTModel],
                  new_fit_vars: list[dict[str, float]],
                  dep_vars,
                  true_lograte: ArrayLike) -> NDArray:
        '''
        Calculates difference between experimental log10(tau^-1)\n
        and log10(tau^-1) obtained from the sum of the provided logmodels\n
        using the provided fit variable values at provided fields

        Parameters
        ----------
        logmodels: list[LogTauHTModel]
            LogTauHTModels which will be evaluated
        new_fit_vars: list[dict[str, float]]
            fit dicts for each LogTauHTModel, must have same order as\n
            logmodel if no vars to fit for that model,\n
            then empty dict is given
        dep_vars: array_like
            inDependent variable values at which model function is evaluated\n
            Shape must be [2, n_rates], where first row contains field values\n
            and second contains temperatures
        true_lograte: array_like
            Experimental Log10(rate)s

        Returns
        -------
        ndarray of floats
            Log10(rate)_trial - Log10(rate)_exp for each temperature
        '''

        # Calculate model log10(relaxation rate) using parameters
        # as sum of contributions from each process
        trial_lograte = np.zeros(len(dep_vars[0]))

        for logmodel, fit_vars in zip(logmodels, new_fit_vars):
            all_vars = {**logmodel.fix_vars, **fit_vars}
            trial_lograte += 10**logmodel.model(all_vars, *dep_vars)

        # sum in linear space, then take log
        trial_lograte = np.log10(trial_lograte)

        residuals = trial_lograte - true_lograte

        return residuals

    @ut.strip_guess
    def fit_to(self, dataset: HTDataset, verbose: bool = True) -> None:
        '''
        Fits model to Dataset

        Parameters
        ----------
        dataset: HTDataset
            Dataset to which a model of rate vs field and temperature will be
            fit
        verbose: bool, default True
            If True, prints information to terminal

        Returns
        -------
        None
        '''

        # Initial guess is a list of fitvars values
        guess = [
            value for logmodel in self.logmodels
            for value in logmodel.fit_vars.values()
        ]

        bounds = np.array([
            logmodel.BOUNDS[name] for logmodel in self.logmodels
            for name in logmodel.fit_vars.keys()
        ]).T

        dep_vars = [
            dataset.fields,
            dataset.temperatures
        ]

        curr_fit = least_squares(
            self.residual_from_float_list,
            args=[
                self.logmodels,
                dep_vars,
                np.log10(dataset.rates),
                dataset.lograte_pm
            ],
            x0=guess,
            bounds=bounds,
            jac='3-point'
        )

        if curr_fit.status == 0:
            if verbose:
                ut.cprint(
                    '\n Fit failed - Too many iterations',
                    'black_yellowbg'
                )

            n_fitted_pars = np.sum(
                [len(logmodel.fit_vars.keys()) for logmodel in self.logmodels]
            )

            stdev = [np.nan] * n_fitted_pars
            self.fit_status = False
        else:

            stdev, no_stdev = stats.svd_stdev(curr_fit)

            self.fit_status = True

        # Add parameters, status and stdev to each LogTauTModel
        it = 0
        for logmodel in self.logmodels:

            # Name of fitted variables in this logmodel
            fit_var_names = logmodel.fit_vars.keys()
            # Number of parameters for this logmodel
            n_pars = len(fit_var_names)

            # Set each standard deviation
            _stdev = stdev[it: it + n_pars]
            logmodel.fit_stdev = {
                label: val
                for label, val in zip(
                    fit_var_names, _stdev
                )
            }

            # Report singular values=0 of Jacobian
            # and indicate that std_dev cannot be calculated
            sings = no_stdev[it: it + n_pars]
            for par, si in zip(fit_var_names, sings):
                if verbose and not si:
                    ut.cprint(
                        f'Warning: Jacobian is degenerate for {par}, standard deviation cannot be found, and is set to zero\n', # noqa
                        'black_yellowbg'
                    )

            # Set final fitted values
            _vals = curr_fit.x[it: it + n_pars]
            logmodel.final_var_values = {
                name: value
                for name, value in zip(fit_var_names, _vals)
            }
            # and fixed values
            for key, val in logmodel.fix_vars.items():
                logmodel.final_var_values[key] = val

            it += n_pars

        return


class LogFDQTMModel(LogTauHModel):
    '''
    Field dependent QTM Model of log10(Relaxation rate)

    Parameters
    ----------
    fit_vars: dict[str, float]
        Parameter to fit in model function\n
        Keys are fit/fix parameter names (see class.PARNAMES)\n
        Values are either float (actual value) or the string 'guess'\n
        If 'guess' then a parameter value is guessed
    fix_vars: dict[str, float]
        Parameter which remain fixed in model function\n
        Keys are fit/fix parameter names (see class.PARNAMES)\n
        Values are either float (actual value) or the string 'guess'\n
        If 'guess' then a parameter value is guessed

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
    fit_status: bool
        True if fit successful, else false
    '''

    #: Model name
    NAME = 'FD-QTM'

    #: Model name with log brackets
    LNAME = 'Log(FD-QTM)'

    #: Model Parameter name strings
    PARNAMES = [
        'Q',
        'Q_H',
        'p'
    ]

    #: Model Parameter name mathmode strings
    VARNAMES_MM = {
        'Q': r'$Q$',
        'Q_H': r'$Q_\mathregular{H}$',
        'p': r'$p$'
    }

    #: Model Parameter name HTML strings
    VARNAMES_HTML = {
        'Q_H': 'Q<sub>H</sub>',
        'Q': 'Q',
        'p': 'p'
    }

    #: Model Parameter unit strings
    UNITS = {
        'Q': 'log10[s]',
        'Q_H': 'log10[Oe^p]',
        'p': ''
    }

    #: Model Parameter unit mathmode strings
    UNITS_MM = {
        'Q': r'$\log_\mathregular{10}\left[\mathregular{s}\right]$',
        'Q_H': r'$\log_\mathregular{10}\left[\mathregular{Oe}^{p}\right]$', # noqa
        'p': ''
    }

    #: Model Parameter unit HTML strings
    UNITS_HTML = {
        'Q': 'log<sub>10</sub>[s]',
        'Q_H': 'log<sub>10</sub>[Oe<sup>p</sup>]',
        'p': ''
    }

    #: Model Parameter bounds
    BOUNDS = {
        'Q': [-np.inf, np.inf],
        'Q_H': [-np.inf, np.inf],
        'p': [0, np.inf]
    }

    @staticmethod
    def set_initial_vals(param_dict: dict[str, str | float]) -> dict[str, float]: # noqa
        '''
        Sets guess values for parameters if requested by user

        Parameters
        ----------
        param_dict: dict[str, str | float]
            Keys are fit/fix parameter names (see class.PARNAMES)\n
            Values are either float (actual value) or the string 'guess'

        Returns
        -------
        dict[str, float]
            Keys are fit/fix parameter names (see class.PARNAMES)\n
            Values are float (actual value) which are initial values of
            parameter
        '''

        # Make copy, any str values will be replaced
        new_param_dict = copy.copy(param_dict)

        # Guesses
        guessdict = {
            'Q': 1,
            'Q_H': -8,
            'p': 2
        }

        # Replace 'guess' with relevant guess
        for var, val in param_dict.items():
            if isinstance(val, str) and val.lower() == 'guess':
                new_param_dict[var] = guessdict[var]

        return new_param_dict

    @staticmethod
    def model(parameters: dict[str, float],
              fields: ArrayLike) -> NDArray:
        '''
        Evaluates field-dependent QTM model of log10(relaxation rate)
        using provided parameter and field values.

        Parameters
        ----------
        parameters: dict[str, float]
            Parameters to use in model function, keys are given in
            class.PARNAMES
        fields: array_like
            field values (Oe) at which model function is evaluated

        Returns
        -------
        ndarray of floats
            log10(Relaxation rate) as a function of field

        '''

        q = parameters['Q']
        qh = parameters['Q_H']
        p = parameters['p']

        fields = np.asarray(fields, dtype=float)

        lograte = np.log10(10**-q / (1 + 10**-qh * fields**p))

        return lograte


class LogRamanIIModel(LogTauHModel):
    '''
    Field dependent Raman-II Model of log10(Relaxation rate)

    Parameters
    ----------
    fit_vars: dict[str, float]
        Parameter to fit in model function\n
        Keys are fit/fix parameter names (see class.PARNAMES)\n
        Values are either float (actual value) or the string 'guess'\n
        If 'guess' then a parameter value is guessed
    fix_vars: dict[str, float]
        Parameter which remain fixed in model function\n
        Keys are fit/fix parameter names (see class.PARNAMES)\n
        Values are either float (actual value) or the string 'guess'\n
        If 'guess' then a parameter value is guessed

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
    fit_status: bool
        True if fit successful, else false
    '''

    #: Model name
    NAME = 'Raman-II'

    #: Model name with log brackets
    LNAME = 'Log(Raman-II)'

    #: Model Parameter name strings
    PARNAMES = [
        'C',
        'm',
    ]

    #: Model Parameter name mathmode strings
    VARNAMES_MM = {
        'C': '$C$',
        'm': '$m$'
    }

    #: Model Parameter name HTML strings
    VARNAMES_HTML = {
        'C': 'C',
        'm': 'm'
    }

    #: Model Parameter unit strings
    UNITS = {
        'C': 'log10[Oe^-m s^-1]',
        'm': ''
    }

    #: Model Parameter unit mathmode strings
    UNITS_MM = {
        'C': r'$\log_\mathregular{10}\left[\mathregular{Oe}^{-m} \ \mathregular{s}^\mathregular{-1}\right]$', # noqa
        'm': ''
    }

    #: Model Parameter name HTML strings
    UNITS_HTML = {
        'C': 'log<sub>10</sub>[Oe<sup>-m</sup> s<sup>-1</sup>]',
        'm': ''
    }

    #: Model Parameter bounds
    BOUNDS = {
        'C': [-np.inf, np.inf],
        'm': [0, np.inf],
    }

    @staticmethod
    def set_initial_vals(param_dict: dict[str, str | float]) -> dict[str, float]: # noqa
        '''
        Sets guess values for parameters if requested by user

        Parameters
        ----------
        param_dict: dict[str, str | float]
            Keys are fit/fix parameter names (see class.PARNAMES)\n
            Values are either float (actual value) or the string 'guess'

        Returns
        -------
        dict[str, float]
            Keys are fit/fix parameter names (see class.PARNAMES)\n
            Values are float (actual value) which are initial values of
            parameter
        '''

        # Make copy, any str values will be replaced
        new_param_dict = copy.copy(param_dict)

        # Guesses
        guessdict = {
            'C': -4,
            'm': 4
        }

        # Replace 'guess' with relevant guess
        for var, val in param_dict.items():
            if isinstance(val, str) and val.lower() == 'guess':
                new_param_dict[var] = guessdict[var]

        return new_param_dict

    @staticmethod
    def model(parameters: dict[str, float],
              fields: ArrayLike) -> NDArray:
        '''
        Evaluates field dependent Raman-II model of log10(relaxation rate)
        using provided parameter and field values.

        Parameters
        ----------
        parameters: dict[str, float]
            Parameters to use in model function, keys are given in
            class.PARNAMES
        fields: array_like
            field values (Oe) at which model function is evaluated

        Returns
        -------
        ndarray of floats
            log10(Relaxation rate) as a function of field

        '''

        c = parameters['C']
        m = parameters['m']

        fields = np.asarray(fields, dtype=float)

        lograte = np.log10(10**c * fields**m)

        return lograte


class LogConstantModel(LogTauHModel):
    '''
    Field-(in)dependent constant Model of log10(Relaxation rate)\n
    This is a field independent model, but is implemented\n
    here to work with the LogTauHModel class.

    Parameters
    ----------
    fit_vars: dict[str, float]
        Parameter to fit in model function\n
        Keys are fit/fix parameter names (see class.PARNAMES)\n
        Values are either float (actual value) or the string 'guess'\n
        If 'guess' then a parameter value is guessed
    fix_vars: dict[str, float]
        Parameter which remain fixed in model function\n
        Keys are fit/fix parameter names (see class.PARNAMES)\n
        Values are either float (actual value) or the string 'guess'\n
        If 'guess' then a parameter value is guessed

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
    fit_status: bool
        True if fit successful, else false
    '''

    #: Model name
    NAME = 'Constant'

    #: Model name with log brackets
    LNAME = 'Log(Constant)'

    #: Model Parameter name strings
    PARNAMES = [
        'Ct',
    ]

    #: Model Parameter name mathmode strings
    VARNAMES_MM = {
        'Ct': r'$Ct$',
    }

    #: Model Parameter name HTML strings
    VARNAMES_HTML = {
        'Ct': 'Ct'
    }

    #: Model Parameter unit strings
    UNITS = {
        'Ct': 'log10[s^-1]'
    }

    #: Model Parameter unit mathmode strings
    UNITS_MM = {
        'Ct': r'$\log_\mathregular{10}\left[\mathregular{s}^\mathregular{-1}\right]$', # noqa
    }

    #: Model Parameter unit HTML strings
    UNITS_HTML = {
        'Ct': 'log<sub>10</sub>[s<sup>-1</sup>]'
    }

    #: Model parameter bounds
    BOUNDS = {
        'Ct': [-np.inf, np.inf],
    }

    @staticmethod
    def set_initial_vals(param_dict: dict[str, str | float]) -> dict[str, float]: # noqa
        '''
        Sets guess values for parameters if requested by user

        Parameters
        ----------
        param_dict: dict[str, str | float]
            Keys are fit/fix parameter names (see class.PARNAMES)\n
            Values are either float (actual value) or the string 'guess'

        Returns
        -------
        dict[str, float]
            Keys are fit/fix parameter names (see class.PARNAMES)\n
            Values are float (actual value) which are initial values of
            parameter
        '''

        # Make copy, any str values will be replaced
        new_param_dict = copy.copy(param_dict)

        # Guesses
        guessdict = {
            'Ct': -4
        }

        # Replace 'guess' with relevant guess
        for var, val in param_dict.items():
            if isinstance(val, str) and val.lower() == 'guess':
                new_param_dict[var] = guessdict[var]

        return new_param_dict

    @staticmethod
    def model(parameters: dict[str, float],
              fields: ArrayLike) -> NDArray:
        '''
        Field-(in)dependent constant Model of log10(Relaxation rate)\n
        using provided parameter and field values.\n
        This is a field independent model, but is implemented\n
        here to work with the LogTauHModel class.

        Parameters
        ----------
        parameters: dict[str, float]
            Parameters to use in model function, keys are given in
            class.PARNAMES
        fields: array_like
            field values (Oe) at which model function is evaluated

        Returns
        -------
        ndarray of floats
            log10(Relaxation rate) as a function of field

        '''

        ct = parameters['Ct']

        lograte = np.zeros(len(fields)) + np.log10(10**ct)

        return lograte


class LogBVVRamanIIModel(LogTauHModel):
    '''
    Field dependent Brons-Van-Vleck * Raman-II Model of log10(Relaxation rate)

    Parameters
    ----------
    fit_vars: dict[str, float]
        Parameter to fit in model function\n
        Keys are fit/fix parameter names (see class.PARNAMES)\n
        Values are either float (actual value) or the string 'guess'\n
        If 'guess' then a parameter value is guessed
    fix_vars: dict[str, float]
        Parameter which remain fixed in model function\n
        Keys are fit/fix parameter names (see class.PARNAMES)\n
        Values are either float (actual value) or the string 'guess'\n
        If 'guess' then a parameter value is guessed

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
    fit_status: bool
        True if fit successful, else false
    '''

    #: Model name
    NAME = 'Brons-Van-Vleck * Raman-II'

    #: Model name with log brackets
    LNAME = 'Log(Brons-Van-Vleck * Raman-II)'

    #: Model Parameter name strings
    PARNAMES = [
        'e',
        'f',
        'C',
        'm'
    ]

    #: Model Parameter name mathmode strings
    VARNAMES_MM = {
        'e': r'$e$',
        'f': r'$f$',
        'C': r'$C$',
        'm': r'$m$',
    }

    #: Model Parameter name HTML strings
    VARNAMES_HTML = {
        'e': 'e',
        'f': 'f',
        'C': 'C',
        'm': 'm'
    }

    #: Model Parameter unit strings
    UNITS = {
        'e': 'log10[Oe^-2]',
        'f': 'log10[Oe^-2]',
        'C': 'log10[s^-1 Oe^-m]',
        'm': ''
    }

    #: Model Parameter unit mathmode strings
    UNITS_MM = {
        'e': r'$\log_\mathregular{10}\left[\mathregular{Oe}^\mathregular{-2}\right]$', # noqa
        'f': r'$\log_\mathregular{10}\left[\mathregular{Oe}^\mathregular{-2}\right]$', # noqa
        'C': r'$\log_\mathregular{10}\left[\mathregular{s}^\mathregular{-1} \mathregular{Oe}^\mathregular{-2}\right]$', # noqa
        'm': ''
    }

    #: Model Parameter unit HTML strings
    UNITS_HTML = {
        'e': 'log<sub>10</sub>[Oe<sup>-2</sup>]',
        'f': 'log<sub>10</sub>[Oe<sup>-2</sup>]',
        'C': 'log<sub>10</sub>[s<sup>-1</sup> Oe<sup>-m</sup>]',
        'm': ''
    }

    #: Model parameter bounds
    BOUNDS = {
        'e': [-np.inf, np.inf],
        'f': [-np.inf, np.inf],
        'C': [-np.inf, np.inf],
        'm': [0, np.inf]
    }

    @staticmethod
    def set_initial_vals(param_dict: dict[str, str | float]) -> dict[str, float]: # noqa
        '''
        Sets guess values for parameters if requested by user

        Parameters
        ----------
        param_dict: dict[str, str | float]
            Keys are fit/fix parameter names (see class.PARNAMES)\n
            Values are either float (actual value) or the string 'guess'

        Returns
        -------
        dict[str, float]
            Keys are fit/fix parameter names (see class.PARNAMES)\n
            Values are float (actual value) which are initial values of
            parameter
        '''

        # Make copy, any str values will be replaced
        new_param_dict = copy.copy(param_dict)

        # Guesses
        guessdict = {
            'e': -5.,
            'f': -5.,
            'C': -4,
            'm': 4.
        }

        # Replace 'guess' with relevant guess
        for var, val in param_dict.items():
            if isinstance(val, str) and val.lower() == 'guess':
                new_param_dict[var] = guessdict[var]

        return new_param_dict

    @staticmethod
    def model(parameters: dict[str, float],
              fields: ArrayLike) -> NDArray:
        '''
        Evaluates field dependent Brons-Van Vleck * Raman-II model of\n
        log10(relaxation rate) using provided parameter and field values.

        Parameters
        ----------
        parameters: dict[str, float]
            Parameters to use in model function, keys are given in
            class.PARNAMES
        fields: array_like
            field values (Oe) at which model function is evaluated

        Returns
        -------
        ndarray of floats
            log10(Relaxation rate) as a function of field

        '''

        e = parameters['e']
        f = parameters['f']
        C = parameters['C']
        m = parameters['m']

        fields = np.asarray(fields, dtype=float)

        lograte = np.log10(
            (10**C * fields**m) * (1 + 10**e * fields**2)/(1 + 10**f * fields**2) # noqa
        )

        return lograte


class LogBVVConstantModel(LogTauHModel):
    '''
    Field-dependent Brons-Van Vleck * constant model of log10(Relaxation rate)

    Parameters
    ----------
    fit_vars: dict[str, float]
        Parameter to fit in model function\n
        Keys are fit/fix parameter names (see class.PARNAMES)\n
        Values are either float (actual value) or the string 'guess'\n
        If 'guess' then a parameter value is guessed
    fix_vars: dict[str, float]
        Parameter which remain fixed in model function\n
        Keys are fit/fix parameter names (see class.PARNAMES)\n
        Values are either float (actual value) or the string 'guess'\n
        If 'guess' then a parameter value is guessed

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
    fit_status: bool
        True if fit successful, else false
    '''

    #: Model name
    NAME = 'Brons-Van-Vleck * Constant'

    #: Model name with log brackets
    LNAME = 'Log(Brons-Van-Vleck * Constant)'

    #: Model Parameter name strings
    PARNAMES = [
        'e',
        'f',
        'Ct'
    ]

    #: Model Parameter name mathmode strings
    VARNAMES_MM = {
        'e': r'$e$',
        'f': r'$f$',
        'Ct': r'$Ct$'
    }

    #: Model Parameter name HTML strings
    VARNAMES_HTML = {
        'e': 'e',
        'f': 'f',
        'Ct': 'Ct'
    }

    #: Model Parameter unit strings
    UNITS = {
        'e': 'log10[Oe^-2]',
        'f': 'log10[Oe^-2]',
        'Ct': 'log10[s^-1]'
    }

    #: Model Parameter unit mathmode strings
    UNITS_MM = {
        'e': r'$\log_\mathregular{10}\left[\mathregular{Oe}^\mathregular{-2}\right]$', # noqa
        'f': r'$\log_\mathregular{10}\left[\mathregular{Oe}^\mathregular{-2}\right]$', # noqa
        'Ct': r'$\log_\mathregular{10}\left[\mathregular{s}^\mathregular{-1}\right]$', # noqa
    }

    #: Model Parameter unit HTML strings
    UNITS_HTML = {
        'e': 'log<sub>10</sub>[Oe<sup>-2</sup>]',
        'f': 'log<sub>10</sub>[Oe<sup>-2</sup>]',
        'Ct': 'log<sub>10</sub>[s<sup>-1</sup>]'
    }

    #: Model parameter bounds
    BOUNDS = {
        'e': [-np.inf, np.inf],
        'f': [-np.inf, np.inf],
        'Ct': [-np.inf, np.inf]
    }

    @staticmethod
    def set_initial_vals(param_dict: dict[str, str | float]) -> dict[str, float]: # noqa
        '''
        Sets guess values for parameters if requested by user

        Parameters
        ----------
        param_dict: dict[str, str | float]
            Keys are fit/fix parameter names (see class.PARNAMES)\n
            Values are either float (actual value) or the string 'guess'

        Returns
        -------
        dict[str, float]
            Keys are fit/fix parameter names (see class.PARNAMES)\n
            Values are float (actual value) which are initial values of
            parameter
        '''

        # Make copy, any str values will be replaced
        new_param_dict = copy.copy(param_dict)

        # Guesses
        guessdict = {
            'e': -5.,
            'f': -5.,
            'Ct': -4
        }

        # Replace 'guess' with relevant guess
        for var, val in param_dict.items():
            if isinstance(val, str) and val.lower() == 'guess':
                new_param_dict[var] = guessdict[var]

        return new_param_dict

    @staticmethod
    def model(parameters: dict[str, float],
              fields: ArrayLike) -> NDArray:
        '''
        Evaluates field dependent Brons-van Vleck * constant model of\n
        log10(relaxation rate) using provided parameter and field values.

        Parameters
        ----------
        parameters: dict[str, float]
            Parameters to use in model function, keys are given in
            class.PARNAMES
        fields: array_like
            field values (Oe) at which model function is evaluated

        Returns
        -------
        ndarray of floats
            log10(Relaxation rate) as a function of field

        '''

        e = parameters['e']
        f = parameters['f']
        Ct = parameters['Ct']

        fields = np.asarray(fields, dtype=float)

        lograte = np.log10(
            10**Ct * (1 + 10**e * fields**2) / (1 + 10**f * fields**2)
        )

        return lograte


class LogOrbachModel(LogTauTModel):
    '''
    Temperature dependent Orbach model of log10(Relaxation rate)

    Parameters
    ----------
    fit_vars: dict[str, float]
        Parameter to fit in model function\n
        Keys are fit/fix parameter names (see class.PARNAMES)\n
        Values are either float (actual value) or the string 'guess'\n
        If 'guess' then a parameter value is guessed
    fix_vars: dict[str, float]
        Parameter which remain fixed in model function\n
        Keys are fit/fix parameter names (see class.PARNAMES)\n
        Values are either float (actual value) or the string 'guess'\n
        If 'guess' then a parameter value is guessed

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
    fit_status: bool
        True if fit successful, else false
    '''

    #: Model name
    NAME = 'Orbach'
    #: Model name with log brackets
    LNAME = 'Log(Orbach)'

    #: Model Parameter name strings
    PARNAMES = [
        'u_eff', 'A',
    ]

    #: Model Parameter name mathmode strings
    VARNAMES_MM = {
        'u_eff': r'$U_\mathregular{eff}$',
        'A': r'$A$'
    }

    #: Model Parameter name HTML strings
    VARNAMES_HTML = {
        'u_eff': 'U<sub>eff</sub>',
        'A': 'A'
    }

    #: Model Parameter unit strings
    UNITS = {
        'u_eff': r'K',
        'A': r'log10[s]'
    }

    #: Model Parameter unit mathmode strings
    UNITS_MM = {
        'u_eff': r'$\mathregular{K}$',
        'A': r'$\log_\mathregular{10}\left[\mathregular{s}\right]$' # noqa
    }

    #: Model Parameter unit HTML strings
    UNITS_HTML = {
        'u_eff': 'K',
        'A': 'log<sub>10</sub>[s]'
    }

    #: Model parameter bounds
    BOUNDS = {
        'u_eff': [0., np.inf],
        'A': [-np.inf, np.inf]
    }

    @staticmethod
    def set_initial_vals(param_dict: dict[str, str | float]) -> dict[str, float]: # noqa
        '''
        Sets guess values for parameters if requested by user

        Parameters
        ----------
        param_dict: dict[str, str | float]
            Keys are fit/fix parameter names (see class.PARNAMES)\n
            Values are either float (actual value) or the string 'guess'

        Returns
        -------
        dict[str, float]
            Keys are fit/fix parameter names (see class.PARNAMES)\n
            Values are float (actual value) which are initial values of
            parameter
        '''

        # Make copy, any str values will be replaced
        new_param_dict = copy.copy(param_dict)

        # Guesses
        guessdict = {
            'u_eff': 1500.,
            'A': -11
        }

        # Replace 'guess' with relevant guess
        for var, val in param_dict.items():
            if isinstance(val, str) and val.lower() == 'guess':
                new_param_dict[var] = guessdict[var]

        return new_param_dict

    @staticmethod
    def model(parameters: dict[str, float],
              temperatures: ArrayLike) -> NDArray:
        '''
        Evaluates temperature dependent Orbach model of log10(relaxation rate)
        using provided parameter and temperature values.

        Parameters
        ----------
        parameters: dict[str, float]
            Parameters to use in model function, keys are given in
            class.PARNAMES
        temperatures: array_like
            temperature values (K) at which model function is evaluated

        Returns
        -------
        ndarray of floats
            log10(Relaxation rate) as a function of temperature

        '''

        u_eff = parameters['u_eff']
        a = parameters['A']

        temperatures = np.asarray(temperatures, dtype=float)

        lograte = np.log10(10**-a * np.exp(-u_eff / temperatures))

        return lograte


class LogRamanModel(LogTauTModel):
    '''
    Temperature dependent Raman Model of log10(Relaxation rate) vs temperature

    Parameters
    ----------
    fit_vars: dict[str, float]
        Parameter to fit in model function\n
        Keys are fit/fix parameter names (see class.PARNAMES)\n
        Values are either float (actual value) or the string 'guess'\n
        If 'guess' then a parameter value is guessed
    fix_vars: dict[str, float]
        Parameter which remain fixed in model function\n
        Keys are fit/fix parameter names (see class.PARNAMES)\n
        Values are either float (actual value) or the string 'guess'\n
        If 'guess' then a parameter value is guessed

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
    fit_status: bool
        True if fit successful, else false
    '''

    #: Model name
    NAME = 'Raman'
    #: Model name with log brackets
    LNAME = 'Log(Raman)'

    #: Model Parameter name strings
    PARNAMES = [
        'R', 'n',
    ]

    #: Model Parameter name mathmode strings
    VARNAMES_MM = {
        'R': r'$R$',
        'n': r'$n$'
    }

    #: Model Parameter name HTML strings
    VARNAMES_HTML = {
        'R': 'R',
        'n': 'n'
    }

    #: Model Parameter unit strings
    UNITS = {
        'R': 'log10[s^-1 K^-n]',
        'n': ''
    }

    #: Model Parameter unit mathmode strings
    UNITS_MM = {
        'R': r'$\log_\mathregular{10}\left[\mathregular{s}^\mathregular{-1} \mathregular{K}^{-n}\right]$', # noqa
        'n': ''
    }

    #: Model Parameter unit HTML strings
    UNITS_HTML = {
        'R': 'log<sub>10</sub>[s<sup>-1</sup> K<sup>-n</sup>]',
        'n': ''
    }

    #: Model parameter bounds
    BOUNDS = {
        'R': [-np.inf, np.inf],
        'n': [0, np.inf]
    }

    @staticmethod
    def set_initial_vals(param_dict: dict[str, str | float]) -> dict[str, float]: # noqa
        '''
        Sets guess values for parameters if requested by user

        Parameters
        ----------
        param_dict: dict[str, str | float]
            Keys are fit/fix parameter names (see class.PARNAMES)\n
            Values are either float (actual value) or the string 'guess'

        Returns
        -------
        dict[str, float]
            Keys are fit/fix parameter names (see class.PARNAMES)\n
            Values are float (actual value) which are initial values of
            parameter
        '''

        # Make copy, any str values will be replaced
        new_param_dict = copy.copy(param_dict)

        # Guesses
        guessdict = {
            'R': -6,
            'n': 3
        }

        # Replace 'guess' with relevant guess
        for var, val in param_dict.items():
            if isinstance(val, str) and val.lower() == 'guess':
                new_param_dict[var] = guessdict[var]

        return new_param_dict

    @staticmethod
    def model(parameters: dict[str, float],
              temperatures: ArrayLike) -> NDArray:
        '''
        Evaluates temperature dependent Raman model of log10(relaxation rate)
        using provided parameter and temperature values.

        Parameters
        ----------
        parameters: dict[str, float]
            Parameters to use in model function, keys are given in
            class.PARNAMES
        temperatures: array_like
            temperature values (K) at which model function is evaluated

        Returns
        -------
        ndarray of floats
            log10(Relaxation rate) as a function of temperature

        '''

        r = parameters['R']
        n = parameters['n']

        temperatures = np.asarray(temperatures, dtype=float)

        lograte = np.log10(10**r * temperatures**n)

        return lograte


class LogPPDRamanModel(LogTauTModel):
    '''
    Temperature dependent Phonon Pair-Driven Raman Model of
    log10(Relaxation rate) vs temperature

    Parameters
    ----------
    fit_vars: dict[str, float]
        Parameter to fit in model function\n
        Keys are fit/fix parameter names (see class.PARNAMES)\n
        Values are either float (actual value) or the string 'guess'\n
        If 'guess' then a parameter value is guessed
    fix_vars: dict[str, float]
        Parameter which remain fixed in model function\n
        Keys are fit/fix parameter names (see class.PARNAMES)\n
        Values are either float (actual value) or the string 'guess'\n
        If 'guess' then a parameter value is guessed

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
    fit_status: bool
        True if fit successful, else false
    '''

    #: Model name
    NAME = 'PPDRaman'
    #: Model name with log brackets
    LNAME = 'Log(PPDRaman)'

    #: Model Parameter name strings
    PARNAMES = [
        'w',
        'R'
    ]

    #: Model Parameter name mathmode strings
    VARNAMES_MM = {
        'R': r'$R$',
        'w': r'$\omega$'
    }

    #: Model Parameter name HTML strings
    VARNAMES_HTML = {
        'R': 'R',
        'w': 'ω'
    }

    #: Model Parameter unit strings
    UNITS = {
        'R': 'log10[s^-1]',
        'w': 'K'
    }

    #: Model Parameter unit mathmode strings
    UNITS_MM = {
        'R': r'$\log_\mathregular{10}\left[\mathregular{s}^\mathregular{-1}\right]$', # noqa
        'w': r'$\mathregular{K}$'
    }

    #: Model Parameter unit HTML strings
    UNITS_HTML = {
        'R': 'log<sub>10</sub>[s<sup>-1</sup>]',
        'w': 'K'
    }

    #: Model parameter bounds
    BOUNDS = {
        'w': [0, np.inf],
        'R': [-np.inf, np.inf]
    }

    @staticmethod
    def set_initial_vals(param_dict: dict[str, str | float]) -> dict[str, float]: # noqa
        '''
        Sets guess values for parameters if requested by user

        Parameters
        ----------
        param_dict: dict[str, str | float]
            Keys are fit/fix parameter names (see class.PARNAMES)\n
            Values are either float (actual value) or the string 'guess'

        Returns
        -------
        dict[str, float]
            Keys are fit/fix parameter names (see class.PARNAMES)\n
            Values are float (actual value) which are initial values of
            parameter
        '''

        # Make copy, any str values will be replaced
        new_param_dict = copy.copy(param_dict)

        # Guesses
        guessdict = {
            'w': 10,
            'R': 4
        }

        # Replace 'guess' with relevant guess
        for var, val in param_dict.items():
            if isinstance(val, str) and val.lower() == 'guess':
                new_param_dict[var] = guessdict[var]

        return new_param_dict

    @staticmethod
    def model(parameters: dict[str, float],
              temperatures: ArrayLike) -> NDArray:
        '''
        Evaluates temperature dependent Phonon Pair-Driven Raman Model of
        log10(relaxation rate) using provided parameter and temperature values.

        Parameters
        ----------
        parameters: dict[str, float]
            Parameters to use in model function, keys are given in
            class.PARNAMES
        temperatures: array_like
            temperature values (K) at which model function is evaluated

        Returns
        -------
        ndarray of floats
            log10(Relaxation rate) as a function of temperature

        '''

        omega = parameters['w']
        R = parameters['R']

        temperatures = np.asarray(temperatures, dtype=float)

        num = np.exp(omega / temperatures)
        denom = (np.exp(omega / temperatures) - 1)**2
        coeff = 10**R

        lograte = np.log10(coeff * (num / denom))

        return lograte


class LogQTMModel(LogTauTModel):
    '''
    Temperature (in)dependent QTM model of log10(Relaxation rate)\n
    This model is temperature independent, but has been implemented here to\n
    work with the LogTauTModel class

    Parameters
    ----------
    fit_vars: dict[str, float]
        Parameter to fit in model function\n
        Keys are fit/fix parameter names (see class.PARNAMES)\n
        Values are either float (actual value) or the string 'guess'\n
        If 'guess' then a parameter value is guessed
    fix_vars: dict[str, float]
        Parameter which remain fixed in model function\n
        Keys are fit/fix parameter names (see class.PARNAMES)\n
        Values are either float (actual value) or the string 'guess'\n
        If 'guess' then a parameter value is guessed

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
    fit_status: bool
        True if fit successful, else false
    '''

    #: Model name
    NAME = 'QTM'
    #: Model name with log brackets
    LNAME = 'Log(QTM)'

    #: Model Parameter name strings
    PARNAMES = [
        'Q'
    ]

    #: Model Parameter name mathmode strings
    VARNAMES_MM = {
        'Q': r'$Q$',
    }

    #: Model Parameter name HTML strings
    VARNAMES_HTML = {
        'Q': 'Q',
    }

    #: Model Parameter unit strings
    UNITS = {
        'Q': 'log10[s]',
    }

    #: Model Parameter unit mathmode strings
    UNITS_MM = {
        'Q': r'$\log_\mathregular{10}\left[\mathregular{s}\right]$',
    }

    #: Model Parameter unit HTML strings
    UNITS_HTML = {
        'Q': 'log<sub>10</sub>[s]'
    }

    #: Model parameter bounds
    BOUNDS = {
        'Q': [-np.inf, np.inf]
    }

    @staticmethod
    def set_initial_vals(param_dict: dict[str, str | float]) -> dict[str, float]: # noqa
        '''
        Sets guess values for parameters if requested by user

        Parameters
        ----------
        param_dict: dict[str, str | float]
            Keys are fit/fix parameter names (see class.PARNAMES)\n
            Values are either float (actual value) or the string 'guess'

        Returns
        -------
        dict[str, float]
            Keys are fit/fix parameter names (see class.PARNAMES)\n
            Values are float (actual value) which are initial values of
            parameter
        '''

        # Make copy, any str values will be replaced
        new_param_dict = copy.copy(param_dict)

        # Guesses
        guessdict = {
            'Q': 1
        }

        # Replace 'guess' with relevant guess
        for var, val in param_dict.items():
            if isinstance(val, str) and val.lower() == 'guess':
                new_param_dict[var] = guessdict[var]

        return new_param_dict

    @staticmethod
    def model(parameters: dict[str, float],
              temperatures: ArrayLike) -> NDArray:
        '''
        Evaluates temperature (in)dependent QTM model of\n
        log10(relaxation rate) using provided parameter and temperature\n
        values.

        This model is temperature independent, but has been implemented here\n
        to work with the LogTauTModel class

        Parameters
        ----------
        parameters: dict[str, float]
            Parameters to use in model function, keys are given in
            class.PARNAMES
        temperatures: array_like
            temperature values (K) at which model function is evaluated

        Returns
        -------
        ndarray of floats
            log10(Relaxation rate) as a function of temperature

        '''

        q = parameters['Q']

        lograte = np.zeros(len(temperatures)) + np.log10(10**-q)

        return lograte


class LogDirectModel(LogTauTModel):
    '''
    Temperature dependent Direct model of log10(Relaxation rate)

    Parameters
    ----------
    fit_vars: dict[str, float]
        Parameter to fit in model function\n
        Keys are fit/fix parameter names (see class.PARNAMES)\n
        Values are either float (actual value) or the string 'guess'\n
        If 'guess' then a parameter value is guessed
    fix_vars: dict[str, float]
        Parameter which remain fixed in model function\n
        Keys are fit/fix parameter names (see class.PARNAMES)\n
        Values are either float (actual value) or the string 'guess'\n
        If 'guess' then a parameter value is guessed

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
    fit_status: bool
        True if fit successful, else false
    '''

    #: Model name
    NAME = 'Direct'

    #: Model name with log brackets
    LNAME = 'Log(Direct)'

    #: Model Parameter name strings
    PARNAMES = [
        'D'
    ]

    #: Model Parameter name mathmode strings
    VARNAMES_MM = {
        'D': r'$D$',
    }

    #: Model Parameter name HTML strings
    VARNAMES_HTML = {
        'D': 'D'
    }

    #: Model Parameter unit strings
    UNITS = {
        'D': 'log10[s-1 K-1]',
    }

    #: Model Parameter unit mathmode strings
    UNITS_MM = {
        'D': r'$\log_\mathregular{10}\left[\mathregular{s}^\mathregular{-1} \mathregular{K}^\mathregular{-1}\right]$', # noqa
    }

    #: Model Parameter unit HTML strings
    UNITS_HTML = {
        'D': 's<sup>-1</sup> K<sup>-1</sup>'
    }

    #: Model parameter bounds
    BOUNDS = {
        'D': [-np.inf, np.inf]
    }

    @staticmethod
    def set_initial_vals(param_dict: dict[str, str | float]) -> dict[str, float]: # noqa
        '''
        Sets guess values for parameters if requested by user

        Parameters
        ----------
        param_dict: dict[str, str | float]
            Keys are fit/fix parameter names (see class.PARNAMES)\n
            Values are either float (actual value) or the string 'guess'

        Returns
        -------
        dict[str, float]
            Keys are fit/fix parameter names (see class.PARNAMES)\n
            Values are float (actual value) which are initial values of
            parameter
        '''

        # Make copy, any str values will be replaced
        new_param_dict = copy.copy(param_dict)

        # Guesses
        guessdict = {
            'D': -2
        }

        # Replace 'guess' with relevant guess
        for var, val in param_dict.items():
            if isinstance(val, str) and val.lower() == 'guess':
                new_param_dict[var] = guessdict[var]

        return new_param_dict

    @staticmethod
    def model(parameters: dict[str, float],
              temperatures: ArrayLike) -> NDArray:
        '''
        Evaluates temperature dependent Direct model of log10(relaxation rate)
        using provided parameter and temperature values.

        Parameters
        ----------
        parameters: dict[str, float]
            Parameters to use in model function, keys are given in
            class.PARNAMES
        temperatures: array_like
            temperature values (K) at which model function is evaluated

        Returns
        -------
        ndarray of floats
            log10(Relaxation rate) as a function of temperature

        '''

        d = parameters['D']

        temperatures = np.asarray(temperatures, dtype=float)

        lograte = np.log10(10**d * temperatures)

        return lograte


class LogRamanQTMPBModel(LogTauTModel):
    '''
    Temperature dependent Phonon Bottlenecked Raman and QTM Model of\n
    log10(Relaxation rate)
    '''

    #: Model name
    NAME = 'Phonon Bottleneck QTM-Raman'
    #: Model name with log brackets
    LNAME = 'Log(Phonon Bottleneck QTM-Raman)'

    #: Model Parameter name strings
    PARNAMES = [
        'R',
        'n',
        'Q',
        'B',
        'm'
    ]

    #: Model Parameter name mathmode strings
    VARNAMES_MM = {
        'R': r'$R$',
        'n': r'$n$',
        'Q': r'$Q$',
        'B': r'$B$',
        'm': r'$m$'
    }

    #: Model Parameter name HTML strings
    VARNAMES_HTML = {
        'R': 'R',
        'n': 'n',
        'Q': 'Q',
        'B': 'B',
        'm': 'm'
    }

    #: Model Parameter unit strings
    UNITS = {
        'R': 'log10[s^-1 K^-n]',
        'n': '',
        'Q': 'log10[s]',
        'B': 'log10[s K^m]',
        'm': ''
    }

    #: Model Parameter unit mathmode strings
    UNITS_MM = {
        'R': r'$\log_\mathregular{10}\left[\mathregular{s}^\mathregular{-1} \mathregular{K}^{-n}\right]$', # noqa
        'n': '',
        'Q': r'$\log_\mathregular{10}\left[\mathregular{s}\right]$',
        'B': r'$\log_\mathregular{10}\left[\mathregular{s} \mathregular{K}^{m}\right]$', # noqa
        'm': ''
    }

    #: Model Parameter unit HTML strings
    UNITS_HTML = {
        'R': 'log<sub>10</sub>[s<sup>-1</sup> K<sup>-n</sup>]',
        'n': '',
        'Q': 'log<sub>10</sub>[s]',
        'B': 'log<sub>10</sub>[s K<sup>m</sup>]',
        'm': ''
    }

    #: Model parameter bounds
    BOUNDS = {
        'R': [-30, np.inf],
        'n': [0, np.inf],
        'Q': [-30, 30.],
        'B': [-30, 30.],
        'm': [0, 30.]
    }

    @staticmethod
    def set_initial_vals(param_dict: dict[str, str | float]) -> dict[str, float]: # noqa
        '''
        Sets guess values for parameters if requested by user

        Parameters
        ----------
        param_dict: dict[str, str | float]
            Keys are fit/fix parameter names (see class.PARNAMES)\n
            Values are either float (actual value) or the string 'guess'

        Returns
        -------
        dict[str, float]
            Keys are fit/fix parameter names (see class.PARNAMES)\n
            Values are float (actual value) which are initial values of
            parameter
        '''

        # Make copy, any str values will be replaced
        new_param_dict = copy.copy(param_dict)

        # Guesses
        guessdict = {
            'R': -6,
            'n': 3,
            'Q': 1,
            'B': 3,
            'm': 2
        }

        # Replace 'guess' with relevant guess
        for var, val in param_dict.items():
            if isinstance(val, str) and val.lower() == 'guess':
                new_param_dict[var] = guessdict[var]

        return new_param_dict

    @staticmethod
    def model(parameters: dict[str, float],
              temperatures: ArrayLike) -> NDArray:
        '''
        Evaluates temperature dependent Phonon Bottlenecked Raman and QTM\n
        model of log10(Relaxation rate) using provided parameter and\n
        temperature values.

        Parameters
        ----------
        parameters: dict[str, float]
            Parameters to use in model function, keys are given in
            class.PARNAMES
        temperatures: array_like
            temperature values (K) at which model function is evaluated

        Returns
        -------
        ndarray of floats
            log10(Relaxation rate) as a function of temperature

        '''

        r = parameters['R']
        n = parameters['n']
        q = parameters['Q']
        b = parameters['B']
        m = parameters['m']

        temperatures = np.asarray(temperatures, dtype=float)

        timespinlat = 1 / (10**r * temperatures**n + 10**-q)

        timelatbath = 10**b * temperatures**(-m)

        lograte = np.log10(1. / (timespinlat + timelatbath))

        return lograte


class LogDirectPBModel(LogTauTModel):
    '''
    Temperature dependent Phonon Bottlenecked Direct Model of\n
    log10(Relaxation rate)
    '''

    #: Model name
    NAME = 'Phonon Bottleneck Direct'
    #: Model name with log brackets
    LNAME = 'Log(Phonon Bottleneck Direct'

    #: Model Parameter name strings
    PARNAMES = [
        'D',
        'B',
        'm'
    ]

    #: Model Parameter name mathmode strings
    VARNAMES_MM = {
        'D': r'$D$',
        'B': r'$B$',
        'm': r'$m$'
    }

    #: Model Parameter name HTML strings
    VARNAMES_HTML = {
        'D': 'D',
        'B': 'B',
        'm': 'm'
    }

    #: Model Parameter unit strings
    UNITS = {
        'D': 'log10[s^-1 K^-1]',
        'B': 'log10[s K^m]',
        'm': ''
    }

    #: Model Parameter unit mathmode strings
    UNITS_MM = {
        'D': r'$\log_\mathregular{10}\left[\mathregular{s}^\mathregular{-1} \mathregular{K}^\mathregular{-1}\right]$', # noqa
        'B': r'$\log_\mathregular{10}\left[\mathregular{s} \mathregular{K}^{m}\right]$', # noqa
        'm': ''
    }

    #: Model Parameter unit HTML strings
    UNITS_HTML = {
        'D': 'log<sub>10</sub>[s<sup>-1</sup> K<sup>-1</sup>]',
        'B': 'log<sub>10</sub>[s K<sup>m</sup>]',
        'm': ''
    }

    #: Model parameter bounds
    BOUNDS = {
        'D': [-30, np.inf],
        'B': [-30, 30.],
        'm': [0, 30.]
    }

    @staticmethod
    def set_initial_vals(param_dict: dict[str, str | float]) -> dict[str, float]: # noqa
        '''
        Sets guess values for parameters if requested by user

        Parameters
        ----------
        param_dict: dict[str, str | float]
            Keys are fit/fix parameter names (see class.PARNAMES)\n
            Values are either float (actual value) or the string 'guess'

        Returns
        -------
        dict[str, float]
            Keys are fit/fix parameter names (see class.PARNAMES)\n
            Values are float (actual value) which are initial values of
            parameter
        '''

        # Make copy, any str values will be replaced
        new_param_dict = copy.copy(param_dict)

        # Guesses
        guessdict = {
            'D': -6,
            'B': 3,
            'm': 2
        }

        # Replace 'guess' with relevant guess
        for var, val in param_dict.items():
            if isinstance(val, str) and val.lower() == 'guess':
                new_param_dict[var] = guessdict[var]

        return new_param_dict

    @staticmethod
    def model(parameters: dict[str, float],
              temperatures: ArrayLike) -> NDArray:
        '''
        Evaluates temperature dependent Phonon Bottlenecked Direct\n
        model of log10(Relaxation rate) using provided parameter and\n
        temperature values.

        Parameters
        ----------
        parameters: dict[str, float]
            Parameters to use in model function, keys are given in
            class.PARNAMES
        temperatures: array_like
            temperature values (K) at which model function is evaluated

        Returns
        -------
        ndarray of floats
            log10(Relaxation rate) as a function of temperature

        '''

        d = parameters['D']
        b = parameters['B']
        m = parameters['m']

        temperatures = np.asarray(temperatures, dtype=float)

        timespinlat = 1 / (10**d * temperatures**-1)

        timelatbath = 10**b * temperatures**(-m)

        lograte = np.log10(1. / (timespinlat + timelatbath))

        return lograte


class LogRamanPBModel(LogTauTModel):
    '''
    Temperature dependent Phonon Bottlenecked Raman Model of\n
    log10(Relaxation rate)
    '''

    #: Model name
    NAME = 'Phonon Bottleneck Raman'
    #: Model name with log brackets
    LNAME = 'Log(Phonon Bottleneck Raman)'

    #: Model Parameter name strings
    PARNAMES = [
        'R',
        'n',
        'B',
        'm'
    ]

    #: Model Parameter name mathmode strings
    VARNAMES_MM = {
        'R': r'$R$',
        'n': r'$n$',
        'B': r'$B$',
        'm': r'$m$'
    }

    #: Model Parameter name HTML strings
    VARNAMES_HTML = {
        'R': 'R',
        'n': 'n',
        'B': 'B',
        'm': 'm'
    }

    #: Model Parameter unit strings
    UNITS = {
        'R': 'log10[s^-1 K^-n]',
        'n': '',
        'B': 'log10[s K^m]',
        'm': ''
    }

    #: Model Parameter unit mathmode strings
    UNITS_MM = {
        'R': r'$\log_\mathregular{10}\left[\mathregular{s}^\mathregular{-1} \mathregular{K}^{-n}\right]$', # noqa
        'n': '',
        'B': r'$\log_\mathregular{10}\left[\mathregular{s} \mathregular{K}^{m}\right]$', # noqa
        'm': ''
    }

    #: Model Parameter unit HTML strings
    UNITS_HTML = {
        'R': 'log<sub>10</sub>[s<sup>-1</sup> K<sup>-n</sup>]',
        'n': '',
        'B': 'log<sub>10</sub>[s K<sup>m</sup>]',
        'm': ''
    }

    #: Model parameter bounds
    BOUNDS = {
        'R': [-30, np.inf],
        'n': [0, np.inf],
        'B': [-30, 30.],
        'm': [0, 30.]
    }

    @staticmethod
    def set_initial_vals(param_dict: dict[str, str | float]) -> dict[str, float]: # noqa
        '''
        Sets guess values for parameters if requested by user

        Parameters
        ----------
        param_dict: dict[str, str | float]
            Keys are fit/fix parameter names (see class.PARNAMES)\n
            Values are either float (actual value) or the string 'guess'

        Returns
        -------
        dict[str, float]
            Keys are fit/fix parameter names (see class.PARNAMES)\n
            Values are float (actual value) which are initial values of
            parameter
        '''

        # Make copy, any str values will be replaced
        new_param_dict = copy.copy(param_dict)

        # Guesses
        guessdict = {
            'R': -6,
            'n': 3,
            'B': 3,
            'm': 2
        }

        # Replace 'guess' with relevant guess
        for var, val in param_dict.items():
            if isinstance(val, str) and val.lower() == 'guess':
                new_param_dict[var] = guessdict[var]

        return new_param_dict

    @staticmethod
    def model(parameters: dict[str, float],
              temperatures: ArrayLike) -> NDArray:
        '''
        Evaluates temperature dependent Phonon Bottlenecked Raman\n
        model of log10(Relaxation rate) using provided parameter and\n
        temperature values.

        Parameters
        ----------
        parameters: dict[str, float]
            Parameters to use in model function, keys are given in
            class.PARNAMES
        temperatures: array_like
            temperature values (K) at which model function is evaluated

        Returns
        -------
        ndarray of floats
            log10(Relaxation rate) as a function of temperature

        '''

        r = parameters['R']
        n = parameters['n']
        b = parameters['B']
        m = parameters['m']

        temperatures = np.asarray(temperatures, dtype=float)

        timespinlat = 1 / (10**r * temperatures**n)

        timelatbath = 10**b * temperatures**(-m)

        lograte = np.log10(1 / (timespinlat + timelatbath))

        return lograte


class LogFTDOrbachModel(LogTauHTModel):
    '''
    Field and temperature dependent Orbach Model of log10(Relaxation rate)

    This model is field independent, but has been implemented here to\n
    work with the LogTauHTModel class

    Parameters
    ----------
    fit_vars: dict[str, float]
        Parameter to fit in model function\n
        Keys are fit/fix parameter names (see class.PARNAMES)\n
        Values are either float (actual value) or the string 'guess'\n
        If 'guess' then a parameter value is guessed
    fix_vars: dict[str, float]
        Parameter which remain fixed in model function\n
        Keys are fit/fix parameter names (see class.PARNAMES)\n
        Values are either float (actual value) or the string 'guess'\n
        If 'guess' then a parameter value is guessed

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
    fit_status: bool
        True if fit successful, else false
    '''

    #: Model name
    NAME = 'FTD-Orbach'
    #: Model name with log brackets
    LNAME = 'Log(FTD-Orbach)'

    #: Model Parameter name strings
    PARNAMES = [
        'u_eff', 'A',
    ]

    #: Model Parameter name mathmode strings
    VARNAMES_MM = {
        'u_eff': r'$U_\mathregular{eff}$',
        'A': r'$A$'
    }

    #: Model Parameter name HTML strings
    VARNAMES_HTML = {
        'u_eff': 'U<sub>eff</sub>',
        'A': 'A'
    }

    #: Model Parameter unit strings
    UNITS = {
        'u_eff': r'K',
        'A': r'log10[s]'
    }

    #: Model Parameter unit mathmode strings
    UNITS_MM = {
        'u_eff': r'$\mathregular{K}$',
        'A': r'$\log_\mathregular{10}\left[\mathregular{s}\right]$' # noqa
    }

    #: Model Parameter unit HTML strings
    UNITS_HTML = {
        'u_eff': 'K',
        'A': 'log<sub>10</sub>[s]'
    }

    #: Model parameter bounds
    BOUNDS = {
        'u_eff': [0., np.inf],
        'A': [-np.inf, np.inf]
    }

    @staticmethod
    def set_initial_vals(param_dict: dict[str, str | float]) -> dict[str, float]: # noqa
        '''
        Sets guess values for parameters if requested by user

        Parameters
        ----------
        param_dict: dict[str, str | float]
            Keys are fit/fix parameter names (see class.PARNAMES)\n
            Values are either float (actual value) or the string 'guess'

        Returns
        -------
        dict[str, float]
            Keys are fit/fix parameter names (see class.PARNAMES)\n
            Values are float (actual value) which are initial values of
            parameter
        '''

        # Make copy, any str values will be replaced
        new_param_dict = copy.copy(param_dict)

        # Guesses
        guessdict = {
            'u_eff': 1500.,
            'A': -11
        }

        # Replace 'guess' with relevant guess
        for var, val in param_dict.items():
            if isinstance(val, str) and val.lower() == 'guess':
                new_param_dict[var] = guessdict[var]

        return new_param_dict

    @staticmethod
    def model(parameters: dict[str, float],
              fields: ArrayLike,
              temperatures: ArrayLike) -> NDArray:
        '''
        Evaluates field and temperature dependent Orbach model of\n
        log10(relaxation rate) using provided parameter and temperature\n
        values.\n

        This model is field independent, but has been implemented here to\n
        work with the LogTauHTModel class

        Parameters
        ----------
        parameters: dict[str, float]
            Parameters to use in model function, keys are given in
            class.PARNAMES
        fields: array_like
            Field values (Oe) at which model function is evaluated.\n
            These are not used, but are provided to match function signature\n
            for the base class's model method.
        temperatures: array_like
            Temperature values (K) at which model function is evaluated


        Returns
        -------
        ndarray of floats
            log10(Relaxation rate) as a function of temperature

        '''

        u_eff = parameters['u_eff']
        a = parameters['A']

        temperatures = np.asarray(temperatures, dtype=float)

        lograte = np.log10(10**-a * np.exp(-u_eff / temperatures))

        return lograte


class LogFTDQTMModel(LogTauHTModel):
    '''
    Field and temperature dependent QTM Model of log10(Relaxation rate)

    This model is temperature independent, but has been implemented here to\n
    work with the LogTauHTModel class

    Parameters
    ----------
    fit_vars: dict[str, float]
        Parameter to fit in model function\n
        Keys are fit/fix parameter names (see class.PARNAMES)\n
        Values are either float (actual value) or the string 'guess'\n
        If 'guess' then a parameter value is guessed
    fix_vars: dict[str, float]
        Parameter which remain fixed in model function\n
        Keys are fit/fix parameter names (see class.PARNAMES)\n
        Values are either float (actual value) or the string 'guess'\n
        If 'guess' then a parameter value is guessed

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
    fit_status: bool
        True if fit successful, else false
    '''

    #: Model name
    NAME = 'FTD-QTM'

    #: Model name with log brackets
    LNAME = 'Log(FTD-QTM)'

    #: Model Parameter name strings
    PARNAMES = [
        'Q',
        'Q_H',
        'p'
    ]

    #: Model Parameter name mathmode strings
    VARNAMES_MM = {
        'Q': r'$Q$',
        'Q_H': r'$Q_\mathregular{H}$',
        'p': r'$p$'
    }

    #: Model Parameter name HTML strings
    VARNAMES_HTML = {
        'Q_H': 'Q<sub>H</sub>',
        'Q': 'Q',
        'p': 'p'
    }

    #: Model Parameter unit strings
    UNITS = {
        'Q': 'log10[s]',
        'Q_H': 'log10[Oe^p]',
        'p': ''
    }

    #: Model Parameter unit mathmode strings
    UNITS_MM = {
        'Q': r'$\log_\mathregular{10}\left[\mathregular{s}\right]$',
        'Q_H': r'$\log_\mathregular{10}\left[\mathregular{Oe}^{p}\right]$', # noqa
        'p': ''
    }

    #: Model Parameter unit HTML strings
    UNITS_HTML = {
        'Q': 'log<sub>10</sub>[s]',
        'Q_H': 'log<sub>10</sub>[Oe<sup>p</sup>]',
        'p': ''
    }

    #: Model Parameter bounds
    BOUNDS = {
        'Q': [-np.inf, np.inf],
        'Q_H': [-np.inf, np.inf],
        'p': [0, np.inf]
    }

    @staticmethod
    def set_initial_vals(param_dict: dict[str, str | float]) -> dict[str, float]: # noqa
        '''
        Sets guess values for parameters if requested by user

        Parameters
        ----------
        param_dict: dict[str, str | float]
            Keys are fit/fix parameter names (see class.PARNAMES)\n
            Values are either float (actual value) or the string 'guess'

        Returns
        -------
        dict[str, float]
            Keys are fit/fix parameter names (see class.PARNAMES)\n
            Values are float (actual value) which are initial values of
            parameter
        '''

        # Make copy, any str values will be replaced
        new_param_dict = copy.copy(param_dict)

        # Guesses
        guessdict = {
            'Q': 1,
            'Q_H': -8,
            'p': 2
        }

        # Replace 'guess' with relevant guess
        for var, val in param_dict.items():
            if isinstance(val, str) and val.lower() == 'guess':
                new_param_dict[var] = guessdict[var]

        return new_param_dict

    @staticmethod
    def model(parameters: dict[str, float],
              fields: ArrayLike,
              temperatures: ArrayLike = []) -> NDArray:
        '''
        Evaluates field and temperature dependent QTM model of\n
        log10(relaxation rate) using provided parameter and field values.\n

        This model is temperature-independent, but has been implemented here\n
        to work with the LogTauHTModel class.

        Parameters
        ----------
        parameters: dict[str, float]
            Parameters to use in model function, keys are given in
            class.PARNAMES
        fields: array_like
            Field values (Oe) at which model function is evaluated
        temperatures: array_like, default []
            Temperature values (K) at which model function is evaluated.\n
            These are not used, but are provided to match function signature\n
            for the base class's model method.

        Returns
        -------
        ndarray of floats
            log10(Relaxation rate) as a function of field

        '''

        q = parameters['Q']
        qh = parameters['Q_H']
        p = parameters['p']

        fields = np.asarray(fields, dtype=float)

        lograte = np.log10(10**-q / (1 + 10**-qh * fields**p))

        return lograte


class LogFTDRamanIIDirectModel(LogTauHTModel):
    '''
    Field and temperature dependent Raman-II/Direct Model of\n
    log10(Relaxation rate).\n

    Raman-II and Direct take the same power-law form when both temperature\n
    and field dependent.

    Parameters
    ----------
    fit_vars: dict[str, float]
        Parameter to fit in model function\n
        Keys are fit/fix parameter names (see class.PARNAMES)\n
        Values are either float (actual value) or the string 'guess'\n
        If 'guess' then a parameter value is guessed
    fix_vars: dict[str, float]
        Parameter which remain fixed in model function\n
        Keys are fit/fix parameter names (see class.PARNAMES)\n
        Values are either float (actual value) or the string 'guess'\n
        If 'guess' then a parameter value is guessed

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
    fit_status: bool
        True if fit successful, else false
    '''

    #: Model name
    NAME = 'FTD-Raman-II-Direct'

    #: Model name with log brackets
    LNAME = 'Log(FTD-Raman-II-Direct)'

    #: Model Parameter name strings
    PARNAMES = [
        'G',
        'x',
        'y'
    ]

    #: Model Parameter name mathmode strings
    VARNAMES_MM = {
        'G': '$G$',
        'x': '$x$',
        'y': '$y$'
    }

    #: Model Parameter name HTML strings
    VARNAMES_HTML = {
        'G': 'G',
        'x': 'x',
        'y': 'y'
    }

    #: Model Parameter unit strings
    UNITS = {
        'G': 'log10[Oe^-x K^-y s^-1]',
        'x': '',
        'y': ''
    }

    #: Model Parameter unit mathmode strings
    UNITS_MM = {
        'G': r'$\log_\mathregular{10}\left[\mathregular{Oe}^{-x} \ \mathregular{K}^{-y} \ \mathregular{s}^\mathregular{-1}\right]$', # noqa
        'x': '',
        'y': ''
    }

    #: Model Parameter name HTML strings
    UNITS_HTML = {
        'G': 'log<sub>10</sub>[Oe<sup>-x</sup> K<sup>-y</sup> s<sup>-1</sup>]', # noqa
        'x': '',
        'y': ''
    }

    #: Model Parameter bounds
    BOUNDS = {
        'G': [-np.inf, np.inf],
        'x': [0., np.inf],
        'y': [0., np.inf]
    }

    @staticmethod
    def set_initial_vals(param_dict: dict[str, str | float]) -> dict[str, float]: # noqa
        '''
        Sets guess values for parameters if requested by user

        Parameters
        ----------
        param_dict: dict[str, str | float]
            Keys are fit/fix parameter names (see class.PARNAMES)\n
            Values are either float (actual value) or the string 'guess'

        Returns
        -------
        dict[str, float]
            Keys are fit/fix parameter names (see class.PARNAMES)\n
            Values are float (actual value) which are initial values of
            parameter
        '''

        # Make copy, any str values will be replaced
        new_param_dict = copy.copy(param_dict)

        # Guesses
        guessdict = {
            'G': -4,
            'x': 4,
            'y': 1
        }

        # Replace 'guess' with relevant guess
        for var, val in param_dict.items():
            if isinstance(val, str) and val.lower() == 'guess':
                new_param_dict[var] = guessdict[var]

        return new_param_dict

    @staticmethod
    def model(parameters: dict[str, float],
              fields: ArrayLike,
              temperatures: ArrayLike) -> NDArray:
        '''
        Evaluates field and temperature dependent Raman-II/Direct model of\n
        log10(relaxation rate) using provided parameter, field and\n
        temperature values.

        Parameters
        ----------
        parameters: dict[str, float]
            Parameters to use in model function, keys are given in
            class.PARNAMES
        fields: array_like
            Field values (Oe) at which model function is evaluated\n
            Must have same number of entries as `temperatures` array
        temperatures: array_like
            Temperature values (K) at which model function is evaluated
            Must have same number of entries as `fields` array

        Returns
        -------
        ndarray of floats
            log10(Relaxation rate) as a function of field

        '''

        g = parameters['G']
        x = parameters['x']
        y = parameters['y']

        fields = np.asarray(fields, dtype=float)

        temperatures = np.asarray(temperatures, dtype=float)

        lograte = np.log10(10**g * fields**x * temperatures**y) # noqa

        return lograte


class LogFTDRamanIModel(LogTauHTModel):
    '''
    Field and temperature dependent Raman-I Model of log10(Relaxation rate)\n

    This model is field independent, but has been implemented here to\n
    work with the LogTauHTModel class.

    Parameters
    ----------
    fit_vars: dict[str, float]
        Parameter to fit in model function\n
        Keys are fit/fix parameter names (see class.PARNAMES)\n
        Values are either float (actual value) or the string 'guess'\n
        If 'guess' then a parameter value is guessed
    fix_vars: dict[str, float]
        Parameter which remain fixed in model function\n
        Keys are fit/fix parameter names (see class.PARNAMES)\n
        Values are either float (actual value) or the string 'guess'\n
        If 'guess' then a parameter value is guessed

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
    fit_status: bool
        True if fit successful, else false
    '''

    #: Model name
    NAME = 'FTD-Raman-I'

    #: Model name with log brackets
    LNAME = 'Log(FTD-Raman-I)'

    #: Model Parameter name strings
    PARNAMES = [
        'R', 'n',
    ]

    #: Model Parameter name mathmode strings
    VARNAMES_MM = {
        'R': r'$R$',
        'n': r'$n$'
    }

    #: Model Parameter name HTML strings
    VARNAMES_HTML = {
        'R': 'R',
        'n': 'n'
    }

    #: Model Parameter unit strings
    UNITS = {
        'R': 'log10[s^-1 K^-n]',
        'n': ''
    }

    #: Model Parameter unit mathmode strings
    UNITS_MM = {
        'R': r'$\log_\mathregular{10}\left[\mathregular{s}^\mathregular{-1} \mathregular{K}^{-n}\right]$', # noqa
        'n': ''
    }

    #: Model Parameter unit HTML strings
    UNITS_HTML = {
        'R': 'log<sub>10</sub>[s<sup>-1</sup> K<sup>-n</sup>]',
        'n': ''
    }

    #: Model parameter bounds
    BOUNDS = {
        'R': [-np.inf, np.inf],
        'n': [0, np.inf]
    }

    @staticmethod
    def set_initial_vals(param_dict: dict[str, str | float]) -> dict[str, float]: # noqa
        '''
        Sets guess values for parameters if requested by user

        Parameters
        ----------
        param_dict: dict[str, str | float]
            Keys are fit/fix parameter names (see class.PARNAMES)\n
            Values are either float (actual value) or the string 'guess'

        Returns
        -------
        dict[str, float]
            Keys are fit/fix parameter names (see class.PARNAMES)\n
            Values are float (actual value) which are initial values of
            parameter
        '''

        # Make copy, any str values will be replaced
        new_param_dict = copy.copy(param_dict)

        # Guesses
        guessdict = {
            'R': -6,
            'n': 3
        }

        # Replace 'guess' with relevant guess
        for var, val in param_dict.items():
            if isinstance(val, str) and val.lower() == 'guess':
                new_param_dict[var] = guessdict[var]

        return new_param_dict

    @staticmethod
    def model(parameters: dict[str, float],
              fields: ArrayLike,
              temperatures: ArrayLike) -> NDArray:
        '''
        Evaluates field and temperature dependent Raman-I model of\n
        log10(relaxation rate) using provided parameter and temperature\n
        values.\n

        This model is field independent, but has been implemented here to\n
        work with the LogTauHTModel class.

        Parameters
        ----------
        parameters: dict[str, float]
            Parameters to use in model function, keys are given in
            class.PARNAMES
        fields: array_like
            Field values (Oe) at which model function is evaluated.\n
            These are not used, but are provided to match function signature\n
            for the base class's model method.
        temperatures: array_like
            Temperature values (K) at which model function is evaluated

        Returns
        -------
        ndarray of floats
            log10(Relaxation rate) as a function of temperature

        '''

        r = parameters['R']
        n = parameters['n']

        temperatures = np.asarray(temperatures, dtype=float)

        lograte = np.log10(10**r * temperatures**n)

        return lograte


class LogFTDPPDRamanIModel(LogTauHTModel):
    '''
    Field and temperature dependent Phonon Pair-Driven Raman-I Model of\n
    log10(Relaxation rate).\n

    This model is field independent, but has been implemented here to\n
    work with the LogTauHTModel class.

    Parameters
    ----------
    fit_vars: dict[str, float]
        Parameter to fit in model function\n
        Keys are fit/fix parameter names (see class.PARNAMES)\n
        Values are either float (actual value) or the string 'guess'\n
        If 'guess' then a parameter value is guessed
    fix_vars: dict[str, float]
        Parameter which remain fixed in model function\n
        Keys are fit/fix parameter names (see class.PARNAMES)\n
        Values are either float (actual value) or the string 'guess'\n
        If 'guess' then a parameter value is guessed

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
    fit_status: bool
        True if fit successful, else false
    '''

    #: Model name
    NAME = 'FTD-PPDRaman-I'

    #: Model name with log brackets
    LNAME = 'Log(FTD-PPDRaman-I)'

    #: Model Parameter name strings
    PARNAMES = [
        'w',
        'R'
    ]

    #: Model Parameter name mathmode strings
    VARNAMES_MM = {
        'R': r'$R$',
        'w': r'$\omega$'
    }

    #: Model Parameter name HTML strings
    VARNAMES_HTML = {
        'R': 'R',
        'w': 'ω'
    }

    #: Model Parameter unit strings
    UNITS = {
        'R': 'log10[s^-1]',
        'w': 'K'
    }

    #: Model Parameter unit mathmode strings
    UNITS_MM = {
        'R': r'$\log_\mathregular{10}\left[\mathregular{s}^\mathregular{-1}\right]$', # noqa
        'w': r'$\mathregular{K}$'
    }

    #: Model Parameter unit HTML strings
    UNITS_HTML = {
        'R': 'log<sub>10</sub>[s<sup>-1</sup>]',
        'w': 'K'
    }

    #: Model parameter bounds
    BOUNDS = {
        'w': [0, np.inf],
        'R': [-np.inf, np.inf]
    }

    @staticmethod
    def set_initial_vals(param_dict: dict[str, str | float]) -> dict[str, float]: # noqa
        '''
        Sets guess values for parameters if requested by user

        Parameters
        ----------
        param_dict: dict[str, str | float]
            Keys are fit/fix parameter names (see class.PARNAMES)\n
            Values are either float (actual value) or the string 'guess'

        Returns
        -------
        dict[str, float]
            Keys are fit/fix parameter names (see class.PARNAMES)\n
            Values are float (actual value) which are initial values of
            parameter
        '''

        # Make copy, any str values will be replaced
        new_param_dict = copy.copy(param_dict)

        # Guesses
        guessdict = {
            'w': 10,
            'R': 4
        }

        # Replace 'guess' with relevant guess
        for var, val in param_dict.items():
            if isinstance(val, str) and val.lower() == 'guess':
                new_param_dict[var] = guessdict[var]

        return new_param_dict

    @staticmethod
    def model(parameters: dict[str, float],
              fields: ArrayLike,
              temperatures: ArrayLike) -> NDArray:
        '''
        Evaluates field and temperature dependent Phonon Pair-Driven Raman-I\n
        model of log10(relaxation rate) using provided parameter and\n
        temperature values.\n

        This model is field independent, but has been implemented here to\n
        work with the LogTauHTModel class.

        Parameters
        ----------
        parameters: dict[str, float]
            Parameters to use in model function, keys are given in
            class.PARNAMES
        fields: array_like
            Field values (Oe) at which model function is evaluated.\n
            These are not used, but are provided to match function signature\n
            for the base class's model method.
        temperatures: array_like
            Temperature values (K) at which model function is evaluated

        Returns
        -------
        ndarray of floats
            log10(Relaxation rate) as a function of temperature

        '''

        omega = parameters['w']
        R = parameters['R']

        temperatures = np.asarray(temperatures, dtype=float)

        num = np.exp(omega / temperatures)
        denom = (np.exp(omega / temperatures) - 1)**2
        coeff = 10**R

        lograte = np.log10(coeff * (num / denom))

        return lograte


class LogFTDBVVRamanIModel(LogTauHTModel):
    '''
    Field and temperature dependent Brons-Van-Vleck Raman-I Model of
    log10(Relaxation rate)\n

    This includes additional field-dependent variables in the Raman-I Model.

    Parameters
    ----------
    fit_vars: dict[str, float]
        Parameter to fit in model function\n
        Keys are fit/fix parameter names (see class.PARNAMES)\n
        Values are either float (actual value) or the string 'guess'\n
        If 'guess' then a parameter value is guessed
    fix_vars: dict[str, float]
        Parameter which remain fixed in model function\n
        Keys are fit/fix parameter names (see class.PARNAMES)\n
        Values are either float (actual value) or the string 'guess'\n
        If 'guess' then a parameter value is guessed

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
    fit_status: bool
        True if fit successful, else false
    '''

    #: Model name
    NAME = 'FTD-Brons-Van-Vleck-Raman-I'

    #: Model name with log brackets
    LNAME = 'Log(FTD-Brons-Van-Vleck-Raman-I)'

    #: Model Parameter name strings
    PARNAMES = [
        'R', 'n', 'e', 'f'
    ]

    #: Model Parameter name mathmode strings
    VARNAMES_MM = {
        'R': r'$R$',
        'n': r'$n$',
        'e': r'$e$',
        'f': r'$f$'
    }

    #: Model Parameter name HTML strings
    VARNAMES_HTML = {
        'R': 'R',
        'n': 'n',
        'e': 'e',
        'f': 'f'
    }

    #: Model Parameter unit strings
    UNITS = {
        'R': 'log10[s^-1 K^-n]',
        'n': '',
        'e': 'log10[Oe^-2]',
        'f': 'log10[Oe^-2]'
    }

    #: Model Parameter unit mathmode strings
    UNITS_MM = {
        'R': r'$\log_\mathregular{10}\left[\mathregular{s}^\mathregular{-1} \mathregular{K}^{-n}\right]$', # noqa
        'n': '',
        'e': r'$\log_\mathregular{10}\left[\mathregular{Oe}^\mathregular{-2}\right]$', # noqa
        'f': r'$\log_\mathregular{10}\left[\mathregular{Oe}^\mathregular{-2}\right]$' # noqa
    }

    #: Model Parameter unit HTML strings
    UNITS_HTML = {
        'R': 'log<sub>10</sub>[s<sup>-1</sup> K<sup>-n</sup>]',
        'n': '',
        'e': 'log<sub>10</sub>[Oe<sup>-2</sup>]',
        'f': 'log<sub>10</sub>[Oe<sup>-2</sup>]'
    }

    #: Model parameter bounds
    BOUNDS = {
        'R': [-np.inf, np.inf],
        'n': [0, np.inf],
        'e': [-np.inf, np.inf],
        'f': [-np.inf, np.inf]
    }

    @staticmethod
    def set_initial_vals(param_dict: dict[str, str | float]) -> dict[str, float]: # noqa
        '''
        Sets guess values for parameters if requested by user

        Parameters
        ----------
        param_dict: dict[str, str | float]
            Keys are fit/fix parameter names (see class.PARNAMES)\n
            Values are either float (actual value) or the string 'guess'

        Returns
        -------
        dict[str, float]
            Keys are fit/fix parameter names (see class.PARNAMES)\n
            Values are float (actual value) which are initial values of
            parameter
        '''

        # Make copy, any str values will be replaced
        new_param_dict = copy.copy(param_dict)

        # Guesses
        guessdict = {
            'R': -6,
            'n': 3,
            'e': -5.,
            'f': -5.
        }

        # Replace 'guess' with relevant guess
        for var, val in param_dict.items():
            if isinstance(val, str) and val.lower() == 'guess':
                new_param_dict[var] = guessdict[var]

        return new_param_dict

    @staticmethod
    def model(parameters: dict[str, float],
              fields: ArrayLike,
              temperatures: ArrayLike) -> NDArray:
        '''
        Evaluates field and temperature dependent Brons-Van-Vleck Raman-I\n
        model of log10(relaxation rate) using provided parameter and
        temperature values.\n

        Parameters
        ----------
        parameters: dict[str, float]
            Parameters to use in model function, keys are given in
            class.PARNAMES
        fields: array_like
            Field values (Oe) at which model function is evaluated.\n
            These are not used, but are provided to match function signature\n
            for the base class's model method.
        temperatures: array_like
            Temperature values (K) at which model function is evaluated

        Returns
        -------
        ndarray of floats
            log10(Relaxation rate) as a function of temperature

        '''

        r = parameters['R']
        n = parameters['n']
        e = parameters['e']
        f = parameters['f']

        fields = np.asarray(fields, dtype=float)
        temperatures = np.asarray(temperatures, dtype=float)

        lograte = np.log10(
            10**r * temperatures**n * (1 + 10**e * fields**2) / (1 + 10**f * fields**2) # noqa
        )

        return lograte


class FitWindow(QtWidgets.QMainWindow):
    '''
    Interactive Fit Window for rate vs temperature/field data fitting
    '''

    def __init__(self, dataset: TDataset | HDataset, usel: object,
                 supported_models: list[LogTauTModel | LogTauHModel],
                 widget_defaults: dict[str, dict[str, float]] = gui.widget_defaults, # noqa
                 *args, **kwargs):

        super(FitWindow, self).__init__(*args, **kwargs)

        # Add shortcut to press q to quit
        self.exit_shortcut = QtWidgets.QShortcut(QtGui.QKeySequence('q'), self)
        self.exit_shortcut.activated.connect(
            lambda: self.close()
        )

        self.setWindowTitle('Interactive Relaxation Profile')

        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setStyleSheet(
            '''
            QMainWindow {
                background-color: white
            }

            QCheckBox {
                spacing: 5px;
                font-size:15px;
            }
            QSlider::groove:horizontal {
            border: 1px solid #bbb;
            background: white;
            height: 10px;
            border-radius: 4px;
            }

            QSlider::sub-page:horizontal {
            background: qlineargradient(x1: 0, y1: 0,    x2: 0, y2: 1,
                stop: 0 #66e, stop: 1 #bbf);
            background: qlineargradient(x1: 0, y1: 0.2, x2: 1, y2: 1,
                stop: 0 #bbf, stop: 1 #55f);
            border: 1px solid #777;
            height: 10px;
            border-radius: 4px;
            }

            QSlider::add-page:horizontal {
            background: #fff;
            border: 1px solid #777;
            height: 10px;
            border-radius: 4px;
            }

            QSlider::handle:horizontal {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 #eee, stop:1 #ccc);
            border: 1px solid #777;
            width: 13px;
            margin-top: -2px;
            margin-bottom: -2px;
            border-radius: 4px;
            }

            QSlider::handle:horizontal:hover {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 #fff, stop:1 #ddd);
            border: 1px solid #444;
            border-radius: 4px;
            }

            QSlider::sub-page:horizontal:disabled {
            background: #bbb;
            border-color: #999;
            }

            QSlider::add-page:horizontal:disabled {
            background: #eee;
            border-color: #999;
            }

            QSlider::handle:horizontal:disabled {
            background: #eee;
            border: 1px solid #aaa;
            border-radius: 4px;
            }
            '''
        )

        # Store dataset
        self.dataset = dataset

        # Set default min, max, init, and step values of sliders and text boxes
        self.defaults = widget_defaults

        # Dictionary for tickbox widgets
        self.tickdict = {
            model.NAME.lower(): None
            for model in supported_models
        }

        # Dictionary for parameter slider, entry, and fitfix widgets
        self.widgetdict = {
            model.NAME.lower(): {
                parname: {
                    'slider': None,
                    'ff_toggle': None,
                    'entry': None
                }
                for parname in model.PARNAMES
            }
            for model in supported_models
        }

        # Minimum Window size
        self.setMinimumSize(QtCore.QSize(1250, 700))

        # Make widgets for entire window
        self.widget = QtWidgets.QWidget(parent=self)
        self.setCentralWidget(self.widget)
        bot_row_widget = QtWidgets.QWidget(self.widget)
        top_row_widget = QtWidgets.QWidget(self.widget)
        rhs_col_widget = QtWidgets.QWidget(top_row_widget)

        rhs_col_scroll = QtWidgets.QScrollArea(rhs_col_widget)
        rhs_col_scroll.setVerticalScrollBarPolicy(
            QtCore.Qt.ScrollBarAlwaysOn
        )
        rhs_col_scroll.setHorizontalScrollBarPolicy(
            QtCore.Qt.ScrollBarAlwaysOff
        )
        rhs_col_scroll.setWidgetResizable(True)

        scroll_container = QtWidgets.QWidget(rhs_col_scroll)
        rhs_col_scroll.setWidget(scroll_container)

        lhs_col_widget = QtWidgets.QWidget(top_row_widget)

        # LHS column - plot only
        lhs_col_layout = QtWidgets.QVBoxLayout(lhs_col_widget)

        # Create pgfplots plot widget
        self.plot_widget = pg.PlotWidget(
            parent=lhs_col_widget
        )
        # Add plot to left column
        lhs_col_layout.addWidget(self.plot_widget)

        # Set loglog axes
        self.plot_widget.setLogMode(True, True)

        # Set white plot background
        self.plot_widget.setBackground('w')

        # Select either field or temperature as x data based on dataset type
        # and set x label of plot
        if isinstance(dataset, HDataset):
            self.exp_xvals = copy.copy(np.asarray(dataset.fields))
            # Shift all data to become defined in log10 space
            # This shift must only be applied when plotting, not
            # when calculating the values of the function
            if any(val < np.finfo(float).eps for val in self.exp_xvals):
                self.logshift = 1.
            else:
                self.logshift = 0.
            self.exp_xvals += self.logshift
            self.plot_widget.setLabel('bottom', 'Field (Oe)')

        elif isinstance(dataset, TDataset):
            self.logshift = 0.
            self.exp_xvals = copy.copy(
                np.asarray(dataset.temperatures, dtype=float)
            )
            self.plot_widget.setLabel('bottom', 'Temperature (K)')
        else:
            raise ValueError('Dataset Type is Unsupported')
        # Experimental rates
        self.exp_rates = np.asarray(dataset.rates, dtype=float)

        # Experimental data
        self.exp = self.plot_widget.plot(
            np.array(self.exp_xvals),
            np.array(self.exp_rates),
            pen=None,
            symbol='x',
            symbolBrush=(0, 0, 0)
        )

        # Find nice y-axis limits
        y_lower, y_upper = gui.calc_y_rate_lims(
            self.exp_rates,
            np.array(dataset.rate_pm)
        )

        # Clip them at sensible values
        [y_lower, y_upper] = np.clip([y_lower, y_upper], 1E-10, 1E10)

        # and set values
        self.plot_widget.setYRange(
            np.log10(y_lower),
            np.log10(y_upper),
            padding=0
        )

        # Add experimental errorbars
        if len(dataset.lograte_pm):
            err = pg.ErrorBarItem(
                x=np.log10(self.exp_xvals),
                y=np.log10(self.exp_rates),
                top=dataset.lograte_pm,
                bottom=dataset.lograte_pm,
                beam=0.005
            )
            self.plot_widget.addItem(err)

        # Axis labels
        self.plot_widget.setLabel('left', 'Rate (s<sup>-1</sup>)')

        # Set dictionary of True (fit) and False (fix) for each
        # parameter of all available models
        usel.fit = {
            parname: True
            for model in supported_models
            for parname in model.PARNAMES
        }

        # Set user selection object and supported models
        self.usel = usel
        self.supported_models = supported_models

        # Calculate each model function and plot
        # Note if shift is applied then these values
        # must be the true x variables as they will be used to compute
        # the model values
        self.x_grid = np.linspace(
            np.min(self.exp_xvals - self.logshift),
            np.max(self.exp_xvals - self.logshift),
            1000
        )

        # Sum of all models, set to zero initially
        total_rates = np.zeros(np.shape(self.x_grid))

        # Dictionary of plots
        # keys are model.NAME.lower(), values are plot_widget.plot
        self.model_plots = {}

        # List of nice colors
        colors = mcolors.TABLEAU_COLORS.values()

        # Loop over all possible models, calculate model values
        # at range of temperatures and plot
        # then add to array of total rates
        for color, model in zip(colors, supported_models):

            # Get initial values
            initials = model.set_initial_vals(
                {
                    par: self.defaults[model.NAME][par]['valinit']
                    for par in model.PARNAMES
                }
            )
            # Calculate rates
            rates = 10**(model.model(initials, self.x_grid))
            # and add to total of all models
            total_rates += rates
            # Plot this model
            _plot = self.plot_widget.plot(
                self.x_grid + self.logshift,
                rates,
                pen={'width': 2.5, 'color': color, 'style': QtCore.Qt.DashLine}
            )
            # and store in dict of all plots
            self.model_plots[model.NAME.lower()] = _plot
            # Remove from actual plot widget
            # since no models are visible initially
            # Plots are re-added with model checkboxes
            self.plot_widget.removeItem(_plot)

        # Calculate initial value of on-screen residual
        self.residual_value = 0.

        # Plot sum of all models
        self.tot = self.plot_widget.plot(
            self.x_grid + self.logshift,
            total_rates,
            pen={'width': 2.5, 'color': 'red'}
        )
        self.plot_widget.removeItem(self.tot)

        # Storage object for final parameter values
        # Set all initial values defaults
        self.parstore = type(
            'obj',
            (object,),
            {
                par: self.defaults[model.NAME][par]['valinit']
                for model in supported_models
                for par in model.PARNAMES
            }
        )

        # Convert log temperature ticks to linear
        ax = self.plot_widget.getAxis('bottom')
        gui.convert_log_ticks_to_lin(
            ax, np.log10(self.exp_xvals), shift=self.logshift
        )

        # RHS column of window
        # This contains each model and its associated parameters
        # Each parameter is controlled by a
        # sliders, Text entry, and a fit/fix toggle
        container_layout = QtWidgets.QVBoxLayout(scroll_container)

        # List of number key shortcuts to toggle models
        self.on_off_shortcut = []

        # For each model, make a box to contain all parameters
        # and populate with parameters

        for mit, model in enumerate(supported_models):
            model_widget = self.make_modelbox(
                model,
                scroll_container,
                mit + 1
            )

            # Add this model to the right hand side of the window
            container_layout.addWidget(model_widget, len(model.PARNAMES))

        # Disable every slider, entry, and fit/fix by default
        # This is toggled by the model checkboxes
        for model in supported_models:
            modelname = model.NAME.lower()
            for parname in model.PARNAMES:
                self.widgetdict[modelname][parname]['slider'].setEnabled(False)
                self.widgetdict[modelname][parname]['entry'].setEnabled(False)
                self.widgetdict[modelname][parname]['ff_toggle'].setEnabled(
                    False
                )

        container_layout.setAlignment(QtCore.Qt.AlignVCenter)
        scroll_container.setSizePolicy(
            QtWidgets.QSizePolicy.Maximum,
            QtWidgets.QSizePolicy.Maximum
        )
        rhs_col_scroll.setMinimumHeight(575)

        # Top row
        # LHS plot, RHS Sliders, text, labels
        top_row_layout = QtWidgets.QHBoxLayout(top_row_widget)
        top_row_layout.addWidget(lhs_col_widget, 3)
        top_row_layout.addWidget(rhs_col_widget, 2)

        # Bottom row

        # Residual read-out widget
        self.residual_widget = QtWidgets.QLabel(
            parent=bot_row_widget,
            text=f'Residual = {self.residual_value:.5f}'
        )

        # Residual read-out widget
        self.fit_status_widget = QtWidgets.QLabel(
            parent=bot_row_widget
        )
        self.fit_status_widget.setAlignment(QtCore.Qt.AlignCenter)
        self.set_fit_status('ready')

        # Finalise button
        self.finalise_btn_widget = QtWidgets.QPushButton(
            parent=bot_row_widget,
            text='Finalise'
        )
        self.finalise_btn_widget.setStyleSheet('font-weight: bold;')

        self.finalise_btn_widget.setEnabled(False)
        self.finalise_btn_widget.clicked.connect(self.finalise)
        self.finalise_btn_widget.setSizePolicy(
            QtWidgets.QSizePolicy.Fixed,
            QtWidgets.QSizePolicy.Fixed
        )

        # Fit button
        self.fit_btn_widget = QtWidgets.QPushButton(
            parent=bot_row_widget,
            text='Update Fit'
        )
        self.fit_btn_widget.setStyleSheet('font-weight: bold;')

        self.fit_btn_widget.setEnabled(False)
        self.fit_btn_widget.clicked.connect(self.update_fit)
        self.fit_btn_widget.setSizePolicy(
            QtWidgets.QSizePolicy.Fixed,
            QtWidgets.QSizePolicy.Fixed
        )

        # Reset Button
        reset_btn_widget = QtWidgets.QPushButton(
            parent=bot_row_widget,
            text='Reset',
        )
        reset_btn_widget.setStyleSheet('font-weight: bold;')
        reset_btn_widget.clicked.connect(self.reset)
        reset_btn_widget.setSizePolicy(
            QtWidgets.QSizePolicy.Fixed,
            QtWidgets.QSizePolicy.Fixed
        )

        # Modify fit and reset button text colors to look good even
        # in MacOS darkmode.
        palette = QtGui.QPalette(self.finalise_btn_widget.palette())
        palette.setColor(QtGui.QPalette.ButtonText, QtGui.QColor('#0db273'))
        self.finalise_btn_widget.setPalette(palette)
        self.fit_btn_widget.setPalette(palette)
        palette.setColor(QtGui.QPalette.ButtonText, QtGui.QColor('#4b6aad'))
        reset_btn_widget.setPalette(palette)

        # Keyboard shortcut, press f to fit if button not greyed out
        self.fit_shortcut = QtWidgets.QShortcut(
            QtGui.QKeySequence('f'), self
        )
        self.fit_shortcut.activated.connect(
            lambda: self.keyboard_fit_shortcut()
        )

        # Keyboard shortcut, press ctrl+f to finalise if button not greyed out
        self.finalise_shortcut = QtWidgets.QShortcut(
            QtGui.QKeySequence('Ctrl+F'), self
        )
        self.finalise_shortcut.activated.connect(
            lambda: self.keyboard_finalise_shortcut()
        )

        bot_row_layout = QtWidgets.QHBoxLayout(bot_row_widget)
        bot_row_layout.addWidget(self.residual_widget)
        bot_row_layout.addWidget(self.fit_status_widget)
        bot_row_layout.addWidget(self.finalise_btn_widget)
        bot_row_layout.addWidget(self.fit_btn_widget)
        bot_row_layout.addWidget(reset_btn_widget)

        # Overall app
        # Top and Bottom rows
        full_layout = QtWidgets.QVBoxLayout(self.widget)
        full_layout.addWidget(top_row_widget)
        full_layout.addWidget(bot_row_widget)

        # Set layout
        self.widget.setLayout(full_layout)
        self.widget.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Expanding
        )

        return

    def keyboard_fit_shortcut(self):
        '''
        Callback for pressing 'f' key.\n
        Runs fit button if not greyed out
        '''

        # Check finalise button is not greyed out
        if self.fit_btn_widget.isEnabled():
            # Run finalise code, this closes app
            self.update_fit()

        return

    def keyboard_finalise_shortcut(self):
        '''
        Callback for pressing 'ctrl+f' key.
        \nRuns finalise button if not greyed out
        '''

        # Check finalise button is not greyed out
        if self.finalise_btn_widget.isEnabled():
            # Run finalise code, this closes app
            self.finalise()

        return

    def set_fit_status(self, status: str) -> None:
        '''
        Sets color and text of fit status widget

        Parameters
        ----------
        status: str
            'ready', 'successful', 'failed'

        Returns
        -------
        None
        '''

        if status == 'ready':
            color = 'white'
            self.fit_status_widget.setText('Ready')
        elif status == 'successful':
            color = 'green'
            self.fit_status_widget.setText('Fit Successful')
        elif status == 'failed':
            color = 'red'
            self.fit_status_widget.setText('Fit Failed')

        stylesheet = '''
            QLabel {
                border: 1px solid black;
                border-radius: 10px;
                padding: 5px;
            '''
        stylesheet += f'\nbackground-color: {color};'
        stylesheet += '\n}'

        self.fit_status_widget.setStyleSheet(stylesheet)

        # Get the font metrics for the label's font
        font_metrics = QtGui.QFontMetrics(self.fit_status_widget.font())
        # Calculate the width of the text
        text_width = font_metrics.horizontalAdvance(
            self.fit_status_widget.text()
        )

        # Set the QLabel's width to the text width
        self.fit_status_widget.setFixedWidth(int(text_width*1.5))

        return

    def reset(self):
        '''
        Callback for Reset button.
        Returns window back to original layout/selections
        '''

        self.set_fit_status('ready')

        # For each model, remove plot, and reset parameter values
        for model in self.supported_models:
            modelname = model.NAME.lower()

            # Disable all models
            self.usel.models[modelname] = False

            # and untick checkboxes
            self.tickdict[modelname].setCheckState(QtCore.Qt.CheckState(False))

            # Remove corresponding plot
            _plot = self.model_plots[modelname]
            self.plot_widget.removeItem(_plot)

            # Reset each parameter slider, entry, and fitfix
            # back to original value
            for parname in model.PARNAMES:
                setattr(
                    self.parstore,
                    parname,
                    self.defaults[model.NAME][parname]['valinit']
                )
                self.widgetdict[modelname][parname]['slider'].setValue(
                    int(self.defaults[model.NAME][parname]['valinit'])
                )
                self.widgetdict[modelname][parname]['entry'].setValue(
                    self.defaults[model.NAME][parname]['valinit']
                )
                self.widgetdict[modelname][parname]['ff_toggle'].setText(
                    'Free'
                )

        # Remove total model plot
        self.plot_widget.removeItem(self.tot)

        return

    def update_fit(self):
        '''
        Callback for update fit button.
        Collects variable values of each model and assembles into fit/fix
        dictionaries, then fits, and updates values on screen.
        '''

        lname_to_model = {
            model.NAME.lower(): model
            for model in self.supported_models
        }

        # Collect variables of each model, if that model is enabled
        # and assign to fit or fix
        _models = []
        _fit_vars = []
        _fix_vars = []
        for modelname, enabled in self.usel.models.items():
            _fit = dict()
            _fix = dict()
            if enabled:
                _models.append(lname_to_model[modelname])
                for name in lname_to_model[modelname].PARNAMES:
                    if self.usel.fit[name]:
                        _fit[name] = getattr(self.parstore, name)
                    else:
                        _fix[name] = getattr(self.parstore, name)
                _fit_vars.append(_fit)
                _fix_vars.append(_fix)

        # Create models
        if isinstance(self.dataset, TDataset):
            _multilogmodel_class = MultiLogTauTModel
        elif isinstance(self.dataset, HDataset):
            _multilogmodel_class = MultiLogTauHModel

        # Perform fit
        # Create MultiLogModel as combination of individual models
        _multilogmodel = _multilogmodel_class(
            _models,
            _fit_vars,
            _fix_vars
        )

        # Fit models to experiment
        _multilogmodel.fit_to(self.dataset, verbose=False)

        if not _multilogmodel.fit_status:
            self.set_fit_status('failed')
            return
        else:
            self.set_fit_status('successful')

        # For each model, update parameter values on screen
        for model in _multilogmodel.logmodels:

            # Set sliders and text boxes to fitted values
            for parname in model.PARNAMES:
                setattr(
                    self.parstore,
                    parname,
                    _multilogmodel.final_var_values[parname]
                )
                self.widgetdict[model.NAME.lower()][parname]['slider'].setValue( # noqa
                    int(_multilogmodel.final_var_values[parname])
                )
                self.widgetdict[model.NAME.lower()][parname]['entry'].setValue( # noqa
                    _multilogmodel.final_var_values[parname]
                )

        return

    def finalise(self):
        '''
        Callback for Finalise button.
        Collects variable values of each model and assembles into fit/fix
        dictionaries, then closes the window.
        '''

        lname_to_model = {
            model.NAME.lower(): model
            for model in self.supported_models
        }

        # Collect variables of each model, if that model is enabled
        # and assign to fit or fix
        for modelname, enabled in self.usel.models.items():
            _fit_vars = dict()
            _fix_vars = dict()
            if enabled:
                model = lname_to_model[modelname]
                for name in model.PARNAMES:
                    if self.usel.fit[name]:
                        _fit_vars[name] = getattr(self.parstore, name)
                    else:
                        _fix_vars[name] = getattr(self.parstore, name)

                self.usel.fit_vars.append(_fit_vars)
                self.usel.fix_vars.append(_fix_vars)

        # Set 'has program been exited' flag to false
        self.usel.exited = False

        # Close the window
        self.close()

        return

    def update_modelplot(self, value: float, parname: str,
                         model: LogTauTModel | LogTauHModel):
        '''
        Updates model plots using new parameter values

        Parameters
        ----------
        value: float
            New value of parameters
        parname: str
            Name of parameter (from model.PARNAMES)
        model: LogTauTModel | LogTauHModel
            Model to which this parameter belongs

        Returns
        -------
        None
        '''

        # Set new parameter value
        setattr(self.parstore, parname, float(value))
        parameters = model.set_initial_vals(
            {
                parname: getattr(self.parstore, parname)
                for parname in model.PARNAMES
            }
        )

        # Recalculate rates for this model
        new_rates = 10**model.model(parameters, self.x_grid)

        # and update model plot data
        _plot = self.model_plots[model.NAME.lower()]
        _plot.setData(self.x_grid + self.logshift, new_rates)

        # Update total plot (sum of all models)
        # Sum ydata of each selected model
        total_rates = np.zeros(self.x_grid.shape)

        # and add to total of all models
        total_rates += np.sum(
            [
                _plot.yData
                for name, _plot in self.model_plots.items()
                if self.usel.models[name]
            ],
            axis=0
        )
        self.tot.setData(self.x_grid + self.logshift, total_rates)

        # Update residual value
        self.residual_value = self.calculate_residual_value()
        self.residual_widget.setText(f'Residual = {self.residual_value:.5f}')

        return

    def calculate_residual_value(self) -> float:
        '''
        Calculates value for on-screen residual using current selected models
        and their parameter values

        Returns
        -------
        float
            Residual sum of squares.
            Defined as sum((log10(exp) - log10(calc))**2)
        '''

        # Calculate rates at experimental value
        _lograte_at_exp = np.zeros(len(self.exp_xvals))

        n_parameters = 0

        # Loop over all available models
        for model in self.supported_models:
            # Include only models which have been selected
            if self.usel.models[model.NAME.lower()]:
                parameters = model.set_initial_vals(
                    {
                        parname: getattr(self.parstore, parname)
                        for parname in model.PARNAMES
                    }
                )
                _lograte_at_exp += 10**model.model(parameters, self.exp_xvals)
                n_parameters += len(parameters)

        if n_parameters == 0:
            rss = 0.
        else:
            rss = np.sum(
                (
                    np.log10(self.exp_rates) - np.log10(_lograte_at_exp)
                )**2
            )

        return rss

    def toggle_plot(self, val: int,
                    model: LogTauTModel | LogTauHModel) -> None:
        '''
        Callback for toggling model checkboxes

        Calculates model data, adds/deletes line from plot, updates total model
        plot, and recalculates residual value

        Parameters
        ----------
        val: int {0, 2}
            Value returned by tickbox widget, specifies off / on
        model: LogTauTModel | LogTauHModel
            Model which is being toggled

        Returns
        -------
        None
        '''

        # Reset fit status widget to ready
        self.set_fit_status('ready')

        # Convert val (0 or 2) to bool
        val = bool(val / 2)

        modelname = model.NAME.lower()

        # Update list of models
        self.usel.models[modelname] = val
        # Update model values and plot data for each model, and for total
        for parname in model.PARNAMES:
            self.update_modelplot(
                getattr(self.parstore, parname),
                parname,
                model
            )

        # Select model plot to toggle
        _plot = self.model_plots[modelname]

        # Add back in plot
        if val:
            self.plot_widget.removeItem(_plot)
            self.plot_widget.addItem(_plot)
        else:
            self.plot_widget.removeItem(_plot)

        # Enable total plot if > 1 model
        # and enable Finalise and Fit buttons if > 0 models
        n_models = np.sum([val for val in self.usel.models.values()])
        if n_models == 0:
            self.fit_btn_widget.setEnabled(False)
            self.finalise_btn_widget.setEnabled(False)
        elif n_models == 1:
            self.fit_btn_widget.setEnabled(True)
            self.finalise_btn_widget.setEnabled(True)
            self.plot_widget.removeItem(self.tot)
        else:
            self.fit_btn_widget.setEnabled(True)
            self.finalise_btn_widget.setEnabled(True)
            self.plot_widget.removeItem(self.tot)
            self.plot_widget.addItem(self.tot)

        # Enable/Disable slider, checkbox, and fitfix
        for parname in model.PARNAMES:
            self.widgetdict[modelname][parname]['slider'].setEnabled(val)
            self.widgetdict[modelname][parname]['entry'].setEnabled(val)
            self.widgetdict[modelname][parname]['ff_toggle'].setEnabled(val)

        # Update residual value
        self.residual_value = self.calculate_residual_value()
        self.residual_widget.setText(f'Residual = {self.residual_value:.5f}')

        return

    def make_modelbox(self, model: LogTauTModel | LogTauHModel,
                      parent: QtWidgets.QWidget,
                      num_key: int) -> QtWidgets.QWidget:
        '''
        Creates widget for a given model, containing a checkbox to toggle
        the model, and a row of interactive widgets for each parameter of the
        model.

        Parameters
        ----------
        model: LogTauTModel | LogTauHModel
            Model for which a widget is made
        parent: QtWidgets.QWidget
            Parent widget for this model widget
        num_key: int
            Integer specifying which num_key will toggle this model on and off

        Returns
        -------
        QtWidgets.QWidget
            Widget for this model
        '''

        # Widget for this model
        model_widget = QtWidgets.QWidget(parent=parent)
        model_layout = QtWidgets.QHBoxLayout(model_widget)

        # Create tickbox to toggle this widget
        tickbox_widget = QtWidgets.QCheckBox(
            parent=model_widget,
            text=model.NAME.replace('Brons-Van-Vleck', 'BVV')
        )

        # Add tickbox to this model
        model_layout.addWidget(tickbox_widget)

        # Add to dictionary of all tickboxes, indexed by model.NAME.lower()
        self.tickdict[model.NAME.lower()] = tickbox_widget

        # When toggled, plot this model
        tickbox_widget.stateChanged.connect(
            lambda val: self.toggle_plot(val, model)
        )

        # Add ability to toggle model using number key
        on_off_shortcut = QtWidgets.QShortcut(
            QtGui.QKeySequence('{:d}'.format(num_key)),
            self
        )
        on_off_shortcut.activated.connect(
            lambda: tickbox_widget.toggle()
        )
        self.on_off_shortcut.append(on_off_shortcut)

        # Create container widget for all parameter rows
        rhs_widget = QtWidgets.QWidget(parent=model_widget)
        rhs_layout = QtWidgets.QVBoxLayout(rhs_widget)

        # Make slider, textbox, and fit/fix toggle for each
        # parameter of the current model
        for parname in model.PARNAMES:

            # Default parameter values
            _defaults = self.defaults[model.NAME][parname]

            # Name and Units as string
            _nu_string = '{} ({})'.format(
                model.VARNAMES_HTML[parname],
                model.UNITS_HTML[parname]
            ).replace('()', '')

            # Callback for interaction with slider, textbox...
            cb = partial(
                self.update_modelplot,
                model=model,
                parname=parname
            )

            # Make row of widgets for this parameter
            parbox_widget, parbox_layout = self.make_parbox(
                cb, parname, _nu_string, _defaults, model_widget,
                model.NAME.lower()
            )

            # and add to the model's box of parameter
            rhs_layout.addWidget(parbox_widget)

        # Set expansion behaviour and centering of widgets
        rhs_layout.setAlignment(QtCore.Qt.AlignVCenter)
        rhs_widget.setSizePolicy(
            QtWidgets.QSizePolicy.Fixed,
            QtWidgets.QSizePolicy.Fixed
        )
        tickbox_widget.setSizePolicy(
            QtWidgets.QSizePolicy.Fixed,
            QtWidgets.QSizePolicy.Fixed
        )

        rhs_layout.setSpacing(0)
        rhs_layout.addStretch(4)

        # Add parameter rows to this model
        model_layout.addWidget(rhs_widget)

        # and set alignment of the model
        model_layout.setAlignment(QtCore.Qt.AlignTop)

        return model_widget

    def not_ify(self, parname: str):
        '''
        Switches fit dictionary entry True <--> False
        for the provided parname
        '''
        self.usel.fit[parname] = not self.usel.fit[parname]

    def make_parbox(self, cb: partial, parname: str, _nu_string: str,
                    defaults: dict[str, float], op_par: QtWidgets.QWidget,
                    modelname: str):
        '''
        Creates set of widgets for a single parameter of a model.\n
        Contains 2 rows, upper is label and units as string, and lower
        is slider, textentry (doublespinbox), and fit/fix toggle button.

        Parameters
        ----------
        cb: functools.partial
            Partial-ly instantiated callback which will be fired when
            widgets of this parameter are interacted with.
        parname: str
            String name of parameter used as key in
            self.widgetdict[widgetdict]
        _nu_string: str
            String name of parameter and units used as title of this parameter
        defaults: dict[str, float]
            Default values of this parameter, keys are min, max, valinit, step
        op_par: QtWidgets.QWidget
            Parent widget
        modelname: str
            String name of model used as key in self.widgetdict
        '''

        # Widget for this parameter's row of widgets
        one_param_widget = QtWidgets.QWidget(parent=op_par)
        one_param_layout = QtWidgets.QVBoxLayout(one_param_widget)

        # For label and units
        top_boxwidget = QtWidgets.QWidget(parent=one_param_widget)
        top_boxlayout = QtWidgets.QHBoxLayout(top_boxwidget)

        # For interactive widgets
        bot_boxwidget = QtWidgets.QWidget(parent=one_param_widget)
        bot_boxlayout = QtWidgets.QHBoxLayout(bot_boxwidget)

        # Add label and units
        name_units = QtWidgets.QLabel(_nu_string)
        name_units.setFont(QtGui.QFont('Arial', 11))

        name_units.setSizePolicy(
            QtWidgets.QSizePolicy.Fixed,
            QtWidgets.QSizePolicy.Fixed
        )

        top_boxlayout.addWidget(name_units)

        # Create slider
        slider = QtWidgets.QSlider(
            orientation=QtCore.Qt.Horizontal,
            parent=bot_boxwidget
        )

        # Scale all slider numbers by this to make into floats
        slider_scale = 1E5

        slider.setMinimum(int(defaults['min'] * slider_scale))
        slider.setMaximum(int(defaults['max'] * slider_scale))
        slider.setValue(int(defaults['valinit'] * slider_scale))
        slider.setSingleStep(int(defaults['step'] * slider_scale))

        self.widgetdict[modelname.lower()][parname]['slider'] = slider

        # Add slider to layout
        bot_boxlayout.addWidget(slider)

        # Create text entry (DoubleSpinBox)
        entry = QtWidgets.QDoubleSpinBox(parent=bot_boxwidget)
        entry.setDecimals(int(defaults['decimals']))
        entry.setButtonSymbols(QtWidgets.QDoubleSpinBox.NoButtons)
        entry.setKeyboardTracking(False)
        entry.setMinimum(defaults['min'])
        entry.setMaximum(defaults['max'])
        entry.setValue(defaults['valinit'])
        entry.setSingleStep(defaults['step'])

        self.widgetdict[modelname.lower()][parname]['entry'] = entry

        # Add doublespinbox to layout
        bot_boxlayout.addWidget(entry)

        # Create fit/fix toggle button
        ff_toggle = QtWidgets.QPushButton('Free', parent=bot_boxwidget)

        self.widgetdict[modelname.lower()][parname]['ff_toggle'] = ff_toggle

        ffsw = {
            'Free': 'Fixed',
            'Fixed': 'Free',
        }

        # Callback for text
        ff_toggle.clicked.connect(
            lambda _: ff_toggle.setText(ffsw[ff_toggle.text()])
        )

        # Callback for fit/fix of this parameter
        ff_toggle.clicked.connect(
            lambda _: self.not_ify(parname)
        )

        # Connect fit/fix to slider and textentry
        slider.valueChanged.connect(lambda val: cb(val * slider_scale**-1))
        slider.valueChanged.connect(
            lambda val: entry.setValue(val * slider_scale**-1)
        )
        entry.valueChanged.connect(cb)
        entry.valueChanged.connect(
            lambda val: slider.setValue(int(val * slider_scale))
        )

        # Add fit/fix to layout
        bot_boxlayout.addWidget(ff_toggle)

        top_boxwidget.setSizePolicy(
            QtWidgets.QSizePolicy.Fixed,
            QtWidgets.QSizePolicy.Fixed
        )
        bot_boxwidget.setSizePolicy(
            QtWidgets.QSizePolicy.Fixed,
            QtWidgets.QSizePolicy.Fixed
        )
        top_boxlayout.setAlignment(QtCore.Qt.AlignHCenter)

        one_param_layout.addWidget(top_boxwidget)
        one_param_layout.addWidget(bot_boxwidget)

        one_param_layout.setContentsMargins(0, 0, 0, 0)
        one_param_layout.setSpacing(2)
        one_param_layout.addStretch(1)
        one_param_layout.setAlignment(QtCore.Qt.AlignVCenter)

        return one_param_widget, one_param_layout


def interactive_fitting(dataset: TDataset | HDataset, app,
                        model_opt: str | list[LogTauTModel | LogTauHModel] = 'from_dataset') -> tuple[list[LogTauTModel | LogTauHModel], list[dict[str, float]], list[dict[str, float]], bool]: # noqa
    '''
    Creates qt window for user to interactively fit models to relaxation
    data

    Parameters
    ----------
    dataset: TDataset | HDataset
        Dataset to plot
    app: QtWidgets.QApplication
        Application used by current program
        Create with `app=QtWidgets.QApplication([])`
    model_opt: str | list[LogTauTModel | LogTauHModel] default 'from_dataset' 
        List of models to offer to user, if 'from_dataset' will generate
        a list based on the dataset provided

    Returns
    -------
    list[LogTauTModel | LogTauHModel]
        Models selected by user
    list[dict[str, float]]
        fit_vars dicts, one per model
    list[dict[str, float]]
        fix_vars dicts, one per model
    bool
        True if user has exited window instead of fitting
        else False
    ''' # noqa

    if model_opt == 'from_dataset':
        if isinstance(dataset, TDataset):
            model_opt = [
                LogOrbachModel,
                LogRamanModel,
                LogPPDRamanModel,
                LogQTMModel,
                LogDirectModel
            ]
        elif isinstance(dataset, HDataset):
            model_opt = [
                LogFDQTMModel,
                LogRamanIIModel,
                LogConstantModel,
                LogBVVRamanIIModel,
                LogBVVConstantModel
            ]
        else:
            raise ValueError('Dataset Type is Unsupported')

    usel = type('obj', (object,), {
        'models': {
            model.NAME.lower(): False
            for model in model_opt
        },
        'fit_vars': [],
        'fix_vars': [],
        'fix': [],
        'exited': True
    })

    param_window = FitWindow(
        dataset,
        usel,
        model_opt,
        gui.widget_defaults
    )
    param_window.show()

    app.exec()

    name_to_model = {
        model.NAME.lower(): model
        for model in model_opt
    }

    r_models = [
        name_to_model[name]
        for name in usel.models
    ]

    return r_models, usel.fit_vars, usel.fix_vars, usel.exited


def plot_fitted_times(dataset: TDataset | HDataset,
                      model: LogTauModel | MultiLogTauModel,
                      show: bool = True, save: bool = False,
                      save_name: str = 'fitted_rates.png',
                      verbose: bool = True,
                      show_params: bool = True) -> tuple[plt.Figure, plt.Axes]:
    '''
    Plots experimental and fitted (model) relaxation rate as\n
    ln(tau) vs 1/xvar where xvar is T or H.

    Parameters
    ----------
    dataset: TDataset | HDataset
        Dataset to plot
    model: LogTauModel | MultiLogTauModel
        Model (fitted) to plot
    show: bool, default True
        If True, show plot on screen
    save: bool, default False
        If True, save plot to file `save_name`
    save_name: str, default = 'fitted_rates.png'
        If save is True, will save plot to this filename
    verbose: bool, default True
        If True, plot file location is written to terminal
    show_params: bool, default True
        If True, shows fitted parameters on plot

    Returns
    -------
    plt.Figure
        Matplotlib figure object
    plt.Axes
        Matplotlib axis object

    Raises
    ------
    ValueError: If dataset type unsupported
    '''

    if not isinstance(dataset, (TDataset, HDataset)):
        raise ValueError('Dataset type unsupported')

    if show_params:
        figsize = (6, 6)
    else:
        figsize = (6, 5.5)

    # Create figure and axes
    fig, ax = plt.subplots(
        1,
        1,
        figsize=figsize,
        num='Fitted relaxation profile'
    )

    _plot_fitted_times(dataset, model, fig, ax, show_params=show_params)

    fig.tight_layout()

    if show:
        plt.show()

    if save:
        fig.savefig(save_name, dpi=500)
        if verbose:
            ut.cprint(
                f'\n Fitted ln(τ) vs 1/{dataset.IDEP_VAR_LABELS[0]} plot saved to \n {save_name}\n', # noqa
                'cyan'
            )

    return fig, ax


def plot_times(dataset: TDataset | HDataset, show: bool = True,
               save: bool = False, save_name: str = 'relaxation_times.png',
               verbose: bool = True) -> tuple[plt.Figure, plt.Axes]:
    '''
    Plots experimental relaxation time as\n
    ln(tau) vs 1/xvar where xvar is T or H.

    Parameters
    ----------
    dataset: TDataset | HDataset
        Dataset to plot
    show: bool, default True
        If True, show plot on screen
    save: bool, default False
        If True, save plot to file `save_name`
    save_name: str, default 'relaxation_times.png'
        If save is True, will save plot to this filename
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
        If dataset type is not HDataset or TDataset
    '''

    # Create figure and axes
    fig, ax = plt.subplots(
        1,
        1,
        figsize=(6, 5.5),
        num='Relaxation profile'
    )

    if isinstance(dataset, HDataset):
        ax.set_xlabel(r'1/H $\left(\mathregular{Oe}^\mathregular{-1}\right)$')
    elif isinstance(dataset, TDataset):
        ax.set_xlabel(r'1/T $\left(\mathregular{K}^\mathregular{-1}\right)$')
    else:
        raise ValueError('Dataset Type is Unsupported')

    # Add uncertainties as errorbars
    if len(dataset.rate_pm):

        # Calculate time errorbars
        times = 1. / dataset.rates
        min_time = 1. / (dataset.rates + dataset.rate_pm[1, :])
        max_time = 1. / (dataset.rates - dataset.rate_pm[0, :])

        ln_min_time = np.log(min_time)
        ln_max_time = np.log(max_time)

        ln_time_plus = ln_max_time - np.log(times)
        ln_time_minus = np.log(times) - ln_min_time

        lntime_mp = np.array([ln_time_minus, ln_time_plus])

        ax.errorbar(
            1. / dataset.dep_vars,
            np.log(times),
            yerr=lntime_mp,
            marker='o',
            lw=0,
            elinewidth=1.5,
            fillstyle='none',
            color='black'
        )
    else:
        ax.plot(
            1. / dataset.dep_vars,
            np.log(1. / dataset.rates),
            marker='o',
            lw=0,
            fillstyle='none',
            color='black'
        )

    # Enable minor ticks
    ax.yaxis.set_minor_locator(AutoMinorLocator())
    ax.xaxis.set_minor_locator(AutoMinorLocator())

    ax.set_ylabel(r'$\ln\left[\tau\right]$ $\left(\ln\left[\mathregular{s}^\mathregular{-1}\right]\right)$') # noqa

    fig.tight_layout()

    if show:
        plt.show()

    if save:
        fig.savefig(save_name, dpi=500)
        if verbose:
            ut.cprint(
                f'\n Fitted ln(tau) vs 1/{dataset.IDEP_VAR_LABELS[0]} plot saved to \n {save_name}\n', # noqa
                'cyan'
            )

    return fig, ax


def _plot_fitted_times(dataset: TDataset | HDataset,
                       model: LogTauModel | MultiLogTauModel,
                       fig: plt.Figure, ax: plt.Axes,
                       show_params: bool = True):
    '''
    Plots experimental and fitted (model) relaxation rate as\n
    ln(tau) vs 1/xvar where xvar is T or H.

    Parameters
    ----------
    dataset: TDataset | HDataset
        Dataset to plot
    model: LogTauModel | MultiLogTauModel
        Model (fitted) to plot
    fig: plt.Figure
        Matplotlib Figure object used for plot
    ax: plt.Axes
        Matplotlib Axis object used for plot
    show_params: bool, default True
        If True, shows fitted parameters on plot

    Returns
    -------
    None

    Raises
    ------
    ValueError
        If dataset type is not HDataset or TDataset
    '''

    if isinstance(dataset, HDataset):
        ax.set_xlabel(r'1/H $\left(\mathregular{Oe}^\mathregular{-1}\right)$')
    elif isinstance(dataset, TDataset):
        ax.set_xlabel(r'1/T $\left(\mathregular{K}^\mathregular{-1}\right)$')
    else:
        raise ValueError('Dataset Type is Unsupported')

    # Add uncertainties as errorbars
    if len(dataset.rate_pm):

        # Calculate time errorbars
        times = 1. / dataset.rates
        min_time = 1. / (dataset.rates + dataset.rate_pm[1, :])
        max_time = 1. / (dataset.rates - dataset.rate_pm[0, :])

        ln_min_time = np.log(min_time)
        ln_max_time = np.log(max_time)

        ln_time_plus = ln_max_time - np.log(times)
        ln_time_minus = np.log(times) - ln_min_time

        lntime_mp = np.array([ln_time_minus, ln_time_plus])

        ax.errorbar(
            1. / dataset.dep_vars,
            np.log(times),
            yerr=lntime_mp,
            marker='o',
            lw=0,
            elinewidth=1.5,
            fillstyle='none',
            label='Experiment',
            color='black'
        )
    else:
        ax.plot(
            1. / dataset.dep_vars,
            np.log(1. / dataset.rates),
            marker='o',
            lw=0,
            fillstyle='none',
            label='Experiment',
            color='black'
        )

    x_vars_grid = np.linspace(
        np.min(dataset.dep_vars),
        np.max(dataset.dep_vars),
        1000
    )

    if isinstance(model, MultiLogTauModel):
        logmodels = model.logmodels
    else:
        logmodels = [model]

    for logmodel in logmodels:

        if type(logmodel) is LogOrbachModel:
            label_fit = '\nFit with'
            label_fit += '\n' + r'{} {:6.2f} s'.format(
                logmodel.VARNAMES_MM['u_eff'],
                logmodel.final_var_values['u_eff']
            )
            label_fit += '\n' + r'{} {:04.3e}'.format(
                logmodel.VARNAMES_MM['A'], logmodel.final_var_values['A']
            )
        elif type(logmodel) is LogRamanModel:
            label_fit = '\nFit with'
            label_fit += '\n' + r'{} {:6.2f} s'.format(
                logmodel.VARNAMES_MM['R'], logmodel.final_var_values['R']
            )
            label_fit += '\n' + r'{} {:04.3e}'.format(
                logmodel.VARNAMES_MM['n'], logmodel.final_var_values['n']
            )
        elif type(logmodel) is LogQTMModel:
            label_fit = '\nFit with'
            label_fit += '\n' + r'{} {:6.2f} s'.format(
                logmodel.VARNAMES_MM['Q'], logmodel.final_var_values['Q']
            )
        elif type(logmodel) is LogDirectModel:
            label_fit = '\nFit with'
            label_fit += '\n' + r'{} {:6.2f} s'.format(
                logmodel.VARNAMES_MM['D'], logmodel.final_var_values['D']
            )
        model_rates = 10**logmodel.model(
            logmodel.final_var_values,
            x_vars_grid,
        )

        # Discard model rates slower than threshold,
        # else these dominate the plot
        thresh = 1E-10
        plot_x_vars_grid = x_vars_grid[model_rates > thresh]
        model_rates = model_rates[model_rates > thresh]
        model_lntau = np.log(1. / np.array(model_rates))

        ax.plot(
            1. / np.array(plot_x_vars_grid),
            model_lntau,
            lw=1.5,
            label=logmodel.NAME,
            ls='--'
        )

    if isinstance(model, MultiLogTauModel) and len(logmodels) > 1: # noqa
        total = np.zeros(len(x_vars_grid))

        for logmodel in logmodels:
            total += 10**logmodel.model(
                logmodel.final_var_values,
                x_vars_grid,
            )

        ax.plot(
            1. / x_vars_grid,
            np.log(1. / total),
            lw=1.5,
            label='Total',
            color='red'
        )

    # Enable minor ticks
    ax.yaxis.set_minor_locator(AutoMinorLocator())
    ax.xaxis.set_minor_locator(AutoMinorLocator())

    expression = ''

    for logmodel in logmodels:
        for it, name in enumerate(logmodel.PARNAMES):
            expression += '{} = {:.3f} '.format(
                logmodel.VARNAMES_MM[name],
                logmodel.final_var_values[name],
            )
            if name in logmodel.fit_vars.keys():
                expression += r'$\pm$ '
                expression += '{:.3f} '.format(logmodel.fit_stdev[name])
            expression += '{}    '.format(logmodel.UNITS_MM[name])
            if it == 1 and len(logmodel.fit_vars.keys()) > 2:
                expression += '\n'
        expression += '\n'

    if show_params:
        ax.text(
            0.0, 1.02, s=expression, fontsize=10, transform=ax.transAxes
        )

    if dataset.IDEP_VAR_NAMES[0] == 'Field':
        ax.legend(
            fontsize='10', numpoints=1, ncol=1, frameon=False
        )
    else:
        ax.legend(
            loc='lower right', fontsize='10', numpoints=1, ncol=1,
            frameon=False
        )

    ax.set_ylabel(r'$\ln\left[\tau\right]$ ($\ln\left[\mathregular{s}^\mathregular{-1}\right]$)') # noqa

    return


def plot_fitted_rates(dataset: TDataset | HDataset,
                      model: LogTauModel | MultiLogTauModel,
                      show: bool = True, save: bool = False,
                      save_name: str = 'fitted_rates.png',
                      verbose: bool = True,
                      show_params: bool = True) -> tuple[plt.Figure, plt.Axes]:
    '''
    Plots experimental and fitted (model) relaxation rate as\n
    rate vs xvar where xvar is T or H. With log log scale.

    Parameters
    ----------
    dataset: TDataset | HDataset
        Dataset to plot
    model: LogTauModel | MultiLogTauModel
        Model (fitted) to plot
    show: bool, default True
        If True, show plot on screen
    save: bool, default False
        If True, save plot to file `save_name`
    save_name: str, default = 'fitted_rates.png'
        If save is True, will save plot to this filename
    verbose: bool, default True
        If True, plot file location is written to terminal
    show_params: bool, default True
        If True, shows fitted parameters on plot

    Returns
    -------
    plt.Figure
        Matplotlib figure object
    plt.Axes
        Matplotlib axis object

    Raises
    ------
    ValueError: If dataset type unsupported
    '''

    if not isinstance(dataset, (TDataset, HDataset)):
        raise ValueError('Dataset type unsupported')

    if show_params:
        figsize = (6, 6)
    else:
        figsize = (6, 5.5)

    # Create figure and axes
    fig, ax = plt.subplots(
        1,
        1,
        figsize=figsize,
        num='Fitted relaxation profile'
    )

    _plot_fitted_rates(dataset, model, fig, ax, show_params=show_params)

    fig.tight_layout()

    warnings.simplefilter('ignore', UserWarning)
    if show:
        plt.show()

    if save:
        fig.savefig(save_name, dpi=500)
        if verbose:
            ut.cprint(
                f'\n Fitted τ⁻¹ vs {dataset.IDEP_VAR_LABELS[0]} plot saved to \n {save_name}\n', # noqa
                'cyan'
            )
    warnings.simplefilter('default', UserWarning)

    return fig, ax


def qt_plot_fitted_rates(app: QtWidgets.QApplication,
                         dataset: TDataset | HDataset,
                         model: LogTauModel | MultiLogTauModel,
                         save: bool = False, show: bool = True,
                         save_name: str = 'fitted_rates.png',
                         verbose: bool = True,
                         show_params: bool = True) -> None:
    '''
    Plots experimental and fitted (model) relaxation rate as\n
    rate vs xvar where xvar is T or H. With log log scale.

    Parameters
    ----------
    dataset: TDataset | HDataset
        Dataset to plot
    model: LogTauModel | MultiLogTauModel
        Model (fitted) to plot
    show: bool, default True
        If True, show plot on screen
    save: bool, default False
        If True, save plot to file `save_name`
    save_name: str, default 'fitted_rates.png'
        If save is True, will save plot to this filename
    verbose: bool, default True
        If True, plot file location is written to terminal
    show_params: bool, default True
        If True, shows fitted parameters on plot

    Returns
    -------
    None

    Raises
    ------
    ValueError: If dataset type unsupported
    '''

    if not isinstance(dataset, (TDataset, HDataset)):
        raise ValueError('Dataset type unsupported')

    window = gui.MatplotlibWindow()

    window.setWindowTitle('Fitted relaxation profile')

    # Add plot
    _plot_fitted_rates(
        dataset, model, window.sc.fig, window.sc.ax, show_params=show_params
    )

    warnings.simplefilter('ignore', UserWarning)
    # Save plot
    if save:
        window.sc.fig.savefig(save_name, dpi=300)
        if verbose:
            ut.cprint(
                f'\n Fitted τ⁻¹ vs {dataset.IDEP_VAR_LABELS[0]} plot saved to \n {save_name}\n', # noqa
                'cyan'
            )

    if show:
        window.show()
        # Call twice else it wont work!
        window.sc.fig.tight_layout()
        window.sc.fig.tight_layout()
        app.exec_()

    warnings.simplefilter('default', UserWarning)

    return


def _plot_fitted_rates(dataset: TDataset | HDataset,
                       model: LogTauModel | MultiLogTauModel,
                       fig: plt.Figure, ax: plt.Axes,
                       show_params: bool = True):
    '''
    Plots experimental and fitted (model) relaxation rate as\n
    rate vs xvar where xvar is T or H. With log log scale.

    Parameters
    ----------
    dataset: TDataset | HDataset
        Dataset to plot
    model: LogTauModel | MultiLogTauModel
        Model (fitted) to plot
    fig: plt.Figure
        Matplotlib Figure object used for plot
    ax: plt.Axes
        Matplotlib Axis object used for plot
    show_params: bool, default True
        If True, shows fitted parameters on plot

    Returns
    -------
    None

    Raises
    ------
    ValueError
        If dataset type is not HDataset or TDataset
    '''

    if isinstance(dataset, HDataset):
        ax.set_xlabel(r'Field (Oe)')
    elif isinstance(dataset, TDataset):
        ax.set_xlabel(r'Temperature (K)')
    else:
        raise ValueError('Dataset Type is Unsupported')

    # Add uncertainties as errorbars
    if len(dataset.rate_pm):
        ax.errorbar(
            dataset.dep_vars,
            dataset.rates,
            yerr=dataset.rate_pm,
            marker='o',
            lw=0,
            elinewidth=1.5,
            fillstyle='none',
            label='Experiment',
            color='black'
        )
    else:
        ax.plot(
            dataset.dep_vars,
            dataset.rates,
            marker='o',
            lw=0,
            fillstyle='none',
            label='Experiment',
            color='black'
        )

    x_vars_grid = np.linspace(
        np.min(dataset.dep_vars),
        np.max(dataset.dep_vars),
        5000
    )

    if isinstance(model, MultiLogTauModel):
        logmodels = model.logmodels
    else:
        logmodels = [model]

    for logmodel in logmodels:

        if type(logmodel) is LogOrbachModel:
            label_fit = '\nFit with'
            label_fit += '\n' + r'{} {:6.2f} s'.format(
                logmodel.VARNAMES_MM['u_eff'],
                logmodel.final_var_values['u_eff']
            )
            label_fit += '\n' + r'{} {:04.3e}'.format(
                logmodel.VARNAMES_MM['A'], logmodel.final_var_values['A']
            )
        elif type(logmodel) is LogRamanModel:
            label_fit = '\nFit with'
            label_fit += '\n' + r'{} {:6.2f} s'.format(
                logmodel.VARNAMES_MM['R'], logmodel.final_var_values['R']
            )
            label_fit += '\n' + r'{} {:04.3e}'.format(
                logmodel.VARNAMES_MM['n'], logmodel.final_var_values['n']
            )
        elif type(logmodel) is LogQTMModel:
            label_fit = '\nFit with'
            label_fit += '\n' + r'{} {:6.2f} s'.format(
                logmodel.VARNAMES_MM['Q'], logmodel.final_var_values['Q']
            )
        elif type(logmodel) is LogDirectModel:
            label_fit = '\nFit with'
            label_fit += '\n' + r'{} {:6.2f} s'.format(
                logmodel.VARNAMES_MM['D'], logmodel.final_var_values['D']
            )
        model_rates = 10**logmodel.model(
            logmodel.final_var_values,
            x_vars_grid,
        )

        ax.plot(
            np.array(x_vars_grid),
            np.array(model_rates),
            lw=1.5,
            label=logmodel.NAME,
            ls='--'
        )

    if isinstance(model, MultiLogTauModel) and len(logmodels) > 1: # noqa
        total = np.zeros(len(x_vars_grid))

        for logmodel in logmodels:
            total += 10**logmodel.model(
                logmodel.final_var_values,
                x_vars_grid,
            )

        ax.plot(
            x_vars_grid,
            total,
            lw=1.5,
            label='Total',
            color='red'
        )

    if isinstance(dataset, HDataset):
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

    gui.format_rate_x_y_axes(
        ax,
        dataset.rates,
        dataset.dep_vars,
        np.abs(dataset.rate_pm),
        x_type=dataset.IDEP_VAR_NAMES[0].lower()
    )

    expression = ''

    for logmodel in logmodels:
        for it, name in enumerate(logmodel.PARNAMES):
            expression += '{} = {:.3f} '.format(
                logmodel.VARNAMES_MM[name],
                logmodel.final_var_values[name],
            )
            if name in logmodel.fit_vars.keys():
                expression += r'$\pm$ '
                expression += '{:.3f} '.format(logmodel.fit_stdev[name])
            expression += '{}    '.format(logmodel.UNITS_MM[name])
            if it == 1 and len(logmodel.fit_vars.keys()) > 2:
                expression += '\n'
        expression += '\n'

    if show_params:
        ax.text(
            0.0, 1.02, s=expression, fontsize=10, transform=ax.transAxes
        )

    if dataset.IDEP_VAR_NAMES[0] == 'Field':
        ax.legend(
            fontsize='10', numpoints=1, ncol=1, frameon=False
        )
    else:
        ax.legend(
            loc='upper left', fontsize='10', numpoints=1, ncol=1, frameon=False
        )

    ax.set_ylabel(r'Rate (s$^\mathregular{-1}$)')

    return


def plot_rates(dataset: TDataset | HDataset, show: bool = True,
               save: bool = False, save_name: str = 'relaxation_rates.png',
               verbose: bool = True) -> tuple[plt.Figure, plt.Axes]:
    '''
    Plots experimental relaxation rate vs field/temperature and
    displays on screen.

    Parameters
    ----------
    dataset: TDataset | HDataset
        Dataset to plot
    show: bool, default True
        If True, show plot on screen
    save: bool, default False
        If True, save plot to file `save_name`
    save_name: str, default 'relaxation_rates.png'
        If save is True, will save plot to this filename
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
        If dataset type is not HDataset or TDataset
    '''

    # Create figure and axes
    fig, ax = plt.subplots(
        1,
        1,
        figsize=(6, 5.5),
        num='Relaxation profile'
    )

    if isinstance(dataset, HDataset):
        ax.set_xlabel(r'Field (Oe)')
    elif isinstance(dataset, TDataset):
        ax.set_xlabel(r'Temperature (K)')
    else:
        raise ValueError('Dataset Type is Unsupported')

    # Add uncertainties as errorbars
    if len(dataset.rate_pm):
        ax.errorbar(
            dataset.dep_vars,
            dataset.rates,
            yerr=dataset.rate_pm,
            marker='o',
            lw=0,
            elinewidth=1.5,
            fillstyle='none',
            color='black'
        )
    else:
        ax.plot(
            dataset.dep_vars,
            dataset.rates,
            marker='o',
            lw=0,
            fillstyle='none',
            color='black'
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

    fig.tight_layout()

    # Suppress symlog warning
    warnings.simplefilter('ignore', UserWarning)

    if save:
        plt.savefig(save_name)
        if verbose:
            ut.cprint(
                f'\n Relaxation plot saved to \n {save_name}\n',
                'cyan'
            )
    if show:
        plt.show()

    # Reenable symlog warning
    warnings.simplefilter('default', UserWarning)

    return fig, ax


def plot_rate_residuals(dataset: TDataset,
                        model: LogTauModel | MultiLogTauModel,
                        save: bool = False, show: bool = True,
                        save_name: str = 'model_residual_tau.png',
                        verbose: bool = True) -> tuple[plt.Figure, plt.Axes]:
    '''
    Plots difference of log10(experiment) and log10(model) relaxation rates
    (log10(experiment_rate) - log10(model_rate) vs Temperature or Field)

    Parameters
    ----------
    dataset: TDataset | HDataset
        Dataset to plot
    model: LogTauModel | MultiLogTauModel
        Model (fitted) to plot
    show: bool, default True
        If True, show plot on screen
    save: bool, default False
        If True, save plot to file `save_name`
    save_name: str, default 'model_residual_tau.png'
        If save is True, will save plot to this filename
    verbose: bool, default True
        If True, plot file location is written to terminal

    Returns
    -------
    plt.Figure
        Matplotlib figure object
    plt.Axes
        Matplotlib axis object
    '''
    # Create figure and axes
    fig, ax = plt.subplots(
        1,
        1,
        figsize=[6, 6],
        num='Residuals'
    )

    _plot_rate_residuals(dataset, model, ax)

    fig.tight_layout()

    warnings.simplefilter('ignore', UserWarning)
    # Save plot
    if save:
        plt.savefig(save_name, dpi=300)
        if verbose:
            ut.cprint(
                f'\n Rate residuals plot saved to \n {save_name}\n',
                'cyan'
            )
    if show:
        plt.show()
    warnings.simplefilter('default', UserWarning)

    return fig, ax


def qt_plot_rate_residuals(app: QtWidgets.QApplication, dataset: TDataset,
                           model: LogTauModel | MultiLogTauModel,
                           save: bool = False, show: bool = True,
                           save_name: str = 'model_residual_tau.png',
                           verbose: bool = True) -> None:
    '''
    Plots difference of log10(experiment) and log10(model) relaxation rates
    in a qt window using matplotlib

    Parameters
    ----------
    app: QtWidgets.QApplication
        Application used by current program
        Create with `app=QtWidgets.QApplication([])`
    dataset: TDataset | HDataset
        Dataset to plot
    model: LogTauModel | MultiLogTauModel
        Model (fitted) to plot
    show: bool, default True
        If True, show plot on screen
    save: bool, default False
        If True, save plot to file `save_name`
    save_name: str, default 'model_residual_tau.png'
        If save is True, will save plot to this filename
    verbose: bool, default True
        If True, plot file location is written to terminal

    Returns
    -------
    None
    '''

    window = gui.MatplotlibWindow()
    window.setWindowTitle('Residuals')

    _plot_rate_residuals(dataset, model, window.sc.ax)

    # Save plot
    if save:
        window.sc.fig.savefig(save_name, dpi=300)
        if verbose:
            ut.cprint(
                f'\n Rate residuals plot saved to \n {save_name}\n',
                'cyan'
            )

    warnings.simplefilter('ignore', UserWarning)
    if show:
        window.show()
        # Call twice else it wont work!
        window.sc.fig.tight_layout()
        window.sc.fig.tight_layout()
        app.exec_()
    warnings.simplefilter('default', UserWarning)

    return


def _plot_rate_residuals(dataset: TDataset | HDataset,
                         model: LogTauModel | MultiLogTauModel,
                         ax: plt.Axes) -> None:
    '''
    Plots difference of log10(experiment) and log10(model) relaxation rates
    onto a given figure and axis

    Parameters
    ----------
    models: list[LogTauModel | MultiLogTauModel]
        Models, one per temperature
    file_name: str
        Name of output file
    ax: plt.Axes
        Matplotlib Axis object used for plot

    Returns
    -------
    None
    ''' # noqa

    if isinstance(dataset, HDataset):
        ax.set_xlabel(r'Field (Oe)')
    elif isinstance(dataset, TDataset):
        ax.set_xlabel(r'Temperature (K)')
    else:
        raise ValueError('Dataset Type is Unsupported')

    # Add additional set of axes to create 'zero' line
    ax2 = ax.twiny()
    ax2.get_yaxis().set_visible(False)
    ax2.set_yticks([])
    ax2.set_xticks([])
    ax2.spines['bottom'].set_position(('zero'))

    if isinstance(model, MultiLogTauModel):
        logmodels = model.logmodels
    else:
        logmodels = [model]

    model_rate = np.zeros(len(dataset.dep_vars))

    for logmodel in logmodels:
        model_rate += 10**logmodel.model(
            logmodel.final_var_values,
            dataset.dep_vars,
        )

    model_lograte = np.log10(model_rate)

    # Plot residuals
    if len(dataset.lograte_pm):
        ax.errorbar(
            dataset.dep_vars,
            np.log10(dataset.rates) - model_lograte,
            yerr=dataset.lograte_pm,
            fmt='b.'
        )
    else:
        ax.plot(
            dataset.dep_vars,
            np.log10(dataset.rates) - model_lograte,
            color='b',
            marker='o',
            lw=0,
            fillstyle='none',
            label='Experiment'
        )
    # Set log scale on x axis
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

    # Set formatting for y axis major ticks
    ax.yaxis.set_major_formatter(ScalarFormatter())

    # Add minor ticks to y axis with no labels
    ax.yaxis.set_minor_locator(AutoMinorLocator())

    # Symmetrise y axis limits based on max abs error
    if len(dataset.lograte_pm):
        all_data = [
            np.log10(dataset.rates) - model_lograte + dataset.lograte_pm
        ]
        all_data += [
            np.log10(dataset.rates) - model_lograte - dataset.lograte_pm
        ]
    else:
        all_data = [
            np.log10(dataset.rates) - model_lograte
        ]
        all_data += [
            np.log10(dataset.rates) - model_lograte
        ]

    ticks, maxval = gui.min_max_ticks_with_zero(all_data, 5)
    ax.set_yticks(ticks)

    ax.set_ylim([- maxval * 1.1, + maxval * 1.1])

    # Axis labels
    ax.set_ylabel(
        r'$\log_\mathregular{10}\left[\tau^\mathregular{-1}_{\mathregular{exp}}\right] - \log_\mathregular{10}\left[\tau^\mathregular{-1}_{\mathregular{fit}}\right]$  $\left(\log_\mathregular{10}\left[\mathregular{s}^\mathregular{-1}\right]\right)$' # noqa
    )

    # Set x tick formatting
    gui.set_rate_xtick_formatting(
        ax,
        dataset.dep_vars,
        x_type=dataset.IDEP_VAR_NAMES[0].lower()
    )

    return


def write_model_params(model: LogTauModel | MultiLogTauModel,
                       file_name: str = 'relaxation_model_params.csv',
                       verbose: bool = True, delimiter: str = ',',
                       extra_comment: str = '') -> None:
    '''
    Writes fitted and fixed parameters of model(s) to file

    Parameters
    ----------
    models: list[LogTauModel | MultiLogTauModel]
        Models to write to file
    file_name: str
        Name of output file
    verbose: bool, default True
        If True, output file location is written to terminal
    delimiter: str, default ','
        Delimiter used in .csv file, usually either ',' or ';'
    extra_comment: str, optional
        Extra comments to add to file after ccfit2 version line
        Must include comment character # for each new line


    Returns
    -------
    None
    ''' # noqa

    if isinstance(model, MultiLogTauModel): # noqa
        logmodels = model.logmodels
    else:
        logmodels = [model]

    # Make header
    header = []
    for logmodel in logmodels:
        for var in logmodel.fit_vars.keys():
            header.append(f'{var} ({logmodel.UNITS[var]})')
            header.append(f'{var}-ESD ({logmodel.UNITS[var]})')
        for var in logmodel.fix_vars.keys():
            header.append(f'{var} ({logmodel.UNITS[var]})')

    header = f'{delimiter}'.join(header)

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

    for logmodel in logmodels:

        for var in logmodel.fit_vars.keys():
            _out.append(logmodel.final_var_values[var])
            _out.append(logmodel.fit_stdev[var])
        for var in logmodel.fix_vars.keys():
            _out.append(logmodel.fix_vars[var])

    _out = np.asarray([_out])

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
            '\n Relaxation Model parameters written to \n {}\n'.format(
                file_name
            ),
            'cyan'
        )

    return


def write_model_data(dataset: TDataset | HDataset,
                     model: LogTauModel | MultiLogTauModel,
                     file_name: str = 'relaxation_model_data.csv',
                     verbose: bool = True,
                     delimiter: str = ',', extra_comment: str = '') -> None:
    '''
    Creates file containing rate vs temperature/field calculated using model
    parameters

    Parameters
    ----------
    dataset: TDataset | HDataset
        Dataset to which a model was successfully fitted (i.e. fit_status=True)
    model: LogTauModel | MultiLogTauModel
        Model which has been fitted to dataset
    file_name: str, default 'relaxation_model_data.csv'
        Name of output file
    verbose: bool, default True
        If True, output file location is written to terminal
    delimiter: str, default ','
        Delimiter used in .csv file, usually either ',' or ';'
    extra_comment: str, optional
        Extra comments to add to file after ccfit2 version line
        Must include comment character # for each new line

    Returns
    -------
    None
    '''

    if not model.fit_status:
        return

    if isinstance(model, MultiLogTauModel):
        logmodels = model.logmodels
    else:
        logmodels = [model]

    # Make header
    if not isinstance(dataset, (HDataset, TDataset)):
        raise ValueError('Dataset Type is Unsupported')

    header = [
        f'{dataset.IDEP_VAR_LABELS[0]} ({dataset.IDEP_VAR_UNITS[0]})'
    ]

    for logmodel in logmodels:
        header.append(f'{logmodel.NAME} rate (s^-1)')

    if len(logmodels) > 1:
        header.append('Total rate (s^-1)')

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
    x_vars_grid = np.linspace(
        np.min(dataset.dep_vars),
        np.max(dataset.dep_vars),
        1000
    )

    # Individual models
    individual = [
        [
            10**logmodel.model(
                logmodel.final_var_values,
                x_vars_grid
            )
        ]
        for logmodel in logmodels
    ]

    if len(logmodels) > 1:
        total = np.sum(individual, axis=0)
        out = np.vstack([x_vars_grid, *individual, total]).T
    else:
        out = np.vstack([x_vars_grid, *individual]).T

    # Save file
    np.savetxt(
        file_name,
        out,
        header=header,
        delimiter=delimiter,
        encoding='utf-8',
        comments=comment
    )

    if verbose:
        ut.cprint(
            '\n Relaxation model τ⁻¹ vs {} written to \n {}\n'.format(
                dataset.IDEP_VAR_LABELS[0],
                file_name
            ),
            'cyan'
        )

    return
