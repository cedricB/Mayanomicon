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


class BarycentricCoordinates(object):
    WEIGHTS_DATA = ('vertex1Weight',
                    'vertex2Weight',
                    'vertex3Weight')

    def __init__(self):
        self.vertex1Weight = 0.0

        self.vertex2Weight = 0.0

        self.vertex3Weight = 0.0

        self.vertex1Util = OpenMaya.MScriptUtil()
        self.vertex1Util.createFromInt(0)

        self.vertex2Util = OpenMaya.MScriptUtil()
        self.vertex2Util.createFromInt(0)

        self.vertex1Pointer = self.vertex1Util.asFloatPtr()    
        self.vertex2Pointer = self.vertex2Util.asFloatPtr()   

        self.previousIdUtil = OpenMaya.MScriptUtil()
        self.previousIdUtil.createFromInt(0)
        self.previousIdUtilPtr = self.previousIdUtil.asIntPtr()

        self.facePoints = OpenMaya.MPointArray()
        self.vertexIndexArray = OpenMaya.MIntArray()

    def getWeight(self,
                  index):
        return getattr(self,
                       self.WEIGHTS_DATA[index])
  
    def collect(self):  
        self.vertex1Weight = self.vertex1Util.getFloat(self.vertex1Pointer)

        self.vertex2Weight = self.vertex1Util.getFloat(self.vertex2Pointer)

        self.vertex3Weight = 1.0 - self.vertex1Weight - self.vertex2Weight

        currentPointIndex = 0
        currentWeight = -100.0

        for index in range(3):
            if self.getWeight(index) > currentWeight:
                currentPointIndex = index
                currentWeight = float(self.getWeight(index))

        self.closestPointIndex = self.vertexIndexArray[currentPointIndex]


class PointOnTriangle(object):
    def __init__(self):
        self.meshIntersector = OpenMaya.MMeshIntersector()

        self.faceIterator = None 

        self.meshPoint = OpenMaya.MPointOnMesh()

        self.closestPnt = OpenMaya.MFloatPoint()

        self.weightUtils = BarycentricCoordinates()

    def collectFromPoint(self,
                         inputPoint):
        sourcePoint = OpenMaya.MPoint(inputPoint.x,
                                      inputPoint.y,
                                      inputPoint.z)

        self.meshIntersector.getClosestPoint(sourcePoint,  
                                             self.meshPoint, 
                                             50.0)    

        self.closestPnt = self.meshPoint.getPoint()
  
        self.meshPoint.getBarycentricCoords(self.weightUtils.vertex1Pointer, 
                                            self.weightUtils.vertex2Pointer)

        self.weightUtils.faceIndex = self.meshPoint.faceIndex()
        self.weightUtils.triangleIndex = self.meshPoint.triangleIndex()
        
        self.faceIterator.setIndex(self.weightUtils.faceIndex, 
                                   self.weightUtils.previousIdUtilPtr)

        self.faceIterator.getTriangle(self.weightUtils.triangleIndex, 
                                      self.weightUtils.facePoints,   
                                      self.weightUtils.vertexIndexArray, 
                                      OpenMaya.MSpace.kObject) 

        self.weightUtils.collect()


class gluePointMapping(OpenMayaMPx.MPxNode):
    API_VERSION = "Any"
    PLUGIN_NODE_NAME = "gluePointMapping"
    PLUGIN_NODE_ID = OpenMaya.MTypeId(0xAA55797)

    PLUGIN_VERSION = "0.0.1"
    AUTHOR = "cedric_bazillou_2018"

    REGISTER_FAILLURE = "Plugin Registration Faillure:\t\n{NAME} will not be loaded"
    
    REGISTER_FAILLURE_MESSAGE = REGISTER_FAILLURE.format(NAME=PLUGIN_NODE_NAME)

    DEREGISTER_FAILLURE = "Plugin deregister Faillure:\t\n{NAME} was not unloaded properly"
    
    DEREGISTER_FAILLURE_MESSAGE = DEREGISTER_FAILLURE.format(NAME=PLUGIN_NODE_NAME)

    def __init__(self):
        OpenMayaMPx.MPxNode.__init__(self)

    def postConstructor(self):
        self.haveInputShapeConnected = False

        self.pointArrayUtils = OpenMaya.MFnVectorArrayData() 

        self.pointArrayValue = OpenMaya.MVectorArray()

        self.mappingArray = OpenMaya.MVectorArray()

        self.triangleUtils = PointOnTriangle()

    def connectionMade(self, 
                       currentNodePlug, 
                       otherNodePlug, 
                       asSource):
        if all([currentNodePlug == gluePointMapping.inputMesh,
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
        if currentNodePlug == gluePointMapping.inputMesh:
            self.haveInputShapeConnected = False

        return OpenMayaMPx.MPxNode.connectionBroken(self, 
                                                    currentNodePlug, 
                                                    otherNodePlug, 
                                                    asSource)

    def haveInputConnection(self,
                            inputObject):
        return not inputObject.isNull()

    def outputAttributeWasRequested(self,
                                    currentPlug):
        if currentPlug == self.output :
            return True
        
        return False

    def needUpdate(self, 
                   currentPlug,
                   dataBlockInput):
        if not self.haveInputShapeConnected:
            return False

        if not self.outputAttributeWasRequested(currentPlug):
            return False

        inputMeshData = dataBlockInput.inputValue(self.inputMesh).asMesh()
        if not self.haveInputConnection(inputMeshData):
            return False

        self.triangleUtils.meshIntersector.create(inputMeshData,
                                                  dataBlockInput.inputValue(self.inputMesh).geometryTransformMatrix())

        if not self.triangleUtils.meshIntersector.isCreated():
            return False

        self.triangleUtils.faceIterator = OpenMaya.MItMeshPolygon(inputMeshData)  

        return True

    def hasPointData(self, 
                     dataBlockInput):
        pointMObject = dataBlockInput.inputValue(self.points).data()

        if not self.haveInputConnection(pointMObject):
            return False

        self.pointArrayUtils.setObject(pointMObject)

        if self.pointArrayUtils.length() == 0:
            return False

        self.pointArrayValue =	self.pointArrayUtils.array()

        self.mappingArray.setLength(self.pointArrayValue.length())

        return True

    def collectClosestPoints(self):
        for pointIndex in xrange(self.pointArrayValue.length()):
            self.triangleUtils.collectFromPoint(self.pointArrayValue[pointIndex])

            outputValue = OpenMaya.MVector(pointIndex,
                                           self.triangleUtils.weightUtils.closestPointIndex,
                                           -1.0)

            self.mappingArray.set(outputValue, 
                                  pointIndex)

    def writeOutput(self, 
                    dataBlockInput): 
        pointArrayUtils = OpenMaya.MFnVectorArrayData() 

        outputData = pointArrayUtils.create(self.mappingArray)

        outputHandle = dataBlockInput.outputValue(self.output)

        outputHandle.setMObject(outputData)

        outputHandle.setClean()     

    def compute(self, 
                currentPlug, 
                dataBlockInput): 
        if not self.needUpdate(currentPlug, 
                               dataBlockInput):
            return

        if not self.hasPointData(dataBlockInput):
            return

        self.collectClosestPoints()

        self.writeOutput(dataBlockInput)

    @staticmethod
    def _createNode():
        return OpenMayaMPx.asMPxPtr(gluePointMapping())
        
    @staticmethod
    def _addShapeAttribute():
        typedAttributeUtils = OpenMaya.MFnTypedAttribute()

        gluePointMapping.inputMesh = typedAttributeUtils.create("inputMesh", 
                                                                "inMsh", 
                                                                OpenMaya.MFnData.kMesh)

        typedAttributeUtils.setHidden(pluginCore.PropertySettings.ATTRIBUTE_HIDDEN_STATUS)

        typedAttributeUtils.setStorable(pluginCore.PropertySettings.ATTRIBUTE_NON_STORABLE_STATUS)

        typedAttributeUtils.setDisconnectBehavior(OpenMaya.MFnAttribute.kNothing)

        gluePointMapping.addAttribute(gluePointMapping.inputMesh)

    @staticmethod
    def _addPointAttribute():
        outputAttributeUtils = OpenMaya.MFnTypedAttribute()

        gluePointMapping.points = outputAttributeUtils.create("points", 
                                                              "pts", 
                                                              OpenMaya.MFnData.kVectorArray)

        outputAttributeUtils.setHidden(pluginCore.PropertySettings.ATTRIBUTE_HIDDEN_STATUS)

        outputAttributeUtils.setStorable(pluginCore.PropertySettings.ATTRIBUTE_STORABLE_STATUS)

        outputAttributeUtils.setDisconnectBehavior(OpenMaya.MFnAttribute.kNothing)

        gluePointMapping.addAttribute(gluePointMapping.points)

    @staticmethod
    def _addOutputAttribute():
        outputAttributeUtils = OpenMaya.MFnTypedAttribute()

        gluePointMapping.output = outputAttributeUtils.create("output", 
                                                              "out", 
                                                              OpenMaya.MFnData.kVectorArray)

        outputAttributeUtils.setHidden(pluginCore.PropertySettings.ATTRIBUTE_HIDDEN_STATUS)

        outputAttributeUtils.setStorable(pluginCore.PropertySettings.ATTRIBUTE_NON_STORABLE_STATUS)

        outputAttributeUtils.setDisconnectBehavior(OpenMaya.MFnAttribute.kNothing)

        gluePointMapping.addAttribute(gluePointMapping.output)

    @staticmethod
    def _addAttributes():
        numericAttributeUtils = OpenMaya.MFnNumericAttribute()

        gluePointMapping._addShapeAttribute()

        gluePointMapping._addPointAttribute()

        gluePointMapping._addOutputAttribute()

        gluePointMapping.attributeAffects(gluePointMapping.inputMesh, 
                                           gluePointMapping.output)

        gluePointMapping.attributeAffects(gluePointMapping.points, 
                                          gluePointMapping.output)


def initializePlugin(mobject):
    mplugin = OpenMayaMPx.MFnPlugin(mobject, 
                                    gluePointMapping.AUTHOR, 
                                    gluePointMapping.PLUGIN_VERSION,
                                    "Any")

    try:
        mplugin.registerNode(gluePointMapping.PLUGIN_NODE_NAME, 
                             gluePointMapping.PLUGIN_NODE_ID, 
                             gluePointMapping._createNode, 
                             gluePointMapping._addAttributes, 
                             OpenMayaMPx.MPxNode.kDependNode)

    except:
        raise Exception(gluePointMapping.REGISTER_FAILLURE_MESSAGE)


def uninitializePlugin(mobject):
    mplugin = OpenMayaMPx.MFnPlugin(mobject)

    try:
        mplugin.deregisterNode(gluePointMapping.PLUGIN_NODE_ID)

    except:
        raise Exception(gluePointMapping.DEREGISTER_FAILLURE_MESSAGE)
