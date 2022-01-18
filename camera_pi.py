import io
import time
import picamera
from base_camera import BaseCamera


class Camera(BaseCamera):

    def __init__(self, message=None):

        # WS had to add this line for compatibility with camera_opencv Camera class
        Camera.message = message

    @staticmethod
    def frames():
        with picamera.PiCamera() as camera:
            # let camera warm up
            time.sleep(2)

            stream = io.BytesIO()
            for _ in camera.capture_continuous(stream, 'jpeg',
                                                 use_video_port=True):
                # return current frame
                stream.seek(0)
                yield stream.read()

                # reset stream for next frame
                stream.seek(0)
                stream.truncate()
