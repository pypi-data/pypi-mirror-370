from google.oauth2 import service_account
from google.cloud import storage
from pydantic import ValidationError

from .utilitarios.validations.gcp_bucket import InitParamsValidator,ListFilesValidator,GetFilesValidator,UploadFilesValidator,DeleteFilesValidator


class GCPBucket():

    def __init__(self, creds_dict: dict = None, creds_file: str = None):
        """
        Inicializa uma instância da classe com as credenciais fornecidas.
        Args:
            creds_dict (dict, opcional): Um dicionário contendo as credenciais para autenticação.
            creds_file (str, opcional): O caminho para um arquivo contendo as credenciais para autenticação.
        Raises:
            ValueError: Se os dados de entrada para inicialização da instância não forem válidos.
        """

        try:

            InitParamsValidator(creds_dict=creds_dict, creds_file=creds_file)

        except ValidationError as e:
        
            raise ValueError("Erro na validação dos dados de input da inicialização da instância:", e.errors())
        
        self.creds_dict = creds_dict
        self.creds_file = creds_file
        self.client = self._create_client()

    def _create_client(self):
        """
        Cria um cliente para interagir com o Google Cloud Storage.
        Este método utiliza as credenciais fornecidas para autenticar e criar
        um cliente do Google Cloud Storage. As credenciais podem ser fornecidas
        como um dicionário (`creds_dict`) ou como um arquivo (`creds_file`).
        Raises:
            ValueError: Se nenhum arquivo de credenciais ou dicionário de credenciais
            for fornecido, ou se ocorrer um erro ao criar o cliente do bucket.
        Returns:
            storage.Client: Uma instância autenticada do cliente do Google Cloud Storage.
        """

        try:

            if self.creds_dict is not None:

                credentials = service_account.Credentials.from_service_account_info(
                    self.creds_dict,
                )

            elif self.creds_file is not None:

                credentials = service_account.Credentials.from_service_account_file(
                    self.creds_file,
                )

            else:

                raise ValueError("Nenhum arquivo de credenciais ou dicionário de credenciais fornecido.")
            
            return storage.Client(credentials=credentials)

        except Exception as e:

            raise ValueError("Erro ao criar o cliente do bucket:", e)
        
    # Função para listar os arquivos em um bucket
    def list_files(self, bucket_name:str) -> dict:
        """
        Lista os arquivos presentes em um bucket do Google Cloud Storage.
        Args:
            bucket_name (str): O nome do bucket do qual os arquivos serão listados.
        Returns:
            dict: Um dicionário contendo:
                - 'success' (bool): Indica se a operação foi bem-sucedida.
                - 'files' (list): Uma lista com os nomes dos arquivos no bucket (presente apenas se 'success' for True).
                - 'error' (str): Mensagem de erro (presente apenas se 'success' for False).
                - 'details' (str): Detalhes adicionais sobre o erro (presente apenas se 'success' for False).
        Raises:
            ValueError: Se os dados de entrada não forem válidos, contendo detalhes do erro de validação.
        """

        try:

            ListFilesValidator(bucket_name=bucket_name)

        except ValidationError as e:
        
            raise ValueError("Erro na validação dos dados de input da função de listagem de arquivos", e.errors())

        try:

            bucket = self.client.bucket(bucket_name)

            blobs = bucket.list_blobs()

            files = [blob.name for blob in blobs]

            return {
                'success':True,
                'files':files
            }
        
        except Exception as e:

            return {
                'success':False,
                'error':str(e),
                'details':'Erro ao acessar o bucket'
            }

    # Função para baixar os arquivos de um bucket
    def get_file(self, bucket_name:str, filename:str, destination:str=None, chunksize:int=256) -> dict:
        """
        Faz o download de um arquivo de um bucket do Google Cloud Storage para um destino local.
        Args:
            bucket_name (str): Nome do bucket no Google Cloud Storage.
            filename (str): Nome do arquivo a ser baixado do bucket.
            destination (str, opcional): Caminho completo onde o arquivo será salvo localmente. 
                Se não for especificado, o arquivo será salvo com o mesmo nome do arquivo no bucket.
            chunksize (int, opcional): Tamanho do chunk em megabytes para o download do arquivo. 
                O padrão é 256 MB.
        Returns:
            dict: Um dicionário contendo o status da operação. 
                - 'success' (bool): Indica se a operação foi bem-sucedida.
                - 'error' (str, opcional): Mensagem de erro, caso ocorra uma exceção.
                - 'details' (str): Detalhes adicionais sobre o sucesso ou falha da operação.
        Raises:
            ValueError: Se os dados de entrada não forem válidos.
        """

        try:

            GetFilesValidator(bucket_name=bucket_name, filename=filename, destination=destination, chunksize=chunksize)

        except ValidationError as e:
        
            raise ValueError("Erro na validação dos dados de input da função para obter arquivos", e.errors())

        if destination is None:
             
            destination = filename

        try:

            bucket = self.client.bucket(bucket_name)
            
        except Exception as e:

            return {
                'success':False,
                'error':str(e),
                'details':'Erro ao acessar o bucket'
            }
        
        try:

            blob = bucket.blob(filename)

            blob.chunk_size = chunksize * 1024 * 1024  # 256M

            blob.download_to_filename(destination)

            return {
                'success':True,
                'details':f'Arquivo baixado para o diretório: {str(destination)}'
            }

        except Exception as e:
        
            return {
                'success':False,
                'error':str(e),
                'details':'Erro ao baixar o arquivo do bucket'
            }

    # Função para realizr o upload de arquivos para um bucket
    def upload_file(self, bucket_name:str, filename:str, destination:str=None) -> dict:
        """
        Faz o upload de um arquivo para um bucket no Google Cloud Storage.
        Args:
            bucket_name (str): Nome do bucket onde o arquivo será enviado.
            filename (str): Caminho do arquivo local que será enviado.
            destination (str, opcional): Caminho de destino no bucket. 
                Se não for especificado, será utilizado o mesmo nome do arquivo local.
        Returns:
            dict: Um dicionário contendo o resultado da operação.
                - 'success' (bool): Indica se o upload foi bem-sucedido.
                - 'details' (str): Mensagem detalhada sobre o resultado.
                - 'error' (str, opcional): Mensagem de erro, caso o upload falhe.
        Raises:
            ValueError: Se os dados de entrada não forem válidos.
        """

        try:

            UploadFilesValidator(bucket_name=bucket_name, filename=filename, destination=destination)

        except ValidationError as e:
        
            raise ValueError("Erro na validação dos dados de input da função para realizar upload de arquivos", e.errors())

        if destination is None:

            destination = filename

        try:

            bucket = self.client.bucket(bucket_name)

        except Exception as e:

            return {
                'success':False,
                'error':str(e),
                'details':'Erro ao acessar o bucket'
            }
        
        try:

            blob = bucket.blob(destination)

            blob.upload_from_filename(filename)

            return {
                'success':True,
                'details':f'Arquivo enviado para o bucket: {str(destination)}'
            }
        
        except Exception as e:

            return {
                'success':False,
                'error':str(e),
                'details':'Erro ao enviar o arquivo para o bucket'
            }

    # Função para deletar arquivos de um bucket
    def delete_file(self, bucket_name:str, filename:str) -> dict:
        """
        Deleta um arquivo de um bucket no Google Cloud Storage.
        Args:
            bucket_name (str): Nome do bucket onde o arquivo está armazenado.
            filename (str): Nome do arquivo a ser deletado.
        Returns:
            dict: Um dicionário contendo o resultado da operação. 
                - 'success' (bool): Indica se a operação foi bem-sucedida.
                - 'error' (str, opcional): Mensagem de erro, caso a operação falhe.
                - 'details' (str): Detalhes adicionais sobre o resultado da operação.
        Raises:
            ValueError: Caso os dados de entrada não passem na validação.
        """

        try:

            DeleteFilesValidator(bucket_name=bucket_name, filename=filename)

        except ValidationError as e:
        
            raise ValueError("Erro na validação dos dados de input da função para deletar arquivos", e.errors())

        try:

            bucket = self.client.bucket(bucket_name)

        except Exception as e:

            return {
                'success':False,
                'error':str(e),
                'details':'Erro ao acessar o bucket'
            }
        
        try:

            blob = bucket.blob(filename)

            blob.delete()

            return {
                'success':True,
                'details':f'Arquivo deletado do bucket: {str(filename)}'
            }

        except Exception as e:

            return {
                'success':False,
                'error':str(e),
                'details':'Erro ao deletar o arquivo do bucket'
            }
