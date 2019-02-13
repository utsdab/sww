'''
DABMLB0606627MG:testProject01 120988$

hrender /Users/Shared/UTS_Jobs/TESTING_HOUDINI/HoudiniProjects/testProject01/scripts/torus1.hipnc
 -d mantra1 -v -f 1 240 -i 1

Usage:

Single frame:   hrender    [options] driver|cop file.hip [imagefile]
Frame range:    hrender -e [options] driver|cop file.hip

driver|cop:     -c /img/imgnet
                -c /img/imgnet/cop_name
                -d output_driver

options:        -w pixels       Output width
                -h pixels       Output height
                -F frame        Single frame
                -b fraction     Image processing fraction (0.01 to 1.0)
		-t take		Render a specified take
                -o output       Output name specification
                -v              Run in verbose mode
                -I              Interleaved, hscript render -I

with "-e":	-f start end    Frame range start and end
                -i increment    Frame increment

Notes:  1)  For output name use $F to specify frame number (e.g. -o $F.pic).
        2)  If only one of width (-w) or height (-h) is specified, aspect ratio
            will be maintained based upon aspect ratio of output driver.

Error: Cannot specify frame range without -e.




mantra -f frame0001.ifd rendered_frame0001.pic



'''

# ##############################################################
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
sh = logging.StreamHandler()
sh.setLevel(logging.INFO)
formatter = logging.Formatter('%(levelname)5.5s \t%(name)s \t%(message)s')
sh.setFormatter(formatter)
logger.addHandler(sh)
# ##############################################################

import json
import os
import time
import sys
import utils_factory as utils
import environment_factory as envfac
import logging

class Job(envfac.TractorJob):
    ''' The payload of gui-data needed to describe a rfm render job '''
    def __init__(self):
        super(Job, self).__init__()
        self.projectfullpath=None
        self.scenefilefullpath=None
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

        self.projectfullpath=None
        self.scenefilefullpath=None

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
        self.houdiniversion=None
        self.rendermanversion=None
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
    ''' Mantra job defined using the tractor api '''

    def __init__(self, job):
        self.job=job

        utils.printdict( self.job.__dict__)

        self.job.dabwork="$DABWORK"

        self.projectpathalias = "$DABRENDER/$TYPE/$SHOW/$PROJECT"
        self.projectpath = os.path.join(self.job.dabwork, self.job.envtype, self.job.envshow, self.job.envproject)
        self.job.envprojectalias = "$PROJECT"
        self.scenefilefullpathalias = "$DABRENDER/$TYPE/$SHOW/$PROJECT/$SCENE"
        self.scenefilefullpath = os.path.join( self.job.dabwork, self.job.envtype, self.job.envshow,
                                                   self.job.envproject,self.job.envscene)
        self.scenename = os.path.basename(self.job.envscene)
        self.scenebasename = os.path.splitext(self.scenename)[0]
        self.sceneext = os.path.splitext(self.scenename)[1]
        self.renderpath = os.path.join( self.job.dabwork, self.job.envtype, self.job.envshow, self.job.envproject,"houdini", self.scenebasename)
        self.renderpathalias = "$DABRENDER/$TYPE/$SHOW/$PROJECT/$SCENENAME"
        self.renderdirectory = os.path.join(self.renderpath,"images")
        self.renderimagesalias = "$DABRENDER/$TYPE/$SHOW/$PROJECT/$SCENENAME/images"
        self.houdiniversion = self.job.houdiniversion,
        self.envkey_houdini = "houdini{}".format(self.houdiniversion[0])
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
        self.finaloutputimagebase = "{}/{}".format(self.renderpath,self.scenebasename)
        # self.proxyoutput = "$DABRENDER/$TYPE/$SHOW/$PROJECT/movies/$SCENENAME_{}.mov".format("datehere")
        self.thedate=time.strftime("%d-%B-%Y")


    def build(self):
        '''
        Main method to build the job
        '''
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
        self.renderjob = self.job.author.Job(title="HOU: {} {} {}-{}".format(
              self.job.username, self.scenename, self.job.jobstartframe, self.job.jobendframe),
              priority=10,
              envkey=[self.envkey_houdini,"ProjectX",
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
                                                      "HOUDINI REGISTER",
                                                      "{na}".format(na=self.job.username),
                                                      "{na} {no} {em} {sc}".format(na=self.job.username, no=self.job.usernumber,em=self.job.useremail, sc=self.scenefilefullpath)))
        task_thisjob.addChild(task_notify_admin_start)


        # ############## 5 NOTIFY USER OF JOB START ###############
        if self.optionsendjobstartemail:
            logger.info("email = {}".format(self.job.useremail))
            task_notify_start = self.job.author.Task(title="Notify Start", service="ShellServices")
            task_notify_start.addCommand(self.mail(self.job.useremail, "JOB", "START", "{}".format(self.scenefilefullpath)))
            task_thisjob.addChild(task_notify_start)


        # ####### make a render directory - mayaproj/arnold/scene/[ass,images]
        _proj = self.projectpath
        _arnolddir = os.path.join(self.projectpath,"houdini")
        _arnoldWorkDir = os.path.join(_arnolddir, self.scenebasename)
        _assDir = os.path.join(_arnoldWorkDir,"ifd")
        _imgDir = os.path.join(_arnoldWorkDir,"images")
        _assFileBase = "{}.ass".format(self.scenebasename)


        task_prefilight = self.job.author.Task(title="Make render directory")
        command_mkdirs1 = self.job.author.Command(argv=[ "mkdir","-p", _arnolddir ],
                    tags=["houdini", "theWholeFarm"],
                    atleast=1,
                    atmost=1,
                    service="Houdini")
        command_mkdirs2 = self.job.author.Command(argv=[ "mkdir","-p", _arnoldWorkDir ],
                    tags=["houdini", "theWholeFarm"],
                    atleast=1,
                    atmost=1,
                    service="Houdini")
        command_mkdirs3 = self.job.author.Command(argv=[ "mkdir","-p", _assDir ],
                    tags=["houdini", "theWholeFarm"],
                    atleast=1,
                    atmost=1,
                    service="Houdini")
        command_mkdirs4 = self.job.author.Command(argv=[ "mkdir", "-p",_imgDir ],
                    tags=["houdini", "theWholeFarm"],
                    atleast=1,
                    atmost=1,
                    service="Houdini")
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

        #TODO not needed now - can use quotes
        __command = "arnoldExportAss"


        # loop thru chunks
        for i, chunk in enumerate(range( 1, _chunks + 1 )):
            _offset = i * _framesperchunk
            _chunkstart = int(self.job.jobstartframe) + _offset
            _chunkend = _chunkstart + _framesperchunk - 1

            if chunk >= _chunks:
                _chunkend = int(self.job.jobendframe)

            task_generate_ifd = self.job.author.Task(title="IFD GEN chunk {} frames {}-{}".format(
                    chunk, _chunkstart, _chunkend ))

            #TODO is this hrender
            command_generate_ifd = self.job.author.Command(argv=[
                    "hbatch", "-proj", self.projectpath, "-command",
                    "{command} -f \"{file}\" -startFrame {start} -endFrame {end}".format(
                            command=__command, file=os.path.join(_assDir,self.scenebasename), start=_chunkstart, end=_chunkend, step=1),
                            "-file", self.scenefilefullpath],
                    tags=["houdini", "theWholeFarm"],
                    atleast=int(self.threads),
                    atmost=int(self.threads),
                    service="Houdini")
            task_generate_ifd.addCommand(command_generate_ifd)
            task_assgen_allframes.addChild(task_generate_ifd)

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
            _ifdfile = "{base}.{frame:04d}.ifd".format(base=os.path.join(_assDir,self.scenebasename), frame=frame)

            _outfile = "{base}.{frame:04d}.exr".format(base=os.path.join(_imgDir,self.scenebasename), frame=frame)
            _shotgunupload = "PR:{} SQ:{} SH:{} TA:{}".format(self.job.shotgunProject,
                                                  self.job.shotgunSeqAssetType,
                                                  self.job.shotgunShotAsset,
                                                  self.job.shotgunTask)

            _taskMetaData={}
            _taskMetaData["imgfile"] = _outfile
            # _taskMetaData["statsfile"] = _statsfile
            _taskMetaData["ifdfile"] = _ifdfile
            _taskMetaData["shotgunupload"] = _shotgunupload
            _jsontaskMetaData = json.dumps(_taskMetaData)
            _title = "RENDER Frame {}".format(frame)
            # _preview = "sho {""}".format(_imgfile)

            task_render_ifd = self.job.author.Task(title=_title, metadata=_jsontaskMetaData)

            '''
             mantra -f frame.0001.ifd rendered_frame0001.pic
            '''

            commonargs = ["mantra", "-f", _ifdfile, _outfile]
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
                                            tags=["mantra", "theWholeFarm"],
                                            atleast=int(self.threads),
                                            atmost=int(self.threads),
                                            service="Houdini")
            task_render_ifd.addCommand(command_render)

            # ############## 5 NOTIFY Task END ###############
            if self.optionsendtaskendemail:
                task_render_ifd.addCommand(self.mail("TASK FRAME {}".format(frame), "END", "{}".format(
                    self.scenefilefullpath)))

            task_render_frames.addChild(task_render_ifd)

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
            _outmov = os.path.join(self.projectpath,"movies",_mov)
            _inseq = "{}.####.exr".format(self.scenebasename)    #cameraShape1/StillLife.####.exr"
            _directory = "{}/arnold/{}/images".format(self.projectpath, self.scenebasename)
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
            task_notify_end.addCommand(self.mail(self.job.useremail, "JOB", "COMPLETE", "{}".format(self.scenefilefullpath)))
            task_thisjob.addChild(task_notify_end)

        self.renderjob.addChild(task_thisjob)

    def validate(self):
        logger.info("\n\n{:_^80}\n{}\n{:_^80}".format("snip", self.renderjob.asTcl(), "snip"))

    def mail(self, to=None, level="Level", trigger="Trigger", body="Render Progress Body"):
        if not to:
            to = self.job.adminemail
        bodystring = "Houdini Render Progress: \nLevel: {}\nTrigger: {}\n\n{}".format(level, trigger, body)
        subjectstring = "FARM JOB: {} {} {} {}".format(level,trigger, str(self.scenebasename), self.job.username)
        mailcmd = self.job.author.Command(argv=["sendmail.py", "-t", "%s"%self.job.useremail, "-b", bodystring, "-s", subjectstring], service="ShellServices")
        return mailcmd

    def spool(self):
        # double check scene file exists
        logger.info("Double Checking: {}".format(os.path.expandvars(self.scenefilefullpath)))
        if os.path.exists(os.path.expandvars(self.cenefilefullpath)):
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


###############################################################################

if __name__ == "__main__":
    logger.setLevel(logging.INFO)
    # logger.info("START TESTING")
    #
    #
    #
    # TEST = Render(
    #                    envdabrender="/Volumes/dabrender",
    #                    envproject="testFarm",
    #                    envshow="matthewgidney",
    #                    envscene="dottyrms.ma",
    #                    envtype="user_work",
    #                    # seqfullpath="/usr/local/tmp/scene/file.ma",
    #                    # mayaprojectpath="/usr/local/tmp/",
    #                    # mayaversion="2016",
    #                    # rendermanversion="20.2",
    #                    startframe=1,
    #                    endframe=12,
    #                    byframe=1,
    #                    outformat="exr",
    #                    resolution="540p",
    #                    options="",
    #                    skipframes=1,
    #                    makeproxy=1,
    #                    threadmemory="4000",
    #                    rendermaxsamples="128",
    #                    threads="4",
    #                    ribgenchunks=3,
    #                    email=[1, 0, 0, 0, 1, 0]
    # )
    # TEST.build()
    # TEST.validate()
    # logger.info("FINISHED TESTING")
