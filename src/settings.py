from PyQt5.QtWidgets import QDialog,QFileDialog,QListWidget
from PyQt5.QtCore import QSettings,QStandardPaths,pyqtSignal
from src.customComponents import *

class settingsWindow(QDialog):
    settingsClosed = pyqtSignal()
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Settings')
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        # grab previous settings from memory
        serialSuggestion = self.getSuggestion('Hub S/N',529250)
        leftSuggestion = self.getSuggestion('Left Motor',0)
        rightSuggestion = self.getSuggestion('Right Motor',1)
        saveDirectorySuggestion = self.getSuggestion('Save Directory',QStandardPaths.writableLocation(QStandardPaths.HomeLocation))

        # create widgets
        self.saveDefault = directoryChooser(saveDirectorySuggestion)
        self.phidgetSetup = phidgetSettings(serialSuggestion,leftSuggestion,rightSuggestion)
        self.phidgetSetup.group.setFixedWidth(200)
        self.ratList  = itemList()
        self.ratList.groupbox.setFixedWidth(200)

        # place widgets
        settingsLayout = QGridLayout()
        settingsLayout.addWidget(self.saveDefault.groupBox,0,0,1,2)
        settingsLayout.addWidget(self.phidgetSetup.group,1,0,Qt.AlignRight)
        settingsLayout.addWidget(self.ratList.groupbox,1,1,2,1,Qt.AlignLeft)
        settingsLayout.setRowStretch(2,1)
        self.setLayout(settingsLayout)

        #widget connections
        self.rejected.connect(self.close)

    def getSuggestion(self,settingName,defaultSuggestion):
        settings = QSettings('Bobcat Engineering','Treadmill')
        if settings.value(settingName) is None:
            return defaultSuggestion
        else:
            return settings.value(settingName)

    def closeEvent(self, event):
        settings = QSettings('Bobcat Engineering','Treadmill')
        settings.setValue('Hub S/N',self.phidgetSetup.serial.line.text())
        settings.setValue('Left Motor',self.phidgetSetup.left_motor_port.line.text())
        settings.setValue('Right Motor',self.phidgetSetup.right_motor_port.line.text())
        settings.setValue('Save Directory',self.saveDefault.value.text())
        settings.setValue('Animal List',self.ratList.getListOfItems())
        self.settingsClosed.emit()

class directoryChooser():
    def __init__(self,suggested):
        # create widgets
        self.label = QLabel('<b>Current Save Directory:</b>')
        self.value = QLabel(suggested)
        self.edit_btn  = QPushButton('Change Directory')
        self.edit_btn.setFocusPolicy(Qt.NoFocus)

        # place widgets
        self.groupBox = QGroupBox('Saving Defaults')
        layout = QGridLayout()
        layout.addWidget(self.label,0,0,1,2)
        layout.addWidget(self.value,1,0,1,2)
        layout.addWidget(self.edit_btn,2,0)
        layout.setColumnStretch(1,1)
        self.groupBox.setLayout(layout)

        # widget connections
        self.edit_btn.clicked.connect(self.chooseFolder)        


    def chooseFolder(self):
        chosenFolder = QFileDialog.getExistingDirectory(
            None,
            'Choose Default Save Directory',
            QStandardPaths.writableLocation(QStandardPaths.HomeLocation)
            )
        if chosenFolder is not '':
            self.value.setText(chosenFolder)

class phidgetSettings():
    def __init__(self,serialSuggestion,leftSuggestion,rightSuggestion):
        self.serial = label_and_text('Hub S/N',serialSuggestion)
        self.left_motor_port = label_and_text('Left\nMotor Port',leftSuggestion)
        self.right_motor_port = label_and_text('Right\nMotor Port',rightSuggestion)

        self.group = QGroupBox('Phidget Setup')
        layout = QGridLayout()       
        layout.addWidget(self.serial.widget,0,0,1,2)
        layout.addWidget(self.left_motor_port.widget,1,0)
        layout.addWidget(self.right_motor_port.widget,1,1)
        self.group.setLayout(layout)

class itemList():
    def __init__(self):
        self.add_btn =  QPushButton('Add ID')
        self.remove_btn = QPushButton('Remove Selection')
        self.item_input = QLineEdit()
        self.list = QListWidget()
        settings = QSettings('Bobcat Engineering','Treadmill')
        try:
            self.list.addItems(settings.value('Animal List'))
        except:
            pass

        self.groupbox = QGroupBox('Animal IDs')
        self.layout = QGridLayout()
        self.layout.addWidget(self.item_input,0,0)
        self.layout.addWidget(self.add_btn,0,1)
        self.layout.addWidget(self.list,1,0,1,2)
        self.layout.addWidget(self.remove_btn,2,0,1,2)
        self.groupbox.setLayout(self.layout)

        self.add_btn.clicked.connect(self.addItem)
        self.item_input.returnPressed.connect(self.addItem)
        self.remove_btn.clicked.connect(self.removeItem)

    def addItem(self):
        itemList = self.getListOfItems()
        newItem = self.item_input.text()
        if newItem != '' and newItem not in itemList:
            self.list.addItem(self.item_input.text())
        self.list.sortItems()
        self.item_input.clear()
    
    def removeItem(self):
        if self.list.count() > 0:
            self.list.takeItem(self.list.currentRow())

    def getListOfItems(self):        
        tempList = []
        for i in range(self.list.count()):
            tempList.append(self.list.item(i).text())
        return tempList