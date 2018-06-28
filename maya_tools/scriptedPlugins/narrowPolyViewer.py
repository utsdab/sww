#-
# ==========================================================================
# Copyright (C) 1995 - 2006 Autodesk, Inc. and/or its licensors.  All
# rights reserved.
#
# The coded instructions, statements, computer programs, and/or related
# material (collectively the "Data") in these files contain unpublished
# information proprietary to Autodesk, Inc. ("Autodesk") and/or its
# licensors, which is protected by U.S. and Canadian federal copyright
# law and by international treaties.
#
# The Data is provided for use exclusively by You. You have the right
# to use, modify, and incorporate this Data into other products for
# purposes authorized by the Autodesk software license agreement,
# without fee.
#
# The copyright notices in the Software and this entire statement,
# including the above license grant, this restriction and the
# following disclaimer, must be included in all copies of the
# Software, in whole or in part, and all derivative works of
# the Software, unless such copies or derivative works are solely
# in the form of machine-executable object code generated by a
# source language processor.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND.
# AUTODESK DOES NOT MAKE AND HEREBY DISCLAIMS ANY EXPRESS OR IMPLIED
# WARRANTIES INCLUDING, BUT NOT LIMITED TO, THE WARRANTIES OF
# NON-INFRINGEMENT, MERCHANTABILITY OR FITNESS FOR A PARTICULAR
# PURPOSE, OR ARISING FROM A COURSE OF DEALING, USAGE, OR
# TRADE PRACTICE. IN NO EVENT WILL AUTODESK AND/OR ITS LICENSORS
# BE LIABLE FOR ANY LOST REVENUES, DATA, OR PROFITS, OR SPECIAL,
# DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES, EVEN IF AUTODESK
# AND/OR ITS LICENSORS HAS BEEN ADVISED OF THE POSSIBILITY
# OR PROBABILITY OF SUCH DAMAGES.
#
# ==========================================================================
#+

import sys
import math
import maya_tools.OpenMaya as OpenMaya
import maya_tools.OpenMayaMPx as OpenMayaMPx
import maya_tools.OpenMayaUI as OpenMayaUI
import maya_tools.OpenMayaRender as OpenMayaRender

glRenderer = OpenMayaRender.MHardwareRenderer.theRenderer()
glFT = glRenderer.glFunctionTable()

kPluginCmdName = "spNarrowPolyViewer"

kInitFlag = "-in"
kInitFlagLong = "-init"

kResultsFlag = "-r"
kResultsFlagLong = "-results"

kClearFlag = "-cl"
kClearFlagLong = "-clear"

kToleranceFlag = "-tol"
kToleranceFlagLong = "-tolerance"

class narrowPolyViewer(OpenMayaMPx.MPx3dModelView):
	def __init__(self):
		OpenMayaMPx.MPx3dModelView.__init__(self)

		self.fOldCamera = OpenMaya.MDagPath()
		self.fCameraList = OpenMaya.MDagPathArray()
		self.fCurrentPass = 0
		self.fDrawManips = True
		self.fOldDisplayStyle = OpenMayaUI.M3dView.kWireFrame
		self.fLightTest = False
		self.fListList = OpenMaya.MDagPathArray()
		self.tol = 10.0

		self.setMultipleDrawEnable(True)

	def multipleDrawPassCount(self):
		return self.fCameraList.length() + 1

	def setCameraList(self, cameraList):
		setMultipleDrawEnable(True)
		self.fCameraList.clear()

		for i in range(cameraList.length()):
			self.fCameraList.append(cameraList[i])

		self.refresh()

	def removeAllCameras(self):
		self.fCameraList.clear()
		self.refresh()

	def getCameraHUDName(self):
		cameraPath = OpenMaya.MDagPath()
		self.getCamera(cameraPath)

		cameraPath.pop()

		hudName = "spNarrowPolyViewer: " + cameraPath.partialPathName()
		return hudName

	def setIsolateSelect(self, list):
		self.setViewSelected(True)
		return self.setObjectsToView(list)

	def setIsolateSelectOff(self):
		return self.setViewSelected(False)

	def preMultipleDraw(self):
		self.fCurrentPass = 0
		self.fDrawManips = False

		dagPath = OpenMaya.MDagPath()

		try:
			oldCamera = OpenMaya.MDagPath()
			self.getCamera(oldCamera)

			self.fOldCamera = oldCamera

			if self.isColorIndexMode():
				self.setColorIndexMode(False)

			displayHUD(False)

			sList = OpenMaya.MSelectionList()
			OpenMaya.MGlobal.getActiveSelectionList(sList)

			sList.getDagPath(0, dagPath)
		except:
			# sys.stderr.write("ERROR: spNarrowPolyViewer.preMultipleDraw b\n")
			pass

		try:
			itMeshPolygon = OpenMaya.MItMeshPolygon(dagPath, OpenMaya.cvar.MObject_kNullObj)

			if None == itMeshPolygon:
				return;

			self.beginGL()

			while not itMeshPolygon.isDone():
				points = OpenMaya.MPointArray()
				itMeshPolygon.getPoints(points, OpenMaya.MSpace.kWorld)
				length = points.length()

				if length == 3:
					for i in range(length):
						p = points[i]
						p1 = points[(i+1)%length]
						p2 = points[(i+2)%length]

						v1 = OpenMaya.MVector(p1 - p)
						v2 = OpenMaya.MVector(p2 - p)

						angle = v1.angle(v2) * 180.0 / math.pi

						if math.fabs(angle - self.tol) < 0.0001 or angle < self.tol:
							glFT.glBegin( OpenMayaRender.MGL_POLYGON )
							glFT.glVertex3f(points[0].x, points[0].y, points[0].z)
							glFT.glVertex3f(points[1].x, points[1].y, points[1].z)
							glFT.glVertex3f(points[2].x, points[2].y, points[2].z)

							glFT.glNormal3f(points[0].x, points[0].y, points[0].z)
							glFT.glNormal3f(points[1].x, points[1].y, points[1].z)
							glFT.glNormal3f(points[2].x, points[2].y, points[2].z)

							glFT.glTexCoord3f(points[0].x, points[0].y, points[0].z)
							glFT.glTexCoord3f(points[1].x, points[1].y, points[1].z)
							glFT.glTexCoord3f(points[2].x, points[2].y, points[2].z)
							glFT.glEnd()

				itMeshPolygon.next()

			self.endGL()
		except:
			# sys.stderr.write("ERROR: spNarrowPolyViewer.preMultipleDraw c\n")
			pass

	def postMultipleDraw(self):
		try:
			self.setCamera(self.fOldCamera)
			self.fDrawManips = True
			self.updateViewingParameters()
		except:
			sys.stderr.write("ERROR: spNarrowPolyViewer.postMultipleDraw\n")
			raise

	def preMultipleDrawPass(self, index):
		self.fCurrentPass = index

		try:
			self.setDisplayAxis(False)
			self.setDisplayAxisAtOrigin(False)
			self.setDisplayCameraAnnotation(False)

			dagPath = OpenMaya.MDagPath()

			if self.fCurrentPass == 0:
				self.getCamera(dagPath)
			else:
				nCameras = self.fCameraList.length()
				if self.fCurrentPass <= nCameras:
					dagPath = self.fCameraList[self.fCurrentPass-1]
				else:
					sys.stderr.write("ERROR: ...too many passes specified\n")
					return

			self.setCameraInDraw(dagPath)

			self.setObjectDisplay(OpenMayaUI.M3dView.kDisplayEverything, True)

			if dagPath == self.fOldCamera:
				self.fDrawManips = True
				self.setObjectDisplay(OpenMayaUI.M3dView.kDisplayGrid, True)

				self.setFogEnabled(True)

				self.setBackgroundFogEnabled(False)

				self.setObjectDisplay(OpenMayaUI.M3dView.kDisplayLights, True)
				self.setObjectDisplay(OpenMayaUI.M3dView.kDisplayCameras, True)
				self.setObjectDisplay(OpenMayaUI.M3dView.kDisplayIkHandles, True)
				self.setObjectDisplay(OpenMayaUI.M3dView.kDisplayDimensions, True)
				self.setObjectDisplay(OpenMayaUI.M3dView.kDisplaySelectHandles, True)

				textPos = OpenMaya.MPoint(0.0, 0.0, 0.0)
				str = "Main View"
				self.drawText(str, textPos, OpenMayaUI.M3dView.kLeft)
			else:
				self.fDrawManips = False
				self.setObjectDisplay(OpenMayaUI.M3dView.kDisplayGrid, False)

				self.setFogEnabled(True)

				self.setObjectDisplay(OpenMayaUI.M3dView.kDisplayLights, False)
				self.setObjectDisplay(OpenMayaUI.M3dView.kDisplayCameras, False)
				self.setObjectDisplay(OpenMayaUI.M3dView.kDisplayIkHandles, False)
				self.setObjectDisplay(OpenMayaUI.M3dView.kDisplayDimensions, False)
				self.setObjectDisplay(OpenMayaUI.M3dView.kDisplaySelectHandles, False)
		except:
			sys.stderr.write("ERROR: spNarrowPolyViewer.preMultipleDrawPass\n")
			raise

		# note do not have light test in here

		# self.setLightingMode(OpenMayaUI.kLightDefault)

		if ((self.fCurrentPass % 2) == 0):
			self.setObjectDisplay(OpenMayaUI.M3dView.kDisplayNurbsSurfaces, True );
			self.setObjectDisplay(OpenMayaUI.M3dView.kDisplayNurbsCurves, True );

		self.updateViewingParameters()

	def postMultipleDrawPass(self, index):
		self.setObjectDisplay(OpenMayaUI.M3dView.kDisplayEverything, True)

	def okForMultipleDraw(self, dagPath):
		if not self.fDrawManips and dagPath.hasFn(OpenMaya.MFn.kManipulator3D):
			return False
		return True

	def multipleDrawPassCount(self):
		return self.fCameraList.length() + 1

	def viewType(self):
		return "spNarrowPolyViewer";




class narrowPolyViewerCmd(OpenMayaMPx.MPxModelEditorCommand):
	def __init__(self):
		OpenMayaMPx.MPxModelEditorCommand.__init__(self)
		self.fCameraList = OpenMaya.MDagPathArray()

	def appendSyntax(self):
		try:
			theSyntax = self._syntax()
			theSyntax.addFlag(kInitFlag, kInitFlagLong)
			theSyntax.addFlag(kResultsFlag, kResultsFlagLong)
			theSyntax.addFlag(kClearFlag, kClearFlagLong)
			theSyntax.addFlag(kToleranceFlag, kToleranceFlagLong, OpenMaya.MSyntax.kDouble)

		except:
			sys.stderr.write( "ERROR: creating syntax for model editor command: %s" % kPluginCmdName )

	def doEditFlags(self):
		try:
			user3dModelView = self.modelView()

			if user3dModelView.viewType() == kPluginCmdName:
				argData = self._parser()

				if argData.isFlagSet(kInitFlag):
					self.initTests(user3dModelView)
				elif argData.isFlagSet(kResultsFlag):
					self.testResults(user3dModelView)
				elif argData.isFlagSet(kClearFlag):
					self.clearResults(user3dModelView)
				elif argData.isFlagSet(kToleranceFlag):
					tol = argData.flagArgumentDouble(kToleranceFlag, 0)
					user3dModelView.tol = tol
					user3dModelView.refresh(True, True)
				else:
					return OpenMaya.kUnknownParameter
		except:
			sys.stderr.write( "ERROR: in doEditFlags for model editor command: %s" % kPluginCmdName )

	def initTests(self, view):
		clearResults(self, view)

		# Add every camera into the scene.  Don't change the main camera,
		# it is OK that it gets reused.
		#
		cameraPath = OpenMaya.MDagPath()
		dagIterator = OpenMaya.MItDag(OpenMaya.MItDag.kDepthFirst, OpenMaya.MFn.kCamera)

		while not dagIterator.isDone():
			try:
				dagIterator.getPath(cameraPath)
				camera = OpenMaya.MFnCamera(cameraPath)
			except:
				continue

			OpenMaya.MGlobal.displayInfo(camera.fullPathName())
			self.fCameraList.append(cameraPath)

			dagIterator.next()

		try:
			view.setCameraList(self.fCameraList)
		except:
			OpenMaya.MGlobal.displayError("Could not set list of cameras\n")
			raise

		view.refresh()

	def testResults(self, view):
		print "fCameraLIst.length() = %d " % (self.fCameraList.length(), )
		length = self.fCameraList.length()

	def clearResults(self, view):
		view.removeAllCameras()
		self.fCameraList.clear()



def cmdCreator():
	return OpenMayaMPx.asMPxPtr( narrowPolyViewerCmd() )

def viewerCreator():
	return OpenMayaMPx.asMPxPtr( narrowPolyViewer() )

# initialize the script plug-in
def initializePlugin(mobject):
	mplugin = OpenMayaMPx.MFnPlugin(mobject)
	try:
		mplugin.registerModelEditorCommand( kPluginCmdName, cmdCreator, viewerCreator)
	except:
		sys.stderr.write( "Failed to register model editor command: %s" % kPluginCmdName )
		raise

# uninitialize the script plug-in
def uninitializePlugin(mobject):
	mplugin = OpenMayaMPx.MFnPlugin(mobject)
	try:
		mplugin.deregisterModelEditorCommand( kPluginCmdName )
	except:
		sys.stderr.write( "Failed to deregister model editor command: %s" % kPluginCmdName )
		raise
