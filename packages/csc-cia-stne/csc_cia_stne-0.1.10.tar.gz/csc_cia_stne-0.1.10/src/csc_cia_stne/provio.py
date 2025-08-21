import logging
import requests
from requests.auth import HTTPBasicAuth
from pydantic import BaseModel, Field, ValidationError
from typing import List, Dict, Union

log = logging.getLogger('__main__')

# Validadores
class ProvioModel(BaseModel):
    """
    Modelo para validação das credenciais de autenticação.
    """
    username: str = Field(..., strip_whitespace=True, min_length=1)
    password: str = Field(..., strip_whitespace=True, min_length=1)

class ExportarRelatorioParams(BaseModel):
    """
    Modelo para validação dos parâmetros do relatório.
    """
    ano: int = Field(..., gt=2015, description="O ano deve ser maior que 2015")
    mes: int = Field(..., ge=1, le=12, description="O mês deve estar entre 1 e 12")
    verbose: bool = Field(False, description="Indica se as mensagens detalhadas devem ser exibidas")

# Classe provio
class Provio:
    """
    Classe para interagir com a API do Provio.
    """

    def __init__(self, username: str, password: str):
        """
        Inicializa a classe com as credenciais de autenticação.

        Args:
            username (str): Nome de usuário para autenticação.
            password (str): Senha para autenticação.

        Raises:
            ValidationError: Se as credenciais forem inválidas de acordo com o modelo `ProvioModel`.
        """        
        # Validação usando Pydantic
        data = ProvioModel(username=username, password=password)

        self.api_url = "https://provio.apps.stone.com.br/api/reports"
        self.auth = HTTPBasicAuth(data.username, data.password)

    def exportar_relatorio_geral(self, ano: int, mes: int, verbose: bool=False) -> Dict[str, Union[bool, str, List[Dict]]]:
        """
        Exporta o relatório geral para o período especificado.

        Args:
            ano (int): Ano do relatório (deve ser maior que 2015).
            mes (int): Mês do relatório (deve estar entre 1 e 12).
            verbose (bool): informa se as requisições devem ser expostas na console

        Returns:
            Dict[str, Union[bool, str, List[Dict]]]: Um dicionário contendo:
                - `success` (bool): Indica se a exportação foi bem-sucedida.
                - `error` (str): Mensagem de erro, se houver.
                - `report` (List[Dict]): Lista de registros exportados, se `success` for `True`.

        Raises:
            ValidationError: Se os parâmetros `ano` e `mes` forem inválidos.
        """        
        # Validação dos parâmetros
        params = ExportarRelatorioParams(ano=ano, mes=mes, verbose=verbose)
        periodo = f"{params.ano}-{params.mes:02d}"
        skip = 0
        todos_os_dados = []  # Lista para armazenar todos os resultados
        requisicao = 0
        try:
            
            while True:
            
                url = f"{self.api_url}/general/{periodo}/{skip}"
                response = requests.get(url=url, auth=self.auth)

                if response.status_code == 200:
            
                    dados = response.json()

                    # Verifica se há itens na resposta
                    if not dados:  # Se a resposta for vazia, interrompa o loop
            
                        break

                    # Adiciona os dados recebidos à lista total
                    todos_os_dados.extend(dados)

                    # Incrementa o skip para buscar a próxima página
                    skip += 500
                    requisicao += 1
                    if verbose:
                        log.info(f"Exportando relatório: Requisição #{str(requisicao).zfill(3)}: {len(todos_os_dados)} registros no total")
            
                else:
            
                    return {"success": False, "error": f"{response.status_code} - {response.text}"}

            return {"success": True, "error": None, "report": todos_os_dados}

        except Exception as e:
            
            return {"success": False, "error": str(e)}
