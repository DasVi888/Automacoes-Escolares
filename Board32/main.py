#MADE BY DAVI CORVELLO COELHO WILCKE - INDUSTRIAL AUTOMATION - CEFET-RJ
#ADVISORS: LEANDRO MARQUES SAMYN AND ARCANO MATHEUS BRAGANÇA LEITE 

from PySide6.QtCore import Qt, QLocale, QTimer, QPoint, QRect, QBuffer, QByteArray, QTranslator, QObject, Signal, QThread
from PySide6.QtWidgets import QInputDialog, QApplication, QMessageBox, QLabel, QWidget, QSizePolicy, QMainWindow, QFileDialog, QGraphicsView, QGraphicsScene, QGraphicsTextItem, QVBoxLayout, QColorDialog
from untitled_ui import Ui_MainWindow
from PySide6.QtGui import QPdfWriter, QGuiApplication, QIcon, QBrush, QPen, QColor, QPainter, QImage, QKeySequence, QShortcut, QPageSize, QGuiApplication, QCursor, QPixmap, QBitmap, QTabletEvent, QFont
import sys
from exec_credits import *
import pickle
import sys
import os
from zipfile import ZipFile
import tempfile
from PySide6.QtGui import QAction
import serial
import threading
from camera import start_camera
import queue


brushColor = QColor(0, 0, 0)
brushSize = 3


LANGUAGE_FILE = "language.txt"
class TranslatorManager:
    def __init__(self, app):
        
        self.app = app
        self.translator = None
        self.current_language = "en"
        self.translations = {
            "en": self.get_english_translations(),
            "pt": self.get_portuguese_translations(),
            "es": self.get_spanish_translations()
        }
        if os.path.exists(LANGUAGE_FILE):
            with open(LANGUAGE_FILE, "r", encoding="utf-8") as f:
                saved_lang = f.read().strip().lower()
                if saved_lang in self.translations:
                    self.set_language(saved_lang)

    
    def get_english_translations(self):
        return {
            "board_title": "Board32",
            "save_document": "Save Document",
            "paint_files": "Paint Files (*.pnt)",
            "open_document": "Open Document",
            "error": "Error",
            "open_error": "Failed to open file: {error}",
            "unsaved_changes": "Unsaved Changes",
            "save_prompt": "You haven't saved your changes yet. Do you want to save before closing?",
            "save": "Save",
            "discard": "Discard",
            "cancel": "Cancel",
            "save_png": "Save as PNG",
            "png_files": "PNG Files (*.png)",
            "success": "Success!",
            "png_saved": "PNG file saved successfully!",
            "png_error": "Unable to save PNG file.",
            "save_all_rar": "Save All Pages as RAR",
            "rar_files": "RAR Files (*.rar)",
            "all_saved": "All pages were saved in RAR file:\n{rar_name}",
            "language": "Language",
            "portuguese_set": "Language changed to Portuguese",
            "portuguese_error": "Could not load Portuguese translation file",
            "spanish_set": "Language changed to Spanish",
            "spanish_error": "Could not load Spanish translation file",
            "english_set": "Language changed to default (English)",
            "delete_page_confirm": "Are you sure you want to delete this page?",
            "page": "Page",
            "delete": "Delete",
            "clean_board": "Clean Board",
            "clean_prompt": "Are you sure you want to clean the board? All drawings will be erased.",
            "new_file": "New File",
            "new_file_prompt": "Create a new file? Unsaved changes will be lost.",
            "close_without_saving": "Close without saving",
            "discard_changes": "Discard Changes",
            "yes": "Yes",
            "no": "No",
            "save_as_pdf": "Save as PDF",
            "pdf_files": "PDF Files (*.pdf)",
            "pdf_saved": "PDF saved successfully at:\n{file_path}",
            "save_all_png": "Save All Pages as PNG",
            "file_menu": "File",
            "edit_menu": "Edit",
            "page_menu": "Page",
            "tools_menu": "Tools",
            "help_menu": "Help",
            "new_action": "New",
            "open_action": "Open",
            "save_action": "Save",
            "exit_action": "Exit",
            "presentation_mode": "Presentation Mode",
            "fullscreen": "Fullscreen",
            "show_hide_menubar": "Show/Hide Menubar",
            "show_toolbar": "Show Toolbar",
            "credits": "Credits",
            "hide_cursor": "Hide cursor",
            "credits_developed_by": '<html><head/><body><p><span style="font-size:14pt; font-weight:700; font-style:italic; text-decoration: underline;">DEVELOPED BY: DAVI CORVELLO, PEDRO LUKAS AND PEDRO OLIVEIRA</span></p></body></html>',
            "credits_advisors": '<html><head/><body><p><span style="font-size:14pt; font-weight:700; font-style:italic; text-decoration: underline;">ADVISORS: LEANDRO MARQUES SAMYN AND ARCANO MATHEUS BRAGANÇA LEITE</span></p></body></html>',
            "search_page": "Search page",
            "no_com_registered_prompt": "No COM port registered for controller bluetooth, do you want to continue?",
            "bt_connect_fail_prompt":   "The program could not connect to the controller bluetooth, do you want to continue?",
            "yes": "Yes",
            "no":  "No",
        }
    
    def get_portuguese_translations(self):
        return {
            "board_title": "Board32",
            "save_document": "Salvar Documento",
            "paint_files": "Arquivos de Pintura (*.pnt)",
            "open_document": "Abrir Documento",
            "error": "Erro",
            "open_error": "Falha ao abrir o arquivo: {error}",
            "unsaved_changes": "Alterações não salvas",
            "save_prompt": "Você não salvou suas alterações. Deseja salvar antes de fechar?",
            "save": "Salvar",
            "discard": "Descartar",
            "cancel": "Cancelar",
            "save_png": "Salvar como PNG",
            "png_files": "Arquivos PNG (*.png)",
            "success": "Sucesso!",
            "png_saved": "Arquivo PNG salvo com sucesso!",
            "png_error": "Não foi possível salvar o arquivo PNG.",
            "save_all_rar": "Salvar Todas as Páginas como RAR",
            "rar_files": "Arquivos RAR (*.rar)",
            "all_saved": "Todas as páginas foram salvas no arquivo RAR:\n{rar_name}",
            "language": "Idioma",
            "portuguese_set": "Idioma alterado para Português",
            "portuguese_error": "Não foi possível carregar o arquivo de tradução português",
            "spanish_set": "Idioma alterado para Espanhol",
            "spanish_error": "Não foi possível carregar o arquivo de tradução espanhol",
            "english_set": "Idioma alterado para Inglês (padrão)",
            "delete_page_confirm": "Tem certeza que deseja excluir esta página?",
            "page": "Página",
            "delete": "Excluir",
            "clean_board": "Limpar Quadro",
            "clean_prompt": "Tem certeza que deseja limpar o quadro? Todos os desenhos serão apagados.",
            "new_file": "Novo Arquivo",
            "new_file_prompt": "Criar um novo arquivo? As alterações não salvas serão perdidas.",
            "close_without_saving": "Fechar sem salvar",
            "discard_changes": "Descartar alterações",
            "yes": "Sim",
            "no": "Não",
            "save_as_pdf": "Salvar como PDF",
            "pdf_files": "Arquivos PDF (*.pdf)",
            "pdf_saved": "PDF salvo com sucesso em:\n{file_path}",
            "save_all_png": "Salvar Todas as Páginas como PNG",
            "file_menu": "Arquivo",
            "edit_menu": "Editar",
            "page_menu": "Página",
            "tools_menu": "Ferramentas",
            "help_menu": "Ajuda",
            "new_action": "Novo",
            "open_action": "Abrir",
            "save_action": "Salvar",
            "exit_action": "Sair",
            "presentation_mode": "Modo Apresentação",
            "fullscreen": "Tela Cheia",
            "show_hide_menubar": "Mostrar/Ocultar Barra de Menu",
            "show_toolbar": "Mostrar Barra de Ferramentas",
            "credits": "Créditos",
            "hide_cursor": "Esconder o cursor",
            "credits_developed_by": '<html><head/><body><p><span style="font-size:14pt; font-weight:700; font-style:italic; text-decoration: underline;">DESENVOLVIDO POR: DAVI CORVELLO, PEDRO LUKAS E PEDRO OLIVEIRA</span></p></body></html>',
            "credits_advisors": '<html><head/><body><p><span style="font-size:14pt; font-weight:700; font-style:italic; text-decoration: underline;">ORIENTADORES: LEANDRO MARQUES SAMYN E ARCANO MATHEUS BRAGANÇA LEITE</span></p></body></html>',
            "search_page": "Procurar página",
            "no_com_registered_prompt": "Não há porta COM registrada para bluetooth do controle, deseja continuar?",
            "bt_connect_fail_prompt":       "O programa não conseguiu se conectar com o bluetooth do controle, deseja continuar?",
            "yes": "Sim",
            "no":  "Não",

        }
    
    def get_spanish_translations(self):
        return {
            "board_title": "Board32",
            "save_document": "Guardar Documento",
            "paint_files": "Archivos de Pintura (*.pnt)",
            "open_document": "Abrir Documento",
            "error": "Error",
            "open_error": "Error al abrir el archivo: {error}",
            "unsaved_changes": "Cambios no guardados",
            "save_prompt": "No has guardado tus cambios. ¿Quieres guardar antes de cerrar?",
            "save": "Guardar",
            "discard": "Descartar",
            "cancel": "Cancelar",
            "save_png": "Guardar como PNG",
            "png_files": "Archivos PNG (*.png)",
            "success": "¡Éxito!",
            "png_saved": "¡Archivo PNG guardado con éxito!",
            "png_error": "No se pudo guardar el archivo PNG.",
            "save_all_rar": "Guardar Todas las Páginas como RAR",
            "rar_files": "Archivos RAR (*.rar)",
            "all_saved": "Todas las páginas se guardaron en el archivo RAR:\n{rar_name}",
            "language": "Idioma",
            "portuguese_set": "Idioma cambiado a Portugués",
            "portuguese_error": "No se pudo cargar el archivo de traducción portugués",
            "spanish_set": "Idioma cambiado a Español",
            "spanish_error": "No se pudo cargar el archivo de traducción español",
            "english_set": "Idioma cambiado a Inglés (predeterminado)",
            "delete_page_confirm": "¿Estás seguro de que quieres eliminar esta página?",
            "page": "Página",
            "delete": "Eliminar",
            "clean_board": "Limpiar Tablero",
            "clean_prompt": "¿Estás seguro de que quieres limpiar el tablero? Todos los dibujos se borrarán.",
            "new_file": "Nuevo Archivo",
            "new_file_prompt": "¿Crear un nuevo archivo? Los cambios no guardados se perderán.",
            "close_without_saving": "Cerrar sin guardar",
            "discard_changes": "Descartar cambios",
            "yes": "Sí",
            "no": "No",
            "save_as_pdf": "Guardar como PDF",
            "pdf_files": "Archivos PDF (*.pdf)",
            "pdf_saved": "PDF guardado con éxito en:\n{file_path}",
            "save_all_png": "Guardar Todas las Páginas como PNG",
            "file_menu": "Archivo",
            "edit_menu": "Editar",
            "page_menu": "Página",
            "tools_menu": "Herramientas",
            "help_menu": "Ayuda",
            "new_action": "Nuevo",
            "open_action": "Abrir",
            "save_action": "Guardar",
            "exit_action": "Salir",
            "presentation_mode": "Modo Presentación",
            "fullscreen": "Pantalla Completa",
            "show_hide_menubar": "Mostrar/Ocultar Barra de Menú",
            "show_toolbar": "Mostrar Barra de Herramientas",
            "credits": "Créditos",
            "hide_cursor": "Ocultar el cursor",
            "credits_developed_by": '<html><head/><body><p><span style="font-size:14pt; font-weight:700; font-style:italic; text-decoration: underline;">DESARROLLADO POR: DAVI CORVELLO, PEDRO LUKAS Y PEDRO OLIVEIRA</span></p></body></html>',
            "credits_advisors": '<html><head/><body><p><span style="font-size:14pt; font-weight:700; font-style:italic; text-decoration: underline;">TUTORES: LEANDRO MARQUES SAMYN Y ARCANO MATHEUS BRAGANÇA LEITE</span></p></body></html>',
            "search_page": "Buscar la pagina",
            "no_com_registered_prompt": "No hay puerto COM registrado para bluetooth del control, ¿desea continuar?",
            "bt_connect_fail_prompt":   "No se pudo conectar con el bluetooth del control, ¿desea continuar?",
            "yes": "Sí",
            "no":  "No",
        }
    
    def translate(self, key, **kwargs):
        translation = self.translations[self.current_language].get(key, key)
        return translation.format(**kwargs)
    
    def set_language(self, lang):
        if lang in self.translations:
            self.current_language = lang

class SerialReaderThread(QThread):
    error_received = Signal()
    code_received  = Signal(str)
    
    def __init__(self, port, baud_rate=115200):
        super().__init__()
        self.port = port
        self.baud_rate = baud_rate
        self.ser = None

    def run(self):
        try:
            self.ser = serial.Serial(self.port, self.baud_rate, timeout=1)
            while True:
                if self.ser.in_waiting > 0:
                    line = self.ser.readline().decode('utf-8').strip()
                    if line:
                        self.code_received.emit(line)
        except serial.SerialException:
            # Emite sinal de erro pra abrir o diálogo
            self.error_received.emit()
        finally:
            if self.ser and self.ser.is_open:
                self.ser.close()

    def stop(self):
        if self.ser and self.ser.is_open:
            self.ser.close()

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)
        self.translator_manager = TranslatorManager(QApplication.instance())
        
        # Configurar traduções iniciais
        self.menuFile.setTitle(self.translator_manager.translate("file_menu"))
        self.menuEdit.setTitle(self.translator_manager.translate("edit_menu"))
        self.menuPage.setTitle(self.translator_manager.translate("page_menu"))
        self.menuTools.setTitle(self.translator_manager.translate("tools_menu"))
        self.menuHelp.setTitle(self.translator_manager.translate("help_menu"))
        
        self.actionNew.setText(self.translator_manager.translate("new_action"))
        self.actionOpen.setText(self.translator_manager.translate("open_action"))
        self.actionSave.setText(self.translator_manager.translate("save_action"))
        self.actionExit.setText(self.translator_manager.translate("exit_action"))
        self.actionSave_as_PDF.setText(self.translator_manager.translate("save_as_pdf"))
        self.actionSave_as_PNG.setText(self.translator_manager.translate("save_png"))
        self.actionSave_all_as_PNG.setText(self.translator_manager.translate("save_all_png"))
        self.actionPresentation_Mode.setText(self.translator_manager.translate("presentation_mode"))
        self.actionFullscreen.setText(self.translator_manager.translate("fullscreen"))
        self.actionShow_Hide_Menubar.setText(self.translator_manager.translate("show_hide_menubar"))
        self.actionShow_Toolbar.setText(self.translator_manager.translate("show_toolbar"))
        self.actionCredits_2.setText(self.translator_manager.translate("credits"))
        
        self.current_file = None
        self.setWindowTitle(self.translator_manager.translate("board_title"))
        icone = QIcon(r"BoardBuntu.jpg")
        self.setWindowIcon(icone)
        self.drawing = False
        self.lastPoint = QPoint()
        self.image = QImage(self.size(), QImage.Format_RGB32)
        self.image.fill(Qt.white)
        self.imageStack = [self.image.copy()]
        self.setTabletTracking(True)

        desktop = QGuiApplication.primaryScreen().virtualSize()
        self.pix = QPixmap(desktop.width(), desktop.height())
        self.pix.fill(Qt.white)
        
        self.HBrush = QColor(255, 255, 0, 150)
        self.lastHcolor = self.HBrush

        self.hasUnsavedChanges = False
        self.updateWindowTitle()
        
        self.pix = QPixmap(self.rect().size())
        self.pix.fill(Qt.white)

        self.begin, self.destination = QPoint(), QPoint()
        self.shapes = []
        self.redo_stack = []

        self.current_curve = []
        self.drawing_mode = 'curve'
        self.currentMode = self.drawing_mode

        self.actionHide_Cursor.setText(self.translator_manager.translate("hide_cursor"))

        self.resize_to_screen()
        self.cursor_visible = True
        self.lastPenColor = brushColor
        self.setCursorColor()
        self.menu_bar = self.menuBar()
        self.tool_bar = self.toolBar
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.tool_bar.addWidget(spacer)
        self.numberLabel = QLabel("1/1")
        self.tool_bar.addWidget(self.numberLabel)
        self.currentNumber = 1
        self.denominator = 1
        self.pages = {1: {'pixmap': self.pix.copy(), 'shapes': []}}
        self.menu_bar_visible = True
        self.tool_bar_visible = True 
        self.imageStack = [self.image.copy()]
        self.setTabletTracking(True)
        self.isFullScreenMode = False
        self.normalGeometry = None

        desktop = QGuiApplication.primaryScreen().virtualSize()
        self.pix = QPixmap(desktop.width(), desktop.height())
        self.pix.fill(Qt.white)

        rar_icon = QIcon(r"rar.png")
        self.actionSave_all_as_PNG.setIcon(rar_icon)
        self.actionSave_all_as_PNG.triggered.connect(self.export_all_pages_as_png)
        self.actionSave_as_PDF.triggered.connect(self.export_all_pages_as_pdf)
        pdf_icon =  QIcon(r"pdf.png")
        self.actionSave_as_PDF.setIcon(pdf_icon)
        self.actionHide_Cursor.triggered.connect(self.hide_cursor)
        cursor_icon = QIcon(r"cursor.png")
        self.actionHide_Cursor.setIcon(cursor_icon)
        self.actionSave_as_PNG.triggered.connect(self.exportPNG)
        self.actionBlack.triggered.connect(self.black)
        self.actionBlack.triggered.connect(self.Change)
        self.actionBlue.triggered.connect(self.blue)
        self.actionBlue.triggered.connect(self.Change)
        self.actionRed.triggered.connect(self.red)
        self.actionRed.triggered.connect(self.Change)  
        self.actionPurple_2.triggered.connect(self.Hpurple)
        self.actionCyan.triggered.connect(self.cyan)
        self.actionCyan.triggered.connect(self.Change)
        self.actionDelete.triggered.connect(self.delclean)
        self.undoShortcut = QShortcut(QKeySequence("Ctrl+Z"), self)
        self.redoShortcut = QShortcut(QKeySequence("Ctrl+Shift+Z"), self)
        self.undoShortcut.activated.connect(self.undo)
        self.redoShortcut.activated.connect(self.redo)
        self.actionErase.triggered.connect(self.erasemode)

        self.actionPen.triggered.connect(self.pen)
        self.actionPurple.triggered.connect(self.purple) 
        self.actionPurple.triggered.connect(self.Change)
        self.actionYellow.triggered.connect(self.yellow)
        self.actionYellow.triggered.connect(self.Change)
        self.actionPink.triggered.connect(self.pink)
        self.actionPink.triggered.connect(self.Change)
        self.actionOrange.triggered.connect(self.orange)
        self.actionOrange.triggered.connect(self.Change)
        self.actionShow_Hide_Menubar.triggered.connect(self.toggle_menubar)
        self.actionShow_Toolbar.triggered.connect(self.toggle_toolbar)
        self.actionNew_Page.triggered.connect(self.NewPage)
        self.actionNext_Page.triggered.connect(self.incrementNumber)
        self.actionPrevious_Page.triggered.connect(self.decrementNumber)
        self.actionDelete_Page.triggered.connect(self.RemovePage)

        self.actionHighlighter_2.triggered.connect(self.HigthLighter)
        self.actionRed_2.triggered.connect(self.Hred)
        self.actionRed_2.triggered.connect(self.HigthLighter)
        self.actionCian.triggered.connect(self.HigthLighter)
        self.actionYellow_2.triggered.connect(self.HigthLighter)
        self.actionYellow_2.triggered.connect(self.Hyellow)
        self.actionPurple_2.triggered.connect(self.HigthLighter)
    
        self.actionRectangle_2.triggered.connect(self.rectangle)
        self.actionRectangle_2.triggered.connect(self.setCursorColor)
        self.actionCian.triggered.connect(self.Hcyan)
        self.actionEllipse.triggered.connect(self.toggle_ellipse_mode)
        self.actionstraight_line.triggered.connect(self.toggle_line_mode)
        self.actionCredits_2.triggered.connect(self.credits)
        self.actionExit.triggered.connect(self.close)

        self.actionFirst_Page.triggered.connect(self.FirstPage)
        self.actionLast_Page.triggered.connect(self.Lastpage)
        self.actionDelete_Last_Page.triggered.connect(self.delete_last_page)
        self.actionPresentation_Mode.triggered.connect(self.PresentationMode)
        self.actionPresentation_Mode.triggered.connect(self.toggle_menubar)
        self.actionPresentation_Mode.triggered.connect(self.toggle_toolbar)
        self.actionFullscreen.triggered.connect(self.PresentationMode)
        self.actionSave.triggered.connect(self.save_image)
        self.actionOpen.triggered.connect(self.open_image)
        self.actionNew.triggered.connect(self.new_file)
        self.actionPortugue_s.triggered.connect(self.set_portuguese)
        self.actionEnglish.triggered.connect(self.set_default_language)
        self.actionEspa_ol.triggered.connect(self.set_spanish)
        
        self.initial_state_shapes = [] 
        self.initial_state_pixmap = None  

        try:
            # Tenta ler a porta serial a partir de um arquivo
            with open("porta_com.txt", "r", encoding="utf-8") as f:
                self.porta = f.read().strip()
        except FileNotFoundError:
            # Arquivo não encontrado: prompt traduzível para usuário
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Warning)
            msg.setWindowTitle(self.translator_manager.translate("error"))
            msg.setText(self.translator_manager.translate("no_com_registered_prompt"))
            # Botões Sim e Não com texto traduzido
            msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            msg.button(QMessageBox.Yes).setText(self.translator_manager.translate("yes"))
            msg.button(QMessageBox.No).setText(self.translator_manager.translate("no"))
            resposta = msg.exec()
            if resposta == QMessageBox.Yes:
                # Prossegue sem porta COM
                self.porta = None
            else:
                # Sai da aplicação
                sys.exit()
    
        self.serial_thread = SerialReaderThread(self.porta)

        self.serial_thread.error_received.connect(self.on_bt_connect_fail)
        self.serial_thread.code_received.connect(self.handle_ir_code)

        if self.porta:
            self.serial_thread.start()
        
        self.camera_click_queue = queue.Queue()
        self.camera_drawing = False
        self.start_camera_thread()
        self.start_camera_listener()
        
        self.translator = translator
        lupa_icon = QIcon(r"lupa.png")
        self.actionSearch_Page.setIcon(lupa_icon)
        self.actionSearch_Page.triggered.connect(self.search_page)
        self.actionSearch_Page.setText(self.translator_manager.translate("search_page"))
        
    def search_page(self):
        num, ok = QInputDialog.getInt(
            self,
            self.translator_manager.translate("page"),             # título: “Página”
            self.translator_manager.translate("page") + ":",       # label: “Página:”
            self.currentNumber,  # valor inicial
            1,                   # minValue
            self.denominator,    # maxValue
            1                    # step
        )
        if not ok:
            return  # usuário cancelou

        # (Opcional: checagem redundante, pois o spinbox não deixa sair do range)
        if num < 1 or num > self.denominator:
            QMessageBox.warning(
                self,
                self.translator_manager.translate("error"),
                f"{self.translator_manager.translate('page')} {num} não existe."
            )
            return

        # Salva estado da página atual
        self.pages[self.currentNumber] = {
            'pixmap': self.pix.copy(),
            'shapes': self.shapes.copy()
        }

        # Carrega a nova página
        self.currentNumber = num
        page_data = self.pages[num]
        self.pix = page_data['pixmap'].copy()
        self.shapes = page_data['shapes'].copy()
        self.redo_stack.clear()

        # Atualiza rótulo e redesenha
        self.numberLabel.setText(f"{self.currentNumber}/{self.denominator}")
        self.redraw_pixmap()
        
    def start_camera_thread(self):
        threading.Thread(
            target=start_camera,
            args=(self.camera_click_queue,),
            daemon=True
        ).start()

    def start_camera_listener(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.check_camera_clicks)
        self.timer.start(50)  

    def check_camera_clicks(self):
        while not self.camera_click_queue.empty():
            data = self.camera_click_queue.get()
            evt = data[0]

            if evt == 'start':
                x, y = data[1]
                self.camera_start_pt = QPoint(x, y)
                self.last_camera_pt   = QPoint(x, y)
                self.camera_drawing = True
                if self.drawing_mode == 'curve':
                    self.points = [self.camera_start_pt]

            elif evt == 'move' and self.camera_drawing:
                x, y = data[1]
                pt = QPoint(x, y)
                if self.drawing_mode == 'curve':
                    self.points.append(pt)
                    painter = QPainter(self.pix)
                    painter.setRenderHint(QPainter.Antialiasing, True)
                    pen = QPen(self.lastPenColor, brushSize, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
                    painter.setPen(pen)
                    for i in range(1, len(self.points)):
                        painter.drawLine(self.points[i - 1], self.points[i])
                    painter.end()
                    self.shapes.append(('curve', self.points.copy(), self.lastPenColor, brushSize))
                    self.redo_stack.clear()
                    self.pages[self.currentNumber] = {
                        'pixmap': self.pix.copy(),
                        'shapes': self.shapes.copy()
                    }
                    self.markAsUnsaved()
                    self.redraw_pixmap()
                    self.points = [pt]
                else:
                    self.last_camera_pt = pt

            elif evt == 'end' and self.camera_drawing:
                self.camera_drawing = False
                if self.camera_start_pt is None or self.last_camera_pt is None:
                    continue

                painter = QPainter(self.pix)
                painter.setRenderHint(QPainter.Antialiasing, True)
                painter.setRenderHint(QPainter.SmoothPixmapTransform, True)
                rect = QRect(self.camera_start_pt, self.last_camera_pt).normalized()

                if self.drawing_mode == 'rectangle':
                    pen = QPen(self.lastPenColor, brushSize)
                    painter.setPen(pen)
                    painter.drawRect(rect)
                    self.shapes.append(('rectangle', rect, self.lastPenColor, brushSize))

                elif self.drawing_mode == 'line':
                    pen = QPen(self.lastPenColor, brushSize)
                    painter.setPen(pen)
                    painter.drawLine(self.camera_start_pt, self.last_camera_pt)
                    self.shapes.append(('line', (self.camera_start_pt, self.last_camera_pt), self.lastPenColor, brushSize))

                elif self.drawing_mode == 'ellipse':
                    pen = QPen(self.lastPenColor, brushSize)
                    painter.setPen(pen)
                    painter.drawEllipse(rect)
                    self.shapes.append(('ellipse', rect, self.lastPenColor, brushSize))

                elif self.drawing_mode == 'highlight':
                    painter.setCompositionMode(QPainter.CompositionMode_SourceOver)
                    painter.setBrush(QBrush(self.HBrush))
                    painter.setPen(Qt.NoPen)
                    painter.drawRect(rect)
                    self.shapes.append(('highlight', rect, self.HBrush, brushSize))

                painter.end()
                self.redo_stack.clear()
                self.pages[self.currentNumber] = {
                    'pixmap': self.pix.copy(),
                    'shapes': self.shapes.copy()
                }
                self.markAsUnsaved()
                self.redraw_pixmap()
                self.update()
    
    def handle_camera_click(self, x, y):
        # converte coordenadas para QPoint
        current_point = QPoint(x, y)

        if not hasattr(self, 'camera_drawing_active'):
            self.camera_drawing_active = False
            self.last_camera_point = None

        if not self.camera_drawing_active:
            # início do movimento
            self.camera_drawing_active = True
            self.last_camera_point = current_point
            return

        if self.last_camera_point is not None:
            painter = QPainter(self.pix)
            pen = QPen(self.lastPenColor, brushSize)
            painter.setRenderHint(QPainter.Antialiasing)
            painter.setPen(pen)
            painter.drawLine(self.last_camera_point, current_point)
            painter.end()

            self.shapes.append(('curve', [self.last_camera_point, current_point], self.lastPenColor, brushSize))
            self.last_camera_point = current_point
            self.markAsUnsaved()
            self.update()

    def on_bt_connect_fail(self):
        QMessageBox.setButtonText(QMessageBox.Yes, self.translator_manager.translate("yes"))
        QMessageBox.setButtonText(QMessageBox.No,  self.translator_manager.translate("no"))

        resposta = QMessageBox.question(
            self,
            self.translator_manager.translate("error"),
            self.translator_manager.translate("bt_connect_fail_prompt"),
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if resposta == QMessageBox.No:
            sys.exit(0)
    
    def handle_ir_code(self, code):
        """Mapeia códigos IR para ações no BoardBuntu"""
        code = code.lower()  
        actions = {
            '0x45': self.close,                 
            '0x46': self.open_image,            
            '0x47': self.delclean,              
            '0x44': self.NewPage,               
            '0x40': self.decrementNumber,       
            '0x43': self.incrementNumber,       
            '0x7': self.export_all_pages_as_pdf, 
            '0x15': self.FirstPage,             
            '0x9': self.FirstPage,              
            '0x16': self.undo,                  
            '0xc': self.redo,                  
            '0x19': self.exportPNG,             
            '0xd': self.export_all_pages_as_png,
            '0x18': self.pen,                  
            '0x5e': self.erasemode,             
            '0x8': self.save_image,            
            '0x1c': self.PresentationMode,      
            '0x5a': self.toggle_toolbar,        
            '0x42': self.toggle_menubar,       
            '0x52': self.hide_cursor,   
            '0x4a': self.HigthLighter,         
        }
        if code in actions:
            actions[code]()
        else:
            print(f"Código IR não reconhecido: {code}")

    def new_file(self):
        if self.hasUnsavedChanges:
            msg_box = QMessageBox(
                QMessageBox.Question,
                self.translator_manager.translate("new_file"),
                self.translator_manager.translate("new_file_prompt"),
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
                self
            )
            
            msg_box.setButtonText(QMessageBox.Save, self.translator_manager.translate("save"))
            msg_box.setButtonText(QMessageBox.Discard, self.translator_manager.translate("discard_changes"))
            msg_box.setButtonText(QMessageBox.Cancel, self.translator_manager.translate("cancel"))
            
            reply = msg_box.exec()
            
            if reply == QMessageBox.Save:
                self.save_image()
                if not self.hasUnsavedChanges:
                    self.reset_file()
                else:
                    return
            elif reply == QMessageBox.Cancel:
                return
        self.reset_file()
        
    def reset_file(self):
        self.pix.fill(Qt.white)
        self.shapes = []
        self.redo_stack = []
        self.pages = {1: {'pixmap': self.pix.copy(), 'shapes': []}}
        self.currentNumber = 1
        self.denominator = 1
        self.numberLabel.setText("1/1")
        self.update()
        self.markAsSaved()
        self.save_initial_state()
        
    def Change(self):
        if self.drawing_mode == 'highlight':
            self.drawing_mode = 'curve'

    def credits(self):
        self.creditos = CreditsWindow(self.translator_manager)
        self.creditos.show()

    def toggle_line_mode(self):
        global brushColor, brushSize
        brushSize  = 3
        self.drawing_mode = 'line'
        self.setCursorColor()

    def toggle_ellipse_mode(self):
        global brushColor, brushSize
        brushSize  = 3
        self.drawing_mode = 'ellipse'
        self.setCursorColor()
    
    def hide_cursor(self):
        """Alterna a visibilidade do cursor do mouse"""
        self.cursor_should_be_visible = not getattr(self, 'cursor_should_be_visible', True)

        if self.cursor_should_be_visible:
            self.setCursor(self.current_tool_cursor)
        else:
            self.setCursor(Qt.BlankCursor)


    def erasemode(self):
        global brushColor, brushSize
        self.drawing_mode = 'curve'
        self.lastBrushSize = brushSize  
        brushColor = Qt.GlobalColor.white
        brushSize = 25
        self.lastPenColor = Qt.white
        self.setEraserCursor()

    def Hred(self):
        self.HBrush = QColor(255, 0, 0, 150)
        self.lastHcolor = QColor(255, 0, 0, 150)
        self.setHcursor()

    def rectangle(self):
        global brushColor, brushSize
        self.drawing_mode = 'rectangle'
        brushSize  = 3

    def HigthLighter(self):
        self.drawing_mode = 'highlight'
        self.setHcursor()

    def NewPage(self):
        self.pages[self.currentNumber] = {'pixmap': self.pix.copy(), 'shapes': self.shapes.copy()}
        self.denominator += 1
        new_page_number = self.denominator
        self.pages[new_page_number] = {'pixmap': QPixmap(self.rect().size()), 'shapes': []}
        self.pages[new_page_number]['pixmap'].fill(Qt.white)
        
        if self.currentNumber == self.denominator - 1:
            self.currentNumber = new_page_number
            self.pix = self.pages[self.currentNumber]['pixmap'].copy()
            self.shapes = self.pages[self.currentNumber]['shapes'].copy()
        
        self.redo_stack.clear()
        self.numberLabel.setText(f"{self.currentNumber}/{self.denominator}")
        self.update()

    def incrementNumber(self):
        if self.currentNumber < self.denominator:
            self.pages[self.currentNumber] = {'pixmap': self.pix.copy(), 'shapes': self.shapes.copy()}
            self.currentNumber += 1
            self.pix = self.pages[self.currentNumber]['pixmap'].copy()
            self.shapes = self.pages[self.currentNumber]['shapes'].copy()
            self.redo_stack.clear()
            self.numberLabel.setText(f"{self.currentNumber}/{self.denominator}")
            self.redraw_pixmap()
            
    def decrementNumber(self):
        if self.currentNumber > 1:
            self.pages[self.currentNumber] = {'pixmap': self.pix.copy(), 'shapes': self.shapes.copy()}
            self.currentNumber -= 1
            self.pix = self.pages[self.currentNumber]['pixmap'].copy()
            self.shapes = self.pages[self.currentNumber]['shapes'].copy()
            self.redo_stack.clear()
            self.numberLabel.setText(f"{self.currentNumber}/{self.denominator}")
            self.redraw_pixmap()

    def RemovePage(self):
        if self.denominator == 1:
            return
            
        reply = QMessageBox.question(
            self,
            self.translator_manager.translate("delete"),
            self.translator_manager.translate("delete_page_confirm"),
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.No:
            return
            
        if self.currentNumber in self.pages and self.denominator > 1:
            self.pages[self.currentNumber] = {'pixmap': self.pix.copy(), 'shapes': self.shapes.copy()}
            self.pages.pop(self.currentNumber)
            remaining_pages = sorted(self.pages.keys())
            
            new_pages = {}
            for i, page_num in enumerate(remaining_pages):
                new_pages[i + 1] = self.pages[page_num]
            
            self.pages = new_pages
            self.denominator = len(self.pages)

            if self.currentNumber > self.denominator:
                self.currentNumber = self.denominator
            
            self.pix = self.pages[self.currentNumber]['pixmap'].copy()
            self.shapes = self.pages[self.currentNumber]['shapes'].copy()
            
            self.redo_stack.clear()
            self.numberLabel.setText(f"{self.currentNumber}/{self.denominator}")
            self.redraw_pixmap()

    def delete_last_page(self):
        if self.denominator > 1:
            self.pages.pop(self.denominator)
            self.denominator -= 1
            self.currentNumber = min(self.currentNumber, self.denominator)
            self.pix = self.pages[self.currentNumber]['pixmap'].copy()
            self.shapes = self.pages[self.currentNumber]['shapes'].copy()
            self.redo_stack.clear()
            self.numberLabel.setText(f"{self.currentNumber}/{self.denominator}")
            self.redraw_pixmap()
    
    def Lastpage(self):
        self.pages[self.currentNumber] = {'pixmap': self.pix.copy(), 'shapes': self.shapes.copy()}
        self.currentNumber = self.denominator
        self.pix = self.pages[self.currentNumber]['pixmap'].copy()
        self.shapes = self.pages[self.currentNumber]['shapes'].copy()
        self.redo_stack.clear()
        self.numberLabel.setText(f"{self.currentNumber}/{self.denominator}")
        self.redraw_pixmap()

    def FirstPage(self):
        self.pages[self.currentNumber] = {'pixmap': self.pix.copy(), 'shapes': self.shapes.copy()}
        self.currentNumber = 1
        self.pix = self.pages[self.currentNumber]['pixmap'].copy()
        self.shapes = self.pages[self.currentNumber]['shapes'].copy()
        self.redo_stack.clear()
        self.numberLabel.setText(f"{self.currentNumber}/{self.denominator}")
        self.redraw_pixmap()

    def mousePressEvent(self, event):
        if event.buttons() & Qt.LeftButton:
            self.markAsUnsaved()
            self.begin = event.pos()
            self.destination = self.begin
            if self.drawing_mode == 'curve':
                self.current_curve = [self.begin]
                painter = QPainter(self.pix)
                pen = QPen(brushColor, 1)  
                painter.setPen(pen)
                painter.drawPoint(self.begin)  
        self.update()

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton:
            self.destination = event.pos()
            if self.drawing_mode == 'curve' : 
                self.current_curve.append(self.destination)
            self.update()

    def mouseReleaseEvent(self, event):
        global brushColor
        global brushSize
        if event.button() & Qt.LeftButton:
            self.markAsUnsaved()
            painter = QPainter(self.pix)
            if self.drawing_mode == 'rectangle':
                pen = QPen(brushColor, brushSize)
                painter.setPen(pen)
                rect = QRect(self.begin, self.destination)
                painter.drawRect(rect.normalized())
                self.shapes.append(('rectangle', rect, brushColor, brushSize))
            elif self.drawing_mode == 'curve':
                pen = QPen(brushColor, brushSize)
                painter.setRenderHint(QPainter.Antialiasing, True)
                painter.setRenderHint(QPainter.SmoothPixmapTransform, True)
                painter.setRenderHint(QPainter.LosslessImageRendering, True)
                painter.setPen(pen)
                if self.current_curve:
                    for i in range(len(self.current_curve) - 1):
                        painter.drawLine(self.current_curve[i], self.current_curve[i + 1])
                self.shapes.append(('curve', self.current_curve, brushColor, brushSize))
                self.current_curve = []
            elif self.drawing_mode == 'highlight':
                painter.setCompositionMode(QPainter.CompositionMode_SourceOver)
                pen = QPen(Qt.NoPen)
                brush = QBrush(self.HBrush)
                painter.setPen(pen)
                painter.setBrush(brush)
                rect = QRect(self.begin, self.destination)
                painter.drawRect(rect.normalized())
                self.shapes.append(('highlight', rect, self.HBrush))
            elif self.drawing_mode == 'ellipse':
                painter.setRenderHint(QPainter.Antialiasing, True)
                painter.setRenderHint(QPainter.SmoothPixmapTransform, True)
                painter.setRenderHint(QPainter.LosslessImageRendering, True)
                pen = QPen(brushColor, brushSize)
                painter.setPen(pen)
                rect = QRect(self.begin, self.destination)
                painter.drawEllipse(rect.normalized())
                self.shapes.append(('ellipse', rect, brushColor))
            elif self.drawing_mode == 'line':
                painter.setRenderHint(QPainter.Antialiasing, True)
                painter.setRenderHint(QPainter.SmoothPixmapTransform, True)
                painter.setRenderHint(QPainter.LosslessImageRendering, True)
                pen = QPen(brushColor, brushSize)
                painter.setPen(pen)
                painter.drawLine(self.begin, self.destination)
                self.shapes.append(('line', (self.begin, self.destination), brushColor))
            
            painter.end()
            self.redo_stack.clear()
            self.begin, self.destination = QPoint(), QPoint()
            self.update()

    def paintEvent(self, event):
        global brushColor, brushSize
        
        # Criar painter principal
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setRenderHint(QPainter.SmoothPixmapTransform, True)
        painter.setRenderHint(QPainter.LosslessImageRendering, True)
        
        # Desenhar conteúdo principal centralizado
        scaled_pix = self.pix.scaled(self.rect().size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        x = (self.width() - scaled_pix.width()) // 2
        y = (self.height() - scaled_pix.height()) // 2
        painter.drawPixmap(x, y, scaled_pix)
        
        # Desenho com mouse
        if not self.begin.isNull() and not self.destination.isNull():
            if self.drawing_mode == 'rectangle':
                pen = QPen(self.lastPenColor, brushSize)
                painter.setPen(pen)
                rect = QRect(self.begin, self.destination).normalized()
                painter.drawRect(rect)
                
            elif self.drawing_mode == 'curve' and self.current_curve:
                pen = QPen(brushColor, brushSize)
                painter.setPen(pen)
                for i in range(len(self.current_curve) - 1):
                    painter.drawLine(self.current_curve[i], self.current_curve[i + 1])
                    
            elif self.drawing_mode == 'highlight':
                painter.setCompositionMode(QPainter.CompositionMode_SourceOver)
                painter.setBrush(QBrush(self.HBrush))
                painter.setPen(Qt.NoPen)
                rect = QRect(self.begin, self.destination).normalized()
                painter.drawRect(rect)
                
            elif self.drawing_mode == 'ellipse':
                pen = QPen(brushColor, brushSize)
                painter.setPen(pen)
                rect = QRect(self.begin, self.destination).normalized()
                painter.drawEllipse(rect)
                
            elif self.drawing_mode == 'line':
                pen = QPen(brushColor, brushSize)
                painter.setPen(pen)
                painter.drawLine(self.begin, self.destination)
        
        # Preview para câmera (usando o MESMO painter)
        if self.camera_drawing and self.drawing_mode != 'curve':
            rect = QRect(self.camera_start_pt, self.last_camera_pt).normalized()
            
            if self.drawing_mode == 'rectangle':
                pen = QPen(self.lastPenColor, brushSize, Qt.DashLine)
                painter.setPen(pen)
                painter.drawRect(rect)
                
            elif self.drawing_mode == 'line':
                pen = QPen(self.lastPenColor, brushSize, Qt.DashLine)
                painter.setPen(pen)
                painter.drawLine(self.camera_start_pt, self.last_camera_pt)
                
            elif self.drawing_mode == 'ellipse':
                pen = QPen(self.lastPenColor, brushSize, Qt.DashLine)
                painter.setPen(pen)
                painter.drawEllipse(rect)
                
            elif self.drawing_mode == 'highlight':
                painter.setCompositionMode(QPainter.CompositionMode_SourceOver)
                painter.setBrush(QBrush(self.HBrush))
                painter.setPen(Qt.NoPen)
                painter.drawRect(rect)
        
        painter.end()  
    
    def Hyellow(self):
        self.HBrush = QColor((255, 255, 0, 150))
        self.lastHcolor = QColor((255, 255, 0, 150))
        
    def markAsUnsaved(self):
        self.hasUnsavedChanges = True
        self.updateWindowTitle()
        
    def markAsSaved(self):
        self.hasUnsavedChanges = False
        self.updateWindowTitle()
        
    def updateWindowTitle(self):
        base_title = self.translator_manager.translate("board_title")
        if self.current_file:
            base_title = f"{self.current_file} - {base_title}"
        if self.hasUnsavedChanges:
            self.setWindowTitle(f"{base_title} *")
        else:
            self.setWindowTitle(base_title)

    def save_image(self):
        if self.current_file:
            initial_path = self.current_file
        else:
            initial_path = ""

        file_path, _ = QFileDialog.getSaveFileName(
            self, 
            self.translator_manager.translate("save_document"),
            initial_path, 
            self.translator_manager.translate("paint_files")
        )
        
        if file_path:
            if not file_path.lower().endswith('.pnt'):
                file_path += '.pnt'
            
            document_data = {
                'current_page': self.currentNumber,
                'total_pages': self.denominator,
                'pages': {}
            }
            self.pages[self.currentNumber] = {'pixmap': self.pix.copy(), 'shapes': self.shapes.copy()}

            for page_num, page_data in self.pages.items():
                byte_array = QByteArray()
                buffer = QBuffer(byte_array)
                buffer.open(QBuffer.OpenModeFlag.WriteOnly)
                page_data['pixmap'].save(buffer, "PNG")
                document_data['pages'][page_num] = {'image_data': byte_array.data(), 'shapes': page_data['shapes']}
            
            with open(file_path, 'wb') as f:
                pickle.dump(document_data, f)

            self.current_file = os.path.basename(file_path)
            self.markAsSaved()

    def open_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            self.translator_manager.translate("open_document"),
            "", 
            self.translator_manager.translate("paint_files")
        )
        
        if file_path:
            try:
                with open(file_path, 'rb') as f:
                    document_data = pickle.load(f)

                self.pages.clear()
                self.shapes.clear()
                self.redo_stack.clear()
                self.currentNumber = document_data['current_page']
                self.denominator = document_data['total_pages']

                for page_num, page_data in document_data['pages'].items():
                    image = QImage()
                    image.loadFromData(page_data['image_data'], "PNG")
                    pixmap = QPixmap.fromImage(image)
                    self.pages[page_num] = {'pixmap': pixmap, 'shapes': page_data['shapes']}
                
                self.pix = self.pages[self.currentNumber]['pixmap'].copy()
                self.shapes = self.pages[self.currentNumber]['shapes'].copy()
                self.numberLabel.setText(f"{self.currentNumber}/{self.denominator}")

                self.current_file = os.path.basename(file_path)
                self.updateWindowTitle()
                self.update()
                self.markAsSaved()
                self.save_initial_state()
                self.resizeEvent(None)
            except Exception as e:
                QMessageBox.critical(
                    self, 
                    self.translator_manager.translate("error"),
                    self.translator_manager.translate("open_error", error=str(e))
                )
        self.resizeEvent(None)            

    def closeEvent(self, event):
        if self.hasUnsavedChanges:
            msg_box = QMessageBox(
                QMessageBox.Question,
                self.translator_manager.translate("unsaved_changes"),
                self.translator_manager.translate("save_prompt"),
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
                self
            )
            
            msg_box.setButtonText(QMessageBox.Save, self.translator_manager.translate("save"))
            msg_box.setButtonText(QMessageBox.Discard, self.translator_manager.translate("close_without_saving"))
            msg_box.setButtonText(QMessageBox.Cancel, self.translator_manager.translate("cancel"))
            
            reply = msg_box.exec()
            
            if reply == QMessageBox.Save:
                self.save_image()
                if not self.hasUnsavedChanges:  # Unified cleanup
                    event.accept()
                else:
                    event.ignore()
            elif reply == QMessageBox.Cancel:
                event.ignore()
            else:
                event.accept()
        else:
            event.accept() 
    def black(self):
        global brushColor, brushSize
        brushColor = Qt.GlobalColor.black
        brushSize  = 3
        self.lastPenColor=(Qt.GlobalColor.black)
        self.setCursorColor()

    def red(self):
        global brushColor, brushSize
        brushColor = Qt.GlobalColor.red
        brushSize  = 3
        self.lastPenColor=(Qt.GlobalColor.red)
        self.setCursorColor()

    def blue(self):
        global brushColor, brushSize
        brushColor = Qt.GlobalColor.blue
        self.lastPenColor=(Qt.GlobalColor.blue)
        brushSize  = 3
        self.setCursorColor()

    def yellow(self):
        global brushColor, brushSize
        brushColor = QColor(255, 255, 0)
        self.lastPenColor= QColor(255, 255, 0)
        brushSize  = 3
        self.setCursorColor()
    
    def purple(self):
        global brushColor, brushSize
        brushColor = QColor(128, 0, 128)  
        self.lastPenColor=(QColor(128, 0, 128)) 
        brushSize  = 3
        self.setCursorColor()

    def orange(self):
        global brushColor, brushSize
        brushColor = QColor(255, 165, 0)  
        self.lastPenColor=(QColor(255, 165, 0))  
        brushSize  = 3
        self.setCursorColor()

    def pink(self):
        global brushColor, brushSize
        brushColor = QColor(255, 192, 203)  
        self.lastPenColor = (QColor(255, 192, 203))
        brushSize  = 3 
        self.setCursorColor()

    def cyan(self):
        global brushColor, brushSize
        brushColor = Qt.GlobalColor.cyan
        self.lastPenColor = (Qt.GlobalColor.cyan)
        brushSize  = 3
        self.setCursorColor()

    def delclean(self):
        self.shapes.append(('paint', Qt.white))
        self.redraw_pixmap()
        self.markAsUnsaved()
        
    def undo(self):
        if self.shapes:
            shape = self.shapes.pop()
            self.redo_stack.append(shape)
            self.redraw_pixmap()
            self.pages[self.currentNumber] = {
                'pixmap': self.pix.copy(),
                'shapes': self.shapes.copy()
            }
            if self.is_at_initial_state():
                self.markAsSaved()
            else:
                self.markAsUnsaved()
                
    def redo(self):
        if self.redo_stack:
            shape = self.redo_stack.pop()
            self.shapes.append(shape)
            self.redraw_pixmap()
            self.pages[self.currentNumber] = {
                'pixmap': self.pix.copy(),
                'shapes': self.shapes.copy()
            }
            self.markAsUnsaved()

    def Hpurple(self):
        self.HBrush = QColor(128, 0, 128, 150)
        self.lastHcolor = QColor(128, 0, 128, 150)
        self.setHcursor()
    
    def Hcyan(self):
        self.HBrush =  QColor(0, 255, 255, 150)
        self.lastHcolor =  QColor(0, 255, 255, 150)
        self.setHcursor()

    def redraw_pixmap(self):
        self.pix.fill(Qt.white)  # Fundo branco padrão
        painter = QPainter(self.pix)
        for shape in self.shapes:
            if shape[0] == 'paint':
                color = shape[1]
                painter.fillRect(self.pix.rect(), color)  # Pintar todo o fundo
            elif shape[0] == 'rectangle':
                pen = QPen(shape[2], shape[3])
                painter.setPen(pen)
                painter.setBrush(Qt.NoBrush)
                painter.drawRect(shape[1].normalized())
            elif shape[0] == 'curve':
                pen = QPen(shape[2], shape[3])
                painter.setRenderHint(QPainter.Antialiasing)
                painter.setRenderHint(QPainter.LosslessImageRendering, True)
                painter.setRenderHint(QPainter.SmoothPixmapTransform, True)
                painter.setPen(pen)
                for i in range(len(shape[1]) - 1):
                    painter.drawLine(shape[1][i], shape[1][i + 1])
            elif shape[0] == 'highlight':
                painter.setCompositionMode(QPainter.CompositionMode_SourceOver)
                pen = QPen(Qt.NoPen)
                brush = QBrush(shape[2], Qt.SolidPattern)
                painter.setPen(pen)
                painter.setBrush(brush)
                painter.drawRect(shape[1].normalized())
            elif shape[0] == 'ellipse':
                painter.setRenderHint(QPainter.Antialiasing, True)
                painter.setRenderHint(QPainter.SmoothPixmapTransform, True)
                painter.setRenderHint(QPainter.LosslessImageRendering, True)
                rect = shape[1]
                color = shape[2]
                pen = QPen(color, 3)
                painter.setPen(pen)
                painter.setBrush(Qt.NoBrush)
                painter.drawEllipse(rect.normalized())
            elif shape[0] == 'line':
                painter.setRenderHint(QPainter.Antialiasing, True)
                painter.setRenderHint(QPainter.SmoothPixmapTransform, True)
                painter.setRenderHint(QPainter.LosslessImageRendering, True)
                points = shape[1]
                color = shape[2]
                pen = QPen(color, 3)
                painter.setPen(pen)
                painter.drawLine(points[0], points[1])
        painter.end()
        self.update()

    def renderDrawingData(self):
        self.clearImage()
        painter = QPainter(self.image)
        painter.setRenderHint(QPainter.Antialiasing)
    
        for shape in self.shapes:
            if shape[0] == 'curve':
                pen = QPen(shape[2], shape[3], Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
                painter.setPen(pen)
                points = shape[1]
                for i in range(len(points) - 1):
                    painter.drawLine(points[i], points[i + 1])
            elif shape[0] == 'rectangle':
                brush = QBrush(QColor(255, 255, 0, 128))
                painter.fillRect(shape[1], brush)
    
        self.update()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        current_shapes = self.shapes.copy()
        current_redo = self.redo_stack.copy()
        
        if hasattr(self, 'loaded_image'):
            new_pix = QPixmap(self.size())
            new_pix.fill(Qt.white)
            
            scaled_pixmap = QPixmap.fromImage(self.loaded_image).scaled(
                self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            
            painter = QPainter(new_pix)
            x = (new_pix.width() - scaled_pixmap.width()) // 2
            y = (new_pix.height() - scaled_pixmap.height()) // 2
            painter.drawPixmap(x, y, scaled_pixmap)
            painter.end()
            
            self.pix = new_pix
        else:
            new_pix = QPixmap(self.size())
            new_pix.fill(Qt.white)
            painter = QPainter(new_pix)
            painter.drawPixmap(0, 0, self.pix.scaled(self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
            painter.end()
            self.pix = new_pix
        
        self.shapes = current_shapes
        self.redo_stack = current_redo
        self.redraw_pixmap()
    
    def resize_to_screen(self):
        screen_rect = QGuiApplication.primaryScreen().availableGeometry()
        self.setGeometry(screen_rect)
        
    def pen(self):
        global brushColor, brushSize
        brushColor = self.lastPenColor
        brushSize  = 3
        self.drawing_mode = 'curve'
        self.setCursorColor()

    def setCursorColor(self):
        cursor_size = 10  
        cursor_pixmap = QPixmap(cursor_size, cursor_size)
        cursor_pixmap.fill(Qt.transparent)

        painter = QPainter(cursor_pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(0, 0, cursor_size, cursor_size)
        painter.setCompositionMode(QPainter.CompositionMode_Source)
        painter.setBrush(self.lastPenColor)
        painter.drawEllipse(2, 2, cursor_size - 4, cursor_size - 4)
        painter.end()

        mask = QBitmap(cursor_pixmap.size())
        painter.setBrush(self.lastPenColor)
        painter.begin(mask)
        painter.setBrush(self.lastPenColor)
        painter.drawEllipse(0, 0, cursor_size, cursor_size)
        painter.end()

        cursor = QCursor(cursor_pixmap, cursor_size // 2, cursor_size // 2)
        self.setCursor(cursor)
        self.current_tool_cursor = cursor  
        if self.cursor_visible:  
            self.setCursor(cursor)
        if not getattr(self, 'cursor_should_be_visible', True):
            self.setCursor(Qt.BlankCursor)

    def setHcursor(self):
        cursor_size = 9 
        cursor_pixmap = QPixmap(cursor_size, cursor_size)
        cursor_pixmap.fill(Qt.transparent)

        painter = QPainter(cursor_pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(Qt.NoPen)
        painter.setBrush(self.lastHcolor)
        painter.drawRect(0, 0, cursor_size, cursor_size)  
        painter.end()

        mask = QBitmap(cursor_pixmap.size())
        mask.fill(Qt.color0)
        painter.begin(mask)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(Qt.color1)
        painter.drawRect(0, 0, cursor_size, cursor_size) 
        painter.end()

        cursor = QCursor(cursor_pixmap)
        self.setCursor(cursor)
        self.current_tool_cursor = cursor  
        if self.cursor_visible:  
            self.setCursor(cursor)
        if not getattr(self, 'cursor_should_be_visible', True):
            self.setCursor(Qt.BlankCursor)
            
    def setEraserCursor(self):
        cursor_size = 25  
        cursor_pixmap = QPixmap(cursor_size, cursor_size)
        cursor_pixmap.fill(Qt.transparent)

        painter = QPainter(cursor_pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(Qt.NoPen)
        painter.setBrush(Qt.black)
        painter.drawEllipse(0, 0, cursor_size, cursor_size)
        painter.end()

        mask = QBitmap(cursor_pixmap.size())
        mask.fill(Qt.color0)
        painter.begin(mask)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(Qt.color1)
        painter.drawEllipse(0, 0, cursor_size, cursor_size)
        painter.end()

        cursor = QCursor(cursor_pixmap, cursor_size // 2, cursor_size // 2)
        self.setCursor(cursor)
        self.current_tool_cursor = cursor  
        if self.cursor_visible:  
            self.setCursor(cursor)
        if not getattr(self, 'cursor_should_be_visible', True):
            self.setCursor(Qt.BlankCursor)        

    def toggle_menubar(self):
        self.menu_bar_visible = not self.menu_bar_visible
        self.menu_bar.setVisible(self.menu_bar_visible)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_F7:
            self.toggle_menubar()
        elif event.key() == Qt.Key_F9:
            self.toggle_toolbar()
        elif event.key() == Qt.Key_F10:
            self.toggle_toolbar()
            self.toggle_menubar()
            self.PresentationMode()
        elif event.key() == Qt.Key_F11:
            self.PresentationMode()
        elif event.key() == Qt.Key_F12: 
            self.hide_cursor()
        else:
            super().keyPressEvent(event)

    def toggle_toolbar(self):
        self.tool_bar_visible = not self.tool_bar_visible
        self.tool_bar.setVisible(self.tool_bar_visible)

    def PresentationMode(self):
        current_shapes = self.shapes.copy()
        current_redo = self.redo_stack.copy()
        
        if not self.isFullScreen():
            self.normalGeometry = self.geometry()
            self.isFullScreenMode = True
            
            tempPix = self.pix.copy()
            screen = QGuiApplication.primaryScreen().size()
            self.showFullScreen()
            
            newPix = QPixmap(screen)
            newPix.fill(Qt.white)
            
            painter = QPainter(newPix)
            painter.drawPixmap(0, 0, tempPix.scaled(screen, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            painter.end()
            
            self.pix = newPix
        else:
            self.isFullScreenMode = False
            self.showNormal()
            self.showMaximized()
            
            newPix = QPixmap(self.normalGeometry.size())
            newPix.fill(Qt.white)
            
            painter = QPainter(newPix)
            painter.drawPixmap(0, 0, self.pix.scaled(self.normalGeometry.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
            painter.end()
            
            self.pix = newPix
        
        self.shapes = current_shapes
        self.redo_stack = current_redo
        self.redraw_pixmap()
            
    def setCursorPos(self, x, y):
        QCursor.setPos(self.mapToGlobal(QPoint(x, y)))
        
    def exportPNG(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, 
            self.translator_manager.translate("save_png"),
            "", 
            self.translator_manager.translate("png_files")
        )

        if file_path:
            if not file_path.lower().endswith('.png'):
                file_path += '.png'

            canvas_size = self.pix.size()
            image = QImage(canvas_size, QImage.Format_ARGB32)
            image.fill(Qt.white)
            
            painter = QPainter(image)
            painter.drawPixmap(0, 0, self.pix)
            painter.end()
            
            if image.save(file_path, "PNG"):
                QMessageBox.information(
                    self, 
                    self.translator_manager.translate("success"),
                    self.translator_manager.translate("png_saved")
                )
            else:
                QMessageBox.critical(
                    self, 
                    self.translator_manager.translate("error"),
                    self.translator_manager.translate("png_error")
                )
                
    def export_all_pages_as_png(self):
        rar_name, _ = QFileDialog.getSaveFileName(
            self,
            self.translator_manager.translate("save_all_rar"),
            "",
            self.translator_manager.translate("rar_files")
        )
        
        if not rar_name:
            return
        
        if not rar_name.lower().endswith('.rar'):
            rar_name += '.rar'

        with tempfile.TemporaryDirectory() as temp_dir:
            image_paths = []

            for page_number, page_data in self.pages.items():
                image = QImage(page_data['pixmap'].size(), QImage.Format_ARGB32)
                image.fill(Qt.white)
                painter = QPainter(image)
                painter.drawPixmap(0, 0, page_data['pixmap'])
                painter.end()

                file_path = os.path.join(temp_dir, f"page_{page_number}.png")
                image.save(file_path, "PNG")
                image_paths.append(file_path)

            with ZipFile(rar_name, 'w') as rar:
                for path in image_paths:
                    rar.write(path, os.path.basename(path))

        QMessageBox.information(
            self,
            self.translator_manager.translate("success"),
            self.translator_manager.translate("all_saved", rar_name=rar_name)
        )

    def set_portuguese(self):
        self.translator_manager.set_language("pt")
        
        if hasattr(self, '_translator'):
            QApplication.instance().removeTranslator(self._translator)
        
        translator = QTranslator()
        if translator.load("portuguese_ts.qm", os.path.dirname(os.path.abspath(__file__))):
            QApplication.instance().installTranslator(translator)
            self._translator = translator
            self.retranslateUi(self)  
        
        # Atualizar textos da interface
        self.menuFile.setTitle(self.translator_manager.translate("file_menu"))
        self.menuEdit.setTitle(self.translator_manager.translate("edit_menu"))
        self.menuPage.setTitle(self.translator_manager.translate("page_menu"))
        self.menuTools.setTitle(self.translator_manager.translate("tools_menu"))
        self.menuHelp.setTitle(self.translator_manager.translate("help_menu"))
        self.actionHide_Cursor.setText(self.translator_manager.translate("hide_cursor"))
        self.actionNew.setText(self.translator_manager.translate("new_action"))
        self.actionOpen.setText(self.translator_manager.translate("open_action"))
        self.actionSave.setText(self.translator_manager.translate("save_action"))
        self.actionExit.setText(self.translator_manager.translate("exit_action"))
        self.actionSave_as_PDF.setText(self.translator_manager.translate("save_as_pdf"))
        self.actionSave_as_PNG.setText(self.translator_manager.translate("save_png"))
        self.actionSave_all_as_PNG.setText(self.translator_manager.translate("save_all_png"))
        self.actionPresentation_Mode.setText(self.translator_manager.translate("presentation_mode"))
        self.actionFullscreen.setText(self.translator_manager.translate("fullscreen"))
        self.actionShow_Hide_Menubar.setText(self.translator_manager.translate("show_hide_menubar"))
        self.actionShow_Toolbar.setText(self.translator_manager.translate("show_toolbar"))
        self.actionCredits_2.setText(self.translator_manager.translate("credits"))
        self.actionSearch_Page.setText(self.translator_manager.translate("search_page"))
        
        self.updateWindowTitle()
        
        QMessageBox.information(
            self, 
            self.translator_manager.translate("language"),
            self.translator_manager.translate("portuguese_set")
        )
        with open(LANGUAGE_FILE, "w", encoding="utf-8") as f:
            f.write("pt")
    def set_spanish(self):
        self.translator_manager.set_language("es")
        
        if hasattr(self, '_translator'):
            QApplication.instance().removeTranslator(self._translator)
        

        translator = QTranslator()
        if translator.load("traducao_es.qm", os.path.dirname(os.path.abspath(__file__))):
            QApplication.instance().installTranslator(translator)
            self._translator = translator
            self.retranslateUi(self)  
        
        # Atualizar textos da interface
        self.menuFile.setTitle(self.translator_manager.translate("file_menu"))
        self.menuEdit.setTitle(self.translator_manager.translate("edit_menu"))
        self.menuPage.setTitle(self.translator_manager.translate("page_menu"))
        self.menuTools.setTitle(self.translator_manager.translate("tools_menu"))
        self.menuHelp.setTitle(self.translator_manager.translate("help_menu"))
        self.actionHide_Cursor.setText(self.translator_manager.translate("hide_cursor"))
        self.actionNew.setText(self.translator_manager.translate("new_action"))
        self.actionOpen.setText(self.translator_manager.translate("open_action"))
        self.actionSave.setText(self.translator_manager.translate("save_action"))
        self.actionExit.setText(self.translator_manager.translate("exit_action"))
        self.actionSave_as_PDF.setText(self.translator_manager.translate("save_as_pdf"))
        self.actionSave_as_PNG.setText(self.translator_manager.translate("save_png"))
        self.actionSave_all_as_PNG.setText(self.translator_manager.translate("save_all_png"))
        self.actionPresentation_Mode.setText(self.translator_manager.translate("presentation_mode"))
        self.actionFullscreen.setText(self.translator_manager.translate("fullscreen"))
        self.actionShow_Hide_Menubar.setText(self.translator_manager.translate("show_hide_menubar"))
        self.actionShow_Toolbar.setText(self.translator_manager.translate("show_toolbar"))
        self.actionCredits_2.setText(self.translator_manager.translate("credits"))
        self.actionSearch_Page.setText(self.translator_manager.translate("search_page"))
        
        self.updateWindowTitle()
        
        QMessageBox.information(
            self, 
            self.translator_manager.translate("language"),
            self.translator_manager.translate("spanish_set")
        )
        with open(LANGUAGE_FILE, "w", encoding="utf-8") as f:
            f.write("es")

    def set_default_language(self):
        self.translator_manager.set_language("en")
        
        if hasattr(self, '_translator'):
            QApplication.instance().removeTranslator(self._translator)
            self._translator = None
        
        self.retranslateUi(self)  
        
        self.menuFile.setTitle(self.translator_manager.translate("file_menu"))
        self.menuEdit.setTitle(self.translator_manager.translate("edit_menu"))
        self.menuPage.setTitle(self.translator_manager.translate("page_menu"))
        self.menuTools.setTitle(self.translator_manager.translate("tools_menu"))
        self.menuHelp.setTitle(self.translator_manager.translate("help_menu"))
        self.actionHide_Cursor.setText(self.translator_manager.translate("hide_cursor"))
        self.actionNew.setText(self.translator_manager.translate("new_action"))
        self.actionOpen.setText(self.translator_manager.translate("open_action"))
        self.actionSave.setText(self.translator_manager.translate("save_action"))
        self.actionExit.setText(self.translator_manager.translate("exit_action"))
        self.actionSave_as_PDF.setText(self.translator_manager.translate("save_as_pdf"))
        self.actionSave_as_PNG.setText(self.translator_manager.translate("save_png"))
        self.actionSave_all_as_PNG.setText(self.translator_manager.translate("save_all_png"))
        self.actionPresentation_Mode.setText(self.translator_manager.translate("presentation_mode"))
        self.actionFullscreen.setText(self.translator_manager.translate("fullscreen"))
        self.actionShow_Hide_Menubar.setText(self.translator_manager.translate("show_hide_menubar"))
        self.actionShow_Toolbar.setText(self.translator_manager.translate("show_toolbar"))
        self.actionCredits_2.setText(self.translator_manager.translate("credits"))
        self.actionSearch_Page.setText(self.translator_manager.translate("search_page"))
        
        self.updateWindowTitle()
        
        QMessageBox.information(
            self, 
            self.translator_manager.translate("language"),
            self.translator_manager.translate("english_set")
        )
        with open(LANGUAGE_FILE, "w", encoding="utf-8") as f:
            f.write("en")

    def save_initial_state(self):
        self.initial_state_shapes = self.shapes.copy()
        self.initial_state_pixmap = self.pix.copy()

    def is_at_initial_state(self):
        if len(self.shapes) != len(self.initial_state_shapes):
            return False
        
        for i, shape in enumerate(self.shapes):
            if i >= len(self.initial_state_shapes) or shape != self.initial_state_shapes[i]:
                return False
        
        return True
    
    def export_all_pages_as_pdf(self):

        self.pages[self.currentNumber] = {'pixmap': self.pix.copy(), 'shapes': self.shapes.copy()}

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            self.translator_manager.translate("save_as_pdf"),
            "",
            self.translator_manager.translate("pdf_files")
        )

        if not file_path:
            return

        if not file_path.lower().endswith('.pdf'):
            file_path += '.pdf'

        pdf_writer = QPdfWriter(file_path)
        pdf_writer.setPageSize(QPageSize(QPageSize.A4))
        pdf_writer.setResolution(300)
        
        painter = QPainter(pdf_writer)
        
        sorted_pages = sorted(self.pages.items())
        total_pages = len(sorted_pages)
        
        for i, (page_num, page_data) in enumerate(sorted_pages):
            image = QImage(page_data['pixmap'].size(), QImage.Format_ARGB32)
            image.fill(Qt.white)
            
            temp_painter = QPainter(image)
            temp_painter.drawPixmap(0, 0, page_data['pixmap'])
            temp_painter.end()
            
            scaled_image = image.scaled(
                pdf_writer.width(),
                pdf_writer.height(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            x = (pdf_writer.width() - scaled_image.width()) // 2
            y = (pdf_writer.height() - scaled_image.height()) // 2
            painter.drawImage(QPoint(x, y), scaled_image)
            
            if i < total_pages - 1:
                pdf_writer.newPage()
        
        painter.end()

        QMessageBox.information(
            self,
            self.translator_manager.translate("success"),
            self.translator_manager.translate("pdf_saved", file_path=file_path)
        )

if __name__ == "__main__":
    app = QApplication(sys.argv)


    lang = "en"
    if os.path.exists("language.txt"):
        with open("language.txt", "r", encoding="utf-8") as f:
            lang = f.read().strip().lower()
    translator = QTranslator()
    if lang == "pt":
        translator.load("portuguese_ts.qm")
    elif lang == "es":
        translator.load("traducao_es.qm")
    app.installTranslator(translator)


    window = MainWindow()
    window._translator = translator  
    window.showMaximized()
    sys.exit(app.exec())