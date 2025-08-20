import numpy as np
import math


class Math:
    """
    Class to simplify and encapsulate functionality related
    to math that could be more complex than the contained 
    in the basic python math module.
    """

    @staticmethod
    def sigmoid(
        value: float
    ):
        """
        TODO: Write doc about this
        """
        # TODO: Maybe avoid np by now and use math
        return 1.0 / (1 + np.exp(-value))
    
    @staticmethod
    def normalize(
        value: float,
        min_value: float,
        max_value: float
    ):
        """
        Normalize the provided 'value' to turn it into another
        value between 0.0 and 1.0.
        """
        return (value - min_value) / (max_value - min_value)

    @staticmethod
    def denormalize(
        value: float,
        min_value: float,
        max_value: float
    ):
        """
        Denormalize the provided 'value' (that must be between
        0.0 and 1.0) by turning it into another value between
        the provided 'min_value' and 'max_value'.
        """
        return value * (max_value - min_value) + min_value

    @staticmethod
    def logarithm(
        value: float,
        base
    ):
        """
        Calculate the logarithm in 'base' base of the provided
        'value' number.
        """
        return math.log(value, base)

    @staticmethod
    def is_power_of_n(
        value: float,
        base
    ):
        """
        Calculate if the provided 'value' number is a power
        of the also provided 'base' number. This means that
        16 and 4 will return True, and 15 and 4, False.
        """
        return Math.logarithm(value, base).is_integer()

    