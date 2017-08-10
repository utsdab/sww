#!/usr/bin/env rmanpy
'''
Renderman for maya job

'''

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

class Job(object):
    def __init__(self):
        """
        The payload of gui-data needed to describe a rfm render job

        """
        self.usernumber = None
        self.username = None
        self.useremail = None

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

        if self.env.department in self.env.config.getoptions("renderjob", "projectgroup"):
            logger.info("Department {}".format(self.env.department))
        else:
            self.department="Other"

        self.farmpriority = None
        self.farmcrew = None

        self.jobtitle = None
        self.jobenvkey = None
        self.jobfile = None
        self.jobstartframe = None
        self.jobendframe = None
        self.jobchunks = None
        self.jobthreads = None
        self.jobthreadmemory = None

        self.optionskipframe = None
        self.optionmakeproxy = None
        # self.optionsendemail = None
        self.optionresolution = None
        self.optionmaxsamples = None

        self.envtype = None
        self.envshow = None
        self.envproject = None
        self.envscene = None

        self.mayaversion = None
        self.rendermanversion = None
        self.shotgunProject = None
        self.shotgunSeqAss = None
        self.shotgunShot = None
        self.shotgunClass = None
        # self.shotgunAsset = None
        # self.shotgunAssettype = None
        self.shotgunTask = None
        self.shotgunProjectId = None

        self.shotgunSeqAssId = None
        self.shotgunShotAssettypeId = None
        self.shotgunTaskId = None
        self.sendToShotgun = False


class Render(object):
    ''' Renderman job defined using the tractor api '''

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
        self.rendermanpath = os.path.join( self.job.dabwork, self.job.envtype, self.job.envshow, self.job.envproject,
                                           "renderman", self.scenebasename)
        self.rendermanpathalias = "$DABRENDER/$TYPE/$SHOW/$PROJECT/renderman/$SCENENAME"
        self.renderdirectory = os.path.join(self.rendermanpath,"images")
        self.renderimagesalias = "$DABRENDER/$TYPE/$SHOW/$PROJECT/renderman/$SCENENAME/images"
        self.mayaversion = self.job.mayaversion,
        self.rendermanversion = self.job.rendermanversion,
        # self.envkey_rms = "rms-{}-maya-{}".format(self.rendermanversion[0], self.mayaversion[0])
        self.envkey_rfm = "rfm-{}-maya-{}".format(self.rendermanversion[0], self.mayaversion[0])
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
        self.ribpath = "{}/rib".format(self.rendermanpath)
        self.finaloutputimagebase = "{}/{}".format(self.rendermanpath,self.scenebasename)
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
        self.renderjob = self.job.env.author.Job(title="RM: {} {} {}-{}".format(
              self.job.username, self.scenename, self.job.jobstartframe, self.job.jobendframe),
              priority=10,
              envkey=[self.envkey_rfm,"ProjectX",
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
        task_thisjob = self.job.env.author.Task(title="Renderman Job")
        task_thisjob.serialsubtasks = 1

        # ############## 5 NOTIFY JOB START ###############
        if self.optionsendjobstartemail:
            logger.info("email = {}".format(self.job.useremail))
            task_notify_start = self.job.env.author.Task(title="Notify Start", service="ShellServices")
            task_notify_start.addCommand(self.mail("JOB", "START", "{}".format(self.mayascenefilefullpath)))
            task_thisjob.addChild(task_notify_start)


        # ############## 1 PREFLIGHT ##############
        task_preflight = self.job.env.author.Task(title="Preflight")
        task_preflight.serialsubtasks = 1
        task_thisjob.addChild(task_preflight)

        task_permissions_preflight  = self.job.env.author.Task(title="Correct Permissions Preflight")
        task_generate_rib_preflight = self.job.env.author.Task(title="Generate RIB Preflight")

        # TODO  this will fail on the .DS files osx creates - need to wrap this up in a python try rxcept clause

        command_permissions1 = self.job.env.author.Command(argv=["chmod","-R","g+w", self.mayaprojectpath],
                                              tags=["chmod", "theWholeFarm"],
                                              atleast=int(self.threads),
                                              atmost=int(self.threads),
                                              service="RfMRibGen")

        command_permissions2 = self.job.env.author.Command(argv=["find",self.mayaprojectpath,"-type","d",
                                                                "-exec", "chmod", "g+s", "{}", "\;"],
                                              tags=["chmod", "theWholeFarm"],
                                              atleast=int(self.threads),
                                              atmost=int(self.threads),
                                              service="RfMRibGen")
        #TODO use command wrapper
        # dab_pre_render layerid start end phase
        __command = "dab_rfm_pre_render"
        # __command = "renderManBatchGenRibForLayer"

        command_ribgen = self.job.env.author.Command(argv=["maya","-batch","-proj", self.mayaprojectpath,"-command",
                                              "{command} {layerid} {start} {end} {phase}".format(
                                                  command=__command,
                                                  layerid=0, start=self.job.jobstartframe, end=self.job.jobendframe, phase=1),
                                              "-file", self.mayascenefilefullpath],
                                              tags=["maya", "theWholeFarm"],
                                              atleast=int(self.threads),
                                              atmost=int(self.threads),
                                              service="RfMRibGen")

        task_permissions_preflight.addCommand(command_permissions1)
        task_permissions_preflight.addCommand(command_permissions2)

        task_generate_rib_preflight.addCommand(command_ribgen)

        task_preflight.addChild(task_permissions_preflight)
        task_preflight.addChild(task_generate_rib_preflight)

        task_render_preflight = self.job.env.author.Task(title="Render Preflight")

        command_render_preflight = self.job.env.author.Command(argv=[
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
        task_render_allframes = self.job.env.author.Task(title="ALL FRAMES {}-{}".format(self.job.jobstartframe,
                                                                                         self.job.jobendframe))
        task_render_allframes.serialsubtasks = 1
        task_ribgen_allframes = self.job.env.author.Task(title="RIB GEN {}-{}".format(self.job.jobstartframe, self.job.jobendframe))

        # divide the frame range up into chunks
        _totalframes = int(self.job.jobendframe) - int(self.job.jobstartframe) + 1
        _chunks = int(self.chunks)
        _framesperchunk = _totalframes
        if _chunks < _totalframes:
            _framesperchunk = int( _totalframes / _chunks )
        else:
            _chunks = 1

        # loop thru chunks
        for i, chunk in enumerate(range( 1, _chunks + 1 )):
            _offset = i * _framesperchunk
            _chunkstart = int(self.job.jobstartframe) + _offset
            _chunkend = _offset+_framesperchunk
            logger.info("Chunk {} is frames {}-{}".format(chunk, _chunkstart, _chunkend))

            if chunk == _chunks:
                _chunkend = int(self.job.jobendframe)

            task_generate_rib = self.job.env.author.Task(title="RIB GEN chunk {} frames {}-{}".format(
                    chunk, _chunkstart, _chunkend ))


            command_generate_rib = self.job.env.author.Command(argv=[
                    "maya", "-batch", "-proj", self.mayaprojectpath, "-command",
                    "{command} {layerid} {start} {end} {phase}".format(command = __command,
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
        task_render_frames = self.job.env.author.Task(title="RENDER Frames {}-{}".format(self.job.jobstartframe,
                                                                                         self.job.jobendframe))
        task_render_frames.serialsubtasks = 0

        for frame in range( int(self.job.jobstartframe), int(self.job.jobendframe) + 1, int(self.job.jobbyframe) ):

            # ################# Job Metadata as JSON
            _imgfile = "{proj}/{scenebase}.{frame:04d}.{ext}".format(
                proj=self.renderdirectory, scenebase=self.scenebasename, frame=frame, ext=self.outformat)
            _statsfile = "{proj}/rib/{frame:04d}/{frame:04d}.xml".format(
                proj=self.rendermanpath, frame=frame)
            _ribfile = "{proj}/rib/{frame:04d}/{frame:04d}.rib".format(
                proj=self.rendermanpath, frame=frame)
            _shotgunupload = "PR:{} SQ:{} SH:{} TA:{}".format(self.job.shotgunProject,
                                                  self.job.shotgunSequence,
                                                  self.job.shotgunShot,
                                                  self.job.shotgunTask)

            _taskMetaData={}
            _taskMetaData["imgfile"] = _imgfile
            _taskMetaData["statsfile"] = _statsfile
            _taskMetaData["ribfile"] = _ribfile
            _taskMetaData["shotgunupload"] = _shotgunupload
            _jsontaskMetaData = json.dumps(_taskMetaData)
            _title = "RENDER Frame {}".format(frame)
            _preview = "sho {""}".format(_imgfile)

            task_render_rib = self.job.env.author.Task(title=_title, preview=_preview, metadata=_jsontaskMetaData)
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
            command_render = self.job.env.author.Command(argv=finalargs,
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
                           yres="720",
                           start=self.job.jobstartframe,
                           end=self.job.jobendframe)
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
        bodystring = "Prman Render Progress: \nLevel: {}\nTrigger: {}\n\n{}".format(level, trigger, body)
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








