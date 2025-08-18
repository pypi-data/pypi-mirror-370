import os
from PyQt5.QtCore import QThread, pyqtSignal

class FileWorker(QThread):
    """
    A QThread-based worker class for searching and listing files in a directory.
    
    Signals:
    - progress_updated: Emits the current progress percentage of file processing
    - search_complete: Emits a list of files matching the search criteria
    - directory_files_found: Emits a list of all files found in the directory
    """
    
    # Signal to update progress during file processing
    progress_updated = pyqtSignal(int)
    
    # Signal to indicate search completion with matching files
    search_complete = pyqtSignal(list)
    
    # Signal to indicate all files in directory have been found
    directory_files_found = pyqtSignal(list)

    def __init__(self, root_dir, search_text=None, list_all=False):
        """
        Initialize the FileWorker thread.
        
        Parameters:
        - root_dir (str): The root directory to start searching from
        - search_text (str, optional): Text to search for in files and .bib files. 
          Defaults to None.
        - list_all (bool, optional): If True, lists all files instead of searching. 
          Defaults to False.
        
        Attributes:
        - root_dir: Stores the root directory path
        - search_text: Lowercase search text (None if not searching)
        - list_all: Flag to determine if listing all files or searching
        - canceled: Flag to allow cancellation of file processing
        """
        super().__init__()
        self.root_dir = root_dir
        self.search_text = search_text.lower() if search_text else None
        self.list_all = list_all
        self.canceled = False

    def run(self):
        """
        Main thread method. Determines whether to list all files or search files 
        based on initialization parameters.
        
        If list_all is True, calls list_all_files()
        If search_text is provided, calls search_files()
        """
        if self.list_all:
            self.list_all_files()
        elif self.search_text:
            self.search_files()

    def list_all_files(self):
        """
        Lists all files in the root directory and its subdirectories, 
        excluding .bib files.
        
        Process:
        1. Count total number of files for progress tracking
        2. Collect all file paths, excluding .bib files
        3. Emit progress and file list via signals
        
        Emits:
        - progress_updated: Progress percentage during file collection
        - directory_files_found: List of all found file paths
        """
        all_files = []
        total_files = 0
        processed_files = 0

        # Primeiro contamos o total de arquivos para a barra de progresso
        for root, _, files in os.walk(self.root_dir):
            for file in files:
                if not file.endswith('.bib') and not file.endswith('.json'):
                    total_files += 1

        if total_files == 0:
            self.directory_files_found.emit([])
            return

        # Agora coletamos todos os arquivos
        for root, _, files in os.walk(self.root_dir):
            if self.canceled:
                break

            for file in files:
                if self.canceled:
                    break

                if file.endswith('.bib') or file.endswith('.json'):
                    continue

                file_path = os.path.join(root, file)
                all_files.append(file_path)

                processed_files += 1
                progress = int((processed_files / total_files) * 100)
                self.progress_updated.emit(progress)
        
        # Emit found files
        self.directory_files_found.emit(all_files)

    def search_files(self):
        """
        Searches files in the root directory and its subdirectories.
        
        Search criteria:
        1. Search in filename (case-insensitive)
        2. If filename doesn't match, search in corresponding .bib file
        
        Process:
        1. Count total number of files for progress tracking
        2. Search files and their .bib counterparts for search text
        3. Collect matching file paths
        4. Emit progress and matching files via signals
        
        Emits:
        - progress_updated: Progress percentage during file search
        - search_complete: List of file paths matching search criteria
        """
        matching_files = []
        total_files = 0
        processed_files = 0

        # Contagem total de arquivos para progresso
        for root, _, files in os.walk(self.root_dir):
            for file in files:
                if not file.endswith('.bib') and not file.endswith('.json'):
                    total_files += 1

        if total_files == 0:
            self.search_complete.emit([])
            return

        # Busca real
        for root, _, files in os.walk(self.root_dir):
            if self.canceled:
                break

            for file in files:
                if self.canceled:
                    break

                if file.endswith('.bib') or file.endswith('.json'):
                    continue

                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, self.root_dir)
                
                # Search in filename
                if self.search_text in file.lower():
                    matching_files.append(file_path)
                else:
                    # Search in .bib file
                    bib_file = file_path + '.bib'
                    if os.path.exists(bib_file):
                        try:
                            with open(bib_file, 'r', encoding='utf-8') as f:
                                content = f.read().lower()
                                if self.search_text in content:
                                    matching_files.append(file_path)
                        except:
                            pass

                processed_files += 1
                progress = int((processed_files / total_files) * 100)
                self.progress_updated.emit(progress)
        
        # Emit matching files
        self.search_complete.emit(matching_files)

    def cancel(self):
        """
        Sets the canceled flag to True, which stops file processing 
        in the current thread.
        """
        self.canceled = True
