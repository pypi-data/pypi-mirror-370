"""
This is an adaption of the rate functions found in manim
library for the moviepy library. I have to use lambda t
functions with the current frame time to be able to resize
or reposition a video, so I have adapted the manim rate
functions to be able to return a factor that, with specific
moviepy functions, will make a change with the factor that
has been calculated with the corresponding rate function.

You can see 'manim/utils/rate_functions.py'.

This is the way I have found to make it work and to be able
to build smoother animations. As manim docummentation says,
the rate functions have been inspired by the ones listed in
this web page: https://easings.net/

Thanks to:
- https://github.com/semitable/easing-functions/blob/master/easing_functions/easing.py

# TODO: Check if any interesting function in
# https://github.com/semitable/easing-functions/blob/master/easing_functions/easing.py
"""
from yta_general_utils.math import Math
from yta_constants.enum import YTAEnum as Enum
from yta_validation.parameter import ParameterValidator
from yta_programming.decorators.requires_dependency import requires_dependency
from math import pow, sqrt
from typing import Callable

import numpy as np


class RateFunction(Enum):
    """
    Rate functions to be used with an 'n' value
    that is between 0.0 and 1.0. This 'n' means
    the x distance within the graphic function
    and will return the y value for that point.
    """

    LINEAR = 'linear'
    SLOW_INTO = 'slow_into'
    SMOOTH = 'smooth'
    SMOOTH_STEP = 'smooth_step'
    SMOOTHER_STEP = 'smoother_step'
    SMOOTHERER_STEP = 'smootherer_step'
    RUSH_INTO = 'rush_into'
    RUSH_FROM = 'rush_from'
    DOUBLE_SMOOTH = 'double_smooth'
    THERE_AND_BACK = 'there_and_back'
    THERE_AND_BACK_WITH_PAUSE = 'there_and_back_with_pause'
    RUNNING_START = 'running_start'
    WIGGLE = 'wiggle'
    EASE_IN_CUBIC = 'ease_in_cubic'
    EASE_OUT_CUBIC = 'ease_out_cubic'
    #SQUISH_RATE_FUNC = 'squish_rate_func'
    LINGERING = 'lingering'
    EXPONENTIAL_DECAY = 'exponential_decay'
    EASE_IN_SINE = 'ease_in_sine'
    EASE_OUT_SINE = 'ease_out_sine'
    EASE_IN_OUT_SINE = 'ease_in_out_sine'
    EASE_IN_QUAD = 'ease_in_quad'
    EASE_OUT_QUAD = 'ease_out_quad'
    EASE_IN_OUT_QUAD = 'ease_in_out_quad'
    EASE_IN_OUT_CUBIC = 'ease_in_out_cubic'
    EASE_IN_QUART = 'ease_in_quart'
    EASE_OUT_QUART = 'ease_out_quart'
    EASE_IN_OUT_QUART = 'ease_in_out_quart'
    EASE_IN_QUINT = 'ease_in_quint'
    EASE_OUT_QUINT = 'ease_out_quint'
    EASE_IN_OUT_QUINT = 'ease_in_out_quint'
    EASE_IN_EXPO = 'ease_in_expo'
    EASE_OUT_EXPO = 'ease_out_expo'
    EASE_IN_OUT_EXPO = 'ease_in_out_expo'
    EASE_IN_CIRC = 'ease_in_circ'
    EASE_OUT_CIRC = 'ease_out_circ'
    EASE_IN_OUT_CIRC = 'ease_in_out_circ'
    EASE_IN_BACK = 'ease_in_back'
    EASE_OUT_BACK = 'ease_out_back'
    EASE_IN_OUT_BACK = 'ease_in_out_back'
    EASE_IN_ELASTIC = 'ease_in_elastic'
    EASE_OUT_ELASTIC = 'ease_out_elastic'
    EASE_IN_OUT_ELASTIC = 'ease_in_out_elastic'
    EASE_IN_BOUNCE = 'ease_in_bounce'
    EASE_OUT_BOUNCE = 'ease_out_bounce'
    EASE_IN_OUT_BOUNCE = 'ease_in_out_bounce'

    @property
    def function(self):
        """
        The function to calculate the value of a given 'n'.
        You can call this function by passing a 'n' value
        and any other needed key parameter.
        """
        return {
            RateFunction.LINEAR: RateFunction.linear,
            RateFunction.SLOW_INTO: RateFunction.slow_into,
            RateFunction.SMOOTH: RateFunction.smooth,
            RateFunction.SMOOTH_STEP: RateFunction.smooth_step,
            RateFunction.SMOOTHER_STEP: RateFunction.smoother_step,
            RateFunction.SMOOTHERER_STEP: RateFunction.smootherer_step,
            RateFunction.RUSH_INTO: RateFunction.rush_into,
            RateFunction.RUSH_FROM: RateFunction.rush_from,
            RateFunction.DOUBLE_SMOOTH: RateFunction.double_smooth,
            RateFunction.THERE_AND_BACK: RateFunction.there_and_back,
            RateFunction.THERE_AND_BACK_WITH_PAUSE: RateFunction.there_and_back_with_pause,
            # RateFunction.RUNNING_START: RateFunction.running_start,
            RateFunction.WIGGLE: RateFunction.wiggle,
            RateFunction.EASE_IN_CUBIC: RateFunction.ease_in_cubic,
            RateFunction.EASE_OUT_CUBIC: RateFunction.ease_out_cubic,
            #RateFunction.SQUISH_RATE_FUNC: squish_rate_func,
            RateFunction.LINGERING: RateFunction.lingering,
            RateFunction.EXPONENTIAL_DECAY: RateFunction.exponential_decay,
            RateFunction.EASE_IN_SINE: RateFunction.ease_in_sine,
            RateFunction.EASE_OUT_SINE: RateFunction.ease_out_sine,
            RateFunction.EASE_IN_OUT_SINE: RateFunction.ease_in_out_sine,
            RateFunction.EASE_IN_QUAD: RateFunction.ease_in_quad,
            RateFunction.EASE_OUT_QUAD: RateFunction.ease_out_quad,
            RateFunction.EASE_IN_OUT_QUAD: RateFunction.ease_in_out_quad,
            RateFunction.EASE_IN_OUT_CUBIC: RateFunction.ease_in_cubic,
            RateFunction.EASE_IN_QUART: RateFunction.ease_in_quart,
            RateFunction.EASE_IN_OUT_QUART: RateFunction.ease_in_out_quart,
            RateFunction.EASE_IN_QUINT: RateFunction.ease_in_quint,
            RateFunction.EASE_OUT_QUINT: RateFunction.ease_out_quint,
            RateFunction.EASE_IN_OUT_QUINT: RateFunction.ease_in_out_quint,
            RateFunction.EASE_IN_EXPO: RateFunction.ease_in_expo,
            RateFunction.EASE_OUT_EXPO: RateFunction.ease_out_expo,
            RateFunction.EASE_IN_OUT_EXPO: RateFunction.ease_in_out_expo,
            RateFunction.EASE_IN_CIRC: RateFunction.ease_in_circ,
            RateFunction.EASE_OUT_CIRC: RateFunction.ease_out_circ,
            RateFunction.EASE_IN_OUT_CIRC: RateFunction.ease_in_out_circ,
            RateFunction.EASE_IN_BACK: RateFunction.ease_in_back,
            RateFunction.EASE_OUT_BACK: RateFunction.ease_out_back,
            RateFunction.EASE_IN_OUT_BACK: RateFunction.ease_in_out_back,
            RateFunction.EASE_IN_ELASTIC: RateFunction.ease_in_elastic,
            RateFunction.EASE_OUT_ELASTIC: RateFunction.ease_out_elastic,
            RateFunction.EASE_IN_OUT_ELASTIC: RateFunction.ease_in_out_elastic,
            RateFunction.EASE_IN_BOUNCE: RateFunction.ease_in_bounce,
            RateFunction.EASE_OUT_BOUNCE: RateFunction.ease_out_bounce,
            RateFunction.EASE_IN_OUT_BOUNCE: RateFunction.ease_in_out_bounce,
        }[self]

    def get_n_value(
        self,
        n: float,
        **kwargs
    ) -> float:
        """
        Apply the rate function to the given 'n' and
        kwargs and obtain the value for that 'n'.

        The 'n' parameter must be a normalized value
        (a value between 0 and 1).

        The result will be the corresponding 'y' 
        value for the given 'n' value.
        """
        ParameterValidator.validate_mandatory_number_between('n', n, 0, 1)

        return self.function(n, **kwargs)
    
    @requires_dependency('matplotlib', 'yta_general_utils', 'matplotlib')
    def plot(
        self,
        n: int = 100
    ):
        """
        Plot a graphic representing 'n' values from
        0.0 to 1.0 to see how the rate function works.
        """
        import matplotlib.pyplot as plt
        
        # Limit and draw axis
        plt.xlim(0, 1)
        plt.ylim(0, 1)
        plt.axhline(0, color = 'black', linewidth = 1)
        plt.axvline(0, color = 'black', linewidth = 1)

        plt.grid(True)

        # We will draw 'n'' values between 0.0 and 1.1
        x_vals = np.linspace(0.0, 1.0, n).tolist()
        y_vals = [
            self.get_n_value(x)
            for x in x_vals
        ]
        plt.scatter(x_vals, y_vals, color = 'white', edgecolors = 'black', s = 100)

        # TODO: I think we don't need to draw anything
        # else. Remove this below if it is ok.
        # # Draw points between nodes
        # for pair_of_node in self.pairs_of_nodes:
        #     positions = pair_of_node.get_n_xy_values_to_plot(100)
        #     t_xs, t_ys = zip(*positions)
        #     xs += t_xs
        #     ys += t_ys
       
        # plt.scatter(xs, ys, color = 'black', s = 1)
        
        plt.title('')
        plt.xlabel('X axis')
        plt.ylabel('Y axis')
        
        plt.show()

    @staticmethod
    def linear(
        n: float
    ) -> float:
        return n
    
    @staticmethod
    def slow_into(
        n: float
    ) -> float:
         return np.sqrt(1 - (1 - n) * (1 - n))
    
    @staticmethod
    def smooth(
        n: float,
        inflection: float = 10.0
    ) -> float:
        error = Math.sigmoid(-inflection / 2)

        return min(
            max((Math.sigmoid(inflection * (n - 0.5)) - error) / (1 - 2 * error), 0),
            1,
        )

    @staticmethod
    def smooth_step(
        n: float
    ) -> float:
        """
        Implementation of the 1st order SmoothStep sigmoid function.
        The 1st derivative (speed) is zero at the endpoints.
        https://en.wikipedia.org/wiki/Smoothstep
        """
        return (
            0
            if n <= 0 else
            (
                3 * n**2 - 2 * n**3
                if n < 1 else
                1
            )
        )

    @staticmethod
    def smoother_step(
        n: float
    ) -> float:
        """
        Implementation of the 2nd order SmoothStep sigmoid function.
        The 1st and 2nd derivatives (speed and acceleration) are zero at the endpoints.
        https://en.wikipedia.org/wiki/Smoothstep
        """
        return (
            0
            if n <= 0 else
            (
                6 * n**5 - 15 * n**4 + 10 * n**3
                if n < 1 else
                1
            )
        )

    @staticmethod
    def smootherer_step(
        n: float
    ) -> float:
        """
        Implementation of the 3rd order SmoothStep sigmoid function.
        The 1st, 2nd and 3rd derivatives (speed, acceleration and jerk) are zero at the endpoints.
        https://en.wikipedia.org/wiki/Smoothstep
        """
        return (
            35 * n**4 - 84 * n**5 + 70 * n**6 - 20 * n**7
            if 0 < n < 1 else
            1
            if n >= 1 else
            0
        )

    @staticmethod
    def rush_into(
        n: float,
        inflection: float = 10.0
    ) -> float:
        return 2 * RateFunction.smooth(n / 2.0, inflection)

    @staticmethod
    def rush_from(
        n: float,
        inflection: float = 10.0
    ) -> float:
        return 2 * RateFunction.smooth(n / 2.0 + 0.5, inflection) - 1

    @staticmethod
    def double_smooth(
        n: float
    ) -> float:
        return (
            0.5 * RateFunction.smooth(2 * n)
            if n < 0.5 else
            0.5 * (1 + RateFunction.smooth(2 * n - 1))
        )

    @staticmethod    
    def there_and_back(
        n: float,
        inflection: float = 10.0
    ) -> float:
        n = (
            2 * n
            if n < 0.5 else
            2 * (1 - n)
        )

        return RateFunction.smooth(n, inflection)

    @staticmethod
    def there_and_back_with_pause(
        n: float,
        pause_ratio: float = 1.0 / 3
    ) -> float:
        a = 1.0 / pause_ratio

        return (
            RateFunction.smooth(a * n)
            if n < 0.5 - pause_ratio / 2 else
            1
            if n < 0.5 + pause_ratio / 2 else
            RateFunction.smooth(a - a * n)
        )

    # @staticmethod    
    # def running_start(
    #     n: float,
    #     pull_factor: float = -0.5
    # ) -> float:
    #     # TODO: This is being taken from manim, but I don't
    #     # want the dependency here, so it is commented by 
    #     # now
    #     from manim.utils.bezier import bezier

    #     return bezier([0, 0, pull_factor, pull_factor, 1, 1, 1])(n)

    @staticmethod
    def wiggle(
        n: float,
        wiggles: float = 2
    ) -> float:
        # TODO: Manim says 'not_quite_there' function is not working
        return RateFunction.there_and_back(n) * np.sin(wiggles * np.pi * n)

    @staticmethod
    def ease_in_cubic(
        n: float
    ) -> float:
        return n * n * n

    @staticmethod
    def ease_out_cubic(
        n: float
    ) -> float:
        return 1 - pow(1 - n, 3)

    @staticmethod
    # TODO: What is this (?)
    def squish_rate_func(
        func: Callable[[float], float],
        a: float = 0.4,
        b: float = 0.6
    ) -> Callable[[float], float]:
        def result(
            n: float
        ):
            return (
                a
                if a == b else
                func(0)
                if n < a else
                func(1)
                if n > b else
                func((n - a) / (b - a))
            )

        return result

    @staticmethod
    def lingering(
        n: float
    ) -> float:
        return RateFunction.squish_rate_func(lambda n: n, 0, 0.8)(n)

    @staticmethod
    def exponential_decay(
        n: float,
        half_life: float = 0.1
    ) -> float:
        # The half-life should be rather small to minimize
        # the cut-off error at the end
        return 1 - np.exp(-n / half_life)

    @staticmethod
    def ease_in_sine(
        n: float
    ) -> float:
        return 1 - np.cos((n * np.pi) / 2)

    @staticmethod
    def ease_out_sine(
        n: float
    ) -> float:
        return np.sin((n * np.pi) / 2)

    @staticmethod
    def ease_in_out_sine(
        n: float
    ) -> float:
        return -(np.cos(np.pi * n) - 1) / 2

    @staticmethod
    def ease_in_quad(
        n: float
    ) -> float:
        return n * n

    @staticmethod
    def ease_out_quad(
        n: float
    ) -> float:
        return 1 - (1 - n) * (1 - n)

    @staticmethod
    def ease_in_out_quad(
        n: float
    ) -> float:
        return (
            2 * n * n
            if n < 0.5 else
            1 - pow(-2 * n + 2, 2) / 2
        )

    @staticmethod
    def ease_in_out_cubic(
        n: float
    ) -> float:
        return (
            4 * n * n * n
            if n < 0.5 else
            1 - pow(-2 * n + 2, 3) / 2
        )

    @staticmethod
    def ease_in_quart(
        n: float
    ) -> float:
        return n * n * n * n

    @staticmethod
    def ease_out_quart(
        n: float
    ) -> float:
        return 1 - pow(1 - n, 4)

    @staticmethod
    def ease_in_out_quart(
        n: float
    ) -> float:
        return (
            8 * n * n * n * n
            if n < 0.5 else
            1 - pow(-2 * n + 2, 4) / 2
        )

    @staticmethod
    def ease_in_quint(
        n: float
    ) -> float:
        return n * n * n * n * n

    @staticmethod
    def ease_out_quint(
        n: float
    ) -> float:
        return 1 - pow(1 - n, 5)

    @staticmethod
    def ease_in_out_quint(
        n: float
    ) -> float:
        return (
            16 * n * n * n * n * n
            if n < 0.5 else
            1 - pow(-2 * n + 2, 5) / 2
        )

    @staticmethod
    def ease_in_expo(
        n: float
    ) -> float:
        return (
            0
            if n == 0 else
            pow(2, 10 * n - 10)
        )

    @staticmethod
    def ease_out_expo(
        n: float
    ) -> float:
        return (
            1
            if n == 1 else
            1 - pow(2, -10 * n)
        )

    @staticmethod
    def ease_in_out_expo(
        n: float
    ) -> float:
        return (
            0
            if n == 0 else
            1
            if n == 1 else
            pow(2, 20 * n - 10) / 2
            if n < 0.5 else
            (2 - pow(2, -20 * n + 10)) / 2
        )

    @staticmethod    
    def ease_in_circ(
        n: float
    ) -> float:
        return 1 - sqrt(1 - pow(n, 2))

    @staticmethod
    def ease_out_circ(
        n: float
    ) -> float:
        return sqrt(1 - pow(n - 1, 2))

    @staticmethod
    def ease_in_out_circ(
        n: float
    ) -> float:
        return (
            (1 - sqrt(1 - pow(2 * n, 2))) / 2
            if n < 0.5
            else (sqrt(1 - pow(-2 * n + 2, 2)) + 1) / 2
        )

    @staticmethod
    def ease_in_back(
        n: float
    ) -> float:
        c1 = 1.70158
        c3 = c1 + 1

        return c3 * n * n * n - c1 * n * n

    @staticmethod
    def ease_out_back(
        n: float
    ) -> float:
        c1 = 1.70158
        c3 = c1 + 1

        return 1 + c3 * pow(n - 1, 3) + c1 * pow(n - 1, 2)

    @staticmethod
    def ease_in_out_back(
        n: float
    ) -> float:
        c1 = 1.70158
        c2 = c1 * 1.525

        return (
            (pow(2 * n, 2) * ((c2 + 1) * 2 * n - c2)) / 2
            if n < 0.5 else
            (pow(2 * n - 2, 2) * ((c2 + 1) * (n * 2 - 2) + c2) + 2) / 2
        )

    @staticmethod
    def ease_in_elastic(
        n: float
    ) -> float:
        c4 = (2 * np.pi) / 3

        return (
            0
            if n == 0 else
            1
            if n == 1 else
            -pow(2, 10 * n - 10) * np.sin((n * 10 - 10.75) * c4)
        )

    @staticmethod
    def ease_out_elastic(
        n: float
    ) -> float:
        c4 = (2 * np.pi) / 3

        return (
            0
            if n == 0 else
            1
            if n == 1 else
            pow(2, -10 * n) * np.sin((n * 10 - 0.75) * c4) + 1
        )

    @staticmethod    
    def ease_in_out_elastic(
        n: float
    ) -> float:
        c5 = (2 * np.pi) / 4.5

        return (
            0
            if n == 0 else
            1
            if n == 1 else
            -(pow(2, 20 * n - 10) * np.sin((20 * n - 11.125) * c5)) / 2
            if n < 0.5 else
            (pow(2, -20 * n + 10) * np.sin((20 * n - 11.125) * c5)) / 2 + 1
        )

    @staticmethod        
    def ease_in_bounce(
        n: float
    ) -> float:
        return 1 - RateFunction.ease_out_bounce(1 - n)

    @staticmethod
    def ease_out_bounce(
        n: float
    ) -> float:
        n1 = 7.5625
        d1 = 2.75

        return (
            n1 * n * n
            if n < 1 / d1 else
            n1 * (n - 1.5 / d1) * (n - 1.5 / d1) + 0.75
            if n < 2 / d1 else
            n1 * (n - 2.25 / d1) * (n - 2.25 / d1) + 0.9375
            if n < 2.5 / d1 else
            n1 * (n - 2.625 / d1) * (n - 2.625 / d1) + 0.984375
        )

    @staticmethod
    def ease_in_out_bounce(
        n: float
    ) -> float:
        return (
            (1 - RateFunction.ease_out_bounce(1 - 2 * n)) / 2
            if n < 0.5 else
            (1 + RateFunction.ease_out_bounce(2 * n - 1)) / 2
        )