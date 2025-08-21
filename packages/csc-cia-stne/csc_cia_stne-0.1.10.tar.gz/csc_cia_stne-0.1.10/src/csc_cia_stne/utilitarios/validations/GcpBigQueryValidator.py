from pydantic import BaseModel, field_validator, model_validator

class InitParamsValidator(BaseModel):
    limit:int
    id_project:str
    creds_dict:dict
    creds_file:str

    @field_validator('limit')
    def check_input_basic(cls, value, info):
        if not isinstance(value, int):
            raise ValueError(f"O parametro 'limit' deve ser um inteiro e não um {type(value)}")
        
        return value

    @field_validator('id_project')
    def check_str_input(cls, value, info):
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"O parametro 'id_project' deve ser uma string e não um {type(value)} e não vazio")
        return value
    
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
        

class tryQueryValidator(BaseModel):

    query_to_execute:str
    organize:bool
    use_legacy:bool
    use_cache:bool
    query_parameters:list

    @field_validator('query_to_execute')
    def check_str_input(cls, value, info):
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"O parametro '{info.field_name}' deve ser uma string não vazia")
        
        return value
    
    @field_validator('organize','use_legacy','use_cache')
    def check_bool_input(cls, value, info):
        if not isinstance(value, bool):
            raise ValueError(f"O parametro '{info.field_name}' deve ser um boleano")
        
        return value
    
    @field_validator('query_parameters')
    def check_list_input(cls, value, info):
        if not isinstance(value, list):
            raise ValueError(f"O parametro '{info.field_name}' deve ser uma lista")
        
        return value


class tryInsertListValidator(BaseModel):
    """
    Classe de validação para o modelo tryInsertListValidator.
    Atributos:
    - insert_limit (int): Limite de inserção.
    - list_to_insert (list): Lista a ser inserida.
    - table (str): Nome da tabela.
    Métodos:
    - check_list_input(value, info): Valida se o valor fornecido para 'list_to_insert' é uma lista não vazia.
    - check_str_input(value, info): Valida se o valor fornecido para 'table' é uma string não vazia.
    - check_int_input(value, info): Valida se o valor fornecido para 'insert_limit' é um inteiro não maior que 10000.
    """
        
    insert_limit:int
    list_to_insert:list
    table:str

    """
    Valida se o valor fornecido para 'list_to_insert' é uma lista não vazia.
    Parâmetros:
    - value: O valor a ser validado.
    - info: Informações adicionais sobre o campo.
    Retorna:
    - O valor fornecido, se for uma lista não vazia.
    Lança:
    - ValueError: Se o valor não for uma lista ou estiver vazio.
    """
    @field_validator('list_to_insert')
    def check_list_input(cls, value, info):
        if not isinstance(value, list) and len(value) > 0:
            raise ValueError(f"O parametro '{info.field_name}' deve ser uma lista e não estar vazia")
        
        return value
    
    """
    Valida se o valor fornecido para 'table' é uma string não vazia.
    Parâmetros:
    - value: O valor a ser validado.
    - info: Informações adicionais sobre o campo.
    Retorna:
    - O valor fornecido, se for uma string não vazia.
    Lança:
    - ValueError: Se o valor não for uma string ou estiver vazio.
    """
    @field_validator('table')
    def check_str_input(cls, value, info):
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"O parametro '{info.field_name}' deve ser uma string não vazia")
        
        return value
    
    """
    Valida se o valor fornecido para 'insert_limit' é um inteiro não maior que 10000.
    Parâmetros:
    - value: O valor a ser validado.
    - info: Informações adicionais sobre o campo.
    Retorna:
    - O valor fornecido, se for um inteiro não maior que 10000.
    Lança:
    - ValueError: Se o valor não for um inteiro ou for maior que 10000.
    """
    @field_validator('insert_limit')
    def check_int_input(cls, value, info):
        if not isinstance(value, int) or value > 10000:
            raise ValueError(f"O parametro '{info.field_name}' deve ser um inteiro não maior que 10000")
        
        return value
