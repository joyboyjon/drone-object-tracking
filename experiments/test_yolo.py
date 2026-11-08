import cv2
import time
from ultralytics import YOLO
VIDEO_PATH = "videos/test1-Sinjuku-Tokyo.mp4"
MODEL_NAME = "yolo11n.pt"
IMG_SIZE = 1280

PERSON = 0
CAR = 2
MOTO = 3

model = YOLO(MODEL_NAME)
video=cv2.VideoCapture(VIDEO_PATH)

if not video.isOpened():
    print(f"Nu pot deschide videoclipul: {VIDEO_PATH}")
    exit()

cv2.namedWindow("Test Yolo", cv2.WINDOW_NORMAL)

frame_count = 0
total_persons = 0
total_cars = 0
start_time = time.time()
prev_time = start_time

while True:
    ok, frame=video.read()
    if not ok:
        break

    results=model(frame,imgsz=IMG_SIZE,verbose=False)
    annotated=results[0].plot()

    classes=results[0].boxes.cls.tolist()
    persons=classes.count(PERSON)
    cars = classes.count(CAR)

    frame_count+=1
    total_persons+=persons
    total_cars+=cars

    now=time.time()
    fps=1/(now-prev_time)
    prev_time=now

    cv2.putText(annotated,f"FPS:{ fps:.1f} | Persoane: {persons} | Masini: {cars}"
                ,(20,40),cv2.FONT_HERSHEY_SIMPLEX,1,(0,255,0),2)

    cv2.imshow("Test YOLO", annotated)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

total_time = time.time() - start_time
video.release()
cv2.destroyAllWindows()
#print(model.names)

print(f"Model: {MODEL_NAME}, imgsz: {IMG_SIZE}")
print(f"Cadre procesate: {frame_count}")
print(f"Medie persoane/cadru: {total_persons / frame_count:.1f}")
print(f"Medie masini/cadru: {total_cars / frame_count:.1f}")
print(f"FPS mediu: {frame_count / total_time:.1f}")