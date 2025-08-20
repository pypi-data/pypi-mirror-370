from google.cloud import bigquery
from google.oauth2 import service_account
from pydantic import ValidationError
from .utilitarios.validations.GcpBigQueryValidator import tryQueryValidator, InitParamsValidator, tryInsertListValidator

class BigQuery():


    def __init__(self, id_project: str, creds_dict: dict = None, creds_file: str = "", limit: int = 3):
        
        """
        Inicializa a classe BigQuery.
        Parâmetros:
        limit (int): O limite de resultados a serem retornados. O valor padrão é 3.
        client (bigquery.Client): O cliente BigQuery a ser utilizado.
        """

        self.limit = limit
        self.id_project = id_project
        self.creds_dict = creds_dict
        self.creds_file = creds_file
        self.client = self.create_client()

        try:
        
            InitParamsValidator(limit=limit, id_project=id_project, creds_dict=creds_dict, creds_file=creds_file)

        except ValidationError as e:
        
            raise ValueError("Erro na validação dos dados de input da inicialização da instância:", e.errors())


    def create_client(self) -> bigquery.Client:
        """
        Cria um cliente BigQuery com base nas credenciais fornecidas.
        Parâmetros:
        - creds_dict (dict): Dicionário contendo as informações das credenciais. Opcional se creds_file for fornecido.
        - creds_file (str): Caminho do arquivo de credenciais. Opcional se creds_dict for fornecido.
        - id_project (str): ID do projeto BigQuery.
        Retorna:
        - client (bigquery.Client): Cliente BigQuery criado com base nas credenciais fornecidas.
        Exceções:
        - Retorna um dicionário com as seguintes chaves em caso de erro:
            - 'status' (bool): False
            - 'error' (str): Mensagem de erro
            - 'details' (str): Detalhes do erro
        """

        try:

            if(self.creds_dict is not None):

                credentials = service_account.Credentials.from_service_account_info(
                    self.creds_dict,
                    scopes=["https://www.googleapis.com/auth/cloud-platform"],
                )

                client = bigquery.Client(credentials=credentials, project=self.id_project)

            elif(str(self.creds_file) > 0):

                credentials = service_account.Credentials.from_service_account_file(
                    self.creds_file,
                    scopes=["https://www.googleapis.com/auth/cloud-platform"],
                )

            else:

                raise ValueError("Credenciais não fornecidas")
            
            return client
        
        except Exception as e:
            
            raise ValueError("Erro ao criar o cliente BigQuery:", e)


    def try_query(self, query_to_execute: str, organize: bool = False, use_legacy: bool = False, use_cache: bool = False, query_parameters: list = []) -> dict:

        """
        Executa uma consulta no BigQuery e retorna o resultado.
        Args:
            query_to_execute (str): A consulta a ser executada.
            organize (bool, optional): Indica se o resultado deve ser organizado em um formato específico. 
                O padrão é True.
        Returns:
            dict: Um dicionário contendo o status da consulta e o resultado, se houver.
                Exemplo:
                {
                    'status': True,
                    'resultado': result_query
                Se ocorrer um erro durante a execução da consulta, o dicionário de retorno terá o seguinte formato:
                {
                    'status': False,
        """
        
        try:

            tryQueryValidator(query_to_execute=query_to_execute, organize=organize, use_legacy=use_legacy, use_cache=use_cache, query_parameters=query_parameters)

        except ValidationError as e:
        
            raise ValueError("Erro na validação dos dados de input da função para tentar executar a query:", e.errors())

        error = ""

        job_config = bigquery.QueryJobConfig(
            priority=bigquery.QueryPriority.INTERACTIVE,
            use_legacy_sql=use_legacy,
            use_query_cache=use_cache,
            query_parameters=[
                bigquery.ScalarQueryParameter(param["name"], param["type"], param["value"]) for param in query_parameters
            ],
        )

        for try_out in range(self.limit):

            try:

                result_query = self.client.query(query_to_execute,job_config=job_config).result()

                error = False

                if organize:

                    result_rows = [dict(row) for row in result_query]

                    result_query = result_rows

                break

            except Exception as e:

                error = e

        if not error:

            return {
                'status':True,
                'resultado':result_query
            }

        else:

            return {
                'status':False,
                'error': str(error)
            }


    def insert_list(self, table: str, list_to_insert: list = [], insert_limit: int = 10000) -> dict:
        
        """
        Insere uma lista de dicionários em uma tabela do BigQuery.
        Args:
            client (bigquery.Client): Cliente do BigQuery.
            table (str): Nome da tabela onde os dados serão inseridos.
            list_to_insert (dict, optional): Lista de dicionários a serem inseridos. O padrão é [].
            limit_trys (int, optional): Número máximo de tentativas de inserção. O padrão é 3.
        Returns:
            dict: Dicionário contendo o status da inserção e informações adicionais.
                - Se a inserção for bem-sucedida:
                    {'status': True, 'inserted': inserted}
                - Se ocorrer um erro durante a inserção:
                    {'status': False, 'error': error, 'last_try': list_to_insert, 'inserted': inserted}
        """

        try:

            tryInsertListValidator(table=table, list_to_insert=list_to_insert, insert_limit=insert_limit)

        except ValidationError as e:
        
            raise ValueError("Erro na validação dos dados de input da função para tentar inserir dados em uma tabela:", e.errors())

        table_ref = self.client.get_table(table)

        error = ""

        inserted = []

        for data in range(0, len(list_to_insert), insert_limit):

            # listagem que será inserida no big query
            list_to_insert = list_to_insert[data:data+10000]

            for try_out in range(self.limit):

                try:

                    self.client.insert_rows(table_ref, list_to_insert)

                    error = False

                except Exception as e:

                    error = e

            if not error:

                inserted.extend(list_to_insert)

                continue

            else:

                return{
                    'status':False,
                    'error':str(error),
                    'last_try':list_to_insert,
                    'inserted':inserted
                }
            
        return {
            'status':True,
            'inserted':inserted
        }
