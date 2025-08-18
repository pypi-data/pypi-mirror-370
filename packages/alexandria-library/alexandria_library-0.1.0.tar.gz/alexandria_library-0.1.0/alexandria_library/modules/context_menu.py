from PyQt5.QtWidgets import QApplication, QMenu, QAction
from PyQt5.QtGui import QIcon
from urllib.parse import quote
import sys
import os 
import json


from .files   import open_folder_from_path
from .files   import open_file_from_path
from .files   import read_file_from_path
from .message import show_message
from .pdfs    import is_pdf
from .pdfs    import get_metadata_pdf
from .pdfs    import is_text_selectable
from .bibtex  import get_bibtex_from_scholar


def generate_worldcat_search_link(book_title, offset=1):
    # Codifica o título para URL (substitui espaços e caracteres especiais)
    encoded_title = quote(book_title)
    # Formata a URL do WorldCat
    url = f"https://search.worldcat.org/pt/search?q={encoded_title}&offset={offset}"
    return url

def get_metadata_from_path(file_path):
    metadata=get_metadata_pdf(file_path)
    metadata_str = json.dumps(metadata, indent=4, ensure_ascii=False)
        
    show_message(   metadata_str, 
                    width=600, 
                    height=300, 
                    read_only=False, 
                    title="Metadata")
 

    
def save_bib_file(  parent,
                    bib_path,
                    default_str, 
                    width=600, 
                    height=300, 
                    read_only=False, 
                    title="Bib file"):
    
    res = show_message( default_str, 
                        width=width, 
                        height=height, 
                        read_only=read_only, 
                        ok_label='Save',
                        title=title,
                        show_close_button=True)
    if res!='':
        with open(bib_path, 'w', encoding='utf-8') as arquivo:
            arquivo.write(res)
            parent.refresh()

def search_bib_data(parent,
                    bib_file,
                    file_path, 
                    width=600, 
                    height=300, 
                    read_only=False, 
                    title="Info of file"):
    
    name = os.path.splitext(os.path.basename(file_path))[0]
    res = show_message( name, 
                        width=width, 
                        height=height, 
                        read_only=read_only, 
                        ok_label='Search',
                        title=title,
                        show_close_button=True)
    if res!='':
        parent.show_notification_message("Sending consult","Please wait...")
        bib_str = get_bibtex_from_scholar(res)
        
        save_bib_file(  parent,
                        bib_file,
                        bib_str, 
                        width=width, 
                        height=height, 
                        read_only=read_only, 
                        title="Bib file")

def copy_to_clipboard(text):
    clipboard = QApplication.clipboard()
    clipboard.setText(text)
    # Não use app.exec_() se isto for parte de um script não-GUI
    
def check_ocr_pdf(parent,file_path,data, max_pages_check=5):
    data["ocr"] = is_text_selectable(file_path, max_pages_check=max_pages_check)
    with open(file_path+'.json', 'w', encoding='utf-8') as arquivo:
        json.dump(data, arquivo, indent=4, ensure_ascii=False)
        parent.refresh()
    
def show_context_menu_from_index(parent, base_path, pos):

    selected = parent.table_view.selectionModel().selectedRows()
    
    if len(selected) == 1 :
        index = parent.table_view.indexAt(pos)
        if not index.isValid():
            return
            
        row   = index.row()
        model = parent.table_view.model()

        proxy_index = model.index(row, 0)
        source_index = model.mapToSource(proxy_index)
        filename = model.sourceModel().itemFromIndex(source_index).text()
        
        
        proxy_index = model.index(row, 1)
        source_index = model.mapToSource(proxy_index)
        rel_dir = model.sourceModel().itemFromIndex(source_index).text()


        file_path = os.path.join(base_path,rel_dir,filename)
        
        menu = QMenu()

        open_folder_action = QAction("Open dir", parent)
        open_folder_action.setIcon(QIcon.fromTheme("folder-open"))
        open_folder_action.triggered.connect(lambda: open_folder_from_path(file_path))
        menu.addAction(open_folder_action)
        
        copy_path_action = QAction("Copy file path", parent)
        copy_path_action.setIcon(QIcon.fromTheme("edit-copy"))
        copy_path_action.triggered.connect(lambda: copy_to_clipboard(file_path))
        menu.addAction(copy_path_action)

        copy_basename_action = QAction("Copy basename", parent)
        copy_basename_action.setIcon(QIcon.fromTheme("edit-copy"))
        copy_basename_action.triggered.connect(lambda: copy_to_clipboard(os.path.basename(file_path)))
        menu.addAction(copy_basename_action)
        
        if is_pdf(file_path):
            get_metadata_action = QAction("Get PDF metadata", parent)
            get_metadata_action.setIcon(QIcon.fromTheme("application-pdf"))
            get_metadata_action.triggered.connect(lambda: get_metadata_from_path(file_path))
            menu.addAction(get_metadata_action)
        

        json_file = file_path + '.json'
        if os.path.exists(file_path):
            data = dict()
            if os.path.exists(json_file):
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
            if is_pdf(file_path):    
                check_ocr_action = QAction("Verify OCR", parent)
                check_ocr_action.setIcon(QIcon.fromTheme("insert-text"))
                check_ocr_action.triggered.connect(lambda: check_ocr_pdf(   parent, 
                                                                            file_path, 
                                                                            data, 
                                                                            max_pages_check=5))
                menu.addAction(check_ocr_action)
        
        bib_file = file_path + '.bib'
        if os.path.exists(bib_file) and os.path.exists(file_path):
            bib_str = read_file_from_path(bib_file)
            open_bib_action = QAction("Open bib file", parent)
            open_bib_action.setIcon(QIcon.fromTheme("text-x-generic"))
            open_bib_action.triggered.connect(lambda: show_message( bib_str, 
                                                                    width=600, 
                                                                    height=300, 
                                                                    read_only=False, 
                                                                    title="Bib file"))
            menu.addAction(open_bib_action)
        else:
            search_bib_action = QAction("Search bib data", parent)
            search_bib_action.setIcon(QIcon.fromTheme("system-search"))
            search_bib_action.triggered.connect(lambda: search_bib_data(parent,
                                                                        bib_file,
                                                                        file_path, 
                                                                        width=600, 
                                                                        height=300, 
                                                                        read_only=False, 
                                                                        title="Info of file"))
            menu.addAction(search_bib_action)
            
            create_bib_action = QAction("Create bib file", parent)
            create_bib_action.setIcon(QIcon.fromTheme("text-x-generic"))
            create_bib_action.triggered.connect(lambda: save_bib_file(  parent,
                                                                        bib_file,
                                                                        "", 
                                                                        width=600, 
                                                                        height=300, 
                                                                        read_only=False, 
                                                                        title="Bib file"))
            menu.addAction(create_bib_action)

        menu.exec_(parent.table_view.viewport().mapToGlobal(pos))
