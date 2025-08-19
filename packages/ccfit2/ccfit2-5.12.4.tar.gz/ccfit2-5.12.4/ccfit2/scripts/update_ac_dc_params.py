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

This script contains a program to update old CCFIT2_cmd.py params.out files
'''


import argparse
import pandas as pd
import numpy as np
import datetime
import os
import sys

import ccfit2.ac as ac
import ccfit2.utils as ut
import ccfit2.dc as dc
from ccfit2.__version__ import __version__


def main():
    parser = argparse.ArgumentParser(
        description=(
            'This script allows you to update an old CCFIT2_cmd.py AC or DC'
            '_params.out file to work with ccfit2 version 5.7.1 and above'
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        'file_name',
        type=str,
        help='Old ccfit2 AC or DC params.out file'
    )

    parser.add_argument(
        '--model',
        type=str,
        choices=[
            'Debye',
            'Generalised Debye',
            'Double Generalised Debye (two-maxima)',
            'Exponential'
        ],
        default='Generalised Debye',
        help='Name of model used to generate the old data'
    )

    uargs = parser.parse_args()

    _models = {
        'Debye': ac.DebyeModel,
        'Generalised Debye': ac.GeneralisedDebyeModel,
        'Double Generalised Debye (two-maxima)': ac.DoubleGDebyeModel,
        'Exponential': dc.ExponentialModel
    }
    _model = _models[uargs.model]

    # Load the headers (column names)
    data = pd.read_csv(
        uargs.file_name,
        comment='#',
        skipinitialspace=True,
        sep=r'\t|\s{1,}',
        engine='python'
    )

    # Remove unnamed headers
    headers = data.keys()
    headers = [he for he in headers if 'Unnamed' not in he]

    # If any of the headers begin with ( then re-read with >1 space delimiter
    # so that bracketed units are included in the header and not treated
    # separately
    if any([he[0] == '(' for he in headers]):
        # Load the headers (column names)
        data = pd.read_csv(
            uargs.file_name,
            comment='#',
            skipinitialspace=True,
            sep=r'\t|\s{2,}',
            engine='python'
        )
        # Remove unnamed headers
        headers = data.keys()
        headers = [he for he in headers if 'Unnamed' not in he]

    # Then load the actual values
    # skipping comments and headers

    # Check number of comments and assume 1 header line
    n_com = 1
    with open(uargs.file_name, 'r') as f:
        for line in f:
            if line[0] == '#':
                n_com += 1

    values = np.loadtxt(
        uargs.file_name,
        skiprows=n_com,
        comments='#'
    )

    # Create dataframe for actual data
    data = pd.DataFrame(values, columns=headers)

    # Remove old tau bounds to avoid confusion
    old_headers = ['tau_ln_ESD-up (s)', 'tau_ln_ESD-lw (s)']
    for old in old_headers:
        if old in data.keys():
            data.pop(old)

    # Calculate <ln(tau)>, and add it to the dataframe with the
    # header ccfit2 expects
    if _model == ac.DoubleGDebyeModel:

        # Update headers
        name_convertor = {
            'T': 'T (K)',
            'H': 'H (Oe)',
            'tau_1': 'tau1 (s)',
            'tau_1-s-dev': 'tau1-s-dev (s)',
            'tau_err_1': 'tau1-s-dev (s)',
            'tau_err_1 (s)': 'tau1-s-dev (s)',
            'tau1_err': 'tau1-s-dev (s)',
            'tau1_err (s)': 'tau1-s-dev (s)',
            'tau_2': 'tau2 (s)',
            'tau_2-s-dev': 'tau2-s-dev (s)',
            'tau_err_2': 'tau2-s-dev (s)',
            'tau_err_2 (s)': 'tau2-s-dev (s)',
            'tau2_err': 'tau2-s-dev (s)',
            'tau2_err (s)': 'tau2-s-dev (s)',
            'alpha_1': 'alpha1 ()',
            'alpha1-s-dev': 'alpha1-s-dev ()',
            'alpha1_err': 'alpha1-s-dev ()',
            'alpha_err_1': 'alpha1-s-dev ()',
            'alpha_err_1 ()': 'alpha1-s-dev ()',
            'alpha_2': 'alpha2 ()',
            'alpha2-s-dev': 'alpha2-s-dev ()',
            'alpha2_err': 'alpha2-s-dev ()',
            'alpha_err_2': 'alpha2-s-dev ()',
            'alpha_err_2 ()': 'alpha2-s-dev ()',
            '<ln(tau1)>': '<ln(tau1)> (ln(s))',
            'sigma_ln(tau1)': 'sigma_ln(tau1) (ln(s))',
            'fit_upper_ln(tau1)': 'fit_upper_ln(tau1) (ln(s))',
            'fit_lower_ln(tau1)': 'fit_lower_ln(tau1) (ln(s))',
            '<ln(tau2)>': '<ln(tau2)> (ln(s))',
            'sigma_ln(tau2)': 'sigma_ln(tau2) (ln(s))',
            'fit_upper_ln(tau2)': 'fit_upper_ln(tau2) (ln(s))',
            'fit_lower_ln(tau2)': 'fit_lower_ln(tau2) (ln(s))'
        }

        data = data.rename(name_convertor, axis=1)

        req_headers = [
            'tau1 (s)',
            'tau2 (s)',
            'tau1-s-dev (s)',
            'tau2-s-dev (s)'
        ]

        if any(rh not in data.keys() for rh in req_headers):
            ut.cprint('Cannot find headers in specified file, did you select the correct --model?', 'red') # noqa
            ut.cprint(' Found:', 'red')
            for rh in req_headers:
                if rh in data.keys():
                    ut.cprint(f'  {rh}', 'red')
            ut.cprint(' Expected:', 'red')
            for rh in req_headers:
                ut.cprint(f'  {rh}', 'red')
            sys.exit()

        # Calculate ln(tau)
        vals = _model.calc_lntau_expect(
            data['tau1 (s)'], data['tau2 (s)']
        )
        data['<ln(tau1)> (ln(s))'] = vals[:, 0]
        data['<ln(tau2)> (ln(s))'] = vals[:, 1]

        # sigma_lntau
        vals = _model.calc_lntau_stdev(
            data['alpha1 ()'], data['alpha2 ()']
        )
        data['sigma_ln(tau1) (ln(s))'] = vals[:, 0]
        data['sigma_ln(tau2) (ln(s))'] = vals[:, 0]

        # and uncertainty in lntau from fitting
        b1, b2 = _model.calc_lntau_fit_ul(
            data['tau1 (s)'],
            data['tau2 (s)'],
            data['tau1-s-dev (s) (s)'],
            data['tau2-s-dev (s) (s)']
        )
        data['fit_upper_ln(tau1) (ln(s))'] = b1[0]
        data['fit_lower_ln(tau1) (ln(s))'] = b1[1]

        data['fit_upper_ln(tau2) (ln(s))'] = b2[0]
        data['fit_lower_ln(tau2) (ln(s))'] = b2[1]

    elif _model == dc.ExponentialModel:

        # Update headers
        name_convertor = {
            'T': 'T (K)',
            'H': 'H (Oe)',
            'H_measured': 'H_measured (Oe)',
            'tau': 'tau* (s)',
            'tau-s-dev': 'tau*-s-dev (s)',
            'tau_err': 'tau*-s-dev (s)',
            'tau_err (s)': 'tau*-s-dev (s)',
            'tau*': 'tau* (s)',
            'tau*-s-dev': 'tau*-s-dev (s)',
            'beta': 'beta ()',
            'beta-s-dev': 'beta-s-dev ()',
            'beta_err': 'beta-s-dev ()',
            'beta_err ()': 'beta-s-dev ()',
            't_offset': 't_offset (s)',
            't_offset-s-dev': 't_offset-s-dev (s)',
            'm_eq': 'm_eq (emu)',
            'm_eq-s-dev': 'm_eq-s-dev (emu)',
            'm_0': 'm_0 (emu)',
            'm_0-s-dev': 'm_0-s-dev (emu)',
            '<ln(tau)>': '<ln(tau)> (ln(s))',
            'sigma_ln(tau)': 'sigma_ln(tau) (ln(s))',
            'fit_upper_ln(tau)': 'fit_upper_ln(tau) (ln(s))',
            'fit_lower_ln(tau)': 'fit_lower_ln(tau) (ln(s))'
        }

        data = data.rename(name_convertor, axis=1)

        req_headers = [
            'tau* (s)',
            'beta ()',
            'tau*-s-dev (s)',
            'beta-s-dev ()'
        ]

        if any(rh not in data.keys() for rh in req_headers):
            ut.cprint('Cannot find headers in specified file, did you select the correct --model?', 'red') # noqa
            ut.cprint(' Found:', 'red')
            for rh in req_headers:
                if rh in data.keys():
                    ut.cprint(f'  {rh}', 'red')
            ut.cprint(' Expected:', 'red')
            for rh in req_headers:
                ut.cprint(f'  {rh}', 'red')
            sys.exit()

        # Calculate lntau
        data['<ln(tau)> (ln(s))'] = _model.calc_lntau_expect(
            data['tau* (s)'], data['beta ()']
        )
        # sigma_lntau
        data['sigma_ln(tau) (ln(s))'] = _model.calc_lntau_stdev(
            data['beta ()']
        )
        # and uncertainty in lntau from fitting
        [upper, lower] = _model.calc_lntau_fit_ul(
            data['tau* (s)'],
            data['beta ()'],
            data['tau*-s-dev (s)'],
            data['beta-s-dev ()']
        )

        data['fit_upper_ln(tau) (ln(s))'] = upper
        data['fit_lower_ln(tau) (ln(s))'] = lower

    # Debye and Generalised Debye
    else:
        # Update headers
        name_convertor = {
            'T': 'T (K)',
            'H': 'H (Oe)',
            'tau': 'tau (s)',
            'tau-s-dev': 'tau-s-dev (s)',
            'tau_err': 'tau-s-dev (s)',
            'tau_err (s)': 'tau-s-dev (s)',
            'alpha': 'alpha ()',
            'alpha-s-dev': 'alpha-s-dev ()',
            'alpha_err': 'alpha-s-dev ()',
            'alpha_err ()': 'alpha-s-dev ()',
            '<ln(tau)>': '<ln(tau)> (ln(s))',
            'sigma_ln(tau)': 'sigma_ln(tau) (ln(s))',
            'fit_upper_ln(tau)': 'fit_upper_ln(tau) (ln(s))',
            'fit_lower_ln(tau)': 'fit_lower_ln(tau) (ln(s))'
        }

        data = data.rename(name_convertor, axis=1)

        if _model == ac.DebyeModel:
            req_headers = [
                'tau (s)',
                'tau-s-dev (s)',
            ]
        else:
            req_headers = [
                'tau (s)',
                'alpha ()',
                'tau-s-dev (s)',
                'alpha-s-dev ()'
            ]
        if any(rh not in data.keys() for rh in req_headers):
            ut.cprint('Cannot find headers in specified file, did you select the correct --model?', 'red') # noqa
            ut.cprint(' Found:', 'red')
            for rh in req_headers:
                if rh in data.keys():
                    ut.cprint(f'  {rh}', 'red')
            ut.cprint(' Expected:', 'red')
            for rh in req_headers:
                ut.cprint(f'  {rh}', 'red')
            sys.exit()

        # Calculate lntau
        data['<ln(tau)> (ln(s))'] = _model.calc_lntau_expect(
            data['tau (s)']
        )

        # sigma_lntau (zero for Debye)
        if _model == ac.DebyeModel:
            data['sigma_ln(tau) (ln(s))'] = [0] * len(data['tau (s)'])
        else:
            data['sigma_ln(tau) (ln(s))'] = _model.calc_lntau_stdev(
                data['alpha ()']
            )

        # and uncertainty in lntau from fitting
        [upper, lower] = _model.calc_lntau_fit_ul(
            data['tau (s)'],
            data['tau-s-dev (s)'],
        )

        data['fit_upper_ln(tau) (ln(s))'] = upper
        data['fit_lower_ln(tau) (ln(s))'] = lower

    name_convertor = {
        'chi_S (cm^3mol^-1)': 'chi_S (cm^3 mol^-1)',
        'chi_S_err (cm^3mol^-1)': 'chi_S-s-dev (cm^3 mol^-1)',
        'chi_T (cm^3mol^-1)': 'chi_T (cm^3 mol^-1)',
        'chi_T_err (cm^3mol^-1)': 'chi_T-s-dev (cm^3 mol^-1)',
    }

    data = data.rename(name_convertor, axis=1)

    # Then save this data to a new csv file which can be read by
    # ccfit2 relaxation
    _head = os.path.splitext(uargs.file_name)[0]
    _out = f'{_head}_NEW.csv'

    # Make comment
    comment = (
        f'#This file was converted to work with ccfit2 v{__version__}'
        ' on {}\n'.format(
            datetime.datetime.now().strftime('%H:%M:%S %d-%m-%Y ')
        )
    )

    f = open(_out, 'w')
    f.write(comment)

    data = data.to_csv(
        f,
        index=False,
        float_format='%.18e',
        na_rep='NAN'
    )
    ut.cprint(f'Updated ccfit2 parameter .csv written to {_out}', 'blue')
