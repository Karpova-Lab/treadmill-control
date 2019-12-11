https://github.com/Karpova-Lab/treadmill-control
# Split-belt Treadmill 
This is documentation for controlling a split-belt treadmill. The hardware was designed and built by [jET](https://www.janelia.org/support-team/janelia-experimental-technology) and the software was developed by the [Karpova Lab](https://github.com/Karpova-Lab). 

<!-- - https://www.sciencedirect.com/science/article/pii/S0166432814001958
- https://www.sciencedirect.com/science/article/pii/S0966636216300376
- https://www.sciencedirect.com/science/article/abs/pii/S0306452213000754 -->


## Motor Hardware

- [Brushless Motor with 24:1 Gearbox](https://www.phidgets.com/?tier=3&catid=101&pcid=81&prodid=1079)
- [Brushless DC Motor Phidget](https://www.phidgets.com/?tier=3&catid=64&pcid=57&prodid=1013)
- [Phidget Hub](https://www.phidgets.com/?tier=3&catid=2&pcid=1&prodid=643)

## Control Software

### Installation
-  Download and install the [Phidgets Windows Drivers](https://www.phidgets.com/docs/OS_-_Windows#Quick_Downloads)
- Download the latest [Treadmill.exe](https://github.com/Karpova-Lab/treadmill-control/releases)
    
### Quickstart
1. Open **Treadmill.exe**
2. Click the "Edit Settings" button
    - Setup a default save directory
    - Input the hub serial number and correct port numbers for the connected motors
    - Add ID numbers to the animal list
    - Exit the settings dialog
3. Select an animal from the dropdown list and click the "Connect" button
4. Edit the motor parameters and click the "Send Parameters" button to start the motors
    - The motors can be stopped by pressing spacebar or pressing the stop button
    - The duty cycle of the motors can be adjusted using arrow keys
        - Up or right arrow to increase
        - Down or left arrow to decrease
5. To end the session click the "Save and Disconnect" button

### Development
The software is written in Python using [PyQt5](https://www.riverbankcomputing.com/software/pyqt/intro) as the GUI framework. To modify and/or run this code you'll need to do the following:

1. Download and install Phidget Drivers and Phidget Python Module
    - [Windows Instructions](https://www.phidgets.com/docs/Language_-_Python_Windows_Command_Line)
    - [Mac Instructions](https://www.phidgets.com/docs/Language_-_Python_macOS_Terminal)
2. Download and install [Python 3](https://www.anaconda.com/distribution/)
3. Download and install PyQt5 by running `pip install PyQt5` or follow instructions [here](https://www.riverbankcomputing.com/software/pyqt/download5)
4. Make desired changes to Python files found in the directory named "src"
5. From the command line, navigate to this directory and run `python treadmill.py`

## Software License

Janelia Open-Source Software

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

- Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
    
- Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.

- Neither the name of HHMI nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS “AS IS” AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.