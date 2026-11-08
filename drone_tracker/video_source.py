import cv2

class VideoSource:
    """Citeste cadre dintr-un fisier video sau de la o camera."""

    def __init__(self,source):
        # cale catre fisier sau camera calculatorului(0)

        self.capture=cv2.VideoCapture(source)
        if not self.capture.isOpened():
            raise RuntimeError(f"Nu pot deschide sursa video: {source}")

        self.fps=self.capture.get(cv2.CAP_PROP_FPS)
        self.width=(int)(self.capture.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height=int(self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT))

    def read(self):
        ok, frame = self.capture.read()
        if not ok:
            return None
        return frame

    def release(self):
        self.capture.release()