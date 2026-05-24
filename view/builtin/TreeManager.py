###############################################################################
#                                                                             #
#   Tree Data Manager                                                         #
#   Versão 1.0.0.0 (Beta)                                                     #
#   Leonardo Amaral de Souza                                                  #
#   Rio de Janeiro, 12/09/1997                                                #
#                                                                             #
###############################################################################


# Bibliotecas próprias para serviços.
from copy    import copy
from os.path import join

# Bibliotecas padrões para interfaces gráficas.
from tkinter import *
from tkinter import ttk

# Bibliotecas próprias para o projeto.
from treedata import TreeData


# Classe principal.
class TreeManager:
    '''
    Classe responsável pelas seguintes operações:
    1. Auxiliar a classe da interface principal em operações com o objeto Tree.
    2. Manter referência aos registros, campos e destaques do objeto Tree.
    3. Proporcionar metódos para a criação, validação, atualização e remoção do objeto Tree.
    '''

    def __init__(self, *args, **kwargs):

        super(TreeManager, self).__init__()


    @staticmethod
    def validate_treedata(function):
        '''
        Método responsável pelas seguintes operações:
        1. Criar decorador para validar a existência e estado do objeto Tree interno antes de execução.
        '''
        
        def wrapper(self, *args, **kwargs):

            if self.application.treedata and self.application.treedata.status:

                # Executa a função.
                return function(self, *args, **kwargs)

        return wrapper


    def reset_treedata_tracking(self):
        '''
        Método responsável pelas seguintes operações:
        1. Resetar o valor das variáveis de controle internas.
        '''
        
        # Referência aos registros e campos.
        self.records = {}
        self.fields  = {}

        # Referência aos registros em destaque.
        self.tracking = {}

        return None
        

    def create_treedata(self, *args, **kwargs):
        '''
        Método responsável pelas seguintes operações:
        1. Auxiliar na criação do objeto Tree Data.
        '''

        # Cria novo objeto Tree Data.
        new_treedata = TreeData(*args, **kwargs)

        return new_treedata


    def delete_treedata(self, *args, **kwargs):
        '''
        Método responsável pelas seguintes operações:
        1. Auxiliar na exclusão do objeto Tree Data.
        '''

        # Deleta o objeto Tree atual.
        del self.treedata

        # Associa o valor padrão.
        self.treedata = None

        return None


    def replace_treedata(self, treedata):
        '''
        Método responsável pelas seguintes operações:
        1. Resetar as variáveis internas de controle.
        2. Substituir o objeto Tree Data interno por uma nova instância.
        '''

        # Reseta as variáveis internas.
        self.reset_treedata_tracking()

        # Valida se informaram o objeto correto.
        if not isinstance(treedata, TreeData):

            # O objeto deve ser do tipo Tree Data ou nada.
            self.treedata = None
            
            return None

        # Novo objeto Tree Data.
        self.treedata = treedata
    
        # Atualiza as configurações da interface gráfica.
        self.settings = treedata.parameters.rules.get('view')

        return treedata
        
