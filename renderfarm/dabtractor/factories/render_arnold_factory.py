#!/usr/bin/env rmanpy
'''
Arnold for maya render job
Arnold 4.2.16.4 darwin clang-3.9.1 oiio-1.7.7 rlm-12.0.2 2017/05/16 12:59:36

Usage:
  kick [option] [option] [option] ...

Options:
  -i <s>          Input .ass file
  -o <s>          Output filename
  -of <s>         Output format: exr jpg png tif
  -r <n n>        Image resolution
  -sr <f>         Scale resolution <f> times in each dimension
  -rg <n n n n>   Render region (minx miny maxx maxy)
  -as <n>         Anti-aliasing samples
  -af <s> <f>     Anti-aliasing filter and width (box disk gaussian ...)
  -asc <f>        Anti-aliasing sample clamp
  -c <s>          Active camera
  -sh <f f>       Motion blur shutter (start end)
  -fov <f>        Camera FOV
  -e <f>          Camera Exposure
  -ar <f>         Aspect ratio
  -g <f>          Output gamma
  -tg <f>         Texture gamma
  -lg <f>         Light source gamma
  -sg <f>         Shader gamma
  -t <n>          Threads
  -bs <n>         Bucket size
  -bc <s>         Bucket scanning (top bottom left right random woven spiral hilbert)
  -td <n>         Total ray depth
  -rfl <n>        Reflection depth
  -rfr <n>        Refraction depth
  -dif <n>        Diffuse depth
  -glo <n>        Glossy depth
  -ds <n>         Diffuse samples
  -gs <n>         Glossy samples
  -d <s.s>        Disable (ignore) a specific node or node.parameter
  -it             Ignore texture maps
  -is             Ignore shaders
  -cm <s>         Set the value of ai_default_reflection_shader.color_mode (use with -is)
  -sm <s>         Set the value of ai_default_reflection_shader.shade_mode (use with -is)
  -om <s>         Set the value of ai_default_reflection_shader.overlay_mode (use with -is)
  -ib             Ignore background shaders
  -ia             Ignore atmosphere shaders
  -il             Ignore lights
  -id             Ignore shadows
  -isd            Ignore mesh subdivision
  -idisp          Ignore displacement
  -ibump          Ignore bump-mapping
  -imb            Ignore motion blur
  -idof           Ignore depth of field
  -isss           Ignore sub-surface scattering
  -idirect        Ignore direct lighting
  -flat           Flat shading
  -sd <n>         Max subdivisions
  -set <s.s> <s>  Set the value of a node parameter (-set name.parameter value)
  -dw             Disable render window (recommended for batch rendering)
  -dp             Disable progressive rendering (recommended for batch rendering)
  -ipr [m|q]      Interactive rendering mode, using Maya (default) or Quake/WASD controls
  -turn <n>       Render n frames rotating the camera around the lookat point
  -v <n>          Verbose level (0..6)
  -nw <n>         Maximum number of warnings
  -log            Enable log file
  -logfile <s>    Enable log file and write to the specified file path
  -l <s>          Add search path for plugin libraries
  -nodes [n|t]    List all installed nodes, sorted by Name (default) or Type
  -info [n|u] <s> Print detailed information for a given node, sorted by Name or Unsorted (default)
  -tree <s>       Print the shading tree for a given node
  -repeat <n>     Repeat the render n times (useful for debugging)
  -resave <s>     Re-save .ass scene to filename
  -db             Disable binary encoding when re-saving .ass files (useful for debugging)
  -forceexpand    Force single-threaded expansion of procedural geometry before rendering or re-saving
  -nstdin         Ignore input from stdin
  -nokeypress     Disable wait for ESC keypress after rendering to display window
  -sl             Skip license check (assume license is not available)
  -licensecheck   Check the connection with the license servers and list installed licenses
  -utest          Run unit tests for the Arnold API
  -av             Print Arnold version number
  -notices        Display copyright notices
  -h, --help      Show this help message

where <n>=integer, <f>=float, <s>=string

Example:
  kick -i teapot.ass -r 640 480 -g 2.2 -o teapot.tif

(c) 2001-2009 Marcos Fajardo and (c) 2009-2016 Solid Angle SL, www.solidangle.com
Acknowledgements: armengol ben brian cliff colman erco francisco quarkx rene scot sergio xray yiotis

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



'''


# TODO

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

class Job(object):
    def __init__(self):
        # The payload of gui-data needed to describe a farm render job
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
            logger.warn("Cant get user credentials: {}".format(err))

        self.mayaprojectfullpath=None
        self.mayascenefullpath=None

        self.farmtier=None

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
        self.rendermanversion=None
        self.shotgunProject=None
        self.shotgunSequence=None
        self.shotgunShot=None
        self.shotgunTask=None
        self.shotgunProjectId=None
        self.shotgunSequenceId=None
        self.shotgunShotId=None
        self.shotgunTaskId=None
        self.sendToShotgun=False


class Render(object):
    '''
    Arnold job defined using the tractor api
    '''

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
        # self.rendermanpath = os.path.join( self.job.dabwork, self.job.envtype, self.job.envshow, self.job.envproject,"renderman", self.scenebasename)
        # self.rendermanpathalias = "$DABRENDER/$TYPE/$SHOW/$PROJECT/renderman/$SCENENAME"
        self.renderdirectory = os.path.join(self.rendermanpath,"images")
        # self.renderimagesalias = "$DABRENDER/$TYPE/$SHOW/$PROJECT/renderman/$SCENENAME/images"
        self.mayaversion = self.job.mayaversion,
        # self.rendermanversion = self.job.rendermanversion,
        # self.envkey_rms = "rms-{}-maya-{}".format(self.rendermanversion[0], self.mayaversion[0])
        # self.envkey_rfm = "rfm-{}-maya-{}".format(self.rendermanversion[0], self.mayaversion[0])
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
        # self.ribpath = "{}/rib".format(self.rendermanpath)
        self.finaloutputimagebase = "{}/{}".format(self.rendermanpath,self.scenebasename)
        # self.proxyoutput = "$DABRENDER/$TYPE/$SHOW/$PROJECT/movies/$SCENENAME_{}.mov".format("datehere")
        self.thedate=time.strftime("%d-%B-%Y")


    def build(self):
        '''
        Main method to build the job
        :return:
        '''
        # ################ 0 JOB ################
        self.renderjob = self.job.env.author.Job(title="RM: {} {} {}-{}".format(
              self.job.username,self.scenename,self.startframe,self.endframe),
              priority=10,
              envkey=[self.envkey_rfm,"ProjectX",
                    "TYPE={}".format(self.job.envtype),
                    "SHOW={}".format(self.job.envshow),
                    "PROJECT={}".format(self.job.envproject),
                    "SCENE={}".format(self.job.envscene),
                    "SCENENAME={}".format(self.scenebasename)],
              metadata="email={} username={} usernumber={}".format(self.job.useremail,self.job.username,self.job.usernumber),
              comment="User is {} {} {}".format(self.job.useremail,self.job.username,self.job.usernumber),
              projects=[str(self.projectgroup)],
              tier=str(self.job.farmtier),
              tags=["theWholeFarm", ],
              service="")


        # ############## 0 ThisJob #################
        task_thisjob = self.job.env.author.Task(title="Arnold Job")
        task_thisjob.serialsubtasks = 1

        # ############## 5 NOTIFY JOB START ###############
        if self.optionsendjobstartemail:
            logger.info("email = {}".format(self.job.useremail))
            task_notify_start = self.job.env.author.Task(title="Notify Start", service="ShellServices")
            task_notify_start.addCommand(self.mail("JOB", "START", "{}".format(self.mayascenefilefullpath)))
            task_thisjob.addChild(task_notify_start)


        '''
        # ############## 1 PREFLIGHT ##############
        task_preflight = self.job.env.site.Task(title="Preflight")
        task_preflight.serialsubtasks = 1
        task_thisjob.addChild(task_preflight)
        task_generate_rib_preflight = self.job.env.site.Task(title="Generate ASS Preflight")
        command_ribgen = self.job.env.site.Command(argv=["maya","-batch","-proj", self.mayaprojectpath,"-command",
                                              "renderManBatchGenRibForLayer {layerid} {start} {end} {phase}".format(
                                                  layerid=0, start=self.startframe, end=self.endframe, phase=1),
                                              "-file", self.mayascenefilefullpath],
                                              tags=["maya", "theWholeFarm"],
                                              atleast=int(self.threads),
                                              atmost=int(self.threads),
                                              service="RfMRibGen")
        task_generate_rib_preflight.addCommand(command_ribgen)
        task_preflight.addChild(task_generate_rib_preflight)
        task_render_preflight = self.job.env.site.Task(title="Render Preflight")

        command_render_preflight = self.job.env.site.Command(argv=[
                "prman","-t:{}".format(self.threads), "-Progress", "-recover", "%r", "-checkpoint", "5m",
                "-cwd", self.mayaprojectpath,
                "renderman/{}/rib/job/job.rib".format(self.scenebasename)],
                tags=["prman", "theWholeFarm"],
                atleast=int(self.threads),
                atmost=int(self.threads),
                service="PixarRender")

        task_render_preflight.addCommand(command_render_preflight)
        task_preflight.addChild(task_render_preflight)

        # ############## 3 RIBGEN ##############
        task_render_allframes = self.job.env.site.Task(title="ALL FRAMES {}-{}".format(self.startframe,self.endframe))
        task_render_allframes.serialsubtasks = 1
        task_ribgen_allframes = self.job.env.site.Task(title="RIB GEN {}-{}".format(self.startframe, self.endframe))

        # divide the frame range up into chunks
        _totalframes=int(self.endframe-self.startframe+1)
        _chunks = int(self.chunks)
        _framesperchunk=_totalframes
        if _chunks < _totalframes:
            _framesperchunk=int(_totalframes/_chunks)
        else:
            _chunks=1

        # loop thru chunks
        for i,chunk in enumerate(range(1,_chunks+1)):
            _offset=i*_framesperchunk
            _chunkstart=(self.startframe+_offset)
            _chunkend=(_offset+_framesperchunk)
            logger.info("Chunk {} is frames {}-{}".format(chunk, _chunkstart, _chunkend))

            if chunk == _chunks:
                _chunkend = self.endframe

            task_generate_rib = self.job.env.site.Task(title="RIB GEN chunk {} frames {}-{}".format(
                    chunk, _chunkstart, _chunkend ))
            command_generate_rib = self.job.env.site.Command(argv=[
                    "maya", "-batch", "-proj", self.mayaprojectpath, "-command",
                    "renderManBatchGenRibForLayer {layerid} {start} {end} {phase}".format(
                            layerid=0, start=_chunkstart, end=_chunkend, phase=2),
                            "-file", self.mayascenefilefullpath],
                    tags=["maya", "theWholeFarm"],
                    atleast=int(self.threads),
                    atmost=int(self.threads),
                    service="RfMRibGen")
            task_generate_rib.addCommand(command_generate_rib)
            task_ribgen_allframes.addChild(task_generate_rib)

        task_render_allframes.addChild(task_ribgen_allframes)


        # ############### 4 RENDER ##############
        task_render_frames = self.job.env.site.Task(title="RENDER Frames {}-{}".format(self.startframe,self.endframe))
        task_render_frames.serialsubtasks = 0

        for frame in range(self.startframe, (self.endframe + 1), self.byframe):
            _imgfile = "{proj}/{scenebase}.{frame:04d}.{ext}".format(
                proj=self.renderdirectory, scenebase=self.scenebasename, frame=frame, ext=self.outformat)
            _statsfile = "{proj}/rib/{frame:04d}/{frame:04d}.xml".format(
                proj=self.rendermanpath, frame=frame)
            _ribfile = "{proj}/rib/{frame:04d}/{frame:04d}.rib".format(
                proj=self.rendermanpath, frame=frame)

            task_render_rib = self.job.env.site.Task(title="RENDER Frame {}".format(frame),
                                          preview="sho {}".format(_imgfile),
                                          metadata="statsfile={} imgfile={}".format(_statsfile, _imgfile))
            commonargs = ["prman", "-cwd", self.mayaprojectpath]
            rendererspecificargs = []

            # ################ handle image resolution formats ###########
            if self.resolution == "720p":
                self.xres, self.yres = 1280, 720
                rendererspecificargs.extend(["-res", "%s" % self.xres, "%s" % self.yres])
            elif self.resolution == "1080p":
                self.xres, self.yres = 1920, 1080
                rendererspecificargs.extend(["-res", "%s" % self.xres, "%s" % self.yres])
            elif self.resolution == "540p":
                self.xres, self.yres = 960, 540
                rendererspecificargs.extend(["-res", "%s" % self.xres, "%s" % self.yres])
            elif self.resolution == "108p":
                self.xres, self.yres = 192, 108
                rendererspecificargs.extend(["-res", "%s" % self.xres, "%s" % self.yres])

            if self.rendermaxsamples != "FROMFILE":
                rendererspecificargs.extend([ "-maxsamples", "{}".format(self.rendermaxsamples) ])

            # if self.threadmemory != "FROMFILE":
            #     rendererspecificargs.extend([ "-memorylimit", "{}".format(self.threadmemory) ])

            rendererspecificargs.extend([
                # "-pad", "4",
                # "-memorylimit", self.threadmemory,  # mb
                "-t:{}".format(self.threads),
                "-Progress",
                "-recover", "%r",
                "-checkpoint", "5m",
                "-statslevel", "2",
                #"-maxsamples", "{}".format(self.rendermaxsamples)  # override RIB ray trace hider maxsamples
                # "-pixelvariance","3"      # override RIB PixelVariance
                # "-d", ""                  # dispType
                #                 -version          : print the version
                # "-progress    ",     : print percent complete while rendering
                # -recover [0|1]    : resuming rendering partial frames
                # -t:X              : render using 'X' threads
                # -woff msgid,...   : suppress error messages from provided list
                # -catrib file      : write RIB to 'file' without rendering
                # -ascii            : write RIB to ASCII format file
                # -binary           : write RIB to Binary format file
                # -gzip             : compress output file
                # -capture file     : write RIB to 'file' while rendering
                # -nobake           : disallow re-render baking
                # -res x y[:par]    : override RIB Format
                # -crop xmin xmax ymin ymax
                #                   : override RIB CropWindow
                # -maxsamples i     : override RIB ray trace hider maxsamples
                # -pixelvariance f  : override RIB PixelVariance
                # -d dispType       : override RIB Display type
                # -statsfile f      : override RIB stats file & level (1)
                # -statslevel i     : override RIB stats level
                # -memorylimit f    : override RIB to set memory limit ratio
                # -checkpoint t[,t] : checkpoint interval and optional exit time
            ])
            userspecificargs = [ utils.expandargumentstring(self.options),"{}".format(_ribfile)]
            finalargs = commonargs + rendererspecificargs + userspecificargs
            command_render = self.job.env.site.Command(argv=finalargs,
                                            tags=["prman", "theWholeFarm"],
                                            atleast=int(self.threads),
                                            atmost=int(self.threads),
                                            service="PixarRender")
            task_render_rib.addCommand(command_render)

            # ############## 5 NOTIFY Task END ###############
            if self.optionsendtaskendemail:
                task_render_rib.addCommand(self.mail("TASK FRAME {}".format(frame), "END", "{}".format(self.mayascenefilefullpath)))

            task_render_frames.addChild(task_render_rib)

        task_render_allframes.addChild(task_render_frames)
        task_thisjob.addChild(task_render_allframes)

        '''
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
            _outmov = os.path.join(self.mayaprojectpath, _mov)
            _inseq = "{}.####.exr".format(self.scenebasename)    #cameraShape1/StillLife.####.exr"
            _directory = "{}/renderman/{}/images".format(self.mayaprojectpath, self.scenebasename)
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
                task_proxy = self.job.env.author.Task(title="Proxy Generation")
                proxycommand = self.job.env.author.Command(argv=_rvio_cmd, service="Transcoding",tags=["rvio", "theWholeFarm"], envkey=["rvio"])
                task_proxy.addCommand(proxycommand)
                task_thisjob.addChild(task_proxy)

            except Exception, proxyerror:
                logger.warn("Cant make a proxy {}".format(proxyerror))

        else:
            logger.info("make proxy = {}".format(self.makeproxy))

        # ############## 6 SEND TO SHOTGUN ###############
        if self.job.sendToShotgun:
            logger.info("Sending to Shotgun = {} {} {} {}".format(self.job.shotgunProjectId,self.job.shotgunSequenceId,self.job.shotgunShotId,self.job.shotgunTaskId))
            _description = "Auto Uploaded from {} {} {} {}".format(self.job.envtype,self.job.envproject, self.job.envshow,self.job.envscene)
            _uploadcmd = ""
            if self.job.shotgunTaskId:
                _uploadcmd = ["shotgunupload.py",
                              "-o", self.job.shotgunOwnerId,
                              "-p", self.job.shotgunProjectId,
                              "-s", self.job.shotgunShotId,
                              "-t", self.job.shotgunTaskId,
                              "-n", _mov,
                              "-d", _description,
                              "-m", _outmov ]
            elif not self.job.shotgunTaskId:
                _uploadcmd = ["shotgunupload.py",
                              "-o", self.job.shotgunOwnerId,
                              "-p", self.job.shotgunProjectId,
                              "-s", self.job.shotgunShotId,
                              "-n", _mov,
                              "-d", _description,
                              "-m", _outmov ]
            task_upload = self.job.env.author.Task(title="SHOTGUN Upload P:{} SQ:{} SH:{} T:{}".format( self.job.shotgunProject,self.job.shotgunSequence,self.job.shotgunShot, self.job.shotgunTask))
            uploadcommand = self.job.env.author.Command(argv=_uploadcmd, service="ShellServices",tags=["shotgun", "theWholeFarm"], envkey=["PixarRender"])
            task_upload.addCommand(uploadcommand)
            task_thisjob.addChild(task_upload)



        # ############## 5 NOTIFY JOB END ###############
        if self.optionsendjobendemail:
            logger.info("email = {}".format(self.job.useremail))
            task_notify_end = self.job.env.author.Task(title="Notify End", service="ShellServices")
            task_notify_end.addCommand(self.mail("JOB", "COMPLETE", "{}".format(self.mayascenefilefullpath)))
            task_thisjob.addChild(task_notify_end)

        self.renderjob.addChild(task_thisjob)

    def validate(self):
        logger.info("\n\n{:_^80}\n{}\n{:_^80}".format("snip", self.renderjob.asTcl(), "snip"))

    def mail(self, level="Level", trigger="Trigger", body="Render Progress Body"):
        bodystring = "Arnold Render Progress: \nLevel: {}\nTrigger: {}\n\n{}".format(level, trigger, body)
        subjectstring = "FARM JOB: {} {} {} {}".format(level,trigger, str(self.scenebasename), self.job.username)
        mailcmd = self.job.env.author.Command(argv=["sendmail.py", "-t", "%s"%self.job.useremail, "-b", bodystring, "-s", subjectstring], service="ShellServices")
        return mailcmd

    def spool(self):
        # double check scene file exists
        logger.info("Double Checking: {}".format(os.path.expandvars(self.mayascenefilefullpath)))
        if os.path.exists(os.path.expandvars(self.mayascenefilefullpath)):
            try:
                logger.info("Spooled correctly")
                # all jobs owner by pixar user on the farm
                self.renderjob.spool(owner=self.job.env.config.getdefault("tractor","jobowner"),port=int(self.job.env.config.getdefault("tractor","port")))

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








