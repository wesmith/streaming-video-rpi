#!/usr/bin/env python3

# WESmith 01/18/22 run webcam and picam from opencv on the rpi 4.


import cv2
from time import time

print(cv2.__version__)

scale = 2
dispW = 320 * scale
dispH = 240 * scale
flip = 0

fps   = 15.0 #  a rough initial value
t_old = time()
# alpha: smoothing factor for frame/sec estimatee
# float 0 to 1; the larger alpha, the more smoothing
alpha = 0.95
wid_hei = (dispW, dispH)


picam = True

if picam:
    # note: picam is hooked to the '0' connector, the webcam is '1':
    cam = cv2.VideoCapture(0)
    cam.set(cv2.CAP_PROP_FRAME_WIDTH,  dispW)
    cam.set(cv2.CAP_PROP_FRAME_HEIGHT, dispH)
    camNam = 'piCam'

else:
    # the following is for the webcam: use '1' if picam used in slot '0'
    cam = cv2.VideoCapture(1)
    cam.set(cv2.CAP_PROP_FRAME_WIDTH,  dispW)
    cam.set(cv2.CAP_PROP_FRAME_HEIGHT, dispH)
    camNam = 'webCam'

actual_dispW = int(cam.get(cv2.CAP_PROP_FRAME_WIDTH))  # this doesn't reflect the 'set' command
actual_dispH = int(cam.get(cv2.CAP_PROP_FRAME_HEIGHT)) # ditto

print('\nUSER-DEFINED DISPLAY WIDTH, HEIGHT: {} {}\n'.\
      format(dispW, dispH))

def add_info(frame, fps):
    font   = cv2.FONT_HERSHEY_SIMPLEX
    f_size = 0.40 * scale
    separation = int(5 * scale)
    row0   = 30
    col0   = 10
    delta  = int(0 * scale)
    thick  = 2 if scale >= 1 else 1
    cv2.putText(frame, fps, (col0, row0 - 3 * delta), font, f_size,
                (120, 255, 120), thick) # light green


while True:

    dt    = time() - t_old
    t_old = time()
    fps   = alpha * fps + (1 - alpha) / dt

    ret, frame = cam.read()

    fpstxt = '{}: {:4.1f} FPS for {} x {}'.format(camNam, fps, *wid_hei)
    add_info(frame, fpstxt)

    cv2.imshow(camNam, frame)

    if cv2.waitKey(1) == ord('q'):
        break

cam.release()
cv2.destroyAllWindows()

