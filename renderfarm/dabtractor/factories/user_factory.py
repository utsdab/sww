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
import json
import shutil
import string
import time
import subprocess
import utils_factory as utils
import environment_factory as envfac
import tractor.api.author as author

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


class Map(object):
    """
    This class is the mapping of student information into a json file that acts like a cache rather than having to do LDAP queries all the time.

    """
    def __init__(self):
        self.env=envfac.Environment()
        # self.dabrender = self.env.alreadyset("DABRENDER","path","/Volume/dabrender")
        # self.dabusr = self.env.alreadyset("DABUSR","path","/Volume/dabrender")
        # self.dabwork = self.env.alreadyset("DABWORK","path","")


        try:
            _mapfilejson = os.path.join(self.dabrender, self.env.getdefault("DABRENDER","usermapfile"))
        except Exception, err:
            logger.critical("No Map Path {}".format(err))
        else:
            logger.info("Map File: {}".format(_mapfilejson))
            self.mapfilejson=_mapfilejson
            with open(self.mapfilejson) as json_data:
                self.all = json.load(json_data)
                self.allusers = self.all.keys()
        finally:
            file(self.mapfilejson).close()


        try:
            _tractorcrewlist = os.path.join(self.dabrender, self.env.getdefault("DABRENDER","tractorcrewlist"))
            if not os.path.isfile(_tractorcrewlist):
                logger.warn("Cant find {}".format(_tractorcrewlist))
                raise IOError
        except Exception, err:
            logger.critical("No Tractor Crew List File Error {}".format(err))
        else:
            logger.info("Tractor Crew List: {}".format(_tractorcrewlist))
            self.tractorcrewlist=_tractorcrewlist
        finally:
            pass


        try:
            _backuppath = os.path.join(self.dabrender, self.env.getdefault("DABRENDER","backuppath"))
            if not os.path.exists(_backuppath):
                logger.warn("Cant find {}".format(_backuppath))
                raise IOError
        except Exception, err:
            logger.critical("No Map File Backup Path Error {}".format(err))
            os.mkdir(self.backuppath)
        else:
            logger.info("Backup Path: {}".format(_backuppath))
            self.backuppath=_backuppath
        finally:
            pass



    def writecrewformat(self):
        #
        # write out the json map data in a tractor crewlist format to a file
        #

        try:
            _crewlist = open(self.tractorcrewlist, 'w')
            if not self.all:
                raise "Error making Data Model from json file"
        except Exception, err:
            logger.warn("Error opening tractorcrewlist file {} : {}".format(self.tractorcrewlist,err))
        else:
            for i, student in enumerate(self.allusers):
                _line='"{number}", # {student} {name} {year}'.format(student = student,
                                                               number=self.all[student].get("number","NONE"),
                                                               name=self.all[student].get("name","NONE"),
                                                               year=self.all[student].get("year","NONE"))
                _crewlist.write("{}\n".format(_line))
                logger.debug(_line)
        finally:
            open(self.tractorcrewlist, 'w').close()


    def getallusers(self):
        # return a dictionary of user info
        try:
            with open(self.mapfilejson) as json_data:
                all = json.load(json_data)
        except Exception, err:
            logger.warn("Error opening json file")
            all=None
        else:
            return all
        finally:
            pass


        ###  print for crews.config file
        # for i, student in enumerate(allusers):
        #     logger.info('"{number}", # {student} {name} {year}'.format(student = student,
        #                                                        number=all[student].get("number","NONE"),
        #                                                        name=all[student].get("name","NONE"),
        #                                                        year=all[student].get("year","NONE")))

    def getuser(self, usernumber):
        # query user in the map file and return the dictionary
        with open(self.mapfilejson) as json_data:
            all = json.load(json_data)
        try:
            _result=all[usernumber]
            logger.debug("Found in Map: {}".format(_result))
            return _result
        except Exception, e:
            logger.warn("{} not found {}".format(usernumber,e))
            return None

    def getusername(self,usernumber):
        return self.getuser(usernumber).get("name")

    def removeuser(self, usernumber):
        # remove a user from the map
        if self.getuser(usernumber):
            # self.backup()
            logger.info("Removing user {}".format(usernumber))

            with open(self.mapfilejson) as json_data:
                all = json.load(json_data)

            all.pop(usernumber, None)
            with open(self.mapfilejson, 'w') as outfile:
                json.dump(all, outfile, sort_keys = True, indent = 4,)

    def backup(self):
        # backup the existing map
        source=self.mapfilejson
        now=utils.getnow()
        if not os.path.isdir(self.backuppath):
            os.mkdir( self.backuppath, 0775 );
        dest=os.path.join(self.backuppath,
                          "{}-{}".format(os.path.basename(self.mapfilejson),now))
        logger.info("Backup: source {}".format(source))
        logger.info("Backup: dest {}".format(dest))
        shutil.copy2(source, dest)

    def adduser(self, number, name, year):
        # add a new user to the json map file
        if not self.getuser(number):
            logger.info("No one by that number {}, adding".format(number))
            try:
                with open(self.mapfilejson) as json_data:
                    all = json.load(json_data)
                new={number:{"name":name,"number":number,"year":year}}
                all.update(new)
                with open(self.mapfilejson, 'w') as outfile:
                    json.dump(all, outfile, sort_keys = True, indent = 4,)
            except Exception, err:
                logger.warn("Error adding user {}".format(err))
                raise
        else:
            logger.info("User {} already in map file".format(number))

class WorkType(object):
    # this is the user work area either work/number or projects/projectname
    def __init__(self,userid=None,projectname=None):
        self.env=envfac.Environment()
        self.dabrenderpath=self.env.getdefault("DABRENDER","path")
        self.dabwork=self.env.getdefault("DABWORK","path")
        self.dabuserprefs=self.env.getdefault("DABUSERPREFS","path")

        if userid:
            self.envtype="user_work"
            self.userid=userid
            self.map=Map()
            self.userdict=self.map.getuser(self.userid)
            self.usernumber=self.userdict.get("number")
            self.username=self.userdict.get("name")
            self.enrol=self.userdict.get("year")
            logger.debug("Usernumber {}, Username {}, Enrolled {}".format (self.usernumber,self.username,self.enrol))

        if projectname:
            self.envtype="project_work"
            self.projectname=projectname

    def makeworkdirectory(self):
        # attempts to make the user_work directory for the user or the project under project_work
        try:
            if self.envtype == "user_work":
                os.mkdir( os.path.join(self.dabwork,self.envtype,self.username))
                logger.info("Made {} under user_work".format(self.username))
            elif self.envtype == "project_work":
                os.mkdir( os.path.join(self.dabwork,self.envtype,self.projectname))
                logger.info("Made {} under project_work".format(self.projectname))
            else:
                logger.info("Made no directories")
                raise
        except Exception, e:
            logger.warn("Made nothing {}".format(e))

    def makeuserprefs(self):
        # attempts to make individual userprefs directory for the user
        try:
            if self.envtype == "users":
                os.mkdir( os.path.join(self.dabuserprefs,self.envtype,self.usernumber))
                logger.info("Made {} under userprefs/{}".format(self.envtype,self.usernumber))
            else:
                logger.info("Made no directories")
                raise
        except Exception, e:
            logger.warn("Made no new userprefs {}".format(e))


class TractorUser(object):
    # this is the crew.config for tractor
    def __init__(self):
        pass

class UtsUser(object):
    '''
    This class represents the UTS user account.  Data is queried from the LDAP server at UTS to build a model of the
    student.  This requires the user to authenticate against the UTS LDAP server.
    Once this is built then the class has methods to write the data to a Map object which caches the info into a json file.
    The json file is owned by pixar user and is edited by creating a farm job which runs as pixar user.  This afford
    a mechanism to manage the reading and writing to this map file.  Its not great but its ok.
    It could be that this file is a serialised file.
    '''
    def __init__(self):
        self.name=None
        self.number = os.getenv("USER")
        self.job=None
        self.env=envfac.Environment()
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

        if self.number in self.env.getdefault("DABRENDER","superuser"):
            logger.info("Your are a superuser - yay")
        else:
            logger.warn("You need to be a superuser to mess with the map file sorry")
            # sys.exit("You need to be a superuser to mess with the map file sorry")

        try:
            # ################ TRACTOR JOB ################
            self.command = ["bash", "-c", "add_farmuser.py -n {} -u {} -y {}".format(self.number,self.name,self.year)]
            # self.args = ["-n",self.number,"-u",self.name,"-y",]
            # self.command = self.base+self.ar
            self.job = self.env.author.Job(title="New User Request: {}".format(self.name),
                                  priority=100,
                                  metadata="user={} realname={}".format(self.number, self.name),
                                  comment="New User Request is {} {} {}".format(self.number, self.name,self.number),
                                  projects=["admin"],
                                  tier="admin",
                                  envkey=["default"],
                                  tags=["theWholeFarm"],
                                  service="ShellServices")
            # ############## 2  RUN COMMAND ###########
            task_parent = self.env.author.Task(title="Parent")
            task_parent.serialsubtasks = 1
            task_bash = self.env.author.Task(title="Command")
            bashcommand = author.Command(argv=self.command)
            task_bash.addCommand(bashcommand)
            task_parent.addChild(task_bash)

            # ############## 7 NOTIFY ###############
            task_notify = self.env.author.Task(title="Notify")
            task_notify.addCommand(self.mail("JOB", "COMPLETE", "blah"))
            task_parent.addChild(task_notify)
            self.job.addChild(task_parent)
        except Exception, joberror:
            logger.warn(joberror)

    def validate(self):
        if self.job:
            logger.info("\n\n{:_^80}\n{}\n{:_^80}".format("snip", self.job.asTcl(), "snip"))

    def mail(self, level="Level", trigger="Trigger", body="Render Progress Body"):
        bodystring = "Add New User: \nLevel: {}\nTrigger: {}\n\n{}".format(level, trigger, body)
        subjectstring = "FARM JOB: %s " % (self.command)
        mailcmd = self.env.author.Command(argv=["sendmail.py", "-t", "%s@uts.edu.au" % self.number,
                                       "-b", bodystring, "-s", subjectstring])
        return mailcmd

    def spool(self):
        try:
            self.job.spool(owner="pixar")
            logger.info("Spooled correctly")
        except Exception, spoolerr:
            logger.warn("A spool error %s" % spoolerr)



class FarmUser(object):
    def __init__(self):
        # the user details as defined in the map
        self.user = os.getenv("USER")
        usermap = Map()

        try:
            _userdict=usermap.getuser(self.user)
            self.name=_userdict.get("name")
            self.number=_userdict.get("number")
            self.year=_userdict.get("year")

        except Exception,err:
            logger.critical("Problem creating User: {}".format(err))
            sys.exit(err)

    def getusername(self):
        return self.name

    def getusernumber(self):
        return self.number

    def getenrolmentyear(self):
        return self.year





if __name__ == '__main__':
    ##### all this is testing
    ##### this  is a factory and shouldnt be called as 'main'

    sh.setLevel(logging.DEBUG)
    logger.setLevel(logging.DEBUG)

    ###############################################
    logger.debug("-------- TEST MAP ------------")
    m = Map()
    for i,j in enumerate(m.allusers):
        logger.debug("{number:12s}{name:24s} {year}".format(number=j,year=m.all.get(j).get("year"),name=m.all.get(
            j).get("name")))


    ###############################################
    # try:
    #     logger.debug("getuser:{} getusername:{}".format( m.getuser("120988"), m.getusername("120988")) )
    # except Exception, err:
    #     logger.warn(err)
    #
    # logger.debug("-------- TEST adduser ------------")
    # try:
    #     # m.getallusers()
    #     m.backup()
    #     m.adduser("1209880","mattgidney","2020")
    #     m.adduser("0000000","nextyearstudent","2016")
    #     m.adduser("9999999","neveryearstudent","2016")
    #
    # except Exception, err:
    #     logger.warn(err)
    #
    #
    # logger.debug("-------- TEST getuser ------------")
    # try:
    #     m.getuser("9999999")
    # except Exception, err:
    #     logger.warn(err)
    #
    # logger.debug("-------- TEST removeuser ------------")
    # try:
    #     m.removeuser("9999999")
    #     m.getuser("9999999")
    # except Exception, err:
    #     logger.warn(err)


    # u = FarmUser()
    # logger.debug( u.name )
    # logger.debug( u.number)
    # logger.debug( u.year)
    # logger.debug( u.user)
    uts = UtsUser()
    logger.debug( uts.name)
    logger.debug( uts.number)


    '''
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
    '''
