'''
This is a tool for layout artists breaking out a scene from a maya file that has used the camera sequencer to create an animatic
It will render each camera using rfm, and optionally create individual maya files for each camera.

mgidney

'''


import os

try:
    import maya.cmds as cmds
    import pymel.core as pmc
except ImportWarning, err:
    print (err)


def sequencer_exists(nodename='sequencer1'):
    # test for a camera sequencer node
    try:
        pmc.PyNode(nodename)
        print "%s Exists"%nodename
    except pmc.MayaObjectError, err:
        print "%s Doesn't Exist %s"%(nodename,err)

    try:
        sequencer=pmc.nt.Sequencer(nodename)
        print "%s is a Sequencer node"%sequencer.nodeName()
    except TypeError, err:
        print "%s is not a Sequencer node, %s"%(nodename, err)
        raise TypeError, 'Cant find a sequencer node named %s'%nodename
    else:
        return sequencer

def run():
    seq=sequencer_exists()
    print seq.nodeName()
    print dir(seq)
    print seq.sources()
    # loop thru the shots and submit farm jobs

if __name__ == "__main__":
    print "RUNNING camera sequencer exporter ...."
    run()



