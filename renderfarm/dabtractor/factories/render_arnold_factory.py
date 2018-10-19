#!/usr/bin/env rmanpy
'''
Renderman for maya job

'''



'''
generating ass files

Exporting an .ass File and Batch Rendering Through MEL
It is possible to export an .ass file and perform a batch render for a single frame using the following commands:
arnoldExportAss -f <filename>
arnoldRender -b;
In both cases you will need to prepend with the following:
currentTime <frameNum>;
For example:
currentTime 1; arnoldExportAss -f "/tmp/scene.001.ass";
The arnoldRender command allows you to render either individual frames or frame ranges. You can specify multiple different frames or frame ranges. These have to be separated with either ; or a whitespace character. Mixing the two separators will not work. When defining frame ranges, you must separate the start and end frame by using .. string. By adding a : to the frame range and adding an extra number after that, you can define the step for the frame. The following examples can also use ; instead of the whitespace:
-seq "1 2 3" - rendering frame 1, 2 and 3.
-seq "1 3..6" - rendering frame 1, and frames between 3 and 6 using a step of 1.
-seq "2 4..7 15..27:4" - rendering frame 2, frames between 4 and 7, and frames between 15 and 27 using a step of 4.

arnoldExportAss  -f "arnold/out.ass" -startFrame 1 -endFrame 3 -frameStep 1 -mask 255 -lightLinks 1 -shadowLinks 2 ;

maya -batch -proj /Volumes/dabrender/work/user_work/matthewgidney/TESTING_Renderfarm  -command "arnoldExportAss -f xxx.ass -startFrame 1 -endFrame 10" -file /Volumes/dabrender/work/user_work/matthewgidney/TESTING_Renderfarm/scenes/test_spiral_ARNOLD2.0001.ma


kick -i /Volumes/dabrender/work/user_work/matthewgidney/TESTING_Renderfarm/data/xxx.0001.ass -t 6 -dp -ds 8 -r 1280 720

-o outputfile eh out.exr


https://github.com/kiryha/AnimationDNA/wiki/06-Tutorials
 
 
Usage:  kick [options] ...
  -i %s               Input .ass file
  -o %s               Output filename
  -of %s              Output format: exr jpg png tif 
  -ocs %s             Output color space
  -r %d %d            Image resolution
  -sr %f              Scale resolution %f times in each dimension
  -rg %d %d %d %d     Render region (minx miny maxx maxy)
  -as %d              Anti-aliasing samples
  -af %s %f           Anti-aliasing filter and width (box triangle gaussian ...)
  -asc %f             Anti-aliasing sample clamp
  -c %s               Active camera
  -sh %f %f           Motion blur shutter (start end)
  -fov %f             Camera FOV
  -e %f               Camera exposure
  -ar %f              Aspect ratio
  -t %d               Threads
  -bs %d              Bucket size
  -bc %s              Bucket scanning (top left random spiral hilbert)
  -td %d              Total ray depth
  -dif %d             Diffuse depth
  -spc %d             Specular depth
  -trm %d             Transmission depth
  -ds %d              Diffuse samples
  -ss %d              Specular samples
  -ts %d              Transmission samples
  -d %s               Disable (ignore) a specific node or node.parameter
  -it                 Ignore texture maps
  -is                 Ignore shaders
  -cm %s              Set the value of ai_default_reflection_shader.color_mode (use with -is)
  -sm %s              Set the value of ai_default_reflection_shader.shade_mode (use with -is)
  -om %s              Set the value of ai_default_reflection_shader.overlay_mode (use with -is)
  -ib                 Ignore background shaders
  -ia                 Ignore atmosphere shaders
  -il                 Ignore lights
  -id                 Ignore shadows
  -isd                Ignore mesh subdivision
  -idisp              Ignore displacement
  -ibump              Ignore bump-mapping
  -imb                Ignore motion blur
  -idof               Ignore depth of field
  -isss               Ignore sub-surface scattering
  -flat               Flat shading
  -sd %d              Max subdivisions
  -set %s.%s %s       Set the value of a node parameter (-set name.parameter value)
  -dw                 Disable render window (recommended for batch rendering)
  -dp                 Disable progressive rendering (recommended for batch rendering)
  -ipr [m|q]          Interactive rendering mode, using Maya (default) or Quake/WASD controls
  -turn %d            Render n frames rotating the camera around the lookat point
  -lookat %f %f %f    Override camera look_at point (useful if the camera is specified by a matrix)
  -position %f %f %f  Override camera position
  -up %f %f %f        Override camera up vector
  -v %d               Verbose level (0..6)
  -nw %d              Maximum number of warnings
  -logfile %s         Write log file to the specified file path
  -l %s               Add search path for plugin libraries
  -nodes [n|t]        List all installed nodes, sorted by Name (default) or Type
  -info [n|u] %s      Print detailed information for a given node, sorted by Name or Unsorted (default)
  -tree %s            Print the shading tree for a given node
  -repeat %d          Repeat the render n times (useful for debugging)
  -resave %s          Re-save .ass scene to filename
  -db                 Disable binary encoding when re-saving .ass files (useful for debugging)
  -forceexpand        Force expansion of procedural geometry before re-saving
  -lcs                List available color spaces in loaded .ass files
  -nostdin            Ignore input from stdin
  -nokeypress         Disable wait for ESC keypress after rendering to display window
  -sl                 Skip license check (assume license is not available)
  -licensecheck       Check the connection with the license servers and list installed licenses
  -utest              Run unit tests for the Arnold API
  -av, --version      Print Arnold version number
  -notices            Print copyright notices
  -h, --help          Show this help message
where %d=integer, %f=float, %s=string
Example:  kick -i teapot.ass -r 640 480 -as 4 -o teapot.tif

-set options.skip_license_check off
'''


import json
import os
import time
import sys
import utils_factory as utils
import environment_factory as envfac
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
sh = logging.StreamHandler()
sh.setLevel(logging.INFO)
formatter = logging.Formatter('%(levelname)5.5s \t%(name)s \t%(message)s')
sh.setFormatter(formatter)
logger.addHandler(sh)


class Job(envfac.TractorJob):
    ''' The payload of gui-data needed to describe a rfm render job '''
    def __init__(self):
        super(Job, self).__init__()
        self.mayaprojectfullpath=None
        self.mayascenefullpath=None
        # This gets department from shotgun and checks it is a valid one in the json file
        # the department is year1 or year2 etc a user can only be in one department.
        if self.department in self.config.getoptions("renderjob", "projectgroup"):
            logger.info("Department {}".format(self.department))
        else:
            self.department="Other"
        self.adminemail = self.config.getdefault("admin", "email")
        logger.info("admin is {}".format(self.adminemail))


class Job2(object):
    def __init__(self):
        """
        The payload of gui-data needed to describe a arnold render job
        """
        self.usernumber=None
        self.username=None
        self.useremail=None

        try:
            self.env = envfac.TractorJob()
            self.usernumber = self.env.usernumber
            self.username = self.env.username
            self.useremail = self.env.useremail
            self.department = self.env.department
            self.dabwork = self.env.dabwork

        except Exception, err:
            logger.warn("Cant get user Job  credentials: {}".format(err))

        self.mayaprojectfullpath=None
        self.mayascenefullpath=None

        self.farmtier=None

        # This gets department from shotgun and checks it is a valid one in the json file
        if self.env.department in self.env.config.getoptions("renderjob", "projectgroup"):
            logger.info("Department {}".format(self.env.department))
        else:
            self.department="Other"

        self.farmpriority=None
        self.farmcrew=None

        self.jobtitle=None
        self.jobenvkey=None
        self.jobfile=None
        self.jobstartframe=None
        self.jobendframe=None
        self.jobchunks=None
        self.jobthreads=None
        self.jobthreadmemory=None

        self.optionskipframe=None
        self.optionmakeproxy=None
        # self.optionsendemail=None
        self.optionresolution=None
        self.optionmaxsamples=None

        self.envtype=None
        self.envshow=None
        self.envproject=None
        self.envscene=None

        self.mayaversion=None
        # self.rendermanversion=None
        self.shotgunProject=None
        self.shotgunProjectId = None
        self.shotgunClass = None
        self.shotgunShotAsset = None
        self.shotgunShotAssetId = None
        self.shotgunSeqAssetType = None
        self.shotgunSeqAssetTypeId = None
        self.shotgunTask=None
        self.shotgunTaskId=None
        self.sendToShotgun=False


class Render(object):
    ''' Arnold job defined using the tractor api '''

    def __init__(self, job):
        self.job=job

        utils.printdict( self.job.__dict__)

        self.job.dabwork="$DABWORK"

        self.mayaprojectpathalias = "$DABRENDER/$TYPE/$SHOW/$PROJECT"
        self.mayaprojectpath = os.path.join(self.job.dabwork, self.job.envtype, self.job.envshow, self.job.envproject)
        self.job.envprojectalias = "$PROJECT"
        self.mayascenefilefullpathalias = "$DABRENDER/$TYPE/$SHOW/$PROJECT/$SCENE"
        self.mayascenefilefullpath = os.path.join( self.job.dabwork, self.job.envtype, self.job.envshow,
                                                   self.job.envproject,self.job.envscene)
        self.scenename = os.path.basename(self.job.envscene)
        self.scenebasename = os.path.splitext(self.scenename)[0]
        self.sceneext = os.path.splitext(self.scenename)[1]
        self.renderpath = os.path.join( self.job.dabwork, self.job.envtype, self.job.envshow, self.job.envproject,"arnold", self.scenebasename)
        self.renderpathalias = "$DABRENDER/$TYPE/$SHOW/$PROJECT/arnold/$SCENENAME"
        self.renderdirectory = os.path.join(self.renderpath,"images")
        self.renderimagesalias = "$DABRENDER/$TYPE/$SHOW/$PROJECT/arnold/$SCENENAME/images"
        self.mayaversion = self.job.mayaversion,
        self.envkey_maya = "maya{}".format(self.mayaversion[0])
        self.startframe = int(self.job.jobstartframe)
        self.endframe = int(self.job.jobendframe)
        self.byframe = int(self.job.jobbyframe)
        self.chunks = int(self.job.jobchunks)  # pixar jobs are one at a time
        self.projectgroup = self.job.department
        self.options = ""
        self.resolution = self.job.optionresolution
        self.outformat = "exr"
        self.makeproxy = self.job.optionmakeproxy
        self.optionsendjobstartemail = self.job.optionsendjobstartemail
        self.optionsendtaskendemail = self.job.optionsendtaskendemail
        self.optionsendjobendemail = self.job.optionsendjobendemail
        self.skipframes = self.job.optionskipframe
        self.rendermaxsamples=self.job.optionmaxsamples
        self.threads = self.job.jobthreads
        self.threadmemory = self.job.jobthreadmemory
        # self.asspath = "{}/ass".format(self.renderpath)
        self.finaloutputimagebase = "{}/{}".format(self.renderpath,self.scenebasename)
        # self.proxyoutput = "$DABRENDER/$TYPE/$SHOW/$PROJECT/movies/$SCENENAME_{}.mov".format("datehere")
        self.thedate=time.strftime("%d-%B-%Y")


    def build(self):
        '''
        Main method to build the job
        :return:
        '''
        # ################# Job Metadata as JSON
        _jobMetaData={}
        _jobMetaData["email"] = self.job.useremail
        _jobMetaData["name"] = self.job.username
        _jobMetaData["number"] = self.job.usernumber
        _jobMetaData["scenename"] = self.scenename
        _jobMetaData["projectpath"] = self.mayaprojectpath
        _jobMetaData["startframe"] = self.job.jobstartframe
        _jobMetaData["endframe"] = self.job.jobendframe
        _jobMetaData["jobtype"] = "RFM"
        _jsonJobMetaData = json.dumps(_jobMetaData)


        # ################ 0 JOB ################
        self.renderjob = self.job.author.Job(title="M2A: {} {} {}-{}".format(
              self.job.username, self.scenename, self.job.jobstartframe, self.job.jobendframe),
              priority=10,
              envkey=[self.envkey_maya,"ProjectX",
                    "TYPE={}".format(self.job.envtype),
                    "SHOW={}".format(self.job.envshow),
                    "PROJECT={}".format(self.job.envproject),
                    "SCENE={}".format(self.job.envscene),
                    "SCENENAME={}".format(self.scenebasename)],
              metadata=_jsonJobMetaData,
              comment="User is {} {} {}".format(self.job.useremail,self.job.username,self.job.usernumber),
              projects=[str(self.projectgroup)],
              tier=str(self.job.farmtier),
              tags=["theWholeFarm", ],
              service="")


        # ############## 0 ThisJob #################
        task_thisjob = self.job.author.Task(title="Maya to Arnold Job")
        task_thisjob.serialsubtasks = 1

        # ############## 4 NOTIFY ADMIN OF TASK START ##########
        logger.info("admin email = {}".format(self.job.adminemail))
        task_notify_admin_start = self.job.author.Task(title="Register", service="ShellServices")
        task_notify_admin_start.addCommand( self.mail(self.job.adminemail,
                                                      "ARNOLD REGISTER",
                                                      "{na}".format(na=self.job.username),
                                                      "{na} {no} {em} {sc}".format(na=self.job.username, no=self.job.usernumber,em=self.job.useremail, sc=self.mayascenefilefullpath)))
        task_thisjob.addChild(task_notify_admin_start)


        # ############## 5 NOTIFY USER OF JOB START ###############
        if self.optionsendjobstartemail:
            logger.info("email = {}".format(self.job.useremail))
            task_notify_start = self.job.author.Task(title="Notify Start", service="ShellServices")
            task_notify_start.addCommand(self.mail(self.job.useremail, "JOB", "START", "{}".format(self.mayascenefilefullpath)))
            task_thisjob.addChild(task_notify_start)


        # ####### make a render directory - mayaproj/arnold/scene/[ass,images]
        _mayaproj = self.mayaprojectpath
        _arnolddir = os.path.join(self.mayaprojectpath,"arnold")
        _arnoldWorkDir = os.path.join(_arnolddir, self.scenebasename)
        _assDir = os.path.join(_arnoldWorkDir,"ass")
        _imgDir = os.path.join(_arnoldWorkDir,"images")
        _assFileBase = "{}.ass".format(self.scenebasename)


        task_prefilight = self.job.author.Task(title="Make render directory")
        command_mkdirs1 = self.job.author.Command(argv=[ "mkdir","-p", _arnolddir ],
                    tags=["maya", "theWholeFarm"],
                    atleast=1,
                    atmost=1,
                    service="Maya")
        command_mkdirs2 = self.job.author.Command(argv=[ "mkdir","-p", _arnoldWorkDir ],
                    tags=["maya", "theWholeFarm"],
                    atleast=1,
                    atmost=1,
                    service="Maya")
        command_mkdirs3 = self.job.author.Command(argv=[ "mkdir","-p", _assDir ],
                    tags=["maya", "theWholeFarm"],
                    atleast=1,
                    atmost=1,
                    service="Maya")
        command_mkdirs4 = self.job.author.Command(argv=[ "mkdir", "-p",_imgDir ],
                    tags=["maya", "theWholeFarm"],
                    atleast=1,
                    atmost=1,
                    service="Maya")
        task_prefilight.addCommand(command_mkdirs1)
        task_prefilight.addCommand(command_mkdirs2)
        task_prefilight.addCommand(command_mkdirs3)
        task_prefilight.addCommand(command_mkdirs4)
        task_thisjob.addChild(task_prefilight)

        # ############## 3 ASSGEN ##############
        task_render_allframes = self.job.author.Task(title="ALL FRAMES {}-{}".format(self.job.jobstartframe,self.job.jobendframe))
        task_render_allframes.serialsubtasks = 1
        task_assgen_allframes = self.job.author.Task(title="ASS GEN {}-{}".format(self.job.jobstartframe,self.job.jobendframe))

        # divide the frame range up into chunks
        _totalframes = int(self.job.jobendframe) - int(self.job.jobstartframe) + 1
        _chunks = int(self.chunks)
        _framesperchunk=_totalframes
        if _chunks < _totalframes:
            _framesperchunk=int(_totalframes/_chunks)
        else:
            _chunks=1

        #TODO use command wrapper here for arnold job
        #TODO not needed now - can use quotes
        __command = "arnoldExportAss"


        # loop thru chunks

        for i, chunk in enumerate(range( 1, _chunks + 1 )):
            _offset = i * _framesperchunk
            _chunkstart = int(self.job.jobstartframe) + _offset
            _chunkend = _chunkstart + _framesperchunk - 1

            if chunk >= _chunks:
                _chunkend = int(self.job.jobendframe)

            task_generate_ass = self.job.author.Task(title="ASS GEN chunk {} frames {}-{}".format(
                    chunk, _chunkstart, _chunkend ))


            command_generate_ass = self.job.author.Command(argv=[
                    "maya", "-batch", "-proj", self.mayaprojectpath, "-command",
                    "{command} -f \"{file}\" -startFrame {start} -endFrame {end}".format(
                            command=__command, file=os.path.join(_assDir,self.scenebasename), start=_chunkstart, end=_chunkend, step=1),
                            "-file", self.mayascenefilefullpath],
                    tags=["maya", "theWholeFarm"],
                    atleast=int(self.threads),
                    atmost=int(self.threads),
                    service="Maya")
            task_generate_ass.addCommand(command_generate_ass)
            task_assgen_allframes.addChild(task_generate_ass)

        task_render_allframes.addChild(task_assgen_allframes)


        # ############### 4 RENDER ##############
        task_render_frames = self.job.author.Task(title="RENDER Frames {}-{}".format(self.job.jobstartframe,
                                                                                         self.job.jobendframe))
        task_render_frames.serialsubtasks = 0

        for frame in range( int(self.job.jobstartframe), int(self.job.jobendframe) + 1, int(self.job.jobbyframe) ):

            # ################# Job Metadata as JSON
            _imgfile = "{proj}/{scenebase}.{frame:04d}.{ext}".format(
                proj=self.renderdirectory, scenebase=self.scenebasename, frame=frame, ext=self.outformat)
            # _statsfile = "{proj}/rib/{frame:04d}/{frame:04d}.xml".format(
            #     proj=self.renderpath, frame=frame)
            _assfile = "{base}.{frame:04d}.ass".format(base=os.path.join(_assDir,self.scenebasename), frame=frame)

            _outfile = "{base}.{frame:04d}.exr".format(base=os.path.join(_imgDir,self.scenebasename), frame=frame)
            _shotgunupload = "PR:{} SQ:{} SH:{} TA:{}".format(self.job.shotgunProject,
                                                  self.job.shotgunSeqAssetType,
                                                  self.job.shotgunShotAsset,
                                                  self.job.shotgunTask)

            _taskMetaData={}
            _taskMetaData["imgfile"] = _outfile
            # _taskMetaData["statsfile"] = _statsfile
            _taskMetaData["assfile"] = _assfile
            _taskMetaData["shotgunupload"] = _shotgunupload
            _jsontaskMetaData = json.dumps(_taskMetaData)
            _title = "RENDER Frame {}".format(frame)
            # _preview = "sho {""}".format(_imgfile)

            task_render_ass = self.job.author.Task(title=_title, metadata=_jsontaskMetaData)

            '''
            kick -i /Volumes/dabrender/work/user_work/matthewgidney/TESTING_Renderfarm/data/xxx.0001.ass -t 6 -dp -ds 8 -r 1280 720
            -set options.procedural_search_path $ARNOLD_PROCEDURAL_PATH   for xgen and kick
            '''

            commonargs = ["kick", "-i", _assfile,
                          "-l", "$ARNOLD_PROCEDURAL_PATH",
                          # "-set", "options.skip_license_check", "off",
                          # "-set", "options.skip_license_check", "off",
                          "-o", _outfile]
            rendererspecificargs = [ "-nstdin", "-nokeypress", "-dp", "-dw" ]

            # ################ handle image resolution formats ###########
            if self.resolution == "720p":
                self.xres, self.yres = 1280, 720
                rendererspecificargs.extend(["-r", "%s" % self.xres, "%s" % self.yres])
            elif self.resolution == "1080p":
                self.xres, self.yres = 1920, 1080
                rendererspecificargs.extend(["-r", "%s" % self.xres, "%s" % self.yres])
            elif self.resolution == "540p":
                self.xres, self.yres = 960, 540
                rendererspecificargs.extend(["-r", "%s" % self.xres, "%s" % self.yres])
            elif self.resolution == "108p":
                self.xres, self.yres = 192, 108
                rendererspecificargs.extend(["-r", "%s" % self.xres, "%s" % self.yres])

            # if self.rendermaxsamples != "FROMFILE":
                # rendererspecificargs.extend([ "-maxsamples", "{}".format(self.rendermaxsamples) ])

            # if self.threadmemory != "FROMFILE":
            #     rendererspecificargs.extend([ "-memorylimit", "{}".format(self.threadmemory) ])

            rendererspecificargs.extend([
                "-t", "{}".format(self.threads),

            ])
            userspecificargs = [ utils.expandargumentstring(self.options)]

            finalargs = commonargs + rendererspecificargs
            command_render = self.job.author.Command(argv=finalargs,
                                            tags=["kick", "theWholeFarm"],
                                            atleast=int(self.threads),
                                            atmost=int(self.threads),
                                            service="Maya")
            task_render_ass.addCommand(command_render)

            # ############## 5 NOTIFY Task END ###############
            if self.optionsendtaskendemail:
                task_render_ass.addCommand(self.mail("TASK FRAME {}".format(frame), "END", "{}".format(
                    self.mayascenefilefullpath)))

            task_render_frames.addChild(task_render_ass)

        task_render_allframes.addChild(task_render_frames)
        task_thisjob.addChild(task_render_allframes)


        # ############## 5 PROXY ###############
        if self.makeproxy:
            '''
            rvio cameraShape1/StillLife.####.exr  -v -fps 25
            -rthreads 4
            -outres 1280 720 -out8
            -leader simpleslate "UTS" "Artist=Anthony" "Show=Still_Life" "Shot=Testing"
            -overlay frameburn .4 1.0 30.0  -overlay matte 2.35 0.3 -overlay watermark "UTS 3D LAB" .2
            -outgamma 2.2
            -o cameraShape1_StillLife.mov
            '''

            #### making proxys with rvio
            # TODO we need to find the actual output frames - right now we huess
            # (self.job.seqbasename,self.job.seqtemplatename)=utils.getSeqTemplate(self.job.selectedframename)

            _mov = "{}_{}.mov".format(self.scenebasename,utils.getnow())
            _outmov = os.path.join(self.mayaprojectpath,"movies",_mov)
            _inseq = "{}.####.exr".format(self.scenebasename)    #cameraShape1/StillLife.####.exr"
            _directory = "{}/arnold/{}/images".format(self.mayaprojectpath, self.scenebasename)
            _seq = os.path.join(_directory, _inseq)


            try:
                utils.makedirectoriesinpath(os.path.dirname(_outmov))
            except Exception, err:
                logger.warn(err)

            try:
                _option1 = "-v -fps 25 -rthreads {threads} -outres {xres} {yres} -t {start}-{end}".format(
                           threads="4",
                           xres="1280",
                           yres = "720",
                           start=self.startframe,
                           end=self.endframe)
                _option2 = "-out8 -outgamma 2.2"
                _option3 = "-overlay frameburn 0.5 1.0 30 -leader simpleslate UTS_BDES_ANIMATION Type={} Show={} Project={} File={} Student={}-{} Group={} Date={}".format(
                              self.job.envtype,
                              self.job.envshow,
                              self.job.envproject,
                              # self.scenebasename,
                              _mov,
                              self.job.usernumber,
                              self.job.username,
                              self.projectgroup,
                              self.thedate)

                _output = "-o %s" % _outmov
                _rvio_cmd = [ utils.expandargumentstring("rvio %s %s %s %s %s" % (_seq, _option1, _option2, _option3, _output)) ]
                task_proxy = self.job.author.Task(title="Proxy Generation")
                proxycommand = self.job.author.Command(argv=_rvio_cmd, service="Transcoding",tags=["rvio", "theWholeFarm"], envkey=["rvio"])
                task_proxy.addCommand(proxycommand)
                task_thisjob.addChild(task_proxy)

            except Exception, proxyerror:
                logger.warn("Cant make a proxy {}".format(proxyerror))

        else:
            logger.info("make proxy = {}".format(self.makeproxy))

        # ############## 6 SEND TO SHOTGUN ###############
        if self.job.sendToShotgun:
            logger.info("Sending to Shotgun = {} {} {} {}".format(self.job.shotgunProjectId,self.job.shotgunSeqAssetTypeId,self.job.shotgunShotAssetId,self.job.shotgunTaskId))
            _description = "Auto Uploaded from {} {} {} {}".format(self.job.envtype,self.job.envproject, self.job.envshow,self.job.envscene)
            _uploadcmd = ""
            if self.job.shotgunTaskId:
                _uploadcmd = ["shotgunupload.py",
                              "-o", self.job.shotgunOwnerId,
                              "-p", self.job.shotgunProjectId,
                              "-s", self.job.shotgunShotAssetId,
                              "-a", self.job.shotgunShotAssetId,
                              "-t", self.job.shotgunTaskId,
                              "-n", _mov,
                              "-d", _description,
                              "-m", _outmov ]
            elif not self.job.shotgunTaskId:
                _uploadcmd = ["shotgunupload.py",
                              "-o", self.job.shotgunOwnerId,
                              "-p", self.job.shotgunProjectId,
                              "-s", self.job.shotgunShotAssetId,
                              "-a", self.job.shotgunShotAssetId,
                              "-n", _mov,
                              "-d", _description,
                              "-m", _outmov ]
            task_upload = self.job.author.Task(title="SHOTGUN Upload P:{} SQ:{} SH:{} T:{}".format( self.job.shotgunProject,self.job.shotgunSeqAssetType,self.job.shotgunShotAsset, self.job.shotgunTask))
            uploadcommand = self.job.author.Command(argv=_uploadcmd, service="ShellServices",tags=["shotgun", "theWholeFarm"], envkey=["PixarRender"])
            task_upload.addCommand(uploadcommand)
            task_thisjob.addChild(task_upload)



        # ############## 5 NOTIFY JOB END ###############
        if self.optionsendjobendemail:
            logger.info("email = {}".format(self.job.useremail))
            task_notify_end = self.job.author.Task(title="Notify End", service="ShellServices")
            task_notify_end.addCommand(self.mail(self.job.useremail, "JOB", "COMPLETE", "{}".format(self.mayascenefilefullpath)))
            task_thisjob.addChild(task_notify_end)

        self.renderjob.addChild(task_thisjob)

    def validate(self):
        logger.info("\n\n{:_^80}\n{}\n{:_^80}".format("snip", self.renderjob.asTcl(), "snip"))

    def mail(self, to=None, level="Level", trigger="Trigger", body="Render Progress Body"):
        if not to:
            to = self.job.adminemail
        bodystring = "Arnold Render Progress: \nLevel: {}\nTrigger: {}\n\n{}".format(level, trigger, body)
        subjectstring = "FARM JOB: {} {} {} {}".format(level,trigger, str(self.scenebasename), self.job.username)
        mailcmd = self.job.author.Command(argv=["sendmail.py", "-t", "%s"%self.job.useremail, "-b", bodystring, "-s", subjectstring], service="ShellServices")
        return mailcmd

    def spool(self):
        # double check scene file exists
        logger.info("Double Checking: {}".format(os.path.expandvars(self.mayascenefilefullpath)))
        if os.path.exists(os.path.expandvars(self.mayascenefilefullpath)):
            try:
                logger.info("Spooled correctly")
                # all jobs owner by pixar user on the farm
                self.renderjob.spool(owner=self.job.config.getdefault("tractor","jobowner"),port=int(self.job.config.getdefault("tractor","port")))

            except Exception, spoolerr:
                logger.warn("A spool error %s" % spoolerr)
        else:
            message = "Maya scene file non existant %s" % self.mayascenefilefullpath
            logger.critical(message)
            logger.critical(os.path.normpath(self.mayascenefilefullpath))
            logger.critical(os.path.expandvars(self.mayascenefilefullpath))

            sys.exit(message)


# ##############################################################################

if __name__ == "__main__":
    logger.setLevel(logging.INFO)
    logger.info("START TESTING")

    """
    Usage:  kick [options] ...
  -i %s               Input .ass file
  -o %s               Output filename
  -of %s              Output format: exr jpg png tif 
  -ocs %s             Output color space for render window
  -r %d %d            Image resolution
  -sr %f              Scale resolution %f times in each dimension
  -rg %d %d %d %d     Render region (minx miny maxx maxy)
  -as %d              Anti-aliasing samples
  -asmax %d           Anti-aliasing samples maximum (for adaptive sampling)
  -af %s %f           Anti-aliasing filter and width (box triangle gaussian ...)
  -asc %f             Anti-aliasing sample clamp
  -c %s               Active camera
  -sh %f %f           Motion blur shutter (start end)
  -fov %f             Camera FOV
  -e %f               Camera exposure
  -ar %f              Pixel aspect ratio
  -t %d               Threads
  -gpu %s             Enabled gpu devices
  -bs %d              Bucket size
  -bc %s              Bucket scanning (top left random spiral hilbert)
  -td %d              Total ray depth
  -dif %d             Diffuse depth
  -spc %d             Specular depth
  -trm %d             Transmission depth
  -ds %d              Diffuse samples
  -ss %d              Specular samples
  -ts %d              Transmission samples
  -d %s               Disable (ignore) a specific node or node.parameter
  -it                 Ignore texture maps
  -is                 Ignore shaders
  -cm %s              Set the value of ai_default_reflection_shader.color_mode (use with -is)
  -sm %s              Set the value of ai_default_reflection_shader.shade_mode (use with -is)
  -om %s              Set the value of ai_default_reflection_shader.overlay_mode (use with -is)
  -ib                 Ignore background shaders
  -ia                 Ignore atmosphere shaders
  -il                 Ignore lights
  -id                 Ignore shadows
  -isd                Ignore mesh subdivision
  -idisp              Ignore displacement
  -ibump              Ignore bump-mapping
  -imb                Ignore motion blur
  -idof               Ignore depth of field
  -isss               Ignore sub-surface scattering
  -flat               Flat shading
  -sd %d              Max subdivisions
  -set %s.%s %s       Set the value of a node parameter (-set name.parameter value)
  -dw                 Disable render window (recommended for batch rendering)
  -dp                 Disable progressive rendering (recommended for batch rendering)
  -ipr [m|q]          Interactive rendering mode, using Maya (default) or Quake/WASD controls
  -turn %d            Render n frames rotating the camera around the lookat point
  -turn_smooth        Use a smooth start/end when rendering turn tables with -turn
  -lookat %f %f %f    Override camera look_at point (useful if the camera is specified by a matrix)
  -position %f %f %f  Override camera position
  -up %f %f %f        Override camera up vector
  -v %d               Verbose level (0..6)
  -nw %d              Maximum number of warnings
  -logfile %s         Write log file to the specified file path
  -ostatsfile %s      Write stats to the specified .json file, overwriting it if it exists
  -statsfile %s       Append stats to the specified .json file
  -profile %s         Write profile events to the specified .json file
  -l %s               Add search path for plugin libraries
  -nodes [n|t]        List all installed nodes, sorted by Name (default) or Type
  -info [n|u] %s      Print detailed information for a given node, sorted by Name or Unsorted (default)
  -tree %s            Print the shading tree for a given node
  -repeat %d          Repeat the render n times (useful for debugging)
  -resave %s          Re-save .ass scene to filename
  -db                 Disable binary encoding when re-saving .ass files (useful for debugging)
  -forceexpand        Force expansion of procedural geometry before re-saving
  -laovs              List available AOVs in loaded .ass files
  -lcs                List available color spaces in loaded .ass files
  -nostdin            Ignore input from stdin
  -nokeypress         Disable wait for ESC keypress after rendering to display window
  -sl                 Skip license check (assume license is not available)
  -op %s              Operator node name to evaluate from
  -iops               Ignore operators
  -licensecheck       Check the connection with the license servers and list installed licenses
  -utest              Run unit tests for the Arnold API
  -av, --version      Print Arnold version number
  -notices            Print copyright notices
  -h, --help          Show this help message
    """








