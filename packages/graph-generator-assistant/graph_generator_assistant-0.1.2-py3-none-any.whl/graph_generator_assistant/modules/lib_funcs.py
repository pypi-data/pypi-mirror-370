from deep_consultation.core import consult_with_deepchat
import re

def extrair_codigo_puro(resposta: str) -> str:
    # Tenta encontrar o código dentro de ```python ```
    match = re.search(r"```python\n(.*?)\n```", resposta, re.DOTALL)
    
    if match:
        return match.group(1).strip()
    
    # Se não houver blocos de código, assume que já é Python puro
    return resposta.strip()

def consultation_in_depth(system_data,system_question,msg):

    OUT=consult_with_deepchat(  system_data["base_url"],
                                system_data["api_key"],
                                system_data["model"],
                                msg,
                                system_question)
                                
    return extrair_codigo_puro(OUT)


