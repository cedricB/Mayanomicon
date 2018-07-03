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


class PointData(object):
    def __init__(self):
        self.wolrdMatrix = OpenMaya.MMatrix()

        self.shapeUtils = None

        self.pointArray = OpenMaya.MVectorArray()

        self.inputObject = OpenMaya.MObject.kNullObj

        self.pointCount = 0

        self.sDivivision = 0

        self.tDivivision = 0

        self.uDivivision = 0

        self.unpackUtils = {OpenMaya.MFnData.kMesh:self.unpackMesh,
                            OpenMaya.MFnData.kNurbsCurve:self.unpackCurve,
                            OpenMaya.MFnData.kNurbsSurface:self.unpackSurface,
                            OpenMaya.MFnData.kLattice:self.unpackLattice}

    def collectFFdSettings(self,
                           shapeFunctionUtils):
        sDivivisionParam = maya.OpenMaya.MScriptUtil()
        sDivivisionParam.createFromInt(0)    
        sDivivisionPtr = sDivivisionParam.asUintPtr()    

        tDivivisionParam = maya.OpenMaya.MScriptUtil()
        tDivivisionParam.createFromInt(0)    
        tDivivisionPtr = tDivivisionParam.asUintPtr()  

        uDivivisionParam = maya.OpenMaya.MScriptUtil()
        uDivivisionParam.createFromInt(0)    
        uDivivisionPtr = uDivivisionParam.asUintPtr()  

        shapeFunctionUtils.getDivisions(sDivivisionPtr,
                                        tDivivisionPtr,
                                        uDivivisionPtr)

        self.sDivivision = maya.OpenMaya.MScriptUtil(sDivivisionPtr).asInt()
        self.tDivivision = maya.OpenMaya.MScriptUtil(tDivivisionPtr).asInt()
        self.uDivivision = maya.OpenMaya.MScriptUtil(uDivivisionPtr).asInt()

        self.pointCount = sDivivision * tDivivision * uDivivision

        self.sliceLength = sDivivision * tDivivision

        self.rowLength = sDivivision

    def convertFFdIndex(self,
                        sIndex,
                        tIndex,
                        uIndex):
        self.pointCount = sIndex + (tIndex * self.rowLength) * (uIndex * self.sliceLength)

    def collectFFdPoints(self):
        pointArray = OpenMaya.MPointArray()
        pointArray.setLength(self.pointCount)

        for sIndex in range(self.sDivivision):
            for tIndex in range(self.tDivivision):
                for uIndex in range(self.uDivivision):
                    writeIndex = self.convertFFdIndex(self,
                                                      sIndex,
                                                      tIndex,
                                                      uIndex)

                    pointArray.set(OpenMaya.MVector(self.shapeUtils.point(sIndex,
                                                                          tIndex,
                                                                          uIndex)*self.wolrdMatrix),
                                   writeIndex)

        return pointArray

    def writeArray(self,
                   pointArray):
        self.pointArray.setLength(pointArray.length())
        for pointIndex in xrange(pointArray.length()):
            self.pointArray.set(OpenMaya.MVector(pointArray[pointIndex] * self.wolrdMatrix), 
                                pointIndex)

    def unpackMesh(self,
                   inputHandle):
        self.inputObject = inputHandle.asMeshTransformed()

        self.shapeUtils = OpenMaya.MFnMesh(self.inputObject)

        pointArray = OpenMaya.MPointArray()

        self.shapeUtils.getPoints(pointArray)

        self.writeArray(pointArray)

    def unpackCurve(self,
                    inputHandle):
        self.inputObject = inputHandle.asNurbsCurveTransformed()

        self.shapeUtils = OpenMaya.MFnNurbsCurve(self.inputObject)

        pointArray = OpenMaya.MPointArray()
        self.shapeUtils.getCVs(pointArray)

        self.writeArray(pointArray)

    def unpackSurface(self,
                      inputHandle):
        self.inputObject = inputHandle.asNurbsSurfaceTransformed()

        self.shapeUtils = OpenMaya.MFnNurbsSurface(self.inputObject)

        pointArray = OpenMaya.MPointArray()
        self.shapeUtils.getCVs(pointArray)

        self.writeArray(pointArray)

    def unpackLattice(self,
                      inputHandle):
        self.inputObject = inputHandle.data()	

        self.shapeUtils = OpenMayaAnim.MFnLattice(self.inputObject)

        self.collectFfdSettings(self.shapeUtils)

        pointArray = self.collectFFdPoints()

        self.writeArray(pointArray)

    def collect(self,
                inputHandle,
                wolrdMatrix):
        self.wolrdMatrix = wolrdMatrix

        self.unpackUtils[inputHandle.type()](inputHandle)


class shapeToPointArray(OpenMayaMPx.MPxNode):
    API_VERSION = "Any"
    PLUGIN_NODE_NAME = "shapeToPointArray"
    PLUGIN_NODE_ID = OpenMaya.MTypeId(0xAA88747)

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

        self.pointUtils = PointData()

    def connectionMade(self, 
                       currentNodePlug, 
                       otherNodePlug, 
                       asSource):
        if all([currentNodePlug == shapeToPointArray.input,
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
        if currentNodePlug == shapeToPointArray.input:
            self.haveInputShapeConnected = False

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
        self.pointUtils.collect(dataBlockInput.inputValue(self.input),
                                dataBlockInput.inputValue(self.matrix).asMatrix())

        if not self.haveInputConnection(self.pointUtils.inputObject):
            return False

        return True

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

        if not self.attachShape(dataBlockInput):
            return False

        return True

    def writeOutput(self, 
                    dataBlockInput): 
        pointArrayUtils = OpenMaya.MFnVectorArrayData() 

        outputData = pointArrayUtils.create(self.pointUtils.pointArray)

        outputHandle = dataBlockInput.outputValue(self.output)

        outputHandle.setMObject(outputData)

        outputHandle.setClean()     

    def compute(self, 
                currentPlug, 
                dataBlockInput): 
        if not self.needUpdate(currentPlug, 
                               dataBlockInput):
            return

        self.writeOutput(dataBlockInput)

    @staticmethod
    def _createNode():
        return OpenMayaMPx.asMPxPtr(shapeToPointArray())

    @staticmethod
    def _addShapeAttribute():
        genericUtils = OpenMaya.MFnGenericAttribute()

        shapeToPointArray.input = genericUtils.create("input", 
                                                      "input")

        genericUtils.setHidden(pluginCore.PropertySettings.ATTRIBUTE_HIDDEN_STATUS)
        genericUtils.addDataAccept(OpenMaya.MFnData.kMesh)
        genericUtils.addDataAccept(OpenMaya.MFnData.kLattice)
        genericUtils.addDataAccept(OpenMaya.MFnData.kNurbsCurve)
        genericUtils.addDataAccept(OpenMaya.MFnData.kNurbsSurface)
  
        shapeToPointArray.addAttribute(shapeToPointArray.input)

    @staticmethod
    def _addMatrixAttribute():
        matrixAttributeUtils = OpenMaya.MFnMatrixAttribute()

        shapeToPointArray.matrix = matrixAttributeUtils.create("matrix", 
                                                               "mtx", 
                                                               OpenMaya.MFnMatrixAttribute.kDouble)

        matrixAttributeUtils.setHidden(pluginCore.PropertySettings.ATTRIBUTE_HIDDEN_STATUS)

        matrixAttributeUtils.setStorable(pluginCore.PropertySettings.ATTRIBUTE_NON_STORABLE_STATUS)

        matrixAttributeUtils.setDisconnectBehavior(OpenMaya.MFnAttribute.kNothing)

        shapeToPointArray.addAttribute(shapeToPointArray.matrix)
        
    @staticmethod
    def _addOutputAttribute():
        outputAttributeUtils = OpenMaya.MFnTypedAttribute()

        shapeToPointArray.output = outputAttributeUtils.create("output", 
                                                               "out", 
                                                               OpenMaya.MFnData.kVectorArray)

        outputAttributeUtils.setHidden(pluginCore.PropertySettings.ATTRIBUTE_HIDDEN_STATUS)

        outputAttributeUtils.setStorable(pluginCore.PropertySettings.ATTRIBUTE_NON_STORABLE_STATUS)

        outputAttributeUtils.setDisconnectBehavior(OpenMaya.MFnAttribute.kNothing)

        shapeToPointArray.addAttribute(shapeToPointArray.output)

    @staticmethod
    def _addAttributes():
        numericAttributeUtils = OpenMaya.MFnNumericAttribute()

        shapeToPointArray._addShapeAttribute()

        shapeToPointArray._addMatrixAttribute()

        shapeToPointArray._addOutputAttribute()

        shapeToPointArray.attributeAffects(shapeToPointArray.matrix, 
                                           shapeToPointArray.output)

        shapeToPointArray.attributeAffects(shapeToPointArray.input, 
                                           shapeToPointArray.output)


def initializePlugin(mobject):
    mplugin = OpenMayaMPx.MFnPlugin(mobject, 
                                    shapeToPointArray.AUTHOR, 
                                    shapeToPointArray.PLUGIN_VERSION,
                                    "Any")
    try:
        mplugin.registerNode(shapeToPointArray.PLUGIN_NODE_NAME, 
                             shapeToPointArray.PLUGIN_NODE_ID, 
                             shapeToPointArray._createNode, 
                             shapeToPointArray._addAttributes, 
                             OpenMayaMPx.MPxNode.kDependNode)

    except:
        raise Exception(shapeToPointArray.REGISTER_FAILLURE_MESSAGE)


def uninitializePlugin(mobject):
    mplugin = OpenMayaMPx.MFnPlugin(mobject)

    try:
        mplugin.deregisterNode(shapeToPointArray.PLUGIN_NODE_ID)

    except:
        raise Exception(shapeToPointArray.DEREGISTER_FAILLURE_MESSAGE)
