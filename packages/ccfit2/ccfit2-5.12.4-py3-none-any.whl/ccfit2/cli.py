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

'''

from . import ac, dc
from . import waveform as wfrm
from . import relaxation as relax
from . import utils as ut

import argparse
import numpy as np
import os
import sys
from qtpy import QtWidgets
import matplotlib.pyplot as plt
from glob import glob
import multiprocessing as mp

import warnings
warnings.filterwarnings('ignore', '.*GUI is implemented.*')
warnings.filterwarnings('ignore', 'invalid value encountered in power')
warnings.filterwarnings('ignore', 'invalid value encountered in log10')
warnings.filterwarnings('ignore', 'invalid value encountered in divide')


# Set user specified font name
if os.getenv('ccfit2_fontname'):
    try:
        plt.rcParams['font.family'] = os.getenv('ccfit2_fontname')
    except ValueError:
        ut.cprint('Error in ccfit2_fontname environment variable', 'red')
        sys.exit(1)

# Set user specified number of cores
NUM_THREADS = 'auto'
if os.getenv('ccfit2_numthreads'):
    try:
        NUM_THREADS = int(os.getenv('ccfit2_numthreads'))
    except ValueError:
        ut.cprint('Error in ccfit2_numthreads environment variable', 'red')
        sys.exit(1)
else:
    NUM_THREADS = mp.cpu_count() - 1

# Set spawn as default start method - MUCH faster on WSL2 than default fork
mp.set_start_method('spawn', force=True)

# Set user specified font size
if os.getenv('ccfit2_fontsize'):
    try:
        plt.rcParams['font.size'] = float(os.getenv('ccfit2_fontsize'))
    except ValueError:
        ut.cprint('Error in ccfit2_fontsize environment variable', 'red')
        sys.exit(1)

# Set user specified plot file format
PFF = '.png'
if os.getenv('ccfit2_plotformat'):
    try:
        PFF = os.getenv('ccfit2_plotformat')
        if PFF[0] != '.':
            PFF = f'.{PFF}'
    except ValueError:
        ut.cprint('Error in ccfit2_plotformat environment variable', 'red')
        sys.exit(1)

# Set user specified plot file format
CSV_DELIMITER = ','
if os.getenv('ccfit2_csvdelimiter'):
    try:
        CSV_DELIMITER = os.getenv('ccfit2_csvdelimiter')
    except ValueError:
        ut.cprint('Error in ccfit2_csvdelimiter environment variable', 'red')
        sys.exit(1)


_SHOW_CONV = {
    'on': True,
    'save': False,
    'show': True,
    'off': False
}

_SAVE_CONV = {
    'on': True,
    'save': True,
    'show': False,
    'off': False
}


def ac_mode_func(uargs):
    '''
    Wrapper function for command line interface call to ac mode

    Parameters
    ----------
    uargs : argparser object
        command line arguments

    Returns
    -------
    None
    '''

    # Make QT application - this MUST happen before any matplotlib/qt
    # plots are made
    app = QtWidgets.QApplication([])

    # Object to store user configuration, paths, etc.
    user_cfg = ut.UserConfig()
    user_cfg.file_name = uargs.input_file

    # Use glob to expand wildcards if on windows
    if 'nt' in os.name and '*' in user_cfg.file_name[0]:
        user_cfg.file_name = glob(user_cfg.file_name[0])

    # mass, mw
    user_cfg.mass = uargs.mass
    user_cfg.mw = uargs.MW

    # Set number of threads
    num_threads = min(NUM_THREADS, len(user_cfg.file_name))
    print_num_threads(num_threads)

    # Check if select_T or select_H is used with wrong x_unit
    if uargs.select_T and uargs.x_var == 'H':
        ut.cprint('Error: --select_T used with --x_var H', 'red')
        sys.exit(1)
    elif uargs.select_H and uargs.x_var == 'T':
        ut.cprint('Error: --select_H used with --x_var T', 'red')
        sys.exit(1)

    # Check input file headers in parallel
    check_mag_files(
        user_cfg.file_name,
        ac.HEADERS_SUPPORTED,
        uargs.data_header,
        num_threads
    )

    pool = mp.Pool(num_threads)
    iterables = [
        (file_name, user_cfg.mass, user_cfg.mw, uargs.data_header)
        for file_name in user_cfg.file_name
    ]
    ac_measurements = pool.starmap(
        ac.Measurement.from_file,
        iterables,
        chunksize=None
    )
    pool.close()
    pool.join()

    # Collapse into a single list
    ac_measurements = [
        m
        for mm in ac_measurements
        for m in mm
    ]

    # Group measurements into sublists of experiments
    # Where order of dimensions dc field strength
    # and temperature depend on choice of x_var
    all_experiments_sep = ac.Experiment.from_measurements(
        ac_measurements, temp_thresh=uargs.temp_thresh,
        field_thresh=uargs.field_thresh,
        x_var=uargs.x_var
    )

    # State independent variable
    if uargs.x_var == 'T':
        ind_var_unit = 'K'
        ind_var_name = 'temperature'
    elif uargs.x_var == 'H':
        ind_var_unit = 'Oe'
        ind_var_name = 'field'

    ut.cprint(f'\nIndependent variable is {ind_var_name}', 'green')

    if uargs.verbose:
        print('\nVerbose mode entered.\n')
        for experiments in all_experiments_sep:
            if uargs.x_var == 'T':
                x_var = experiments[0].rep_dc_field
                print('{}: {} {}'.format(
                    ind_var_name.capitalize(), x_var, ind_var_unit)
                )
                for experiment in experiments:
                    print(
                        (
                            'The raw temperatures at this field have been'
                            ' grouped as:'
                        )
                    )
                    print(
                        'Mean={:04.1f}, Min={}, Max={}\nRaw={}'.format(
                            experiment.rep_temperature,
                            np.min(experiment.raw_temperatures),
                            np.max(experiment.raw_temperatures),
                            experiment.raw_temperatures
                        )
                    )
            else:
                x_var = experiments[0].rep_temperature
                print('{}: {} {}'.format(
                    ind_var_name.capitalize(), x_var, ind_var_unit)
                )
                for experiment in experiments:
                    print(
                        (
                            'The raw fields at this temperature have been'
                            ' grouped as:'
                        )
                    )
                    print(
                        'Mean={:04.1f}, Min={}, Max={}\nRaw={}'.format(
                            experiment.rep_dc_field,
                            np.min(experiment.dc_fields),
                            np.max(experiment.dc_fields),
                            experiment.rep_dc_field
                        )
                    )
                print('{} Frequencies: {}\n'.format(
                    len(experiment.ac_freqs), experiment.ac_freqs)
                )

    # Manual selection of temperatures to fit
    if uargs.select_T:
        all_experiments_sep = [
            ac.interactive_t_select(experiments)
            for experiments in all_experiments_sep
        ]

    elif uargs.unselect_T:
        all_experiments_sep = [
            ac.interactive_t_select(experiments, on=True)
            for experiments in all_experiments_sep
        ]

    elif uargs.select_H:
        all_experiments_sep = [
            ac.interactive_h_select(experiments)
            for experiments in all_experiments_sep
        ]

    elif uargs.unselect_H:
        all_experiments_sep = [
            ac.interactive_h_select(experiments, on=True)
            for experiments in all_experiments_sep
        ]

    if uargs.process == 'plot':
        for experiments in all_experiments_sep:
            # Base save names for plots
            save_name = '{:.1f}K_{:.1f}Oe{}'.format(
                experiments[0].rep_temperature,
                experiments[0].rep_dc_field,
                PFF
            )
            if uargs.x_var == 'T':
                x_var = experiments[0].rep_dc_field
            elif uargs.x_var == 'H':
                x_var = experiments[0].rep_temperature
            cc_save_name = f'cole_cole_{save_name}'

            ac.plot_colecole(
                experiments,
                save=True,
                show=False,
                x_var=uargs.x_var,
                save_name=os.path.join(user_cfg.results_dir, cc_save_name),
                window_title='Cole-Cole plot for {:.1f} {}'.format(
                    x_var,
                    ind_var_unit
                )
            )

            sus_save_name = f'susc_{save_name}'

            ac.plot_susceptibility(
                experiments,
                save=True,
                show=False,
                x_var=uargs.x_var,
                save_name=os.path.join(user_cfg.results_dir, sus_save_name),
                window_title='AC susceptibility for {:.1f} {}'.format(
                    x_var,
                    ind_var_unit
                )
            )
            plt.show()
        sys.exit()

    unique_dc_fields = np.unique(
        [experiments[0].rep_dc_field for experiments in all_experiments_sep]
    )

    unique_temperatures = np.unique(
        [experiments[0].rep_temperature for experiments in all_experiments_sep]
    )

    # For each AC experiment, fit an AC model to the data
    for f_it, (experiments, dc_field, temperature) in enumerate(zip(all_experiments_sep, unique_dc_fields, unique_temperatures)): # noqa
        if uargs.x_var == 'T':
            _msg = '\n Fitting AC Susceptibility at {:.5f} Oe'.format(
                dc_field
            )
        else:
            _msg = '\n Fitting AC Susceptibility at {:.5f} K'.format(
                temperature
            )
        ut.cprint(_msg, 'black_bluebg')

        # Interactive window to choose AC model
        # for current set of experiments
        chosen_model = ac.interactive_ac_model_select(
            experiments,
            uargs.x_var
        )

        # Create a model instance for each experiment
        # all parameters are fitted in cli mode
        fit_vars = {var: 'guess' for var in chosen_model.PARNAMES}
        fix_vars = {}
        models: list[ac.Model] = [
            chosen_model(
                fit_vars=fit_vars, fix_vars=fix_vars, experiment=experiment
            )
            for experiment in experiments
        ]
        # Update flat lines threshold
        for model in models:
            model.flat_thresh = uargs.flat_thresh

        # Feed fits forward in temperature/field
        # Use T=n fit for T=n+1 guess
        prev_fit = models[0].fit_vars
        for model, experiment in zip(models, experiments):

            # Update guesses
            for key in model.fit_vars.keys():
                model.fit_vars[key] = prev_fit[key]

            if uargs.verbose:
                print('For T= {:.2f} K and H= {:4.1f} Oe'.format(
                    experiment.rep_temperature, experiment.rep_dc_field
                ))
                print('Fixed parameters are:')
                print(model.fix_vars)
                print('Fit parameter guesses are:')
                print(model.fit_vars)

            model.fit_to(experiment, no_discard=uargs.discard_off)

            if uargs.verbose:
                print('Final parameters are:')
                print(model.final_var_values)

            # Use these fitted params as next guess, if fit successful
            if model.fit_status:
                prev_fit = model.final_var_values
            # Else use this model's guess as next guess
            else:
                prev_fit = model.fit_vars

        # Check for total failure
        if all(not model.fit_status for model in models):
            ut.cprint('\n    ***Error***:', 'red')
            if uargs.x_var == 'T':
                ut.cprint(
                    'At {:.5f} Oe, all fits failed.'.format(dc_field),
                    'red'
                )
                # Exit if only one field
                if len(unique_dc_fields) == 1:
                    sys.exit(1)
                # else go to next field
                else:
                    continue
            else:
                ut.cprint(
                    'At {:.2f} K, all fits failed.'.format(temperature),
                    'red'
                )
                # Exit if only one temperature
                if len(unique_temperatures) == 1:
                    sys.exit(1)
                # else go to next temperature
                else:
                    continue

        # For each field, save to file all associated fit params and model
        # funcs
        if uargs.x_var == 'T':
            base_filename = 'ac_{:.1f}Oe_{}'.format(
                dc_field,
                chosen_model.NAME.lower().replace(' ', '_')
            )
        else:
            base_filename = 'ac_{:.2f}K_{}'.format(
                temperature,
                chosen_model.NAME.lower().replace(' ', '_')
            )
        base_filename = os.path.join(user_cfg.results_dir, base_filename)
        fit_filename = '{}_params.csv'.format(base_filename)
        model_filename = '{}_model.csv'.format(base_filename)

        ac.write_model_params(
            models,
            fit_filename,
            delimiter=CSV_DELIMITER
        )
        ac.write_model_data(
            experiments,
            models,
            model_filename,
            delimiter=CSV_DELIMITER
        )

        # Fitted cole cole plot, either separate or on one figure
        if uargs.single_plots != 'off':
            for experiment, model in zip(experiments, models):
                single_cc_save_name = 'ac_cole_cole_{:.2f}K_{:.3}Oe_{}{}'.format( # noqa
                    experiment.rep_temperature,
                    experiment.rep_dc_field,
                    model.NAME.lower().replace(' ', '_'),
                    PFF
                )
                single_sus_save_name = 'ac_susc_{:.2f}K_{:.3}Oe_{}{}'.format(
                    experiment.rep_temperature,
                    experiment.rep_dc_field,
                    model.NAME.lower().replace(' ', '_'),
                    PFF
                )
                ac.plot_single_fitted_cole_cole(
                    experiment,
                    model,
                    save_name=os.path.join(
                        user_cfg.results_dir,
                        single_cc_save_name
                    ),
                    save=uargs.single_plots in ['save', 'on'],
                    show=False,
                )
                ac.plot_single_fitted_susceptibility(
                    experiment,
                    model,
                    save_name=os.path.join(
                        user_cfg.results_dir,
                        single_sus_save_name
                    ),
                    save=uargs.single_plots in ['save', 'on'],
                    show=False
                )
                if uargs.single_plots in ['show', 'on']:
                    plt.show()
                plt.close('all')

        cc_save_name = f'{base_filename}_cole_cole{PFF}'
        ac.plot_fitted_colecole(
            experiments,
            models,
            save_name=os.path.join(user_cfg.results_dir, cc_save_name),
            save=True,
            show=False,
            x_var=uargs.x_var
        )

        sus_save_name = f'{base_filename}_susc{PFF}'
        ac.plot_fitted_susceptibility(
            experiments,
            models,
            save_name=os.path.join(user_cfg.results_dir, sus_save_name),
            save=True,
            show=False,
            x_var=uargs.x_var
        )
        plt.show()

        # If only susc, loop back here
        if uargs.process == 'susc':
            continue

        # Proceed to fit the relaxation profile after having finished fitting
        # the AC data.
        if uargs.x_var == 'T':
            _msg = '\n Fitting relaxation rate vs temperature at {:.2f} Oe\n'.format( # noqa
                dc_field
            )
            ut.cprint(_msg, 'black_bluebg')

            if np.sum([model.fit_status for model in models]) <= 2:
                ut.cprint(
                    '    ***Warning***:\n    Not enough data points to fit the relaxation profile', # noqa
                    'red'
                )
                continue

        if uargs.x_var == 'H':
            _msg = '\n Fitting relaxation rate vs field at {:.2f} K\n'.format(
                temperature
            )
            ut.cprint(_msg, 'black_bluebg')

            if np.sum([model.fit_status for model in models]) <= 2:
                ut.cprint(
                    '    ***Warning***:\n    Not enough data points to fit the relaxation profile', # noqa
                    'red'
                )
                continue

        # Create dataset to store relaxation rate and temperature data
        if uargs.x_var == 'T':
            try:
                datasets = relax.TDataset.from_ac_dc(models)
            except TypeError:
                ut.cprint(
                    'Relaxation fitting of double tau models is unsupported',
                    'black_yellowbg'
                )
                ut.cprint(
                    'Split your _params.csv file into individual .csv files using', # noqa
                    'black_yellowbg'
                )
                ut.cprint(
                    'split_rates <_param_file>',
                    'green'
                )
                ut.cprint(
                    'and run',
                    'black_yellowbg'
                )
                ut.cprint(
                    'ccfit2 relaxation',
                    'green'
                )
                ut.cprint(
                    'on each file',
                    'black_yellowbg'
                )
                sys.exit()

        else:
            try:
                datasets = relax.HDataset.from_ac_dc(models)
            except TypeError:
                ut.cprint(
                    'Relaxation fitting of double tau models is unsupported',
                    'black_yellowbg'
                )
                ut.cprint(
                    'Split your data into individual .csv files using split_rates', # noqa
                    'black_yellowbg'
                )
                ut.cprint(
                    'and run ccfit2 relaxation',
                    'black_yellowbg'
                )
                sys.exit()

        for d_it, dataset in enumerate(datasets):

            if any(val < 0 for val in dataset.dep_vars):
                ut.cprint(
                    f'Warning: Negative {ind_var_name} value found in dataset',
                    'black_yellowbg'
                )
                # Print the negative value
                neg_vals = dataset.dep_vars[dataset.dep_vars < 0.]
                for val in neg_vals:
                    ut.cprint(
                        f'Negative {ind_var_name} value: {val:.4e} {ind_var_unit}', # noqa
                        'black_yellowbg'
                    )
                if ind_var_name == 'temperature':
                    ut.red_exit('Check input data')
                else:
                    ut.cprint('Setting to zero', 'black_yellowbg')
                    dataset.dep_vars[dataset.dep_vars < 0.] = 0.

            # Ask user to select relaxation processes to fit, select
            # initial values, and fix parameters if desired
            rmodels, fit_vars, fix_vars, exited = relax.interactive_fitting(
                dataset, app
            )
            if uargs.x_var == 'T':
                if exited:
                    if len(unique_dc_fields) > 1 and f_it != len(unique_dc_fields) - 1: # noqa
                        ut.cprint(
                            '\n Skipping to next field',
                            'black_yellowbg'
                        )
                        continue
                    elif len(datasets) > 1 and d_it != len(datasets) - 1:
                        ut.cprint(
                            '\n Skipping to next dataset',
                            'black_yellowbg'
                        )
                        continue
                    else:
                        ut.cprint('\n Exiting fit window', 'red')
                        sys.exit(1)
            else:
                if exited:
                    if len(unique_temperatures) > 1 and f_it != len(unique_temperatures) - 1: # noqa
                        ut.cprint(
                            '\n Skipping to next field',
                            'black_yellowbg'
                        )
                        continue
                    elif len(datasets) > 1 and d_it != len(datasets) - 1:
                        ut.cprint(
                            '\n Skipping to next dataset',
                            'black_yellowbg'
                        )
                        continue
                    else:
                        ut.cprint('\n Exiting fit window', 'red')
                        sys.exit(1)

            if not any(len(fv) for fv in fit_vars):
                ut.cprint('\n Error: All parameters fixed', 'red')
                sys.exit(1)
            if uargs.x_var == 'T':
                # Create MultiLogModel as combination of individual models
                multilogmodel = relax.MultiLogTauTModel(
                    rmodels,
                    fit_vars,
                    fix_vars
                )
            else:
                # Create MultiLogModel as combination of individual models
                multilogmodel = relax.MultiLogTauHModel(
                    rmodels,
                    fit_vars,
                    fix_vars
                )

            # Fit to experiment
            multilogmodel.fit_to(dataset)

            model_names = ''
            for _mod in multilogmodel.logmodels:
                model_names += '{}_'.format(
                    _mod.NAME.lower().replace(' ', '-').replace('*', 'x')
                )

            if uargs.x_var == 'T':
                # Plot data
                base_filename = f'relaxation_{dc_field:.1f}Oe_{model_names}'
                # add number if more than one dataset is fitted
                if len(datasets) > 1:
                    base_filename = '{}_set_{:d}'.format(
                        base_filename,
                        d_it + 1
                    )

            else:
                # Plot data
                base_filename = f'relaxation_{temperature:.1f}K_{model_names}'
                # add number if more than one dataset is fitted
                if len(datasets) > 1:
                    base_filename = '{}_set_{:d}'.format(
                        base_filename,
                        d_it + 1
                    )

            base_filename = os.path.join(user_cfg.results_dir, base_filename)

            fit_plot_filename = f'{base_filename}fitted{PFF}'
            residuals_plot_filename = f'{base_filename}residuals{PFF}'

            relax.plot_fitted_rates(
                dataset,
                multilogmodel,
                save=True,
                show=True,
                save_name=fit_plot_filename
            )

            relax.plot_rate_residuals(
                dataset,
                multilogmodel,
                save=True,
                show=True,
                save_name=residuals_plot_filename
            )

            # Save raw data
            fit_filename = '{}params.csv'.format(base_filename)
            model_filename = '{}model.csv'.format(base_filename)

            relax.write_model_params(multilogmodel, fit_filename)
            relax.write_model_data(
                dataset,
                multilogmodel,
                model_filename,
                delimiter=CSV_DELIMITER
            )

    return


class FitFixAction(argparse.Action):
    '''
    Custom argparse action for Fit and Fix variable optional arguments
    '''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __call__(self, parser, namespace, values: list[str], option_string):
        '''
        When called by argparse, checks the fit and fit variables have
        two entries, the first is either string 'fit' or 'fix'
        and second is either:
        string 'guess'
        a float
        or string containing filename of parameters file
        '''
        if values[0].lower() not in ['fit', 'fix']:
            parser.error('First option must be fit or fix')
        elif ut.can_float(values[1]):
            values[1] = float(values[1])
        elif isinstance(values[1], str):
            # Check file exists
            if values[1].lower() == 'guess':
                pass
            elif not os.path.exists(values[1]):
                parser.error(
                    'Second option must be either: the word \'guess\', a filename, or a value' # noqa
                )

        # Add True to signify that the user added this argument to their cli
        # call
        values.append(True)

        setattr(namespace, self.dest, values)


class MultiAction(argparse.Action):
    '''
    Custom argparse action for multiple variable optional arguments
    '''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __call__(self, parser, namespace, values: list[str], option_string):
        '''
        When called by argparse, checks the variables have
        three entries, the first two are strings containing filenames
        and the third is either:
        a float
        or string containing filename of parameters file
        '''
        if not os.path.exists(values[0]):
            parser.error(
                'First option must be a filename'
            )
        elif not os.path.exists(values[1]):
            parser.error(
                'Second option must be a filename'
            )
        elif ut.can_float(values[2]):
            values[2] = float(values[2])
        else:
            parser.error(
                'Third option must be a float'
            )

        setattr(namespace, self.dest, values)


class DiffAction(argparse.Action):
    '''
    Custom argparse action for optional arguments which are can be floats or
    filenames
    '''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __call__(self, parser, namespace, value, option_string):
        '''
        When called by argparse, checks the variables have
        one entry, either:
        a float, or string containing filename of parameters file
        '''

        if ut.can_float(value):
            value = float(value)
        elif isinstance(value, str):
            # Check file exists
            if not os.path.exists(value):
                parser.error(
                    'Second option must be either: a value or a filename'
                )

        setattr(namespace, self.dest, value)


def extract_dc_param_args(arg_val: str | float,
                          n_rep: int) -> list[str | float]:
    '''
    Converts input fit/fix value option into list of n_rep entries containing
    values as 'guess', a float, or floats read from file

    Parameters
    ----------
    arg_val: str | float
        Fit/Fix value, either string 'guess', a float, or a filename string
    n_rep: int
        Number of times to repeat 'guess' or float

    Returns
    -------
    list[str | float]
        list of n_rep entries containing values as 'guess', a float,
        or floats read from file
    '''

    if arg_val == 'guess':
        output = ['guess'] * n_rep
    elif isinstance(arg_val, float):
        output = [arg_val] * n_rep
    else:
        encoding = ut.detect_encoding(arg_val)
        output = np.loadtxt(arg_val, skiprows=1, usecols=0, encoding=encoding)
        if len(output) != n_rep:
            ut.cprint(
                f'Error: File {arg_val} length does not match number of experiments', # noqa 
                'red'
            )
            sys.exit(1)

    return output


def extract_dc_field_calibration_args(arg_val: str | float,
                                      n_rep: int) -> list[str | float]:
    '''
    Converts input MultiAction value option into list of n_rep entries
    containing values as a float or floats read from file

    Parameters
    ----------
    arg_val: str | float
        Fit/Fix value, either a float or a filename string
    n_rep: int
        Number of times to repeat float

    Returns
    -------
    list[str | float]
        list of n_rep entries containing values as a float,
        or floats read from file
    '''

    if isinstance(arg_val, float):
        output = [arg_val] * n_rep
    else:
        encoding = ut.detect_encoding(arg_val)
        output = np.loadtxt(arg_val, skiprows=0, usecols=0, encoding=encoding)
        if len(output) != n_rep:
            ut.cprint(
                f'Error: File {arg_val} length does not match number of experiments', # noqa 
                'red'
            )
            sys.exit(1)

    return output


def calibrate_meq(sat_file: str, calc_file: str, sat_field: float,
                  n_exp: int) -> list[str | float]:
    '''
    Calibrates M_eq using theoretically calculated equilibrium magnetisation
    data as a function of field and the experimentally determined magnetisation
    at saturation

    Parameters
    ----------
    sat_file: str
        Name of file containing experimental saturation fields
    calc_file: str
        Name of file containing theoretical magnetisation curve
    sat_field: float
        Value for saturation field for all experiments.
    n_exp: int
        Number of experiments to expect in file

    Returns
    -------
    list[float]
        Calibrated values of M_eq, one per experiment
    '''

    encoding0 = ut.detect_encoding(sat_file)
    encoding1 = ut.detect_encoding(calc_file)
    sat_mag_data = np.loadtxt(sat_file, skiprows=0, encoding=encoding0)
    calc_mag_data = np.loadtxt(calc_file, skiprows=0, encoding=encoding1)

    if len(sat_mag_data) != n_exp:
        ut.cprint(
            f'Error: File {sat_file} length does not match number of experiments', # noqa 
            'red'
        )
        sys.exit(1)

    # Pick out calculated moment at experimental saturation field
    calc_sat_pos = np.where(calc_mag_data == sat_field)
    calc_sat = calc_mag_data[calc_sat_pos[0], 1][0]

    # create empty list to fill with M_eq values
    calib_Meq = []
    for i, sats in enumerate(sat_mag_data[:, 0]):
        # copy theoretically calculated Meq
        calib_mag_data = np.copy(calc_mag_data)

        # Calculate calibration factor
        # as ratio of calculated moment verses experimental moment at
        # experimental saturation field
        factor = calc_sat / sat_mag_data[i, 1]

        # apply calibration factor to experimental moment
        calib_mag_data[:, 1] /= factor

        # pick out calibrated M_eq for each experiment
        calib_Meq_pos = np.where(calib_mag_data == sats)
        calib_Meq.append(calib_mag_data[calib_Meq_pos[0], 1][0])

    # Catch empty list of calibrated values
    if not len(calib_Meq):
        ut.cprint(
            'Error: M_eq calibration failed. Please check input',
            'red'
        )
        sys.exit(1)

    return calib_Meq


def dc_mode_func(uargs):
    '''
    Wrapper function for command line interface call to dc mode

    Parameters
    ----------
    uargs : argparser object
        command line arguments

    Returns
    -------
    None
    '''

    # Parse model parameter arguments to enforce mutually exclusive groups
    stretched_par_args = [uargs.taustar, uargs.beta]
    double_par_args = [
        uargs.taustar1, uargs.beta1, uargs.taustar2,
        uargs.beta2, uargs.frac
    ]

    # Check if double parameters specified with stretched model
    if uargs.model == 'stretched':
        if any(len(par_arg) == 3 for par_arg in double_par_args):
            ut.cprint(
                'Error: Specified parameters do not match --model stretched',
                'red'
            )
            sys.exit(1)

    # Check if stretched parameters specified with double model
    if uargs.model == 'double':
        if any(len(par_arg) == 3 for par_arg in stretched_par_args):
            ut.cprint(
                'Error: Specified parameters do not match --model double',
                'red'
            )
            sys.exit(1)

    # Make QT application - this MUST happen before any matplotlib/qt
    # plots are made
    app = QtWidgets.QApplication([])

    # Object to store user configuration, paths, etc.
    user_cfg = ut.UserConfig()
    user_cfg.file_name = uargs.input_file

    # Use glob to expand wildcards if on windows
    if 'nt' in os.name and '*' in user_cfg.file_name[0]:
        user_cfg.file_name = glob(user_cfg.file_name[0])

    # Set number of threads
    num_threads = min(NUM_THREADS, len(user_cfg.file_name))
    print_num_threads(num_threads)

    # Get file header indices and names
    # enforce specific moment header if user requests
    header_dict = dc.HEADERS_SUPPORTED
    if uargs.moment_header == 'moment':
        header_dict['moment'] = ['Moment (emu)']
    elif uargs.moment_header == 'fixed':
        header_dict['moment'] = ['DC Moment Fixed Ctr (emu)']
    elif uargs.moment_header == 'free':
        header_dict['moment'] = ['DC Moment Free Ctr (emu)']

    # Check input file headers in parallel
    check_mag_files(
        user_cfg.file_name,
        header_dict,
        uargs.data_header,
        num_threads
    )

    # Load each point from file as a measurement in parallel
    pool = mp.Pool(num_threads)
    iterables = [
        (file_name, uargs.data_header)
        for file_name in user_cfg.file_name
    ]
    all_measurements = pool.starmap(
        dc.Measurement.from_file,
        iterables,
        chunksize=None
    )

    # Close Pool and let all the processes complete
    pool.close()
    pool.join()

    _all_measurements = []

    # Trim measurements to ignore values at saturating and
    # decaying field
    if not uargs.no_field_discard:
        for measurements in all_measurements:
            diff_thresh = uargs.dfield_thresh
            # Forward difference of field
            field_diff = np.abs(
                np.diff(
                    [measurement.dc_field for measurement in measurements]
                )
            )
            # Flip field diff and find first value > threshold, then index to
            # unflipped
            n_pts = len(measurements)
            cut_at = n_pts - np.argmax(np.flip(field_diff) > diff_thresh) - 1

            # Cut to stable field values only
            measurements = measurements[cut_at:]
            _all_measurements += measurements

    # Replace all measurements with trimmed measurements
    all_measurements = _all_measurements

    ut.cprint('.... Done!', 'black_bluebg')

    # Group measurements into sublists of experiments
    # Where order of dimensions dc field strength
    # and temperature depend on choice of x_var
    all_experiments_sep = dc.Experiment.from_measurements(
        all_measurements,
        temp_thresh=uargs.temp_thresh,
        field_thresh=uargs.field_thresh,
        x_var=uargs.x_var,
        cut_moment=uargs.cut_moment
    )

    # State independent variable
    if uargs.x_var == 'T':
        ind_var_name = 'temperature'
        ind_var_unit = 'K'
    elif uargs.x_var == 'H':
        ind_var_name = 'field'
        ind_var_unit = 'Oe'

    ut.cprint(f'\nIndependent variable is {ind_var_name}', 'green')

    # Convert measured dc field values to calibrated field values
    if uargs.field_calibration is not None:
        for experiments in all_experiments_sep:
            actual_fields = extract_dc_field_calibration_args(
                uargs.field_calibration, len(experiments)
            )
            for experiment, field in zip(experiments, actual_fields):
                experiment.dc_fields[:] = field

    # Plot moment and dc field against time and exit if requested
    # one plot for each set of isothermal or isofield experiments
    if uargs.process == 'plot':

        if uargs.x_var == 'T':
            iso_unit = 'Oe'
            iso_var = 'H'
            iso_var_full = 'field'

        elif uargs.x_var == 'H':
            iso_var = 'T'
            iso_var_full = 'thermal'
            iso_unit = 'K'

        ut.cprint(
            (
                '\nPlotting moment and field against time for each '
                f'set of iso{iso_var_full} experiments...'
            ),
            'green'
        )

        for experiments in all_experiments_sep:
            # If independent variable is Temperature
            # then experiments are isofield
            if uargs.x_var == 'T':
                if uargs.field_calibration is not None:
                    iso_val = actual_fields[0]
                else:
                    iso_val = experiments[0].rep_dc_field

            # If independent variable is DC Field
            # then experiments are isothermal
            elif uargs.x_var == 'H':
                iso_val = experiments[0].rep_temperature

            # Put isovalue and isovariable name in filename for decays plot
            file_name = 'raw_decays_{:.2f}_{}{}'.format(
                iso_val,
                iso_unit,
                PFF
            )
            file_name = os.path.join(user_cfg.results_dir, file_name)

            # Plot each iso-set of experimental decays and field values
            dc.plot_decays_and_fields(
                experiments, show=True, save=True, iso_var=iso_var,
                x_scale=uargs.plot_axes[0], y_scale=uargs.plot_axes[1],
                save_name=file_name
            )

        ut.cprint('.... Done!', 'green')

        sys.exit()

    unique_dc_fields = np.unique(
        [experiments[0].rep_dc_field for experiments in all_experiments_sep]
    )

    unique_temperatures = np.unique(
        [experiments[0].rep_temperature for experiments in all_experiments_sep]
    )

    ut.cprint('\n Fitting DC Decays\n', 'black_bluebg')
    # Fit decays to exponential function

    # Create models, one per experiment
    # specifying type of model, and which parameters will
    # be fitted and which are fixed

    for experiments, dc_field, temperature in zip(all_experiments_sep, unique_dc_fields, unique_temperatures): # noqa
        models: list[dc.Model] = []
        if uargs.model == 'stretched':
            parargs = [
                uargs.taustar, uargs.beta, uargs.M_eq,
                uargs.M_0, uargs.t_offset
            ]

            names = [
                'tau*', 'beta', 'm_eq', 'm_0', 't_offset'
            ]

            # Convert each fit parameter into a list with n_input_files entries
            all_vars = {
                name: [
                    arg[0], extract_dc_param_args(arg[1], len(experiments))
                ]
                for name, arg in zip(names, parargs)
            }

            all_fit_vars = {
                name: value[1]
                for name, value in all_vars.items()
                if 'fit' in value[0]
            }

            all_fix_vars = {
                name: value[1]
                for name, value in all_vars.items()
                if 'fix' in value[0]
            }

            # Calibrate M_eq based on theoretical values
            if uargs.M_eq_calibration is not None:
                all_fix_vars['m_eq'] = calibrate_meq(
                    *uargs.M_eq_calibration,
                    len(experiments)
                )

            model_to_use = dc.ExponentialModel
            for it, experiment in enumerate(experiments):
                fit_vars = {
                    key: all_fit_vars[key][it]
                    for key in all_fit_vars.keys()
                }
                fix_vars = {
                    key: all_fix_vars[key][it]
                    for key in all_fix_vars.keys()
                }
                models.append(model_to_use(fit_vars, fix_vars, experiment))

        elif uargs.model == 'double':

            parargs = [
                uargs.taustar1, uargs.taustar2, uargs.beta1,
                uargs.beta2, uargs.M_eq,
                uargs.M_0, uargs.t_offset, uargs.frac
            ]

            names = [
                'tau*1', 'tau*2', 'beta1', 'beta2', 'm_eq', 'm_0', 't_offset',
                'frac'
            ]

            # Convert each fit parameter into a list with n_input_files entries
            all_vars = {
                name: [
                    arg[0], extract_dc_param_args(arg[1], len(experiments))
                ]
                for name, arg in zip(names, parargs)
            }

            all_fit_vars = {
                name: value[1]
                for name, value in all_vars.items()
                if 'fit' in value[0]
            }

            all_fix_vars = {
                name: value[1]
                for name, value in all_vars.items()
                if 'fix' in value[0]
            }

            # Calibrate M_eq based on theoretical values
            if uargs.M_eq_calibration is not None:
                all_fix_vars['m_eq'] = calibrate_meq(
                    *uargs.M_eq_calibration,
                    len(all_experiments_sep)
                )
            model_to_use = dc.DoubleExponentialModel
            for it, experiment in enumerate(experiments):
                fit_vars = {
                    key: all_fit_vars[key][it]
                    for key in all_fit_vars.keys()
                }
                fix_vars = {
                    key: all_fix_vars[key][it]
                    for key in all_fix_vars.keys()
                }
                models.append(model_to_use(fit_vars, fix_vars, experiment))

        # For each model and accompanying experiment, fit model
        for model, experiment in zip(models, experiments):
            if uargs.verbose:
                print('Fit parameter guesses are:')
                print(model.fit_vars)
                print('Fixed parameters are:')
                print(model.fix_vars)
                print()
            # Fit model
            model.fit_to(experiment)

            # Plot decay with fit
            if model.fit_status:
                if uargs.decay_plots in ['on', 'show', 'save']:
                    file_name = 'fitted_decay_{:.2f}K_{:.1f}Oe{}'.format(
                        experiment.rep_temperature,
                        experiment.dc_fields[-1],
                        PFF
                    )
                    file_name = os.path.join(user_cfg.results_dir, file_name)

                    dc.plot_fitted_decay(
                        experiment=experiment, model=model,
                        show=_SHOW_CONV[uargs.decay_plots],
                        save=_SAVE_CONV[uargs.decay_plots],
                        save_name=file_name, x_scale=uargs.plot_axes[0],
                        y_scale=uargs.plot_axes[1],
                        show_params=uargs.hide_params
                    )
                    plt.close('all')
            else:
                ut.cprint(
                    (
                        f'\n Cannot save/show plot for T = {model.temperature}'
                        f'K and {model.dc_field} Oe as fit has failed'
                    ),
                    'black_yellowbg'
                )

        # Check for total failure
        if all(not model.fit_status for model in models):
            ut.cprint('\n    ***Error***:', 'red')
            if uargs.x_var == 'T':
                ut.cprint(
                    'At {:.5f} Oe, all fits failed.'.format(dc_field),
                    'red'
                )
                # Exit if only one field
                if len(unique_dc_fields) == 1:
                    sys.exit(1)
                # else go to next field
                else:
                    continue
            else:
                ut.cprint(
                    'At {:.2f} K, all fits failed.'.format(temperature),
                    'red'
                )
                # Exit if only one temperature
                if len(unique_temperatures) == 1:
                    sys.exit(1)
                # else go to next temperature
                else:
                    continue

        if uargs.x_var == 'T':
            if uargs.field_calibration is not None:
                x_var = actual_fields[0]
            else:
                x_var = experiments[0].rep_dc_field
        elif uargs.x_var == 'H':
            x_var = experiments[0].rep_temperature

        # Create output files
        if uargs.x_var == 'T':
            base_filename = 'dc_{:.2f}Oe_{}'.format(
                x_var,
                model.NAME.lower().replace(' ', '_')
            )
        else:
            base_filename = 'dc_{:.2f}K_{}'.format(
                x_var,
                model.NAME.lower().replace(' ', '_')
            )
        base_filename = os.path.join(user_cfg.results_dir, base_filename)

        # Save parameters to file
        dc.write_model_params(
            models,
            file_name='{}params.csv'.format(base_filename),
            delimiter=CSV_DELIMITER
        )
        # Save modelled data to file
        dc.write_model_data(
            experiments,
            models,
            file_name='{}model.csv'.format(base_filename),
            delimiter=CSV_DELIMITER
        )

        # Exit if only one temperature/field for all points
        if uargs.x_var == 'T':
            if len(np.unique([e.rep_temperature for e in experiments])) == 1:
                ut.cprint(
                    '\n Did you mean to select field as x_var?\n', 'red'
                )
                sys.exit(1)
        elif uargs.x_var == 'H':
            if len(np.unique([e.rep_dc_field for e in experiments])) == 1:
                ut.cprint(
                    '\n Did you mean to select temperature as x_var?\n', 'red'
                )
                sys.exit(1)

        # If only decays then move to next set of experiments
        if uargs.process == 'decays':
            continue
        if uargs.x_var == 'T':
            ut.cprint(
                '\n Fitting relaxation rate vs temperature\n', 'black_bluebg'
                )
        else:
            ut.cprint(
                '\n Fitting relaxation rate vs field\n', 'black_bluebg'
                )

        # Create dataset to store relaxation rate, temperature and field data
        try:
            if uargs.x_var == 'T':
                datasets = relax.TDataset.from_ac_dc(models)
            else:
                datasets = relax.HDataset.from_ac_dc(models)
        except TypeError:
            ut.cprint(
                'Relaxation fitting of double tau models is unsupported',
                'black_yellowbg'
            )
            ut.cprint(
                'Split your data into individual .csv files using split_rates',
                'black_yellowbg'
            )
            ut.cprint(
                'and run ccfit2 relaxation',
                'black_yellowbg'
            )
            sys.exit()

        for d_it, dataset in enumerate(datasets):

            if any(val < 0 for val in dataset.dep_vars):
                ut.cprint(
                    f'Warning: Negative {ind_var_name} value found in dataset',
                    'black_yellowbg'
                )
                # Print the negative value
                neg_vals = dataset.dep_vars[dataset.dep_vars < 0.]
                for val in neg_vals:
                    ut.cprint(
                        f'Negative {ind_var_name} value: {val:.4e} {ind_var_unit}', # noqa
                        'black_yellowbg'
                    )
                if ind_var_name == 'temperature':
                    ut.red_exit('Check input data')
                else:
                    ut.cprint('Setting to zero', 'black_yellowbg')
                    dataset.dep_vars[dataset.dep_vars < 0.] = 0.

            # Ask user to select relaxation processes to fit, select
            # initial values, and fix parameters if desired
            rmodels, fit_vars, fix_vars, exited = relax.interactive_fitting(
                dataset, app
            )

            if exited:
                ut.cprint('\n Exiting fit window', 'red')
                sys.exit(1)

            if not any(len(fv) for fv in fit_vars):
                ut.cprint('\n Error: All parameters fixed', 'red')
                sys.exit(1)

            # Create MultiLogModel as combination of individual models
            if uargs.x_var == 'T':
                multilogmodel = relax.MultiLogTauTModel(
                    rmodels,
                    fit_vars,
                    fix_vars
                )
            else:
                multilogmodel = relax.MultiLogTauHModel(
                    rmodels,
                    fit_vars,
                    fix_vars
                )

            # Fit model to dataset
            multilogmodel.fit_to(dataset)

            model_names = ''
            for _mod in multilogmodel.logmodels:
                model_names += '{}_'.format(
                    _mod.NAME.lower().replace(' ', '-').replace('*', 'x')
                )
            # Plot data

            # Create filename based on field or temperature

            # If xvar is temperature, specify fixed field in filename
            if uargs.x_var == 'T':
                if uargs.field_calibration is not None:
                    base_filename = 'relaxation_{:.2f}Oe_{}'.format(
                        actual_fields[0],
                        model_names
                    )
                else:
                    base_filename = 'relaxation_{:.2f}Oe_{}'.format(
                        dc_field,
                        model_names
                    )
            # If xvar is field, specify fixed temperature in filename
            else:
                base_filename = 'relaxation_{:.2f}K_{}'.format(
                    temperature,
                    model_names
                )
            # add number if more than one dataset is fitted
            if len(datasets) > 1:
                base_filename = '{}_set_{:d}'.format(base_filename, d_it + 1)
            base_filename = os.path.join(user_cfg.results_dir, base_filename)

            fit_plot_filename = f'{base_filename}fitted{PFF}'
            residuals_plot_filename = f'{base_filename}residuals{PFF}'

            # Plot fitted model and experimental rates
            relax.plot_fitted_rates(
                dataset,
                multilogmodel,
                save=True,
                save_name=fit_plot_filename
            )

            # Plot log10(rate) residuals between fitted model and experimental
            # rates
            relax.plot_rate_residuals(
                dataset,
                multilogmodel,
                save=True,
                save_name=residuals_plot_filename
            )

            fit_filename = '{}params.csv'.format(base_filename)
            model_filename = '{}model.csv'.format(base_filename)

            relax.write_model_params(multilogmodel, fit_filename)
            relax.write_model_data(
                dataset,
                multilogmodel,
                model_filename,
                delimiter=CSV_DELIMITER
            )

    return


def relaxation_mode_func(uargs):
    '''
    Wrapper function for command line interface call to relaxation mode

    Parameters
    ----------
    uargs : argparser object
        command line arguments

    Returns
    -------
    None

    '''

    # Make QT application - this MUST happen before any matplotlib/qt
    # plots are made
    app = QtWidgets.QApplication([])

    # Use glob to expand wildcards if on windows
    if 'nt' in os.name and '*' in uargs.input_files[0]:
        uargs.input_files = glob(uargs.input_files[0])

    if any('.out' in fn for fn in uargs.input_files):
        ut.cprint(
            'Warning: .out files are deprecated',
            'black_yellowbg'
        )
        ut.cprint(
            'convert to .csv or use --filetype legacy',
            'black_yellowbg'
        )
        ut.cprint(
            'else unpredicted behaviour may occur',
            'black_yellowbg'
        )

    # Set temperature or field dependence of rates
    if uargs.x_var == 'T':
        _dataset_class = relax.TDataset
        _multilogmodel_class = relax.MultiLogTauTModel
        ind_var_name = 'temperature'
        ind_var_unit = 'K'
    else:
        _dataset_class = relax.HDataset
        _multilogmodel_class = relax.MultiLogTauHModel
        ind_var_name = 'field'
        ind_var_unit = 'Oe'

    ut.cprint(
        f'\n Fitting relaxation rate vs {ind_var_name}\n',
        'black_bluebg'
    )

    _parsers = {
        'rate': _dataset_class.from_rate_files,
        'legacy': _dataset_class._from_ccfit2_files,
        'ccfit2': _dataset_class.from_ccfit2_csv
    }

    # Create dataset which stores relaxation rate and temperature data
    try:
        dataset = _parsers[uargs.filetype](uargs.input_files)
    except ValueError as ve:
        ut.cprint(str(ve), 'red')
        exit()

    # Check for negative dependent variable values in dataset
    # and set to zero
    if any(val < 0 for val in dataset.dep_vars):
        ut.cprint(
            f'Warning: Negative {ind_var_name} value found in dataset',
            'black_yellowbg'
        )
        # Print the negative value
        neg_vals = dataset.dep_vars[dataset.dep_vars < 0.]
        for val in neg_vals:
            ut.cprint(
                f'Negative {ind_var_name} value: {val:.4e} {ind_var_unit}',
                'black_yellowbg'
            )
        if ind_var_name == 'temperature':
            ut.red_exit('Check input data')
        else:
            ut.cprint('Setting to zero', 'black_yellowbg')
            dataset.dep_vars[dataset.dep_vars < 0.] = 0.

    # Plot rates and exit
    if uargs.process == 'plot':
        if uargs.plot_type in ['rate', 'both']:
            relax.plot_rates(
                dataset,
                save=True,
                save_name=f'relaxation_rates{PFF}'
            )
        if uargs.plot_type in ['time', 'both']:
            relax.plot_times(
                dataset,
                save=True,
                save_name=f'relaxation_times{PFF}'
            )
        sys.exit()

    # Disable weighting of residuals by setting uncertainties
    # as empty arrays
    if uargs.no_weights:
        dataset.lograte_pm = []

    # Ask user to select relaxation processes to fit, select
    # initial values, and fix parameters if desired
    rmodels, fit_vars, fix_vars, exited = relax.interactive_fitting(
        dataset, app
    )

    if exited:
        ut.cprint('\n Exiting fit window', 'red')
        sys.exit(1)

    if not any(len(fv) for fv in fit_vars):
        ut.cprint('\n Error: All parameters fixed', 'red')
        sys.exit(1)

    # Create MultiLogModel as combination of individual models
    multilogmodel = _multilogmodel_class(
        rmodels,
        fit_vars,
        fix_vars
    )

    # Fit to experiment
    multilogmodel.fit_to(dataset)

    # Construct string from model names
    model_names = ''
    for _mod in multilogmodel.logmodels:
        model_names += '{}_'.format(
            _mod.NAME.lower().replace(' ', '-').replace('*', 'x')
        )
    # Plot fitted model and experiment
    if uargs.plot_type in ['rate', 'both']:
        relax.plot_fitted_rates(
            dataset,
            multilogmodel,
            save=True,
            save_name=f'relaxation_{model_names}fitted_rates{PFF}',
            show_params=uargs.hide_params
        )
    if uargs.plot_type in ['time', 'both']:
        relax.plot_fitted_times(
            dataset,
            multilogmodel,
            save=True,
            save_name=f'relaxation_{model_names}fitted_times{PFF}',
            show_params=uargs.hide_params
        )
    # Plot log10(rate) residuals between dataset and model
    relax.plot_rate_residuals(
        dataset,
        multilogmodel,
        save=True,
        save_name=f'relaxation_{model_names}residuals{PFF}'
    )

    fit_filename = f'relaxation_{model_names}params.csv'
    model_filename = f'relaxation_{model_names}model.csv'

    relax.write_model_params(multilogmodel, fit_filename)
    relax.write_model_data(
        dataset,
        multilogmodel,
        model_filename,
        delimiter=CSV_DELIMITER
    )

    return


def waveform_mode_func(uargs):
    '''
    Wrapper function for command line interface call to waveform mode

    Parameters
    ----------
    uargs : argparser object
        command line arguments

    Returns
    -------
    None

    '''

    user_cfg = ut.UserConfig()
    user_cfg.file_name = uargs.input_file

    # Use glob to expand wildcards if on windows
    if 'nt' in os.name and '*' in user_cfg.file_name[0]:
        user_cfg.file_name = glob(user_cfg.file_name[0])

    # Set number of threads
    num_threads = min(NUM_THREADS, len(user_cfg.file_name))
    print_num_threads(num_threads)

    # Check input file headers in parallel
    check_mag_files(
        user_cfg.file_name,
        wfrm.HEADERS_SUPPORTED,
        uargs.data_header,
        num_threads
    )

    # Load each point from file as a measurement in parallel
    pool = mp.Pool(num_threads)
    iterables = [
        (file_name, uargs.data_header, uargs.field_window, uargs.temp_thresh)
        for file_name in user_cfg.file_name
    ]
    all_experiments = pool.starmap(
        wfrm.Experiment.from_files,
        iterables,
        chunksize=None
    )

    # Manually sort by temperature
    # since starmap doesnt order all_experiments
    all_experiments = ut.flatten_recursive(all_experiments)

    all_experiments = sorted(
        all_experiments,
        key=lambda k: k.rep_temperature
    )

    # Find mean temperature values
    _, split_ind = ut.find_mean_values(
        [
            e.rep_temperature
            for e in all_experiments
        ],
        thresh=uargs.temp_thresh
    )

    # and split into sublists grouped by mean temperature
    all_experiments: list[list[wfrm.Experiment]] = np.split(
        all_experiments,
        split_ind
    )

    # Plot raw data if requested
    # separate plot for each temperature
    if uargs.process == 'plot_raw':
        for experiments in all_experiments:
            wfrm.plot_raw_moment_field(
                experiments,
                window_title=f'Raw Waveform Data at {experiments[0].rep_temperature:} K' # noqa
            )

    ac_experiments = []

    # Fourier transform each temperature's set of experiments
    # and create corresponding AC Experiment to store AC data
    for experiments in all_experiments:
        # Carry out Fourier transform of moment and field
        ft_experiments = [
            wfrm.FTExperiment.from_experiment(experiment)
            for experiment in experiments
        ]

        # Plot fourier transform vs and moment/field if requested
        for ft_exp, exp in zip(ft_experiments, experiments):

            # FT Plot
            _save_name = 'waveform_FT_{:.3f}_mHz_{:.2f}_K{}'.format(
                1 / ft_exp.period * 1000,
                exp.rep_temperature,
                PFF
            )
            if uargs.ft_plots != 'off':
                fig, _ = wfrm.plot_ft(
                    ft_exp,
                    show=False,
                    save=_SAVE_CONV[uargs.ft_plots],
                    save_name=os.path.join(
                        user_cfg.results_dir,
                        _save_name
                    ),
                    window_title='Fourier Transformed Data for {:.5f} Hz'.format( # noqa
                        1 / ft_exp.period
                    ),
                    verbose=True
                )
                # Delete fig if not to be shown
                if not _SHOW_CONV[uargs.ft_plots]:
                    plt.close(fig)

            # Moment and Field plot
            _save_name = 'waveform_moment_field_{:.3f}_mHz_{:.2f}_K{}'.format(
                1 / ft_exp.period * 1000,
                exp.rep_temperature,
                PFF
            )
            if uargs.mf_plots != 'off':
                fig, _ = wfrm.plot_moment_and_field(
                    exp,
                    show=False,
                    save=_SAVE_CONV[uargs.mf_plots],
                    save_name=os.path.join(
                        user_cfg.results_dir,
                        _save_name
                    ),
                    window_title='Waveform Data for {:.5f} Hz'.format(
                        1 / ft_exp.period
                    ),
                    verbose=True
                )
                # Delete fig if not to be shown
                if not _SHOW_CONV[uargs.mf_plots]:
                    plt.close(fig)

            # Show plots
            if _SHOW_CONV[uargs.mf_plots] or _SHOW_CONV[uargs.ft_plots]:
                plt.show()
                plt.close('all')

        # Create ac.Experiment object from Fourier transform results
        ac_experiments.append(
            wfrm.FTExperiment.create_ac_experiment(
                ft_experiments, experiments, mass=None, mw=None
            )
        )

    if uargs.susc_plot in ['on', 'show', 'save']:
        # Plot susceptibility data
        _save_name = f'waveform_susc{PFF}'
        ac.plot_susceptibility(
            ac_experiments,
            show=_SHOW_CONV[uargs.susc_plot],
            save=_SAVE_CONV[uargs.susc_plot],
            save_name=os.path.join(user_cfg.results_dir, _save_name),
            verbose=True
        )
        plt.close('all')

    # Create magnetometer file style input for ccfit2 ac mode
    _file_name = os.path.join(
        user_cfg.results_dir, 'waveform_ccfit2_ac_input.out'
    )

    ac.save_ac_magnetometer_file(
        ac_experiments,
        file_name=_file_name,
        verbose=False
    )

    ut.cprint(' Use this file as input to ccfit2 ac:', 'green')
    ut.cprint(f' {_file_name}', 'blue')

    return


class CustomErrorArgumentParser(argparse.ArgumentParser):
    '''
    Custom ArgumentParser to handle errors and print usage\n
    This is required to avoid the default behavior of argparse which
    modifies the usage message when it prints, conflicting with the preset
    values used in the subparsers.
    '''
    def error(self, message):
        self.print_usage(sys.stderr)
        sys.stderr.write(f"error: {message}.\n")
        sys.stderr.write("       Use -h to see all options.\n")
        sys.exit(2)


def read_args(arg_list=None):
    '''
    Parser for command line arguments. Uses subparsers for individual programs

    Parameters
    ----------
    args : argparser object
        command line arguments

    Returns
    -------
    None

    '''

    description = '''
    This is the command line interface to ccfit2.\n
    A program for fitting relaxation data from
    AC and DC magnetometry experiments.
    '''

    epilog = 'Type\n'
    epilog += ut.cstring('ccfit2 <subprogram> -h\n', 'cyan')
    epilog += 'for help with a specific subprogram.\n'

    for i, arg in enumerate(sys.argv):
        if (arg[0] == '-') and arg[1].isdigit():
            sys.argv[i] = f' {arg}'

    parser = CustomErrorArgumentParser(
        description=description,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=epilog,
        usage=ut.cstring(
            'ccfit2 <subprogram> [options]\n',
            'cyan'
        )
    )
    parser._positionals.title = 'Subprograms'

    # create the top-level parser
    subparsers = parser.add_subparsers(dest='exe_mode')

    # AC mode
    description_ac = '''
    Extract relaxation times from AC susceptibility data and
    (optionally) fit the resulting relaxation profile.
    '''

    ac_parser = subparsers.add_parser(
        'ac',
        description=description_ac,
        formatter_class=argparse.RawTextHelpFormatter,
        usage=ut.cstring(
            'ccfit2 ac <filename(s)> <mass> <MW> [options]\n',
            'cyan'
        )
    )

    ac_parser._positionals.title = 'Mandatory arguments'

    ac_parser.set_defaults(func=ac_mode_func)
    ac_parser.add_argument(
        'input_file',
        metavar='filename(s)',
        type=str,
        nargs='+',
        help=(
            'Magnetometer file(s) containing the raw AC data.\n'
            'Supports shell-style wildcards, e.g. data_*.dat.\n'
            'See Documentation for expected format'
        )
    )
    ac_parser.add_argument(
        'mass',
        type=float,
        help='Sample mass (mg)'
    )
    ac_parser.add_argument(
        'MW',
        type=float,
        help='Sample molecular weight (g/mol)'
    )
    ac_parser.add_argument(
        '--x_var',
        metavar='<Option>',
        choices=['T', 'H'],
        default='T',
        help=(
            'Independent variable used for plotting AC data and fitting rates.\n' # noqa
            'Either temperature (T) or DC field (H)\n\n'
            '  If T is specified, the AC data is grouped by DC field and\n'
            '  Cole-Cole plots are shown for a single DC field with multiple temperatures.\n' # noqa
            '  Relaxation rates are then fitted as a function of temperature.\n\n' # noqa
            '  If H is specified, the AC data is grouped by temperature and\n'
            '  Cole-Cole plots are shown for a single temperature with multiple fields.\n' # noqa
            '  Relaxation rates are then fitted as a function of DC field.\n'
            'Default: %(default)s\n'
        )
    )
    ac_parser.add_argument(
        '--process',
        metavar='<Option>',
        choices=['plot', 'susc', 'all'],
        default='all',
        help=(
            'What to do:\n'
            ' - \'plot\' just shows the raw data\n'
            ' - \'susc\' fits only the AC data\n'
            ' - \'all\' fits AC data and relaxation profile\n'
            'Default: %(default)s.\n'
        )
    )
    ac_parser.add_argument(
        '--discard_off',
        action='store_true',
        help='Fit the susceptibilities even if no peak can be found'
    )
    ac_parser.add_argument(
        '--temp_thresh',
        metavar='<float>',
        type=float,
        default=0.1,
        help='Threshold used to discriminate between temperatures, default 0.1 K' # noqa
    )
    ac_parser.add_argument(
        '--field_thresh',
        metavar='<float>',
        type=float,
        default=1,
        help='Threshold used to discriminate between DC Fields, default 1 Oe'
    )

    x_var_selector = ac_parser.add_mutually_exclusive_group()
    x_var_selector.add_argument(
        '--select_T',
        action='store_true',
        help=(
            'Interactively select the temperatures to fit\n'
        )
    )
    x_var_selector.add_argument(
        '--unselect_T',
        action='store_true',
        help=(
            'Interactively deselect the temperatures to ignore\n'
            'Produces same window as --select_T, but with all temperatures\n'
            'pre-selected.'
        )
    )
    x_var_selector.add_argument(
        '--select_H',
        action='store_true',
        help=(
            'Interactively select the fields to fit\n'
        )
    )
    x_var_selector.add_argument(
        '--unselect_H',
        action='store_true',
        help=(
            'Interactively deselect the fields to ignore\n'
            'Produces same window as --select_h, but with all fields\n'
            'pre-selected.'
        )
    )

    ac_parser.add_argument(
        '--data_header',
        metavar='<str>',
        type=str,
        default='[Data]',
        help=(
            'String used to locate start of data in ac.dat file '
            'Default: %(default)s.\n'
        )
    )
    ac_parser.add_argument(
        '--single_plots',
        type=str,
        choices=['on', 'show', 'save', 'off'],
        default='off',
        help=(
            'Plot each experiment and colecole/susceptibility\n'
            '(with fits if successful) separately\n'
            ' - \'on\' shows and saves the plots\n'
            ' - \'show\' shows the plots\n'
            ' - \'save\' saves the plots\n'
            ' - \'off\' neither shows nor saves\n'
            'Default: %(default)s.\n'
        )
    )
    # Error defined as
    # sqrt( sum(square( linear(val_x, *linear_popt) -  val_y )) ).
    # The larger this value, the tighter the constraint.\n
    ac_parser.add_argument(
        '--flat_thresh',
        metavar='<Value>',
        type=float,
        default=1E-06,
        help='Threshold to discard flat lines. Default: 1E-06'
    )

    ac_parser.add_argument(
        '--verbose',
        action='store_true',
        help='Print the read-in values from the file indicated'
    )

    # Waveform
    description_Waveform = '''
    Extract AC susceptibilities from waveform data
    See PCCP, 2019, 21, 22302-22307 for method details
    '''
    epilog_Waveform = '''
    This module creates a $NAME_toccfit.dat file to be passed to the AC module
    '''
    waveform_parser = subparsers.add_parser(
        'waveform',
        description=description_Waveform,
        epilog=epilog_Waveform,
        formatter_class=argparse.RawTextHelpFormatter,
        usage=ut.cstring(
            'ccfit2 waveform <filename(s)> [options]\n',
            'cyan'
        )
    )

    waveform_parser.set_defaults(func=waveform_mode_func)
    waveform_parser._positionals.title = 'Mandatory arguments'

    waveform_parser.add_argument(
        'input_file',
        type=str,
        metavar='filename(s)',
        nargs='+',
        help=(
            'Magnetometer file(s), one per DC frequency.\n'
            'Supports shell-style wildcards, e.g. data_*.dat\n'
            'See Documentation for expected format'
        )
    )
    waveform_parser.add_argument(
        '--field_window',
        metavar='<field_window>',
        type=float,
        nargs=2,
        default=[-1, 1],
        help=(
            'Min & max field values (Oe) used to define the amplitude of the\n'
            'applied field in the waveform blocks. Values of field between\n'
            'these two values in the middle of each frequencey block will be\n'
            'deleted.\n'
            'Default: %(default)s.\n'
        )
    )
    waveform_parser.add_argument(
        '--data_header',
        metavar='<str>',
        type=str,
        default='[Data]',
        help='String used to locate data in <filename(s)>. Default: [Data]'
    )

    waveform_parser.add_argument(
        '--ft_plots',
        choices=['on', 'show', 'save', 'off'],
        metavar='<str>',
        type=str,
        default='off',
        help=(
            'Plot Fourier transform of each individual waveform experiment\n'
            ' - \'on\' shows and saves the plots\n'
            ' - \'show\' shows the plots\n'
            ' - \'save\' saves the plots\n'
            ' - \'off\' neither shows nor saves\n'
            'Default: %(default)s.\n'
        )
    )
    waveform_parser.add_argument(
        '--mf_plots',
        choices=['on', 'show', 'save', 'off'],
        metavar='<str>',
        type=str,
        default='off',
        help=(
            'Plot Moment and Field vs time for each individual waveform experiment\n' # noqa
            ' - \'on\' shows and saves the plots\n'
            ' - \'show\' shows the plots\n'
            ' - \'save\' saves the plots\n'
            ' - \'off\' neither shows nor saves\n'
            'Default: %(default)s.\n'
        )
    )
    waveform_parser.add_argument(
        '--susc_plot',
        choices=['on', 'show', 'save', 'off'],
        metavar='<str>',
        type=str,
        default='on',
        help=(
            'Plot Susceptibility data obtained from the Fourier transform\n'
            ' - \'on\' shows and saves the plots\n'
            ' - \'show\' shows the plots\n'
            ' - \'save\' saves the plots\n'
            ' - \'off\' neither shows nor saves\n'
            'Default: %(default)s.\n'
        )
    )
    waveform_parser.add_argument(
        '--temp_thresh',
        metavar='<float>',
        type=float,
        default=0.1,
        help='Threshold used to discriminate between temperatures, default 0.1 K' # noqa
    )
    waveform_parser.add_argument(
        '--process',
        metavar='<Option>',
        choices=['plot_raw', 'all'],
        default='all',
        help=(
            'What to do:\n'
            ' - \'plot_raw\' Show only raw waveform moment and field data\n'
            ' - \'all\' - Extract AC susceptibilities from waveform data\n'
            'Default: %(default)s.\n'
        )
    )

    # DC mode
    description_dc = '''
    Extract relaxation times from magnetisation decays using exponentials and
    (optionally) fit the resulting relaxation profile
    '''
    dc_parser = subparsers.add_parser(
        'dc',
        description=description_dc,
        formatter_class=argparse.RawTextHelpFormatter,
        usage=ut.cstring(
            'ccfit2 dc <filename(s)> [options]\n',
            'cyan'
        )
    )
    dc_parser._positionals.title = 'Mandatory arguments'

    dc_parser.set_defaults(func=dc_mode_func)

    dc_parser.add_argument(
        'input_file',
        metavar='filename(s)',
        nargs='+',
        type=str,
        help=(
            'Magnetometer file(s) containing the raw DC data.\n'
            'Supports shell-style wildcards, e.g. data_*.dat\n'
            'See Documentation for expected format'
        )
    )
    dc_parser.add_argument(
        '--x_var',
        metavar='<Option>',
        choices=['T', 'H'],
        default='T',
        help=(
            'Independent variable used for plotting DC data and fitting rates.\n' # noqa
            'Either temperature (T) or DC field (H)\n\n'
            '  If T is specified, the DC data is grouped by DC field and\n'
            '  relaxation rates are then fitted as a function of temperature.\n\n' # noqa
            '  If H is specified, the DC data is grouped by temperature and\n'
            '  relaxation rates are then fitted as a function of DC field.\n'
            'Default: %(default)s\n'
        )
    )
    dc_parser.add_argument(
        '--temp_thresh',
        metavar='<float>',
        type=float,
        default=0.1,
        help='Threshold used to discriminate between temperatures, default 0.1 K' # noqa
    )
    dc_parser.add_argument(
        '--field_thresh',
        metavar='<float>',
        type=float,
        default=1,
        help='Threshold used to discriminate between fields, default 1 Oe'
    )
    dc_parser.add_argument(
        '--process',
        metavar='<Option>',
        choices=['plot', 'decays', 'all'],
        default='all',
        help=(
            'What to do:\n'
            ' - \'plot\' Show only raw magnetisation decays\n'
            ' - \'decays\' - Fit only the magnetisation decays\n'
            ' - \'all\' - Fit magnetisation decays and relaxation profile\n'
            'Default: %(default)s.\n'
        )
    )
    dc_parser.add_argument(
        '--model',
        metavar='<Option>',
        choices=['stretched', 'double'],
        default='stretched',
        help=(
            'Select which model to apply to each decay trace\n'
            ' - \'stretched\' - Fit to a single stretched exponential\n'
            ' - \'double\' - Fit to a double stretched exponential\n'
            'Default: %(default)s.\n'
        )
    )

    meq_values = dc_parser.add_mutually_exclusive_group()

    meq_values.add_argument(
        '--M_eq',
        metavar='<fit/fix VALUE>',
        default=['fix', 0.],
        action=FitFixAction,
        nargs=2,
        help=(
            'Controls fitting/fixing of M_eq.\n'
            'First value is either the word fit or fix\n'
            'Second value is either the initial value  or fixed value as :\n'
            ' - The word guess - uses the final measured moment for each experiment (after cutting with --cut_moment)\n' # noqa
            ' - A single number specifying a single value to use for all experiments\n' # noqa
            ' - A filename, where the file contains a column of parameter values, one per experiment \n' # noqa
            'Default: %(default)s.\n'
        )
    )

    meq_values.add_argument(
        '--M_eq_calibration',
        metavar='<Value>',
        action=MultiAction,
        nargs=3,
        default=None,
        help=(
            'Calibrate M_eq for infield decays where sample mass or Molecular mass is unknown\n' # noqa
            'First value is the filename for the experimental saturation magnetisations\n'  # noqa
            'Second value is the filename for the theoretical magnetisation curves\n'  # noqa
            'Third value is the saturation magnetisation in Oe for all experiments\n' # noqa
            'Default: %(default)s.\n'
        )
    )

    dc_parser.add_argument(
        '--M_0',
        metavar='<fit/fix VALUE>',
        default=['fix', 'guess'],
        action=FitFixAction,
        nargs=2,
        help=(
            'Controls fitting/fixing of M_0.\n'
            'First value is either the word fit or fix\n'
            'Second value is either the initial value  or fixed value as :\n'
            ' - The word guess - uses the first measured moment for each experiment\n' # noqa
            ' - A single number specifying a single value to use for all experiments\n' # noqa
            ' - A filename, where the file contains a column of parameter values, one per experiment \n' # noqa
            'Default: %(default)s.\n'
        )
    )

    dc_parser.add_argument(
        '--t_offset',
        metavar='<fit/fix VALUE>',
        default=['fix', 0.],
        action=FitFixAction,
        nargs=2,
        help=(
            'Controls fitting/fixing of t_offset.\n'
            'First value is either the word fit or fix\n'
            'Second value is either the initial value  or fixed value as :\n'
            ' - A single number specifying a single value to use for all experiments\n' # noqa
            ' - A filename, where the file contains a column of parameter values, one per experiment \n' # noqa
            'Default: %(default)s.\n'
        )
    )

    dc_parser.add_argument(
        '--taustar',
        metavar='<fit/fix VALUE>',
        default=['fit', 100.],
        action=FitFixAction,
        nargs=2,
        help=(
            'Controls fitting/fixing of tau* in Stretched Exponential model.\n'
            'First value is either the word fit or fix\n'
            'Second value specifies the initial value  or fixed value as :\n'
            ' - A single number specifying a single value to use for all experiments\n' # noqa
            ' - A filename, where the file contains a column of parameter values, one per experiment \n' # noqa
            'Default: %(default)s.\n'
        )
    )

    dc_parser.add_argument(
        '--beta',
        metavar='<fit/fix VALUE>',
        default=['fit', 0.95],
        action=FitFixAction,
        nargs=2,
        help=(
            'Controls fitting/fixing of beta in Stretched Exponential model.\n'
            'First value is either the word fit or fix\n'
            'Second value is either the initial value  or fixed value as :\n'
            ' - A single number specifying a single value to use for all experiments\n' # noqa
            ' - A filename, where the file contains a column of parameter values, one per experiment \n' # noqa
            'Default: %(default)s.\n'
        )
    )

    dc_parser.add_argument(
        '--taustar1',
        metavar='<fit/fix VALUE>',
        default=['fit', 50.],
        action=FitFixAction,
        nargs=2,
        help=(
            'Controls fitting/fixing of tau_1* in Double Exponential Model.\n'
            'First value is either the word fit or fix\n'
            'Second value specifies the initial value  or fixed value as :\n'
            ' - A single number specifying a single value to use for all experiments\n' # noqa
            ' - A filename, where the file contains a column of parameter values, one per experiment \n' # noqa
            'Default: %(default)s.\n'
        )
    )

    dc_parser.add_argument(
        '--taustar2',
        metavar='<fit/fix VALUE>',
        default=['fit', 5000.],
        action=FitFixAction,
        nargs=2,
        help=(
            'Controls fitting/fixing of tau_2* in Double Exponential Model.\n'
            'First value is either the word fit or fix\n'
            'Second value specifies the initial value  or fixed value as :\n'
            ' - A single number specifying a single value to use for all experiments\n' # noqa
            ' - A filename, where the file contains a column of parameter values, one per experiment \n' # noqa
            'Default: %(default)s.\n'
        )
    )

    dc_parser.add_argument(
        '--beta1',
        metavar='<fit/fix VALUE>',
        default=['fit', 0.95],
        action=FitFixAction,
        nargs=2,
        help=(
            'Controls fitting/fixing of beta_1 in Double Exponential Model.\n'
            'First value is either the word fit or fix\n'
            'Second value is either the initial value  or fixed value as :\n'
            ' - A single number specifying a single value to use for all experiments\n' # noqa
            ' - A filename, where the file contains a column of parameter values, one per experiment \n' # noqa
            'Default: %(default)s.\n'
        )
    )

    dc_parser.add_argument(
        '--beta2',
        metavar='<fit/fix VALUE>',
        default=['fit', 0.95],
        action=FitFixAction,
        nargs=2,
        help=(
            'Controls fitting/fixing of beta_2 in Double Exponential Model.\n'
            'First value is either the word fit or fix\n'
            'Second value is either the initial value  or fixed value as :\n'
            ' - A single number specifying a single value to use for all experiments\n' # noqa
            ' - A filename, where the file contains a column of parameter values, one per experiment \n' # noqa
            'Default: %(default)s.\n'
        )
    )

    dc_parser.add_argument(
        '--frac',
        metavar='<fit/fix VALUE>',
        default=['fit', 0.5],
        action=FitFixAction,
        nargs=2,
        help=(
            'Controls fitting/fixing of fraction in Double Exponential Model.\n' # noqa
            'First value is either the word fit or fix\n'
            'Second value is either the initial value or fixed value as :\n'
            ' - A single number specifying a single value to use for all experiments\n' # noqa
            ' - A filename, where the file contains a column of parameter values, one per experiment \n' # noqa
            'Default: %(default)s.\n'
        )
    )

    dc_parser.add_argument(
        '--cut_moment',
        metavar='<number>',
        type=float,
        default=0.01,
        help=(
            'Number specifying a %% of initial moment.\n'
            'Moments smaller than this will be discarded.\n'
            'Disable by setting to 0.\n'
            'Default: %(default)s.\n'
        )
    )
    dc_parser.add_argument(
        '--field_calibration',
        metavar='<VALUE>',
        action=DiffAction,
        default=None,
        help=(
            'Set what the target field has been calibrated to. Options are:\n'
            ' - A single value giving the actual field for all experiments.\n'
            ' - A filename, where the file contains a column of parameter values, one per experiment \n' # noqa
            'Default: %(default)s.\n'
        )
    )

    field_cutting = dc_parser.add_mutually_exclusive_group()

    field_cutting.add_argument(
        '--dfield_thresh',
        metavar='<number>',
        type=float,
        default=0.5,
        help=(
            'Threshold (in Oe) used for finding stable field\n'
            'Defined as difference between DC fields, below which field is '
            'considered stable\n'
            'Default: %(default)s.\n'
        )
    )

    field_cutting.add_argument(
        '--no_field_discard',
        action='store_true',
        help='''Do not cut data at stable field'''
    )

    dc_parser.add_argument(
        '--data_header',
        metavar='<str>',
        type=str,
        default='[Data]',
        help=(
            'String used to locate start of data in dc.dat file '
            'Default: %(default)s.\n'
        )
    )

    dc_parser.add_argument(
        '--moment_header',
        metavar='<str>',
        type=str,
        choices=['find', 'moment', 'fixed', 'free'],
        default='find',
        help=(
            'Controls which column of datafile is used for magnetic moment.\n'
            'Choices are:\n'
            ' - find - ccfit2 will use the first non-empty column it can find\n' # noqa
            ' - moment - ccfit2 will use the \'Moment (emu) column\'\n'
            ' - fixed - ccfit2 will use the \'DC Moment Fixed Ctr (emu)\' column\n' # noqa
            ' - free - ccfit2 will use the \'DC Moment Free Ctr (emu)\' column\n' # noqa
            'Default: %(default)s.\n'
        )
    )

    dc_parser.add_argument(
        '--decay_plots',
        type=str,
        choices=['on', 'show', 'save', 'off'],
        default='show',
        help=(
            'Visualisation options for individual magnetisation decay plots\n'
            ' - \'on\' shows and saves the plots\n'
            ' - \'show\' shows the plots\n'
            ' - \'save\' saves the plots\n'
            ' - \'off\' neither shows nor saves\n'
            'Default: %(default)s.\n'
        )
    )

    dc_parser.add_argument(
        '--hide_params',
        action='store_false',
        help='''Hides parameters on magnetisation decay plots.'''
    )

    dc_parser.add_argument(
        '--plot_axes',
        metavar='<str>',
        type=str,
        nargs=2,
        default=['linear', 'linear'],
        choices=['linear', 'log'],
        help=(
            'Choose between linear and log axes for plotting the DC decay '
            'traces.\n'
            'Default: %(default)s.\n'
        )
    )
    dc_parser.add_argument(
        '--verbose',
        action='store_true',
        help='Print guess information to screen'
    )

    # Relaxation Profile
    description_relaxation = '''
    Fit the field- and/or temperature-dependence of relaxation times.
    '''
    relaxation_parser = subparsers.add_parser(
        'relaxation',
        description=description_relaxation,
        formatter_class=argparse.RawTextHelpFormatter,
        usage=ut.cstring(
            'ccfit2 relaxation <filename(s)> [options]\n',
            'cyan'
        )
    )

    relaxation_parser.set_defaults(func=relaxation_mode_func)
    relaxation_parser._positionals.title = 'Mandatory arguments'

    relaxation_parser.add_argument(
        'input_files',
        metavar='filename(s)',
        type=str,
        nargs='+',
        help=(
            'Either AC or DC <>_params.csv files.\n'
            'Supports shell-style wildcards, e.g. data_*.csv\n'
            'See documentation for format'
        )
    )
    relaxation_parser.add_argument(
        '--x_var',
        metavar='<Option>',
        choices=['T', 'H'],
        default='T',
        help=(
            'Fit either the temperature (T) or field (H) dependence of '
            'rates (isofield or isothermal).\n'
            'Options: T, H\n'
            'Default: %(default)s.\n'
        )
    )
    relaxation_parser.add_argument(
        '--process',
        metavar='<Option>',
        choices=['plot', 'all'],
        default='all',
        help=(
            'What to do:\n'
            ' - \'plot\' Show only raw relaxation profile\n'
            ' - \'all\' - Fit relaxation profile\n'
            'Default: %(default)s.\n'
        )
    )

    relaxation_parser.add_argument(
        '--filetype',
        metavar='<Option>',
        choices=['ccfit2', 'rate', 'legacy'],
        default='ccfit2',
        help=(
            'Type of file to read. Options:\n'
            ' - ccfit2 = *_params.csv file\n'
            ' - legacy = OLD *_params.out file\n'
            ' - rate = rates file (see docs)\n'
            'Default: %(default)s.\n'
        )
    )

    relaxation_parser.add_argument(
        '--no_weights',
        action='store_true',
        help='Disable weighting of fit using uncertainties'
    )

    relaxation_parser.add_argument(
        '--verbose',
        action='store_true',
        help='Print the read-in values from the file indicated.'
    )

    relaxation_parser.add_argument(
        '--plot_type',
        metavar='<Option>',
        choices=['rate', 'time', 'both'],
        default='rate',
        help=(
            'Type of final relaxation plot to produce\n'
            ' - \'rate\' rate vs T or H on a log-log or log-symlog plot\n'
            ' - \'time\' ln(time) vs 1/T or 1/H on a lin-lin plot\n'
            ' - \'both\' produce both of the above\n'
            'Default: %(default)s.\n'
        )
    )

    relaxation_parser.add_argument(
        '--hide_params',
        action='store_false',
        help='''Hides parameters on fitted relaxation plots.'''
    )

    # If argument list is none, then call function func
    # which is assigned to help function
    # read sub-parser
    parser.set_defaults(func=lambda args: parser.print_help())
    known_args = parser.parse_args(arg_list)

    known_args.func(known_args)

    return known_args


def main():
    read_args()


def check_mag_files(file_names: list[str], header_dict: dict[str, str],
                    data_header: str, num_threads: int):
    '''
    A list-compatible version of check_mag_file
    which supports multiple files and parallelisation

    If errors are found, then program exits with red error message

    Parameters
    ----------
    file_name: list[str]
        Files to check
    header_dict: dict[str, str]
        One of ac.HEADERS_SUPPORTED, dc.HEADERS_SUPPORTED,\n
        waveform.HEADERS_SUPPORTED
    data_header: str:
        Header line which marks start of file's data section
    num_threads: int
        Number of threads to use

    Returns
    -------
        None
    '''

    # Check all file headers in parallel
    ut.cprint(
        f'\n Parsing {len(file_names):d} Input File(s)',
        'black_bluebg'
    )
    num_threads = min(num_threads, len(file_names))
    pool = mp.Pool(num_threads)
    iterables = [
        (file_name, header_dict, data_header)
        for file_name in file_names
    ]

    try:
        pool.starmap(ut.parse_mag_file, iterables, chunksize=None)
    except ValueError as err:
        pool.close()
        pool.join()
        ut.cprint(f'\n***Error***\n{str(err)}', 'red')
        sys.exit(1)

    pool.close()
    pool.join()


def print_num_threads(num_threads: int):
    '''
    Prints the number of threads to screen

    Parameters
    ----------
    num_threads: int
        Integer specifying the number of threads

    Returns
    -------
    None
    '''
    if num_threads == 1:
        ut.cprint(f'\n Using {num_threads:d} thread\n', 'black_bluebg')
    else:
        ut.cprint(f'\n Using {num_threads:d} threads\n', 'black_bluebg')

    return
