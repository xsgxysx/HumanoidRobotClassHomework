import sys
import os

import cv2
from ultralytics import YOLO

current_file = os.path.abspath(__file__)
project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_file)))
sys.path.insert(0, project_root)

from src.utils.video_stream import get_frame

if __name__ == "__main__":

    model = YOLO("yolo11n.pt")
    model.to("cuda")
    for frame in get_frame(ip="192.168.137.71", port=8888):
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
        results = model(frame, stream=True, conf=0.5)  # conf 设置置信度阈值
        for result in results:
            annotated_frame = result.plot()
            cv2.imshow("YOLO11 Detection", annotated_frame)