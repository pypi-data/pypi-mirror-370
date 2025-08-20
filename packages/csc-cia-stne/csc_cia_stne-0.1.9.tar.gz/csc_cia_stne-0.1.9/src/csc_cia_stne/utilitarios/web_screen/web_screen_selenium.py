import time
import os

# Selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    WebDriverException,
    NoSuchElementException,
)
from selenium.webdriver.chrome.options import Options
from .web_screen_abstract import WebScreenAbstract


class WebScreenSelenium(WebScreenAbstract):
    """
    Classe que implementa a interface WebScreenAbstract usando Selenium.
    Métodos:
        configuracao_inicial():
            Configura o ambiente inicial para interações com a tela web usando Selenium.
        click_on_screen(target: str, timeout: int = 10):
            Clica em um elemento na tela web usando Selenium.
        input_value(target: str, value: str, clear: bool = True):
            Insere um valor em um campo de entrada na tela web usando Selenium.
        select_value(target: str, value: str):
            Seleciona um valor em um campo de seleção na tela web usando Selenium.
    """

    def __init__(
        self,
        headless: bool = True,
        disable_gpu: bool = True,
        no_sandbox: bool = True,
        timeout: int = 10,
        security: bool = False,
        scale: float = 0.8,
        download_path: str = "./tmp/",
    ):
        """
        Inicializa a classe responsável por configurar e gerenciar o WebDriver do Selenium.

        Args:
            headless (bool, opcional): Define se o navegador será executado em modo headless (sem interface gráfica).
                           Padrão é True.
            disable_gpu (bool, opcional): Define se a GPU será desativada durante a execução do navegador.
                          Padrão é True.
            no_sandbox (bool, opcional): Define se o navegador será executado sem o modo sandbox.
                         Padrão é True.
            timeout (int, opcional): Tempo limite (em segundos) para operações do WebDriver.
                         Padrão é 10.
            security (bool, opcional): Define se configurações adicionais de segurança serão aplicadas.
                           Padrão é False.
            scale (float, opcional): Define o fator de escala da interface do navegador.
                         Deve ser um número positivo. Padrão é 0.8.

        Raises:
            ValueError: Caso os parâmetros fornecidos sejam inválidos.
            ModuleNotFoundError: Caso o módulo Selenium não esteja instalado.
            WebDriverException: Caso ocorra um erro ao inicializar o WebDriver do Selenium.
            Exception: Para outros erros durante a inicialização da classe.
        """
        if not isinstance(scale, (int, float)) or scale <= 0:
            raise ValueError("O parâmetro 'scale' deve ser um número positivo.")
        if not isinstance(headless, bool):
            raise ValueError("O parâmetro 'headless' deve ser um booleano.")
        if not isinstance(disable_gpu, bool):
            raise ValueError("O parâmetro 'disable_gpu' deve ser um booleano.")
        if not isinstance(no_sandbox, bool):
            raise ValueError("O parâmetro 'no_sandbox' deve ser um booleano.")
        if not isinstance(timeout, int) or timeout <= 0:
            raise ValueError(
                "O parâmetro 'timeout' deve ser um número inteiro positivo."
            )
        if not isinstance(security, bool):
            raise ValueError("O parâmetro 'security' deve ser um booleano.")

        self.driver = None
        self.timeout = timeout
        self.security = security
        self.screenshot = []
        try:

            chrome_options = Options()

            if headless:
                chrome_options.add_argument("--headless")
            if disable_gpu:
                chrome_options.add_argument("--disable-gpu")
            if no_sandbox:
                chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-popup-blocking")
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument(f"--force-device-scale-factor={scale}")
            os.makedirs(download_path, exist_ok=True)
            chrome_options.add_experimental_option(
                "prefs",
                {
                    "download.default_directory": os.path.abspath(download_path),
                    "download.prompt_for_download": False,  # Não perguntar onde salvar
                    "directory_upgrade": True,
                    "safebrowsing.enabled": True,  # Para evitar bloqueios do Chrome
                },
            )

            chrome_options.add_argument(
                "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
            )

            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.maximize_window()
            self.driver.implicitly_wait(20)

        except ModuleNotFoundError:
            raise ModuleNotFoundError(
                "O módulo Selenium não está instalado. Por favor, instale-o usando 'pip install selenium'."
            )
        except WebDriverException:
            raise WebDriverException(
                "Erro ao inicializar o WebDriver do Selenium. Verifique se o ChromeDriver está instalado e configurado corretamente."
            )
        except Exception as e:
            raise Exception("Erro na inicialização da classe:", e)

    def select_one_element(
        self,
        target: str,
        time: int = 15,
        webdrive_type: str = "visibilidade_do_elemento",
    ):
        """
        Seleciona um único elemento na página da web com base no XPath fornecido.
        Args:
            target (str): O XPath do elemento a ser localizado.
            time (int, opcional): O tempo máximo (em segundos) para aguardar o elemento.
                O padrão é 15 segundos.
            webdrive_type (str, opcional): O tipo de condição de espera para localizar o elemento.
                Pode ser "elemento_clicavel" para aguardar que o elemento seja clicável ou
                "visibilidade_do_elemento" para aguardar que o elemento esteja visível.
                O padrão é "visibilidade_do_elemento".
        Returns:
            WebElement: O elemento localizado.
        Raises:
            TimeoutError: Se o tempo de espera for excedido e o elemento não for localizado.
            Exception: Para qualquer outro erro inesperado ao localizar o elemento.
        """
        webdrive_map = {
            "elemento_clicavel": EC.element_to_be_clickable,
            "visibilidade_do_elemento": EC.visibility_of_element_located,
        }
        try:
            element = WebDriverWait(self.driver, time).until(
                webdrive_map.get(webdrive_type, EC.visibility_of_element_located)(
                    (By.XPATH, target)
                )
            )
            return {"success": True, "element": element, "erro": None}
        except TimeoutException as e:
            return {"success": False, "element": None, "erro": e}
        except Exception as e:
            return {"success": False, "element": None, "erro": e}

    def select_elements(
        self,
        target: str,
        time: int = 15,
    ):
        """
        Seleciona múltiplos elementos na página utilizando um XPath.
        Args:
            target (str): O XPath dos elementos a serem localizados.
            time (int, opcional): O tempo máximo de espera (em segundos) para localizar os elementos.
                                  O padrão é 15 segundos.
        Returns:
            list: Uma lista de elementos Web encontrados pelo XPath.
        Raises:
            Exception: Lança uma exceção se ocorrer um erro ao buscar os elementos.
        """
        try:
            element = WebDriverWait(self.driver, time).until(
                lambda driver: driver.find_elements(By.XPATH, target)
            )
            return {"success": True, "elements": element, "erro": None}
        except Exception as e:
            return {"success": False, "elements": None, "erro": e}

    def close_tab(self):
        """
        Fecha a aba atual do navegador.

        Este método tenta fechar a aba ativa do navegador utilizando o driver Selenium.
        Caso ocorra algum erro durante o processo, uma exceção será levantada com uma
        mensagem descritiva.

        Raises:
            Exception: Caso ocorra um erro ao tentar fechar a aba, uma exceção será
            levantada contendo detalhes do erro.
        """
        try:
            self.driver.close()
            return {"success": True, "erro": None, "element": None}
        except Exception as e:
            return {"success": False, "erro": e, "element": None}

    def get_driver(self):
        """
        Retorna o driver da instância atual.

        Returns:
            WebDriver: O driver associado a esta instância.
        """
        return {"success": True, "erro": None, "driver": self.driver}

    def change_tab(self, tab_index: int):
        """
            Args:
                tab_index (int): Índice da aba para a qual mudar (0 para a primeira aba).

            Raises:
                IndexError: Se o índice fornecido não corresponder a uma aba existente.
                Exception: Para outros erros que possam ocorrer ao tentar mudar de aba.
        Altera para a aba especificada pelo índice.
        :param tab_index: Índice da aba para a qual mudar (0 para a primeira aba).
        """
        try:
            self.driver.switch_to.window(self.driver.window_handles[tab_index])
            return {"success": True, "erro": None, "element": None}
        except IndexError as e:
            return {"success": False, "erro": e, "element": None}
        except Exception as e:
            return {"success": False, "erro": e, "element": None}

    def execute_script(self, script: str, *args):
        """
        Executa um script JavaScript na aba atual.
        :param script: O script JavaScript a ser executado.
        """
        try:
            self.driver.execute_script(script, *args)
            return {"success": True, "erro": None, "element": None}
        except Exception as e:
            return {"success": False, "erro": e, "element": None}

    def scroll_until_element_found(
        self,
        target: str,
        max_scrolls: int = 20,
        scroll_pause_time: int = 1,
    ):
        """
        Rola a página até que um elemento seja encontrado ou o número máximo de rolagens seja atingido.

        Args:
            target (str): O XPath do elemento alvo que deve ser encontrado.
            max_scrolls (int, opcional): O número máximo de rolagens permitidas. Padrão é 20.
            scroll_pause_time (int, opcional): O tempo de pausa (em segundos) entre cada rolagem. Padrão é 1.

        Returns:
            WebElement: O elemento encontrado correspondente ao XPath fornecido.

        Raises:
            Exception: Se o elemento não for encontrado após o número máximo de rolagens.
        """
        for _ in range(max_scrolls):
            try:
                element = self.driver.find_element(By.XPATH, target)
                ActionChains(self.driver).move_to_element(element).perform()
                return {"success": True, "element": element, "erro": None}
            except NoSuchElementException:
                self.driver.execute_script("window.scrollBy(0, window.innerHeight);")
                time.sleep(scroll_pause_time)
        return {
            "success": False,
            "element": None,
            "erro": f"Elemento com o xpath '{target}' não encontrado após {max_scrolls} rolagens.",
        }

    def scroll_virtuallist_until_element_found(
        self,
        list_target: str,
        target: str,
        max_scrolls: int = 20,
        scroll_pause_time: int = 0.2,
    ):
        """
        Rola uma lista virtual até que um elemento específico seja encontrado.
        Este método tenta localizar um elemento em uma lista virtual rolando-a para baixo
        até que o elemento seja encontrado ou até que o número máximo de rolagens seja atingido.
        Args:
            list_target (str): O alvo da lista virtual que será rolada.
            target (str): O XPath do elemento que se deseja localizar.
            max_scrolls (int, opcional): O número máximo de rolagens permitidas. Padrão é 20.
            scroll_pause_time (int, opcional): O tempo de pausa (em segundos) entre as rolagens. Padrão é 0.2.
        Returns:
            WebElement: O elemento encontrado.
        Raises:
            Exception: Se o elemento não for encontrado após o número máximo de rolagens.
        """
        for _ in range(max_scrolls):
            try:
                element = self.driver.find_element(By.XPATH, target)
                return {"success": True, "element": element, "erro": None}
            except NoSuchElementException:
                for _ in range(10):
                    list_target.send_keys(Keys.ARROW_DOWN)
                    time.sleep(0.1)
                time.sleep(scroll_pause_time)
        return {
            "success": False,
            "erro": f"Elemento com o xpath '{target}' não encontrado após {max_scrolls} rolagens.",
            "element": None,
        }

    def refresh_page(self):
        """
        Atualiza a página atual no navegador.

        Este método tenta atualizar a página atual utilizando o método `refresh` do driver.
        Caso ocorra algum erro durante o processo, uma exceção será levantada com uma mensagem
        descritiva.

        Raises:
            Exception: Caso ocorra algum erro ao tentar atualizar a página, uma exceção será
            levantada contendo a mensagem de erro original.
        """
        try:
            self.driver.refresh()
            return {"success": True, "erro": None, "element": None}
        except Exception as e:
            return {"success": False, "erro": e, "element": None}

    def save_screenshot(self, screenshot_path: str):
        """
        Captura uma captura de tela da página atual.

        Este método tenta capturar uma captura de tela da página atual utilizando o método `screenshot` do driver.
        A captura de tela é salva em um arquivo temporário e o caminho do arquivo é retornado.

        Returns:
            str: O caminho do arquivo onde a captura de tela foi salva.

        Raises:
            Exception: Caso ocorra algum erro ao capturar a captura de tela, uma exceção será levantada.
        """
        if not screenshot_path or not isinstance(screenshot_path, str):
            return {
                "success": False,
                "erro": "O caminho para salvar a captura de tela deve ser uma string não vazia.",
                "diretorio": None,
            }
        try:
            screenshot_path = f"{screenshot_path}screenshot_{int(time.time())}.png"
            self.driver.save_screenshot(screenshot_path)
            return {"success": True, "erro": None, "diretorio": screenshot_path}
        except Exception as e:
            return {"success": False, "erro": e, "diretorio": None}
