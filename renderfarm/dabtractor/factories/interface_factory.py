import os
import sys

import PySide.QtCore as qc
import PySide.QtGui as qg

# print os.path.abspath(qc.__file__)
# print os.path.abspath(qg.__file__)

import adhoc_jobs_factory as adhoc
import user_factory as ufac
import environment_factory as envfac
from sww.renderfarm.dabtractor.utils.sendmail import Mail

# ##############################################################
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
sh = logging.StreamHandler()
sh.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(levelname)5.5s \t%(filename)s as %(name)s \t%(message)s')
sh.setFormatter(formatter)
logger.addHandler(sh)
# ##############################################################


# -------------------------------------------------------------------------------------------------------------------- #
CFG = ufac.FarmUser()
WIDTH = 400
WIDTH_SMALL = WIDTH*0.3
WIDTH_HALF = WIDTH*0.5
WIDTH_MID = WIDTH*0.7
MIN_WIDTH = WIDTH*0.4
MIN_HEIGHT=25
STYLE_PRESSED = "background-color:lightgreen;color:darkblue"
STYLE_BG1     = "background-color:rgb(190, 255, 190);color:rgb(30, 0, 0)"
STYLE_BG2     = "background-color:rgb(210, 255, 210);color:rgb(0, 30, 0)"
STYLE_BG3     = "border:1px solid rgba(0,0,0,190);background-color:rgb(100, 255, 100);color:rgb(0, 30, 0)"
SPACING0=0
SPACING1=0
SPACING2=2
SPACING3=6


class UserWidget(qg.QWidget):
    def __init__(self,job):
        super(UserWidget, self).__init__()
        self.job = job
        self.username=CFG.name
        self.job.username = self.username
        self.usernumber=CFG.number
        self.job.usernumber=self.usernumber

        self.setLayout(qg.QVBoxLayout())
        self.layout().setSpacing(SPACING1)
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.setSizePolicy(qg.QSizePolicy.Minimum, qg.QSizePolicy.Fixed)

        self.layout().addWidget(Splitter("USER DETAILS"))
        self.usernumber_text_layout = qg.QHBoxLayout()
        self.usernumber_text_layout.setSpacing(SPACING3)
        self.usernumber_text_layout.setContentsMargins(0, 0, 0, 0)
        self.usernumber_text_layout.addSpacerItem(qg.QSpacerItem(5,0, qg.QSizePolicy.Fixed))

        self.usernumber_text_lb = qg.QLabel('$USER:      {}'.format(self.usernumber))
        self.usernumber_text_layout.addWidget(self.usernumber_text_lb)
        self.layout().addLayout(self.usernumber_text_layout)

        self.username_text_layout = qg.QHBoxLayout()
        self.username_text_layout.setSpacing(SPACING2)
        self.username_text_layout.setContentsMargins(0, 0, 0, 0)
        self.username_text_layout.addSpacerItem(qg.QSpacerItem(5,0, qg.QSizePolicy.Fixed))
        self.username_text_lb = qg.QLabel('$USERNAME:  {}'.format(self.username))
        self.username_text_layout.addWidget(self.username_text_lb)

        self.layout().addLayout(self.username_text_layout)
        self.layout().addSpacerItem(qg.QSpacerItem(0, 5, qg.QSizePolicy.Expanding))


-------------------------------------------------------------------------------------------------------------------- #
class ShowWidget(qg.QWidget):
    def __init__(self, job):
        super(ShowWidget, self).__init__()
        self.job = job
        self.setLayout(qg.QVBoxLayout())
        self.layout().setSpacing(SPACING0)
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.setSizePolicy(qg.QSizePolicy.Minimum, qg.QSizePolicy.Fixed)

        # $DABWORK ------------------------------------------------------------------------------------ #
        self.dabwork_text_lb = qg.QLabel('$DABWORK:')
        self.dabwork_text_lb.setMinimumWidth(WIDTH_SMALL)
        self.dabwork_text_le = qg.QLineEdit(self.job.dabwork)
        self.dabwork_text_le.setReadOnly(True)
        self.dabwork_text_layout = qg.QHBoxLayout()
        self.dabwork_text_layout.setSpacing(SPACING1)
        self.dabwork_text_layout.setContentsMargins(0, 0, 0, 0)
        self.dabwork_text_layout.addWidget(self.dabwork_text_lb)
        self.dabwork_text_layout.addWidget(self.dabwork_text_le)
        self.layout().addLayout(self.dabwork_text_layout)

        self.dabwork_text_le.setMinimumHeight(MIN_HEIGHT)
        self.dabwork_text_le.setStyleSheet(STYLE_BG3)
        self.job.dabworkpath=self.job.dabwork

        #  $TYPE  ---------------------------------------
        self.type_text_lb = qg.QLabel('$TYPE:')
        self.type_text_lb.setMinimumWidth(WIDTH_SMALL)
        self.type_combo = qg.QComboBox()
        self.type_combo.setMinimumWidth(WIDTH_MID)
        self.type_combo.setEditable(False)
        self.type_combo.addItem('user_work')
        self.type_combo.addItem('project_work')
        self.type_combo.setCurrentIndex(0)
        self.type_layout = qg.QHBoxLayout()
        self.type_layout.setSpacing(SPACING1)
        self.type_layout.setContentsMargins(0, 0, 0, 0)
        self.type_combo.activated.connect(lambda: self._type_change())
        self.type_layout.addWidget(self.type_text_lb)
        self.type_layout.addWidget(self.type_combo)

        self.type_combo.setMinimumHeight(MIN_HEIGHT)
        self.type_combo.setStyleSheet(STYLE_BG1)

        self.type_layout.addSpacerItem(qg.QSpacerItem(0, 5, qg.QSizePolicy.Expanding))
        self.layout().addLayout(self.type_layout)

        #  $SHOW  ---------------------------------------
        self.show_text_lb = qg.QLabel('$SHOW:')
        self.show_text_lb.setMinimumWidth(WIDTH_SMALL)
        self.show_combo = qg.QComboBox()
        self.show_combo.setMinimumWidth(WIDTH_MID)
        self.show_combo.setEditable(False)
        self.show_combo.addItem(self.job.username)
        self.show_combo.setCurrentIndex(0)
        self.show_layout = qg.QHBoxLayout()
        self.show_layout.setSpacing(SPACING1)
        self.show_layout.setContentsMargins(0, 0, 0, 0)
        self.show_combo.activated.connect(lambda: self._show_change())
        self.show_layout.addWidget(self.show_text_lb)
        self.show_layout.addWidget(self.show_combo)
        self.show_combo.setMinimumHeight(MIN_HEIGHT)
        self.show_combo.setStyleSheet(STYLE_BG1)
        self.show_layout.addSpacerItem(qg.QSpacerItem(0, 5, qg.QSizePolicy.Expanding))
        self.layout().addLayout(self.show_layout)

        # set initial values
        self._type_change()
        self._show_change()
        # self._project_change()

    def _type_change(self):
        _type = self.type_combo.currentText()
        self.job.typepath=os.path.join(self.job.dabwork, _type)
        self.job.type=_type

        if _type=="user_work":
            self._combo_from_path(self.show_combo, self.job.username)
            self.job.showpath = os.path.join(self.job.typepath, self.job.username)
            # self._combo_from_path(self.project_combo, self.job.showpath)
        elif _type=="project_work":
            self._combo_from_path(self.show_combo, self.job.typepath)
            # self._combo_from_path(self.project_combo, "")

        logger.info("Type changed to {}".format(_type))
        self._show_change()

    def _show_change(self):
        _show=self.show_combo.currentText()
        self.job.showpath = os.path.join(self.job.dabwork, self.job.type, _show)
        self.job.show = _show
        logger.info("Show changed to {}".format(_show))


    def _combo_from_path(self, _combobox, _dirpath):
        # rebuild a combobox list from the contents of a path
        # given a path build a list of files and directories
        _files=[]
        _dirs=[]
        try:
            _combobox.clear()
        except Exception,err:
            logger.critical("cant clear combobox: {}".format(err))
            sys.exit("cant clear combobox: {}".format(err))

        if os.path.isdir(_dirpath):
            _items = os.listdir(_dirpath)
            for i, _item in enumerate(_items):
                if os.path.isfile(os.path.join(_dirpath, _item)):
                    _files.append(_item)
                elif os.path.isdir(os.path.join(_dirpath, _item)):
                    _dirs.append(_item)
        else:
            _dirs = [_dirpath]

        for i, _item in enumerate(_dirs):
            _combobox.addItem(_item)

    def _get_show(self):
        pass

# -------------------------------------------------------------------------------------------------------------------- #
class SceneWidget(qg.QWidget):
    def __init__(self,job):
        super(SceneWidget, self).__init__()
        self.job=job
        self.setLayout(qg.QVBoxLayout())
        self.setSizePolicy(qg.QSizePolicy.Minimum, qg.QSizePolicy.Fixed)
        self.layout().setSpacing(SPACING0)
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.scene_file_lb = qg.QPushButton("Then Select Scene File")
        self.scene_file_lb.setMinimumWidth(MIN_WIDTH)
        # self.scene_file_le.setReadOnly(True)
        self.scene_file_layout = qg.QHBoxLayout()
        self.scene_file_layout.setSpacing(SPACING1)
        self.scene_file_layout.setContentsMargins(0, 0, 0, 0)
        self.scene_file_layout.addWidget(self.scene_file_lb)
        self.scene_file_lb.setStyleSheet(STYLE_PRESSED)

        self.layout().addLayout(self.scene_file_layout)
        self.scene_file_lb.clicked.connect(lambda : self._get_scene())

    def _get_scene(self):
        try:
            f = File(startplace = self.job.projfullpath)
        except Exception, err:
            logger.warn("Project full path not found %s"%err)
        else:
            self.job.scenefullpath = f.fullpath
            self.job.scenerelpath = f.relpath
            self.job.scene = f.relpath
            self.scene_file_lb.setText("SCENE: %s"%f.relpath)
        try:
            self.job.setfromscenefile(self.job.scenefullpath)
            self.job.putback()
            logger.info("Scene changed to {}".format(self.job.scene))
        except Exception,err:
            logger.warn("Environment vars not put back %s"%err)
            self.scene_file_lb.setText("Then Select Scene File")

# -------------------------------------------------------------------------------------------------------------------- #
class ProjWidget(qg.QWidget):
    def __init__(self,job):
        super(ProjWidget, self).__init__()
        self.job=job
        self.setLayout(qg.QVBoxLayout())
        self.setSizePolicy(qg.QSizePolicy.Minimum, qg.QSizePolicy.Fixed)
        self.layout().setSpacing(SPACING1)
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.proj_file_lb = qg.QPushButton("Select Project Root First")
        self.proj_file_lb.setMinimumWidth(MIN_WIDTH)
        # self.scene_file_le.setReadOnly(True)
        self.proj_file_layout = qg.QHBoxLayout()
        self.proj_file_layout.setSpacing(SPACING1)
        self.proj_file_layout.setContentsMargins(0, 0, 0, 0)
        # self.proj_file_layout.addWidget(self.proj_text_lb)
        self.proj_file_layout.addWidget(self.proj_file_lb)

        _pressed = "background-color:lightgreen;color:darkblue"
        self.proj_file_lb.setStyleSheet(_pressed)

        self.layout().addLayout(self.proj_file_layout)
        self.proj_file_lb.clicked.connect(lambda : self._get_proj())

    def _get_proj(self):
        f = Directory(startplace = self.job.showpath)
        self.job.projfullpath = f.fullpath
        self.job.projrelpath = f.relpath
        self.job.proj = f.relpath
        self.proj_file_lb.setText("PROJECT: %s" % f.relpath)
        try:
            self.job.setfromprojroot(self.job.projfullpath)
            self.job.putback()
            logger.info("Proj changed to {}".format(self.job.proj))
        except Exception,err:
            logger.info("Environment vars not put back %s",err)
            self.proj_file_lb.setText("Select Project Root First")



# -------------------------------------------------------------------------------------------------------------------- #
class SubmitWidget(qg.QWidget):
    def __init__(self, job, feedback):
        super(SubmitWidget, self).__init__()
        self.job = job
        self.fb=feedback
        self.setLayout(qg.QVBoxLayout())
        self.setSizePolicy(qg.QSizePolicy.Minimum, qg.QSizePolicy.Fixed)
        self.submit_layout_1_bttn = qg.QPushButton('Sanity Check')
        self.submit_layout_2_bttn = qg.QPushButton('Validate')
        self.submit_layout_3_bttn = qg.QPushButton('SUBMIT')
        self.button_group=qg.QWidget()
        self.button_group.setLayout(qg.QHBoxLayout())
        self.button_group.layout().setSpacing(SPACING1)
        self.button_group.layout().setContentsMargins(0, 0, 0, 0)
        self.button_group.layout().addWidget(self.submit_layout_1_bttn)
        self.button_group.layout().addWidget(self.submit_layout_2_bttn)
        self.button_group.layout().addWidget(self.submit_layout_3_bttn)
        self.layout().setSpacing(SPACING1)
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().addWidget(Splitter("SUBMIT JOB"))
        self.layout().addWidget(self.button_group)

        self.submit_layout_1_bttn.clicked.connect(self.sanity)
        self.submit_layout_2_bttn.clicked.connect(self.validate)
        self.submit_layout_3_bttn.clicked.connect(self.submit)

    def sanity(self):
        logger.info("Sanity Checker Pressed")
        self.fb.write("---Sanity Check Start---")
        self.fb.write("Not implemented yet")
        self.fb.write("---Sanity Check Ended---")

    def validate(self):
        logger.info("Validate Job Pressed")
        self.fb.write("Validate Job")
        self.job.printme()
        if self.job.mode=="rms":
            self.job.rmsvalidate()
        elif self.job.mode=="maya":
            self.job.mayavalidate()
        elif self.job.mode=="nuke":
            self.job.nukevalidate()
        elif self.job.mode=="bash":
            self.job.commandvalidate()
        # elif self.job.mode=="diag":
        #     self.job.commandvalidate()
        # elif self.job.mode=="bug":
        #     self.job.commandvalidate()


    def submit(self):
        self.fb.write("Submit Job")
        logger.info("Submit Job Pressed")
        self.job.spool()


# -------------------------------------------------------------------------------------------------------------------- #
class OutputWidget(qg.QWidget):
    def __init__(self,job):
        super(OutputWidget, self).__init__()
        self.job=job
        self.setLayout(qg.QVBoxLayout())
        self.layout().setSpacing(SPACING1)
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.setSizePolicy(qg.QSizePolicy.Minimum, qg.QSizePolicy.Fixed)

        self.resolution_text_lb = qg.QLabel('RESOLUTION:')
        self.resolution_combo = qg.QComboBox()
        self.resolution_combo.addItems(CFG.env.getoptions("render","resolution"))
        self.resolution_combo.setMinimumWidth(WIDTH_HALF)
        self.resolution_layout = qg.QHBoxLayout()
        self.resolution_combo.setCurrentIndex(0)
        self.resolution_layout.setContentsMargins(0, 0, 0, 0)
        self.resolution_layout.setSpacing(SPACING1)
        self.resolution_layout.addWidget(self.resolution_text_lb)
        self.resolution_layout.addSpacerItem(qg.QSpacerItem(0, 5, qg.QSizePolicy.Expanding))
        self.resolution_layout.addWidget(self.resolution_combo)
        self.layout().addLayout(self.resolution_layout)

        self.outformat_text_lb = qg.QLabel('OUTPUT:')
        self.outformat_combo = qg.QComboBox()
        self.outformat_combo.addItems(CFG.env.getoptions("render","outformat"))
        self.outformat_combo.setMinimumWidth(WIDTH_HALF)
        self.outformat_layout = qg.QHBoxLayout()
        self.outformat_layout.setContentsMargins(0, 0, 0, 0)
        self.outformat_layout.setSpacing(SPACING1)
        self.outformat_layout.addWidget(self.outformat_text_lb)
        self.outformat_layout.addSpacerItem(qg.QSpacerItem(0, 5, qg.QSizePolicy.Expanding))
        self.outformat_layout.addWidget(self.outformat_combo)
        self.layout().addLayout(self.outformat_layout)

        # set initial
        self._resolution(self.resolution_combo.currentText())
        self._outformat(self.outformat_combo.currentText())
        # connections
        self.outformat_combo.activated.connect(lambda: self._outformat(self.outformat_combo.currentText()))
        self.resolution_combo.activated.connect(lambda: self._resolution(self.resolution_combo.currentText()))

    def _outformat(self, _value):
        self.job.outformat=_value
        logger.info("Out Format group changed to {}".format(self.job.outformat))

    def _resolution(self, _value):
        self.job.resolution=_value
        logger.info("Resolution group changed to {}".format(self.job.resolution))

# -------------------------------------------------------------------------------------------------------------------- #
class RangeWidget(qg.QWidget):
    def __init__(self,job):
        super(RangeWidget, self).__init__()
        self.job=job
        self.setLayout(qg.QVBoxLayout())
        self.layout().setSpacing(SPACING1)
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.setSizePolicy(qg.QSizePolicy.Minimum, qg.QSizePolicy.Fixed)

        self.framerange_layout = qg.QGridLayout()
        self.framerange_layout.setContentsMargins(0, 0, 0, 0)
        self.framerange_layout.setSpacing(SPACING1)

        self.framerange_start_text_lb = qg.QLabel('START:')
        self.framerange_start_text_lb.setMinimumWidth(20)
        self.framerange_start_text_le = qg.QLineEdit("1")
        self.framerange_start_text_le.setMaximumWidth(50)

        self.framerange_end_text_lb = qg.QLabel('END:')
        self.framerange_end_text_lb.setMinimumWidth(15)
        self.framerange_end_text_le = qg.QLineEdit("24")
        self.framerange_end_text_le.setMaximumWidth(50)

        self.framerange_by_text_lb = qg.QLabel('BY:')
        self.framerange_by_text_lb.setMinimumWidth(15)
        self.framerange_by_text_le = qg.QLineEdit("1")
        self.framerange_by_text_le.setMaximumWidth(50)

        self.framerange_layout.addItem(qg.QSpacerItem(0, 5, qg.QSizePolicy.Expanding), 0, 0)
        self.framerange_layout.addWidget(self.framerange_start_text_lb, 0, 1)
        self.framerange_layout.addWidget(self.framerange_start_text_le, 0, 2)

        self.framerange_layout.addItem(qg.QSpacerItem(0, 5, qg.QSizePolicy.Expanding),0,3)
        self.framerange_layout.addWidget(self.framerange_end_text_lb, 0, 4)
        self.framerange_layout.addWidget(self.framerange_end_text_le, 0, 5)

        self.framerange_layout.addItem(qg.QSpacerItem(0, 5, qg.QSizePolicy.Expanding),0,6)
        self.framerange_layout.addWidget(self.framerange_by_text_lb,0,7)
        self.framerange_layout.addWidget(self.framerange_by_text_le,0,8)
        self.framerange_layout.addItem(qg.QSpacerItem(0, 5, qg.QSizePolicy.Expanding),0,9)

        self.chunks_text_lb = qg.QLabel('JOB CHUNKS:')
        self.chunks_combo = qg.QComboBox()

        self.chunks_combo.addItems(CFG.env.getoptions("render","chunks"))
        self.chunks_combo.setMinimumWidth(WIDTH_HALF)
        self.chunks_layout = qg.QHBoxLayout()
        self.chunks_layout.setContentsMargins(0, 0, 0, 0)
        self.chunks_layout.setSpacing(SPACING1)
        self.chunks_layout.addWidget(self.chunks_text_lb)
        self.chunks_layout.addSpacerItem(qg.QSpacerItem(0, 5, qg.QSizePolicy.Expanding))
        self.chunks_layout.addWidget(self.chunks_combo)
        self.chunks_combo.setCurrentIndex(0)

        # set initial values
        self._start()
        self._end()
        self._by()
        self._chunks()

        self.framerange_start_text_le.textEdited.connect(lambda: self._start())
        self.framerange_end_text_le.textEdited.connect(lambda: self._end())
        self.framerange_by_text_le.textEdited.connect(lambda: self._by())
        self.chunks_combo.activated.connect(lambda: self._chunks())

        self.layout().addSpacerItem(qg.QSpacerItem(0,10, qg.QSizePolicy.Expanding))
        self.layout().addLayout(self.framerange_layout)
        self.layout().addLayout(self.chunks_layout)
        self.layout().addSpacerItem(qg.QSpacerItem(0,10, qg.QSizePolicy.Expanding))

    def _start(self):
        self.job.startframe = self.framerange_start_text_le.text()
        logger.info("Start changed to {}".format(self.job.startframe))

    def _end(self):
        self.job.endframe = self.framerange_end_text_le.text()
        logger.info("End changed to {}".format(self.job.endframe))

    def _by(self):
        self.job.byframe = self.framerange_by_text_le.text()
        logger.info("By changed to {}".format(self.job.byframe))

    def _chunks(self):
        self.job.chunks = self.chunks_combo.currentText()
        logger.info("Chunks changed to {}".format(self.job.chunks))

# -------------------------------------------------------------------------------------------------------------------- #
class MayaJobWidget(qg.QWidget):
    def __init__(self, job):
        super(MayaJobWidget, self).__init__()
        self.job=job
        self.setLayout(qg.QVBoxLayout())
        self.layout().setSpacing(SPACING1)
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().setAlignment(qc.Qt.AlignTop)
        self.setSizePolicy(qg.QSizePolicy.Minimum, qg.QSizePolicy.Fixed)

        # BUILD MAYA WIDGET BITS
        self.layout().addWidget(Splitter("MAYA RENDER OPTIONS"))

        self.mayaversion_text_lb = qg.QLabel('MAYA VERSION:')
        self.mayaversion_combo = qg.QComboBox()
        self.mayaversion_combo.addItems(CFG.env.getoptions("maya","versions"))
        self.mayaversion_combo.setMinimumWidth(WIDTH_HALF)
        self.mayaversion_layout = qg.QHBoxLayout()
        self.mayaversion_layout.setContentsMargins(0, 0, 0, 0)
        self.mayaversion_layout.setSpacing(SPACING1)
        self.mayaversion_layout.addWidget(self.mayaversion_text_lb)
        self.mayaversion_layout.addSpacerItem(qg.QSpacerItem(0, 5, qg.QSizePolicy.Expanding))
        self.mayaversion_layout.addWidget(self.mayaversion_combo)
        self.layout().addLayout(self.mayaversion_layout)

        self.renderer_text_lb = qg.QLabel('RENDERER:')
        self.renderer_combo = qg.QComboBox()
        self.renderer_combo.addItems(CFG.env.getoptions("maya","mayarenderer"))
        self.renderer_combo.setMinimumWidth(WIDTH_HALF)
        self.renderer_layout = qg.QHBoxLayout()
        self.renderer_layout.setContentsMargins(0, 0, 0, 0)
        self.renderer_layout.setSpacing(SPACING1)
        self.renderer_layout.addWidget(self.renderer_text_lb)
        self.renderer_layout.addSpacerItem(qg.QSpacerItem(0, 5, qg.QSizePolicy.Expanding))
        self.renderer_layout.addWidget(self.renderer_combo)
        self.layout().addLayout(self.renderer_layout)

        self.options_text_lb = qg.QLabel('OPTIONS:')
        self.options_combo = qg.QComboBox()
        self.options_combo.addItem("")
        self.options_combo.setEditable(True)
        self.options_combo.setMinimumWidth(WIDTH_SMALL)
        self.options_layout = qg.QHBoxLayout()
        self.options_layout.setContentsMargins(0, 0, 0, 0)
        self.options_layout.setSpacing(SPACING0)
        self.options_layout.addWidget(self.options_text_lb)
        self.options_layout.addSpacerItem(qg.QSpacerItem(0, 5, qg.QSizePolicy.Expanding))
        self.options_layout.addWidget(self.options_combo)
        self.layout().addLayout(self.options_layout)

        # set initial values
        self._renderer(self.renderer_combo.currentText())
        self._mayaversion(self.mayaversion_combo.currentText())
        self._options(self.options_combo.currentText())

        # connect vlaues to widget
        self.renderer_combo.activated.connect(lambda: self._renderer(self.renderer_combo.currentText()))
        self.mayaversion_combo.activated.connect(lambda: self._mayaversion(self.mayaversion_combo.currentText()))
        self.options_combo.editTextChanged.connect(lambda: self._options(self.options_combo.currentText()))

    def _renderer(self, _value):
        self.job.renderer = _value
        logger.info("Maya Renderer changed to {}".format(self.job.renderer))
    def _mayaversion(self, _value):
        self.job.mayaversion = _value
        logger.info("Maya Version changed to {}".format(self.job.mayaversion))
    def _options(self, _value):
        self.job.options = _value
        logger.info("Options changed to {}".format(self.job.options))


# -------------------------------------------------------------------------------------------------------------------- #
class ThreadMemoryWidget(qg.QWidget):
    def __init__(self,job):
        super(ThreadMemoryWidget, self).__init__()
        self.job = job
        self.setLayout(qg.QVBoxLayout())
        self.setSizePolicy(qg.QSizePolicy.Minimum, qg.QSizePolicy.Fixed)
        self.layout().setSpacing(SPACING0)
        self.layout().setContentsMargins(0, 0, 0, 0)

        self.threads_layout = qg.QHBoxLayout()
        self.threads_layout.setContentsMargins(0, 0, 0, 0)
        self.threads_layout.setSpacing(SPACING0)
        self.threads_text_lb = qg.QLabel('THREADS:')
        self.threads_combo = qg.QComboBox()
        self.threads_combo.setMinimumWidth(WIDTH_HALF)
        self.threads_combo.addItems(CFG.env.getoptions("render","threads"))

        self.threads_combo.setCurrentIndex(0)
        self.threads_layout.addWidget(self.threads_text_lb)
        self.threads_layout.addSpacerItem(qg.QSpacerItem(0, 5, qg.QSizePolicy.Expanding))
        self.threads_layout.addWidget(self.threads_combo)
        self._threads(self.threads_combo.currentText())
        self.threads_combo.activated.connect(lambda: self._threads(self.threads_combo.currentText()))
        self.layout().addLayout(self.threads_layout)

        self.threadmemory_layout = qg.QHBoxLayout()
        self.threadmemory_layout.setContentsMargins(0, 0, 0, 0)
        self.threadmemory_layout.setSpacing(0)
        self.threadmemory_text_lb = qg.QLabel('THREAD MEMORY MB:')
        self.threadmemory_combo = qg.QComboBox()
        self.threadmemory_combo.setMinimumWidth(WIDTH_HALF)
        self.threadmemory_combo.addItems(CFG.env.getoptions("render","rendermemory"))
        self.threadmemory_combo.setCurrentIndex(0)
        self.threadmemory_layout.addWidget(self.threadmemory_text_lb)
        self.threadmemory_layout.addSpacerItem(qg.QSpacerItem(0, 5, qg.QSizePolicy.Expanding))
        self.threadmemory_layout.addWidget(self.threadmemory_combo)
        self._memory(self.threadmemory_combo.currentText())
        self.threadmemory_combo.activated.connect(lambda: self._memory(self.threadmemory_combo.currentText()))
        self.layout().addLayout(self.threadmemory_layout)

        self.threadmemory_combo.setCurrentIndex(0)
        self.threads_combo.setCurrentIndex(0)

    def _threads(self, _value):
        self.job.threads = _value
        logger.info("Threads changed to {}".format(self.job.threads))

    def _memory(self, _value):
        self.job.threadmemory=_value
        logger.info("Thread Memory changed to {} mb".format(self.job.threadmemory))


class CommonRenderOptionsWidget(qg.QWidget):
    def __init__(self,job):
        super(CommonRenderOptionsWidget, self).__init__()
        self.job=job
        self.setLayout(qg.QVBoxLayout())
        self.layout().setSpacing(0)
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().setAlignment(qc.Qt.AlignTop)
        self.setSizePolicy(qg.QSizePolicy.Minimum, qg.QSizePolicy.Fixed)

        # SHOW WIDGET
        self.show_widget = ShowWidget(self.job)
        self.layout().addWidget(self.show_widget)
        # COMMON RENDER OPTIONS
        self.layout().addWidget(Splitter("COMMON RENDER OPTIONS"))
        # PROJ WIDGET
        self.proj_widget = ProjWidget(self.job)
        self.layout().addWidget(self.proj_widget)
        # SCENE WIDGET
        self.scene_widget = SceneWidget(self.job)
        self.layout().addWidget(self.scene_widget)
        # OUTPUT WIDGET
        self.outformat_widget = OutputWidget(self.job)
        self.layout().addWidget(self.outformat_widget)
        # RANGE WIDGET
        self.range_widget = RangeWidget(self.job)
        self.layout().addWidget(self.range_widget)
        # THREADS AND MEMORY WIDGET
        self.threadmem_widget = ThreadMemoryWidget(self.job)
        self.layout().addWidget(self.threadmem_widget)

# -------------------------------------------------------------------------------------------------------------------- #
class FeedbackWidget(qg.QTextEdit):
    def __init__(self):
        super(FeedbackWidget, self).__init__()
        self.setMinimumHeight(100)
        self.setMaximumHeight(130)
        self.setWordWrapMode(qg.QTextOption.WordWrap)
        self.setReadOnly(True)

    def clear(self):
        self.clear()

    def write(self, _text):
        self.append(_text)


# -------------------------------------------------------------------------------------------------------------------- #
class RendermanJobWidget(qg.QWidget):
    def __init__(self,job):
        super(RendermanJobWidget, self).__init__()
        self.job=job
        self.setLayout(qg.QVBoxLayout())
        self.layout().setSpacing(0)
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().setAlignment(qc.Qt.AlignTop)
        self.setSizePolicy(qg.QSizePolicy.Minimum, qg.QSizePolicy.Fixed)

        # BUILD RENDERMAN OPTIONS
        self.renderman_widget = RendermanWidget(self.job)
        self.layout().addWidget(self.renderman_widget)


# -------------------------------------------------------------------------------------------------------------------- #
class RendermanWidget(qg.QWidget):
    def __init__(self, job):
        super(RendermanWidget, self).__init__()
        self.job=job
        self.setLayout(qg.QVBoxLayout())
        self.layout().setSpacing(0)
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.setSizePolicy(qg.QSizePolicy.Minimum, qg.QSizePolicy.Fixed)

        self.layout().addWidget(Splitter("RENDERMAN OPTIONS"))

        self.mayaversion_text_lb = qg.QLabel('MAYA VERSION:')
        self.mayaversion_combo = qg.QComboBox()
        self.mayaversion_combo.addItems(CFG.env.getoptions("maya","versions"))
        self.mayaversion_combo.setMinimumWidth(WIDTH_HALF)
        self.mayaversion_layout = qg.QHBoxLayout()
        self.mayaversion_layout.setContentsMargins(0, 0, 0, 0)
        self.mayaversion_layout.setSpacing(0)
        self.mayaversion_layout.addWidget(self.mayaversion_text_lb)
        self.mayaversion_layout.addSpacerItem(qg.QSpacerItem(0, 5, qg.QSizePolicy.Expanding))
        self.mayaversion_layout.addWidget(self.mayaversion_combo)
        self.layout().addLayout(self.mayaversion_layout)

        self.rmanversion_text_lb = qg.QLabel('RMAN VERSION:')
        self.rmanversion_combo = qg.QComboBox()
        self.rmanversion_combo.addItems(CFG.env.getoptions("renderman","versions"))
        self.rmanversion_combo.setMinimumWidth(WIDTH_HALF)
        self.rmanversion_layout = qg.QHBoxLayout()
        self.rmanversion_layout.setContentsMargins(0, 0, 0, 0)
        self.rmanversion_layout.setSpacing(0)
        self.rmanversion_layout.addWidget(self.rmanversion_text_lb)
        self.rmanversion_layout.addSpacerItem(qg.QSpacerItem(0, 5, qg.QSizePolicy.Expanding))
        self.rmanversion_layout.addWidget(self.rmanversion_combo)
        self.layout().addLayout(self.rmanversion_layout)

        self.integrator_text_lb = qg.QLabel('INTEGRATOR:')
        self.integrator_combo = qg.QComboBox()
        self.integrator_combo.addItems(CFG.env.getoptions("renderman","integrators"))
        self.integrator_combo.setMinimumWidth(WIDTH_HALF)
        self.integrator_combo.setCurrentIndex(0)
        self.integrator_layout = qg.QHBoxLayout()
        self.integrator_layout.setContentsMargins(0, 0, 0, 0)
        self.integrator_layout.setSpacing(0)
        self.integrator_layout.addWidget(self.integrator_text_lb)
        self.integrator_layout.addSpacerItem(qg.QSpacerItem(0, 5, qg.QSizePolicy.Expanding))
        self.integrator_layout.addWidget(self.integrator_combo)
        self.layout().addLayout(self.integrator_layout)

        self.maxsamples_text_lb = qg.QLabel('MAX SAMPLES:')
        self.maxsamples_combo = qg.QComboBox()
        self.maxsamples_combo.addItems(CFG.env.getoptions("render","maxsamples"))
        self.maxsamples_combo.setMinimumWidth(WIDTH_HALF)

        self.maxsamples_combo.setCurrentIndex(0)

        self.maxsamples_layout = qg.QHBoxLayout()
        self.maxsamples_layout.setContentsMargins(0, 0, 0, 0)
        self.maxsamples_layout.setSpacing(0)
        self.maxsamples_layout.addWidget(self.maxsamples_text_lb)
        self.maxsamples_layout.addSpacerItem(qg.QSpacerItem(0, 5, qg.QSizePolicy.Expanding))
        self.maxsamples_layout.addWidget(self.maxsamples_combo)
        self.layout().addLayout(self.maxsamples_layout)

        self.options_text_lb = qg.QLabel('OPTIONS:')
        self.options_combo = qg.QComboBox()
        self.options_combo.addItem("-v")
        self.options_combo.addItem("-binary")
        self.options_combo.setEditable(True)
        self.options_combo.setMinimumWidth(WIDTH_HALF)
        self.options_layout = qg.QHBoxLayout()
        self.options_layout.setContentsMargins(0, 0, 0, 0)
        self.options_layout.setSpacing(0)
        self.options_layout.addWidget(self.options_text_lb)
        self.options_layout.addSpacerItem(qg.QSpacerItem(0, 5, qg.QSizePolicy.Expanding))
        self.options_layout.addWidget(self.options_combo)
        self.layout().addLayout(self.options_layout)

        # set initial values
        self._rms_maxsamples(self.maxsamples_combo.currentText())
        self._rms_integrator(self.integrator_combo.currentText())
        self._rman_version(self.rmanversion_combo.currentText())
        self._maya_version(self.mayaversion_combo.currentText())
        self._rms_options(self.options_combo.currentText())

        # connect values to widget
        self.maxsamples_combo.activated.connect(lambda: self._rms_maxsamples(self.maxsamples_combo.currentText()))
        self.integrator_combo.activated.connect(lambda: self._rms_integrator(self.integrator_combo.currentText()))
        self.mayaversion_combo.activated.connect(lambda: self._maya_version(self.mayaversion_combo.currentText()))
        self.rmanversion_combo.activated.connect(lambda: self._rman_version(self.rmanversion_combo.currentText()))
        self.options_combo.editTextChanged.connect(lambda: self._rms_options(self.options_combo.currentText()))

    def _rms_maxsamples(self, _value):
        self.job.rms_maxsamples=_value
        logger.info("rms_maxsamples changed to {}".format(self.job.rms_maxsamples))

    def _rman_version(self, _value):
        self.job.rmanversion=_value
        logger.info("RMS Version changed to {}".format(self.job.rmanversion))

    def _maya_version(self, _value):
        self.job.mayaversion=_value
        logger.info("RMS Version changed to {}".format(self.job.mayaversion))

    def _rms_integrator(self, _value):
        self.job.rms_integrator=_value
        logger.info("Integrator changed to {}".format(self.job.rms_integrator))

    def _rms_options(self, _value):
        self.job.rms_options=_value
        logger.info("Options  changed to {}".format(self.job.rms_options))

# -------------------------------------------------------------------------------------------------------------------- #
class BashJobWidget(qg.QWidget):
    def __init__(self,job):
        super(BashJobWidget, self).__init__()
        self.job=job
        self.setLayout(qg.QVBoxLayout())
        self.layout().setSpacing(0)
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().setAlignment(qc.Qt.AlignTop)
        self.setSizePolicy(qg.QSizePolicy.Minimum, qg.QSizePolicy.Fixed)

        # BASH WIDGET
        self.bash_widget = BashWidget(self.job)
        self.layout().addWidget(self.bash_widget)

# -------------------------------------------------------------------------------------------------------------------- #
class BashWidget(qg.QWidget):
    def __init__(self,job):
        super(BashWidget, self).__init__()
        _target = "120988@uts.edu.au"
        self.defaults={
            "custon":"",
            "project disk report":\
                 "du -sg ${DABWORK}/project_work/* | sort -rn | mail %s"%_target,
            "user disk report":\
                 "du -sg ${DABWORK}/user_work/* | sort -rn | mail %s"%_target,
            }

        self.job=job
        self.setLayout(qg.QVBoxLayout())
        self.layout().setSpacing(0)
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.setSizePolicy(qg.QSizePolicy.Minimum, qg.QSizePolicy.Fixed)
        self.layout().addWidget(Splitter("BASH COMMAND"))
        self.bashcommand_text_lb = qg.QLabel('COMMAND:')
        self.bashcommand_combo = qg.QComboBox()
        self.bashcommand_combo.setEditable(False)
        self.bashcommand_combo.setMinimumWidth(WIDTH_MID)
        self.bashcommand_layout = qg.QHBoxLayout()
        self.bashcommand_layout.setContentsMargins(0, 0, 0, 0)
        self.bashcommand_layout.setSpacing(0)
        self.bashcommand_layout.addWidget(self.bashcommand_text_lb)
        self.bashcommand_layout.addSpacerItem(qg.QSpacerItem(0, 5, qg.QSizePolicy.Expanding))
        self.bashcommand_layout.addWidget(self.bashcommand_combo)
        self.layout().addLayout(self.bashcommand_layout)
        self.commandtext= FeedbackWidget()
        self.commandtext.setReadOnly(False)
        self.layout().addWidget(self.commandtext)
        self.bashcommand_combo.addItems(list(self.defaults.keys()))
        self.bashcommand_combo.setCurrentIndex(0)

        # set initial values
        self._options(self.bashcommand_combo.currentText())
        self._commandedit(self.commandtext.toPlainText())

        # connect values to widget
        self.bashcommand_combo.activated.connect(lambda: self._options(self.bashcommand_combo.currentText()))
        self.commandtext.textChanged.connect(lambda: self._commandedit(self.commandtext.toPlainText()))


    def _options(self, _value):
        self.commandtext.setText(self.defaults.get(_value))
        logger.info("Default changed to {}".format(_value))

    def _commandedit(self, _value):
        self.job.bashcommand = _value
        logger.info("Command changed to {}".format(self.job.bashcommand))




# -------------------------------------------------------------------------------------------------------------------- #
class DiagnosticJobWidget(qg.QWidget):
    def __init__(self,job):
        super(DiagnosticJobWidget, self).__init__()
        self.job=job
        self.setLayout(qg.QVBoxLayout())
        self.layout().setSpacing(0)
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().setAlignment(qc.Qt.AlignTop)

        self.setSizePolicy(qg.QSizePolicy.Minimum, qg.QSizePolicy.Fixed)

        # DIAGNOSTIC WIDGET
        self.diagnostic_widget = DiagnosticsWidget(self.job)
        self.layout().addWidget(self.diagnostic_widget)

# -------------------------------------------------------------------------------------------------------------------- #
class BugWidget(qg.QWidget):
    def __init__(self,job):
        super(BugWidget, self).__init__()
        self.job=job
        self.setLayout(qg.QVBoxLayout())
        self.layout().setSpacing(0)
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().setAlignment(qc.Qt.AlignTop)
        self.setSizePolicy(qg.QSizePolicy.Minimum, qg.QSizePolicy.Fixed)

        # BUG WIDGET
        self.layout().addWidget(Splitter("SEND BUG DETAILS TO MATT"))
        self.setLayout(qg.QVBoxLayout())
        self.setSizePolicy(qg.QSizePolicy.Minimum, qg.QSizePolicy.Fixed)
        self.bug_widget = FeedbackWidget()
        self.bug_widget.setReadOnly(False)
        self.layout().addWidget(self.bug_widget)
        self.email_layout_bttn = qg.QPushButton('Email Matt')
        self.layout().addWidget(self.email_layout_bttn)
        self.layout().addSpacerItem(qg.QSpacerItem(0,50, qg.QSizePolicy.Expanding))

        self.email_layout_bttn.clicked.connect(self.mailjob)

    def email(self):
        logger.info("Sending to matt: {}".format( self.bug_widget.toPlainText()))
        m=Mail(mailto="120988@uts.edu.au",
               mailfrom="{}@student.uts.edu.au".format(self.job.usernumber),
               mailsubject="Bug Report from {}".format(self.job.username),
               mailbody=self.bug_widget.toPlainText())
        m.send()

    def mailjob(self):
        TEST = adhoc.SendMail(mailbody=self.bug_widget.toPlainText(),
                              mailsubject="mail subject",
                              mailcc="mail cc",
                              mailfrom="tractor",
                              mailto="120988@uts.edu.au")
        TEST.build()
        TEST.validate()
        TEST.spool()



# -------------------------------------------------------------------------------------------------------------------- #
class DiagnosticsWidget(qg.QWidget):
    def __init__(self,job):
        super(DiagnosticsWidget, self).__init__()
        self.job=job
        self.setLayout(qg.QVBoxLayout())
        self.layout().setSpacing(0)
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.setSizePolicy(qg.QSizePolicy.Minimum, qg.QSizePolicy.Fixed)

        self.layout().addWidget(Splitter("DIAGNOSTICS OPTIONS"))

        self.version_layout = qg.QHBoxLayout()
        self.version_layout.setContentsMargins(0, 0, 0, 0)
        self.version_layout.setSpacing(0)
        self.layout().addLayout(self.version_layout)

        self.version_layout.addSpacerItem(qg.QSpacerItem(0, 5, qg.QSizePolicy.Expanding))


# -------------------------------------------------------------------------------------------------------------------- #
class NukeJobWidget(qg.QWidget):
    def __init__(self,job):
        super(NukeJobWidget, self).__init__()
        self.job=job
        self.setLayout(qg.QVBoxLayout())
        self.layout().setSpacing(0)
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().setAlignment(qc.Qt.AlignTop)
        self.setSizePolicy(qg.QSizePolicy.Minimum, qg.QSizePolicy.Fixed)

        # NUKE WIDGET
        self.nuke_widget = NukeWidget(self.job)
        self.layout().addWidget(self.nuke_widget)

# -------------------------------------------------------------------------------------------------------------------- #
class NukeWidget(qg.QWidget):
    def __init__(self,job):
        super(NukeWidget, self).__init__()
        self.job=job
        self.setLayout(qg.QVBoxLayout())
        self.layout().setSpacing(0)
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.setSizePolicy(qg.QSizePolicy.Minimum, qg.QSizePolicy.Fixed)

        self.layout().addWidget(Splitter("NUKE OPTIONS"))

        self.version_layout = qg.QHBoxLayout()
        self.version_layout.setContentsMargins(0, 0, 0, 0)
        self.version_layout.setSpacing(0)
        self.layout().addLayout(self.version_layout)

        self.version_text_lb = qg.QLabel('NUKE VERSION:')
        self.version_combo = qg.QComboBox()
        self.version_combo.addItems(CFG.env.getoptions("nuke","versions"))
        self.version_combo.setMinimumWidth(WIDTH_HALF)
        self.version_layout = qg.QHBoxLayout()
        self.version_layout.setContentsMargins(0, 0, 0, 0)
        self.version_layout.setSpacing(0)
        self.version_layout.addWidget(self.version_text_lb)
        self.version_layout.addSpacerItem(qg.QSpacerItem(0, 5, qg.QSizePolicy.Expanding))
        self.version_layout.addWidget(self.version_combo)
        self.layout().addLayout(self.version_layout)

        self.options_text_lb = qg.QLabel('OPTIONS:')
        self.options_combo = qg.QComboBox()
        self.options_combo.setToolTip("Select from presets or edit yourself")
        self.options_combo.addItem("")
        self.options_combo.addItem("-V 2")
        self.options_combo.addItem("-V 2 -F 1-10 -F 20 -F 50-80x10")
        self.options_combo.setEditable(True)
        self.options_combo.setMinimumWidth(MIN_WIDTH)
        self.options_layout = qg.QHBoxLayout()
        self.options_layout.setContentsMargins(0, 0, 0, 0)
        self.options_layout.setSpacing(0)
        self.options_layout.addWidget(self.options_text_lb)
        self.options_layout.addSpacerItem(qg.QSpacerItem(0, 5, qg.QSizePolicy.Expanding))
        self.options_layout.addWidget(self.options_combo)
        self.layout().addLayout(self.options_layout)

        # set initial values
        self._nuke_version(self.version_combo.currentText())
        self._options(self.options_combo.currentText())

        # connect vlaues to widget
        self.version_combo.activated.connect(lambda: self._nuke_version(self.version_combo.currentText()))
        self.options_combo.editTextChanged.connect(lambda: self._options(self.options_combo.currentText()))

    def _options(self, _value):
        self.job.nukeoptions = _value
        logger.info("Options changed to {}".format(self.job.nukeoptions))

    def _nuke_version(self, _value):
        self.job.nukeversion = _value
        logger.info("Version changed to {}".format(self.job.nukeversion))

# -------------------------------------------------------------------------------------------------------------------- #
class HoudiniJobWidget(qg.QWidget):
    def __init__(self,job):
        super(HoudiniJobWidget, self).__init__()
        self.job=job
        self.setLayout(qg.QVBoxLayout())
        self.layout().setSpacing(0)
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().setAlignment(qc.Qt.AlignTop)
        self.setSizePolicy(qg.QSizePolicy.Minimum, qg.QSizePolicy.Fixed)

        # HOUDINI WIDGET
        self.houdini_widget = HoudiniWidget(self.job)
        self.layout().addWidget(self.houdini_widget)


# -------------------------------------------------------------------------------------------------------------------- #
class HoudiniWidget(qg.QWidget):
    def __init__(self,job):
        super(HoudiniWidget, self).__init__()
        self.job=job
        self.setLayout(qg.QVBoxLayout())
        self.layout().setSpacing(0)
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.setSizePolicy(qg.QSizePolicy.Minimum, qg.QSizePolicy.Fixed)

        self.layout().addWidget(Splitter("HOUDINI OPTIONS"))

        self.version_layout = qg.QHBoxLayout()
        self.version_layout.setContentsMargins(0, 0, 0, 0)
        self.version_layout.setSpacing(0)
        self.layout().addLayout(self.version_layout)

        self.version_text_lb = qg.QLabel('HOUDINI VERSION:')
        self.version_combo = qg.QComboBox()
        self.version_combo.addItems(CFG.env.getoptions("houdini","versions"))
        self.version_combo.setMinimumWidth(WIDTH_SMALL)
        self.version_layout = qg.QHBoxLayout()
        self.version_layout.setContentsMargins(0, 0, 0, 0)
        self.version_layout.setSpacing(0)
        self.version_layout.addWidget(self.version_text_lb)
        self.version_layout.addSpacerItem(qg.QSpacerItem(0, 5, qg.QSizePolicy.Expanding))
        self.version_layout.addWidget(self.version_combo)
        self.layout().addLayout(self.version_layout)

        self.options_text_lb = qg.QLabel('OPTIONS:')
        self.options_combo = qg.QComboBox()
        self.options_combo.setToolTip("Select from presets or edit yourself")
        self.options_combo.addItem("")
        self.options_combo.addItem("-V 2")
        self.options_combo.addItem("-V 2 -F 1-10 -F 20 -F 50-80x10")
        self.options_combo.setEditable(True)
        self.options_combo.setMinimumWidth(WIDTH_SMALL)
        self.options_layout = qg.QHBoxLayout()
        self.options_layout.setContentsMargins(0, 0, 0, 0)
        self.options_layout.setSpacing(0)
        self.options_layout.addWidget(self.options_text_lb)
        self.options_layout.addSpacerItem(qg.QSpacerItem(0, 5, qg.QSizePolicy.Expanding))
        self.options_layout.addWidget(self.options_combo)
        self.layout().addLayout(self.options_layout)

        # set initial values
        self._houdini_version(self.version_combo.currentText())
        self._options(self.options_combo.currentText())

        # connect vlaues to widget
        self.version_combo.activated.connect(lambda: self._houdini_version(self.version_combo.currentText()))
        self.options_combo.editTextChanged.connect(lambda: self._options(self.options_combo.currentText()))

    def _options(self, _value):
        self.job.houdinioptions = _value
        logger.info("Options changed to {}".format(self.job.houdinioptions))

    def _houdini_version(self, _value):
        self.job.houdiniversion = _value
        logger.info("Version changed to {}".format(self.job.houdiniversion))



# -------------------------------------------------------------------------------------------------------------------- #
class TractorWidget(qg.QWidget):
    def __init__(self,job):
        super(TractorWidget, self).__init__()
        self.job=job
        self.setLayout(qg.QVBoxLayout())
        self.layout().setSpacing(0)
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.setSizePolicy(qg.QSizePolicy.Minimum, qg.QSizePolicy.Fixed)

        self.tractor_options_splitter = Splitter("JOB TRACTOR OPTIONS")
        self.layout().addWidget(self.tractor_options_splitter)

        self.project_group_layout = qg.QHBoxLayout()
        self.project_group_layout.setContentsMargins(0, 0, 0, 0)
        self.project_group_layout.setSpacing(0)
        self.project_group_text_lb = qg.QLabel('PROJECT GROUP:')
        self.project_group_combo = qg.QComboBox()
        self.project_group_combo.addItems(CFG.env.getoptions("renderjob","projectgroup"))
        self.project_group_combo.setCurrentIndex(0)
        self.project_group_layout.addSpacerItem(qg.QSpacerItem(0, 5, qg.QSizePolicy.Expanding))
        self.project_group_layout.addWidget(self.project_group_text_lb)
        self.project_group_layout.addWidget(self.project_group_combo)

        self.layout().addLayout(self.project_group_layout)

        # set initial
        self._projectgroup(self.project_group_combo.currentText())
        # connections
        self.project_group_combo.activated.connect(lambda: self._projectgroup(self.project_group_combo.currentText()))

    def _projectgroup(self, _value):
        self.job.projectgroup =_value
        logger.info("Project group changed to {}".format(self.job.projectgroup))



# -------------------------------------------------------------------------------------------------------------------- #
class Directory(qg.QFileDialog):
    def __init__(self,startplace=None,title="Select a Directory Please"):
        super(Directory, self).__init__()
        self.setWindowTitle(title)
        self.setModal(True)
        self.fullpath = None
        self.relpath = None
        self.setDirectory(startplace)
        self.directory = self.getExistingDirectory(self,title)

        try:
            if self.directory:
                logger.info( "proj root: {}".format(self.directory))
                self.relpath= os.path.relpath(self.directory,startplace)
                self.fullpath=self.directory
                logger.info( "proj root rel: {}".format(self.relpath))
        except Exception, err:
            logger.warn( "directory: {}".format(err))

# -------------------------------------------------------------------------------------------------------------------- #
class File(qg.QFileDialog):
    def __init__(self,startplace=None,title='Select a File Please',filetypes=["*.ma","*.mb","*.nk","*.hip"]):
        super(File, self).__init__()
        # self.setWindowTitle(title)
        '''
        osx dialogue doesnt see the title dammit
        '''
        self.setModal(True)
        self.setDirectory(startplace)
        self.setFilter('*.ma')
        self.fullpath = None
        self.relpath = None
        self.fileName = self.getOpenFileName(self,title, startplace, "Files (%s)" % " ".join(filetypes))
        try:
            if self.fileName:
                logger.info( "scene file: {}".format(self.fileName))
                self.relpath= os.path.join(os.path.relpath(os.path.dirname(self.fileName[0]),startplace),
                                           os.path.basename(self.fileName[0]))
                self.fullpath=self.fileName[0]
        except Exception, err:
            logger.warn( "file: {}".format(err))

# -------------------------------------------------------------------------------------------------------------------- #
class Splitter(qg.QWidget):
    def __init__(self, text=None, shadow=True, color=(150, 150, 150)):
        super(Splitter, self).__init__()
        self.setMinimumHeight(2)
        self.setLayout(qg.QHBoxLayout())
        self.layout().setContentsMargins(2,8,2,4)
        self.layout().setSpacing(0)
        self.layout().setAlignment(qc.Qt.AlignVCenter)

        first_line = qg.QFrame()
        first_line.setFrameStyle(qg.QFrame.HLine)
        self.layout().addWidget(first_line)

        main_color  = 'rgba( %s, %s, %s, 255)' %color
        shadow_color = 'rgba( 45,  45,  45, 255)'

        bottom_border = ''
        if shadow:
            bottom_border = 'border-bottom:1px solid %s;' %shadow_color

        style_sheet = "border:0px solid rgba(0, 0, 0, 0); \
                       background-color: %s; \
                       max-height:1px; \
                       %s" %(main_color, bottom_border)

        first_line.setStyleSheet(style_sheet)

        if text is None:
            return

        first_line.setMaximumWidth(5)
        font = qg.QFont()
        font.setBold(True)

        text_width = qg.QFontMetrics(font)
        width = text_width.width(text) + 6

        label = qg.QLabel()
        label.setText(text)
        label.setFont(font)
        label.setMaximumWidth(width)
        label.setAlignment(qc.Qt.AlignHCenter | qc.Qt.AlignVCenter)

        self.layout().addWidget(label)

        second_line = qg.QFrame()
        second_line.setFrameStyle(qg.QFrame.HLine)
        second_line.setStyleSheet(style_sheet)
        self.layout().addWidget(second_line)

# -------------------------------------------------------------------------------------------------------------------- #
class FarmJobExtraWidget(qg.QWidget):
    def __init__(self, job):
        super(FarmJobExtraWidget, self).__init__()
        self.job=job
        self.setLayout(qg.QVBoxLayout())
        self.layout().setSpacing(4)
        self.layout().setContentsMargins(2,2,2,2)
        self.setSizePolicy(qg.QSizePolicy.Minimum, qg.QSizePolicy.Fixed)

        # self.layout().addWidget(Splitter("FARM EXTRA OPTIONS"))

        self.farm_group_box = qg.QGroupBox("Farm Options")
        self.farm_group_box_layout = qg.QGridLayout()
        self.farm_radio_box1 = qg.QRadioButton("Notify by Email")
        self.farm_radio_box2 = qg.QRadioButton("Make Edit Proxy")
        self.farm_radio_box3 = qg.QRadioButton("Send Proxy to Shotgun")
        self.farm_radio_box4 = qg.QRadioButton("Cleanup Render Trash")

        self.farm_radio_box1.setCheckable(True)
        self.farm_radio_box1.setAutoExclusive(False)
        self.farm_radio_box2.setCheckable(True)
        self.farm_radio_box2.setAutoExclusive(False)
        self.farm_radio_box2.setCheckable(True)
        self.farm_radio_box3.setAutoExclusive(False)
        self.farm_radio_box4.setCheckable(True)
        self.farm_radio_box4.setAutoExclusive(False)

        self.farm_group_box_layout.addWidget(self.farm_radio_box1,0,0)
        self.farm_group_box_layout.addWidget(self.farm_radio_box2,0,1)
        self.farm_group_box_layout.addWidget(self.farm_radio_box3,1,0)
        self.farm_group_box_layout.addWidget(self.farm_radio_box4,1,1)

        self.layout().addLayout(self.farm_group_box_layout)

        # connections
        self.farm_radio_box1.clicked.connect(lambda: self._box1(self.farm_radio_box1.isChecked()))
        self.farm_radio_box2.clicked.connect(lambda: self._box2(self.farm_radio_box2.isChecked()))
        self.farm_radio_box3.clicked.connect(lambda: self._box3(self.farm_radio_box3.isChecked()))
        self.farm_radio_box4.clicked.connect(lambda: self._box4(self.farm_radio_box4.isChecked()))

        # set initial
        self.farm_radio_box1.setChecked(True)
        self.farm_radio_box2.setChecked(True)
        self.farm_radio_box3.setChecked(False)
        self.farm_radio_box4.setChecked(False)
        self._box1(True)
        self._box2(True)
        self._box3(False)
        self._box4(False)

    def _box2(self, _value):
        self.job.makeproxy = _value
        logger.info("Options - Make proxy changed to {}".format(self.job.makeproxy))

    def _box1(self, _value):
        self.job.sendmail = _value
        logger.info("Options - Send mail changed to {}".format(self.job.sendmail))

    def _box3(self, _value):
        self.job.sendtoshotgun = _value
        logger.info("Options - Send to Shotgun changed to {}".format(self.job.sendtoshotgun))

    def _box4(self, _value):
        self.job.cleanup = _value
        logger.info("Options - Cleanup changed to {}".format(self.job.cleanup))

