#!/usr/bin/python

'''
Useful user functions
'''

import datetime
import os
import string
import subprocess
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

def printdict(dict):
    if type(dict) == type({"a": "1"}):
        for i, key in enumerate(dict.keys()):
            try:
                logger.info("DICT {:3} {:20}: {}".format(i, key, dict.get(key)))
            except:
                logger.info("Skipping {}").format(key)


def ensure_dir(f):
    d = os.path.dirname(f)
    logger.debug("Checking {}".format(f))
    if not os.path.exists(d):
        logger.warn("Not found, Making {}".format(f))
        os.makedirs(os.path.expandvars(d))
    else:
        logger.debug("Found dir {}".format(f))

def ensure_link(f):
    # check link and if not then raise
    logger.debug("Checking link {}".format(f))
    if not os.path.islink(f):
        logger.warn("Link Not found {}".format(f))
        raise
    else:
        logger.debug("Found link {}".format(f))


def sendmail(mailto,
             mailsubject,
             mailbody,
             mailfrom):
    logger.debug("%s %s %s %s" % (mailto, mailsubject, mailbody, mailfrom))

    sendmail_location = "/usr/sbin/sendmail"  # sendmail location
    p = os.popen("%s -t" % sendmail_location, "w")
    p.write("From: %s\n" % str(mailfrom[0]))
    p.write("To: %s\n" % str(mailto[0]))
    p.write("Subject: %s\n" % str(mailsubject[0]))
    p.write("\n")  # blank line separating headers from body
    p.write("%s" % str(mailbody[0]))
    status = p.close()
    if status != 0:
        print "Sendmail exit status", status
    return status


def getfrompathlist(filetoget, iconpath="ICONPATH"):
    # the path list is much assumed to be much like the environment PATH list separated by :
    # the file is without string
    # returns the matching full path
    _iconpaths = []
    _icon = None

    try:
        _iconpath_paths = os.environ[iconpath].split(os.pathsep)
    except KeyError,e:
        logger.warn("Something wrong with icon path variable {}".format(iconpath))

    for i, _path in enumerate(_iconpaths):
        if os.path.isfile(os.path.join(_path, filetoget)):
            _icon = os.path.join(_path, filetoget)
            logger.debug("Found icon: {}".format(_icon))

    return _icon


def getvalues(entries):
    for entry in entries:
        field = entry[0]
        text = entry[1].get()
        logger.info('%s: "%s"' % (field, text))


def usedirmap(inputstring):
    # wraps a command string up as per dirmap needs in pixar tractor eg. %D(mayabatch)
    return '%D({thing})'.format(thing=inputstring)


def expandargumentstring(inputargs=""):
    """
    This takes a string like "-r 2 -l 4" and returns
    {-r} {2} {-l} {4} which is what tractor wants for arguments
    """
    mystring = inputargs.strip()  # the while loop will leave a trailing space,
                  # so the trailing whitespace must be dealt with
                  # before or after the while loop
    while '  ' in mystring:
        mystring = mystring.replace('  ', ' ')

    arglist = mystring.split(" ")
    outputstring = "} {".join(arglist)
    return outputstring

def getSeqTemplate(exampleFrameName):
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
            _split = exampleFrameName.split(".")
            _ext = _split[-1]
            _frame = _split[-2]
            _precision = len(_frame)
            _base = ".".join(_split[:-2])
        except Exception, err:
            logger.warn("Cant split the filename properly needs to be of format name.####.ext : {}".format(err))
            seqbasename = None
            seqtemplatename = None
        else:
            seqbasename = _base
            seqtemplatename = "{b}.{:#^{p}}.{e}".format('#', b=_base, p=_precision, e=_ext)
        return (seqbasename,seqtemplatename)

def hasBadNaming(fullpath):
    # TODO add some checking of names
    _result=None
    # print string.punctuation
    # mypunctuation = '''!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~'''
    mypunctuation = '''!"#$%&'()*+,-/:;<=>?@[\]^`{|}~'''


    nowhitespace = fullpath.translate(string.maketrans("",""), string.whitespace)
    expandedpath =  os.path.expandvars(fullpath)
    logger.info("***************************************************")
    logger.info("Path to check: {}".format(fullpath))
    logger.info("      becomes: {}".format(expandedpath))

    if fullpath != nowhitespace:
        logger.info("*****************************************")
        logger.critical("No SPACES in names please!!!")
        _result=fullpath
    else:
        dirname = expandedpath
        path_split = []
        while True:
            dirname,leaf = os.path.split(dirname)
            if (leaf):
                path_split = [leaf] + path_split #Adds one element, at the beginning of the list
            else:
                break;
        for bit in path_split:
            nopunctuation= bit.translate(string.maketrans("",""), mypunctuation)
            if bit != nopunctuation:
                logger.info("*****************************************")
                logger.critical("FIX Your Badly named file or directory: {}".format(bit))
                logger.critical("    No PUNCTUATION in names please!!!")
                _result=bit
                break
    logger.info("*****************************************")
    return _result


def getfloat(inputstring):
    """
    :param inputstring:
    :return:
    """
    cleanstring = inputstring.strip(string.punctuation)
    return cleanstring

def getnow():
    return datetime.datetime.now().strftime("%Y-%m-%d__%H-%M")

def makedirectoriesinpath(path):
    #looks at a path and makes the directories that may be missing
    try:
        os.makedirs(os.path.expandvars(os.path.dirname(path)))
        logger.info("Made directory {}".format(path))
    except Exception,err:
        logger.warn("Didnt make {} {}".format(path,err))
        # sys.exit("Cant make directory")
        raise

def dictfromlistofdicts(dlist=[{}],dkey="code",dvalue="id"):
        #  used for shotgun find returns,  cherry pick dictionary values to be the key and value in a simple new
        # dictionary
        logger.debug("...{} Key={} Value={}".format(dlist[0].keys(),dkey,dvalue))
        _result={}
        for i,d in enumerate(dlist):
            _uniqdkey="{} ({})".format(d.get(dkey),d.get(dvalue))
            _result[_uniqdkey]=d.get(dvalue)
        logger.debug("{}".format( _result ))
        return _result

def truncatepath(inputpath,truncatebit):
    if os.path.isdir(inputpath):
        _pathbits = os.path.abspath(inputpath).split("/")
        _truncated = []
        _matched = False
        for i,bit in enumerate(_pathbits):
            if bit == truncatebit:
                _matched = True
                break
            print i, bit
            _truncated.append(bit)
        _truncatedpath="/".join(_truncated)
        if os.path.isdir(_truncatedpath):
            return _truncatedpath
    else:
        logger.warn("Not a path when truncating")

def cleanname(email):
        _nicename = email.split("@")[0]
        _compactnicename = _nicename.lower().translate(None, string.whitespace)
        _cleancompactnicename = _compactnicename.translate(None, string.punctuation)
        logger.debug("Cleaned name is : %s" % _cleancompactnicename)
        return _cleancompactnicename


class RenderOutput(object):
    '''
    Class to handle render output from renderman etc
    pass in sequences for nuke or proxy generation
    '''
    def __init__(self,filepath=None):
        self.toplevelfilepath=filepath
        logger.debug("Top level filepath: {}".format(self.toplevelfilepath))

    def _runlsseq(self):
        # lsseq is in tractor utils and should be in the path
        filepath=self.toplevelfilepath
        if os.path.isdir(filepath):
            _env=dict(os.environ, my_env_prop='value')
            _lsseqpath="lsseq"
            _env['PATH'] = '{}:{}'.format(_lsseqpath,_env["PATH"])
            p = subprocess.Popen(["lsq","-q","-R","-o","-l", filepath],
                                 stdout=subprocess.PIPE)
            q = subprocess.Popen(["lsseq","-R","-O","-p","-1","--format","nuke", filepath],
                                 stdout=subprocess.PIPE)
            a = q.communicate()[0]
            print a
            b = a.split()
            y=[]
            z=[]
            for i, x in enumerate(b,1):
                # print i
                if i % 2:
                    y.append(x)
                else:
                    z.append(x)

            for j, each in enumerate( zip(y,z) ):
                print j,each




if __name__ == "__main__":
    # testing here
    sh.setLevel(logging.DEBUG)
    # logger.debug("Testing icons={}".format(me.name))
    # logger.debug("Testing number={}".format(me.number))
    # logger.debug("Testing dabrenderwork={}".format(me.dabrenderwork))
    # logger.debug("test getfloat")
    # a='(20.1),'
    # getfloat(a)

    # N=RenderOutput("/Users/Shared/UTS_Jobs/TEACHING_renderman/testFarm/renderman")
    # N=RenderOutput("/Users/Shared/UTS_Jobs/TEACHING_renderman/project/renderman")
    # N._runlsseq()
    # print getnow()
    print string.punctuation
    mp='''!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~'''
    print type(string.punctuation)
    print mp




