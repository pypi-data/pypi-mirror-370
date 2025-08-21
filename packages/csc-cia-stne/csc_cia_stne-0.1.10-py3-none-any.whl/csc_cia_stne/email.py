import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from pydantic import BaseModel, ValidationError, field_validator

class InitParamsValidator(BaseModel):
    """
    Classe para validar os parâmetros de inicialização.
    Atributos:
    - email_sender (str): O endereço de e-mail do remetente.
    - email_password (str): A senha do e-mail.
    Métodos:
    - check_str_input(value, info): Valida se o valor é uma string não vazia.
    """
    email_sender: str
    email_password: str

    """
    Valida se o valor é uma string não vazia.
    Parâmetros:
    - value: O valor a ser validado.
    - info: Informações sobre o campo.
    Retorna:
    - value: O valor validado.
    Lança:
    - ValueError: Se o valor não for uma string ou estiver vazio.
    """
    @field_validator('email_sender','email_password')
    def check_str_input(cls, value, info):
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"O campo '{info.field_name}' deve ser strings e não {type(value)}")
        return value
    
class SendEmailParamsValidator(BaseModel):
    """
    Classe para validar os parâmetros de envio de e-mail.
    Atributos:
    - to (list): Lista de destinatários do e-mail.
    - message (str): Mensagem do e-mail.
    - title (str): Título do e-mail.
    - reply_to (str): Endereço de e-mail para resposta.
    - attachments (list, opcional): Lista de anexos do e-mail.
    - cc (list, opcional): Lista de destinatários em cópia do e-mail.
    - cco (list, opcional): Lista de destinatários em cópia oculta do e-mail.
    """

    to: list
    message: str
    title: str
    reply_to:str
    attachments: list = []
    cc: list = []
    cco: list = []

    """
    Valida se o valor é uma string não vazia.
    Parâmetros:
    - value (str): Valor a ser validado.
    - info (FieldInfo): Informações sobre o campo.
    Retorna:
    - str: O valor validado.
    Lança:
    - ValueError: Se o valor não for uma string ou estiver vazio.
    """
    @field_validator('message','title','reply_to')
    def check_str_input(cls, value, info):
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"O campo '{info.field_name}' deve ser strings e não {type(value)}")
        return value
    
    """
    Valida se o valor é uma lista.
    Parâmetros:
    - value (list): Valor a ser validado.
    - info (FieldInfo): Informações sobre o campo.
    Retorna:
    - list: O valor validado.
    Lança:
    - ValueError: Se o valor não for uma lista.
    """
    @field_validator('to','attachments','cc','cco')
    def check_list_input(cls, value, info):
        if not isinstance(value, list):
            raise ValueError(f"O parametro '{info.field_name}' deve ser uma lista")
        
        return value

class Email():

    def __init__(self, email_sender, email_password):
        """
        Inicializa uma instância da classe Email.
        Args:
            email_sender (str): O endereço de e-mail do remetente.
            email_password (str): A senha do e-mail do remetente.
        Raises:
            ValueError: Se houver um erro na validação dos dados de entrada da inicialização da instância.
        Returns:
            None
        """

        self.email_sender = email_sender
        self.email_password = email_password

        try:
        
            InitParamsValidator(email_sender=email_sender, email_password=email_password)

        except ValidationError as e:
        
            raise ValueError("Erro na validação dos dados de input da inicialização da instância:", e.errors())


        self.server = self.login_email()

        if not isinstance(self.server, smtplib.SMTP) and 'status' in self.server and not self.server['status']:

            raise ValueError("Erro na validação dos dados de input da inicialização da instância:", self.server['error'])


    def login_email(self):
        """
        Realiza o login no servidor de e-mail.
        Returns:
            smtplib.SMTP: Objeto que representa a conexão com o servidor de e-mail.
        Raises:
            dict: Dicionário contendo o status de erro caso ocorra uma exceção durante o login.
        Example:
            email_sender = 'seu_email@gmail.com'
            email_password = 'sua_senha'
            email = Email(email_sender, email_password)
            server = email.login_email()
        """

        try:

            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(self.email_sender, self.email_password)

            return server

        except Exception as e:

            return {
                'status':False,
                'error':str(e)
            }

    
    def send_email( self, to : list , message : str , title : str , reply_to: str, attachments : list = [] , cc : list = [] , cco : list = [], from_mask: str = "", block_by_attachments:bool=False) -> dict:
        """
        Envia um email com os parâmetros fornecidos.
        Args:
            to (list): Lista de destinatários do email.
            message (str): Corpo do email.
            title (str): Título do email.
            reply_to (str): Endereço de email para resposta.
            attachments (list, optional): Lista de caminhos dos arquivos anexos. Defaults to [].
            cc (list, optional): Lista de destinatários em cópia. Defaults to [].
            cco (list, optional): Lista de destinatários em cópia oculta. Defaults to [].
            from_mask (str, optional): Mascara para definir como se o envio estivesse vindo de outro email
        Returns:
            dict: Dicionário com o status do envio do email. Se o envio for bem-sucedido, o dicionário terá a chave 'status' com valor True. Caso contrário, terá a chave 'status' com valor False e a chave 'error' com a descrição do erro.
        Raises:
            ValueError: Se houver erro na validação dos dados para o envio do email.
        Example:
            email = EmailSender()
            to = ['example1@example.com', 'example2@example.com']
            message = 'Olá, isso é um teste de email.'
            title = 'Teste de Email'
            reply_to = 'noreply@example.com'
            attachments = ['/path/to/file1.txt', '/path/to/file2.txt']
            cc = ['cc1@example.com', 'cc2@example.com']
            cco = ['cco1@example.com', 'cco2@example.com']
            result = email.send_email(to, message, title, reply_to, attachments, cc, cco)
            print(result)
        """

        try:
        
            SendEmailParamsValidator(to=to, message=message, title=title, reply_to=reply_to, attachments=attachments, cc=cc, cco=cco)

        except ValidationError as e:
        
            raise ValueError("Erro na validação dos dados para o envio do email:", e.errors())

        try:

            msg = MIMEMultipart()

            if from_mask != "":
            
                msg["From"] = from_mask

            else:

                msg["From"] = self.email_sender
            
            msg["To"] = (",").join(to)
            
            msg["cc"] = (",").join(cc)
            
            msg['Reply-To'] = reply_to

            msg["Subject"] = title

            for file in attachments:

                try:

                    attachment = open(file, "rb")
                    
                    part = MIMEBase("application", "octet-stream")
                    
                    part.set_payload(attachment.read())
                    
                    encoders.encode_base64(part)
                    
                    part.add_header("Content-Disposition", f"attachment; filename={file.split('/')[-1]}")
                    
                    msg.attach(part)

                    attachment.close()

                except Exception as e:

                    if block_by_attachments:

                        return {
                            'status':False,
                            'error':str(e)
                        }

            msg.attach(MIMEText(message, 'html'))

            self.server.sendmail(self.email_sender, to + cc + cco, msg.as_string())

            return True

        except Exception as e:

            return {
                'status':False,
                'error':str(e)
            }