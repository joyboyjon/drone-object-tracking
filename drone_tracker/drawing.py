import cv2

TARGET_COLOR = (0, 0, 255)      # rosu (OpenCV foloseste ordinea BGR)
OTHER_COLOR = (180, 180, 180)   # gri


def draw_tracks(frame, tracks, target):
    """Deseneaza toate obiectele urmarite si evidentiaza tinta."""
    for track in tracks:
        is_target = target is not None and track.track_id == target.track_id
        color = TARGET_COLOR if is_target else OTHER_COLOR
        thickness = 3 if is_target else 1

        cv2.rectangle(frame, (track.x1, track.y1), (track.x2, track.y2),
                      color, thickness)

        if is_target:
            label = f"TINTA id:{track.track_id}"
            cv2.putText(frame, label, (track.x1, track.y1 - 8),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
            cv2.circle(frame, track.center, 4, color, -1)