# Validador
from pydantic import ValidationError

# Validadores de parametros
from .utilitarios.validations.web_validator import InitParamsValidator
from .utilitarios.web_screen import WebScreenSelenium, WebScreenBotCity


class web_screen:

    def __init__(
        self,
        model: str = "selenium",
        timeout: int = 60,
        headless: bool = True,
        disable_gpu: bool = True,
        no_sandbox: bool = True,
        security: bool = True,
        download_path: str = "./tmp/",
    ):
        """
        Inicializa a instância da classe Web.
        Parâmetros:
        - model (str): O modelo a ser utilizado, pode ser "selenium" ou outro modelo suportado.
        - timeout (int): O tempo limite em segundos para aguardar a resposta do navegador.
        - headless (bool): Define se o navegador será executado em modo headless (sem interface gráfica).
        - disable_gpu (bool): Define se a aceleração de hardware do GPU será desabilitada.
        - no_sandbox (bool): Define se o sandbox do navegador será desabilitado.
        - security (bool): Define se a segurança do navegador será habilitada.
        Raises:
        - ValueError: Se ocorrer um erro na validação dos dados de entrada da inicialização da instância.
        """

        self.model = model
        self.timeout = timeout
        self.security = security
        self.driver = None
        try:

            InitParamsValidator(
                model=model,
                timeout=timeout,
                headless=headless,
                disable_gpu=disable_gpu,
                no_sandbox=no_sandbox,
                security=security,
            )

        except ValidationError as e:

            raise ValueError(
                "Erro na validação dos dados de input da inicialização da instância:",
                e.errors(),
            )

        self.instancia = (
            WebScreenSelenium(
                headless=headless,
                disable_gpu=disable_gpu,
                no_sandbox=no_sandbox,
                timeout=timeout,
                security=security,
                download_path=download_path,
            )
            if model.upper() == "SELENIUM"
            else WebScreenBotCity(
                headless=headless,
                disable_gpu=disable_gpu,
                no_sandbox=no_sandbox,
                timeout=timeout,
                security=security,
                download_path=download_path,
            )
        )
