# encoding:utf-8
from maths_add.except_error import decorate

import maths_add.computation.addtion
import maths_add.computation.reduce
import maths_add.computation.multiply
import maths_add.computation.division

__all__ = [
    "Computation"
]


@decorate()
class Computation(object):
    def __init__(self):
        pass

    def addtion(self, *args):
        result = maths_add.computation.addtion.addTion(*args)
        return result

    def reduce(self, *args):
        result = maths_add.computation.reduce.reduceTion(*args)
        return result

    def multiply(self, *args):
        result = maths_add.computation.multiply.multiplyTion(*args)
        return result

    def division(self, *args):
        result = maths_add.computation.division.divisionTion(*args)
        return result
