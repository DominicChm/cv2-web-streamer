# CV2-Web-Streamer

**NOTE: On the first run of your project, `cv2-web-streamer` needs to download binaries from Github, so make sure you're connected to the internet!**


Example: Streams your webcam to [localhost:8889/camera](http://localhost:8889/camera) and an inverted version to [localhost:8889/inverted](http://localhost:8889/inverted)
```py
from cv2_web_streamer import CV2WebStreamer
import cv2  

vid = cv2.VideoCapture(0) 

# Create a CV2 streamer
streamer = CV2WebStreamer()

# Create a stream (analagous to a cv2 imshow window) at <ip-address>:<port>/camera 
camera_stream = streamer.get_stream("camera")

# Create another at <ip-address>:<port>/inverted 
inverted_stream = streamer.get_stream("inverted")

while(True): 
      
    # Capture the video frame by frame 
    ret, frame = vid.read() 
    
    # Invert colors to make a second stream
    inverted_frame = cv2.bitwise_not(frame)
  
    # Display the resulting frame at localhost:8889/camera
    camera_stream.frame(frame) 

    # Display the resulting frame at localhost:8889/inverted
    inverted_stream.frame(inverted_frame) 
```

Multiple streams (as many as your computer can handle encoding) are supported. Streams will choose their size based on the first frame fed to them. They're accessible through the web at

# Caveats
Currently, cv2-web-streamer only supports `bgr` streams. Use `cv2.cvtColor` to convert anything streamed to cv2-web-streamer to `bgr` before passing it.
# Embedding
Embedding streams in other web apps is easy - use an iFrame. Otherwise,
see https://github.com/bluenviron/mediamtx/tree/main for additional strategies including the source code used to connect to the webrtc stream.