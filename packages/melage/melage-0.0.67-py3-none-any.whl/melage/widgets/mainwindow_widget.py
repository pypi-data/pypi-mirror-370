__AUTHOR__ = 'Bahram Jafrasteh'


import os
import sys
sys.path.append('..')
from os.path import join, basename, dirname
#from PyQt5.QtWidgets import QFileDialog
from PyQt5 import QtWidgets, QtCore, QtGui
from melage.widgets.fileDialog_widget import QFileDialogPreview
from melage.utils.readData import readData
from melage.utils.utils import rhasattr
from melage.widgets.settings_widget import settingsBN
from melage.widgets.repeat_widget import repeatN
from melage.widgets.screenshot_widget import screenshot
from melage.widgets.enhanceImWidget import enhanceIm
from PyQt5.QtCore import Qt, QSettings
from melage.widgets.colorwidget import NewDialog
from melage.widgets.dockWidgets import dockWidgets
from melage.widgets.openglWidgets import openglWidgets
from melage.widgets.iminfo import iminfo_dialog
from melage.widgets.N4Dialog import N4Dialog, Worker
from melage.utils.utils import select_proper_widgets, setCursorWidget, \
    getCurrentSlice, updateSight, changeCoronalSagittalAxial, setSliceSeg, str_conv, find_avail_widgets,\
     update_last, manually_check_tree_item, update_image_sch, clean_parent_image, compute_volume
from melage.utils.source_folder import *
import time
from functools import partial
from collections import defaultdict


class Ui_Main(dockWidgets, openglWidgets):
    """
    Main widgets
    """
    setNewImage = QtCore.pyqtSignal(object)
    setNewImage2 = QtCore.pyqtSignal(object)
    def __init__(self):
        """
        Initializing the main attributes
        """
        super(Ui_Main, self).__init__()
        pwd = os.path.abspath(__file__)
        self.startTime = time.time()
        self.colorsCombinations = defaultdict(list)
        self._timer_id = -1
        self._last_index_select_image_eco = 2 # index for selection of image type ('neonatal', 'fetal', 'mri')
        self._last_index_select_image_mri = 2 # index for selection of image type ('neonatal', 'fetal', 'mri')
        self._last_state_guide_lines = False # guide lines are not activate
        self._last_state_preview = False # preview to show image preview before opening
        self.format_eco = 'None'
        self.format_mri = 'None'
        self._loaded = False
        self._num_adapted_points = 0
        self._firstSelection = None
        self._Xtimes = 1
        self._rad_circle = 50
        self._rad_circle_dot = 50
        self.num_measure_area = 0
        self.num_measure_length = 0
        self.source_dir = os.path.dirname(os.path.dirname(pwd))
        self.settingsBN = settingsBN(self)
        self.expectedTime = self.settingsBN.doubleSpinBox.value() * 60
        self.iminfo_dialog = iminfo_dialog(self)
        self._points_adapt_eco = []
        self._points_adapt_mri = []
        self.linePoints = []
        self._lastlines = []
        self._lineinfo = []
        self._slice_interp = [ [], [], []]
        self.tol_trk = 3
        self.linked_models = None
        self.linked = False
        self.filenameEco = ''
        self.filenameMRI = ''
        self.settingsBN.newConfig.connect(
            lambda vals: self.setConf(vals))

        self.repeatTimes = repeatN(self)
        self.repeatTimes.numberN.connect(
            lambda  value: self.setXTimes(value)
        )

        self.screenShot = screenshot(self)
        self.N4_dialog = N4Dialog(self)
        self.N4_dialog.closeSig.connect(partial(self.maskingClose, 3))

        self.N4_dialog.buttonpressed.connect(
            lambda  value: self.N4_correction(value)
        )
        self.N4_dialog.buttonpressed2.connect(
            lambda  value: self.N4_back(value)
        )

        from melage.widgets.ApplyMask import Masking
        from melage.widgets.ChangeSystem import ChangeCoordSys
        from melage.widgets.MaskOperations import MaskOperations
        from melage.widgets.HistImage import HistImage
        from melage.widgets.ImageThresholding import ThresholdingImage
        from melage.widgets.brain_extraction import BET
        from melage.widgets.brain_extraction_dl import BE_DL
        from melage.widgets.Segmentation import Tissue_Seg
        from melage.widgets.registrationWidget import RegistrationDialog
        from melage.widgets.tranformationWidget import TransformationDialog
        from melage.utils.utils import resize_window
        self.resizeImage = resize_window(self, use_combobox=True)
        self.Masking = Masking(self)
        self.ImageThresholding = ThresholdingImage(self)
        self.HistImage = HistImage(self)

        self.BET = BET(self)
        self.BET.set_pars()
        self.BE_DL = BE_DL(self)
        self.BE_DL.set_pars()

        self.Tissue_Seg = Tissue_Seg(self)
        self.Tissue_Seg.set_pars()

        self.registrationD = RegistrationDialog(self, self.source_dir)
        self.transformationD = TransformationDialog(self, self.source_dir)
        self.registrationD.datachange.connect(self.updateDataRegistration)
        self.MaskingOperations = MaskOperations(self)
        self.ChCoordSys = ChangeCoordSys(self)
        self.Masking.closeSig.connect(partial(self.maskingClose, 3))
        self.resizeImage.closeSig.connect(partial(self.maskingClose, 3))
        self.resizeImage.pushbutton.accepted.connect(partial(self.maskingClose, 3))
        self.resizeImage.pushbutton.rejected.connect(partial(self.maskingClose, 3))
        self.resizeImage.resizeim.connect(
            lambda value: self.resize_image(value, None)
        )
        self.resizeImage.comboboxCh.connect(
            lambda value1, value2: self.resize_image(value1, value2)
        )
        self.HistImage.closeSig.connect(partial(self.maskingClose, 3))
        self.BET.closeSig.connect(partial(self.maskingClose, 4))
        self.BE_DL.closeSig.connect(partial(self.maskingClose, 5))
        self.Tissue_Seg.closeSig.connect(partial(self.maskingClose, 10))


        self.ImageThresholding.closeSig.connect(partial(self.maskingClose, 3))
        self.MaskingOperations.closeSig.connect(partial(self.maskingClose, 3))
        self.registrationD.closeSig.connect(partial(self.maskingClose, 3))
        self.transformationD.closeSig.connect(partial(self.maskingClose, 3))
        self.ChCoordSys.closeSig.connect(partial(self.maskingClose, 3))
        self.iminfo_dialog.closeSig.connect(partial(self.maskingClose, 3))
        self.iminfo_dialog.buttonBox.clicked.connect(partial(self.maskingClose, 3))
        self.BET.betcomp.connect(
                                 lambda value: self.Thresholding('BET', value))
        self.BET.datachange.connect(self.updateDataBET)
        self.BE_DL.betcomp.connect(
                                   lambda value: self.Thresholding('Deep BET', value))

        self.BE_DL.back_orig.connect(
                                   lambda value: self.Thresholding('Deep BET', value))
        self.BE_DL.datachange.connect(partial(self.updateDataBEDL, 0))
        self.Tissue_Seg.datachange.connect(partial(self.updateDataBEDL, 1))
        self.Tissue_Seg.betcomp.connect(
                                   lambda value: self.Thresholding('Segmentation', value))


        self.ImageThresholding.applySig.connect(partial(self.Thresholding, 'apply'))
        self.ImageThresholding.histeqSig.connect(
                                   lambda value: self.Thresholding('histeq', value))
        self.ImageThresholding.repltSig.connect(partial(self.Thresholding, 'replot'))
        self.ChCoordSys.buttonpressed.connect(
            lambda value: self.applyNewCoordSys(value)
        )
        self.ChCoordSys.comboBox_image.currentIndexChanged.connect(
            self.setCurrentCoordsystem
        )
        self.Masking.buttonpressed.connect(
            lambda  value: self.applyMaskToImage(value, False)
        )

        self.MaskingOperations.buttonpressed.connect(
            lambda value: self.applyMaskToImage(value, True)
        )

        self.axis_eco = [0, 0, 1]
        self.axis_mri = [0, 0, 1]
        self.enhanceIm = enhanceIm(self)
        if not os.path.exists('.temp'):
            os.mkdir('.temp')
        self.MouseButtonPress = False
        self.MouseButtonRelease = False
        self._translate = QtCore.QCoreApplication.translate
        self._rotationAngleEco_coronal = 0
        self._rotationAngleEco_axial = 0
        self._rotationAngleEco_sagittal = 0
        self._rotationAngleMRI_coronal = 0
        self._rotationAngleMRI_axial = 0
        self._rotationAngleMRI_sagittal = 0
        self._lastReaderSegCol = []
        self._lastReaderSegInd = []
        self._lastReaderSegPrevCol = []
        self._lastMax = 10
        self._undoTimes = 0
        self._lastWindowName = None

        self.allowChangeScn = False
        self._filters = "Nifti(*.nia *.nii *.nii.gz *.hdr *.img *.img.gz *.mgz);;Vol (*.vol *.V00);;DICOM(*.dcm **);;NRRD(*.nrrd *.nhdr);;DICOMDIR(*DICOMDIR*)"
        formats = [ll.replace(' ', '').replace(')', '') for el in self._filters.split(';;') for ll in el.split('*')[1:]]
        formats = [el for el in formats if el != '' and '.' in el]
        self._availableFormats = formats
        self.settings = QSettings("./brainNeonatal.ini", QSettings.IniFormat) # setting to save
        self._basefileSave = ''



    def setConf(self, list_vals):
        """
        Configuration of MELAGE
        :param list_vals:
        :return:
        """
        self.expectedTime = list_vals[0]*60

    def setXTimes(self, val):
        """
        Set number of repetition
        :param val:
        :return:
        """
        self._Xtimes = val

    def showScreenShotWindow(self):
        """
        Take screen shot from window
        :return:
        """
        if self.screenShot.exec_() == self.screenShot.Accepted:
            type_im = self.screenShot.screencombo_data.currentText().lower()
            type_plane = self.screenShot.screencombo_plane.currentText().lower()
            vs = self.screenShot.screencombo_plane.isVisible()
            if type_im == 'ultrasound':
                if not hasattr(self, 'readImECO'):
                    self.screenShot.screen_error_msgbox('There is no UltraSound image')
                    return
                k = ['coronal', 'sagittal', 'axial'].index(type_plane)
                name = 'openGLWidget_' + str(k+1)
                widget = getattr(self, name)
                img = widget.takescreenshot()
            elif type_im == 'mri':
                if not hasattr(self, 'readImMRI'):
                    self.screenShot.screen_error_msgbox('There is no MRI image')
                    return
                k = ['coronal', 'sagittal', 'axial'].index(type_plane)+3
                name = 'openGLWidget_' + str(k+1)
                widget = getattr(self, name)
                img = widget.takescreenshot()
            else:
                # total
                img = []
                widgets_num = [0, 1, 2, 3, 4, 5, 10, 11]
                for k in widgets_num:
                    name = 'openGLWidget_' + str(k + 1)
                    widget = getattr(self, name)
                    if widget.imSlice is not None:
                        img = widget.takescreenshot('whole', self.width(), self.height())
                        break
            if img is None:
                self.screenShot.screen_error_msgbox('There is no image')
                return
            filters = "png(*.png)"
            opts = QtWidgets.QFileDialog.DontUseNativeDialog

            if len(img) == 0:
                screen = QtWidgets.QApplication.primaryScreen()
                winid = QtWidgets.QApplication.desktop().winId()
                p = screen.grabWindow(winid)
                fileObj = QtWidgets.QFileDialog.getSaveFileName(self, "Open File", self.source_dir, filters, options=opts)
                if fileObj[0] == '':
                    return
                filename = fileObj[0] + '.png'
                p.save(filename, 'png')
            else:
                fileObj = QtWidgets.QFileDialog.getSaveFileName(self, "Open File", self.source_dir, filters, options=opts)
                if fileObj[0] == '':
                    return
                filename = fileObj[0] + '.png'
                self.save_screenshot(img, filename)

    def showRpeatWindow(self):
        """
        Repetition window
        :return:
        """
        if self.repeatTimes.exec_() == self.repeatTimes.Accepted:
            val = self.repeatTimes.doubleSpinBox.value()
            self._Xtimes = int(val)
        else:
            self._Xtimes = 1

    def showInfoWindow(self):
        """
        Show information window
        :return:
        """
        self.settingsBN.show()

    def showIMVARSWindow(self):
        self.enhanceIm.show()

    def showImInfoWindow(self):
        self.iminfo_dialog.show()

    def setupUi(self, Main):
        """

        :param Main:
        :return:
        """
        Main.setObjectName("Main")
        Main.setEnabled(True)
        Main.resize(851, 733)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Main.sizePolicy().hasHeightForWidth())
        Main.setSizePolicy(sizePolicy)
        Main.setMinimumSize(QtCore.QSize(800, 800))
        Main.setBaseSize(QtCore.QSize(1280, 720))
        ### change geometry
        availableGeometry = self.screen().availableGeometry()
        self.resize(availableGeometry.width() , availableGeometry.height() )
        #self.move((availableGeometry.width() ) // 2, (availableGeometry.height()) // 2)
        ###
        font = QtGui.QFont()
        font.setFamily("Ubuntu")
        Main.setFont(font)
        Main.setCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
        Main.setDockNestingEnabled(True)
        self.centralwidget = QtWidgets.QWidget(Main)
        self.centralwidget.setEnabled(True)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding,
                                           QtWidgets.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.centralwidget.sizePolicy().hasHeightForWidth())
        self.centralwidget.setSizePolicy(sizePolicy)
        self.centralwidget.setMinimumSize(QtCore.QSize(800, 600))
        self.centralwidget.setObjectName("centralwidget")
        self.setContextMenuPolicy(Qt.ActionsContextMenu)

        self.createDockWidget(Main)
        self.createOpenGLWidgets(self.centralwidget, self.colorsCombinations)
        self.widgets_mri = [4, 5, 6, 12]
        self.widgets_eco = [11,1,2,3]
        #self.table_widget.setFunctionRemove(self.removeTableItem)
        #self.table_widget_measure.setFunctionRemove(self.removeTableMeasureItem)


        self.horizontalSlider_1.valueChanged.connect(self.changeSight1)
        self.horizontalSlider_2.valueChanged.connect(self.changeSight2)
        self.horizontalSlider_3.valueChanged.connect(self.changeSight3)
        self.horizontalSlider_4.valueChanged.connect(self.changeSight4)
        self.horizontalSlider_5.valueChanged.connect(self.changeSight5)
        self.horizontalSlider_6.valueChanged.connect(self.changeSight6)
        self.horizontalSlider_11.valueChanged.connect(self.changeSightTab3)
        self.horizontalSlider_12.valueChanged.connect(self.changeSightTab4)

        self.table_update.clicked.connect(self.linkMRIECO)
        self.table_link.clicked.connect(self.linkBoth)

        self.horizontalSlider_1.setVisible(False)
        self.horizontalSlider_2.setVisible(False)
        self.horizontalSlider_3.setVisible(False)
        self.horizontalSlider_4.setVisible(False)
        self.horizontalSlider_5.setVisible(False)
        self.horizontalSlider_6.setVisible(False)
        self.horizontalSlider_7.setVisible(False)
        self.horizontalSlider_8.setVisible(False)
        self.horizontalSlider_9.setVisible(False)
        self.horizontalSlider_10.setVisible(False)
        self.horizontalSlider_11.setVisible(False)
        self.horizontalSlider_12.setVisible(False)

        self.radioButton_1.setVisible(False)
        self.radioButton_2.setVisible(False)
        self.radioButton_3.setVisible(False)
        self.radioButton_4.setVisible(False)
        self.radioButton_21_1.setVisible(False)
        self.radioButton_21_2.setVisible(False)
        self.radioButton_21_3.setVisible(False)
        self.radioButton_21.setVisible(False)

        self.radioButton_1.clicked.connect( partial(self.changeToCoronal, 'eco') )
        self.radioButton_2.clicked.connect( partial (self.changeToSagittal, 'eco') )
        self.radioButton_3.clicked.connect( partial( self.changeToAxial, 'eco') )
        self.radioButton_4.clicked.connect(self.showSegOnWindow)

        self.radioButton_21_1.clicked.connect( partial(self.changeToCoronal, 'mri') )
        self.radioButton_21_2.clicked.connect( partial (self.changeToSagittal, 'mri') )
        self.radioButton_21_3.clicked.connect( partial( self.changeToAxial, 'mri') )
        self.radioButton_21.clicked.connect( self.showSegOnWindow)

        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_2.sizePolicy().hasHeightForWidth())
        self.label_1.setSizePolicy(sizePolicy)
        self.label_2.setSizePolicy(sizePolicy)
        self.label_3.setSizePolicy(sizePolicy)
        self.label_4.setSizePolicy(sizePolicy)
        self.label_5.setSizePolicy(sizePolicy)
        self.label_6.setSizePolicy(sizePolicy)
        self.label_7.setSizePolicy(sizePolicy)
        self.label_8.setSizePolicy(sizePolicy)
        self.label_9.setSizePolicy(sizePolicy)
        self.label_10.setSizePolicy(sizePolicy)
        self.label_11.setSizePolicy(sizePolicy)
        self.label_12.setSizePolicy(sizePolicy)

        Main.setCentralWidget(self.centralwidget)

        #self.createOpenglWidgets()

        
        #########################   Menus ################################
        self.menubar = QtWidgets.QMenuBar(Main)
        self.menubar.setNativeMenuBar(False)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1050, 22))
        self.menubar.setObjectName("menubar")
        Main.setMenuBar(self.menubar)

        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        self.menuAbout = QtWidgets.QMenu(self.menubar)
        self.menuAbout.setObjectName("menuAbout")

        self.menuView = QtWidgets.QMenu(self.menubar)
        self.menuView.setObjectName("menuView")

        self.menuToolbar = QtWidgets.QMenu(self.menuView)
        self.menuToolbar.setObjectName("menuToolbar")

        self.menuWidgets = QtWidgets.QMenu(self.menuView)
        self.menuWidgets.setObjectName("menuWidgets")

        self.menuTools = QtWidgets.QMenu(self.menubar)
        self.menuTools.setObjectName("menuTools")

        self.menuSeg = QtWidgets.QMenu(self.menuTools)
        self.menuSeg.setObjectName("menuSeg")

        self.menuCalc = QtWidgets.QMenu(self.menubar)
        self.menuCalc.setObjectName("menuCalc")

        self.menuPreprocess = QtWidgets.QMenu(self.menuTools)
        self.menuPreprocess.setObjectName("menuPrep")

        self.menuSegmentation = QtWidgets.QMenu(self.menuTools)
        self.menuSegmentation.setObjectName("menuSeg")

        self.menuRegistration = QtWidgets.QMenu(self.menuTools)
        self.menuRegistration.setObjectName("menuRegistration")

        self.menuBasicInfo = QtWidgets.QMenu(self.menuTools)
        self.menuBasicInfo.setObjectName("MenuBasicInfo")

        self.menuImport = QtWidgets.QMenu(self.menubar)
        self.menuImport.setObjectName("menuImport")

        self.menuExport = QtWidgets.QMenu(self.menubar)
        self.menuExport.setObjectName("menuExport")

        self.menuTV = QtWidgets.QMenu(self.menuCalc)
        self.menuTV.setObjectName("menuTV")

        ######################### Status Bar ################################
        self.statusbar = QtWidgets.QStatusBar(Main)
        self.statusbar.setObjectName("statusbar")
        Main.setStatusBar(self.statusbar)

        ######################### Open ################################
        self.actionOpenUS = QtWidgets.QAction(Main)
        self.actionOpenUS.setObjectName("actionOpenUS")
        icon_eco = QtGui.QIcon()
        icon_eco.addPixmap(QtGui.QPixmap(source_folder+"/view1.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)

        self.actionOpenUS.setIcon(icon_eco)
        self.actionOpenUS.setIconText('open')
        self.actionOpenUS.triggered.connect(self.browseUS)
        self.actionOpenUS.setDisabled(True)

        self.actionOpenMRI = QtWidgets.QAction(Main)
        self.actionOpenMRI.setObjectName("actionOpenMRI")
        icon_mri = QtGui.QIcon()
        icon_mri.addPixmap(QtGui.QPixmap(source_folder+"/view2.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self.actionOpenMRI.setIcon(icon_mri)
        self.actionOpenMRI.setIconText('open')
        self.actionOpenMRI.triggered.connect(self.browseMRI)
        self.actionOpenMRI.setDisabled(True)

        ######################### Actiton Open MultiSlices ###################
        self.actionComboBox = QtWidgets.QComboBox(Main)
        self.actionComboBox.setObjectName("actionComboBox")
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setRetainSizeWhenHidden(True)
        sizePolicy.setHeightForWidth(self.actionComboBox.sizePolicy().hasHeightForWidth())
        self.actionComboBox.setMinimumSize(QtCore.QSize(100, 0))
        self.actionComboBox.setSizePolicy(sizePolicy)
        self.actionComboBox.setObjectName("View1")
        self.actionComboBox.currentTextChanged.connect(self.changeVolume)
        self.actionComboBox.setDisabled(True)
        self.actionComboBox.setObjectName("comboBox")
        cbstyle = """
                    QComboBox QAbstractItemView {border: 1px solid grey;
                    background: #03211c; 
                    selection-background-color: #03211c;
                    "text-align: left;"} 
                    QComboBox {background: #03211c;margin-right: 1px;}
                    QComboBox::drop-down {
                subcontrol-origin: margin;}
                padding-left
                    """
        self.actionComboBox.setStyleSheet(cbstyle)
        for r in range(2):
            self.actionComboBox.addItem("{}".format(r))
        self.actionComboBox.setVisible(False)


        ######################### Load MEAN FA ###############################
        self.actionOpenFA = QtWidgets.QAction(Main)
        self.actionOpenFA.setObjectName("actionOpenFA")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(source_folder+"/dti.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self.actionOpenFA.setIcon(icon)
        self.actionOpenFA.setIconText('open')
        self.actionOpenFA.triggered.connect(self.browseFA)
        self.actionOpenFA.setDisabled(True)

        ######################### Load Tractography ###############################
        self.actionOpenTract = QtWidgets.QAction(Main)
        self.actionOpenTract.setObjectName("actionOpenTract")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(source_folder+"/tract.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self.actionOpenTract.setIcon(icon)
        self.actionOpenTract.setIconText('open')
        self.actionOpenTract.triggered.connect(self.browseTractoGraphy)
        self.actionOpenTract.setDisabled(True)

        ######################### New Project ################################
        self.actionNew = QtWidgets.QAction(Main)
        self.actionNew.setObjectName("actionNew")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(source_folder+"/new.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self.actionNew.setIcon(icon)
        self.actionNew.setIconText('New')
        self.actionNew.triggered.connect(self.newProject)

        ######################### Close US ################################
        self.actionCloseUS = QtWidgets.QAction(Main)
        self.actionCloseUS.setObjectName("actionNew")
        #icon = QtGui.QIcon()
        #icon.addPixmap(QtGui.QPixmap(source_folder+"/new.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        #self.actionCloseUS.setIcon(icon)
        self.actionCloseUS.setIconText('Close View 1')
        self.actionCloseUS.triggered.connect(self.CloseUS)
        #self.actionCloseUS.triggered.connect(self.CloseUS)

        ######################### Close MRI ################################
        self.actionCloseMRI = QtWidgets.QAction(Main)
        self.actionCloseMRI.setObjectName("actionNew")
        #icon = QtGui.QIcon()
        #icon.addPixmap(QtGui.QPixmap(source_folder+"/new.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        #self.actionCloseUS.setIcon(icon)
        self.actionCloseMRI.setIconText('Close View 2')
        self.actionCloseMRI.triggered.connect(self.CloseMRI)
        #self.actionCloseMRI.triggered.connect(partial(self.CloseMRI, dialogue=False))



        ######################### Import ################################




        self.actionImportSegMRI = QtWidgets.QAction(Main)
        self.actionImportSegMRI.setObjectName("action SegEco")
        #icon = QtGui.QIcon()
        #icon.addPixmap(QtGui.QPixmap(source_folder+"/new.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        #self.actionCloseUS.setIcon(icon)
        icon_mriS = QtGui.QIcon()
        icon_mriS.addPixmap(QtGui.QPixmap(source_folder+"/view2_seg.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self.actionImportSegMRI.setIcon(icon_mriS)
        self.actionImportSegMRI.setIconText('Segmented View 2')
        self.actionImportSegMRI.triggered.connect(partial(self.importData, 'MRISEG'))
        self.actionImportSegMRI.setDisabled(True)

        self.actionImportSegEco = QtWidgets.QAction(Main)
        self.actionImportSegEco.setObjectName("action SegEco")
        icon_ecoS = QtGui.QIcon()
        icon_ecoS.addPixmap(QtGui.QPixmap(source_folder+"/view1_seg.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self.actionImportSegEco.setIcon(icon_ecoS)
        self.actionImportSegEco.setIconText('Segmented view 1')
        self.actionImportSegEco.triggered.connect(partial(self.importData, 'USSEG'))
        self.actionImportSegEco.setDisabled(True)
        self.menuImport.addAction(self.actionOpenUS)
        self.menuImport.addAction(self.actionOpenMRI)


        self.menuImport.addSeparator()
        self.menuImport.addAction(self.actionImportSegEco)
        self.menuImport.addAction(self.actionImportSegMRI)





        ######################### Export ################################
        self.actionExportImEco = QtWidgets.QAction(Main)
        self.actionExportImEco.setObjectName("action ImEco")
        #icon = QtGui.QIcon()
        #icon.addPixmap(QtGui.QPixmap(source_folder+"/new.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        #self.actionCloseUS.setIcon(icon)
        self.actionExportImEco.setIcon(icon_eco)
        self.actionExportImEco.setIconText('Image View 1')
        self.actionExportImEco.triggered.connect(partial(self.exportData, 'USIM'))



        self.actionExportSegEco = QtWidgets.QAction(Main)
        self.actionExportSegEco.setObjectName("action SegEco")
        self.actionExportSegEco.setIcon(icon_ecoS)
        #icon = QtGui.QIcon()
        #icon.addPixmap(QtGui.QPixmap(source_folder+"/new.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        #self.actionCloseUS.setIcon(icon)
        self.actionExportSegEco.setIconText('Segmented View 1')
        self.actionExportSegEco.triggered.connect(partial(self.exportData, 'USSEG'))




        self.actionExportImMRI = QtWidgets.QAction(Main)
        self.actionExportImMRI.setObjectName("action IMMRI")
        self.actionExportImMRI.setIcon(icon_mri)
        #icon = QtGui.QIcon()
        #icon.addPixmap(QtGui.QPixmap(source_folder+"/new.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        #self.actionCloseUS.setIcon(icon)
        self.actionExportImMRI.setIconText('Image view 2')
        self.actionExportImMRI.triggered.connect(partial(self.exportData, 'MRIIM'))


        self.actionExportSegMRI = QtWidgets.QAction(Main)
        self.actionExportSegMRI.setObjectName("action SegEco")
        self.actionExportSegMRI.setIcon(icon_mriS)
        #icon = QtGui.QIcon()
        #icon.addPixmap(QtGui.QPixmap(source_folder+"/new.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        #self.actionCloseUS.setIcon(icon)
        self.actionExportSegMRI.setIconText('Segmented View 2')
        self.actionExportSegMRI.triggered.connect(partial(self.exportData, 'MRISEG'))

        self.menuExport.addAction(self.actionExportImMRI)
        self.menuExport.addAction(self.actionExportImEco)




        self.menuExport.addSeparator()
        self.menuExport.addAction(self.actionExportSegEco)
        self.menuExport.addAction(self.actionExportSegMRI)

        self.actionExportImMRI.setDisabled(True)
        self.actionExportSegMRI.setDisabled(True)

        self.actionExportImEco.setDisabled(True)
        self.actionExportSegEco.setDisabled(True)


        ######################### ScreenShot ################################
        self.actionScreenS = QtWidgets.QAction(Main)
        self.actionScreenS.setObjectName("actionNew")
        #icon = QtGui.QIcon()
        #icon.addPixmap(QtGui.QPixmap(source_folder+"/new.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        #self.actionCloseUS.setIcon(icon)
        self.actionScreenS.setIconText('Screen Shot')
        self.actionScreenS.triggered.connect(self.showScreenShotWindow)



        ######################### Load ################################
        self.actionLoad = QtWidgets.QAction(Main)
        self.actionLoad.setObjectName("actionLoad")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(source_folder+"/load.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self.actionLoad.setIcon(icon)
        self.actionLoad.setIconText('load')
        self.actionLoad.triggered.connect(self.loadProject)

        ######################### View -> Main Toolbar ################################
        self.actionMain_Toolbar = QtWidgets.QAction(Main)
        icon1 = QtGui.QIcon()
        #icon1.addPixmap(QtGui.QPixmap(source_folder+"e/action_check.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        #icon1.addPixmap(QtGui.QPixmap(source_folder+"/action_check_OFF.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        #self.actionMain_Toolbar.setIcon(icon1)
        self.actionMain_Toolbar.setObjectName("actionMain_Toolbar")
        self.actionMain_Toolbar.setCheckable(True)

        ######################### View -> GUIDELINES ################################
        self.action_guideLines = QtWidgets.QAction(Main)
        icon1 = QtGui.QIcon()
        self.action_guideLines.setObjectName("Guide lines")
        self.action_guideLines.setCheckable(True)

        ######################### View -> AXIS ################################
        self.action_axisLines = QtWidgets.QAction(Main)
        icon1 = QtGui.QIcon()
        self.action_axisLines.setObjectName("Axis lines")
        self.action_axisLines.setCheckable(True)
        ######################### View -> ZOOM PAN ROTATE TOOLBAR ################################
        self.action_interaction_Toolbar = QtWidgets.QAction(Main)
        icon1 = QtGui.QIcon()
        self.action_interaction_Toolbar.setObjectName("Interaction_Toolbar")
        self.action_interaction_Toolbar.setCheckable(True)

        ######################### File -> INFO ################################
        self.actionFile_info = QtWidgets.QAction(Main)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(source_folder+"/settings.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self.actionFile_info.setIcon(icon2)
        self.actionFile_info.setObjectName("actionFile_info")
        self.actionFile_info.triggered.connect(self.showInfoWindow)


        ######################### Tools -> Undo ################################
        self.actionUndo = QtWidgets.QAction(Main)
        #icon2 = QtGui.QIcon()
        #icon2.addPixmap(QtGui.QPixmap(source_folder+"/settings.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        #self.actionUndo.setIcon(icon2)
        self.actionUndo.setObjectName("action Undo")
        self.actionUndo.triggered.connect(self.Undo)

        ######################### Tools -> Redo ################################
        self.actionRedo = QtWidgets.QAction(Main)
        # icon2 = QtGui.QIcon()
        # icon2.addPixmap(QtGui.QPixmap(source_folder+"/settings.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        # self.actionUndo.setIcon(icon2)
        self.actionRedo.setObjectName("action Redo")
        self.actionRedo.triggered.connect(self.Redo)
        ######################### Tools -> contourGen ################################
        #self.actionContourGen = QtWidgets.QAction(Main)
        #self.actionContourGen.setObjectName("action contour generator")
        #self.actionContourGen.triggered.connect(self.GenerateContour)

        ######################### File -> ChangeImage ################################
        self.actionFile_changeIM = QtWidgets.QAction(Main)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(source_folder+"/info.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self.actionFile_changeIM.setIcon(icon2)
        self.actionFile_changeIM.setObjectName("actionFile_changeIM")
        self.actionFile_changeIM.triggered.connect(self.showIMVARSWindow)

        ######################### File -> Info ################################
        self.actionfile_iminfo = QtWidgets.QAction(Main)
        self.actionfile_iminfo.setObjectName("actionFile_info")
        self.actionfile_iminfo.triggered.connect(partial(self.maskingShow, 5))

        ######################### File -> convert ################################
        self.actionconvert = QtWidgets.QAction(Main)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(source_folder+"/export.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self.actionconvert.setIcon(icon)
        self.actionconvert.setObjectName("actionconvert")
        self.actionconvert.triggered.connect(self.convert)


        ######################### File -> save to nifti ################################
        #self.actionsaveModified = QtWidgets.QAction(Main)
        #icon = QtGui.QIcon()
        #icon.addPixmap(QtGui.QPixmap(source_folder+"/export.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        #self.actionsaveModified.setIcon(icon)
        #self.actionsaveModified.setObjectName("actionsavemodified")
        #self.actionsaveModified.triggered.connect(self.save_eco_to_nifti)

        ######################### File -> exit ################################
        self.actionexit = QtWidgets.QAction(Main)
        self.actionexit.setObjectName("actionexit")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(source_folder+"/close.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self.actionexit.setIcon(icon)
        self.actionexit.triggered.connect(self.close)

        ######################### Logo ################################
        self.logo = QtWidgets.QLabel(Main)
        self.logo.setPixmap(QtGui.QPixmap(source_folder+"/melage_top.png"))
        self.logo.resize(100,50)

        ######################### File -> save ################################
        self.actionsave = QtWidgets.QAction(Main)
        self.actionsave.setObjectName("actionsave")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(source_folder+"/save.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self.actionsave.setIcon(icon)
        self.actionsave.triggered.connect(self.save)
        self.actionsave.setDisabled(True)

        ######################### File -> saveas ################################
        self.actionsaveas = QtWidgets.QAction(Main)
        self.actionsaveas.setObjectName("actionsaveas")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(source_folder+"/saveas.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self.actionsaveas.setIcon(icon)
        self.actionsaveas.triggered.connect(self.saveas)
        self.actionsaveas.setDisabled(True)

        ######################### Pan Zoom ################################
        self.actionPan = QtWidgets.QAction(Main)
        self.actionPan.setObjectName("actionPan")
        self._icon_Hand_IXFaded = QtGui.QIcon()
        self._icon_Hand_IXFaded.addPixmap(QtGui.QPixmap(source_folder+"/Hand_IXFaded.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self._icon_Hand_IX = QtGui.QIcon()
        self._icon_Hand_IX.addPixmap(QtGui.QPixmap(source_folder+"/Hand_IX.png"), QtGui.QIcon.Normal,
                                          QtGui.QIcon.On)

        self.actionPan.setIcon(self._icon_Hand_IXFaded)

        self.actionContour = QtWidgets.QAction(Main)
        self.actionContour.setObjectName("actionContour")
        self._icon_contourFaded = QtGui.QIcon()
        self._icon_contourFaded.addPixmap(QtGui.QPixmap(source_folder+"/contourFaded.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self._icon_contour = QtGui.QIcon()
        self._icon_contour.addPixmap(QtGui.QPixmap(source_folder+"/contour.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)

        self.actionContour.setIcon(self._icon_contourFaded)


        self.actionPoints = QtWidgets.QAction(Main)
        self.actionPoints.setObjectName("actionPoints")
        self._icon_pointsFaded = QtGui.QIcon()
        self._icon_pointsFaded.addPixmap(QtGui.QPixmap(source_folder+"/pointsFaded.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self._icon_points = QtGui.QIcon()
        self._icon_points.addPixmap(QtGui.QPixmap(source_folder+"/points.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)

        self.actionPoints.setIcon(self._icon_pointsFaded)



        self.actionCircles = QtWidgets.QAction(Main)
        self.actionCircles.setObjectName("action Circles")
        self._icon_CircleFaded = QtGui.QIcon()
        self._icon_CircleFaded.addPixmap(QtGui.QPixmap(source_folder+"/circle_faded.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self._icon_circles = QtGui.QIcon()
        self._icon_circles.addPixmap(QtGui.QPixmap(source_folder+"/circle.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)

        self.actionCircles.setIcon(self._icon_CircleFaded)


        self.actionGoTo = QtWidgets.QAction(Main)
        self.actionGoTo.setCheckable(True)
        self.actionGoTo.setObjectName("goto")
        self._icon_gotoFaded = QtGui.QIcon()
        self._icon_gotoFaded.addPixmap(QtGui.QPixmap(source_folder+"/synchFaded.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self._icon_goto = QtGui.QIcon()
        self._icon_goto.addPixmap(QtGui.QPixmap(source_folder+"/synch.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)

        self.actionGoTo.setIcon(self._icon_gotoFaded)



        self.action3D = QtWidgets.QAction(Main)
        self.action3D.setCheckable(True)
        self.action3D.setChecked(True)
        self.action3D.setObjectName("goto")
        self._icon_3dFaded = QtGui.QIcon()
        self._icon_3dFaded.addPixmap(QtGui.QPixmap(source_folder+"/3dFaded.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self._icon_3d = QtGui.QIcon()
        self._icon_3d.addPixmap(QtGui.QPixmap(source_folder+"/3d.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)

        self.action3D.setIcon(self._icon_3d)

        self.actionZoomIn = QtWidgets.QAction(Main)
        self.actionZoomIn.setCheckable(True)
        self.actionZoomIn.setChecked(True)
        self.actionZoomIn.setObjectName("goto")
        self._icon_zoomIn = QtGui.QIcon()
        self._icon_zoomIn.addPixmap(QtGui.QPixmap(source_folder+"/zoom_inFaded.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self._icon_zoomIn = QtGui.QIcon()
        self._icon_zoomIn.addPixmap(QtGui.QPixmap(source_folder+"/zoom_in.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)

        self.actionZoomIn.setIcon(self._icon_zoomIn)


        self.actionZoomOut = QtWidgets.QAction(Main)
        self.actionZoomOut.setCheckable(True)
        self.actionZoomOut.setChecked(True)
        self.actionZoomOut.setObjectName("goto")
        self._icon_zoomOut = QtGui.QIcon()
        self._icon_zoomOut.addPixmap(QtGui.QPixmap(source_folder+"/zoom_outFaded.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self._icon_zoomOut = QtGui.QIcon()
        self._icon_zoomOut.addPixmap(QtGui.QPixmap(source_folder+"/zoom_out.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)

        self.actionZoomOut.setIcon(self._icon_zoomOut)


        self.actionContourX = QtWidgets.QAction(Main)
        self.actionContourX.setObjectName("actionContourX")
        self._icon_contourXFaded = QtGui.QIcon()
        self._icon_contourXFaded.addPixmap(QtGui.QPixmap(source_folder+"/contourXFaded.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self._icon_contourX = QtGui.QIcon()
        self._icon_contourX.addPixmap(QtGui.QPixmap(source_folder+"/contourX.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self.actionContourX.setIcon(self._icon_contourXFaded)


        self.actionColor = QtWidgets.QAction(Main)
        self.actionColor.setObjectName("actionColor")
        self._icon_colorXFaded = QtGui.QIcon()
        self.pixmap_box_color = QtGui.QPixmap(source_folder + "/box.png")
        colr = [1,1,1]
        self.pixmap_box_color.fill((QtGui.QColor(colr[0]*255, colr[1]*255, colr[2]*255, 1*255)))
        self._icon_colorXFaded.addPixmap(self.pixmap_box_color, QtGui.QIcon.Normal, QtGui.QIcon.On)
        self._icon_colorX = QtGui.QIcon()
        colr = [1, 0, 0]
        self.pixmap_box_color.fill((QtGui.QColor(colr[0]*255, colr[1]*255, colr[2]*255, 1*255)))
        self._icon_colorX.addPixmap(QtGui.QPixmap(source_folder+"/box.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self.actionColor.setIcon(self._icon_colorXFaded)
        self.actionColor.triggered.connect(self.color_picker)
        self.newdialog = NewDialog(Main)

        self.pixmap_box_label = QtWidgets.QLabel(Main)
        self.pixmap_box_label.setText('Combined')





        self.actionEraseX = QtWidgets.QAction(Main)
        self.actionEraseX.setObjectName("actionEraseX")
        self._icon_eraseXFaded = QtGui.QIcon()
        self._icon_eraseXFaded.addPixmap(QtGui.QPixmap(source_folder+"/EraserXFaded.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self._icon_eraseX = QtGui.QIcon()
        self._icon_eraseX.addPixmap(QtGui.QPixmap(source_folder+"/EraserX.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self.actionEraseX.setIcon(self._icon_eraseXFaded)



        self.actionRuler = QtWidgets.QAction(Main)
        self.actionRuler.setObjectName("actionMeasure")
        self._icon_rulerFaded = QtGui.QIcon()
        self._icon_rulerFaded.addPixmap(QtGui.QPixmap(source_folder+"/rulerFaded.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self._icon_ruler = QtGui.QIcon()
        self._icon_ruler.addPixmap(QtGui.QPixmap(source_folder+"/ruler.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self.actionRuler.setIcon(self._icon_ruler)


        self.actionLine = QtWidgets.QAction(Main)
        self.actionLine.setObjectName("actionLine")
        self._icon_lineFaded = QtGui.QIcon()
        self._icon_lineFaded.addPixmap(QtGui.QPixmap(source_folder+"/linefaded.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self._icon_line = QtGui.QIcon()
        self._icon_line.addPixmap(QtGui.QPixmap(source_folder+"/line.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self.actionLine.setIcon(self._icon_line)



        self.actionPaint = QtWidgets.QAction(Main)
        self.actionPaint.setObjectName("actionPaint")
        self._icon_pencilFaded = QtGui.QIcon()
        self._icon_pencilFaded.addPixmap(QtGui.QPixmap(source_folder+"/pencilFaded.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self._icon_pencil = QtGui.QIcon()
        self._icon_pencil.addPixmap(QtGui.QPixmap(source_folder+"/pencil.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)

        self.actionPaint.setIcon(self._icon_pencilFaded)


        self.actionErase = QtWidgets.QAction(Main)
        self.actionErase.setObjectName("actionErase")
        self._icon_EraserFaded = QtGui.QIcon()
        self._icon_EraserFaded.addPixmap(QtGui.QPixmap(source_folder+"/EraserFaded.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self._icon_Eraser = QtGui.QIcon()
        self._icon_Eraser.addPixmap(QtGui.QPixmap(source_folder+"/Eraser.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self.actionErase.setIcon(self._icon_EraserFaded)




        self.actionLazyContour = QtWidgets.QAction(Main)
        self.actionLazyContour.setObjectName("actionLazyContour")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(source_folder+"/zoom_out.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self.actionLazyContour.setIcon(icon)


        self.actionArrow = QtWidgets.QAction(Main)
        self.actionArrow.setObjectName("actionArrow")
        self._icon_arrowFaded = QtGui.QIcon()
        self._icon_arrowFaded.addPixmap(QtGui.QPixmap(source_folder+"/arrowFaded.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self._icon_arrow = QtGui.QIcon()
        self._icon_arrow.addPixmap(QtGui.QPixmap(source_folder+"/arrow.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self.actionArrow.setIcon(self._icon_arrowFaded)

        ######################### Rotate ################################

        self.actionrotate = QtWidgets.QAction(Main)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap( source_folder+"/action_check.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        icon1.addPixmap(QtGui.QPixmap(source_folder+"/action_check_OFF.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionrotate.setIcon(icon1)
        self.actionrotate.setObjectName("actionrotate")
        self.actionrotate.setCheckable(True)


        #self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        #self.pushButton.setGeometry(QtCore.QRect(50, 330, 89, 25))
        #self.pushButton.setObjectName("pushButton")



        ######################## SEG ########################################
        self.actionNNVentriclesSagittal = QtWidgets.QAction(Main)
        self.actionNNVentriclesSagittal.setObjectName("actionSag")
        self.actionNNVentriclesCoronal = QtWidgets.QAction(Main)
        self.actionNNVentriclesCoronal.setObjectName("actionCor")
        self.actionNNVentriclesAxial = QtWidgets.QAction(Main)
        self.actionNNVentriclesAxial.setObjectName("actionNNVentriclesAxial")

        self.actionNNventricleSegm = QtWidgets.QAction(Main)
        self.actionNNventricleSegm.setObjectName('Ventricle segmentation')

        self.actionN4Bias = QtWidgets.QAction(Main)
        self.actionN4Bias.setObjectName('N4 Bias field correction')

        self.actionTissueSeg = QtWidgets.QAction(Main)
        self.actionTissueSeg.setObjectName('FCM')


        self.actionHistImage = QtWidgets.QAction(Main)
        self.actionHistImage.setObjectName('Histogram Image')

        self.actionResizeImage = QtWidgets.QAction(Main)
        self.actionResizeImage.setObjectName('Histogram Image')

        self.actionBET = QtWidgets.QAction(Main)
        self.actionBET.setObjectName('BET')

        self.actionBEDL = QtWidgets.QAction(Main)
        self.actionBEDL.setObjectName('Deep BET')

        self.actionImageThresholding = QtWidgets.QAction(Main)
        self.actionImageThresholding.setObjectName('Image Thresholding')


        self.actionImageRegistration = QtWidgets.QAction(Main)
        self.actionImageRegistration.setObjectName('Image Registration')

        self.actionImageTransformation = QtWidgets.QAction(Main)
        self.actionImageTransformation.setObjectName('Image Transformation')

        self.actionMasking = QtWidgets.QAction(Main)
        self.actionMasking.setObjectName('Image Masking')

        self.actionOperationMask = QtWidgets.QAction(Main)
        self.actionOperationMask.setObjectName('Masking Operations')

        self.actionChangeCS = QtWidgets.QAction(Main)
        self.actionChangeCS.setObjectName('Change CS')


        self.actionNNventricleGatherIm = QtWidgets.QAction(Main)
        self.actionNNventricleGatherIm.setObjectName("actionNNventricleGatherIm")

        ######################## CALC ########################################

        self.actionTVCor = QtWidgets.QAction(Main)
        self.actionTVCor.setObjectName('3DVolume Coronal')

        self.actionTVSag = QtWidgets.QAction(Main)
        self.actionTVSag.setObjectName('3DVolume Sagital')

        self.actionTVAx = QtWidgets.QAction(Main)
        self.actionTVAx.setObjectName('3DVolume Axial')

        ######################### Help->Aobut ################################
        self.actionabout = QtWidgets.QAction(Main)
        self.actionabout.setObjectName("actionabout")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(source_folder+"/about.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self.actionabout.setIcon(icon)
        self.actionabout.triggered.connect(self.about)


        ######################### Help->Aobut ################################
        #self.actionVersion = QtWidgets.QAction(self.menubar)
        #self.actionVersion.setObjectName("actionVersion")
        #self.actionVersion.setStyleSheet("color: blue;")
        #self.actionVersion = QtWidgets.QWidgetAction(Main)
        #self.actionVersion.setForeground(QtGui.QColor('blue'))
        self.actionVersion = QtWidgets.QWidgetAction(self)
        label = QtWidgets.QLabel("Version {}".format(VERSION))
        label.setStyleSheet("color: white;")
        self.actionVersion.setDefaultWidget(label)

        ######################### Help->Manual ################################
        self.actionmanual = QtWidgets.QAction(Main)
        self.actionmanual.setObjectName("actionabout")
        #icon = QtGui.QIcon()
        #icon.addPixmap(QtGui.QPixmap(source_folder+"/about.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        #self.actionmanual.setIcon(icon)
        self.actionmanual.triggered.connect(self.manual)



        ######################### Actions ################################
        #self.menuFile.addAction(self.actionOpenUS)
        #self.menuFile.addAction(self.actionOpenMRI)
        self.menuFile.addAction(self.actionNew)
        self.menuFile.addAction(self.actionLoad)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionsave)
        self.menuFile.addAction(self.actionsaveas)
        #self.menuFile.addAction(self.actionsaveModified)
        self.menuFile.addSeparator()
        #self.menuFile.addAction(self.actionconvert)
        self.menuFile.addMenu(self.menuImport)
        self.menuFile.addMenu(self.menuExport)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionScreenS)

        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionCloseUS)
        self.menuFile.addAction(self.actionCloseMRI)

        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionFile_info)
        self.menuFile.addAction(self.actionexit)

        self.menuAbout.addAction(self.actionmanual)
        self.menuAbout.addAction(self.actionabout)
        self.menuAbout.addAction(self.actionVersion)


        self.menuView.addAction(self.actionMain_Toolbar)
        self.menuView.addAction(self.action_interaction_Toolbar)
        self.menuView.addAction(self.action_guideLines)
        self.menuView.addAction(self.action_axisLines)
        self.menuView.addMenu(self.menuToolbar)
        self.menuToolbar.addAction(self.actionMain_Toolbar)
        self.menuToolbar.addAction(self.action_interaction_Toolbar)
        self.menuView.addMenu(self.menuWidgets)
        actions_widgets = self.createPopupMenu().actions()
        for action in actions_widgets:
            self.menuWidgets.addAction(action)

        self.menuSeg.addSeparator()

        #self.menuSeg.addAction(self.actionNNVentriclesSagittal)
        #self.menuSeg.addAction(self.actionNNVentriclesCoronal)
        #self.menuSeg.addAction(self.actionNNVentriclesAxial)
        self.menuSeg.addAction(self.actionNNventricleSegm)

        #self.menuSeg.addAction(self.actionNNventricleGatherIm)


        self.menuTV.addSeparator()
        self.menuTV.addAction(self.actionTVCor)
        self.menuTV.addAction(self.actionTVSag)
        self.menuTV.addAction(self.actionTVAx)

        self.menuBasicInfo.addAction(self.actionHistImage)

        self.menuBasicInfo.addAction(self.actionfile_iminfo)

        self.menuRegistration.addAction(self.actionImageRegistration)
        self.menuRegistration.addAction(self.actionImageTransformation)



        self.menuPreprocess.addAction(self.actionMasking)
        self.menuPreprocess.addAction(self.actionOperationMask)
        self.menuPreprocess.addSeparator()
        self.menuPreprocess.addAction(self.actionResizeImage)
        self.menuPreprocess.addAction(self.actionChangeCS)
        self.menuPreprocess.addSeparator()
        self.menuPreprocess.addAction(self.actionN4Bias)



        self.menuSegmentation.addAction(self.actionBEDL)
        self.menuSegmentation.addAction(self.actionBET)
        self.menuSegmentation.addSeparator()
        self.menuSegmentation.addAction(self.actionTissueSeg)
        self.menuSegmentation.addAction(self.actionImageThresholding)


        self.menuCalc.addAction(self.menuTV.menuAction())

        #self.menuTools.addAction(self.actionrotate)
        #self.menuTools.addAction(self.actionPan)
        #self.menuTools.addAction(self.actionContour)
        #self.menuTools.addAction(self.actionLazyContour)
        #self.menuTools.addAction(self.actionNNventricleSegm)
        #self.menuTools.addAction(self.actionFile_changeIM)
        self.menuTools.addAction(self.actionUndo)
        self.menuTools.addAction(self.actionRedo)
        #self.menuTools.addAction(self.actionContourGen)
        #self.menuTools.addAction(self.menuSeg.menuAction())
        self.menuTools.addSeparator()
        self.menuTools.addAction(self.menuPreprocess.menuAction())
        self.menuTools.addSeparator()
        self.menuTools.addAction(self.menuSegmentation.menuAction())
        self.menuTools.addSeparator()
        #self.menuTools.addAction(self.menuRegistration.menuAction())
        self.menuTools.addAction(self.menuBasicInfo.menuAction())

        #self.menuTools.addAction(self.actionNNventricleGatherIm)

        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuView.menuAction())
        self.menubar.addAction(self.menuTools.menuAction())
        #self.menubar.addAction(self.menuCalc.menuAction())
        self.menubar.addAction(self.menuAbout.menuAction())
        #self.menubar.addAction(self.actionVersion)


        self.toolBar = QtWidgets.QToolBar(Main)
        self.toolBar.setObjectName("toolBar")
        Main.addToolBar(QtCore.Qt.TopToolBarArea, self.toolBar)
        Main.insertToolBarBreak(self.toolBar)
        self.toolBar.addAction(self.actionNew)
        self.toolBar.addAction(self.actionLoad)
        self.toolBar.addAction(self.actionsave)

        self.toolBar.addSeparator()
        #self.toolBar.addAction(self.actionsaveas)
        #spacerItem = QtWidgets.QWidget()
        #spacerItem.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        #self.toolBar.addWidget(spacerItem)
        cts = """
        QToolBar {
  background-color: #000000;
  border-bottom: 0px solid #19232D;
  padding: 0px;
  font-weight: bold;
  spacing: 0px;
}
QToolBar::separator:horizontal
{
	width: 10px;
	margin-left: 10px;
		margin-right: 10px;
}
QToolButton{margin: 2px 2px;}
        """
        self.toolBar.setStyleSheet(cts)

        self.toolBar.addAction(self.actionOpenUS)
        self.toolBar.addAction(self.actionImportSegEco)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.actionOpenMRI)
        self.toolBar.addAction(self.actionImportSegMRI)



        #self.toolBar.addAction(self.actionOpenFA)
        #self.toolBar.addAction(self.actionOpenTract)
        self.toolBar.addSeparator()
        self.actionComboBox_visible = self.toolBar.addWidget(self.actionComboBox)
        self.actionComboBox_visible.setVisible(False)
        #self.toolBar.addSeparator()
        spacerItem = QtWidgets.QWidget()
        spacerItem.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)

        self.toolBar.addWidget(spacerItem)

        self.toolBar.addWidget(self.logo)
        self.toolBar.addAction(self.actionexit)

        self.toolBar2 = QtWidgets.QToolBar(Main)
        self.toolBar2.setObjectName("Interaction")
        Main.addToolBar(QtCore.Qt.TopToolBarArea, self.toolBar2)
        Main.insertToolBarBreak(self.toolBar2)
        self.toolBar2.addAction(self.actionArrow)
        self.toolBar2.addAction(self.actionPan)
        self.toolBar2.addSeparator()
        self.toolBar2.setStyleSheet(cts)
        self.toolBar2.addAction(self.actionErase)
        self.toolBar2.addAction(self.actionEraseX)
        self.toolBar2.addSeparator()
        self.toolBar2.addAction(self.actionPaint)
        self.toolBar2.addAction(self.actionContour)
        self.toolBar2.addAction(self.actionContourX)
        self.toolBar2.addAction(self.actionCircles)
        self.toolBar2.addSeparator()
        self.toolBar2.addAction(self.actionColor)
        self.toolBar2.addWidget(self.pixmap_box_label)
        #self.toolBar2.addSeparator()




        spacerItem = QtWidgets.QWidget()
        spacerItem.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)

        self.toolBar2.addWidget(spacerItem)

        self.toolBar2.addAction(self.actionLine)

        self.toolBar2.addAction(self.actionPoints)
        self.toolBar2.addSeparator()
        self.toolBar2.addAction(self.actionZoomIn)
        self.toolBar2.addAction(self.actionZoomOut)
        self.toolBar2.addSeparator()
        self.toolBar2.addAction(self.actionRuler)
        self.toolBar2.addAction(self.actionGoTo)
        self.toolBar2.addAction(self.action3D)
        self.toolBar2.setDisabled(True)


        self.actionArrow.triggered.connect(partial(self.setCursors, 0))
        self.actionPan.triggered.connect(partial(self.setCursors, 2))
        self.actionPaint.triggered.connect(partial(self.setCursors, 1))
        self.actionErase.triggered.connect(partial(self.setCursors, 3))
        self.actionRuler.triggered.connect(partial(self.setCursors,6))
        self.actionLine.triggered.connect(partial(self.setCursors, 8))
        self.actionContour.triggered.connect(partial(self.setCursors, 4))
        self.actionPoints.triggered.connect(partial(self.setCursors, 5))
        self.actionCircles.triggered.connect(partial(self.setCursors, 9, None))
        #self.actionGoTo.triggered.connect(partial(self.setCursors, 7))
        self.actionGoTo.triggered.connect(self.activateGuidelines)
        self.action3D.triggered.connect(self.activate3d)
        self.actionZoomIn.triggered.connect(partial(self.Zoom, 'In'))
        self.actionZoomOut.triggered.connect(partial(self.Zoom, 'Out'))
        self.actionContourX.triggered.connect(self.showRpeatWindow)
        self.actionContourX.triggered.connect(partial(self.setCursorsX, 4))
        self.actionEraseX.triggered.connect(self.showRpeatWindow)
        self.actionEraseX.triggered.connect(partial(self.setCursorsX, 3))
        #self.actionSegExportEco.triggered.connect(self.showScreenShotWindow)




        self.retranslateUi(Main)
        QtCore.QMetaObject.connectSlotsByName(Main)


        #self.horizontalSlider.valueChanged.connect(self.openGLWidget.setXRotation)
        #self.openGLWidget.xRotationChanged.connect(self.horizontalSlider.setValue)


        ######################### Visibility ################################

        self.actionMain_Toolbar.triggered.connect(self.toolBar.setVisible)
        self.action_guideLines.triggered.connect(self.activateGuidelines)
        self.action_axisLines.triggered.connect(self.activateAxisLines)
        self.toolBar.visibilityChanged.connect(self.actionMain_Toolbar.setChecked)

        #self.action_interaction_Toolbar.triggered.connect(self.toolBar2.setVisible)
        #self.toolBar2.visibilityChanged.connect(self.action_interaction_Toolbar.setChecked)


        ######################## OPENG GL CONTROL PANNEL ########################


        self.hs_t1_1.valueChanged.connect(self.changeBrightness)
        self.hs_t1_2.valueChanged.connect(self.changeContrast)
        self.hs_t1_3.valueChanged.connect(self.changeBandPass)
        self.hs_t1_4.valueChanged.connect(self.changeSobel)
        self.hs_t1_5.valueChanged.connect(self.Rotate)
        self.hs_t1_7.valueChanged.connect(self.changeBandPass)
        #self.hs_t1_8.valueChanged.connect(self.changeColorize)
        #self.colorize.clicked.connect(self.changeColorize)
        self.toggle1_1.clicked.connect(self.changeHamming)


        self.hs_t2_1.valueChanged.connect(self.changeBrightness)
        self.hs_t2_2.valueChanged.connect(self.changeContrast)
        self.hs_t2_3.valueChanged.connect(self.changeBandPass)
        self.hs_t2_7.valueChanged.connect(self.changeBandPass)
        #self.hs_t2_8.valueChanged.connect(self.changeColorize)
        #self.colorize_MRI.clicked.connect(self.changeColorize)


        self.hs_t2_4.valueChanged.connect(self.changeSobel)
        self.hs_t2_5.valueChanged.connect(self.Rotate)
        self.toggle2_1.clicked.connect(self.changeHamming)

        self.page1_s2c.clicked.connect(self.C2S)
        self.page2_s2c.clicked.connect(self.C2S)

        #self.dw2_cb.currentTextChanged.connect(self.changeColorPen)

        #self.dockWidgetContents_mri_colors.cha
        self.dw2_s2.valueChanged.connect(self.changeSizePen)
        self.dw2_s1.valueChanged.connect(lambda value: self.changeRadiusCircle(value, True))


        self.dw4_s1.valueChanged.connect(self.vnetricleSegmentShow)
        self.scroll_intensity.valueChanged.connect(lambda thrsh: self.ColorIntensityChange(thrsh, 'seg'))
        self.scroll_image_intensity.valueChanged.connect(lambda thrsh: self.ColorIntensityChange(thrsh, 'image'))



        self.page1_rot_cor.currentTextChanged.connect(self.changeRotAx)
        self.page2_rot_cor.currentTextChanged.connect(self.changeRotAx)

        self.dw5_s1.valueChanged.connect(self.trackDistance)
        self.dw5_s2.valueChanged.connect(self.trackThickness)






        #self.actionrotate.triggered.connect(self.horizontalSlider.setVisible)
        #self.actionrotate.triggered.connect(self.label_horizontalSlider.setVisible)
        self.actionNNventricleSegm.triggered.connect(self.segmentVentricles)
        self.actionN4Bias.triggered.connect(partial(self.maskingShow, 3))
        self.actionHistImage.triggered.connect(partial(self.maskingShow, 4))
        self.actionResizeImage.triggered.connect(partial(self.maskingShow, 8))
        self.actionBET.triggered.connect(partial(self.maskingShow, 7))
        self.actionBEDL.triggered.connect(partial(self.maskingShow, 9))#masking

        self.actionTissueSeg.triggered.connect(partial(self.maskingShow, 10))  # FCM
 # FCM


        self.actionImageThresholding.triggered.connect(partial(self.maskingShow, 6))
        self.actionImageRegistration.triggered.connect(partial(self.registerShow, 0))
        self.actionImageTransformation.triggered.connect(partial(self.registerShow, 1))
        self.actionMasking.triggered.connect(partial(self.maskingShow, 0))
        self.actionOperationMask.triggered.connect(partial(self.maskingShow, 1))
        self.actionChangeCS.triggered.connect(partial(self.maskingShow, 2))

        self.actionNNVentriclesCoronal.triggered.connect(partial(self.vnetricleSegmentShow, 50))
        self.actionNNVentriclesAxial.triggered.connect(partial(self.vnetricleSegmentShow, 50))
        self.actionNNVentriclesSagittal.triggered.connect(partial(self.vnetricleSegmentShow, 50))

        self.actionTVCor.triggered.connect(partial(self.CalcTotalVolume, 'Coronal'))
        self.actionTVSag.triggered.connect(partial(self.CalcTotalVolume, 'sagittal'))
        self.actionTVAx.triggered.connect(partial(self.CalcTotalVolume, 'Axial'))

        self.actionNNventricleGatherIm.triggered.connect(self.gatherToIm)
        name = 'openGLWidget_'
        for i in range(12):

            nameWidget = name + str(i + 1)
            if hasattr(self, nameWidget):
                widget = getattr(self, name + str(i + 1))
                widget.segChanged.connect(
                    lambda whiteInd, currentWidnowName, colorInd, sliceNum: self.updateSegmentation(whiteInd, currentWidnowName,
                                                                                          colorInd, sliceNum))

                widget.LineChanged.connect(
                    lambda params: self.updateLP(params))
                widget.interpolate.connect(
                    lambda params: self.Interpolate(params))
                widget.zoomchanged.connect(lambda value, slider: self.changeRadiusCircle(value, slider))

                widget.rulerInfo.connect(
                    lambda distance, colorind: self.update_table_measure(distance, colorind))

                widget.sliceNChanged.connect(
                    lambda sliceNumber: self.updateSliceNumber(sliceNumber)
                )
                widget.goto.connect(
                    lambda slices, currentWidnowName: self.updateAllSlices(slices, currentWidnowName)
                )

        self.setNewImage.connect(
            lambda shapeImage: self.openGLWidget_14.createGridAxis(shapeImage)
        )

        self.setNewImage2.connect(
            lambda shapeImage: self.openGLWidget_24.createGridAxis(shapeImage)
        )

        self.openGLWidget_14.point3dpos.connect(
            lambda pose3d, windowName : self.updateLabelPs(pose3d, windowName, 'eco')
        )
        self.openGLWidget_24.point3dpos.connect(
            lambda pose3d, windowName : self.updateLabelPs(pose3d, windowName, 'mri')
        )


        self.openGLWidget_14.update_3dview.connect(
            lambda map_type, reset : self.update3Dview(map_type, None, 'eco')
        )
        self.openGLWidget_24.update_3dview.connect(
            lambda map_type, reset : self.update3Dview(map_type, None, 'mri')
        )


        self.openGLWidget_14.update_cmap.connect(
            lambda map_type, reset : self.update3Dview(map_type, reset, 'eco')
        )
        self.openGLWidget_24.update_cmap.connect(
            lambda map_type, reset : self.update3Dview(map_type, reset, 'mri')
        )



        self.tabWidget.currentChanged.connect(self.changedTab)
        self.openGLWidget_11.resized.connect(self.changedTab)
        self.openGLWidget_12.resized.connect(self.changedTab)

        self.setFocusPolicy(Qt.StrongFocus)
        self.installEventFilter(self)
        self.init_state()
        self.create_cursors()

        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        self.toolBar2.setSizePolicy(sizePolicy)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        self.toolBar.setSizePolicy(sizePolicy)

        self.Main = Main


    def updateDataBEDL(self, index):
        """
        Brain Extraction widget
        :return:
        """
        if index ==0:
            el = self.BE_DL
        elif index == 1:
            el = self.Tissue_Seg
        ind_image = el.comboBox_image.currentIndex()
        from melage.utils.utils import make_image_using_affine
        if ind_image==0:
            if not hasattr(self, 'readImECO'):
                return
            if not hasattr(self.readImECO, 'im'):
                return
            affine, header = None, None
            if hasattr(self.readImECO, 'affine'):
                affine = self.readImECO.affine
            if hasattr(self.readImECO, 'header'):
                header = self.readImECO.header
            img = make_image_using_affine(self.readImECO.npImage, affine, header)
            el.setData(img, self.readImECO.ImSpacing)
        elif ind_image==1:
            if not hasattr(self, 'readImMRI'):
                return
            if not hasattr(self.readImMRI, 'im'):
                return
            affine, header = None, None
            if hasattr(self.readImMRI, 'affine'):
                affine = self.readImMRI.affine
            if hasattr(self.readImMRI, 'header'):
                header = self.readImMRI.header
            img = make_image_using_affine(self.readImMRI.npImage, affine, header)
            el.setData(img, self.readImMRI.ImSpacing)


    def updateDataRegistration(self):
        """
        Image to Image registration window
        :return:
        """
        val = self.registrationD
        ind_image = val.comboBox_image.currentIndex()
        if ind_image==0:
            if not hasattr(self, 'readImECO'):
                return
            if not hasattr(self.readImECO, 'im'):
                return
            val.setData(self.readImECO.im)
        elif ind_image==1:
            if not hasattr(self, 'readImMRI'):
                return
            if not hasattr(self.readImMRI, 'im'):
                return

            val.setData(self.readImMRI.im)


    def updateDataBET(self):
        """
        Updating Brain Extraction Tools
        :return:
        """
        ind_image = self.BET.comboBox_image.currentIndex()
        if ind_image==0:
            if not hasattr(self, 'readImECO'):
                return
            if not hasattr(self.readImECO, 'im'):
                return
            self.BET.setData(self.readImECO.npImage, self.readImECO.ImSpacing)
        elif ind_image==1:
            if not hasattr(self, 'readImMRI'):
                return
            if not hasattr(self.readImMRI, 'im'):
                return

            self.BET.setData(self.readImMRI.npImage, self.readImMRI.ImSpacing)

    def resize_image(self, ind_image, ind=None):
        """
        Image resize
        :param ind_image:
        :param ind:
        :return:
        """
        hasattr(self.readImMRI, 'im')
        if ind is not None:
            if ind == 0 and hasattr(self.readImECO, 'im'):
                spacing = self.readImECO.ImSpacing
                txt = '{:.3f},{:.3f},{:.3f}'.format(spacing[0], spacing[1], spacing[2])
                self.resizeImage.label_current_spc.setText(txt)
            elif ind == 1 and hasattr(self.readImMRI, 'im'):
                spacing = self.readImMRI.ImSpacing
                txt = '{:.3f},{:.3f},{:.3f}'.format(spacing[0], spacing[1], spacing[2])
                self.resizeImage.label_current_spc.setText(txt)
            else:
                txt = '{:.3f},{:.3f},{:.3f}'.format(0, 0, 0)
                self.resizeImage.label_current_spc.setText(txt)
            return
        from melage.utils.utils import resample_to_spacing, convert_to_ras
        spacing = self.resizeImage.label_new_spc.value()
        isLinear = self.resizeImage.radioButton_1.isChecked()
        method = 'spline'
        if isLinear:
            method='linear'

        if ind_image==0:
            if not hasattr(self, 'readImECO'):
                return
            if not hasattr(self.readImECO, 'im'):
                return
            self.readImECO.im = resample_to_spacing(self.readImECO.im, spacing, method)
            transform, self.readImECO.source_system = convert_to_ras(self.readImECO.im.affine, target=self.readImECO.target_system)
            self.readImECO.im = self.readImECO.im.as_reoriented(transform)
            self.readImECO.set_metadata()
            self.readImECO.read_pars(reset_seg=True)
            self.browseUS(fileObj=None, use_dialog=False)
            self.changedTab()
        elif ind_image==1:
            if not hasattr(self, 'readImMRI'):
                return
            if not hasattr(self.readImMRI, 'im'):
                return
            self.readImMRI.im = resample_to_spacing(self.readImMRI.im, spacing, method)
            transform, self.readImMRI.source_system = convert_to_ras(self.readImMRI.im.affine, target=self.readImMRI.target_system)
            self.readImMRI.im = self.readImMRI.im.as_reoriented(transform)
            self.readImMRI.set_metadata()
            self.readImMRI.read_pars(reset_seg=True)
            self.browseMRI(fileObj=None, use_dialog=False)
            self.changedTab()


    def applyMaskToImage(self, values, operation=False):
        """
        Apply masks to image
        :param values:
        :return:
        """
        if len(values)==3:
            ind_image, ind_sel, keep = values
            ind_color = int(float(self.color_name[ind_sel].split('_')[0]))
        else:
            ind_image, ind_sel, ind_sel2, type_operation = values
            ind_color = int(float(self.color_name[ind_sel].split('_')[0]))
            ind_color2 = int(float(self.color_name[ind_sel2].split('_')[0]))

        if ind_image==0:
            if not hasattr(self, 'readImECO'):
                return
            if not hasattr(self.readImECO, 'im'):
                return

            ind_selected = self.readImECO.npSeg==ind_color
            if operation:
                ind_selected2 = self.readImECO.npSeg == ind_color2
                if type_operation=='+':
                    ind_selected = (ind_selected.astype('int') + ind_selected2.astype('int'))>0
                    self.readImECO.npSeg[ind_selected] = ind_color
                elif type_operation== '-':
                    ind_selected = (ind_selected.astype('int') - ind_selected2.astype('int'))>0
                    self.readImECO.npSeg[ind_selected] = ind_color
            else:
                if ind_color!=9876:
                    im = self.readImECO.npImage.copy()
                else:
                    im = self.readImECO.im.get_fdata().copy()
                if ind_selected.sum() > 1:
                    if keep:
                        im[~ind_selected] = 0
                    else:
                        im[ind_selected] = 0
                from melage.utils.utils import make_image
                im = make_image(im, self.readImECO.im)
                self.readImECO.changeImData(im, axis=[0, 1, 2])
                self.browseUS(fileObj=None, use_dialog=False)
            self.changedTab()
        elif ind_image==1:
            if not hasattr(self, 'readImMRI'):
                return
            if not hasattr(self.readImMRI, 'im'):
                return
            ind_selected = self.readImMRI.npSeg == ind_color
            if operation:
                ind_selected2 = self.readImMRI.npSeg == ind_color2
                if type_operation=='+':
                    ind_selected = (ind_selected.astype('int') + ind_selected2.astype('int'))>0
                    self.readImMRI.npSeg[ind_selected] = ind_color
                elif type_operation== '-':
                    ind_selected = (ind_selected.astype('int') - ind_selected2.astype('int'))>0
                    self.readImMRI.npSeg[ind_selected] = ind_color
            else:
                if ind_color != 9876:
                    im = self.readImMRI.npImage.copy()
                else:
                    im = self.readImMRI.im.get_fdata().copy()

                if ind_selected.sum() > 1:
                    if keep:
                        im[~ind_selected]=0
                    else:
                        im[ind_selected] = 0
                from melage.utils.utils import make_image
                im = make_image(im, self.readImMRI.im)
                self.readImMRI.changeImData(im, axis=[0, 1, 2])
                self.browseMRI(fileObj=None, use_dialog=False)
            self.changedTab()

    def setCurrentCoordsystem(self):
        """
        Current Coordinate System
        :return:
        """
        from melage.utils.utils import getCurrentCoordSystem
        current = 'None'
        if self.ChCoordSys.comboBox_image.currentIndex()==0:
            try:
                current = getCurrentCoordSystem(self.readImECO.im.affine)
            except:
                pass
        elif self.ChCoordSys.comboBox_image.currentIndex()==1:
            try:
                current = getCurrentCoordSystem(self.readImMRI.im.affine)
            except:
                pass
        self.ChCoordSys.label_current.setText(current)

    def applyNewCoordSys(self, values):
        """
        Apply new coordsystem
        :param values:
        :return:
        """
        ind_image, targ_system = values
        if ind_image==0:
            if not hasattr(self, 'readImECO'):
                return
            if not hasattr(self.readImECO, 'im'):
                return

            status = self.readImECO._changeCoordSystem(targ_system)
            if status:
                self.setCurrentCoordsystem()
                self.readImECO.source_system = targ_system
                self.browseUS(fileObj=None, use_dialog=False)
                self.changedTab()
        elif ind_image==1:
            if not hasattr(self, 'readImMRI'):
                return
            if not hasattr(self.readImMRI, 'im'):
                return
            status = self.readImMRI._changeCoordSystem(targ_system)
            if status:
                self.setCurrentCoordsystem()
                self.browseMRI(fileObj=None, use_dialog=False)
                self.changedTab()

    def maskingClose(self, val):
        """
        Clear information from masking
        :param val:
        :return:
        """
        if val==4:
            self.BET.clear()
        elif val==5:
            self.BE_DL.clear()
            for ind in range(2):
                save_var = '_immri_bedl_{}'.format(ind)
                save_var_seg = '_immri_bedl_seg_{}'.format(ind)
                setattr(self, save_var, None)
                setattr(self, save_var_seg, None)
        elif val==10:
            self.Tissue_Seg.clear()
        self.setEnabled(True)




    def reconstruction(self, reconstruct, ind, reader, alg):
        if reconstruct:
            save_var = '_immri_bedl_{}'.format(ind)
            save_var_seg = '_immri_bedl_seg_{}'.format(ind)
            if not hasattr(self, save_var):#[::-1, ::-1, ::-1].transpose(2, 1, 0)
                setattr(self, save_var,
                        reader.im.__class__(reader.im.dataobj[:], reader.im.affine, reader.im.header))
                setattr(self, save_var_seg, reader.npSeg)
            elif getattr(self, save_var) is None:
                    setattr(self, save_var,
                                    reader.im.__class__(reader.im.dataobj[:], reader.im.affine, reader.im.header))
                    setattr(self, save_var_seg, reader.npSeg)
            reader.im = alg.im_rec
            reader.set_metadata()
            reader.read_pars(reset_seg=False)
        else:
            save_var = '_immri_bedl_{}'.format(ind)
            save_var_seg = '_immri_bedl_seg_{}'.format(ind)
            if not hasattr(self, save_var):
                return
            # reader.im = self._immri_tmp
            if getattr(self, save_var) is None:
                return
            reader.im = getattr(self, save_var)
            reader.set_metadata()
            reader.read_pars(adjust_for_show=True)
            self.setNewImage2.emit(reader.npImage.shape)
            reader.npSeg = getattr(self, save_var_seg)#[::-1, ::-1, ::-1].transpose(2, 1, 0)
            delattr(self, save_var_seg)
            delattr(self, save_var)






    def Thresholding(self, val, reconstruct=False):


        """
        Brain extraction related
        :param val:
        :return:
        """

        at_eco = hasattr(self, 'readImECO')
        at_mri = hasattr(self, 'readImMRI')

        if val=='BET' or val=='Deep BET' or val=='histeq' or val=='Segmentation':
            if val=='BET':
                alg = self.BET
            elif val == 'histeq':
                alg = self.ImageThresholding
            elif val=='Deep BET':
                alg = self.BE_DL
            elif val=='Segmentation':
                alg = self.Tissue_Seg
            ind = alg.comboBox_image.currentIndex()
            if ind == 0 and at_eco:
                if hasattr(self.readImECO, 'npImage'):
                    if val != 'histeq':
                        self.readImECO.npSeg = alg.mask.transpose(2, 1, 0)[::-1, ::-1, ::-1]
                    if hasattr(alg,'im_rec'):
                        reader = self.readImECO
                        if alg.im_rec is not None:
                            if not hasattr(alg.im_rec, 'get_fdata'):
                                from melage.utils.utils import make_image
                                alg.im_rec = make_image(alg.im_rec, reader.im)
                            self.reconstruction(reconstruct, ind, reader, alg)
                            if val == 'histeq' and not reconstruct:
                                alg.plot(self.readImECO.npImage)
                    if self.readImECO.npImage is not None:
                        self.updateDispEco(self.readImECO.npImage, self.readImECO.npSeg, initialState=True)
                    #self.BET.clear()
            elif ind == 1 and at_mri:
                if hasattr(self.readImMRI, 'npImage'):
                    if val != 'histeq':
                        self.readImMRI.npSeg = alg.mask
                    if hasattr(alg,'im_rec'):
                        reader = self.readImMRI
                        if alg.im_rec is not None:
                            if not hasattr(alg.im_rec, 'get_fdata'):
                                from melage.utils.utils import make_image
                                alg.im_rec = make_image(alg.im_rec, reader.im)
                            self.reconstruction(reconstruct, ind, reader, alg)
                            if val == 'histeq' and not reconstruct:
                                alg.plot(self.readImMRI.npImage)
                    if self.readImMRI.npImage is not None:
                        self.updateDispMRI(self.readImMRI.npImage, self.readImMRI.npSeg, initialState=True)
                    #self.BET.clear()
            return

        ind = self.ImageThresholding.comboBox_image.currentIndex()

        if val == 'apply':
            if hasattr(self.ImageThresholding,'_currentThresholds'):
                from melage.utils.utils import apply_thresholding
                ind = self.ImageThresholding.comboBox_image.currentIndex()
                if ind == 0 and at_eco:
                    if hasattr(self.readImECO, 'npImage'):
                        self.readImECO.npSeg = apply_thresholding(self.readImECO.npImage, self.ImageThresholding._currentThresholds)
                        self.updateDispEco(self.readImECO.npImage, self.readImECO.npSeg, initialState=True)
                elif ind == 1 and at_mri:
                    if hasattr(self.readImMRI, 'npImage'):
                        self.readImMRI.npSeg = apply_thresholding(self.readImMRI.npImage, self.ImageThresholding._currentThresholds)
                        self.updateDispMRI(self.readImMRI.npImage, self.readImMRI.npSeg, initialState=True)
        elif val=='replot':

            repl = False
            if ind==0:

                if at_eco:
                    at_im_eco = hasattr(self.readImECO, 'npImage')
                    if at_im_eco:
                        self.ImageThresholding.plot(self.readImECO.npImage)
                        repl = True
            else:

                if at_mri:
                    at_im_mri = hasattr(self.readImMRI, 'npImage')
                    if at_im_mri:
                        self.ImageThresholding.plot(self.readImMRI.npImage)
                        repl = True
            if not repl:
                self.ImageThresholding.emptyPlot()

    def registerShow(self, val=1):
        """
        Image to Image registration widget
        :param val: the parameter that defines type of operation (transformation or registration)
        :return:
        """
        self.setEnabled(False)

        if val == 0:
            el = self.registrationD
            at_eco = hasattr(self, 'readImECO')
            at_mri = hasattr(self, 'readImMRI')
            if at_eco and at_mri:
                at_im_eco = hasattr(self.readImECO, 'npImage')
                at_im_mri = hasattr(self.readImMRI, 'npImage')
                if not at_im_eco and at_im_mri and val in [0, 1, 2, 3, 6, 7, 8, 9]:
                    el.comboBox_image.setCurrentIndex(1)
        elif val == 1:
            el = self.transformationD
        el.setEnabled(True)
        el.show()

    def maskingShow(self, val=1):
        """
        Show different widget according to the define parameter val
        :param val:
        :return:
        """
        self.setEnabled(False)
        if val == 0:
            el = self.Masking
        elif val == 1:
            el = self.MaskingOperations
        elif val == 2:
            el = self.ChCoordSys
        elif val==3:
            el = self.N4_dialog
        elif val == 4:
            el = self.HistImage
        elif val == 5:
            el = self.iminfo_dialog

            try:
                for i, widg in enumerate([self.readImECO, self.readImMRI]):
                    el.set_tag_value(widg, ind=i)
            except:
                pass

        elif val == 6:
            el = self.ImageThresholding
        elif val == 7:
            el = self.BET
        elif val == 8:
            el = self.resizeImage
            el.label_warning.setText('Image Resizing (isotropic)?')
        elif val == 9:
            el = self.BE_DL
            self.setEnabled(True)
        elif val==10:
            el = self.Tissue_Seg
            self.setEnabled(True)
        try:
            at_eco = hasattr(self, 'readImECO')
            at_mri = hasattr(self, 'readImMRI')

            if val in [0, 1, 2, 3, 6, 7, 8, 9, 10, 11, 12]:
                if at_mri and hasattr(self.readImMRI, 'npImage'):
                    el.comboBox_image.setCurrentIndex(1)
                    if hasattr(el, 'comboBox_image_type'):
                        el.comboBox_image_type.setCurrentIndex(1)
                    if val == 7:
                        self.BET.setData(self.readImMRI.npImage, self.readImMRI.ImSpacing)
                        self.BE_DL.comboBox_image.setCurrentIndex(1)
                        self.updateDataBEDL(index=0)
                    elif val in [9, 10]:
                        from melage.utils.utils import make_image_using_affine
                        affine = getattr(self.readImMRI, 'affine', None)
                        header = getattr(self.readImMRI, 'header', None)
                        img = make_image_using_affine(self.readImMRI.npImage, affine, header)
                        el.setData(img, self.readImMRI.ImSpacing)
                        el.comboBox_image.setCurrentIndex(1)

                elif at_eco and hasattr(self.readImECO, 'npImage'):
                    if val == 7:
                        self.BET.setData(self.readImECO.npImage, self.readImECO.ImSpacing)
                    elif val in [9, 10]:
                        from melage.utils.utils import make_image_using_affine
                        affine = getattr(self.readImECO, 'affine', None)
                        header = getattr(self.readImECO, 'header', None)
                        img = make_image_using_affine(self.readImECO.npImage, affine, header)
                        el.setData(img, self.readImECO.ImSpacing)
                        el.comboBox_image.setCurrentIndex(0)

            if val == 6:
                index = el.comboBox_image.currentIndex()
                if index == 0 and at_eco:
                    el.plot(self.readImECO.npImage)
                elif index == 1 and at_mri:
                    el.plot(self.readImMRI.npImage)

            elif val in [4, 5]:
                name_mri = self.filenameMRI if at_mri else None
                name_eco = self.filenameEco if at_eco else None
                if val == 4:
                    if at_mri:
                        el.plot(self.readImMRI.npImage, 1)
                    if at_eco:
                        el.plot(self.readImECO.npImage, 2)
                el.UpdateName(name_eco,name_mri)

            elif val == 8:
                ind = el.comboBox_image.currentIndex()
                self.resize_image(None, ind)

            if val in [0, 1]:
                el.setComboBoxColors(self.color_name)
            elif val == 2:
                self.setCurrentCoordsystem()


            el.setEnabled(True)
            el.show()
        except Exception as e:
            self.setEnabled(True)
            print(e)

    def _cutIM(self, _cutIM):
        """
        Cut image based on a defined limits
        :param _cutIM:
        :return:
        """
        sender = QtCore.QObject.sender(self)
        nameS = 'horizontalSlider_'
        totalvalues = []
        if sender.id in [1,2,3]:
            slider_list = [3, 1, 2]
        elif sender.id in [4,5,6]:
            slider_list = [6,4,5]
        for i in slider_list:
            slider = getattr(self, nameS + str(i))
            totalvalues.append([slider._first, slider._second])

        shp = self.readImECO.im.shape
        sortedT = [sorted(i) for i in totalvalues]
        for i , el in enumerate(sortedT):
            if el[0]<=0:
                el[0]=0
            if el[1]>=shp[i] or el[1]==0:
                el[1]=shp[i]
        im = self.readImECO.im.get_fdata()
        im = im[sortedT[0][0]:sortedT[0][1], sortedT[0][0]:sortedT[1][1], sortedT[2][0]:sortedT[2][1]]
        from melage.utils.utils import make_image
        im = make_image(im, self.readImECO.im)
        self.readImECO.im = im

        self.readImECO.changeData(type='eco', imchange=True, state=False, axis=[0,1,2])
        self.browseUS(fileObj=None, use_dialog=False)
        #self.updateDispEco(self.readImECO.npImage, self.readImECO.npSeg, initialState=True)

    def changeVolume(self):
        """
        Change image volume in 4D images
        :return:
        """
        value = self.actionComboBox.objectName()
        if value=='View2' and hasattr(self, 'readImMRI'):
            self.browseMRI(use_dialog=False)
        elif value=='View1' and hasattr(self, 'readImECO'):
            self.browseUS(use_dialog=False)


    def color_picker(self):
        """
        Pick a color
        :return:
        """
        from melage.utils.utils import addTreeRoot
        colordialog = QtWidgets.QColorDialog(self.newdialog)
        color = colordialog.getColor()
        if self.newdialog.exec_() == QFileDialogPreview.Accepted:
            newindex = self.newdialog.lineEdit.text()
            newText = self.newdialog.lineEdit2.text()
            root = self.tree_colors.model().sourceModel().invisibleRootItem()
            similar_items = []
            for l in range(root.rowCount()):
                signal = root.child(l)
                if signal.text()==newindex:
                    similar_items.append(signal)
            #    self.tree_colors.invisibleRootItemi().child(l)
            if len(similar_items)>0:
                qm = QtWidgets.QMessageBox(self.newdialog)
                ret = qm.question(self.newdialog, '', "Do you want to override the color?", qm.Yes | qm.No)
                if ret == qm.Yes:
                    for l in similar_items:
                        root.removeRow(l.row())
                else:
                    return
            from melage.utils.utils import add_new_tree_widget
            color_rgb = [l / 255.0 for l in color.getRgb()]
            add_new_tree_widget(self, newindex, newText, color_rgb)
            #parent.setCheckState(True,QtCore.Qt.CheckState())
        #self.styleChoice.setStyleSheet("QWidget { background-color: %s}" % color.name())



    def CalcTotalVolume(self, segwnd='sagital'):
        """
        Calculate region volume
        :param segwnd:
        :return:
        """
        from melage.utils.utils import compute_vol_seg

        widgets = select_proper_widgets(self)
        sender = QtCore.QObject.sender(self)
        try:
            #sender_ind = widgets.index(sender)
            if rhasattr(self, 'readImECO.npSeg'):
                sender_ind = 1
            elif rhasattr(self, 'readImMRI.npSeg'):
                sender_ind = 5

            reader = self.readImECO if sender_ind < 3 else self.readImMRI
            self.dockWidget_3.setVisible(True)
            self.setEnabled(False)
            self.progressBarSaving.setValue(20)
            selected_points_total = compute_vol_seg(reader.npSeg, segwnd)
            if sender_ind < 3:
                self.updateSegmentation(selected_points_total, 'ECO_'+segwnd, self.openGLWidget_1.colorInd, self.openGLWidget_1.sliceNum)
            else:
                self.updateSegmentation(selected_points_total, 'MRI_'+segwnd, self.openGLWidget_3.colorInd, self.openGLWidget_3.sliceNum)
            self.progressBarSaving.setValue(80)
            selected_points_total = []
            #if sender_ind < 3 and sender_ind != 11:
            #    self.openedFileName.setText(
             #   'File: {}, TV: {}'.format(self.filenameEco,
             #                             Seg_new.sum() * self.readImECO.ImSpacing[0]**3))
            #else:
            #    self.openedFileName.setText(
            #    'File: {}, TV: {}'.format(self.filenameMRI,
            #                              Seg_new.sum() * self.readImMRI.ImSpacing[0]**3))
            self.progressBarSaving.setValue(100)
            self.setEnabled(True)
            self.dockWidget_3.setVisible(False)
        except Exception as e:
            print('Calculate Total Volume')
            print(e)




    def activateAxisLines(self, val):
        """
        show axis values
        :param val: boolean
        :return:
        """
        widgets = [self.openGLWidget_4, self.openGLWidget_5, self.openGLWidget_6, self.openGLWidget_11, self.openGLWidget_1, self.openGLWidget_2, self.openGLWidget_3, self.openGLWidget_12]

        for widget in widgets:
            widget.showAxis = val
            widget.update()

    def Zoom(self, val):
        """
        Zoomming operation
        :param val:
        :return:
        """
        if self.tabWidget.currentIndex() == 0:
            widgets_mri = [self.openGLWidget_4, self.openGLWidget_5, self.openGLWidget_6]
            widgets_eco = [self.openGLWidget_1, self.openGLWidget_2, self.openGLWidget_3]
            widgets = widgets_mri + widgets_eco
        elif self.tabWidget.currentIndex() == 2:
            widgets = [self.openGLWidget_11]
        elif self.tabWidget.currentIndex() == 3:
            widgets = [self.openGLWidget_12]
        else:
            widgets = []

        if val=='In':
            for widget in widgets:
                if widget.isVisible():
                    widget.scaleF = widget.ZOOM_OUT_FACTOR
                    if 0.0 < widget.zoom_level_y * widget.scaleF < 5 or 0.0 < widget.zoom_level_x * widget.scaleF < 5:
                        widget.updateScale(0, 0, widget.scaleF, widget.scaleF)
        elif val == 'Out':
            for widget in widgets:
                if widget.isVisible():
                    widget.scaleF = widget.ZOOM_IN_FACTOR
                    if 0.0 < widget.zoom_level_y * widget.scaleF < 5 or 0.0 < widget.zoom_level_x * widget.scaleF < 5:
                        widget.updateScale(0, 0, widget.scaleF, widget.scaleF)
    def activate3d(self, val):
        """
        Activate 3D show
        :param val:
        :return:
        """
        widgets = [self.openGLWidget_14, self.openGLWidget_24]
        if val:
            self.action3D.setIcon(self._icon_3d)
            for widget in widgets:
                widget.setVisible(True)
            self.label_points_2.setVisible(True)
            self.label_points.setVisible(True)

        else:
            self.action3D.setIcon(self._icon_3dFaded)
            self.label_points_2.setVisible(False)
            self.label_points.setVisible(False)

            for widget in widgets:
                widget.setVisible(False)
                #widget.setMaximumSize(QtCore.QSize(width_3d, self.height() - self.height() / 3))

    def activateGuidelines(self, val):
        """
        Activate guidelines
        :param val:
        :return:
        """
        #widgets = select_proper_widgets(self)
        widgets = [self.openGLWidget_4, self.openGLWidget_5, self.openGLWidget_6, self.openGLWidget_11, self.openGLWidget_1, self.openGLWidget_2, self.openGLWidget_3, self.openGLWidget_12]
        self._last_state_guide_lines = val
        if val:
            for widget in widgets:
                widget.enabledGoTo = True
            self.actionGoTo.setIcon(self._icon_goto)
        else:
            for widget in widgets:
                widget.guidelines_v = []
                widget.guidelines_h = []
                widget.enabledGoTo = False
                widget.makeObject()
                widget.update()
            self.actionGoTo.setIcon(self._icon_gotoFaded)

    def Interpolate(self, params):
        """
        Interpolation
        :param params:
        :return:
        """
        [sliceNum, currentWidnowName, apply_interp, WI_index] = params

        if currentWidnowName=='sagittal':
            slices = [sl[0] for sl in self._slice_interp[0]]
            if sliceNum in slices:
                index = slices.index(sliceNum)
                self._slice_interp[0].pop(index)
            self._slice_interp[0].append([sliceNum, WI_index])
        elif currentWidnowName == 'axial':
            slices = [sl[0] for sl in self._slice_interp[1]]
            if sliceNum in slices:
                index = slices.index(sliceNum)
                self._slice_interp[1].pop(index)
            self._slice_interp[1].append([sliceNum, WI_index])
        elif currentWidnowName == 'coronal':
            slices = [sl[0] for sl in self._slice_interp[2]]
            if sliceNum in slices:
                index = slices.index(sliceNum)
                self._slice_interp[2].pop(index)
            self._slice_interp[2].append([sliceNum, WI_index])

        if not apply_interp:
            return
        from melage.utils.utils import slice_intepolation
        sender = QtCore.QObject.sender(self)
        if sender.id in [1,2,3,11]:
            reader = self.readImECO
        elif sender.id in [4,5,6,12]:
            reader = self.readImMRI
        if currentWidnowName == 'sagittal':
            slicesWI = self._slice_interp[0]
            if len(slicesWI) < 2:
                return
            slices = [sl[0] for sl in slicesWI]
            WI = [sl[1] for sl in slicesWI]
            self.app.processEvents()
            whiteInd=  slice_intepolation(reader, slices, currentWidnowName, sender.colorInd, WI)
            self.updateSegmentation(whiteInd, currentWidnowName, sender.colorInd, sender.sliceNum)
            self._slice_interp[0] = []
        elif currentWidnowName == 'axial':
            slicesWI = self._slice_interp[1]
            if len(slicesWI) < 2:
                return
            slices = [sl[0] for sl in slicesWI]
            WI = [sl[1] for sl in slicesWI]
            self.app.processEvents()
            whiteInd= slice_intepolation(reader, slices, currentWidnowName, sender.colorInd, WI)
            self.updateSegmentation(whiteInd, currentWidnowName, sender.colorInd, sender.sliceNum)
            self._slice_interp[1] = []
        elif currentWidnowName == 'coronal':
            slicesWI = self._slice_interp[2]
            if len(slicesWI) < 2:
                return
            slices = [sl[0] for sl in slicesWI]
            WI = [sl[1] for sl in slicesWI]
            if len(slices) < 2:
                return
            self.app.processEvents()
            whiteInd= slice_intepolation(reader, slices, currentWidnowName, sender.colorInd, WI)
            self.updateSegmentation(whiteInd, currentWidnowName, sender.colorInd, sender.sliceNum)
            self._slice_interp[2] = []


    def updateLP(self, params):
        """
        lp: line points
        :return:
        """
        lp, colorInd, empty, gen_contour = params
        if empty:
            from melage.utils.utils import locateWidgets
            self.linePoints = []
            self._lineinfo= []
            readerName, reader, widgets = locateWidgets(self._lastChangedWidgest[0], self)
            if hasattr(self, '_colorInd'):
                reader.npSeg[reader.npSeg == 1500] = 0

                for widget in widgets:
                    setSliceSeg(widget, reader.npSeg)
                    if widget == self.openGLWidget_11:
                        self.openGLWidget_14.paint(reader.npSeg, reader.npImage, widget.currentWidnowName,
                                                   widget.sliceNum)
                    elif widget == self.openGLWidget_12:
                        self.openGLWidget_24.paint(reader.npSeg, reader.npImage, widget.currentWidnowName,
                                                   widget.sliceNum)
                    widget.makeObject()
                    widget.update()

                #removeLastLines(self._lastlines, reader.npSeg, self._colorInd)
                self._lastlines = []
            return
        elif gen_contour:
            self.GenerateContour()
            return
        self.linePoints.append(lp[0])
        self.linePoints.append(lp[1])
        self._colorInd = colorInd


    def removeTableMeasureItem(self, index):
        """
        remove items from measurement table
        :param index:
        :return:
        """
        def find_current_line_number():
            _num_measure = max(self.num_measure_length, self.num_measure_area)
            for i in range(_num_measure):
                if self.table_widget_measure.item(i,0).text() == '' or self.table_widget_measure.item(i,1).text()== '':
                    self.num_measure_length = i
                    self.num_measure_area = i
                    break

            for i in range(self.table_widget_measure.rowCount()):
                if i >= self.num_measure_length:
                    self.table_widget_measure.removeRow(i)

        try:
            selectedRows = [i.row() for i in self.table_widget_measure.selectedIndexes()]
            selectedColumns = [i.column() for i in self.table_widget_measure.selectedIndexes()]
            for row, column in zip(selectedRows, selectedColumns):
                newitem = QtWidgets.QTableWidgetItem()
                self.table_widget_measure.setItem(row, column, newitem)
            #for item in self.table_widget_measure.selectedItems():
            #    newitem = QtWidgets.QTableWidgetItem()
            #    self.table_widget_measure.setItem(item.row(), item.column(), newitem)
            find_current_line_number()
        except Exception as e:
            print('Measure Table Item')
            pass




    def removeTableItem(self, index):
        """
        remove item from table
        :param index:
        :return:
        """
        if self._points_adapt_mri:
            selectedRows = []

            selectedRows = [i.row() for i in self.table_widget.selectedIndexes()]
            for ij in selectedRows:

                self.updateSegmentation(self._points_adapt_mri[ij], 'MRI', 0, 0)
                self.updateSegmentation(self._points_adapt_eco[ij], 'ECO', 0, 0)
                #self._points_adapt_mri.pop(index)
                #self._points_adapt_eco.pop(index)
                #selectedRow = self.table_widget.currentRow()
                self._num_adapted_points -=1
                index = self.table_widget.selectedIndexes()[0].row()
                self.table_widget.removeRow(index)
                self.table_widget.setRowCount(25)
            self._points_adapt_mri = [i for n, i in enumerate(self._points_adapt_mri) if n not in selectedRows]
            self._points_adapt_eco = [i for n, i in enumerate(self._points_adapt_eco) if n not in selectedRows]


        #self.table_widget.setItem(self._num_adapted_points, 0, QtWidgets.QTableWidgetItem(str(whiteInd[0])))

    def linkMRIECO(self):
        """
        Lkinking MRI and US images
        :return:
        """
        from melage.utils.utils import LinkMRI_ECO
        if len(self._points_adapt_mri)>=3:
            self.linked_models = LinkMRI_ECO(self._points_adapt_mri, self._points_adapt_eco)

    def linkBoth(self, value):
        """
        Linking both images
        :param value:
        :return:
        """
        if self.linked_models is not None:
            if value:
                self.linked = True
                self.table_link.setText(self._translate("Main", "Linked"))
            else:
                self.linked = False
                self.table_link.setText(self._translate("Main", "Link"))
        else:
            self.table_link.setChecked(False)




    def updateSliceNumber(self, val):
        """
        Updating slice number
        :param val:
        :return:
        """
        sender = QtCore.QObject.sender(self)
        name = 'openGLWidget_'
        nameS = 'horizontalSlider_'
        for i in range(12):
            nameWidget = name + str(i + 1)
            widget = getattr(self, nameWidget)
            if sender == widget:
                slider = getattr(self, nameS + str(i + 1))
                if val <=slider.maximum():
                    slider.setValue(val)



    def updateSegPlanes(self, val, windowName, imtype):
        """
        Go to a segmentation plane according to 3D point location
        :param val:
        :param windowName:
        :return:
        """
        from melage.utils.utils import generate_extrapoint_on_line
        name = 'openGLWidget_'
        nameS = 'horizontalSlider_'
        if windowName is None:
            if imtype == 'eco':
                i = 11
            elif imtype == 'mri':
                i = 12
            else:
                return
            nameWidget = name + str(i)
            widget = getattr(self, nameWidget)
            if widget.isVisible():
                widget.guidelines_h = []
                widget.guidelines_v = []
            widget.makeObject()
            widget.update()
            return

        vals = [int(v) for v in val]

        widgets = select_proper_widgets(self)
        if widgets[0].imType== 'eco':
            shapes = self.readImECO.npImage.shape
        else:
            shapes = self.readImMRI.npImage.shape

        if windowName == 'coronal':
            val = [vals[2], vals[0], vals[1]]
            line_h = generate_extrapoint_on_line([0,val[0]], [shapes[2],val[0]], val[2])
            line_v = generate_extrapoint_on_line([val[1],0], [val[1],shapes[0]], val[2])
        elif windowName == 'sagittal':
            val = [vals[0], vals[1], vals[2]]
            line_h = generate_extrapoint_on_line([0,val[2]], [shapes[1],val[2]], val[0])
            line_v = generate_extrapoint_on_line([val[1],0], [val[1],shapes[0]], val[0])

        elif windowName == 'axial':
            val = [vals[2], vals[0], vals[1]]
            line_h = generate_extrapoint_on_line([0,val[2]], [shapes[2],val[2]], val[1])
            line_v = generate_extrapoint_on_line([val[1],0], [val[1],shapes[1]], val[0])
        else:
            return



        if imtype=='eco':
            i = 11
        elif imtype== 'mri':
            i = 12
        else:
            return
        if windowName=='coronal':
            v = vals[1]
            self.changeToCoronal(imtype)
        elif windowName == 'axial':
            v = vals[2]
            self.changeToAxial(imtype)
        elif windowName == 'sagittal':
            v = vals[0]
            self.changeToSagittal(imtype)


        nameWidget = name + str(i)
        widget = getattr(self, nameWidget)
        if widget.isVisible():
            windowName = widget.currentWidnowName
            #widget.enabledGoTo= True
            widget.guidelines_h = line_h
            widget.guidelines_v = line_v
            widget.makeObject()
            widget.update()
            slider = getattr(self, nameS + str(i))
            slider.setValue(v)


    def updateAllSlices(self, val, windowName):
        """
        Updating all slices
        :param val:
        :param windowName:
        :return:
        """
        from melage.utils.utils import generate_extrapoint_on_line

        val = [int(v) for v in val]
        line_sagittal_h = []
        line_axial_h = []
        line_coronal_h = []
        line_sagittal_v = []
        line_axial_v = []
        line_coronal_v = []
        widgets = select_proper_widgets(self)
        if widgets[0].imType== 'eco':
            shapes = self.readImECO.npImage.shape
        else:
            shapes = self.readImMRI.npImage.shape

        if windowName[0] == 'coronal':
            val = [val[2], val[0], val[1]]
            line_sagittal_h = generate_extrapoint_on_line([0,val[2]], [shapes[1],val[2]], val[1])
            line_sagittal_v = generate_extrapoint_on_line([val[0],0], [val[0],shapes[0]], val[1])

            line_axial_v = generate_extrapoint_on_line([val[1],0], [val[1],shapes[1]], val[2])
            line_axial_h = generate_extrapoint_on_line([0,val[0]], [shapes[2],val[0]], val[2])
        elif windowName[0] == 'sagittal':
            val = [val[0], val[2], val[1]]
            line_coronal_h = generate_extrapoint_on_line([0,val[2]], [shapes[2],val[2]], val[0])
            line_coronal_v = generate_extrapoint_on_line([val[1],0], [val[1],shapes[0]], val[0])

            line_axial_h = generate_extrapoint_on_line([0,val[0]], [shapes[2],val[0]], val[2])
            line_axial_v = generate_extrapoint_on_line([val[1],0], [val[1],shapes[1]], val[2])

        elif windowName[0] == 'axial':
            val = [val[1], val[0], val[2]]
            line_coronal_v = generate_extrapoint_on_line([val[1],0], [val[1],shapes[0]], val[0])
            line_coronal_h = generate_extrapoint_on_line([0,val[2]], [shapes[2],val[2]], val[0])

            line_sagittal_v = generate_extrapoint_on_line([val[0],0], [val[0],shapes[0]], val[1])
            line_sagittal_h = generate_extrapoint_on_line([0,val[2]], [shapes[1],val[2]], val[1])#shapes[2] to shapes[1]
        name = 'openGLWidget_'
        nameS = 'horizontalSlider_'

        if windowName[1]=='eco':
            for i, v in zip(range(3), val):
                nameWidget = name + str(i + 1)
                widget = getattr(self, nameWidget)
                if widget.isVisible():
                    windowName = widget.currentWidnowName
                    if windowName == 'axial':
                        widget.guidelines_h = line_axial_h
                        widget.guidelines_v = line_axial_v
                        widget.makeObject()
                        widget.update()
                    elif windowName == 'sagittal':
                        widget.guidelines_h = line_sagittal_h
                        widget.guidelines_v = line_sagittal_v
                        widget.makeObject()
                        widget.update()
                    elif windowName == 'coronal':
                        widget.guidelines_h = line_coronal_h
                        widget.guidelines_v = line_coronal_v
                        widget.makeObject()
                        widget.update()
                    slider = getattr(self, nameS + str(i + 1))
                    slider.setValue(v)
        elif windowName[1]=='mri':
            for i, v in zip(range(3), val):
                nameWidget = name + str(i + 1+3)
                widget = getattr(self, nameWidget)
                if widget.isVisible():
                    windowName = widget.currentWidnowName
                    if windowName == 'axial':
                        widget.guidelines_h = line_axial_h
                        widget.guidelines_v = line_axial_v
                        widget.makeObject()
                        widget.update()
                    elif windowName == 'sagittal':
                        widget.guidelines_h = line_sagittal_h
                        widget.guidelines_v = line_sagittal_v
                        widget.makeObject()
                        widget.update()
                    elif windowName == 'coronal':
                        widget.guidelines_h = line_coronal_h
                        widget.guidelines_v = line_coronal_v
                        widget.makeObject()
                        widget.update()
                    slider = getattr(self, nameS + str(i + 1 + 3))
                    slider.setValue(v)


    def _setFadedPix(self, val):
        """
        Fading icons
        :param val:
        :return:
        """
        self.actionContour.setIcon(self._icon_contourFaded)
        self.actionPoints.setIcon(self._icon_pointsFaded)
        self.actionCircles.setIcon(self._icon_CircleFaded)
        #self.actionGoTo.setIcon(self._icon_gotoFaded)
        self.actionContourX.setIcon(self._icon_contourXFaded)
        self.actionEraseX.setIcon(self._icon_eraseXFaded)
        self.actionArrow.setIcon(self._icon_arrowFaded)
        self.actionPaint.setIcon(self._icon_pencilFaded)
        self.actionPan.setIcon(self._icon_Hand_IXFaded)
        self.actionErase.setIcon(self._icon_EraserFaded)
        self.actionRuler.setIcon(self._icon_rulerFaded)
        #self.dock_widget_table.setVisible(False)
        #self.dock_widget_measure.setVisible(False)
        self.main_toolbox.setCurrentIndex(0)

        if self._Xtimes == 1:

            if val == 0:
                self.actionArrow.setIcon(self._icon_arrow)
            elif val == 1:
                self.actionPaint.setIcon(self._icon_pencil)
                self.main_toolbox.setCurrentIndex(5)
            elif val == 2:
                self.actionPan.setIcon(self._icon_Hand_IX)
            elif val == 3:

                self.actionErase.setIcon(self._icon_Eraser)
            elif val == 4:
                self.actionContour.setIcon(self._icon_contour)
            elif val == 5:
                self.actionPoints.setIcon(self._icon_pointsFaded)
                #self.dock_widget_table.setVisible(True)
                self.changedTab()
            elif val == 6:
                self.actionRuler.setIcon(self._icon_ruler)
                #self.dock_widget_measure.setVisible(True)
            elif val == 7:
                self.actionGoTo.setIcon(self._icon_goto)
            elif val==9:
                self.actionCircles.setIcon(self._icon_CircleFaded)
                self.main_toolbox.setCurrentIndex(5)


        else:
            if val == 4:
                self.actionContourX.setIcon(self._icon_contourX)
            elif val == 3:
                self.actionEraseX.setIcon(self._icon_eraseX)

    def setCursorsX(self, val):
        """
        Selecting correct cursor with repetition
        :param val:
        :return:
        """
        guide_lines = self.actionGoTo.isChecked()
        if val == 3:
            guide_lines = False
        #if val == 5:
        #    self._num_adapted_points = 0
        #else:
            #self._points_adapt_eco = []
            #self._points_adapt_mri = []
            #self.table_widget.clear()

        #icon = QtGui.QIcon()
        #icon.addPixmap(QtGui.QPixmap(source_folder+"/contourX.png"), QtGui.QIcon.Selected, QtGui.QIcon.On)
        if abs(self._Xtimes) >1:
            self._setFadedPix(val)

            for k in range(12):
                name = 'openGLWidget_' + str(k + 1)
                widget = getattr(self, name)

                if widget.isVisible():
                    widget.enabledGoTo = guide_lines
                    setCursorWidget(widget, val, abs(self._Xtimes))


    def setCursors(self, val, rad_circle=None):

        """
        Selecting correct cursor
        :param val:
        :param rad_circle:
        :return:
        """
        manual_set = False
        self._Xtimes = 1
        if rad_circle is None and val==9:#circle
            self.dw2_s1.setValue(200)
            #rad_circle = self._rad_circle_dot
            manual_set = True
        self._setFadedPix(val)
        if val == 7:
            self.action_guideLines.setChecked(True)
        guide_lines = self.actionGoTo.isChecked()
        if val == 3:
            guide_lines = False

        #if val == 5:
        #    self._num_adapted_points = 0
        #else:
         #   self._points_adapt_eco = []
         #   self._points_adapt_mri = []
         #   self.table_widget.clear()
        #if val == 9:
            #try:
            #    self.actionCircles.triggered.connect(partial(self.setCursors, val, self._rad_circle))
            #except:
            #    pass
        for k in range(12):
            name = 'openGLWidget_' + str(k + 1)
            widget = getattr(self, name)
            if widget.isVisible():
                #if val==9:
                    #widget._radius_circle = rad_circle
                widget.enabledGoTo = guide_lines
                if val == 1:
                    self.dw2_s1.setValue(8)
                if manual_set:
                    widget._radius_circle = self._rad_circle*abs(widget.to_real_world( 1, 0)[0] - widget.to_real_world(0, 0)[0])
                    #rad_circle = self._rad_circle
                    self.changeRadiusCircle(None)
                else:
                    setCursorWidget(widget, val, abs(self._Xtimes), self._rad_circle)


    def update3Dview(self, map_type, reset,  typew='eco'):
        if typew == 'eco':
            if not hasattr(self, 'readImECO') or not hasattr(self.readImECO, 'npImage'):
                return  # Return if npImage or npSeg does not exist for ECO
        else:
            if not hasattr(self, 'readImMRI') or not hasattr(self.readImMRI, 'npImage'):
                return  # Return if npImage or npSeg does not exist for MRI


        if reset is None:
            if typew=='eco':
                self.openGLWidget_14.paint(self.readImECO.npSeg, self.readImECO.npImage, None)
            else:
                self.openGLWidget_24.paint(self.readImMRI.npSeg, self.readImMRI.npImage, None)
        else:
            if typew == 'eco':
                self.openGLWidget_14.cmap_image(self.readImECO.npImage, map_type, reset)
            else:
                self.openGLWidget_24.cmap_image(self.readImMRI.npImage, map_type, reset)




    def updateLabelPs(self, pos3d, windowName, typew='eco'):
        """
        Updating label points
        :param pos3d:
        :param windowName:
        :param typew:
        :return:
        """
        if type(pos3d)==list:

            pos3d[1] = pos3d[1] % 360
            if typew == 'eco':
                txt = 'El:' + str_conv(pos3d[0]) + ', Az: ' + str_conv(pos3d[1]) + ', Dis: ' + str_conv(pos3d[2])
                self.label_points.setText(txt)
            elif typew == 'mri':
                txt = 'El:' + str_conv(pos3d[0]) + ', Az: ' + str_conv(pos3d[1]) + ', Dis: ' + str_conv(pos3d[2])
                self.label_points_2.setText(txt)

        else:

            if any(pos3d < -1) or pos3d.max()> 2000:
                return

            if typew== 'eco':
                txt = 'S:' + str_conv(pos3d[0]) + ', C: '+ str_conv(pos3d[1])+', A: '+ str_conv(pos3d[2])
                self.label_points.setText(txt)
                self.updateSegPlanes(pos3d, windowName, 'eco')
            elif typew == 'mri':
                txt = 'S:' + str_conv(pos3d[0]) + ', C: '+ str_conv(pos3d[1])+', A: '+ str_conv(pos3d[2])
                self.label_points_2.setText(txt)

                self.updateSegPlanes(pos3d, windowName, 'mri')
        if not self.label_points_2.isVisible():
            self.label_points_2.setVisible(True)
            self.label_points.setVisible(True)


    def updateSegmentation(self, whiteInd, currentWidnowName, colorInd, sliceNum):
        """
        Updating segmentation
        :param whiteInd:
        :param currentWidnowName:
        :param colorInd:
        :param sliceNum:
        :return:
        """
        from melage.utils.utils import repetition, destacked

        #whiteInd, edges = whiteIndEdges
        def updateWidget(widget, reader, whiteInd, colorInd):
            try:
                #reader.npSeg[tu
                # ple(zip(*whiteInd))] = colorInd
                update_last(self, reader.npSeg, colorInd, whiteInd, widget.colorInd)
                setSliceSeg(widget, reader.npSeg)
                if widget == self.openGLWidget_11:
                    self.openGLWidget_14.paint(reader.npSeg, reader.npImage, currentWidnowName, sliceNum)
                    widget.makeObject()
                    widget.update()
                elif widget == self.openGLWidget_12:
                    self.openGLWidget_24.paint(reader.npSeg, reader.npImage, currentWidnowName, sliceNum)
                    widget.makeObject()
                    widget.update()
                else:
                    widget.makeObject()
                    widget.update()
            except Exception as e:
                print('Update Widget')
                print(e)

        self._sender = QtCore.QObject.sender(self)
        sender = self._sender
        if type(colorInd) == bool:
            linking = False
            if linking:
                name = 'openGLWidget_'
                widgets = select_proper_widgets(self)
                try:
                    sender_ind =  widgets.index(sender)
                    if sender_ind<3:
                        self.table_widget.setItem(self._num_adapted_points, 0, QtWidgets.QTableWidgetItem(str(whiteInd[0])))
                        self._points_adapt_eco.append(whiteInd[0])
                    else:
                        self.table_widget.setItem(self._num_adapted_points, 1, QtWidgets.QTableWidgetItem(str(whiteInd[0])))
                        self._points_adapt_mri.append(whiteInd[0])
                    reader = self.readImECO if sender_ind < 3 else self.readImMRI
                    widget_name = name + str(sender_ind+1)
                    updateWidget(getattr(self, widget_name), reader, whiteInd, colorInd)
                    if self._firstSelection is None:
                        self._firstSelection = True
                        for widget in widgets:
                            widget.setDisabled(True)
                        new_ind = sender_ind+1+3 if sender_ind < 3 else sender_ind+1-3
                        next_widget = getattr(self, name + str(new_ind))
                        next_widget.setDisabled(False)
                    elif self._firstSelection == True:
                        for widget in widgets:
                            widget.setDisabled(False)
                        self._firstSelection = None
                        self._num_adapted_points += 1
                except Exception as e:
                    print('Linking Error')
                    print(e)

        else:
            if self.linked or currentWidnowName=='MRI' or currentWidnowName=='ECO':


                widgets_mri = [self.openGLWidget_4, self.openGLWidget_5, self.openGLWidget_6, self.openGLWidget_12]
                widgets_eco = [self.openGLWidget_11, self.openGLWidget_1, self.openGLWidget_2, self.openGLWidget_3]
                if self.tabWidget.currentIndex() == 0:
                    widgets_mri = [self.openGLWidget_4, self.openGLWidget_5, self.openGLWidget_6]
                    widgets_eco = [self.openGLWidget_1, self.openGLWidget_2, self.openGLWidget_3]
                elif self.tabWidget.currentIndex() == 2:
                    widgets_mri = []
                    widgets_eco = [self.openGLWidget_11]
                elif self.tabWidget.currentIndex() == 3:
                    widgets_mri = [self.openGLWidget_12]
                    widgets_eco = []
                if colorInd == 0:
                    if currentWidnowName =='MRI':
                        reader = self.readImMRI

                        for widget in widgets_mri:
                            updateWidget(widget, reader, whiteInd.reshape(-1,3), colorInd)
                    elif currentWidnowName == 'ECO':
                        reader = self.readImECO
                        for widget in widgets_eco:
                            updateWidget(widget, reader, whiteInd.reshape(-1,3), colorInd)

                else:
                    if sender in widgets_mri:
                        x=self.linked_models[0].predict(whiteInd)
                        y=self.linked_models[1].predict(whiteInd)
                        z=self.linked_models[2].predict(whiteInd)
                        whiteInd_eco = destacked(x,y,z).astype('int')
                        whiteInds = [whiteInd, whiteInd_eco]
                    elif sender in widgets_eco:
                        x=self.linked_models[3].predict(whiteInd)
                        y=self.linked_models[4].predict(whiteInd)
                        z=self.linked_models[5].predict(whiteInd)
                        whiteInd_mri = destacked(x,y,z).astype('int')
                        whiteInds = [whiteInd_mri, whiteInd]

                    else:
                        return

                    if whiteInd is not None:
                        for reader, widgets, readerName, whiteIn in zip([self.readImMRI, self.readImECO], [widgets_mri, widgets_eco],
                                                   ['readImMRI', 'readImECO'], whiteInds):
                            self._lastChangedWidgest = widgets
                            self._lastReader = readerName
                            #self._lastReaderSegInd, self._lastReaderSegCol = getNoneZeroSeg(reader.npSeg)
                            print(a)
                            self._lastReaderSegInd.append(whiteIn)
                            self._lastReaderSegCol.append(colorInd)
                            self._lastReaderSegPrevCol.append(widgets[0].colorInd)
                            # self._lastReaderSeg = reader.npSeg.copy()

                            try:
                                assert (whiteIn.shape[1] == 3)
                                update_last(self, reader.npSeg, colorInd, whiteInd, widgets[0].colorInd)
                                #reader.npSeg[tuple(zip(*whiteIn))] = colorInd

                                for widget in widgets:
                                    setSliceSeg(widget, reader.npSeg)

                                    if widget == self.openGLWidget_11:
                                        self.openGLWidget_14.paint(reader.npSeg, reader.npEdge, currentWidnowName, sliceNum)
                                    elif widget == self.openGLWidget_12:
                                        self.openGLWidget_24.paint(reader.npSeg, reader.npEdge, currentWidnowName, sliceNum)

                                    widget.makeObject()
                                    widget.update()
                            except Exception as e:
                                print(e)
                                print('impossible')


            else:
                readerName = ''
                if sender == self.openGLWidget_4 or sender == self.openGLWidget_5 or sender == self.openGLWidget_6 or sender == self.openGLWidget_12:
                    # mri Image
                    readerName = 'readImMRI'
                    reader = self.readImMRI
                    widgets = []
                    if self.tabWidget.currentIndex() == 0:
                        widgets = [self.openGLWidget_4, self.openGLWidget_5, self.openGLWidget_6]
                    elif self.tabWidget.currentIndex()==3:
                        widgets = [self.openGLWidget_12]
                elif sender == self.openGLWidget_1 or sender == self.openGLWidget_2 or sender == self.openGLWidget_3 or sender == self.openGLWidget_11:
                    # eco
                    readerName = 'readImECO'
                    reader = self.readImECO
                    widgets = []
                    if self.tabWidget.currentIndex() == 0:
                        widgets = [self.openGLWidget_1, self.openGLWidget_2, self.openGLWidget_3]
                    elif self.tabWidget.currentIndex() == 2:
                        widgets = [self.openGLWidget_11]

                elif sender in [self.actionTVSag, self.actionTVCor, self.actionTVAx]:

                    if currentWidnowName.split('_')[0]=='ECO':
                        readerName = 'readImECO'
                        reader = self.readImECO
                        self._sender = self.openGLWidget_1
                        if self.tabWidget.currentIndex() == 0:
                            widgets = [self.openGLWidget_1, self.openGLWidget_2, self.openGLWidget_3]
                        elif self.tabWidget.currentIndex() == 2:
                            widgets = [self.openGLWidget_11]
                        elif self.tabWidget.currentIndex() == 3:
                            widgets = [self.openGLWidget_12]
                    elif currentWidnowName.split('_')[0]=='MRI':
                        readerName = 'readImMRI'
                        reader = self.readImMRI
                        self._sender = self.openGLWidget_5
                        widgets = [self.openGLWidget_4, self.openGLWidget_5, self.openGLWidget_6]
                    else:
                        return
                else:
                    return



                if whiteInd is not None:
                    if colorInd==9876:
                        return
                    self._lastChangedWidgest = widgets
                    self._lastWindowName = currentWidnowName
                    self._lastReader = readerName
                    #self._lastReaderSegInd, self._lastReaderSegCol = getNoneZeroSeg(reader.npSeg)

                    #self._lastReaderSeg = reader.npSeg.copy()


                    try:
                        if (whiteInd.shape[1] != 3):
                            return
                        if (whiteInd.shape[0] <= 0):
                            return
                        #self.dockWidget_3.setVisible(True)
                        #self.setEnabled(False)
                        if sender.imType=='mri':
                            shp = self.readImMRI.npImage.shape
                            self.readImMRI._npSeg = None
                        elif sender.imType=='eco':
                            shp = self.readImECO.npImage.shape
                            self.readImECO._npSeg = None
                        whiteInd = repetition(shp, whiteInd, self._Xtimes, currentWidnowName)
                        #edges = repetition(edges, self._Xtimes, currentWidnowName)
                        self.progressBarSaving.setValue(40)

                        update_last(self, reader.npSeg, colorInd, whiteInd, widgets[0].colorInd, guide_lines=colorInd==1500)


                        #update_edges(reader, edges)
                        self.progressBarSaving.setValue(60)
                        """
                        
                        if colorInd != 0:
                            WI = getZeroSeg(reader.npSeg, whiteInd)
                            self._lastReaderSegCol.append(colorInd)
                            self._lastReaderSegInd.append(WI)
                        else:
                            self._lastReaderSegCol.append(colorInd)
                            WI = getNoneZeroSeg(reader.npSeg, whiteInd)
                            self._lastReaderSegInd.append(WI)
                        self._lastReaderSegPrevCol.append(widgets[0].colorInd)
                        self._undoTimes = 0
                        reader.npSeg[tuple(zip(*whiteInd))] = colorInd
                        if len(self._lastReaderSegInd)> self._lastMax:
                            self._lastReaderSegCol = self._lastReaderSegCol[1:]
                            self._lastReaderSegInd = self._lastReaderSegInd[1:]
                            self._lastReaderSegPrevCol = self._lastReaderSegPrevCol[1:]
                        """
                        first_entry= True
                        for widget in widgets:
                            setSliceSeg(widget, reader.npSeg)
                            if hasattr(self, 'readImECO'):
                                if reader==self.readImECO and first_entry:
                                    self.openGLWidget_14.paint(reader.npSeg, reader.npImage, currentWidnowName, sliceNum)
                                    first_entry = False
                            if hasattr(self, 'readImMRI'):
                                if reader==self.readImMRI and first_entry:
                                    self.openGLWidget_24.paint(reader.npSeg, reader.npImage, currentWidnowName, sliceNum)
                                    first_entry = False
                            widget.makeObject()
                            widget.update()
                        self.progressBarSaving.setValue(100)
                        #self.setEnabled(True)
                        self.dockWidget_3.setVisible(False)
                        self.progressBarSaving.setValue(0)
                    except Exception as e:
                        self.setEnabled(True)
                        self.dockWidget_3.setVisible(False)
                        self.progressBarSaving.setValue(0)
                        print(e)
                        print('impossible')

    def update_table_measure(self,values, columnind):
        """
        Updating table measurements
        :param values:
        :param columnind:
        :return:
        """
        cont = self.table_widget_measure.rowCount()
        rw = cont
        for r in range(cont):
            itm = self.table_widget_measure.item(r, 1)
            if itm is None:
                rw = r
                break
            elif itm.text()=='':
                rw = r
                break
        if rw==cont:
            self.table_widget_measure.insertRow(rw)
        clm = self.table_widget_measure.columnCount()
        if values[1]=='0':
            values[-1] = self.filenameEco
        if values[1]=='1':
            values[-1] = self.filenameMRI
        for c in range(clm):
            self.table_widget_measure.setItem(rw, c, QtWidgets.QTableWidgetItem(values[c]))



    def GenerateContour(self):
        """
        Generating contours
        :return:
        """
        from melage.utils.utils import convexhull_spline, locateWidgets, SearchForAdditionalPoints

        if len(self.linePoints)<2:
            return
        if not hasattr(self, '_lastReader'):
            return
        sender = QtCore.QObject.sender(self)
        try:
            reader = getattr(self, self._lastReader)

            windowname = self._lastWindowName
            sliceNum = [w.sliceNum for w in self._lastChangedWidgest if w.currentWidnowName==windowname][0]
            use_additional = True
            if use_additional:
                seg = [w.segSlice for w in self._lastChangedWidgest if w.currentWidnowName == windowname][0]

                total_points, success, len_ls = SearchForAdditionalPoints(seg, sliceNum, windowname,max_lines=0, line_info=self._lineinfo,
                                                                          active_color_ind = self._colorInd)
                self._lineinfo = []
                if (len_ls['h']+len_ls['v'])>0:
                    selected_points = list(total_points) + self.linePoints
                else:
                    selected_points = self.linePoints
            else:
                selected_points = self.linePoints

            whiteInd, remps = convexhull_spline(selected_points, windowname, sliceNum, reader.npSeg)

            self.linePoints = remps
            readerName, reader, widgets = locateWidgets(self._lastChangedWidgest[0], self)
            if hasattr(self, '_colorInd'):
                update_last(self, reader.npSeg, self._colorInd, whiteInd, widgets[0].colorInd)
                reader.npSeg[reader.npSeg == 1500] = widgets[0].colorInd
                #removeLastLines(self._lastlines, reader.npSeg, self._colorInd)
                self._lastlines = []
                #reader.npSeg[tuple(zip(*whiteInd))] = self._colorInd



            for widget in widgets:
                setSliceSeg(widget, reader.npSeg)
                if widget == self.openGLWidget_11:
                    self.openGLWidget_14.paint(reader.npSeg, reader.npImage, widget.currentWidnowName, widget.sliceNum)
                elif widget == self.openGLWidget_12:
                    self.openGLWidget_24.paint(reader.npSeg, reader.npImage, widget.currentWidnowName, widget.sliceNum)
                if hasattr(widget, 'linePoints'):
                    widget.linePoints = []
                    widget.startLinePoints = []
                widget.makeObject()
                widget.update()


        except Exception as e:
            pass
    def Undo(self):
        if not hasattr(self, '_lastReader'):
            return
        num_els = len(self._lastReaderSegInd)
        if (num_els-self._undoTimes)<=0 :
            return
        reader = getattr(self, self._lastReader)
        #reader.npSeg *= 0
        curr_list = num_els-self._undoTimes-1
        _lastReaderSegInd = self._lastReaderSegInd[curr_list]
        _lastReaderSegInd, inds, us = _lastReaderSegInd
        _lastReaderSegCol = self._lastReaderSegCol[curr_list]
        _lastReaderSegPrevCol = self._lastReaderSegPrevCol[curr_list]
        if _lastReaderSegPrevCol == _lastReaderSegCol or not any([_lastReaderSegCol==0, _lastReaderSegPrevCol==0]):
            _lastReaderSegCol = 0
        else:
            _lastReaderSegCol = _lastReaderSegPrevCol
        if _lastReaderSegInd.shape[0]!=0:
            if inds is not None:
                for ind, u in zip(inds, us):
                    reader.npSeg[tuple(zip(*_lastReaderSegInd[ind]))] = u
            else:
                reader.npSeg[tuple(zip(*_lastReaderSegInd))] =  _lastReaderSegCol
        self._undoTimes += 1
        for widget in self._lastChangedWidgest:
            setSliceSeg(widget, reader.npSeg)
            widget.update()
            if widget == self.openGLWidget_11:
                self.openGLWidget_14.paint(reader.npSeg,reader.npImage, widget.currentWidnowName, widget.sliceNum)
            elif widget == self.openGLWidget_12:
                self.openGLWidget_24.paint(reader.npSeg,reader.npImage, widget.currentWidnowName, widget.sliceNum)
            if widget != self.openGLWidget_14:
                widget.makeObject()
                widget.update()


    def Redo(self):
        """
        Redo the segmentation
        :return:
        """
        if not hasattr(self, '_lastReader'):
            return
        num_els = len(self._lastReaderSegInd)
        #if (num_els-self._undoTimes)<=0:
        #    return
        reader = getattr(self, self._lastReader)
        #reader.npSeg *= 0
        curr_list = num_els - self._undoTimes
        if curr_list>=num_els:
            return
        _lastReaderSegInd = self._lastReaderSegInd[curr_list]
        _lastReaderSegInd, inds, us = _lastReaderSegInd
        _lastReaderSegCol = self._lastReaderSegCol[curr_list]
        _lastReaderSegPrevCol = self._lastReaderSegPrevCol[curr_list]
        if _lastReaderSegPrevCol == _lastReaderSegCol:
            _lastReaderSegCol = _lastReaderSegPrevCol
        else:
            _lastReaderSegCol = 0


        if _lastReaderSegInd.shape[0]!=0:
            #if inds is not None:
            #    for ind, u in zip(inds, us):
            #        reader.npSeg[tuple(zip(*_lastReaderSegInd[ind]))] = u
            #else:
            reader.npSeg[tuple(zip(*_lastReaderSegInd))] =  _lastReaderSegCol
        self._undoTimes -= 1
        for widget in self._lastChangedWidgest:
            setSliceSeg(widget, reader.npSeg)
            widget.update()
            if widget == self.openGLWidget_11:
                self.openGLWidget_14.paint(reader.npSeg, reader.npImage, widget.currentWidnowName, widget.sliceNum)
            elif widget == self.openGLWidget_12:
                self.openGLWidget_24.paint(reader.npSeg, reader.npImage, widget.currentWidnowName, widget.sliceNum)
            if widget != self.openGLWidget_14 or widget != self.openGLWidget_24:
                widget.makeObject()
                widget.update()

    def showSegOnWindow(self, value):
        """
        Enable segmentation
        :param value:
        :return:
        """
        sender = QtCore.QObject.sender(self)
        if sender == self.radioButton_21:
            ## mri
            self.openGLWidget_12.showSeg = value
            self.openGLWidget_12.makeObject()
            self.openGLWidget_12.update()
        elif sender == self.radioButton_4:
            ## eco
            self.openGLWidget_11.showSeg = value
            self.openGLWidget_11.makeObject()
            self.openGLWidget_11.update()




    def gatherToIm(self):
        """
        For ventricle segmentation
        :return:
        """
        from melage.utils.utils import findWhiteVoxels
        if not hasattr(self, 'seg'):
            return
        totalPs = self.openGLWidget_11.totalPs[self.segmentShowWindowName]
        Nseg = findWhiteVoxels(totalPs, self.segmentShowWindowName, self._segNN)
        setattr(self, 'seg_'+self.segmentShowWindowName, Nseg)


    def changeRotAx(self, val):
        """
        rotating image
        :param val:
        :return:
        """
        sender = QtCore.QObject.sender(self)
        if sender == self.page1_rot_cor:
            #if self.readImECO.npSeg.max()>0 and val:
                #self.page1_rot_cor.setChecked(False)
                #return
            if val.lower()=='coronal':
                self.hs_t1_5.setValue(self._rotationAngleEco_coronal)
            elif val.lower()== 'axial':
                self.hs_t1_5.setValue(-self._rotationAngleEco_axial)
            elif val.lower() == 'sagittal':
                self.hs_t1_5.setValue(-self._rotationAngleEco_sagittal)
        elif sender == self.page2_rot_cor:
            if self.readImMRI.npSeg.max()>0 and val:
                self.page2_rot_cor.setChecked(False)
                return
            if val.lower() == 'coronal':
                self.hs_t2_5.setValue(self._rotationAngleMRI_coronal)
            elif val.lower()== 'axial':
                self.hs_t2_5.setValue(-self._rotationAngleMRI_axial)
            elif val.lower()== 'sagittal':
                self.hs_t2_5.setValue(-self._rotationAngleMRI_sagittal)

    def C2S(self, value):
        """
        Coronal to Sagittal
        :param value:
        :return:
        """
        sender = QtCore.QObject.sender(self)
        if sender == self.page1_s2c:
            if not hasattr(self, 'readImECO'):
                return
            if not hasattr(self.readImECO, 'npSeg'):
                return
            if self._rotationAngleEco_axial != 0 or self._rotationAngleEco_coronal!=0 or self._rotationAngleEco_sagittal!=0 or self.readImECO.npSeg.max()>0:
                MessageBox = QtWidgets.QMessageBox(self)
                if self._rotationAngleEco_axial != 0 or self._rotationAngleEco_coronal!=0 or self._rotationAngleEco_sagittal!=0:
                    MessageBox.setText('You are not allowed to change the image after rotation')
                else:
                    MessageBox.setText('You are not allowed to change the image after segmentation')
                MessageBox.setWindowTitle('Warning')
                MessageBox.show()
                self.page1_s2c.setChecked(not value)
                return
            #if value:
            #    self.readImECO.changeData(imchange=True)
            #    self.updateDispEco(self.readImECO.npImage, self.readImECO.npSeg, initialState=True)
            #else:
                #self.readImECO.updateData(self.readImECO.im)
            ###""

            npSeg = self.readImECO.npSeg.copy()
            from melage.utils.utils import make_image
            if hasattr(self.readImECO, '_imChanged'):
                npSeg = make_image(npSeg, self.readImECO._imChanged)
            else:
                npSeg = make_image(npSeg, self.readImECO.im)
            #""

            self.readImECO.changeData(type = 'eco', imchange=True, state= value)

            self.updateDispEco(self.readImECO.npImage, self.readImECO.npSeg, initialState=True)

        elif sender == self.page2_s2c:
            if not hasattr(self, 'readImMRI'):
                return
            if not hasattr(self.readImMRI, 'npSeg'):
                return
            if self._rotationAngleMRI_axial != 0 or self._rotationAngleMRI_coronal != 0 or self._rotationAngleMRI_sagittal != 0 or self.readImMRI.npSeg.max()>0:
                MessageBox = QtWidgets.QMessageBox(self)

                if self._rotationAngleMRI_axial != 0 or self._rotationAngleMRI_coronal != 0 or self._rotationAngleMRI_sagittal != 0:
                    MessageBox.setText('You are not allowed to change the image after rotation')
                else:
                    MessageBox.setText('You are not allowed to change the image after segmentation')

                MessageBox.setWindowTitle('Warning')
                MessageBox.show()
                self.page2_s2c.setChecked(not value)
                return
            #if value:
            #    self.readImMRI.changeData(imchange=True)
            #    self.updateDispMRI(self.readImMRI.npImage, self.readImMRI.npSeg, initialState=True)
            #else:
            self.readImMRI.changeData(type='t1', imchange=True, state= value)
            self.updateDispMRI(self.readImMRI.npImage, self.readImMRI.npSeg, initialState=True, tract=self.readImMRI.tract)


    def segmentVentricles(self):
        """
        Segmentation of ventricles
        :return:
        """
        try:
            from Ventriculos.options.options import options as netOpts
            from Ventriculos.test import test as netEval
        except:
            print('We can not segment image. Please check pytorch installation')
            pass

        if hasattr(self, 'readImECO'):
            if hasattr(self.readImECO,'npImage'):
                print('be patient...')
                opts = netOpts().parse()
                opts.chkptDir = '../Ventriculos/'+opts.chkptDir
                opts.modelName = 'Net2D'
                opts.state = 'train'
                opts.dataDir = 'dataset'
                opts.dataset = 'twoD'
                opts.GPUs = '0'
                opts.batchSize = 64
                opts.shuffle = False
                opts.useAugment = False
                opts.dir3d = 'Ventriculos/Seg/TestIsa'
                opts.modelNetG = 'unet2d'
                opts.numThreads = 8
                im = self.readImECO.npImage
                im = im.transpose([0, 2, 1])

                self.dockWidget_3.setVisible(True)
                self.setEnabled(False)
                self.progressBarSaving.setValue(20)

                self._segNN = netEval(im, opts).transpose([0, 2, 1])
                self.progressBarSaving.setValue(80)


                self.vnetricleSegmentShow(thrsh=50)

                self.progressBarSaving.setValue(100)

                self.setEnabled(True)
                self.dockWidget_3.setVisible(False)
                self.progressBarSaving.setValue(0)
        pass

    def ColorIntensityChange(self, thrsh = 0, dtype='image'):
        """
        Changing color intensity
        :param thrsh:
        :dtype image or seg
        :return:
        """
        not_exist1, not_exist2 = False, False
        if hasattr(self, 'readImMRI'):
            if not hasattr(self.readImMRI, 'npSeg'):
                not_exist1 = True
        if hasattr(self, 'readImECO'):
            if not hasattr(self.readImECO, 'npSeg'):
                not_exist2 = True
        if not_exist1 and not_exist2:
            return
        if dtype=='image':
            widgets_num = [0,1,2,3,4,5,10,11,13,23]
            for k in widgets_num:
                name = 'openGLWidget_' + str(k + 1)
                widget = getattr(self, name)

                if widget.isVisible():#k  in [13,23]:
                    if k==13:
                        widget.intensityImg = thrsh / 1000
                        self.update3Dview(None, None, typew='eco')
                    elif k==23:
                        widget.intensityImg = thrsh / 1000
                        self.update3Dview(None, None, typew='mri')
                    #widget.intensityImg = thrsh/100
                widget.update()
        elif dtype=='seg':
            widgets_num = [0,1,2,3,4,5,10,11,13,23]
            for k in widgets_num:
                name = 'openGLWidget_' + str(k + 1)
                widget = getattr(self, name)
                widget.intensitySeg = thrsh/100
                if k not in [13,23]:
                    widget.makeObject()
                else:
                    widget.GLV.intensitySeg = thrsh/100
                    widget.GLSC.intensitySeg = thrsh / 100
                widget.update()

    def trackDistance(self, thrsh=50):
        if not hasattr(self, 'readImMRI'):
            self.dw5_s1.setValue(0)
            self.dw5lb1.setText('0')
            return
        if not hasattr(self.readImMRI, 'npImage'):
            self.dw5_s1.setValue(0)
            self.dw5lb1.setText('0')
            return

        if not hasattr(self.readImMRI, 'tract'):
            self.dw5_s1.setValue(0)
            self.dw5lb1.setText('0')
            return
        oldMin, oldMax = 0, 100

        shp = self.readImMRI.npImage.shape
        NewMin, NewMax = 1, min(min(shp[0], shp[1]), shp[2])//6
        OldRange = (oldMax - oldMin)
        NewRange = (NewMax - NewMin)
        thrsh = (((thrsh - oldMin) * NewRange) / OldRange) + NewMin
        self.tol_trk = thrsh
        widgets_num = [3, 4, 5]
        for k in range(12):
            name = 'openGLWidget_' + str(k + 1)
            widget = getattr(self, name)
            if k in widgets_num:
                widget.updateInfo(*getCurrentSlice(widget,
                                                   self.readImMRI.npImage, self.readImMRI.npSeg, widget.sliceNum, self.readImMRI.tract, tol_slice=self.tol_trk), widget.sliceNum,
                                  self.readImMRI.npImage.shape,
                                  initialState=False, imSpacing=self.readImMRI.ImSpacing)

                widget.makeObject()
                widget.update()
                widget.show()

    def trackThickness(self, thrsh=50):
        """"
        Thickness in tractography images
        """
        if not hasattr(self, 'readImMRI'):
            self.dw5_s2.setValue(0)
            self.dw5lb2.setText('0')
            return
        if not hasattr(self.readImMRI, 'npImage'):
            self.dw5_s2.setValue(0)
            self.dw5lb2.setText('0')
            return
        if not hasattr(self.readImMRI, 'tract'):
            self.dw5_s2.setValue(0)
            self.dw5lb2.setText('0')
            return
        oldMin, oldMax = 0, 100

        NewMin, NewMax = 1, 10#min(min(shp[0], shp[1]), shp[2])//6
        OldRange = (oldMax - oldMin)
        NewRange = (NewMax - NewMin)
        thrsh = (((thrsh - oldMin) * NewRange) / OldRange) + NewMin

        widgets_num = [3, 4, 5]
        for k in range(12):
            name = 'openGLWidget_' + str(k + 1)
            widget = getattr(self, name)
            if k in widgets_num:

                widget.width_line_tract =thrsh
                widget.makeObject()
                widget.update()
                widget.show()



    def vnetricleSegmentShow(self, thrsh = 50):
        """
        Show segmentation widget
        :param thrsh:
        :return:
        """
        if not hasattr(self, '_segNN'):
            self.dw4_s1.setValue(50)
            self.dw4lb1.setText('50')
            #MessageBox = QtWidgets.QMessageBox(self)
            #MessageBox.setText('Please segment image before using this command')
            #MessageBox.show()
            return
        thrsh /= 100
        seg = self._segNN/255.0
        seg[seg>thrsh]=1
        seg[seg<=thrsh]=0
        self.openGLWidget_14.clear()
        self.readImECO.npSeg = seg
        self.updateDispEco(self.readImECO.npImage, self.readImECO.npSeg, initialState=True)



    def changeMagicToolTo222l(self, value):
        widgets = find_avail_widgets(self)
        for k in widgets:
            name = 'openGLWidget_' + str(k)
            widget = getattr(self, name)

            if k in [14, 24] or not widget.isVisible():
                continue
            if widget.enabledMagicTool:
                widget._tol_magic_tool = self.dw2_s2.value()

    def changeRadiusCircle(self, value, slider=False):
        """
        Change circle radius
        :param value:
        :param slider:
        :return:
        """
        oldMin, oldMax = 0, 100
        NewMin, NewMax = 50, 80
        #OldRange = (oldMax - oldMin)
        #NewRange = (NewMax - NewMin)
        #value = (((value - oldMin) * NewRange) / OldRange) + NewMin
        if value is not None:
            self._rad_circle = value
        else:
            self._rad_circle = self.dw2_s1.value()
        try:
            self.actionCircles.triggered.disconnect(partial(self.setCursors, 9, self._rad_circle))
        except:
            pass
        widgets = find_avail_widgets(self)
        for k in widgets:
            name = 'openGLWidget_' + str(k)
            widget = getattr(self, name)

            if k in [14, 24] or not widget.isVisible():
                continue
            if widget.enabledMagicTool:
                widget._tol_magic_tool = self.dw2_s1.value()
                continue
            if not widget.enabledCircle:
                continue
            self._rad_circle_dot = self._rad_circle*abs(widget.to_real_world( 1, 0)[0] - widget.to_real_world(0, 0)[0])
            self._tol_cricle_tool =((self.dw2_s2.value()-self.dw2_s2.minimum())/(self.dw2_s2.maximum()-self.dw2_s2.minimum()))*(2-0.5)+0.5
            widget._radius_circle = self._rad_circle*abs(widget.to_real_world( 1, 0)[0] - widget.to_real_world(0, 0)[0])
            setCursorWidget(widget, 9, 1, self._rad_circle)

        self.actionCircles.triggered.connect(partial(self.setCursors, 9, self._rad_circle))

    def changeSizePen(self,value): # change color pen
        """
        change size pen
        :param value: size pen
        :return: set current pen size
        """
        rng = 30/100
        value *= rng
        val_tol = ((self.dw2_s2.value()-self.dw2_s2.minimum())/(self.dw2_s2.maximum()-self.dw2_s2.minimum()))*(2-0.5)+0.5
        self.openGLWidget_1.widthPen = value
        self.openGLWidget_1._tol_cricle_tool = val_tol
        self.openGLWidget_1.update()

        self.openGLWidget_2.widthPen = value
        self.openGLWidget_2._tol_cricle_tool = val_tol
        self.openGLWidget_2.update()

        self.openGLWidget_3.widthPen = value
        self.openGLWidget_3._tol_cricle_tool = val_tol
        self.openGLWidget_3.update()

        self.openGLWidget_4.widthPen = value
        self.openGLWidget_4._tol_cricle_tool = val_tol
        self.openGLWidget_4.update()

        self.openGLWidget_5.widthPen = value
        self.openGLWidget_5._tol_cricle_tool = val_tol
        self.openGLWidget_5.update()

        self.openGLWidget_6.widthPen = value
        self.openGLWidget_6._tol_cricle_tool = val_tol
        self.openGLWidget_6.update()

        self.openGLWidget_11.widthPen = value
        self.openGLWidget_11._tol_cricle_tool = val_tol
        self.openGLWidget_11.update()

        self.openGLWidget_12.widthPen = value
        self.openGLWidget_12._tol_cricle_tool = val_tol
        self.openGLWidget_12.update()

    def changeImage(self, value):
        """
        Change Image
        :param value:
        :return:
        """
        #parent = self.tree_colors.model().sourceModel().invisibleRootItem()
        from melage.utils.utils import clean_parent_image
        index_row = value.index().row()
        [info, _, _, indc] = self.imported_images[index_row]#
        index_view = info[0][2]
        try:
            if value.checkState()==Qt.Checked:
                if info[1]<3:#image loading
                    #if info[1]<2: #eco loading
                    if index_view==0:
                        cond = self.browseUS(info, use_dialog=False)
                        if cond:
                            self.imported_images[index_row][2] = True
                            clean_parent_image(self, index_row, [indc, indc+'_Seg'], index_view=index_view)
                        else:
                            value.setCheckState(Qt.Unchecked)
                    else:
                        cond = self.browseMRI(info, use_dialog=False)
                        if cond:
                            self.imported_images[index_row][2] = True
                            clean_parent_image(self, index_row, [indc, indc+'_Seg'], index_view=index_view)
                        else:
                            value.setCheckState(Qt.Unchecked)
                else: #segmentation loading
                    #if info[1]<5: #eco loading
                    if index_view == 0:
                        cond = self.importData(type_image='usseg', fileObj=info[0])
                        if cond:
                            self.imported_images[index_row][2] = True
                            clean_parent_image(self, index_row, [indc], index_view=index_view)
                        else:
                            value.setCheckState(Qt.Unchecked)
                    else:
                        cond = self.importData(type_image='mriseg', fileObj=info[0])
                        if cond:
                            self.imported_images[index_row][2] = True
                            clean_parent_image(self, index_row, [indc],index_view=index_view)
                        else:
                            value.setCheckState(Qt.Unchecked)

            else: #close image
                if info[1]<3:#image loading
                    #if info[1]<2: #eco loading
                    if index_view == 0:
                        cond = self.CloseUS(message_box='on')
                        if cond:
                            if 'US' in info[0][1]:
                                self.imported_images.pop(index_row)
                                parent = self.tree_images.model().sourceModel().invisibleRootItem()
                                parent.removeRow(index_row)
                            else:
                                self.imported_images[index_row][2] = False
                                clean_parent_image(self, -1, ['Fetal_Seg','US_Seg'], index_view=index_view)
                        else:
                            value.setCheckState(Qt.Checked)
                    else:
                        cond = self.CloseMRI(message_box='on', dialogue=True)
                        if cond:
                            if 'MRI' in info[0][1]:
                                self.imported_images.pop(index_row)
                                parent = self.tree_images.model().sourceModel().invisibleRootItem()
                                parent.removeRow(index_row)
                            else:
                                self.imported_images[index_row][2] = False
                                clean_parent_image(self, -1, ['MRI_Seg'],index_view)
                        else:
                            value.setCheckState(Qt.Checked)
                else: #segmentation loading
                    #if info[1] < 5:  # eco loading
                    if index_view == 0:
                        self.closeImportData(type_image='usseg')
                        self.imported_images[index_row][2] = False
                    else:
                        self.closeImportData(type_image='mriseg')
                        self.imported_images[index_row][2] = False
        except Exception as e:
            print(e)

    def changeColorPen(self,value): # change color pen
        """
        change color pen
        :param value: color pen
        :return: set current color
        """


        text =''
        if type(value)!=str:
            colrInds = []
            if value.checkState()==Qt.Checked:
                ind = int(float(value.text()))
                text = self.tree_colors.model().sourceModel().item(value.row(), 1).text()
            else:
                ind = None
                text = ''
            root = self.tree_colors.model().sourceModel().invisibleRootItem()
            for i in range(root.rowCount()):
                signal = root.child(i)
                if signal.checkState()==Qt.Checked:
                    colrInds.append(int(float(signal.text())))
            if len(colrInds)==0:
                #colrInds = []
                ind = 9876
                text='Combined'


        try:
            """
            
            if value =='':
                ind = 9876#self.dw2Text.index('X_Combined') + 1
            else:
                try:
                    ind = int(self.dw2Text[self.dw2Text.index(value)].split('_')[0])
                except:
                    ind = 9876#self.dw2Text.index(value) + 1
            """
            #sender = QtCore.QObject.sender(self)
            sender_eco = False
            for f in self.widgets_eco:
                a = getattr(self, 'openGLWidget_{}'.format(f))
                if a.isVisible():
                    sender_eco = True
                    break

            #if sender_eco:
            if hasattr(self, 'readImECO'):
                if hasattr(self.readImECO, 'npSeg'):
                    txt = compute_volume(self.readImECO, self.filenameEco, colrInds, in_txt=self.openedFileName.text(),
                                         ind_screen=0)
                    self.openedFileName.setText(txt)

            #else:
            if hasattr(self, 'readImMRI'):
                if hasattr(self.readImMRI, 'npSeg'):
                    txt = compute_volume(self.readImMRI, self.filenameMRI, colrInds, in_txt=self.openedFileName.text(),
                                         ind_screen=1)
                    self.openedFileName.setText(txt)
            if ind is not None:
                self._selected_seg_color = ind
                #if 9876 not in colrInds:
                try:
                    colorPen = self.colorsCombinations[ind]
                except:
                    colorPen = [1, 0, 0, 1]
                #else:
                #    colorPen = [1,0,0,1]
                colorPen = [int(float(i*255)) for i in colorPen]
                self.pixmap_box_color.fill(
                    (QtGui.QColor(colorPen[0], colorPen[1], colorPen[2], 255)))
                self._icon_colorX.addPixmap(self.pixmap_box_color, QtGui.QIcon.Normal,
                                            QtGui.QIcon.On)
                self.pixmap_box_label.setText(text)
                self.actionColor.setIcon(self._icon_colorX)
                    #pixmap.fill((QtGui.QColor(colorPen[0] * 255.0, colorPen[1] * 255.0, colorPen[2] * 255.0, 1 * 255.0)))
                    #self._icon_colorX.addPixmap(QtGui.QPixmap(source_folder + "/box.png"), QtGui.QIcon.Normal,
                    #                            QtGui.QIcon.On)
                    #self._icon_colorX.addPixmap()

            widgets = find_avail_widgets(self)
            prefix = 'openGLWidget_'
            for k in widgets:
                name = prefix + str(k)
                widget = getattr(self, name)
                if ind is not None:
                    widget.colorInd = ind
                widget.colorInds = colrInds
                if not widget.isVisible():
                    continue
                if k in [14]:
                    widget.paint(self.readImECO.npSeg,
                                       self.readImECO.npImage, None)
                elif k in [24]:
                    widget.paint(self.readImMRI.npSeg,
                          self.readImMRI.npImage, None)
                else:
                    if ind is not None:
                        widget.colorObject = colorPen
                    widget.makeObject()
                    widget.update()


                    #widget.show()
        except Exception as e:
            print('Imposible to change the color {}'.format(e))


    def changeBrightness(self,value): # change contrast brightns
        """
        Change contrast and brightness
        :param value:
        :return:
        """
        sender = QtCore.QObject.sender(self)
        value /= 100
        #print(fffff)
        if sender == self.hs_t1_1:
            self.openGLWidget_1.brightness = value
            self.openGLWidget_1.update()
            self.openGLWidget_2.brightness = value
            self.openGLWidget_2.update()
            self.openGLWidget_3.brightness = value
            self.openGLWidget_3.update()
            self.openGLWidget_11.brightness = value
            self.openGLWidget_11.update()
        elif sender == self.hs_t2_1:
            self.openGLWidget_4.brightness = value
            self.openGLWidget_4.update()
            self.openGLWidget_5.brightness = value
            self.openGLWidget_5.update()
            self.openGLWidget_6.brightness = value
            self.openGLWidget_6.update()
            self.openGLWidget_12.brightness = value
            self.openGLWidget_12.update()

    def changeContrast(self,value): # change contrast brightns
        sender = QtCore.QObject.sender(self)
        value = (value/100+1)
        widgets_num = []
        if sender == self.hs_t1_2:
            widgets_num = [0, 1, 2, 10]
        elif sender == self.hs_t2_2:
            widgets_num = [3, 4, 5, 11]
        for k in widgets_num:
            name = 'openGLWidget_' + str(k + 1)
            widget = getattr(self, name)
            widget.contrast = value
            if k in widgets_num:
                widget.makeObject()
                widget.update()


    def changeBandPass(self,value): # change threshold
        """
        Image enhancement BandPass
        :param value:
        :return:
        """
        sender = QtCore.QObject.sender(self)
        value =value/100
        if sender == self.hs_t1_3:
            self.openGLWidget_1.BandPR1 = value
            self.openGLWidget_1.makeObject()
            self.openGLWidget_1.update()
            self.openGLWidget_2.BandPR1 = value
            self.openGLWidget_2.makeObject()
            self.openGLWidget_2.update()
            self.openGLWidget_3.BandPR1 = value
            self.openGLWidget_3.makeObject()
            self.openGLWidget_3.update()

            self.openGLWidget_11.BandPR1 = value
            self.openGLWidget_11.makeObject()
            self.openGLWidget_11.update()

        elif sender == self.hs_t1_7:
            self.openGLWidget_1.BandPR2 = value
            self.openGLWidget_1.makeObject()
            self.openGLWidget_1.update()
            self.openGLWidget_2.BandPR2 = value
            self.openGLWidget_2.makeObject()
            self.openGLWidget_2.update()
            self.openGLWidget_3.BandPR2 = value
            self.openGLWidget_3.makeObject()
            self.openGLWidget_3.update()
            self.openGLWidget_11.BandPR2 = value
            self.openGLWidget_11.makeObject()
            self.openGLWidget_11.update()
        elif sender == self.hs_t2_3:
            self.openGLWidget_4.BandPR1 = value
            self.openGLWidget_4.makeObject()
            self.openGLWidget_4.update()
            self.openGLWidget_5.BandPR1 = value
            self.openGLWidget_5.makeObject()
            self.openGLWidget_5.update()
            self.openGLWidget_6.BandPR1 = value
            self.openGLWidget_6.makeObject()
            self.openGLWidget_6.update()
            self.openGLWidget_12.BandPR1 = value
            self.openGLWidget_12.makeObject()
            self.openGLWidget_12.update()
        elif sender == self.hs_t2_7:
            self.openGLWidget_4.BandPR2 = value
            self.openGLWidget_4.makeObject()
            self.openGLWidget_4.update()
            self.openGLWidget_5.BandPR2 = value
            self.openGLWidget_5.makeObject()
            self.openGLWidget_5.update()
            self.openGLWidget_6.BandPR2 = value
            self.openGLWidget_6.makeObject()
            self.openGLWidget_6.update()
            self.openGLWidget_12.BandPR2 = value
            self.openGLWidget_12.makeObject()
            self.openGLWidget_12.update()


    def changeHamming(self,value): # change threshold
        """
        Add hamming filter
        :param value:
        :return:
        """
        sender = QtCore.QObject.sender(self)
        if sender == self.toggle1_1:
            self.openGLWidget_1.hamming = value
            self.openGLWidget_1.makeObject()
            self.openGLWidget_1.update()
            self.openGLWidget_2.hamming = value
            self.openGLWidget_2.makeObject()
            self.openGLWidget_2.update()
            self.openGLWidget_3.hamming = value
            self.openGLWidget_3.makeObject()
            self.openGLWidget_3.update()
            self.openGLWidget_11.hamming = value
            self.openGLWidget_11.makeObject()
            self.openGLWidget_11.update()
        elif sender == self.toggle2_1:
            self.openGLWidget_4.hamming = value
            self.openGLWidget_4.makeObject()
            self.openGLWidget_4.update()
            self.openGLWidget_5.hamming = value
            self.openGLWidget_5.makeObject()
            self.openGLWidget_5.update()
            self.openGLWidget_6.hamming = value
            self.openGLWidget_6.makeObject()
            self.openGLWidget_6.update()
            self.openGLWidget_12.hamming = value
            self.openGLWidget_12.makeObject()
            self.openGLWidget_12.update()



    def changeSobel(self, value):
        """
        Use soble operator
        :param value:
        :return:
        """
        sender = QtCore.QObject.sender(self)
        if sender == self.hs_t1_4:
            if value>0:
                self.openGLWidget_1.activateSobel = True
                self.openGLWidget_2.activateSobel = True
                self.openGLWidget_3.activateSobel = True
                self.openGLWidget_11.activateSobel = True
                value = 1 - value/100
                self.openGLWidget_1.thresholdSobel = value
                self.openGLWidget_1.update()
                self.openGLWidget_2.thresholdSobel = value
                self.openGLWidget_2.update()
                self.openGLWidget_3.thresholdSobel = value
                self.openGLWidget_3.update()
                self.openGLWidget_11.thresholdSobel = value
                self.openGLWidget_11.update()
            else:
                self.openGLWidget_1.activateSobel = False
                self.openGLWidget_2.activateSobel = False
                self.openGLWidget_3.activateSobel = False
                self.openGLWidget_11.activateSobel = False
                self.openGLWidget_1.update()
                self.openGLWidget_2.update()
                self.openGLWidget_3.update()
                self.openGLWidget_11.update()
        elif sender == self.hs_t2_4:
            if value>0:
                self.openGLWidget_4.activateSobel = True
                self.openGLWidget_5.activateSobel = True
                self.openGLWidget_6.activateSobel = True
                self.openGLWidget_12.activateSobel = True
                value = 1 - value/100
                self.openGLWidget_4.thresholdSobel = value
                self.openGLWidget_4.update()
                self.openGLWidget_5.thresholdSobel = value
                self.openGLWidget_5.update()
                self.openGLWidget_6.thresholdSobel = value
                self.openGLWidget_6.update()
                self.openGLWidget_12.thresholdSobel = value
                self.openGLWidget_12.update()
            else:
                self.openGLWidget_4.activateSobel = False
                self.openGLWidget_5.activateSobel = False
                self.openGLWidget_6.activateSobel = False
                self.openGLWidget_12.activateSobel = False
                self.openGLWidget_4.update()
                self.openGLWidget_5.update()
                self.openGLWidget_6.update()
                self.openGLWidget_12.update()


    def changeWidthPen(self):
        pass


    def changeColorize(self, value):
        """
        Colorize image
        :param value:
        :return:
        """
        sender = QtCore.QObject.sender(self)

        if sender == self.hs_t1_8 or sender == self.colorize:
            if self.tabWidget.currentIndex() == 0:
                widgets_num = [0, 1, 2]
            elif self.tabWidget.currentIndex() == 2:
                widgets_num = [10]
            elif self.tabWidget.currentIndex() == 3:
                widgets_num = [11]
            else:
                widgets_num = []
            current_val = self.hs_t1_8.value()
            if self.colorize.isChecked():
                for k in range(12):
                    name = 'openGLWidget_' + str(k + 1)
                    widget = getattr(self, name)
                    widget.n_colors = current_val
                    if k in widgets_num:
                        widget.makeObject()
                        widget.update()
            else:
                for k in range(12):
                    name = 'openGLWidget_' + str(k + 1)
                    widget = getattr(self, name)
                    widget.n_colors = 0
                    if k in widgets_num:
                        widget.makeObject()
                        widget.update()

        elif sender == self.hs_t2_8 or sender == self.colorize_MRI:
            if self.tabWidget.currentIndex() == 0:
                widgets_num = [3, 4, 5]
            else:
                widgets_num = []
            current_val = self.hs_t2_8.value()
            if self.colorize_MRI.isChecked():
                for k in range(12):
                    name = 'openGLWidget_' + str(k + 1)
                    widget = getattr(self, name)
                    widget.n_colors = current_val
                    if k in widgets_num:
                        widget.makeObject()
                        widget.update()
            else:
                for k in range(12):
                    name = 'openGLWidget_' + str(k + 1)
                    widget = getattr(self, name)
                    widget.n_colors = 0
                    if k in widgets_num:
                        widget.makeObject()
                        widget.update()








    def Rotate(self, value):
        """
        Rotating image
        :param value:
        :return:
        """
        from melage.utils.utils import rotation3d
        from melage.utils.utils import make_image, len_unique
        sender = QtCore.QObject.sender(self)

        for k in range(12):
            name = 'openGLWidget_' + str(k + 1)
            widget = getattr(self, name)
            widget.zRot = 0
            widget.update()
        if sender == self.hs_t1_5:
            if not hasattr(self, 'readImECO'):
                return
            if not hasattr(self.readImECO, 'npSeg') :
                return

            uq, lenuq = len_unique(self.readImECO.npSeg)
            if lenuq>2:


                #MessageBox = QtWidgets.QMessageBox(self)
                #MessageBox.setText('You are not allowed to change the image after segmentation')
                #MessageBox.setWindowTitle('Warning')
                #MessageBox.show()
                #self.page1_s2c.setChecked(False)

                #self.hs_t1_5.valueChanged.disconnect()
                self.hs_t1_5.blockSignals(True)
                self.lb_t1_5.blockSignals(True)
                if self.page1_rot_cor.currentText().lower() == 'coronal':
                    self.hs_t1_5.setValue(self._rotationAngleEco_coronal)
                    self.lb_t1_5.setNum(self._rotationAngleEco_coronal)
                elif self.page1_rot_cor.currentText().lower() == 'axial':
                    self.hs_t1_5.setValue(self._rotationAngleEco_axial)
                    self.lb_t1_5.setNum(self._rotationAngleEco_axial)
                elif self.page1_rot_cor.currentText().lower() == 'sagittal':
                    self.hs_t1_5.setValue(self._rotationAngleEco_sagittal)
                    self.lb_t1_5.setNum(self._rotationAngleEco_sagittal)
                self.hs_t1_5.blockSignals(False)
                self.lb_t1_5.blockSignals(False)
                #self.hs_t1_5.valueChanged.connect(self.Rotate)
                return
            if self.page1_rot_cor.currentText().lower() == 'coronal':
                self._rotationAngleEco_coronal = value
            elif self.page1_rot_cor.currentText().lower() == 'axial':
                self._rotationAngleEco_axial = -value
            elif self.page1_rot_cor.currentText().lower() == 'sagittal':
                self._rotationAngleEco_sagittal = -value


            self.dockWidget_3.setVisible(True)
            self.setEnabled(False)
            self.progressBarSaving.setValue(20)

            rr = 0
            im, rot_mat = rotation3d(self.readImECO._imChanged, self._rotationAngleEco_axial,
                            self._rotationAngleEco_coronal, self._rotationAngleEco_sagittal)
            if lenuq>1:
                if self.readImECO._npSeg is None:
                    self.readImECO._npSeg = self.readImECO.npSeg

                npSeg = self.readImECO._npSeg.copy()

                Segm = make_image(npSeg, self.readImECO._imChanged)

                npSeg, _ = rotation3d(Segm, self._rotationAngleEco_axial,
                                self._rotationAngleEco_coronal, self._rotationAngleEco_sagittal)
                #for rot, axs in zip([self._rotationAngleEco_axial,self._rotationAngleEco_sagittal, self._rotationAngleEco_coronal],
                #               [[0,0,1], [1,0,0],[0,1,0]]):
                npSeg[npSeg > 0] = uq.max()
                #    if rr == 0:
                #        im = rotation3d(self.readImECO._imChanged, rot, axs)
                #        rr += 1
                #    else:
                #        im = rotation3d(im, rot, axs)
                self.readImECO.npSeg = npSeg
            self.readImECO.metadata['rot_axial'] = self._rotationAngleEco_axial
            self.readImECO.metadata['rot_sagittal'] = self._rotationAngleEco_sagittal
            self.readImECO.metadata['rot_coronal'] = self._rotationAngleEco_coronal


            """
            if self._rotationAngleEco_axial != 0:
                im = rotation3d(self.readImECO._imChanged, self._rotationAngleEco_axial, [0,0,1])
                if self._rotationAngleEco_coronal != 0:
                    im = rotation3d(im, self._rotationAngleEco_coronal, [0,1,0])
            else:
                im = rotation3d(self.readImECO._imChanged, self._rotationAngleEco_coronal, [0,1,0])
            """
            self.progressBarSaving.setValue(80)
            self.readImECO.updateData(im, rot_mat, type='eco')
            self.updateDispEco(self.readImECO.npImage, self.readImECO.npSeg, initialState=True)

            self.progressBarSaving.setValue(100)
            self.setEnabled(True)
            self.dockWidget_3.setVisible(False)
            self.progressBarSaving.setValue(0)
        elif sender == self.hs_t2_5:
            if not hasattr(self, 'readImMRI'):
                return
            if not hasattr(self.readImMRI, 'npSeg') :
                return

            #if not hasattr(self, 'readImMRI'):
            #    return
            #if not hasattr(self.readImMRI, 'npSeg') or value == self._rotationAngleMRI_axial or value == self._rotationAngleMRI_coronal:
            #    return
            if self.readImMRI.npSeg.max()>0:
                #MessageBox = QtWidgets.QMessageBox(self)
                #MessageBox.setText('You are not allowed to change the image after segmentation')
                #MessageBox.setWindowTitle('Warning')
                #MessageBox.show()
                #self.page2_s2c.setChecked(False)
                self.hs_t2_5.blockSignals(True)
                if self.page2_rot_cor.currentText().lower() == 'coronal':
                    self.hs_t2_5.setValue(self._rotationAngleMRI_coronal)
                    self.lb_t2_5.setNum(self._rotationAngleMRI_coronal)
                elif self.page2_rot_cor.currentText().lower() == 'axial':
                    self.hs_t2_5.setValue(self._rotationAngleMRI_axial)
                    self.lb_t2_5.setNum(self._rotationAngleMRI_axial)
                elif self.page2_rot_cor.currentText().lower() == 'sagittal':
                    self.hs_t2_5.setValue(self._rotationAngleMRI_sagittal)
                    self.lb_t2_5.setNum(self._rotationAngleMRI_sagittal)
                self.hs_t2_5.blockSignals(False)
                return
            if self.page2_rot_cor.currentText().lower() == 'coronal':
                self._rotationAngleMRI_coronal = value
            if self.page2_rot_cor.currentText().lower() == 'axial':
                self._rotationAngleMRI_axial = -value
            if self.page2_rot_cor.currentText().lower() == 'sagittal':
                self._rotationAngleMRI_sagittal = -value

            self.dockWidget_3.setVisible(True)
            self.setEnabled(False)
            self.progressBarSaving.setValue(20)
            im, rot_mat = rotation3d(self.readImMRI._imChanged, self._rotationAngleMRI_axial,
                            self._rotationAngleMRI_coronal, self._rotationAngleMRI_sagittal)

            self.readImMRI.metadata['rot_axial'] = self._rotationAngleMRI_axial
            self.readImMRI.metadata['rot_sagittal'] = self._rotationAngleMRI_sagittal
            self.readImMRI.metadata['rot_coronal'] = self._rotationAngleMRI_coronal


            self.progressBarSaving.setValue(80)

            self.readImMRI.updateData(im, rot_mat, type='t1')
            self.updateDispMRI(self.readImMRI.npImage, self.readImMRI.npSeg, initialState=True, tract=self.readImMRI.tract)

            self.progressBarSaving.setValue(100)
            self.setEnabled(True)
            self.dockWidget_3.setVisible(False)
            self.progressBarSaving.setValue(0)

    def create_cursors(self):
        """
        Create desired cursors
        :return:
        """
        bitmap = QtGui.QPixmap(source_folder+"/Hand.png")
        self.cursorOpenHand = QtGui.QCursor(bitmap)


        bitmap = QtGui.QPixmap(source_folder+"/Handsqueezed.png")
        self.cursorClosedHand = QtGui.QCursor(bitmap)


        bitmap = QtGui.QPixmap(source_folder+"/zoom_in.png")
        self.cursorZoomIn = QtGui.QCursor(bitmap)


        bitmap = QtGui.QPixmap(source_folder+"/zoom_out.png")
        self.cursorZoomOut = QtGui.QCursor(bitmap)



        bitmap = QtGui.QPixmap(source_folder+"/rotate.png")
        self.cursorRotate = QtGui.QCursor(bitmap)


        #bitmap = QtGui.QPixmap(source_folder+"/arrow.png")
        self.cursorArrow = QtGui.QCursor(Qt.ArrowCursor)

        self.setCursor(self.cursorArrow)



    def init_state(self):
        """
        Initial state
        :return:
        """
        self.toolBar.setVisible(True)
        self.actionMain_Toolbar.setChecked(True)
        self.actionrotate.setChecked(False)




    def save(self):
        """
        saving current state
        :return:
        """
        if self._basefileSave != '':
            self.dockWidget_3.setVisible(True)
            self.setEnabled(False)
            self.progressBarSaving.setValue(0)

            self.saveChanges()

            self.progressBarSaving.setValue(100)
            self.setEnabled(True)
            self.dockWidget_3.setVisible(False)
            self.progressBarSaving.setValue(0)


    def saveas(self):
        """
        Save as
        :return:
        """
        filters = "BrainNeonatal (*.bn)"
        opts =QtWidgets.QFileDialog.DontUseNativeDialog
        fileObj = QtWidgets.QFileDialog.getSaveFileName( self, "Open File", self.source_dir, filters, options=opts)
        if fileObj[0] == '':
            return
        self._basefileSave, _ = os.path.splitext(fileObj[0])
        self.dockWidget_3.setVisible(True)
        self.setEnabled(False)

        self.progressBarSaving.setValue(0)

        self.saveChanges()

        self.setEnabled(True)
        self.dockWidget_3.setVisible(False)
        self.progressBarSaving.setValue(0)



    def save_eco_to_nifti(self):
        """
        Save US iamge to NIFTI
        :return:
        """
        from melage.utils.utils import save_modified_nifti
        if not hasattr(self, 'readImECO'):
            return
        try:
            self.dockWidget_3.setVisible(True)
            self.setEnabled(False)
            self.progressBarSaving.setValue(0)

            self.saveChanges()


            status =save_modified_nifti(self.readImECO, self.source_dir, self.filenameEco)

            self.progressBarSaving.setValue(100)
            self.setEnabled(True)
            self.dockWidget_3.setVisible(False)
            self.progressBarSaving.setValue(0)

        except Exception as e:
            print(e)
            return e
        return True

    def convert(self):
        """
        Data Conversion
        :return:
        """
        from melage.utils.utils import save_as_nifti, save_as_nrrd, save_as_dicom

        filters = "DICOM (*.dcm);;Nifti (*.nia *.nii *.nii.gz *.hdr *.img *.img.gz *.mgz);;NRRD (*.nrrd *.nhdr)"
        opts =QtWidgets.QFileDialog.DontUseNativeDialog
        fileObj = QtWidgets.QFileDialog.getSaveFileName( self, "Open File", self.source_dir, filters, options=opts)

        if  fileObj[1] != '' and hasattr(self, 'readImECO'):
            outfile_format = filters.split(';;').index(fileObj[1])
            if self.readImECO.success:
                file_path, file_extension = os.path.splitext(fileObj[0])
                self.setCursor(QtCore.Qt.WaitCursor)
                if outfile_format == 0: # DICOM
                    save_as_dicom(self.npImage, self.readImECO.metadata_dict, file_path)
                elif outfile_format == 1: # NIFTI
                    save_as_nifti(self.npImage, self.readImECO.metadata_dict, file_path)
                elif outfile_format == 2: # NRRD
                    save_as_nrrd(self.npImage, self.readImECO.metadata_dict, file_path)
                self.setCursor(QtCore.Qt.ArrowCursor)


    def save_changes_auto(self):
        """
        Automatic saving project
        :return:
        """
        tm = time.time() - self.startTime
        if tm  > self.expectedTime:
            try:
                self.dockWidget_3.setVisible(True)
                self.setEnabled(False)
                self.progressBarSaving.setValue(0)
                print(tm, 'Automatic Saving')
                self.saveChanges()
                self.setEnabled(True)
                self.dockWidget_3.setVisible(False)
                self.progressBarSaving.setValue(0)
                self.startTime = time.time()

            except Exception as e:
                print(e)
                print('Save changes error')
                self.setEnabled(True)
                self.dockWidget_3.setVisible(False)
                self.progressBarSaving.setValue(0)

    #def mouseReleaseEvent(self, event):

        ##################################################self.save_changes_auto()
        #return super(Ui_Main, self).mousePressEvent(event)


     #   pass
     #   if event.type() == Qt.RightButton and self.cursorOpenHand.mask().cacheKey() == self.cursor().mask().cacheKey(): # Open hand cursor
      #      self.pan(True, cursor_open = False)


    #def mouseReleaseEvent(self, event):
     #   if self.cursorClosedHand.mask().cacheKey() == self.cursor().mask().cacheKey():  # closed hand cursor
      #      self.pan(True, cursor_open = True)

    def changedTab(self):
        """
        Changing the tabe
        :return:
        """
        if self.tabWidget.currentIndex() == 0:
            widgets_num = [0, 1, 2, 3, 4, 5]
        elif self.tabWidget.currentIndex() == 2:
            widgets_num = [10, 13]
        elif self.tabWidget.currentIndex() == 3:
            widgets_num = [11, 23]
        else:
            widgets_num = []
        #widgets = select_proper_widgets(self)
        for k in widgets_num:
            name = 'openGLWidget_' + str(k + 1)
            nameS = 'horizontalSlider_' + str(k + 1)
            widget = getattr(self, name)
            if k == 23:
                try:
                    self.openGLWidget_24.paint(self.readImMRI.npSeg, self.readImMRI.npImage, None)
                except:
                    pass
            elif k == 13:
                try:
                    self.openGLWidget_14.paint(self.readImECO.npSeg, self.readImECO.npImage, None)
                except:
                    pass
            else:
                if widget.imSlice is not None:
                    #if k == 10:
                    #    self.changeToSagittal()
                    #else:
                    slider = getattr(self, nameS)
                    slider.setRange(0, widget.imDepth)
                    slider.setValue(widget.sliceNum)
                    widget.UpdatePaintInfo()
                    if k in widgets_num:
                        widget.makeObject()
                        widget.update()
        #if self.tabWidget.currentIndex() == 2:
        #    if self.openGLWidget_24.
        #    self.openGLWidget_24.paint(self.readImMRI.npSeg, None, None)
        #elif self.tabWidget.currentIndex() == 3:
        #    self.openGLWidget_14.paint(self.readImECO.npSeg, None, None)



    def eventFilter(self, obj, event):
        from PyQt5.QtCore import QEvent

        if event.type() ==QEvent.Resize: # window resizing
            for k in range(12):
                name = 'openGLWidget_' + str(k + 1)
                widget = getattr(self, name)
                if widget.imSlice is not None:
                    widget.UpdatePaintInfo()
                    widget.update()

        if event.type() == QEvent.UpdateRequest:
            pass
        elif event.type() == QEvent.MouseButtonRelease:
            self.MouseButtonRelease = True


        if (event.type() == QEvent.KeyPress):
            if event.key() == Qt.Key_Control:
                if self.openGLWidget_1.hasFocus():
                    self.openGLWidget_2.zRot = self.openGLWidget_1.zRot
                    self.openGLWidget_2.update()



        return QtWidgets.QWidget.eventFilter(self, obj, event)


    def manual(self):

        """
        HELP MELAGE
        :return:
        """
        url = os.path.join(os.path.dirname(source_folder), 'README.html')
        QtGui.QDesktopServices.openUrl(QtCore.QUrl.fromLocalFile(url))


        """
        
        try:
            import webbrowser
 
            webbrowser.open(url,new=2)
        except:
            pass
        """




    def about(self):
        """
        About MELAGE
        :return:
        """
        from melage.widgets.melageAbout import about_dialog
        try:
            dialog = about_dialog(self, source_folder)
            dialog.show()
        except Exception as e:
            print(e)

        #MessageBox = QtWidgets.QMessageBox(self)
        #MessageBox.setText(' MELAGE \n Hospital Puerta del Mar\n March 2021')
        #MessageBox.show()

    def main_toolbar_visibility(self, value):
        self.toolBar.setVisible(value)
        if self.actionMain_Toolbar.isChecked():
            self.toolBar.setVisible(True)
        else:
            self.toolBar.setVisible(False)


    def changeToCoronal(self, typw='eco'):
        """
        Change to coronal
        :param typw:
        :return:
        """
        if typw == 'eco':
            changeCoronalSagittalAxial(self.horizontalSlider_11, self.openGLWidget_11,
                                       self.readImECO, 'coronal', 3, self.label_11, initialState = True, tol_slice=self.tol_trk)

            self.radioButton_1.setChecked(True)
            self.radioButton_2.setChecked(False)
            self.radioButton_3.setChecked(False)
        elif typw == 'mri':
            changeCoronalSagittalAxial(self.horizontalSlider_12, self.openGLWidget_12,
                                       self.readImMRI, 'coronal', 3, self.label_12, initialState = True, tol_slice=self.tol_trk)

            self.radioButton_21_1.setChecked(True)
            self.radioButton_21_2.setChecked(False)
            self.radioButton_21_3.setChecked(False)


    def changeToSagittal(self, typw='eco'):
        """
        Changing to sagittal
        :param typw:
        :return:
        """
        if typw == 'eco':
            changeCoronalSagittalAxial(self.horizontalSlider_11, self.openGLWidget_11,
                                   self.readImECO, 'sagittal', 1, self.label_11, initialState = True, tol_slice=self.tol_trk)
            self.radioButton_1.setChecked(False)
            self.radioButton_2.setChecked(True)
            self.radioButton_3.setChecked(False)
        elif typw == 'mri':
            changeCoronalSagittalAxial(self.horizontalSlider_12, self.openGLWidget_12,
                                       self.readImMRI, 'sagittal', 1, self.label_12, initialState = True, tol_slice=self.tol_trk)

            self.radioButton_21_1.setChecked(False)
            self.radioButton_21_2.setChecked(True)
            self.radioButton_21_3.setChecked(False)


    def changeToAxial(self, typw='eco'):
        if typw == 'eco':
            changeCoronalSagittalAxial(self.horizontalSlider_11, self.openGLWidget_11,
                                   self.readImECO, 'axial', 5, self.label_11, initialState = True, tol_slice=self.tol_trk)
            self.radioButton_1.setChecked(False)
            self.radioButton_2.setChecked(False)
            self.radioButton_3.setChecked(True)
        elif typw == 'mri':
            changeCoronalSagittalAxial(self.horizontalSlider_12, self.openGLWidget_12,
                                       self.readImMRI, 'axial', 5, self.label_12, initialState=True, tol_slice=self.tol_trk)

            self.radioButton_21_1.setChecked(False)
            self.radioButton_21_2.setChecked(False)
            self.radioButton_21_3.setChecked(True)


    def changeSightTab3(self, value):
        """

        :param value:
        :return:
        """
        if self.allowChangeScn:
            updateSight(self.horizontalSlider_11, self.openGLWidget_11, self.readImECO, value, tol_slice=self.tol_trk)

    def changeSightTab4(self, value):
        if self.allowChangeScn:
            updateSight(self.horizontalSlider_12, self.openGLWidget_12, self.readImMRI, value, tol_slice=self.tol_trk)

    def changeSight1(self, value):
        if self.allowChangeScn:
            updateSight(self.horizontalSlider_1, self.openGLWidget_1, self.readImECO, value, tol_slice=self.tol_trk)


    def changeSight2(self, value):
        if self.allowChangeScn:
            updateSight(self.horizontalSlider_2, self.openGLWidget_2, self.readImECO, value, tol_slice=self.tol_trk)

    def changeSight3(self, value):
        if self.allowChangeScn:
            updateSight(self.horizontalSlider_3, self.openGLWidget_3, self.readImECO, value, tol_slice=self.tol_trk)

    def changeSight4(self, value):
        if self.allowChangeScn:
            updateSight(self.horizontalSlider_4, self.openGLWidget_4, self.readImMRI, value, tol_slice=self.tol_trk)


    def changeSight5(self, value):
        if self.allowChangeScn:
            updateSight(self.horizontalSlider_5, self.openGLWidget_5, self.readImMRI, value, tol_slice=self.tol_trk)



    def changeSight6(self, value):
        if self.allowChangeScn:
            updateSight(self.horizontalSlider_6, self.openGLWidget_6, self.readImMRI, value, tol_slice=self.tol_trk)




    def updateDispEco(self, npImage = None, npSeg = None, initialState= False):
        """
        Updating US image
        :param npImage:
        :param npSeg:
        :param initialState:
        :return:
        """
        if npImage is None:
            return
        #if not '9876_Combined' in self.dw2Text:
        #    self.dw2Text.append('9876_Combined')
        self.allowChangeScn = False
        self.ImageEnh_view1.setVisible(True)
        self.tree_colors.setVisible(True)
        #ind, colorPen = self.colorsCombinations[self.dw2Text.index(self.dw2_cb.currentText())]
        ind = 9876#self.dw2Text.index(self.dw2_cb.currentText())+1

        colorPen = [1, 0, 0, 1]



        #self.labelLeft_1.setText(str_conv(self.readImECO.ImOrigin[1]))
        #self.labelRight_1.setText(str_conv(self.readImECO.ImEnd[1]))
        #self.labelCenter_1.setText(str_conv(self.readImECO.ImCenter[1]))
        if self.horizontalSlider_1.maximum()!= self.readImECO.ImExtent[3]-1:
            self.horizontalSlider_1.setRange(0, self.readImECO.ImExtent[3])
            self.horizontalSlider_1.setValue(self.readImECO.ImExtent[3]//2)
            self.label_1.setText(str_conv(self.readImECO.ImExtent[3] // 2))

        if self.horizontalSlider_2.maximum()!= self.readImECO.ImExtent[1]-1:
            self.horizontalSlider_2.setRange(0, self.readImECO.ImExtent[1])
            self.horizontalSlider_2.setValue(self.readImECO.ImExtent[1]//2)
            self.label_2.setText(str_conv(self.readImECO.ImExtent[1] // 2))

        if self.horizontalSlider_3.maximum() != self.readImECO.ImExtent[5]-1:
            self.horizontalSlider_3.setRange(0, self.readImECO.ImExtent[5])
            self.horizontalSlider_3.setValue(self.readImECO.ImExtent[5]//2)
            self.label_3.setText(str_conv(self.readImECO.ImExtent[5] // 2))

        if self.horizontalSlider_11.maximum() != self.readImECO.ImExtent[3]-1:
            self.horizontalSlider_11.setRange(0, self.readImECO.ImExtent[3])
            self.horizontalSlider_11.setValue(self.readImECO.ImExtent[3]//2)
            self.label_11.setText(str_conv(self.readImECO.ImExtent[3]//2))

        self.openGLWidget_1.updateCurrentImageInfo(npImage.shape)
        self.openGLWidget_2.updateCurrentImageInfo(npImage.shape)
        self.openGLWidget_3.updateCurrentImageInfo(npImage.shape)
        self.openGLWidget_11.currentWidnowName = 'coronal'
        self.openGLWidget_11.updateCurrentImageInfo(npImage.shape)

        """
        sliceNum = self.horizontalSlider_1.value()
        self.openGLWidget_1.points = []
        self.openGLWidget_1.updateInfo(*getCurrentSlice(self.openGLWidget_1,
                                                        npImage, npSeg, sliceNum), sliceNum, npImage.shape, initialState)
        self.openGLWidget_1.colorObject = colorPen
        self.openGLWidget_1.colorInd = ind
        self.openGLWidget_1.update()
        """






        self.radioButton_1.setVisible(True)
        self.radioButton_2.setVisible(True)
        self.radioButton_3.setVisible(True)
        self.radioButton_4.setVisible(True)




        name_lbl = 'label_'
        name_widg = 'openGLWidget_'
        name_slider = 'horizontalSlider_'

        for i in [1,2,3,11]:
            widget = getattr(self, name_widg+str(i))
            slider = getattr(self, name_slider+str(i))
            widget.colorObject = colorPen
            widget.colorInd = ind
            widget.setVisible(True)
            slider.setVisible(True)
            widget.points = []
            sliceNum = slider.value()
            widget.updateInfo(*getCurrentSlice(widget,
                                                             npImage, npSeg, sliceNum, tol_slice=self.tol_trk), sliceNum, npImage.shape,
                                            initialState=initialState, imSpacing=self.readImECO.ImSpacing)
            widget.update()

        """
        
        self.openGLWidget_11.colorObject = colorPen
        self.openGLWidget_11.colorInd = ind
        self.openGLWidget_11.points = []
        sliceNum = self.horizontalSlider_11.value()
        self.openGLWidget_11.updateInfo(*getCurrentSlice(self.openGLWidget_11,
                                                        npImage, npSeg, sliceNum), sliceNum, npImage.shape, initialState = initialState)
        self.openGLWidget_11.update()


        self.openGLWidget_2.colorObject = colorPen
        self.openGLWidget_2.colorInd = ind
        self.openGLWidget_2.points = []
        sliceNum = self.horizontalSlider_2.value()
        self.openGLWidget_2.updateInfo(*getCurrentSlice(self.openGLWidget_2,
                                                         npImage, npSeg, sliceNum), sliceNum, npImage.shape, initialState = initialState)
        self.openGLWidget_2.update()




        self.openGLWidget_3.colorObject = colorPen
        self.openGLWidget_3.colorInd = ind
        self.openGLWidget_3.points = []
        sliceNum = self.horizontalSlider_3.value()
        self.openGLWidget_3.updateInfo(*getCurrentSlice(self.openGLWidget_3,
                                                        npImage, npSeg, sliceNum), sliceNum, npImage.shape, initialState = initialState)
        self.openGLWidget_3.setVisible(True)
        self.openGLWidget_3.update()
        """
        if not initialState:
            self.openGLWidget_14.clear()
            self.openGLWidget_14._seg_im = None
            self.openGLWidget_14.paint(self.readImECO.npSeg,
                                       self.readImECO.npImage, None)
            self.openGLWidget_14.colorInd = ind
            self.openGLWidget_14.paint(self.readImECO.npSeg, self.readImECO.npImage, None)
        else:
            self.openGLWidget_14._image = self.readImECO.npImage

        self.allowChangeScn = True



    def updateDispMRI(self, npImage = None, npSeg = None, initialState = False, tract=None):
        """
        Update MRI
        :param npImage:
        :param npSeg:
        :param initialState:
        :param tract:
        :return:
        """
        if npImage is None:
            return
        try:
            self.page1_mri.setVisible(True)
            self.tree_colors.setVisible(True)
            self.allowChangeScn = False
            colorPen = [1, 0, 0, 1]
            ind = 9876
            #try:
            #    ind = self.dw2Text.index('X_Combined')+1
            #    colorPen = self.colorsCombinations[ind]
            #except:
            #    colorPen = [1,0,0,1]
            #    ind = 1

            self.horizontalSlider_4.setRange(0, self.readImMRI.ImExtent[3])
            self.horizontalSlider_4.setValue(self.readImMRI.ImExtent[3]//2)
            self.label_4.setText(str_conv(self.readImMRI.ImExtent[3] // 2))
            self.label_4.setVisible(True)
            self.horizontalSlider_5.setRange(0, self.readImMRI.ImExtent[1])
            self.horizontalSlider_5.setValue(self.readImMRI.ImExtent[1]//2)
            self.label_5.setText(str_conv(self.readImMRI.ImExtent[1]//2))
            self.label_5.setVisible(True)
            self.horizontalSlider_6.setRange(0, self.readImMRI.ImExtent[5])
            self.horizontalSlider_6.setValue(self.readImMRI.ImExtent[5]//2)
            self.label_6.setText(str_conv(self.readImMRI.ImExtent[5]//2))
            self.label_6.setVisible(True)
            self.openGLWidget_4.updateCurrentImageInfo(npImage.shape)
            self.openGLWidget_5.updateCurrentImageInfo(npImage.shape)
            self.openGLWidget_6.updateCurrentImageInfo(npImage.shape)


            self.horizontalSlider_12.setRange(0, self.readImMRI.ImExtent[3])
            self.horizontalSlider_12.setValue(self.readImMRI.ImExtent[3]//2)
            self.label_12.setText(str_conv(self.readImMRI.ImExtent[3]//2))

            self.openGLWidget_12.currentWidnowName = 'coronal'
            self.openGLWidget_12.updateCurrentImageInfo(npImage.shape)

            self.radioButton_21.setVisible(True)
            self.radioButton_21_1.setVisible(True)
            self.radioButton_21_2.setVisible(True)
            self.radioButton_21_3.setVisible(True)

            name_lbl = 'label_'
            name_widg = 'openGLWidget_'
            name_slider = 'horizontalSlider_'

            for i in [4,5,6,12]:
                widget = getattr(self, name_widg+str(i))
                slider = getattr(self, name_slider+str(i))
                widget.colorObject = colorPen
                widget.colorInd = ind
                widget.setVisible(True)
                slider.setVisible(True)
                widget.points = []
                sliceNum = slider.value()
                widget.updateInfo(*getCurrentSlice(widget,
                                                                 npImage, npSeg, sliceNum, tract, tol_slice=self.tol_trk), sliceNum, npImage.shape,
                                                initialState=initialState, imSpacing=self.readImMRI.ImSpacing)
                widget.update()
            if not initialState:
                self.openGLWidget_24.clear()
                self.openGLWidget_24._seg_im = None
                self.openGLWidget_24.paint(self.readImMRI.npSeg,
                                           self.readImMRI.npImage, None)
                self.openGLWidget_24.colorInd = ind
            else:
                self.openGLWidget_24._image = self.readImMRI.npImage
            self.allowChangeScn = True
        except Exception as e:
            self.warning_msgbox(
                '{} There is something wrong please check the file.'.format(e))


    def BEDL_back(self, value, forward=1):
        """
        Backtransforming the enhanced image
        :param value:
        :return:
        """
        if forward:
            if value == 0:
                if not hasattr(self, 'readImECO'):
                    return
                reader = self.readImECO
                widgets_num = [0, 1, 2, 10]
            elif value == 1:
                if not hasattr(self, 'readImMRI'):
                    return
                reader = self.readImMRI
                widgets_num = [3, 4, 5, 10]
            else:
                return
            if not hasattr(reader, 'npImage'):
                return

            save_var = '_immri_bedl_{}'.format(value)
            save_var_seg = '_immri_bedl_seg_{}'.format(value)
            if not hasattr(self, save_var):
                setattr(self, save_var, reader.im.__class__(reader.im.dataobj[:], reader.im.affine, reader.im.header))
                setattr(self, save_var_seg, reader.npSeg)
            reader.im = out
            reader.set_metadata()
            reader.read_pars()
            if value == 0:
                self.setNewImage.emit(reader.npImage.shape)
            elif value == 1:
                self.setNewImage2.emit(reader.npImage.shape)
            self.tabWidget.setTabVisible(3, True)
            self.changedTab()
            for k in widgets_num:
                name = 'openGLWidget_' + str(k + 1)
                widget = getattr(self, name)
                widget.makeObject()
                widget.update()
            if value == 0:
                self.updateDispEco(reader.npImage, reader.npSeg, initialState=True)
                if self.N4_dialog._shrinkfactor > 1:
                    self.reset_page1_eco()
                    self.toolBar2.setDisabled(False)
                    self._rotationAngleEco_coronal = 0
                    self._rotationAngleEco_axial = 0
                    self._rotationAngleEco_sagittal = 0
                    self.hs_t1_5.setValue(0)

                    txt = compute_volume(self.readImECO, self.filenameEco, [9876], in_txt=self.openedFileName.text(),
                                         ind_screen=0)
                    self.openedFileName.setText(txt)

            if value == 1:
                self.updateDispMRI(reader.npImage, reader.npSeg, initialState=True, tract=reader.tract)
                if self.N4_dialog._shrinkfactor > 1:
                    self.reset_page1_mri()
                    self.hs_t2_5.setValue(0)
                    self.toolBar2.setDisabled(False)
                    txt = compute_volume(reader, self.filenameMRI, [9876], in_txt=self.openedFileName.text(),
                                         ind_screen=1)
                    self.openedFileName.setText(txt)


                self._rotationAngleMRI_coronal = 0
                self._rotationAngleMRI_axial = 0
                self._rotationAngleMRI_sagittal = 0
            self.BE_DL.backbutton.setVisible(True)
        else:
            if value == 0:
                if not hasattr(self, 'readImECO'):
                    return
                reader = self.readImECO
                widgets_num = [0, 1, 2, 10]
            elif value==1:
                if not hasattr(self, 'readImMRI'):
                    return
                reader = self.readImMRI
                widgets_num = [3, 4, 5, 10]
            else:
                return
            if not hasattr(reader, 'npImage'):
                return


            save_var = '_immri_bedl_{}'.format(value)
            save_var_seg = '_immri_bedl_seg_{}'.format(value)
            if not hasattr(self, save_var):
                return
            #reader.im = self._immri_tmp
            reader.im = getattr(self, save_var)
            reader.set_metadata()
            reader.read_pars()
            self.setNewImage2.emit(reader.npImage.shape)
            reader.npSeg = getattr(self, save_var_seg)
            delattr(self, save_var_seg)
            delattr(self, save_var)

            self.tabWidget.setTabVisible(3, True)

            for k in widgets_num:
                name = 'openGLWidget_' + str(k + 1)
                widget = getattr(self, name)
                widget.makeObject()
                widget.update()
            # self.readImMRI.npImage = standardize(self.readImMRI.npImage)
            if value==0:
                self.updateDispEco(reader.npImage, reader.npSeg, initialState=True)
                self._rotationAngleEco_coronal = 0
                self._rotationAngleEco_axial = 0
                self._rotationAngleEco_sagittal=0
            elif value == 1:
                self.updateDispMRI(reader.npImage, reader.npSeg, initialState=True, tract=reader.tract)
                self._rotationAngleMRI_coronal = 0
                self._rotationAngleMRI_axial = 0
                self._rotationAngleMRI_sagittal=0


    def N4_back(self, value):
        """
        N4 image processing
        :param value:
        :return:
        """
        if value == 0:
            if not hasattr(self, 'readImECO'):
                return
            reader = self.readImECO
            widgets_num = [0, 1, 2, 10]
        elif value==1:
            if not hasattr(self, 'readImMRI'):
                return
            reader = self.readImMRI
            widgets_num = [3, 4, 5, 10]
        else:
            return
        if not hasattr(reader, 'npImage'):
            return


        save_var = '_immri_tmp_{}'.format(value)
        save_var_seg = '_immri_tmp_seg_{}'.format(value)
        if not hasattr(self, save_var):
            return
        #reader.im = self._immri_tmp
        reader.im = getattr(self, save_var)
        reader.set_metadata()
        reader.read_pars()
        self.setNewImage2.emit(reader.npImage.shape)
        reader.npSeg = getattr(self, save_var_seg)
        delattr(self, save_var_seg)
        delattr(self, save_var)

        self.tabWidget.setTabVisible(3, True)

        for k in widgets_num:
            name = 'openGLWidget_' + str(k + 1)
            widget = getattr(self, name)
            widget.makeObject()
            widget.update()
        # self.readImMRI.npImage = standardize(self.readImMRI.npImage)
        if value==0:
            self.updateDispEco(reader.npImage, reader.npSeg, initialState=True)
            self._rotationAngleEco_coronal = 0
            self._rotationAngleEco_axial = 0
            self._rotationAngleEco_sagittal=0
        elif value == 1:
            self.updateDispMRI(reader.npImage, reader.npSeg, initialState=True, tract=reader.tract)
            self._rotationAngleMRI_coronal = 0
            self._rotationAngleMRI_axial = 0
            self._rotationAngleMRI_sagittal=0

    def print(self):
        print('salam')

    def N4_correction(self, value):
        """
        N4 correction
        :param value:
        :return:
        """
        if value == 0:
            if not hasattr(self, 'readImECO'):
                return
            reader = self.readImECO
            widgets_num = [0, 1, 2, 10]
        elif value==1:
            if not hasattr(self, 'readImMRI'):
                return
            reader = self.readImMRI
            widgets_num = [3, 4, 5, 10]
        else:
            return
        if not hasattr(reader, 'npImage'):
            return

        save_var = '_immri_tmp_{}'.format(value)
        save_var_seg = '_immri_tmp_seg_{}'.format(value)
        if not hasattr(self, save_var):
            setattr(self, save_var, reader.im.__class__(reader.im.dataobj[:], reader.im.affine, reader.im.header))
            setattr(self, save_var_seg, reader.npSeg)

        self.setEnabled(False)
        self.N4_dialog.inputimage = reader.im
        self.N4_dialog.setEnabled(False)


        worker = Worker(0)
        worker.inputimage = reader.im
        #QtCore.QCoreApplication.processEvents()

        thread = QtCore.QThread()
        def on_quit():
            thread.quit()
            thread.wait()
        worker.moveToThread(thread)
        worker.set_params(reader.npImage, self.N4_dialog.params, reader.im.affine)
        thread.started.connect(worker.run)
        #worker.finished.connect(worker.deleteLater)
        worker.finished.connect(on_quit)
        #thread.finished.connect(thread.deleteLater)
        thread.start()

        self.N4_dialog.progressBar.setVisible(True)

        self.N4_dialog.progressBar.setValue(10)
        self.app.processEvents()
        worker.run()
        self.setEnabled(True)
        self.N4_dialog.setEnabled(True)
        self.N4_dialog.progressBar.setValue(100)
        self.N4_dialog.progressBar.setVisible(False)
        if worker.out is not None:
            out = worker.out
        else:
            return

        #out = self.N4_dialog.execute()
        #self.inputimage = None
        #self.N4_dialog.setEnabled(True)

        reader.im = out
        reader.set_metadata()
        reader.read_pars()
        if self.N4_dialog._shrinkfactor>1:
            if value==0:
                self.setNewImage.emit(reader.npImage.shape)
            elif value==1:
                self.setNewImage2.emit(reader.npImage.shape)
        self.tabWidget.setTabVisible(3, True)
        self.changedTab()
        for k in widgets_num:
            name = 'openGLWidget_' + str(k + 1)
            widget = getattr(self, name)
            widget.makeObject()
            widget.update()
        if value==0:
            self.updateDispEco(reader.npImage, reader.npSeg, initialState=True)
            if self.N4_dialog._shrinkfactor > 1:
                self.reset_page1_eco()
                self.toolBar2.setDisabled(False)
                self._rotationAngleEco_coronal = 0
                self._rotationAngleEco_axial = 0
                self._rotationAngleEco_sagittal = 0
                self.hs_t1_5.setValue(0)
                # self.openedFileName.setText('Eco: {}, \n MRI: {}'.format(self.filenameEco, self.filenameMRI))
                #txt = 'File: {}, TV: {}'.format(self.filenameEco,
                #                                self.readImECO.npSeg.sum() * self.readImECO.ImSpacing[0] ** 3)
                #self.openedFileName.setText(txt)
                txt = compute_volume(self.readImECO, self.filenameEco, [9876], in_txt=self.openedFileName.text(),
                                     ind_screen=1)
                self.openedFileName.setText(txt)

        if value==1:
            self.updateDispMRI(reader.npImage, reader.npSeg, initialState=True, tract=reader.tract)
            if self.N4_dialog._shrinkfactor>1:
                self.reset_page1_mri()
                self.hs_t2_5.setValue(0)
                self.toolBar2.setDisabled(False)
                txt = compute_volume(reader, self.filenameMRI, [9876], in_txt=self.openedFileName.text(),
                                     ind_screen=1)
                self.openedFileName.setText(txt)
                #self.openedFileName.setText(
                #    'File: {}, TV: {}'.format(self.filenameMRI,
                #                              reader.npSeg.sum() * reader.ImSpacing[0]))

            self._rotationAngleMRI_coronal = 0
            self._rotationAngleMRI_axial = 0
            self._rotationAngleMRI_sagittal=0
        self.N4_dialog.pushButton_2.setVisible(True)

    def retranslateUi(self, Main):
        self._translate = QtCore.QCoreApplication.translate
        Main.setWindowTitle(self._translate("Main", "MELAGE"))
        self.menuFile.setTitle(self._translate("Main", "File"))
        self.menuAbout.setTitle(self._translate("Main", "Help"))
        self.menuView.setTitle(self._translate("Main", "View"))
        self.menuToolbar.setTitle(self._translate("Main", "Toolbars"))
        self.menuWidgets.setTitle(self._translate("Main", "Widgets"))
        self.actionOpenUS.setText(self._translate("Main", "Image View 1"))
        self.actionOpenMRI.setText(self._translate("Main", "Image View 2"))
        self.actionOpenFA.setText(self._translate("Main", "OpenFA"))
        self.actionLoad.setText(self._translate("Main", "Load project"))
        self.actionNew.setText(self._translate("Main", "New project"))
        self.actionFile_info.setText(self._translate("Main", "Settings"))
        self.actionFile_changeIM.setText(self._translate("Main", "Change IM"))
        self.actionfile_iminfo.setText(self._translate("Main", "Images Info."))
        #self.actionconvert.setText(self._translate("Main", "Convert"))
        #self.actionsaveModified.setText(self._translate("Main", "SAVE MODIFIED"))
        self.actionexit.setText(self._translate("Main", "Exit"))
        self.actionabout.setText(self._translate("Main", "About"))
        self.actionmanual.setText(self._translate("Main", "Help"))
        self.actionVersion.setText(self._translate("Main", "Version 2.1.1"))
        #self.pushButton.setText(self._translate("Main", "PushButton"))
        self.toolBar.setWindowTitle(self._translate("Main", "Main ToolBar"))
        self.toolBar2.setWindowTitle(self._translate("Main", "Interaction"))


        self.action_interaction_Toolbar.setText(self._translate("Main", "Interaction"))
        self.action_guideLines.setText(self._translate("Main", "Guides"))
        self.action_axisLines.setText(self._translate("Main", "Axis"))
        self.actionPan.setText(self._translate("Main", "Pan"))
        self.actionContour.setText(self._translate("Main", "Contour"))
        self.actionPoints.setText(self._translate("Main", "Point Selection"))
        self.actionCircles.setText(self._translate("Main", "Circle Selection"))
        self.actionGoTo.setText(self._translate("Main", "Link"))
        self.action3D.setText(self._translate("Main", "3D"))
        self.actionZoomIn.setText(self._translate("Main", "Zoom In"))
        self.actionZoomOut.setText(self._translate("Main", "Zoom Out"))
        self.actionContourX.setText(self._translate("Main", "Contour X times"))
        self.actionEraseX.setText(self._translate("Main", "Eraser X times"))
        self.actionPaint.setText(self._translate("Main", "Paint"))
        self.actionErase.setText(self._translate("Main", "Erase"))
        self.actionNNventricleGatherIm.setText(self._translate("Main", "Gather Current Segmentation to Image"))
        self.actionLazyContour.setText(self._translate("Main", "Zoom Out"))
        self.actionNNventricleSegm.setText(self._translate("Main", "NN Segmentation"))
        self.actionN4Bias.setText(self._translate("Main", "N4 Bias Field Correction"))
        self.actionTissueSeg.setText(self._translate("Main", "Tissue Seg"))
        self.actionHistImage.setText(self._translate("Main", "Image Histogram"))
        self.actionResizeImage.setText(self._translate("Main", "Resize"))
        self.actionBET.setText(self._translate("Main", "BET"))
        self.actionBEDL.setText(self._translate("Main", "DeepBET"))
        self.actionImageThresholding.setText(self._translate("Main", "Image Thresholding"))
        self.actionImageRegistration.setText(self._translate("Main", "Image Registration"))
        self.actionImageTransformation.setText(self._translate("Main", "Image Transformation"))
        self.actionMasking.setText(self._translate("Main", "Image Masking"))
        self.actionOperationMask.setText(self._translate("Main", "Masking Operation"))
        self.actionChangeCS.setText(self._translate("Main", "Change CS"))
        self.actionNNVentriclesSagittal.setText(self._translate("Main", "Sagittal") )
        self.actionNNVentriclesCoronal.setText( self._translate("Main", "Coronal") )
        self.actionNNVentriclesAxial.setText( self._translate("Main", "Axial") )
        self.actionrotate.setText(self._translate("Main", "Rotate"))
        self.actionArrow.setText(self._translate("Main", "Arrow"))
        self.menuTools.setTitle(self._translate("Main", "Tools"))
        self.menuBasicInfo.setTitle(self._translate("Main", "Basic Info"))
        self.menuCalc.setTitle(self._translate("Main", "Calc"))
        self.menuPreprocess.setTitle(self._translate("Main", "Preprocessing"))
        self.menuSegmentation.setTitle(self._translate("Main", "Segmentation"))
        self.menuRegistration.setTitle(self._translate("Main", "Registeration"))

        self.menuExport.setTitle(self._translate("Main", "Export"))
        self.menuImport.setTitle(self._translate("Main", "Import"))
        self.menuTV.setTitle(self._translate("Main", "Total Volume"))
        self.actionTVCor.setText(self._translate("Main", "Coronal"))
        self.actionTVSag.setText(self._translate("Main", "Sagital"))
        self.actionTVAx.setText(self._translate("Main", "Axial"))
        self.menuSeg.setTitle( self._translate("Main", "Ventricle Segmentation") )
        self.actionMain_Toolbar.setText(self._translate("Main", "Main Toolbar"))
        self.actionsave.setText(self._translate("Main", "Save"))
        self.actionsaveas.setText(self._translate("Main", "Save as"))
        self.actionLine.setText(self._translate("Main", "Draw Line"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.mutulaViewTab), self._translate("Main", "Mutual view"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.reservedTab), self._translate("Main", "Rserved"))

        self.tabWidget.setTabText(self.tabWidget.indexOf(self.segmentationTab), self._translate("Main", "View 1"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.MRISegTab), self._translate("Main", "View 2"))
        self.tabWidget.setTabVisible(1, False)
        self.tabWidget.setStyleSheet("QTabBar::tab {"+"height: {}px; width: {}px;".format(self.height()//52,self.width()//12)+"}");
        #self.tabWidget.setTabVisible(2, False)
        #self.tabWidget.setTabVisible(3, False)


        self.radioButton_21_1.setText(self._translate("Main", "Coronal"))
        self.radioButton_21_2.setText(self._translate("Main", "Sagittal"))
        self.radioButton_21_3.setText(self._translate("Main", "Axial"))
        self.radioButton_21.setText(self._translate("Main", "Show Seg"))

        self.radioButton_1.setText(self._translate("Main", "Coronal"))
        self.radioButton_2.setText(self._translate("Main", "Sagittal"))
        self.radioButton_3.setText(self._translate("Main", "Axial"))
        self.radioButton_4.setText(self._translate("Main", "Show Seg"))



        self.actionUndo.setText(self._translate("Main", "Undo"))
        self.actionRedo.setText(self._translate("Main", "Redo"))
        #self.actionContourGen.setText(self._translate("Main", "Contour Gen from line"))
        manually_check_tree_item(self,'9876')


    def loadProject(self):
        """
        Loading saved project
        :return:
        """
        filters = "BrainNeonatal (*.bn)"
        opts =QtWidgets.QFileDialog.DontUseNativeDialog
        fileObj = QtWidgets.QFileDialog.getOpenFileName( self, "Open File", self.source_dir, filters, options=opts)
        if fileObj[0] != '':

            self._basefileSave, _ = os.path.splitext(fileObj[0])

            self.dockWidget_3.setVisible(True)
            self.setEnabled(False)

            self.progressBarSaving.setValue(0)
            self._loaded = False
            self.CloseUS(message_box='off')
            self.CloseMRI(message_box='off')
            self.loadChanges()

            self.activateGuidelines(False)
            self.progressBarSaving.setValue(100)
            self.setEnabled(True)
            self.dockWidget_3.setVisible(False)
            self.progressBarSaving.setValue(0)

            if self._openUSEnabled:
                self.actionOpenUS.setDisabled(False)
            self.actionOpenMRI.setDisabled(False)
            self.actionOpenFA.setDisabled(True)
            self.actionOpenTract.setDisabled(True)
            if rhasattr(self, 'readImECO.npImage'):
                self.actionImportSegEco.setDisabled(False)
                self.actionExportImEco.setDisabled(False)
                self.actionExportSegEco.setDisabled(False)

            if rhasattr(self, 'readImMRI.npImage'):
                self.actionImportSegMRI.setDisabled(False)
                self.actionExportImMRI.setDisabled(False)
                self.actionExportSegMRI.setDisabled(False)
            #self.actionImportSegMRI.setDisabled(False)
            self.actionsave.setDisabled(False)
            self.actionsaveas.setDisabled(False)
            self.toolBar2.setDisabled(False)
            self.startTime = time.time()

        else:
            return

    def newProject(self):
        opts = QtWidgets.QFileDialog.DontUseNativeDialog
        fileObj = QtWidgets.QFileDialog.getSaveFileName(self, "Open File", self.source_dir, options=opts)
        if fileObj[0] != '':

            self._basefileSave, _ = os.path.splitext(fileObj[0])
            if self._openUSEnabled:
                self.actionOpenUS.setDisabled(False)
            self.actionOpenMRI.setDisabled(False)

            self.actionOpenFA.setDisabled(True)
            self.actionOpenTract.setDisabled(True)
            self.actionsave.setDisabled(False)
            self.actionsaveas.setDisabled(False)
            self.reset_page1_eco()
            self.reset_page1_mri()
            widgets_num = [0, 1, 2, 3, 4, 5, 10, 11]
            for k in widgets_num:
                name = 'openGLWidget_' + str(k + 1)
                widget = getattr(self, name)
                widget.resetInit()
                widget.initialState()
            self.openGLWidget_14.clear()
            self.openGLWidget_24.clear()
            self.Main.setWindowTitle(self._translate("Main", os.path.basename(self._basefileSave)))
            self.save()


    def CloseUS(self, message_box='on'):
        def setVisible(val):

            self.actionImportSegEco.setDisabled(True)
            self.actionExportImEco.setDisabled(True)
            self.actionExportSegEco.setDisabled(True)


            self.radioButton_1.setVisible(val)
            self.radioButton_2.setVisible(val)
            self.radioButton_3.setVisible(val)
            self.radioButton_4.setVisible(val)
            for k in [1,2,3,11]:
                name = 'openGLWidget_' + str(k)
                slider = getattr(self, 'horizontalSlider_' + str(k))
                label = getattr(self, 'label_' + str(k))
                label.setVisible(val)
                slider.setVisible(val)
                widget = getattr(self, name)
                widget.setVisible(val)
                widget.imType = 'eco'
                widget.clear()
                widget.resetInit()
                widget.initialState()
        if message_box=='off':
            setVisible(False)
            self.reset_page1_eco()
            self.openGLWidget_14.clear()
            self.ImageEnh_view1.setVisible(False)
            #self.tree_colors.setVisible(False)

            # self.save()
            self.readImECO = []
            self.changedTab()
        else:
            qm = QtWidgets.QMessageBox(self)
            cond = qm.question(self, '', "Are you sure to close View 1?", qm.Yes | qm.No)
            if cond==qm.Yes:

                setVisible(False)
                self.reset_page1_eco()
                self.openGLWidget_14.clear()
                self.ImageEnh_view1.setVisible(False)
                #self.tree_colors.setVisible(False)
                #self.save()

                self.readImECO = []
                #self.changedTab()
                for k in  [4,5,6,12]:
                    name = 'openGLWidget_' + str(k)
                    widget = getattr(self, name)
                    event = QtGui.QResizeEvent(widget.size(), widget.size())
                    widget.resizeEvent(event)
                    widget.resize(QtCore.QSize(widget.size().width(), widget.size().height() * 2))
                #self.browseUS(use_dialog=False)
                self.actionComboBox_visible.setVisible(False)
                self.actionComboBox_visible.setDisabled(True)
                try:
                    self.actionComboBox.currentTextChanged.disconnect(self.changeVolume)
                    self.actionComboBox.setObjectName("View1")
                except:
                    pass
                self.actionComboBox.clear()

                clean_parent_image(self, -1, ['View 1'], index_view=0)
                #clean_parent_image2(self, fileObj[0], 'View 1', index_view=0)
                #self.changedTab()
            return cond




    def CloseMRI(self, message_box='on', dialogue=True):
        """
        Closing MRI image
        :param message_box:
        :param dialogue:
        :return:
        """
        def setVisible(val):
            self.actionImportSegMRI.setDisabled(True)
            self.actionExportImMRI.setDisabled(True)
            self.actionExportSegMRI.setDisabled(True)

            self.radioButton_21.setVisible(val)
            self.radioButton_21_1.setVisible(val)
            self.radioButton_21_2.setVisible(val)
            self.radioButton_21_3.setVisible(val)
            txt = self.openedFileName.text()
            division_ind = txt.find(' ; ')
            if division_ind!=-1:
                if division_ind != 0:
                    kept_part = txt[:division_ind - 1]
                else:
                    kept_part = ''
                self.openedFileName.setText(kept_part+' ; ')

            for k in [4,5,6,12]:
                slider = getattr(self, 'horizontalSlider_' + str(k))
                label = getattr(self, 'label_' + str(k))
                label.setVisible(val)
                slider.setVisible(val)

                name = 'openGLWidget_' + str(k)
                widget = getattr(self, name)
                widget.setVisible(val)
                widget.imType = 'mri'
                widget.clear()
                widget.resetInit()
                widget.initialState()

        if message_box=='off':
            setVisible(False)
            self.reset_page1_mri()
            self.openGLWidget_24.clear()
            # self.save()
            self.readImMRI = []
            self.page1_mri.setVisible(False)
            #self.tree_colors.setVisible(False)

        else:
            if dialogue:
                qm = QtWidgets.QMessageBox(self)
                ret = qm.question(self, '', "Are you sure to close View 2?", qm.Yes | qm.No)
                cond = ret==qm.Yes
            else:
                cond = True
            if cond:
                setVisible(False)
                self.reset_page1_mri()
                self.openGLWidget_24.clear()
                #self.save()
                self.readImMRI = []
                self.page1_mri.setVisible(False)
                #self.tree_colors.setVisible(False)
            for k in [1,2,3,11]:
                name = 'openGLWidget_' + str(k)
                widget = getattr(self, name)
                event = QtGui.QResizeEvent(widget.size(), widget.size())
                widget.resizeEvent(event)
                widget.resize(QtCore.QSize(widget.size().width(),widget.size().height()*2))
            self.actionComboBox_visible.setVisible(False)
            self.actionComboBox_visible.setDisabled(True)
            self.actionComboBox.setObjectName("View2")
            try:
                self.actionComboBox.currentTextChanged.disconnect(self.changeVolume)
            except:
                pass
            self.actionComboBox.clear()
            clean_parent_image(self, -1, ['View 2'], index_view=1)
            return cond

    def _check_status_warning_eco(self):

        if not hasattr(self, 'readImECO'):
            self.warning_msgbox('There is no UltraSound image')
            return False
        if not hasattr(self.readImECO, 'npImage'):
            self.warning_msgbox('There is no UltraSound image')
            return False
        return True

    def _check_status_warning_mri(self):
        if not hasattr(self, 'readImMRI'):
            self.warning_msgbox('There is no MRI image')
            return False
        if not hasattr(self.readImMRI, 'npImage'):
            self.warning_msgbox('There is no MRI image')
            return False
        return True

    def _filesave_dialog(self, filters,opts, pref='', currentCS=None):
        """
        Dialogue to save files
        :param filters:
        :param opts:
        :param pref:
        :param currentCS:
        :return:
        """
        #fileObj = QtWidgets.QFileDialog.getSaveFileName(self, "Open File", self.source_dir+'/'+pref, filters, options=opts)
        from melage.widgets.fileDialog_widget import QFileSaveDialogPreview
        #from melage.utils.utils import getCurrentCoordSystem
        check_save = True
        if hasattr(self, '_last_state_save_csv' ):
            check_save=self._last_state_save_csv
        dialg = QFileSaveDialogPreview(self, "Open File", self.source_dir+'/'+pref, filters, options=opts, check_state_csv=check_save)

        dialg.setCS(currentCS)


        #if dialg.exec_() == QFileSaveDialogPreview.Accepted:
        dialg.exec_()
        cs, from_to, save_csv = dialg.getInfo()
        self._last_state_save_csv = dialg.checkBox_csv.isChecked()
        fileObj = dialg.getFileSelected()
        fileObj[1] = dialg.selectedNameFilter()

        if fileObj[0] == '':
            self.warning_msgbox('No file name is selected')
        return fileObj, [cs, from_to, save_csv]


    def exportData(self, type):
        """
        Export data
        :param type:
        :return:
        """
        from melage.utils.utils import save_3d_img, export_tables
        def save_as_image(reader, file, img, format=0, type_im = 'mri', cs=['RAS', 'AS']):

            try:
                self.dockWidget_3.setVisible(True)
                self.setEnabled(False)

                self.progressBarSaving.setValue(0)
                if format==1:
                    save_3d_img(reader, file, img, 'tif', type_im=type_im, cs=cs)
                    export_tables(self, file[:-7] + "_table")
                elif format==0:

                    save_3d_img(reader, file, img, format='nifti', type_im=type_im, cs=cs)
                    export_tables(self, file+"_table")

                self.setEnabled(True)
                self.dockWidget_3.setVisible(False)
                self.progressBarSaving.setValue(0)
            except Exception as e:
                self.setEnabled(True)
                self.dockWidget_3.setVisible(False)
                self.progressBarSaving.setValue(0)
                print('save 3d image')

        filters = "NifTi (*.nii *.nii.gz *.mgz);;tif(*.tif)"
        opts = QtWidgets.QFileDialog.DontUseNativeDialog
        currentCS = 'RAS'
        if type.lower()=='usim':
            status = self._check_status_warning_eco()
            if not status:
                return
            try:
                #fl = '.'.join(self.filenameEco.split('.')[:-1])
                fl = self.filenameEco
                flfmt = [el for el in self._availableFormats if el in self.filenameMRI]
                flfmt = flfmt[flfmt.index(max(flfmt))]
                fl = fl.replace(flfmt, '')
                newn = fl + '_new'
            except:
                newn = ''
            if hasattr(self.readImECO, 'source_system'):
                currentCS = self.readImECO.source_system
            fileObj, cs = self._filesave_dialog(filters, opts, newn, currentCS=currentCS)
            if fileObj[0] != '':
                save_as_image(self.readImECO, fileObj[0], self.readImECO.npImage, format=filters.split(';;').index(fileObj[1]), type_im='eco', cs=cs)
        elif type.lower()=='usseg':
            status = self._check_status_warning_eco()
            if not status:
                return
            try:
                #fl = '.'.join(self.filenameEco.split('.')[:-1])
                fl = self.filenameEco
                flfmt = [el for el in self._availableFormats if el in self.filenameMRI]
                flfmt = flfmt[flfmt.index(max(flfmt))]
                fl = fl.replace(flfmt, '')
                newn = fl + '_seg'
            except:
                newn = ''
            if hasattr(self.readImECO, 'source_system'):
                currentCS = self.readImECO.source_system
            fileObj, cs = self._filesave_dialog(filters, opts, newn, currentCS=currentCS)
            if fileObj[0] != '':
                save_as_image(self.readImECO, fileObj[0], self.readImECO.npSeg, format=filters.split(';;').index(fileObj[1]), type_im='eco', cs=cs)
        elif type.lower()=='mriim':
            status = self._check_status_warning_mri()
            if not status:
                return
            try:
                #fl = '.'.join(self.filenameMRI.split('.')[:-1])
                fl = self.filenameMRI
                flfmt = [el for el in self._availableFormats if el in self.filenameMRI]
                flfmt = flfmt[flfmt.index(max(flfmt))]
                fl = fl.replace(flfmt, '')
                newn = fl + '_new'
            except:
                newn = ''
            if hasattr(self.readImMRI, 'source_system'):
                currentCS = self.readImMRI.source_system
            fileObj, currentCS = self._filesave_dialog(filters, opts, newn, currentCS=currentCS)
            if fileObj[0] != '':
                save_as_image(self.readImMRI, fileObj[0], self.readImMRI.npImage,format=filters.split(';;').index(fileObj[1]), cs=currentCS)
        elif type.lower()=='mriseg':
            status = self._check_status_warning_mri()
            if not status:
                return
            try:
                fl = self.filenameMRI
                flfmt = [el for el in self._availableFormats if el in self.filenameMRI]
                flfmt = flfmt[flfmt.index(max(flfmt))]
                fl = fl.replace(flfmt, '')
                #fl = '.'.join(self.filenameMRI.split('.')[:-1])
                newn = fl + '_seg'
            except:
                newn = ''

            if hasattr(self.readImMRI, 'source_system'):
                currentCS = self.readImMRI.source_system
            fileObj, cs = self._filesave_dialog(filters, opts, newn, currentCS=currentCS)
            if fileObj[0]!='':
                save_as_image(self.readImMRI, fileObj[0], self.readImMRI.npSeg, format=filters.split(';;').index(fileObj[1]), cs=cs)



    def closeImportData(self, type_image):
        """

        :param type_image:
        :return:
        """
        if type_image.lower()=='usseg':
            if hasattr(self, 'readImECO'):
                if hasattr(self.readImECO, 'npImage'):
                    self.readImECO.npSeg = self.readImECO.npImage*0
                    self.updateDispEco(self.readImECO.npImage, self.readImECO.npSeg, initialState=True)
        elif type_image.lower()=='mriseg':
            if hasattr(self, 'readImMRI'):
                if hasattr(self.readImMRI, 'npImage'):
                    self.readImMRI.npSeg = self.readImMRI.npImage*0
                    self.updateDispMRI(self.readImMRI.npImage, self.readImMRI.npSeg, initialState=True,
                                       tract=self.readImMRI.tract)



    def importData(self, type_image, fileObj=None):
        """
        Importing image data
        :param type_image:
        :param fileObj:
        :return:
        """
        from melage.utils.utils import read_segmentation_file, make_all_seg_visibl
        update_color_s = False # do not update color scheme
        if fileObj is None or type(fileObj)==bool:
            update_color_s = True
            opts =QtWidgets.QFileDialog.DontUseNativeDialog
            fileObj = QtWidgets.QFileDialog.getOpenFileName( self, "Open File", self.source_dir, self._filters, options=opts)
            if fileObj[0]=='':
                return False

        if type_image.lower()=='usseg':
            if hasattr(self, 'readImECO'):
                if hasattr(self.readImECO, 'npImage'):
                    npSeg, readable, equalDim = read_segmentation_file(self, fileObj[0], self.readImECO, update_color_s=update_color_s)
                    if not equalDim:
                        self.warning_msgbox(
                            'Expected segmentation with dimensions {}, but the segmentation has {}'.format(self.readImECO.npImage.shape, npSeg.shape))
                        return False
                    if not readable:
                        self.warning_msgbox('The number of colors are less than the segmentated parts. Unable to read the file.')
                        return False
                    if len(self.readImECO.npImage.shape) != len(npSeg.shape):
                        return False

                    self.readImECO.npSeg = npSeg.astype('int')
                    #manually_check_tree_item(self, '9876')
                    #self.openGLWidget_14.paint(self.readImECO.npSeg, self.readImECO.npImage, None)
                    self.updateDispEco(self.readImECO.npImage, self.readImECO.npSeg, initialState=True)
                    make_all_seg_visibl(self)
                    ls = manually_check_tree_item(self, '9876')
                    self.changeColorPen(self.tree_colors.model().sourceModel().invisibleRootItem().child(ls[0]))
                    return True
        elif type_image.lower()=='mriseg':
            if hasattr(self, 'readImMRI'):
                if hasattr(self.readImMRI, 'npImage'):
                    npSeg, readable, equalDim = read_segmentation_file(self, fileObj[0], self.readImMRI, update_color_s=update_color_s)
                    if not equalDim:
                        self.warning_msgbox(
                            'Expected segmentation with dimensions {}, but the segmentation has {}'.format(self.readImMRI.npImage.shape, npSeg.shape))
                        return False
                    if not readable:
                        self.warning_msgbox(
                             'The number of colors are less than the segmentated parts. Unable to read the file.')
                        return False
                    if len(self.readImMRI.npImage.shape) != len(npSeg.shape):
                        return False

                    self.readImMRI.npSeg = npSeg.astype('int')
                    #manually_check_tree_item(self, '9876')
                    #self.openGLWidget_24.paint(self.readImMRI.npSeg, self.readImMRI.npImage, None)
                    self.updateDispMRI(self.readImMRI.npImage, self.readImMRI.npSeg, initialState=True,
                                       tract=self.readImMRI.tract)
                    ls = manually_check_tree_item(self, '9876')
                    self.changeColorPen(self.tree_colors.model().sourceModel().invisibleRootItem().child(ls[0]))
                    #make_all_seg_visibl(self)
                    return True

    def save_screenshot(self, img, filename):
        """
        This function export segmentation results to a file.
        :return:
        """
        from melage.utils.utils import save_numpy_to_png

        self.dockWidget_3.setVisible(True)
        self.setEnabled(False)

        self.progressBarSaving.setValue(0)

        save_numpy_to_png(filename, img)

        self.setEnabled(True)
        self.dockWidget_3.setVisible(False)
        self.progressBarSaving.setValue(0)

    def loadChanges(self):
        """
        This function load all previous values if it is possible
        :return:
        """
        try:
            import cPickle as pickle
        except ModuleNotFoundError:
            from sys import platform
            if platform == "linux" or platform == "linux2":
                try:
                    import pickle5 as pickle
                except:
                    import pickle
            else:
                import pickle
        from melage.utils.utils import loadAttributeWidget, getUnique, adapt_previous_versions, manually_check_tree_item

        sender = QtCore.QObject.sender(self)


        if type(self._basefileSave) == bool or self._basefileSave=='' or self._loaded:
            return
        try:
            self.settings = QSettings(self._basefileSave + '.ini', self.settings.IniFormat)
            #self.restoreState(self.settings.value("windowState"))
           # if self.settings.value("windowState") is not None:
             #   self.restoreState(self.settings.value("windowState"))
            self.openGLWidget_14._updatePaint = False
            self.openGLWidget_24._updatePaint = False
            self.activate3d(True)
            file = self._basefileSave+'.bn'
            dic = None
            self.progressBarSaving.setValue(20)
            if os.path.getsize(file)>0:
                from cryptography.fernet import Fernet
                try:
                    f = Fernet(self._key_picke)
                    with open(file, 'rb') as inputs:
                        # read all file data
                        file_data = inputs.read()
                    self.progressBarSaving.setValue(40)
                    time.sleep(2)
                    encrypted_data = f.decrypt(file_data)
                    with open(file, 'wb') as inputs:
                        inputs.write(encrypted_data)
                    self.progressBarSaving.setValue(60)
                    time.sleep(2)
                    with open(file, 'rb') as inputs:
                        unpickler = pickle.Unpickler(inputs)
                        dic = unpickler.load()
                except:
                    with open(file, 'rb') as inputs:
                        unpickler = pickle.Unpickler(inputs)
                        dic = unpickler.load()

            if dic is not None:


                if 'measurements' in dic:
                    vals = dic['measurements']
                    self.table_widget_measure.setRowCount(len(vals))
                    self.table_widget_measure.setColumnCount(8)
                    r = 0
                    for row in range(len(vals)):
                        for col in range(len(vals[row])):
                            self.table_widget_measure.setItem(row, col, QtWidgets.QTableWidgetItem(vals[row][col]))
                        r += 1
                else:
                    self.table_widget_measure.setRowCount(0)

                self.progressBarSaving.setValue(65)
                name = 'openGLWidget_'
                nameS = 'horizontalSlider_'
                widgets_num = [0, 1, 2, 3, 4, 5, 10, 11, 13, 23]
                for i in widgets_num:
                    nameWidget = name + str(i + 1)
                    if hasattr(self, name + str(i + 1)):
                        widget = getattr(self, name + str(i + 1))
                        if i <13:
                            slider = getattr(self, nameS + str(i + 1))
                            slider.setVisible(True)
                        if i == 10:
                            self.radioButton_1.setVisible(True)
                            self.radioButton_2.setVisible(True)
                            self.radioButton_3.setVisible(True)
                            self.radioButton_4.setVisible(True)
                        elif i == 11:
                            self.radioButton_21_1.setVisible(True)
                            self.radioButton_21_2.setVisible(True)
                            self.radioButton_21_3.setVisible(True)
                            self.radioButton_21.setVisible(True)
                        self.progressBarSaving.setValue(65+len(widgets_num)//2)


                        loadAttributeWidget(widget, nameWidget, dic, self.progressBarSaving)
                        self.scroll_intensity.setValue(int(widget.intensitySeg * 100))


                        if i < 13:
                            if widget.imSlice is not None:
                                widget.setVisible(True)
                                widget.makeObject()
                                widget.update()
                            else:
                                widget.setVisible(False)
                                slider.setVisible(False)


                names = ['readImECO', 'readImMRI']
                for name in names:
                    #if not hasattr(self, name):
                    if name == 'readImECO':
                        imtype = 'eco'
                    else:
                        imtype = 't1'
                    setattr(self, name, readData(type=imtype))
                    readD = getattr(self, name)

                    loadAttributeWidget(readD, name, dic, self.progressBarSaving)

                    self.progressBarSaving.setValue(80)
                self.app.processEvents()
                uqm = []
                if hasattr(self, 'readImECO'):
                    if hasattr(self.readImECO, 'npImage'):
                        self.tree_colors.setVisible(True)
                        self.readImECO.npSeg = self.readImECO.npSeg.astype('int')
                        #uqm = getUnique(self.readImECO.npSeg)
                        self.ImageEnh_view1.setVisible(True)
                        self.readImECO.manuallySetIms('eco')
                        self.setNewImage.emit(self.readImECO.npImage.shape)
                        self.openGLWidget_14.load_paint(self.readImECO.npSeg)
                        self.tabWidget.setTabVisible(2, True)

                        widgets_num = [0, 1, 2, 3, 4, 5, 10, 11, 13, 23]
                        for i in widgets_num:
                            name = 'openGLWidget_'
                            widget = getattr(self, name + str(i + 1))
                            if i < 13 and widget.imSlice is not None and hasattr(widget, 'affine') and hasattr(self.readImMRI, 'affine'):
                                if widget.imType == 'eco':
                                    widget.affine = self.readImMRI.affine
                            self.progressBarSaving.setValue(90)
                        #start = time.time()
                        self.updateDispEco(self.readImECO.npImage, self.readImECO.npSeg, initialState=True)
                        #print(time.time() - start)
                        if not hasattr(self.readImECO, 'npEdge'):
                            self.readImECO.npEdge = []
                self.app.processEvents()
                uqi = []
                if hasattr(self, 'readImMRI'):
                    if hasattr(self.readImMRI, 'npImage'):
                        self.readImMRI.npSeg = self.readImMRI.npSeg.astype('int')
                        #uqi = getUnique(self.readImMRI.npSeg)
                        self.tabWidget.setTabVisible(3, True)
                        self.page1_mri.setVisible(True)
                        self.tree_colors.setVisible(True)
                        self.readImMRI.manuallySetIms('t1')
                        self.setNewImage2.emit(self.readImMRI.npImage.shape)
                        #self.openGLWidget_24.load_paint(self.readImMRI.npSeg)

                        widgets_num = [0, 1, 2, 3, 4, 5, 10, 11, 13, 23]
                        for i in widgets_num:
                            name = 'openGLWidget_'
                            widget = getattr(self, name + str(i + 1))
                            if i < 13 and widget.imSlice is not None and hasattr(widget, 'affine') and hasattr(self.readImMRI, 'affine'):
                                if widget.imType == 'mri':
                                    widget.affine = self.readImMRI.affine

                        self.updateDispMRI(self.readImMRI.npImage, self.readImMRI.npSeg, initialState=True, tract=self.readImMRI.tract)
                        if not hasattr(self.readImMRI, 'npEdge'):
                            self.readImMRI.npEdge = []
                        if hasattr(self.readImMRI, 'ims'):
                            shape = self.readImMRI.ims.shape
                            self.actionComboBox.setObjectName("View2")
                            try:
                                self.actionComboBox.currentTextChanged.disconnect(self.changeVolume)
                            except:
                                pass
                            self.actionComboBox.clear()
                            for r in range(shape[-1]):
                                self.actionComboBox.addItem("{}".format(r + 1))
                            try:
                                self.actionComboBox.currentTextChanged.connect(self.changeVolume)
                            except:
                                pass
                            self.actionComboBox_visible.setVisible(True)
                            self.actionComboBox_visible.setDisabled(False)
                        else:
                            self.actionComboBox_visible.setVisible(False)
                            self.actionComboBox_visible.setDisabled(True)
                        self.progressBarSaving.setValue(95)
                        self.app.processEvents()

                loadAttributeWidget(self, 'main', dic, self.progressBarSaving)
                self.imported_images = []
                self.tree_images.model().sourceModel().clear()
                self.tree_images.model().sourceModel().setColumnCount(2)
                self.tree_images.model().sourceModel().setHorizontalHeaderLabels(['Index', 'Name'])

                if hasattr(self, 'readImMRI'):
                    if hasattr(self.readImMRI, 'im'):
                        format = 'None'
                        if hasattr(self, 'format_mri'):
                            format = self.format_mri
                        #self.iminfo_dialog.setmri(
                        #    [self.readImMRI.im.header, self.readImMRI.im.affine, self.filenameMRI, format])
                        if self.filenameEco:
                            file_out = 'View 1: {}, View 2: {}'.format(self.filenameEco, self.filenameMRI)
                        else:
                            file_out = 'View 2: {}'.format(self.filenameMRI)
                        info1, color1 = [[[self.filenameMRI], "*MRI_loaded"],2, 1], [1,1,0]
                        update_image_sch(self, info=info1, color=color1, loaded=True)
                        #info1, color1 = [[self.filenameMRI+'_seg', 'MRI_loaded_seg'],5], [0,1,1]
                        #update_image_sch(self, info=info1, color=color1, loaded=True)
                        self.iminfo_dialog.updata_name_iminfo(self.filenameMRI, 1)
                        if hasattr(self.readImMRI, 'im_metadata'):
                            self.iminfo_dialog.set_tag_value(self.readImMRI, ind=1)
                if hasattr(self, 'readImECO'):
                    if hasattr(self.readImECO, 'im'):
                        format = 'None'
                        if hasattr(self, 'format_eco'):
                            format = self.format_eco
                        #self.iminfo_dialog.seteco(
                        #    [self.readImECO.im.header, self.readImECO.im.affine, self.filenameEco, format])
                        self.iminfo_dialog.updata_name_iminfo(self.filenameEco, 0)

                        info1, color1 = [[[self.filenameEco],"*View 1 (loaded)"],0,0], [0, 1, 1]
                        update_image_sch(self, info=info1, color=color1, loaded=True)
                        #info1, color1 = [[self.filenameEco+"_seg","US_loaded_seg"],3], [0,1,1]
                        #update_image_sch(self, info=info1, color=color1, loaded=True)

                        if hasattr(self.readImECO, 'im_metadata'):
                            self.iminfo_dialog.set_tag_value(self.readImECO, ind=0)
                self.progressBarSaving.setValue(98)
                from melage.utils.utils import set_new_color_scheme, update_widget_color_scheme, make_all_seg_visibl

                #if not self.dw2_cb.currentText() in self.dw2Text:
                #self.dw2_cb.currentTextChanged.disconnect(self.changeColorPen)
                self.tree_colors.model().sourceModel().itemChanged.disconnect(self.changeColorPen)
                #color_index_rgb = [[key, self.colorsCombinations[key][0], self.colorsCombinations[key][1],
                #             self.colorsCombinations[key][2], self.colorsCombinations[key][3]] for key in
                #            self.colorsCombinations.keys() if len(self.colorsCombinations[key]) > 0]
                #self.color_name = [self.tree_colors.invisibleRootItem().child(i).text(0)+"_"+self.tree_colors.invisibleRootItem().child(i).text(1) for i in range(self.tree_colors.invisibleRootItem().childCount())]

                #self.color_index_rgb,self.color_name, self.colorsCombinations = combinedIndex(self.colorsCombinations, self.color_index_rgb, self.color_name, uqm, uqi)

                adapt_previous_versions(self)
                set_new_color_scheme(self)
                update_widget_color_scheme(self)
                self.tree_colors.model().sourceModel().itemChanged.connect(self.changeColorPen)
                #self.dw2_cb.currentTextChanged.connect(self.changeColorPen)
                #elif abs(len(self.colorsCombinations.keys())-len(self.dw2Text))==1:
                #    self.colorsCombinations[len(self.dw2Text)] = [1, 0, 0, 1]

                #make_all_seg_visibl(self)
                self.hs_t1_5.setValue(0)
                self.lb_t1_5.setText('0')
                self.hs_t2_5.setValue(0)
                self.lb_t2_5.setText('0')

                self.openGLWidget_4.imType = 'mri'
                self.openGLWidget_5.imType = 'mri'
                self.openGLWidget_6.imType = 'mri'
                self.scroll_intensity.setValue(int(self.openGLWidget_1.intensitySeg*100))
                #manually_check_tree_item(self,'9876')
                widgets = [1,2,3,4,5,6,11,12,14,24]
                prefix = 'openGLWidget_'
                for k in widgets:
                    name = prefix + str(k)
                    widget = getattr(self, name)
                    widget.colorInds = []
                #ls = [i for i in range(self.tree_colors.invisibleRootItem().childCount()) if
                #      self.tree_colors.invisibleRootItem().child(i).text(0) == '9876']
                #for l in ls:
                #    self.tree_colors.invisibleRootItem().child(l).setCheckState(0, Qt.Checked)

                #self.restoreState(self.settings.value("windowState"))
               # if self.settings.value("windowState") is not None:
                  #  self.restoreState(self.settings.value("windowState"))
                self.progressBarSaving.setVisible(False)
                self.openGLWidget_14._updatePaint = True
                self.openGLWidget_24._updatePaint = True
                self.expectedTime = self.settingsBN.doubleSpinBox.value()*60
                self.dw2_s1.setValue(int(self.dw2lb1.text()))
                self.dw2_s2.setValue(int(self.dw2lb2.text()))
                #self.changedTab()
        except Exception as e:
            print('Load changes')
            print(e)
        finally:
            self._loaded = True




    def browseUS(self, fileObj=None, use_dialog=True):
        """
        Browsing MRI
        :param fileObj:
        :param use_dialog:
        :return:
        """

        def setVisible(val, imtype='eco'):
            self.actionImportSegEco.setDisabled(False)
            self.actionExportImEco.setDisabled(False)
            self.actionExportSegEco.setDisabled(False)


            self.radioButton_1.setVisible(val)
            self.radioButton_2.setVisible(val)
            self.radioButton_3.setVisible(val)
            self.radioButton_4.setVisible(val)
            for k in [1,2,3,11]:
                name = 'openGLWidget_' + str(k)
                slider = getattr(self, 'horizontalSlider_' + str(k))
                label = getattr(self, 'label_' + str(k))
                label.setVisible(val)
                slider.setVisible(val)
                widget = getattr(self, name)
                widget.setVisible(val)
                widget.imType = imtype

        self.init_state()

        if use_dialog or fileObj is not None:
            if not isinstance(fileObj, list):
                fileObj = ['', '']
                opts = QtWidgets.QFileDialog.DontUseNativeDialog
                dialg = QFileDialogPreview(self, "Open File", self.source_dir, self._filters, options=opts,
                                           index=self._last_index_select_image_mri, last_state=self._last_state_preview)
                dialg.setFileMode(QtWidgets.QFileDialog.ExistingFile)

                if dialg.exec_() == QFileDialogPreview.Accepted:
                    fileObj = dialg.getFileSelected()
                    fileObj[1] = dialg.selectedNameFilter()

                if not fileObj[0]:
                    return False

                self._last_state_preview = dialg.checkBox_preview.isChecked()
                index = dialg._combobox_type.currentIndex()
            else:
                [fileObj, index] = fileObj

            if index == 2:
                imtype = 'eco'
                #readImECO, Info = self.readD(fileObj, 't1', target_system='IPL')
                readImECO, Info = self.readD(fileObj, 't1', target_system='RAS')
            else:
                print('Please optimze the trage system')
                imtype = 'eco'
                if index == 0:
                    readImECO, Info = self.readD(fileObj, 'neonatal', target_system='SPR')
                elif index == 1:
                    readImECO, Info = self.readD(fileObj, 'fetal', target_system='PLI')
                else:
                    return False

            if Info[2].lower() != 'success':
                return False
            else:
                self.readImECO = readImECO
            self._last_index_select_image_eco = index


        if hasattr(self, 'readImMRI'):
            if hasattr(self.readImMRI, 'npImage'):
                for k in [3,4,5]:
                    name = 'openGLWidget_' + str(k + 1)
                    widget = getattr(self, name)
                    widget.setVisible(True)

                self.updateDispMRI(self.readImMRI.npImage, self.readImMRI.npSeg, initialState=True)

        if use_dialog:
            self.actionComboBox_visible.setVisible(False)
            self.actionComboBox_visible.setDisabled(True)
        else:
            Info = None
            txt = self.actionComboBox.currentText()

            if txt:
                Info = self.readImECO.UpdateAnotherDim(int(float(txt)) - 1)

            if hasattr(self.readImECO, '_fileDicom'):
                self.filenameEco = self.readImECO._fileDicom

            if Info is None:
                Info = [True, True, 'success']
                if not hasattr(self, '_format'):
                    self._format = 'NIFTI'

            readImECO = self.readImECO

        if Info[2].lower() != 'success':
            return False
        else:
            self.readImECO = readImECO

        if hasattr(self.readImECO, 'ims') and use_dialog:
            _num_dims = self.readImECO._num_dims
            if _num_dims > 1:
                try:
                    self.actionComboBox.currentTextChanged.disconnect(self.changeVolume)
                except:
                    pass
                self.actionComboBox.clear()
                for r in range(_num_dims):
                    self.actionComboBox.addItem("{}".format(r + 1))

                self.actionComboBox_visible.setDisabled(False)
                self.actionComboBox_visible.setVisible(True)
                self.actionComboBox.setObjectName("View1")

                try:
                    self.actionComboBox.currentTextChanged.connect(self.changeVolume)
                except:
                    pass

        setVisible(True)

        if hasattr(self.readImECO, 'npImage'):
            self.format_eco = self._format

            if fileObj is not None:
                if hasattr(self.readImECO, '_fileDicom'):
                    self.filenameEco = self.readImECO._fileDicom
                else:
                    self.filenameEco = basename(fileObj[0])

            if self.filenameMRI:
                file_out = 'US: {}, MRI: {}'.format(self.filenameEco, self.filenameMRI)
            else:
                file_out = 'MRI: {}'.format(self.filenameMRI)

            self.iminfo_dialog.updata_name_iminfo(self.filenameEco, 0)

            if hasattr(self.readImECO, 'im_metadata'):
                self.iminfo_dialog.set_tag_value(self.readImECO, ind=0)

            """
            from melage.utils.utils import update_color_scheme
            if rhasattr(self, 'readImECO.npSeg'):
                update_color_scheme(self, self.readImMRI.npSeg, self.readImECO.npSeg, dialog=False)
            else:
                update_color_scheme(self, self.readImMRI.npSeg, dialog=False)
            """

            ls = manually_check_tree_item(self, '9876')
            self.changeColorPen(self.tree_colors.model().sourceModel().invisibleRootItem().child(ls[0]))

            if self.readImECO.npImage is not None:
                self.tabWidget.setTabVisible(2, True)


                widgets_num = [0, 1, 2, 10]
                for k in widgets_num:
                    widget_name = 'openGLWidget_' + str(k+1)
                    widget = getattr(self, widget_name)
                    widget.resetInit()
                    widget.initialState()
                    if 'Affine' in self.readImECO.im_metadata:
                        widget.affine = self.readImECO.im_metadata['Affine']


                self.updateDispEco(self.readImECO.npImage, self.readImECO.npSeg, initialState=True)

                self.changedTab()
                self.reset_page1_eco()

                if use_dialog:
                    self.setCurrentCoordsystem()
                    self.HistImage.UpdateName(self.filenameEco, None)
                    self.iminfo_dialog.UpdateName(self.filenameEco, None)
                    info1, color1 = [[[fileObj[0]], fileObj[1]], 2, 1], [1, 1, 0]
                    update_image_sch(self, info=info1, color=color1, loaded=True)

                    from melage.utils.utils import clean_parent_image2
                    clean_parent_image2(self, fileObj[0], 'View 1', index_view=0)

            self.setNewImage.emit(self.readImECO.npImage.shape)
            self.readInfo(Info)
            self.reset_page1_eco()

            self._rotationAngleEco_coronal = 0
            self._rotationAngleEco_axial = 0
            self._rotationAngleEco_sagittal=0


            self.hs_t1_5.setValue(0)
            self.toolBar2.setDisabled(False)

            txt = compute_volume(self.readImECO, self.filenameEco, [9876], in_txt=self.openedFileName.text(),
                                 ind_screen=0)
            self.openedFileName.setText(txt)

        else:
            setVisible(False)

        self.activateGuidelines(self._last_state_guide_lines)

        if self.BE_DL.isVisible():
            self.updateDataBEDL(index=0)
        else:
            self.BE_DL.clear()

        if self.Tissue_Seg.isVisible():
            self.updateDataBEDL(index=1)
        else:
            self.Tissue_Seg.clear()

        for ind in range(2):
            save_var = '_immri_bedl_{}'.format(ind)
            save_var_seg = '_immri_bedl_seg_{}'.format(ind)
            setattr(self, save_var,None)
            setattr(self, save_var_seg, None)

        return True


    def browseTractoGraphy(self, fileObj=None):
        """
        Browsing Tractography images
        :param fileObj:
        :return:
        """
        from melage.utils.utils import load_trk
        # Browse Tractography
        if not hasattr(self,'readImMRI'):
            return
        if not hasattr(self.readImMRI, 'npImage'):
            return
        if fileObj is None or type(fileObj) is bool:
            opts =QtWidgets.QFileDialog.DontUseNativeDialog
            fileObj = QtWidgets.QFileDialog.getOpenFileName( self, "Open File", self.source_dir, 'track(*.trk)', options=opts)
        if fileObj[0]=='':
            return
        stk, success = load_trk(fileObj[0])
        #from melage.utils.utils import get_affine_shape
        if not hasattr(self.readImMRI, 'affine'):
            self.readImMRI.afine = self.readImMRI.im.affine
        if not success:
            return
        from melage.utils.utils import get_world_from_trk
        vox_world = get_world_from_trk(stk.streamlines, self.readImMRI.affine, inverse=True)
        self.readImMRI.tract = vox_world


        if hasattr(self, 'readImMRI'):
            if hasattr(self.readImMRI, 'npSeg'):
                widgets_num = [0, 1, 2, 11]
                for k in widgets_num:
                    name = 'openGLWidget_' + str(k + 1)
                    widget = getattr(self, name)
                    widget.resetInit()
                    widget.initialState()
                widgets_num = [3, 4, 5]
                name_slider = 'horizontalSlider_'
                for k in widgets_num:
                    name = 'openGLWidget_' + str(k+1)
                    slider = getattr(self, name_slider + str(k+1))
                    widget = getattr(self, name)
                    sliceNum = slider.value()

                    widget.updateInfo(*getCurrentSlice(widget,
                                                       self.readImMRI.npImage, self.readImMRI.npSeg, sliceNum, self.readImMRI.tract, tol_slice=self.tol_trk), sliceNum, self.readImMRI.npImage.shape,
                                      initialState=False, imSpacing=self.readImMRI.ImSpacing)
                    widget.makeObject()
                    widget.update()



    def browseFA(self, fileObj=None):

        # Browse Fractional Anisotropy
        if fileObj is None or type(fileObj) is bool:
            opts =QtWidgets.QFileDialog.DontUseNativeDialog
            fileObj = QtWidgets.QFileDialog.getOpenFileName( self, "Open File", self.source_dir, self._filters, options=opts)
        if fileObj[0]=='':
            return
        Img, _ = self.readD(fileObj, type='t1')
        npImage = Img.npImage.astype('int')
        npImage[Img.npImage <=20] = 0
        npImage[(Img.npImage <= 40) * (Img.npImage > 20)] = 1
        npImage[(Img.npImage <= 60) * (Img.npImage > 40)] = 2
        npImage[(Img.npImage <= 80) * (Img.npImage > 60)] = 3
        npImage[(Img.npImage <= 100) * (Img.npImage > 80)] = 4
        npImage[(Img.npImage > 100)] = 5
        #npImage[Img.npImage <= 10] = 0
        if hasattr(self, 'readImMRI'):
            if hasattr(self.readImMRI, 'npSeg'):
                widgets_num = [0, 1, 2, 11]
                for k in widgets_num:
                    name = 'openGLWidget_' + str(k + 1)
                    widget = getattr(self, name)
                    widget.resetInit()
                    widget.initialState()
                self.readImMRI.npSeg = npImage
                widgets_num = [3, 4, 5]
                name_slider = 'horizontalSlider_'
                for k in widgets_num:
                    name = 'openGLWidget_' + str(k+1)
                    slider = getattr(self, name_slider + str(k+1))
                    widget = getattr(self, name)
                    sliceNum = slider.value()

                    widget.updateInfo(*getCurrentSlice(widget,
                                                       self.readImMRI.npImage, self.readImMRI.npSeg, sliceNum, self.readImMRI.tract, tol_slice=self.tol_trk), sliceNum, self.readImMRI.npImage.shape,
                                      initialState=False, imSpacing=self.readImMRI.ImSpacing)
                    widget.makeObject()
                    widget.update()

    def browseMRI(self, fileObj=None, use_dialog=True):
        """
        Browsing MRI
        :param fileObj:
        :param use_dialog:
        :return:
        """

        def setVisible(val):
            self.actionImportSegMRI.setDisabled(False)
            self.actionExportImMRI.setDisabled(False)
            self.actionExportSegMRI.setDisabled(False)

            self.radioButton_21.setVisible(val)
            self.radioButton_21_1.setVisible(val)
            self.radioButton_21_2.setVisible(val)
            self.radioButton_21_3.setVisible(val)

            for k in [4, 5, 6, 12]:
                slider = getattr(self, 'horizontalSlider_' + str(k))
                label = getattr(self, 'label_' + str(k))
                label.setVisible(val)
                slider.setVisible(val)

                widget_name = 'openGLWidget_' + str(k)
                widget = getattr(self, widget_name)
                widget.setVisible(val)
                widget.imType = 'mri'

        self.init_state()

        if use_dialog or fileObj is not None:
            if not isinstance(fileObj, list):
                fileObj = ['', '']
                opts = QtWidgets.QFileDialog.DontUseNativeDialog
                dialg = QFileDialogPreview(self, "Open File", self.source_dir, self._filters, options=opts,
                                           index=self._last_index_select_image_mri, last_state=self._last_state_preview)
                dialg.setFileMode(QtWidgets.QFileDialog.ExistingFile)

                if dialg.exec_() == QFileDialogPreview.Accepted:
                    fileObj = dialg.getFileSelected()
                    fileObj[1] = dialg.selectedNameFilter()

                if not fileObj[0]:
                    return False

                self._last_state_preview = dialg.checkBox_preview.isChecked()
                index = dialg._combobox_type.currentIndex()
            else:
                [fileObj, index] = fileObj

            if index == 2:
                imtype = 'mri'
                #readImMRI, Info = self.readD(fileObj, 't1', target_system='IPL')
                readImMRI, Info = self.readD(fileObj, 't1', target_system='RAS')
            else:
                imtype = 'eco'
                print('Please optimze the trage system')
                if index == 0:
                    readImMRI, Info = self.readD(fileObj, 'neonatal', target_system='SPR')
                elif index == 1:
                    readImMRI, Info = self.readD(fileObj, 'fetal', target_system='PLI')
                else:
                    return False

            if Info[2].lower() != 'success':
                return False
            else:
                self.readImMRI = readImMRI
            self._last_index_select_image_mri = index

        if hasattr(self, 'readImECO'):
            if hasattr(self.readImECO, 'npImage'):
                for k in range(3):
                    widget_name = 'openGLWidget_' + str(k + 1)
                    widget = getattr(self, widget_name)
                    widget.setVisible(True)
                self.updateDispEco(self.readImECO.npImage, self.readImECO.npSeg, initialState=True)

        if use_dialog:
            self.actionComboBox_visible.setVisible(False)
            self.actionComboBox_visible.setDisabled(True)
        else:
            Info = None
            txt = self.actionComboBox.currentText()

            if txt:
                Info = self.readImMRI.UpdateAnotherDim(int(float(txt)) - 1)

            if hasattr(self.readImMRI, '_fileDicom'):
                self.filenameMRI = self.readImMRI._fileDicom

            if Info is None:
                Info = [True, True, 'success']
                if not hasattr(self, '_format'):
                    self._format = 'NIFTI'

            readImMRI = self.readImMRI

        if Info[2].lower() != 'success':
            return False
        else:
            self.readImMRI = readImMRI

        if hasattr(self.readImMRI, 'ims') and use_dialog:
            _num_dims = self.readImECO._num_dims
            if _num_dims > 1:
                try:
                    self.actionComboBox.currentTextChanged.disconnect(self.changeVolume)
                except:
                    pass
                self.actionComboBox.clear()
                for r in range(_num_dims):
                    self.actionComboBox.addItem("{}".format(r + 1))

                self.actionComboBox_visible.setDisabled(False)
                self.actionComboBox_visible.setVisible(True)
                self.actionComboBox.setObjectName("View2")

                try:
                    self.actionComboBox.currentTextChanged.connect(self.changeVolume)
                except:
                    pass

        setVisible(True)

        if hasattr(self.readImMRI, 'npImage'):
            self.format_mri = self._format

            if fileObj is not None:
                if hasattr(self.readImMRI, '_fileDicom'):
                    self.filenameMRI = self.readImMRI._fileDicom
                else:
                    self.filenameMRI = basename(fileObj[0])

            if self.filenameEco:
                file_out = 'US: {}, MRI: {}'.format(self.filenameEco, self.filenameMRI)
            else:
                file_out = 'MRI: {}'.format(self.filenameMRI)

            self.iminfo_dialog.updata_name_iminfo(self.filenameMRI, 1)

            if hasattr(self.readImMRI, 'im_metadata'):
                self.iminfo_dialog.set_tag_value(self.readImMRI, ind=1)

            """
            from melage.utils.utils import update_color_scheme
            if rhasattr(self, 'readImECO.npSeg'):
                update_color_scheme(self, self.readImMRI.npSeg, self.readImECO.npSeg, dialog=False)
            else:
                update_color_scheme(self, self.readImMRI.npSeg, dialog=False)
            """

            ls = manually_check_tree_item(self, '9876')
            self.changeColorPen(self.tree_colors.model().sourceModel().invisibleRootItem().child(ls[0]))

            if self.readImMRI.npImage is not None:
                self.tabWidget.setTabVisible(3, True)

                widgets_num = [0, 1, 2, 11]
                widgets_num = [4, 5, 6, 11]
                for k in widgets_num:
                    widget_name = 'openGLWidget_' + str(k)
                    widget = getattr(self, widget_name)
                    widget.resetInit()
                    widget.initialState()
                    if 'Affine' in self.readImMRI.im_metadata:
                        widget.affine = self.readImMRI.im_metadata['Affine']

                self.updateDispMRI(self.readImMRI.npImage, self.readImMRI.npSeg, initialState=True,
                                   tract=self.readImMRI.tract)
                self.changedTab()
                self.reset_page1_mri()

                if use_dialog:
                    self.setCurrentCoordsystem()
                    self.HistImage.UpdateName(None, self.filenameMRI)
                    self.iminfo_dialog.UpdateName(None, self.filenameMRI)
                    info1, color1 = [[[fileObj[0]], fileObj[1]], 2, 1], [1, 1, 0]
                    update_image_sch(self, info=info1, color=color1, loaded=True)

                    from melage.utils.utils import clean_parent_image2
                    clean_parent_image2(self, fileObj[0], 'View 2', index_view=1)

            self.setNewImage2.emit(self.readImMRI.npImage.shape)
            self.readInfo(Info)
            self.reset_page1_mri()

            self._rotationAngleMRI_coronal = 0
            self._rotationAngleMRI_axial = 0
            self._rotationAngleMRI_sagittal = 0

            self.hs_t2_5.setValue(0)
            self.toolBar2.setDisabled(False)

            txt = compute_volume(self.readImMRI, self.filenameMRI, [9876], in_txt=self.openedFileName.text(),
                                 ind_screen=1)
            self.openedFileName.setText(txt)

        else:
            setVisible(False)

        self.activateGuidelines(self._last_state_guide_lines)

        if self.BE_DL.isVisible():
            self.updateDataBEDL(index=0)
        else:
            self.BE_DL.clear()

        if self.Tissue_Seg.isVisible():
            self.updateDataBEDL(index=1)
        else:
            self.Tissue_Seg.clear()

        for ind in range(2):
            save_var = '_immri_bedl_{}'.format(ind)
            save_var_seg = '_immri_bedl_seg_{}'.format(ind)
            setattr(self, save_var, None)
            setattr(self, save_var_seg, None)

        return True

    def warning_msgbox(self, text= None): # warning message box
        if text is None:
            text = 'There is an error.'
        MessageBox = QtWidgets.QMessageBox(self)
        MessageBox.setText(text)
        MessageBox.setWindowTitle('Warning')
        MessageBox.show()

    def readInfo(self, Info):
        """
        Reading information form images
        :param Info:
        :return:
        """
        if Info[2] == 'No file':
            MessageBox = QtWidgets.QMessageBox(self)
            if Info[0] and not Info[1]:
                MessageBox.setText('Read JSON metadata, Image data not found')
                MessageBox.setWindowTitle('Reading Warning')
            elif not Info[0] and not Info[1]:
                MessageBox.setText('JSON metadata data not found, Image data not found')
                MessageBox.setWindowTitle('Reading Error')
            elif not Info[0] and Info[1]:
                MessageBox.setText('JSON metadata data not found, Read Image data')

                MessageBox.setWindowTitle('Reading Warning')
            MessageBox.setWindowTitle('Reading Error')
            MessageBox.show()

    def readD(self, fileObj, type = 'eco', target_system='IPL'):

        if fileObj[1] != '':

            self.source_dir = dirname(fileObj[0])
            filters = self._filters.split(';;')
            index_sel = filters.index(fileObj[1])
            outfile_format = self._filters.split(';;')[index_sel].lower()
            filters[0], filters[index_sel] = filters[index_sel], filters[0]
            self._filters = ';;'.join(filters)
            #if type == 'eco':
            #    self.filenameEco = basename(fileObj[0])
            #else:
            #    self.filenameMRI = basename(fileObj[0])
            filename = basename(fileObj[0])
            _, file_extension = os.path.splitext(fileObj[0])
            self.file_extension = file_extension
            self.setCursor(QtCore.Qt.WaitCursor)
            readIM = readData(type=type, target_system=target_system)
            format = 'None'
            try:
                if type == 'eco':
                    if 'vol' in outfile_format: # Kretz data
                        Info = readIM.readKretz(join(self.source_dir, filename))
                        format = 'VOL'
                    elif 'nii' in outfile_format: # read NIFTI
                        Info = readIM.readNIFTI(join(self.source_dir, filename), type)
                        format = 'NIFTI'
                    elif 'nrrd' in outfile_format: # Read NRRD
                        Info = readIM.readNRRD(join(self.source_dir, filename), type)
                        format = 'NRRD'
                    elif 'dcm' in outfile_format: # READ DICOM
                        Info = readIM.readDICOM(join(self.source_dir, filename), type)
                        format = 'DICOM'
                    else:
                        Info = [False, False, 'No file']
                    if Info[1]==True:
                        self._format = format

                else:
                    if 'vol' in outfile_format: # Kretz data
                        Info = readIM.readKretz(join(self.source_dir, filename))
                        format = 'VOL'
                    elif 'nii' in outfile_format: # read NIFTI
                        Info = readIM.readNIFTI(join(self.source_dir, filename), type)
                        format = 'NIFTI'
                    elif 'dicom' in outfile_format: # READ DICOM
                        Info = readIM.readDICOM(join(self.source_dir, filename), type)
                        format = 'DICOM'
                        if hasattr(readIM, '_fileDicom'):
                            self.filenameMRI = readIM._fileDicom
                    elif 'nrrd' in outfile_format: # Read NRRD
                        Info = readIM.readNRRD(join(self.source_dir, filename), type)
                        format = 'NRRD'
                    else:
                        Info = [False, False, 'No file']
                if Info[1] == True:
                    self._format = format

                self.setCursor(QtCore.Qt.ArrowCursor)
            except Exception as e:
                print(e)
                Info = [False, False, 'No file']
            self.setCursor(QtCore.Qt.ArrowCursor)
            return readIM, Info
        else:
            return [], [False, False, 'No file']







class MainWindow0(QtWidgets.QMainWindow, Ui_Main):
    def __init__(self, *args, obj = None, **kwargs):
        super(MainWindow0, self).__init__(*args, **kwargs)
        QWidget.__init__(self)
        self.setupUi(self)
        #QtCore.QTimer.singleShot(5000, self.showChildWindow)






if __name__ == '__main__':
    from PyQt5 import QtWidgets, QtCore, QtGui
    from PyQt5.QtWidgets import QWidget
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow0()
    window.show()
    sys.exit(app.exec_())
