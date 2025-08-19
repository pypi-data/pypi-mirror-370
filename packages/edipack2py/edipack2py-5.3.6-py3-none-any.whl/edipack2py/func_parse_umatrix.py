from ctypes import *
import numpy as np
import os, sys
import types


def reset_umatrix(self):
    """

    This function resets to 0 all the interaction coefficients

    """

    reset_umatrix_wrap = self.library.reset_umatrix
    reset_umatrix_wrap.argtypes = None
    reset_umatrix_wrap.restype = None

    reset_umatrix_wrap()


def add_twobody_operator(self, oi, si, oj, sj, ok, sk, ol, sl, Uijkl):
    """

    This function lets the user add an interaction term on-the-fly.
    The input parameters are the spin and orbital indices of the second
    quantized operators and the interaction coefficient.
    The order of the indices is consistent with those of the umatrix file
    (see :ref:`EDIpack documentation <edipack:parse_umatrix>`).

    :type oi: int
    :param oi: orbital index of :math:`c^{\\dagger}_{i}`

    :type si: str
    :param si: spin index of :math:`c^{\\dagger}_{i}`

    :type oj: int
    :param oj: orbital index of :math:`c^{\\dagger}_{j}`

    :type sj: str
    :param sj: spin index of :math:`c^{\\dagger}_{j}`

    :type ok: int
    :param ok: orbital index of :math:`c_{k}`

    :type sk: str
    :param sk: spin index of :math:`c_{k}`

    :type ol: int
    :param ol: orbital index of :math:`c_{l}`

    :type sl: str
    :param sl: spin index of :math:`c_{l}`

    :type float: Uijkl
    :param Uijkl: interaction coefficient

    """

    add_twobody_operator_wrap = self.library.add_twobody_operator
    add_twobody_operator_wrap.argtypes = [
        c_int,
        c_int,
        c_int,
        c_int,
        c_int,
        c_int,
        c_int,
        c_int,
        c_double,
    ]
    add_twobody_operator_wrap.restype = None

    orbvector = [oi, oj, ok, ol]
    spinvector = [si, sj, sk, sl]

    mapping = {"u": 1, "d": 2}
    spinvector = [mapping[x] for x in spinvector]
    orbvector = [x + 1 for x in orbvector]

    add_twobody_operator_wrap(
        orbvector[0],
        spinvector[0],
        orbvector[1],
        spinvector[1],
        orbvector[2],
        spinvector[2],
        orbvector[3],
        spinvector[3],
        Uijkl,
    )
