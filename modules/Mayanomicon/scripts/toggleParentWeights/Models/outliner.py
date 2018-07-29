import pickle
from PySide import QtGui
from PySide import QtCore


class BasicDragDropData(QtCore.QMimeData):
    TARGET_TYPE = 'application/x-basicdragdrop'

    def __init__(self,
                 item_data,
                 input_index):
        super(BasicDragDropData, self).__init__()

        self.item_index_value = input_index

        self.item_data = item_data

    def formats(self):
        return self.TARGET_TYPE

    def display(self):
        return self.item_data.value


class BasicDragDropModel(QtCore.QAbstractListModel):
    TARGET_TYPE = 'application/x-basicdragdrop'

    def __init__(self, items=None):
        super(BasicDragDropModel, self).__init__()

        if not items:
            self.items = []

        else:
            self.items = items[:]

    def rowCount(self, parent=QtCore.QModelIndex()):
        return len(self.items)

    def columnCount(self, parent):
        return 1

    def getValue(self,
                 row):
        return self.items[row]

    def getTargetDropIndex(self,
                           input_row,
                           parent):
        swap_row = int(input_row)
        if isinstance(parent.data, 
                      QtCore.QObject):
            swap_row = parent.row()

        if swap_row > len(self.items)-1:
            swap_row = len(self.items)-1

        if swap_row < 0:
            swap_row = parent.row()

        return swap_row

    def data(self, 
             index, 
             role=QtCore.Qt.DisplayRole):
        if not index.isValid():
            return None

        if role == QtCore.Qt.DisplayRole:
            return self.items[index.row()].display()

        return None

    def setData(self, 
                index, 
                value, 
                role=QtCore.Qt.EditRole):
        if role != QtCore.Qt.EditRole:
            return False

        if not value.strip():
            return False

        self.items[index.row()].rename(value)
        self.dataChanged.emit(index, 
                              index)

        return True

    def supportedDropActions(self):
        return QtCore.Qt.MoveAction

    def flags(self, index):
        return QtCore.Qt.ItemIsSelectable |  \
               QtCore.Qt.ItemIsDragEnabled | \
               QtCore.Qt.ItemIsDropEnabled | \
               QtCore.Qt.ItemIsEditable | \
               QtCore.Qt.ItemIsEnabled

    def dropMimeData(self, 
                     data, 
                     action, 
                     row, 
                     column, 
                     parent):
        is_valid_drop_data = super(BasicDragDropModel,
                                   self).dropMimeData(data, 
                                                      action, 
                                                      row, 
                                                      column, 
                                                      parent)

        if data.formats() != self.TARGET_TYPE:
            return False

        target_drop_index = self.getTargetDropIndex(row,
                                                    parent)

        source_component = data.item_data

        target_component = self.getValue(target_drop_index)
        
        if source_component == target_component:
            return False

        self.items[target_drop_index] = source_component

        self.items[data.item_index_value] = target_component

        self.items[target_drop_index] = source_component

        self.items[data.item_index_value] = target_component

        self.dataChanged.emit(QtCore.QModelIndex(), 
                              QtCore.QModelIndex())

        return True

    def mimeData(self, 
                 indexes):
        return BasicDragDropData(self.items[indexes[0].row()],
                                 indexes[0].row())

    def mimeTypes(self):
        return self.TARGET_TYPE
