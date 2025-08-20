
from pydantic import BaseModel, field_validator, EmailStr

class InitParamsValidator(BaseModel):
    """
    Classe responsável por validar os parâmetros de inicialização.
    Atributos:
    - key (str): A chave de autenticação.
    - with_subject (str): O assunto da autenticação.
    - scopes (list): A lista de escopos.
    - version (str): A versão.
    Métodos:
    - check_str_input(cls, value, info): Valida se o valor é uma string não vazia.
    - check_list_input(cls, value, info): Valida se o valor é uma lista.
    """
        
    token: dict
    with_subject: EmailStr
    scopes : list
    version : str

    """
    Valida se o valor é uma string não vazia.
    Parâmetros:
    - value (Any): O valor a ser validado.
    - info (FieldInfo): Informações sobre o campo.
    Retorna:
    - value (Any): O valor validado.
    Lança:
    - ValueError: Se o valor não for uma string ou estiver vazio.
    """
    @field_validator("version")
    def check_str_input(cls, value, info):
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"O campo '{info.field_name}' deve ser strings e não {type(value)}")
        return value
    
    @field_validator('token')
    def check_dict_input(cls, value, info):
        if not isinstance(value, dict):
            raise ValueError(f"O campo '{info.field_name}' deve ser um dicionário e não {type(value)}")
        return value

    """
    Valida se o valor é uma lista.
    Parâmetros:
    - value (Any): O valor a ser validado.
    - info (FieldInfo): Informações sobre o campo.
    Retorna:
    - value (Any): O valor validado.
    Lança:
    - ValueError: Se o valor não for uma lista.
    """
    @field_validator('scopes')
    def check_list_input(cls, value, info):
        if not isinstance(value, list):
            raise ValueError(f"O parametro '{info.field_name}' deve ser uma lista")
        
        return value

class CreateFolderValidator(BaseModel):
    """
    Validação para a criação de uma pasta no Google Drive.
    Atributos:
    - name (str): O nome da pasta a ser criada.
    - parent_folder_id (str): O ID da pasta pai onde a nova pasta será criada.
    Métodos:
    - check_str_input(value, info): Valida se o valor fornecido é uma string não vazia.
    """
    name: str
    parent_folder_id: str
    validate_existence: bool

    """
    Valida se o valor fornecido é uma string não vazia.
    Parâmetros:
    - value: O valor a ser validado.
    - info: Informações sobre o campo sendo validado.
    Retorna:
    - O valor fornecido, se for uma string não vazia.
    Lança:
    - ValueError: Se o valor não for uma string ou for uma string vazia.
    """
    @field_validator('name','parent_folder_id')
    def check_str_input(cls, value, info):
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"O campo '{info.field_name}' deve ser strings e não {type(value)}")
        return value

    @field_validator('validate_existence')
    def check_bool_input(cls, value, info):
        if not isinstance(value, bool):
            raise ValueError(f"O campo '{info.field_name}' deve ser bool e não {type(value)}")
        return value

class ListFolderValidator(BaseModel):
    """
    Validação para a classe ListFolderValidator.

    Atributos:
    - query (str): A consulta a ser realizada.
    - spaces (str): Os espaços a serem considerados.
    - fields (str): Os campos a serem retornados.

    Métodos:
    - check_str_input(cls, value, info): Valida se o valor fornecido é uma string não vazia.

    """

    query: str
    fields: str
    spaces: str

    """
    Valida se o valor fornecido é uma string não vazia.

    Parâmetros:
    - value (Any): O valor a ser validado.
    - info (FieldInfo): Informações sobre o campo.

    Retorna:
    - value (Any): O valor validado.

    Lança:
    - ValueError: Se o valor não for uma string ou for uma string vazia.

    """
    @field_validator('query','spaces','fields')
    def check_str_input(cls, value, info):
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"O campo '{info.field_name}' deve ser strings e não {type(value)}")
        return value
    
class UploadValidator(BaseModel):
    """
    Validador para upload de arquivo no Google Drive.

    Atributos:
    - file_path (str): Caminho do arquivo a ser enviado.

    """
    folder_id: str
    name: str
    file_path: str
    mimetype: str

    @field_validator('folder_id','name','file_path', 'mimetype')
    def check_str_input(cls, value, info):
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"O campo '{info.field_name}' deve ser strings e não {type(value)}")
        return value
