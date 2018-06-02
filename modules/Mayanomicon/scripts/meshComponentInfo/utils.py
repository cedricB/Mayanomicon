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

import maya.cmds
import maya.OpenMaya as OpenMaya

class Builder(object):
    PLUGIN_NAME = 'meshComponentInfo'

    def __init__(self):
        self.meshNode = None

        self.drivenTransform = None

        self.hubNode = None

    def isLoaded(self):
        return maya.cmds.pluginInfo(self.PLUGIN_NAME, 
                                    query=True, 
                                    loaded=True)

    def initialize(self):
        maya.cmds.loadPlugin(self.PLUGIN_NAME)

    def attach(self,
               meshNode,
               node):
        if not self.isLoaded():
            self.initialize()

        shapes = maya.cmds.listRelatives(meshNode,
                                         shapes=True,
                                         fullPath=True) or []

        if not shapes:
            
            return

        if not maya.cmds.nodeType(shapes[0]) == 'mesh':
            OpenMaya.MGlobal.displayError('Sorry {} must be a mesh'.format(shapes[0]))

            return

        self.meshNode = meshNode

        self.drivenTransform = node

        if not all([self.meshNode,
                    self.drivenTransform]):
            OpenMaya.MGlobal.displayError('Please provide mesh and transform nodes')

            return

        if self.meshNode == self.drivenTransform:
            OpenMaya.MGlobal.displayError('Sorry {} cannot be driven by its own worldMesh shape'.format(self.drivenTransform))

            return

        self.hubNode = maya.cmds.createNode(self.PLUGIN_NAME,
                                            n='{}_ComponentConstraint1'.format(self.drivenTransform))

        maya.cmds.connectAttr('{}.worldMesh[0]'.format(shapes[0]),
                              '{}.input'.format(self.hubNode),
                              force=True)

        maya.cmds.connectAttr('{}.output'.format(self.hubNode),
                              '{}.translate'.format(self.drivenTransform),
                              force=True)