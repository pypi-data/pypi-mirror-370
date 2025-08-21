import os
import shutil

def recriar_pasta(caminho_pasta):
    """
    Remove a pasta existente, se houver, e cria uma nova pasta no caminho especificado.
    Args:
        caminho_pasta (str): O caminho da pasta a ser recriada.
    Returns:
        tuple: Uma tupla contendo um valor booleano indicando se a operação foi bem-sucedida e uma mensagem de erro em caso de falha.
    Examples:
        >>> recriar_pasta('/caminho/para/pasta')
        (True, None)
    """

    try:

        # Se a pasta já existir, remove-a
        if os.path.exists(caminho_pasta) and os.path.isdir(caminho_pasta):
            shutil.rmtree(caminho_pasta)  # Deleta a pasta e todo o conteúdo

        # Cria a pasta novamente
        os.makedirs(caminho_pasta)
        return True, None

    except Exception as e:

        return False, e

