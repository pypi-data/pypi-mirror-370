"""
This file has been commented to delete the code in a near future
and avoid the use of 'cv2' so we can remove it as a requirement.
"""

# from yta_general_utils.temp import Temp
# from PIL import Image

# import os


# # Interesting: http://www.leancrew.com/all-this/2013/11/transparency-with-pil/
# # Also this: https://www.101computing.net/pixel-art-in-python/
# # Try this to save drawing Pixel Arts: https://stackoverflow.com/questions/41319971/is-there-a-way-to-save-turtles-drawing-as-an-animated-gif
 
# PROJECT_ABSOLUTE_PATH = os.getenv('PROJECT_ABSOLUTE_PATH')
# TOUSE_ABSOLUTE_PATH = os.getenv('TOUSE_ABSOLUTE_PATH')
# FONTS_PATH = 'C:/USERS/DANIA/APPDATA/LOCAL/MICROSOFT/WINDOWS/FONTS/'

# def test_minecraft():
#     # This can turn a video into a pixel art video, amazing
#     #test_pixelart('C:/Users/dania/Downloads/nico.MOV', 'test_pixelart.mp4')

#     ICON_FILENAME = TOUSE_ABSOLUTE_PATH + 'minecraft_resources/fav.png'

#     icon = Image.open(ICON_FILENAME)
#     img = Image.new('RGB', (icon.width, icon.height))

#     for x in range(img.width):
#         for y in range(img.height):
#             img.putpixel((x, y), (icon.getpixel((x, y))))
#             img.save(Temp.create_filename('tmp_pixel_' + str(x) + '_' + str(y) + '.png'))

#     # Try this to preview (?) (https://stackoverflow.com/questions/42719095/how-to-show-an-image-with-pillow-and-update-it)
    
# def live_preview():
#     import numpy as np
#     import cv2

#     def sin2d(x,y):
#         """2-d sine function to plot"""
#         return np.sin(x) + np.cos(y)

#     def getFrame():
#         """Generate next frame of simulation as numpy array"""

#         # Create data on first call only
#         if getFrame.z is None:
#             xx, yy = np.meshgrid(np.linspace(0,2*np.pi,w), np.linspace(0,2*np.pi,h))
#             getFrame.z = sin2d(xx, yy)
#             getFrame.z = cv2.normalize(getFrame.z,None,alpha=0,beta=1,norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_32F)

#         # Just roll data for subsequent calls
#         getFrame.z = np.roll(getFrame.z,(1,2),(0,1))
#         return getFrame.z

#     # Frame size
#     w, h = 640, 480

#     getFrame.z = None

#     while True:
#         # Get a numpy array to display from the simulation
#         npimage=getFrame()

#         cv2.imshow('image', npimage)
#         cv2.waitKey(1)

