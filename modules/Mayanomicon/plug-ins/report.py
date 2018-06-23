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

import math, sys
import maya.api.OpenMaya as OpenMaya
import maya.api.OpenMayaUI as OpenMayaUI
import maya.api.OpenMayaRender as OpenMayaRender

#Sadly Viewport2.0 needs new API
def maya_useNewAPI():
    pass


class PropertySettings(object):
    DEFAULT_FLOAT_VALUE = 0.0

    DEFAULT_INDEX_VALUE = 0

    ATTRIBUTE_NON_KEYABLE_STATUS = False

    ATTRIBUTE_HIDDEN_STATUS = True

    ATTRIBUTE_NON_HIDDEN_STATUS = False

    ATTRIBUTE_NON_STORABLE_STATUS = False

    ATTRIBUTE_IS_STORABLE_STATUS = False

    ATTRIBUTE_EXPOSED_STATUS = True

    HIDE_MATRIX_ATTRIBUTES = True

    DEFAULT_DISTANCE  = OpenMaya.MDistance(DEFAULT_FLOAT_VALUE, 
                                           OpenMaya.MDistance.kCentimeters)

    DEFAULT_ANGLE = OpenMaya.MAngle(DEFAULT_FLOAT_VALUE,
                                    OpenMaya.MAngle.kDegrees)


class report(OpenMaya.MPxNode):
    API_VERSION = "Any"
    PLUGIN_NODE_NAME = "report"
    PLUGIN_NODE_ID = OpenMaya.MTypeId(0x24BCD479)

    DRAW_CLASSIFICATION = "drawdb/geometry/reportLocator"

    DRAW_REGISTER = "reportLocatorPlugin"

    PLUGIN_VERSION = "0.0.1"
    AUTHOR = "cedric_bazillou_2018"

    REGISTER_FAILLURE = "Plugin Registration Faillure:\t\n{NAME} will not be loaded"
    
    REGISTER_FAILLURE_MESSAGE = REGISTER_FAILLURE.format(NAME=PLUGIN_NODE_NAME)

    DEREGISTER_FAILLURE = "Plugin deregister Faillure:\t\n{NAME} was not unloaded properly"

    DEREGISTER_FAILLURE_MESSAGE = DEREGISTER_FAILLURE.format(NAME=PLUGIN_NODE_NAME)

    LABEL_DISPLAY = '{LABEL}:\n\t{NUMBER:.3f}'

    VALUE_DISPLAY = '{:.3f}'

    LABEL_VECTOR_DISPLAY = '{LABEL}:\n\t{X:.3f} {Y:.3f} {Z:.3f}'

    VECTOR_DISPLAY = '{X:.3f} {Y:.3f} {Z:.3f}'

    IS_NUMERIC = 0

    IS_VECTOR = 1

    IS_ANGLES = 2

    def __init__(self):
        OpenMaya.MPxNode.__init__(self)

    def outputAttributeWasRequested(self,
                                    currentPlug):
        if currentPlug == self.output :
            return True
        
        return False

    def needUpdate(self, 
                   currentPlug,
                   dataBlockInput): 
        if not self.outputAttributeWasRequested(currentPlug):
            return False

        return True

    def writeOutput(self, 
                    dataBlockInput,
                    outputLabel): 
        outputHandle = dataBlockInput.outputValue(self.output) 

        outputHandle.setString(outputLabel)

        outputHandle.setClean()

    def buildVectorLabel(self,
                          inlabel,
                          dataBlockInput):
        inValues = dataBlockInput.inputValue(self.translate).asVector()

        if not inlabel.strip():
            return self.VECTOR_DISPLAY.format(X=inValues.x,
                                              Y=inValues.y,
                                              Z=inValues.z)

        outputLabel = self.LABEL_VECTOR_DISPLAY.format(LABEL=inlabel.strip(),
                                                       X=inValues.x,
                                                       Y=inValues.y,
                                                       Z=inValues.z)

        return outputLabel

    def buildAngleLabel(self,
                        inlabel,
                        dataBlockInput):
        inValues = dataBlockInput.inputValue(self.rotate).asDouble3()

        if not inlabel.strip():
            return self.VECTOR_DISPLAY.format(X=math.degrees(inValues[0]),
                                              Y=math.degrees(inValues[1]),
                                              Z=math.degrees(inValues[2]))

        outputLabel = self.LABEL_VECTOR_DISPLAY.format(LABEL=inlabel.strip(),
                                                       X=math.degrees(inValues[0]),
                                                       Y=math.degrees(inValues[1]),
                                                       Z=math.degrees(inValues[2]))

        return outputLabel

    def buildNumericLabel(self,
                          inlabel,
                          dataBlockInput):
        inDouble = dataBlockInput.inputValue(self.inputNumber).asDouble()

        if not inlabel.strip():
            return self.VALUE_DISPLAY.format(inDouble)

        outputLabel = self.LABEL_DISPLAY.format(LABEL=inlabel.strip(),
                                                NUMBER=inDouble)

        return outputLabel

    def prepareHudLabel(self,
                        dataBlockInput):
        inputTypeValue = int(dataBlockInput.inputValue(self.inputType).asShort())

        inlabel = dataBlockInput.inputValue(self.inputLabel).asString()

        if inputTypeValue == self.IS_NUMERIC:
            return self.buildNumericLabel(inlabel,
                                          dataBlockInput)

        elif inputTypeValue == self.IS_VECTOR:
            return self.buildVectorLabel(inlabel,
                                         dataBlockInput)

        else:
            return self.buildAngleLabel(inlabel,
                                        dataBlockInput)

        return outputLabel

    def compute(self, 
                currentPlug, 
                dataBlockInput): 
        if not self.needUpdate(currentPlug, 
                               dataBlockInput):
            return

        outputLabel = self.prepareHudLabel(dataBlockInput)

        self.writeOutput(dataBlockInput,
                         outputLabel)

    @staticmethod
    def _createNode():
        return report()

    @staticmethod
    def _addVectorAttributes(attributeName,
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

        numericAttributeUtils.storable = True
        numericAttributeUtils.keyable = True
        numericAttributeUtils.hidden = False

        return inputMObject

    @staticmethod
    def _addOutputAttributes():
        typedAttributeUtils = OpenMaya.MFnTypedAttribute()

        report.output = typedAttributeUtils.create("output", 
                                                   "out", 
                                                   OpenMaya.MFnData.kString)

        typedAttributeUtils.storable = PropertySettings.ATTRIBUTE_NON_STORABLE_STATUS
        typedAttributeUtils.keyable = PropertySettings.ATTRIBUTE_NON_KEYABLE_STATUS
        typedAttributeUtils.hidden = PropertySettings.ATTRIBUTE_HIDDEN_STATUS

        report.addAttribute(report.output)

    @staticmethod
    def _addToogleAttribute():
        enumerateAttribute =  OpenMaya.MFnEnumAttribute()
        report.inputType = enumerateAttribute.create("inputType", 
                                                     "itp", 
                                                     0 )

        enumerateAttribute.addField("number", 0)
        enumerateAttribute.addField("position", 1)
        enumerateAttribute.addField("rotation", 2)
        enumerateAttribute.storable = True
        enumerateAttribute.hidden = False
        enumerateAttribute.keyable = True

        report.addAttribute(report.inputType)

    @staticmethod
    def _addInputAttribute():
        inputAttributeUtils = OpenMaya.MFnTypedAttribute()

        report.inputLabel = inputAttributeUtils.create("inputLabel", 
                                                       "inLbl", 
                                                       OpenMaya.MFnData.kString)

        inputAttributeUtils.storable = PropertySettings.ATTRIBUTE_IS_STORABLE_STATUS
        inputAttributeUtils.keyable = PropertySettings.ATTRIBUTE_NON_KEYABLE_STATUS
        inputAttributeUtils.hidden = PropertySettings.ATTRIBUTE_NON_HIDDEN_STATUS

        report.addAttribute(report.inputLabel)

        report._addToogleAttribute()

        numericAttributeUtils = OpenMaya.MFnNumericAttribute()
        report.inputNumber = numericAttributeUtils.create("inputNumber",
                                                          "num", 
                                                          OpenMaya.MFnNumericData.kDouble)

        numericAttributeUtils.storable = True
        numericAttributeUtils.keyable = True
        numericAttributeUtils.hidden = False

        report.addAttribute(report.inputNumber)

        report.translate = report._addVectorAttributes("translate",
                                                       "t",
                                                       PropertySettings.DEFAULT_DISTANCE)

        report.addAttribute(report.translate)

        report.rotate = report._addVectorAttributes("rotate",
                                                    "r",
                                                    PropertySettings.DEFAULT_ANGLE)

        report.addAttribute(report.rotate)

    @staticmethod
    def _addAttributes():
        report._addInputAttribute()

        report._addOutputAttributes()

        report.attributeAffects(report.inputNumber, 
                                report.output)
                            
        report.attributeAffects(report.translate, 
                                report.output)

        report.attributeAffects(report.rotate, 
                                report.output)

        report.attributeAffects(report.inputType, 
                                report.output)

        report.attributeAffects(report.inputLabel, 
                                report.output)


class reportLocator(OpenMayaUI.MPxLocatorNode):
    API_VERSION = "Any"
    PLUGIN_NODE_NAME = "reportLocator"
    PLUGIN_NODE_ID = OpenMaya.MTypeId(0x24BCD379)

    PLUGIN_VERSION = "0.0.1"
    AUTHOR = "cedric_bazillou_2018"

    REGISTER_FAILLURE = "Locator Registration Faillure:\t\n{NAME} will not be loaded"
    
    REGISTER_FAILLURE_MESSAGE = REGISTER_FAILLURE.format(NAME=PLUGIN_NODE_NAME)

    DEREGISTER_FAILLURE = "Locator deregister Faillure:\t\n{NAME} was not unloaded properly"

    DEREGISTER_FAILLURE_MESSAGE = DEREGISTER_FAILLURE.format(NAME=PLUGIN_NODE_NAME)

    @staticmethod
    def _createNode():
        return reportLocator()

    @staticmethod
    def _addAttributes():
        inputAttributeUtils = OpenMaya.MFnTypedAttribute()

        reportLocator.text = inputAttributeUtils.create("text", 
                                                        "txt", 
                                                        OpenMaya.MFnData.kString)

        inputAttributeUtils.storable = PropertySettings.ATTRIBUTE_IS_STORABLE_STATUS
        inputAttributeUtils.keyable = PropertySettings.ATTRIBUTE_NON_KEYABLE_STATUS
        inputAttributeUtils.hidden = PropertySettings.ATTRIBUTE_NON_HIDDEN_STATUS

        reportLocator.addAttribute(reportLocator.text)

    def __init__(self):
        OpenMayaUI.MPxLocatorNode.__init__(self)

    def postConstructor(self):
        thisNode = self.thisMObject()

        self.textplug = OpenMaya.MPlug(thisNode, 
                                       self.text)

        self.defaultPosition = OpenMaya.MPoint(0.0, 0.0, 0.0)

        corner1 = OpenMaya.MPoint(-0.17, 0.0, -0.7)
        corner2 = OpenMaya.MPoint(0.17, 0.0, 0.3)

        self.defaultBounds = OpenMaya.MBoundingBox(corner1, 
                                                   corner2)

        self.worldPoint = OpenMaya.MPoint(0, 0, 0)

        self.nodeMatrix = OpenMaya.MMatrix()

        self.xPosPointer = 0
        self.yPosPointer = 0

    def compute(self, 
                currentPlug, 
                dataBlockInput): 
        pass

    def computeViewOffset(self,
                          view,
                          offsetX,
                          offsetY,
                          pathSpaceMatrix,
                          offsetIndex):
        worldPt = OpenMaya.MPoint()
        worldVector = OpenMaya.MVector() 
        pointOffset = OpenMaya.MPoint()

        view.viewToWorld(offsetX,
                         offsetY+offsetIndex*-20, 
                         worldPt, 
                         worldVector)

        offsetVector = OpenMaya.MVector(worldVector.x,
                                        worldVector.y,
                                        worldVector.z) 

        offsetVector.normalize()

        return OpenMaya.MPoint(worldPt.x + offsetVector.x,
                               worldPt.y + offsetVector.y,
                               worldPt.z + offsetVector.z) * pathSpaceMatrix

    def getPointOffset(self, 
                       view, 
                       path,
                       pointCount):
        self.nodeMatrix = path.inclusiveMatrix()

        self.worldPoint.x = self.nodeMatrix[12]
        self.worldPoint.y = self.nodeMatrix[13]
        self.worldPoint.z = self.nodeMatrix[14]

        isClipped = False
        self.xPosPointer, self.yPosPointer, isClipped = view.worldToView(self.worldPoint)

        offsetX = int(self.xPosPointer) 
        offsetY = int(self.yPosPointer)
        
        return (self.computeViewOffset(view,
                                       offsetX,
                                       offsetY,
                                       path.inclusiveMatrixInverse(),
                                       index)
                for index in xrange(pointCount))

    def getTextData(self):
        inputText = str(self.textplug.asString()) 

        if '\n' in inputText:
            inputTextArray = [item.replace('\t', '  ')
                              for item in inputText.split('\n')]
        else:
            inputTextArray = [inputText]

        return inputTextArray

    def draw(self, 
             view, 
             path, 
             style, 
             status):
        inputTextArray = self.getTextData()

        pointOffsetArray = self.getPointOffset(view, 
                                               path,
                                               len(inputTextArray))

        view.beginGL()
        for index, pointOffset in enumerate(pointOffsetArray):
            worldPt = OpenMaya.MPoint(pointOffset.x,
                                      pointOffset.y,
                                      pointOffset.z)

            view.drawText(inputTextArray[index], 
                          worldPt,
                          OpenMayaUI.M3dView.kLeft)

        view.endGL()

    def isBounded(self):
        return True

    def boundingBox(self):
        return self.defaultBounds


class reportLocatorData(OpenMaya.MUserData):
	def __init__(self):
		OpenMaya.MUserData.__init__(self, False)  

		self.fColor = OpenMaya.MColor()
		self.fSoleLineList = OpenMaya.MPointArray()


class reportLocatorDrawOverride(OpenMayaRender.MPxDrawOverride):
    PLUGIN_NODE_NAME = "reportLocatorDrawOverride"

    REGISTER_FAILLURE = "Override Registration Faillure:\t\n{NAME} will not be loaded"
    
    REGISTER_FAILLURE_MESSAGE = REGISTER_FAILLURE.format(NAME=PLUGIN_NODE_NAME)

    DEREGISTER_FAILLURE = "Override deregister Faillure:\t\n{NAME} was not unloaded properly"

    DEREGISTER_FAILLURE_MESSAGE = DEREGISTER_FAILLURE.format(NAME=PLUGIN_NODE_NAME)

    @staticmethod
    def _createOverride(inputMObject):
        return reportLocatorDrawOverride(inputMObject)

    @staticmethod
    def draw(context, data):
        return

    def __init__(self, 
                 inputMObject):
        OpenMayaRender.MPxDrawOverride.__init__(self, 
                                                inputMObject, 
                                                reportLocatorDrawOverride.draw)

        self.mCurrentBoundingBox = OpenMaya.MBoundingBox()

        corner1 = OpenMaya.MPoint( -0.17, 0.0, -0.7 )
        corner2 = OpenMaya.MPoint( 0.17, 0.0, 0.3 )

        self.mCurrentBoundingBox.expand(corner1)
        self.mCurrentBoundingBox.expand(corner2)

        self.mCustomBoxDraw = True
        self.pos = OpenMaya.MPoint(0.0, 0.0, 0.0)  ## Position of the text

        depNodeFn = OpenMaya.MFnDependencyNode(inputMObject)
        self.textplug = depNodeFn.findPlug('text', True)

        self.worldPoint = OpenMaya.MPoint(0, 0, 0)

        self.nodeMatrix = OpenMaya.MMatrix()

        self.defaultPosition = OpenMaya.MPoint(0.0, 0.0, 0.0)

    def getTextData(self):
        inputText = str(self.textplug.asString()) 

        if '\n' in inputText:
            inputTextArray = [item.replace('\t', '  ')
                              for item in inputText.split('\n')]
        else:
            inputTextArray = [inputText]

        return inputTextArray

    def getPointInScreenCoordinates(self,
                                    objectMDagPath,
                                    frameContext):
        self.nodeMatrix = objectMDagPath.inclusiveMatrix()

        self.worldPoint.x = self.nodeMatrix[12]
        self.worldPoint.y = self.nodeMatrix[13]
        self.worldPoint.z = self.nodeMatrix[14]

        viewPoint = self.worldPoint*frameContext.getMatrix(frameContext.kViewProjMtx)
        basePointX = 0.0
        basePointY = 0.0
        if viewPoint.z != 0.0:
            basePointX = (viewPoint.x/viewPoint.z)*0.5
            basePointY = (viewPoint.y/viewPoint.z)*0.5
        basePointX += 0.5
        basePointY += 0.5

        originX, originY, width, height = frameContext.getViewportDimensions()
        viewPoint.x = basePointX*width
        viewPoint.y = basePointY*height
        viewPoint.z = 0.0

        return viewPoint

    def getPointOffset(self, 
                       objectMDagPath,
                       frameContext,
                       pointCount):   
        viewPoint = self.getPointInScreenCoordinates(objectMDagPath,
                                                     frameContext)

        return (OpenMaya.MPoint(viewPoint.x,
                                viewPoint.y+offsetIndex*-20,
                                0.0)
                for offsetIndex in xrange(pointCount))

    def supportedDrawAPIs(self):
        return OpenMayaRender.MRenderer.kOpenGL | OpenMayaRender.MRenderer.kDirectX11

    def isBounded(self, 
                  objectMDagPath, 
                  cameraPath):
        return True

    def boundingBox(self, 
                    objectMDagPath, 
                    cameraPath):
        return self.mCurrentBoundingBox

    def disableInternalBoundingBoxDraw(self):
        return self.mCustomBoxDraw

    def prepareForDraw(self, 
                       objectMDagPath, 
                       cameraPath, 
                       frameContext, 
                       oldData):
        if not isinstance(oldData, 
                          reportLocatorData):
            return reportLocatorData()

        return oldData

    def hasUIDrawables(self):
        return True

    def addUIDrawables(self, 
                       objectMDagPath, 
                       drawManager, 
                       frameContext, 
                       locatordata):
        if not isinstance(locatordata, 
                          reportLocatorData):
            return

        inputTextArray = self.getTextData()
        pointOffsetArray = self.getPointOffset(objectMDagPath,
                                               frameContext,
                                               len(inputTextArray))

        drawManager.beginDrawable()
        textColor = OpenMaya.MColor((0.1, 0.8, 0.8, 1.0)) 

        drawManager.setColor(textColor)

        for index, pointOffset in enumerate(pointOffsetArray):
            drawManager.text2d(pointOffset,
                               inputTextArray[index])


        drawManager.endDrawable()


def initializePlugin(mobject):
    mplugin = OpenMaya.MFnPlugin(mobject, 
                                    report.AUTHOR, 
                                    report.PLUGIN_VERSION,
                                    "Any")
    try:
        mplugin.registerNode(report.PLUGIN_NODE_NAME, 
                             report.PLUGIN_NODE_ID, 
                             report._createNode, 
                             report._addAttributes, 
                             OpenMaya.MPxNode.kDependNode)

    except:
        raise Exception(report.REGISTER_FAILLURE_MESSAGE)

    try:
        mplugin.registerNode(reportLocator.PLUGIN_NODE_NAME, 
                             reportLocator.PLUGIN_NODE_ID, 
                             reportLocator._createNode, 
                             reportLocator._addAttributes, 
                             OpenMaya.MPxNode.kLocatorNode,
                             report.DRAW_CLASSIFICATION)

    except:
        raise Exception(reportLocator.REGISTER_FAILLURE_MESSAGE)

    try:
        OpenMayaRender.MDrawRegistry.registerDrawOverrideCreator(report.DRAW_CLASSIFICATION,
                                                                 report.DRAW_REGISTER, 
                                                                 reportLocatorDrawOverride._createOverride)

    except:
        raise Exception(reportLocatorDrawOverride.REGISTER_FAILLURE_MESSAGE)


def uninitializePlugin(mobject):
    mplugin = OpenMaya.MFnPlugin(mobject)

    try:
        mplugin.deregisterNode(report.PLUGIN_NODE_ID)

    except:
        raise Exception(report.DEREGISTER_FAILLURE_MESSAGE)

    try:
        mplugin.deregisterNode(reportLocator.PLUGIN_NODE_ID)

    except:
        raise Exception(reportLocator.DEREGISTER_FAILLURE_MESSAGE)

    try:
        OpenMayaRender.MDrawRegistry.deregisterDrawOverrideCreator(report.DRAW_CLASSIFICATION,
                                                                   report.DRAW_REGISTER)

    except:
        raise Exception(reportLocatorDrawOverride.DEREGISTER_FAILLURE_MESSAGE)
