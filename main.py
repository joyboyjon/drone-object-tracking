import threading
import time

import cv2
from ultralytics import YOLO

from drone_tracker.video_source import VideoSource
from drone_tracker.tracks import extract_tracks
from drone_tracker.target_selector import TargetSelector
from drone_tracker.drawing import draw_tracks, draw_motion
from drone_tracker.motion import MotionAnalyzer
from drone_tracker.web_server import SharedState, create_app

VIDEO_PATH = "videos/test1-Sinjuku-Tokyo.mp4"
MODEL_NAME = "yolo11n.pt"
IMG_SIZE = 1280
TRACKED_CLASSES = [0, 2]  # 0 = persoana, 2 = masina
TRACKER_CONFIG = "config/bytetrack_custom.yaml"

TARGET_CLASS = 0
SIZE_RULE = "largest"
MAX_LOST_FRAMES = 60

def run_tracking(state):
    """Ruleaza teste unul dupa altul, la comenzile din pagina web."""
    while True:
        state.playing.wait()      # asteptam butonul Start sau Reia testul
        state.take_restart()      # stergem o eventuala cerere veche de reluare
        finished = run_test(state)
        if finished:
            state.add_event("Clip terminat. Apasa 'Reia testul' pentru o noua rulare.")
            state.playing.clear()


def run_test(state):
    """O rulare completa a clipului.
    Returneaza True daca clipul s-a terminat, False daca a fost intrerupt."""
    # Obiecte noi la fiecare test: clipul porneste de la inceput,
    # iar trackerul, tinta si traseele sunt resetate
    model = YOLO(MODEL_NAME)
    source = VideoSource(VIDEO_PATH)
    selector = TargetSelector(TARGET_CLASS, SIZE_RULE, MAX_LOST_FRAMES)
    motion = MotionAnalyzer(source.fps, history_size=None, speed_window=20)
    state.add_event(f"--- Test nou | sursa: {source.width}x{source.height}, "
                    f"{source.fps:.0f} FPS ---")

    prev_time = time.time()

    prev_time = time.time()
    frame_index = 0           # numarul cadrului curent
    last_target_id = None     # tinta din cadrul anterior
    last_lost_frames = 0      # de cate cadre lipsea tinta in cadrul anterior
    frames_with_target = 0    # in cate cadre tinta a fost vizibila
    targets_chosen = 0        # cate tinte au fost alese in total
    last_confidence = 0.0     # increderea tintei in ultimul cadru in care a fost vazuta

    while True:
        state.playing.wait()      # pe pauza, bucla asteapta aici
        if state.take_restart():
            source.release()
            state.add_event(f"[cadru {frame_index}] Test intrerupt pentru reluare")
            return False

        frame = source.read()
        if frame is None:
            break
        frame_index += 1

        results = model.track(
            frame,
            imgsz=IMG_SIZE,
            classes=TRACKED_CLASSES,
            persist=True,
            tracker=TRACKER_CONFIG,
            verbose=False,
        )
        tracks = extract_tracks(results[0])

        # Alegere manuala: click primit din pagina web
        point = state.pop_click()
        if point is not None:
            x, y = point
            chosen = selector.select_at(x, y, tracks)
            if chosen is not None:
                state.add_event(f"[cadru {frame_index}] Click la ({x}, {y}): "
                                f"tinta aleasa manual id {chosen.track_id}")
            else:
                state.add_event(f"[cadru {frame_index}] Click la ({x}, {y}): "
                                f"niciun obiect in apropiere")

        target = selector.update(tracks)
        motion.update(tracks, target, frame_index)

        # 1. Tinta veche a fost abandonata (a lipsit prea mult)
        if last_target_id is not None and selector.target_id != last_target_id:
            state.add_event(f"[cadru {frame_index}] Tinta id {last_target_id} abandonata")
            last_target_id = None

        # 2. Tinta este vizibila: este noua sau a fost regasita
        if target is not None:
            frames_with_target += 1
            if target.track_id != last_target_id:
                targets_chosen += 1
                state.add_event(f"[cadru {frame_index}] Tinta noua: id {target.track_id} | "
                                f"arie {target.area} px | centru {target.center} | "
                                f"incredere {target.confidence:.2f}")
            elif last_lost_frames > 0:
                state.add_event(f"[cadru {frame_index}] Tinta id {target.track_id} "
                                f"regasita dupa {last_lost_frames} cadre | "
                                f"incredere {target.confidence:.2f}")
            last_target_id = target.track_id
            last_confidence = target.confidence

        # 3. Tinta tocmai a disparut in acest cadru
        elif selector.target_id is not None and selector.lost_frames == 1:
            state.add_event(f"[cadru {frame_index}] Tinta id {selector.target_id} pierduta | "
                            f"ultima incredere {last_confidence:.2f}")

        last_lost_frames = selector.lost_frames

        annotated = frame.copy()
        draw_tracks(annotated, tracks, target)
        if target is not None:
            draw_motion(annotated, motion.trajectory(), target.center,
                        motion.velocity())

        now = time.time()
        fps = 1 / (now - prev_time)
        prev_time = now

        if target is not None:
            status = f"Tinta: id {target.track_id}"
        elif selector.target_id is not None:
            status = f"Tinta pierduta ({selector.lost_frames} cadre)"
        else:
            status = "Caut tinta..."

        state.set_frame(annotated)
        state.set_status({
            "fps": round(fps, 1),
            "objects": len(tracks),
            "frame": frame_index,
            "target": status,
            "motion": motion.describe() if target is not None else "",
        })

    source.release()
    state.add_event("--- Rezumat ---")
    state.add_event(f"Cadre procesate: {frame_index}")
    state.add_event(f"Tinte alese: {targets_chosen}")
    if frame_index > 0:
        percent = 100 * frames_with_target / frame_index
        state.add_event(f"Cadre cu tinta vizibila: {frames_with_target} ({percent:.0f}%)")
    return True


if __name__ == "__main__":
    state = SharedState()
    worker = threading.Thread(target=run_tracking, args=(state,), daemon=True)
    worker.start()

    app = create_app(state)
    print("Deschide in browser: http://127.0.0.1:5000")
    app.run(host="127.0.0.1", port=5000, threaded=True)