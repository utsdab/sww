#!/usr/bin/python
"""
    All these Classes are to do with the defining of the USER

    This code handles the creation of a user area.
    At UTS the $USER is a number and there is no nice name exposed at all.
    However we can query this from the ldap database using ldapsearch.
    Thus we can definr the concept of renderusername and renderusernumber
    this just need to be in the path some place  dabanim/usr/bin
"""
import os
import sys
import string
import time
import subprocess
import utils_factory as utils
import environment_factory as envfac
import tractor.api.author as author
import shotgun_factory as sgt

# ##############################################################
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
sh = logging.StreamHandler()
sh.setLevel(logging.INFO)
formatter = logging.Formatter('%(levelname)5.5s \t%(filename)s as %(name)s \t%(message)s')
sh.setFormatter(formatter)
logger.addHandler(sh)
# ##############################################################



# class WorkType(object):
#     """
#     This is the user work area either work/number or projects/projectname
#     """
#     def __init__(self,userid=None,projectname=None):
#         self.env=envfac.Environment()
#         self.dabrenderpath=self.env.getdefault("DABRENDER","path")
#         self.dabwork=self.env.getdefault("DABWORK","path")
#         self.dabuserprefs=self.env.getdefault("DABUSERPREFS","path")
#
#         if userid:
#             self.envtype="user_work"
#             self.userid=userid
#             self.map=Map()
#             self.userdict=self.map.getuser(self.userid)
#             self.usernumber=self.userdict.get("number")
#             self.username=self.userdict.get("name")
#             self.enrol=self.userdict.get("year")
#             logger.debug("Usernumber {}, Username {}, Enrolled {}".format (self.usernumber,self.username,self.enrol))
#
#         if projectname:
#             self.envtype="project_work"
#             self.projectname=projectname
#
#     def makeworkdirectory(self):
#         """ Attempts to make the user_work directory for the user or
#         the project under project_work """
#         try:
#             if self.envtype == "user_work":
#                 os.mkdir( os.path.join(self.dabwork,self.envtype,self.username))
#                 logger.info("Made {} under user_work".format(self.username))
#             elif self.envtype == "project_work":
#                 os.mkdir( os.path.join(self.dabwork,self.envtype,self.projectname))
#                 logger.info("Made {} under project_work".format(self.projectname))
#             else:
#                 logger.info("Made no directories")
#                 raise
#         except Exception, e:
#             logger.warn("Made nothing {}".format(e))
#
#     def makeuserprefs(self):
#         """ Attempts to make individual userprefs directory for the user
#         :return:
#         """
#         try:
#             if self.envtype == "users":
#                 os.mkdir( os.path.join(self.dabuserprefs,self.envtype,self.usernumber))
#                 logger.info("Made {} under userprefs/{}".format(self.envtype,self.usernumber))
#             else:
#                 logger.info("Made no directories")
#                 raise
#         except Exception, e:
#             logger.warn("Made no new userprefs {}".format(e))


class UtsUser(object):
    """
    This class represents the UTS user account.  Data is queried from the
    LDAP server at UTS to build a model of the student.  This requires the
    user to authenticate against the UTS LDAP server.
    Once this is built then the class has methods to write the data to a
    Map object which caches the info into a json file.
    The json file is owned by pixar user and is edited by creating a farm
    job which runs as pixar user.  This afford a mechanism to manage the
    reading and writing to this map file.  Its not great but its ok.
    It could be that this file is a serialised file.
    """
    def __init__(self):
        """

        """
        self.name=None
        self.number = os.getenv("USER")
        self.job=None
        self.farmjob=envfac.FarmJob()
        self.env=envfac.Environment2()
        self.year=time.strftime("%Y")
        logger.info("Current Year is %s" % self.year)


        try:
            p = subprocess.Popen(["ldapsearch", "-h", "moe-ldap1.itd.uts.edu.au", "-LLL", "-D",
                                  "uid=%s,ou=people,dc=uts,dc=edu,dc=au" % self.number,
                                  "-Z", "-b", "dc=uts,dc=edu,dc=au", "-s", "sub", "-W",
                                  "uid=%s" % self.number, "uid", "mail"], stdout=subprocess.PIPE)
            result = p.communicate()[0].splitlines()

            logger.debug(">>>%s<<<<" % result)
            niceemailname = result[2].split(":")[1]
            nicename = niceemailname.split("@")[0]
            compactnicename = nicename.lower().translate(None, string.whitespace)
            cleancompactnicename = compactnicename.translate(None, string.punctuation)
            logger.info("UTS thinks you are: %s" % cleancompactnicename)
            self.name = cleancompactnicename

        except Exception, error7:
            logger.warn("    Cant get ldapsearch to work: %s" % error7)
            sys.exit("UTS doesnt seem to know you")

    def addtomap(self):
        """

        :return:
        """

        try:
            # ################ TRACTOR JOB ################
            self.command = ["bash", "-c", "add_farmuser.py -n {} -u {} -y {}".format(self.number,self.name,self.year)]
            # self.args = ["-n",self.number,"-u",self.name,"-y",]
            # self.command = self.base+self.ar
            self.job = self.farmjob.author.Job(title="New User Request: {}".format(self.name),
                                               priority=100,
                                               metadata="user={} realname={}".format(self.number, self.name),
                                               comment="New User Request is {} {} {}".format(self.number, self.name,self.number),
                                               projects=["admin"],
                                               tier="admin",
                                               envkey=["default"],
                                               tags=["theWholeFarm"],
                                               service="ShellServices")
            # ############## 2  RUN COMMAND ###########
            task_parent = self.farmjob.author.Task(title="Parent")
            task_parent.serialsubtasks = 1
            task_bash = self.farmjob.author.Task(title="Command")
            bashcommand = author.Command(argv=self.command)
            task_bash.addCommand(bashcommand)
            task_parent.addChild(task_bash)

            # ############## 7 NOTIFY ###############
            task_notify = self.farmjob.author.Task(title="Notify")
            task_notify.addCommand(self.mail("JOB", "COMPLETE", "blah"))
            task_parent.addChild(task_notify)
            self.job.addChild(task_parent)
        except Exception, joberror:
            logger.warn(joberror)

    def validate(self):
        """

        :return:
        """
        if self.job:
            logger.info("\n\n{:_^80}\n{}\n{:_^80}".format("snip", self.job.asTcl(), "snip"))

    def mail(self, level="Level", trigger="Trigger", body="Render Progress Body"):
        """
        A method to handle sending mail.
        :param level:
        :param trigger:
        :param body:
        :return: mail command
        """
        bodystring = "Add New User: \nLevel: {}\nTrigger: {}\n\n{}".format(level, trigger, body)
        subjectstring = "FARM JOB: %s " % (self.command)
        mailcmd = self.farmjob.author.Command(argv=["sendmail.py", "-t", "%s@uts.edu.au" % self.number,
                                       "-b", bodystring, "-s", subjectstring])
        return mailcmd

    def spool(self):
        """
        Spool to the farm method.
        :return:
        """
        try:
            self.job.spool(owner="{}".format(envfac.FarmJob.getdefault("tractor","jobowner")))
            logger.info("Spooled correctly")
        except Exception, spoolerr:
            logger.warn("A spool error %s" % spoolerr)



class FarmUser(object):
    def __init__(self):
        """ The user details as defined in the map, each user has data held in a
        dictionary """
        self.env=envfac.Environment2()
        self.user = self.env.environ["USER"]

        try:
            __sgt = sgt.Person()
        except Exception,err:
            logger.critical("Problem creating User: {}".format(err))
            sys.exit(err)
        else:
            self.name=__sgt.dabname
            self.number=__sgt.dabnumber





if __name__ == '__main__':
    """
    All this is testing, this  is a factory and shouldnt be called as 'main'
    """
    sh.setLevel(logging.DEBUG)
    logger.setLevel(logging.DEBUG)

    ###############################################


    ###############################################
    """
    try:
        logger.debug("getuser:{} getusername:{}".format( m.getuser("120988"), m.getusername("120988")) )
    except Exception, err:
        logger.warn(err)

    logger.debug("-------- TEST adduser ------------")
    try:
        # m.getallusers()
        m.backup()
        m.adduser("1209880","mattgidney","2020")
        m.adduser("0000000","nextyearstudent","2016")
        m.adduser("9999999","neveryearstudent","2016")

    except Exception, err:
        logger.warn(err)


    logger.debug("-------- TEST getuser ------------")
    try:
        m.getuser("9999999")
    except Exception, err:
        logger.warn(err)

    logger.debug("-------- TEST removeuser ------------")
    try:
        m.removeuser("9999999")
        m.getuser("9999999")
    except Exception, err:
        logger.warn(err)


    u = FarmUser()
    logger.debug( u.name )
    logger.debug( u.number)
    logger.debug( u.year)
    logger.debug( u.user)

    """

    uts = UtsUser()
    logger.debug( uts.name)
    logger.debug( uts.number)


    """
    logger.debug("-------- TEST show __dict__ ------------")
    try:
        logger.debug("MAP: {}".format(m.__dict__))
        logger.debug("   : {}".format(dir(m)))
    except Exception, err:
        logger.warn(err)

    logger.debug("-------- TEST USER------------")
    try:
        u=User()
        logger.debug("USER: {}".format(u.__dict__))
        logger.debug("    : {}".format(dir(u)))
    except Exception, err:
        logger.warn(err)

    logger.debug("-------- TEST ENVTYPE ------------")
    try:
        e=WorkType(userid="120988")
        e.makedirectory()
        e=WorkType(projectname="albatross")
        e.makedirectory()
        logger.debug("ENVTYPE: {}".format(e.__dict__))
        logger.debug("       : {}".format(dir(e)))
    except Exception, err:
        logger.warn(err)
    """
