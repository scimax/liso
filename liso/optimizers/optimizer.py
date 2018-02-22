#!/usr/bin/env python
"""
Optimizer class.

Author: Jun Zhu
"""
from abc import ABC
from abc import abstractmethod


class Optimizer(ABC):
    """Abstract Class for Optimizer Object"""
    category = None  # should be either 'global' or 'local'.

    def __init__(self, name):
        """Optimizer Class Initialization

        :param name: string
            Optimizer name.
        """
        self.name = name
        self.rank = 0  # for parallel run

    @abstractmethod
    def __call__(self, opt_problem):
        """Run Optimizer (Calling Routine)

        :param opt_problem: Optimization object
            Optimization problem instance.
        """
        raise NotImplemented
