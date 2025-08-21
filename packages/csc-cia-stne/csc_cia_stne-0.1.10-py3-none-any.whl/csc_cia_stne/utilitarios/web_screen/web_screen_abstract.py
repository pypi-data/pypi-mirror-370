from abc import ABC, abstractmethod


class WebScreenAbstract(ABC):
    """
    Classe abstrata que define a interface para interações com a tela web.
    Métodos Abstratos:
        configuracao_inicial():
            Configura o ambiente inicial para interações com a tela web.
        click_on_screen(target: str, timeout: int = 10):
            Clica em um elemento na tela web.
        input_value(target: str, value: str, clear: bool = True):
            Insere um valor em um campo de entrada na tela web.
        select_value(target: str, value: str):
            Seleciona um valor em um campo de seleção na tela web.
    """

    @abstractmethod
    def select_one_element(
        self,
        target: str,
        time: int = 15,
        webdrive_type: str = "visibilidade_do_elemento",
    ):
        """
        Seleciona um único elemento na página da web com base no alvo especificado.

        Args:
            target (str): O seletor ou identificador do elemento a ser selecionado.
            time (int, opcional): O tempo máximo (em segundos) para aguardar o elemento estar disponível.
                O padrão é 15 segundos.
            webdrive_type (str, opcional): O tipo de condição de espera para o elemento.
                Pode ser, por exemplo, "visibilidade_do_elemento". O padrão é "visibilidade_do_elemento".

        Raises:
            NotImplementedError: Indica que o método ainda não foi implementado.
        """
        raise NotImplementedError("Método 'select_element' ainda não implementado.")

    @abstractmethod
    def select_elements(
        self,
        target: str,
        time: int = 15,
    ):
        """
        Seleciona elementos na tela com base no alvo especificado.

        Args:
            target (str): O identificador do elemento ou grupo de elementos a serem selecionados.
            time (int, opcional): O tempo máximo, em segundos, para aguardar a seleção dos elementos.
                                  O padrão é 15 segundos.

        Raises:
            NotImplementedError: Exceção levantada indicando que o método ainda não foi implementado.
        """
        raise NotImplementedError("Método 'select_elements' ainda não implementado.")

    @abstractmethod
    def close_tab(self):
        """
        Fecha a aba atual do navegador.
        Este método deve ser implementado para fechar a aba ativa do navegador.
        """
        raise NotImplementedError("Método 'close_tab' ainda não implementado.")

    @abstractmethod
    def get_driver(self):
        """
        Retorna o driver da instância atual.
        Este método deve ser implementado para retornar a instância do driver web utilizado.
        """
        raise NotImplementedError("Método 'get_driver' ainda não implementado.")

    @abstractmethod
    def change_tab(self, tab_index: int):
        """
        Altera para a aba especificada pelo índice.
        Args:
            tab_index (int): Índice da aba para a qual mudar (0 para a primeira aba).
        Raises:
            NotImplementedError: Indica que o método ainda não foi implementado.
        """
        raise NotImplementedError("Método 'change_tab' ainda não implementado.")
