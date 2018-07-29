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

import pluginCore


class ToggleParentWeights(OpenMayaMPx.MPxNode):
    API_VERSION = "Any"
    PLUGIN_NODE_NAME = "toggleParentWeights"
    PLUGIN_NODE_ID = OpenMaya.MTypeId(0xBB99747)

    PLUGIN_VERSION = "0.0.1"
    AUTHOR = "cedric_bazillou_2018"

    REGISTER_FAILLURE = "Plugin Registration Faillure:\t\n{NAME} will not be loaded"
    
    REGISTER_FAILLURE_MESSAGE = REGISTER_FAILLURE.format(NAME=PLUGIN_NODE_NAME)

    DEREGISTER_FAILLURE = "Plugin deregister Faillure:\t\n{NAME} was not unloaded properly"
    
    DEREGISTER_FAILLURE_MESSAGE = DEREGISTER_FAILLURE.format(NAME=PLUGIN_NODE_NAME)

    DEFAULT_COUNT = 1

    DEFAULT_INDEX = 0

    def __init__(self):
        OpenMayaMPx.MPxNode.__init__(self)

    def postConstructor(self):
        self.outputHandle = None

        self.currentActiveIndexValue = 0

        self.outputCountValue = 0

        self.currentDataHandleArray = []

        self.ouputBuilder = None
    
        self.toggleStateArray = OpenMaya.MIntArray()

    def initializeHandles(self):
        self.currentDataHandleArray = []

        for writeIndex in range(self.outputCountValue):
            currentDataHandle = self.ouputBuilder.addElement(writeIndex)
            currentDataHandle.setBool(False)
            
            self.currentDataHandleArray.append(currentDataHandle)

    def resize(self, 
               dataBlockInput): 
        self.currentActiveIndexValue = dataBlockInput.inputValue(self.activeIndex).asInt()
        self.outputCountValue = dataBlockInput.inputValue(self.outputCount).asInt()

        if self.currentActiveIndexValue > (self.outputCountValue - 1):
            self.currentActiveIndexValue = self.outputCountValue - 1

        buildNumberOfElements = self.ouputBuilder.elementCount()
        if buildNumberOfElements < 1:
            resizeRange = self.outputCountValue

        else:
            resizeRange = self.outputCountValue-buildNumberOfElements

        if resizeRange < 1:
            return

        self.ouputBuilder.growArray(resizeRange)

        self.initializeHandles()

    def collectOutputhandle(self,
                            dataBlockInput):
        if self.outputHandle is None:
            self.outputHandle = dataBlockInput.outputArrayValue(self.output)

    def prepareBuilder(self):
        if self.ouputBuilder is None:
            self.ouputBuilder = self.outputHandle.builder()

    def writeOutput(self): 
        if not self.outputHandle:
            return

        self.outputHandle.set(self.ouputBuilder)
        self.outputHandle.setAllClean()

    def updateToggleStates(self):
        if not self.currentDataHandleArray:
            self.initializeHandles()

        for item in self.currentDataHandleArray:
            item.setBool(False)

        self.currentDataHandleArray[self.currentActiveIndexValue].setBool(True)

    def compute(self, 
                currentPlug, 
                dataBlockInput): 
        self.collectOutputhandle(dataBlockInput)

        self.prepareBuilder()

        self.resize(dataBlockInput)

        self.updateToggleStates()

        self.writeOutput()

    @staticmethod
    def createNode():
        return OpenMayaMPx.asMPxPtr(ToggleParentWeights())

    @staticmethod
    def addOutputCountAttribute():
        numericAttributeUtils = OpenMaya.MFnNumericAttribute()

        ToggleParentWeights.outputCount = numericAttributeUtils.create("outputCount", 
                                                                       "cn", 
                                                                       OpenMaya.MFnNumericData.kInt,
                                                                       ToggleParentWeights.DEFAULT_COUNT)

        numericAttributeUtils.setStorable(pluginCore.PropertySettings.ATTRIBUTE_STORABLE_STATUS)
        numericAttributeUtils.setKeyable(pluginCore.PropertySettings.ATTRIBUTE_KEYABLE_STATUS)
        numericAttributeUtils.setHidden(pluginCore.PropertySettings.ATTRIBUTE_NOT_HIDDEN_STATUS)
        numericAttributeUtils.setMin(ToggleParentWeights.DEFAULT_COUNT)
        numericAttributeUtils.setSoftMax(16)

        ToggleParentWeights.addAttribute(ToggleParentWeights.outputCount)

    @staticmethod
    def addActiveIndextAttribute():
        numericAttributeUtils = OpenMaya.MFnNumericAttribute()

        ToggleParentWeights.activeIndex = numericAttributeUtils.create("activeIndex", 
                                                                       "aID", 
                                                                       OpenMaya.MFnNumericData.kInt,
                                                                       ToggleParentWeights.DEFAULT_INDEX)

        numericAttributeUtils.setStorable(pluginCore.PropertySettings.ATTRIBUTE_STORABLE_STATUS)
        numericAttributeUtils.setKeyable(pluginCore.PropertySettings.ATTRIBUTE_KEYABLE_STATUS)
        numericAttributeUtils.setHidden(pluginCore.PropertySettings.ATTRIBUTE_NOT_HIDDEN_STATUS)
        numericAttributeUtils.setMin(ToggleParentWeights.DEFAULT_INDEX)

        ToggleParentWeights.addAttribute(ToggleParentWeights.activeIndex)

    @staticmethod
    def addOutputAttribute():
        numericAttributeUtils = OpenMaya.MFnNumericAttribute()

        ToggleParentWeights.output = numericAttributeUtils.create("output", 
                                                                  "out",
                                                                  OpenMaya.MFnNumericData.kBoolean)

        numericAttributeUtils.setStorable(pluginCore.PropertySettings.ATTRIBUTE_STORABLE_STATUS)
        numericAttributeUtils.setKeyable(pluginCore.PropertySettings.ATTRIBUTE_NON_KEYABLE_STATUS)
        numericAttributeUtils.setHidden(pluginCore.PropertySettings.ATTRIBUTE_NOT_HIDDEN_STATUS)
        numericAttributeUtils.setArray(True)
        numericAttributeUtils.setUsesArrayDataBuilder(True)

        ToggleParentWeights.addAttribute(ToggleParentWeights.output)

    @staticmethod
    def addAttributes():
        ToggleParentWeights.addOutputCountAttribute()
        
        ToggleParentWeights.addActiveIndextAttribute()

        ToggleParentWeights.addOutputAttribute()

        ToggleParentWeights.attributeAffects(ToggleParentWeights.outputCount, 
                                             ToggleParentWeights.output)

        ToggleParentWeights.attributeAffects(ToggleParentWeights.activeIndex, 
                                             ToggleParentWeights.output)


def initializePlugin(mobject):
    mplugin = OpenMayaMPx.MFnPlugin(mobject, 
                                    ToggleParentWeights.AUTHOR, 
                                    ToggleParentWeights.PLUGIN_VERSION,
                                    "Any")
    try:
        mplugin.registerNode(ToggleParentWeights.PLUGIN_NODE_NAME, 
                             ToggleParentWeights.PLUGIN_NODE_ID, 
                             ToggleParentWeights.createNode, 
                             ToggleParentWeights.addAttributes, 
                             OpenMayaMPx.MPxNode.kDependNode)

    except:
        raise Exception(ToggleParentWeights.REGISTER_FAILLURE_MESSAGE)


def uninitializePlugin(mobject):
    mplugin = OpenMayaMPx.MFnPlugin(mobject)

    try:
        mplugin.deregisterNode(ToggleParentWeights.PLUGIN_NODE_ID)

    except:
        raise Exception(ToggleParentWeights.DEREGISTER_FAILLURE_MESSAGE)
