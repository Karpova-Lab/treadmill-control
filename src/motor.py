from src.BLDC import *
from src.customComponents import *
from PyQt5.QtWidgets import QCheckBox, QFrame, QProgressBar
from PyQt5.QtCore import QObject, pyqtSignal, QSettings
import sys
from math import pi

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
        self.accel = label_and_spin('Acceleration',[.1,100],.01,.25)
        self.decel = label_and_spin('Deceleration',[.1,100],.01,.5)
        self.duty = label_and_spin('Duty Cycle',[0.15,1],.01,.15)
        
        self.update_btn = QPushButton('Send Parameters')
        self.update_btn.setStyleSheet("background-color: #00cc00;")
        self.update_btn.setFocusPolicy(Qt.NoFocus)

        self.speed_lbl = QLabel(' cm/s')
        self.speed_lbl.setAlignment(Qt.AlignCenter)
        self.speed_bar = QProgressBar()
        self.speed_bar.setMinimum(0)
        self.speed_bar.setMaximum(90)
        self.speed_bar.setTextVisible(False)

        # control groupbox
        horzLine = QFrame()
        horzLine.setFrameShape(QFrame.HLine)
        horzLine.setFrameShadow(QFrame.Sunken)

        self.control_group = QGroupBox(saveName)
        control_layout = QGridLayout()
        control_layout.addWidget(self.flip_checkbox,0,0,Qt.AlignCenter)
        control_layout.addWidget(self.accel.widget,1,0)
        control_layout.addWidget(self.decel.widget,2,0)
        control_layout.addWidget(horzLine,3,0)
        control_layout.addWidget(self.duty.widget,4,0)
        control_layout.addWidget(self.update_btn,5,0)
        control_layout.addWidget(self.speed_lbl,6,0)
        control_layout.addWidget(self.speed_bar,7,0)
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
        commutations = 8*3 # 8 poles * 3 phase
        gearReduction = 24 # 24:1 gearbox
        wheelRadius = .75*2.54 # .75inches * 2.54"/cm
        self.conversion = 1/commutations*1/gearReduction *2*pi*wheelRadius # cm
        
    def update_fxn(self):
        if self.flip_checkbox.isChecked():
            flip = -1
        else:
            flip = 1
        self.ch.setTargetVelocity(self.duty.spin.value()*self.dir*flip)
        self.ch.setAcceleration(self.accel.spin.value())
        self.duty.spin.clearFocus()
        self.accel.spin.clearFocus()
        self.decel.spin.clearFocus()

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
                self.ch.setRescaleFactor(self.conversion)
            except PhidgetException as e:
                PrintOpenErrorMessage(e, self.ch)
                raise EndProgramSignal("Program Terminated: Open Failed")
            self.startClock.emit()
            self.control_group.setEnabled(True)
            self.oldPos = self.ch.getPosition()

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
        self.speed = abs((self.newPos - self.oldPos)*2) #timer interval is 500ms so we multiply distance by 2 to get cm/s
        self.oldPos = self.newPos
        self.speed_lbl.setText('{:.1f} cm/s'.format(self.speed))
        self.speed_bar.setValue(self.speed)