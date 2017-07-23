#!/usr/bin/env python
'''
This code supports all access to shotgun which is used as an authentication model for users, and
as the main production tracking database.

'''
# TODO  handle no connection to shotgun especially in dev mode

from pprint import pprint
import string
import sys
import logging
import os
from sww.shotgun_api3 import Shotgun
from sww.renderfarm.dabtractor.factories.site_factory import JsonConfig
from sww.renderfarm.dabtractor.factories.utils_factory import dictfromlistofdicts
from sww.renderfarm.dabtractor.factories.utils_factory import cleanname

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
sh = logging.StreamHandler()
sh.setLevel(logging.INFO)
formatter = logging.Formatter('%(levelname)5.5s \t%(name)s \t%(message)s')
sh.setFormatter(formatter)
logger.addHandler(sh)


class ShotgunBase(object):
    # set up how to access shotgun if possible
    def __init__(self):
        # Get the keys to talk to shotgun from the configuration files
        self.development = None
        if os.environ.get("DABDEV"):
            self.development = os.environ.get("DABDEV")
            logger.warn("DEVMODE: You are in DEV mode")

        self.config=JsonConfig()
        self.serverpath = str(self.config.getdefault("shotgun", "serverpath"))
        self.scriptname = str(self.config.getdefault("shotgun", "scriptname"))
        self.scriptkey  = str(self.config.getdefault("shotgun", "scriptkey"))
        try:
            self.sg = Shotgun(self.serverpath, self.scriptname, self.scriptkey)
        except Exception, err:
            logger.warn("SHOTGUN: Cant talk to shotgun")
            self.sg=None
        else:
            logger.info("SHOTGUN: talking to shotgun ...... %s" % self.serverpath)

class Person(ShotgunBase):
    """
    This is a model of the user account as registered in shotgun
    Basically used for authentication, need a proxy account if we cant reach shotgun.
    """
    def __init__(self, shotgunlogin=None):
        """
        :param shotgunlogin: optional name to use - defaults to $USER
        """
        super(Person, self).__init__()
        self.tractor = None
        self.shotgunname = None
        self.shotgun_id = None
        self.email = None
        self.login = None
        self.user_work = None
        self.dabname = None
        self.dabnumber = None
        self.department = None
        self.user_prefs = None
        self.user_work = None

        if shotgunlogin:
            self.shotgunlogin = shotgunlogin
        else:
            self.shotgunlogin = os.environ["USER"]

        if not self.sg:
            self.getDevInfo()
        else:
            self.getInfo()


    def getInfo(self):

        __fields = ['login','name','firstname','lastname','department','email','sg_tractor','id']
        __filters =  [['login','is', self.shotgunlogin]]
        __person=None

        try:
            __person=self.sg.find_one("HumanUser",filters=__filters,fields=__fields)
        except Exception, err:
            logger.warn("%s"%err)
            raise
        else:
            if __person.has_key('sg_tractor'):
                self.tractor = __person.get('sg_tractor')
            if __person.has_key('name'):
                self.shotgunname = __person.get('name')
            if __person.has_key('email'):
                self.email =__person.get('email')
                self.dabname = cleanname(self.email)
                self.user_work = os.path.join(os.environ["DABWORK"], "user_work", self.dabname)
            if __person.has_key('department'):
                self.department = __person.get('department').get('name')
            if __person.has_key('id'):
                self.shotgun_id = __person.get('id')
            if __person.has_key('login'):
                self.login = __person.get('login')
                self.dabnumber = self.login
                self.user_prefs = os.path.join(os.environ["DABWORK"], "user_prefs", self.dabnumber)
        finally:
            if  not self.tractor:
                    logger.critical("Shotgun user {} is not Active. Sorry.".format(self.shotgunlogin))
                    sys.exit()
            logger.debug("Shotgun Login {} : {}".format(self.shotgunlogin,__person))

    def getDevInfo(self):
        self.tractor = None
        self.shotgunname = "Matthew Gidney"
        self.shotgun_id = "120988"
        self.email = "matthew.gidney@uts.edu.au"
        self.login = "120988"
        self.dabname = cleanname(self.email)
        self.dabnumber = "120988"
        self.department = "development"
        self.user_prefs = os.path.join(os.environ["DABWORK"], "user_prefs", self.dabnumber)
        self.user_work = os.path.join(os.environ["DABWORK"], "user_work", self.dabname)

    def myProjects(self):
        try:
            __fields = ['id', 'login','name', 'users', 'email', 'projects', 'groups']
            __filters = [['login','is',self.dabnumber]]
            _result = self.sg.find("HumanUser",filters=__filters,fields=__fields)
            _me = dictfromlistofdicts(_result,"name","id")
            _projects=_result[0].get('projects')
            _myprojects = dictfromlistofdicts(_projects,"name","id")
        except Exception, err:
            _myprojects={}
        else:
            pass
        finally:
            return _myprojects

    def seqFromProject(self,project_id=None):
        # project_id = _myprojects.get('YR3_2017--171') # 171 # Demo Project
        try:
            fields = ['id', 'code']
            filters = [['project', 'is', {'type': 'Project', 'id': project_id} ]]
            seq = self.sg.find("Sequence",filters,fields)
            _sequences = dictfromlistofdicts(seq,"code","id")
        except Exception, err:
            logger.warn("Cant find any sequences")
            _sequences={}
        finally:
            return _sequences

    def assetFromProject(self, project_id=None):
        # project_id = _myprojects.get('YR3_2017--171') # 171 # Demo Project
        _assets={}
        try:
            fields = ['id', 'code']
            filters = [['project', 'is', {'type': 'Project', 'id': project_id} ]]
            seq = self.sg.find("Asset",filters,fields)
            _assets = dictfromlistofdicts(seq,"code","id")
        except Exception, err:
            logger.warn("Cant find any sequences")
        finally:
            return _assets

    def assettypeFromAsset(self,project_id=None,asset_id=None):
        pass


    def taskFromAsset(self,project_id=None, asset_id=None):
        # asset_id = _shots.get('ssA_gp1_tm2_01--3127')
        try:
            fields = ['id','cached_display_name']
            filters = [
                ['project', 'is', {'type': 'Project', 'id': project_id}],
                ['entity', 'is', {'type': 'Shot', 'id': asset_id}]
                 ]
            task = self.sg.find("Task",filters,fields)
            _tasks=dictfromlistofdicts(task,"cached_display_name","id")
        except Exception, err:
            logger.warn("Cant find any tasks")
            _tasks={}
        finally:
            return _tasks

    def shotFromSeq(self,project_id=None,sequence_id=None):
        # sequence_id = _sequences.get("ssA_gp1--277")
        try:
            fields = ['id', 'code']
            filters = [
                ['project', 'is', {'type': 'Project', 'id': project_id}],
                ['sg_sequence', 'is', {'type': 'Sequence', 'id': sequence_id}]
                 ]
            shottask = self.sg.find("Shot", filters, fields)
            _shots=dictfromlistofdicts(shottask,"code","id")
        except Exception, err:
            logger.warn("Cant find any shots")
            _shots={}
        finally:
            return _shots

    def taskFromShot(self,project_id=None,shot_id=None):
        # shot_id = _shots.get('ssA_gp1_tm2_01--3127')
        try:
            fields = ['id','cached_display_name']
            filters = [
                ['project', 'is', {'type': 'Project', 'id': project_id}],
                ['entity', 'is', {'type': 'Shot', 'id': shot_id}]
                 ]
            task = self.sg.find("Task",filters,fields)
            _tasks=dictfromlistofdicts(task,"cached_display_name","id")
        except Exception, err:
            logger.warn("Cant find any tasks")
            _tasks={}
        finally:
            return _tasks


class Projects(ShotgunBase):
    def __init__(self):
        super(Projects, self).__init__()
        self.allprojects=None
        self.projects()

    def projects(self):
        __fields = ['id', 'name']
        __filters = [['id', 'greater_than', 0]]
        try:
            self.allprojects = self.sg.find("Project",__filters,__fields)
        except Exception, err:
            logger.warn("Projects %s".format(err))
        else:
            logger.info("Found %d Projects" % (len(self.allprojects)))
            for project in self.allprojects:
                logger.debug("  Id = {:4} - {:20}".format(project['id'],project['name']))
            pprint(self.allprojects)

    def assets(self, projectid):
        # returns a list of dicts  [ {code:, type:, id: } ] of assets for a given projectid

        fields = ['id', 'code', 'sg_asset_type', 'type']
        filters = [
                    ['project', 'is', {'type': 'Project', 'id': projectid} ],
                    # ['sg_status_list', 'is', 'ip'],
                  ]

        _assets = self.sg.find("Asset", filters, fields)

        if len(_assets) < 1:
            print "couldn't find any Assets"
        else:
            print "Found %d Assets" % (len(_assets))
            pprint (_assets)

    def assettype(self, projectid, assetid):
        # returns a list of dicts  [ {code:, type:, id: } ] of sequences for a given projectid
        fields = ['id', 'code', 'sg_asset_type' ]
        filters = [
                    ['project', 'is', {'type': 'Project', 'id': projectid}],
                    # ['asset', 'is', {'type': 'Asset', 'id': assetid }],
                    # ['entity', 'is', {'type': 'Asset', 'id': assetid}]
                  ]
        _assettype = self.sg.find("Asset", filters, fields)

        if len(_assettype) < 1:
            print "couldn't find any AssetTypes"
        else:
            print "Found %d AssetTypes" % (len(_assettype))
            pprint (_assettype)

    def assettask(self, projectid, assetid):
        # returns a list of dicts  [ {code:, type:, id: } ] of sequences for a given projectid
        fields = ['id','code',
                  # 'cached_display_name',
                  'content',
                  "step",
                  # 'project',
                  # 'sibling_tasks'
                  ]
        filters = [
                    ['project', 'is', {'type': 'Project', 'id': projectid}],
                    # ['asset', 'is', {'type': 'Asset', 'id': assetid }],
                    ['entity', 'is', {'type': 'Asset', 'id': assetid}]
                    ]
        _assettask = self.sg.find("Task", filters, fields)

        if len(_assettask) < 1:
            print "couldn't find any AssetTypes"
        else:
            print "Found %d Asset Tasks" % (len(_assettask))
            pprint (_assettask)
        # pprint (self.sg.schema_field_read("Task"))

    def sequences(self, projectid):
        # returns a list of dicts  [ {code:, type:, id: } ] of sequences for a given projectid
        fields = ['id', 'code']
        filters = [['project', 'is', {'type': 'Project', 'id': projectid}]]
        sequences= self.sg.find("Sequence", filters, fields)

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
            logger.warn("Cant get Human user info from shotgun %s"%err)
            raise
        else:
            self.people=__people
            for __person in self.people:
                try:
                    logger.info("{l:12} # {d:9}{c:24}{n:24}{e:40}".format(l=__person.get('login'),
                                                         n=__person.get('name'),
                                                         c = cleanname(__person.get('email')),
                                                         e=__person.get('email'),
                                                         d=__person.get('department').get('name')))
                except:
                    logger.warn("Problem with user {}".format(__person))


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
                _line='"{l}",   # {d:9}{c:24}{n:24}{e:40}\n'.format(l=person.get('login'),
                                                         n=person.get('name'),
                                                         c=cleanname(person.get('email')),
                                                         e=person.get('email'),
                                                         d=person.get('department').get('name'))
                _file.write(_line)
            _file.close()
        finally:
            logger.info("Wrote tractor crew file: {}".format(self.crewfilefullpath))



class NewVersion(ShotgunBase):
    # new version object
    def __init__(self, media = None,
                 projectid = None,
                 shotid = None,
                 taskid = None,
                 versioncode = 'test colours seq.mov',
                 description = 'Created from Proxy Farm Job',
                 ownerid = None,
                 tag = "RenderFarm Proxy"
                 ):
        super(NewVersion, self).__init__()
        self.project = {'type': 'Project', 'id': projectid}
        self.shotid=shotid
        self.taskid=taskid
        self.versioncode = versioncode
        self.description = description
        self.ownerid = ownerid
        self.tag = tag
        self.media = media
        logger.info("SHOTGUN: File to upload ...... %s"%self.media)
        if projectid and shotid and taskid:
            self.data = { 'project': self.project,
                         'code': self.versioncode,
                         'description': self.description,
                         'sg_status_list': 'rev',  # pending review
                         # "sg_sequence": {"type": "Sequence", "id": 109},
                         'entity': {'type':'Shot', 'id':self.shotid},
                         'sg_task': {'type':'Task', 'id':self.taskid},
                         'user': {'type': 'HumanUser', 'id': self.ownerid }
                          }
        elif projectid and shotid and not taskid:
            self.data = { 'project': self.project,
                         'code': self.versioncode,
                         'description': self.description,
                         'sg_status_list': 'rev',  # pending review
                         # "sg_sequence": {"type": "Sequence", "id": 109},
                         'entity': {'type':'Shot', 'id':self.shotid},
                         # 'sg_task': {'type':'Task', 'id':self.taskid},
                         'user': {'type': 'HumanUser', 'id': self.ownerid }
                          }
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
    logger.info("--------- TESTING {} ------".format(__file__))
    # ----------------------------------------------
    # upload a movie example
    # a = ShotgunBase()
    # b=NewVersion(projectid=171,
    #              shotid=3130,
    #              taskid=9374,
    #              versioncode='from tractor 1',
    #              description='test version using shotgun_repos api',
    #              ownerid=381,
    #              media='/Users/Shared/UTS_Dev/Volumes/dabrender/work/user_work/matthewgidney/testing2017/movies/seq1.mov')
    # ----------------------------------------------
    # Query projects shots etc
    # c=Projects()
    # c.sequences(89)
    # c.shots(89,48)
    # sys.exit()
    #
    # ----------------------------------------------
    p=Person()
    # pprint(dir(p))
    logger.info("Shotgun Tractor User >>>> Login={number}   Name={name}  Email={email} Dept={dept}".format(\
        name=p.dabname,number=p.dabnumber,email=p.email,dept=p.department))
    logger.info("--------- FINISHED TESTING -------------")

    print p.myProjects()
    p.assetFromProject()


    pr=Projects()
    pr.assets(175)

    pr.assettask(175,1241)


    sys.exit()

    # ----------------------------------------------
    # pe=People()
    # print pe.people
    # pe.writetractorcrewfile("/Users/120988/Desktop/crew.list.txt")
    #
    # ----------------------------------------------
    # Find Character Assets in Sequence WRF_03 in projectX
    # fields = ['id', 'code', 'sg_asset_type']
    # sequence_id = 48 # Sequence "WFR_03"
    # filters = [
    #     ['project', 'is', "projectx"],
    #     ['sg_asset_type', 'is', 'Character'],
    #     ['sequences', 'is', {'type': 'Sequence', 'id': sequence_id}]
    #     ]
    #
    # assets = sg.find("Asset", filters, fields)
    #
    # if len(assets) < 1:
    #     print "couldn't find any Assets"
    # else:
    #     print "Found %d Assets" % (len(assets))
    #     print assets
    #
    # ----------------------------------------------
    # Find Projects id and name
    #
    # >>> # Find Character Assets in Sequence 100_FOO
    # >>> # -------------
    # >>> fields = ['id', 'code', 'sg_asset_type']
    # >>> sequence_id = 2 # Sequence "100_FOO"
    # >>> project_id = 4 # Demo Project
    # >>> filters = [
    # ...     ['project', 'is', {'type': 'Project', 'id': project_id}],
    # ...     ['sg_asset_type', 'is', 'Character'],
    # ...     ['sequences', 'is', {'type': 'Sequence', 'id': sequence_id}]
    # ... ]
    # >>> assets= sg.find("Asset",filters,fields)

    # ----------------------------------------------
    # p=ShotgunBase()
    # _p=p.sg.schema_field_read('Project')
    #
    # for each in _p.keys():
    #     print each, _p[each]
    # pprint(_p)

    # __fields = ['id', 'name', 'users', 'archived']
    # __filters = [['archived','is',False]]
    # _result = p.sg.find("Project",filters=__filters,fields=__fields)
    # pprint(_result)
    # projects = Projects()
    # pprint.pprint(projects.projects)


    # ----------------------------------------------
    # p=ShotgunBase()
    # _p=p.sg.schema_field_read('HumanUser')
    #
    # for each in _p.keys():
    #     print each, _p[each]
    # pprint(_p)
    # pprint( p.sg.schema_field_read('HumanUser'))
    #
    # __fields = ['id', 'login','name', 'users', 'email', 'projects', 'groups']
    # __filters = [['login','is','120988']]
    # _result = p.sg.find("HumanUser",filters=__filters,fields=__fields)
    # pprint(_result)
    # projects = Projects()
    # pprint(projects.projects)

    ####  make playlist
    ####  add version to playlist

    # mg=Person("120988")
    # print(mg.myProjects())
    # print mg.seqFromProject(171)
    # print mg.shotFromSeq(171,281)
    # print mg.taskFromShot(171,3143)
    # sys.exit()

    # Find Sequences..........................
    # project_id = _myprojects.get('YR3_2017--171') # 171 # Demo Project
    # fields = ['id', 'code']
    # filters = [['project', 'is', {'type': 'Project', 'id': project_id} ]]
    # seq = p.sg.find("Sequence",filters,fields)
    # pprint(seq)
    # _sequences = dictfromlistofdicts(seq,"code","id")
    #
    # pprint(p.sg.schema_entity_read('Shot'))
    # pprint(p.sg.schema_field_read('Shot'))

    # Find Shots ..............................
    # sequence_id = _sequences.get("ssA_gp1--277")
    # fields = ['id', 'code']
    # filters = [
    #     ['project', 'is', {'type': 'Project', 'id': project_id}],
    #     ['sg_sequence', 'is', {'type': 'Sequence', 'id': sequence_id}]
    #      ]
    # shottask = p.sg.find("Shot", filters, fields)
    # _shots=dictfromlistofdicts(shottask,"code","id")
    # pprint(_shots)
    # pprint( p.sg.schema_field_read('Task'))

    # >>> # Find Tasks ..............................
    # shot_id = _shots.get('ssA_gp1_tm2_01--3127')
    # fields = ['id','cached_display_name']
    # filters = [
    #     ['project', 'is', {'type': 'Project', 'id': project_id}],
    #     ['entity', 'is', {'type': 'Shot', 'id': shot_id}]
    #      ]
    # task = p.sg.find("Task",filters,fields)
    # # pprint(task)
    # _tasks=dictfromlistofdicts(task,"cached_display_name","id")


    # >>> # Find Assets..........................

    pprint( p.sg.schema_field_read('Asset'))
    project_id = _myprojects.get('YR3_2017--171') # 171 # Demo Project
    fields = ['id', 'code']
    filters = [['project', 'is', {'type': 'Project', 'id': project_id} ]]
    asset = p.sg.find("Assets",filters,fields)
    pprint(asset)
    _assets = dictfromlistofdicts(assets,"code","id")
    #
    # pprint(p.sg.schema_entity_read('Shot'))
    # pprint(p.sg.schema_field_read('Shot'))






