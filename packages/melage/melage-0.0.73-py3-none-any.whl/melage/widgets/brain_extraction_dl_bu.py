__AUTHOR__ = 'Bahram Jafrasteh'

"""
    Main BrainExtractor class
"""
import os
import numpy as np
import nibabel as nib
from PyQt5 import QtCore, QtGui, QtWidgets
from functools import partial


from PyQt5.QtCore import pyqtSignal
import sys
from PyQt5.QtWidgets import QDialog, QApplication, QPushButton, QVBoxLayout
from PyQt5.QtCore import Qt
from melage.utils.utils import convert_to_ras, LargestCC
def to_str(val):
    return '{:.2f}'.format(val)

def remove_zero(f_data, value=0):
    """
    Remove non segmented areas from image
    :param f_data:
    :param value:
    :return:
    """

    xs, ys, zs = np.where(f_data > value) #find zero values
    tol = 4

    min_max = []
    for x in [xs, ys, zs]:
        minx = min(x)-tol if min(x)-tol>1 else min(x)
        maxx = max(x) + tol if max(x) + tol < f_data.shape[0]-1 else max(x)
        min_max.append([minx, maxx])
    f_data = f_data[min_max[0][0]:min_max[0][1] + 1, min_max[1][0]:min_max[1][1] + 1, min_max[2][0]:min_max[2][1] + 1]

    return f_data, min_max

def centralize_image(img, maxas=128, border=None):
    """
    Put image in the center
    :param img:
    :param maxas:
    :param border:
    :return:
    """

    n = img.shape
    if type(maxas) != list:
        maxas= [maxas, maxas, maxas]
    pads = np.array([maxas[i] - a for i, a in enumerate(n)])
    pads_r = pads // 2
    pads_l = pads - pads_r
    npads_l = pads_l * -1
    npads_r = pads_r * -1
    if border is None:
        border = img[0,0,0]
    new_img = np.ones((maxas[0], maxas[1], maxas[2]))*border

    pads_r[pads_r < 0] = 0
    pads_l[pads_l < 0] = 0
    npads_l[npads_l < 0] = 0
    npads_r[npads_r < 0] = 0
    # print(pads_l, pads_r)
    new_img[pads_r[0]:maxas[0] - pads_l[0], pads_r[1]:maxas[1] - pads_l[1], pads_r[2]:maxas[2] - pads_l[2]] = img[
                                                                                                  npads_r[0]:n[0] -npads_l[0],
                                                                                                  npads_r[1]:n[1] -npads_l[1],
                                                                                                  npads_r[2]:n[2] -npads_l[2]]
    return new_img, [pads, pads_l, pads_r, npads_l, npads_r, n]

class BE_DL(QDialog):
    """
    This class has been implemented to use deep learning algorithms for brain extraction
    """
    closeSig = pyqtSignal()
    betcomp = pyqtSignal(int)
    datachange = pyqtSignal()
    back_orig = pyqtSignal(int)

    backbutton = pyqtSignal()
    """

    """
    def __init__(self, parent=None
                 ):
        super(BE_DL, self).__init__(parent)
        #self.load_filepath = 'widgets/Hybrid_latest.pth'
        self._curent_weight_dir = os.path.dirname(os.path.join(os.getcwd()))
        """
        Initialization of Brain Extractor

        Computes image range/thresholds and
        estimates the brain radius
        """
    def set_pars(self, threshold=-0.5, remove_extra_bone=True):
        #print("Initializing...")

        # get image resolution

        self.threshold = threshold
        self.borderp = 0.0

        # store brain extraction parameters
        self.setupUi()
    def setData(self, img, res):
        # store the image
        self.img = img
        self.initial_mask = None
        self.shape = img.shape  # 3D shape




    def activate_advanced(self, value):
        self.widget.setEnabled(value)

    def setupUi(self):
        Dialog = self.window()
        Dialog.setObjectName("N4")
        Dialog.resize(500, 220)
        self.grid_main = QtWidgets.QGridLayout(self)
        self.grid_main.setContentsMargins(0, 0, 0, 0)
        self.grid_main.setObjectName("gridLayout")

        self.hbox = QtWidgets.QHBoxLayout()
        self.hbox.setContentsMargins(0, 0, 0, 0)
        self.hbox.setObjectName("gridLayout")
        self.grid_main.addLayout(self.hbox, 0, 0)

        self.checkBox = QtWidgets.QCheckBox()
        self.hbox.addWidget(self.checkBox, 0)
        self.checkBox.setObjectName("checkBox")
        self.checkBox.stateChanged.connect(self.activate_advanced)
        self.comboBox_image = QtWidgets.QComboBox()
        self.comboBox_image.setGeometry(QtCore.QRect(20, 10, 321, 25))
        self.comboBox_image.setObjectName("comboBox")
        for i in range(2):
            self.comboBox_image.addItem("")
        self.comboBox_image.currentIndexChanged.connect(self.datachange)

        self.comboBox_models = QtWidgets.QComboBox()
        self.comboBox_models.setGeometry(QtCore.QRect(20, 10, 321, 25))
        self.comboBox_models.setObjectName("comboBox")
        for i in range(2):
            self.comboBox_models.addItem("")
        self.comboBox_models.currentIndexChanged.connect(partial(self.parChanged, True))


        self.hbox.addWidget(self.comboBox_image, 1)
        self.hbox.addWidget(self.comboBox_models, 2)


        self.progressBar = QtWidgets.QProgressBar()
        self.progressBar.setEnabled(False)
        self.progressBar.setProperty("value", 0)
        self.progressBar.setAlignment(QtCore.Qt.AlignCenter)
        self.progressBar.setObjectName("progressBar")
        self.progressBar.setMaximum(100)



        self.hbox2 = QtWidgets.QHBoxLayout()
        self.hbox2.setContentsMargins(0, 0, 0, 0)
        self.hbox2.setObjectName("gridLayout")
        self.hbox2.addWidget(self.progressBar, 1)



        self.widget = QtWidgets.QWidget()
        self.widget.setObjectName("widget")
        self.gridLayout = QtWidgets.QGridLayout(self.widget)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")
        self.splitter_3 = QtWidgets.QSplitter(self.widget)
        self.splitter_3.setOrientation(QtCore.Qt.Horizontal)
        self.splitter_3.setObjectName("splitter_3")


        self.gridLayout.addWidget(self.splitter_3, 0, 0, 1, 1)
        self.splitter = QtWidgets.QSplitter(self.widget)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName("splitter")
        self.checkbox_thresholding = QtWidgets.QCheckBox(self.splitter)
        #self.checkbox_thresholding.setAlignment(QtCore.Qt.AlignCenter)
        self.checkbox_thresholding.setObjectName("checkbox_thresholding")
        self.checkbox_thresholding.setChecked(False)

        self.checkbox_otsu = QtWidgets.QCheckBox(self.splitter)
        #self.checkbox_otsu.setAlignment(QtCore.Qt.AlignCenter)
        self.checkbox_otsu.setObjectName("checkbox_thresholding")
        self.checkbox_otsu.setChecked(False)
        self.checkbox_otsu.stateChanged.connect(self.resetParams)


        #self.checkbox_bone = QtWidgets.QCheckBox(self.splitter)
        #self.checkbox_bone.setObjectName("histogram_bone")
        #self.checkbox_bone.setChecked(False)
        self.label_type = QtWidgets.QLabel(self.splitter)
        self.label_type.setAlignment(QtCore.Qt.AlignCenter)
        self.label_type.setObjectName("label")
        self.comboBox_image_type = QtWidgets.QComboBox(self.splitter)
        self.comboBox_image_type.setGeometry(QtCore.QRect(20, 10, 321, 25))
        self.comboBox_image_type.setObjectName("comboBox")
        self.comboBox_image_type.setCurrentIndex(0)
        self.comboBox_image_type.currentIndexChanged.connect(partial(self.parChanged, False))
        for i in range(2):
            self.comboBox_image_type.addItem("")


        #self.histogram_threshold_min = QtWidgets.QDoubleSpinBox(self.splitter)
        #self.histogram_threshold_min.setObjectName("histogram_threshold_min")
        #self.histogram_threshold_min.setValue(6)#(self.ht_min)*100)
        #self.histogram_threshold_min.setMaximum(10)
        #self.histogram_threshold_min.setMinimum(0)

        #self.histogram_threshold_max = QtWidgets.QDoubleSpinBox(self.splitter)
        #self.histogram_threshold_max.setObjectName("histogram_threshold_max")
        #self.histogram_threshold_max.setValue((self.ht_max) * 100)
        #self.histogram_threshold_max.setMaximum(100)
        #self.histogram_threshold_max.setMinimum(0)

        #self.histogram_threshold_min.setEnabled(True)
        #self.histogram_threshold_max.setEnabled(False)

        self.gridLayout.addWidget(self.splitter, 1, 0, 1, 1)



        self.splitter_2 = QtWidgets.QSplitter(self.widget)
        self.splitter_2.setOrientation(QtCore.Qt.Horizontal)
        self.splitter_2.setObjectName("splitter_2")


        self.label = QtWidgets.QLabel(self.splitter_2)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.fractional_threshold = QtWidgets.QDoubleSpinBox(self.splitter_2)
        self.fractional_threshold.setObjectName("fractional_threshold")

        self.fractional_threshold.setMaximum(10)
        self.fractional_threshold.setMinimum(-10)
        self.fractional_threshold.setSingleStep(0.1)
        self.fractional_threshold.setValue(self.threshold)

        self.pushButton_original = QtWidgets.QPushButton(self.widget)
        self.pushButton_original.setObjectName("pushButton_2")
        self.pushButton_original.clicked.connect(self.back_original)
        self.pushButton_original.setVisible(False)

        #self.label_pma = QtWidgets.QLabel(self.splitter_2)
        #self.label_pma.setAlignment(QtCore.Qt.AlignCenter)
        #self.label_pma.setObjectName("label")
        #self.border_pix = QtWidgets.QDoubleSpinBox(self.splitter_2)
        #self.border_pix.setObjectName("PMA")
        #self.border_pix.setValue((self.borderp))
        #self.border_pix.setMaximum(150)
        #self.border_pix.setMinimum(0)
        #self.border_pix.setSingleStep(5)
        #self.border_pix.valueChanged.connect(partial(self.parChanged, False))
        self.gridLayout.addWidget(self.splitter_2, 2, 0, 1, 1)


        self.splitter_3 = QtWidgets.QSplitter(self.widget)
        self.splitter_3.setOrientation(QtCore.Qt.Horizontal)
        self.splitter_3.setObjectName("splitter_3")

        self.label_fl = QtWidgets.QLabel(self.splitter_3)
        self.label_fl.setAlignment(QtCore.Qt.AlignCenter)
        self.label_fl.setObjectName("label_5")
        self.load_filepath = os.path.join(self._curent_weight_dir)
        self.bt_load_weight = QtWidgets.QPushButton(self.splitter_3)
        self.bt_load_weight.setObjectName("pushButton")
        self.bt_load_weight.pressed.connect(self.load_weight_dialog)
        self.bt_load_weight.setDefault(False)
        self.pushButton = QtWidgets.QPushButton()

        self.pushButton.setObjectName("pushButton")
        self.pushButton.pressed.connect(self.accepted_emit)
        self.hbox2.addWidget(self.pushButton, 0)
        self.pushButton.setDefault(True)
        self.gridLayout.addWidget(self.splitter_3, 3, 0, 1, 1)

        self.widget.setEnabled(False)


        self.grid_main.addWidget(self.widget)
        self.grid_main.addLayout(self.hbox2, 20, 0)

        self.label_pr = QtWidgets.QLabel()
        self.label_pr.setAlignment(QtCore.Qt.AlignCenter)
        self.label_pr.setObjectName("label_2")
        self.label_pr.setText('fdfdf')
        self.label_pr.setVisible(False)

        self.grid_main.addWidget(self.label_pr)
        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)


    def resetParams(self, state):

        self.init_im_rec = None
        self.initial_mask = None

    def back_original(self):
        self.back_orig.emit(0)
        self.pushButton_original.setVisible(False)

    def parChanged(self, model_changed=True):
        """
        if model parameter changed the user needs to run the algorithm again
        :param model_changed:
        :return:
        """
        self.initial_mask = None
        if model_changed:
            ci = self.comboBox_models.currentIndex()
            #if ci== 0:
            #    self.fractional_threshold.setValue(-0.5)
            #    self.load_filepath = os.path.join(self._curent_weight_dir,'unet3d_latest.pth')
            if ci==0:
                self.load_filepath = os.path.join(self._curent_weight_dir,'NMPNET.pth')
                self.fractional_threshold.setValue(-0.5)
            elif ci == 1:
                self.load_filepath = os.path.join(self._curent_weight_dir,'synthstrip.1.pt')
                self.fractional_threshold.setValue(1)
            #elif ci==3:
            #    self.load_filepath = os.path.join(self._curent_weight_dir,'Hybrid_latest_custom.pth')
            #    self.fractional_threshold.setValue(-0.5)
            else:
                return
            self.label_fl.setText(self.load_filepath)
    def load_weight_dialog(self):
        opts = QtWidgets.QFileDialog.DontUseNativeDialog
        pwd = os.path.abspath(__file__)
        source_dir = os.path.dirname(os.path.dirname(pwd))
        fileObj = QtWidgets.QFileDialog.getOpenFileName(self, "Open File", source_dir, "pth (*.pth *.pt)", options=opts)
        if fileObj[0] == '':
            return
        self.load_filepath = fileObj[0]
        self.label_fl.setText(self.load_filepath)
        self.initial_mask = None
        self.init_im_rec = None
    def clear(self):
        # store the image
        self.img = None
        self.shape = None  # 3D shape
        self.mask = None
        self.im_rec = None
        self.initial_mask = None
        self.init_im_rec = None

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "DEEPL BET"))
        self.checkBox.setText(_translate("Dialog", "Advanced"))
        self.comboBox_image.setItemText(0, _translate("Dialog", "Top Image"))
        self.comboBox_image.setItemText(1, _translate("Dialog", "Bottom Image"))
        self.comboBox_image_type.setItemText(0, _translate("Dialog", "Ultrasound"))
        self.comboBox_image_type.setItemText(1, _translate("Dialog", "MRI"))

        self.comboBox_models.setItemText(0, _translate("Dialog", "NPM NET"))
        self.comboBox_models.setItemText(1, _translate("Dialog", "SynthStrip"))


        self.pushButton.setText(_translate("Dialog", "Apply"))
        self.pushButton_original.setText(_translate("Dialog", "Back"))
        self.checkbox_thresholding.setText(_translate("Dialog", "CUDA"))
        self.checkbox_otsu.setText(_translate("Dialog", "Otsu"))

        self.bt_load_weight.setText(_translate("Dialog", "Load Network Weights"))
        self.label.setText(_translate("Dialog", "Threshold"))
        self.label_type.setText(_translate("Dialog", "Image type"))



        self.label_fl.setText(_translate("Dialog", self.load_filepath))


    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        self.closeSig.emit()
        super(BE_DL, self).closeEvent(a0)

    def accepted_emit(self):
        if not hasattr(self,'initial_mask'):
            return
        try:
            self.label_pr.setVisible(True)
            self.label_pr.setText('Initialization...')
            self.pushButton_original.setVisible(False)

            self.progressBar.setValue(5)
            self._progress = 5

            if self.initial_mask is None:
                self.initial_mask, self.init_im_rec = self.initialization()

            self.label_pr.setText('prediction...')
            self.mask = self.compute_mask(self.initial_mask)

            """
            a = self.initial_mask.get_fdata().copy()
            a *= self.mask
            from melage.utils.utils import standardize
            a = standardize(-a, 20)
            a[self.mask==0] = -1
            a = nib.Nifti1Image(a, self.initial_mask.affine, self.initial_mask.header)
            a.to_filename('/home/binibica/eco/172_X_20210325_seg0.nii.gz')
            """
            if self.init_im_rec is not None:
                from melage.utils.utils import standardize
                a1 = standardize(self.img.get_fdata() * self.mask)
                rec = standardize(self.init_im_rec.get_fdata() * self.mask)

                mse = np.mean((a1 - rec) ** 2)
                max_pixel_value = np.max(a1)
                psnr = 10 * np.log10((max_pixel_value ** 2) / mse)
                print("PSNR: {:.2f}".format(psnr))

                from skimage.metrics import structural_similarity
                print("Structural similarity : {:.2f}".format(structural_similarity(a1, rec)))



                imB = self.init_im_rec.get_fdata().copy()
                #bmin, bmax = imB[self.mask>0].min(), imB[self.mask>0].max()
                #imB = (imB - bmin) / (bmax-bmin)  # range
                imB[~(self.mask > 0)] = 0
                #from scipy.ndimage import gaussian_filter
                #alpha, sigma = 1.5, 5
                #blurred = gaussian_filter(imB, 5)
                #sharpened_mask =  (imB - blurred)

                #sharpened_mask = (
                #            (sharpened_mask - sharpened_mask.min()) / (sharpened_mask.max() - sharpened_mask.min()))
                #sharpened_mask[~(self.mask > 0)] = 0
                self.im_rec = nib.Nifti1Image(imB, self.init_im_rec.affine, self.init_im_rec.header)
            else:
                imB = self.img.get_fdata().copy()
                imB[~(self.mask > 0)] = 0
                self.im_rec = nib.Nifti1Image(imB, self.img.affine, self.img.header)
            self.progressBar.setValue(98)
            self.label_pr.setVisible(False)
            self._progress = 100
            self.progressBar.setValue(self._progress)
            self._progress =0
            self.betcomp.emit(True)
            self.pushButton_original.setVisible(True)
        except Exception as e:
            print(e)
            self.screen_error_msgbox(e.args[0])
    def screen_error_msgbox(self, text= None):
        if text is None:
            text = 'There is an error. Screen is not captured. Please check the content.'
        MessageBox = QtWidgets.QMessageBox(self)
        MessageBox.setText(str(text))
        MessageBox.setWindowTitle('Warning')
        MessageBox.show()
        self.progressBar.setValue(0)

    def initialization(self):
        def rescaleint8(x):
            """
            y = a+(b-a)*(x-min(x))/(max(x)-min(x))
            Parameters
            ----------
            x

            Returns
            -------

            """
            oldMin, oldMax = int(x.min()), x.max()
            NewMin, NewMax = 0, 1000
            OldRange = (oldMax - oldMin)
            NewRange = (NewMax - NewMin)
            y = NewMin + (NewRange) * ((x - oldMin) / (OldRange))
            return y
        def signdf(df):
            if df<=0:
                return -1
            else:
                return 1
        pv = self._progress
        self.progressBar.setValue(pv+1)
        #from melage.widgets.be_dl import MRI_bet
        from melage.widgets.be_dl_unet3d import Unet3D

        from melage.widgets.DeepLModels.Unet3DAtt import Unet3DAtt
        from melage.widgets.Synthstrip import StripModel
        # find the center of mass of image
        from nibabel.processing import resample_to_output, resample_from_to
        import torch
        #imA = self.img
        imA = self.img.__class__(self.img.dataobj[:], self.img.affine, self.img.header)

        if self.checkbox_thresholding.isChecked():
            if torch.cuda.is_available() :
                # device = torch.device("cuda")
                device = torch.device("cuda:0")
                torch.cuda.set_device(0)
                torch.backends.cudnn.benchmark = True
            else:
                device = torch.device("cpu")
        else:
            device = torch.device("cpu")
        ci = self.comboBox_models.currentIndex()
        if ci== 0:
            #model = Unet3D(time_embed=True, spacing_embed=True)
            model = Unet3DAtt(time_embed=True, spacing_embed=True)
            #self.fractional_threshold.setValue(-0.5)
        elif ci==1:
            model = StripModel()
            #self.fractional_threshold.setValue(-0.5)
        #elif ci == 2:

            #self.fractional_threshold.setValue(1)
        #elif ci==2:
        #    from melage.widgets.DeepLModels.NPP.models.model import UNet
        #    self.fractional_threshold.setValue(0)
        #    model = UNet()
        #    self.fractional_threshold.setValue(-0.5)
        else:
            return
        model.eval()

        #transform, source = convert_to_ras(imA.affine, target='RAS')
        #imA = imA.as_reoriented(transform)
        #self.borderp = self.border_pix.value()
        self.borderp = 0
        if ci==1:
            transform, source = convert_to_ras(imA.affine, target='LIA')
            imAa = imA.as_reoriented(transform)
            shape_initial = imAa.shape
            image_used, pad_zero = remove_zero(imAa.get_fdata(), 0)
            imAzero = nib.Nifti1Image(image_used, imAa.affine, imAa.header)
            affine_used, header_used = imAa.affine, imAa.header.copy()
            NewSpacing = 1
            imAa = resample_to_output(imAzero, [NewSpacing, NewSpacing, NewSpacing])

            transform, source = convert_to_ras(imAa.affine, target='LIA')
            imAa = imAa.as_reoriented(transform)
            target_shape = np.clip(np.ceil(np.array(imAa.shape[:3]) / 64).astype(int) * 64, 192, 320)
        else:
            shape_initial = imA.shape
            border_value = imA.get_fdata()[0,0,0]
            if self.checkbox_otsu.isChecked():
                try:
                    from melage.utils.utils import Threshold_MultiOtsu
                    border_value = Threshold_MultiOtsu(imA.get_fdata(), 4)[0]
                except:
                    pass
            image_used, pad_zero = remove_zero(imA.get_fdata(), border_value)
            imAzero = nib.Nifti1Image(image_used, imA.affine, imA.header)
            affine_used, header_used = imA.affine, imA.header.copy()
            Spacing = imAzero.header['pixdim'][1:4]

            NewSpacing = Spacing.max()  # [0]
            if Spacing.max() != Spacing.min():
                NewSpacing = Spacing.min()
                Spacing = [Spacing.min()]
            else:
                Spacing = [Spacing[0]]

            minus_sign = False
            maxdim = np.array([el * sp / NewSpacing for el in imAzero.shape for sp in Spacing]).max()
            df = (maxdim - 192)

            if df>0:
                resize_need = True
                #minus_sign = True
                prev_sign = signdf(df)
                while True:
                    maxdim = np.array([el * sp / NewSpacing for el in imAzero.shape for sp in Spacing]).max()
                    df = (maxdim - 192)
                    if signdf(df) != prev_sign:
                        break
                    if abs(abs(df) - self.borderp)<10: #and df <= 0:
                        break
                    if minus_sign:
                        NewSpacing -= 0.1
                    else:
                        NewSpacing += 0.1
                    prev_sign = signdf(df)
                while True:
                    imAa = resample_to_output(imAzero, [NewSpacing, NewSpacing, NewSpacing])
                    df = (np.max(imAa.shape) - 192)
                    if signdf(df) != prev_sign and df < 0:
                        break
                    prev_sign = signdf(df)
                    if abs(df) <= self.borderp and df <= 0:
                        break
                    else:
                        if signdf(df) == -1:
                            minus_sign = True
                            minus_signed = True
                        else:
                            minus_sign = False
                    if minus_sign:
                        NewSpacing -= 0.1
                    else:
                        NewSpacing += 0.1
                transform, source = convert_to_ras(imAa.affine, target='RAS')
                if source!='RAS':
                    imAa = imAa.as_reoriented(transform)
            else:
                resize_need = False
                transform, source = convert_to_ras(imAzero.affine, target='RAS')
                imAa = imAzero.as_reoriented(transform)
                #imAa = nib.Nifti1Image(imAzero.get_fdata(), imAzero.affine, imAzero.header)
        #transform, source = convert_to_ras(imAa.affine, target='RAS')
        #imAa = imAa.as_reoriented(transform)
        pixdim = imAa.header['pixdim'][1:4]
        affine = imAa.affine

        if ci!=1:
            imA = imAa.get_fdata()
            #imA -= imA.min()
            #imA = rescaleint8(imAa.get_fdata())/1000
            #imA = (imA / imA.max()).clip(0, 1)
            if ci==0:
                imA = ((imA - imA.min()) / (imA.max() - imA.min()))
            else:
                imA = 2 * ((imA - imA.min()) / (imA.max() - imA.min())) - 1
            #imA = (imA - imA.mean())/np.std(imA)
            #imA = ((imA - imA.min()) / (imA.max() - imA.min()))
        else:
            imA = imAa.get_fdata()
            imA -= imA.min()
            if np.percentile(imA, 99)!=0:
                imA = (imA / np.percentile(imA, 99)).clip(0, 1)
            else:
                imA = (imA / imA.max()).clip(0, 1)
        if ci==1:
            imA, info_back = centralize_image(imA, list(target_shape))
        else:
            imA, info_back = centralize_image(imA, 192)
        del imAa
        [pads, pads_l, pads_r, npads_l, npads_r, shape_img] = info_back



        #rescaleint8(imA)
        #imA -= imA.min()
        #if np.percentile(imA, 99)!=0:
        #    imA = (imA / np.percentile(imA, 99)).clip(0, 1)
        #else:
        #    imA = (imA / imA.max()).clip(0, 1)

        imA = torch.from_numpy(imA).to(torch.float).unsqueeze(0).unsqueeze(0)


        print('loading model weight...')
        #pma = self.border_pix.value()
        if self.comboBox_image_type.currentIndex()==0:
            eco_mri = -1
        else:
            eco_mri = 1
        #time = torch.from_numpy(np.array([pma, eco_mri])).to(device).unsqueeze(0).to(torch.float)
        if ci!=0:
            time = torch.from_numpy(np.array(eco_mri)).unsqueeze(0).to(torch.float)
            time = torch.concat([time.reshape(-1,1), torch.from_numpy(pixdim).reshape(-1,1)]).squeeze().unsqueeze(0).to(device)
        else:
            time = torch.from_numpy(np.array(eco_mri)).unsqueeze(0).to(torch.float).to(device)
        imA = imA.to(device)
        model.to(device)
        self.progressBar.setValue(40)
        self.label_pr.setText('loading model...')
        if ci==1:
            state_dict = torch.load(self.load_filepath, map_location=device)
            model.load_state_dict(state_dict['model_state_dict'])
        else:
            try:
                state_dict = torch.load(self.load_filepath, map_location=device)
                #d = OrderedDict((k.replace('norm', 'norm2') if 'norm' in k else k, v) for k, v in state_dict['model'].items())
                if hasattr(state_dict, 'forward'):
                    model = state_dict
                else:
                    try:
                        model.load_state_dict(state_dict['state_dict'], strict=False)
                    except:
                        model.load_state_dict(state_dict['model'], strict=False)
            except:
                model = torch.load(self.load_filepath, map_location=device)

        self.progressBar.setValue(50)
        self.label_pr.setText('computing mask...')
        im_mask = model.forward(imA, time)

        if ci==0:
            im_mask, im_rec=im_mask
            im_mask = im_mask.detach().cpu().squeeze().numpy()
            im_rec = im_rec.detach().cpu().squeeze().numpy()
            maxas = [i for i in im_mask.shape]
            im_rec = im_rec[pads_r[0]:maxas[0] - pads_l[0], pads_r[1]:maxas[1] - pads_l[1],
                      pads_r[2]:maxas[2] - pads_l[2]]
            im_rec = ((im_rec - im_rec.min()) * 255 / np.ptp(im_rec))
            im_mask = im_mask[pads_r[0]:maxas[0] - pads_l[0], pads_r[1]:maxas[1] - pads_l[1],
                      pads_r[2]:maxas[2] - pads_l[2]]
        else:
            im_mask = im_mask.detach().cpu().squeeze().numpy()
            maxas = [i for i in im_mask.shape]
            im_mask = im_mask[pads_r[0]:maxas[0] - pads_l[0], pads_r[1]:maxas[1] - pads_l[1], pads_r[2]:maxas[2] - pads_l[2]]
            im_rec = None
        if ci==1:
            mask = nib.Nifti1Image(im_mask, affine, header_used)
            mask = resample_from_to(mask, imAzero)
            im_mask = np.zeros(shape_initial)
            im_mask[pad_zero[0][0]:pad_zero[0][1] + 1, pad_zero[1][0]:pad_zero[1][1] + 1,
            pad_zero[2][0]:pad_zero[2][1] + 1] = mask.get_fdata()
        self.progressBar.setValue(80)
        header = self.img.header.copy()

        header['pixdim'][1:4] = pixdim
        mask = nib.Nifti1Image(im_mask, affine, header)
        if ci==1:
            _, source = convert_to_ras(self.img.affine, target='LIA')
            transform, _ = convert_to_ras(mask.affine, target=source)
            mask = mask.as_reoriented(transform)
        else:
            mask = nib.Nifti1Image(im_mask, affine, header_used)
            _, source = convert_to_ras(self.img.affine)
            transform, _ = convert_to_ras(mask.affine, target=source)
            mask = mask.as_reoriented(transform)
            if im_rec is not None:
                _rec = nib.Nifti1Image(im_rec, affine, header_used)
                _rec = _rec.as_reoriented(transform)
            else:
                _rec = None
            if resize_need:
                mask = resample_from_to(mask, imAzero)
                if _rec is not None:
                    _rec = resample_from_to(_rec, imAzero)
            im_mask = np.ones(shape_initial)*mask.get_fdata()[0,0,0]

            im_mask[pad_zero[0][0]:pad_zero[0][1] + 1, pad_zero[1][0]:pad_zero[1][1] + 1,
            pad_zero[2][0]:pad_zero[2][1] + 1] = mask.get_fdata()
            mask = nib.Nifti1Image(im_mask, self.img.affine, self.img.header)
            if ci==0:
                im_rec = np.ones(shape_initial) * _rec.get_fdata()[0, 0, 0]
                im_rec[pad_zero[0][0]:pad_zero[0][1] + 1, pad_zero[1][0]:pad_zero[1][1] + 1,
                pad_zero[2][0]:pad_zero[2][1] + 1] = _rec.get_fdata()
                im_rec = nib.Nifti1Image(im_rec, self.img.affine, self.img.header)

        return mask, im_rec


    def compute_mask(self, mask):
        """
        Convert surface mesh to volume
        """
        threshold = self.fractional_threshold.value()
        try:
            import surfa as sf
            if type(mask)==sf.image.framed.Volume:
                label = mask.copy()
                label = (label < threshold).connected_component_mask(k=1, fill=True)
                return label.data.astype('int')
        except:
            pass

        #from nibabel.processing import resample_from_to
        from skimage.measure import label as label_connector
        from scipy.ndimage import binary_fill_holes


        im_mask = mask.get_fdata().copy()
        #from utils.utils import Threshold_MultiOtsu


        ind = im_mask >= threshold
        im_mask[ind] = 0
        im_mask[~ind] = 1
        """
        
        if self.checkbox_bone.isChecked():
            A = self.img.get_fdata() * im_mask
            thresholds = Threshold_MultiOtsu(A, 5)
            im_mask[A > thresholds[-1]] = 0
        """
        #label correction
        label_correction = False

        labels = im_mask
        labels = binary_fill_holes(labels)
        labels, labels_freq = LargestCC(labels, connectivity=1)
        argmax = np.argmax(
            [self.img.get_fdata()[labels == el].sum() for el in range(len(labels_freq)) if el != 0]) + 1
        #connectivity = 1
        #labels = label_connector(labels, connectivity=connectivity)
        # labels[labels>1]=1
        #frequency = np.bincount(labels.flat)
        # argmax = [el for el in np.argsort(-frequency) if el != 0][0]
        #argmax = np.argmax([self.img.get_fdata()[labels == el].sum() for el in range(len(frequency)) if el != 0]) + 1
        ind = labels != argmax
        labels[ind] = 0
        labels[~ind]=1

        if label_correction:
            connectivity = 1
            labels = label_connector(im_mask, connectivity=connectivity)
            # labels[labels>1]=1
            frequency = np.bincount(labels.flat)
            #argmax = [el for el in np.argsort(-frequency) if el != 0][0]
            argmax = np.argmax([self.img.get_fdata()[labels==el].sum() for el in range(len(frequency)) if el != 0])+1
            ind = labels != argmax
            labels[ind] = 0
            # labels[~ind]=0
            labels = binary_fill_holes(labels)
            for slc in range(labels.shape[0]):
                im = labels[slc, :, :]
                if im.max() == 0:
                    continue
                labels[slc, :, :] = binary_fill_holes(im)
            for slc in range(labels.shape[1]):
                im = labels[:, slc, :]
                if im.max() == 0:
                    continue
                labels[:, slc, :] = binary_fill_holes(im)

            for slc in range(labels.shape[2]):
                im = labels[:, :, slc]
                if im.max() == 0:
                    continue

                lbl = label_connector(im, connectivity=connectivity)
                frequency = np.bincount(lbl.flat)
                argmax = [el for el in np.argsort(-frequency) if el != 0][0]
                ind_remove = frequency < 0.1 * frequency[argmax]
                if ind_remove.any():
                    index_remove = np.argwhere(ind_remove)
                    for el in index_remove:
                        ind = lbl == el
                        lbl[ind] = 0
                    lbl[lbl > 0] = 1
                else:
                    continue
                labels[:, :, slc] = lbl.copy()

            for slc in range(labels.shape[2]):
                im = labels[:, :, slc]
                if im.max() == 0:
                    continue
                labels[:, :, slc] = binary_fill_holes(im)

        return labels.astype('int')


def run():
    import sys
    app = QtWidgets.QApplication(sys.argv)
    file = 't1_withoutmask.nii.gz'
    import nibabel as nib
    #m = nib.load(file)
    #res = m.header["pixdim"][1]
    #nibf = m.get_fdata()
    from melage.utils.utils import standardize
    #nibf = standardize(nibf)
    window = BE_DL()
    #window.setData(m, res)
    window.set_pars()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    run()

