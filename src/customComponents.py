from PyQt5.QtWidgets import QLabel, QDoubleSpinBox, QWidget, QGridLayout, QLineEdit, QGroupBox, QPushButton
from PyQt5.QtCore import Qt

class label_and_spin():
    def __init__(self,label,range,step,startVal):
        self.label = QLabel(label)

        self.spin = QDoubleSpinBox()
        self.spin.setRange(range[0],range[1])
        self.spin.setSingleStep(step)
        self.spin.setValue(startVal)

        self.widget = QWidget()
        self.layout = QGridLayout()
        self.layout.setContentsMargins(0,0,0,0)
        self.layout.addWidget(self.label,0,0,Qt.AlignRight)
        self.layout.addWidget(self.spin,0,1)
        self.widget.setLayout(self.layout)
        
    def setEnabled(self,val):
        self.label.setEnabled(val)
        self.spin.setEnabled(val)

class label_and_text():
    def __init__(self,label,startVal,vertical=True):
        self.label = QLabel(label)
        self.label.setAlignment(Qt.AlignCenter)
        
        self.line = QLineEdit()
        self.line.setAlignment(Qt.AlignCenter)
        self.line.setText(str(startVal))

        self.widget = QWidget()
        self.layout = QGridLayout()
        self.layout.setContentsMargins(0,0,0,0)
        if vertical==True:
            self.layout.addWidget(self.label,0,0,Qt.AlignCenter)
            self.layout.addWidget(self.line,1,0)
        else:
            self.layout.addWidget(self.label,0,0,Qt.AlignRight)
            self.layout.addWidget(self.line,0,1)
        self.widget.setLayout(self.layout)

    def setEnabled(self,val):
        self.label.setEnabled(val)
        self.line.setEnabled(val)