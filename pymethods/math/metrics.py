import numpy as np


def error(true, pred):
    return (pred - true)/true


def percentage_error(true, pred):
    return error * 100


def absolute_error(true, pred):
    return np.abs(error(true, pred))


def absolute_percentage_error(true, pred):
    return absolute_error(true, pred) * 100


def relative_difference(true, pred):
    numerator = np.abs(pred - true)
    denominator = np.abs(pred) + np.abs(true)
    return 2 * numerator/denominator


def relative_percentage_difference(true, pred):
    return relative_difference(true, pred) * 100
