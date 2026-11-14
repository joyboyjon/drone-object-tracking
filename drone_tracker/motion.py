import math
from collections import deque

# Unghiul 0 = spre dreapta; axa y creste in jos, deci 90 = spre jos
DIRECTIONS = ["dreapta", "dreapta-jos", "jos", "stanga-jos",
              "stanga", "stanga-sus", "sus", "dreapta-sus"]


class MotionAnalyzer:
    """Calculeaza viteza, directia si traseul tintei."""

    def __init__(self, fps, history_size=90, speed_window=10, min_speed=5):
        self.fps = fps                      # cadre pe secunda ale clipului
        self.speed_window = speed_window    # din cate pozitii calculam viteza
        self.min_speed = min_speed          # sub aceasta viteza, tinta sta pe loc
        self.history_size = history_size
        self.histories = {}
        self.target_id = None

    def update(self, tracks, target, frame_index):
        """Inregistreaza pozitiile tuturor obiectelor alese vreodata ca tinta."""
        # 1. O tinta aleasa pentru prima data primeste un istoric nou
        if target is not None:
            self.target_id = target.track_id
            if target.track_id not in self.histories:
                self.histories[target.track_id] = deque(maxlen=self.history_size)

        # 2. Adaugam pozitia fiecarui obiect care are istoric,
        #    chiar daca acum nu este tinta curenta
        for track in tracks:
            history = self.histories.get(track.track_id)
            if history is not None:
                history.append((frame_index, track.center))

    def velocity(self):
        """Returneaza viteza (vx, vy) in pixeli pe secunda, sau None."""
        history = self.histories.get(self.target_id)
        if history is None or len(history) < 2:
            return None
        recent = list(history)[-self.speed_window:]
        f1, (x1, y1) = recent[0]
        f2, (x2, y2) = recent[-1]
        seconds = (f2 - f1) / self.fps
        if seconds <= 0:
            return None
        return (x2 - x1) / seconds, (y2 - y1) / seconds

    def describe(self):
        """Text scurt cu viteza si directia, pentru afisare."""
        v = self.velocity()
        if v is None:
            return "viteza: necunoscuta"
        vx, vy = v
        speed = math.hypot(vx, vy)
        if speed < self.min_speed:
            return f"viteza: {speed:.0f} px/s (pe loc)"
        angle = math.degrees(math.atan2(vy, vx)) % 360
        direction = DIRECTIONS[round(angle / 45) % 8]
        return f"viteza: {speed:.0f} px/s spre {direction}"

    def trajectory(self):
        """Lista pozitiilor tintei, de la cea mai veche la cea mai noua."""
        history = self.histories.get(self.target_id, [])
        return [point for _, point in history]