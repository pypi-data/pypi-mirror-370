import requests
import base64, json
import os
import logging
from pydantic import ValidationError
from .utilitarios.validations.ServiceNowValidator import *


class ServiceNow:

    def __init__(
        self, username: str = None, password: str = None, env: str = None
    ) -> None:
        """
        Inicializa uma instância da classe ServiceNow.

        Parâmetros:
            username (str): Nome de usuário para autenticação. Obrigatório e não pode ser nulo ou vazio.
            password (str): Senha para autenticação. Obrigatória e não pode ser nula ou vazia.
            env (str): Ambiente no qual a instância será utilizada. Deve ser 'dev', 'qa', 'qas' ou 'prod'.

        Raises:
            ValueError: Caso qualquer um dos parâmetros não seja fornecido, seja nulo ou vazio, ou se 'env' não for um valor válido.

        Atributos:
            username (str): Nome de usuário normalizado.
            password (str): Senha normalizada.
            env (str): Nome do ambiente em letras maiúsculas.
            api_url (str): URL base da API correspondente ao ambiente.
            api_header (dict): Cabeçalhos padrão para requisições API.
        """
        try:
            InitParamsValidator(username=username, password=password, env=env)
        except ValidationError as e:
            raise ValueError(
                "Erro na validação dos dados de input da inicialização da instância 'ServiceNow':",
                e.errors(),
            )

        # Normaliza o valor de 'env' para maiúsculas
        env = env.strip().upper()

        # Dicionário de ambientes válidos e URLs correspondentes
        valid_envs = {
            "DEV": "https://stonedev.service-now.com/api",
            "QA": "https://stoneqas.service-now.com/api",
            "QAS": "https://stoneqas.service-now.com/api",
            "PROD": "https://stone.service-now.com/api",
        }

        # Verifica se 'env' é válido
        if env not in valid_envs:
            raise ValueError(
                "O valor de 'env' precisa ser 'dev', 'qa', 'qas' ou 'prod'."
            )

        # Atribui as variáveis de instância
        self.__username = username.strip()
        self.__password = password.strip()
        self.env = env
        self.api_url = valid_envs[env]
        self.api_header = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def __auth(self):
        """
        Retorna o e-mail e senha para realizar a autenticação.
        """
        return (self.__username, self.__password)

    def request(self, url: str, params: str = "", timeout: int = 15):
        """
        Realiza uma requisição GET para a URL especificada.

        Parâmetros:
            url (str): URL para a qual a requisição será enviada.
            params (dict, opcional): Parâmetros de consulta (query parameters) a serem incluídos na requisição.
                Padrão é uma string vazia.

        Retorno:
            dict: Um dicionário contendo:
                - success (bool): Indica se a requisição foi bem-sucedida.
                - result (dict ou None): Resultado da resposta, se disponível. Contém o conteúdo JSON do campo "result".
                - error (Exception ou None): Objeto de exceção em caso de erro, ou None se não houver erros.

        Tratamento de exceções:
            - requests.exceptions.HTTPError: Lança um erro HTTP caso o código de status indique falha.
            - requests.exceptions.RequestException: Captura outros erros relacionados à requisição, como timeout ou conexão.
            - Exception: Captura erros inesperados.

        Logs:
            - Logs de depuração são gerados para erros HTTP, erros de requisição e exceções inesperadas.
            - Um aviso é registrado caso a resposta não contenha o campo "result".

        Observações:
            - Utiliza autenticação fornecida pelo método privado `__auth()`.
            - Define um tempo limite (`timeout`) de 15 segundos.
            - Verifica o certificado SSL (`verify=True`).
        """
        try:
            RequestValidator(url=url, params=params, timeout=timeout)
        except ValidationError as e:
            raise ValueError(
                "Erro na validação dos dados de input do método:", e.errors()
            )

        try:
            response = requests.get(
                url,
                params=params,
                auth=self.__auth(),
                headers=self.api_header,
                timeout=timeout,
                verify=True,
            )

            # VALIDA SE HOUVE SUCESSO NA REQUISIÇÃO
            response.raise_for_status()

            # Analisa o conteúdo da resposta JSON
            result = response.json()
            if "result" in result:
                return {"success": True, "result": result.get("result")}
            else:
                logging.debug("A resposta não contém o campo 'result'.")
                return {"success": False, "result": result}

        except requests.exceptions.HTTPError as http_err:
            logging.debug(f"Erro HTTP ao buscar os detalhes do ticket: {http_err}")
            return {"success": False, "result": None, "error": str(http_err)}

        except requests.exceptions.RequestException as req_err:
            logging.debug(f"Erro ao buscar os detalhes do ticket: {req_err}")
            return {"success": False, "result": None, "error": str(req_err)}

        except Exception as e:
            logging.debug(f"Erro inesperado: {e}")
            return {"success": False, "result": None, "error": str(e)}

    def __request_download(self, url, params="", timeout=15):
        """
        Realiza uma requisição GET para a URL especificada.

        Parâmetros:
            url (str): URL para a qual a requisição será enviada.
            params (dict, opcional): Parâmetros de consulta (query parameters) a serem incluídos na requisição.
                Padrão é uma string vazia.

        Retorno:
            dict: Um dicionário contendo:
                - success (bool): Indica se a requisição foi bem-sucedida.
                - result (dict ou None): Resultado da resposta, se disponível. Contém o conteúdo JSON do campo "result".
                - error (Exception ou None): Objeto de exceção em caso de erro, ou None se não houver erros.

        Tratamento de exceções:
            - requests.exceptions.HTTPError: Lança um erro HTTP caso o código de status indique falha.
            - requests.exceptions.RequestException: Captura outros erros relacionados à requisição, como timeout ou conexão.
            - Exception: Captura erros inesperados.

        Logs:
            - Logs de depuração são gerados para erros HTTP, erros de requisição e exceções inesperadas.
            - Um aviso é registrado caso a resposta não contenha o campo "result".

        Observações:
            - Utiliza autenticação fornecida pelo método privado `__auth()`.
            - Define um tempo limite (`timeout`) de 15 segundos.
            - Verifica o certificado SSL (`verify=True`).
        """
        try:
            response = requests.get(
                url,
                params=params,
                auth=self.__auth(),
                headers=self.api_header,
                timeout=timeout,
                verify=True,
            )

            # VALIDA SE HOUVE SUCESSO NA REQUISIÇÃO
            response.raise_for_status()
            # Analisa o conteúdo da resposta JSON
            if response.status_code == 200:
                return {"success": True, "result": response}
            else:
                logging.debug("Erro ao realizar a consulta")
                return {"success": False, "result": response.status_code}

        except requests.exceptions.HTTPError as http_err:
            logging.debug(f"Erro HTTP ao buscar os detalhes do ticket: {http_err}")
            return {"success": False, "error": str(http_err), "result": None}

        except requests.exceptions.RequestException as req_err:
            logging.debug(f"Erro ao buscar os detalhes do ticket: {req_err}")
            return {"success": False, "error": str(req_err), "result": None}

        except Exception as e:
            logging.debug(f"Erro inesperado: {e}")
            return {"success": False, "error": str(e), "result": None}

    def put(self, url, payload, timeout=15):
        """
        Realiza uma requisição PUT para a URL especificada.

        Parâmetros:
            url (str): URL para a qual a requisição será enviada.
            payload (dict): Dados a serem enviados no corpo da requisição. Será convertido para JSON.

        Retorno:
            dict: Um dicionário contendo:
                - success (bool): Indica se a requisição foi bem-sucedida.
                - result (dict ou None): Resultado da resposta, se disponível. Contém o conteúdo JSON do campo "result".

        Tratamento de exceções:
            - requests.exceptions.HTTPError: Lança um erro HTTP caso o código de status indique falha. O erro é registrado nos logs.
            - requests.exceptions.RequestException: Captura outros erros relacionados à requisição, como timeout ou problemas de conexão. O erro é registrado nos logs.
            - Exception: Captura erros inesperados e os registra nos logs.

        Logs:
            - Registra mensagens de depuração detalhadas quando a atualização é bem-sucedida ou quando a resposta não contém o campo "result".
            - Registra mensagens de erro para exceções HTTP, erros de requisição e outros erros inesperados.

        Observações:
            - Utiliza autenticação fornecida pelo método privado `__auth()`.
            - Define um tempo limite (`timeout`) de 15 segundos.
            - Verifica o certificado SSL (`verify=True`).
            - O cabeçalho da requisição é definido com `self.api_header`.
        """
        try:
            PutValidator(url=url, payload=payload, timeout=timeout)
        except ValidationError as e:
            raise ValueError(
                "Erro na validação dos dados de input do método:", e.errors()
            )

        payload = json.dumps(payload)

        try:
            response = requests.put(
                f"{url}",
                auth=self.__auth(),
                headers=self.api_header,
                data=f"{payload}",
                timeout=timeout,
                verify=True,
            )

            # VALIDA SE HOUVE SUCESSO NA REQUISIÇÃO
            response.raise_for_status()

            # POSSUINDO 'RESULT', TEREMOS O RETORNO DO TICKET ABERTO.
            result = response.json()
            if "result" in result:
                update = result["result"]
                logging.debug(
                    f"Atualização concluída com sucesso. Registro atualizado: {update['sys_id']} | Alterações: {payload}"
                )
                return {"success": True, "result": update}
            else:
                logging.debug(
                    f"A Resposta da sua requisição não contém o campo 'Result'. Segue o retorno: \n {result} | Alterações: {payload}"
                )
                return {"success": False, "result": result}

        # TRATAMENTOS DE ERRO
        except requests.exceptions.HTTPError as http_err:
            logging.debug(
                f"Erro HTTP ao tentar atualizar o ticket: {http_err} \n Reposta da solicitação: {response.json().get('error').get('message')}"
            )
            return {"success": False, "error": str(http_err), "result": None}

        except requests.exceptions.RequestException as req_err:
            logging.debug(f"Erro ao tentar atualizar o ticket: \n {req_err}")
            return {"success": False, "error": str(req_err), "result": None}

        except Exception as e:
            logging.debug(f"Erro inesperado: \n {e}")
            return {"success": False, "error": str(e), "result": None}

    def post(
        self, url: str, variables: dict, header_content_type="", timeout: int = 15
    ):
        """
        Função para criar um novo ticket no servicenow usando o API REST.

            Parametros:
                - Payload (Dict): Dicionário contendo os dados que serão utilizados para criar o ticket
            Retorno:
                - Dict: Um dicionário contendo os detalhes do ticket criado
            Raises:
                - Exception: Se ocorrer um erro ao criar o ticket.

        """
        try:
            PostValidator(url=url, variables=variables)
        except ValidationError as e:
            raise ValueError(
                "Erro na validação dos dados de input do método:", e.errors()
            )

        if header_content_type:
            header = header_content_type
        else:
            header = self.api_header

        # Ajustar o Payload para a abertura do ticket
        payload = {"sysparm_quantity": "1", "variables": json.dumps(variables)}
        try:
            response = requests.post(
                f"{url}",
                auth=self.__auth(),
                headers=header,
                data=f"{payload}",
                timeout=timeout,
            )

            # VALIDA SE HOUVE SUCESSO NA REQUISIÇÃO
            response.raise_for_status()

            # POSSUINDO 'RESULT', TEREMOS O RETORNO DO TICKET ABERTO.
            result = response.json()
            if "result" in result:
                ticket_number = result["result"].get("number")
                ticket_sys_id = result["result"].get("sys_id")
                logging.debug(
                    f"Ticket registrado com sucesso. Número: {ticket_number} | SYS_ID: {ticket_sys_id}"
                )
                return {"success": True, "result": result["result"]}
            else:
                logging.debug(
                    f"A Resposta da sua requisição não contém o campo 'Result'. Segue o retorno: \n {result}"
                )
                return {"success": False, "result": result}

        # TRATAMENTOS DE ERRO
        except requests.exceptions.HTTPError as http_err:

            logging.debug(
                f"Erro HTTP ao tentar registrar o ticket: {http_err} \n Reposta da solicitação: {response.json().get('error').get('message')}"
            )
            return {"success": False, "error": str(http_err), "result": None}

        except requests.exceptions.RequestException as req_err:
            logging.debug(f"Erro ao tentar registrar o ticket: \n {req_err}")
            return {"success": False, "error": str(req_err), "result": None}

        except Exception as e:
            logging.debug(f"Erro inesperado: \n {e}")
            return {"success": False, "error": str(e), "result": None}

    def listar_tickets(
        self,
        tabela: str = None,
        campos: list = None,
        query: str = None,
        limite: int = 50,
        timeout: int = 15,
        sysparm_display_value: str = "",
    ) -> dict:
        """lista tickets do ServiceNow

        Args:
            tabela (str): tabela do ServiceNow de onde a query será feita
            campos (list): lista de campos com valores a trazer
            query (str): query do ServiceNow
            limite (int, optional): quantidade máxima de tickets para trazer. Default=50
            timeout (int, optional): segundos para a requisicao dar timeout. Default=15

        Returns:
            dict: dicionário com o resultado da query
        """
        try:
            ListTicketValidator(
                tabela=tabela,
                campos=campos,
                query=query,
                limite=limite,
                timeout=timeout,
            )
        except ValidationError as e:
            raise ValueError(
                "Erro na validação dos dados de input do método:", e.errors()
            )

        params = {
            "sysparm_query": query,
            "sysparm_fields": ",".join(campos),
            "sysparm_display_value": sysparm_display_value,
            "sysparm_limit": limite,
        }

        url = f"{self.api_url}/now/table/{tabela}"

        try:
            response = self.request(url=url, params=params, timeout=timeout)
            return response

        except Exception as e:
            logging.debug(f"erro: {e}")
            return str(e)

    def update_ticket(
        self,
        tabela: str = None,
        sys_id: str = None,
        payload: dict = None,
        timeout: int = 15,
    ) -> dict:
        """Atualiza as informações de um ticket

        Args:
            tabela (str): Tabela do ServiceNow de onde o ticket pertence
            sys_id (str): sys_id do ticket a ser atualizado
            campos (dict): Dicionário com os dados a serem atualizados no ticket
            timeout (int, optional): segundos para a requisicao dar timeout. Default=15

        Returns:
            dict: resposta do ServiceNow
        """
        try:
            UpdateTicketValidator(
                tabela=tabela, sys_id=sys_id, payload=payload, timeout=timeout
            )
        except ValidationError as e:
            raise ValueError(
                "Erro na validação dos dados de input do método:", e.errors()
            )

        payload["assigned_to"] = self.__username

        try:

            url = f"{self.api_url}/now/table/{tabela}/{sys_id}"
            response = self.put(url, payload=payload, timeout=timeout)
            return response

        except Exception as e:
            return str(e)

    def anexar_arquivo_no_ticket(
        self,
        header_content_type: dict = None,
        anexo_path: str = None,
        tabela: str = None,
        sys_id: str = None,
        timeout: int = 15,
    ):
        """Anexa arquivo em um ticket do ServiceNow

        Args:
            header_content_type (dict): Dicionário contendo a chave 'Content-Type' com a especificação do tipo do arquivo
            anexo_path (str): Path do arquivo a ser anexado
            tabela (str): Tabela do ServiceNow de onde o ticket pertence
            sys_id (str): sys_id do ticket o qual o arquivo será anexado
            timeout (int, optional): segundos para a requisicao dar timeout. Default=15

        Returns:
            dict: resposta do ServiceNow
        """
        if header_content_type is None:
            header_content_type = self.__valida_header_content_type(
                anexo_path, header_content_type
            )

        try:
            AttachFileTicketValidator(
                header_content_type=header_content_type,
                anexo_path=anexo_path,
                tabela=tabela,
                sys_id=sys_id,
                timeout=timeout,
            )
        except ValidationError as e:
            raise ValueError(
                "Erro na validação dos dados de input do método:", e.errors()
            )

        if not os.path.exists(anexo_path):
            raise FileExistsError(f"O arquivo não foi encontrado ({anexo_path})")

        # Converte as chaves do dicionário para minúsculas
        header_content_type_lower = {
            k.lower(): v for k, v in header_content_type.items()
        }

        if "content-type" not in header_content_type_lower:
            raise ValueError(
                "O parâmetro 'header_content_type' não possui a chave 'Content-Type' com o tipo do anexo"
            )

        nome_arquivo = os.path.basename(anexo_path)
        try:
            with open(anexo_path, "rb") as f:
                url = f"{self.api_url}/now/attachment/file?table_name={tabela}&table_sys_id={sys_id}&file_name={nome_arquivo}"
                response = requests.post(
                    url,
                    headers=header_content_type,
                    auth=(self.__username, self.__password),
                    data=f,
                    timeout=timeout,
                )

            logging.debug("Arquivo adicionado no ticket")
            return {"success": True, "result": response}

        except Exception as e:
            return {"success": False, "result": None, "error": str(e)}

    def __valida_header_content_type(self, anexo_path, header_content_type):
        """
        Valida e define o cabeçalho `Content-Type` baseado na extensão do arquivo anexado.

        Parâmetros:
            anexo_path (str): Caminho do arquivo que será validado e utilizado para determinar o `Content-Type`.

        Funcionalidade:
            - Baseado na extensão do arquivo especificado, define um valor apropriado para `header_content_type` caso esteja ausente:
                - `.zip` → `application/zip`
                - `.xlsx` → `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`
                - `.pdf` → `application/pdf`
                - `.txt` → `text/plain`
            - Gera um erro se `header_content_type` não for do tipo `dict` após a definição.

        Erros:
            - ValueError: Caso `header_content_type` não seja um dicionário válido após as validações.

        Observação:
            - O parâmetro `header_content_type` é uma variável local utilizada para compor os cabeçalhos HTTP, contendo informações do tipo de conteúdo do arquivo.

        """

        # Pré validando 'header_content_type'
        if (
            os.path.splitext(anexo_path)[1].lower() == ".zip"
            and header_content_type is None
        ):

            header_content_type = {"Content-Type": "application/zip"}

        elif (
            os.path.splitext(anexo_path)[1].lower() == ".xlsx"
            and header_content_type is None
        ):

            header_content_type = {
                "Content-Type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            }

        elif (
            os.path.splitext(anexo_path)[1].lower() == ".pdf"
            and header_content_type is None
        ):

            header_content_type = {"Content-Type": "application/pdf"}

        elif (
            os.path.splitext(anexo_path)[1].lower() == ".txt"
            and header_content_type is None
        ):

            header_content_type = {"Content-Type": "text/plain"}

        # Validação de 'header_content_type'
        if not isinstance(header_content_type, dict):
            raise ValueError(
                "O parâmetro 'header_content_type' precisa ser um dicionário contendo o 'Content-Type' do arquivo a ser anexado. (Ex: {\"Content-Type\": \"application/zip\"})"
            )

        return header_content_type

    def download_anexo(self, sys_id_file: str, file_path: str, timeout: int = 15):
        """
        Faz o download de um anexo do ServiceNow utilizando o `sys_id` do arquivo e salva no caminho especificado.

        Parâmetros:
            sys_id_file (str): O identificador único (sys_id) do arquivo no ServiceNow.
            file_path (str): O caminho completo onde o arquivo será salvo localmente.
            timeout (int, opcional): O tempo limite, em segundos, para a requisição HTTP. Padrão é 15 segundos.

        Retorna:
            bool: Retorna `True` se o arquivo foi salvo com sucesso no caminho especificado.
            dict: Em caso de erro, retorna um dicionário com os seguintes campos:
                - "success" (bool): Indica se a operação foi bem-sucedida (`False` em caso de falha).
                - "error" (str): Mensagem de erro detalhada em caso de falha.
                - "path" (str, opcional): O caminho do arquivo salvo, caso tenha sido criado após a criação de diretórios.

        Comportamento:
            - Em caso de sucesso na requisição HTTP (status code 200), o arquivo é salvo no `file_path`.
            - Caso o caminho do arquivo não exista, tenta criá-lo automaticamente.
            - Registra logs de erros ou informações em caso de falha.

        Exceções Tratadas:
            - FileNotFoundError: Se o caminho especificado não existir, tenta criar os diretórios necessários.
            - Exception: Registra quaisquer outros erros inesperados durante o salvamento.

        Logs:
            - `logging.debug`: Para erros de salvamento no arquivo.
            - `logging.error`: Para erros genéricos durante o processo.
            - `logging.info`: Para informações sobre falhas na requisição HTTP.

        Exemplo:
            obj.download_anexo("abc123sysid", "/caminho/para/salvar/arquivo.txt")
            {'success': False, 'error': 'Status code: 404'}
        """
        try:
            DownloadFileValidator(sys_id_file=sys_id_file, file_path=file_path)
        except ValidationError as e:
            raise ValueError(
                "Erro na validação dos dados de input do método:", e.errors()
            )

        url = f"{self.api_url}/now/attachment/{sys_id_file}/file"
        response = self.__request_download(url=url, timeout=timeout)
        response = response.get("result")
        if response.status_code == 200:
            try:
                if not os.path.exists(file_path):
                    diretorio = os.path.dirname(file_path)
                    print(diretorio)
                    os.makedirs(diretorio, exist_ok=True)
                    logging.debug(f"Diretorio criado: {diretorio}")
                with open(file_path, "wb") as f:
                    f.write(response.content)
                return {"success": True, "path": file_path}

            except FileNotFoundError:
                try:
                    path = os.path.dirname(file_path)
                    os.makedirs(path)
                    with open(file_path, "wb") as f:
                        f.write(response.content)
                    return {"success": True, "path": file_path}
                except Exception as e:
                    logging.debug(f"Erro ao salvar o arquivo. Erro: {e}")
                return {"success": False, "error": str(e)}
            except Exception as e:
                logging.error(f"Erro ao salvar o arquivo. Erro: {e}")
                return {"success": False, "error": str(e)}
        else:
            logging.debug(f"{response.status_code}")
            return {"success": False, "error": f"Status code: {response.status_code }"}

    def get_variables_from_ticket(self, sys_id: str, campos: str = ""):
        """
        Obtém as variáveis associadas ao ticket.
        args:
            sys_id : STR - Id do ticket
        """
        if isinstance(campos, list):
            campos = ",".join(campos)
        if campos == "":
            campos = "name,question_text,type,default_value, sys_id"

        logging.debug(f"Obtendo variáveis do ticket {sys_id}")
        url = f"{self.api_url}/now/table/item_option_new"
        params = {
            "sysparm_query": f"cat_item={sys_id}",
            "sysparm_display_value": "true",
            "sysparm_fields": campos,
        }
        response = self.request(url, params=params)
        return response

    def get_anexo(
        self,
        sys_id: str = None,
        tabela: str = None,
        campo: str = "default",
        download_dir: str = None,
        timeout: int = 15,
    ) -> dict:
        """Traz os anexos de um campo do ticket especificado

        Args:
            sys_id (str): sys_id do ticket
            tabela (str): tabela do ticket
            campo (str, optional): campo do anexo
            timeout (int, optional): segundos para a requisicao dar timeout. Default=15

        Returns:
            dict: dicionário com os anexos do ticket
        """
        try:
            GetAttachValidator(
                sys_id=sys_id, tabela=tabela, timeout=timeout, download_dir=download_dir
            )
        except ValidationError as e:
            raise ValueError(
                "Erro na validação dos dados de input do método:", e.errors()
            )

        if download_dir is not None:
            if not isinstance(download_dir, str) or not download_dir.strip():
                raise ValueError(
                    "O parâmetro 'download_dir' precisa ser a pasta pra onde o anexo será feito o download."
                )
            if not os.path.exists(download_dir):
                raise NotADirectoryError(
                    f"A pasta informada '{download_dir}' não existe"
                )

        # Validação de 'campo'
        if not isinstance(campo, str) or not campo.strip():
            raise ValueError(
                "O parâmetro 'campo' precisa ser uma string não vazia com o nome do campo do anexo."
            )

        campo = str(campo).strip().lower()

        # Convert bytes to base64
        def __bytes_to_base64(image_bytes):

            return base64.b64encode(image_bytes).decode("utf-8")

        def __formatar_tamanho(tamanho_bytes):
            # Converte o valor de string para inteiro
            tamanho_bytes = int(tamanho_bytes)

            # Define os múltiplos de bytes
            unidades = ["B", "KB", "MB", "GB", "TB"]

            # Itera sobre as unidades até encontrar a maior possível
            for unidade in unidades:
                if tamanho_bytes < 1024:
                    return f"{tamanho_bytes:.2f} {unidade}"
                tamanho_bytes /= 1024

            # Caso o valor seja maior que o esperado (Exabyte ou superior)
            return f"{tamanho_bytes:.2f} PB"  # Petabyte

        anexo_dict = {"var_servicenow": campo, "anexos": []}

        try:
            if campo == "default":
                url = f"{self.api_url}/now/attachment?sysparm_query=table_name={tabela}^table_sys_id={sys_id}"
                response = self.__request_download(url, timeout=timeout)
                response = response.get("result")
                if response.status_code == 200:
                    for attachment in response.json().get("result", []):
                        arquivo = {
                            "file_name": attachment["file_name"],
                            "size": __formatar_tamanho(attachment["size_bytes"]),
                            "content_type": attachment["content_type"],
                            "base64": None,
                        }
                        byte_response = self.__request_download(
                            attachment["download_link"], timeout=timeout
                        )
                        byte_response = byte_response.get("result")
                        if byte_response.status_code == 200:
                            arquivo["base64"] = __bytes_to_base64(byte_response.content)
                            if download_dir:
                                with open(
                                    os.path.join(download_dir, arquivo["file_name"]),
                                    "wb",
                                ) as f:
                                    f.write(byte_response.content)
                            anexo_dict["anexos"].append(arquivo)
                    return {"success": True, "result": anexo_dict}
                return {
                    "success": False,
                    "error": response.json(),
                    "status_code": response.status_code,
                }

            else:
                url = f"{self.api_url}/now/table/{tabela}?sysparm_query=sys_id={sys_id}&sysparm_fields={campo}&sysparm_display_value=all"
                response = self.__request_download(url, timeout=timeout)
                response = response.get("result")
                if response.status_code == 200 and response.json().get("result"):
                    campo_data = response.json()["result"][0].get(campo)
                    if campo_data:
                        attachment_id = campo_data["value"]
                        attachment_url = (
                            f"{self.api_url}/now/attachment/{attachment_id}/file"
                        )
                        byte_response = self.__request_download(
                            attachment["download_link"], timeout=timeout
                        )
                        byte_response = byte_response.get("result")
                        if byte_response.status_code == 200:
                            arquivo = {
                                "file_name": campo_data["display_value"],
                                "size": __formatar_tamanho(
                                    byte_response.headers.get("Content-Length", 0)
                                ),
                                "content_type": byte_response.headers.get(
                                    "Content-Type"
                                ),
                                "base64": __bytes_to_base64(byte_response.content),
                            }
                            if download_dir:
                                with open(
                                    os.path.join(download_dir, arquivo["file_name"]),
                                    "wb",
                                ) as f:
                                    f.write(byte_response.content)
                            anexo_dict["anexos"].append(arquivo)
                    return {"success": True, "result": anexo_dict, "error": None}
                return {
                    "success": False,
                    "error": response.json(),
                    "status_code": response.status_code,
                }

        except Exception as e:
            logging.debug("Erro ao obter anexos.")
            return {"success": False, "error": str(e)}
        
    def criar_task(self, payload: dict, header_content_type: dict = None, timeout: int = 15):
        """
        Cria uma nova task no ServiceNow utilizando os dados fornecidos no payload.
        Args:
            payload (dict): Dicionário contendo os dados necessários para criação da task.
            header_content_type (dict, opcional): Cabeçalho HTTP personalizado para a requisição. Se não informado, utiliza o cabeçalho padrão da instância.
            timeout (int, opcional): Tempo limite (em segundos) para a requisição HTTP. Padrão é 15 segundos.
        Returns:
            dict: Dicionário contendo o resultado da operação.
                - Se sucesso: {"success": True, "result": <dados da task criada>}
                - Se falha: {"success": False, "error": <mensagem de erro>, "result": None}
        Raises:
            TypeError: Se o payload não for um dicionário.
        Observações:
            - Realiza tratamento de erros HTTP, de requisição e erros inesperados, registrando logs para depuração.
        """
        if not isinstance(payload, dict):
            raise TypeError("Payload deve ser um dicionário.")
        if not isinstance(timeout, int):
            raise TypeError("Timeout deve ser um inteiro.")

        if header_content_type:
            header = header_content_type
        else:
            header = self.api_header
        data = json.dumps(payload)
        url = f"{self.api_url}/now/table/sc_task"
        try:
            response = requests.post(
                f"{url}",
                auth=self.__auth(),
                headers=header,
                data=data,
                timeout=timeout,
            )
            response.raise_for_status()

            result = response.json()

            return {"success": True, "result": result["result"]} if "result" in result else {"success": False, "result": result}
        
        # TRATAMENTOS DE ERRO
        except requests.exceptions.HTTPError as http_err:

            logging.debug(
                f"Erro HTTP ao tentar registrar o ticket: {http_err} \n Reposta da solicitação: {response.json().get('error').get('message')}"
            )
            return {"success": False, "error": str(http_err), "result": None}

        except requests.exceptions.RequestException as req_err:
            logging.debug(f"Erro ao tentar registrar o ticket: \n {req_err}")
            return {"success": False, "error": str(req_err), "result": None}

        except Exception as e:
            logging.debug(f"Erro inesperado: \n {e}")
            return {"success": False, "error": str(e), "result": None}
