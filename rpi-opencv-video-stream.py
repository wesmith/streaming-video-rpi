#!/usr/bin/env python3

# WS TODO
# - (done) run webcam via opencv
# - add command-line inputs: camera type, url, port, frame size
# - fix the stylesheet
# - add change-detection, other algos


from importlib import import_module
import os
from flask import Flask, render_template, Response
from flask import jsonify, request

# import camera driver
if os.environ.get('CAMERA'):
    Camera = import_module('camera_' +\
                           os.environ['CAMERA']).Camera
else:
    from camera import Camera

# Raspberry Pi camera module (requires picamera package)
# from camera_pi import Camera

default_button = ['DEFAULT_VALUES', 0]

invert = {'INVERT_COLORS': {'YES': 10, 'NO': 11}}
flip   = {'FLIP_IMAGE':{'HORIZ': 20, 'VERT': 21,
                        '180_DEG': 22, 'NO_FLIP': 23}}
gray   = {'GRAYSCALE': {'YES': 30, 'NO': 31}}
blur   = {'BLUR':      {'TURN_OFF': 41}}

button_vals  = {'0': 'DEFAULT',
               '10': 'INVERT ON',  '11': 'INVERT OFF',
               '20': 'FLIP HORIZ', '21': 'FLIP VERT',
               '22': 'FLIP 180 DEG', '23': 'NO FLIP',
               '30': 'GRAYSCALE',   '31': 'COLOR',
               '41': 'NO BLURRING', '42': 'BLURRING ON'}

class Message():
    def __init__(self, button_vals):
        self.value   = '0'
        self.mapping = button_vals
        self.kernel  = None

msg = Message(button_vals)

app = Flask(__name__)

@app.route('/')
def index():
    """Video streaming home page."""
    return render_template('index.html',
                           default=default_button,
                           invert=invert,
                           flip=flip,
                           gray=gray,
                           blur=blur)
def gen(camera):
    """Video streaming generator function."""
    yield b'--frame\r\n'
    while True:
        frame = camera.get_frame()
        yield b'Content-Type: image/jpeg\r\n\r\n' + frame +\
              b'\r\n--frame\r\n'

@app.route('/button_input', methods=['POST', 'GET'])
def button_inputs():
    # update the message to the Camera class from button inputs
    if request.method == "POST":
        result_txt = request.form['button_value']
        # '999' is the symbol to indicate
        #       blurring-kernel size input
        if result_txt[-3:] == '999':
            val = result_txt[:-3] # strip off the symbol
            print('val: {}'.format(val))
            ttt = 'Blurring with kernel size {} x {}'.format(val, val)
            print(ttt)
            msg.value  = '42'
            msg.kernel = int(val)
            return jsonify(output=ttt)
        else:
            msg.value = result_txt
            #print('button value: {}'.format(result_txt))
            return jsonify(output=msg.mapping[msg.value])

@app.route('/video_feed')
def video_feed():
    """
    Video streaming route. Put this in the src attribute of an
    img tag.
    """
    txt = 'multipart/x-mixed-replace; boundary=frame'
    # WS added passing a message to the Camera class
    return Response(gen(Camera(message=msg)), mimetype=txt)


if __name__ == '__main__':
    # WS added debug for automatic reloading
    app.run(host='0.0.0.0', threaded=True, debug=True)
