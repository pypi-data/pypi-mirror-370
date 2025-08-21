from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import (
    TimeoutException,
    WebDriverException,
    NoSuchElementException,
)

# Botcity
from botcity.web import WebBot, Browser
from botcity.web.util import element_as_select
from .web_screen_abstract import WebScreenAbstract


class WebScreenBotCity(WebScreenAbstract):
    """
    Classe que implementa a interface WebScreenAbstract usando BotCity.
    Métodos:
        configuracao_inicial():
            Configura o ambiente inicial para interações com a tela web usando BotCity.
        click_on_screen(target: str, timeout: int = 10):
            Clica em um elemento na tela web usando BotCity.
        input_value(target: str, value: str, clear: bool = True):
            Insere um valor em um campo de entrada na tela web usando BotCity.
        select_value(target: str, value: str):
            Seleciona um valor em um campo de seleção na tela web usando BotCity.
    """

    def __init__(
        self,
        headless: bool = True,
        disable_gpu: bool = True,
        no_sandbox: bool = True,
        timeout: int = 10,
        security: bool = False,
        download_path: str = "./tmp/",
    ):
        """
        Inicializa a classe com as configurações para o WebBot.
        Args:
            headless (bool): Define se o navegador será executado em modo headless (sem interface gráfica).
                             Padrão é True.
            disable_gpu (bool): Define se o uso de GPU será desativado no navegador. Padrão é True.
            no_sandbox (bool): Define se o navegador será executado sem o modo sandbox. Padrão é True.
            timeout (int): Tempo limite (em segundos) para operações realizadas pelo WebBot. Padrão é 10.
            security (bool): Define se configurações de segurança adicionais serão aplicadas. Padrão é False.
        Raises:
            ValueError: Caso ocorra algum erro durante a inicialização da classe.
        """
        self.web_bot = None
        self.timeout = timeout
        self.security = security
        self.screenshot = []
        try:

            # Criação do drive para botcity

            self.web_bot = WebBot()

            # Configurar o navegador (por exemplo, Chrome)
            self.web_bot.browser = Browser.CHROME

            self.web_bot.driver_path = ChromeDriverManager().install()

            # Configurar as opções do Chrome
            self.web_bot.headless = headless
            self.web_bot.disable_gpu = disable_gpu
            self.web_bot.no_sandbox = no_sandbox
            self.web_bot.download_folder_path = download_path

        except Exception as e:
            raise ValueError("Erro na inicialização da classe:", e)

    def select_one_element(self, target):
        """
        Clica em um elemento na tela identificado pelo seletor fornecido.
        Args:
            target (str): O seletor XPATH do elemento a ser clicado.
            timeout (int, opcional): O tempo máximo (em segundos) para aguardar
                que o elemento esteja disponível e não esteja obsoleto.
                O padrão é 10 segundos.
        Returns:
            dict: Um dicionário contendo:
                - "success" (bool): Indica se a operação foi bem-sucedida.
                - "error" (Exception ou None): A exceção capturada em caso de falha,
                  ou None se não houver erro.
                - "details" (None): Reservado para informações adicionais,
                  atualmente sempre retorna None.
        Raises:
            Exception: Qualquer exceção capturada durante a execução será retornada
            no campo "error" do dicionário de retorno.
        """
        try:
            element_click = self.web_bot.find_element(target, By.XPATH)
            self.web_bot.wait_for_stale_element(
                element=element_click, timeout=self.timeout
            )
            return {"success": True, "error": None, "element": element_click}
        except NoSuchElementException:
            return {
                "success": False,
                "error": f"Elemento com o seletor '{target}' não encontrado.",
            }
        except TimeoutException:
            return {
                "success": False,
                "error": f"Tempo limite excedido ao tentar localizar o elemento com o seletor '{target}'.",
            }
        except Exception as e:
            return {"success": False, "error": e}

    def close_tab(self):
        try:
            """
            Fecha a aba atual do navegador.
            Este método tenta fechar a aba ativa do navegador utilizando o método `close_tab` do WebBot.
            Caso ocorra algum erro durante o processo, uma exceção será levantada com uma mensagem descritiva.
            """
            self.web_bot.close_page()
            return {"success": True, "error": None}
        except WebDriverException as e:
            return {"success": False, "error": f"Erro ao fechar a aba: {e}"}
        except TimeoutException:
            return {
                "success": False,
                "error": "Tempo limite excedido ao tentar fechar a aba.",
            }
        except Exception as e:
            return {"success": False, "error": f"Erro ao fechar a aba: {e}"}

    def select_elements(self, target):
        """
        Clica em um elemento na tela identificado pelo seletor fornecido.
        Args:
            target (str): O seletor XPATH do elemento a ser clicado.
            timeout (int, opcional): O tempo máximo (em segundos) para aguardar
                que o elemento esteja disponível e não esteja obsoleto.
                O padrão é 10 segundos.
        Returns:
            dict: Um dicionário contendo:
                - "success" (bool): Indica se a operação foi bem-sucedida.
                - "error" (Exception ou None): A exceção capturada em caso de falha,
                  ou None se não houver erro.
                - "details" (None): Reservado para informações adicionais,
                  atualmente sempre retorna None.
        Raises:
            Exception: Qualquer exceção capturada durante a execução será retornada
            no campo "error" do dicionário de retorno.
        """
        try:
            element_click = self.web_bot.find_elements(target, By.XPATH)
            self.web_bot.wait_for_stale_element(
                element=element_click, timeout=self.timeout
            )
            return {"success": True, "error": None, "element": element_click}
        except NoSuchElementException:
            return {
                "success": False,
                "error": f"Elemento com o seletor '{target}' não encontrado.",
            }
        except TimeoutException:
            return {
                "success": False,
                "error": f"Tempo limite excedido ao tentar localizar o elemento com o seletor '{target}'.",
            }
        except Exception as e:
            return {"success": False, "error": e}

    def input_value(self, target: str, value: str, clear: bool = True):
        """
        Insere um valor em um elemento da página web identificado pelo seletor XPath.

        Args:
            target (str): O seletor XPath do elemento onde o valor será inserido.
            value (str): O valor a ser inserido no elemento.
            clear (bool, opcional): Indica se o campo deve ser limpo antes de inserir o valor.
                                    O padrão é True.

        Returns:
            dict: Um dicionário contendo:
                - "success" (bool): Indica se a operação foi bem-sucedida.
                - "details" (None): Reservado para informações adicionais (atualmente não utilizado).
                - "error" (str ou Exception): Mensagem de erro ou exceção, caso ocorra.

        Exceções Tratadas:
            - NoSuchElementException: Lançada quando o elemento não é encontrado.
            - TimeoutException: Lançada quando o tempo limite para localizar o elemento é excedido.
            - Exception: Captura qualquer outra exceção que possa ocorrer.

        """
        try:
            element_input = self.web_bot.find_element(target, By.XPATH)
            self.web_bot.wait_for_stale_element(
                element=element_input, timeout=self.timeout
            )
            if clear:
                element_input.clear()
            element_input.send_keys(value)
            return {"success": True, "error": None}
        except NoSuchElementException:
            return {
                "success": False,
                "details": None,
                "error": f"Elemento com o seletor '{target}' não encontrado.",
            }
        except TimeoutException:
            return {
                "success": False,
                "details": None,
                "error": f"Tempo limite excedido ao tentar localizar o elemento com o seletor '{target}'.",
            }
        except Exception as e:
            return {"success": False, "details": None, "error": e}

    def select_value(self, target: str, value: str):
        """
        Seleciona um valor em um elemento do tipo <select> na página da web.

        Args:
            target (str): O seletor XPath do elemento <select> que será manipulado.
            value (str): O valor que será selecionado no elemento <select>.

        Returns:
            dict: Um dicionário contendo:
                - "success" (bool): Indica se a operação foi bem-sucedida.
                - "details" (None): Reservado para informações adicionais (atualmente não utilizado).
                - "error" (str ou Exception): Mensagem de erro em caso de falha ou a exceção capturada.

        Exceções Tratadas:
            - NoSuchElementException: Lançada quando o elemento com o seletor especificado não é encontrado.
            - TimeoutException: Lançada quando o tempo limite para localizar o elemento é excedido.
            - Exception: Captura qualquer outra exceção inesperada.

        Observação:
            Certifique-se de que o elemento identificado pelo seletor seja um elemento <select> válido.
        """
        try:
            element_select = self.web_bot.find_element(target, By.XPATH)
            self.web_bot.wait_for_stale_element(
                element=element_select, timeout=self.timeout
            )
            element_select = element_as_select(element_select)
            element_select.select_by_value(value)
            return {"success": True, "error": None}
        except NoSuchElementException:
            return {
                "success": False,
                "details": None,
                "error": f"Elemento com o seletor '{target}' não encontrado.",
            }
        except TimeoutException:
            return {
                "success": False,
                "details": None,
                "error": f"Tempo limite excedido ao tentar localizar o elemento com o seletor '{target}'.",
            }
        except Exception as e:
            return {"success": False, "details": None, "error": e}

    def get_driver(self):
        """
        Retorna a instância do driver web associada ao bot.

        Returns:
            WebDriver: A instância do driver web utilizada pelo bot.
        """
        return self.web_bot

    def change_tab(self, tab_index: int):
        try:
            """
            Altera para a aba especificada pelo índice.
            Args:
                tab_index (int): Índice da aba para a qual mudar (0 para a primeira aba).
            Raises:
                IndexError: Se o índice fornecido não corresponder a uma aba existente.
                Exception: Para outros erros que possam ocorrer ao tentar mudar de aba.
            """
            self.web_bot.activate_tab(tab_index)
            return {"success": True, "error": None}
        except IndexError:
            return {
                "success": False,
                "error": f"A aba com índice {tab_index} não existe.",
            }
        except Exception as e:
            return {"success": False, "error": f"Erro ao mudar de aba: {e}"}
