from yta_validation.parameter import ParameterValidator
from dataclasses import dataclass


@dataclass
class GraphicAxis:
    """
    Class that represent a Graphic axis with
    its min and max range.
    """

    range: tuple[float, float] = None
    """
    The range of the axis, a (min, max) tuple.
    """

    def __init__(
        self,
        min: float,
        max: float
    ):
        ParameterValidator.validate_is_mandatory_number('min', min)
        ParameterValidator.validate_is_mandatory_number('max', max)
        
        if min >= max:
            raise Exception('The "min" parameter cannot be greater or equal than the "max" parameter.')

        self.range = (min, max)

    @property
    def min(
        self
    ):
        """
        The minimum value.
        """
        return self.range[0]
    
    @property
    def max(
        self
    ):
        """
        The maximum value.
        """
        return self.range[1]