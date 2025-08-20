"""
THIS IS VERY IMPORTANT TO UNDERSTAND THE CODE:

- First of all, the distance. Imagine the graphic
once it's been plotted. If you go from the origin
to the end, there is a distance you are virtually
drawing. That is the global distance. The distance
from the origin, normalized, is d=1.0. The origin
is d=0.0 and the end is d=1.0.

- As you are using pairs of nodes, there is also a
local distance in between each pair of nodes.
Imagine, for a second, that each pair of nodes is
a graphic by itself. The first node is the d=0.0
and the second node is the d=1.0 (in local distance
terms).

- If you have, for example, 5 pairs of nodes, as
the total global distance is d=1.0, each pair of
nodes will represent a 1/5 of that total global
distance, so each pair of nodes local distance
is a 1/5 = 0.2 of the total global distance.
Knowing that, in order, the pairs of nodes
represent the global distance as follows:
[0.0, 0.2], (0.2, 0.4], (0.4, 0.6], (0.6, 0.8]
and (0.8, 1.0] (for the same example with 5 pairs
of nodes).

- Now that you have clear the previous steps, if
you think about a global distance of d=0.3, that
will be in the second pair of nodes (the one that
represents (0.2, 0.4] range. But that d=0.3 is in
terms of global distance, so we need to adapt it
to that pair of nodes local distance. As we
skipped 1 (the first) pair of nodes, we need to
substract its distance representation from our
global distance, so d=0.3 - 0.2 => d=0.1. Now, as
d=0.1 is a global distance value, we need to turn
it into a local distance value. As each pair of
nodes represents a 0.2 of the global distance, we
do this: d=0.1 / 0.2 => d=0.5 and we obtain a
local distance of d=0.5. That is the local
distance within the second pair of nodes (in this
example) we need to look for.

- Once we know the local distance we need to 
look for, as we now the pair of nodes X value of
each of those nodes, we can calculate the
corresponding X value for what that local distance
fits.

As you can see, we go from a global distance to
a local X value to obtain the corresponding Y
of the affected pair of nodes. This class has
been created with the purpose of following
an animation progress, so the distance we are
talking about is actually the amount of that
animation we have done previously so we can obtain
the next value we need to apply to obtain the
animation the graphic describes.
"""
from yta_general_utils.math.graphic.graphic_axis import GraphicAxis
from yta_general_utils.math.graphic.node import Node
from yta_general_utils.math.graphic.pair_of_nodes import PairOfNodes
from yta_general_utils.math.progression import Progression
from yta_programming.decorators.requires_dependency import requires_dependency
from yta_validation.parameter import ParameterValidator
from typing import Union


class Graphic:
    """
    Class to represent a Graphic in which we will
    place Nodes and apply rate functions between
    those nodes to calculate the corresponding y
    values.

    This class allows Nodes that are not placed in
    the same position. The Nodes will be ordered
    automatically by their 'x' position, but you can
    add them unordered (but unrepeated).

    This Graphic class has been created to be able
    to use them as a custom parameter modifier as
    we are able to build the Graphic we want and
    apply it to any parameter.
    """
    
    x_axis: GraphicAxis = None
    """
    The x axis which contains the min and max x 
    valid values.
    """
    y_axis: GraphicAxis = None
    """
    The y axis which contains the min and max y
    valid values.
    """
    _nodes: list[Node] = None
    """
    The list of nodes defined in the graphic to
    build it. These nodes are interconnected with
    a rate function.
    """

    @property
    def nodes(
        self
    ):
        """
        Get the nodes ordered by the x position.
        """
        return sorted(self._nodes, key = lambda node: node.position[0])
    
    @property
    def min_x(
        self
    ):
        return min(self.nodes, key = lambda node: node.x).x
    
    @property
    def max_x(
        self
    ):
        return max(self.nodes, key = lambda node: node.x).x
    
    @property
    def min_y(
        self
    ):
        return min(self.nodes, key = lambda node: node.y).y
    
    @property
    def max_y(
        self
    ):
        return max(self.nodes, key = lambda node: node.y).y
    
    @property
    def pairs_of_nodes(
        self
    ) -> list[PairOfNodes]:
        """
        Get pairs of nodes ordered by the x position. There
        is, at least, one pair of nodes that will be, if no
        more nodes added, the first and the last one.
        """
        return [
            PairOfNodes(self.nodes[index], self.nodes[index + 1])
            for index, _ in enumerate(self.nodes[1:])
        ]

    def __init__(
        self,
        x_axis: GraphicAxis,
        y_axis: GraphicAxis
    ):
        ParameterValidator.validate_mandatory_instance_of('x_axis', x_axis, GraphicAxis)
        ParameterValidator.validate_mandatory_instance_of('y_axis', y_axis, GraphicAxis)

        # TODO: Maybe make it possible to be instantiated with a
        # list of nodes
        
        self.x_axis = x_axis
        self.y_axis = y_axis
        self._nodes = []

    def add_node(
        self,
        x: float,
        y: float
    ):
        """
        Add a new node to the graphic if its position is
        inside the x and y axis ranges and if there is not
        another node in that position.

        This method returns the instance so you can chain
        more than one 'add_node' method call.
        """
        ParameterValidator.validate_mandatory_number_between('x', x, self.x_axis.min, self.x_axis.max)
        ParameterValidator.validate_mandatory_number_between('y', y, self.y_axis.min, self.y_axis.max)
        
        if self._get_node(x) is not None:
            raise Exception('There is another node in the provided "x" position.')

        self._nodes.append(Node(x, y))

        return self

    def get_n_values(
        self,
        n: int
    ):
        """
        Return a list of 'n' (x, y) values of the graphic
        from the start to the end of it.
        """
        return [
            self.get_xy_from_normalized_d(d)
            for d in Progression(0, 1, n).values
        ]

    def get_xy_from_normalized_d(
        self,
        d: float
    ):
        """
        Get a not normalized tuple (x, y) representing the
        position for the provided global distance 'd', that
        is the global distance in the whole graphic X axis.
        The lower (left) 'x' of the graphic would be
        d=0.0 and the highest (right) 'x', d=1.0.

        The distance 'd' is useful when trying to animate
        things.
        """
        x = self._get_x_from_normalized_d(d)
        _, y = self.get_xy_from_not_normalized_x(x)

        return (
            x,
            y
        )
    
    def get_xy_from_not_normalized_x(
        self,
        x: float
    ) -> tuple[float, float]:
        """
        Get a not normalized tuple (x, y) representing
        the position for the provided 'x' of the graphic.

        The returned 'x' value will be the same as the one
        provided as parameter.
        """
        ParameterValidator.validate_mandatory_number_between('x', x, self.min_x, self.max_x)
        
        return (
            x,
            self._get_pair_of_node_from_x(x).get_y_from_not_normalized_x(x).value
        )
    
    def _get_node(
        self,
        x: float
    ) -> Union[Node, None]:
        """
        Get the node placed at the provided 'x' if existing
        or None if not. This method is used internally to
        verify that there is not another node at the same
        position when adding one.
        """
        return next((
            node
            for node in self.nodes
            if node.x == x
        ), None)
    
    def _get_pair_of_node_from_x(
        self,
        x: float
    ) -> Union[PairOfNodes, None]:
        """
        Obtain the pair of nodes in which the provided 'x'
        is contained, or None if there is no pair of nodes
        for that position.
        """
        return next((
            pair_of_node
            for pair_of_node in self.pairs_of_nodes
            if x <= pair_of_node.max_x
        ), None)

    def _get_x_from_normalized_d(
        self,
        d: float
    ) -> float:
        """
        Obtain the not normalized 'x' value for the
        provided 'd', that is the global distance in the
        whole graphic X axis. The lower (left) 'x' of
        the graphic would be d=0.0 and the highest
        (right) 'x', d=1.0.

        In the graphic, the distance from the first 'x'
        to the last 'x' is d=1.0. The first (lower) 'x'
        value is d=0.0 and the last (highest) 'x' value
        is d=1.0. The graphic contains more than one 
        pair of nodes, so the actual X to which this 
        global 'd' refers to is in one of those pairs
        of nodes.

        If a graphic contains 5 pairs of nodes, as the
        global distance is d=1.0, each pair of nodes
        represents a d=0.2. First pair of nodes from
        [0.0, 0.2], second pair (0.2, 0.4], etc. So,
        if a global distance d=0.3 is requested, the
        second pair of nodes (in the example below) 
        will be used to calculate its X and the 
        corresponding Y value.
        """
        ParameterValidator.validate_mandatory_number_between('d', d, 0.0, 1.0)
        
        # 'd' is the distance within the whole graphic
        # representation with a value between [0.0, 1.0]
        num_of_pairs_of_nodes = len(self.pairs_of_nodes)
        # This is the distance that each pair of nodes is
        # representing (also between [0.0, 1.0]). As a
        # reminder, if 5 pairs of nodes, 1.0 / 5 = 0.2, so
        # each pair of nodes would be representing a 0.2
        # portion of the whole graphic distance.
        pair_of_nodes_d = 1 / num_of_pairs_of_nodes
        # Same example as above, 5 pairs of nodes:
        # d = 0.2 // 0.2 = index 1 which is for the 2nd pair
        # d = 0.3 // 0.2 = index 1 which is for the 2nd pair
        # d = 0.7 // 0.2 = index 3 which is for the 4th pair
        # TODO: Maybe let the last value (exact, so % = 0) for
        # the previous pair instead of for the next one (?)
        pair_of_nodes_index = (
            int(d // pair_of_nodes_d)
            if d != 1.0 else
            num_of_pairs_of_nodes - 1
        )
        pair_of_nodes = self.pairs_of_nodes[pair_of_nodes_index]

        # If d=0.3, we will use the 2nd pair of nodes, but that
        # as we skipped the first pair of points, we need to
        # substract the corresponding amount, so d=0.3 - 0.2 =>
        # d=0.1. Now, working locally in the 2nd pair of nodes,
        # we are looking for the d=0.1, which is a general
        # distance that we need to turn into a local one. As
        # the pair of nodes is representing a total of 0.2d of
        # the total graphic distance, that d=0.1 represents 
        # the 0.5 in the local distance of that pair of nodes:
        # d=0.2 = d=1.0 locally => 0.1 * 1 / 0.2 = 0.1 / 0.2 = 0.5
        # so the 10% (0.1d) in global terms means a 50% (0.5d) in
        # local pair of nodes terms.
        # Formula explained with the same example below:
        # X = 0.3 % (1 * 0.2) / 0.2
        # X = 0.3 % 0.2 / 0.2
        # X = 0.1 / 0.2
        # X = 0.5
        d = (
            (
                d % (pair_of_nodes_index * pair_of_nodes_d) / pair_of_nodes_d
                if pair_of_nodes_index > 0 else
                d / pair_of_nodes_d
            )
            if d != 1.0 else
            d
        )
        # Now we need to ask the pair of nodes to calculate the Y
        # position of the X that is in the 'd' local distance:
        # y = min_x + d * (max_x - min_x)
        return pair_of_nodes.left_node.x + d * (pair_of_nodes.right_node.x - pair_of_nodes.left_node.x)
    
    @requires_dependency('matplotlib', 'yta_general_utils', 'matplotlib')
    def plot(
        self
    ):
        import matplotlib.pyplot as plt
        
        # Limit and draw axis
        plt.xlim(self.x_axis.min, self.x_axis.max)
        plt.ylim(self.y_axis.min, self.y_axis.max)
        plt.axhline(0, color = 'black', linewidth = 1)
        plt.axvline(0, color = 'black', linewidth = 1)

        plt.grid(True)

        # Draw nodes
        x_vals = [node.x for node in self.nodes]
        y_vals = [node.y for node in self.nodes]
        plt.scatter(x_vals, y_vals, color = 'white', edgecolors = 'black', s = 100)

        # Draw points between nodes
        xs = []
        ys = []
        for pair_of_node in self.pairs_of_nodes:
            positions = pair_of_node.get_n_xy_values_to_plot(100)
            t_xs, t_ys = zip(*positions)
            xs += t_xs
            ys += t_ys
       
        plt.scatter(xs, ys, color = 'black', s = 1)
        
        plt.title('')
        plt.xlabel('X axis')
        plt.ylabel('Y axis')
        
        plt.show()