# encoding:utf-8
import math


def decorate(func):
    def wrapper(*args):
        try:
            return func(*args)
        except Exception:
            return math.nan

    return wrapper
