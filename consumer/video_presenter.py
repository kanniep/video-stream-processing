import logging
import random
import time

import cv2
import numpy as np


def plot_one_box(x, img, color=None, label=None, line_thickness=None):
    # Plots one bounding box on image img
    tl = line_thickness or round(
        0.002 * (img.shape[0] + img.shape[1]) / 2) + 1  # line/font thickness
    color = color or [random.randint(0, 255) for _ in range(3)]
    c1, c2 = (int(x[0]), int(x[1])), (int(x[2]), int(x[3]))
    cv2.rectangle(img, c1, c2, color, thickness=tl, lineType=cv2.LINE_AA)
    if label:
        tf = max(tl - 1, 1)  # font thickness
        t_size = cv2.getTextSize(label, 0, fontScale=tl / 3, thickness=tf)[0]
        c2 = c1[0] + t_size[0], c1[1] - t_size[1] - 3
        cv2.rectangle(img, c1, c2, color, -1, cv2.LINE_AA)  # filled
        cv2.putText(img, label, (c1[0], c1[1] - 2), 0, tl / 3,
                    [225, 255, 255], thickness=tf, lineType=cv2.LINE_AA)


class VideoPresenter:
    def __init__(self):
        self.last_show_time = time.time()
        self.fps = 0
        self.delay = 0

    def image_derializer(self, image_bytes):
        return cv2.imdecode(np.frombuffer(
            image_bytes, dtype=np.uint8), cv2.IMREAD_UNCHANGED)

    def show(self, message):
        frame = self.image_derializer(message.image_info.image)
        detections = message.detections
        for i, detection in enumerate(detections):
            if detection.confidence >= 0.5:
                label = f'{detection.category} {detection.confidence:.2f}'
                plot_one_box([detection.x1, detection.y1, detection.x2,
                              detection.y2], frame, label=label, line_thickness=2)
        cv2.putText(frame, "FPS: {} with {} secs delay".format(self.fps, self.delay),
                    (0, 20),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0, 255, 0),
                    2)
        cv2.imshow('Stream', frame)
        show_time = time.time() - self.last_show_time
        self.last_show_time = time.time()
        self.fps = int(1 / show_time)
        self.delay = time.time() - message.timestamp()[1] / 1000
        if cv2.waitKey(1) & 0xFF == ord('q'):
            cv2.destroyAllWindows()
