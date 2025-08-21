import requests
from datetime import datetime,timezone
from dateutil.relativedelta import relativedelta

from .utilitarios.validations.waccess import InitParamsValidator,CreateUserValidator,ValidateExistenceValidator,CreateWaccessValidator,UpdateWaccessValidator,UpdateUserValidator,AddPhotoValidator,ChangeGroupsUserValidator,AddCardUserValidator,GetUserCardsValidator,CreateCardValidator,AssociateCardUserValidator,TurnOffUserValidator,RemoveGroupsValidator

class Waccess():

    def __init__(self, headers:dict, url:str):
        """
        Inicializa a classe Waccess.
        """

        try:

            InitParamsValidator(
                headers=headers,
                url=url
            )

        except Exception as e:

            raise ValueError("Erro na validação dos dados de input da inicialização da instância:", e.errors())

        self.waccess_headers = headers
        self.waccess_url = url

    # Função para criar usuario no waccess
    def create_user(self, cpf:str, name:str, email:str, empresa:str, rg:str=None) -> dict:
        """
        Cria um usuário no sistema WAccess, caso ele ainda não exista.
        Args:
            cpf (str): CPF do usuário a ser criado.
            name (str): Nome do usuário.
            email (str): E-mail do usuário.
            empresa (str): Nome da empresa associada ao usuário.
            rg (str, opcional): RG do usuário. Padrão é None.
        Returns:
            dict: Um dicionário contendo:
                - 'success' (bool): Indica se a operação foi bem-sucedida.
                - 'code' (str): Mensagem de status da operação.
                - 'data' (dict): Dados adicionais relacionados à operação.
        """

        try:

            CreateUserValidator(
                cpf=cpf,
                name=name,
                email=email,
                empresa=empresa,
                rg=rg
            )

        except Exception as e:

            raise ValueError("Erro na validação dos dados de input da criação do usuario:", e.errors())

        # Valida a existencia do usuario dentro do waccess

        status_existence = self._validate_existence(cpf=cpf)

        if status_existence is False:

            # Liberado para criar o usuario

            status_creation = self._create_waccess(
                cpf=cpf,
                name=name,
                email=email,
                rg=rg,
                empresa=empresa
            )

            if status_creation['success'] is False:

                return {
                    'success':False,
                    'code':'Erro ao criar usuario no waccess',
                    'data':status_creation['data']
                }
            
            else:

                return {
                    'success':True,
                    'code':'Usuario criado com sucesso no waccess',
                    'data':status_creation['data']
                }

        else:

            return {
                'success':True,
                'code':'Usuario já existe no waccess',
                'data':status_existence
            }
    
    def _validate_existence(self, cpf:str):
        """
        Valida a existência de um cadastro no sistema WAccess com base no CPF fornecido.
        Args:
            cpf (str): O CPF do titular do cartão a ser validado.
        Returns:
            dict: Um dicionário contendo os dados do titular do cartão, caso encontrado.
            bool: Retorna False se o titular do cartão não for encontrado.
        Raises:
            ValueError: Se ocorrer um erro na requisição HTTP ou outro erro inesperado.
        """

        try:

            ValidateExistenceValidator(
                cpf=cpf
            )

        except Exception as e:

            raise ValueError("Erro na validação dos dados de input da validação de existencia:", e.errors())

        try:

            reply = requests.get(
                f"{self.waccess_url}/cardholders?CHtype=2&IdNumber={cpf}",
                headers=self.waccess_headers,
                verify=False,
            )

            if reply.status_code == 200:

                result = reply.json()[0]

                return result

            else:

                return False

        except requests.exceptions.RequestException as e:
           
           raise ValueError("Erro na validação de existencia", e)
        
        except Exception as e:

            raise ValueError("Erro na validação de existencia", e)

    def _create_waccess(self, name:str, email:str,cpf:str, rg:str=None, empresa:str=None) -> dict:
        """
        Cria um registro de "cardholder" no sistema WAccess.
        Args:
            name (str): Nome do usuário.
            email (str): Endereço de e-mail do usuário.
            cpf (str): CPF do usuário.
            rg (str, opcional): RG do usuário. Padrão é None.
            empresa (str, opcional): Nome da empresa do usuário. Se for "TERCEIRIZADO", 
                o campo "CompanyID" será configurado como 21. Padrão é None.
        Returns:
            dict: Um dicionário contendo o resultado da operação.
                - 'success' (bool): Indica se a operação foi bem-sucedida.
                - 'data' (dict): Dados retornados pela API em caso de sucesso ou erro.
        """

        try:

            CreateWaccessValidator(
                name=name,
                email=email,
                cpf=cpf,
                empresa=empresa,
                rg=rg
            )

        except Exception as e:

            raise ValueError("Erro na validação dos dados de input da criação do usuario:", e.errors())

        cardholder = {
            'PartitionID': 1,
            'CHtype': 2,
            'IdNumber': cpf,
            'FirstName': name,
            'AuxText05': str(rg),
            'EMail': email,
            'AuxLst01': None,
            'AuxText04':None,
            'AuxText15':None,
            'AuxTextA01':f'Usuário criado por API via'
        }

        if str(empresa).upper() == 'TERCEIRIZADO':

            cardholder["CompanyID"] = 21

        reply = requests.post(
            f'{self.waccess_url}/cardholders',
            headers=self.waccess_headers,
            json=cardholder,
            verify=False,
        )

        if reply.status_code == 201:

            result = reply.json()

            return {
                'success':True,
                'data':result
            }
        
        else:

            return {
                'success':False,
                'data':reply.json()
            }

    # Função para atualizar usuario no waccess
    def update_user_information(self, name:str, cpf:str, email:str, status:int, empresa:str=None ,rg:str=None, foto:str=None) -> dict:
        """
        Atualiza as informações de um usuário no sistema WAccess.
        Args:
            name (str): Nome do usuário.
            cpf (str): CPF do usuário.
            email (str): E-mail do usuário.
            empresa (str): Nome da empresa associada ao usuário.
            status (int): Status do usuário (ativo/inativo).
            rg (str, opcional): RG do usuário. Padrão é None.
            foto (str, opcional): Caminho ou referência para a foto do usuário. Padrão é None.
        Returns:
            dict: Um dicionário contendo o resultado da operação com as seguintes chaves:
                - success (bool): Indica se a operação foi bem-sucedida.
                - code (str): Mensagem descritiva do resultado.
                - data (qualquer): Dados adicionais relacionados ao resultado da operação.
        """

        # Valida a existencia do usuario dentro do waccess

        try:

            UpdateWaccessValidator(
                cpf=cpf,
                name=name,
                email=email,
                empresa=empresa,
                rg=rg,
                status=status
            )

        except Exception as e:
    
            raise ValueError("Erro na validação dos dados de input da atualização do usuario:", e.errors())

        status_existence = self._validate_existence(cpf=cpf)

        if status_existence is False:

            return {
                'success':False,
                'code':'Usuario não existe no waccess',
                'data':status_existence
            }
        
        status_update = self._update_user(
            name=name,
            email=email,
            cpf=cpf,
            rg=rg,
            empresa=empresa,
            status=status
        )

        if status_update['success'] is False:

            return {
                'success':False,
                'code':'Erro ao atualizar usuario no waccess',
                'data':status_update['data']
            }

        if self._add_photo(
            chid=status_existence['CHid'],
            picture=foto
        ) is False:

            return {
                'success':False,
                'code':'Erro ao adicionar foto no usuario',
                'data':status_update['data']
            }
        
        return {
                'success':True,
                'code':'Dados atualizados com sucesso no waccess',
            }

    def _update_user(self, name:str, email:str, cpf:str, status:int , rg:str=None, empresa:str=None) -> dict:

        try:

            UpdateUserValidator(
                cpf=cpf,
                name=name,
                email=email,
                empresa=empresa,
                rg=rg,
                status=status
            )
            
        except Exception as e:

            raise ValueError("Erro na validação dos dados de input da atualização do usuario:", e.errors())
   
    def _add_photo(self, chid:str, picture:str) -> dict:
        """
        Adiciona uma foto a um titular de cartão no sistema WAccess.
        Args:
            chid (str): O identificador do titular do cartão.
            picture (str): O caminho ou os dados da imagem a ser enviada.
        Returns:
            dict: Retorna True se a foto foi adicionada com sucesso, 
                  caso contrário, retorna False.
        """

        try:

            AddPhotoValidator(
                chid=chid,
                picture=picture
            )

        except Exception as e:

            raise ValueError("Erro na validação dos dados de input da adição da foto:", e.errors())

        reply = requests.post(
            f'{self.waccess_url}/cardholders/{chid}/photos/1',
            headers=self.waccess_headers,
            files=(('photoJpegData', picture), ),
            verify=False,
        )

        if reply.status_code == 200:

            return True

        else:

            return False

    # Adicionar grupo(s)
    def change_groups_user(self, cpf:str, groups_list:list) -> dict:
        """
        Altera os grupos associados a um usuário no sistema WAccess.
        Args:
            cpf (str): CPF do usuário cujo grupo será alterado.
            groups_list (list): Lista de dicionários contendo as ações e IDs dos grupos.
                Cada item da lista deve ter o formato:
                {
                    'action': 'add' ou 'remove',
                    'group_id': <ID do grupo>
        Returns:
            dict: Um dicionário contendo o status da operação.
                - Se o usuário não existir:
                    {
                        'success': False,
                        'code': 'Usuario não existe no waccess',
                        'data': False
                - Se a operação for bem-sucedida:
                    {
                        'success': True,
                        'code': 'Grupos atualizados com sucesso no waccess',
                        'data': [
                            {
                                'success': True ou False,
                                'action': 'add' ou 'remove',
                                'group_id': <ID do grupo>,
                                'error': <Erro retornado pela API, se houver>
                            },
                            ...
                        ]
        """

        try:

            ChangeGroupsUserValidator(
                cpf=cpf,
                groups_list=groups_list
            )
        
        except Exception as e:
    
            raise ValueError("Erro na validação dos dados de input da alteração dos grupos do usuario:", e.errors())

        status_existence = self._validate_existence(cpf=cpf)

        if status_existence is False:

            return {
                'success':False,
                'code':'Usuario não existe no waccess',
                'data':status_existence
            }
        
        # Adicionar/Remover grupos do usuario

        result = []

        for item_groups in groups_list:

            if item_groups['action'] == 'add':

                reply = requests.post(
                    f'{self.waccess_url}/cardholders/{status_existence["CHid"]}/groups/{item_groups["group_id"]}',
                    headers=self.waccess_headers,
                    verify=False,
                )

            elif item_groups['action'] == 'remove':

                reply = requests.delete(
                    f'{self.waccess_url}/cardholders/{status_existence["CHid"]}/groups/{item_groups["group_id"]}',
                    headers=self.waccess_headers,
                    verify=False,
                )
    
            if reply.status_code == 204:

                result.append({
                    'success':True,
                    'action':item_groups['action'],
                    'group_id':item_groups['group_id']
                })

            else:

                result.append({
                    'success':False,
                    'action':item_groups['action'],
                    'group_id':item_groups['group_id'],
                    'error':reply.json()
                })

        return {
            'success':True,
            'code':'Grupos atualizados com sucesso no waccess',
            'data':result
        }
   
    # Adicionar cracha
    def add_card_user(self, cpf:str, card:str) -> dict:
        """
        Adiciona um cartão a um usuário no sistema WAccess.
        Este método realiza as seguintes etapas:
        1. Verifica a existência do usuário no sistema WAccess.
        2. Verifica se o usuário está ativo.
        3. Cria o cartão no sistema WAccess, caso ele ainda não exista.
        4. Remove outros cartões associados ao usuário, se necessário.
        5. Associa o novo cartão ao usuário.
        Args:
            cpf (str): CPF do usuário a ser verificado.
            card (str): Número do cartão a ser associado ao usuário.
        Returns:
            dict: Um dicionário contendo o status da operação. As chaves possíveis são:
                - 'success' (bool): Indica se a operação foi bem-sucedida.
                - 'code' (str): Código ou mensagem descritiva do status da operação.
                - 'data' (opcional): Dados adicionais relacionados ao status da operação.
        """

        try:

            AddCardUserValidator(
                cpf=cpf,
                card=card
            )

        except Exception as e:
    
            raise ValueError("Erro na validação dos dados de input da adição do cartão:", e.errors())

        status_existence = self._validate_existence(cpf=cpf)

        if status_existence is False:

            return {
                'success':False,
                'code':'Usuario não existe no waccess',
                'data':status_existence
            }

        elif str(status_existence['CHState']) == "1" or str(status_existence['CHState']) == "2":

            return {
                'success':False,
                'code':'Usuario inativo no waccess',
                'data':status_existence
            }
        
        # Verifica a existencia do cartão

        status_creation_card = self._create_card(card=card)

        if not status_creation_card:

            return {
                'success':False,
                'code':'Erro ao criar cartão no waccess',
                'data':status_creation_card
            }
        
        # Verifica a existencia do cartão do colaborador

        status_user_cards = self._get_user_cards(chid=status_existence['CHid'])

        # Remove os outros cartões do colaborador

        if status_user_cards['success'] is True:

            for item_card in status_user_cards['data']:

                if item_card['CardNumber'] != card:

                    reply = requests.delete(
                        f'{self.waccess_url}/cards/{item_card["CardID"]}',
                        headers=self.waccess_headers,
                        verify=False,
                    )

                    if reply.status_code != 204:

                        return {
                            'success':False,
                            'code':'Erro ao remover cartão do colaborador',
                            'data':reply.json()
                        }

        # Associa o cartão ao usuario
        
        status_associate_card = self._associate_card_user(card=card, chid=status_existence['CHid'])

        if status_associate_card is False:
    
            return {
                'success':False,
                'code':'Erro ao associar cartão ao colaborador',
            }

        else:

            return {
                'success':True,
                'code':'Cartão associado com sucesso ao colaborador',
            }

    def _get_user_cards(self, chid:str) -> dict:
        """
        Obtém os cartões associados a um usuário específico (cardholder) no sistema WAccess.
        Args:
            chid (str): O identificador único do cardholder.
        Returns:
            dict: Um dicionário contendo:
                - 'success' (bool): Indica se a operação foi bem-sucedida.
                - 'data' (dict ou list): Os dados retornados pela API em caso de sucesso,
                  ou a resposta de erro em caso de falha.
        """

        try:

            GetUserCardsValidator(
                chid=chid
            )

        except Exception as e:

            raise ValueError("Erro na validação dos dados de input da obtenção dos cartões do usuario:", e.errors())

        reply = requests.get(
            f'{self.waccess_url}/cardholders/{chid}/cards',
            headers=self.waccess_headers,
            verify=False,
        )

        if reply.status_code == 200:

            result = reply.json()

            return {
                'success':True,
                'data':result
            }
        
        else:
                
            return {
                'success':False,
                'data':reply.json()
            }

    def _create_card(self,card:str) -> bool:
        """
        Cria um cartão no sistema WAccess.
        Args:
            card (str): O número do cartão a ser criado.
        Returns:
            bool: Retorna True se o cartão foi criado com sucesso (status HTTP 201),
                  caso contrário, retorna False.
        Observações:
            - O cartão criado terá validade de 10 anos a partir da data atual.
            - A comunicação com o sistema WAccess é feita via uma requisição HTTP POST.
            - Certifique-se de que `self.waccess_url` e `self.waccess_headers` estejam configurados corretamente.
        """

        try:

            CreateCardValidator(
                card=card
            )

        except Exception as e:
    
            raise ValueError("Erro na validação dos dados de input da criação do cartão:", e.errors())

        command = {
            'ClearCode': card,
            'CardNumber': card,
            'CardStartValidityDateTime': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S'),
            'CardEndValidityDateTime': (datetime.now(timezone.utc)+relativedelta(days=3650)).strftime('%Y-%m-%dT%H:%M:%S'),
        }

        reply = requests.post(
            f'{self.waccess_url}/cards',
            headers=self.waccess_headers,
            json=command,
            verify=False,
        )

        if reply.status_code == 201:

            return True

        else:

            return False
    
    def _associate_card_user(self, card:str, chid:str) -> bool:
        """
        Associa um cartão a um usuário no sistema WAccess.
        Args:
            card (str): O ID do cartão a ser associado.
            chid (str): O ID do titular do cartão (CardHolder ID).
        Returns:
            bool: Retorna True se a associação for bem-sucedida (status HTTP 201),
                  caso contrário, retorna False.
        Observação:
            - O campo 'CardStartValidityDateTime' é definido como a data e hora atual no formato UTC.
            - O campo 'CardEndValidityDateTime' é definido como 10 anos a partir da data e hora atual.
            - A requisição é enviada para o endpoint '/cardholders/{chid}/cards' da URL base do WAccess.
            - A verificação SSL está desativada (verify=False).
        """
        
        try:

            AssociateCardUserValidator(
                card=card,
                chid=chid
            )

        except Exception as e:
        
            raise ValueError("Erro na validação dos dados de input da associação do cartão:", e.errors())

        command = {
            'CardID': card,
            'CHid': card,
            'CardStartValidityDateTime': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S'),
            'CardEndValidityDateTime': (datetime.now(timezone.utc)+relativedelta(days=3650)).strftime('%Y-%m-%dT%H:%M:%S'),
        }

        reply = requests.post(
            f'{self.waccess_url}/cardholders/{chid}/cards',
            headers=self.waccess_headers,
            json=command,
            verify=False,
        )

        if reply.status_code == 201:

            return True

        else:

            return False

    # Função para inativar usuario no waccess
    def turn_off_user(self, cpf:str) -> dict:
        """
        Desativa um usuário no sistema WAccess.
        Este método realiza as seguintes etapas:
        1. Valida a existência do usuário no WAccess.
        2. Remove os grupos de acesso associados ao usuário.
        3. Remove os cartões vinculados ao usuário.
        4. Inativa o usuário no sistema WAccess.
        Args:
            cpf (str): CPF do usuário que será desativado.
        Returns:
            dict: Um dicionário contendo o resultado da operação:
                - 'success' (bool): Indica se a operação foi bem-sucedida.
                - 'code' (str): Mensagem de status da operação.
                - 'data' (opcional): Dados adicionais, como resposta da API em caso de erro.
        Exceções:
            - Caso o usuário não exista no WAccess, retorna um dicionário com 'success' como False e uma mensagem apropriada.
            - Caso ocorra um erro ao inativar o usuário, retorna um dicionário com 'success' como False e os detalhes do erro.
        """

        try:

            TurnOffUserValidator(
                cpf=cpf
            )

        except Exception as e:
                    
            raise ValueError("Erro na validação dos dados de input da inativação do usuario:", e.errors())

        # Valida a existencia do usuario dentro do waccess

        status_existence = self._validate_existence(cpf=cpf)

        if status_existence is False:

            return {
                'success':False,
                'code':'Usuario não existe no waccess',
                'data':status_existence
            }

        # Remove os grupos de acesso

        self._remove_groups(
            chid=status_existence['CHid'],
            cpf=cpf
        )
        
        # Remove o cartão do colaborador

        status_user_cards = self._get_user_cards(chid=status_existence['CHid'])

        for item_card in status_user_cards['data']:

            requests.delete(
                f'{self.waccess_url}/cards/{item_card["CardID"]}',
                headers=self.waccess_headers,
                verify=False,
            )

        # Inativa o usuario no waccess

        reply = requests.put(
            f'{self.waccess_url}/cardholders/{status_existence["CHid"]}',
            headers=self.waccess_headers,
            json={
                'CHState': 1,
            },
            verify=False,
        )

        if reply.status_code == 204:
    
            return {
                'success':True,
                'code':'Usuario inativado com sucesso no waccess',
            }
        
        else:
        
            return {
                'success':False,
                'code':'Erro ao inativar usuario no waccess',
                'data':reply.json()
            }

    def _remove_groups(self, chid:str,cpf:str) -> bool:
        """
        Remove todos os grupos associados a um usuário específico no sistema WAccess.
        Args:
            chid (str): O ID do titular do cartão (Cardholder ID) no sistema WAccess.
            cpf (str): O CPF do usuário associado ao titular do cartão.
        Returns:
            bool: Retorna True se os grupos foram removidos com sucesso, 
                  caso contrário, retorna False.
        Detalhes:
            - Faz uma requisição GET para obter os grupos associados ao titular do cartão.
            - Prepara uma lista de ações para remover todos os grupos encontrados.
            - Chama o método `change_groups_user` para aplicar as alterações.
            - Retorna False se a requisição inicial falhar.
        """

        try:

            RemoveGroupsValidator(
                chid=chid,
                cpf=cpf
            )

        except Exception as e:
    
            raise ValueError("Erro na validação dos dados de input da remoção dos grupos do usuario:", e.errors())

        reply = requests.get(
            f'{self.waccess_url}/cardholders/{chid}/groups',
            headers=self.waccess_headers,
            verify=False,
        )

        if reply.status_code == 200:

            groups  = reply.json()

            groups_remove = []

            for item_group in groups:
                
                groups_remove.append({
                    'action':'remove',
                    'group_id':item_group['GroupID']
                })

            self.change_groups_user(
                cpf=cpf,
                groups_list=groups_remove
            )

            return True

        else:

            return False
