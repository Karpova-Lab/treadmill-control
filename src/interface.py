from PyQt5.QtWidgets import QApplication, QMainWindow,QMessageBox,QPlainTextEdit,QComboBox
from PyQt5.QtGui import QTextCursor,QIcon
from PyQt5.QtCore import QTimer,QDateTime,QSize
from src.motor import *
from src.settings import *
import time
import os
import subprocess
import sys
from pathlib import Path

version  =  "1.0.1"
versionDate = "02/22/2019"

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

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.timer = QTimer()
        self.startTime = 0
        self.startDateTime = ""
        main_widget = QWidget()
        window_layout = QGridLayout()

        # create widgets
        self.settings_btn = QPushButton('Edit Settings')
        self.settings_btn.setIcon(QIcon('src/icons/settings.svg'))
        self.settings_btn.setIconSize(QSize(11,11))
        self.settings_btn.setFlat(True)
        self.left_motor = TreadMotor('Left Motor',1)      
        self.right_motor = TreadMotor('Right Motor',-1)   
        self.settingsDialog = settingsWindow()
        self.animalID =  QLabel('Animal #')
        self.animalSelection = QComboBox()
        self.updateRatList()
        self.connect_btn  = QPushButton('Connect')   
        self.update_btn = QPushButton('Update Parameters')
        self.update_btn.setEnabled(False)
        self.stop_btn = QPushButton()
        self.stop_btn.setIcon(QIcon('src/icons/stop.svg'))
        self.stop_btn.setIconSize(QSize(40,40))
        self.stop_btn.setEnabled(False)
        self.textEdit = QPlainTextEdit()
        self.textEdit.setEnabled(False)
        self.saveButton = QPushButton("Save and Disconnect")
        self.saveButton.setEnabled(False)


        # place widgets
        setup_group = QGroupBox('Experiment Setup')
        setup_layout = QGridLayout()    
        setup_layout.addWidget(self.animalID,0,0,Qt.AlignRight)  
        setup_layout.addWidget(self.animalSelection,0,1)  
        setup_layout.addWidget(self.connect_btn,1,0,1,2)


        setup_group.setLayout(setup_layout)

        # add widgets to main window
        window_layout.addWidget(self.settings_btn,0,0,Qt.AlignLeft)  
        window_layout.addWidget(setup_group,1,0,1,2)
        window_layout.addWidget(self.left_motor.control_group,2,0)
        window_layout.addWidget(self.right_motor.control_group,2,1)
        window_layout.addWidget(self.update_btn,3,0,1,2)
        window_layout.addWidget(self.stop_btn,4,0,1,2)

        window_layout.addWidget(self.textEdit,5,0,1,2)
        window_layout.addWidget(self.saveButton,6,0,1,2)
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
        self.update_btn.clicked.connect(self.updateMotors)
        self.stop_btn.clicked.connect(self.stopMotors)

        # Menu
        self.setupMenu()

    def connectMotors(self):
        if (not self.left_motor.isConnected and not self.right_motor.isConnected):
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
                except:
                    self.left_motor.close_connection()
                    self.connect_btn.setText('Connect')            
                    QMessageBox.warning(self, 'Error',
                    "Failed to connect to the right motor on port [{}] of hub [{}].\n\nIn the Settings dialog, check that the Phidget Setup has the correct values".format(righ_motorPort,hub_serialNumber), QMessageBox.Ok)
        else:
            self.left_motor.close_connection()
            self.right_motor.close_connection()
            self.connect_btn.setText('Connect')

    def updateMotors(self):
        self.left_motor.update_fxn()
        self.right_motor.update_fxn()

    def stopMotors(self):
        self.left_motor.stop_fxn()
        self.right_motor.stop_fxn()

    def startUpdating(self):
        self.update_btn.setEnabled(True)
        self.stop_btn.setEnabled(True)
        self.animalSelection.setEnabled(False)
        self.textEdit.setEnabled(True)
        self.saveButton.setEnabled(True)
        print("timer started")
        self.timer.start(500)
        self.startTime = time.time()
        self.startDateTime = QDateTime.currentDateTime().toString("yyyy_MM_dd_hh_mm")
        self.textEdit.insertPlainText(self.startDateTime + "\n")
        self.textEdit.moveCursor(QTextCursor.End) #scrolls to the end whenever there is new data

    def stopUpdating(self):
        self.update_btn.setEnabled(False)
        self.stop_btn.setEnabled(False)
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
        self.textEdit.insertPlainText(dataText)
        self.textEdit.moveCursor(QTextCursor.End) #scrolls to the end whenever there is new data

    def saveFile(self):
        saveName = QFileDialog.getSaveFileName(self,
                        "Save Velocity Log",
                        self.animalSelection.currentText() + "_" + self.startDateTime + "_treadmill_log","(*.csv)"
                        )
        print("savename"+saveName[0])

        if saveName[0] != '':
            self.left_motor.open_connection()
            self.right_motor.open_connection()
            with open(saveName[0], "w") as text_file:
                text_file.write(self.textEdit.toPlainText())
        else:
            print("save canceled") 

    def openSaveDirectory(self):
        saveDirectory = self.settingsDialog.saveDefault.value.text()
        openFolder(str(Path(saveDirectory)))

    def openAppLocation(self):
        openFolder(str(Path(os.getcwd())))     

    def closeEvent(self, event):
        self.left_motor.close_connection()
        # reply = QMessageBox.question(self, 'Message',
        #     "Are you sure to quit?", QMessageBox.Yes, QMessageBox.No)
        # if reply == QMessageBox.Yes:
        #     self.left_motor.close_connection()
        #     event.accept()
        # else:
        #     event.ignore()

    def setupMenu(self):
        bar  = self.menuBar()
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