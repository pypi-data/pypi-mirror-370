import os
import subprocess
import platform

def open_from_filepath(file_path):
    """Open the file in the default text editor according to the operating system"""
    
    # Verifica se o arquivo existe
    if not os.path.exists(file_path):
        print(f"The file {file_path} does not exist.")
        return -1
    
    # Detecta o sistema operacional
    so = platform.system().lower()
    
    try:
        # Define o editor baseado no sistema operacional
        if so == "linux" or so == "darwin":  # Linux ou macOS
            subprocess.Popen(["xdg-open", file_path])  # Usado no Linux e macOS
        elif so == "windows":  # Windows
            subprocess.Popen(["notepad", file_path])  # Notepad para Windows
        else:
            print(f"Operating system not supported for opening files.")
            return -3
        
        print(f"File {file_path} opened with default editor.")
        return 0
    
    except Exception as e:
        print(f"Error trying to open file: {e}")
        return -2

    return 0

