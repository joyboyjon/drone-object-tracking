from dataclasses import dataclass


@dataclass
class Track:
    """Un obiect urmarit intr-un cadru."""
    track_id: int
    class_id: int
    confidence: float
    x1: int
    y1: int
    x2: int
    y2: int

    @property
    def area(self):
        return (self.x2 - self.x1) * (self.y2 - self.y1)

    @property
    def center(self):
        return ((self.x1 + self.x2) // 2, (self.y1 + self.y2) // 2)


def extract_tracks(result):
    """Transforma rezultatul YOLO intr-o lista de obiecte Track."""
    boxes = result.boxes
    if boxes.id is None:
        return []

    tracks = []
    for box, track_id, class_id, conf in zip(
        boxes.xyxy.tolist(),
        boxes.id.int().tolist(),
        boxes.cls.int().tolist(),
        boxes.conf.tolist(),
    ):
        x1, y1, x2, y2 = map(int, box)
        tracks.append(Track(track_id, class_id, conf, x1, y1, x2, y2))
    return tracks