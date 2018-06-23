import math, sys
import maya.OpenMaya as OpenMaya
import maya.OpenMayaMPx as OpenMayaMPx

kPluginNodeName = "numToStringNode"
kPluginNodeId = OpenMaya.MTypeId(0x24BCD179) 


class numToStringNode(OpenMayaMPx.MPxNode):
	labelStr = OpenMaya.MObject()
	inputNum   = OpenMaya.MObject()
	output  = OpenMaya.MObject()

	def __init__(self):
		OpenMayaMPx.MPxNode.__init__(self)
		
	def compute(self,Plug,Data):
		labelStr_Hdle = Data.inputValue(self.labelStr)	
		inputNum_Hdle = Data.inputValue(self.inputNum)
		output_Handle = Data.outputValue(self.output)		
		
		inDouble = inputNum_Hdle.asDouble()
		inlabel = labelStr_Hdle.asString()
		resStream = inlabel + '_' + str(round( inDouble , 3))
		if len ( inlabel ) == 0:
			resStream = str(round( inDouble , 3))
			
		output_Handle.setString( resStream )
		
		Data.setClean(Plug)	


def nodeCreator():
	return OpenMayaMPx.asMPxPtr(numToStringNode())

def nodeInitializer():

	labelStr_Attr =  OpenMaya.MFnTypedAttribute()
	numToStringNode.labelStr = labelStr_Attr.create( "labelStr", "lss", OpenMaya.MFnData.kString  )
	labelStr_Attr.setStorable(1)
	labelStr_Attr.setKeyable(0)
	labelStr_Attr.setHidden(False)
	numToStringNode.addAttribute( numToStringNode.labelStr  )

	
	inputShape_Attr =  OpenMaya.MFnNumericAttribute()	
	numToStringNode.inputNum = inputShape_Attr.create( "inputNum", "num", OpenMaya.MFnNumericData.kDouble  )
	inputShape_Attr.setStorable(0)
	inputShape_Attr.setKeyable(0)
	inputShape_Attr.setHidden(0)		
	numToStringNode.addAttribute( numToStringNode.inputNum )

	output_Attr =  OpenMaya.MFnTypedAttribute()
	numToStringNode.output = output_Attr.create( "output", "out", OpenMaya.MFnData.kString  )
	output_Attr.setStorable(0)
	output_Attr.setKeyable(0)
	output_Attr.setHidden(False)
	numToStringNode.addAttribute( numToStringNode.output)

	numToStringNode.attributeAffects( numToStringNode.inputNum , numToStringNode.output )		
	numToStringNode.attributeAffects( numToStringNode.labelStr  , numToStringNode.output )			
	
	
def initializePlugin(mobject):
	mplugin = OpenMayaMPx.MFnPlugin(mobject, "Bazillou2010", "1.0", "Any")
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





