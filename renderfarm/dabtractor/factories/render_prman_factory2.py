#!/usr/bin/env rmanpy
'''
To do:
    find commonality in render jobs and put it in base class

    implement ribchunks - DONE
    implement option args and examples - rms.ini

    implement previews???
    implement stats to browswer

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

import tractor.api.author as author
import tractor.api.query as tq
import os
import time
import sys
# import user_factory as ufac
import utils_factory as utils
# import environment_factory as envfac


class RenderPrman(object):
    ''' Renderman job defined using the tractor api '''

    def __init__(self, job):
        super(RenderPrman, self).__init__()
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
        # self.job.envprojectname = os.path.basename(self.mayaprojectpath)
        self.ribpath = "{}/rib".format(self.rendermanpath)
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
              metadata="username={} usernumber={}".format(self.job.username,self.job.usernumber),
              comment="LocalUser is {} {}".format(self.job.username,self.job.usernumber),
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
            task_notify = self.job.env.author.Task(title="Notify", service="ShellServices")
            task_notify.addCommand(self.mail("JOB", "START", "{}".format(self.mayascenefilefullpath)))
            task_thisjob.addChild(task_notify)

        self.renderjob.addChild(task_thisjob)

        # ############## 1 PREFLIGHT ##############
        task_preflight = self.job.env.author.Task(title="Preflight")
        task_preflight.serialsubtasks = 1
        task_thisjob.addChild(task_preflight)
        task_generate_rib_preflight = self.job.env.author.Task(title="Generate RIB Preflight")
        command_ribgen = self.job.env.author.Command(argv=["maya","-batch","-proj", self.mayaprojectpath,
                                              "-command",
                                              "renderManBatchGenRibForLayer {layerid} {start} {end} {phase}".format(
                                                  layerid=0, start=self.startframe, end=self.endframe, phase=1),
                                              "-file", self.mayascenefilefullpath],
                                              tags=["maya", "theWholeFarm"],
                                              atleast=int(self.threads),
                                              atmost=int(self.threads),
                                              service="RfMRibGen")
        task_generate_rib_preflight.addCommand(command_ribgen)
        task_preflight.addChild(task_generate_rib_preflight)
        task_render_preflight = author.Task(title="Render Preflight")

        command_render_preflight = author.Command(argv=[
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
        task_render_allframes = self.job.env.author.Task(title="ALL FRAMES {}-{}".format(self.startframe,self.endframe))
        task_render_allframes.serialsubtasks = 1
        task_ribgen_allframes = self.job.env.author.Task(title="RIB GEN {}-{}".format(self.startframe, self.endframe))

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

            task_generate_rib = author.Task(title="RIB GEN chunk {} frames {}-{}".format(
                    chunk, _chunkstart, _chunkend ))
            command_generate_rib = author.Command(argv=[
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
        task_render_frames = self.job.env.author.Task(title="RENDER Frames {}-{}".format(self.startframe,self.endframe))
        task_render_frames.serialsubtasks = 0

        for frame in range(self.startframe, (self.endframe + 1), self.byframe):
            _imgfile = "{proj}/{scenebase}.{frame:04d}.{ext}".format(
                proj=self.renderdirectory, scenebase=self.scenebasename, frame=frame, ext=self.outformat)
            _statsfile = "{proj}/rib/{frame:04d}/{frame:04d}.xml".format(
                proj=self.rendermanpath, frame=frame)
            _ribfile = "{proj}/rib/{frame:04d}/{frame:04d}.rib".format(
                proj=self.rendermanpath, frame=frame)

            task_render_rib = self.job.env.author.Task(title="RENDER Frame {}".format(frame),
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
            command_render = self.job.env.author.Command(argv=finalargs,
                                            tags=["prman", "theWholeFarm"],
                                            atleast=int(self.threads),
                                            atmost=int(self.threads),
                                            service="PixarRender")

            task_render_rib.addCommand(command_render)

            # ############## 5 NOTIFY Task END ###############
            if self.optionsendtaskendemail:
                # logger.info("email = {}".format(self.job.useremail))
                # task_notify = self.job.env.author.Task(title="Notify", service="ShellServices")
                task_render_rib.addCommand(self.mail("TASK FRAME {}".format(frame), "END", "{}".format(
                    self.mayascenefilefullpath)))
                # task_thisjob.addChild(task_notify)

            self.renderjob.addChild(task_thisjob)
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
            _outmov = "{}/movies/{}.mov".format(self.mayaprojectpath, self.scenebasename,utils.getnow())
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
                              self.scenebasename,
                              self.job.usernumber,
                              self.job.username,
                              self.projectgroup,
                              self.thedate)


                _output = "-o %s" % _outmov

                _rvio_cmd = [ utils.expandargumentstring("rvio %s %s %s %s %s" % (_seq, _option1, _option2, _option3, _output)) ]

                task_proxy = self.job.env.author.Task(title="Proxy Generation")
                proxycommand = author.Command(argv=_rvio_cmd,
                                      service="Transcoding",
                                      tags=["rvio", "theWholeFarm"],
                                      envkey=["rvio"])
                task_proxy.addCommand(proxycommand)
                task_thisjob.addChild(task_proxy)

            except Exception, proxyerror:
                logger.warn("Cant make a proxy {}".format(proxyerror))

        else:
            logger.info("make proxy = {}".format(self.makeproxy))

        # ############## 5 NOTIFY JOB END ###############
        if self.optionsendjobendemail:
            logger.info("email = {}".format(self.job.useremail))
            task_notify = self.job.env.author.Task(title="Notify", service="ShellServices")
            task_notify.addCommand(self.mail("JOB", "COMPLETE", "{}".format(self.mayascenefilefullpath)))
            task_thisjob.addChild(task_notify)

        self.renderjob.addChild(task_thisjob)

    def validate(self):
        logger.info("\n\n{:_^80}\n{}\n{:_^80}".format("snip", self.renderjob.asTcl(), "snip"))

    def mail(self, level="Level", trigger="Trigger", body="Render Progress Body"):
        bodystring = "Prman Render Progress: \nLevel: {}\nTrigger: {}\n\n{}".format(level, trigger, body)
        subjectstring = "FARM JOB: {} {} {} {}".format(level,trigger, str(self.scenebasename), self.job.username)
        mailcmd = author.Command(argv=["sendmail.py", "-t", "%s"%self.job.useremail, "-b", bodystring, "-s", subjectstring], service="ShellServices")
        return mailcmd

    def spool(self):
        # double check scene file exists
        logger.info("Double Checking: {}".format(os.path.expandvars(self.mayascenefilefullpath)))
        if os.path.exists(os.path.expandvars(self.mayascenefilefullpath)):
            try:
                logger.info("Spooled correctly")
                # all jobs owner by pixar user on the farm
                self.renderjob.spool(owner=self.job.env.getdefault("tractor","jobowner"),
                               port=int(self.job.env.getdefault("tractor","port")))

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








