from math import gcd


# TODO: Maybe I can refactor this with the new method below
# TODO: Is this interesting or can I remove it?
def resize_to_fit_on_region(
    element_size: tuple,
    region_size: tuple
):
    """
    This method calculates the size that the 'element_size' must be
    resized to in order to fit the provided 'region_size'. Fitting 
    means that the element will cover the whole region.

    This method is useful to resize images or videos that will be
    placed behind alpha (transparent) areas of images so they will
    fit perfectly.

    This method returns a group of two values that are the expected
    element width and height (w, h).
    """
    # TODO: Check that the format is ok and the values are also ok
    if (
        len(element_size) != 2 or
        len(region_size) != 2
    ):
        raise Exception('The provided "element_size" and "region_size" parameters are not tuples of (w, h) values.')

    element_width, element_height = element_size
    region_width, region_height = region_size

    great_common_divisor = gcd(element_width, element_height)
    step_x = element_width / great_common_divisor
    step_y = element_height / great_common_divisor

    # Make sure they are even numbers to be able to move at least
    # one pixel on each side
    if (
        step_x % 2 != 0 or
        step_y % 2 != 0
    ):
        step_x *= 2
        step_y *= 2

    # If element is larger than region, we need to make it smaller.
    # In any other case, bigger
    if (
        element_width > region_width and
        element_height > region_height
    ):
        step_x = -step_x
        step_y = -step_y
    
    do_continue = True
    tmp_size = [element_width, element_height]
    while (do_continue):
        tmp_size = [tmp_size[0] + step_x, tmp_size[1] + step_y]

        if (
            step_x < 0 and
            (
                tmp_size[0] < region_width or
                tmp_size[1] < region_height
            )
        ):
            # The previous step had the right dimensions
            tmp_size[0] += abs(step_x)
            tmp_size[1] += abs(step_y)
            do_continue = False
        elif (
            step_x > 0 and
            (
                tmp_size[0] > region_width and
                tmp_size[1] > region_height
            )
        ):
            # This step is ok
            do_continue = False

    return (
        tmp_size[0],
        tmp_size[1]
    )