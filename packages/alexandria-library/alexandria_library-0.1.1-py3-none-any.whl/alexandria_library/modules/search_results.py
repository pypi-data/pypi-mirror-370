import os
import json
from PyQt5.QtWidgets import QHeaderView
from PyQt5.QtGui import QStandardItem

from alexandria_library.modules.proxy import CaseInsensitiveSortModel

def display_search_results_from_file_list(parent, base_path, file_list):

    
    # Clear the model
    parent.all_files_model.clear()
    
    parent.all_files_model.setHorizontalHeaderLabels(["Arquives","Directories","bib","ocr"])
    
    parent.progress_bar.setValue(0)
    L = len(file_list)

    for l,file_path in enumerate(file_list):
        relative_path = os.path.relpath(file_path, base_path)
        filename  = os.path.basename(relative_path)
        directory = os.path.dirname(relative_path)
        
        item1 = QStandardItem(filename)
        item2 = QStandardItem(directory)
        
        if os.path.exists(file_path+'.bib'):
            item3 = QStandardItem("✅")
        else:
            item3 = QStandardItem("❌")
            
        item4 = QStandardItem("")
        if os.path.exists(file_path+'.json'):
            with open(file_path+'.json', 'r', encoding='utf-8') as f:
                dados = json.load(f)
                ocr = dados.get("ocr",None)
                if ocr==True:
                    item4 = QStandardItem("✅")
                elif ocr==False:
                    item4 = QStandardItem("❌")
            
        
        parent.all_files_model.appendRow([item1,item2,item3,item4])
        
        parent.progress_bar.setValue(int(((l+1)*100.0)/L))
    parent.progress_bar.setValue(0)
    
    # Configurar a view para mostrar as colunas
    parent.proxy_model = CaseInsensitiveSortModel()
    parent.proxy_model.setSourceModel(parent.all_files_model)
    parent.table_view.setModel(parent.proxy_model)
    
    # Configurações de redimensionamento de colunas
    header = parent.table_view.horizontalHeader()
    header.setEnabled(True)
    header.setVisible(True)

    # Configuração global POR ÚLTIMO
    header.setSectionResizeMode(QHeaderView.Interactive)
            
    # Opcional: Habilitar movimentação de colunas
    header.setSectionsMovable(True)
    
    # Definir largura inicial da segunda coluna
    header.resizeSection(0, 500)  # Largura inicial de 150 pixels
    header.resizeSection(1, 150)  
    header.resizeSection(2, 30)  
    header.resizeSection(3, 30)  
            
    parent.statusBar().showMessage(f"{len(file_list)} files found")
