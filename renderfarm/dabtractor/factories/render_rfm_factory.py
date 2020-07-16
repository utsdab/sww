#!/usr/bin/env python2
''' Renderman for maya job '''

# TODO  wrap the rib command up in a sanity checker script.
# TODO  dab_rfm_pre_render.mel

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
    ''' The payload of gui-data needed to describe the render job '''
    def __init__(self):
        super(Job, self).__init__()
        self.projectfullpath=None
        self.scenefullpath=None
        # This gets department from shotgun and checks it is a valid one in the json file
        # the department is year1 or year2 etc a user can only be in one department.
        if self.department in self.config.getoptions("renderjob", "projectgroup"):
            logger.info("Department {}".format(self.department))
        else:
            self.department="Other"
        self.adminemail = self.config.getdefault("admin", "email")
        logger.info("admin is {}".format(self.adminemail))


class Render(object):
    ''' Renderman job defined using the tractor api '''
    def __init__(self, job):
        self.job=job
        # utils.printdict( self.job.__dict__)
        self.job.dabwork="$DABWORK"
        self.projectpathalias = "$DABRENDER/$TYPE/$SHOW/$PROJECT"
        self.job.envprojectalias = "$PROJECT"
        self.scenefilefullpathalias = "$DABRENDER/$TYPE/$SHOW/$PROJECT/$SCENE"
        self.renderpathalias = "$DABRENDER/$TYPE/$SHOW/$PROJECT/renderman/$SCENENAME"
        self.renderimagesalias = "$DABRENDER/$TYPE/$SHOW/$PROJECT/renderman/$SCENENAME/images"

        self.projectpath = os.path.join(self.job.dabwork, self.job.envtype, self.job.envshow, self.job.envproject)
        self.scenefilefullpath = os.path.join( self.job.dabwork, self.job.envtype, self.job.envshow,self.job.envproject,self.job.envscene)
        self.scenename = os.path.basename(self.job.envscene)
        self.scenebasename = os.path.splitext(self.scenename)[0]
        self.sceneext = os.path.splitext(self.scenename)[1]
        self.renderpath = os.path.join( self.job.dabwork, self.job.envtype, self.job.envshow, self.job.envproject, "renderman", self.scenebasename)
        # self.renderdirectory = os.path.join(self.renderpath,"images")
        self.envkey_rfm = "rfm-{}".format(self.job.rendermanversion)
        self.envkey_prman = "prman-{}".format(self.job.rendermanversion)
        self.envkey_maya = "maya{}".format(self.job.mayaversion)
        self.options = ""
        self.outformat = "exr"
        self.ribpath = "{}/rib".format(self.renderpath)
        self.finaloutputimagebase = "{}/{}".format(self.renderpath,self.scenebasename)
        self.thedate=time.strftime("%d-%B-%Y")

    def build(self):
        ''' Main method to build the job '''
        logger.info("Starting job BUILD")

        # ################# Job Metadata as JSON
        _jobMetaData={}
        _jobMetaData["email"] = self.job.useremail
        _jobMetaData["name"] = self.job.username
        _jobMetaData["number"] = self.job.usernumber
        _jobMetaData["scenename"] = self.scenename
        _jobMetaData["projectpath"] = self.projectpath
        _jobMetaData["startframe"] = self.job.jobstartframe
        _jobMetaData["endframe"] = self.job.jobendframe
        _jobMetaData["jobtype"] = "RFM"
        _jsonJobMetaData = json.dumps(_jobMetaData)

        # ################ 0 JOB ################
        self.renderjob = self.job.author.Job(title="RFM: {} {} {}-{}".format(
              self.job.username, self.scenename, self.job.jobstartframe, self.job.jobendframe),
              priority=10,
              envkey=[self.envkey_rfm,self.envkey_maya,"ProjectX",
                    "TYPE={}".format(self.job.envtype),
                    "SHOW={}".format(self.job.envshow),
                    "PROJECT={}".format(self.job.envproject),
                    "SCENE={}".format(self.job.envscene),
                    "SCENENAME={}".format(self.scenebasename)],
              metadata=_jsonJobMetaData,
              comment="User is {} {} {}".format(self.job.useremail,self.job.username,self.job.usernumber),
              projects=[str(self.job.department)],
              tier=str(self.job.farmtier),
              tags=["thewholefarm", ],
              service="")


        # ############## 0 ThisJob #################
        task_job = self.job.author.Task(title="Renderman For Maya Job")
        task_job.serialsubtasks = 1

        # ############## 4 NOTIFY ADMIN OF TASK START ##########
        logger.info("admin email = {}".format(self.job.adminemail))
        task_notify_admin_start = self.job.author.Task(title="REGISTER", service="shellservices")
        task_notify_admin_start.addCommand(self.mail(self.job.adminemail,"RFM REGISTER","{na}".format(na=self.job.username), "{na} {no} {em} {sc}".format(na=self.job.username, no=self.job.usernumber,em=self.job.useremail,sc=self.scenefilefullpath)))
        task_job.addChild(task_notify_admin_start)

        # ############## 5 NOTIFY USER OF JOB START ###############
        if self.job.optionsendjobstartemail:
            logger.info("email = {}".format(self.job.useremail))
            task_notify_start = self.job.author.Task(title="NOTIFY Start", service="shellservices")
            task_notify_start.addCommand(self.mail(self.job.useremail, "JOB", "START", "{}".format(self.scenefilefullpath)))
            task_job.addChild(task_notify_start)

        # ############## 1 PREFLIGHT ##############
        task_preflight = self.job.author.Task(title="PREFLIGHT", service="PixarRender")
        task_preflight.serialsubtasks = 1
        # ### txmake
        task_generate_textures_preflight = self.job.author.Task(title="_TEXTURES")
        # command_txmake = self.job.author.Command(argv=[
        #     "txmake","-smode","periodic","-tmode","periodic","-format","pixar","threads"
        #     "-filter","catmull-rom","-resize","up-","-compression","lossless","-newer","infile","outfile",],
        #     tags=["maya", "thewholefarm"], atleast=int(self.job.jobthreads),  atmost=int(self.job.jobthreads), service="PixarRender",envkey=[self.envkey_rfm])
        #TODO  handle texture making

        command_txmake = self.job.author.Command(
            argv=["ls","-l",],
            tags=["maya", "thewholefarm"],
            atleast=int(self.job.jobthreads),
            atmost=int(self.job.jobthreads),
            service="PixarRender",
            envkey=[self.envkey_rfm])

        task_generate_textures_preflight.addCommand(command_txmake)
        task_preflight.addChild(task_generate_textures_preflight)
        task_job.addChild(task_preflight)

        # ############## 3 GENERATE INTERMEDIATE FILES ##############
        task_render_allframes = self.job.author.Task(title="RENDER FRAMES")
        task_render_allframes.serialsubtasks = 1
        task_ribgen_allframes = self.job.author.Task(title="RIBGEN {}-{}".format(self.job.jobstartframe, self.job.jobendframe))


        # divide the frame range up into chunks
        _totalframes = int(self.job.jobendframe) - int(self.job.jobstartframe) + 1
        _chunks = int(self.job.jobchunks)
        _framesperchunk = _totalframes
        if _chunks < _totalframes:
            _framesperchunk = int( _totalframes / _chunks )
        else:
            _chunks = 1

        for i, chunk in enumerate(range( 1, _chunks + 1 )):
            _offset = i * _framesperchunk
            _chunkstart = int(self.job.jobstartframe) + _offset
            _chunkend = _chunkstart + _framesperchunk - 1
            if chunk >= _chunks:
                _chunkend = int(self.job.jobendframe)
            logger.info("Chunk {} is frames {}-{}".format(chunk, _chunkstart, _chunkend))
            task_generate_rib = self.job.author.Task(title="_RIBGEN Chunk {} frames {}-{}".format( chunk, _chunkstart, _chunkend ))

            command_generate_rib = self.job.author.Command(
                argv=[
                "Render", "-r","renderman", "-rib",
                "-proj", self.projectpath,
                "-preRender", "dab_rfm_pre_render_mel",
                "-t", str(self.job.jobthreads),
                "-s", str(_chunkstart),
                "-e", str(_chunkend),
                "-b", str(self.job.jobbyframe),
                self.scenefilefullpath],
                tags=["maya", "thewholefarm"],
                atleast=int(self.job.jobthreads),
                atmost=int(self.job.jobthreads),
                service="RfMRibGen",
                envkey=[self.envkey_rfm,self.envkey_maya])

            task_generate_rib.addCommand(command_generate_rib)
            task_ribgen_allframes.addChild(task_generate_rib)

        task_render_allframes.addChild(task_ribgen_allframes)

        # ############### 4 RENDER ##############
        task_render_frames = self.job.author.Task(title="RENDER {}-{}".format(self.job.jobstartframe,self.job.jobendframe))
        task_render_frames.serialsubtasks = 0
        for frame in range( int(self.job.jobstartframe), int(self.job.jobendframe) + 1, int(self.job.jobbyframe) ):
            # ################# Job Metadata as JSON
            _imgfile = "{proj}/images/{scenebase}/{scenebase}_beauty.{frame:04d}.{ext}".format( proj=self.projectpath, scenebase=self.scenebasename, frame=frame, ext=self.outformat)
            _statsfile = "{proj}/renderman/rib/{scenebase}/{scenebase}.{frame:04d}.xml".format( proj=self.projectpath, scenebase=self.scenebasename,frame=frame)
            _ribfile = "{proj}/renderman/rib/{scenebase}/{scenebase}.{frame:04d}.rib".format( proj=self.projectpath,scenebase=self.scenebasename,frame=frame)
            _shotgunupload = "PR:{} SQ:{} SH:{} TA:{}".format(self.job.shotgunProject,self.job.shotgunSeqAssetType,self.job.shotgunShotAsset,self.job.shotgunTask)
            _taskMetaData={}
            _taskMetaData["imgfile"] = _imgfile
            _taskMetaData["statsfile"] = _statsfile
            _taskMetaData["ribfile"] = _ribfile
            _taskMetaData["shotgunupload"] = _shotgunupload
            _jsontaskMetaData = json.dumps(_taskMetaData)
            _title = "_RENDER Frame {}".format(frame)
            _preview = "sho {}".format(_imgfile)

            task_render_rib = self.job.author.Task(title=_title, preview=_preview, metadata=_jsontaskMetaData)
            commonargs = [ "prman", "-cwd", self.projectpath ]
            rendererspecificargs = []
            rendererspecificargs.extend([
                "-t:{}".format(self.job.jobthreads),
                "-Progress",
                "-recover", "%r",
                "-checkpoint", "20m",
                "-statslevel", "2",
                "-res", "{}".format(self.job.xres), "{}".format(self.job.yres), ])
            userspecificargs = [ utils.expandargumentstring(self.options), "{}".format(_ribfile) ]
            finalargs = commonargs + rendererspecificargs + userspecificargs

            command_render = self.job.author.Command(
                argv=finalargs,
                tags=["prman", "thewholefarm"],
                atleast=int(self.job.jobthreads),
                atmost=int(self.job.jobthreads),
                service="PixarRender",
                envkey=[self.envkey_prman])
            task_render_rib.addCommand(command_render)

            task_render_frames.addChild(task_render_rib)
        task_render_allframes.addChild(task_render_frames)
        task_job.addChild(task_render_allframes)



    def validate(self):
        #TODO  check to see if there is already this job on the farm
        logger.info("Starting job VALIDATE")
        logger.info("\n\n{:_^80}\n{}\n{:_^80}".format("snip", self.renderjob.asTcl(),"snip"))
        logger.info("Ending job VALIDATE")

    def mail(self, to=None, level="Level", trigger="Trigger", body="Render Progress Body"):
        if not to:
            to = self.job.adminemail
        bodystring = "Prman Render Progress: \nLevel: {}\nTrigger: {}\n\n{}".format(level, trigger, body)
        subjectstring = "FARM JOB: {} {} {} {}".format(level,trigger, str(self.scenebasename), self.job.username)
        mailcmd = self.job.author.Command(
            argv=["sendmail.py", "-t", to, "-b", bodystring, "-s", subjectstring],
            service="shellservices")
        return mailcmd

    def spool(self):
        # double check scene file exists
        logger.info("Starting job SPOOL")
        logger.info("Double Checking: {}".format(os.path.expandvars(self.scenefilefullpath)))
        if os.path.exists(os.path.expandvars(self.scenefilefullpath)):
            try:
                logger.info("Spooled correctly")
                # all jobs owner by pixar user on the farm
                self.renderjob.spool(owner=self.job.config.getdefault("tractor","jobowner"),port=int(self.job.config.getdefault("tractor","port")))
            except Exception, spoolerr:
                logger.warn("A spool error %s" % spoolerr)
        else:
            message = "Maya scene file non existant %s" % self.scenefilefullpath
            logger.critical(message)
            logger.critical(os.path.normpath(self.scenefilefullpath))
            logger.critical(os.path.expandvars(self.scenefilefullpath))
            sys.exit(message)
        logger.info("Ending job SPOOL")


# ##############################################################################
if __name__ == "__main__":
    logger.setLevel(logging.DEBUG)
    logger.info("START TESTING")

    job = Job()

    '''
    Render -r renderman -h
    /Applications/Autodesk/maya2018/Maya.app/Contents/MacOS ~
    
    Usage: ./Render [options] filename
           where "filename" is a Maya ASCII or a Maya binary file.
    
    Common options:
      -help              Print help
      -test              Print Mel commands but do not execute them
      -verb              Print Mel commands before they are executed
      -keepMel           Keep the temporary Mel file
      -listRenderers     List all available renderers
      -renderer string   Use this specific renderer
      -r string          Same as -renderer
      -proj string       Use this Maya project to load the file
      -log string        Save output into the given file
      -rendersetuptemplate string Apply a render setup template to your scene before command line rendering.  Only templates exported via File > Export All in the Render Setup editor are supported.  Render setting presets and AOVs are imported from the template.  Render settings and AOVs are reloaded after the template if the -rsp and -rsa flags are used in conjunction with this flag.
      -rst string        Same as -rendersetuptemplate
      -rendersettingspreset string Apply the scene Render Settings from this template file before command line rendering.  This is equivalent to performing File > Import Scene Render Settings in the Render Setup editor, then batch rendering.
      -rsp string        Same as -rendersettingspreset
      -rendersettingsaov string Import the AOVs from this json file before command line rendering.
      -rsa string        Same as -rendersettingsaov
    
    Specific options for renderer "renderman": RenderMan renderer
    
      -rib                          Output RIB instead of rendering images.
      -ribFile string               Enables rib output and specifies the output RIB file.
      -imageFile string             The output image file.
      -cam string                   The camera.
      -res int int                  The resoution.
      -crop float float float float Set the crop window of the final image
      -bake                         Do a bake pass rather than rendering images.  This causes         PxrBakeTexture nodes to write their output files.
      -checkpoint string            Checkpoint interval and optional exit time.
      -rd string                    Directory in which to store image files
      -of string                    Output image file format.  See the Render Settings window to find available formats
      -t int                        The number of threads to use for rendering.
      -jobid string                 The unique jobid (time stamp) to avoid overwriting older/concurent renders.
    Frame numbering options
      -s float                      Starting frame for an animation sequence
      -e float                      End frame for an animation sequence
      -b float                      By frame (or step) for an animation sequence
    Render Layers:
      -rl boolean|name(s)           Render each render layer separately
    Mel callbacks
      -preRender string             Mel code executed before rendering
      -postRender string            Mel code executed after rendering
      -preLayer string              Mel code executed before each render layer
      -postLayer string             Mel code executed after each render layer
      -preFrame string              Mel code executed before each frame
      -postFrame string             Mel code executed after each frame
      
      
    
    Maya Batch Rendering from the Command Line
    You may also use additional flags: -rl (render layer), -crop, -preRender, -postRender, -preLayer, -postLayer, -preFrame, -postFrame, -jobid
    
    From a command line use the following:
    
    Render -r renderman sceneFile
    It is also possible to only generate RIB without subsequently rendering.
    
    Render -r rib sceneFile
    A complete list of the options can also be seen by running:
    
    Render -r renderman -h
    If you get a warning like the following, you need to put rmanRenderer.xml and ribRenderer.xml from the RenderMan for Maya installation in a place where Maya can find it.
    
    Cannot open renderer description file "rendermanRenderer.xml"
    You can copy the files from the RenderMan for Maya installation,
    
    eg. C:/Program Files/Pixar/RenderManForMaya-22.0/etc/rendermanRenderer.xml
    Into the directory where Maya looks for these under the Maya installation,
    
    eg. C:/Program Files/Autodesk/Maya2018/bin/rendererDesc/
    Or you can set up the Maya environment variable called MAYA_RENDER_DESC_PATH so that rmanRenderer.xml and ribRenderer.xml will be found.
    
    Prman Rendering from the Command Line (Advanced)
    When doing a maya batch render, RenderMan for Maya generates RIB files and then prman (executable) is launched for those rib files.  However, you may already have RIB files on disk and just want to run prman on them.
    
    Job Structure
    The RIB files generated by RenderMan for Maya live within the maya project.   For example:
    
    <maya_project>/renderman/myscene/rib/
    RIB files are organized into subdirectories for each frame, like 0001, 0002, 0003.  There is also one subdirectory called "job" which is for caches of static objects, and processing commands that do not need to happen every frame, such as converting textures and cleanup.
    
    Here is an example of the commands that would typically happen for a three frame job.  Note the use of the -cwd arg to specify the maya project as the current working directory that prman should run out of.  The project relative path to the rib file is supplied as the last argument of the command.  Rib files contain project relative paths by default.
    
    prman -t:0 -cwd C:/Users/user/Documents/maya/projects/default/ renderman/test_0725120019/rib/job/job.rib
    prman -t:0 -cwd C:/Users/user/Documents/maya/projects/default/ renderman/test_0725120019/rib/0001/0001.rib
    prman -t:0 -cwd C:/Users/user/Documents/maya/projects/default/ renderman/test_0725120019/rib/0002/0002.rib
    prman -t:0 -cwd C:/Users/user/Documents/maya/projects/default/ renderman/test_0725120019/rib/0003/0003.rib
    prman -t:0 -cwd C:/Users/user/Documents/maya/projects/default/ renderman/test_0725120019/rib/job/post.rib
    Each frame rib file, like 0001.rib references other rib files located in the same directory, for each camera or render layer that is active for the frame.  Here is an example of typical contents of a frame directory:
    
    renderman/test_0725120019/rib/0001:
    0001.rib
    perspShape_Final.0001.rib
    perspShape_Final.0001.rlf
    perspShape_Final.0001.xml
    The file called 0001.rib is the "driver" RIB file for the frame.  It will reference RIB files for each pass (for different cameras or render layers) that occur in the frame.
    
    There are some files in the directory that aren't RIB files.  What are those?
    
    The user made RLF files (assigned for GPU archives) contain material and binding information.  Materials are injected into the RIB file by a RIF at render time.
    
    The XML file is generated during rendering.  It contains diagnostic information about the render.


    rvio cameraShape1/StillLife.####.exr  -v -fps 25
    -rthreads 4
    -outres 1280 720 -out8
    -leader simpleslate "UTS" "Artist=Anthony" "Show=Still_Life" "Shot=Testing"
    -overlay frameburn .4 1.0 30.0  -overlay matte 2.35 0.3 -overlay watermark "UTS 3D LAB" .2
    -outgamma 2.2
    -o cameraShape1_StillLife.mov



ffmpeg exr to mov

ffmpeg -y -i seq_v001.%04d.exr -vf lutrgb=r=gammaval(0.45454545):g=gammaval(0.45454545):b=gammaval(0.45454545) -vcodec libx264 -pix_fmt yuv420p -preset slow -crf 18 -r 25 out.mov

ffmpeg -y -gamma 2.2 -i seq_v001.%04d.exr -vcodec libx264 -pix_fmt yuv420p -preset slow -crf 18 -r 25 out.mov
-filter:v scale=720:-1

ffmpeg -y -gamma 2.2 -i rmf22_test_cube_textured_100.0001__perspShape_beauty.%04d.exr -vcodec libx264 -pix_fmt yuv420p -preset slow -crf 18 -filter:v scale=1280:720 -r 25 out.mov


    '''









