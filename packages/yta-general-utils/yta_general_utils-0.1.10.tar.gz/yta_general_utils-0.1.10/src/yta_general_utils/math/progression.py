from yta_general_utils.math.value_normalizer import ValueNormalizer
from yta_general_utils.math.rate_functions.rate_function_argument import RateFunctionArgument
from yta_validation.parameter import ParameterValidator

import numpy as np


class Progression:
    """
    Class to represent a progression of 'n' values from
    'start' to 'end' (including both in that 'n' amount),
    with an associated rate function to calculate the
    values between those 'start' and 'end' limits.

    The progression can be ascending or descending.

    This class is useful to obtain each individual value
    that must be applied in different use cases.
    """
    
    _start: float = None
    _end: float = None
    _n: float = None
    """
    The number of values including 'start' and 'end'. 
    This number must be greater or equal to 2.
    """
    _values: list[float] = None
    """
    The amount of values that will exist the progression
    (including 'start' and 'end'). A progression with
    n = 2 will be as simple as [start, end].
    """
    _rate_function: RateFunctionArgument = None
    """
    The function to calculate the values in between the
    start and end limits.
    """

    @property
    def values(
        self
    ):
        """
        The list of 'n' values (including 'start' and 'end') 
        between those limits and according to the provided
        'rate_function'.
        """
        if self._values is None:
            start, end = (
                (self.end, self.start)
                if self.start > self.end else
                (self.start, self.end)
            )

            values = [
                ValueNormalizer(start, end).denormalize(normalized_value)
                for normalized_value in Progression.get_n_normalized_values(self.n, self.rate_function)
            ]

            # If limits are switched, we need to recalculate it
            values = (
                [
                    self.end - value + self.start
                    for value in values
                ]
                if self.start > self.end else
                values
            )

            self._values = values

        return self._values

    @property
    def start(
        self
    ):
        """
        The first value of the progression, that acts as a limit.
        """
        return self._start
    
    @start.setter
    def start(
        self,
        value: float
    ):
        ParameterValidator.validate_mandatory_number('value', value)

        if self._start != value:
            self._values = None
            self._start = value

    @property
    def end(
        self
    ):
        """
        The last value of the progression, that acts as a limit.
        """
        return self._end
    
    @end.setter
    def end(
        self,
        value: float
    ):
        ParameterValidator.validate_mandatory_number('value', value)
        
        if self._end != value:
            self._values = None
            self._end = value

    @property
    def n(
        self
    ):
        """
        The amount of total values in the progression including
        'start' and 'end'.
        """
        return self._n
    
    @n.setter
    def n(
        self,
        value: int
    ):
        """
        The amount of total values in the progression including
        'start' and 'end'.
        """
        ParameterValidator.validate_mandatory_positive_int('value', value, do_include_zero = False)
        
        if self._n != value:
            self._values = None
            self._n = value

    @property
    def rate_function(
        self
    ):
        """
        The rate function that will be applied to calculate
        the 'n' values between 'start' and 'end'.
        """
        return self._rate_function
    
    @rate_function.setter
    def rate_function(
        self,
        value: RateFunctionArgument
    ):
        # TODO: Validate rate function

        self._values = None
        self._rate_function = value

    def __init__(
        self,
        start: float,
        end: float,
        n: int,
        rate_function: RateFunctionArgument = RateFunctionArgument.default()
    ):
        ParameterValidator.validate_mandatory_number('start', start)
        ParameterValidator.validate_mandatory_number('end', end)
        ParameterValidator.validate_mandatory_positive_int('n', n, do_include_zero = False)

        if n < 2:
            raise Exception('The provided "n" parameter is not greater or equal than 2.')
        
        self._start = start
        self._end = end
        self._n = n
        self._rate_function = rate_function
        self._values = None

    @staticmethod
    def get_n_equally_distributed_normalized_values(
        n: int
    ):
        """
        Get a list containing 'n' equally distributed (and
        normalized) values between the instance's 'start'
        and 'end' (both included). The 'n' value must be
        equal or greater than 2.

        If `n = 6`:
        - `[0.0, 0.2, 0.4, 0.6, 0.8, 1.0]`
        """
        ParameterValidator.validate_mandatory_positive_int('n', n, do_include_zero = False)

        if n < 2:
            raise Exception('The provided "n" parameter is not greater or equal than 2.')

        return np.linspace(0.0, 1.0, n).tolist()

    @staticmethod
    def get_n_normalized_values(
        n: int,
        rate_function: RateFunctionArgument = RateFunctionArgument.default()
    ):
        """
        Get a list containing 0.0 and 1.0 limits and
        'n' - 2 values in between the instance's 
        'start' and 'end' limits according to the
        provided 'rate_function'.

        If `n = 6` and `rate_function = ease_in_quad`:
        - `[0.0, 0.04, 0.16, 0.36, 0.64, 1.0]`
        """
        ParameterValidator.validate_mandatory_positive_int('n', n, do_include_zero = False)

        if n < 2:
            raise Exception('The provided "n" parameter is not greater or equal than 2.')
        
        return [
            rate_function.get_n_value(normalized_value)
            for normalized_value in Progression.get_n_equally_distributed_normalized_values(n)
        ]

# TODO: I need to review the GraphicInterpolation and refactor
# it with the new NormalizedValue, ValueNormalizer and more...
# Code must be completely clear and as self-descriptive as
# possible