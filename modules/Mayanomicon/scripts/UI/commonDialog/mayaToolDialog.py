import maya.OpenMayaUI as OpenMayaUI
import maya.cmds 

import inspect
import os
import posixpath 

from PySide import QtGui
from PySide import QtCore
from shiboken import wrapInstance


class MayaTool(QtGui.QMainWindow):
    def __init__(self,
                 title):
        super(MayaTool, self).__init__(self.getMainWindow())

        self.removePreviousWindow(title)

        self.setWindowTitle('{}_Tool'.format(title))
        self.setObjectName(title)

        self.setupUi()

    def removePreviousWindow(self,
                             windowName):
        """
            Only allow one instance of the tool.
        """
        widgetLink = OpenMayaUI.MQtUtil.findControl(windowName)

        if widgetLink is not None:
            guiFullName = OpenMayaUI.MQtUtil.fullName(long(widgetLink))
            maya.cmds.deleteUI(guiFullName)

    def getMainWindow(self):
        """
            Return the Maya main window widget as a Python object
         
            return: Maya Main Window.
        """
        mainWindowPtr = OpenMayaUI.MQtUtil.mainWindow()

        return wrapInstance(long(mainWindowPtr), 
                            QtGui.QWidget)

    def prepareContent(self):
        """
            Use this method to add widget.
        """
        pass

    def setupUi(self):
        """
            Create main components of the tool.
        """
        self.mainFrame = QtGui.QWidget()

        self.mainLayout = QtGui.QVBoxLayout()

        self.prepareContent()

        self.mainFrame.setLayout(self.mainLayout)

        self.setCentralWidget(self.mainFrame)


