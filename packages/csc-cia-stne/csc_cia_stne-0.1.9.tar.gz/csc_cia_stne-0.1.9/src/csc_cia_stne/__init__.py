import os
from dotenv import load_dotenv
from .logger_json import get_logger as get_logger_json
from .logger_rich import get_logger as get_logger_rich
from .karavela import Karavela
from .servicenow import ServiceNow
from .stne_admin import StoneAdmin
from .bc_sta import BC_STA
from .bc_correios import BC_Correios
from .gcp_bigquery import BigQuery
from .email import Email
from .provio import Provio
from .google_drive import GoogleDrive
from .slack import Slack
from .web import web_screen
from .wacess import Waccess
from .gcp_bucket import GCPBucket
from .ftp import FTP

# Define os itens disponíveis para importação
__all__ = [
    "Karavela",
    "BigQuery",
    "BC_Correios",
    "BC_STA",
    "StoneAdmin",
    "ServiceNow",
    "Util",
    "logger",
    "Provio",
    "Email", 
    "GoogleDrive",
    "Slack",
    "web_screen",
    "Waccess",
    "GCPBucket",
    "FTP"
]

_diretorio_inicial = os.getcwd()
_caminho_env = os.path.join(_diretorio_inicial, ".env")

# Carrega .env
load_dotenv(_caminho_env)
logger = None  # Inicializa como None

def _running_in_container():
    """
    Verifica se o código está sendo executado dentro de um container.
    Retorna True se estiver sendo executado dentro de um container e False caso contrário.
    """

    if os.environ.get("KUBERNETES_SERVICE_HOST") or os.path.exists("/.dockerenv"):
        
        return True
    
    try:
    
        with open("/proc/1/cgroup", "rt") as file:
    
            for line in file:
    
                if "docker" in line or "kubepods" in line:
    
                    return True
    
    except FileNotFoundError as e:
    
        return False
    
    return False
    
def logger(nome:str='__main__'):
    """
    Retorna um objeto logger com base no ambiente de execução.
    Se a variável de ambiente 'ambiente_de_execucao' estiver definida e for igual a "karavela",
    retorna um logger formatado em JSON usando a função get_logger_json().
    Caso contrário, se estiver executando em um container, retorna um logger formatado em JSON
    usando a função get_logger_json().
    Caso contrário, retorna um logger formatado em texto usando a função get_logger_rich().
    Exemplo de uso:
    logger_obj = logger()
    logger_obj.info("Mensagem de informação")
    logger_obj.error("Mensagem de erro")
    """
    
    if os.getenv('ambiente_de_execucao') is not None and os.getenv('ambiente_de_execucao') == "karavela":
        
        return get_logger_json(nome)
    
    elif _running_in_container():
        
        return get_logger_json(nome)
    
    else:
        
        return get_logger_rich(nome)
