__AUTHOR__ = 'Bahram Jafrasteh'

from melage.utils.utils import make_affine
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtCore import Qt

from melage.utils.source_folder import source_folder

class RegistrationDialog(QtWidgets.QDialog):
    """
    Image to image registration dialogue
    """
    closeSig = pyqtSignal()
    datachange = pyqtSignal()

    def __init__(self, parent=None, source_dir = 'None'):
        self.source_dir = source_dir
        QtWidgets.QDialog.__init__(self, parent)
        self.setWindowTitle("Child Window!")
        self.setupUi()
        self._sourceFolder = source_folder
        #self.setFixedSize(800,120)
        self.reg_weights_path = None

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        self.closeSig.emit()
        super(RegistrationDialog, self).closeEvent(a0)

    def setupUi(self):
        self.filters = "NifTi (*.nii *.nii.gz)"
        Form = self.window()
        Form.setObjectName("Registration form")
        #Form.resize(750, 120)
        #self = QtWidgets.QWidget(Form)
        #self.setGeometry(QtCore.QRect(11, 11, 731, 101))
        self.setObjectName("widget")
        self.setMinimumSize(750, 120)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
        self.setSizePolicy(sizePolicy)

        self.gridLayout = QtWidgets.QGridLayout(self)
        self.gridLayout.setContentsMargins(10, 10, 10, 10)
        self.gridLayout.setObjectName("gridLayout")
        self.lineEdit_target = QtWidgets.QLineEdit(self)
        self.lineEdit_target.setObjectName("lineEdit_target")
        self.gridLayout.addWidget(self.lineEdit_target, 2, 1, 1, 4)
        self.label_ref = QtWidgets.QLabel(self)
        self.label_ref.setAlignment(QtCore.Qt.AlignCenter)
        self.label_ref.setObjectName("label_ref")

        self.checkBox_ref = QtWidgets.QCheckBox(self)
        self.checkBox_ref.setObjectName("checkBox")


        self.comboBox_image = QtWidgets.QComboBox(self)
        #self.comboBox_image.setGeometry(QtCore.QRect(20, 10, 321, 25))
        self.comboBox_image.setObjectName("comboBox")
        self.comboBox_image.addItem("")
        self.comboBox_image.addItem("")
        #self.comboBox_image.currentIndexChanged.connect(self.datachange)

        #
        self.gridLayout.addWidget(self.checkBox_ref, 0, 0, 1, 2)

        self._splitter0 = QtWidgets.QSplitter(self)
        self._splitter0.setOrientation(QtCore.Qt.Horizontal)
        self._splitter0.setObjectName("splitter")


        self.label_criterion = QtWidgets.QLabel(self._splitter0)
        self.label_criterion.setAlignment(QtCore.Qt.AlignCenter)
        self.label_criterion.setObjectName("label_criterion")
        #self.gridLayout.addWidget(self.label_criterion, 0, 2, 1, 1)

        self.label_method = QtWidgets.QLabel(self)
        self.label_method.setAlignment(QtCore.Qt.AlignCenter)
        self.label_method.setObjectName("label_criterion")
        self.gridLayout.addWidget(self.label_method, 0, 4, 1, 1)

        self.combobox_criterion = QtWidgets.QComboBox(self._splitter0)
        self.combobox_criterion.setObjectName("combobox_criterion")
        self.gridLayout.addWidget(self._splitter0, 0, 2, 1, 1)
        self._list_criterion = ['Mutual Information','Correlation', 'Joint Mutual Information', 'MSE']
        for i, el in enumerate(self._list_criterion):
            self.combobox_criterion.addItem("    {}    ".format(el))
            self.combobox_criterion.setItemData(i, Qt.AlignCenter, Qt.TextAlignmentRole)
        self.combobox_methods = QtWidgets.QComboBox(self)
        self.combobox_methods.setObjectName("combobox_methods")
        self._list_methods = [ 'Rigid', 'Spline','Free Form']
        for i, el in enumerate(self._list_methods):
            self.combobox_methods.addItem("    {}    ".format(el))
            self.combobox_methods.setItemData(i, Qt.AlignCenter, Qt.TextAlignmentRole)
        self.gridLayout.addWidget(self.combobox_methods, 0, 5, 1, 1)




        self.gridLayout.addWidget(self.label_ref, 1, 0, 1, 1)

        self.button_moving = QtWidgets.QPushButton(self)
        self.button_moving.setObjectName("button_moving")
        self.gridLayout.addWidget(self.button_moving, 2, 5, 1, 1)
        self.lineEdit_fixed = QtWidgets.QLineEdit(self)
        self.lineEdit_fixed.setObjectName("lineEdit")

        self.button_fixed = QtWidgets.QPushButton(self)
        self.button_fixed.setObjectName("button_fixed")
        self.gridLayout.addWidget(self.button_fixed, 1, 5, 1, 1)


        self.label_weights = QtWidgets.QLabel(self)
        self.label_weights.setAlignment(QtCore.Qt.AlignCenter)
        self.label_weights.setObjectName("label_ref")
        self.gridLayout.addWidget(self.label_weights, 3, 0, 1, 1)
        self.lineEdit_out = QtWidgets.QLineEdit(self)
        self.lineEdit_out.setObjectName("lineEdit")
        self.gridLayout.addWidget(self.lineEdit_out, 3, 1, 1, 4)
        self.button_out = QtWidgets.QPushButton(self)
        self.button_out.setObjectName("button_out")
        self.gridLayout.addWidget(self.button_out, 3, 5, 1, 1)


        self.label_moving = QtWidgets.QLabel(self)
        self.label_moving.setAlignment(QtCore.Qt.AlignCenter)
        self.label_moving.setObjectName("label_moving")
        self.gridLayout.addWidget(self.label_moving, 2, 0, 1, 1)

        self.lineEdit_fixed.setReadOnly(True)
        self.lineEdit_target.setReadOnly(True)
        self.lineEdit_out.setReadOnly(True)
        self.gridLayout.addWidget(self.comboBox_image, 1, 1, 1, 4)
        self.gridLayout.addWidget(self.lineEdit_fixed, 1, 1, 1, 4)
        self.lineEdit_fixed.setVisible(False)

        self.OK = QtWidgets.QPushButton(self)
        self.OK.setObjectName("checkBox_5")
        self.gridLayout.addWidget(self.OK, 4, 5, 2, 2)

        self.checkBox_multir = QtWidgets.QCheckBox(self)
        self.checkBox_multir.setObjectName("checkBox")
        self.gridLayout.addWidget(self.checkBox_multir, 4, 0, 1, 1)


        self.splitter = QtWidgets.QSplitter(self)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName("splitter")

        self.label_nbins = QtWidgets.QLabel(self.splitter)
        self.label_nbins.setAlignment(QtCore.Qt.AlignCenter)
        self.label_nbins.setObjectName("label_ref")
        #self.gridLayout.addWidget(self.label_nbins, 4, 1, 2, 2)
        self.nobins = QtWidgets.QSpinBox(self.splitter)
        self.nobins.setAlignment(QtCore.Qt.AlignCenter)
        self.nobins.setObjectName("label_ref")
        #self.nobins.setValidator(QtGui.QDoubleValidator())
        #self.nobins.setMaxLength(2)
        #self.nobins.setText('25')
        self.nobins.setMaximum(200)
        self.nobins.setMinimum(10)
        self.nobins.setValue(25)


        self.nobins.setSingleStep(10)

        self.gridLayout.addWidget(self.splitter, 4, 1, 1, 1)

        self.splitter2 = QtWidgets.QSplitter(self)
        self.splitter2.setOrientation(QtCore.Qt.Horizontal)
        self.splitter2.setObjectName("splitter")

        self.label_sp = QtWidgets.QLabel(self.splitter2)
        self.label_sp.setAlignment(QtCore.Qt.AlignCenter)
        self.label_sp.setObjectName("label_ref")
        #self.gridLayout.addWidget(self.label_sp, 4, 3, 1, 1)
        self.sp = QtWidgets.QDoubleSpinBox(self.splitter2)
        self.sp.setAlignment(QtCore.Qt.AlignCenter)
        self.sp.setObjectName("label_ref")
        self.gridLayout.addWidget(self.splitter2, 4, 2, 1, 1)
        self.sp.setMaximum(1)
        self.sp.setMinimum(0.01)
        self.sp.setSingleStep(0.05)
        #self.sp.setValidator(QtGui.QDoubleValidator())
        #self.sp.setMaxLength(1)
        #self.sp.setText()
        self.checkBox_multir.setChecked(True)
        self.checkBox_ref.setChecked(True)
        self.button_fixed.setEnabled(False)
        self.lineEdit_fixed.setEnabled(False)
        self.comboBox_image.currentIndexChanged.connect(self.datachange)

        self.button_fixed.clicked.connect(self.browse_ref)
        self.button_moving.clicked.connect(self.browse_target)
        self.button_out.clicked.connect(self.save_out)
        self.OK.clicked.connect(self.runRegistration)
        self.checkBox_ref.stateChanged.connect(self.activate_advanced)
        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)


    def save_out(self, value):
        from PyQt5.QtWidgets import QFileDialog
        #from utils.utils import getCurrentCoordSystem

        opts = QtWidgets.QFileDialog.DontUseNativeDialog
        dialg = QFileDialog(self, "Open File", self.source_dir, filter='TFM (*.tfm)',options=opts)
        dialg.setFileMode(QFileDialog.AnyFile)
        dialg.setAcceptMode(QFileDialog.AcceptSave)
        if dialg.exec_() == QFileDialog.Accepted:
            self.reg_weights_path = dialg.selectedFiles()[0] + '.tfm'
            self.lineEdit_out.setText(self.reg_weights_path)
        return
    def activate_advanced(self, value):
        self.button_fixed.setEnabled(not value)
        self.lineEdit_fixed.setEnabled(not value)
        self.comboBox_image.setEnabled(value)
        self.comboBox_image.setVisible(value)
        self.lineEdit_fixed.setVisible(not value)

    def setData(self, img):
        self.file_fixed = img

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Registration"))

        self.label_ref.setText(_translate("Form", "Fixed"))
        self.label_nbins.setText(_translate("Form", "No Bins"))
        self.label_sp.setText(_translate("Form", "Sampling"))
        self.checkBox_ref.setText(_translate("Form", "Current image as reference"))
        self.checkBox_multir.setText(_translate("Form", "MultiResolution"))
        self.button_moving.setText(_translate("Form", "Moving"))
        self.button_fixed.setText(_translate("Form", "Fixed"))
        self.button_out.setText(_translate("Form", "Out"))
        self.label_moving.setText(_translate("Form", "Moving"))
        self.label_weights.setText(_translate("Form", "Weights"))
        self.comboBox_image.setItemText(0, _translate("Dialog", "Top Image"))
        self.comboBox_image.setItemText(1, _translate("Dialog", "Bottom Image"))
        self.label_criterion.setText(_translate("Form", "Criterion"))
        self.label_method.setText(_translate("Form", "Method"))
        self.OK.setText(_translate("Form", "REGISTER"))


    def accepted_emit(self):
        self.lineEdit.text()
        num = self.lineEdit.text()
        if num=='' or float(num)==0:
            self.message()
            return False
        txt = self.lineEdit2.text()
        if txt=='':
            self.message()
            return False
        self.ColorIndName.emit([num, txt])
        self.accept()

    def browse_ref(self):
        fileObj = ['', '']
        #if fileObj is None or type(fileObj) is bool:
        opts = QtWidgets.QFileDialog.DontUseNativeDialog
        dialg = QFileDialog( self, "Open File", self.source_dir, self.filters, options=opts)
        dialg.setFileMode(QtWidgets.QFileDialog.ExistingFile)
        if dialg.exec_() == QFileDialog.Accepted:
            fileObj = dialg.selectedFiles()
            if len(fileObj)>0:
                self.file_fixed = fileObj[0]
                self.lineEdit_fixed.setText(self.file_fixed)

    def browse_target(self):
        fileObj = ['', '']
        #if fileObj is None or type(fileObj) is bool:
        opts = QtWidgets.QFileDialog.DontUseNativeDialog
        dialg = QFileDialog( self, "Open File", self.source_dir, self.filters, options=opts)
        dialg.setFileMode(QtWidgets.QFileDialog.ExistingFile)
        if dialg.exec_() == QFileDialog.Accepted:
            fileObj = dialg.selectedFiles()
            if len(fileObj)>0:
                self.file_moving = fileObj[0]
                self.lineEdit_target.setText(self.file_moving)
    def runRegistration(self):
        #self.file_moving = '/home/binibica/PycharmProjects/tmp/HPUM8_01.nii.gz'
        #self.file_fixed ='/home/binibica/PycharmProjects/tmp/8149_X_20180111_X_t1_rescaled.nii.gz'

        from melage.utils.registration import FFD_registration, RegistrationSpline, RegistrationRigid
        from melage.utils.utils import read_nib_as_sitk

        if not (hasattr(self, 'file_moving') and hasattr(self, 'file_fixed')):
            return
        if self.reg_weights_path is None:
            return



        method = self._list_methods[self.combobox_methods.currentIndex()].lower()
        criterion = self._list_criterion[self.combobox_criterion.currentIndex()].lower()


        normalized = True
        params = dict()
        params['fixed_mask'] = None
        params['fixed_points'] = None
        params['moving_points'] = None
        params['MultiRes'] = self.checkBox_multir.isChecked()
        params['nbins'] = int(self.nobins.value())
        params['sp'] = self.sp.value()  # sampling percentage
        import SimpleITK as sitk
        if type(self.file_fixed)!= str:
            fixed = read_nib_as_sitk(self.file_fixed)
        else:
            fixed = sitk.ReadImage(self.file_fixed, sitk.sitkFloat32)

        moving = sitk.ReadImage(self.file_moving, sitk.sitkFloat32)

        if normalized or criterion=='mse':
            fixed = sitk.Normalize(fixed)
            fixed = sitk.DiscreteGaussian(fixed, 2.0)
            moving = sitk.Normalize(moving)
            moving = sitk.DiscreteGaussian(moving, 2.0)
        if method == 'Rigid':
            out, outTx = RegistrationRigid(fixed, moving, criterion, *[params])
        elif method=='Spline':
            out, outTx = RegistrationSpline(fixed, moving, criterion, *[params])
        elif method=='Free Form':
            out, outTx = FFD_registration(fixed, moving, criterion, *[params])
        else:
            return
        sitk.WriteTransform(outTx, self.reg_weights_path)


def run():
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = RegistrationDialog()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    run()