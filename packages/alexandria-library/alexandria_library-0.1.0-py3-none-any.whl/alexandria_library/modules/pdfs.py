import PyPDF2
# pip install PyPDF2
from typing import Dict, Any

from PyPDF2 import PdfReader

def is_text_selectable(filepath, max_pages_check=5):
    has_text = False
    try:
        reader = PdfReader(filepath)
        # Verifica apenas as primeiras 'max_pages_check' páginas
        for i, page in enumerate(reader.pages):
            if i >= max_pages_check:
                break
            text = page.extract_text()
            if text and text.strip():  # Se extrair texto não vazio
                has_text = True
                break
    except Exception as e:
        print(f"Erro ao processar PDF: {e}")
        return False
    return has_text

def is_pdf(filepath):
    try:
        with open(filepath, 'rb') as file:
            header = file.read(5)  # Lê os primeiros 5 bytes
            return header == b'%PDF-'
    except:
        return False

def modificar_metadados_pdf(caminho_pdf: str, novos_metadados: Dict[str, Any], caminho_saida: str = None) -> bool:
    """
    Modifica os metadados de um arquivo PDF.

    Parâmetros:
    caminho_pdf (str): Caminho do arquivo PDF original
    novos_metadados (dict): Dicionário com novos metadados a serem modificados
    caminho_saida (str, opcional): Caminho para salvar o novo PDF. 
                                   Se não especificado, sobrescreve o arquivo original.

    Retorna:
    bool: True se a modificação foi bem-sucedida, False caso contrário
    """
    try:
        # Abre o arquivo PDF em modo de leitura binária
        with open(caminho_pdf, 'rb') as arquivo:
            # Cria um leitor de PDF
            leitor_pdf = PyPDF2.PdfReader(arquivo)
            
            # Cria um escritor de PDF
            escritor_pdf = PyPDF2.PdfWriter()
            
            # Adiciona todas as páginas do PDF original
            for pagina in leitor_pdf.pages:
                escritor_pdf.add_page(pagina)
            
            # Atualiza os metadados com os novos valores
            metadados = leitor_pdf.metadata or {}
            for chave, valor in novos_metadados.items():
                # Convert key to NameObject and value to TextStringObject
                metadados[PyPDF2.generic.NameObject(chave)] = PyPDF2.generic.TextStringObject(str(valor))
            
            # Adiciona os metadados atualizados ao escritor
            escritor_pdf.add_metadata(metadados)
            
            # Determina o caminho de saída
            caminho_final = caminho_saida or caminho_pdf
            
            # Salva o novo PDF com os metadados modificados
            with open(caminho_final, 'wb') as arquivo_saida:
                escritor_pdf.write(arquivo_saida)
            
            return True
    
    except FileNotFoundError:
        print(f"Erro: Arquivo não encontrado em {caminho_pdf}")
        return False
    except PyPDF2.errors.PdfReadError:
        print(f"Erro: Não foi possível ler o arquivo PDF em {caminho_pdf}")
        return False
    except Exception as e:
        print(f"Erro inesperado: {e}")
        return False
        
def get_metadata_pdf(caminho_pdf):
    """
    Extrai metadados de um arquivo PDF.

    Parâmetros:
    caminho_pdf (str): Caminho completo para o arquivo PDF

    Retorna:
    dict: Dicionário contendo os metadados do PDF
    """
    default_dict = {}
    try:
        with open(caminho_pdf, 'rb') as arquivo:
            leitor_pdf = PyPDF2.PdfReader(arquivo)
            metadados = leitor_pdf.metadata
            if metadados is None:
                return default_dict

            # Convert the metadata to a regular dictionary with string keys
            regular_dict = default_dict.copy()
            for key, value in metadados.items():
                regular_dict[str(key)] = str(value)
                
            return regular_dict
    
    except FileNotFoundError:
        print(f"Erro: Arquivo não encontrado em {caminho_pdf}")
        return default_dict
    except PyPDF2.errors.PdfReadError:
        print(f"Erro: Não foi possível ler o arquivo PDF em {caminho_pdf}")
        return default_dict
    except Exception as e:
        print(f"Erro inesperado: {e}")
        return default_dict

# Exemplo de uso
if __name__ == "__main__":
    pdf_path = "/mnt/boveda/DATASHEET/GDS-806810.pdf"
    metadados = get_metadata_pdf(pdf_path)
    
    # Imprimir os metadados de forma legível
    for chave, valor in metadados.items():
        print(f"{chave}: {valor}")
    
    metadados['/Title'] = 'title'
    
    modificar_metadados_pdf(pdf_path, metadados)
