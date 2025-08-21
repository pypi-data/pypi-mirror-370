import os
from botcity.maestro import *
from typing import Optional

def get_secret(name: str, maestro: Optional[BotMaestroSDK] = None, activity_label: Optional[str] = None) -> str:
    """
    Obtém um segredo a partir de diferentes fontes, como variáveis de ambiente, arquivos locais ou o BotMaestroSDK.
    Args:
        name (str): O nome do segredo a ser recuperado.
        maestro (Optional[BotMaestroSDK]): Instância opcional do BotMaestroSDK para buscar o segredo.
        activity_label (Optional[str]): Rótulo opcional de atividade para buscar o segredo no BotMaestroSDK.
    Returns:
        str: O valor do segredo recuperado. Retorna `None` se o segredo não for encontrado.
    Comportamento:
    1. Primeiro tenta recuperar o segredo a partir de uma variável de ambiente.
    2. Caso não encontre, verifica em diferentes diretórios locais:
       - ./secrets
       - ./.secrets
       - ./private
       - ./.private
       - /secrets
    3. Se o segredo ainda não for encontrado, tenta buscar no BotMaestroSDK, utilizando o rótulo de atividade, se fornecido.
    Exceções:
    - Caso ocorra algum erro ao buscar o segredo no BotMaestroSDK, o segredo será definido como `None`.
    """
    # Tentando extrair da variavel de ambiente
    secret = os.getenv(name)
    
    # secret não encontrada em variavel de ambiente, tentando extrair do arquivo em /secret
    if secret is None:

        # verifica na pasta ./secrets
        if os.path.exists(f"./secrets/{name}"):

            with open(f"./secrets/{name}",'r', encoding="utf-8") as secret_file:
        
                secret = secret_file.read()

        # verifica na pasta ./.secrets
        elif os.path.exists(f"./.secrets/{name}"):

            with open(f"./.secrets/{name}",'r', encoding="utf-8") as secret_file:
        
                secret = secret_file.read()

        # verifica na pasta ./private
        elif os.path.exists(f"./private/{name}"):

            with open(f"./private/{name}",'r', encoding="utf-8") as secret_file:
        
                secret = secret_file.read()

        # verifica na pasta ./.private
        elif os.path.exists(f"./.private/{name}"):

            with open(f"./.private/{name}",'r', encoding="utf-8") as secret_file:
        
                secret = secret_file.read()

        # verifica na pasta /secrets
        elif os.path.exists(f"/secrets/{name}"):

            with open(f"/secrets/{name}",'r', encoding="utf-8") as secret_file:
        
                secret = secret_file.read()

        elif maestro and isinstance(maestro, BotMaestroSDK):
            try:
                if activity_label and isinstance(activity_label, str):
                    secret = maestro.get_credential(label=activity_label, key=name)
                else:
                    secret = maestro.get_credential(label=name, key=name)
            
            except Exception as e:
                secret = None

    return secret