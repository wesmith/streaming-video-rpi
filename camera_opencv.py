import os
import cv2
from base_camera import BaseCamera
import datetime          # WS
import rpi_status as ws  # WS module
from time import time    # WS


def sec_to_dhms(sec): # seconds to day, hour, min, sec
    dd, r  = divmod(sec, 24*3600)
    hh, r  = divmod(r,      3600)
    mm, ss = divmod(r,        60)
    return 'Camera uptime: {} D, {} H, {} M, {:.1f} S'.\
            format(int(dd), int(hh), int(mm), ss)

def add_info(frame, fps, cam_uptime, scale, wid_hei, msg): # WS
    font   = cv2.FONT_HERSHEY_SIMPLEX
    f_size = 0.90 * scale
    separation = int(10 * scale)
    row0   = frame.shape[0] - separation
    col0   = 10
    delta  = int(30 * scale)
    thick  = 2 if scale >= 1 else 1

    timestamp = datetime.datetime.now()
    # %f adds the microseconds, for latency testing
    txt = timestamp.strftime("%d %B %Y %I:%M:%S %p %f")
    cv2.putText(frame, txt, (col0, row0), font, f_size,
                (255, 120, 255), thick) # light magenta
    temp = ws.get_temp()
    temp = '{}: {}'.format(*temp)
    cv2.putText(frame, temp, (col0, row0 - delta), font, f_size,
                (0, 255, 255), thick) # bright yellow
    #uptime = ws.get_uptime()  # system uptime
    #uptime = '{}: {}'.format(*uptime)
    uptime = sec_to_dhms(cam_uptime)
    cv2.putText(frame, uptime, (col0, row0 - 2 * delta), font, f_size,
                (255, 255, 120), thick) # light cyan
    fps = '{:4.1f} FPS for width {}, height {}'.format(fps, *wid_hei)
    cv2.putText(frame, fps, (col0, row0 - 3 * delta), font, f_size,
                (120, 255, 120), thick) # light green
    msg = '{}'.format(msg)
    cv2.putText(frame, msg, (col0, row0 - 4 * delta), font, f_size,
                (255, 255, 255), thick) # white
    return frame

class Camera(BaseCamera):
    video_source = 1  # WS if only webcam, this is 0; if picam connected, this is 1
    #message = None  # WS

    def __init__(self, message=None):
        if os.environ.get('OPENCV_CAMERA_SOURCE'):
            val = int(os.environ['OPENCV_CAMERA_SOURCE']) # WS
            Camera.set_video_source(val) # WS: shorten line
            
        Camera.message = message # WS
       
        super(Camera, self).__init__()
        
    @staticmethod
    def set_video_source(source):
        Camera.video_source = source
        
    @staticmethod
    def frames():
        cam = cv2.VideoCapture(Camera.video_source)
        if not cam.isOpened():
            raise RuntimeError('Could not start camera.')

        # WS some size options (not a complete list)
        # develop at 'large' or 'medium'
        size = 'large' #'medium'
        sizes = {'small':  ( 160, 120), # image too small
                 'medium': ( 320, 240), # ok for development
                 'large':  ( 640, 480), # ok for development
                 'Xlarge': (1280, 960)} # image too big
        scale = {'small': 0.25, 'medium': 0.50, 
                 'large': 1.00, 'Xlarge': 2.00}
        wid, hei = sizes[size]
        cam.set(cv2.CAP_PROP_FRAME_WIDTH,  wid)  # WS
        cam.set(cv2.CAP_PROP_FRAME_HEIGHT, hei)  # WS
        
        fps   = 15.0   # WS a rough initial value
        t_start = t_old = time() # WS
        # WS alpha: smoothing factor for frame/sec estimate,
        # float 0 to 1; the larger alpha, the more smoothing
        alpha = 0.9

        # processing flags
        INVERT = False
        BLUR   = False
        FLIP   = False
        
        while True:
            # WS calculate frames/sec (fps) in while loop
            dt    = time() - t_old
            t_old = time()
            fps   = alpha * fps + (1 - alpha) / dt
            cam_uptime = t_old - t_start  # time cam on in sec
            
            # read current frame
            _, img = cam.read()

            # get user's button-push from the web page
            msg = Camera.message
            
            # get processing flags
            if msg.value =='0':
                INVERT = BLUR = FLIP = GRAY = False

            # invert colors
            if msg.value == '10': INVERT = True
            if msg.value == '11': INVERT = False

            # blur image with kw x kw kernel
            if msg.value == '42':
                BLUR = True; kw = msg.kernel
            if msg.value == '41': BLUR = False

            # flip image
            if msg.value == '20':
                FLIP = True; flip_val =  1 # horiz
            if msg.value == '21':
                FLIP = True; flip_val =  0 # vert
            if msg.value == '22':
                FLIP = True; flip_val = -1 # 180 deg
            if msg.value == '23': FLIP = False

            # grayscale
            if msg.value == '30': GRAY = True
            if msg.value == '31': GRAY = False

            # image processing steps go here

            if INVERT: img = ~img
            if BLUR:   img = cv2.blur(img, (kw, kw))
            if FLIP:   img = cv2.flip(img, flip_val)

            # add text on image after processing
            mapper = {1: 'ON', 0: 'OFF'}
            button_state = 'INVERT {}, BLUR {}, FLIP {}, GRAY {}'.\
                            format(mapper[INVERT], mapper[BLUR],
                                   mapper[FLIP], mapper[GRAY])
            img = add_info(img, fps, cam_uptime,
                           scale[size], sizes[size], button_state)
                           #msg.mapping[msg.value]) # WS

            # do this after change-detection algorithm and adding text
            # note: 3 channels going to 1 channel
            if GRAY:   img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            # encode as a jpeg image and return it
            yield cv2.imencode('.jpg', img)[1].tobytes()
