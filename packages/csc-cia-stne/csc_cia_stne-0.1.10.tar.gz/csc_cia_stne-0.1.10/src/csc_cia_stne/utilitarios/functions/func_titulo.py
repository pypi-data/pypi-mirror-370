import os
from datetime import datetime
from rich import print
from rich.panel import Panel
from rich.style import Style
import logging
from pydantic import BaseModel
from pydantic import ValidationError, field_validator

# Classe para validar - titulo
class TituloSettings(BaseModel):
    """
    Classe que define as configurações do título do projeto.
    Atributos:
    - project_name (str): O nome do projeto.
    - project_version (str): A versão do projeto.
    - project_dev_name (str): O nome do desenvolvedor do projeto.
    - project_dev_mail (str): O e-mail do desenvolvedor do projeto.
    Métodos:
    - check_non_empty_string(value, info): Método de validação para garantir que nenhum campo seja uma string vazia.
    """
    
    # Titulo
    project_name: str
    project_version: str
    project_dev_name: str
    project_dev_mail: str
    # Validador para garantir que nenhum campo seja uma string vazia
    """
    Método de validação para garantir que nenhum campo seja uma string vazia.
    Parâmetros:
    - value: O valor do campo a ser validado.
    - info: Informações sobre o campo a ser validado.
    Retorna:
    - O valor do campo se for uma string não vazia.
    Lança:
    - ValueError: Se o valor do campo for uma string vazia.
    Exemplo de uso:
    ```
    settings = TituloSettings()
    settings.check_non_empty_string("GitHub Copilot", "project_name")
    ```
    """
    @field_validator('project_name', 'project_version', 'project_dev_name', 'project_dev_mail')
    def check_non_empty_string(cls, value, info):
        if not isinstance(value, str) or not value.strip():
            
            raise ValueError(f"O parâmetro '{info.field_name}' deve ser uma string não vazia.")
        
        return value


# Retorna data de modificação
def last_modified()->datetime:
    """
    Retorna a data da última atualização do script

    """
    base_dir = os.path.abspath(os.getcwd())

    newest_date = None

    for root, _, files in os.walk(base_dir):
        
        for file in files:
        
            if file.endswith('.py'):
        
                file_path = os.path.join(root, file)
                file_modification_date = os.path.getmtime(file_path)
                
                if newest_date is None or file_modification_date > newest_date:
        
                    newest_date = file_modification_date

    # Converter o timestamp para um objeto datetime
    last_modified_date = datetime.fromtimestamp(newest_date)
    last_modified_date = last_modified_date.strftime("%Y%m%d")
    
    return last_modified_date

def titulo(project_name:str,project_version:str,project_dev_name:str,project_dev_mail:str):
    """
    Gera um título formatado para exibição do projeto.
    Args:
        project_name (str): Nome do projeto.
        project_version (str): Versão do projeto.
        project_dev_name (str): Nome do desenvolvedor do projeto.
        project_dev_mail (str): E-mail do desenvolvedor do projeto.
    Raises:
        ValueError: Caso alguma variável obrigatória esteja ausente no arquivo .env ou nas variáveis de ambiente da máquina.
    Example:
        >>> titulo("Meu Projeto", "1.0", "João", "joao@example.com")
        [Exemplo de saída]
    """

    try:
        settings = TituloSettings(project_name=project_name,project_version=project_version,project_dev_name=project_dev_name,project_dev_mail=project_dev_mail)
        #return settings

    except ValidationError as e:
        # Extrair os detalhes da exceção
        errors = e.errors()
        missing_vars = [error['loc'][0] for error in errors if error['type'] == 'missing']
        
        # Criar uma mensagem personalizada
        if missing_vars:
            missing_vars_str = ', '.join(missing_vars)
            raise ValueError(
                f"As seguintes variáveis obrigatórias estão ausentes no arquivo .env ou nas variáveis de ambiente da máquina, impossibi: {missing_vars_str}"
            )


    if os.getenv('ambiente_de_execucao') is None or os.getenv('ambiente_de_execucao') != "karavela":

        estilo_box = Style(bold=True)
        print(
            Panel(
                f"""
                    [bold chartreuse3]CIA [bold white]| [bold chartreuse3]Centro de Inteligência e Automação [bold white]([bold chartreuse3]cia@stone.com.br[bold white])[bold green]\n
                    Projeto[bold white]: [bold green]{project_name}\n
                    Versão[bold white]: [bold green]{project_version}\n
                    Dev[bold white]: [bold green]{project_dev_name} [bold white]([bold green]{project_dev_mail}[bold white])[bold green]\n
                    Última atualização[bold white]: [bold green]{last_modified()}
                """, 
                title="Stone", 
                subtitle="CSC-CIA", 
                style=estilo_box, 
                border_style="bold chartreuse3"
            )   
        )

    else:

        logging.info("CSC | CIA - Centro de Inteligência e Automação")
        logging.info(f"Projeto: {project_name}")
        logging.info(f"\tVersão: {project_version} (Última modificação: {last_modified()})")
        logging.info("\tTime: CIA <cia@stone.com.br>")
        logging.info(f"\tDesenvolvedor: {project_dev_name} <{project_dev_mail}>")
        logging.info("-")

