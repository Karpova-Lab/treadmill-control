from src.BLDC import *
from src.customComponents import *
from PyQt5.QtWidgets import QCheckBox
from PyQt5.QtCore import QObject,pyqtSignal,QSettings

class TreadMotor(QObject):
    startClock = pyqtSignal()
    stopClock = pyqtSignal()

    def __init__(self,saveName,direction):
        super().__init__()        
        # create motor object
        try:
            self.ch = BLDCMotor()
        except PhidgetException as e:
            sys.stderr.write("Runtime Error -> Creating BLDCMotor: \n\t")
            DisplayError(e)
            raise
        except RuntimeError as e:
            sys.stderr.write("Runtime Error -> Creating BLDCMotor: \n\t" + e)
            raise
        self.ch.setIsHubPortDevice(0)
        self.ch.setChannel(0)  
        self.ch.setOnAttachHandler(onAttachHandler)
        self.ch.setOnDetachHandler(onDetachHandler)
        self.ch.setOnErrorHandler(onErrorHandler)

        # widgets
        self.connect = QPushButton('Connect '+saveName)
        self.flip_checkbox = QCheckBox('Flip Direction')
        self.accel = label_and_spin('Acceleration',[.1,100],.01,.1)
        self.decel = label_and_spin('Deceleration',[0,100],.01,.1)
        self.duty = label_and_spin('Duty Cycle',[0,1],.01,.1)
        self.speed_lbl = QLabel(' rpm')
        self.speed_lbl.setAlignment(Qt.AlignCenter)

        # control groupbox
        self.control_group = QGroupBox(saveName)
        control_layout = QGridLayout()
        control_layout.addWidget(self.flip_checkbox,0,0,Qt.AlignCenter)
        control_layout.addWidget(self.accel.widget,1,0)
        control_layout.addWidget(self.decel.widget,2,0)
        control_layout.addWidget(self.duty.widget,3,0)
        control_layout.addWidget(self.speed_lbl,4,0)
        self.control_group.setLayout(control_layout)
        self.control_group.setEnabled(False)
        
        #variables
        self.isConnected = False
        self.oldPos = 0
        self.newPos = 0
        self.speed = 0
        self.startTime = time.time()
        self.saveName = saveName
        self.dir = direction

    def update_fxn(self):
        if self.flip_checkbox.isChecked():
            flip = -1
        else:
            flip = 1
        self.ch.setTargetVelocity(self.duty.spin.value()*self.dir*flip)
        self.ch.setAcceleration(self.accel.spin.value())

    def stop_fxn(self):
        self.ch.setAcceleration(self.decel.spin.value()) # set to 0 for e-stop
        self.ch.setTargetVelocity(0)
    
    def open_connection(self,serialNumber,motorPort):
        if (not self.isConnected):
            try:
                self.ch.setDeviceSerialNumber(serialNumber)
                self.ch.setHubPort(motorPort)
                self.ch.openWaitForAttachment(5000)
                self.isConnected = True
                self.ch.setDataInterval(100)
                self.ch.setRescaleFactor(1/(8*3*4.9)) # 8 poles * 3 phase * 4.9:1 gear reduction. Unit=rpm
            except PhidgetException as e:
                PrintOpenErrorMessage(e, self.ch)
                raise EndProgramSignal("Program Terminated: Open Failed")
            self.startClock.emit()
            self.control_group.setEnabled(True)
        else:
            self.close_connection()

    def close_connection(self):
            self.isConnected = False
            self.control_group.setEnabled(False)
            self.ch.setOnVelocityUpdateHandler(None)
            self.ch.setOnPositionChangeHandler(None)

            self.stopClock.emit()
            self.speed = 0
            self.ch.close()            

    def getSpeed(self):
        self.newPos = self.ch.getPosition()
        self.speed = abs((self.newPos - self.oldPos)*60)
        self.oldPos = self.newPos
        self.speed_lbl.setText('{:.1f} rpm'.format(self.speed))

