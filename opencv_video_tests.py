#!/usr/bin/env python3

# WESmith 01/18/22 test webcam and picam from opencv capture
# and picamera capture on the rpi 4.

from picamera import PiCamera
from picamera.array import PiRGBArray
import cv2
import time, datetime, argparse

print('openCV version {}'.format(cv2.__version__))

BASE_WIDTH  = 320
BASE_HEIGHT = 240

def init(sleep=1, fps=15.0):
    # fps is a rough initial frame/sec value
    time.sleep(sleep) # delay for camera warm-up
    return fps, time.time()


def add_info(frame, fps, camNam, wid_hei):
    font   = cv2.FONT_HERSHEY_SIMPLEX
    scale  = wid_hei[0] / BASE_WIDTH
    f_size = 0.30 * scale
    separation = int(5 * scale)
    row0   = 30
    col0   = 10
    delta  = int(1 * scale)
    #thick  = 2 if scale >= 1 else 1
    thick = 1

    fpstxt = '{}: {:4.0f} FPS for {} x {}'.\
                 format(camNam, fps, *wid_hei)
    cv2.putText(frame, fpstxt, (col0, row0),
                font, f_size,
                (120, 255, 120), thick) # light green

    timestamp = datetime.datetime.now()
    # %f adds the microseconds, for latency testing
    txt = timestamp.strftime("%d %B %Y %I:%M:%S %p %f")
    cv2.putText(frame, txt, (col0, row0 + 15 * delta),
                font, f_size,
                (120, 255, 120), thick) # light green


def openCV_capture(picam, wid_hei, alpha):

    if picam:
        # note: picam is hooked to the '0'
        # connector, the webcam is '1':
        cam    = cv2.VideoCapture(0)
        camNam = 'piCam, openCV capture'

    else:
        # the following is for the webcam:
        # use '1' if picam used in slot '0'
        cam    = cv2.VideoCapture(1)
        camNam = 'webCam, openCV capture'

    cam.set(cv2.CAP_PROP_FRAME_WIDTH,  wid_hei[0])
    cam.set(cv2.CAP_PROP_FRAME_HEIGHT, wid_hei[1])

    fps, t_old = init(sleep=1, fps=15.0)

    while True:

        t_now = time.time()
        fps   = alpha * fps + (1 - alpha) / (t_now - t_old)
        t_old = t_now

        _, frame = cam.read()

        add_info(frame, fps, camNam, wid_hei)

        cv2.imshow(camNam, frame)

        if cv2.waitKey(1) == ord('q'):
            break

    cam.release()
    cv2.destroyAllWindows()


def picamera_capture(picam, wid_hei, alpha):

    if picam:
        camera = PiCamera(0)
        camNam = 'piCam, picamera capture'

    else:
        # NOTE: from picam/webcam experiments, the picam
        # is superior to the webcam (re: FPS) and the openCV
        # capture is better than the picamera capture
        # (re: FPS) so there are no plans to implement this
        # webcam/picamera combination
        txt = '\nPicamera capture of webcam '
        txt += 'is not implemented at this time.\n'
        print(txt)
        exit()
        #camera = PiCamera(1) # '1' not working yet
        #camNam = 'webCam, picamera capture'

    camera.resolution = wid_hei
    output = PiRGBArray(camera, size=wid_hei)
    camera.framerate = 60 # this didn't help: see 01/18/22 enotes

    fps, t_old = init(sleep=1, fps=15.0)

    for image in camera.capture_continuous(output, format='bgr',
                                           use_video_port=True):
        t_now = time.time()
        fps   = alpha * fps + (1 - alpha) / (t_now - t_old)
        t_old = t_now

        frame = image.array

        add_info(frame, fps, camNam, wid_hei)

        cv2.imshow(camNam, frame)

        output.truncate(0)

        if cv2.waitKey(1) == ord('q'):
            break

    cv2.destroyAllWindows()


def run(opencv=False, picam=True, scale=2, alpha=0.95):
    '''
    opencv: True: opencv capture, False: picamera capture
    picam:  True: picam, False: webcam
    scale:  1: 320x240, 2: 640x480, 3: 960x720, 4: 1280x960
    alpha:  smoothing factor for frame/sec estimate,
            float 0 to 1; the larger alpha, the more smoothing
    '''
    dispW   = BASE_WIDTH  * scale
    dispH   = BASE_HEIGHT * scale
    wid_hei = (dispW, dispH)

    if opencv:
        openCV_capture(picam, wid_hei, alpha)
    else:
        picamera_capture(picam, wid_hei, alpha)


if __name__=='__main__':

    run(opencv=True, picam=True, scale=1, alpha=0.95)
# NOTE: include 'press q in video-display window to quit'