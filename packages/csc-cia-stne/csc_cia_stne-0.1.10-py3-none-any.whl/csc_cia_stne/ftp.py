import pycurl
import socket
import time
import os
from io import BytesIO

from .utilitarios.validations.ftp import InitParamsValidator,UploadDownloadValidator,ListFilesValidator

class FTP():

    def __init__(self, host:str , user:str , password:str , timeout:int=30, port:bool=21, tls:bool=True, ssl:bool=True, verify_ssl:bool=False, verify_host:bool=False, tryouts:int=3):

        self.host = host
        self.user = user
        self.password = password
        self.port = port
        self.timeout = timeout
        self.tls = tls
        self.ssl = ssl
        self.verify_ssl = verify_ssl
        self.verify_host = verify_host
        self.tryouts = tryouts

        try:

            InitParamsValidator(
                host=self.host,
                user=self.user,
                password=self.password,
                port=self.port,
                timeout=self.timeout,
                tls=self.tls,
                ssl=self.ssl,
                verify_ssl=self.verify_ssl,
                verify_host=self.verify_host,
                tryouts=self.tryouts
            )

        except Exception as e:
            
            raise ValueError(f"Erro na validação dos parâmetros de inicialização: {str(e)}")


        self._test_connection()

    def _test_connection(self):
        """
        Testa a conexão com o servidor FTP utilizando o host e a porta especificados.
        Este método tenta estabelecer uma conexão de socket com o servidor FTP
        usando os parâmetros `host` e `port`. Caso a conexão seja bem-sucedida,
        retorna `True`. Caso contrário, levanta uma exceção `ConnectionError` com
        uma mensagem apropriada.
        Raises:
            ConnectionError: Se ocorrer um timeout ou se a conexão for recusada.
            ConnectionError: Se ocorrer um erro desconhecido durante a tentativa de conexão.
        Returns:
            bool: `True` se a conexão for bem-sucedida.
        """

        try:

            with socket.create_connection((self.host, self.port), timeout=self.timeout) as sock:

                sock.close()

                return True

        except (socket.timeout, ConnectionRefusedError) as e:

            raise ConnectionError(f"Erro de timeout ou conexão negada {self.host}:{self.port}. Error: {str(e)}")
        
        except Exception as e:

            raise ConnectionError(f"Erro desconhecido ao tentar conexão com {self.host}:{self.port}. Error: {str(e)}")
        
    def _login_server(self):
        """
        Estabelece uma conexão com o servidor FTP utilizando as credenciais fornecidas e configurações de segurança.
        Configurações:
        - `self.user` e `self.password`: Credenciais de autenticação para o servidor FTP.
        - `self.tls`: Se True, força o uso de TLS para a conexão.
        - `self.ssl`: Se True, ativa FTPS explícito.
        - `self.verify_ssl`: Se False, desativa a verificação de certificado SSL.
        - `self.verify_host`: Se False, desativa a verificação do host SSL.
        Retorna:
            pycurl.Curl: Objeto de conexão configurado para o servidor FTP.
        Exceções:
            ConnectionError: Lançada quando ocorre um erro ao tentar estabelecer a conexão com o servidor FTP.
        """

        try:

            connection_ftp = pycurl.Curl()

            connection_ftp.setopt(connection_ftp.USERPWD, f"{self.user}:{self.password}")

            connection_ftp.setopt(connection_ftp.CONNECTTIMEOUT, self.timeout)  # Tempo limite para conexão
                    
            connection_ftp.setopt(connection_ftp.TIMEOUT, self.timeout*2)  # Tempo limite para operação

            if self.tls is True:

                connection_ftp.setopt(connection_ftp.USE_SSL, connection_ftp.USESSL_ALL)  # Força uso de TLS
            
            if self.ssl is True:
        
                connection_ftp.setopt(connection_ftp.FTP_SSL, connection_ftp.FTPSSL_ALL)  # Ativa FTPS explícito

            if self.verify_ssl is False:
                
                connection_ftp.setopt(connection_ftp.SSL_VERIFYPEER, 0)  # Desativar verificação SSL (ajuste conforme necessário)
            
            if self.verify_host is False:

                connection_ftp.setopt(connection_ftp.SSL_VERIFYHOST, 0)  # Desativar verificação de host SSL

            return connection_ftp
        
        except Exception as e:
        
            self._test_connection()

            raise ConnectionError(f"Erro ao tentar conexão com o servidor FTP {self.host}:{self.port}. Error: {str(e)}")
    
    def upload_or_download_file(self, filename:str, filepathftp:str, method:str="UPLOAD"):
        """
        Faz upload ou download de um arquivo para/da um servidor FTP.
        Args:
            filename (str): Nome do arquivo local a ser enviado ou recebido.
            filepathftp (str): Caminho remoto no servidor FTP onde o arquivo será enviado ou recebido.
            method (str, opcional): Método de operação, "UPLOAD" para enviar arquivo ou "DOWNLOAD" para baixar arquivo. 
                                    O padrão é "UPLOAD".
        Returns:
            dict: Um dicionário contendo:
                - 'status' (bool): Indica se a operação foi bem-sucedida.
                - 'status_code' (int): Código de resposta do servidor FTP.
                - 'message' (str): Mensagem indicando o resultado da operação.
        Raises:
            FileNotFoundError: Se o arquivo especificado não for encontrado.
            PermissionError: Se houver problemas de permissão ao acessar o arquivo.
            Exception: Para outros erros durante a operação.
        Nota:
            O método tenta realizar a operação várias vezes, conforme definido em `self.tryouts`.
            Em caso de falha, retorna um status indicando o erro.
        """
        
        try:

            UploadDownloadValidator(
                filename=filename,
                filepathftp=filepathftp,
                method=method.upper()
            )

        except Exception as e:

            raise ValueError(f"Erro na validação dos parâmetros de upload/download: {str(e)}")

        filename = os.path.join(os.getcwd(), filename)

        connection_ftp = self._login_server()

        remote_path = f"{filepathftp}{filename}"

        ftp_url = f"ftp://{self.host}{remote_path}"

        status_upload = True

        methodfile = "rb"

        if method.upper() == "DOWNLOAD":

            methodfile = "wb"

        for try_out in range(self.tryouts):

            time.sleep(5)

            try:

                with open(filename, methodfile) as file:

                    connection_ftp.setopt(connection_ftp.URL, ftp_url)

                    connection_ftp.setopt(connection_ftp.UPLOAD, 1)

                    if method.upper() == "UPLOAD":
                    
                        connection_ftp.setopt(connection_ftp.READDATA, file)
                    
                    elif method.upper() == "DOWNLOAD":
                      
                        connection_ftp.setopt(connection_ftp.WRITEDATA, file)

                    connection_ftp.perform()

                    status_code = connection_ftp.getinfo(connection_ftp.RESPONSE_CODE)

                    break
                
            except FileNotFoundError as e:

                raise FileNotFoundError(f"Arquivo '{filename}' não encontrado. Error: {str(e)}")
            
            except PermissionError as e:

                raise PermissionError(f"Permissão negada para acessar o arquivo '{filename}'. Error: {str(e)}")

            except Exception as e:

                status_code = None
                
                status_upload = False

        if status_code == 226:

            status_upload = True

        else:

            status_upload = False
        
        connection_ftp.close()

        return {
            'status': status_upload,
            'status_code': status_code
        }
    
    def list_files(self, filepathftp:str):
        """
        Lista arquivos em um diretório FTP especificado.
        Este método conecta-se a um servidor FTP, lista os arquivos disponíveis no diretório especificado
        e retorna os nomes dos arquivos juntamente com metadados, se disponíveis.
        Args:
            filepathftp (str): Caminho do diretório no servidor FTP onde os arquivos serão listados.
        Returns:
            dict: Um dicionário contendo:
                - 'status' (bool): Indica se a operação foi bem-sucedida.
                - 'status_code' (int ou None): Código de resposta do servidor FTP.
                - 'message' (str): Mensagem detalhando o resultado da operação.
                - 'files' (list): Lista de arquivos encontrados no diretório FTP.
        Raises:
            ConnectionError: Caso ocorra algum erro ao criar o buffer de memória ou ao definir a URL do FTP.
        """

        try:

            ListFilesValidator(filepathftp=filepathftp)

        except Exception as e:

            raise ValueError(f"Erro na validação dos parâmetros de listagem de arquivos: {str(e)}")

        try:

            buffer = BytesIO()

        except Exception as e:

            raise ConnectionError(f"Erro ao criar buffer de memória. Error: {str(e)}")
        
        connection_ftp = self._login_server()

        ftp_url = f"ftp://{self.host}{filepathftp}"

        for try_out in range(self.tryouts):

            try:

                connection_ftp.setopt(connection_ftp.URL, ftp_url)

                connection_ftp.setopt(connection_ftp.WRITEDATA, buffer)

                connection_ftp.setopt(connection_ftp.VERBOSE, False)

                connection_ftp.setopt(connection_ftp.NOBODY, False)

                connection_ftp.setopt(connection_ftp.DIRLISTONLY, False)  # True = apenas nomes; False = nomes + metadados estilo ls -l
    
                connection_ftp.perform()

                try:
                    files_to_organize = buffer.getvalue().decode('utf-8')
                except UnicodeDecodeError:
                    files_to_organize = buffer.getvalue().decode('latin-1')
                
                lines_of_file = files_to_organize.splitlines()

                organized_list = []

                for line in lines_of_file:
                    parts = line.strip().split()
                    if parts:
                        nome = parts[-1]
                        organized_list.append(nome)

                connection_ftp.close()

                return {
                    'status': True,
                    'files': organized_list
                }

            except Exception as e:

                raise ConnectionError(f"Erro ao definir URL do FTP. Error: {str(e)}")

        connection_ftp.close()

        return {
            'status': False,
            'message': f"Falha ao listar arquivos de {self.host}:{self.port}/{filepathftp}."
        }