#!/usr/bin/env rmanpy
'''
Shotgun API examples

'''

# TODO

import os
from pprint import pprint
import sys
import sww.renderfarm.dabtractor.factories.shotgun_factory as sgfac

import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
sh = logging.StreamHandler()
sh.setLevel(logging.INFO)
formatter = logging.Formatter('%(levelname)5.5s \t%(name)s \t%(message)s')
sh.setFormatter(formatter)
logger.addHandler(sh)

PROJID = 175 #hons 89
# SEQID=
# SHOTID=
# TASKID=
# ASSETID=

# person = sgfac.Person()
# projects = sgfac.Projects()
# shotgun = sgfac.ShotgunBase()

# projects.assets(PROJID)

sg = sgfac.ShotgunBase()

# pprint (  sg.sg.find( "Shot", [ ['project.Project.id', 'is', PROJID] ],
#                       ['code', 'sg_sequence.Sequence.sg_status_list']))
#     )
# print "------------ Full Schema -------------------"
# pprint(sg.sg.schema_read())

# sys.exit("stop")

# __project = ['project.Project.id', 'is', PROJID]
#
# pprint(sg.sg.schema_field_read('Project', field_name=None, project_entity=__project))

print "------------ Project -------------------"
__fields = ['id',
            'sg_asset_type',
            'episodes',
            'sequences',
            'shots',
            'archived',
            'name'
            ]
# __filters = [['id', 'is', PROJID], ['archived', 'is_not', False]]
__filters = [['archived', 'is', False]]

# pprint (  sg.sg.find( "Project", filters = [], fields = __fields))

__projects = sg.sg.find( "Project", filters = __filters, fields = __fields)
pprint(__projects)


PROJID=175
print "------------ Episode -------------------"
__fields = ['code',
            'id',
            'sequences',
            'assets',
            # 'shots',
            # 'tasks',
            ]
__filters = [
                ['project.Project.id', 'is', PROJID]
            ]

__episode = sg.sg.find( "Episode", filters = __filters, fields = __fields)
pprint(__episode)


EPID = 2
print "------------ Asset -------------------"
__fields = ['code', 'id',
            'sg_asset_type',
            'episodes',
            'sequences',
            'shots',
            'name'
            ]
__filters = [['project.Project.id', 'is', PROJID],
             ['episodes.Episode.id', 'is', EPID],
             ]

_asset = sg.sg.find( "Asset", filters = __filters, fields = __fields)
pprint (_asset)


ASSETID=1241
print "------------ Asset Tasks -------------------"
__fields = ['id',
            'cached_display_name',
            'assets',
            'tasks',
            'entity',
            'step'
            ]
__filters = [
                ['project.Project.id', 'is', PROJID],
                ['entity.Asset.id', 'is', ASSETID],
            ]

__assettask = sg.sg.find( "Task", filters=__filters, fields=__fields)
pprint(__assettask)


SEQID = 310
print "------------ Sequence -------------------"
__fields = ['code', 'id',
            'shots',
            'assets'
            ]
__filters = [
              ['project.Project.id', 'is', PROJID],
              ['id', 'is', SEQID],
            ]

__sequence = sg.sg.find( "Sequence", filters=__filters, fields=__fields)
                      # ['code', 'sg_sequence.Sequence.sg_status_list']
pprint (__sequence)


SHOTID = 3361
print "------------ Shots -------------------"
__fields = ['code', 'id',
            'cached_display_name',
            'assets',
            'tasks'
            ]
__filters = [
               ['project.Project.id', 'is', PROJID] ,
               ['id', 'is', SHOTID],
            ]

__shot = sg.sg.find( "Shot", filters = __filters, fields = __fields)

pprint(__shot)


TASKID = 9556
print "------------ Shot Tasks -------------------"
__fields = ['id',
            'cached_display_name',
            'assets',
            'tasks',
            'entity',
            'sg_status_list',
            'step'
            ]
__filters =  [
                ['project.Project.id', 'is', PROJID],
                ['id', 'is', TASKID],
             ]

__shottask = sg.sg.find( "Task", filters = __filters, fields = __fields)

pprint(__shottask)


'''
print "------------ CutItem -------------------"
__fields = ['id',
            'cached_display_name',
            # 'assets',
            'shot',
            # 'entity',
            # 'step',
            'list_order',
            'cut',
            'cut_order',

            ]
__filters =  [['project.Project.id', 'is', PROJID] ]

pprint (  sg.sg.find( "CutItem", filters = __filters, fields = __fields)
                      # ['code', 'sg_sequence.Sequence.sg_status_list']
        )

print "------------ Department -------------------"
__fields = ['id',
            'code',
            # 'assets',
            'shot',
            # 'department_type',
             'cached_display_name',
            'list_order',
            ]
__filters =  []
    # [['project.Project.id', 'is', PROJID] ]

pprint (  sg.sg.find( "Department", filters = __filters, fields = __fields)
                      # ['code', 'sg_sequence.Sequence.sg_status_list']
        )

'''
