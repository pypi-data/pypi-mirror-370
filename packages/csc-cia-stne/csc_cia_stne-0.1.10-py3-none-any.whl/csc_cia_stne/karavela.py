import os
from botcity.maestro import *
from typing import Optional


class Karavela():

    def __init__(self)->None:
        """Inicia a instância da classe Karavela

        """
        self.healthy_check_file = None
    
    def create_health_check_file(self,health_check_filename:str = None)->bool:
        """
        Cria um arquivo de verificação de saúde.
        Args:
            health_check_filename (str, optional): O nome do arquivo de verificação de saúde. 
                Se não for fornecido, um ValueError será levantado.
        Returns:
            bool: True se o arquivo for criado com sucesso.
        Raises:
            ValueError: Se o parâmetro health_check_filename não for fornecido.
        Example:
            >>> karavela = Karavela()
            >>> karavela.create_health_check_file("health_check.txt")
            True
        """
        
        
        if health_check_filename is None or health_check_filename == "":
            
            raise ValueError("O método 'create_health_check_file' precisa do parâmetro health_check_filename especificado")
        
        self.health_check_filename = health_check_filename

        try:

            if not os.path.exists(self.health_check_filename):

                directory = os.path.dirname(self.health_check_filename)

                if not os.path.exists(directory) and str(directory).strip() != "":
             
                    os.makedirs(directory)
                
            with open(f'{self.health_check_filename}', 'w') as f:
                           
                f.write('OK!')
                return True
            
        except Exception as e:
        
            raise e
    
    def destroy_health_check_file(self)->bool:
        """
        Remove o arquivo de verificação de saúde.
        Retorna:
            bool: True se o arquivo foi removido com sucesso, False caso contrário.
        Raises:
            ValueError: Se o método 'create_health_check_file' não foi executado antes.
            Exception: Se ocorrer algum erro durante a remoção do arquivo.
        """
        
        
        if self.health_check_filename is None:
        
            raise ValueError("O método 'create_health_check_file' precisa ser executado antes")
        
        try:

            if os.path.exists(self.health_check_filename):

                os.remove(self.health_check_filename)
                return True
                
            else:
            
                return True
                    
        except Exception as e:
        
            raise e
    
    
    # def get_secret(self, name: str, maestro: Optional[BotMaestroSDK] = None) -> str:
    #     """Extrai a secret do ambiente

    #     Args:
    #         name (str): nome da variavel ou arquivo da secret
    #         maestro ( Optional[BotMaestroSDK]): Recebe o Maestro da Botcity. e opcional.

    #     Returns:
    #         str: string da secret armazenada na variável de ambiente ou no arquivo de secret
    #     """
        
    #     # Tentando extrair da variavel de ambiente
    #     secret = os.getenv(name)
        
    #     # secret não encontrada em variavel de ambiente, tentando extrair do arquivo em /secret
    #     if secret is None:

    #         # verifica na pasta ./secrets
    #         if os.path.exists(f"./secrets/{name}"):

    #             with open(f"./secrets/{name}",'r') as secret_file:
            
    #                 secret = secret_file.read()

    #         # verifica na pasta ./.secrets
    #         elif os.path.exists(f"./.secrets/{name}"):

    #             with open(f"./.secrets/{name}",'r') as secret_file:
            
    #                 secret = secret_file.read()

    #         # verifica na pasta ./private
    #         elif os.path.exists(f"./private/{name}"):

    #             with open(f"./private/{name}",'r') as secret_file:
            
    #                 secret = secret_file.read()

    #         # verifica na pasta ./.private
    #         elif os.path.exists(f"./.private/{name}"):

    #             with open(f"./.private/{name}",'r') as secret_file:
            
    #                 secret = secret_file.read()

    #         # verifica na pasta /secrets
    #         elif os.path.exists(f"/secrets/{name}"):

    #             with open(f"/secrets/{name}",'r') as secret_file:
            
    #                 secret = secret_file.read()

    #         elif maestro and isinstance(maestro, BotMaestroSDK):
    #             try:
                
    #                 secret = maestro.get_credential(label=name, key=name)
                
    #             except Exception as e:
                    
    #                 secret = None

    #     return secret
    
