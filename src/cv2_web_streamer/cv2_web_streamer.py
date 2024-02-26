import subprocess
import time
import atexit

from subprocess import Popen
from ._assets import ensure_assets_installed, mediamtx
from .cv2_web_stream import CV2WebStream

class CV2WebStreamer:
    def __init__(self, logger=None):
        self.initialized = False
        self.logger = logger

        self.PATH_CONFIG = mediamtx.PATH_INSTALL_DIR / "mediamtx.yml"
        self.streams = []

    def _generate_config(self):
        """Generates a YAML config describing all currently active streams"""
        with open(self.PATH_CONFIG, "w") as cfg:
            entries = [
                "paths:\n",
                *[f"    {stream.stream_name}:\n" for stream in self.streams],
            ]
            cfg.writelines(entries)

    def start(self):
        if self.initialized:
            return
        
        ensure_assets_installed()

        # Initialize mediamtx config
        self._generate_config()

        self.process = Popen(
            [mediamtx.executable(), self.PATH_CONFIG],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            stdin=subprocess.PIPE,
        )
        
        atexit.register(self.cleanup)

        # TODO: monitor stdout for when mtx is ready for connections
        time.sleep(1)

        self.initialized = True

    def cleanup(self):
        self.process.kill()

    def get_stream(self, stream_name, size=None, framerate=None):
        self.start()

        stream = CV2WebStream(self, stream_name, size, framerate)
        self.streams.append(stream)
        self._generate_config()
        return stream


if __name__ == "__main__":

    m = CV2WebStreamer()
    m.start()

    s = m.get_stream("test").start()

    time.sleep(100000)
