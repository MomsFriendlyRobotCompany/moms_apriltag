import cv2


bgr2rgb = lambda im: cv2.cvtColor(im, cv2.COLOR_BGR2RGB)
rgb2bgr = lambda im: cv2.cvtColor(im, cv2.COLOR_RGB2BGR)

bgr2gray = lambda im: cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
gray2bgr = lambda im: cv2.cvtColor(im, cv2.COLOR_GRAY2BGR)

rgb2gray = lambda im: cv2.cvtColor(im, cv2.COLOR_RGB2GRAY)
gray2rgb = lambda im: cv2.cvtColor(im, cv2.COLOR_GRAY2RGB)