from yta_general_utils.math.graphic.graphic import Graphic
from yta_general_utils.math.value_normalizer import ValueNormalizer
from yta_validation.parameter import ParameterValidator


class RateFunctionGraphic:
    """
    A Graphic instance that uses itself as a rate
    function and returns the corresponding value
    for the given 'n'.

    TODO: Maybe force that the provided graphic 
    must end in the maximum Y value so, when
    normalized, it ends in value 1.
    """

    def __init__(
        self,
        graphic: Graphic
    ):
        ParameterValidator.validate_mandatory_instance_of('graphic', graphic, Graphic)

        self.graphic = graphic
        """
        The graphic instance.
        """
        
    def get_n_value(
        self,
        n: float
    ):
        """
        Get the corresponding value for the given 'n' normalized
        value that must be between 0 and 1.
        """
        return ValueNormalizer(self.graphic.min_y, self.graphic.max_y).normalize(self.graphic.get_xy_from_normalized_d(n)[1])