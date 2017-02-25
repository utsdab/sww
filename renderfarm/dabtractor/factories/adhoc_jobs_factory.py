#!/usr/bin/env rmanpy
"""
To do:
    find commonality in render jobs and put it in base class

    implement ribchunks - DONE
    implement option args and examples - rms.ini

    implement previews???
    implement stats to browswer

"""
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
import sys
import user_factory as ufac
import environment_factory as envfac

class JobBase(object):
    """
    Base class for all batch jobs
    """
    def __init__(self):
        self.user = os.getenv("USER")
        self.spooljob = False
        self.env=envfac.Environment2()
        self.farmjob=envfac.FarmJob()

        try:
            ru = ufac.FarmUser()
        except Exception, erroruser:
            logger.warn("Cant get the users name and number back %s" % erroruser)
            sys.exit("Cant get the users name")
        else:
            self.renderusernumber = ru.number
            self.renderusername = ru.name
            self.dabrender = self.env.environ["DABRENDER"]
            self.dabrenderworkpath = self.env.environ["DABWORK"]
            self.initialProjectPath = self.env.environ["DABWORK"]

        if os.path.isdir(self.dabrender):
            logger.info("Found %s" % self.dabrender)
        else:
            self.initialProjectPath = None
            logger.critical("Cant find central filer mounted %s" % self.dabrender)
            raise Exception, "dabrender not a valid mount point"


class SendMail(JobBase):
    """ Mail from pixar job defined using the tractor api """

    def __init__(self,mailto,mailfrom,mailcc,mailsubject,mailbody):
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

    def build(self):
        """ Main method to build the job  """
        ########### TESTING ##############

        if self.testing:
            _service_Testing="Testing"
            _tier="admin"

        else:
            _service_Testing=""
            _tier="batch"

        # ################ 0 JOB ################
        self.job = self.farmjob.author.Job(title="MAIL: {}".format(self.renderusername),
                              priority=10,
                              envkey=["ShellServices"],
                              metadata="user={} username={} usernumber={}".format(self.user, self.renderusername,
                                                                                  self.renderusernumber),
                              comment="LocalUser is {} {} {}".format(self.user,self.renderusername,
                                                                     self.renderusernumber),
                              projects=["admin"],
                              tier=_tier,
                              tags=["theWholeFarm"],
                              service=_service_Testing)

        # ############## 0 ThisJob #################
        task_thisjob = self.farmjob.author.Task(title="Adhoc Job")
        task_thisjob.serialsubtasks = 1


        # ############## 5 NOTIFY ###############
        # logger.info("email = {}".format(self.email))
        task_notify = self.farmjob.author.Task(title="Notify", service="ShellServices")
        task_notify.addCommand(self.bugreport("BUG", self.mailbody))
        task_thisjob.addChild(task_notify)

        self.job.addChild(task_thisjob)


    def validate(self):
        logger.info("\n\n{:_^80}\n{}\n{:_^80}".format("snip", self.job.asTcl(), "snip"))

    def mail(self, level="Level", trigger="Trigger", body="Render Progress Body"):
        bodystring = "Prman Render Progress: \nLevel: {}\nTrigger: {}\n\n{}".format(level, trigger, body)
        subjectstring = "FARM JOB: %s %s" % (str(self.scenebasename), self.renderusername)
        mailcmd = self.farmjob.author.Command(argv=["sendmail.py", "-t", "%s@uts.edu.au" % self.user,
                                       "-b", bodystring, "-s", subjectstring], service="ShellServices")

        return mailcmd

    def bugreport(self, level="BUG", body="Bug report details"):
        _bodystring = "LEVEL: {}\n\n\nDETAILS: \n\n{}".format(level, body)
        _subjectstring = "BUG REPORT: From {} {}\n".format(str(self.renderusername),str(self.renderusernumber))
        mailcmd = self.farmjob.author.Command(argv=["sendmail.py", "-t", "%s@uts.edu.au" % "120988",
                                       "-b", _bodystring, "-s", _subjectstring], service="ShellServices")
        cccmd = self.farmjob.author.Command(argv=["sendmail.py", "-t", "%s@uts.edu.au" % self.user,
                                       "-b", _bodystring, "-s", _subjectstring], service="ShellServices")
        return mailcmd

    def spool(self):
        # double check scene file exists
        try:
            logger.info("Spooled correctly")
            # all jobs owner by pixar user on the farm
            self.job.spool(owner="pixar")
        except Exception, spoolerr:
            logger.warn("A spool error %s" % spoolerr)
            sys.exit(spoolerr)


class SimpleCommand(JobBase):
    """ Simple command to run as Pixar with no arguments """

    def __init__(self):
        """       """
        super(SimpleCommand, self).__init__()
        self.testing=False

    def build(self):
        """ Main method to build the job  """

        # ################ 0 JOB ################
        self.job = self.farmjob.author.Job(\
            title="CLEANUP: {}".format(self.renderusername),
            priority=10,
            envkey=["ShellServices"],
            metadata="user={} username={} usernumber={}".format(self.user, self.renderusername,self.renderusernumber),
            comment="LocalUser is {} {} {}".format(self.user,self.renderusername,self.renderusernumber),
            projects=["admin"],
            tier="admin",
            tags=["theWholeFarm"],
            service="")

        # ############## 0 ThisJob #################
        task_thisjob = self.farmjob.author.Task(title="Cleanup Job")
        task_thisjob.serialsubtasks = 1


        cleancmd = self.farmjob.author.Command(argv=["makeworkareas.py"])

        task_notify = self.farmjob.author.Task(title="Cleanup", service="ShellServices")
        task_notify.addCommand(cleancmd)

        task_thisjob.addChild(task_notify)

        self.job.addChild(task_thisjob)

    def validate(self):
        logger.info("\n\n{:_^80}\n{}\n{:_^80}".format("snip", self.job.asTcl(), "snip"))


    def spool(self):
        # double check scene file exists
        try:
            logger.info("Spooled correctly")
            # all jobs owner by pixar user on the farm
            self.job.spool(owner="pixar")
        except Exception, spoolerr:
            logger.warn("A spool error %s" % spoolerr)
            sys.exit(spoolerr)

# ##############################################################################

if __name__ == "__main__":
    logger.setLevel(logging.DEBUG)
    logger.info("START TESTING")

    _body = '''Hello there this is a mail
    from the testing part of matts code that
    hopes to show where the bugs are and how to deal with them.  Does that sound ok?
    Matt'''
    # TEST = SendMail(mailbody=_body,mailsubject="mail subject",mailcc="mail cc",mailto="120988@uts.edu.au")
    # TEST.build()
    # TEST.validate()
    # TEST.spool()
    # logger.info("FINISHED TESTING")

    TEST2 = SimpleCommand()
    TEST2.build()
    TEST2.validate()
    TEST2.spool()
    logger.info("FINISHED TESTING")





