import cv2
import numpy as np
import paho.mqtt.client as mqtt

# MQTT broker details
broker_address = "192.168.1.107"
broker_port = 1883
topic = "scan"

# Webcam properties
width = 320
height = 240

# Motion detection parameters
threshold = 2000  # Adjust this value based on the sensitivity of motion detection

# Initialize the webcam
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

# Initialize the MQTT client
client = mqtt.Client()

# Function to publish the image via MQTT
def publish_image(image):
    _, img_encoded = cv2.imencode(".jpg", image)
    client.publish(topic, img_encoded.tobytes())

# Function to handle MQTT message received
def on_message(client, userdata, msg):
    pass  # Add your logic here for handling incoming MQTT messages

# Connect to the MQTT broker and subscribe to the topic
client.connect(broker_address, broker_port)
client.subscribe(topic)

# Set the MQTT message callback
client.on_message = on_message

# Start the MQTT loop in a separate thread
client.loop_start()

# Initialize variables for motion detection
previous_frame = None
motion_detected = False
reset_background=0
count=0

# Main loop
while True:
    # Read the current frame from the webcam
    ret, frame = cap.read()

    # Convert the frame to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Apply Gaussian blur to reduce noise
    blur_size = (21, 21)
    blurred = cv2.GaussianBlur(gray, blur_size, 1)

    # If this is the first frame, save it for later comparison
    reset_background+=1 
    if previous_frame is None:
        previous_frame = blurred
        continue
    
    # reset backgroud frame
    if reset_background >= 20:
        previous_frame = blurred
        reset_background = 0
        count = 0
        continue
    
    #print(count)

    # Compute the absolute difference between the current frame and the previous frame
    frame_diff = cv2.absdiff(previous_frame, gray)

    # Apply thresholding to detect significant differences
    _, thresh = cv2.threshold(frame_diff, 21, 255, cv2.THRESH_BINARY)

    # Perform dilation to fill in the gaps
    thresh = cv2.dilate(thresh, None, iterations=1)

    # Find contours of moving objects
    contours, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Initialize a flag to check if there is motion detection
    motion_detected = False

    # Iterate through the contours
    for contour in contours:
        # If the contour area is larger than the threshold, consider it as a moving object
        if cv2.contourArea(contour) > threshold:
            x, y, w, h = cv2.boundingRect(contour)
            #cv2.rectangle(frame, (x, y), (x + w, y + h), (10, 10, 255), 2)
            motion_detected = True

    # Publish the frame as an image via MQTT if there is motion detection
    if motion_detected:
        count+=1
        publish_image(frame)
        print("Motion detected : " + str(count))
        
    # Show the video preview
    cv2.imshow("Scanning", frame_diff)

    # Check for key press to exit the loop
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the webcam and destroy all windows
cap