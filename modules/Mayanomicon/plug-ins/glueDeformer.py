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

import math 
import maya.OpenMaya as OpenMaya
import maya.OpenMayaMPx as OpenMayaMPx
import maya.OpenMayaAnim as OpenMayaAnim

import pluginCore
import maya.cmds


class glueDeformer(OpenMayaMPx.MPxDeformerNode):
    API_VERSION = "Any"
    PLUGIN_NODE_NAME = "glueDeformer"
    PLUGIN_NODE_ID = OpenMaya.MTypeId(0xAA22797)

    PLUGIN_VERSION = "0.0.1"
    AUTHOR = "cedric_bazillou_2018"

    REGISTER_FAILLURE = "Plugin Registration Faillure:\t\n{NAME} will not be loaded"
    
    REGISTER_FAILLURE_MESSAGE = REGISTER_FAILLURE.format(NAME=PLUGIN_NODE_NAME)

    DEREGISTER_FAILLURE = "Plugin deregister Faillure:\t\n{NAME} was not unloaded properly"
    
    DEREGISTER_FAILLURE_MESSAGE = DEREGISTER_FAILLURE.format(NAME=PLUGIN_NODE_NAME)

    def __init__(self):
        OpenMayaMPx.MPxDeformerNode.__init__(self)

    def postConstructor(self):
        self.haveInputShapeConnected = False

        self.pointArrayUtils = OpenMaya.MFnVectorArrayData() 

        self.pointArrayValue = OpenMaya.MVectorArray()

    def connectionMade(self, 
                       currentNodePlug, 
                       otherNodePlug, 
                       asSource):
        if all([currentNodePlug == glueDeformer.bindMesh,
                currentNodePlug.isNull() is False]):
            self.haveInputShapeConnected = True

        return OpenMayaMPx.MPxNode.connectionMade(self, 
                                                  currentNodePlug, 
                                                  otherNodePlug, 
                                                  asSource)

    def connectionBroken(self, 
                         currentNodePlug, 
                         otherNodePlug, 
                         asSource):
        if currentNodePlug == glueDeformer.bindMesh:
            self.haveInputShapeConnected = False

        return OpenMayaMPx.MPxNode.connectionBroken(self, 
                                                    currentNodePlug, 
                                                    otherNodePlug, 
                                                    asSource)

    def haveInputConnection(self,
                            inputObject):
        return not inputObject.isNull()

    def hasPointData(self, 
                     dataBlockInput):
        pointMObject = dataBlockInput.inputValue(self.indexMapping).data()

        if not self.haveInputConnection(pointMObject):
            return False

        self.pointArrayUtils.setObject(pointMObject)

        if self.pointArrayUtils.length() == 0:
            return False

        self.pointArrayValue = self.pointArrayUtils.array()
        return True

    def deform(self,
               dataBlockInput,
               geometryIterator,
               wolrdMatrix,
               multiIndex):
        if not self.haveInputShapeConnected:
            return False

        if not self.hasPointData(dataBlockInput):
            return

        vertexPositions = OpenMaya.MPointArray()
        geometryIterator.allPositions(vertexPositions, 
                                      OpenMaya.MSpace.kObject)

        bindMeshUtils = OpenMaya.MFnMesh(dataBlockInput.inputValue(self.bindMesh).asMesh())  
        bindPoints = OpenMaya.MPointArray()
        bindMeshUtils.getPoints(bindPoints,
                                OpenMaya.MSpace.kObject)

        worldMatrix = dataBlockInput.inputValue(self.bindMesh).geometryTransformMatrix()

        for index in xrange(self.pointArrayValue.length()):
            currentMap = self.pointArrayValue[index]

            vertexPositions.set(bindPoints[int(currentMap.y)]*worldMatrix,
                                int(currentMap.x))

        geometryIterator.setAllPositions(vertexPositions, 
                                         OpenMaya.MSpace.kObject)

    @staticmethod
    def _createNode():
        return OpenMayaMPx.asMPxPtr(glueDeformer())
        
    @staticmethod
    def _addShapeAttribute():
        typedAttributeUtils = OpenMaya.MFnTypedAttribute()

        glueDeformer.bindMesh = typedAttributeUtils.create("bindMesh", 
                                                           "inMsh", 
                                                           OpenMaya.MFnData.kMesh)

        typedAttributeUtils.setHidden(pluginCore.PropertySettings.ATTRIBUTE_HIDDEN_STATUS)

        typedAttributeUtils.setStorable(pluginCore.PropertySettings.ATTRIBUTE_NON_STORABLE_STATUS)

        typedAttributeUtils.setDisconnectBehavior(OpenMaya.MFnAttribute.kNothing)

        glueDeformer.addAttribute(glueDeformer.bindMesh)

    @staticmethod
    def _addMappinAttribute():
        outputAttributeUtils = OpenMaya.MFnTypedAttribute()

        glueDeformer.indexMapping = outputAttributeUtils.create("indexMapping", 
                                                                "in", 
                                                                 OpenMaya.MFnData.kVectorArray)

        outputAttributeUtils.setHidden(pluginCore.PropertySettings.ATTRIBUTE_HIDDEN_STATUS)

        outputAttributeUtils.setStorable(pluginCore.PropertySettings.ATTRIBUTE_NON_STORABLE_STATUS)

        outputAttributeUtils.setDisconnectBehavior(OpenMaya.MFnAttribute.kNothing)

        glueDeformer.addAttribute(glueDeformer.indexMapping)

    @staticmethod
    def _getOutputAttribute():
        apiVersion = maya.cmds.about(apiVersion=True)
        if apiVersion < 201600:
            return OpenMayaMPx.cvar.MPxDeformerNode_outputGeom

        return OpenMayaMPx.cvar.MPxGeometryFilter_outputGeom

    @staticmethod
    def _addAttributes():
        numericAttributeUtils = OpenMaya.MFnNumericAttribute()

        glueDeformer._addShapeAttribute()

        glueDeformer._addMappinAttribute()

        outputGeometry = glueDeformer._getOutputAttribute()

        glueDeformer.attributeAffects(glueDeformer.bindMesh, 
                                      outputGeometry)

        glueDeformer.attributeAffects(glueDeformer.indexMapping, 
                                      outputGeometry)


def initializePlugin(mobject):
    mplugin = OpenMayaMPx.MFnPlugin(mobject, 
                                    glueDeformer.AUTHOR, 
                                    glueDeformer.PLUGIN_VERSION,
                                    "Any")

    try:
        mplugin.registerNode(glueDeformer.PLUGIN_NODE_NAME, 
                             glueDeformer.PLUGIN_NODE_ID, 
                             glueDeformer._createNode, 
                             glueDeformer._addAttributes, 
                             OpenMayaMPx.MPxNode.kDeformerNode)

    except:
        raise Exception(glueDeformer.REGISTER_FAILLURE_MESSAGE)


def uninitializePlugin(mobject):
    mplugin = OpenMayaMPx.MFnPlugin(mobject)

    try:
        mplugin.deregisterNode(glueDeformer.PLUGIN_NODE_ID)

    except:
        raise Exception(glueDeformer.DEREGISTER_FAILLURE_MESSAGE)
