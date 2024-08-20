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
To overcome the issues, the a GUI based controller is implemented. Adapted from the pishot project, 
this controller employs a Flask-based web-framework to manage remote live video streams and remote control of photo taken from multiple Raspberry Pi cameras.
Each Raspberry Pi runs a Flask server that captures and streams video from its connected camera.
A master Flask server, hosted on a central device, aggregates these streams, providing a web-based GUI for real-time monitoring and adjustment of camera positions.  

<p align="center"> <img src="work flow.png">
