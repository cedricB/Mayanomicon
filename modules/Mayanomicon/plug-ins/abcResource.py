import maya.OpenMaya as OpenMaya
import maya.OpenMayaMPx as OpenMayaMPx

import os
import re

import alembic
import alembic.Abc
import pluginCore

import maya.cmds

class AbcShape(object):
    POINT_ATTRIBUTE = 'P'

    def __init__(self,
                 node):
        self.abc_node = node
        
        self.name = node.getName()
        
        self.full_path = node.getFullName()

        self.type = None
        
        self.shapeProperty = self.getShapeProperty()

        self.attributeMapping = self.getAttributeMapping()

        self.pointCount = 0 

    def clear(self):
        self.abc_node = None

        self.shapeProperty = None

    def collect(self):
        pass

    def getShapeProperty(self):
        return self.abc_node.getProperties().getProperty(0)

    def getTypeComponents(self,
                          attributeMapping):
        pass

    def getCoreComponents(self):
        self.pointCount = len(self.attributeMapping[self.POINT_ATTRIBUTE].samples[0])

        self.getTypeComponents(self.attributeMapping)

    def getAttributeMapping(self):               
        return {header.getName():self.shapeProperty.getProperty(header.getName())
                for header in self.shapeProperty.propertyheaders}

    def unpackHeader(self):
        self.pointCount = len(self.attributeMapping[self.POINT_ATTRIBUTE].samples[0])

        return {'name':self.name,
                'full_path':self.full_path,
                'type':self.type,
                'pointCount':self.pointCount}


class AbcMesh(AbcShape):
    POINT_ATTRIBUTE = 'P'
    FACE_COUNT_ATTRIBUTE = '.faceCounts'
    FACE_INDICES_ATTRIBUTE = '.faceIndices'

    CORE_ATTRIBUTES = (POINT_ATTRIBUTE,
                       FACE_COUNT_ATTRIBUTE,
                       FACE_INDICES_ATTRIBUTE)

    NORMAL_ATTRIBUTE = 'N'

    def __init__(self,
                 node):
        super(AbcMesh, self).__init__(node)
        
        self.type = 'mesh'

        self.numPolygons = 0

        self.normals = []

        self.geometryObject = None

    def collect(self):
        if self.geometryObject is not None:
            return

        self.getCoreComponents()

        meshFunctionUtils = OpenMaya.MFnMesh()

        meshDataUtils = OpenMaya.MFnMeshData()
        
        self.geometryObject = meshDataUtils.create()
        
        meshFunctionUtils.create(self.pointCount,
                                 self.numPolygons,
                                 self.getPositions(self.attributeMapping[self.POINT_ATTRIBUTE]),
                                 self.getFaceCounts(self.attributeMapping[self.FACE_COUNT_ATTRIBUTE]),
                                 self.getFaceIndices(self.attributeMapping[self.FACE_INDICES_ATTRIBUTE]),
                                 self.geometryObject) 

    def getTypeComponents(self,
                          attributeMapping):
        self.numPolygons = len(attributeMapping[self.FACE_COUNT_ATTRIBUTE].samples[0])    

    def getNormals(self,
                   attributeMapping):
        if self.NORMAL_ATTRIBUTE not in attributeMapping:
            return

        """
        self.normals = [item
                        for item in attributeMapping[self.NORMAL_ATTRIBUTE].samples[0])
        """

    def getUvs(self,
               attributeMapping):
        pass

    def getPositions(self,
                     sampleProperty):
        position = OpenMaya.MPointArray(len(sampleProperty.samples[0]))

        for index, item in enumerate(sampleProperty.samples[0]):
            position.set(OpenMaya.MPoint(item[0],
                                         item[1],
                                         item[2]), 
                              index)

        return position

    def getFaceIndices(self,
                       sampleProperty):
        faceIndices = OpenMaya.MIntArray(len(sampleProperty.samples[0]))

        for index, item in enumerate(sampleProperty.samples[0]):
            faceIndices.set(item, 
                            index)

        return faceIndices

    def getFaceCounts(self,
                      sampleProperty):
        faceCounts = OpenMaya.MIntArray(len(sampleProperty.samples[0]))

        for index, item in enumerate(sampleProperty.samples[0]):
            faceCounts.set(item, 
                           index)

        return faceCounts


class AbcPackage(object):
    def __init__(self,
                 types=None,
                 name_pattern=".*Shape"):
        if not types:
            self.types = ['AbcGeom_PolyMesh_v1']

        else:
            self.types = types[:]

        self.name_pattern = name_pattern
        
        self.shape_array = []

    def getNodeType(self,
                    node):
        return node.getProperties().propertyheaders[0].getMetaData().get("schema")

    def isPolyMesh(self,
                   node):
        if alembic.AbcGeom.IPolyMesh.matches(node.getMetaData()):
            return True

        return False

    def findShapes(self,
                   node):
        return [item
                for item in self.find_iter(node)]

    def find_iter(self,
                  node):
        if all([re.match(self.name_pattern, 
                         node.getName()),
                self.isPolyMesh(node)]):
            yield AbcMesh(node)
    
        for child in node.children:
            for grandchild in self.find_iter(child):
                yield grandchild

    def clear(self):
        self.shape_array = []

    def collectShapeArray(self,
                          input_file_path):
        if not os.path.exists(input_file_path):
            return False

        self.clear()

        current_archive = alembic.Abc.IArchive(input_file_path)
        
        self.shape_array = self.findShapes(current_archive.getTop())

        if not self.shape_array:
            return False

        return True


class AbcResource(OpenMayaMPx.MPxNode):
    API_VERSION = "Any"
    PLUGIN_NODE_NAME = "abcResource"
    PLUGIN_NODE_ID = OpenMaya.MTypeId(0xCC55797)

    PLUGIN_VERSION = "0.0.1"
    AUTHOR = "cedric_bazillou_2018"

    REGISTER_FAILLURE = "Plugin Registration Faillure:\t\n{NAME} will not be loaded"
    
    REGISTER_FAILLURE_MESSAGE = REGISTER_FAILLURE.format(NAME=PLUGIN_NODE_NAME)

    DEREGISTER_FAILLURE = "Plugin deregister Faillure:\t\n{NAME} was not unloaded properly"
    
    DEREGISTER_FAILLURE_MESSAGE = DEREGISTER_FAILLURE.format(NAME=PLUGIN_NODE_NAME)

    RESOLVE_PATH = "./"

    def __init__(self):
        OpenMayaMPx.MPxNode.__init__(self)

    def postConstructor(self):
        self.streamUtils = AbcPackage()

        self.process = {"output":self.processShapes,
                        "report":self.processReport}

    def outputAttributeWasRequested(self,
                                    currentPlug):
        if currentPlug == self.report:
            return "report"

        if all([currentPlug.isElement() == True,
                currentPlug.array() == self.output]):
            return "output"
        
        return None

    def needUpdate(self, 
                   currentPlug,
                   dataBlockInput):
        return self.outputAttributeWasRequested(currentPlug)

    def collect(self,
                input_file_path):
        self.streamUtils.collectShapeArray(input_file_path)

        if not self.streamUtils.shape_array:
            return False

        return True

    def processReport(self,
                      dataBlockInput): 
        if not self.collect(self.getAbcFile(dataBlockInput)):
            return

        outputUtils = OpenMaya.MFnStringArrayData()

        reportValues = [mesh.unpackHeader()
                        for mesh in self.streamUtils.shape_array]

        reportObject = outputUtils.create(reportValues)
        
        reportHandle = dataBlockInput.outputValue(self.report)
        reportHandle.setMObject(reportObject)
        reportHandle.setClean()

        self.streamUtils.clear()

    def processShapes(self,
                      dataBlockInput): 
        if not self.collect(self.getAbcFile(dataBlockInput)):
            return

        self.outputHandle = dataBlockInput.outputArrayValue(self.output)

        self.ouputBuilder = self.outputHandle.builder()

        for meshIndex, mesh in enumerate(self.streamUtils.shape_array):
            mesh.collect()

            currentHandle = self.ouputBuilder.addElement(meshIndex)
            
            currentHandle.setMObject(mesh.geometryObject)

        self.outputHandle.set(self.ouputBuilder)

        self.outputHandle.setAllClean()

        self.streamUtils.clear()

    def getAbcFile(self,
                   dataBlockInput):
        abcFile = str(dataBlockInput.inputValue(AbcResource.alembicPath).asString())
        
        abcFile = abcFile.strip()
        
        if not abcFile:
            return None

        if not abcFile.startswith(self.RESOLVE_PATH):
            return abcFile

        filePath = str(maya.cmds.file(q=True, 
                                      location=True))

        if filePath == 'unknown':
            return None

        abcFile = abcFile.replace(self.RESOLVE_PATH, '')
        
        abcFile = os.path.join(os.path.dirname(filePath),
                               abcFile).replace('\\', '/')

        return abcFile

    def compute(self, 
                currentPlug, 
                dataBlockInput): 
        updateType = self.needUpdate(currentPlug, 
                                     dataBlockInput)
        
        if not updateType:
            return

        self.process[updateType](dataBlockInput)

    @staticmethod
    def _createNode():
        return OpenMayaMPx.asMPxPtr(AbcResource())

    @staticmethod
    def _addAlembicPathAttribute():
        stringAttributeUtils = OpenMaya.MFnTypedAttribute()

        alembicStringData = OpenMaya.MFnStringData()
        AbcResource.alembicPath = stringAttributeUtils.create("alembicPath", 
                                                              "aPath", 
                                                              OpenMaya.MFnData.kString,
                                                              alembicStringData.create(''))

        stringAttributeUtils.setStorable(pluginCore.PropertySettings.ATTRIBUTE_EXPOSED_STATUS)
        stringAttributeUtils.setHidden(False)
        stringAttributeUtils.setKeyable(False)

        AbcResource.addAttribute(AbcResource.alembicPath)

    @staticmethod
    def _addOutputAttribute():
        outputAttributeUtils = OpenMaya.MFnTypedAttribute()

        AbcResource.output = outputAttributeUtils.create("output", 
                                                         "out", 
                                                          OpenMaya.MFnData.kMesh)

        outputAttributeUtils.setHidden(pluginCore.PropertySettings.ATTRIBUTE_HIDDEN_STATUS)

        outputAttributeUtils.setStorable(pluginCore.PropertySettings.ATTRIBUTE_NON_STORABLE_STATUS)

        outputAttributeUtils.setDisconnectBehavior(OpenMaya.MFnAttribute.kNothing)

        outputAttributeUtils.setArray(True)

        outputAttributeUtils.setUsesArrayDataBuilder(True)    

        AbcResource.addAttribute(AbcResource.output)

    @staticmethod
    def _addReportAttribute():
        outputAttributeUtils = OpenMaya.MFnTypedAttribute()

        AbcResource.report = outputAttributeUtils.create("report", 
                                                         "rpr", 
                                                         OpenMaya.MFnData.kStringArray)

        outputAttributeUtils.setHidden(pluginCore.PropertySettings.ATTRIBUTE_HIDDEN_STATUS)

        outputAttributeUtils.setStorable(pluginCore.PropertySettings.ATTRIBUTE_NON_STORABLE_STATUS)

        AbcResource.addAttribute(AbcResource.report)

    @staticmethod
    def _addAttributes():
        numericAttributeUtils = OpenMaya.MFnNumericAttribute()

        AbcResource._addAlembicPathAttribute()

        AbcResource._addOutputAttribute()
        
        AbcResource._addReportAttribute()

        AbcResource.attributeAffects(AbcResource.alembicPath, 
                                     AbcResource.output)
                                     
        AbcResource.attributeAffects(AbcResource.alembicPath, 
                                     AbcResource.report)                                  


def initializePlugin(mobject):
    mplugin = OpenMayaMPx.MFnPlugin(mobject, 
                                    AbcResource.AUTHOR, 
                                    AbcResource.PLUGIN_VERSION,
                                    "Any")

    try:
        mplugin.registerNode(AbcResource.PLUGIN_NODE_NAME, 
                             AbcResource.PLUGIN_NODE_ID, 
                             AbcResource._createNode, 
                             AbcResource._addAttributes, 
                             OpenMayaMPx.MPxNode.kDependNode)

    except:
        raise Exception(AbcResource.REGISTER_FAILLURE_MESSAGE)


def uninitializePlugin(mobject):
    mplugin = OpenMayaMPx.MFnPlugin(mobject)

    try:
        mplugin.deregisterNode(AbcResource.PLUGIN_NODE_ID)

    except:
        raise Exception(AbcResource.DEREGISTER_FAILLURE_MESSAGE)
