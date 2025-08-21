from pydantic import BaseModel, field_validator, model_validator

class InitParamsValidator(BaseModel):

    headers: dict
    url: str

    @field_validator('headers')
    def check_input_dict(cls, value, info):
        if not isinstance(value, dict):
            raise ValueError(f"O parametro 'headers' deve ser um dicionário e não um {type(value)}")
        return value
    
    @field_validator('url')
    def check_str_input(cls, value, info):
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"O parametro 'url' deve ser uma string e não um {type(value)} e não vazio")
        return value
    
class CreateUserValidator(BaseModel):

    cpf: str
    name: str
    email: str
    empresa: str
    rg: str

    @field_validator('cpf','name','email','empresa')
    def check_str_input(cls, value, info):
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"O parametro '{info.field_name}' deve ser uma string e não um {type(value)} e não vazio")
        return value

    @field_validator('rg')
    def check_rg_input(cls, value, info):
        if not isinstance(value, str) or value is not None:
            raise ValueError(f"O parametro 'rg' deve ser uma string e não um {type(value)}")
        return value
    
class ValidateExistenceValidator(BaseModel):

    cpf: str

    @field_validator('cpf')
    def check_str_input(cls, value, info):
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"O parametro 'cpf' deve ser uma string e não um {type(value)} e não vazio")
        return value
    
class CreateWaccessValidator(BaseModel):

    name:str
    cpf:str
    empresa:str
    email:str
    rg:str

    @field_validator('cpf','name','email')
    def check_str_input(cls, value, info):
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"O parametro '{info.field_name}' deve ser uma string e não um {type(value)} e não vazio")
        return value
    
    @field_validator('empresa', 'rg')
    def check_rg_input(cls, value, info):
        if not isinstance(value, str) or value is not None:
            raise ValueError(f"O parametro '{info.field_name}' deve ser uma string e não um {type(value)}")
        return value
    
class UpdateWaccessValidator(BaseModel):

    name:str
    cpf:str
    empresa:str
    email:str
    rg:str
    foto:str
    status:int

    @field_validator('cpf','name','email')
    def check_str_input(cls, value, info):
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"O parametro '{info.field_name}' deve ser uma string e não um {type(value)} e não vazio")
        return value
    
    @field_validator('status')
    def check_status_input(cls, value, info):
        if not isinstance(value, int) or value not in [0, 1]:
            raise ValueError(f"O parametro '{info.field_name}' deve ser um inteiro e não um {type(value)} e deve ser 0 ou 1")
        return value
    
    @field_validator('empresa', 'rg','foto')
    def check_str_none_input(cls, value, info):
        if not isinstance(value, str) or value is not None:
            raise ValueError(f"O parametro '{info.field_name}' deve ser uma string e não um {type(value)}")
        return value
    
class UpdateUserValidator(BaseModel):

    name:str
    cpf:str
    empresa:str
    email:str
    rg:str
    status:int

    @field_validator('cpf','name','email')
    def check_str_input(cls, value, info):
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"O parametro '{info.field_name}' deve ser uma string e não um {type(value)} e não vazio")
        return value
    
    @field_validator('status')
    def check_status_input(cls, value, info):
        if not isinstance(value, int) or value not in [0, 1]:
            raise ValueError(f"O parametro '{info.field_name}' deve ser um inteiro e não um {type(value)} e deve ser 0 ou 1")
        return value
    

    @field_validator('empresa', 'rg')
    def check_rg_input(cls, value, info):
        if not isinstance(value, str) or value is not None:
            raise ValueError(f"O parametro '{info.field_name}' deve ser uma string e não um {type(value)}")
        return value
    
class AddPhotoValidator(BaseModel):

    foto:str
    chid:str

    @field_validator('foto','chid')
    def check_str_input(cls, value, info):
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"O parametro '{info.field_name}' deve ser uma string e não um {type(value)} e não vazio")
        return value
    
class ChangeGroupsUserValidator(BaseModel):

    groups_list: list[dict]
    cpf: str

    @field_validator('groups_list')
    def check_list_input(cls, value, info):
        if not isinstance(value, list):
            raise ValueError(f"O parametro '{info.field_name}' deve ser uma lista de dicts e não um {type(value)}")
        return value
    
    @field_validator('cpf')
    def check_str_input(cls, value, info):
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"O parametro '{info.field_name}' deve ser uma string e não um {type(value)} e não vazio")
        return value
    
class AddCardUserValidator(BaseModel):

    card: str
    cpf: str

    @field_validator('card','cpf')
    def check_str_input(cls, value, info):
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"O parametro '{info.field_name}' deve ser uma string e não um {type(value)} e não vazio")
        return value
    
class GetUserCardsValidator(BaseModel):

    chid: str

    @field_validator('chid')
    def check_str_input(cls, value, info):
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"O parametro '{info.field_name}' deve ser uma string e não um {type(value)} e não vazio")
        return value
    
class CreateCardValidator(BaseModel):

    card: str

    @field_validator('card')
    def check_str_input(cls, value, info):
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"O parametro '{info.field_name}' deve ser uma string e não um {type(value)} e não vazio")
        return value
    
class AssociateCardUserValidator(BaseModel):

    card: str
    chid: str

    @field_validator('card','chid')
    def check_str_input(cls, value, info):
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"O parametro '{info.field_name}' deve ser uma string e não um {type(value)} e não vazio")
        return value
    
class TurnOffUserValidator(BaseModel):

    cpf: str

    @field_validator('cpf')
    def check_str_input(cls, value, info):
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"O parametro '{info.field_name}' deve ser uma string e não um {type(value)} e não vazio")
        return value
    
class RemoveGroupsValidator(BaseModel):

    chid: str
    cpf: str

    @field_validator('cpf','chid')
    def check_str_input(cls, value, info):
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"O parametro '{info.field_name}' deve ser uma string e não um {type(value)} e não vazio")
        return value