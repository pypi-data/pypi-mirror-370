import filetype
# pip install filetype

def type_of_file(filepath):
    kind = filetype.guess(filepath)
    if kind is None:
        return "Tipo desconhecido ou não suportado"
    return (kind.extension, kind.mime)

# Exemplo de uso
if __name__ == "__main__":
    pdf_path = "/mnt/boveda/DATASHEET/GDS-806810.pdf"
    
    print(type_of_file(pdf_path)[1])  
