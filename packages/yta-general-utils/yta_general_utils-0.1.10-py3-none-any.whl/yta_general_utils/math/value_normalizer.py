from yta_general_utils.math import Math
from yta_validation.number import NumberValidator
from yta_validation.parameter import ParameterValidator


# TODO: Maybe create a Value class to be able to
# handle if it has been normalized or not and to
# also handle its range? It could be interesting
# for Progression class, but it is too much I
# think...

# TODO: What about inverted limits and ranges (?)
class ValueNormalizer:
    """
    Class to simplify the process of obtaining normalized
    values between a range and also converting them into
    a value within a new range.

    The range of normalized values will be always [0, 1].
    """
    
    def __init__(
        self,
        lower_limit: float,
        upper_limit: float
    ):
        if lower_limit > upper_limit:
            raise Exception('Review the limits. The lower limit cannot be equal or greater to the upper limit.')

        self.lower_limit = lower_limit
        self.upper_limit = upper_limit

    def _validate_outlier_value(
        self,
        value: float
    ):
        """
        Validate if the provided 'value' is within the limits
        or if it is an outlier, raising an Exception it an
        outlier value is detected.
        """
        if not NumberValidator.is_number_between(value, self.lower_limit, self.upper_limit):
            raise Exception(f'The provided "value" is out of the limits [{str(self.lower_limit)}, {str(self.upper_limit)}] and this outliers are not accepted due to "do_accept_outliers" parameter False value.')
        
    def _validate_normalized_outlier_value(
        self,
        value: float
    ):
        """
        Validate if the provided 'value' is within the 
        normalized limits or if it is an outlier, raising
        an Exception it an outlier value is detected.
        """
        if not NumberValidator.is_number_between(value, 0, 1):
            raise Exception(f'The provided "value" is out of the limits [0, 1] and this outliers are not accepted due to "do_accept_outliers" parameter False value.')

    def normalize(
        self,
        value: float,
        do_accept_outliers: bool = True
    ):
        """
        Obtain the provided 'value' as a normalized value,
        that will be between 0 and 1 according to this
        instance lower and upper limit. The provided
        'value' must be a not normalized value.

        If 'do_accept_outliers' is True, giving a value
        out of the range will also return its corresponding
        normalized value.
        
        A value equal than the lower limit would be 0, and
        a value equal to the upper limit, 1.

        15 is 0.5 in [0, 1] range for [10, 20] limits.
        """
        ParameterValidator.validate_mandatory_number('value', value)
        
        if not do_accept_outliers:
            self._validate_outlier_value(value)

        return (
            1.0
            if self.lower_limit == self.upper_limit else
            Math.normalize(value, self.lower_limit, self.upper_limit)
        )
    
    def denormalize(
        self,
        value: float,
        do_accept_outliers: bool = True
    ):
        """
        Obtain the provided normalized 'value' as a value
        that will be between this instance lower and upper
        limit.  The provided 'value' must be a normalized
        value.

        If 'do_accept_outliers' is True, giving a value
        out of the normalized range will also return its
        corresponding value according to the original range
        (that will be out of it, obviously).
        
        A value equal than 0 would be the lower limit, and
        a value equal to 1, the upper limit.

        0.5 is 15 is [10, 20] range for [0, 1] normalized 
        limits.
        """
        ParameterValidator.validate_mandatory_number('value', value)
        
        if not do_accept_outliers:
            self._validate_normalized_outlier_value(value)

        return (
            self.lower_limit
            if self.lower_limit == self.upper_limit else
            Math.denormalize(value, self.lower_limit, self.upper_limit)
        )
    
    def to_range_value(
        self,
        value: float,
        new_range_lower_limit: float,
        new_range_upper_limit: float,
        do_accept_outliers: bool = True
    ):
        """
        Obtain the provided 'value' as its corresponding 
        value within a new range in between the provided
        'new_range_lower_limit' and 'new_range_upper_limit'.
        The provided 'value' must be a not normalized value.

        If 'do_accept_outliers' is True, giving a value
        out of the range will also return its corresponding
        value in the new range.

        If lower limit is 10 and upper limit is 20, and a 
        value of 15 is provided, the normalized value would
        be 0.5, but as we want in a new range, we transform
        it. Asking for a new range lower limit of 0 and a 
        new range upper limit of 100, the same 15 value will
        return 50 in this method.

        15 is 0.5 in [0, 1] range for [10, 20] limits, but
        50 in the new [0, 100] range.
        """
        if new_range_lower_limit >= new_range_upper_limit:
            raise Exception('Review the limits. The new range lower limit cannot be equal or greater to the new range upper limit.')
        
        if not do_accept_outliers:
            self._validate_outlier_value(value)
        
        return Math.denormalize(self.normalize(value), new_range_lower_limit, new_range_upper_limit)