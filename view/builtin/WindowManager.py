###############################################################################
#                                                                             #
#   Tree Data Manager                                                         #
#   Versão 1.0.0.0 (Beta)                                                     #
#   Leonardo Amaral de Souza                                                  #
#   Rio de Janeiro, 12/09/1997                                                #
#                                                                             #
###############################################################################


#from eksoffice import EksOffice

from tkinter import *
from tkinter import ttk

class WindowManager:
    '''
    Classe responsável pelas seguintes operações:
    1. Auxiliar a classe da interface principal em operações com a janela principal.
    2. Proporcionar metódos para a criação, validação, atualização e remoção da janela principal.
    3. Manter referência aos registros e campos criados na interface.
    '''

    def __init__(self):

        pass





class StandardResult(object):
    '''
    Classe responsável pelas seguintes operações:
    1. Padronizar o resultado das janelas gráficas de componentes.
    1. Proporcionar metódos auxiliares para a manipulação do resultado.
    '''
    
    def __init__(self):

        # Variáveis.
        self.variables = {}

        # Registros obtidos no resultado.
        self.records = []

        # Campos obtidos no resultado.
        self.fields = []
        
        # Ações não devem ser executadas.
        self.no_trigger = BooleanVar()

        # Variáveis para ações genéricas.
        self.variable_boolean = BooleanVar()

        # Variáveis para ações específicas.
        self.trigger_highlight = BooleanVar()
        self.trigger_newwindow = BooleanVar()

        # Bandeira para solicitar o restart da interface gráfica.
        self.restart_gui = None

        # Caminhos.
        self.path1 = None
        self.path2 = None


    def get(self, name):

        if name not in self.variables:

            return None

        return self.variables.get(name)


    def set_boolean(self, name, overwrite=True):

        if name in self.variables and not overwrite:

            return None

        self.variables[name] = BooleanVar()

        return


    def callback(self, *args, **kwargs):

        return None


    def process(self, *args, **kwargs):

        return None

   
