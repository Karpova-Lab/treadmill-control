from PyQt5.QtWidgets import QApplication, QMainWindow,QMessageBox,QPlainTextEdit,QComboBox
from PyQt5.QtGui import QTextCursor, QIcon, QKeyEvent
from PyQt5.QtCore import QTimer, QDateTime, QSize, Qt
from src.motor import *
from src.settings import *
import time
import os
import subprocess
from pathlib import Path
#*Semantic Versioning
# MAJOR version when you make incompatible API changes,
# MINOR version when you add functionality in a backwards-compatible manner, and
# PATCH version when you make backwards-compatible bug fixes.
version = "1.4.1"
versionDate = "03/22/2019"

if sys.platform == 'darwin':
    def openFolder(path):
        subprocess.check_call(['open', '--', path])
elif sys.platform == 'linux2':
    def openFolder(path):
        subprocess.check_call(['xdg-open', '--', path])
elif sys.platform == 'win32':
    def openFolder(path):
        try:
            output = subprocess.check_call(['explorer', path])
        except subprocess.CalledProcessError as e:
            output = e.output
            print(output)

#https://blog.aaronhktan.com/posts/2018/05/14/pyqt5-pyinstaller-executable
#supported packages:https://github.com/pyinstaller/pyinstaller/wiki/Supported-Packages
#from windows command line `pyinstaller --onefile treadmill.spec`
# Translate asset paths to useable format for PyInstaller
def resource_path(relative_path):
  if hasattr(sys, '_MEIPASS'):
      return os.path.join(sys._MEIPASS, relative_path)
  return os.path.join(os.path.abspath('.'), relative_path)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.timer = QTimer()
        self.startTime = 0
        self.startDateTime = ""
        main_widget = QWidget()
        window_layout = QGridLayout()

        # create widgets
        columnWidth = 188

        self.settings_btn = QPushButton('Edit Settings')
        self.settings_btn.setIcon(QIcon(resource_path('src/icons/settings.svg')))
        self.settings_btn.setIconSize(QSize(11,11))
        self.settings_btn.setFlat(True)
        self.settings_btn.setFocusPolicy(Qt.NoFocus)

        self.independent_check = QCheckBox('Independent Control')
        self.independent_check.setEnabled(False)
        self.independent_check.setFocusPolicy(Qt.NoFocus)

        self.left_motor = TreadMotor('Left Motor',1)      
        self.right_motor = TreadMotor('Right Motor',-1)   
        self.left_motor.control_group.setFixedWidth(columnWidth)
        self.right_motor.control_group.setFixedWidth(columnWidth)

        self.settingsDialog = settingsWindow()
        self.animalID =  QLabel('Animal #')
        self.animalSelection = QComboBox()
        self.animalSelection.setFocusPolicy(Qt.NoFocus)
        self.updateRatList()
        self.connect_btn  = QPushButton('Connect')   
        self.connect_btn.setFocusPolicy(Qt.NoFocus)


        self.minus_btn = QPushButton('-')
        self.plus_btn = QPushButton('+')

        self.stop_btn = QPushButton()
        self.stop_btn.setIcon(QIcon(resource_path('src/icons/stop.svg')))
        self.stop_btn.setIconSize(QSize(columnWidth*.7,columnWidth*.7))
        self.stop_btn.setFixedSize(columnWidth,columnWidth)

        self.textEdit = QPlainTextEdit()
        self.textEdit.setEnabled(False)
        self.textEdit.setFixedWidth(columnWidth)
        
        self.saveButton = QPushButton("Save and Disconnect")
        self.saveButton.setEnabled(False)

        # place widgets
        setup_group = QGroupBox('Experiment Setup')
        setup_layout = QGridLayout()    
        setup_layout.addWidget(self.animalID,0,0,Qt.AlignRight)  
        setup_layout.addWidget(self.animalSelection,0,1)  
        setup_layout.addWidget(self.connect_btn,0,2)
        setup_group.setLayout(setup_layout)

        #live controls Widget
        self.liveWidget = QWidget()
        live_layout = QGridLayout()
        live_layout.addWidget(self.minus_btn,1,0)
        live_layout.addWidget(self.plus_btn,1,1)
        live_layout.addWidget(self.stop_btn,2,0,1,2)
        live_layout.setContentsMargins(0,0,0,0)
        self.liveWidget.setLayout(live_layout)
        self.liveWidget.setEnabled(False)


        # add widgets to main window
        window_layout.addWidget(self.settings_btn,0,0,Qt.AlignLeft)  
        window_layout.addWidget(setup_group,1,0,1,2)
        window_layout.addWidget(self.independent_check,2,0,1,2,Qt.AlignCenter)
        window_layout.addWidget(self.left_motor.control_group,3,0,Qt.AlignRight)
        window_layout.addWidget(self.right_motor.control_group,3,1,Qt.AlignLeft)
        window_layout.addWidget(self.liveWidget,4,0,Qt.AlignRight)
        window_layout.addWidget(self.textEdit,4,1,3,1,Qt.AlignLeft)
        window_layout.setRowStretch(6,1)
        window_layout.addWidget(self.saveButton,7,0,1,2)
        main_widget.setLayout(window_layout)

        self.setCentralWidget(main_widget)
        self.setWindowTitle('Treadmill Controller')

        # connections
        self.left_motor.startClock.connect(self.startUpdating)
        self.left_motor.stopClock.connect(self.stopUpdating)
        self.saveButton.clicked.connect(self.saveFile)
        self.settingsDialog.settingsClosed.connect(self.updateRatList)
        self.settings_btn.clicked.connect(self.settingsDialog.exec)
        self.connect_btn.clicked.connect(self.connectMotors)
        self.timer.timeout.connect(self.printData)
        self.left_motor.update_btn.clicked.connect(self.leftUpdateClicked)
        self.right_motor.update_btn.clicked.connect(self.rightUpdateClicked)
        self.stop_btn.clicked.connect(self.stopMotors)
        self.left_motor.flip_checkbox.clicked.connect(self.matchRight)
        self.left_motor.accel.spin.valueChanged.connect(self.matchRight)
        self.left_motor.decel.spin.valueChanged.connect(self.matchRight)
        self.left_motor.duty.spin.valueChanged.connect(self.matchRight)
        self.independent_check.clicked.connect(self.makeIndependent)
        self.minus_btn.clicked.connect(self.decrease_duty)
        self.plus_btn.clicked.connect(self.increase_duty)

        # Menu
        self.setupMenu()

    def matchRight(self):
        if not self.independent_check.isChecked():
            self.right_motor.flip_checkbox.setChecked(self.left_motor.flip_checkbox.isChecked())
            self.right_motor.accel.spin.setValue(self.left_motor.accel.spin.value())
            self.right_motor.decel.spin.setValue(self.left_motor.decel.spin.value())
            self.right_motor.duty.spin.setValue(self.left_motor.duty.spin.value())

    def makeIndependent(self):
        self.right_motor.control_group.setEnabled(self.independent_check.isChecked())
        self.matchRight()

    def connectMotors(self):
        if (not self.left_motor.isConnected and not self.right_motor.isConnected): #Connect button clicked
            # get values from memory
            settings = QSettings('Bobcat Engineering','Treadmill')
            hub_serialNumber = settings.value('Hub S/N',type=int)
            left_motorPort = settings.value('Left Motor',type=int)
            righ_motorPort = settings.value('Right Motor',type=int)

            #open connections
            keepGoing = True
            self.connect_btn.setText('Disconnect')
            try:
                self.left_motor.open_connection(hub_serialNumber,left_motorPort)
            except:
                self.connect_btn.setText('Connect')
                QMessageBox.warning(self, 'Error',
                "Failed to connect to the left motor on port [{}] of hub [{}].\n\nIn the Settings dialog, check that the Phidget Setup has the correct values".format(left_motorPort,hub_serialNumber), QMessageBox.Ok)
                keepGoing = False
            if keepGoing:
                try:
                    self.right_motor.open_connection(hub_serialNumber,righ_motorPort)
                    self.makeIndependent()
                except:
                    self.left_motor.close_connection()
                    self.connect_btn.setText('Connect')            
                    QMessageBox.warning(self, 'Error',
                    "Failed to connect to the right motor on port [{}] of hub [{}].\n\nIn the Settings dialog, check that the Phidget Setup has the correct values".format(righ_motorPort,hub_serialNumber), QMessageBox.Ok)
        else: # Disconnect button clicked
            self.disconnectMotors()

    def disconnectMotors(self):
        self.left_motor.close_connection()
        self.right_motor.close_connection()
        self.connect_btn.setText('Connect')

    def leftUpdateClicked(self):
        if self.independent_check.isChecked():
            self.left_motor.update_fxn()
            self.liveWidget.setEnabled(True)
        else:
            self.updateMotors()
    def rightUpdateClicked(self):
        self.right_motor.update_fxn()
        self.liveWidget.setEnabled(True)

    def updateMotors(self):
        self.left_motor.update_fxn()
        self.right_motor.update_fxn()
        self.liveWidget.setEnabled(True)

    def increase_duty(self):
        self.left_motor.duty.spin.setValue(self.left_motor.duty.spin.value() + .01) 
        if self.independent_check.isChecked():
            self.right_motor.duty.spin.setValue(self.right_motor.duty.spin.value() + .01) 
        self.updateMotors()

    def decrease_duty(self):
        self.left_motor.duty.spin.setValue(self.left_motor.duty.spin.value() - .01) 
        if self.independent_check.isChecked():
            self.right_motor.duty.spin.setValue(self.right_motor.duty.spin.value() - .01) 
        self.updateMotors()

    def stopMotors(self):
        self.left_motor.stop_fxn()
        self.right_motor.stop_fxn()
        self.liveWidget.setEnabled(False)

    def startUpdating(self):
        self.independent_check.setEnabled(True)
        self.animalSelection.setEnabled(False)
        self.textEdit.setEnabled(True)
        self.saveButton.setEnabled(True)
        print("timer started")
        self.timer.start(500)
        self.startTime = time.time()
        self.startDateTime = QDateTime.currentDateTime().toString("yyyy_MM_dd_hh_mm")
        self.textEdit.insertPlainText(self.startDateTime + "\n")
        self.textEdit.insertPlainText("version," + version + '\n')
        self.textEdit.moveCursor(QTextCursor.End) #scrolls to the end whenever there is new data

    def stopUpdating(self):
        self.independent_check.setEnabled(False)
        self.animalSelection.setEnabled(True)
        self.textEdit.setEnabled(False)
        self.saveButton.setEnabled(False)
        print("timer stopped")
        self.timer.stop()

    def printData(self):
        if self.left_motor.isConnected:
            self.left_motor.getSpeed()
        if self.right_motor.isConnected:
            self.right_motor.getSpeed()

        dataText = '{:.3f},{:.1f},{:.1f}\n'.format(time.time()- self.startTime,self.left_motor.speed,self.right_motor.speed) 
        self.textEdit.moveCursor(QTextCursor.End) #scrolls to the end whenever there is new data
        self.textEdit.insertPlainText(dataText)

    def saveFile(self):
        saveName = QFileDialog.getSaveFileName(self,
                                               "Save Velocity Log",
                                               self.settingsDialog.saveDefault.value.text() +'/'+ self.animalSelection.currentText() + "_" + self.startDateTime + "_treadmill_log","(*.csv)"
                                               )
        print("savename"+saveName[0])

        if saveName[0] != '':
            self.disconnectMotors()
            with open(saveName[0], "w") as text_file:
                text_file.write(self.textEdit.toPlainText())
            self.textEdit.clear()
        else:
            print("save canceled") 

    def openSaveDirectory(self):
        saveDirectory = self.settingsDialog.saveDefault.value.text()
        openFolder(str(Path(saveDirectory)))

    def openAppLocation(self):
        openFolder(str(Path(os.getcwd())))

    def closeEvent(self, event):
        self.disconnectMotors()
        # reply = QMessageBox.question(self, 'Message',
        #     "Are you sure to quit?", QMessageBox.Yes, QMessageBox.No)
        # if reply == QMessageBox.Yes:
        #     self.left_motor.close_connection()
        #     event.accept()
        # else:
        #     event.ignore()

    def setupMenu(self):
        bar = self.menuBar()
        fileMenu  = bar.addMenu('File')
        settings_action = fileMenu.addAction('Settings...')
        settings_action.triggered.connect(self.settingsDialog.exec)
        goMenu = bar.addMenu('Go To')
        goToSaveDir_action = goMenu.addAction("Default Save Directory")
        goToSaveDir_action.triggered.connect(self.openSaveDirectory)
        goToAppLocation_action = goMenu.addAction('App Install Directory')
        goToAppLocation_action.triggered.connect(self.openAppLocation)
        
        helpMenu = bar.addMenu('Help')
        aboutAction = helpMenu.addAction('About...')
        self.aboutDialog = QMessageBox()
        self.aboutDialog.setWindowTitle("About")
        self.aboutDialog.setText('Version: {}\nUpdated: {}'.format(version,versionDate))
        self.aboutDialog.setStandardButtons(QMessageBox.Close)
        aboutAction.triggered.connect(self.aboutDialog.exec)

    def updateRatList(self):
        self.animalSelection.clear()
        settings = QSettings('Bobcat Engineering','Treadmill')
        try:
            self.animalSelection.addItems(settings.value('Animal List'))
        except:
            pass

    def keyPressEvent(self, event):
        if type(event) == QKeyEvent:
            pressedKey = event.key()
            if pressedKey == 32: # stop motors with space bar
                self.stopMotors()
            elif pressedKey == 16777236 or pressedKey == 16777235 : # increase duty with up or right arrow
                self.increase_duty()
            elif pressedKey == 16777234 or pressedKey == 16777237: # decreased duty with down or left arrow
                self.decrease_duty()
            event.accept()
        else:
            event.ignore()