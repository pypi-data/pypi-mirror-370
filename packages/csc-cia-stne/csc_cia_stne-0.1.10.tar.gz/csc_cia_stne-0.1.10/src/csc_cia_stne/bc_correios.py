import json
import logging
from zeep import Client
from zeep.transports import Transport
from requests import Session
from requests.auth import HTTPBasicAuth
from datetime import timedelta, datetime, time
from typing import List, Tuple, Union, Optional
from pydantic import BaseModel

class PastasAutorizadas(BaseModel):
    MensagemErro: Optional[str] = None
    OcorreuErro: bool
    PastasAutorizadas: Optional[list] = None
    QuantidadePastasAutorizadas: int

class ItemListaCorreio(BaseModel):

    Assunto: str
    Data:datetime
    UnidadeDestinataria: str
    DependenciaDestinataria: Optional[str] = None
    UnidadeRemetente: str
    DependenciaRemetente: Optional[str] = None
    Grupo: Optional[str] = None
    Status: str
    TipoCorreio: str
    NumeroCorreio: int
    Pasta: dict
    Setor: Optional[str] = None
    Transicao: int
    Versao: int

class ItemMsgCorreio(ItemListaCorreio):
    
    OcorreuErro: bool
    MensagemErro: Optional[str] = None
    #NumeroCorreio = None
    #Transicao = None
    #Versao = None
    #Assunto = None
    Ementa: Optional[list] = None
    Conteudo: str
    #TipoCorreio = None
    De: str
    Para: str
    EnviadaPor: str
    EnviadaEm: datetime
    RecebidaPor: str
    RecebidaEm: datetime
    Despachos: Optional[list] = None
    Anexos: Optional[list] = None

class AnexoDict(BaseModel):

    IdAnexo: int
    NomeAnexo: str
    Conteudo: str

class BC_Correios:
    
    def __init__(self, wsdl_url:str, usuario:str, senha:str, correios_por_pasta_pasta_unidade_nome:str='40797', correios_por_pasta_pasta_unidade_ativa:bool=True, correios_por_pasta_pasta_unidade_tipo:str='InstituicaoFinanceira', correios_por_pasta_pasta_tipo:str='CaixaEntrada',correios_por_pasta_apenas_mensagens:bool=True, correios_por_pasta_pesquisar_em_todas_as_pastas:bool=True):
        """
        Inicializa a classe BC_Correios.
        Parâmetros:
        - wsdl_url (str): URL do WSDL do serviço dos Correios.
        - usuario (str): Nome de usuário para autenticação no serviço dos Correios.
        - senha (str): Senha para autenticação no serviço dos Correios.
        - correios_por_pasta_pasta_unidade_nome (str, opcional): Nome da unidade da pasta dos Correios. Valor padrão é '40797'.
        - correios_por_pasta_pasta_unidade_ativa (bool, opcional): Indica se a unidade da pasta dos Correios está ativa. Valor padrão é True.
        - correios_por_pasta_pasta_unidade_tipo (str, opcional): Tipo da unidade da pasta dos Correios. Valor padrão é 'InstituicaoFinanceira'.
        - correios_por_pasta_pasta_tipo (str, opcional): Tipo da pasta dos Correios. Valor padrão é 'CaixaEntrada'.
        - correios_por_pasta_apenas_mensagens (bool, opcional): Indica se deve retornar apenas mensagens da pasta dos Correios. Valor padrão é True.
        - correios_por_pasta_pesquisar_em_todas_as_pastas (bool, opcional): Indica se deve pesquisar em todas as pastas dos Correios. Valor padrão é True.
        """

        try:

            session = Session()
            session.auth = HTTPBasicAuth(usuario,senha)
            
            transport = Transport(session=session,timeout=120,operation_timeout=120)
            
            self.client = Client(wsdl_url, transport=transport)
            self.is_connected = True
            self.error = None
            self.CorreiosPorPastaPastaUnidadeNome = correios_por_pasta_pasta_unidade_nome
            self.CorreiosPorPastaPastaUnidadeAtiva = correios_por_pasta_pasta_unidade_ativa
            self.CorreiosPorPastaPastaUnidadeTipo = correios_por_pasta_pasta_unidade_tipo
            self.CorreiosPorPastaPastaTipo = correios_por_pasta_pasta_tipo
            self.CorreiosPorPastaApenasMensagens = correios_por_pasta_apenas_mensagens
            self.CorreiosPorPastaPesquisarEmTodasAsPastas = correios_por_pasta_pesquisar_em_todas_as_pastas
        
        except Exception as e:
            
            self.is_connected = False
            self.error = e

    def consultar_pastas_autorizadas(self)->Tuple[bool, Union[PastasAutorizadas, Exception]]:
        """
        Retorna as pastas de correio e os setores que o usuário tem permissão de acessar.
        """
        
        try:
        
            response = self.client.service.ConsultarPastasAutorizadas()
            
            if response.OcorreuErro:
            
                raise Exception(response.MensagemErro)
            
            pastas = PastasAutorizadas(MensagemErro=response.MensagemErro, OcorreuErro=response.OcorreuErro, QuantidadePastasAutorizadas=response.QuantidadePastasAutorizadas,PastasAutorizadas=response.PastasAutorizadas.PastaAutorizadaWSDTO)
            
            return True, pastas
        
        except Exception as e:
        
            return False, e

    def consultar_correios_por_pasta(self,ultimos_x_dias:int=None,data_inicial:datetime=None,data_final:datetime=None)->Tuple[bool, Union[List['ItemListaCorreio'], Exception]]:

        """
        Retorna uma lista com os cabeçalhos dos correios contidos em uma pasta.

        A consulta pode ser realizada de 2 maneiras:
        1. Especificando um intervalo de dias relativos ao dia atual (com `ultimos_x_dias`).
        2. Informando explicitamente uma `data_inicial` E `data_final`.

        Args:
            ultimos_x_dias (int, opcional): O número de dias a contar para trás a partir da data atual. Se especificado, ignorará `data_inicial` e `data_final`.
            data_inicial (datetime, opcional): Data inicial do intervalo para filtrar os correios.
            data_final (datetime, opcional): Data final do intervalo para filtrar os correios.

        Returns:
            tuple: Um par contendo:
                - bool: Indica se a operação foi bem-sucedida (True) ou falhou (False).
                - Union[list[ItemListaCorreio], Exception]: Retorna uma lista de objetos `ItemListaCorreio` contendo os detalhes dos correios encontrados, ou uma exceção em caso de erro.
        """

        try:
            
            if ultimos_x_dias is not None and isinstance(ultimos_x_dias,int):
                
                agora = datetime.now()
                
                # Pegando mensagens antigas, ja lidas, no desenvolvimento, para nao atrapalhar o time com as mensagens nao lidas atuais
                #logger.warning("VERIFICAR DATA DO 'AGORA'!")
                #agora = datetime.now() - timedelta(days=150)
                
                dt_inicial_iso_format = agora - timedelta(days=ultimos_x_dias)
                dt_inicial_iso_format = datetime.combine(dt_inicial_iso_format.date(), time.min)
                dt_inicial_iso_format = dt_inicial_iso_format.isoformat()
                
                dt_final_iso_format = datetime.combine(agora.date(), time.max)
                dt_final_iso_format = agora.isoformat()
            
            elif data_inicial is isinstance(data_inicial,datetime) and data_final is isinstance(data_final,datetime):
                
                dt_inicial_iso_format =  data_inicial.isoformat()
                dt_final_iso_format = data_final.isoformat()
            
            else:
                
                raise ValueError("ultimos_x_dias se for informado, precisa ser um numero inteiro. Ou entao se for informado data_inicial E data_final, esses 2 parametros precisam ser datetime")

            correios_filtrados = []
            correios_repetidos = []
            pagina_atual = 1
            
            def objeto_ja_existe_na_lista(novo_item, lista_de_correios):

                for item in lista_de_correios:

                    if (str(item.NumeroCorreio) == str(novo_item.NumeroCorreio)):

                        return True

                return False

            proxima_centena = 100
            while True:

                correios = None
                params = {
                    'Pasta': {
                        'Unidade': {
                            'Nome': self.CorreiosPorPastaPastaUnidadeNome,
                            'Ativa': self.CorreiosPorPastaPastaUnidadeAtiva,
                            'Tipo': self.CorreiosPorPastaPastaUnidadeTipo
                        },
                        'Tipo': self.CorreiosPorPastaPastaTipo
                    },
                    'ApenasMensagens': self.CorreiosPorPastaApenasMensagens,
                    'PesquisarEmTodasAsPastas': self.CorreiosPorPastaPesquisarEmTodasAsPastas,
                    'Pagina': pagina_atual,
                    'DataInicial': dt_inicial_iso_format,
                    'DataFinal': dt_final_iso_format,
                }
                
                response = self.client.service.ConsultarCorreiosPorPasta(params)
                
                if response.OcorreuErro:
                    raise Exception(f"Erro ao consultar correios: {response.MensagemErro}")
                
                # Verifica a quantidade total de correios na primeira iteração
                try:

                    # Acessa a lista de correios diretamente
                    correios = response.Correios.ResumoCorreioWSDTO
                    
                    if not correios:

                        # Se não houver mais itens, paramos a busca
                        break
                except:

                    # Fim da listagem de correios
                    break
                
                for correio in correios:

                    item_de_lista_de_correios = ItemListaCorreio(
                        Assunto=correio.Assunto,
                        Data=correio.Data,
                        UnidadeDestinataria=correio.UnidadeDestinataria,
                        DependenciaDestinataria=correio.DependenciaDestinataria,
                        UnidadeRemetente=correio.UnidadeRemetente,
                        DependenciaRemetente=correio.DependenciaRemetente,
                        Grupo=correio.Grupo,
                        Status=correio.Status,
                        TipoCorreio=correio.TipoCorreio,
                        NumeroCorreio=correio.NumeroCorreio,
                        Pasta={
                            'Unidade': correio.Pasta.Unidade,
                            'Dependencia': correio.Pasta.Dependencia,
                            'Setor': correio.Pasta.Setor,
                            'Tipo': correio.Pasta.Tipo
                            },
                        Setor=correio.Setor,
                        Transicao=correio.Transicao,
                        Versao=correio.Versao
                        )
                    if objeto_ja_existe_na_lista(novo_item=item_de_lista_de_correios,lista_de_correios=correios_filtrados) == False:

                        correios_filtrados.append(item_de_lista_de_correios)
                    else:
                        correios_repetidos.append(item_de_lista_de_correios)

                if len(correios_filtrados) >= proxima_centena:

                    logging.info(f"Página #{pagina_atual}: {len(correios_filtrados)} correios armazenados no total")
                    proxima_centena = proxima_centena + 100

                # Avança para a próxima página
                pagina_atual += 1

            return True, correios_filtrados
        
        except Exception as e:
            
            return False, e

    def ler_correio(self, numero:int,data_rebimento:datetime,tipo:str,transicao:int,versao:int,pasta:str)-> Tuple[bool, Union[ItemMsgCorreio, Exception]]:
        """
        Retorna o conteúdo de um correio.
        
        Args:
            correio (ItemListaCorreio): objeto da classe ItemListaCorreio (item da listagem de mensagens)
        
        Returns:
            tuple: Um par contendo:
                - bool: Indica se a operação foi bem-sucedida (True) ou falhou (False).
                - Union[ItemMsgCorreio, Exception]: Retorna um objeto da classe ItemMsgCorreio contendo os detalhes do correio lido, ou uma exceção em caso de erro.
        """

        try:

            # Substituir aspas simples por aspas duplas
            pasta = pasta.replace("'", '"').replace("None", "null")
            pasta = json.loads(pasta)
            #params = {
            #    'Correio': {
            #        'NumeroCorreio': correio.NumeroCorreio,
            #        'Data': correio.Data.isoformat(),
            #        'TipoCorreio': correio.TipoCorreio,
            #        'Transicao': correio.Transicao,
            #        'Versao': correio.Versao,
            #        'Pasta': correio.Pasta
            #    }
            #}

            params = {
                'Correio': {
                    'NumeroCorreio': numero,
                    'Data': data_rebimento.isoformat(),
                    'TipoCorreio': tipo,
                    'Transicao': transicao,
                    'Versao': versao,
                    'Pasta': {
                        'Unidade': pasta["Unidade"],
                        'Dependencia': pasta["Dependencia"],
                        'Setor': pasta["Setor"],
                        'Tipo': pasta["Tipo"],
                        }
                }
            }

            response = self.client.service.LerCorreio(params)
            
            #novo start
            
            #print("antes")
            #print("response type:",type(response))
            #print("response:")
            #print(response)
            if response.OcorreuErro:
                raise Exception(f"Erro ao detalhar correio: {response.MensagemErro}")
            
            #msg_detail = ItemMsgCorreio()
            #msg_detail.OcorreuErro = response.OcorreuErro
            #msg_detail.MensagemErro = response.MensagemErro
            ##msg_detail.NumeroCorreio = response.DetalheCorreio.NumeroCorreio
            ##msg_detail.Transicao = response.DetalheCorreio.Transicao
            ##msg_detail.Versao = response.DetalheCorreio.Versao
            ##msg_detail.Assunto = response.DetalheCorreio.Assunto
            #msg_detail.Ementa = response.DetalheCorreio.Ementa
            #msg_detail.Conteudo = response.DetalheCorreio.Conteudo
            ##msg_detail.TipoCorreio = response.DetalheCorreio.TipoCorreio
            #msg_detail.De = response.DetalheCorreio.De
            #msg_detail.Para = response.DetalheCorreio.Para
            #msg_detail.EnviadaPor = response.DetalheCorreio.EnviadaPor
            #msg_detail.EnviadaEm = response.DetalheCorreio.EnviadaEm
            #msg_detail.RecebidaPor = response.DetalheCorreio.RecebidaPor
            #msg_detail.RecebidaEm = response.DetalheCorreio.RecebidaEm
            #msg_detail.Despachos = response.DetalheCorreio.Despachos
            #if response.DetalheCorreio.Anexos:
            #     msg_detail.Anexos = response.DetalheCorreio.Anexos.AnexoWSDTO


            #msg_detail = ItemMsgCorreio(
            #    **correio.model_dump(),
            #    OcorreuErro = response.OcorreuErro,
            #    MensagemErro = response.MensagemErro,
            #    #msg_detail.NumeroCorreio = response.DetalheCorreio.NumeroCorreio
            #    #msg_detail.Transicao = response.DetalheCorreio.Transicao
            #    #msg_detail.Versao = response.DetalheCorreio.Versao
            #    #msg_detail.Assunto = response.DetalheCorreio.Assunto
            #    Ementa = response.DetalheCorreio.Ementa,
            #    Conteudo = response.DetalheCorreio.Conteudo,
            #    #msg_detail.TipoCorreio = response.DetalheCorreio.TipoCorreio
            #    De = response.DetalheCorreio.De,
            #    Para = response.DetalheCorreio.Para,
            #    EnviadaPor = response.DetalheCorreio.EnviadaPor,
            #    EnviadaEm = response.DetalheCorreio.EnviadaEm,
            #    RecebidaPor = response.DetalheCorreio.RecebidaPor,
            #    RecebidaEm = response.DetalheCorreio.RecebidaEm,
            #    Despachos = response.DetalheCorreio.Despachos,
            #    Anexos = response.DetalheCorreio.Anexos.AnexoWSDTO
            #)


            msg_detail = {
                "OcorreuErro": response.OcorreuErro,
                "MensagemErro": response.MensagemErro,
                #msg_detail.NumeroCorreio = response.DetalheCorreio.NumeroCorreio
                #msg_detail.Transicao = response.DetalheCorreio.Transicao
                #msg_detail.Versao = response.DetalheCorreio.Versao
                #msg_detail.Assunto = response.DetalheCorreio.Assunto
                "Ementa": response.DetalheCorreio.Ementa,
                "Conteudo": response.DetalheCorreio.Conteudo,
                #msg_detail.TipoCorreio = response.DetalheCorreio.TipoCorreio
                "De": response.DetalheCorreio.De,
                "Para": response.DetalheCorreio.Para,
                "EnviadaPor": response.DetalheCorreio.EnviadaPor,
                "EnviadaEm": response.DetalheCorreio.EnviadaEm,
                "RecebidaPor": response.DetalheCorreio.RecebidaPor,
                "RecebidaEm": response.DetalheCorreio.RecebidaEm,
                "Despachos": response.DetalheCorreio.Despachos,
                "Anexos": response.DetalheCorreio.Anexos.AnexoWSDTO
            }


            #print("depois")
            #print("response novo type:",type(msg_detail))
            #print("response novo:")
            #print(msg_detail)
            #print(msg_detail.Anexos)


            """
            xx = {
                'MensagemErro': None,
                'OcorreuErro': False,
                'DetalheCorreio': {
                    'NumeroCorreio': 124311198,
                    'Transicao': 46142046,
                    'Versao': 670,
                    'Assunto': 'SOLJUD 2024087211',
                    'Ementa': None,
                    'Conteudo': '\n<pre>\nOfício 026707/2024-BCB/Deati/Coadi-1\nPE 262353/e-BC 2024211930                                               Brasília, 23 de setembro de 2024.\nJUD/EXT - 2024/087211E\n\nA todas as instituições financeiras.\n\nAssunto: Ofício S\\N, de 13 de setembro de 2024\nProcesso: 5094191-48.2024.8.09.0142\n\nPrezados Senhores,\n\nAtendendo à requisição do(a) Juíz de Direito MARLI PIMENTA NAVES, do(a) Juizado Especial Cível, encaminhamos, em anexo, para exame e adoção das\nprovidências julgadas cabíveis, a determinação judicial exarada no ofício em epígrafe.\n\n\n2. A propósito, esclarecemos que eventuais dúvidas a respeito da ordem, inclusive com relação a número de CPF/CNPJ, somente serão dirimidas\njunto ao Juízo demandante, ou ao órgão por ele designado, para onde devem ser encaminhadas as correspondências alusivas ao assunto,\nmencionando-se os números do ofício e do processo.\n\n\n3. Finalmente, alertamos que a inobservância à norma do sigilo bancário contido na Lei Complementar 105, de 10 de janeiro de 2001, sujeitará os\nresponsáveis às sanções previstas no artigo 10 da mencionada Lei, cabendo ainda à instituição zelar por manter a privacidade das informações\nrelativas a clientes (artigo 5º, item X, da CF/88).\n\n\nAtenciosamente,\n\nDepartamento de Atendimento Institucional – DEATI\nGerência de Relacionamento Institucional – GERIN\n\n\nGILDO TEREZA DOS REIS\nTECNICO\n\nMAURO MAGNO MACHADO JUNIOR      \nTECNICO                         \n\nDocumento transmitido por correio eletrônico, via BC Correio, dispensado de assinatura.\n</pre>\n',
                    'TipoCorreio': 'MENSAGEM',
                    'De': 'DEATI',
                    'Para': '40797 (Transmissão para grupo geral F1)',
                    'EnviadaPor': 'DEATI.GILDO',
                    'EnviadaEm': datetime.datetime(2024, 9, 23, 10, 40, 19),
                    'RecebidaPor': '407970001.PALCANTARA',
                    'RecebidaEm': datetime.datetime(2024, 9, 25, 14, 45, 51),
                    'Despachos': None,
                    'Anexos': {
                        'AnexoWSDTO': [
                            {
                                'IdAnexo': 538648,
                                'NomeAnexo': '-2024-171630-211930--20092024233504.PDF',
                                'Conteudo': None
                            }
                        ]
                    }
                }
            }
            """


            #logger.debug("parou aqui 6757576")
            #sys.exit(0)
            #novo end

            #return True, response
            return True, msg_detail

            # Serializa o objeto SOAP em um dicionário Python
            #serialized_response = serialize_object(response)
            
            # Converte o dicionário em um JSON formatado
            #response_json = json.dumps(serialized_response, indent=4, default=str)

            #return True, response_json

        except Exception as e:

            return False, e
        
    def obter_anexo(self, numero:int, versao:int, transicao:int,pasta:str,anexo_id:int,file_name:str,conteudo:str)-> Tuple[bool,Union[dict, Exception]]:
        """
        Obtém um anexo de um correio eletrônico.
        
        Args:
            correio (ItemListaCorreio): objeto da classe ItemListaCorreio (item da listagem de mensagens)
            anexo (AnexoDict): um item do dicionário da lista de anexos de ItemListaCorreio
        
        Returns:
            tuple: Um par contendo:
                - bool: Indica se a operação foi bem-sucedida (True) ou falhou (False).
                - Union[dict, Exception]: Retorna um dicionario com dados do anexo, ou uma exceção em caso de erro.

        """
        #logger.info("ANEXOS PARA OBTER")
        #print(correio.Anexos)
        try:
            
            pasta = pasta.replace("'", '"').replace("None", "null")
            pasta = json.loads(pasta)
            
            # Monta os parâmetros para a requisição SOAP
            params = {
                'NumeroCorreio': numero,
                'Versao': versao,
                'Transicao': transicao,
                #'Pasta': pasta,
                'Pasta': {
                        'Unidade': pasta["Unidade"],
                        'Dependencia': pasta["Dependencia"],
                        'Setor': pasta["Setor"],
                        'Tipo': pasta["Tipo"],
                        },
                #'Pasta': {
                #    'Unidade': {
                #        'Nome': pasta['Unidade']['Nome'],
                #        'Ativa': pasta['Unidade']['Ativa'],
                #        'Tipo': pasta['Unidade']['Tipo']
                #    },
                #    'Dependencia': pasta['Dependencia'],
                #    'Setor': {
                #        'Nome': pasta['Setor']['Nome'],
                #        'Ativo': pasta['Setor']['Ativo']
                #    },
                #    'Tipo': pasta['Tipo']
                #},
                'Anexo': {
                    'IdAnexo': anexo_id,
                    'NomeAnexo': file_name,
                    'Conteudo': conteudo  # Conteúdo em base64
                }
            }

            # Faz a requisição SOAP para o método ObterAnexo
            response = self.client.service.ObterAnexo(parametros=params)
            #logger.info("response")
            #logger.info(response)
            
            # Acessa os dados da resposta (IdAnexo, NomeAnexo, Conteudo)
            if response and hasattr(response, 'Anexo'):
                id_anexo = response.Anexo.IdAnexo
                nome_anexo = response.Anexo.NomeAnexo
                conteudo_anexo = response.Anexo.Conteudo
                
                # Retorna os dados capturados como um dicionário
                return True, {
                    'IdAnexo': id_anexo,
                    'NomeAnexo': nome_anexo,
                    'Conteudo': conteudo_anexo
                }
            else:
                return False, Exception("Correio não possui anexo")
        
        except Exception as e:
            
            return False, e

    def encerrar(self):
        """Fecha o cliente e libera a sessão."""
        
        try:
        
            self.client.transport.session.close()
        
        except:
            
            pass

