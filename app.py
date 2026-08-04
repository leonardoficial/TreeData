###############################################################################
#                                                                             #
#   Tree Data Manager                                                         #
#   Versão 1.0.0.0 (Beta)                                                     #
#   Leonardo Amaral de Souza                                                  #
#   Rio de Janeiro, 12/09/1997                                                #
#                                                                             #
###############################################################################


# Bibliotecas padrões para serviços.
import os
import json
import logging
import pathlib

# Bibliotecas próprias para o projeto.
from treedata.controller import Middleware


# Classe principal.
class TreeData:

    # Logger da aplicação.
    logger = None
    
    # Configurações da aplicação.
    settings = {}


    def __init__(self, link, parameters=None, settings={}):
        
        # Sistema de logging configurado.
        self.logger = logging.getLogger("TreeData")

        # Mensagem para o suporte.
        self.logger.debug("Nova instância Tree Data!")

        # O status do objeto indica se ele está apto para uso.
        self.status = False

        # Intermediador entre lógica da aplicação e regras de negócios.
        self.middleware = Middleware(TreeData.settings)

        # Caso o parametrizador não seja informado, realiza a detecção automática.
        if not parameters:

            # Caminho completo da base de dados.
            name = link

            if settings.get("basename", True):

                # Nome base da fonte de dados.
                name = os.path.basename(link)

            # Parametrizador detectado pelo nome do link.
            parameters = self.middleware.detect_parameters(name)

        # Parametrizador do link.
        self.parameters = self.middleware.parameters(parameters, settings)

        # Caso parametrizador não seja detectado, não é possível proceder.
        if not parameters or not self.parameters:

            # Mensagem para o suporte.
            self.logger.error("Não foi possível encontrar o parametrizador correspondente!")

            return None

        # Inicializa o link correspondente.
        self.link = self.parameters.LinkClass(link, self.parameters, TreeData.settings)

        # Caso o link não esteja apto para uso.
        if not self.link.status:

            # Mensagem para o suporte.
            self.logger.debug("Não foi possível conectar a fonte de dados!")
            
            return None
            
        # Padroniza o link com as regras do parametrizador.
        self.link = self.parameters.standardize_link(self.link)

        # Cria o objeto representativo a partir da junção lógica do link e parametrizador.
        self.structure = self.parameters.StructureClass(link=self.link, parameters=self.parameters, settings=settings)

        # Permite que os Plugins realizem tratativas no objeto criado.
        self.parameters.Plugins.post_standardize(self)

        # Atualiza o status de uso do objeto.
        self.status = True

        # Mensagem para o suporte.
        self.logger.debug("O objeto Tree Data foi criado!")
        

    def save(self, persistent=False, settings={}):

        # Garante que a estrutura esteja atualizada para salvamento.
        self.structure.save()

        # Persistência dos dados.
        if persistent:

            # Resultado do salvamento persistente.
            result = self.link.save(settings)

            # Mensagem para o suporte.
            #self.logger.debug("O objeto Tree Data foi salvo persistentemente!")

            return result

        return None
    

    @classmethod
    def configure(clss, path=None, configuration=None):
        '''
        Metódo responsável pelas seguintes operações:
        PROC-1: Carregar o arquivo de configuração principal da aplicação.
        PROC-2: Configurar e salvar persistentemente o arquivo de configuração.
        '''

        TreeData.logger.debug("ABERTURA DO ARQUIVO DE CONFIGURAÇÕES DE APLICAÇÃO!")
        
        # Configurações da aplicação.
        settings = {
            "default-exports": {
            		"csv": { "demiliter": "," }
            	},
            "paths": {
                "icons":        r"controller\icons",
                "tasks":	r"controller\tasks",
                "plugins":	r"controller\plugins",
                "layouts":	r"controller\layouts",
                "parameters":   r"controller\parameters",
                "dictionaries": r"controller\dictionaries"
            },
            "bases": {
		"NONE":     1,
		"CSN":	    4,
		"PSN":      7,
		"ENUM":     1,
		"BYTE":     1,
		"UBYTE":    1,
		"WORD":     2,
		"DWORD":    4,
		"UWORD":    2,
		"UDWORD":   4,
		"BITS8":    1,
		"BITS16":   2,
		"BITS32":   4,
		"DATETIME": 4,
            },
            "associate": {
		"^.*.csv$":  "CSV.json",
                "^.*.json$": "JSON.json"
            },
            "file": {
                "default": { "type": "decimal", "mode": "r", "saving-mode": "w" }
            }
        }

        # Diretório deste arquivo.
        folder_path = pathlib.Path(__file__).resolve().parent

        if path:

            settings_path = path

        else:
             settings_path = folder_path

        
        # Caminho padrão do arquivo de configurações principal.
        settings_path = os.path.join(settings_path, "settings.json")
        
        # Tenta abrir o arquivo de configurações.
        try:
            
            with open(settings_path, encoding="utf-8") as file:

                # Configurações customizadas.
                custom_settings = json.load(file)

                # Atualiza configuração padrão com a customizada.
                #settings.update(custom_settings)

                # Para cada.
                for main_key, dictionary in custom_settings.items():

                    # Somente para dicionários.
                    if not isinstance(dictionary, dict):

                        continue

                    if main_key not in settings:

                        settings[main_key] = {}

                    for sub_key, value in dictionary.items():

                        settings[main_key][sub_key] = value

                        #print(main_key, sub_key, value)

                # Altera as configurações caso solicitado.
                if configuration:

                    # Atualiza as configurações nativas com as novas carregadas.
                    settings.update(configuration)
        
                # Atualiza os caminhos absolutos.
                for key in settings['paths']:

                    if settings.get('path', False):

                        folder_path = settings['path']

                    settings['paths'][key] = os.path.join(folder_path, settings['paths'][key])
                
        except Exception:

            # Mensagem para o suporte.
            TreeData.logger.critical("Erro ao abrir o arquivo de configurações principal!")
            
            pass
        
        return settings


    @classmethod
    def configure_logger(clss):

        # Sistema de logs.
        logger = logging.getLogger("TreeData")
        
        # Evita duplicidade de logs.
        logger.propagate = False
        logger.handlers.clear()
        
        # Formatação padrão.
        formatter = logging.Formatter('[ %(levelname)s ] %(name)s: %(message)s')
        
        # Configuração de log para o console.
        ch = logging.StreamHandler()

        # Nível.
        ch.setLevel(logging.DEBUG)

        # Formatação.
        ch.setFormatter(formatter)
        
        # Adiciona os Handlers.
        logger.addHandler(ch)

        # Mensagem para o suporte.
        logger.info("Sistema de logging inicializado!")

        return logger


