#!/usr/bin/env rmanpy

"""
To do:
    cleanup routine for rib
    create a ribgen then prman version
    check and test options
    run farmuser to check is user is valid


    from maya script editor.......
    import sys
    sys.path.append("/Users/Shared/UTS_Dev/gitRepositories/utsdab/usr")
    sys.path.append("/Applications/Pixar/Tractor-2.2/lib/python2.7/site-packages")
    from software.maya.uts_tools import tractor_submit_maya_UI as ts
    import rmanpy
    ts.main()

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

################################
env=envfac.Environment()
# tractorjob=envfac.TractorJob()
_thisuser = os.getenv("USER")
_hostname = env.config.getdefault("tractor","engine")
_port = env.config.getdefault("tractor","port")
_user = env.config.getdefault("tractor","jobowner")

tq.setEngineClientParam(hostname=_hostname, port=int(_port), user=_user, debug=True)

class JobDetails(object):
    def __init__(self,jid=None):
        self.jid=jid
        _mdata={}

        try:
            _job = tq.jobs("jid in [{}]".format(jid),columns=["jid", "title","metadata","numerror","spooled"])
            _jid=_job[0]["jid"]
            _title=_job[0]["title"]
            _mdata["jid"]=_job[0]["jid"]
            _mdata["title"]=_job[0]["title"]
            _metadata=_job[0]["metadata"]
            _split=_metadata.split(" ")
            for s in _split:
                _bits=s.split("=")
                _mdata[_bits[0]]=_bits[1]

        except Exception, err:
            logger.critical("Metadata Error JID () : {}".format(self.jid,err))
        else:
            # pprint(_job)
            self.username=_mdata.get("username")
            self.email=_mdata.get("email")
            self.usernumber=_mdata.get("usernumber")
            self.title=_mdata.get("title")
            self.spooltime =_job[0]["spooltime"]

def getjobs():
    job = tq.jobs("owner in [pixar] and spooltime < -1d",columns=["jid", "title","metadata","numerror"],sortby=["title"])
    '''
    jobs = tq.jobs("owner in [freddie brian john roger] and spooltime < -8d")
    tq.jobs(columns=["jid", "owner", "title", "metadata"])
    tq.jobs("active or ready", sortby=["-priority", "spooltime"])
    tq.jobs("active", sortby=["-numactive"], limit=10)
    tq.tasks("state=error and Job.spooltime > -24h", columns=["Job.spooltime", "Job.title"], sortby=["Job.priority"])
    '''
    pprint(job)

    jids=[]

    for i,j in enumerate(job):
        # print i,j.values()
        jids.append( j.get("jid") )
    return jids



def gettimes():
    jids=getjobs()
    report=[]
    for i,j in enumerate(jids):
        invocation = tq.invocations("jid={}".format(j),columns=["elapsedreal","numslots"])
        totalseconds = 0.0
        title=tq.jobs("jid={}".format(j),columns=["title","numerror","numtasks","numdone"])
        errors=tq.jobs("jid={}".format(j),columns=["numerror","numtasks","numdone"])
        # print errors
        #err=errors.get("numerror")
        # err=errors[0]
        # done=errors[2]
        # tasks=errors[1]
        # done=errors.get("numdone")
        # tasks=errors.get("numtasks")
        for i,inv in enumerate(invocation):
            try:
                totalseconds=totalseconds+(inv.get("elapsedreal")*inv.get("numslots"))
            except:
                pass
        # print "total {} core seconds".format(totalseconds)
        corehours=totalseconds/60.0/60.0
        report.append( ",{},${:.2f},{}".format(j,
                                                        # tasks,done,err,
                                                        corehours*0.2,title[0].get("title") ))

    for i,r in enumerate(report):
        print i,r
def getstuff(days=1):

    report=[]
    jobs=tq.jobs("owner in [pixar] and spooltime > -{}d".format(int(days)),
                 columns=["jid","title","numerror","numtasks","numdone","elapsedsecs","maxslots"],
                 # limit=5,
                 sortby=["elapsedsecs"])

    report.append( "i,costjid, tasks, errors, done, cost $, title, corehours")

    for i,j in enumerate(jobs):
        # print j
        jid=j.get("jid")
        tasks=j.get("numtasks")
        errors=j.get("numerror")
        done=j.get("numdone")
        title=j.get("title")
        elapsedsecs=j.get("elapsedsecs")
        # maxslots=j.get("maxslots")

        invocation = tq.invocations("jid={}".format(jid),columns=["elapsedreal","numslots"])
        totalseconds = 0.0


        for i,inv in enumerate(invocation):
            try:
                totalseconds=totalseconds+(inv.get("elapsedreal")*inv.get("numslots"))
            except:
                pass
        # print "total {} core seconds".format(totalseconds)
        corehours=totalseconds/60.0/60.0
        cost=corehours*0.2
        report.append( ",{jid}, {tasks}, {errors}, {done}, {cost:.02f}, {title}, {corehours:.01f}".format(jid=jid,
                                                        tasks=tasks,errors=errors,done=done,
                                                        cost=cost, title=title,
                                                        corehours=corehours))


    for i,r in enumerate(report):
        print i,r


if __name__ == '__main__':
    # getjobs()
    # getstuff(1)

    print "**********************************************"
    j=JobDetails(8464)
    pprint(j.__dict__)

    print "**********************************************"
    k=JobDetails()
    pprint(k.__dict__)
