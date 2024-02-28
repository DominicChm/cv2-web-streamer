from cv2_web_streamer import CV2WebStreamer
import cv2  

vid = cv2.VideoCapture(0) 

# Create a CV2 streamer
streamer = CV2WebStreamer(inherit_stdout=True)

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