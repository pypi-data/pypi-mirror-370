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

    xs, ys, zs = np.where(f_data > value)  # find zero values
    tol = 4

    min_max = []
    for x in [xs, ys, zs]:
        minx = min(x) - tol if min(x) - tol > 1 else min(x)
        maxx = max(x) + tol if max(x) + tol < f_data.shape[0] - 1 else max(x)
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
        maxas = [maxas, maxas, maxas]
    pads = np.array([maxas[i] - a for i, a in enumerate(n)])
    pads_r = pads // 2
    pads_l = pads - pads_r
    npads_l = pads_l * -1
    npads_r = pads_r * -1
    if border is None:
        border = img[0, 0, 0]
    new_img = np.ones((maxas[0], maxas[1], maxas[2])) * border

    pads_r[pads_r < 0] = 0
    pads_l[pads_l < 0] = 0
    npads_l[npads_l < 0] = 0
    npads_r[npads_r < 0] = 0
    # print(pads_l, pads_r)
    new_img[pads_r[0]:maxas[0] - pads_l[0], pads_r[1]:maxas[1] - pads_l[1], pads_r[2]:maxas[2] - pads_l[2]] = img[
                                                                                                              npads_r[
                                                                                                                  0]:n[
                                                                                                                         0] -
                                                                                                                     npads_l[
                                                                                                                         0],
                                                                                                              npads_r[
                                                                                                                  1]:n[
                                                                                                                         1] -
                                                                                                                     npads_l[
                                                                                                                         1],
                                                                                                              npads_r[
                                                                                                                  2]:n[
                                                                                                                         2] -
                                                                                                                     npads_l[
                                                                                                                         2]]
    return new_img, [pads, pads_l, pads_r, npads_l, npads_r, n]


class Tissue_Seg(QDialog):
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
        super(Tissue_Seg, self).__init__(parent)
        # self.load_filepath = 'widgets/Hybrid_latest.pth'
        self._curent_weight_dir = os.path.dirname(os.path.join(os.getcwd()))
        """
        Initialization of Brain Extractor

        Computes image range/thresholds and
        estimates the brain radius
        """

    def set_pars(self, threshold=50, remove_extra_bone=True):
        # print("Initializing...")

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
        for i in range(3):
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


        self.checkbox_post = QtWidgets.QCheckBox(self.splitter)
        # self.checkbox_post.setAlignment(QtCore.Qt.AlignCenter)


        # self.checkbox_bone = QtWidgets.QCheckBox(self.splitter)
        # self.checkbox_bone.setObjectName("histogram_bone")
        # self.checkbox_bone.setChecked(False)
        self.label_type = QtWidgets.QLabel(self.splitter)
        self.label_type.setAlignment(QtCore.Qt.AlignCenter)
        self.label_type.setObjectName("label")
        self.spinbox_num_tissue = QtWidgets.QSpinBox(self.splitter)

        self.spinbox_num_tissue.setMaximum(50)
        self.spinbox_num_tissue.setMinimum(2)
        self.spinbox_num_tissue.setSingleStep(1)
        self.spinbox_num_tissue.setValue(3)

        #self.spinbox_num_tissue.setGeometry(QtCore.QRect(20, 10, 321, 25))
        #self.spinbox_num_tissue.setObjectName("comboBox")
        #self.spinbox_num_tissue.setCurrentIndex(0)
        #self.spinbox_num_tissue.currentIndexChanged.connect(partial(self.parChanged, False))
        #for i in range(2):
        #    self.spinbox_num_tissue.addItem("")

        # self.histogram_threshold_min = QtWidgets.QDoubleSpinBox(self.splitter)
        # self.histogram_threshold_min.setObjectName("histogram_threshold_min")
        # self.histogram_threshold_min.setValue(6)#(self.ht_min)*100)
        # self.histogram_threshold_min.setMaximum(10)
        # self.histogram_threshold_min.setMinimum(0)

        # self.histogram_threshold_max = QtWidgets.QDoubleSpinBox(self.splitter)
        # self.histogram_threshold_max.setObjectName("histogram_threshold_max")
        # self.histogram_threshold_max.setValue((self.ht_max) * 100)
        # self.histogram_threshold_max.setMaximum(100)
        # self.histogram_threshold_max.setMinimum(0)

        # self.histogram_threshold_min.setEnabled(True)
        # self.histogram_threshold_max.setEnabled(False)

        self.gridLayout.addWidget(self.splitter, 1, 0, 1, 1)

        self.splitter_2 = QtWidgets.QSplitter(self.widget)
        self.splitter_2.setOrientation(QtCore.Qt.Horizontal)
        self.splitter_2.setObjectName("splitter_2")

        self.label = QtWidgets.QLabel(self.splitter_2)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.max_iter = QtWidgets.QSpinBox(self.splitter_2)
        self.max_iter.setObjectName("fractional_threshold")

        self.max_iter.setMaximum(1000)
        self.max_iter.setMinimum(2)
        self.max_iter.setSingleStep(1)
        self.max_iter.setValue(50)



        # self.label_pma = QtWidgets.QLabel(self.splitter_2)
        # self.label_pma.setAlignment(QtCore.Qt.AlignCenter)
        # self.label_pma.setObjectName("label")
        # self.border_pix = QtWidgets.QDoubleSpinBox(self.splitter_2)
        # self.border_pix.setObjectName("PMA")
        # self.border_pix.setValue((self.borderp))
        # self.border_pix.setMaximum(150)
        # self.border_pix.setMinimum(0)
        # self.border_pix.setSingleStep(5)
        # self.border_pix.valueChanged.connect(partial(self.parChanged, False))
        self.gridLayout.addWidget(self.splitter_2, 2, 0, 1, 1)

        self.splitter_3 = QtWidgets.QSplitter(self.widget)
        self.splitter_3.setOrientation(QtCore.Qt.Horizontal)
        self.splitter_3.setObjectName("splitter_3")


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



    def parChanged(self, model_changed=True):
        """
        if model parameter changed the user needs to run the algorithm again
        :param model_changed:
        :return:
        """
        self.initial_mask = None
        if model_changed:
            ci = self.comboBox_models.currentIndex()
            if ci == 0:
                self.max_iter.setValue(50)

            elif ci == 1:
                self.max_iter.setValue(50)
            elif ci == 2:
                self.max_iter.setValue(1)
            else:
                return



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
        Dialog.setWindowTitle(_translate("Dialog", "Tissue Segmetnation"))
        self.checkBox.setText(_translate("Dialog", "Advanced"))
        self.comboBox_image.setItemText(0, _translate("Dialog", "View 1"))
        self.comboBox_image.setItemText(1, _translate("Dialog", "View 2"))
        #self.spinbox_num_tissue.setItemText(0, _translate("Dialog", "Ultrasound"))
        #self.spinbox_num_tissue.setItemText(1, _translate("Dialog", "MRI"))
        self.comboBox_models.setItemText(0, _translate("Dialog", "esFCM"))
        self.comboBox_models.setItemText(1, _translate("Dialog", "FCM"))
        self.comboBox_models.setItemText(2, _translate("Dialog", "GMM"))


        self.pushButton.setText(_translate("Dialog", "Apply"))

        self.checkbox_post.setText(_translate("Dialog", "PostCorr."))
        # self.checkbox_bone.setText(_translate("Dialog", "Remove extra bone"))

        self.label.setText(_translate("Dialog", "No. Iteration"))
        self.label_type.setText(_translate("Dialog", "Image type"))

        # self.label_pma.setText(_translate("Dialog", "Border Pixels"))


    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        self.closeSig.emit()
        super(Tissue_Seg, self).closeEvent(a0)

    def accepted_emit(self):
        if not hasattr(self, 'initial_mask'):
            return
        try:
            self.label_pr.setVisible(True)
            self.label_pr.setText('Initialization...')


            self.progressBar.setValue(5)
            self._progress = 5

            if self.initial_mask is None:
                self.mask = self.initialization()




            """
            a = self.initial_mask.get_fdata().copy()
            a *= self.mask
            from melage.utils.utils import standardize
            a = standardize(-a, 20)
            a[self.mask==0] = -1
            a = nib.Nifti1Image(a, self.initial_mask.affine, self.initial_mask.header)
            a.to_filename('/home/binibica/eco/172_X_20210325_seg0.nii.gz')
            """

            self.im_seg = nib.Nifti1Image(self.mask, self.img.affine, self.img.header)
            self.progressBar.setValue(98)
            self.label_pr.setVisible(False)
            self._progress = 100
            self.progressBar.setValue(self._progress)
            self._progress = 0
            self.betcomp.emit(True)

        except Exception as e:
            print(e)
            self.screen_error_msgbox(e.args[0])

    def screen_error_msgbox(self, text=None):
        if text is None:
            text = 'There is an error. Screen is not captured. Please check the content.'
        MessageBox = QtWidgets.QMessageBox(self)
        MessageBox.setText(str(text))
        MessageBox.setWindowTitle('Warning')
        MessageBox.show()
        self.progressBar.setValue(0)

    def initialization(self):
        ci = self.comboBox_models.currentIndex()
        use_ssim = True
        equalize = False
        padding = 0
        image_range = 1000
        tissue_labels = None
        num_tissues = self.spinbox_num_tissue.value()
        fuzziness = 3
        post_correction = self.checkbox_post.isChecked()
        constraint = False
        InitMethod = 'otsu'
        if num_tissues>3 and not constraint:
            post_correction = False
            InitMethod = "kmeans"

        epsilon = 5e-3
        max_iter = self.max_iter.value()
        image_used, pad_zero = remove_zero(self.img.get_fdata(), 0)
        if ci == 0:
            from melage.widgets.Segmentation.FCM import esFCM


            model = esFCM(image_used, self.img.affine,
                          image_range, num_tissues, fuzziness,
                          epsilon=epsilon, max_iter=max_iter,
                          padding=padding,
                          tissuelabels=tissue_labels,
                          mask=image_used>0, use_ssim=use_ssim)
            try:
                model.initialize_fcm(initialization_method=InitMethod)
            except:
                model.initialize_fcm(initialization_method='kmeans')

            model.fit(self.progressBar)
            seg1 = model.predict(use_softmax=True).astype('int')
            seg_init2 = np.zeros(self.img.shape)
            seg_init2[pad_zero[0][0]:pad_zero[0][1] + 1, pad_zero[1][0]:pad_zero[1][1] + 1,
            pad_zero[2][0]:pad_zero[2][1] + 1] = seg1
            return seg_init2

        elif ci == 1:
            from melage.widgets.Segmentation.FCM import FCM_pure as FCM
            model = FCM(image_used, self.img.affine, None,
                          image_range, num_tissues, fuzziness,
                          epsilon=epsilon, max_iter=max_iter,
                          padding=padding, constraint=False, post_correction=True, mask =image_used>0)
            try:
                model.initialize_fcm(initialization_method=InitMethod)
            except:
                model.initialize_fcm(initialization_method='kmeans')
            model.fit(self.progressBar)
            seg1 = model.predict(use_softmax=True).astype('int')
            seg_init2 = np.zeros(self.img.shape)
            seg_init2[pad_zero[0][0]:pad_zero[0][1] + 1, pad_zero[1][0]:pad_zero[1][1] + 1,
            pad_zero[2][0]:pad_zero[2][1] + 1] = seg1
            return seg_init2
        elif ci == 2:
            self.max_iter.setValue(1)
        else:
            return

    def compute_mask(self, mask):
        """
        Convert surface mesh to volume
        """
        threshold = self.max_iter.value()
        try:
            import surfa as sf
            if type(mask) == sf.image.framed.Volume:
                label = mask.copy()
                label = (label < threshold).connected_component_mask(k=1, fill=True)
                return label.data.astype('int')
        except:
            pass

        # from nibabel.processing import resample_from_to
        from skimage.measure import label as label_connector
        from scipy.ndimage import binary_fill_holes

        im_mask = mask.get_fdata().copy()
        # from utils.utils import Threshold_MultiOtsu

        ind = im_mask >= threshold
        im_mask[ind] = 0
        im_mask[~ind] = 1
        """

        if self.checkbox_bone.isChecked():
            A = self.img.get_fdata() * im_mask
            thresholds = Threshold_MultiOtsu(A, 5)
            im_mask[A > thresholds[-1]] = 0
        """
        # label correction
        label_correction = False

        labels = im_mask
        labels = binary_fill_holes(labels)
        labels, labels_freq = LargestCC(labels, connectivity=1)
        argmax = np.argmax(
            [self.img.get_fdata()[labels == el].sum() for el in range(len(labels_freq)) if el != 0]) + 1
        # connectivity = 1
        # labels = label_connector(labels, connectivity=connectivity)
        # labels[labels>1]=1
        # frequency = np.bincount(labels.flat)
        # argmax = [el for el in np.argsort(-frequency) if el != 0][0]
        # argmax = np.argmax([self.img.get_fdata()[labels == el].sum() for el in range(len(frequency)) if el != 0]) + 1
        ind = labels != argmax
        labels[ind] = 0
        labels[~ind] = 1

        if label_correction:
            connectivity = 1
            labels = label_connector(im_mask, connectivity=connectivity)
            # labels[labels>1]=1
            frequency = np.bincount(labels.flat)
            # argmax = [el for el in np.argsort(-frequency) if el != 0][0]
            argmax = np.argmax(
                [self.img.get_fdata()[labels == el].sum() for el in range(len(frequency)) if el != 0]) + 1
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
    # m = nib.load(file)
    # res = m.header["pixdim"][1]
    # nibf = m.get_fdata()
    from melage.utils.utils import normalize_mri
    # nibf = standardize(nibf)
    window = Tissue_Seg()
    # window.setData(m, res)
    window.set_pars()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    run()

