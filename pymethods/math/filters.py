# -*- coding: utf-8 -*-
"""
Created on Tue Mar 26 14:56:34 2019

@author: chris
"""
import numpy as _np
import scipy as _scipy
# python numbers=enable

_padding_dict = {
    'mirror': 'mirror_pad',
    'zero': 'zero_pad',
    'replication': 'replication_pad',
    'periodic': 'periodic_pad',
    'periodic_replication': 'periodic_replication_pad',
    'valid': 'valid_pad'
}


class sgolay2d:

    def __new__ (
            cls, array, window_size=5, order=3, padding='zero',
            derivative=None, **kwargs):

        # number of terms in the polynomial expression
        n_terms = (order + 1) * (order + 2) / 2.0

        if window_size % 2 == 0:
            raise ValueError('window_size must be odd')

        if window_size**2 < n_terms:
            raise ValueError('order is too high for the window size')

        kwargs['window_size'] = window_size

        if len(array.shape) == 3:
            output = _np.zeros_like(array)
            for i, dim in enumerate(array):
                dim = getattr(cls, _padding_dict[padding])(dim, **kwargs)
                output[i, :, :] = cls._filter(
                    dim, window_size, order, derivative=derivative)
            return output
        elif len(array.shape) == 2:
            array = getattr(cls, _padding_dict[padding])(array, **kwargs)
            return cls._filter(
                array, window_size, order, derivative=derivative)

    @classmethod
    def _filter(cls, Z, window_size, order, derivative=None):

        half_size = window_size // 2

        # exponents of the polynomial.
        # p(x,y) = a0 + a1*x + a2*y + a3*x^2 + a4*y^2 + a5*x*y + ...
        # this line gives a list of two item tuple. Each tuple contains
        # the exponents of the k-th term. First element of tuple is for x
        # second element for y.
        # Ex. exps = [(0,0), (1,0), (0,1), (2,0), (1,1), (0,2), ...]
        exps = [(k-n, n) for k in range(order+1) for n in range(k+1)]

        # coordinates of points
        ind = _np.arange(-half_size, half_size+1, dtype=_np.float64)
        dx = _np.repeat(ind, window_size)
        dy = _np.tile(ind, [window_size, 1]).reshape(window_size**2, )

        # build matrix of system of equation
        A = _np.empty((window_size**2, len(exps)))
        for i, exp in enumerate(exps):
            A[:, i] = (dx**exp[0]) * (dy**exp[1])

        if derivative is None:
            m = _np.linalg.pinv(A)[0].reshape((window_size, -1))
            return _scipy.signal.fftconvolve(Z, m, mode='valid')
        elif derivative == 'col':
            c = _np.linalg.pinv(A)[1].reshape((window_size, -1))
            return _scipy.signal.fftconvolve(Z, -c, mode='valid')
        elif derivative == 'row':
            r = _np.linalg.pinv(A)[2].reshape((window_size, -1))
            return _scipy.signal.fftconvolve(Z, -r, mode='valid')
        elif derivative == 'both':
            c = _np.linalg.pinv(A)[1].reshape((window_size, -1))
            r = _np.linalg.pinv(A)[2].reshape((window_size, -1))
            return _scipy.signal.fftconvolve(Z, -r, mode='valid'), \
                 _scipy.signal.fftconvolve(Z, -c, mode='valid')

    @classmethod
    def valid(cls, z, *, window_size):
        return z

    @classmethod
    def mirror_pad(cls, z, *, window_size):
        half_size = window_size // 2
        # pad input array with appropriate values at the four borders
        new_shape = z.shape[0] + 2*half_size, z.shape[1] + 2*half_size
        Z = _np.zeros((new_shape))
        # top band
        band = z[0, :]
        Z[:half_size, half_size:-half_size] = \
            band - _np.abs(_np.flipud(z[1: half_size + 1, :]) - band)
        # bottom band
        band = z[-1, :]
        Z[-half_size:, half_size:-half_size] =\
            band + _np.abs(_np.flipud(z[-half_size-1:-1, :]) - band)
        # left band
        band = _np.tile(z[:, 0].reshape(-1, 1), [1, half_size])
        Z[half_size:-half_size, :half_size] =\
            band - _np.abs(_np.fliplr(z[:, 1:half_size + 1]) - band)
        # right band
        band = _np.tile(z[:, -1].reshape(-1, 1), [1, half_size])
        Z[half_size:-half_size, -half_size:] = \
            band + _np.abs(_np.fliplr(z[:, - half_size - 1:-1]) - band)
        # central band
        Z[half_size:-half_size, half_size:-half_size] = z
        # top left corner
        band = z[0, 0]
        Z[:half_size, :half_size] =\
            band - _np.abs(
                _np.flipud(_np.fliplr(z[1:half_size+1, 1:half_size+1])) - band)
        # bottom right corner
        band = z[-1, -1]
        Z[-half_size:, -half_size:] =\
            band + _np.abs(
                _np.flipud(_np.fliplr(z[-half_size-1:-1,-half_size-1:-1])) - band)
        # top right corner
        band = Z[half_size, -half_size:]
        Z[:half_size, -half_size:] =\
            band - _np.abs(
                _np.flipud(Z[half_size+1:2*half_size + 1, -half_size:]) - band)
        # bottom left corner
        band = Z[-half_size:, half_size].reshape(-1, 1)
        Z[-half_size:, :half_size] =\
            band - _np.abs(
                _np.fliplr(Z[-half_size:, half_size+1:2*half_size+1]) - band)
        return Z

    @classmethod
    def zero_pad(cls, z, *, window_size):
        half_size = window_size // 2
        # pad input array with appropriate values at the four borders
        new_shape = z.shape[0] + 2*half_size, z.shape[1] + 2*half_size
        Z = _np.zeros((new_shape))
        # central band
        Z[half_size:-half_size, half_size:-half_size] = z
        return Z

    @classmethod
    def replication_pad(cls, z, *, window_size):
        half_size = window_size // 2
        # pad input array with appropriate values at the four borders
        new_shape = z.shape[0] + 2*half_size, z.shape[1] + 2*half_size
        Z = _np.zeros((new_shape))
        # top band
        Z[:half_size, half_size:-half_size] = z[0, None, :]
        # bottom band
        Z[-half_size:, half_size:-half_size] = z[-1, None, :]
        # left band
        Z[half_size:-half_size, :half_size] = z[:, 0, None]
        # right band
        Z[half_size:-half_size, -half_size:] = z[:, -1, None]
        # central band
        Z[half_size:-half_size, half_size:-half_size] = z
        # top left corner
        Z[:half_size, :half_size] = Z[:half_size, half_size]
        # bottom right corner
        Z[-half_size:, -half_size:] = Z[-half_size:, -half_size-1]
        # top right corner
        Z[:half_size, -half_size:] = Z[:half_size, -half_size-1]
        # bottom left corner
        Z[-half_size:, :half_size] = Z[-half_size:, half_size]
        return Z

    @classmethod
    def periodic_pad(cls, z, *, window_size):
        half_size = window_size // 2
        # pad input array with appropriate values at the four borders
        new_shape = z.shape[0] + 2*half_size, z.shape[1] + 2*half_size
        Z = _np.zeros((new_shape))
        # top band
        Z[:half_size, half_size:-half_size] = z[-1, None, :]
        # bottom band
        Z[-half_size:, half_size:-half_size] = z[0, None, :]
        # left band
        Z[half_size:-half_size, :half_size] = z[:, -1, None]
        # right band
        Z[half_size:-half_size, -half_size:] = z[:, 0, None]
        # central band
        Z[half_size:-half_size, half_size:-half_size] = z
        # top left corner
        Z[:half_size, :half_size] = z[:half_size, -half_size:]
        # bottom right corner
        Z[-half_size:, -half_size:] = z[-half_size:, -1]
        # top right corner
        Z[:half_size, -half_size:] = z[:half_size, :half_size]
        # bottom left corner
        Z[-half_size:, :half_size] = z[-half_size:, -half_size:]
        return Z

    @classmethod
    def periodic_replication_pad(cls, z, *, window_size):
        half_size = window_size // 2
        # pad input array with appropriate values at the four borders
        new_shape = z.shape[0] + 2*half_size, z.shape[1] + 2*half_size
        Z = _np.zeros((new_shape))
        # top band
        Z[:half_size, half_size:-half_size] = z[-1, None, :]
        # bottom band
        Z[-half_size:, half_size:-half_size] = z[0, None, :]
        # left band
        Z[half_size:-half_size, :half_size] = z[:, 0, None]
        # right band
        Z[half_size:-half_size, -half_size:] = z[:, -1, None]
        # central band
        Z[half_size:-half_size, half_size:-half_size] = z
        # top left corner
        Z[:half_size, :half_size] = Z[:half_size, half_size]
        # bottom right corner
        Z[-half_size:, -half_size:] = Z[-half_size:, -half_size-1]
        # top right corner
        Z[:half_size, -half_size:] = Z[:half_size, -half_size-1]
        # bottom left corner
        Z[-half_size:, :half_size] = Z[-half_size:, half_size]
        return Z