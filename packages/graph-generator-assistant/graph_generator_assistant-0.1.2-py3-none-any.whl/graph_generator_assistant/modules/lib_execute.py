#!/usr/bin/python3

import importlib.util
import os
import tempfile

import sys
import io
from contextlib import redirect_stdout

def execute_function_from_string(parent, module_name, base_path, output_filepath):
    module_path = os.path.join(base_path, f"{module_name}.py")
    
    # Cria um buffer para capturar a saída
    output_buffer = io.StringIO()
    
    try:
        # Redireciona stdout para o buffer
        with redirect_stdout(output_buffer):
            # Carrega e executa o módulo
            spec = importlib.util.spec_from_file_location(module_name, module_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Obtém e executa a função
            func = getattr(module, module_name)
            func(output_filepath=output_filepath)
            
        # Obtém a saída capturada
        output_text = output_buffer.getvalue()+"\nEND\n"
        
    except Exception as e:
        output_text = f"Erro na execução: {str(e)}"
    finally:
        output_buffer.close()
    
    # Atualiza o widget de texto
    parent.text_output.appendPlainText(output_text)


def generate_data(  parent,
                    mod_path, # input Path of module
                    img_path  # output image path
                    ):
    module_src_dir  = os.path.dirname(mod_path)    
    module_name     = os.path.splitext(os.path.basename(mod_path))[0]
    
    execute_function_from_string(   parent,
                                    module_name, 
                                    module_src_dir, 
                                    img_path)


def save_data(parent,mod_name, mod_str):
    temp_dir = tempfile.gettempdir()
    mod_path = os.path.join(temp_dir, mod_name + ".py")
    img_path = os.path.join(temp_dir, mod_name + ".png")

    with open(mod_path, "w", encoding="utf-8") as arquivo:
        arquivo.write(mod_str)

    generate_data(parent,mod_path, img_path)

    return mod_path, img_path
    
if __name__ == '__main__':
    # Exemplo de uso
    generate_data(None,"../templates/workflow_diagram1.py","salida.pdf")
    #execute_function_from_string(None,"workflow_diagram1", "../templates","salida.pdf")

