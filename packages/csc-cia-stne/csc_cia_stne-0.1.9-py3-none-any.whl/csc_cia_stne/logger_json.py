import logging
from pythonjsonlogger import jsonlogger

def setup_json_logger(nome):
    
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
    logger.setLevel(logging.INFO)

    # Remove handlers anteriores, se houver
    if logger.hasHandlers():
        logger.handlers.clear()

    log_handler = logging.StreamHandler()
    formatter = jsonlogger.JsonFormatter(
        fmt='%(asctime)s %(levelname)s %(name)s %(message)s %(pathname)s %(lineno)d %(exc_info)s %(stack_info)s %(funcName)s %(module)s',
        json_ensure_ascii=False
    )
    log_handler.setFormatter(formatter)
    logger.addHandler(log_handler)

    # Capturando logs da biblioteca FastAPI/Uvicorn
    #uvicorn_logger = logging.getLogger("uvicorn")
    #uvicorn_logger.handlers = logger.handlers
    #uvicorn_logger.setLevel(logging.INFO)

    #uvicorn_error_logger = logging.getLogger("uvicorn.error")
    #uvicorn_error_logger.handlers = logger.handlers
    #uvicorn_error_logger.setLevel(logging.INFO)

    #uvicorn_access_logger = logging.getLogger("uvicorn.access")
    #uvicorn_access_logger.handlers = logger.handlers
    #uvicorn_access_logger.setLevel(logging.INFO)

    return logger

# Chama a função para configurar o logger
#logger = setup_json_logger()

def get_logger(nome):
    """
    logger = logging.getLogger("my_json_logger")
    if not logger.hasHandlers():  # Evita configurar múltiplas vezes
        handler = logging.StreamHandler()
        formatter = logging.Formatter(json.dumps({"level": "%(levelname)s", "message": "%(message)s"}))
        handler.setFormatter(formatter)
        logger.setLevel(logging.DEBUG)
        logger.addHandler(handler)
    """
    logger = setup_json_logger(nome)
    return logger