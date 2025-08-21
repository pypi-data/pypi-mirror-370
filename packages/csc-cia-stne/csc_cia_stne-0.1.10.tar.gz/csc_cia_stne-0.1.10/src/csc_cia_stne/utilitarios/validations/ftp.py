from pydantic import BaseModel, field_validator

class InitParamsValidator(BaseModel):
    """
    Classe InitParamsValidator
    Valida os parâmetros de inicialização para conexão FTP.
    Atributos:
        host (str): Endereço do servidor FTP. Deve ser uma string não vazia.
        user (str): Nome de usuário para autenticação. Deve ser uma string não vazia.
        password (str): Senha para autenticação. Deve ser uma string não vazia.
        port (int): Porta do servidor FTP. Deve ser um inteiro positivo.
        tryouts (int): Número de tentativas de conexão. Deve ser um inteiro positivo.
        timeout (int): Tempo limite para conexão em segundos. Deve ser um inteiro positivo.
        tls (bool): Indica se a conexão deve usar TLS. Deve ser um valor booleano.
        ssl (bool): Indica se a conexão deve usar SSL. Deve ser um valor booleano.
        verify_ssl (bool): Indica se o certificado SSL deve ser verificado. Deve ser um valor booleano.
        verify_host (bool): Indica se o host deve ser verificado. Deve ser um valor booleano.
    Métodos:
        check_str_input(cls, value, info):
            Valida se os campos 'host', 'user' e 'password' são strings não vazias.
            Levanta ValueError caso o valor seja inválido.
        check_int_input(cls, value, info):
            Valida se os campos 'port', 'timeout' e 'tryouts' são inteiros positivos.
            Levanta ValueError caso o valor seja inválido.
        check_bool_input(cls, value, info):
            Valida se os campos 'tls', 'ssl', 'verify_ssl' e 'verify_host' são booleanos.
            Levanta ValueError caso o valor seja inválido.
    """
    host:str
    user:str
    password:str
    port:int
    tryouts:int
    timeout:int
    tls:bool
    ssl:bool
    verify_ssl:bool
    verify_host:bool

    @field_validator('host','user','password')
    def check_str_input(cls, value, info):
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"O parametro '{info.field_name}' deve ser uma string e não um {type(value)} e não vazio")
        return value
    
    @field_validator('port','timeout','tryouts')
    def check_int_input(cls, value, info):
        if not isinstance(value, int) or value <= 0:
            raise ValueError(f"O parametro '{info.field_name}' deve ser um inteiro positivo e não um {type(value)}")
        return value
    
    @field_validator('tls','ssl','verify_ssl','verify_host')
    def check_bool_input(cls, value, info):
        if not isinstance(value, bool):
            raise ValueError(f"O parametro '{info.field_name}' deve ser um booleano e não um {type(value)}")
        return value
    

class UploadDownloadValidator(BaseModel):
    """
    Classe UploadDownloadValidator
    Valida os parâmetros fornecidos para operações de upload e download via FTP.
    Atributos:
        filename (str): Nome do arquivo. Deve ser uma string não vazia.
        filepathftp (str): Caminho no FTP onde o arquivo está localizado ou será armazenado. Deve ser uma string não vazia.
        method (str): Método da operação, deve ser 'upload' ou 'download'.
    Métodos:
        check_str_input(cls, value, info):
            Valida se os campos 'filename' e 'filepathftp' são strings não vazias.
            Levanta ValueError se o valor não for uma string ou estiver vazio.
        check_method(cls, value):
            Valida se o campo 'method' é 'upload' ou 'download'.
            Levanta ValueError se o valor não for uma das opções válidas.
    """
    filename:str
    filepathftp:str
    method:str

    @field_validator('filename','filepathftp')
    def check_str_input(cls, value, info):
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"O parametro '{info.field_name}' deve ser uma string e não um {type(value)} e não vazio")
        return value
    
    @field_validator('method')
    def check_method(cls, value):
        if str(value).lower() not in ['upload', 'download']:
            raise ValueError(f"O parametro 'method' deve ser 'upload' ou 'download', mas foi recebido '{value}'")
        return value
    

class ListFilesValidator(BaseModel):
    """
    Classe ListFilesValidator
    Valida os parâmetros relacionados ao caminho de arquivos no FTP.
    Atributos:
        filepathftp (str): Representa o caminho do arquivo no FTP. Deve ser uma string não vazia.
    Métodos:
        check_str_input(cls, value, info):
            Valida se o valor fornecido para o campo 'filepathftp' é uma string não vazia.
            Levanta um ValueError caso o valor não seja uma string ou seja vazio.
    """
    filepathftp:str

    @field_validator('filepathftp')
    def check_str_input(cls, value, info):
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"O parametro '{info.field_name}' deve ser uma string e não um {type(value)} e não vazio")
        return value