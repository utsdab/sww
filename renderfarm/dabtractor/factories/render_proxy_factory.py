#!/usr/bin/env rmanpy
# TODO  add in frame fange override
# TODO  add in date suffic and versioning  rather than overwriting.

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

import os
import time
import sys
from pprint import pprint
import utils_factory as utils
import sww.renderfarm.dabtractor.factories.environment_factory as envfac



class Job(object):
    """ job parameters - variants should be derived by calling factories as needed """
    def __init__(self):
        """ The payload of gui-data needed to describe a farm render job """
        self.usernumber=None
        self.username=None
        self.useremail=None
        try:
            self.env=envfac.TractorJob()
        except Exception, err:
            logger.warn("Cant get user credentials: {}".format(err))
        else:
            self.usernumber=self.env.usernumber
            self.username=self.env.username
            self.useremail=self.env.useremail
            self.department=self.env.department
            self.dabwork=self.env.dabwork
        self.projectfullpath=None
        self.nukescriptfullpath=None
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
        # self.optionmakeproxy=None
        self.optionresolution=None
        self.options=None
        self.envtype=None
        self.envshow=None
        self.envproject=None
        self.envscene=None
        self.seqbasename=None
        self.shotgunProjectId=None
        self.shotgunSequenceId=None
        self.shotgunShotId=None
        self.shotgunTaskId=None
        self.sendToShotgun=False
        # self.softwareversion=None


class Render_RV(object):
    ''' Renderman job defined using the tractor api '''

    def __init__(self, job):
        self.job=job

        utils.printdict( self.job.__dict__)

        self.job.dabworkalias= "$DABWORK"  # this needs to be set in default environment in tractor keys
        self.job.projectpathalias = "$DABWORK/$TYPE/$SHOW/$PROJECT"
        self.job.projectpath = os.path.join(self.job.dabworkalias, self.job.envtype, self.job.envshow, self.job.envproject)
        self.job.envprojectalias = "$PROJECT"
        self.job.seqfullpathalias = "$DABWORK/$TYPE/$SHOW/$PROJECT/$SCENE"
        self.job.seqfullpath = os.path.join(self.job.dabworkalias, self.job.envtype, self.job.envshow, self.job.envproject, self.job.envscene)
        self.job.selectedframename = os.path.basename(self.job.seqfullpath)  # seq1.0001.exr
        self.job.seqdirname = os.path.dirname(self.job.seqfullpath)

        '''
        MUST HAVE .####.ext at the end <<<<<<<<<<<
        name.0001.####.exr
        name.####.exr
        name.sss.ttt.####.exr
        name.#######.exr

        '{:#^{prec}}'.format('#',prec=6)
        '######'
        '''
        try:
            _split = self.job.selectedframename.split(".")
            _ext = _split[-1]
            _frame = _split[-2]
            _precision = len(_frame)
            _base = ".".join(_split[:-2])
        except Exception, err:
            logger.warn("Cant split the filename properly needs to be of format name.####.ext : {}".format(err))
            self.job.seqbasename = None
            self.job.seqtemplatename = None
        else:
            self.job.seqbasename = _base
            self.job.seqtemplatename = "{b}.{:#^{p}}.{e}".format('#', b=_base, p=_precision, e=_ext)

        # logger.critical("wwwwwwww")

        self.startframe = int(self.job.jobstartframe)
        self.endframe = int(self.job.jobendframe)

        # logger.critical("wwwwwwww")

        self.byframe = int(self.job.jobbyframe)
        self.chunks = int(self.job.jobchunks)  # pixar jobs are one at a time
        self.projectgroup = self.job.department

        # logger.critical("wwwwwwww")
        self.options = ""
        self.resolution = self.job.optionresolution
        # self.outformat = "exr"
        self.optionsendjobstartmail = self.job.optionsendjobstartemail
        self.optionsendjobendemail = self.job.optionsendjobendemail
        self.skipframes = self.job.optionskipframe
        self.threads = self.job.jobthreads
        self.threadmemory = self.job.jobthreadmemory
        self.thedate=time.strftime("%d-%B-%Y")


    def build(self):
        '''
        Main method to build the job
        '''
        # ################ 0 JOB ################
        logger.critical("xxxxxxxxx")

        self.renderjob = self.job.env.author.Job(title="PROXY: {} {} {}-{}".format(
              self.job.username,self.job.seqtemplatename,self.startframe,self.endframe),
              priority=10,
              envkey=["ProjectX",
                    "TYPE={}".format(self.job.envtype),
                    "SHOW={}".format(self.job.envshow),
                    "PROJECT={}".format(self.job.envproject),
                    "SCENE={}".format(self.job.envscene),
                    "SCENENAME={}".format(self.job.seqbasename)],
              metadata="username={} usernumber={}".format(self.job.username,self.job.usernumber),
              comment="LocalUser is {} {}".format(self.job.username,self.job.usernumber),
              projects=[str(self.projectgroup)],
              tier=str(self.job.farmtier),
              tags=["theWholeFarm", ],
              service="")

        # ############## 0 ThisJob #################
        task_thisjob = self.job.env.author.Task(title="Proxy Make Job")
        task_thisjob.serialsubtasks = 1

        # ############## 5 NOTIFY JOB START ###############
        if self.optionsendjobstartmail:
            logger.info("email = {}".format(self.job.useremail))
            task_notify_start = self.job.env.author.Task(title="Notify Start", service="ShellServices")
            task_notify_start.addCommand(self.mail("JOB", "START", "{}".format(self.job.seqfullpath)))
            task_thisjob.addChild(task_notify_start)

        # ############## 1 PREFLIGHT ##############
        task_preflight = self.job.env.author.Task(title="Preflight")
        task_preflight.serialsubtasks = 1
        task_thisjob.addChild(task_preflight)

        _inseq = self.job.seqtemplatename
        _directory = os.path.dirname(self.job.seqfullpath)
        _outmovdir = os.path.join(self.job.dabworkalias,self.job.envtype,self.job.envshow,self.job.envproject,"movies")
        _seq = os.path.join(_directory, _inseq)
        _outmov = os.path.join(_outmovdir,"{}.mov".format(self.job.seqbasename))

        _mkdir_cmd = [ utils.expandargumentstring("mkdir -p %s" % (_outmovdir)) ]
        task_mkdir = self.job.env.author.Task(title="Make output directory")
        mkdircommand = self.job.env.author.Command(argv=_mkdir_cmd, service="Transcoding",tags=["rvio", "theWholeFarm"], envkey=["rvio"])

        task_mkdir.addCommand(mkdircommand)
        task_preflight.addChild(task_mkdir)

        '''
        rvio cameraShape1/StillLife.####.exr  -v -fps 25
        -rthreads 4
        -outres 1280 720 -out8
        -leader simpleslate "UTS" "Artist=Anthony" "Show=Still_Life" "Shot=Testing"
        -overlay frameburn .4 1.0 30.0
        -overlay matte 2.35 0.3
        -overlay watermark "UTS 3D LAB" .2
        -outgamma 2.2
        -o cameraShape1_StillLife.mov
        '''
        # TODO  options for frame rate and resolution

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
                          self.job.seqbasename,
                          self.job.usernumber,
                          self.job.username,
                          self.projectgroup,
                          self.thedate)
            _output = "-o %s" % _outmov
            _rvio_cmd = [ utils.expandargumentstring("rvio %s %s %s %s %s" % (_seq, _option1, _option2, _option3, _output)) ]
            task_proxy = self.job.env.author.Task(title="RVIO Proxy Generation")
            proxycommand = self.job.env.author.Command(argv=_rvio_cmd, service="Transcoding",tags=["rvio", "theWholeFarm"], envkey=["rvio"])
            task_proxy.addCommand(proxycommand)
            task_thisjob.addChild(task_proxy)

        except Exception, proxyerror:
            logger.warn("Cant make a proxy {}".format(proxyerror))


        # ############## 5 NOTIFY JOB END ###############
        if self.optionsendjobendemail:
            logger.info("email = {}".format(self.job.useremail))
            task_notify_end = self.job.env.author.Task(title="Notify End", service="ShellServices")
            task_notify_end.addCommand(self.mail("JOB", "COMPLETE", "{}".format(self.job.seqfullpath)))
            task_thisjob.addChild(task_notify_end)

        self.renderjob.addChild(task_thisjob)

        # ############## 6 SETD TO SHOTGUN ###############
        if self.job.sendToShotgun:
            logger.info("Sending to Shotgun = {} {} {} {}".format(self.job.shotgunProjectId,self.job.shotgunSequenceId,
                                                         self.job.shotgunShotId,self.job.shotgunTaskId))

            # TODO  add in shotgun upload here

            # task_notify_end = self.job.env.author.Task(title="Notify End", service="ShellServices")
            # task_notify_end.addCommand(self.mail("JOB", "COMPLETE", "{}".format(self.job.seqfullpath)))
            # task_thisjob.addChild(task_notify_end)

    def validate(self):
        logger.info("\n\n{:_^80}\n{}\n{:_^80}".format("snip", self.renderjob.asTcl(), "snip"))

    def mail(self, level="Level", trigger="Trigger", body="Render Progress Body"):
        bodystring = "Prman Render Progress: \nLevel: {}\nTrigger: {}\n\n{}".format(level, trigger, body)
        subjectstring = "FARM JOB: {} {} {} {}".format(level, trigger, str(self.job.seqbasename), self.job.username)
        mailcmd = self.job.env.author.Command(argv=["sendmail.py", "-t", "%s"%self.job.useremail, "-b", bodystring, "-s", subjectstring], service="ShellServices")
        return mailcmd

    def spool(self):
        # double check scene file exists
        logger.info("Double Checking: {}".format(os.path.expandvars(self.job.seqfullpath)))
        if os.path.exists(os.path.expandvars(self.job.seqfullpath)):
            try:
                logger.info("Spooled correctly")
                # all jobs owner by pixar user on the farm
                self.renderjob.spool(owner=self.job.env.getdefault("tractor","jobowner"),
                               port=int(self.job.env.getdefault("tractor","port")))

            except Exception, spoolerr:
                logger.warn("A spool error %s" % spoolerr)
        else:
            message = "Scene file non existant %s" % self.job.seqfullpath
            logger.critical(message)
            logger.critical(os.path.normpath(self.job.seqfullpath))
            logger.critical(os.path.expandvars(self.job.seqfullpath))

            sys.exit(message)


# ##############################################################################

if __name__ == "__main__":
    logger.setLevel(logging.INFO)
    logger.info("START TESTING")








