import cv2
import time
from collections import deque
from common.proto_models import image_pb2
from threading import Thread


class VideoReader:
    def __init__(self, device_id=0, frame_size=(1024, 768), frame_rate=20.0, buffer_size=10, enable_camera_reader_thread=False):
        self.frame_size = frame_size
        self.frame_rate = frame_rate
        self.buffer_size = buffer_size
        self.device = device_id
        self.enable_camera_reader_thread = enable_camera_reader_thread

        self.cap = None
        self.online = False

        if enable_camera_reader_thread:
            self.deque = deque(maxlen=1)
            self.thread = Thread(target=self.get_frame, args=())
            self.thread.daemon = True
            self.thread.start()

            while (True):
                if not self.online:
                    print('Waiting for camera to ready...')
                    time.sleep(2)
                else:
                    break
        else:
            self.init_camera()

    def init_camera(self):
        self.cap = cv2.VideoCapture(self.device)
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, self.buffer_size)
        self.cap.set(cv2.CAP_PROP_FOURCC,
                     cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.frame_size[0])
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.frame_size[1])
        self.cap.set(cv2.CAP_PROP_FPS, self.frame_rate)
        camera_details = "Capturing camera {} at {}x{}, {}p and buffer size of {}".format(self.device, self.cap.get(
            cv2.CAP_PROP_FRAME_WIDTH), self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT), self.cap.get(cv2.CAP_PROP_FPS), self.cap.get(cv2.CAP_PROP_BUFFERSIZE))
        print(camera_details)
        self.online = True

    def verify_network_stream(self, link):
        """Attempts to receive a frame from given link"""

        cap = cv2.VideoCapture(link)
        if not cap.isOpened():
            print('CAMERA is already opened')
            return False
        cap.release()
        return True

    def load_network_stream(self):
        """Verifies stream link and open new stream if valid"""

        if self.verify_network_stream(self.device):
            self.init_camera()
        else:
            print('Cannot connect to camera in the init thread')

    def serialize(self, image, _):
        _, im_buf_arr = cv2.imencode(".jpg", image)
        bytes_image = im_buf_arr.tobytes()
        return image_pb2.ImageInfo(
            width=self.frame_size[0], height=self.frame_size[1], image=bytes_image).SerializeToString()

    def get_frame(self):
        """Reads frame, serializes to proto and puts in queue"""

        self.load_network_stream()

        while True:
            try:
                if self.online:
                    # Read next frame from stream and insert into deque
                    status, frame = self.cap.read()
                    if status:
                        self.deque.appendleft(frame)
                    else:
                        self.cap.release()
                        self.online = False
                        print('Cannot read from Camera')
                else:
                    # Attempt to reconnect
                    print('attempting to reconnect', self.device)
                    time.sleep(2)
                # time.sleep(0.02)
            except AttributeError:
                pass

    def read(self):
        """Get serialized image from the queue"""

        # if self.deque and self.online:
        if self.online:
            # Grab latest frame
            if self.enable_camera_reader_thread:
                frame = self.deque[-1]
            else:
                _, frame = self.cap.read()
            return frame
        else:
            print('Waiting for camera for 2 more secs')
            time.sleep(2)
            return None

    def release(self):
        self.cap.release()
