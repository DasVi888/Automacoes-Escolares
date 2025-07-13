from PySide6.QtWidgets import QMainWindow, QApplication
from cred_ui import Ui_Form

class CreditsWindow(QMainWindow):
    def __init__(self, translator_manager):
        super().__init__()
        self.translator_manager = translator_manager
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.translate_ui()

    def translate_ui(self):
        self.setWindowTitle(self.translator_manager.translate("credits"))
        self.ui.label.setText(self.translator_manager.translate("credits_developed_by"))
        self.ui.label_2.setText(self.translator_manager.translate("credits_advisors"))
