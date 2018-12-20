#!/usr/bin/env python2
'''
This code supports all access to shotgun which is used as an authentication model for users, and
as the main production tracking database.

'''
# TODO  handle no connection to shotgun especially in dev mode
# TODO put project-if at top leve; of Project

from pprint import pprint
import string
import sys
import logging
import os
import inspect
# import Set
from shotgun_api3 import Shotgun
from renderfarm.dabtractor.factories.site_factory import JsonConfig
from renderfarm.dabtractor.factories.utils_factory import dictfromlistofdicts
from renderfarm.dabtractor.factories.utils_factory import dictfromlistofdictionaries
from renderfarm.dabtractor.factories.utils_factory import cleanname

logger = logging.getLogger(__name__)
# logger.setLevel(logging.DEBUG)
sh = logging.StreamHandler()
sh.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(levelname)5.5s \t%(name)s \t%(message)s')
sh.setFormatter(formatter)
logger.addHandler(sh)


class ShotgunBase(object):
    # set up how to access shotgun if possible
    def __init__(self):
        logger.debug("Initiated Base Class {}".format(self.__class__.__name__))
        # Get the keys to talk to shotgun from the configuration files
        self.development = None
        if os.environ.get("DABDEV"):
            self.development = os.environ.get("DABDEV")
            logger.warn("DEVMODE: You are in DEV mode: {}".format(self.development))
        self.config=JsonConfig()
        self.serverpath = str(self.config.getdefault("shotgun", "serverpath"))
        self.scriptname = str(self.config.getdefault("shotgun", "scriptname"))
        self.scriptkey  = str(self.config.getdefault("shotgun", "scriptkey"))
        try:
            self.sg = Shotgun(self.serverpath, self.scriptname, self.scriptkey)
        except RuntimeError, err:
            logger.warn("SHOTGUN: Cant talk to shotgun")
            self.sg = None
        else:
            logger.info("SHOTGUN: talking to shotgun ...... %s" % self.serverpath)


class ShotgunLink(object):
    """ this is the target in shotgun you want to link the output to"""
    def __init__(self):
        logger.debug("Initiated Class {}".format(self.__class__.__name__))
        self.username=None
        self.userid=None
        self.linkproject=None
        self.linkprojectid=None
        self.linkclass=None
        self.linksequence=None
        self.linksequenceid=None
        self.linkshot=None
        self.linkshotid=None
        self.linkasset=None
        self.linkassetid=None
        self.linkassettype=None
        self.linkassettypeid=None
        self.linktype=None
        self.linktypeid=None


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
        logger.debug("Initiated Class {}".format(self.__class__.__name__))
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
        self.shotgunlogin = None

        if shotgunlogin:
            self.shotgunlogin = shotgunlogin
            logger.debug("Shotgun Login Found: {}".format(self.shotgunlogin))
        else:
            self.shotgunlogin = os.environ["USER"]
            logger.debug("Shotgun Login Not Found using $USER: {}".format(self.shotgunlogin))
        if not self.sg:
            self.getDevInfo()
        else:
            self.getInfo()

    def getInfo(self):
        __fields = ['login', 'name', 'firstname', 'lastname', 'department',
                    'email', 'sg_tractor', 'id']
        __filters = [['login', 'is', self.shotgunlogin]]
        __person = None

        try:
            __person=self.sg.find_one("HumanUser",filters=__filters,fields=__fields)
        except RuntimeError, err:
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
                self.user_prefs = os.path.join(os.environ["DABUSERPREFS"], self.dabnumber)
        finally:
            if  not self.tractor:
                logger.critical("Shotgun user {} is not Active. Sorry.".format(self.shotgunlogin))
                sys.exit()
            logger.info("Shotgun Login {} : {}".format(self.shotgunlogin,__person))

    def getDevInfo(self):
        self.tractor = None
        self.shotgunname = "Matthew Gidney"
        self.shotgun_id = "120988"
        self.email = "matthew.gidney@uts.edu.au"
        self.login = "120988"
        self.dabname = cleanname(self.email)
        self.dabnumber = "120988"
        self.department = "development"
        self.user_prefs = os.path.join(os.environ["DABUSERPREFS"], self.dabnumber)
        self.user_work = os.path.join(os.environ["DABWORK"], "user_work", self.dabname)

    def myProjects(self):
        # Return a simple dictionary of projects and project ids
        _myprojects = {}
        try:
            __fields = ['id', 'name', 'projects']
            __filters = [['login', 'is', self.dabnumber]]
            _result = self.sg.find("HumanUser",filters=__filters,fields=__fields)
            _projects = _result[0].get('projects')
            _myprojects = dictfromlistofdicts(_projects, "name", "id")
        except RuntimeError, err:
            _myprojects = {}
        finally:
            return _myprojects


    def myGroups(self):
        # Return a simple dictionary of projects and project ids
        _mygroups = {}
        try:
            __fields = ['id', 'name', 'groups']
            __filters = [['login', 'is', self.dabnumber]]
            _result = self.sg.find("HumanUser",filters=__filters,fields=__fields)
            _groups = _result[0].get('groups')
            _mygroups = dictfromlistofdicts(_groups, "name", "id")
        except RuntimeError, err:
            _mygroups = {}
        finally:
            return _mygroups

    def me(self):
        # Return a simple dictionary of user info
        _result = []
        try:
            __fields = ['id', 'login', 'name', 'users', 'email']
            __filters = [['login', 'is', self.dabnumber]]
            _result = self.sg.find("HumanUser", filters=__filters, fields=__fields)
            # _me = dictfromlistofdicts(_result, "name", "id")
            # _email =  dictfromlistofdicts(_result, "name", "email")
        except:
            pass
        finally:
            return _result[0]

class Software(ShotgunBase):
    '''
    This class replesents software that may be configured in  projects
    '''
    def __init__(self):
        super(Software, self).__init__()
        # print the whole schema
        # pprint(self.sg.schema_entity_read())
        # pprint( self.sg.schema_field_read('Software'))
        logger.debug("Initiated Class {}".format(self.__class__.__name__))

    def getprojectsoftware(self, project_id=None):
        _software = None
        _fields = ['id', 'code','engine', 'cached_display_name', 'projects','version_names']
        _filters = [['projects', 'is', {'type': 'Project', 'id': project_id } ]]
        p=Person()
        try:
            software = p.sg.find("Software", _filters, _fields)
        except Exception, err:
            logger.warn("{}".format(err))
        else:
            logger.debug(software)
            _software = dictfromlistofdicts(software,'code','version_names')
        finally:
            logger.debug(_software)
            pass
    def getallsoftware(self):
        # return all the software that is active
        pass
    def getdefaultsoftware(self):
        # this comes from the json file
        pass

class Project(ShotgunBase):
    def __init__(self,pid=None):
        super(Project, self).__init__()
        logger.debug("Initiated Class {}".format(self.__class__.__name__))
        self.allprojects = None
        self.project_id = pid
        self.software = {}
        ## todo test pid validity


    def projects(self):
        # get all non archived projects
        _fields = ['id', 'name']
        _filters = [
            ['id', 'greater_than', 0],
            ['archived', 'is', False],
        ]
        try:
            self.allprojects = self.sg.find("Project", _filters, _fields)
        except RuntimeError, err:
            logger.warn("Projects %s".format(err))
        else:
            logger.info("Found %d Projects" % (len(self.allprojects)))
            for project in self.allprojects:
                logger.info("  Id = {:4} - {:20}".format(project['id'],project['name']))
        finally:
            return self.allprojects

    def assets(self, projectid, sg_asset_type):
        # get assets from project and asset type
        _assets = []
        _fields = ['id', 'code', 'sg_asset_type', 'type']
        _filters = [
                    ['project', 'is', {'type': 'Project', 'id': projectid} ],
                    ['sg_asset_type', 'is', sg_asset_type ],
                    # ['sg_status_list', 'is', 'ip'],
                  ]
        try:
            _assets = self.sg.find("Asset", _filters, _fields)
        except RuntimeError:
            logger.warn("Couldn't find any Assets")
        else:
            logger.info("Found {} Assets".format(len(_assets)))
        finally:
            return _assets

    def assettypes(self, projectid):
        # get asset types in project
        _assettypes = set([])
        _fields = ['sg_asset_type' ]
        _filters = [
                    ['project', 'is', {'type': 'Project', 'id': projectid}],
                  ]
        try:
            _assettype = self.sg.find("Asset", _filters, _fields)
        except RuntimeError:
            logger.warn("couldn't find any AssetTypes")
        else:
            for each in _assettype:
                _assettypes.add(each["sg_asset_type"])
            logger.info( "Found %d AssetTypes" % (len(_assettypes)))
        finally:
            return list(_assettypes)

    def assettask(self, projectid, assetid):
        # get tasks from assets and project
        _assettasks = []
        _fields = ['id','code',
                  # 'cached_display_name',
                  'content',
                  "step",
                  # 'project',
                  # 'sibling_tasks'
                  ]
        _filters = [
                    ['project', 'is', {'type': 'Project', 'id': projectid}],
                    # ['asset', 'is', {'type': 'Asset', 'id': assetid }],
                    ['entity', 'is', {'type': 'Asset', 'id': assetid}]
                    ]
        try:
            _assettask = self.sg.find("Task", _filters, _fields)
            _assettasks = dictfromlistofdicts(_assettask, "content", "id")
        except RuntimeError:
            logger.warn("Couldn't find any AssetTypes")
        else:
            logger.info("Found {} Asset Tasks".format(len(_assettask)))
        finally:
            return _assettasks

    def sequences(self, projectid):
        # get sequences from project
        fields = ['id', 'code']
        filters = [['project', 'is', {'type': 'Project', 'id': projectid}]]
        sequences= self.sg.find("Sequence", filters, fields)

        if len(sequences) < 1:
            logger.info( "couldn't find any Sequences")
        else:
            logger.info("Found %d Sequences" % (len(sequences)))
            logger.debug(sequences)

    def shots(self, project_id, sequence_id):
        # get shots from sequence and project
        _shots = None
        _fields = ['id', 'code', 'shots']
        _filters = [
            ['project', 'is', {'type': 'Project', 'id': project_id}],
            ['sg_sequence', 'is', {'type': 'Sequence', 'id': sequence_id}]
        ]
        try:
            _shot = self.sg.find("Shot", _filters, _fields)
            _shots = dictfromlistofdicts(_shot, "code", "id")
        except RuntimeError:
            logger.warn("Cant find any shots")
        finally:
            return _shots


    def shottasks(self, project_id, shot_id):
        # get tasks from shot and project
        _tasks = {}
        _fields = ['id','cached_display_name']
        _filters = [
            ['project', 'is', {'type': 'Project', 'id': project_id}],
            ['entity', 'is', {'type': 'Shot', 'id': shot_id}]
        ]
        try:
            _task = self.sg.find("Task", _filters, _fields)
            _tasks = dictfromlistofdicts(_task, "cached_display_name", "id")
        except RuntimeError:
            logger.warn("Cant find any tasks")
        finally:
            return _tasks

    def episodeFromProject(self, project_id=None):
        # get episodes from project
        _episodes = None
        _fields = ['id', 'code', 'episode' ]
        _filters = [
            ['project', 'is', {'type': 'Project', 'id': project_id}],
        ]
        try:
            _ep = self.sg.find("Episode", _filters, _fields)
            _episodes = dictfromlistofdicts(_ep, "code", "id")
        except RuntimeError, err:
            logger.warn("Cant find any episodes in project {pr}".format(pr=project_id))
        finally:
            return _episodes

    def seqFromProject(self,project_id=None):
        # get sequence from project
        _sequences = {}
        _fields = ['id', 'code']
        _filters = [
            ['project', 'is', {'type': 'Project', 'id': project_id}]
        ]
        try:
            _seq = self.sg.find("Sequence", _filters, _fields)
            _sequences = dictfromlistofdicts(_seq,"code","id")
        except RuntimeError, err:
            logger.warn("Cant find any sequences")
        finally:
            return _sequences

    def assetFromProject(self, project_id=None):
        # get assets from
        _assets = {}
        _fields = ['id', 'code']
        _filters = [
            ['project', 'is', {'type': 'Project', 'id': project_id}]
        ]
        try:
            _asset = self.sg.find("Asset", _filters, _fields)
            _assets = dictfromlistofdicts(_asset, "code", "id")
        except RuntimeError:
            logger.warn("Cant find any sequences")
        finally:
            return _assets

    def assetFromAssetType(self, project_id=None, asset_type=None):
        # get asset
        _assets = {}
        _fields = ['id','code','sg_asset_type' ]
        _filters = [
                    ['project', 'is', {'type': 'Project', 'id': project_id}],
                    ['sg_asset_type', 'is', asset_type],
        ]
        # print project_id,asset_type
        try:
            _asset = self.sg.find("Asset", _filters, _fields)
            _assets = dictfromlistofdicts(_asset, "code", "id")

        except RuntimeError:
            logger.warn("Cant find any {at} assets".format(at=asset_type))
        finally:
            return _assets

    def taskFromAsset(self, project_id=None, asset_id=None):
        # get task from asset
        _tasks = {}
        _fields = ['id','cached_display_name']
        _filters = [
            ['project', 'is', {'type': 'Project', 'id': project_id}],
            ['entity', 'is', {'type': 'Shot', 'id': asset_id}]
        ]
        try:
            _task = self.sg.find("Task", _fields, _filters)
            _tasks = dictfromlistofdicts(_task,"cached_display_name","id")
        except RuntimeError:
            logger.warn("Cant find any tasks")
        finally:
            return _tasks

    def shotFromSeq(self, project_id=None, sequence_id=None):
        # get shots from sequence and project
        _shots = {}
        _fields = ['id', 'code']
        _filters = [
            ['project', 'is', {'type': 'Project', 'id': project_id}],
            ['sg_sequence', 'is', {'type': 'Sequence', 'id': sequence_id}]
        ]
        try:
            _shottask = self.sg.find("Shot", _filters, _fields)
            _shots = dictfromlistofdicts(_shottask,"code","id")
        except RuntimeError:
            logger.warn("Cant find any shots")
        finally:
            return _shots

    def taskFromShot(self, project_id=None, shot_id=None):
        # get tasks from shot
        _tasks = {}
        _fields = ['id','cached_display_name']
        _filters = [
            ['project', 'is', {'type': 'Project', 'id': project_id}],
            ['entity', 'is', {'type': 'Shot', 'id': shot_id}]
        ]
        try:
            _task = self.sg.find("Task", _filters, _fields)
            _tasks=dictfromlistofdicts(_task, "cached_display_name", "id")
        except RuntimeError:
            logger.warn("Cant find any tasks")
        finally:
            return _tasks

    def getsoftware(self, project_id=None):
        '''
        Looks to shotgun software to get definitions
        Baseline defaults have  the group default attribute set
        Group Name is used as the software key
        Projects should only have one version set for the desktop, the defaults is just a way to identify
        the baseline in order to define envars.
        '''
        _software = None

        _fields = ['id',
                   'code',
                   # 'engine',
                   # 'cached_display_name',
                   # 'products',
                   # 'projects',
                   'group_name',
                   'group_default',
                   'version_names']
        # _filters = [['projects', 'is', {'type': 'Project', 'id': project_id } ]]
        # _filters = [['projects', 'is_not', {'type': 'Project', 'id': 0 } ]]

        if project_id is None:
            #general default
            # logger.info("Project ID is {}".format("None"))
            _filters = [['projects', 'is_not', {'type': 'Project', 'id': 0 } ],
                        ['group_default', 'is', True]
                        ]
            try:
                _software = self.sg.find("Software", _filters, _fields)
            except Exception, err:
                logger.warn("{}".format(err))
            else:
                # logger.debug(_software)
                logger.info("Software defaults - if no project is specified")
            finally:
                _softwared = dictfromlistofdictionaries(_software,'group_name','version_names')
                logger.info(_softwared)
                # pprint(_softwared)
                self.software=_softwared
        else:
            #specific for the project
            # logger.info("Project ID is {}".format(project_id))
            _filters = [['projects', 'is', {'type': 'Project', 'id': project_id } ],
                        # ['group_default', 'is', True]
                        ]
            try:
                _software = self.sg.find("Software", _filters, _fields)
            except Exception, err:
                logger.warn("{}".format(err))
            else:
                # logger.debug(_software)
                logger.info("Software for Project {}".format(project_id))
            finally:
                _softwared = dictfromlistofdictionaries(_software,'group_name','version_names')
                logger.info(_softwared)
                # pprint(_softwared)
                self.software=_softwared




class People(ShotgunBase):
    def __init__(self):
        super(People, self).__init__()
        logger.debug("Initiated Class {}".format(self.__class__.__name__))
        __fields = ['login', 'name', 'firstname', 'lastname',
                    'department', 'email', 'sg_tractor']
        __filters = [['sg_tractor','is', True]]
        __people = None
        self.people = None
        try:
            __people = self.sg.find("HumanUser", __filters, __fields)
        except RuntimeError, err:
            logger.warn("Cant get Human user info from shotgun %s"%err)
            raise
        else:
            self.people=__people
            for __person in self.people:
                try:
                    logger.info("{l:12} # {d:9}{c:24}{n:24}{e:40}".format(l=__person.get('login'),
                                                         n = __person.get('name'),
                                                         c = cleanname(__person.get('email')),
                                                         e = __person.get('email'),
                                                         d = __person.get('department').get('name')))
                except:
                    logger.warn("Problem with user {}".format(__person))

    @classmethod
    def cleanname(cls, dirtyemail):
        _return = None
        try:
            _return = cleanname(dirtyemail)
        except AssertionError:
            pass

        return _return

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

class Schema(ShotgunBase):
    # just to see the schema

    def __init__(self):
        super(Schema, self).__init__()

    def task(self):
        pprint(self.sg.schema_field_read("Task"))

    def shot(self):
        pprint(self.sg.schema_field_read("Shot"))

    def asset(self):
        pprint(self.sg.schema_field_read("Asset"))

    def humanuser(self):
        pprint(self.sg.schema_field_read("HumanUser"))

    def episode(self):
        pprint(self.sg.schema_field_read("Episode"))

    def sequence(self):
        pprint(self.sg.schema_field_read("Sequence"))


class Version(ShotgunBase):
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
        super(Version, self).__init__()
        logger.debug("Initiated Class {}".format(self.__class__.__name__))

        self.project = {'type': 'Project', 'id': projectid}
        self.shotid=shotid
        self.taskid=taskid
        self.versioncode = versioncode
        self.description = description
        self.ownerid = ownerid
        self.tag = tag
        self.media = media
        self.hasslate = True
        logger.info("SHOTGUN: File to upload ...... %s"%self.media)
        if projectid and shotid and taskid:
            self.data = { 'project': self.project,
                         'code': self.versioncode,
                         'description': self.description,
                         'sg_status_list': 'rev',  # pending review
                         # "sg_sequence": {"type": "Sequence", "id": 109},
                         'entity': {'type':'Shot', 'id':self.shotid},
                         'sg_task': {'type':'Task', 'id':self.taskid},
                         'user': {'type': 'HumanUser', 'id': self.ownerid },
                         'sg_movie_has_slate' : self.hasslate
                          }
        elif projectid and shotid and not taskid:
            self.data = { 'project': self.project,
                         'code': self.versioncode,
                         'description': self.description,
                         'sg_status_list': 'rev',  # pending review
                         # "sg_sequence": {"type": "Sequence", "id": 109},
                         'entity': {'type':'Shot', 'id':self.shotid},
                         # 'sg_task': {'type':'Task', 'id':self.taskid},
                         'user': {'type': 'HumanUser', 'id': self.ownerid },
                          'sg_movie_has_slate' : self.hasslate
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
    logger.debug(">>>> TESTING {} ------".format(__file__))
    # ----------------------------------------------
    # upload a movie example
    # a = ShotgunBase()
    # b=Version(projectid=171,
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

    # ############ SOFTWARE TEST
    logger.debug("TEST CLASS SOFTWARE")
    # p=Project()
    # p.getsoftware()
    # pprint (p.projects())
    # s=Software()
    # aa=s.getprojectsoftware(176)
    # q=Project()
    # q.getsoftware(176)
    # raise SystemExit(".......done and exiting")


    ########## PERSON TEST
    # p = Person("120988")
    # print "Shotgun Tractor User >>>> Login={number}   Name={name}  Email={email} Dept={dept}".format(name=p.dabname,number=p.dabnumber,email=p.email,dept=p.department)
    #
    # print p.myProjects()
    # print p.myGroups()
    # print p.me()
    # raise SystemExit(".......done and exiting")

    logger.debug(">>>> SCHEMA {} ------".format(__file__))
    schema=Schema()
    # schema.task()
    # schema.asset()
    # schema.shot()
    # schema.humanuser()
    # schema.episode()
    # schema.sequence()


    # ############# PROJECT TEST
    # pr = Project()
    # print pr.projects()
    # print pr.assettypes(175)
    # print pr.assets(175, "Prop")
    # print pr.assettask(175,1241)
    # print pr.assetFromAssetType(175,"character")

    # pr.sequences(175)
    # pr.shots(175,304)
    # pr.shottasks(175,4140)
    # p.assetFromProject()
    # p.episodeFromProject(135)
    # pr.taskFromAsset(175,1241)


    # ############# PEOPLE TEST
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

    # pprint( p.sg.schema_field_read('Asset'))
    # project_id = _myprojects.get('YR3_2017--171') # 171 # Demo Project
    # fields = ['id', 'code']
    # filters = [['project', 'is', {'type': 'Project', 'id': project_id} ]]
    # asset = p.sg.find("Assets",filters,fields)
    # pprint(asset)
    # _assets = dictfromlistofdicts(assets,"code","id")
    #
    # pprint(p.sg.schema_entity_read('Shot'))
    # pprint(p.sg.schema_field_read('Shot'))






