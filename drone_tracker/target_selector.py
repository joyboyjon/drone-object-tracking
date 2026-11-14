import math

class TargetSelector:
    """Alege automat tinta dupa tip si marime si o pastreaza intre cadre."""

    def __init__(self, target_class, size_rule="largest", max_lost_frames=60):
        self.target_class = target_class
        self.size_rule = size_rule
        self.max_lost_frames = max_lost_frames
        self.target_id = None
        self.lost_frames = 0

    def update(self, tracks):
        """Primeste obiectele din cadrul curent si returneaza tinta (sau None)."""
        # 1. Daca avem deja o tinta, o cautam in cadrul curent
        if self.target_id is not None:
            for track in tracks:
                if track.track_id == self.target_id:
                    self.lost_frames = 0
                    return track

            # Tinta nu este in cadru: asteptam putin, poate reapare
            self.lost_frames += 1
            if self.lost_frames <= self.max_lost_frames:
                return None

            # A lipsit prea mult: renuntam la ea
            self.target_id = None
            self.lost_frames = 0

        # 2. Nu avem tinta: alegem una noua
        candidates = [t for t in tracks if t.class_id == self.target_class]
        if not candidates:
            return None

        if self.size_rule == "largest":
            target = max(candidates, key=lambda t: t.area)
        else:
            target = min(candidates, key=lambda t: t.area)

        self.target_id = target.track_id
        return target

    def select_at(self, x, y ,tracks, max_distance=50):
        """Alege ca tinta obiectul aflat la pozitia (x,y), unde s-a dat click."""
        # 1. Obiectele al caror chenar contine punctul
        inside = [t for t in tracks
                  if t.x1 <= x <= t.x2 and t.y1 <= y <= t.y2]
        if inside:
            chosen = min(inside, key=lambda t: t.area)
        else:
            # 2. Altfel, obiectul cu centrul cel mai apropiat de punct
            def distance(t):
                cx, cy = t.center
                return math.hypot(cx - x, cy - y)

            chosen = min(tracks, key=distance, default=None)
            if chosen is None or distance(chosen) > max_distance:
                return None

        self.target_id = chosen.track_id
        self.lost_frames = 0
        return chosen