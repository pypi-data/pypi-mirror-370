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

This module contains statistics helper functions
'''

from scipy.linalg import svd
from scipy.optimize._optimize import OptimizeResult
import numpy as np


def svd_stdev(curr_fit: OptimizeResult) -> tuple[list[float], list[bool]]:
    '''
    Calculates standard deviation of fit-parameters given output of scipy
    least_squares.

    Uses SVD of jacobian to check for singlular values equal to zero.
    Singular values equal to zero are discarded, so the corresponding
    parameter has a standard deviation which cannot be computed and is
    instead set to zero
    (i.e. they are meaningless)

    Parameters
    ----------
    curr_fit: OptimizeResult
        Result object from scipy.optimise.least_squares

    Returns
    -------
    list[float]
        Standard deviation on parameters
    list[bool]
        bool for each parameter, if False, then standard deviation cannot be
        calculated (and is set to zero)
    '''

    # SVD of jacobian
    _, s, VT = svd(curr_fit.jac, full_matrices=False)
    # Zero threshold as multiple of machine precision
    threshold = np.finfo(float).eps * max(curr_fit.jac.shape) * s[0]
    # Find singular values = 0.
    nonzero_sing = s > threshold
    # Truncate to remove these values
    s = s[nonzero_sing]
    VT = VT[:s.size]
    # Calculate covariance of each parameter using truncated arrays
    pcov = VT.T / s**2 @ VT
    # Scale by reduced chi**2 to remove influence of input sigma (if present)
    # and just obtain standard deviation of fit
    chi2dof = np.sum(curr_fit.fun**2)
    chi2dof /= (curr_fit.fun.size - curr_fit.x.size)
    pcov *= chi2dof
    stdev = np.sqrt(np.diag(pcov))

    no_stdev = stdev > threshold

    if sum(nonzero_sing) == len(nonzero_sing):
        no_stdev = [True] * len(nonzero_sing)

    return stdev, no_stdev
