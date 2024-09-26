# Strawberry Imaging via Raspberry Pi Cameras
This project aims to use Raspberry Pi cameras to capture high-resolution images of strawberries positioned on a rotating platform. 
The primary objective is to use these images to create a detailed 3D model of a strawberry by applying the Structure from Motion (SfM) algorithm.

To achieve accurate and consistent results, the imaging process must be meticulously controlled. As the strawberry rotates, the cameras 
will capture images at regular intervals, ensuring a complete 360-degree view. It is crucial that these images are taken from multiple angles around the strawberry 
to capture all aspects of its shape and surface texture. The consistency of the imaging rate and the coverage of all angles are key factors in producing a reliable and precise 3D model.

# Challenge 
The project involves capturing images of over 100 strawberries. To optimize the process, multiple Raspberry Pi cameras are employed, 
each dedicated to capturing images of the strawberry from a specific angle every two seconds. 
This approach allows for the simultaneous capture of all necessary angles, significantly reducing the time required for the imaging process. The challenges are: 

- The coordination and control of multiple Raspberry Pi cameras to ensure they operate synchronously, maintaining the required 
two-second interval between captures. 
- Ensure each camera is properly aligned to capture the strawberry at an optimal angle, 
with accurate focus and appropriate exposure settings.

# Design Specification

<p align="center"> <img src="Work Overflow.png">
  
To overcome the issues, a GUI based controller is implemented. Inspired and adapted from the [Pishot](https://github.com/revalo/pishot) project, 
this controller employs a Flask-based web-framework server to manage hostname,  remote live video streams and remote control of photo taken from multiple Raspberry Pi cameras.
Each Raspberry Pi runs a Flask server that captures and streams video from its connected camera.
A master Flask server, hosted on a central device, aggregates these streams, providing a web-based GUI for real-time monitoring and adjustment of camera positions.  

Once the monitoring has done, you can use the master flask server to control the raspberry pi flask server to take images from the cameras. Once captured, these images will be saved locally and sent back to the central device.  Since the GUI also offers the directory typing, these images sent back from different pi board will be saved to the directory you typed, streamlining the process of managing and storing photos from the Raspberry Pi cameras.

<p align="center"> <img src="IMG_9504.jpg">

# Usage
## Setup
The project uses two Raspberry Pi Model 4B+ Board, each of which controlling one Raspberry Pi Camera Module 3 Wide. 
Ensure the cameras are properly connected to the boards and enabled. Test the camera via 
```php
sudo libcamera-jpeg -o test.jpg
```

## Instruction
To enable the GUI control:
- Download the ```piserver``` folder to the Pi. Configure each Pi to run the following script on boot-up:
  ```php
  python server.py --secret SECRET
  ```
  Replace ```SECRET``` with a long unrecognizable string. Make sure this secret is consistent across all PI's and make sure we write it down.
   For instructions on how to execute a script automatically upon system boot, please refer to the provided guide https://www.instructables.com/Raspberry-Pi-Launch-Python-script-on-startup/
- Download the ```master``` server to your computer/laptop that you would like to host the GUI controller. Make sure your computer / laptop is on the same network as all the Pi devices you wish to remote control. To launch the GUI use the command:
  ```php
  python master.py --secret SECRET
  ```
  Note that the ```SECRET``` here must be the same secret that you used with all the Pi's.

The support folder contains the stl files of the joiner and the base for holding the camera. It provides two degress of freedom so that the camera angles of imaging can be adjusted accordingly.
