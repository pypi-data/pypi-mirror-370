"""
This file has been commented to delete the code in a near future
and avoid the use of 'cv2' so we can remove it as a requirement.
"""

# import cv2


# def detect_faces(image_filename):
#     """
#     This method receives the 'image_filename' image input and detects the faces that
#     are in that image. It returns an array with all existing faces, with their coordinates
#     and the width and height of the rectangle that surrounds the face.
#     """
#     # I used this: https://www.datacamp.com/tutorial/face-detection-python-opencv
#     img = cv2.imread(image_filename)
#     gray_image = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

#     face_classifier = cv2.CascadeClassifier(
#         cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
#     )

#     face = face_classifier.detectMultiScale(
#         gray_image, scaleFactor = 1.1, minNeighbors = 5, minSize = (40, 40)
#     )

#     faces_detected = []

#     for (x, y, w, h) in face:
#         faces_detected.append({
#             'x': x,
#             'y': y,
#             'width': w,
#             'height': h,
#         })
#         #cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 4)

#     #cv2.imwrite('wip/screenshot_with_faces.png', img)
        
#     return faces_detected
    
# def detect_humans(image_filename):
#     """
#     This method receives the 'image_filename' image input and detects the humans that
#     are in that image. It returns an array with all existing humans, with their coordinates
#     and the width and height of the rectangle that surrounds the human.

#     This works only for human full bodies.
#     """
#     # Reading the Image
#     image = cv2.imread(image_filename)

#     # initialize the HOG descriptor
#     hog = cv2.HOGDescriptor()
#     hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

#     # detect humans in input image
#     (humans, _) = hog.detectMultiScale(image, winStride = (10, 10), padding = (32, 32), scale = 1.1)

#     # getting no. of human detected
#     print('Human Detected : ', len(humans))

#     humans_detected = []

#     # loop over all detected humans
#     for (x, y, w, h) in humans:
#         humans_detected.append({
#             'x': x,
#             'y': y,
#             'width': w,
#             'height': h,
#         })
#         pad_w, pad_h = int(0.15 * w), int(0.01 * h)
#         cv2.rectangle(image, (x + pad_w, y + pad_h), (x + w - pad_w, y + h - pad_h), (0, 255, 0), 2)

#     cv2.imwrite('wip/test_human_detection.png', image)

#     return humans_detected