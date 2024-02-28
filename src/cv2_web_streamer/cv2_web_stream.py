import atexit
import subprocess
from ._assets import ffmpeg

class CV2WebStream:
    def __init__(self, mediamtx, stream_name, inherit_stdout=False, size=None, framerate=None):
        self.size = size
        self.framerate = framerate
        self.stream_name = stream_name
        self.mediamtx = mediamtx
        self.initialized = False
        self.inherit_stdout = inherit_stdout

    def start(self, frame=None):
        if self.initialized:
            return self

        if frame is not None:
            # Invert cv2 <rows>x<cols> to ffmpeg's <cols>x<rows>
            self.size = (frame.shape[1], frame.shape[0])
        elif self.size is None:
            raise Exception(
                "Could not determine size. Either call `start` with an"
                "explicit size or ensure the first frame passed has a shape."
            )

        ffmpeg_executable = ffmpeg.executable()

        self.ffmpeg = subprocess.Popen(
            [
                # https://groups.google.com/g/discuss-webrtc/c/3tLWL9yyjsA?pli=1
                # https://superuser.com/questions/564402/explanation-of-x264-tune
                ffmpeg_executable or "ffmpeg",
                "-f","rawvideo",
                "-framerate", "60",
                "-s", "{}x{}".format(*self.size),
                "-pix_fmt", "bgr24",
                # "-r", repr(60),
                "-i", "-",
                "-c:v", "libx264",
                "-tune", "zerolatency",
                "-preset","ultrafast",
                # Enabling sliced threads (on version ffmpeg 4.4.2 - outdated Ubuntu default)
                # causes non-gop frames to drop
                # "-x264-params", "sliced-threads=0",
                "-g", "60",
                "-bf", "0",
                "-f", "rtsp",
                f"rtsp://localhost:8554/{self.stream_name}",
            ],
            stdout=subprocess.STDOUT if self.inherit_stdout else subprocess.DEVNULL,
            stderr=subprocess.STDOUT if self.inherit_stdout else subprocess.DEVNULL,
            stdin=subprocess.PIPE,
        )

        atexit.register(self.cleanup)

        self.initialized = True

        return self

    def cleanup(self):
        self.ffmpeg.kill()

    def frame(self, f):
        """Write a frame to the web stream"""
        self.start(f)
        self.ffmpeg.stdin.write(f.tostring())