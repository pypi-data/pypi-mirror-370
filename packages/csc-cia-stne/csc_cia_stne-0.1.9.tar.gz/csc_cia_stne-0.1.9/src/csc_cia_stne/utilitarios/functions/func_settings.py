import yaml
import os
import sys


def get_config(file_path:str="settings.yaml",file_path_local:str=None,env:str='dev') -> dict:
    """
    Retorna as configurações carregadas a partir de um arquivo YAML.
    Parâmetros:
    - file_path (str): O caminho do arquivo YAML.
    - file_path_local (str, opcional): O caminho local do arquivo YAML, caso exista.
    - prod (str, opcional): Indica se as configurações de produção devem ser carregadas.
    Retorna:
    - dict: Um dicionário contendo as configurações carregadas do arquivo YAML.
    Lança:
    - FileNotFoundError: Caso o arquivo especificado não seja encontrado.
    - Exception: Caso ocorra algum erro ao carregar as configurações.
    Exemplo de uso:
    config = get_config('/path/to/config.yaml', prod=True)
    """

    # Essa validação serve apenas para que continue funcionando mesmo se for dentro de um executavel

    file_path = os.path.join(os.getcwd(), file_path)

    try:

        base_path = sys._MEIPASS

    except:

        base_path = os.path.abspath(".")

    if os.path.exists(file_path):

        file_place = os.path.join(base_path, file_path)

    elif file_path_local is not None:

        file_path_local = os.path.join(os.getcwd(), file_path_local)

        file_place = os.path.join(base_path, file_path_local)

    else:

        raise FileNotFoundError(f"Arquivo '{file_path}' não encontrado.")
    
    try:

        with open(file_place, 'r', encoding='utf-8') as f:

            config = yaml.safe_load(f)

        if env.lower() == "prod":
            try:
                
                config['env'] = config['prod']

            except:

                config['env'] = {}

        elif env.lower() == "qa":

            try:

                config['env'] = config['qa']

            except:

                config['env'] = {}
        
        else:

            try:

                config['env'] = config['dev']

            except:

                config['env'] = {}

        return config

    except Exception as e:

        raise(e)