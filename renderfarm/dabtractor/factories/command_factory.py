#!/usr/bin/env python2
'''
This code supports submitting bash shell scripts to the farm
Some common commands are wrapped up as convenience objects - like mail and rsync

'''

# TODO


import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
sh = logging.StreamHandler()
sh.setLevel(logging.INFO)
formatter = logging.Formatter('%(levelname)5.5s \t%(name)s \t%(message)s')
sh.setFormatter(formatter)
logger.addHandler(sh)


import os
import sys
import renderfarm.dabtractor.environment_factory as envfac

class Base(object):
    """ Base class for all batch jobs """
    def __init__(self):
        self.spooljob = False
        self.testing = False
        self.fj=envfac.TractorJob()

class Bash(Base):
    """ A simple bash command """
    def __init__(self, command="", projectgroup="admin", email=[1,0,0,0,1,0], tier="admin"):
        super(Bash, self).__init__()
        self.command = command
        self.projectgroup = projectgroup
        self.email = email
        self.tier = tier

        self.job = self.fj.author.Job(\
            title="Bash Job: {}".format(self.fj.usernumber),
            priority=10,
            metadata="user={} realname={}".format(self.fj.usernumber,self.fj.username),
            comment="LocalUser is {} {}".format(self.fj.usernumber, self.fj.username),
            projects=[str(self.projectgroup)],
            tier=str(self.tier),
            tags=["thewholefarm"],
            service="shellservices")

    def build(self):
        """ Main method to build the job """

        task_parent = self.fj.author.Task(title="Parent")
        task_parent.serialsubtasks = 1
        task_bash = self.fj.author.Task(title="Command")

        bashcommand = self.fj.author.Command(argv=["bash","-c",self.command])
        task_bash.addCommand(bashcommand)
        task_parent.addChild(task_bash)

        # logger.info("email = {}".format(self.email))
        task_notify = self.fj.author.Task(title="Notify")
        task_notify.addCommand(self.mail("JOB", "COMPLETE", "blah"))
        task_parent.addChild(task_notify)
        self.job.addChild(task_parent)

    def validate(self):
        """ Validate the job script """
        logger.info("\n\n{s:_^80}\n{j}\n{s:_^80}".format(s="snip", j=self.job.asTcl()))

    def mail(self, level="Level", trigger="Trigger", body="Render Progress Body"):
        bodystring = "Bash Progress: \nLevel: {l}\nTrigger: {t}\n\n{b}".format(\
            l=level,t=trigger, b=body)
        subjectstring = "FARM JOB: %s " % (self.command)
        mailcmd = self.fj.author.Command(argv=["sendmail.py", "-t", self.fj.useremail,\
                                               "-b", bodystring, "-s", subjectstring])
        return mailcmd

    def spool(self):
        try:
            self.job.spool(owner=self.fj.jobowner,port=int(self.fj.port))
        except Exception, spoolerr:
            logger.warn("A spool error %s" % spoolerr)
        else:
            logger.info("Spooled correctly")


# ##############################################################################
class Rsync(Base):
    """   """
    def __init__(self,
                 sourcedirectory="",
                 targetdirectory="",
                 spoolipaddress="",
                 spoolhost="",
                 options="",
                 email=[1,0,0,0,1,0]
    ):

        super(Rsync, self).__init__()
        self.sourcedirectory = sourcedirectory
        self.spoolipaddress = spoolipaddress
        self.targetdirectory = targetdirectory
        self.spoolhost = spoolhost
        self.options = options
        self.email = email

        self.job = self.fj.author.Job(title="Rsync Job: {}".format(self.fj.username),
                      priority=100,
                      # envkey=["maya{}".format(self.mayaversion)],
                      metadata="user={} realname={}".format(self.fj.usernumber,
                                                            self.fj.username),
                      comment="LocalUser is {} {}".format(self.fj.usernumber,
                                                          self.fj.username),
                      service="shellservices")


    def build(self):
        """ Main method to build the job """
        logger.info("Source Directory: {}".format(self.sourcedirectory))
        logger.info("Target Directory:{}".format(self.targetdirectory))
        logger.info("Spool Host: {}".format(self.spoolhost))
        logger.info("Spool Ip Address:{}".format(self.spoolipaddress))
        logger.info("Options: {}".format(self.options))

        # ############## general commands ############
        env = self.fj.author.Command(argv=["printenv"], samehost=1)
        pwd = self.fj.author.Command(argv=["pwd"], samehost=1)

        # ############## PARENT #################
        parent = self.fj.author.Task(title="Parent Task")
        parent.serialsubtasks = 1

        # ############## 2  RSYNC ###########
        task_loadon = self.fj.author.Task(title="Rsync", service="shellservices")
        _sourceproject = self.sourcedirectory
        _targetproject = self.targetdirectory

        if _sourceproject == _targetproject:
            logger.info("No need to rsync source and target the same project")
            self.sourcetargetsame = True
        else:
            _loadonsource = self.sourcedirectory
            _loadontarget = self.targetdirectory
            logger.info("Loadon Project Source: %s" % _loadonsource)
            logger.info("Loadon Project Target: %s" % _loadontarget)
            loadon = self.fj.author.Command(argv=["rsync", "-au", _loadonsource, _loadontarget])
            task_loadon.addCommand(loadon)
            parent.addChild(task_loadon)

        # ############## 7 NOTIFY ###############
        logger.info("email = {}".format(self.email))
        """
        window.emailjob.get(),
        window.emailtasks.get(),
        window.emailcommands.get(),
        window.emailstart.get(),
        window.emailcompletion.get(),
        window.emailerror.get()
        """
        task_notify = self.fj.author.Task(title="Notify", service="shellservices")
        task_notify.addCommand(self.mail("JOB", "COMPLETE", "blah"))
        parent.addChild(task_notify)
        self.job.addChild(parent)

    def validate(self):
        logger.info("\n\n{:_^80}\n{}\n{:_^80}".format("snip", self.job.asTcl(), "snip"))

    def mail(self, level="Level", trigger="Trigger", body="Render Progress Body"):
        bodystring = "Rsync Progress: \nLevel: {}\nTrigger: {}\n\n{}".format(level, trigger, body)
        subjectstring = "FARM JOB: %s %s" % (str(self.sourcedirectory), self.targetdirectory)
        mailcmd = self.fj.author.Command(argv=["sendmail.py", "-t", self.fj.useremail, "-b", bodystring, "-s", subjectstring], service="shellservices")
        return mailcmd

    def spool(self):
        if os.path.exists(self.sourcedirectory):
            try:
                logger.info("Spooled correctly")
                self.job.spool(owner=self.fj.jobowner, port=int(self.fj.port))
            except Exception, spoolerr:
                logger.warn("A spool error %s" % spoolerr)
        else:
            message = "Cant find source %s" % self.sourcedirectory
            logger.critical(message)
            sys.exit(message)

class SendMail(Base):
    """ Mail from pixar job defined using the tractor api """

    def __init__(self, mailto, mailfrom, mailcc, mailsubject, mailbody):
        """
        :param mailto:
        :param mailfrom:
        :param mailcc:
        :param mailsubject:
        :param mailbody:
        """
        super(SendMail, self).__init__()
        self.testing=False
        self.mailto=mailto
        self.mailfrom=mailfrom
        self.mailcc=mailcc
        self.mailsubject=mailsubject
        self.mailbody=mailbody

        self.job = self.fj.author.Job(title="MAIL: {}".format(self.fj.username),
          priority=10,
          envkey=["shellservices"],
          metadata="username={} usernumber={}".format(self.fj.username, self.fj.usernumber),
          comment="LocalUser is {} {}".format(self.fj.username, self.fj.usernumber),
          projects=["admin"],
          tier="batch",
          tags=["thewholefarm"],
          service="")

    def build(self):
        """ Main method to build the job  """
        task_thisjob = self.fj.author.Task(title="Adhoc Job")
        task_thisjob.serialsubtasks = 1

        task_notify = self.fj.author.Task(title="Notify", service="shellservices")
        task_notify.addCommand(self.bugreport("BUG", self.mailbody))
        task_thisjob.addChild(task_notify)

        self.job.addChild(task_thisjob)

    def validate(self):
        """ Validate """
        logger.info("\n\n{:_^80}\n{}\n{:_^80}".format("snip", self.job.asTcl(), "snip"))

    def mail(self, level="Level", trigger="Trigger", body="Render Progress Body"):
        bodystring = "Prman Render Progress: \nLevel: {}\nTrigger: {}\n\n{}".format(level, trigger, body)
        subjectstring = "FARM JOB: %s %s" % (str(self.fj.usernumber), self.fj.username)
        mailcmd = self.fj.author.Command(argv=["sendmail.py", "-t", self.fj.useremail, "-b", bodystring, "-s", subjectstring], service="shellservices")

        return mailcmd

    def bugreport(self, level="BUG", body="Bug report details"):
        _bodystring = "LEVEL: {}\n\n\nDETAILS: \n\n{}".format(level, body)
        _subjectstring = "BUG REPORT: From {} {}\n".format(str(self.fj.username),str(self.fj.usernumber))
        mailcmd = self.fj.author.Command(argv=["sendmail.py", "-t", "%s@uts.edu.au" % "120988", "-b", _bodystring, "-s", _subjectstring], service="shellservices")
        cccmd = self.fj.author.Command(argv=["sendmail.py", "-t", self.fj.useremail, "-b", _bodystring, "-s", _subjectstring], service="shellservices")
        return mailcmd

    def spool(self):
        try:
            self.job.spool(owner="pixar")
        except Exception, spoolerr:
            logger.warn("A spool error %s" % spoolerr)
            sys.exit(spoolerr)
        else:
            logger.info("Spooled correctly")


# ##############################################################################

if __name__ == '__main__':

    logger.setLevel(logging.DEBUG)
    logger.info("Running test for {}".format(__name__))
    logger.info("START TESTING")

    logger.info("{s:*^80}".format(s=" TEST BASH "))
    TEST = Bash(
               # startdirectory="/var/tmp",
               command="farm_check.py > out.txt",
               email=[0,0,0,0,0,0]
    )

    TEST.build()
    TEST.validate()
    # TEST.spool()
    logger.info("{s:*^80}".format(s=" TEST RSYNC "))

    RSYNC=Rsync()
    RSYNC.build()
    RSYNC.validate()

    logger.info("{s:*^80}".format(s=" TEST SENDMAIL "))
    SM=SendMail(mailto="120988@uts.edu.au", mailfrom="pixar@uts.edu.au", mailcc="", \
                mailsubject="TEST", mailbody="get a body")
    SM.build()
    SM.validate()

