from pydantic import BaseModel, field_validator, model_validator

class InitParamsValidator(BaseModel):
    """
    Classe InitParamsValidator
    Valida os parâmetros de inicialização para garantir que pelo menos um dos 
    parâmetros 'creds_dict' ou 'creds_file' seja fornecido.
    Atributos:
        creds_dict (dict): Um dicionário contendo as credenciais.
        creds_file (str): Um caminho para o arquivo contendo as credenciais.
    Métodos:
        check_others_input(cls, model):
            Valida se pelo menos um dos parâmetros 'creds_dict' ou 'creds_file' 
            foi fornecido. Levanta um ValueError caso ambos estejam ausentes ou 
            inválidos.
    """

    creds_dict:dict
    creds_file:str

    @model_validator(mode="after")
    def check_others_input(cls, model):
        creds_dict = model.creds_dict
        creds_file = model.creds_file

        if isinstance(creds_dict, dict):
            return model

        elif isinstance(creds_file, str) and creds_file.strip():
            return model

        else:
            raise ValueError("Pelo menos um dos parâmetros 'creds_dict' ou 'creds_file' deve ser fornecido.")
        
class ListFilesValidator(BaseModel):
    """
    Classe ListFilesValidator
    Valida os dados relacionados ao nome de um bucket no Google Cloud Platform (GCP).
    Atributos:
        bucket_name (str): Nome do bucket que será validado. Deve ser uma string não vazia.
    Métodos:
        check_str_name(cls, value, info):
            Valida se o valor fornecido para o nome do bucket é uma string não vazia.
            Levanta um ValueError se a validação falhar.
    """

    bucket_name:str

    @field_validator("bucket_name")
    def check_str_name(cls, value, info):
        if not isinstance(value, str) or not value.strip():
            raise ValueError("O nome do bucket deve ser uma string não vazia.")
        return value
    
class GetFilesValidator(BaseModel):
    """
    Classe GetFilesValidator
    Valida os parâmetros necessários para operações relacionadas a arquivos em um bucket GCP.
    Atributos:
        bucket_name (str): Nome do bucket GCP. Deve ser uma string não vazia.
        filename (str): Nome do arquivo. Deve ser uma string não vazia.
        destination (str): Caminho de destino. Deve ser uma string.
        chunksize (int): Tamanho dos chunks para processamento. Deve ser um inteiro.
    Métodos:
        check_str_name(cls, value, info):
            Valida se os campos 'bucket_name' e 'filename' são strings não vazias.
            Lança ValueError se a validação falhar.
        check_destination(cls, value, info):
            Valida se o campo 'destination' é uma string.
            Lança ValueError se a validação falhar.
        check_chunksize(cls, value, info):
            Valida se o campo 'chunksize' é um inteiro.
            Lança ValueError se a validação falhar.
    """

    bucket_name:str
    filename:str
    destination:str
    chunksize:int

    @field_validator("bucket_name","filename")
    def check_str_name(cls, value, info):
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"O parametro '{info.field_name}' deve ser uma string e não um {type(value)} e não vazio")
        return value
    
    @field_validator("destination")
    def check_destination(cls, value, info):
        if not isinstance(value, str) or value is not None:
            raise ValueError(f"O parametro '{info.field_name}' deve ser uma string e não um {type(value)}")
        return value
    
    @field_validator("chunksize")
    def check_chunksize(cls, value, info):
        if not isinstance(value, int):
            raise ValueError(f"O parametro '{info.field_name}' deve ser um inteiro e não um {type(value)}")
        return value
    
class UploadFilesValidator(BaseModel):
    """
    Classe UploadFilesValidator
    Valida os parâmetros necessários para o upload de arquivos em um bucket GCP.
    Atributos:
        bucket_name (str): Nome do bucket onde o arquivo será armazenado.
        filename (str): Nome do arquivo a ser enviado.
        destination (str): Caminho de destino dentro do bucket.
    Métodos:
        check_str_name(cls, value, info):
            Valida se os campos 'bucket_name' e 'filename' são strings não vazias.
            Levanta um ValueError caso a validação falhe.
        check_destination(cls, value, info):
            Valida se o campo 'destination' é uma string.
            Levanta um ValueError caso a validação falhe.
    """

    bucket_name:str
    filename:str
    destination:str

    @field_validator("bucket_name","filename")
    def check_str_name(cls, value, info):
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"O parametro '{info.field_name}' deve ser uma string e não um {type(value)} e não vazio")
        return value
    
    @field_validator("destination")
    def check_destination(cls, value, info):
        if not isinstance(value, str) or value is not None:
            raise ValueError(f"O parametro '{info.field_name}' deve ser uma string e não um {type(value)}")
        return value
    
class DeleteFilesValidator(BaseModel):
    """
    Classe DeleteFilesValidator
    Valida os parâmetros necessários para a exclusão de arquivos em um bucket GCP.
    Atributos:
        bucket_name (str): Nome do bucket onde os arquivos estão armazenados.
        filename (str): Nome do arquivo a ser excluído.
    Métodos:
        check_str_name(cls, value, info):
            Valida se os valores fornecidos para os campos 'bucket_name' e 'filename' 
            são strings não vazias. Levanta um ValueError caso a validação falhe.
    """

    bucket_name:str
    filename:str

    @field_validator("bucket_name","filename")
    def check_str_name(cls, value, info):
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"O parametro '{info.field_name}' deve ser uma string e não um {type(value)} e não vazio")
        return value