import maya.OpenMayaUI as OpenMayaUI
import maya.cmds 
import pickle
from PySide import QtGui
from PySide import QtCore
from shiboken import wrapInstance

from UI.commonDialog import mayaToolDialog
from UI.commonWidgets import nodePicker

from toggleParentWeights.Widgets import outlinerWidgets
from toggleParentWeights import lib as toggleParentWeightsLib
reload(nodePicker)
reload(outlinerWidgets)
reload(toggleParentWeightsLib)


class ToggleParentWeightsTool(mayaToolDialog.MayaTool):
    def __init__(self):
        super(ToggleParentWeightsTool, self).__init__('ToggleParentWeights')

    def prepareContent(self):
        self.createButton = QtGui.QPushButton('Connect toggle node')
        self.createButton.setMinimumHeight(38)

        self.constraintWidget = nodePicker.NodePicker('Choose Parent constraint:',
                                                      filter='constraint')

        self.constraintView = outlinerWidgets.BasicListView()

        self.mainLayout.addWidget(self.constraintWidget)
        self.mainLayout.addWidget(self.constraintView)
        self.mainLayout.addWidget(self.createButton)

        self.setMinimumWidth(490)

        self.createButton.clicked.connect(self._connectNodes)

        self.constraintWidget.actionButton.clicked.connect(self._populateParentTargets)

    def _populateParentTargets(self):
        node = str(self.constraintWidget.stringWidget.text()).strip()
        
        if not node:
            return

        self.constraintView._populate(node)

    def _connectNodes(self):
        node = str(self.constraintWidget.stringWidget.text()).strip()  

        if not node:
            return

        nodeUtils = toggleParentWeightsLib.Builder()
        nodeUtils.attach(self.constraintView.getParentTargets())

def Run():
    toggleUI = ToggleParentWeightsTool()

    toggleUI.show()

    return toggleUI