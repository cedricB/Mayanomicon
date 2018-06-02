import os
import posixpath 
import maya.cmds 
import maya.mel 

import PySide.QtGui as QtGui
import PySide.QtCore as QtCore


class NodePicker(QtGui.QWidget):
    def __init__(self,
                 labelName,
                 icon='picker.png'):
        super(NodePicker, self).__init__()

        self.labelName = labelName

        self.icon = icon

        self.initUI()

    def initUI(self):
        self.mainLayout = QtGui.QHBoxLayout()

        self.mainLayout.setContentsMargins(0, 0, 0, 0)

        self.labelWidget = QtGui.QLabel(self.labelName)
        self.stringWidget = QtGui.QLineEdit()
        self.actionButton = QtGui.QPushButton('')

        self.actionButton.setFixedSize(20, 20)

        self.mainLayout.addWidget(self.labelWidget)
        self.mainLayout.addWidget(self.stringWidget)
        self.mainLayout.addWidget(self.actionButton)

        self.setLayout(self.mainLayout)

        self._setIcon(self.actionButton,
                      self.icon)

        self.actionButton.clicked.connect(self._pickSelection)

    def _setIcon(self,
                 button,
                 iconName):
        icon = QtGui.QIcon()

        currentDirectory = str(__file__)
        for index in range(4):
            currentDirectory = os.path.dirname(currentDirectory)

        imagePath = posixpath.join(currentDirectory,
                                   'icons',
                                   iconName)

        imagePath = imagePath.replace('\\', '/')

        icon.addPixmap(QtGui.QPixmap(imagePath))
        button.setIcon(icon)

    def _pickSelection(self):
        self.stringWidget.setText('')

        currentSelection = maya.cmds.ls(sl=True, o=True) or []

        if not currentSelection:
            return

        self.stringWidget.setText(currentSelection[0])