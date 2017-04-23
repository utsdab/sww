#!/usr/bin/env rmanpy

"""
To do:
"""

###############################################################
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
sh = logging.StreamHandler()
sh.setLevel(logging.INFO)
formatter = logging.Formatter('%(levelname)5.5s \t%(name)s \t%(message)s')
sh.setFormatter(formatter)
logger.addHandler(sh)
###############################################################

import os, sys
from pprint import pprint
import tractor.api.query as tq
import sww.renderfarm.dabtractor.factories.environment_factory as envfac
import json

class TQuery(object):
    def __init__(self):
        env=envfac.Environment()
        _hostname = env.config.getdefault("tractor","engine")
        _port = env.config.getdefault("tractor","port")
        _user = env.config.getdefault("tractor","jobowner")
        self.tq = tq.setEngineClientParam(hostname=_hostname, port=int(_port), user=_user, debug=False)

class JobDetails(TQuery):
    def __init__(self,jid=None):
        super(JobDetails, self).__init__()
        self.jid=jid

        try:
            _job = tq.jobs("jid in [{}]".format(jid),columns=["jid", "title","metadata","numerror","spooled"])
            _jmd=json.loads(_job[0]["metadata"])

            for key in _jmd.keys():
                self.__dict__[key]=_jmd.get(key)

        except Exception, err:
            logger.critical("Metadata Error JID () : {}".format(self.jid,err))
        else:
            self.title = _job[0]["title"]
            self.spooltime = _job[0]["spooltime"]

class TaskDetails(TQuery):
    def __init__(self,jid,tid):
        super(TaskDetails, self).__init__()
        pass
        try:
            pass
        except:
            pass

if __name__ == '__main__':

    print "**********************************************"
    j=JobDetails(jid=8479)

    pprint(j.__dict__)
    #
    # print "**********************************************"
    # k=JobDetails()
    # pprint(k.__dict__)


