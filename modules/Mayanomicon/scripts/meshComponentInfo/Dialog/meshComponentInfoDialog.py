import maya.OpenMayaUI as OpenMayaUI
import maya.cmds 

from PySide import QtGui
from PySide import QtCore
from shiboken import wrapInstance

from UI.commonDialog import mayaToolDialog
from UI.commonWidgets import nodePicker
from meshComponentInfo import utils as meshComponentUtils


class MeshComponentInfoTool(mayaToolDialog.MayaTool):
    def __init__(self):
        super(MeshComponentInfoTool, self).__init__('MeshComponentInfo')

    def prepareContent(self):
        self.createButton = QtGui.QPushButton('Connect Node to Shape')
        self.createButton.setMinimumHeight(38)

        self.shapeWidget = nodePicker.NodePicker('Shape:')

        self.nodeWidget = nodePicker.NodePicker('Node:')
        
        self.mainLayout.addWidget(self.shapeWidget)
        self.mainLayout.addWidget(self.nodeWidget)
        self.mainLayout.addWidget(self.createButton)

        self.setMinimumWidth(400)

        self.createButton.clicked.connect(self._connectNodes)

    def _connectNodes(self):
        shape = self.shapeWidget.stringWidget.text() 
        node = self.nodeWidget.stringWidget.text() 

        if not all([shape, node]):
            return
    
        builder = meshComponentUtils.Builder()
        
        builder.attach(shape, node)


def Run():
    meshUI = MeshComponentInfoTool()

    meshUI.show()

    return meshUI