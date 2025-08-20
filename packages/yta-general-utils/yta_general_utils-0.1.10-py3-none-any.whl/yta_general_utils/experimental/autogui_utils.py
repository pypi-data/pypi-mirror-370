"""
TODO: This is a collection of interesting utils that
should be in a different library or, at least, 
removed from the experimental folder of this one.
"""
from yta_random import Random
from time import sleep

import pyautogui


def long_wait():
    """
    Waits from 2 to 6 seconds, moving the cursor accidentally 3 times.
    """
    wait(Random.float_between(2, 6, 0.001))
    # from random import randint
    # wait(randint(2000, 6000) * 0.001)

def short_wait():
    """
    Waits from 0.4 to 2 seconds, moving the cursor accidentally 3 times.
    """
    wait(Random.float_between(0.4, 2, 0.001))
    # from random import randint
    # wait(randint(40, 200) * 0.01)

def wait(time):
    """
    Waits for the provided 'time' in seconds and
    accidentally moves the cursor 3 times.
    """
    sleep_factors = [0.23, 0.48, 0.29]
    for i in range(3):
        sleep(time * sleep_factors[i])
        x_movement = Random.int_between(1, 7)
        if Random.bool():
            x_movement = -x_movement
        y_movement = Random.int_between(1, 7)
        if Random.bool():
            y_movement = -y_movement
        pyautogui.move(x_movement, y_movement)

def write(text):
    for char in text:
        pyautogui.write(char)
        sleep(Random.float_between(0.05, 0.2, 0.001))

def scroll(height):
    times = height % 200
    for i in range(times):
        pyautogui.scroll(height / times)
        sleep(Random.float_between(0.01, 0.08, 0.001))

def click_element(driver, element):
    # TODO: Avoid passing the driver please, or refactor if possible
    move_to_element(driver, element)
    position = pyautogui.position()
    pyautogui.click(position[0], position[1])

def move_to_element(chromedriver, element):
    panel_height = chromedriver.execute_script('return window.outerHeight - window.innerHeight;')
    panel_width = chromedriver.execute_script('return window.outerWidth - window.innerWidth;')
    print('panel height: ' + str(panel_height))
    print('panel width: ' + str(panel_width))
    print('y: ' + str(element.location['y']))
    print('x: ' + str(element.location['x']))
    print('width: ' + str(element.size['width']))
    print('height: ' + str(element.size['height']))
    x = element.location['x'] + panel_width + (element.size['width'] / 2)
    y = element.location['y'] + panel_height + (element.size['height'] / 2)
    print('x: ' + str(x))
    print('y: ' + str(y))
    move_cursor_to(x, y)

def move_cursor_to(x, y):
    # We can fail and then get back
    x1, y1 = pyautogui.position()  # Starting position
    # (0, 0) is upper left
    x_error = Random.int_between(0, int(0.2 * abs(x - x1)))
    if Random.bool():
        x_error = -x_error
    y_error = Random.int_between(0, int(0.2 * abs(y - y1)))
    if Random.bool():
        y_error = -y_error

    # We move first to the position with an error
    __move_cursor_to(x + x_error, y + y_error)
    # We spend some time in realizing we failed (60 to 230ms)
    sleep(Random.float_between(0.06, 0.23, 0.001))
    # We then move to the expected position
    __move_cursor_to(x, y)

def __move_cursor_to(x2, y2):
    import numpy as np
    import time
    from scipy import interpolate
    import math

    # Any duration less than this is rounded to 0.0 to instantly move the mouse.
    pyautogui.MINIMUM_DURATION = 0  # Default: 0.1
    # Minimal number of seconds to sleep between mouse moves.
    pyautogui.MINIMUM_SLEEP = 0  # Default: 0.05
    # The number of seconds to pause after EVERY public function call.
    pyautogui.PAUSE = 0  # Default: 0.1

    def point_dist(x1,y1,x2,y2):
        return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
    
    cp = Random.int_between(2, 5)  # Number of control points. Must be at least 2.
    x1, y1 = pyautogui.position()  # Starting position

    # Distribute control points between start and destination evenly.
    x = np.linspace(x1, x2, num = cp, dtype = 'int')
    y = np.linspace(y1, y2, num = cp, dtype = 'int')

    # Randomise inner points a bit (+-RND at most).
    RND = 10
    xr = [
        Random.int_between(-RND, RND)
        for _ in range(cp)
    ]
    yr = [
        Random.int_between(-RND, RND)
        for _ in range(cp)
    ]
    xr[0] = yr[0] = xr[-1] = yr[-1] = 0
    x += xr
    y += yr

    # Approximate using Bezier spline.
    degree = 3 if cp > 3 else cp - 1  # Degree of b-spline. 3 is recommended.
    # Must be less than number of control points.
    tck, u = interpolate.splprep([x, y], k = degree)
    # Move upto a certain number of points
    u = np.linspace(0, 1, num = 2 + int(point_dist(x1, y1, x2, y2) / 50.0))
    points = interpolate.splev(u, tck)

    # Move mouse.
    duration = 0.1
    timeout = duration / len(points[0])
    point_list=zip(*(i.astype(int) for i in points))
    for point in point_list:
        #pyautogui.moveTo(*point, uniform(0.6, 1.7), pyautogui.easeOutQuad)
        pyautogui.moveTo(*point)
        time.sleep(timeout + Random.int_between(0, 1) * 0.005)