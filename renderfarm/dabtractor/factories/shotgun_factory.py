#!/usr/bin/env python
import pprint
import string
import os
import sys
from sww.shotgun_api3 import Shotgun
import environment_factory as envfac

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

class ShotgunBase(object):
    # base object
    def __init__(self):
        self.env=envfac.Environment2()
        self.serverpath = str(self.env.getdefault("shotgun", "serverpath"))
        self.scriptname = str(self.env.getdefault("shotgun", "scriptname"))
        self.scriptkey  = str(self.env.getdefault("shotgun", "scriptkey"))
        self.sg = Shotgun( self.serverpath, self.scriptname, self.scriptkey)
        logger.info("SHOTGUN: talking to shotgun ...... %s" % self.serverpath)

class Person(ShotgunBase):
    """
    This is a model of the user account as registered in shotgun
    Basically used for authentication
    """
    def __init__(self,shotgunlogin=None):
        """
        :param shotgunlogin: optional name to use - defaults to $USER
        """
        super(Person, self).__init__()
        if not shotgunlogin:
            self.shotgunlogin=os.environ["USER"]
        __fields = ['login','name','firstname','lastname','department','email','sg_tractor']
        __filters =  [['login','is', self.shotgunlogin]]
        __person=None
        try:
            __person=self.sg.find_one("HumanUser",filters=__filters,fields=__fields)
        except Exception, err:
            logger.warn("%s"%err)
            raise
        else:
            if __person.has_key('sg_tractor'):
                self.tractor=__person.get('sg_tractor')

            if __person.has_key('name'):
                self.shotgunname=__person.get('name')
            if __person.has_key('email'):
                self.email=__person.get('email')
                self.dabname=self.cleanname(self.email)
            if __person.has_key('department'):
                self.department=__person.get('department').get('name')
            if __person.has_key('login'):
                self.login=__person.get('login')
                self.dabnumber=self.login
        finally:
            if  not self.tractor:
                    logger.critical("Shotgun user {} is not Active. Sorry.".format(self.shotgunlogin))
                    sys.exit()
            logger.debug("Shotgun Login {} : {}".format(self.shotgunlogin,__person))

    def cleanname(self,email):
        _nicename = email.split("@")[0]
        _compactnicename = _nicename.lower().translate(None, string.whitespace)
        _cleancompactnicename = _compactnicename.translate(None, string.punctuation)
        logger.debug("Cleaned name is : %s" % _cleancompactnicename)
        return _cleancompactnicename


class Projects(ShotgunBase):
    def __init__(self):
        super(Projects, self).__init__()
        __fields = ['id', 'name']
        __filters = [['id','greater_than',0]]

        try:
            self.projects=self.sg.find("Project",__filters,__fields)
        except Exception, err:
            logger.warn("%s"%err)
        else:
            logger.info("Found %d Projects" % (len(self.projects)))
            # logger.debug(self.projects)
            for project in self.projects:
                logger.info("   %s %s"%(project['id'],project['name']))

    def assets(self):
        pass
    def type(self):
        pass

    def sequences(self, projectid):
        # returns a list of dicts  [ {code:, type:, id: } ] of sequences for a given projectid
        fields = ['id', 'code']
        filters = [['project', 'is', {'type': 'Project', 'id': projectid}]]
        sequences= self.sg.find("Sequence",filters,fields)

        if len(sequences) < 1:
            print "couldn't find any Sequences"
        else:
            print "Found %d Sequences" % (len(sequences))
            print sequences


    def shots(self, projectid, sequenceid):
        # returns a list of dicts  [ {code:, type:, id: } ] of sequences for a given projectid
        _fields  = ['id', 'code', 'shots']
        _filters = [
                     ['project',   'is', {'type': 'Project',  'id': projectid}],
                     # ['sequences', 'is', {'type': 'Sequence', 'id': sequenceid }]
                  ]
        shots = self.sg.find("Sequence", _filters, _fields)


        if len(shots) < 1:
            print "couldn't find any shots"
        else:
            print "Found %d shots" % (len(shots))
            print shots

    def tasks(self):
        pass

class People(ShotgunBase):
    def __init__(self):
        super(People, self).__init__()
        __fields = ['login','name','firstname','lastname','department','email','sg_tractor']
        __filters =  [['sg_tractor','is', True]]
        __people=None
        self.people=None
        try:
            __people=self.sg.find("HumanUser",filters=__filters,fields=__fields)
        except Exception, err:
            logger.warn("%s"%err)
            raise
        else:
            self.people=__people
            for __person in self.people:
                logger.debug("{l:12} # {d:9}{c:24}{n:24}{e:40}".format(l=__person.get('login'),
                                                         n=__person.get('name'),
                                                         c=self.cleanname(__person.get('email')),
                                                         e=__person.get('email'),
                                                         d=__person.get('department').get('name')))
    @staticmethod
    def cleanname(email):
        _nicename = email.split("@")[0]
        _compactnicename = _nicename.lower().translate(None, string.whitespace)
        _cleancompactnicename = _compactnicename.translate(None, string.punctuation)
        # logger.debug("Cleaned name is : %s" % _cleancompactnicename)
        return _cleancompactnicename

    def writetractorcrewfile(self,crewfilefullpath=None):
        """
        Write out a tractor crew file for use with tractor.
        each user entry is a line, most is comment and unnecessary.
        eg. 11401229 # Year4 haeinfkim   Hae-In Kim  Hae-In.F.Kim@student.uts.edu.au

        :param crewfile: The full path file name to be created, if none use default
        :return:  the pilepath written, None if failed.
        """
        self.crewfilefullpath=crewfilefullpath
        try:
            _file=open(self.crewfilefullpath,"w")
        except IOError, err:
            logger.warn("Cant open file {} : {}".format(self.crewfilefullpath,err))
        else:
            for i, person in enumerate(self.people):
                _line="{l:12} # {d:9}{c:24}{n:24}{e:40}\n".format(l=person.get('login'),
                                                         n=person.get('name'),
                                                         c=self.cleanname(person.get('email')),
                                                         e=person.get('email'),
                                                         d=person.get('department').get('name'))
                _file.write(_line)
            _file.close()
        finally:
            logger.info("Wrote tractor crew file: {}".format(self.crewfilefullpath))










class NewVersion(ShotgunBase):
    # new version object
    def __init__(self, media = None,
                 projectid = 89,
                 shotname = 'shot',
                 taskname = 'task',
                 versioncode = 'From Tractor',
                 description = 'Created from Farm Job',
                 ownerid = 38,
                 tag = "RenderFarm Proxy"
                 ):
        super(NewVersion, self).__init__()
        self.project = {'type': 'Project', 'id': projectid}
        self.shotname = shotname
        self.taskname = taskname
        self.versioncode = versioncode
        self.description = description
        self.owner = {'type':'HumanUser', 'id': ownerid}
        self.tag = tag
        self.media = media
        logger.info("SHOTGUN: File to upload ...... %s"%self.media)

        self.shotfilters = [ ['project','is', self.project],['code', 'is', self.shotname] ]
        self.shot = self.sg.find_one('Shot', self.shotfilters)

        self.taskfilters = [ ['project','is', self.project],
                    ['entity','is',{'type':'Shot','id': self.shot['id']}],
                    ['content','is',self.taskname] ]
        self.task = self.sg.find_one('Task',self.taskfilters)

        self.data = { 'project': self.project,
                 'code': self.versioncode,
                 'description': self.description,
                 'sg_status_list': 'rev',
                 'entity': {'type':'Shot', 'id':self.shot['id']},
                 'sg_task': {'type':'Task', 'id':self.task['id']},
                 'user': self.owner }
        self.version_result = self.sg.create('Version', self.data)
        logger.info("SHOTGUN: New Version Created : %s" % self.version_result)
        logger.info("SHOTGUN: Sending then transcoding.......")

        # ----------------------------------------------
        # Upload Latest Quicktime
        # ----------------------------------------------
        self.version_id = self.version_result.get('id')
        __result = self.sg.upload("Version", self.version_id, self.media, "sg_uploaded_movie", self.tag)
        logger.info ("SHOTGUN: Done uploading, upload reference is: %s"%__result)


    def test(self):
        pass



# ##############################################################################

if __name__ == "__main__":
    logger.setLevel(logging.DEBUG)
    logger.info("------------------------------START TESTING")

    #  upload a movie
    # a = ShotgunBase()
    # b=NewVersion(projectid=89,
    #              shotname="tractortesting",
    #              taskname='layout',
    #              versioncode='from tractor 1',
    #              description='test version using shotgun_repos api',
    #              ownerid=38,
    #              media='/Users/Shared/UTS_Dev/test_RMS_aaocean.0006.mov')

    # query projects shots etc
    # c=Projects()
    # c.sequences(89)
    # c.shots(89,48)

    p=Person()
    logger.info("Shotgun Tractor User >>>> Login={number}   Name={name}  Email={email}".format(\
        name=p.dabname,number=p.dabnumber,email=p.email))
    logger.info("-------------------------------FINISHED TESTING")


    pe=People()
    pe.writetractorcrewfile("/Users/120988/Desktop/crew.list.txt")

    # print p.sg.schema_field_read('HumanUser')
    # s=ShotgunBase()
    # filter=
    # field=
    # print s.sg.schema_entity_read('Person')
    # print p.sg.schema_read()



'''

# ----------------------------------------------
# Find Character Assets in Sequence WRF_03 in projectX
# ----------------------------------------------
fields = ['id', 'code', 'sg_asset_type']
sequence_id = 48 # Sequence "WFR_03"
filters = [
    ['project', 'is', projectx],
    ['sg_asset_type', 'is', 'Character'],
    ['sequences', 'is', {'type': 'Sequence', 'id': sequence_id}]
    ]

assets= sg.find("Asset",filters,fields)

if len(assets) < 1:
    print "couldn't find any Assets"
else:
    print "Found %d Assets" % (len(assets))
    print assets


# ----------------------------------------------
# Find Projects id and name
# ----------------------------------------------
fields = ['id', 'name']
filters = [['id','greater_than',0]]

projects= sg.find("Project",filters,fields)

if len(projects) < 1:
    print "couldn't find any Assets"
else:
    print "Found %d Assets" % (len(projects))
    pprint.pprint(projects)
############################################################


####  make playlist
####  add version to playlist

'''
