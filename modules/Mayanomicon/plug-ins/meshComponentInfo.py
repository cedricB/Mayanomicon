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


class PropertySettings(object):
    DEFAULT_FLOAT_VALUE = 0.0

    DEFAULT_INDEX_VALUE = 0

    ATTRIBUTE_NON_KEYABLE_STATUS = False

    ATTRIBUTE_HIDDEN_STATUS = True

    ATTRIBUTE_NON_STORABLE_STATUS = False

    ATTRIBUTE_EXPOSED_STATUS = True

    HIDE_MATRIX_ATTRIBUTES = True


class meshComponentInfo(OpenMayaMPx.MPxNode):
    API_VERSION = "Any"
    PLUGIN_NODE_NAME = "meshComponentInfo"
    PLUGIN_NODE_ID = OpenMaya.MTypeId(0xBB99747)

    PLUGIN_VERSION = "0.0.1"
    AUTHOR = "cedric_bazillou_2018"

    REGISTER_FAILLURE = "Plugin Registration Faillure:\t\n{NAME} will not be loaded"
    
    REGISTER_FAILLURE_MESSAGE = REGISTER_FAILLURE.format(NAME=PLUGIN_NODE_NAME)

    DEREGISTER_FAILLURE = "Plugin deregister Faillure:\t\n{NAME} was not unloaded properly"
    
    DEREGISTER_FAILLURE_MESSAGE = DEREGISTER_FAILLURE.format(NAME=PLUGIN_NODE_NAME)

    VERTEX_TYPE = 0

    EDGE_TYPE = 1

    FACE_TYPE = 2

    def __init__(self):
        OpenMayaMPx.MPxNode.__init__(self)

    def postConstructor(self):
        self.meshUtils = OpenMaya.MFnMesh()

        self.edgeUtils = None

        self.faceUtils = None

        self.pointValue = OpenMaya.MPoint()

        self.haveInputMeshConnected = False

    def connectionMade(self, 
                       currentNodePlug, 
                       otherNodePlug, 
                       asSource):
        if all([currentNodePlug == meshComponentInfo.input,
                currentNodePlug.isNull() is False]):
            self.haveInputMeshConnected = True

        return OpenMayaMPx.MPxNode.connectionMade(self, 
                                                  currentNodePlug, 
                                                  otherNodePlug, 
                                                  asSource)

    def connectionBroken(self, 
                         currentNodePlug, 
                         otherNodePlug, 
                         asSource):
        if currentNodePlug == meshComponentInfo.input:
            self.haveInputMeshConnected = False

            self.edgeUtils = None

            self.faceUtils = None

        return OpenMayaMPx.MPxNode.connectionBroken(self, 
                                                    currentNodePlug, 
                                                    otherNodePlug, 
                                                    asSource)

    def haveInputConnection(self,
                            inputObject):
        return not inputObject.isNull()

    def attachShape(self,
                    dataBlockInput):
        imputMeshObject = dataBlockInput.inputValue(self.input).asMesh()

        if not self.haveInputConnection(imputMeshObject):
            return False

        self.componentTypeValue = int(dataBlockInput.inputValue(self.componentType).asShort())

        self.meshUtils.setObject(imputMeshObject)
        
        self.edgeUtils = OpenMaya.MItMeshEdge(imputMeshObject)

        self.faceUtils = OpenMaya.MItMeshPolygon(imputMeshObject)

        return True

    def outputAttributeWasRequested(self,
                                    currentPlug):
        if currentPlug == self.output :
            return True
        
        return False

    def needUpdate(self, 
                   currentPlug,
                   dataBlockInput): 

        if not self.haveInputMeshConnected:
            return False

        if not self.outputAttributeWasRequested(currentPlug):
            return False

        if not self.attachShape(dataBlockInput):
            return False

        return True

    def getComponentIndex(self,
                          dataBlockInput):
        componentIndex = dataBlockInput.inputValue(self.componentIndex).asInt()

        if self.componentTypeValue == self.VERTEX_TYPE:
            if componentIndex > self.meshUtils.numVertices()-1:
                return self.meshUtils.numVertices()-1

        elif self.componentTypeValue == self.EDGE_TYPE:
            if componentIndex > self.meshUtils.numEdges()-1:
                return self.meshUtils.numEdges()-1

        elif self.componentTypeValue == self.FACE_TYPE:
            if componentIndex > self.meshUtils.numPolygons()-1:
                return self.meshUtils.numPolygons()-1
    
        return componentIndex

    def createIntPointer(self):
		previousIndexUtils = OpenMaya.MScriptUtil()
		previousIndexUtils.createFromInt(0)

		return previousIndexUtils.asIntPtr()

    def getFaceCenter(self,
                      componentIndex):
        self.faceUtils.setIndex(componentIndex, 
                                self.createIntPointer())

        self.pointValue = self.faceUtils.center(OpenMaya.MSpace.kWorld)

    def getVertexPosition(self,
                          componentIndex):
        self.meshUtils.getPoint(componentIndex, 
                                self.pointValue, 
                                OpenMaya.MSpace.kWorld)

    def getEdgeCenter(self,
                      componentIndex):
        self.edgeUtils.setIndex(componentIndex, 
                                self.createIntPointer())

        self.pointValue = self.edgeUtils.center(OpenMaya.MSpace.kWorld)

    def getPoint(self,
                 dataBlockInput):
        componentIndex = self.getComponentIndex(dataBlockInput)

        if self.componentTypeValue == self.VERTEX_TYPE:
            self.getVertexPosition(componentIndex)

        elif self.componentTypeValue == self.EDGE_TYPE:
            self.getEdgeCenter(componentIndex)

        elif self.componentTypeValue == self.FACE_TYPE:
            self.getFaceCenter(componentIndex)

    def writeOutput(self, 
                    dataBlockInput): 
        outputHandle = dataBlockInput.outputValue(self.output) 

        outputHandle.set3Double(self.pointValue.x,
                                self.pointValue.y,
                                self.pointValue.z)

        outputHandle.setClean()     

    def compute(self, 
                currentPlug, 
                dataBlockInput): 
        if not self.needUpdate(currentPlug, 
                               dataBlockInput):
            return

        self.getPoint(dataBlockInput)

        self.writeOutput(dataBlockInput)

    @staticmethod
    def _createNode():
        return OpenMayaMPx.asMPxPtr(meshComponentInfo())

    @staticmethod
    def _addComponentTypeAttribute():
        enumAttributeUtils = OpenMaya.MFnEnumAttribute()
        
        meshComponentInfo.componentType = enumAttributeUtils.create("componentType", 
                                                                    "componentType",  
                                                                    PropertySettings.DEFAULT_INDEX_VALUE)

        enumAttributeUtils.addField("vertex", 0)
        enumAttributeUtils.addField("edge", 1)
        enumAttributeUtils.addField("face", 2)

        enumAttributeUtils.setKeyable(True)

        meshComponentInfo.addAttribute(meshComponentInfo.componentType)

    @staticmethod
    def _addMeshInputAttribute():
        inputAttributeUtils = OpenMaya.MFnTypedAttribute()

        meshComponentInfo.input = inputAttributeUtils.create("input", 
                                                             "in", 
                                                             OpenMaya.MFnMeshData.kMesh)

        inputAttributeUtils.setStorable(PropertySettings.ATTRIBUTE_NON_STORABLE_STATUS)

        inputAttributeUtils.setKeyable(PropertySettings.ATTRIBUTE_NON_KEYABLE_STATUS)

        inputAttributeUtils.setHidden(PropertySettings.ATTRIBUTE_HIDDEN_STATUS)

        meshComponentInfo.addAttribute(meshComponentInfo.input)  

    @staticmethod
    def _addTransformAttributes(attributeName,
                                attributeShortName,
                                inputDefaultValue):
        numericAttributeUtils = OpenMaya.MFnNumericAttribute()

        unitAttributeUtils = OpenMaya.MFnUnitAttribute()

        inputMObjectX = unitAttributeUtils.create("{0}X".format(attributeName), 
                                                  "{0}x".format(attributeShortName), 
                                                  inputDefaultValue)

        inputMObjectY = unitAttributeUtils.create("{0}Y".format(attributeName), 
                                                  "{0}y".format(attributeShortName), 
                                                  inputDefaultValue)

        inputMObjectZ = unitAttributeUtils.create("{0}Z".format(attributeName), 
                                                  "{0}z".format(attributeShortName), 
                                                  inputDefaultValue)

        inputMObject = numericAttributeUtils.create(attributeName, 
                                                    attributeShortName,
                                                    inputMObjectX,
                                                    inputMObjectY,
                                                    inputMObjectZ)

        numericAttributeUtils.setStorable(PropertySettings.ATTRIBUTE_NON_STORABLE_STATUS)
        numericAttributeUtils.setKeyable(PropertySettings.ATTRIBUTE_NON_KEYABLE_STATUS)
        numericAttributeUtils.setHidden(PropertySettings.ATTRIBUTE_HIDDEN_STATUS)

        return inputMObject

    @staticmethod
    def _addOutputAttributes():
        defaultDistance = OpenMaya.MDistance(PropertySettings.DEFAULT_FLOAT_VALUE, 
                                             OpenMaya.MDistance.kCentimeters)

        meshComponentInfo.output = meshComponentInfo._addTransformAttributes("output",
                                                                             "out",
                                                                             defaultDistance)

        meshComponentInfo.addAttribute(meshComponentInfo.output) 

    @staticmethod
    def _addIndexAttribute():
        numericAttributeUtils = OpenMaya.MFnNumericAttribute()

        meshComponentInfo.componentIndex = numericAttributeUtils.create("componentIndex", 
                                                                        "idValue", 
                                                                        OpenMaya.MFnNumericData.kLong)

        numericAttributeUtils.setMin(0)

        numericAttributeUtils.setWritable(True)
        numericAttributeUtils.setStorable(True)
        numericAttributeUtils.setKeyable(True)
        numericAttributeUtils.setHidden(False)

        meshComponentInfo.addAttribute(meshComponentInfo.componentIndex) 

    @staticmethod
    def _addAttributes():
        meshComponentInfo._addComponentTypeAttribute()

        meshComponentInfo._addIndexAttribute()

        meshComponentInfo._addMeshInputAttribute()

        meshComponentInfo._addOutputAttributes()

        meshComponentInfo.attributeAffects(meshComponentInfo.componentType, 
                                           meshComponentInfo.output)

        meshComponentInfo.attributeAffects(meshComponentInfo.componentIndex, 
                                           meshComponentInfo.output)

        meshComponentInfo.attributeAffects(meshComponentInfo.input, 
                                           meshComponentInfo.output)


def initializePlugin(mobject):
    mplugin = OpenMayaMPx.MFnPlugin(mobject, 
                                    meshComponentInfo.AUTHOR, 
                                    meshComponentInfo.PLUGIN_VERSION,
                                    "Any")
    try:
        mplugin.registerNode(meshComponentInfo.PLUGIN_NODE_NAME, 
                             meshComponentInfo.PLUGIN_NODE_ID, 
                             meshComponentInfo._createNode, 
                             meshComponentInfo._addAttributes, 
                             OpenMayaMPx.MPxNode.kDependNode)

    except:
        raise Exception(meshComponentInfo.REGISTER_FAILLURE_MESSAGE)


def uninitializePlugin(mobject):
    mplugin = OpenMayaMPx.MFnPlugin(mobject)

    try:
        mplugin.deregisterNode(meshComponentInfo.PLUGIN_NODE_ID)

    except:
        raise Exception(meshComponentInfo.DEREGISTER_FAILLURE_MESSAGE)


