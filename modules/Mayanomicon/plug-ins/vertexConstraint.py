"""#////////////////////////////////////////////////////////////////////////////////////////////
#//
#//   Plug Name:             vertexConstraint Node 2.0 beta
#//   orignal Author:        Chad Robert Morgan
#//                          unfortunately Chad's site with the source code...
#//                          http://members.aol.com/docmorgan/plugins.htm
#//                          doesn't exist anymore...
#//
#/////////////////////////////////////////////////////////////////////////////////////////////
#//
#//   converted Chad's c++ code to a Python Plugin, changed a little bit to the original code...
#//   Alex V. U. Strarup... http://www.strarup.net ... april 2009
#//   3d@strarup.net
#//
#/////////////////////////////////////////////////////////////////////////////////////////////
#////////////////////////////////////////////////////////////////////////////////////////////
#//
#//  DESCRIPTION :	this plug is a Node which make it posible to constrain
#//                     objects to vertices...
#//                     first select the vertex you want your object constrained to
#//                     then select your object... and type the command...
#//                     vertexConstraint;
#//
#//-////////////////////////////////////////////////////////////////////////////////////////////
#//
#//  Installation: put this script in the Maya plugin folder...
#//                to activate the plugin, type loadPlugin vertexConstraint;
#//                or load via Plugin Manager...
#//
#//-////////////////////////////////////////////////////////////////////////////////////////////
#//
#//  Conditions : Use at your own risk, No Banana throwing or whatever if it doesn't work...
#//               NO RESPONSABILITIES DUE TO MALFUNCTION, JOB LOST, WHATEVER...
#//               copy... steal... modify it... do whatever you want...
#//               as long you don't call me up early in the morning... :-D
#//
#//-/////////////////////////////////////////////////////////////////////////////////////////////
#//-///////////////////////////////////   Start of Code /////////////////////////////////////////
#//-////////////////////////////////////////////////////////////////////////////////////////////
"""
import math, sys
import maya.OpenMaya as OpenMaya
import maya.OpenMayaMPx as OpenMayaMPx

kPluginNodeName = "vertexConstraint"
kPluginCmdName="vertexConstraint"
# The id is a 32bit value used to identify this type of node in the binary file format.
# please don't use this number in any other plugin's...
# but get your own by contacting Autodesk... 
# original id was ( 0x000c1 ) however not sure if this was an unique value...
# so added one of the Id's I got from Alias back in 2004...
kPluginNodeId = OpenMaya.MTypeId(0x0010A781) # id nr. 2 from Alias...

# da Node definition...
class vertexConstraintNode(OpenMayaMPx.MPxNode):
      inputShape = OpenMaya.MObject()
      output = OpenMaya.MObject()
      outputX = OpenMaya.MObject()
      outputY = OpenMaya.MObject()
      outputZ = OpenMaya.MObject()
      vertexIndex = OpenMaya.MObject()
      constraintParentInverseMatrix = OpenMaya.MObject()

      def __init__(self):
            OpenMayaMPx.MPxNode.__init__(self)

      #da compute function thingie...
      def compute(self,daPlug,daData):
            if daPlug == vertexConstraintNode.output or daPlug.parent() == vertexConstraintNode.output:
                  try:
                        inputData = daData.inputValue(vertexConstraintNode.inputShape)
                  except:
                        sys.stderr.write("Oh Mama %s failed to get da MDataHandle inputValue inputShape\n") %kPluginNodeName; raise
                  try:
                        vertHandle = daData.inputValue(vertexConstraintNode.vertexIndex)
                  except:
                        sys.stderr.write("Oh Mama %s failed to get da MDataHandle inputValue vertexIndex\n") %kPluginNodeName; raise
                  try:
                        inverseMatrixHandle = daData.inputValue(vertexConstraintNode.constraintParentInverseMatrix)
                  except:
                        sys.stderr.write("Oh Mama %s failed to get da MDataHandle inputValue constraintParentInverseMatrix\n") %kPluginNodeName; raise
                  try:
                        outputHandle = daData.outputValue(vertexConstraintNode.output)
                  except:
                        sys.stderr.write("Oh Mama %s failed to get da MDataHandle outputValue output\n") %kPluginNodeName; raise
                  nodeFn = OpenMaya.MFnDependencyNode()
                  mesh = OpenMaya.MObject()
                  mesh = inputData.asMesh()

                  index = vertHandle.asInt() 
                  vert = OpenMaya.MFnMesh(mesh)
                  inverseMatrix = OpenMaya.MMatrix()
                  inverseMatrix = inverseMatrixHandle.asMatrix()
                  pos = OpenMaya.MPoint()
                  try:
                        vert.getPoint(index, pos, OpenMaya.MSpace.kWorld)
                  except:
                        sys.stderr.write("Oh Mama %s Could not get vert position\n") %kPluginNodeName; raise
                  pos *= inverseMatrix
                  #set output attrs
                  posX = outputHandle.child(vertexConstraintNode.outputX)
                  posX.setDouble(pos.x)
                  posY = outputHandle.child(vertexConstraintNode.outputY)
                  posY.setDouble(pos.y)
                  posZ = outputHandle.child(vertexConstraintNode.outputZ)
                  posZ.setDouble(pos.z)
                  daData.setClean(daPlug)


#--------------------------------------------------------------------------------------
# da creator may he have mercy on us... :-D
# this method exists to give Maya a way to create new objects of this type...
#--------------------------------------------------------------------------------------
def nodeCreator():
      return OpenMayaMPx.asMPxPtr(vertexConstraintNode())

def nodeInitializer():
      nAttr = OpenMaya.MFnNumericAttribute()
      tAttr = OpenMaya.MFnTypedAttribute()
      mAttr = OpenMaya.MFnMatrixAttribute()
      cAttr = OpenMaya.MFnCompoundAttribute()
      try:
            vertexConstraintNode.inputShape = tAttr.create( "inputShape", "inS", OpenMaya.MFnMeshData.kMesh)
            tAttr.setStorable(0)
            tAttr.setKeyable(0)
      except:
            sys.stderr.write("Oh Mama failed to create da inputShape attribute\n"); raise 
      try:
            vertexConstraintNode.vertexIndex = nAttr.create( "vertex", "vert", OpenMaya.MFnNumericData.kLong)
            nAttr.setWritable(1)
            nAttr.setStorable(1)
            nAttr.setArray(0)
      except:
            sys.stderr.write("Oh Mama failed to create da vertexIndex attribute\n"); raise 
      try:
            vertexConstraintNode.constraintParentInverseMatrix = mAttr.create("constraintParentInverseMatrix", "pim",  OpenMaya.MFnMatrixAttribute.kDouble)
            mAttr.setStorable(0)
            mAttr.setKeyable(0)
      except:
            sys.stderr.write("Oh Mama failed to create da constraintParentInverseMatrix attribute\n"); raise 
      try:
            vertexConstraintNode.outputX = nAttr.create( "outputX", "X", OpenMaya.MFnNumericData.kDouble)
      except:
            sys.stderr.write("Oh Mama failed to create da outputX attribute\n"); raise 
      try:
            vertexConstraintNode.outputY = nAttr.create( "outputY", "Y", OpenMaya.MFnNumericData.kDouble)
      except:
            sys.stderr.write("Oh Mama failed to create da outputY attribute\n"); raise 
      try:
            vertexConstraintNode.outputZ = nAttr.create( "outputZ", "Z", OpenMaya.MFnNumericData.kDouble)
      except:
            sys.stderr.write("Oh Mama failed to create da outputZ attribute\n"); raise 
      try:
            vertexConstraintNode.output = cAttr.create("output", "out")
            cAttr.addChild(vertexConstraintNode.outputX)
            cAttr.addChild(vertexConstraintNode.outputY)
            cAttr.addChild(vertexConstraintNode.outputZ)
            cAttr.setStorable(0)
            cAttr.setKeyable(0)
            cAttr.setArray(0)
      except:
            sys.stderr.write("Oh Mama failed to create da output attribute\n"); raise 
      try:
            vertexConstraintNode.addAttribute(vertexConstraintNode.inputShape)
      except:
            sys.stderr.write("Oh Mama failed to add da input attributes\n"); raise 
      try:
            vertexConstraintNode.addAttribute(vertexConstraintNode.vertexIndex)
      except:
            sys.stderr.write("Oh Mama failed to add da input attributes\n"); raise 
      try:
            vertexConstraintNode.addAttribute(vertexConstraintNode.constraintParentInverseMatrix)
      except:
            sys.stderr.write("Oh Mama failed to add da input attributes\n"); raise 
      try:
            vertexConstraintNode.addAttribute(vertexConstraintNode.output)
      except:
            sys.stderr.write("Oh Mama failed to add da input attributes\n"); raise 
      try:
            vertexConstraintNode.attributeAffects( vertexConstraintNode.inputShape, vertexConstraintNode.output )
      except:
            sys.stderr.write("Oh Mama failed setting da attributeAffects\n"); raise 
      try:
            vertexConstraintNode.attributeAffects( vertexConstraintNode.vertexIndex, vertexConstraintNode.output )
      except:
            sys.stderr.write("Oh Mama failed setting da attributeAffects\n"); raise 
      try:
            vertexConstraintNode.attributeAffects( vertexConstraintNode.constraintParentInverseMatrix, vertexConstraintNode.output )
      except:
            sys.stderr.write("Oh Mama failed setting da attributeAffects\n"); raise 
      # everything is oki doki... :)

#--------------------------------------------------------------------------------
#--------------------------- da end of the nodeInitilizer -----------------------
#--------------------------------------------------------------------------------

# start off vertexConstraint command....
# command
class vertexConstraintCmd(OpenMayaMPx.MPxCommand):
      def __init__(self):
            OpenMayaMPx.MPxCommand.__init__(self)
            self.dgMod = OpenMaya.MDGModifier()

      def redoIt(self):
            try:
                  self.dgMod.doIt()
                  print( "vertexConstraint created......\n")
            except:
                  sys.stderr.write( "Error creating vertexConstraint command\n" ); raise

      def undoIt(self):
            try:
                  self.dgMod.undoIt()
                  print( "vertexConstraint removed....\n")
            except:
                  sys.stderr.write( "Error removing vertexConstraint command\n" ); raise

      def doIt(self, args):
            slist = OpenMaya.MSelectionList()
            OpenMaya.MGlobal.getActiveSelectionList(slist)
            component = OpenMaya.MObject()
            targetDagPath = OpenMaya.MDagPath()
            targetVertexFn = OpenMaya.MFnMesh()
            destDagPath = OpenMaya.MDagPath()
            destTransformFn = OpenMaya.MFnTransform()


            try:
                  vert = OpenMaya.MItSelectionList(slist, OpenMaya.MFn.kMeshVertComponent)
            except:
                  sys.stderr.write("Oh Mama %s Could not create iterator\n") %kPluginCmdName; raise
            try:
                  vert.getDagPath(targetDagPath, component)
            except:
                  sys.stderr.write("Oh Mama %s Could not get dag path to vertex\n") %kPluginCmdName; raise
            if(component.isNull()):
                  sys.stderr.write("Oh Mama no vertexes are selected\n"); raise
            try:
                  targetVertexFn.setObject(targetDagPath)
            except:
                  sys.stderr.write("Oh Mama %s Could not set vertes to object\n") %kPluginCmdName; raise
            try:
                  vertIndex = OpenMaya.MItMeshVertex(targetDagPath, component)
            except:
                  sys.stderr.write("Oh Mama %s Could not get the vertIndex\n") %kPluginCmdName; raise
            try:
                  dest = OpenMaya.MItSelectionList(slist, OpenMaya.MFn.kTransform)
            except:
                  sys.stderr.write("Oh Mama %s Could not create iterator\n") %kPluginCmdName; raise
            try:
                  dest.getDagPath(destDagPath)
            except:
                  sys.stderr.write("Oh Mama %s Could not get dag path to transform\n") %kPluginCmdName; raise
            try:
                  destTransformFn.setObject(destDagPath)
            except:
                  sys.stderr.write("Oh Mama %s Could not set fn to transform\n") %kPluginCmdName; raise
            # create vertexConstraint node
            try:
                  vertexConstraintObj = OpenMaya.MObject(self.dgMod.createNode("vertexConstraint"))
            except:
                  sys.stderr.write("Oh Mama %s Could not create vertexConstraint node\n") %kPluginCmdName; raise
            vertexConstraintFn = OpenMaya.MFnDependencyNode(vertexConstraintObj)
            inMeshPlug = OpenMaya.MPlug()
            inMeshPlug = vertexConstraintFn.findPlug("inputShape")
            # get output worldmesh from shape
            worldMeshPlug = OpenMaya.MPlug()
            worldMeshPlug = targetVertexFn.findPlug("worldMesh")
            worldMeshPlug = worldMeshPlug.elementByLogicalIndex(targetDagPath.instanceNumber())
            inverseMatrix = OpenMaya.MPlug()
            inverseMatrix = destTransformFn.findPlug("parentInverseMatrix")
            inverseMatrix = inverseMatrix.elementByLogicalIndex(destDagPath.instanceNumber())
            vertexPlug = OpenMaya.MPlug()
            vertexPlug = vertexConstraintFn.findPlug("vertex")
            vertexPlug.setInt(vertIndex.index())
            try:
                  self.dgMod.connect((vertexConstraintFn.findPlug("output")), (destTransformFn.findPlug("translate")))
            except:
                  sys.stderr.write("Oh Mama %s Could not connect output to translation\n") %kPluginCmdName; raise
            try:
                  self.dgMod.connect(worldMeshPlug, inMeshPlug)
            except:
                  sys.stderr.write("Oh Mama %s Could not connect world mesh to constraint\n") %kPluginCmdName; raise
            try:
                  self.dgMod.connect(inverseMatrix, vertexConstraintFn.findPlug("constraintParentInverseMatrix"))
            except:
                  sys.stderr.write("Oh Mama %s Could not connect world mesh to constraint\n") %kPluginCmdName; raise
            self.redoIt()

      def isUndoable(self):
            return True

# command Creator
def cmdCreator():
# Create the command
      return OpenMayaMPx.asMPxPtr( vertexConstraintCmd() )

# initialize the script plug-in
def initializePlugin(mobject):
      mplugin = OpenMayaMPx.MFnPlugin(mobject, "vertex Constraint Node", "2.0", "Any")
      try:
            mplugin.registerNode( kPluginNodeName, kPluginNodeId, nodeCreator, nodeInitializer, OpenMayaMPx.MPxNode.kDependNode)
      except:
            sys.stderr.write( "Failed to register node: %s" % kPluginNodeName ); raise
      try:
            mplugin.registerCommand( kPluginCmdName, cmdCreator )
      except:
            sys.stderr.write( "Failed to register command: %s\n" % kPluginCmdName ); raise  

# uninitialize the script plug-in
def uninitializePlugin(mobject):
      mplugin = OpenMayaMPx.MFnPlugin(mobject)
      try:
            mplugin.deregisterNode( kPluginNodeId )
      except:
            sys.stderr.write( "Failed to deregister node: %s" % kPluginNodeName ); raise
      try:
            mplugin.deregisterCommand( kPluginCmdName )
      except:
            sys.stderr.write( "Failed to unregister command: %s\n" % kPluginCmdName ); raise 





