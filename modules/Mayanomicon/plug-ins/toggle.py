'''
########################################################################
#                                                                      #
#             toggle.py                                              #
#                                                                      #
#             Email: cedricbazillou@gmail.com                          #
#             blog: http://circecharacterworks.wordpress.com/          #
########################################################################
    L I C E N S E:
        Copyright (c) 2013 Cedric BAZILLOU All rights reserved.
        
        Permission is hereby granted to Normanstudios/ mikros / onyx films companies to
            -to modify the file
            -distribute
            -share
            -do derivative work  

        The above copyright notice and this permission notice shall be included in all copies of the Software 
        and is subject to the following conditions:
            - These 3 companies uses the same type of license
            - credit the original author
            - does not claim patent nor copyright from the original work
            - this plugin is not sold to third parties

    P U R P O S E:
        toggle weights for space switching, visibility, blendshape etc

    I N S T A L L A T I O N:
        Copy the "toggle.py" to your Maya plugins directory
        Windows: Program Files\Autodesk\MayaXXXX\bin\plug-ins\ 

        or better in your maya user directory:
        %MAYA_APP_DIR%\%mayaNumber%\scripts\plug-ins\( create one if it does not exists )
'''

import math, sys
import maya.OpenMaya as OpenMaya
import maya.OpenMayaMPx as OpenMayaMPx
import maya.OpenMayaAnim as OpenMayaAnim
import maya.cmds as cmds

kPluginNodeName = "toggle"
kPluginNodeId = OpenMaya.MTypeId(0xAAC1245) 

version = 0.2
author = 'cedric BAZILLOU'

class toggle(OpenMayaMPx.MPxNode):
    def compute(self,Plug,Data):
        #data handles Layout
        numberofOutput_Val        = Data.inputValue(self.numberofOutput ).asInt()
        activeIndex_Val  = Data.inputValue(self.activeIndex ).asInt()
        outState_handle  = Data.outputArrayValue(self.outState ) 

        #FoolProof check
        if activeIndex_Val > (numberofOutput_Val - 1):
            activeIndex_Val = numberofOutput_Val - 1
        ThsNde = self.thisMObject()

        self.write_ouputState( outState_handle,numberofOutput_Val,activeIndex_Val,ThsNde )
    def write_ouputState(self,outState_handle,numberofOutput_Val,activeIndex_Val,ThsNde ):
        cBuilder = outState_handle.builder()
        bldChck = cBuilder.elementCount()
        growVal = numberofOutput_Val-bldChck
        
        if growVal>0:
            #print 'we need to grow this array of ', bldChck , ' elements by  ', growVal
            cBuilder.growArray ( growVal )

        stateList = []
        stateList = [ 0 for k in range(numberofOutput_Val) ]
        stateList[activeIndex_Val] = 1
        
        currentDH = OpenMaya.MDataHandle()
        for n in range(0,numberofOutput_Val):
            currentDH = cBuilder.addElement(n)
            currentDH.setBool(stateList[n])
            
        bldChck = cBuilder.elementCount()
        # prune unwanted index --> equivalent to removeMultiInstance...
        if bldChck>numberofOutput_Val:
            depFn = OpenMaya.MFnDependencyNode( ThsNde )
            curvePointsPlug = depFn.findPlug('outState')            
            outName = curvePointsPlug.info()
            for k in range(bldChck-1,numberofOutput_Val-1,-1):
                try:
                    cBuilder.removeElement(k)
                except:
                    # --> a bit dirty but it help when node is not connected yet we have access to the correct number of output attribute
                    # when node is connected this fallback is not needed anymore
                    cmds.removeMultiInstance( '%s[%s]'%(outName,k), b=True ) 
        outState_handle.set(cBuilder)
        outState_handle.setAllClean()
def nodeCreator():
    return OpenMayaMPx.asMPxPtr(toggle())
def link_relashionShip( DriverList, driven_Attribute ):
    for driver in DriverList:
        toggle.attributeAffects(driver,driven_Attribute)
def nodeInitializer():
    nAttr = OpenMaya.MFnNumericAttribute()

    #----------------------------------------------------------------------------------------------- Input Attributes

    toggle.numberofOutput = nAttr.create( "numberOfOutput", "cn", OpenMaya.MFnNumericData.kInt,1)
    nAttr.setStorable(1)
    nAttr.setKeyable(1)
    nAttr.setHidden(0)
    nAttr.setMin(1)
    nAttr.setSoftMax(16)
    toggle.addAttribute( toggle.numberofOutput )
    
    toggle.activeIndex = nAttr.create( "activeIndex", "aID", OpenMaya.MFnNumericData.kInt,0)
    nAttr.setStorable(1)
    nAttr.setKeyable(1)
    nAttr.setHidden(0)
    nAttr.setMin(0)
    toggle.addAttribute( toggle.activeIndex )

    toggle.outState = nAttr.create( "outState", "oSt", OpenMaya.MFnNumericData.kBoolean)
    nAttr.setStorable(1)
    nAttr.setKeyable(0)
    nAttr.setHidden(0)
    nAttr.setArray(1)
    nAttr.setUsesArrayDataBuilder(1)    
    toggle.addAttribute( toggle.outState )

    DriverList = [ toggle.numberofOutput, toggle.activeIndex ]
    link_relashionShip(DriverList,toggle.outState )

def initializePlugin(mobject):
    mplugin = OpenMayaMPx.MFnPlugin(mobject, "Bazillou2012", "0.2", "Any")
    try:
        mplugin.registerNode( kPluginNodeName, kPluginNodeId, nodeCreator, nodeInitializer, OpenMayaMPx.MPxNode.kDependNode)
    except:
        sys.stderr.write( "Failed to register node: %s" % kPluginNodeName ); raise
def uninitializePlugin(mobject):
    mplugin = OpenMayaMPx.MFnPlugin(mobject)
    try:
        mplugin.deregisterNode( kPluginNodeId )
    except:
        sys.stderr.write( "Failed to deregister node: %s" % kPluginNodeName ); raise