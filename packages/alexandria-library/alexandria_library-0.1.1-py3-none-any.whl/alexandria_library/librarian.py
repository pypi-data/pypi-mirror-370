from PyQt5.QtWidgets import (QApplication, QMainWindow, QTreeView, QTableView, QAbstractItemView,   
                             QFileSystemModel, QSplitter, QToolBar, QAction, QLabel, QFileDialog, 
                             QMenu, QProgressBar, QVBoxLayout, QWidget, QSizePolicy, 
                             QHBoxLayout, QLineEdit, QPushButton, QMessageBox)
from PyQt5.QtCore import QDir, Qt, QUrl
from PyQt5.QtGui import QIcon, QStandardItemModel, QDesktopServices

from alexandria_library.modules.proxy import CaseInsensitiveSortModel

import os
import sys
import signal
import subprocess
import platform

#BASE_PATH = os.path.expanduser("/media/fernando/INFORMATION/CIENCIA/CIENCIA-BOOKS+NOTES/")
#BASE_PATH = os.path.expanduser("/mnt/boveda/DATASHEET")
BASE_PATH  = os.path.expanduser("~/Alexandria")



from alexandria_library.modules.worker  import FileWorker
from alexandria_library.modules.files   import save_file_in
from alexandria_library.modules.files   import open_file_from_index
from alexandria_library.modules.files   import open_folder_from_path
from alexandria_library.modules.context_menu   import show_context_menu_from_index
from alexandria_library.modules.about_window   import show_about_window
from alexandria_library.modules.search_results import display_search_results_from_file_list
from alexandria_library.desktop import create_desktop_file, create_desktop_directory, create_desktop_menu
import alexandria_library.about as about

if not os.path.exists(BASE_PATH):
    os.makedirs(os.path.join(BASE_PATH,"Library"))

class Alexandria(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(about.__program_name__)
        self.setGeometry(50, 100, 1100, 600)
        self.current_file_model = None
        
        # Icon
        base_dir_path = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(base_dir_path, 'icons', 'logo.png')
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        # Configuração dos modelos
        self.dir_model = QFileSystemModel()
        self.dir_model.setRootPath(BASE_PATH)
        self.dir_model.setFilter(QDir.AllDirs | QDir.NoDotAndDotDot)

        # Modelo para arquivos do diretório atual (não recursivo)
        self.file_model = QFileSystemModel()
        self.file_model.setFilter(QDir.Files | QDir.NoDotAndDotDot)
        
        self.file_model.setNameFilters(["!*.bib","!*.json"])
        self.file_model.setNameFilterDisables(False)
        # False, os arquivos que não correspondem aos filtros são completamente ocultos
        # True, os arquivos não correspondentes seriam desabilitados, mas ainda visíveis

        # Modelo para todos os arquivos (recursivo)
        self.all_files_model = QStandardItemModel()

        # Configuração da interface
        self.init_ui()
        self.create_toolbar()
        self.create_statusbar()

    def init_ui(self):
        # Widgets principais
        self.tree_view = QTreeView()
        self.tree_view.setModel(self.dir_model)
        self.tree_view.setRootIndex(self.dir_model.index(BASE_PATH))
        self.tree_view.setHeaderHidden(True)
        self.tree_view.hideColumn(1)
        self.tree_view.hideColumn(2)
        self.tree_view.hideColumn(3)
        self.tree_view.setSelectionMode(QTreeView.SingleSelection)
        self.tree_view.selectionModel().selectionChanged.connect(self.on_tree_selection_changed)

        self.table_view = QTableView()
        self.proxy_model = CaseInsensitiveSortModel()
        self.proxy_model.setSourceModel(self.all_files_model)
        self.table_view.setModel(self.proxy_model)  # Começa com o modelo vazio
        
        # Configurações para tornar a tabela não editável
        
        # 1. Desabilita edição direta das células
        self.table_view.setEditTriggers(QAbstractItemView.NoEditTriggers)
        # 2. Permite seleção de células/linhas
        self.table_view.setSelectionMode(QAbstractItemView.ExtendedSelection)
        # 3. Habilita seleção de texto para cópia
        self.table_view.setTextElideMode(Qt.ElideNone)
        # 4. Permite seleção de múltiplas linhas/células
        self.table_view.setSelectionBehavior(QAbstractItemView.SelectRows)
        # 5. Para copiar, você pode adicionar um shortcut de teclado para Ctrl+C
        self.table_view.installEventFilter(self)
        # 6, Sorting
        self.table_view.setSortingEnabled(True)
        
        self.table_view.doubleClicked.connect(self.open_file)
        self.table_view.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table_view.customContextMenuRequested.connect(self.show_context_menu)

        # Splitter
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self.tree_view)
        splitter.addWidget(self.table_view)
        splitter.setSizes([200, 600])

        # base path
        self.basepath_box = QLineEdit()
        self.basepath_box.setText(BASE_PATH)
        self.basepath_box.returnPressed.connect(self.basepath_box_pressed)
        change_basepath_button = QPushButton("Select path")
        change_basepath_button.clicked.connect(self.select_base_path)
        
        basepath_layout = QHBoxLayout()
        basepath_layout.addWidget(QLabel("Base path:"))
        basepath_layout.addWidget(self.basepath_box)
        basepath_layout.addWidget(change_basepath_button)

        # Filtro de busca
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search in file names and *.bib files...")
        self.search_box.returnPressed.connect(self.start_search)
        search_button = QPushButton("Search")
        search_button.clicked.connect(self.start_search)
        clear_button = QPushButton("Clean")
        clear_button.clicked.connect(self.clear_search)

        search_layout = QHBoxLayout()
        search_layout.addWidget(self.search_box)
        search_layout.addWidget(search_button)
        search_layout.addWidget(clear_button)

        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0) #self.progress_bar.setVisible(False)

        # Layout principal
        main_layout = QVBoxLayout()
        main_layout.addLayout(basepath_layout)
        main_layout.addWidget(splitter)
        main_layout.addLayout(search_layout)
        main_layout.addWidget(self.progress_bar)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def create_toolbar(self):
        self.toolbar = QToolBar("Tool bar")
        self.toolbar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        self.addToolBar(self.toolbar)
        
        #
        self.add_file_action = QAction(QIcon.fromTheme('edit-copy'), "Add to Lib.", self)
        self.add_file_action.setToolTip("Copy file to some path in the library directory.")
        self.add_file_action.triggered.connect(self.add_file)
        self.toolbar.addAction(self.add_file_action)
        
        #
        self.refresh_action = QAction(QIcon.fromTheme('view-refresh'), "Refresh", self)
        self.refresh_action.triggered.connect(self.refresh)
        self.refresh_action.setToolTip("Refresh the information of all files in the library directory.")
        self.toolbar.addAction(self.refresh_action)

        # Adicionar o espaçador
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.toolbar.addWidget(spacer)
        
        self.coffee_action = QAction("Coffee", self)
        self.coffee_action.setIcon(QIcon.fromTheme("emblem-favorite"))
        self.coffee_action.setToolTip("Buy me a coffee (TrucomanX)")
        self.coffee_action.triggered.connect(self.buy_me_a_coffee)
        self.toolbar.addAction(self.coffee_action)
        
        #
        self.about_action = QAction(QIcon.fromTheme('help-about'), "About", self)
        self.about_action.triggered.connect(self.open_about)
        self.about_action.setToolTip("Show the information of program.")
        self.toolbar.addAction(self.about_action)
        

    def buy_me_a_coffee(self):
        self.status_bar.showMessage("Buy me a coffee in https://ko-fi.com/trucomanx")
        QDesktopServices.openUrl(QUrl("https://ko-fi.com/trucomanx"))    

    def create_statusbar(self):
        self.statusBar().showMessage("Ready")

    def open_about(self):
        data = {
            "version": about.__version__,
            "package": about.__package__,
            "program_name": about.__program_name__,
            "author": about.__author__,
            "email": about.__email__,
            "description": about.__description__,
            "url_source": about.__url_source__,
            "url_doc": about.__url_doc__,
            "url_funding": about.__url_funding__,
            "url_bugs": about.__url_bugs__
        }
        
        base_dir_path = os.path.dirname(os.path.abspath(__file__))
        logo_path = os.path.join(base_dir_path, 'icons', 'logo.png')
        
        show_about_window(data, logo_path)


    def on_tree_selection_changed(self):
        
        selected = self.tree_view.selectedIndexes()
        if selected:
            index = selected[0]
            path = self.dir_model.filePath(index)
            
            self.load_all_files_from_directory(path)

   
    def load_all_files_from_directory(self, directory):
        self.table_view.setEnabled(False)
        
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        self.worker = FileWorker(directory, list_all=True)
        self.worker.progress_updated.connect(self.update_progress)
        self.worker.directory_files_found.connect(self.display_search_results)
        self.worker.start()

    def add_file(self):
        save_file_in(self,BASE_PATH,self.refresh)


    def refresh(self):
        self.dir_model.setRootPath("")  # Força atualização
        self.dir_model.setRootPath(BASE_PATH)
        self.tree_view.setRootIndex(self.dir_model.index(BASE_PATH))
        self.on_tree_selection_changed()
       
    def change_base_path(self,new_path):
        global BASE_PATH
        if os.path.exists(new_path) and os.path.isdir(new_path):
            #self.tree_view.selectionModel().clearSelection()
            
            BASE_PATH = str(new_path)
            
            self.basepath_box.setText(BASE_PATH)

            self.dir_model.setRootPath(BASE_PATH)
            self.tree_view.setModel(self.dir_model)
            self.tree_view.setRootIndex(self.dir_model.index(BASE_PATH))
            
            model = QStandardItemModel()  
            model.clear()  
            self.proxy_model = CaseInsensitiveSortModel()
            self.proxy_model.setSourceModel(model)
            self.table_view.setModel(self.proxy_model) 

    def basepath_box_pressed(self):
        new_path = self.basepath_box.text()
        self.change_base_path(new_path)

    def select_base_path(self):
        
        new_path = QFileDialog.getExistingDirectory(
            self, 
            "Select or create a Diretory", 
            BASE_PATH,
            QFileDialog.ShowDirsOnly | QFileDialog.DontUseNativeDialog  # Importante para ter mais opções
        )

        if new_path:
            self.change_base_path(new_path)
 
        

    def open_file(self, index):
        open_file_from_index(self,BASE_PATH,index)
        
    def show_context_menu(self, pos):
        show_context_menu_from_index(self, BASE_PATH, pos)

    def start_search(self):
        search_text = self.search_box.text().strip()
        if not search_text:
            return

        selected = self.tree_view.selectedIndexes()
        if not selected:
            search_root = BASE_PATH
        else:
            search_root = self.dir_model.filePath(selected[0])

        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)

        self.worker = FileWorker(search_root, search_text)
        self.worker.progress_updated.connect(self.update_progress)
        self.worker.search_complete.connect(self.display_search_results)
        self.worker.start()

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def display_search_results(self, file_list):
        display_search_results_from_file_list(self, BASE_PATH, file_list)
        self.table_view.setEnabled(True)

    def clear_search(self):
        self.search_box.clear()
        self.progress_bar.setValue(0) #self.progress_bar.setVisible(False)
        self.on_tree_selection_changed()

    def show_notification_message(self, title, message):
        """Show a system notification"""
        if platform.system() == "Linux":
            msg = message.replace("\""," ")
            os.system(f'notify-send "⚠️ {title} ⚠️" "{msg}"')
        else:
            app = QApplication.instance()
            
            tray_icon = app.property("tray_icon")
            
            if tray_icon:
                tray_icon.showMessage("⚠️ " + title + " ⚠️", message, QSystemTrayIcon.Information, 3000)

    def closeEvent(self, event):
        if hasattr(self, 'worker') and self.worker.isRunning():
            self.worker.cancel()
            self.worker.wait()
        event.accept()

def main():
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    
    create_desktop_directory()    
    create_desktop_menu()
    create_desktop_file('~/.local/share/applications')
    
    for n in range(len(sys.argv)):
        if sys.argv[n] == "--autostart":
            create_desktop_directory(overwrite = True)
            create_desktop_menu(overwrite = True)
            create_desktop_file('~/.config/autostart', overwrite=True)
            return
        if sys.argv[n] == "--applications":
            create_desktop_directory(overwrite = True)
            create_desktop_menu(overwrite = True)
            create_desktop_file('~/.local/share/applications', overwrite=True)
            return
    
    app = QApplication(sys.argv)
    app.setApplicationName(about.__package__) # xprop WM_CLASS # *.desktop -> StartupWMClass    
    window = Alexandria()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
