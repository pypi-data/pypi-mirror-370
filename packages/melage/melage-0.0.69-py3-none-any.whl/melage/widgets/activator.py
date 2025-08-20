

from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import pyqtSignal
from cryptography.fernet import Fernet




class activation_dialog(QtWidgets.QDialog):
    ColorIndName = pyqtSignal(object)
    def __init__(self, parent=None, source_dir=None):
        QtWidgets.QDialog.__init__(self, parent)
        self.setWindowTitle("Activation")
        self.setupUi()
        self.source_dir = source_dir
        self._key = b'06P-FDiXLVUICoQ7pHk0GjaDoCv7lRGA1LJtTdYMHbI='
    def setupUi(self):
        Activate = self.window()
        Activate.setObjectName("Dialog")
        Activate.resize(490, 160)

        self.widget = QtWidgets.QWidget(Activate)
        self.widget.setGeometry(QtCore.QRect(10, 20, 471, 131))
        self.widget.setObjectName("widget")
        self.gridLayout = QtWidgets.QGridLayout(self.widget)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")
        self.days_l = QtWidgets.QLineEdit(self.widget)
        self.days_l.setAlignment(QtCore.Qt.AlignCenter)
        self.days_l.setObjectName("emial_l")
        self.gridLayout.addWidget(self.days_l, 2, 1, 1, 1)
        self.key = QtWidgets.QLabel(self.widget)
        self.key.setAlignment(QtCore.Qt.AlignCenter)
        self.key.setObjectName("key")
        self.gridLayout.addWidget(self.key, 1, 0, 1, 1)
        self.key_l = QtWidgets.QLineEdit(self.widget)
        self.key_l.setObjectName("key_l")
        self.gridLayout.addWidget(self.key_l, 1, 1, 1, 1)
        self.user = QtWidgets.QLabel(self.widget)
        self.user.setAlignment(QtCore.Qt.AlignCenter)
        self.user.setObjectName("user")
        self.gridLayout.addWidget(self.user, 0, 0, 1, 1)
        self.user_l = QtWidgets.QLineEdit(self.widget)
        #self.user_l.setReadOnly(True)
        self.user_l.setObjectName("user_l")
        self.user_l.textChanged.connect(self.generate_id)
        self.gridLayout.addWidget(self.user_l, 0, 1, 1, 1)
        self.buttonBox = QtWidgets.QDialogButtonBox(self.widget)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel | QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.buttonBox.accepted.connect(self.accepted_emit)
        self.gridLayout.addWidget(self.buttonBox, 3, 1, 1, 1)
        self.days = QtWidgets.QLabel(self.widget)
        self.days.setAlignment(QtCore.Qt.AlignCenter)
        self.days.setObjectName("email")
        self.gridLayout.addWidget(self.days, 2, 0, 1, 1)
        self.key_l.setReadOnly(True)
        self.days_l.setValidator(QtGui.QIntValidator())
        self.days_l.setMaxLength(7)
        self.MessageBox = QtWidgets.QMessageBox(self)
        self.retranslateUi(Activate)
        self.buttonBox.rejected.connect(Activate.reject)  # type: ignore
 # type: ignore
        QtCore.QMetaObject.connectSlotsByName(Activate)
    def encrypt(self,message: bytes) -> bytes:
        return Fernet(self._key).encrypt(message)

    def decrypt(self, token: bytes) -> bytes:
        return Fernet(self._key).decrypt(token)
    def generate_id(self):
        import uuid
        from base64 import b64encode
        #init = uuid.getnode()
        #id = str(init)
        try:
            txt = self.user_l.text().strip()
            self.id = self.decrypt(bytes(txt, 'utf-8')).decode('utf-8')
        except:
            pass
        #self.user_l.setText(id)



    def retranslateUi(self, Activate):
        _translate = QtCore.QCoreApplication.translate
        Activate.setWindowTitle(_translate("Activate", "Key Generator"))
        self.days_l.setText(_translate("Activate", "15"))
        self.key.setText(_translate("Activate", "Key"))
        self.user.setText(_translate("Activate", "User"))
        self.days.setText(_translate("Activate", "Number of Days"))

    def _create_pass(self):
        import uuid
        from base64 import b64encode
        str_int = self.id[:-8]
        self.registration_date = self.id[-8:]
        str_total = str_int
        i = 0
        while True:
            if int(str_total).bit_length()>=128:
                break
            str_total += str_int[i]
            i += 1
            if i >= len(str_int):
                i = 0
        while True:
            if int(str_total).bit_length()<=128:
                break
            str_total = str_total[:-1]

        id_bytes = uuid.UUID(int=int(str_total))
        txt = b64encode(id_bytes.bytes).decode('utf-8')
        #generate_number = [ord(i) for i in txt[::-1]]
        list_alphabet = [ord(chr(i)) for i in range(ord('A'), ord('Z') + 1)]
        passwd = ''.join([chr(ord(i)) if ord(i) in list_alphabet else str(ord(i)) for i in txt[::-1]])
        return passwd
    def generate_key(self):
        try:
            import datetime
            passwd = self._create_pass()
            current_date = self.registration_date#datetime.datetime.today().strftime('%Y-%m-%d')
            expiration_date = (datetime.datetime.today() + datetime.timedelta(days=int(float(self.days_l.text())))).strftime('%Y-%m-%d')
            key = self.encrypt(bytes(passwd + '_X_BAHRAM_X_' + current_date + '_X_BAHRAM_X_' + expiration_date+'_X_BAHRAM_X_'+'FULL', 'utf-8'))
            return key.decode('utf-8')
        except:
            return '0'



    def accepted_emit(self):
            self.key_l.setText(self.generate_key())





def run():
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = activation_dialog()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    run()