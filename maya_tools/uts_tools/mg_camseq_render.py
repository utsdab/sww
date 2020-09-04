'''
# This is a tool for layout artists breaking out a scene from a maya file that has used the camera sequencer to create an animatic
# It will render each camera using rfm, and optionally create individual maya files for each camera.
#
# the camera sequence is so lame when it comes to exporting for a shot based workflow
# the retiming inside maya is particularly problematic when rendering and it is best everything is flattened to a normal time line.
# One of the other camera sequencers is probably a better choice.  all the sequencer can deliver is a playblast
#
# spooling to tractor works but local queue doesnt work with the modified script....is it a port?
'''

import os
import sys
from functools import partial
import time

try:
    import rfm2.api.strings as apistr
    import rfm2.spool as rfm2s
    import rfm2.ui as rfmui
except ImportError as ie:
    print("Failed to import module: {}".format(ie))
try:
    import maya_tools.uts_tools.rfm_tractor2 as rfmt2
except ImportError as ie:
    print("Failed to import module: {}".format(ie))
try:
    import maya.cmds as mc
    import pymel.core as pmc

except ImportWarning, err:
    print "Failed to import pymel or maya python %s" % (err)


def get_sources():
    srcs = []
    try:
        seq = pmc.ls(type='sequencer')[0]
    except Exception, err:
        print "Cant find a camera sequencer node."
    else:
        print "Found a sequencer node: %s"%seq.name()
        srcs = seq.sources()
    unmuted_srcs = []
    for src in srcs:
        track = src.getTrack()
        scale = src.getScale()
        if scale == 1.0:
            pass
        else:
            print "Bad scale for %s - muting" % src.getShotName()
            src.setMute(True)
        mute = src.getMute()
        source = src.name()
        shotname = src.getShotName()
        camInputs = src.inputs()
        cam = camInputs[0]
        camShape = cam.getShape()
        print "Track %s   Muted %s   Source %s  Shotname %s   Camera %s  CameraShape %s"%(track, mute, source, shotname, cam, camShape)
        pmc.setAttr(camShape.renderable,False)
        if not mute:
            unmuted_srcs.append(src)

    return unmuted_srcs

def run(unmuted_srcs, queue):
    is_localqueue = True
    rfmui.prefs.set_pref_by_name('rfmRenderBatchQueue','Local Queue')

    try:
        if queue == 'Local Queue':
            is_localqueue = True
            rfmui.prefs.set_pref_by_name('rfmRenderBatchQueue','Local Queue')
        elif queue == 'Tractor':
            is_localqueue = False
            rfmui.prefs.set_pref_by_name('rfmRenderBatchQueue','Tractor')
    except Exception as ie:
        print("Cant set the queue at all: {}".format(ie))

    #
    # force style to be rib
    #
    rfmui.prefs.set_pref_by_name('rfmRenderBatchSpoolStyle','RIB')
    # The renderable camera is not specified by the "defaultRenderGlobals" node,
    # but rather by the .renderable attribute for each Camera in the scene
    # You'll need to query each Camera to find out which ones are flagged to be renderable
    if unmuted_srcs :
        for src in unmuted_srcs:
            print "--------- %s -- %s -----------"% (src.getName(), src.getCurrentCamera())
            #
            #  test if source is muted or if track is muted or there is no current camera
            #
            print " Start:   %4s  Dur:   %4s  End:      %4s " % ( src.getStartTime(), src.getSourceDuration(), src.getEndTime())
            print " Dur:     %4s  Track: %4s  ShotName: %s " % ( src.getSourceDuration(), src.getTrack(), src.getShotName())
            print " SqStart: %4s  Scale: %4s  SqDur:    %4s   SqEnd: %4s " % ( src.getSequenceStartTime(), src.getScale(), src.getSequenceDuration(), src.getSequenceEndTime())
            #
            # set globals for each shot
            #
            pmc.SCENE.defaultRenderGlobals.animation.set(1)
            pmc.SCENE.defaultRenderGlobals.animationRange.set(0)
            pmc.SCENE.defaultRenderGlobals.extensionPadding.set(4)
            pmc.SCENE.defaultRenderGlobals.startFrame.set(src.getSequenceStartTime())
            pmc.SCENE.defaultRenderGlobals.endFrame.set(src.getSequenceEndTime())
            pmc.SCENE.defaultRenderGlobals.byFrameStep.set(1)
            #
            # turn off all sim engines
            # set the rfm setting
            # no aovs, maybe set integrator and resolution?
            # store current renderable cameras to restore later
            # if there is a renderlayer with the same name as the camera then switch to it - nice
            # then restore later
            #
            cam = src.getCurrentCamera()
            camShape = pmc.listRelatives(cam)[0]
            pmc.setAttr(camShape.renderable,True)
            print "Using camers {}".format(cam)
            #
            # submit to tractor or localqueue using RIB method
            #
            try:
                if is_localqueue:

                    rfm2s.rfm_tractor.batch_render_spool(do_bake=False)
                else:
                    rfmt2.batch_render_spool(do_bake=False)

            except Exception, err:
                print "Cant Spool %s" % err
            finally:
                print "done....."
                pmc.setAttr(camShape.renderable,False)
                time.sleep(5)
# TODO:  make a UI
#   does this need an interface at all?


class myUI(object):
    def __init__(self, *args, **kwargs):
        super(myUI, self).__init__(*args, **kwargs)
        #
        # set the ui main window dimension
        #
        self.template = pmc.uiTemplate('ExampleTemplate', force=True)
        self.template.define(pmc.button, width=300, height=40, align='left')
        self.template.define(pmc.text, width=300, height=40, align='center')
        self.template.define(pmc.frameLayout, borderVisible=True, labelVisible=False)

        self.unmuted_srcs = get_sources()

        with pmc.window(title='Batch Render Cam Seq',menuBar=True,menuBarVisible=True) as self.win:
            # start the template block
            with self.template:
                with pmc.columnLayout( rowSpacing=5 ):
                    with pmc.frameLayout():
                        with pmc.columnLayout():
                            self.t1=pmc.text("Found %s Sources"%len(self.unmuted_srcs))
                            self.b1=pmc.button( label='LOCAL RENDER ',
                               command = pmc.Callback( self.buttonPressed, 'Local Queue' ))
                            self.b2=pmc.button( label='TRACTOR RENDER ',
                               command = pmc.Callback( self.buttonPressed, 'Tractor' ))
                            self.b3=pmc.button( label='EXIT',
                               command = pmc.Callback( self.exitbutton ))

    def buttonPressed(self, name):
        queue = name
        print "Batch render to %s!" % name
        run(self.unmuted_srcs, queue)

    def interrupt(self):
        print "Interrupt a false start"
        #
        # to do
        #

    def generatePerCameraScenefiles(self):
        print "Generating a maya scene for each camera"
        #
        # to do
        #


    def exitbutton(self):
        print "Exit Window"
        self.win.delete()

def main():
    w = myUI()

if __name__ == "__main__":
    print "RUNNING camera sequencer exporter ...."
    main()



