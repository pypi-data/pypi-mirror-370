import base64

def b64decode(b64_string:str=None)->str:
    """Faz o decode de uma string em base64

    Args:
        b64_string (str): string em base64

    Returns:
        str: string em texto
    """
        
    if b64_string is None or b64_string == "":
    
        raise ValueError("Uma string Base64 precisa ser informada com o parâmetro 'b64_string'")
    
    try:
    
        b64_decode_output = base64.b64decode(b64_string).decode('utf-8')
    
    except:
    
        raise TypeError("A string informada não está em formato Base64")

    return b64_decode_output

def b64encode(string_to_convert:str=None)->base64:
    """Faz o encode de uma string para base64

    Args:
        string_to_convert (str): string para converter em base64

    Returns:
        base64: string convertida para base64
    """
    
    if string_to_convert is None or string_to_convert == "":
    
        raise ValueError("Uma string precisa ser informada com o parâmetro 'string_to_convert'")
    
    try:
    
        b64_encode_output = base64.b64encode(str(string_to_convert).encode('utf-8')).decode('utf-8')
    
    except Exception as e:
    
        raise TypeError(f"Erro ao converter a string para Base64: {e}")

    return b64_encode_output

