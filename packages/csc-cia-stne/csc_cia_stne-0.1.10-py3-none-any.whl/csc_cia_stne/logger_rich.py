import logging
import platform
from rich.logging import RichHandler
from rich.theme import Theme
from rich.console import Console
from rich.traceback import install
import re
import traceback
import os

def get_logger(nome):
    """
    Retorna um objeto logger configurado com base nas variáveis de ambiente.
    Returns:
        logging.Logger: Objeto logger configurado.
    Raises:
        ValueError: Se o valor da variável de ambiente 'log_level' não for 'DEBUG', 'INFO', 'WARNING', 'ERROR' ou 'CRITICAL'.
    """
    # Instala formatações de exception da biblioteca Rich
    install()

    # Definindo o nível de log baseado nas configurações
    if os.getenv('log_level') is None or os.getenv('log_level') == "DEBUG":
        
        log_config_level = logging.DEBUG

    elif os.getenv('log_level') == "INFO":

        log_config_level = logging.INFO
    
    elif os.getenv('log_level') == "WARNING" or os.getenv('log_level') == "WARN":
        
        log_config_level = logging.WARNING

    elif os.getenv('log_level') == "ERROR":

        log_config_level = logging.ERROR

    elif os.getenv('log_level') == "CRITICAL":

        log_config_level = logging.CRITICAL

    else:

        log_config_level = logging.INFO  # ou outro nível padrão
        raise ValueError("'log_level' precisa ser 'DEBUG,'INFO','WARNING','ERROR' ou 'CRITICAL'")

    # Definindo o tema customizado
    custom_theme = Theme({
        # python -m rich.color - cores
        # python -m rich.default_styles - item + cor padrão
        "logging.level.debug": "bold bright_cyan",
        "logging.level.info": "bold bright_white",
        "logging.level.warning": "bold orange1",
        "logging.level.error": "bold red blink",
        "logging.level.critical": "bold white on red blink",
        "logging.level.success": "bold bright_green",
        "log.time":"bold white",
        "log.message":"bold gray70",
        "repr.str":"dark_olive_green3",
        "inspect.value.border":"blue",
    })

    console = Console(theme=custom_theme)

    class CustomRichHandler(RichHandler):
        def __init__(self, *args, rich_tracebacks=True, show_time=True, show_level=True, show_path=True, console=console, omit_repeated_times=True, **kwargs):
            super().__init__(rich_tracebacks=rich_tracebacks, show_time=show_time, log_time_format="%d/%m/%Y %H:%M:%S", show_level=show_level, show_path=show_path, console=console, omit_repeated_times=omit_repeated_times, *args, **kwargs)
            self.show_time = show_time
            self.sistema_operacional = f"{platform.system()} {platform.release()}".upper()

        def emit(self, record):
            # Verifica se a variável global está definida e se o valor dela é 'SERVER'
            if "SERVER" in self.sistema_operacional:
                return  # Não faz nada, impedindo a exibição do log
            
            super().emit(record)  # Caso contrário, processa normalmente

        def format(self, record: logging.LogRecord) -> str:
            try:
                msg = f"| {record.getMessage()}"
                msg = msg.replace("\n", "\n| ")
                #msg = f"{record.getMessage()}"

                return(str(msg))
            except Exception as e:
                print("FALHA AO FORMATAR O LOG")
                print(e)

    def add_log_level(level_name, level_num, method_name=None):
        """
        Adiciona um log level

        Parâmetros:
            level_name (str): Nome do level
            level_num (int): Número do level
        """
        if not method_name:
        
            method_name = level_name.lower()

        if hasattr(logging, level_name):
        
            raise AttributeError('{} already defined in logging module'.format(level_name))
        
        if hasattr(logging, method_name):
        
            raise AttributeError('{} already defined in logging module'.format(method_name))
        
        if hasattr(logging.getLoggerClass(), method_name):
        
            raise AttributeError('{} already defined in logger class'.format(method_name))

        def log_for_level(self, message, *args, **kwargs):
            
            if self.isEnabledFor(level_num):

                #self._log(level_num, message, args, **kwargs)
                self._log(level_num, message, args, **{**kwargs, "stacklevel": 2})
                
        def log_to_root(message, *args, **kwargs):
            
            logging.log(level_num, message, *args, **kwargs)

        logging.addLevelName(level_num, level_name)
        setattr(logging, level_name, level_num)
        setattr(logging.getLoggerClass(), method_name, log_for_level)
        setattr(logging, method_name, log_to_root)

    if not 'SUCCESS' in logging._nameToLevel:
        add_log_level("SUCCESS",21)

    logger = logging.getLogger(nome)

    # Sendo setado aqui pois no basicConfig estava gerando logs para as libs do slack_sdk e big query

    # Adiciona o CustomRichHandler se ainda não estiver presente
    if not any(isinstance(handler, CustomRichHandler) for handler in logger.handlers):
        logger.addHandler(CustomRichHandler())

    logger.setLevel(log_config_level)

    return logger