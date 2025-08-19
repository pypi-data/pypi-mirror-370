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

This module contains utility functions for ccfit2
'''


import numpy as np
from numpy.typing import ArrayLike
import os
from charset_normalizer import detect
from pathlib import Path
import sys


def red_exit(string):
    cprint(string, 'red')
    sys.exit(-1)
    return


def flatten_recursive(to_flat: list[list]) -> list:
    '''
    Flatten a list of lists recursively.

    Parameters
    ----------
    to_flat: list

    Returns
    -------
    list
        Input list flattened to a single list
    '''

    if to_flat == []:
        return to_flat
    if isinstance(to_flat[0], list):
        return flatten_recursive(to_flat[0]) + flatten_recursive(to_flat[1:])
    return to_flat[:1] + flatten_recursive(to_flat[1:])


class UserConfig():
    '''
    Contains user configuration information.
    Used in cli and interactive element callbacks

    Parameters
    ----------
    None

    Attributes
    ----------
    mass: float
        Mass of sample
    mw: float
        Molecular weight of sample
    file_name: str | list[str]
        Name(s) of input files
    results_dir: str
        Results directory
    '''

    def __init__(self):

        self.mass = np.nan
        self.mw = np.nan

        # Magnetometer output files, these are INPUT to ccfit2
        self._file_name = None
        self._results_dir = None

    @property
    def n_input_files(self) -> int:
        if self._file_name is None:
            return 0
        elif isinstance(self._file_name, str):
            return 1
        else:
            return len(self._file_name)

    @property
    def file_name(self) -> list[str]:
        return self._file_name

    @file_name.setter
    def file_name(self, value: str | list[str]):

        # Single file name
        if isinstance(value, str):

            self._file_name = [os.path.abspath(value)]

            self.results_dir = '{}_results'.format(
                os.path.splitext(os.path.abspath(self._file_name[0]))[0]
            ).replace('.', '_')

        # Multiple file names
        elif isinstance(value, list):

            self._file_name = [
                os.path.abspath(val) for val in value
            ]
            # If a common path is equal to folder of data, then make results
            # directory in execution directory
            if os.path.commonpath(self._file_name) != os.path.dirname(self._file_name[0]): # noqa
                self.results_dir = os.path.abspath("results")
            # But if it is, then make a new results directory in that folder
            else:
                self.results_dir = os.path.join(
                    os.path.commonpath(self._file_name),
                    'results'
                )

        return

    @property
    def results_dir(self) -> str:
        return self._results_dir

    @results_dir.setter
    def results_dir(self, value):
        self._results_dir = value
        if not os.path.exists(self.results_dir):
            os.mkdir(self.results_dir)
        return


def parse_headers(file: str, data_index: int,
                  supported_headers: dict[str, list[str]],
                  delim: str = ',',
                  encoding: str = 'find') -> tuple[dict[str, int], dict[str, str]]: # noqa
    '''
    Extracts headers from a file and returns header name and column position
    in file

    Parameters
    ----------
    file: str
        Name of magnetometer output file
    data_index: int
        Line which specifies the beginning of the data block in input file
    supported_headers: dict[str, list[str]]
        Keys are generic header names, values are specific implementations\n
        of that header. e.g. see HEADERS_SUPPORTED in ac.py and dc.py
    delim: str default ','
        Delimiter for file
    encoding: str, default 'find'
        Encoding to use for file

    Returns
    -------
    dict[str, int]
        Keys are generic header names given as keys of supported_headers\n
        Values are column index of header in file
        If header is not found, value is -1
    dict[str, str]
        Keys are generic header names given as keys of supported_headers\n
        Values are specific header names found in file
        If header is not found, value is empty string

    Raises
    ------
    ValueError
        If no headers can be found
    '''

    if encoding == 'find':
        encoding = detect_encoding(file)

    generic_headers = supported_headers.keys()

    headers = []

    # Open file and store all headers
    with open(file, 'r', encoding=encoding) as f:
        for it, line in enumerate(f):
            if it == data_index:
                headers = line.split(delim)
                break

    # Remove spaces before/after delimiter, and remove carriage-return
    headers = [he.lstrip().rstrip() for he in headers]

    if not len(headers):
        raise ValueError('Cannot find headers in file')

    if '\n' in headers:
        headers.pop(-1)

    # Get indices of required headers in file
    # Set default as -1 (not found)
    header_indices = {name: -1 for name in generic_headers}
    header_names = {name: '' for name in generic_headers}
    for hit, header in enumerate(headers):
        for key, sup_heads in supported_headers.items():
            if header_indices[key] in [-1, -2]:
                for sup_head in sup_heads:
                    if header == sup_head:
                        # Read column of file and attempt to
                        # convert strings to floats, if not possible then mark
                        # as nan
                        data = np.loadtxt(
                            file,
                            skiprows=data_index + 1,
                            delimiter=delim,
                            converters={
                                hit: lambda s: (float(s.strip() or np.nan))
                            },
                            usecols=hit,
                            encoding=encoding
                        )
                        # If all are nan, then this column is empty and
                        # shouldnt be used
                        if all(np.isnan(da) for da in data):
                            # Set header index as -2 for empty column
                            header_indices[key] = -2
                        else:
                            header_indices[key] = hit
                            header_names[key] = header

    return header_indices, header_names


def locate_data_header(file: str, data_header: str = '[Data]',
                       encoding: str = 'find') -> int:
    '''
    Check whether `data_header` is in file.

    Parameters
    ----------
    file: str
        Name of file to search
    data_header: str, default '[Data]'
        Line which specifies the beginning of the data block in input file
    encoding: str, default 'find'
        Specifies encoding of file

    Returns
    -------
    int
        line number containing data header, -1 if header not located.
    '''

    if encoding == 'find':
        encoding = detect_encoding(file)

    data_index = -1

    # Open file and store line containing data header
    with open(file, 'r', encoding=encoding) as f:
        for it, line in enumerate(f):
            if data_header in line:
                data_index = it + 1
                break

    return data_index


def find_mean_values(values: ArrayLike, thresh: float = 0.1) -> tuple[
        list[float], list[int]]:
    '''
    Finds mean value from a list of values by locating values for which
    step size is >= `thresh`

    Returns list of same length with all values replaced by mean(s)

    Parameters
    ----------
    values: array_like
        Values to look at
    thresh: float, default 0.1
        Threshold used to discriminate between values

    Returns
    -------
    list[float]
        Mean values, same size as original values list
    list[int]
        indices of original list at which value changes by more than
        0.1
    '''

    # Find values for which step size is >= thresh
    mask = np.abs(np.diff(values)) >= thresh
    # and mark indices at which to split
    split_indices = np.where(mask)[0] + 1

    # For values with similar step size, record mean temperature
    means = [
        [np.mean(grp)] * grp.size
        for grp in np.split(values, split_indices)
    ]

    return np.concatenate(means), split_indices


def can_float(s: str) -> bool:
    '''
    For a given string, checks if conversion to float is possible

    Parameters
    ----------
    s: str
        string to check

    Returns
    -------
    bool
        True if value can be converted to float
    '''
    out = True
    try:
        s = float(s.strip())
    except ValueError:
        out = False

    return out


def platform_check(func):
    '''
    Decorator to check platform for color terminal output.\n
    Windows Anaconda prompt will not support colors by default, so
    colors are disabled for all windows machines, unless the
    ccfit2_termcolor envvar is defined
    '''

    def check(*args):
        if 'nt' in os.name and not os.getenv('ccfit2_termcolor'):
            print(args[0])
        else:
            func(*args)

    return check


def cstring(string: str, color: str) -> str:
    '''
    Returns colorised string

    Parameters
    ----------
    string: str
        String to print
    color: str {red, green, yellow, blue, magenta, cyan, white, black_yellowbg, white_bluebg} # noqa
        String name of color

    Returns
    -------
    None
    '''

    ccodes = {
        'red': '\u001b[31m',
        'green': '\u001b[32m',
        'yellow': '\u001b[33m',
        'blue': '\u001b[34m',
        'magenta': '\u001b[35m',
        'cyan': '\u001b[36m',
        'white': '\u001b[37m',
        'black_yellowbg': '\u001b[30;43m\u001b[K',
        'white_bluebg': '\u001b[37;44m\u001b[K',
        'black_bluebg': '\u001b[30;44m\u001b[K'
    }
    end = '\033[0m\u001b[K'

    # Count newlines at neither beginning nor end
    num_c_nl = string.rstrip('\n').lstrip('\n').count('\n')

    # Remove right new lines to count left new lines
    num_l_nl = string.rstrip('\n').count('\n') - num_c_nl
    l_nl = ''.join(['\n'] * num_l_nl)

    # Remove left new lines to count right new lines
    num_r_nl = string.lstrip('\n').count('\n') - num_c_nl
    r_nl = ''.join(['\n'] * num_r_nl)

    # Remove left and right newlines, will add in again later
    _string = string.rstrip('\n').lstrip('\n')

    _string = '{}{}{}{}{}'.format(l_nl, ccodes[color], _string, end, r_nl)

    return _string


@platform_check
def cprint(string: str, color: str, **kwargs):
    '''
    Prints colorised output to screen

    Parameters
    ----------
    string: str
        String to print
    color: str {red, green, yellow, blue, magenta, cyan, white}
        String name of color

    Returns
    -------
    None
    '''

    print(cstring(string, color), **kwargs)

    return


def detect_encoding(file: str, threshold: float = 0.75) -> str:
    '''
    Detects encoding of given file

    Parameters
    ----------
    file: str
        Name of file (with path, if not in cwd)
    threshold: float, default 0.75
        Threshold for encoding confidence, below this a warning is triggered

    Returns
    -------
    str
        Encoding of file

    Raises
    ------
    RuntimeWarning
        If encoding confidence < threshold
    '''

    filepath = Path(file)

    # We must read as binary (bytes) because we don't yet know encoding
    blob = filepath.read_bytes()

    # Detect encoding of file
    encoding = detect(blob)

    if encoding['confidence'] < threshold:
        raise RuntimeWarning(
            f'Encoding confidence <{threshold}, file encoding may not be understood!' # noqa
        )

    return encoding['encoding']


def alldiff(values: ArrayLike, thresh: float = 0.) -> list[bool]:
    '''
    Calculates forward and backwards difference of values
    and returns a list of booleans, one per value.
    Bool is False iff abs of both forward and backwards differences
    are > threshold for a given value

    Parameters
    ----------
    values: array_like
        Values to check
    thresh: float, default = 0.
        Threshold for abs forward and backwards difference check

    Returns
    -------
    list[bool]
        False iff abs of both forward and backwards differences
        are > threshold for a given value.\n
        Else True.
    '''

    pre = np.insert(values, 0, values[0])
    post = np.insert(values, len(values), values[-1])

    fdiff = np.diff(post)
    # backward difference = flip, take forward difference, flip again
    bdiff = np.flip(np.diff(np.flip(pre)))

    results = [
        not (abs(fd) > thresh and abs(bd) > thresh)
        for fd, bd in zip(fdiff, bdiff)
    ]

    # for first point, if unstable relative to next, mark as False
    if abs(fdiff[0]) > thresh:
        results[0] = False
    # for last point, if unstable relative to previous, mark as False
    if abs(bdiff[-1]) > thresh:
        results[-1] = False

    return results


def parse_mag_file(file_name: str, header_dict: dict[str, str],
                   data_header: str, encoding: str = 'find') -> None:
    '''
    Checks specified magnetometry file contains the required data headers

    If errors are found, then program exits with red error message

    Parameters
    ----------
    file_name: str
        File to check
    header_dict: dict[str, str]
        One of ac.HEADERS_SUPPORTED, dc.HEADERS_SUPPORTED,\n
        waveform.HEADERS_SUPPORTED
    data_header: str:
        Header line which marks start of file's data section
    encoding: str, default 'find'
        Encoding to use when opening file

    Returns
    -------
    int
        Line number for line containing data_header
    dict[str, int]
        Keys are generic header names given as keys of supported_headers\n
        Values are column index of header in file
        If header is not found, value is -1
    dict[str]
        Keys are generic header names given as keys of supported_headers\n
        Values are specific header names found in file
        If header is not found, value is empty string
    '''

    if encoding == 'find':
        encoding = detect_encoding(file_name)

    # Check data_pointer is in file
    data_index = locate_data_header(
        file_name,
        data_header=data_header,
        encoding=encoding
    )

    # If data_pointer is not present, print error message
    if data_index < 0:
        message = '    --data_header {}\n'.format(data_header)
        message += '    is not present in \n'
        message += '    {}\n'.format(file_name)
        raise ValueError(message)

    header_indices, header_names = parse_headers(
        file_name,
        data_index,
        header_dict,
        encoding=encoding
    )

    # If any headers are not present, or are empty print error message
    message = ''
    if any(val == -1 for val in header_indices.values()):
        for ind, name in zip(header_indices.values(), header_names.keys()):
            if ind == -1:
                message += '\n {} column not found.'.format(name.upper())
                message += '\n  Supported headers for this column are: '
                for i in header_dict[name]:
                    message += '\n   {} '.format(i)
            elif ind == -2:
                message += '\n {} column is empty.'.format(name.upper())
        message += '\nManually change the input file or raise'
        message += ' a GitLab Issue\n'
        raise ValueError(message)

    return data_index, header_indices, header_names


def strip_guess(func):
    '''
    Utility function used as decorator on fit_to methods
    Removes guess kwarg or arg and prints deprecation notice
    This should be removed in 6.0.0
    '''
    def remove(*args, **kwargs):
        if len(args) == 4:
            args = [args[0], args[2], args[3]]
            cprint('guess argument was deprecated in 5.7.0', 'black_yellowbg')
        if len(args) == 3 and 'guess' not in kwargs:
            args = [args[0], args[2]]
            cprint('guess argument was deprecated in 5.7.0', 'black_yellowbg')
        if 'guess' in kwargs:
            kwargs.pop('guess')
            cprint('guess argument was deprecated in 5.7.0', 'black_yellowbg')
        return func(*args, **kwargs)
    return remove
