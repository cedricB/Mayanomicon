import pickle
from PySide import QtGui
from PySide import QtCore
from toggleParentWeights import lib as toggleParentWeightsLib
from toggleParentWeights.Models import outliner
reload(outliner)
reload(toggleParentWeightsLib)


class BasicListView(QtGui.QListView):
    def __init__(self, parent=None):
        super(BasicListView, self).__init__(parent)

        self.setDragDropMode(self.InternalMove)

        self.setSpacing(2)
        self.setUniformItemSizes(True)

        self.constraintViewModel = outliner.BasicDragDropModel()

        self.setModel(self.constraintViewModel)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            super(BasicListView, self).dragEnterEvent(event)

    def dragMoveEvent(self, event):
        super(BasicListView, self).dragMoveEvent(event)

    def dropEvent(self, event):
        event.setDropAction(QtCore.Qt.MoveAction)
        super(BasicListView, self).dropEvent(event)

    def _populate(self,
                  node):
        if not node:
            return

        nodeUtils = toggleParentWeightsLib.Builder()
        
        model_data = nodeUtils.collectParentTargets(node)

        self.constraintViewModel = outliner.BasicDragDropModel(model_data)

        self.setModel(self.constraintViewModel)

    def getParentTargets(self):
        return self.constraintViewModel.items[:]