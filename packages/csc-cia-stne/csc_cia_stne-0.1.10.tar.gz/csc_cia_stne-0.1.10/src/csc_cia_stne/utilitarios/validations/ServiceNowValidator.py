from pydantic import BaseModel, field_validator, model_validator
from typing import List


class InitParamsValidator(BaseModel):
    """
    Classe responsável por validar os parâmetros de inicialização.
    Atributos:
    - username (str): O nome de usuário.
    - password (str): A senha.
    - env (str): O ambiente.
    Métodos:
    - check_str_input(value, info): Valida se o valor é uma string não vazia.
    """
    username: str
    password: str
    env: str

    """
    Valida se o valor é uma string não vazia.
    Parâmetros:
    - value: O valor a ser validado.
    - info: Informações sobre o campo.
    Retorna:
    - O valor validado.
    Lança:
    - ValueError: Se o valor não for uma string ou for uma string vazia.
    """
    @field_validator('username', 'password', 'env')
    def check_str_input(cls, value, info):
        if not value.strip():
            raise ValueError(f"O campo '{info.field_name}' não pode ser vazio")
        if not isinstance(value, str):
           raise ValueError(f"O campo '{info.field_name}' deve ser string e não ser do tipo: {type(value)}")
        return value


class RequestValidator(BaseModel):
    """
    Classe para validar os campos de uma requisição.
    Atributos:
    - url (str): A URL da requisição.
    - timeout (int): O tempo limite da requisição em segundos. O valor padrão é 15.
    Métodos:
    - check_str_input(value, info): Valida se o valor é uma string não vazia.
    - check_input_basic(value, info): Valida se o valor é um inteiro.
    """
    url: str
    timeout: int = 15
    

    """
    Valida se o valor é uma string não vazia.
    Parâmetros:
    - value: O valor a ser validado.
    - info: Informações sobre o campo.
    Retorna:
    - O valor validado.
    Lança:
    - ValueError: Se o valor não for uma string ou estiver vazio.
    """
    @field_validator('url')
    def check_str_input(cls, value, info):
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"O campo '{info.field_name}' deve ser uma string e não um {type(value)} e não vazio")
        return value
    
    """
    Valida se o valor é um inteiro.
    Parâmetros:
    - value: O valor a ser validado.
    - info: Informações sobre o campo.
    Retorna:
    - O valor validado.
    Lança:
    - ValueError: Se o valor não for um inteiro.
    """
    @field_validator('timeout')
    def check_input_basic(cls, value, info):
        if not isinstance(value, int):
            raise ValueError(f"O campo '{info.field_name}' deve ser um inteiro e não um {type(value)}")
        
        return value


class PutValidator(BaseModel):
    """
    Classe de validação para requisições PUT.
    Atributos:
    - url (str): A URL da requisição PUT.
    - payload (dict): O payload da requisição PUT.
    - timeout (int): O tempo limite da requisição PUT em segundos. O valor padrão é 15.
    Métodos:
    - check_str_input(value, info): Valida se o valor do atributo 'url' é uma string não vazia.
    - check_input_basic(value, info): Valida se o valor do atributo 'timeout' é um inteiro.
    - check_dict_input(value, info): Valida se o valor do atributo 'payload' é um dicionário.
    """
        
    url : str
    payload : dict
    timeout : int = 15

    """
    Valida se o valor do atributo 'url' é uma string não vazia.
    Parâmetros:
    - value: O valor do atributo 'url'.
    - info: Informações sobre o campo sendo validado.
    Retorna:
    - O valor do atributo 'url' se for válido.
    Lança:
    - ValueError: Se o valor não for uma string ou for uma string vazia.
    """
    @field_validator('url')
    def check_str_input(cls, value, info):
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"O campo '{info.field_name}' deve ser uma string e não um {type(value)} e não vazio")
        return value
    
    """
    Valida se o valor do atributo 'timeout' é um inteiro.
    Parâmetros:
    - value: O valor do atributo 'timeout'.
    - info: Informações sobre o campo sendo validado.
    Retorna:
    - O valor do atributo 'timeout' se for válido.
    Lança:
    - ValueError: Se o valor não for um inteiro.
    """
    @field_validator('timeout')
    def check_input_basic(cls, value, info):
        if not isinstance(value, int):
            raise ValueError(f"O campo '{info.field_name}' deve ser um inteiro e não um {type(value)}")
        return value
    
    """
    Valida se o valor do atributo 'payload' é um dicionário.
    Parâmetros:
    - value: O valor do atributo 'payload'.
    - info: Informações sobre o campo sendo validado.
    Retorna:
    - O valor do atributo 'payload' se for válido.
    Lança:
    - ValueError: Se o valor não for um dicionário.
    """
    @field_validator('payload')
    def check_dict_input(cls, value, info):
        if not isinstance(value, dict):
            raise ValueError(f"O campo '{info.field_name}' deve ser um dicionário e não um {type(value)}")
        return value


class PostValidator(BaseModel):
    """
    Classe responsável por validar os dados de um post.
    Atributos:
    - url (str): A URL do post.
    - variables (dict): As variáveis do post.
    Métodos:
    - check_str_input(value, info): Valida se o valor do campo 'url' é uma string não vazia.
    - check_dict_input(value, info): Valida se o valor do campo 'variables' é um dicionário.
    """
    url : str
    variables : dict

    @field_validator('url')
    def check_str_input(cls, value, info):
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"O campo '{info.field_name}' deve ser uma string e não um {type(value)} e não vazio")
        return value
    
    @field_validator('variables')
    def check_dict_input(cls, value, info):
        if not isinstance(value, dict):
            raise ValueError(f"O campo '{info.field_name}' deve ser um dicionário e não um {type(value)}")
        return value


class ListTicketValidator(BaseModel):
    """
    Classe para validar os campos de entrada da lista de tickets.
    Atributos:
    - tabela (str): Nome da tabela.
    - query (str): Consulta a ser realizada.
    - campos (List[str]): Lista de campos.
    - timeout (int): Tempo limite.
    - limit (int): Limite de resultados.
    Métodos:
    - check_str_input(value, info): Valida se o valor é uma string não vazia.
    - check_input_basic(value, info): Valida se o valor é um inteiro.
    - check_list_input(value, info): Valida se o valor é uma lista.
    """
    tabela : str
    query : str
    campos : List[str]
    timeout : int
    limite : int
    
    @field_validator('tabela', 'query')
    def check_str_input(cls, value, info):
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"O campo '{info.field_name}' deve ser uma string e não um {type(value)} e não vazio")
        return value
    
    @field_validator('timeout', 'limite')
    def check_input_basic(cls, value, info):
        if not isinstance(value, int):
            raise ValueError(f"O campo '{info.field_name}' deve ser um inteiro e não um {type(value)}")
        return value
    
    @field_validator('campos')
    def check_list_input(cls, value, info):
        if not isinstance(value, list):
            raise ValueError(f"O campo '{info.field_name}' deve ser uma lista e não um {type(value)}")
        return value
    

class UpdateTicketValidator(BaseModel):
    """
    Classe responsável por validar os campos do ticket de atualização.
    Atributos:
    - sys_id (str): O ID do ticket.
    - tabela (str): A tabela do ticket.
    - payload (List[str]): A carga útil do ticket.
    - timeout (int): O tempo limite para a operação.
    Métodos:
    - check_str_input(value, info): Valida se o valor fornecido é uma string não vazia.
    - check_input_basic(value, info): Valida se o valor fornecido é um inteiro.
    - check_list_input(value, info): Valida se o valor fornecido é uma lista.
    """
        
    sys_id : str
    tabela : str
    payload : dict
    timeout : int

    """
    Valida se o valor fornecido é uma string não vazia.
    Parâmetros:
    - value (Any): O valor a ser validado.
    - info (FieldInfo): Informações sobre o campo.
    Retorna:
    - value (Any): O valor validado.
    Lança:
    - ValueError: Se o valor não for uma string ou estiver vazio.
    """
    @field_validator('sys_id', 'tabela')
    def check_str_input(cls, value, info):
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"O campo '{info.field_name}' deve ser uma string e não um {type(value)} e não vazio")
        return value
    
    """
    Valida se o valor fornecido é um inteiro.
    Parâmetros:
    - value (Any): O valor a ser validado.
    - info (FieldInfo): Informações sobre o campo.
    Retorna:
    - value (Any): O valor validado.
    Lança:
    - ValueError: Se o valor não for um inteiro.
    """
    @field_validator('timeout')
    def check_input_basic(cls, value, info):
        if not isinstance(value, int):
            raise ValueError(f"O campo '{info.field_name}' deve ser um inteiro e não um {type(value)}")
        return value

    """
    Valida se o valor fornecido é uma lista.
    Parâmetros:
    - value (Any): O valor a ser validado.
    - info (FieldInfo): Informações sobre o campo.
    Retorna:
    - value (Any): O valor validado.
    Lança:
    - ValueError: Se o valor não for uma lista.
    """
    @field_validator('payload')
    def check_list_input(cls, value, info):
        if not isinstance(value, dict):
            raise ValueError(f"O campo '{info.field_name}' deve ser uma lista e não um {type(value)}")
        return value


class DownloadFileValidator(BaseModel):
    """
    Classe responsável por validar os campos do ticket de download.
    Atributos:
    - sys_id_file (str): O ID do anexo dentro do formulário aberto.
    - file_path (str): URL onde será salvo o arquivo.
    Métodos:
    - check_str_input(value, info): Valida se o valor fornecido é uma string não vazia.
    """
    sys_id_file : str
    file_path : str
    
    
    """
    Valida se o valor fornecido é uma string não vazia.
    Parâmetros:
    - value (Any): O valor a ser validado.
    - info (FieldInfo): Informações sobre o campo.
    Retorna:
    - value (Any): O valor validado.
    Lança:
    - ValueError: Se o valor não for uma string ou estiver vazio.
    """
    @field_validator('sys_id_file', 'file_path')
    def check_str_input(cls, value, info):
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"O campo '{info.field_name}' deve ser uma string e não um {type(value)} e não vazio")
        return value


class AttachFileTicketValidator(BaseModel):
    """
    Classe responsável por validar os campos de entrada do anexo de um ticket no ServiceNow.
    Atributos:
    - header_content_type (dict): O cabeçalho Content-Type da requisição.
    - anexo_path (str): O caminho do anexo a ser enviado.
    - tabela (str): O nome da tabela do ServiceNow.
    - sys_id (str): O ID do registro no ServiceNow.
    - timeout (int): O tempo limite da requisição.
    Métodos:
    - check_str_input(value, info): Valida se o valor do campo é uma string não vazia.
    - check_input_basic(value, info): Valida se o valor do campo é um inteiro.
    - check_dict_input(value, info): Valida se o valor do campo é um dicionário.
    """
    header_content_type : dict
    anexo_path : str
    tabela : str
    sys_id : str
    timeout : int

    @field_validator('sys_id', 'tabela', 'anexo_path')
    def check_str_input(cls, value, info):
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"O campo '{info.field_name}' deve ser uma string e não um {type(value)} e não vazio")
        return value
    
    @field_validator('timeout')
    def check_input_basic(cls, value, info):
        if not isinstance(value, int):
            raise ValueError(f"O campo '{info.field_name}' deve ser um inteiro e não um {type(value)}")
        return value
    
    @field_validator('header_content_type')
    def check_dict_input(cls, value, info):
        if not isinstance(value, dict):
            raise ValueError(f"O campo '{info.field_name}' deve ser um dicionário e não um {type(value)}")
        return value
    

class GetAttachValidator(BaseModel):
    """
    Classe responsável por validar os campos de entrada para a obtenção de anexos no ServiceNow.
    Atributos:
    - sys_id (str): O ID do registro no ServiceNow.
    - tabela (str): O nome da tabela no ServiceNow.
    - campo (str): O nome do campo no ServiceNow.
    - download_dir (str): O diretório onde o anexo será salvo.
    - timeout (int): O tempo limite para a operação de obtenção de anexo.
    Métodos:
    - check_str_input(value, info): Valida se os campos sys_id, tabela, campo e download_dir são strings não vazias.
    - check_input_basic(value, info): Valida se o campo timeout é um inteiro.
    """
        
    sys_id : str
    tabela : str
    download_dir : str
    timeout : int

    """
    Valida se os campos sys_id, tabela, campo e download_dir são strings não vazias.
    Parâmetros:
    - value: O valor do campo a ser validado.
    - info: Informações sobre o campo.
    Retorna:
    - O valor do campo, se for válido.
    Lança:
    - ValueError: Se o campo não for uma string ou estiver vazio.
    """
    @field_validator('sys_id', 'tabela','download_dir')
    def check_str_input(cls, value, info):
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"O campo '{info.field_name}' deve ser uma string e não um {type(value)} e não vazio")
        return value
    
    """
    Valida se o campo timeout é um inteiro.
    Parâmetros:
    - value: O valor do campo a ser validado.
    - info: Informações sobre o campo.
    Retorna:
    - O valor do campo, se for válido.
    Lança:
    - ValueError: Se o campo não for um inteiro.
    """
    @field_validator('timeout')
    def check_input_basic(cls, value, info):
        if not isinstance(value, int):
            raise ValueError(f"O campo '{info.field_name}' deve ser um inteiro e não um {type(value)}")
        return value