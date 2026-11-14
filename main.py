import time

import cv2
from ultralytics import YOLO

from drone_tracker.video_source import VideoSource
from drone_tracker.tracks import extract_tracks
from drone_tracker.target_selector import TargetSelector
from drone_tracker.drawing import draw_tracks

VIDEO_PATH = "videos/test1-Sinjuku-Tokyo.mp4"
MODEL_NAME = "yolo11n.pt"
IMG_SIZE = 1280
TRACKED_CLASSES = [0,2] #0=pers 2 = car
TRACKER_CONFIG = "config/bytetrack_custom.yaml"

TARGET_CLASS=0
SIZE_RULE="largest"
MAX_LOST_FRAMES=60

model = YOLO(MODEL_NAME)
source = VideoSource(VIDEO_PATH)
selector= TargetSelector(TARGET_CLASS,SIZE_RULE,MAX_LOST_FRAMES)
print(f"Sursa: {source.width}x{source.height}, {source.fps:.0f} FPS")
print("Click stanga pe un obiect pentru a-l alege ca tinta. Tasta q = iesire.")

click = {"point": None}  

def on_mouse(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        click["point"] = (x, y)

cv2.namedWindow("Drone tracker", cv2.WINDOW_NORMAL)
cv2.resizeWindow("Drone tracker", 960,455)
cv2.setMouseCallback("Drone tracker", on_mouse)

prev_time = time.time()
frame_index = 0           # numarul cadrului curent
last_target_id = None     # tinta din cadrul anterior
last_lost_frames = 0      # de cate cadre lipsea tinta in cadrul anterior
frames_with_target = 0    # in cate cadre tinta a fost vizibila
targets_chosen = 0        # cate tinte au fost alese in total
last_confidence = 0.0     # increderea tintei in ultimul cadru in care a fost vazuta


while True:
    frame = source.read()
    if frame is None:
        break
    frame_index+=1

    results = model.track(
        frame,
        imgsz=IMG_SIZE,
        classes=TRACKED_CLASSES,
        persist=True,
        tracker=TRACKER_CONFIG,
        verbose=False,
    )
    tracks=extract_tracks(results[0])
    # Alegere manuala: daca s-a dat click, alegem obiectul de acolo
    if click["point"] is not None:
        x, y = click["point"]
        click["point"] = None
        chosen = selector.select_at(x, y, tracks)
        if chosen is not None:
            print(f"[cadru {frame_index}] Click la ({x}, {y}): "
                  f"tinta aleasa manual id {chosen.track_id}")
        else:
            print(f"[cadru {frame_index}] Click la ({x}, {y}): "
                  f"niciun obiect in apropiere")
    target=selector.update(tracks)
    # 1. Tinta veche a fost abandonata (a lipsit prea mult)
    if last_target_id is not None and selector.target_id != last_target_id:
        print(f"[cadru {frame_index}] Tinta id {last_target_id} abandonata")
        last_target_id = None

    # 2. Tinta este vizibila: este noua sau a fost regasita
    if target is not None:
        frames_with_target += 1
        if target.track_id != last_target_id:
            targets_chosen += 1
            print(f"[cadru {frame_index}] Tinta noua: id {target.track_id} | "
                  f"arie {target.area} px | centru {target.center} | "
                  f"incredere {target.confidence:.2f}")
        elif last_lost_frames > 0:
            print(f"[cadru {frame_index}] Tinta id {target.track_id} "
                  f"regasita dupa {last_lost_frames} cadre | "
                  f"incredere {target.confidence:.2f}")
        last_target_id = target.track_id
        last_confidence = target.confidence

    # 3. Tinta tocmai a disparut in acest cadru
    elif selector.target_id is not None and selector.lost_frames == 1:
        print(f"[cadru {frame_index}] Tinta id {selector.target_id} pierduta | "
              f"ultima incredere {last_confidence:.2f}")

    last_lost_frames = selector.lost_frames

    annotated=frame.copy()
    draw_tracks(annotated, tracks, target)

    now = time.time()
    fps = 1 / (now - prev_time)
    prev_time = now

    if target is not None:
        status=f"Tinta: id {target.track_id}"
    elif selector.target_id is not None:
        status=f"Tinta pierduta ({selector.lost_frames} cadre)"
    else:
        status="Cauta tinta..."
    
    text=f"FPS: {fps:.1f}| Obiecte: {len(tracks)}|{status}"
    cv2.putText(annotated,text,(20,40),
    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    if target is not None:
        info = (f"Cadru {frame_index} | centru {target.center} | "
                f"arie {target.area} px | incredere {target.confidence:.2f}")
    else:
        info = f"Cadru {frame_index}"
    cv2.putText(annotated, info, (20, 80),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
    cv2.imshow("Drone tracker", annotated)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

source.release()
cv2.destroyAllWindows()
print("\n--- Rezumat ---")
print(f"Cadre procesate: {frame_index}")
print(f"Tinte alese: {targets_chosen}")
if frame_index > 0:
    percent = 100 * frames_with_target / frame_index
    print(f"Cadre cu tinta vizibila: {frames_with_target} ({percent:.0f}%)")