import time

import cv2
from ultralytics import YOLO

from drone_tracker.video_source import VideoSource

VIDEO_PATH = "videos/test1-Sinjuku-Tokyo.mp4"
MODEL_NAME = "yolo11n.pt"
IMG_SIZE = 1280
TRACKED_CLASSES = [0,2] #0=pers 2 = car
TRACKER_CONFIG = "config/bytetrack_custom.yaml"

model = YOLO(MODEL_NAME)
source = VideoSource(VIDEO_PATH)
print(f"Sursa: {source.width}x{source.height}, {source.fps:.0f} FPS")

cv2.namedWindow("Drone tracker", cv2.WINDOW_NORMAL)

prev_time = time.time()
seen_ids = set()

while True:
    frame = source.read()
    if frame is None:
        break

    results = model.track(
        frame,
        imgsz=IMG_SIZE,
        classes=TRACKED_CLASSES,
        persist=True,
        tracker=TRACKER_CONFIG,
        verbose=False,
    )
    result=results[0]
    annotated=result.plot()

    ids = result.boxes.id
    num_tracked = 0 if ids is None else len(ids)
    if ids is not None:
        seen_ids.update(ids.int().tolist())

    now = time.time()
    fps = 1 / (now - prev_time)
    prev_time = now

    text = f"FPS: {fps:.1f} | Obiecte urmarite: {num_tracked}"
    cv2.putText(annotated, text, (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    cv2.imshow("Drone tracker", annotated)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

source.release()
cv2.destroyAllWindows()
print(f"ID-uri distincte afisate: {len(seen_ids)}")
print(f"ID maxim: {max(seen_ids) if seen_ids else 0}")