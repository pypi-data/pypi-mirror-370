from yta_general_utils.math.value_normalizer import ValueNormalizer
from yta_validation.number import NumberValidator
from yta_validation.parameter import ParameterValidator
from dataclasses import dataclass


@dataclass
class NormalizableValue:
    """
    Class to represent a value within a range, useful
    to normalize or denormalize it without doubt if the
    value is yet normalized or not.

    We store any value as not normalized but you are
    able to normalize it in any case as we know the 
    range.
    """

    value: float = None
    """
    The value not normalized.
    """
    range: tuple[float, float] = None
    """
    The range in which the 'value' is contained when
    not normalized so we can use it to normalized it.
    """

    @property
    def normalized(
        self
    ) -> float:
        """
        The 'value' but normalized according to the 'range' in
        which the lower limit will by represented by the 0 and
        the upper limit by the 1.
        """
        return ValueNormalizer(self.range[0], self.range[1]).normalize(self.value)

    def __init__(
        self,
        value: float,
        range: tuple[float, float],
        value_is_normalized: bool = False
    ):
        """
        Initialize the 'value' within the 'range' provided. If
        the 'value' provided is already normalized, set the 
        'value_is_normalized' flag as True to be correctly
        recognized.
        """
        ParameterValidator.validate_mandatory_tuple('range', range, 2)
        
        if range[0] > range[1]:
            raise Exception('The provided "range" first value is greater or equal to the second one.')
        
        if (
            not value_is_normalized and
            not NumberValidator.is_number_between(value, range[0], range[1])
        ):
            raise Exception('The provided "value" is out of the given "range".')
        elif (
            value_is_normalized and
            not NumberValidator.is_number_between(value, 0, 1)
        ):
            raise Exception('The provided "value" is out of the normalized range [0, 1].')
        
        # Denormalize the value if the one provided is normalized
        value = (
            ValueNormalizer(range[0], range[1]).denormalize(value)
            if value_is_normalized else
            value
        )
        
        self.value = value
        self.range = range