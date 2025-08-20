from yta_general_utils.math.graphic.node import Node
from yta_general_utils.math.normalizable_value import NormalizableValue
from yta_general_utils.math.rate_functions.rate_function_argument import RateFunctionArgument
from yta_general_utils.math.rate_functions.rate_function import RateFunction
from yta_general_utils.math.progression import Progression
from yta_validation.parameter import ParameterValidator


# This class is very similar to PairOfCoordinates,
# maybe we can do something to avoid the duplicated
# code
class PairOfNodes:
    """
    Class to represent a pair of consecutive Nodes
    within a Graphic, that are connected and able
    to calculate any 'd' value between them. The
    left node must be positioned in a lower X than 
    the right one to be consecutive and valid.

    This pair of nodes will be represented by the 0
    to 1 X and Y axis values locally so they can be
    turned into the general Graphic value applying
    the general Graphic limits.
    """
    
    left_node: Node = None
    right_node: Node = None
    rate_function: RateFunctionArgument = None
    """
    The rate function to join the left node with the
    right node.
    """

    @property
    def max_x(
        self
    ):
        """
        The maximum X value, which is the right node X value.
        """
        return self.right_node.x
    
    @property
    def min_x(
        self
    ):
        """
        The minimum X value, which is the left node X value.
        """
        return self.left_node.x
    
    @property
    def max_y(
        self
    ):
        """
        The maximum Y value, which can be the left node or
        right node Y value.
        """
        return max([self.left_node.y, self.right_node.y])
    
    @property
    def min_y(
        self
    ):
        """
        The minimum Y value, which can be the left node or
        right node Y value.
        """
        return min([self.left_node.y, self.right_node.y])
    
    @property
    def is_descendant(
        self
    ):
        """
        Check if the Y value of the left node is greater
        than the Y value of the right node. If so, the
        pair of nodes is descendant (in Y value).
        """
        return self.left_node.y > self.right_node.y

    def __init__(
        self,
        left_node: Node,
        right_node: Node,
        rate_function: RateFunctionArgument = RateFunctionArgument(RateFunction.EASE_IN_OUT_SINE)
    ):
        if left_node.x > right_node.x:
            raise Exception('The left_node "x" value must be lower than the right_node "x" value.')
        
        self.left_node = left_node
        self.right_node = right_node
        self.rate_function = rate_function

    def get_n_xy_values_to_plot(
        self,
        n: int = 100,
        do_normalize: bool = False
    ) -> list[tuple[NormalizableValue, NormalizableValue]]:
        """
        Return 'n' (x, y) values to be plotted. Each of those
        X and Y values are normalized only if 'do_normalize'
        flag parameter is set as True.
        """
        ParameterValidator.validate_mandatory_positive_number('n', n, do_include_zero = False)
        
        n = int(n)

        xs = [
            NormalizableValue(x, (self.min_x, self.max_x))
            for x in Progression(self.min_x, self.max_x, 100, RateFunctionArgument.default()).values
        ]
        ys = [
            self.get_y_from_not_normalized_x(x.value)
            for x in xs
        ]

        if do_normalize:
            xs = [
                x.normalized
                for x in xs
            ]
            ys = [
                y.normalized
                for y in ys
            ]
        else:
            xs = [
                x.value
                for x in xs
            ]
            ys = [
                y.value
                for y in ys
            ]

        return list(zip(xs, ys))

    def get_y_from_not_normalized_x(
        self,
        x: float
    ) -> NormalizableValue:
        """
        The X parameter must be a value between the left
        node X and the right node X.
        """
        return self._get_y_from_x(x, is_x_normalized = False)
    
    def get_y_from_normalized_x(
        self,
        x: float
    ) -> NormalizableValue:
        """
        The X parameter must be a value between 0 and 1,
        being 0 the left node X and 1 the right node X.
        """
        return self._get_y_from_x(x, is_x_normalized = True)
    
    def _get_y_from_x(
        self,
        x: float,
        is_x_normalized: bool = False
    ) -> NormalizableValue:
        """
        Get the Y value for the given X, depending on if
        the X value is normalized or not, flagged with the
        'is_x_normalized' parameter.
        
        This method is for internal use only.
        """
        lower_limit = (
            self.min_x
            if not is_x_normalized else
            0
        )
        upper_limit = (
            self.max_x
            if not is_x_normalized else
            1
        )

        ParameterValidator.validate_mandatory_number_between('x', x, lower_limit, upper_limit)
        
        value = NormalizableValue(x, (self.min_x, self.max_x), value_is_normalized = is_x_normalized)
        value = NormalizableValue(self.rate_function.get_n_value(value.normalized), (self.min_y, self.max_y), value_is_normalized = True)
        value = NormalizableValue(1 - value.normalized, (self.min_y, self.max_y), value_is_normalized = True) if self.is_descendant else value

        return value