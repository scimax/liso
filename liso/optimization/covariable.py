#!/usr/bin/python
"""
Author: Jun Zhu
"""


class Covariable(object):
    """Covariable class.

    Covariable is a variable which changes along with another variable.
    """
    def __init__(self, name, dependent, scale=1.0, shift=0.0):
        """Initialize CoVariable object

        The value of the variable is calculated by:
        covar = scale *var + shift

        :param name: string
            Name of the co-variable.
        :param dependent: string
            Name of the dependent variable.
        :param scale: float
            Coefficient.
        :param shift: float
            Coefficient.
        """
        self.name = name

        self.dependent = dependent
        self.scale = scale
        self.shift = shift

    def __str__(self):
        text = '{:^12}  {:^12}  {:^12}  {:^12}\n'.format(
            'Name', 'Dependent', 'scale', 'shift')
        text += '{:^12}  {:^12}  {:^12.4e}  {:^12.4e}\n'.format(
            self.name, self.dependent, self.scale, self.shift)
        return text
