https://github.com/Karpova-Lab/treadmill-control
# Split-belt Treadmill 
This is documentation for controlling a split-belt treadmill. The hardware was designed and built by [jET](https://www.janelia.org/support-team/janelia-experimental-technology) and the software was developed by the [Karpova Lab](https://github.com/Karpova-Lab). 

<!-- - https://www.sciencedirect.com/science/article/pii/S0166432814001958
- https://www.sciencedirect.com/science/article/pii/S0966636216300376
- https://www.sciencedirect.com/science/article/abs/pii/S0306452213000754 -->


## Motor Hardware

- [Brushless Motor with 4.9:1 Gearbox](https://www.phidgets.com/?tier=3&catid=101&pcid=81&prodid=1077)
- [Brushless DC Motor Phidget](https://www.phidgets.com/?tier=3&catid=64&pcid=57&prodid=1013)
- [Phidget Hub](https://www.phidgets.com/?tier=3&catid=2&pcid=1&prodid=643)

## Control Software

### Requirements
- Python 3
- PyQt5
- Phidget Drivers and python libraries

### Installation

1. Download and install [Python 3](https://www.anaconda.com/distribution/)
2. Run `pip install PyQt5` or follow instructions [here](https://www.riverbankcomputing.com/software/pyqt/download5)
3. Install Phidget Drivers
    - [Windows Instructions](https://www.phidgets.com/docs/Language_-_Python_Windows_Command_Line)
    - [Mac Instructions](https://www.phidgets.com/docs/Language_-_Python_macOS_Terminal)

### Quickstart

1. In the "root" of this directory, run `python treadmill.py` from the command line
2. Click the "Edit Settings" 
    - Setup a default save directory
    - Input the Hub serial number and correct port numbers for the connected motors
    - Add ID numbers to the animal list
    - Exit the settings dialog
3. Select an animal from the dropdown list and click the "Connect" button
4. Edit the acceleration and duty cycle parameters and click the "Update Parameters" button to move the motors
5. To end the session click the "Save and Disconnect" button