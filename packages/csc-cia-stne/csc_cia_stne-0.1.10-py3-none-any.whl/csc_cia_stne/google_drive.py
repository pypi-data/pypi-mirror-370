import os
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError
from io import BytesIO
from google.oauth2 import service_account
from .utilitarios.validations.GoogleDriveValidator import (
    InitParamsValidator,
    CreateFolderValidator,
    ListFolderValidator,
    UploadValidator,
)
from pydantic import ValidationError


class GoogleDrive:
    """
    Classe responsável por gerenciar operações no Google Drive, como upload de arquivos, criação de pastas
    e listagem de conteúdo. Utiliza a API do Google Drive para realizar essas operações.

    Args:
        key (str): Chave de autenticação para acessar a API do Google Drive.
    """

    _instance = None  # Atributo de classe para armazenar a única instância.

    def __new__(cls, *args, **kwargs):
        # Verifica se já existe uma instância da classe.
        if cls._instance is None:
            # Cria e armazena a instância na primeira chamada.
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(
        self,
        token: dict,
        with_subject: str,
        scopes: list = ["https://www.googleapis.com/auth/drive"],
        version: str = "v3",
    ):
        """
        Inicializa uma instância da classe GoogleDrive.
        Parâmetros:
        - key (str): A chave para acessar o segredo necessário para autenticação.
        - with_subject (str): O assunto para o qual a autenticação será realizada.
        - scopes (list): Uma lista de escopos de permissão para acesso ao Google Drive. O valor padrão é ["https://www.googleapis.com/auth/drive"].
        - version (str): A versão da API do Google Drive a ser utilizada. O valor padrão é "v3".
        Raises:
        - ValueError: Se ocorrer um erro na validação dos dados de input da inicialização da instância.
        Exemplo de uso:
        ```
        google_drive = GoogleDrive(key="chave_secreta", with_subject="assunto", scopes=["https://www.googleapis.com/auth/drive"], version="v3")
        ```
        """

        try:
            InitParamsValidator(
                token=token, with_subject=with_subject, scopes=scopes, version=version
            )
        except ValidationError as e:
            raise ValueError(
                "Erro na validação dos dados de input da inicialização da instância:",
                e.errors(),
            )
        self.__token = token
        self.version = version
        self.scopes = scopes
        self.with_subject = with_subject
        self.page_size = 1000
        self.service = self.__create_service()

    def __create_service(self):
        """
        Cria um serviço do Google Drive.
        Returns:
            cred: Objeto de credenciais do Google Drive.
            False: Caso ocorra algum erro ao criar o serviço.
        Raises:
            Exception: Caso ocorra algum erro ao criar o serviço do Google Drive.
        Exemplo de uso:
            service = create_service()
            if service:
                # Fazer algo com o serviço do Google Drive
            else:
                # Tratar o erro de criação do serviço
        """

        try:
            auth = self.__autentica(self.with_subject)
            service = build(f"drive", f"{self.version}", credentials=auth)
            return service
        except Exception as e:
            return False

    def __autentica(self, with_subject: str):
        """
        Autentica o usuário com as credenciais fornecidas e retorna as credenciais delegadas para o assunto especificado.
        Args:
            with_subject (str): O assunto para o qual as credenciais serão delegadas.
        Returns:
            google.auth.credentials.Credentials: As credenciais delegadas para o assunto especificado.
        Raises:
            Exception: Se ocorrer um erro durante a autenticação.
        Example:
            # Autenticar com o assunto "user@example.com"
            credentials = self.__autentica("user@example.com")
        """

        try:
            credentials = service_account.Credentials.from_service_account_info(
                self.__token, scopes=self.scopes
            )
            delegated_credencial = credentials.with_subject(with_subject)
            return delegated_credencial

        except Exception as e:
            return False

    def upload(self, folder_id: str, name: str, file_path: str, mimetype: str):
        """
        Faz o upload de um arquivo para o Google Drive em uma pasta especificada.

        Args:
            folder_id (str): ID da pasta no Google Drive onde o arquivo será armazenado.
            name (str): Nome do arquivo que será carregado.
            file_path (str): Caminho completo do arquivo no sistema local.
            mimetype (str): Tipo MIME do arquivo a ser carregado.
                exemplos:   text/plain
                            text/html
                            image/jpeg
                            image/png
                            audio/mpeg
                            audio/ogg
                            audio/*
                            video/mp4
                            application/octet-stream

        Returns:
            dict: Informações sobre o arquivo carregado, incluindo o ID do arquivo.
            None: Caso o caminho do arquivo não seja encontrado.
        """
        try:
            UploadValidator(
                folder_id=folder_id, name=name, file_path=file_path, mimetype=mimetype
            )
        except ValidationError as e:
            raise ValueError(
                "Erro na validação dos dados para realizar o upload do arquivo",
                e.errors(),
            )

        file_metadata = {"name": name, "parents": [folder_id]}
        if not os.path.exists(file_path):
            return {
                "success": False,
                "result": None,
                "error": "Diretório ou arquivo não encontrado",
            }

        try:
            media = MediaFileUpload(file_path, mimetype=mimetype, resumable=True)
            file = (
                self.service.files()
                .create(
                    body=file_metadata,
                    media_body=media,
                    fields="id",
                    supportsAllDrives=True,
                )
                .execute()
            )

            return {"success": True, "result": file}
        except Exception as e:

            return {"success": False, "result": None, "error": str(e)}

    def _validate_folder_existence(self, folder: str, id_folder: str):
        """
        Verifica a existência de uma pasta no Google Drive.
        Args:
            folder (str): O nome da pasta a ser verificada.
            id_folder (str): O ID da pasta pai.
        Returns:
            dict or None: Um dicionário contendo as informações da pasta se ela existir, caso contrário, retorna None.
        Raises:
            ValueError: Se ocorrer algum erro durante a busca pela pasta.
        """

        query = f"'{id_folder}' in parents and trashed=false"

        try:

            response = (
                self.service.files()
                .list(
                    q=query,
                    spaces="drive",
                    fields="nextPageToken, files(id, name, mimeType)",
                    pageToken=None,
                    includeItemsFromAllDrives=True,
                    supportsAllDrives=True,
                )
                .execute()
            )

            items = response.get("files", [])

            for item in items:

                if (
                    item["mimeType"] == "application/vnd.google-apps.folder"
                    and item["name"] == folder
                ):

                    return item

            return None

        except Exception as e:

            raise ValueError(f"Erro tentando procurar pela pasta:{e}")

    def create_folder(
        self, name: str, parent_folder_id: str, validate_existence: bool = False
    ):
        """
        Cria uma pasta no Google Drive dentro de uma pasta existente.

        Args:
            name (str): Nome da pasta a ser criada.
            parent_folder_id (int): ID da pasta pai onde a nova pasta será criada.
            validate_existence (bool): Se True, verifica se a pasta já existe antes de criá-la. Defaults to False.
        Returns:
            str: ID da pasta criada.
        """
        try:
            CreateFolderValidator(
                name=name,
                parent_folder_id=parent_folder_id,
                validate_existence=validate_existence,
            )
        except ValidationError as e:
            raise ValueError(
                "Erro na validação dos dados de input da inicialização da instância:",
                e.errors(),
            )

        status_existence = None

        if validate_existence:

            status_existence = self._validate_folder_existence(name, parent_folder_id)

        if status_existence is None:

            try:
                folder_metadata = {
                    "name": name,
                    "parents": [parent_folder_id],
                    "mimeType": "application/vnd.google-apps.folder",
                }
                folder = (
                    self.service.files()
                    .create(body=folder_metadata, fields="id", supportsAllDrives=True)
                    .execute()
                )
                return {"success": True, "result": folder}
            except Exception as e:
                return {"success": False, "result": None, "error": str(e)}

        return {"success": True, "result": status_existence}

    def list_items_folder(
        self,
        query: str = "",
        spaces: str = "drive",
        fields: str = "nextPageToken, files(id, name)",
    ):
        """
        Lista os arquivos e pastas no Google Drive com base nos critérios fornecidos.

        Args:
            query (str, optional): Critério de busca para os arquivos ou pastas no Google Drive.
                                Consulte https://developers.google.com/drive/api/v3/ref-search-terms.
                                Defaults to "".
                                exemplo: query = 'ID_DA_PASTA_NO_GOOGLE_DRIVE' in parents and trashed=false"
            spaces (str, optional): Especifica os locais de armazenamento a serem consultados. Pode ser 'drive',
                                    'appDataFolder', ou 'photos'. Defaults to 'drive'.
            fields (str, optional): Campos a serem retornados na resposta. Consulte a documentação para os campos disponíveis.
                                    Defaults to "nextPageToken, files(id, name)".

        Returns:
            dict: Dicionário contendo o resultado da busca.
        """
        try:
            ListFolderValidator(query=query, fields=fields, spaces=spaces)
        except ValidationError as e:
            raise ValueError(
                "Erro na validação dos dados de input da lista:", e.errors()
            )
        try:
            results = (
                self.service.files()
                .list(
                    q=query,
                    spaces=spaces,
                    pageSize=self.page_size,
                    fields=fields,
                    supportsAllDrives=True,
                    includeItemsFromAllDrives=True,
                )
                .execute()
            )
            return {"success": True, "result": results}
        except HttpError as hr:
            return {"success": False, "result": None, "error": str(hr)}
        except Exception as e:
            return {"success": False, "result": None, "error": str(e)}

    def download_google_files(self, file: str, mimeType: str, path: str):
        """
        Obtém o conteúdo de um arquivo armazenado no Google Drive. Aceito somente para extensões Google

        Esta função acessa o Google Drive usando a API e lê os dados do arquivo especificado, retornando-os como um objeto binário de memória (`BytesIO`).

        Parâmetros:
            - file (str): Dicionário contendo informações do arquivo no Google Drive, incluindo as chaves:
                - `"name"`: Nome do arquivo.
                - `"id"`: ID do arquivo.

        Retorna:
            - BytesIO: Objeto em memória contendo os dados do arquivo.
            - None: Caso ocorra um erro ao tentar abrir ou ler o arquivo.

        Logs:
            - Registra mensagens indicando o início e o término da leitura do arquivo.
            - Em caso de falha, registra o erro ocorrido.

        Exceções:
            - Qualquer erro durante o processo será capturado e registrado no log. A função retornará `None` nesses casos.

        Dependências:
            - A função assume a existência de um atributo `self.service` configurado para interagir com a API do Google Drive.
        """
        if not os.path.exists(path):
            os.makedirs(path)
        try:
            request = self.service.files().export_media(
                fileId=file.get("id"), mimeType=mimeType
            )
            file_path = f"{path}{file["name"]}"
            with open(file_path, "wb") as f:
                f.write(request.execute())
            return {
                "success": True,
                "result": file_path,
                "error": None,
            }

        except Exception as e:
            return {"success": False, "result": None, "error": str(e)}

    def download_others_files(self, file: str, path: str):
        """
        Obtém o conteúdo de um arquivo armazenado nos seguintes formatos:
        .xlsx, .pdf, .jpg, etc.

        Esta função acessa o Google Drive usando a API e lê os dados do arquivo especificado, retornando-os como um objeto binário de memória (`BytesIO`).

        Parâmetros:
            - file (str): Dicionário contendo informações do arquivo no Google Drive, incluindo as chaves:
                - `"name"`: Nome do arquivo.
                - `"id"`: ID do arquivo.
            - mimeType (str): Tipo do arquivo, por exemplo: xlsx = application/vnd.openxmlformats-officedocument.spreadsheetml.sheet
            - path (str): diretório onde será salvo o arquivo.

        Retorna:
            - BytesIO: Objeto em memória contendo os dados do arquivo.
            - None: Caso ocorra um erro ao tentar abrir ou ler o arquivo.

        Logs:
            - Registra mensagens indicando o início e o término da leitura do arquivo.
            - Em caso de falha, registra o erro ocorrido.

        Exceções:
            - Qualquer erro durante o processo será capturado e registrado no log. A função retornará `None` nesses casos.

        Dependências:
            - A função assume a existência de um atributo `self.service` configurado para interagir com a API do Google Drive.
        """
        if not os.path.exists(path):
            os.makedirs(path)
        try:
            request = self.service.files().get_media(fileId=file.get("id"))
            file_path = f"{path}{file["name"]}"
            with open(file_path, "wb") as f:
                f.write(request.execute())
            return {
                "success": True,
                "result": file_path,
            }

        except Exception as e:
            return {"success": False, "result": None}

    def get_base_data(self, id_sheet: str, page: str) -> list:
        """
        Retorna os dados da planilha especificada.
        Parâmetros:
        - drive_client: Cliente do Google Drive.
        - id_sheet: ID da planilha.
        - page: Nome da página da planilha.
        Retorna:
        - Uma lista contendo os valores da planilha.
        Exemplo de uso:
        >>> drive_client = ...
        >>> id_sheet = "abc123"
        >>> page = "Sheet1"
        >>> data = get_base_data(drive_client, id_sheet, page)
        """
        try:
            sheet = self.service.spreadsheets()
            result = sheet.values().get(spreadsheetId=id_sheet, range=page).execute()
            values = result.get("values", [])
            return {"success": True, "result": values}
        except Exception as e:
            return {"success": False, "result": None, "error": str(e)}

    def delete_file(self, id_file:str):
        """
        Exclui um arquivo do Google Drive pelo seu ID.
        Args:
            id_file (str): O ID do arquivo a ser excluído.
        Returns:
            dict: Um dicionário indicando se a exclusão foi bem-sucedida.
                - {"success": True} se o arquivo foi excluído com sucesso.
                - {"success": False, "error": <mensagem de erro>} se ocorreu uma exceção.
        """

        try:
            self.service.files().delete(fileId=id_file, supportsAllDrives=True).execute()
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}