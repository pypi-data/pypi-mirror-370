import base64
from slack_sdk import WebClient
from pydantic import BaseModel, ValidationError, field_validator
from typing import Union


class InitParamsValidator(BaseModel):
    """
    Classe para validar os parâmetros de inicialização.
    Atributos:
    - token_slack: Union[str, dict] - O token do Slack, que pode ser uma string ou um dicionário.
    - channel_id: str - O ID do canal do Slack.
    - on_base64: bool - Indica se o token do Slack está em base64.
    Métodos:
    - validate_token_slack(value, info): Valida o token do Slack.
    - validate_token_slack_dict(value, info): Valida o token do Slack quando é um dicionário.
    - validate_token_slack(value, info): Valida o valor de on_base64.
    """
        
    token_slack: Union[str, dict]
    channel_id:str
    on_base64:bool

    """
    Valida o token do Slack.
    Parâmetros:
    - value: str - O valor do token do Slack.
    - info: dict - Informações adicionais sobre o campo.
    Retorna:
    - str: O valor do token do Slack, se for válido.
    Lança:
    - ValueError: Se o valor não for uma string ou estiver vazio.
    """
    @field_validator('channel_id')
    def validate_str(cls, value, info):
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"O campo '{info.field_name}' deve ser strings e não {type(value)}")
        return value

    """
    Valida o token do Slack quando é um dicionário.
    Parâmetros:
    - value: dict - O valor do token do Slack.
    - info: dict - Informações adicionais sobre o campo.
    Retorna:
    - dict: O valor do token do Slack, se for válido.
    Lança:
    - ValueError: Se o valor não for um dicionário ou uma string vazia.
    """
    @field_validator('token_slack')
    def validate_dict(cls, value, info):
        if not isinstance(value, dict) and (not isinstance(value, str) or not value.strip()):
            raise ValueError(f"O campo '{info.field_name}' deve ser strings e não {type(value)}")
        return value
    
    """
    Valida o valor de on_base64.
    Parâmetros:
    - value: bool - O valor de on_base64.
    - info: dict - Informações adicionais sobre o campo.
    Retorna:
    - bool: O valor de on_base64, se for válido.
    Lança:
    - ValueError: Se o valor não for um booleano.
    """
    @field_validator('on_base64')
    def validate_bool(cls, value, info):
        if not isinstance(value, bool):
            raise ValueError(f"O campo '{info.field_name}' deve ser strings e não {type(value)}")
        return value


class SendSlackMessageParamsValidator(BaseModel):
    """
    Valida os parâmetros para enviar uma mensagem no Slack.
    Atributos:
    - message (str): A mensagem a ser enviada.
    - highlights (list): Uma lista de destaques.
    - files (list): Uma lista de arquivos.
    Métodos:
    - validate_message(value, info): Valida o campo 'message' para garantir que seja uma string não vazia.
    - validate_list(value, info): Valida os campos 'highlights' e 'files' para garantir que sejam listas.
    """

    message:str
    highlights:list
    file_list:list

    @field_validator('message')
    def validate_message(cls, value, info):
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"O campo '{info.field_name}' deve ser strings e não {type(value)}")
        return value
    
    @field_validator('highlights','file_list')
    def validate_list(cls, value, info):
        if not isinstance(value, list):
            raise ValueError(f"O campo '{info.field_name}' deve ser strings e não {type(value)}")
        return value


class Slack():


    def __init__(self, token_slack:Union[str, dict], channel_id, on_base64:bool=False):
        """
        Inicializa a classe Slack.
        Parâmetros:
        - token_slack (str): O token de autenticação do Slack.
        - base64 (bool, opcional): Indica se o token_slack está codificado em base64. O padrão é False.
        """
        
        self.token_slack = token_slack
        self.on_base64 = on_base64
        self.channel_id = channel_id

        try:
        
            InitParamsValidator(token_slack=token_slack, on_base64=on_base64,channel_id=channel_id)

        except ValidationError as e:
        
            raise ValueError("Erro na validação dos dados de input da inicialização da instância:", e.errors())

        if self.on_base64:

            self.token_slack = base64.b64decode(self.token_slack).decode('utf-8')

        self.client = WebClient(self.token_slack)


    def send_message(self, message:str, highlights:list=[] , file_list:list=[]):
        """
        Envia uma mensagem para o canal do Slack.
        Parâmetros:
        - message: str - A mensagem a ser enviada.
        - highlights: list - Uma lista de destaques (attachments) a serem exibidos junto com a mensagem.
        - files: list (opcional) - Uma lista de arquivos a serem anexados à mensagem.
        Retorna:
        Um dicionário com as seguintes chaves:
        - status: bool - Indica se o envio da mensagem foi bem-sucedido.
        - message: dict - A resposta da API do Slack contendo informações sobre a mensagem enviada.
        - success_attachments: list - Uma lista dos anexos que foram enviados com sucesso.
        - failed_success_attachments: list - Uma lista dos anexos que falharam ao serem enviados.
        Caso ocorra algum erro durante o envio da mensagem, o dicionário terá a seguinte estrutura:
        - status: bool - Indica se ocorreu um erro durante o envio da mensagem.
        - error: dict - A resposta da API do Slack contendo informações sobre o erro ocorrido.
        - success_attachments: list - Uma lista dos anexos que foram enviados com sucesso.
        - failed_attachments: list - Uma lista dos anexos que falharam ao serem enviados.
        """
        
        try:
        
            SendSlackMessageParamsValidator(message=message, highlights=highlights, file_list=file_list)

        except ValidationError as e:
        
            raise ValueError("Erro na validação dos dados de input da inicialização da instância:", e.errors())


        failed_attachments = []

        success_attachments = []

        result_message = self.client.chat_postMessage(
            channel=self.channel_id,
            text=message,
            blocks=[
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": message
                    }
                },
            ],
            attachments=highlights
        )

        if file_list is not None and len(file_list) > 0:

            # validar os arquivos anexados

            for file_item in file_list:

                if 'title' in file_item and 'file' in file_item:

                    if file_item['title'] is not None and len(str(file_item['title']).replace(" ","")) > 0 and file_item['file'] is not None and len(str(file_item['file']).replace(" ","")) > 0:

                        success_attachments.append(file_item)

                    else:

                        failed_attachments.append(file_item)

                else:

                    failed_attachments.append(file_item)

            if len(success_attachments) > 0:

                # Enviar mensagem com anexos

                result_message = self.client.files_upload_v2(
                    channel=self.channel_id,
                    initial_comment="anexos",
                    file_uploads=success_attachments
                )

        if result_message.get('ok', True):

            return {
                'status':True,
                'message':result_message,
                'success_attachments':success_attachments,
                'failed_success_attachments':failed_attachments
            }
        
        else:

            return {
                'status':False,
                'error':result_message,
                'success_attachments':success_attachments,
                'failed_attachments':failed_attachments
            }