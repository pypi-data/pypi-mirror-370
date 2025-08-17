# encoding:utf-8

import maths_add.advanced_computation.power
import maths_add.advanced_computation.root
import maths_add.advanced_computation.logarithm
import maths_add.advanced_computation.multiple_powers
from maths_add.except_error import decorate

__all__ = [
    "Advanced_Computation"
]


@decorate()
class Advanced_Computation(object):
    def __init__(self):
        pass

    def power(self, *args):
        result = maths_add.advanced_computation.power.powerTion(*args)
        return result

    def root(self, *args):
        result = maths_add.advanced_computation.root.rootTion(*args)
        return result

    def logarithm(self, *args):
        result = maths_add.advanced_computation.logarithm.logTion(*args)
        return result

    def multiple_powers(self, *args):
        result = maths_add.advanced_computation.multiple_powers.M_powersTion(*args)
        return result
