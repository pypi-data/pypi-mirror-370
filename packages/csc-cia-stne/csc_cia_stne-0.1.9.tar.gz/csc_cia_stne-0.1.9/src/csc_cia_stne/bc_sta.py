import logging
import hashlib
import requests
from requests.auth import HTTPBasicAuth
import xml.etree.ElementTree as ET
from xml.dom.minidom import parseString
from pydantic import BaseModel, ValidationError, field_validator, Field, HttpUrl
from typing import Literal, Dict, Union, Optional, List
from datetime import datetime

log = logging.getLogger('__main__')

def xml_to_dict(element):
    """Converte um elemento XML recursivamente para um dicionário."""
    if not list(element):  # Se não tem filhos, retorna apenas o texto
        return element.text.strip() if element.text else ""

    result = {}
    for child in element:
        child_data = xml_to_dict(child)
        if child.tag in result:
            if isinstance(result[child.tag], list):
                result[child.tag].append(child_data)
            else:
                result[child.tag] = [result[child.tag], child_data]
        else:
            result[child.tag] = child_data

    if element.attrib:
        result["@atributos"] = element.attrib  # Adiciona atributos XML se existirem

    return result

def xml_response_to_json(response_text):
    """Converte a resposta XML para um dicionário JSON válido."""

    root = ET.fromstring(response_text)
    lista = xml_to_dict(root)
    if not isinstance(lista, dict):
        return []
    return list(lista.values())[0]  # Agora retorna um dicionário em vez de uma string JSON

def print_element(element, indent=0):
    """Função recursiva para exibir campos e subcampos"""
    prefix = " " * (indent * 2)  # Indentação para visualização hierárquica
    print(f"{prefix}- {element.tag}: {element.text.strip() if element.text else ''}")
    
    # Se o elemento tiver atributos, exibir
    if element.attrib:
        print(f"{prefix}  Atributos: {element.attrib}")
    
    # Percorrer subelementos
    for child in element:
        print_element(child, indent + 1)

# Validações dos inputs
class InitParamsValidator(BaseModel):
    """
    Classe responsável por validar os parâmetros de inicialização.
    Atributos:
        usuario (str): O nome de usuário.
        senha (str): A senha do usuário.
        ambiente (Literal["prd", "hml"]): O ambiente, que pode ser "prd" (produção) ou "hml" (homologação).
    Métodos:
        check_non_empty_string(value, info): Método de validação para garantir que cada parâmetro é uma string não vazia.
    """
        
    usuario: str
    senha: str
    ambiente: Literal["prd", "hml"]  # Aceita apenas "prd" ou "sdx"

    # Validação para garantir que cada parâmetro é uma string não vazia
    """
    Método de validação para garantir que cada parâmetro é uma string não vazia.
    Parâmetros:
        value (Any): O valor do parâmetro a ser validado.
        info (FieldInfo): As informações do campo a ser validado.
    Retorna:
        value (Any): O valor do parâmetro validado.
    Lança:
        ValueError: Se o valor do parâmetro não for uma string não vazia.
    """
    @field_validator('usuario', 'senha')
    def check_non_empty_string(cls, value, info):
        if not isinstance(value, str) or not value.strip():
            
            raise ValueError(f"O parâmetro '{info.field_name}' deve ser uma string não vazia.")
        
        return value

class EnviarArquivoValidator(BaseModel):
    """
    Classe responsável por validar os parâmetros de envio de arquivo.
    Args:
        tipo_arquivo (str): O código do tipo de envio a ser utilizado para o STA.
            Verificar códigos disponíveis na documentação STA.
        file_content (bytes): O conteúdo do arquivo a ser enviado, em formato de bytes.
        nome_arquivo (str): O nome do arquivo a ser enviado.
            Deve ser uma string não vazia e terminar com uma extensão de arquivo comum.
        observacao (str): A observação relacionada ao envio do arquivo.
            Deve ser uma string não vazia.
        destinatarios (Optional[Union[Dict[str, str], str]], optional): Os destinatários do arquivo.
            Pode ser um dicionário ou uma string XML. Defaults to None.
    Raises:
        ValueError: Se algum dos parâmetros não atender às condições de validação.
    Returns:
        O valor de cada parâmetro, se a validação for bem-sucedida.
    """
    tipo_arquivo:str
    file_content:bytes
    nome_arquivo:str
    observacao:str
    destinatarios:Optional[Union[Dict[str, str], str]] = None  # Aceita um dicionário
    
    @field_validator("tipo_arquivo")
    def check_tipo_arquivo(cls, value):
        if not isinstance(value, str) or not value.strip():
    
            raise ValueError("O parâmetro 'tipo_arquivo' deve ser uma string não vazia, com o código do tipo de envio a ser utilizado para o STA, verificar codigos disponíveis na documentação STA")
    
        return value
    
    # Validador para file_content: deve ter conteúdo em bytes
    @field_validator("file_content")
    def check_file_content(cls, value):
        if not isinstance(value, bytes) or len(value) == 0:
            raise ValueError("O parâmetro 'file_content' deve ser um byte array não vazio.")
        return value
    
    # Validador para nome_arquivo: deve ser uma string não vazia e terminar com uma extensão de arquivo comum
    @field_validator("nome_arquivo")
    def check_nome_arquivo(cls, value):
        if not isinstance(value, str) or not value.strip():
            raise ValueError("O nome do arquivo deve ser uma string não vazia.")
        if not value.lower().endswith(('.zip', '.xpto')):
            raise ValueError("O nome do arquivo deve ter uma extensão válida.")
        return value
    
    @field_validator("observacao")
    def check_observacao(cls, value):
        if not isinstance(value, str) or not value.strip():
    
            raise ValueError("O parâmetro 'observacao' deve ser uma string não vazia")
    
        return value

    # Validador para destinatarios: aceita um dicionário ou uma string XML opcional
    @field_validator("destinatarios")
    def check_destinatarios(cls, value):
        if value is not None:
            
            if not isinstance(value, list):
            
                raise ValueError("O parâmetro 'destinatarios' deve ser uma lista de dicionários.")
            
            for item in value:
            
                if not isinstance(item, dict):
            
                    raise ValueError("Cada destinatário deve ser um dicionário.")
            
                required_keys = {"unidade", "dependencia", "operador"}
            
                if not required_keys.issubset(item.keys()):
            
                    raise ValueError("Cada destinatário deve conter as chaves 'unidade', 'dependencia' e 'operador'. Verifique a documentação da API BC STA para entender o que colocar cada campo")
        
        return value

class ListarArquivosParams(BaseModel):
    """
    Parâmetros para listar arquivos disponíveis na API STA.

    Atributos:
        nivel (str): Nível de detalhe da consulta. Aceita apenas 'RES', 'BAS' ou 'COMPL'.
        inicio (str): Data e hora de início no formato ISO 8601 (yyyy-MM-ddTHH:mm:ss).
        fim (str): Data e hora de fim no formato ISO 8601 (yyyy-MM-ddTHH:mm:ss).
        situacao (Optional[str]): Situação da transmissão, podendo ser 'REC' ou 'A_REC'.
        identificadorDocumento (Optional[str]): Identificador do documento, se aplicável.
        qtd (int): Quantidade máxima de resultados (valor padrão: 100, máximo permitido: 100).
        tipo_arquivo (list): lista de tipos de arquivo para filtrar ['ACCS002','ACCS003','AJUD301','AJUD302','AJUD303','AJUD304','AJUD305','AJUD308','AJUD309','AJUD310','AJUD331','AMES102','AMTF102','ASVR9810','ATXB001']
    """
    nivel: Literal['RES', 'BAS', 'COMPL']
    #inicio: str = Field(..., regex=r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}$")
    inicio: str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}$")
    fim: Optional[str] = Field(None, pattern=r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}$")
    situacao: Optional[Literal['REC', 'A_REC']] = None
    identificadorDocumento: Optional[str] = None
    qtd: int = Field(default=100, le=100)
    #tipo_arquivo: Optional[str] = None
    tipo_arquivo: Optional[List[
        Literal[
            'ACCS002', 'ACCS003', 'AJUD301', 'AJUD302', 'AJUD303', 'AJUD304', 'AJUD305', 'AJUD308',
            'AJUD309', 'AJUD310', 'AJUD331', 'AMES102', 'AMTF102', 'ASVR9810', 'ATXB001'
        ]
    ]] = None

class DownloadArquivoParams(BaseModel):
    protocolo: str = Field(..., min_length=1, description="Código do protocolo")
    filename: Optional[str] = Field(None, description="Nome e caminho do arquivo")

class DownloadArquivoResponse(BaseModel):
    success: bool = Field(..., description="Indica se o download foi bem-sucedido")
    status_code: int = Field(..., ge=100, le=599, description="Código de status HTTP")
    content: Union[bytes, str] = Field(..., description="Conteúdo do arquivo (em bytes se sucesso, em string se erro)")

class BC_STA:
    
    def __init__(self, usuario:str, senha:str, ambiente:str):
        """
        Inicializa uma instância da classe BC_STA.
        Parâmetros:
        - usuario (str): O nome de usuário para autenticação.
        - senha (str): A senha para autenticação.
        - ambiente (str): O ambiente de execução ('prd' para produção ou qualquer outro valor para ambiente de teste).
        Raises:
        - ValueError: Se houver erro na validação dos dados de input da inicialização da instância 'BC_STA'.
        Exemplo de uso:
        ```
        bc_sta = BC_STA(usuario='meu_usuario', senha='minha_senha', ambiente='prd')
        ```
        """

        try:
            
            InitParamsValidator(usuario=usuario, senha=senha, ambiente=ambiente)
        
        except ValidationError as e:
        
            raise ValueError("Erro na validação dos dados de input da inicialização da instância 'BC_STA':", e.errors())
        
        if ambiente == 'prd':
            
            self.base_url = "https://sta.bcb.gov.br/staws"
        
        else:
            
            self.base_url = "https://sta-h.bcb.gov.br/staws"
        
        try:

            self.auth = HTTPBasicAuth(usuario,senha)
            self.error = None
            self.headers = {'Content-Type': 'application/xml'}
            self.is_connected = self.verifica_conexao()

        except Exception as e:

            self.is_connected = False
            self.error = e
    
    def verifica_conexao(self):
        """
        Verifica a conexão com o servidor STA do Banco Central do Brasil.
        Returns:
            bool: True se a conexão for bem-sucedida, False caso contrário.
        Raises:
            Exception: Se ocorrer algum erro durante a verificação da conexão.
        Example:
            # Criando uma instância da classe
            bc_sta = BCSTA()
            # Verificando a conexão
            conexao = bc_sta.verifica_conexao()
        """
        try:

            response = requests.get("https://sta.bcb.gov.br/staws/arquivos?tipoConsulta=AVANC&nivelDetalhe=RES", auth=self.auth)
            
            # Verificando o status e retornando a resposta
            if response.status_code == 200:

                return True

            else:

                return False


        except Exception as e:

            raise e

    def enviar_arquivo(self, tipo_arquivo:str, file_content:bytes, nome_arquivo:str, observacao:str, destinatarios:dict=None):
        """
        Envia um arquivo para um determinado destino.
            tipo_arquivo (str): O tipo de arquivo a ser enviado.
            nome_arquivo (str): O nome do arquivo.
            observacao (str): Uma observação opcional.
            destinatarios (dict, optional): Um dicionário contendo informações sobre os destinatários do arquivo. 
                O dicionário deve ter a seguinte estrutura:
                {
                    'unidade': 'nome_da_unidade',
                    'dependencia': 'nome_da_dependencia',  # opcional
                    'operador': 'nome_do_operador'  # opcional
                O campo 'dependencia' e 'operador' são opcionais.
                - 'enviado': Um valor booleano indicando se o arquivo foi enviado com sucesso.
                - 'protocolo': O protocolo gerado, caso o arquivo tenha sido enviado com sucesso.
                - 'link': O link do arquivo, caso tenha sido enviado com sucesso.
                - 'erro': Uma mensagem de erro, caso ocorra algum problema no envio do arquivo.
            ValueError: Se ocorrer um erro na validação dos dados de entrada.
            Exception: Se ocorrer um erro durante o envio do arquivo.
            # Exemplo de chamada da função
            tipo_arquivo = 'documento'
            nome_arquivo = 'arquivo.txt'
            observacao = 'Este é um arquivo de teste'
            destinatarios = {
                'unidade': 'unidade_destino',
                'dependencia': 'dependencia_destino',
                'operador': 'operador_destino'
            resposta = enviar_arquivo(tipo_arquivo, file_content, nome_arquivo, observacao, destinatarios)
        """
        try:
            
            EnviarArquivoValidator(tipo_arquivo=tipo_arquivo, file_content=file_content, nome_arquivo=nome_arquivo, observacao=observacao, destinatarios=destinatarios)
        
        except ValidationError as e:
        
            raise ValueError("Erro na validação dos dados de input do método 'enviar_arquivo':", e.errors())

        def generate_sha256_hash(file_content):
            """
            Gera o hash SHA-256 do conteúdo de um arquivo.
            Args:
                file_content (bytes): O conteúdo do arquivo como uma sequência de bytes.
            Returns:
                str: O hash SHA-256 do conteúdo do arquivo.
            Example:
                file_content = b'Lorem ipsum dolor sit amet'
                hash_value = generate_sha256_hash(file_content)
                print(hash_value)
            """
            
            # Gera o hash SHA-256 do arquivo
            sha256_hash = hashlib.sha256()
            sha256_hash.update(file_content)
            return sha256_hash.hexdigest()

        def process_response(xml_content):
            """
            Processa o conteúdo XML de resposta e retorna um dicionário com as informações relevantes.
            Args:
                xml_content (str): O conteúdo XML de resposta.
            Returns:
                dict: Um dicionário contendo as seguintes chaves:
                    - 'enviado': Um valor booleano indicando se o XML foi enviado com sucesso.
                    - 'protocolo': O protocolo extraído do XML, caso tenha sido enviado com sucesso.
                    - 'link': O link extraído do XML, caso tenha sido enviado com sucesso.
                    - 'erro': Uma mensagem de erro, caso ocorra algum problema no processamento do XML.
            Raises:
                None
            Exemplo de uso:
                xml = "<root>...</root>"
                resposta = process_response(xml)
                print(resposta)
            """

            try:

                root = ET.fromstring(xml_content)

                # Verifica se há um elemento <Erro> no XML
                erro = None
                erro_elem = root.find('Erro')
                
                if erro_elem is not None:
                
                    codigo_erro = erro_elem.find('Codigo').text
                    descricao_erro = erro_elem.find('Descricao').text
                    erro = f"Erro {codigo_erro}: {descricao_erro}"
                    resposta = {
                        'enviado':False,
                        'protocolo': None,
                        'link': None,
                        'erro': erro
                        }                                    

                else:

                    protocolo = root.find('Protocolo').text
                    link = root.find('.//atom:link', namespaces={'atom': 'http://www.w3.org/2005/Atom'}).attrib['href']
                    resposta = {
                        'enviado':True,
                        'protocolo': protocolo,
                        'link': link,
                        'erro': None
                        }

                return resposta

            except ET.ParseError as e:

                resposta = {
                    'enviado': False,
                    'protocolo': None,
                    'link': None,
                    'erro': f"Error processing XML: {str(e)}"
                }
                return resposta
        
        url = self.base_url + '/arquivos'

        # Calcula o hash SHA-256 do conteúdo do arquivo
        hash_sha256 = generate_sha256_hash(file_content)
        tamanho_arquivo = len(file_content)  # Tamanho do arquivo em bytes

        # Constrói o XML de requisição
        parametros = ET.Element('Parametros')
        ET.SubElement(parametros, 'IdentificadorDocumento').text = tipo_arquivo
        ET.SubElement(parametros, 'Hash').text = hash_sha256
        ET.SubElement(parametros, 'Tamanho').text = str(tamanho_arquivo)
        ET.SubElement(parametros, 'NomeArquivo').text = nome_arquivo
        
        # Campo observação é opcional
        if observacao:
            ET.SubElement(parametros, 'Observacao').text = observacao

        # Campo destinatários é opcional
        if destinatarios:

            destinatarios_elem = ET.SubElement(parametros, 'Destinatarios')

            for dest in destinatarios:

                destinatario_elem = ET.SubElement(destinatarios_elem, 'Destinatario')
                ET.SubElement(destinatario_elem, 'Unidade').text = dest['unidade']

                if 'dependencia' in dest:

                    ET.SubElement(destinatario_elem, 'Dependencia').text = dest['dependencia']

                if 'operador' in dest:

                    ET.SubElement(destinatario_elem, 'Operador').text = dest['operador']

        # Converte o XML para string
        xml_data = ET.tostring(parametros, encoding='utf-8', method='xml')

        # Envia a requisição POST
        response = requests.post(url, headers=self.headers, data=xml_data, auth=self.auth, timeout=60)

        if response.status_code == 201:  # Verifica se o protocolo foi criado com sucesso
            
            resultado_protocolo = process_response(response.text)
            
            # Protocolo gerado, prosseguir com envio do arquivo
            if resultado_protocolo["enviado"]:
                
                try:
                    
                    # Solicita o envio
                    protocolo = resultado_protocolo["protocolo"]
                    # URL do endpoint, incluindo o protocolo
                    url = url + f"/{protocolo}/conteudo"

                    # Envia a requisição PUT com o conteúdo binário do arquivo
                    response = requests.put(url, data=file_content, auth=self.auth, timeout=60)
                    
                    if response.status_code == 200:
                    
                        return resultado_protocolo
                    
                    else:
                    
                        resposta = {
                            'enviado':False,
                            'protocolo': None,
                            'link': None,
                            'erro': f"Falha ao enviar arquivo. Status code: {response.status_code}, Text: {response.text}, Reason: {response.reason}"
                            }
                        return resposta

                except Exception as e:
                    
                    erro = str(e)
                    resposta = {
                        'enviado':False,
                        'protocolo': None,
                        'link': None,
                        'erro': erro
                        }
                    return resposta



            # Protocolo não foi gerado, retornar erro
            else:
            
                return resultado_protocolo

        else:

            print(response.text)
            resposta = {
                'enviado': False,
                'protocolo': None,
                'link': None,
                'erro': f"Failed to create protocol. Status code: {response.status_code}, Reason: {response.reason}"
            }
            #return f"Failed to create protocol. Status code: {response.status_code}, Reason: {response.reason}"
            return resposta

    def listar_arquivos(self, nivel: Literal['RES', 'BAS', 'COMPL'], inicio: str, fim: str = None,situacao: Optional[Literal['REC', 'A_REC']] = None, identificadorDocumento: Optional[str] = None, qtd: int = 100, tipo_arquivo:list=None):
        """Lista os arquivos do STA com os parâmetros informados.

        Args:
            nivel (Literal['RES', 'BAS', 'COMPL']): nivel de detalhamento da consulta
            inicio (str): data de inicio, no padrao 'AAAA-MM-DDTHH:MM:SS'
            fim (str, optional): data de fim da consulta, no padrao 'AAAA-MM-DDTHH:MM:SS'
            situacao (Optional[Literal['REC', 'A_REC']], optional): Arquivos já recebidos ou ainda não recebidos. Default=None (Todos).
            identificadorDocumento (Optional[str], optional): Identificador documento. Default=None (Todos).
            qtd (int, optional): Quantidade de arquivos na resposta. Default=100 (máximo=100).
            tipo_arquivo (list, optional): Tipo de arquivo para fazer download. Default=None (Todos). Opções: ['ACCS002', 'ACCS003', 'AJUD301', 'AJUD302', 'AJUD303', 'AJUD304', 'AJUD305', 'AJUD308', 'AJUD309', 'AJUD310', 'AJUD331', 'AMES102', 'AMTF102', 'ASVR9810', 'ATXB001'].

        Returns:
            list: Lista de arquivos do STA
        """
        resultados = []
        ultima_data = inicio

        while True:
            params = ListarArquivosParams(nivel=nivel, inicio=ultima_data, fim=fim, situacao=situacao, identificadorDocumento=identificadorDocumento, qtd=qtd, tipo_arquivo=tipo_arquivo)
            
            url = f"{self.base_url}/arquivos?tipoConsulta=AVANC&nivelDetalhe={params.nivel}"
            url += f"&dataHoraInicio={params.inicio}&situacaoTransmissao={params.situacao}" if params.situacao else ""
            url += f"&identificadorDocumento={params.identificadorDocumento}" if params.identificadorDocumento else ""
            url += f"&dataHoraFim={params.fim}" if params.fim else ""
            url += f"&qtdMaxResultados={params.qtd}"

            response = requests.get(
                url,
                headers=self.headers,
                auth=self.auth, 
                timeout=60,
            )

            if response.status_code == 200:
        
                try:
        
                    dados = xml_response_to_json(response.text)

                    if not dados:  # Verifica se a lista está vazia
        
                        break  # Sai do loop se não houver mais dados
                    
                    # Filtra apenas os arquivos do tipo 'AJUD308'
                    if tipo_arquivo is not None:

                        if isinstance(dados, list):
                            dados_filtrados = [arquivo for arquivo in dados if arquivo.get("TipoArquivo") in tipo_arquivo]
                        elif dados.get("TipoArquivo") in tipo_arquivo:
                            dados_filtrados = [dados]

                        resultados.extend(dados_filtrados)

                    else:

                        resultados.extend(dados)

                    # Verifica se o campo 'DataHoraDisponibilizacao' existe no último registro
                    if dados and isinstance(dados, list) and 'DataHoraDisponibilizacao' in dados[-1]:

                        ultima_data = dados[-1]['DataHoraDisponibilizacao']  # Atualiza a data para a próxima requisição

                    elif dados and isinstance(dados, dict) and 'DataHoraDisponibilizacao' in dados:
                        
                        ultima_data = dados['DataHoraDisponibilizacao']  # Atualiza a data para a próxima requisição
                    
                    else:

                        log.error("Campo 'DataHoraDisponibilizacao' não encontrado ou estrutura inesperada.")
                        return False

                except ET.ParseError as e:

                    log.error(f"Erro ao processar XML: {e}")
                    return False
        
            else:
                
                log.error(f"Erro ao listar arquivos: response code {response.status_code}\n{response.text}")
                return False
        
        return resultados
    
    def download_arquivo(self,protocolo:str,filename:str=None):
        """Faz o download de um arquivo de um protocolo especifico

        Args:
            protocolo (str): protocolo
            filename (str): path+nome do arquivo

        Returns:
            dict: {"success": bool, "status_code": int, "content": bytes/str}
        """
        
        # Validação dos parâmetros
        try:
        
            params = DownloadArquivoParams(protocolo=protocolo, filename=filename)
        
        except ValidationError as e:
        
            return Exception(str(e))
        
        url = f"/arquivos/{protocolo}/conteudo"
        response = requests.get(
            self.base_url + url,
            auth=self.auth, 
            timeout=60,
            headers={"Connection": "keep-alive"},
        )

        if response.status_code == 200:
            
            if filename is not None:
                
                try:
                
                    with open(filename, "wb") as arquivo:
                
                        arquivo.write(response.content)
                
                except Exception as e:
                
                    raise Exception(f"Falha ao salvar o arquivo em disco\n{str(e)}")
                
            return {"success": True, "status_code": int(response.status_code), "content": response.content }
        
        else:
        
            return {"success": False, "status_code": int(response.status_code), "content": response.text}


    def qs_gerar_xml_string_responder_nao_cliente(self,protocolo_inicial_ordem:str,numctrlccs:str,cnpj_cpf:str,numctrlenvio:str,numprocjud:str,identdemissor:str,identddestinatario:str,domsist:str,nuop:str,dtmovto:datetime,cnpjbaseentrespons:str):
        
        """Gera a string do arquivo XML de resposta para nao-cliente para ser enviado ao STA
        Args:
            protocolo_inicial_ordem (str): protocolo inicial da ordem de quebra de sigilo, do arquivo AMES102
            numctrlccs (str): numero de controle ccs
            cnpj_cpf (str): documento do solicitado
            numctrlenvio (str): numero de controle de envio
            numprocjud (str): numero do processo judicial
            identdemissor (str): identificacao do emissor
            identddestinatario (str): identificacao do destinatario
            domsist (str): domsist
            nuop (str): numero da operacao
            dtmovto (datetime): data da movimentacao
            cnpjbaseentrespons (str): cnpjbaseentrespons
        Returns:
            str: string formatada para gerar um arquivo xml de resposta
        """
        try:

            ns = "http://www.bcb.gov.br/MES/CCS0012.xsd"
            
            doc = ET.Element("DOC", xmlns=ns)
            
            bcmsg = ET.SubElement(doc, "BCMSG")
            ET.SubElement(bcmsg, "IdentdEmissor").text = identdemissor
            ET.SubElement(bcmsg, "IdentdDestinatario").text = identddestinatario
            ET.SubElement(bcmsg, "DomSist").text = domsist
            ET.SubElement(bcmsg, "NUOp").text = nuop
            
            sismsg = ET.SubElement(doc, "SISMSG")
            ccs0012 = ET.SubElement(sismsg, "CCS0012")
            ET.SubElement(ccs0012, "CodMsg").text = "CCS0012"
            ET.SubElement(ccs0012, "CNPJBaseEntRespons").text = cnpjbaseentrespons
            ET.SubElement(ccs0012, "NumCtrlCCSOr").text = numctrlccs
            ET.SubElement(ccs0012, "SitAtedmntReq").text = "03"
            ET.SubElement(ccs0012, "DtMovto").text = dtmovto.strftime("%Y-%m-%d")
            
            #return ET.tostring(doc, encoding="utf-8", xml_declaration=True).decode("utf-8")
            xml_str = ET.tostring(doc, encoding="utf-8", xml_declaration=True).decode("utf-8")

            # Formatando XML com indentação para melhor visualização
            xml_formatado = parseString(xml_str).toprettyxml(indent="  ")
            return xml_formatado
        
        except Exception as e:
        
            raise Exception(f"Falha ao gerar XML de resposta de Quebra de Sigilo:\n{e}")
        