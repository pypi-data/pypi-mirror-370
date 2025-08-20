from dataclasses import dataclass


@dataclass
class Node:
    """
    Class that represent a Node in a Graphic, which
    has to be inside the limits (this is checked by
    the Graphic when added to it).
    """
    
    position: tuple[float, float]

    @property
    def x(
        self
    ) -> float:
        return self.position[0]

    @property
    def y(
        self
    ) -> float:
        return self.position[1]

    def __init__(
        self,
        x: float,
        y: float
    ):
        self.position = (x, y)