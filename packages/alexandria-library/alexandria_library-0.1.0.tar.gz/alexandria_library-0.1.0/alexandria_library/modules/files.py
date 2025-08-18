from PyQt5.QtWidgets import QFileDialog, QMessageBox
import shutil
import os
import subprocess
import sys

def read_file_from_path(file_path):
    """Lê o conteúdo completo do arquivo usando gerenciador de contexto."""
    with open(file_path, 'r', encoding='utf-8') as arquivo:
        conteudo = arquivo.read()
    return conteudo

def open_folder_from_path(file_path):
    folder_path = os.path.dirname(file_path)
    if os.path.exists(folder_path):
        if os.name == 'nt':
            os.startfile(folder_path)
        else:
            opener = 'open' if sys.platform == 'darwin' else 'xdg-open'
            subprocess.call([opener, folder_path])

def open_file_from_path(file_path):
    if os.path.exists(file_path):
        if os.name == 'nt':
            os.startfile(file_path)
        else:
            opener = 'open' if sys.platform == 'darwin' else 'xdg-open'
            subprocess.call([opener, file_path])

def open_file_from_index(parent,base_path,index):

        row    = index.row()
        model = parent.table_view.model()

        proxy_index = model.index(row, 0)
        source_index = model.mapToSource(proxy_index)
        filename = model.sourceModel().itemFromIndex(source_index).text()
        
        proxy_index = model.index(row, 1)
        source_index = model.mapToSource(proxy_index)
        rel_dir = model.sourceModel().itemFromIndex(source_index).text()

        file_path = os.path.join(base_path,rel_dir,filename)
            
        open_file_from_path(file_path)

def save_file_in(parent,base_path,func_refresh):
    file_dialog = QFileDialog()
    file_path, _ = file_dialog.getOpenFileName(parent, "Salvar Arquivo")

    if file_path:
        try:
            dir_path = file_dialog.getExistingDirectory(parent, "Save in?",
                                   base_path,
                                   QFileDialog.ShowDirsOnly)
            shutil.copy2(file_path, dir_path)
            func_refresh()
            
        except Exception as e:
            QMessageBox.warning(parent, "Erro", f"Não foi possível criar o arquivo: {str(e)}")
