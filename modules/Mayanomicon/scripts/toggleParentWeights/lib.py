"""
    MIT License

    L I C E N S E:
        Copyright (c) 2018 Cedric BAZILLOU All rights reserved.
        Email: cedricbazillou@gmail.com     
        blog: http://circecharacterworks.wordpress.com/  

    Permission is hereby granted, free of charge, to any person obtaining a copy of this software 
    and associated documentation files (the "Software"), to deal in the Software without restriction,
    including without limitation the rights to use, copy, modify, merge, publish, distribute,
    sublicense, and/or sell copies of the Software,and to permit persons to whom the Software 
    is furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in all copies 
    or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, 
    INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, 
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT 
    HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, 
    TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
    DEALINGS IN THE SOFTWARE.

    https://opensource.org/licenses/MIT
"""

import maya.cmds
import maya.OpenMaya as OpenMaya


class TargetData(object):
    PROPERTY = '{}.target[{}].targetWeight'

    def __init__(self,
                 connection_index,
                 constraint):
        self.constraint = constraint

        self.connection_index = connection_index

        target_property = self.PROPERTY.format(constraint, 
                                               connection_index)

        attribute = maya.cmds.listConnections(target_property,
                                              shapes=True,
                                              plugs=True)[0]

        self.attribute = attribute.split('.')[-1]

    def getConnectionPlug(self):
        return '{}.{}'.format(self.constraint,
                              self.attribute)

    def rename(self,
               attribute):
        attribute = str(attribute).strip().replace(' ', '_')

        maya.cmds.renameAttr(self.getConnectionPlug(),
                             attribute)

        self.attribute = attribute

    def connect(self,
                toggleNode,
                index):
        maya.cmds.connectAttr('{}.output[{}]'.format(toggleNode,
                                                     index),
                              self.getConnectionPlug(),
                              force=True)

    def display(self):
        return self.attribute


class Builder(object):
    PLUGIN_NAME = 'toggleParentWeights'
    
    ENUM_PROPERTY = 'space'

    def __init__(self):
        self.inputConstraint = None

        self.hubNode = None

    def isLoaded(self):
        return maya.cmds.pluginInfo(self.PLUGIN_NAME, 
                                    query=True, 
                                    loaded=True)

    def initialize(self):
        maya.cmds.loadPlugin(self.PLUGIN_NAME)

    def getDrivenNode(self):
        for item in [maya.cmds.listConnections('{}.constraintRotate'.format(self.inputConstraint),
                                               destination=True),
                     maya.cmds.listConnections('{}.constraintRotateX'.format(self.inputConstraint),
                                               destination=True)]:
            if item:
                return item[0]

        return None

    def attach(self,
               inputTargetDataArray):
        if not self.isLoaded():
            self.initialize()

        if not inputTargetDataArray:
            return

        self.inputConstraint = inputTargetDataArray[0].constraint
        
        if not maya.cmds.objExists(self.inputConstraint):
            OpenMaya.MGlobal.displayError('{} does not exists\nPlease refesh your tool'.format(self.inputConstraint))

        self.drivenTransform = self.getDrivenNode()

        if not all([self.inputConstraint,
                    self.drivenTransform]):
            OpenMaya.MGlobal.displayError('Please provide a pConstraint and transform node')

            return

        self.hubNode = maya.cmds.createNode(self.PLUGIN_NAME,
                                            n='{}_toggle1'.format(self.drivenTransform))

        maya.cmds.setAttr('{}.outputCount'.format(self.hubNode),
                          len(inputTargetDataArray))

        space_labels = [item.attribute
                        for item in inputTargetDataArray]

        maya.cmds.addAttr(self.drivenTransform,
                          ln=self.ENUM_PROPERTY,
                          sn=self.ENUM_PROPERTY,
                          at='enum',
                          enumName=":".join(space_labels),
                          k=True)

        maya.cmds.connectAttr('{}.{}'.format(self.drivenTransform,
                                             self.ENUM_PROPERTY),
                              '{}.activeIndex'.format(self.hubNode),
                              force=True)

        for index,item in enumerate(inputTargetDataArray):
            item.connect(self.hubNode, index)

    def collectParentTargets(self,
                             intputConstraint):
        index_array = maya.cmds.getAttr('{}.target'.format(intputConstraint), mi=True)
        
        return [TargetData(item,
                           intputConstraint)
                for item in index_array]
