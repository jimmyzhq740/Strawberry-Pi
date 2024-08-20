import socket
import os 
import requests
import dweepy
import time
import random
import threading
import argparse
import cv2

from datetime import datetime
from picamera2 import  Picamera2
from libcamera import  controls
from flask import Flask, jsonify, Response, send_file, request
from uuid import getnode as get_mac
from utils import is_raspberry_pi, get_thing
#from camera import gen_video, set_lensposition_state, capture_and_send_image,set_exposure_state

lensposition=5
#in microseconds
exposuretime=10000
picam2=None

app = Flask(__name__)
def get_camera():
    global picam2
    if picam2 is None: 
        picam2 = Picamera2()
    return picam2

def release_camera():
    global picam2
    if picam2 is not None:
        picam2.stop()
        picam2.close()
        picam2=None



def gen_video():
    """Video streaming generator function."""
    global lensposition
    global exposuretime
    picam2 = get_camera()
    print('hi')
    capture_config=picam2.create_still_configuration({'format':'RGB888', 'size':(600,800)})
    picam2.configure(capture_config)
    picam2.start()
    
    #vs = cv2.VideoCapture(0)
    while True:
        picam2.set_controls({"ExposureTime":exposuretime})
        # Set manual focus
        picam2.set_controls({"AfMode": controls.AfModeEnum.Manual,"LensPosition":lensposition})
        frame = picam2.capture_array()
        #print (lensposition)
        #ret,frame=vs.read()
        ret, jpeg = cv2.imencode('.jpg', frame)
        frame=jpeg.tobytes()
        yield (b'--frame\r\n'
        b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

def capture_and_send_image(counter):
    global lensposition
    global exposuretime
    picam2 = get_camera()
    capture_config=picam2.create_still_configuration({'format':'RGB888', 'size':(3072,4096)})
    picam2.configure(capture_config)
    picam2.start()
    picam2.set_controls({"ExposureTime":exposuretime})
    image_directory= '/home/jimmyzhang/Desktop/piserver/images'
    if not os.path.exists(image_directory):
        os.makedirs(image_directory)
    image_paths=[]
    for i in range (counter):
        time.sleep(2)
        current_time=datetime.now().strftime("%Y%m%d_%H%M%S")
        image_path = f'{image_directory}/image_{current_time}.jpg'
        picam2.set_controls({"AfMode": controls.AfModeEnum.Manual,"LensPosition":lensposition})
        picam2.capture_file(image_path)
        image_paths.append(image_path)
    release_camera()
    return image_paths

def set_lensposition_state (state):
    global lensposition
    if state == 'increase':
        lensposition += 1
        print (lensposition)
        return lensposition
    elif state == 'decrease':
        lensposition -=1
        print (lensposition)
        return lensposition

def set_exposure_state(state):
    global exposuretime
    if state == 'increase':
        exposuretime += 1000
        print (exposuretime)
        return exposuretime
    elif state == 'decrease':
        exposuretime -= 1000
        print (exposuretime)
        return exposuretime

def get_ip():
    """
    Get the external IP address as a string
    """
    try:
        #socket.gethostname() retrieves the hostname of the machine, in this case, return raspberrypi  
        ip_list = socket.gethostbyname_ex(socket.gethostname())[2]

        #filter out localhost address
        ip = next ((ip for ip in ip_list if not ip.startswith("127.")), None)

        if ip:
            return ip
    except socket.gaierror:
        pass

    # if the above method fails, use an alternative approach 
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8",53))
            return s.getsockname()[0]
    except Exception:
        return "no IP found"

def getserial():
    # Extract serial from cpuinfo file
    cpuserial = "0000000000000000"
    try:
        f = open('/proc/cpuinfo', 'r')
        for line in f:
            if line[0:6] == 'Serial':
                cpuserial = line[10:26]
        f.close()
    except:
        cpuserial = "ERROR000000000"
    return cpuserial

def get_hw_id():
    """
    Retrieve a unique hardware identifier for the machine it's running.
    The identifier could be a MAC address for non-raspberry pi 
    Or a UUID for raspberry pi device
    """
    if not is_raspberry_pi():
        return str(hex(get_mac()))
    
    if os.path.exists('/home/pi/serial.txt'):
        with open('/home/pi/serial.txt', 'r') as f:
            return f.read().strip()
    
    r = requests.get("https://www.uuidgenerator.net/api/version4")
    uid = str(r.content)

    with open('/home/pi/serial.txt', 'w') as f:
        f.write(uid)

    return uid.strip()

last_ip = "ha"

def ip_update_loop(secret, verbose):
    """
    Periodically check and update the local IP address and the master server IP. 
    It uses a service called dweepy to get the master server's IP and then
    continuously checks the local IP address, updating the master server 
    if the local Ip address changes

    """
    global last_ip

    #The secret is turned into SHA-1 hash in hex format
    secret = get_thing(secret)

    master_ip = ""

    #The first while loop gets the IP address of the master server
    while True:
        print("Getting mastcapture_and_send_imageer")
        try:
            d = dweepy.get_latest_dweet_for(secret)
            print(d)
            master_ip = d[0]['content']['master_ip']
            break
        except Exception as e:
            print(e)

        time.sleep(random.randint(4, 30))

    print("Master IP", master_ip)

    print (get_ip())
    # this while runs infinitly, and update the local ip address via last_ip= get_ip()
    while True:
        if (last_ip != get_ip()):
            try:
                requests.get("http://%s:5555/ip/%s" % (master_ip, get_ip()))
                last_ip = get_ip()
            except:
                last_ip = "ha"
        time.sleep(3)

@app.route('/ping')
def ping():
    """
    Endpoint to receive the uuid of a raspberry pi
    """
    return jsonify({"uuid": get_hw_id()})

@app.route('/reboot')
def reboot():
    """
    Endpoint to reboot
    """
    os.system('sudo reboot')
    return jsonify({"ok": "ok"})

#http://127.0.0.1:5000/reboot

@app.route('/increaselens')
def increase_lens():
    result = set_lensposition_state ('increase')
    return jsonify(result)     

@app.route('/decreaselens')
def decrease_lens():
    result = set_lensposition_state ('decrease')
    return jsonify(result)   

@app.route('/increaseexposuretime')
def increase_exposuretime():
    result = set_exposure_state ('increase')
    return jsonify(result)     

@app.route('/decreaseexposuretime')
def decrease_exposuretime():
    result = set_exposure_state ('decrease')
    return jsonify(result)

@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen_video(),mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/start_capture')
def start_capture():
    image_paths = capture_and_send_image(10)
    image_urls = [f"http://{request.host}/images/{os.path.basename(path)}" for path in image_paths]
    return jsonify({"images":image_urls}),200

@app.route('/images/<filename>')
def get_image(filename):
    image_path = os.path.join('/home/jimmyzhang/Desktop/piserver/images', filename)
    return send_file(image_path, mimetype='image/jpeg')

@app.route('/stopcamera')
def stop_camera_endpoint():
    release_camera()
    return jsonify({'message':'Camera stopped'})
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="PiShot slave server.")

    parser.add_argument(
        "--secret",
        help="A long unique string that's consistent across all Pi's",
        action="store",
        dest="secret",
        type=str,
        required=True,
    )

    parser.add_argument(
        "--verbose",
        help="Print out verbose messages.",
        action="store_true",
        dest="verbose",
    )

    args = parser.parse_args()

    #threading used to run the system 
    ip_thread = threading.Thread(
        target=ip_update_loop,
        args=(args.secret, args.verbose,)
    )

    ip_thread.daemon = True
    ip_thread.start()

    app.run(host="0.0.0.0", port=5000)

print (get_ip())
print (getserial())
print (get_hw_id())
print (socket.gethostname())
print (socket.gethostbyname_ex(socket.gethostname()))