import cv2
import numpy as np
import paho.mqtt.client as mqtt

# MQTT broker configuration
broker = "localhost"
port = 1883
topic = "scan"

# OpenCV window name
window_name = "Motion detected"

# Image saving settings
save_path = "P:/MQTTPIC/"
counter = 0

# Callback function for MQTT message reception
def on_message(client, userdata, msg):
    global counter
    
    try:
        # Convert the received message payload to a NumPy array
        image_data = np.frombuffer(msg.payload, dtype=np.uint8)
        
        # Decode the image
        image = cv2.imdecode(image_data, cv2.IMREAD_COLOR)
        
        # Display the image in a window
        cv2.imshow(window_name, image)
        cv2.waitKey(1)
        
        # Save the image with a counter as the filename
        filename = f"scan_{counter}.jpg"
        cv2.imwrite(save_path + filename, image)
        
        # Increment the counter
        counter += 1     
        print(f"Image saved: {filename}")
            
    except Exception as e:
        print(f"Error saving image: {str(e)}")

# Create an MQTT client instance
client = mqtt.Client()

# Set the callback function for MQTT message reception
client.on_message = on_message

# Connect to the MQTT broker
client.connect(broker, port)

# Subscribe to the image topic
client.subscribe(topic)

# Create an OpenCV window
cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

# Main loop
while True:
    # Process incoming MQTT messages
    client.loop()

    # Break the loop if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Destroy the OpenCV window
cv2.destroyAllWindows()

