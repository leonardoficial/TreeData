###############################################################################
#                                                                             #
#   Tree Data Manager                                                         #
#   Versão 1.0.0.0 (Beta)                                                     #
#   Leonardo Amaral de Souza                                                  #
#   Rio de Janeiro, 12/09/1997                                                #
#                                                                             #
###############################################################################

# Teste mobile.

import os, re, sys, importlib.util, json, shlex, codecs, logging, uuid, pathlib


from pathlib import Path

from configparser           import ConfigParser
from importlib.machinery    import SourceFileLoader
from importlib.util         import spec_from_loader, module_from_spec

from treedata.model        import File, FileTable, SQLDatabase
from treedata.model        import StructureTable, StructureJSON, StructureLayout, StructureConfigParser

from treedata.util         import ExpressionService, FunctionService


# Padrão de Design usado para retornar a referência ao objeto já inicializado.
# Importante para o desempenho da aplicação visto que diversos arquivos podem usar o mesmo layout.

def singleton(_class):
    
    instances = {}
    
    def getinstance(*args, **kwargs):
        
        if _class not in instances:
            
            instances[_class] = _class(*args, **kwargs)

        return instances[_class]
    
    return getinstance


@singleton
class Middleware:
    '''
    Classe responsável pelas seguintes operações:
    PROC-1: Disponibilizar os arquivos de layouts e parâmetros, retornando o singleton por demanda.
    '''

    def __init__(self, settings={}, extra_settings={}):

        # Sistema de logging configurado.
        self.logger = logging.getLogger("TreeData.Middleware")

        # Referência às configurações da aplicação Tree Data.
        self.settings = settings

        # Variáveis para controle dos layouts.
        self.layouts_dict = {}
        self.layouts_list = []

        # Variáveis para controle dos parametros
        self.paramaters_dict = {}
        self.parameters_list = []

        # Caminho do diretório de layouts.
        self.path = pathlib.Path(__file__).resolve().parent

        # Caso não seja possível localizar o diretório de layouts,
        if not os.path.exists(self.path):
            
            # Mensagem para o suporte.
            self.logger.critical("Não foi possível localizar o diretório do Middleware!")

            return None

        # Lista os parametrizadores disponíveis.
        #self.availables = self.list_parameters(extra_settings)


    @staticmethod
    def execute(this, path, globalss, context):
        '''
        Método responsável pelas seguintes operações:
        PROC-1: Carregar o arquivo de tarefa informado pelo caminho.
        PROC-2: TAGGED-IMPROVE: Descriptografar o arquivo de tarefa.
        PROC-3: Executar a tarefa passando somente os contextos necessários.
        '''

        # Código da tarefa a ser executada.
        task_code = ""

        # TAGGED-IMPROVE: Validar se o arquivo existe antes.
        if not path or not os.path.exists(path):

            # Mensagem para o suporte.
            #self.logger.error("Não foi possível localizar o arquivo de tarefa!")

            return None

        # Tenta ler o arquivo de tarefa.
        try:

            with open(path, "r") as file:

                # Leitura do código da tarefa.
                task_code = file.read()
            
        except:

            # Mensagem para o suporte.
            self.logger.error("Não foi possível carregar o arquivo de tarefa!")

            return None
    
        # Tenta executar o código da tarefa.
        try:

            # Configura o objeto a ser trabalhado no contexto.
            context['treedata'] = this
            context['this'] = this

            # Execução da tarefa.
            exec(task_code, globalss, context)

            return True

        except:

            print("ERRO AO EXECUTAR")

            pass
            # Mensagem para o suporte.
            #self.logger.error("Não foi possível executar o código da tarefa!")
        
        
        return True

        
    def parameters(self, name, settings={}):
        '''
        Método responsável pelas seguintes operações:
        PROC-1: Carregar o arquivo de parâmetros solicitado.
        PROC-2: Retornar a instância configurada da classe Parameters.
        '''
        
        # Parâmetro encontrado.
        parameter = None

        # Procura parâmetro no controle interno.
        if name in self.parameters_list:
            
            parameter = self.paramaters_dict[name]

        # Caso não encontrado, carrega o arquivo de parâmetro.
        else:

            path = os.path.join(self.path, "parameters")

            path = self.settings['paths']['parameters']

            # Carrega o arquivo de parâmetros.
            parameter = Parameters(name, path, self.settings, settings)

            # Em caso de erros.
            if not parameter.status:
                
                # Mensagem para o suporte.
                self.logger.debug("Não foi possível carregar os parâmetros!")

                return None

            # Atualiza o parâmetro carregado no controle interno.
            self.parameters_list.append(name)
            self.paramaters_dict[name] = parameter

        return parameter


    def layout(self, name: str, parameters):
        '''
        Método responsável pelas seguintes operações:
        PROC-1: Carregar o arquivo de layout solicitado.
        PROC-2: Retornar a instância configurada da classe Layout.
        '''

        # Layout encontrado.
        layout = None

        # Caminho completo do arquivo de layout (IMPROVE).
        path = os.path.join(self.path, "layouts")

        path = self.settings['paths']['layouts']


        # Procura layout no controle interno primeiro.
        if name in self.layouts_list:
            
            layout = self.layouts_dict[name]

        # Caso não encontrado, carrega o arquivo do layout.
        else:
            
            layout = Layout(name, path, parameters, self.settings)

            # Em caso de erros.
            if not layout.status:
                
                # Mensagem para o suporte.
                self.logger.debug("Não foi possível carregar o layout!")

                return None

            # Atualiza o layout carregado no controle interno.
            self.layouts_list.append(name)
            self.layouts_dict[name] = layout

        return layout


    def list_parameters(self, settings):

        # Arquivos de parâmetros disponíveis.
        availables = {}

        # Lista os arquivos disponíveis.
        parameters_list = next(os.walk(self.path))[2]

        # Para cada parâmetro.
        for parameters_name in parameters_list:

            # Detalhes sobre o parâmetro.
            paramaters_details = self.detail_parameters(parameters_name)

            # Filtro por tipo.
            filter_type = settings.get('filter-parameters', False)
            
            # Filtro por tipo de parâmetro.
            if filter_type:

                # Validação.
                if filter_type != paramaters_details['type']:
            
                    continue

                # Parâmetros filtrados são mapeados pelo nome base.
                parameters_name = paramaters_details['base-name']
                
            # Detalhes do parametrizador disponível.
            availables[parameters_name] =  paramaters_details

        return availables


    def detail_parameters(self, parameters_full_name):
        '''
        Método responsável pelas seguintes operações:
        PROC-1: Detalhar informações sobre o parametrizador.
        '''

        # TAGGED-IMPROVE: Adiconar regex para validar o nome do parâmetro.

        # Extração.
        try:
            
            parameters_type, parameters_base_name, parameters_extension = parameters_full_name.split(".")
            
        except:

            # Mensagem para o suporte.
            self.logger.error("Não foi possível detalhar o parâmetro pelo nome!")

            return None

        # Detalhado do resultado.
        result = {
            'type': parameters_type,
            'base-name': parameters_base_name,
            'full-name': parameters_full_name,
            'extension': parameters_extension
        }

        return result


    def detect_parameters(self, link):
        '''
        Método responsável pelas seguintes operações:
        PROC-1: Detectar o parametrizador com base no nome do link informado.
        '''
        
        # Retorno padrão para caso não encontre layout para o arquivo.
        parameters_name = None

        # Mapeamentos de parametrizador.
        associations = self.settings.get("associate", {}).items()
        
        # Para cada mapeamento de arquivo salvo.
        for regex, parameters_name in associations:

            # Expressão regular.
            regex = re.compile(regex, re.IGNORECASE)
            
            if re.match(regex, link):

                # Parametrizador encontrado
                return parameters_name
            
        # Mensagem para o suporte.
        self.logger.debug("Não foi possível encontrar parametrizador para o link '%s'", link)


class Layout(object):
    '''
    Classe responsável pelas seguintes operações:
    PROC-1: Carregar o arquivo do layout solicitado.
    '''

    def __init__(self, name, path, parameters, settings):

        # Variáveis internas.
        self.name     = name
        self.path     = path
        self.offset   = 0
        self.records  = {}

        # O status do objeto indica se ele está apto para uso.
        self.status = True

        # Referência às configurações da aplicação Tree Data.
        self.settings = settings

        # Referência ao objeto de parâmetros correspondente ao layout.
        self.parameters = parameters

        # Caminho absoluto para o arquivo do layout solicitado.
        layout_path = os.path.join(path, name)

        # Verifica a existência do arquivo de layout.
        if not os.path.exists(layout_path):
            
            return None

        # Regras de configuração do campo.
        field_settings = self.parameters.rules['link']['settings'].get("field", {})

        # Expressão regular utilizada para localizar os campos.
        field_regex = field_settings.get("ID-regex")

        # Compila a expressão regular.
        field_regex = re.compile(field_regex, re.IGNORECASE)

        # Processo de parse dos dados do arquivo.
        self.parser = ConfigParser(interpolation=None)
        self.parser.read( layout_path, encoding="utf-8" )

        # Para cada tipo de registro.
        for record_name in self.parser.sections():

            # Modelo do registro.
            new_record = dict(name=record_name, offset=0, fields={})

            # Adiciona o dicinário ao controle interno.
            self.records[record_name] = new_record

            # Para cada campo do registro.
            for item in self.parser.items(record_name):

                # Nome do campo e valores.
                field_name = item[0]
                field_data = item[1]

                # Os fields são vetores, então devem ser tratados separadamente dos demais campos.
                if field_regex.match(field_name):

                    # Tenta configurar o campo field com as regras internas da aplicação.
                    try:

                        # Nome das variáveis do campo de acordo com o layout.
                        variables_name = field_settings.get("variables")
                        
                        # Valores das variáveis de configuração do campo.
                        variables_data = shlex.split(field_data)

                        # O consumo padrão de bytes está pré-definido para 1 no modelo de campo.
                        field_layout = dict(bytes=1)

                        # Seta as variáveis de configuração do campo.
                        for index, value in enumerate( variables_data ):

                            # Nome da configuração.
                            variable_value = variables_name[index]

                            # Atualiza o modelo de campo.
                            field_layout[variable_value] = value
                        
                        # Valor de consumo de bytes padrão para cada tipo.
                        bases = self.settings["bases"]

                        # Caso tipo do campo esteja cadastrado, associar o valor de bytes.
                        if "type" in field_layout and field_layout["type"] in bases:

                            # Tipo do campo.
                            field_type = field_layout["type"]

                            # Associação ao valor catalogado.
                            field_layout["bytes"] = bases[field_type]

                        # O consumo explícito de bytes é definido pela propriedade "override_bytes".
                        # Caso não esteja presente, será utilizado o consumo padrão pré-definido ou catalogado.
                        if "override_bytes" in field_layout:

                            # Consumo de bytes do campo.
                            field_override_bytes = field_layout["override_bytes"]

                            # Associa ao valor catalogado.
                            field_layout["bytes"] = int( field_override_bytes )

                        # Novo offset total do registro.
                        offset_total = int(new_record["offset"]) + int(field_layout["bytes"])

                        # Atualiza o offset total do registro.
                        new_record.update(offset=offset_total)

                        # Adiciona campo ao registro.
                        new_record["fields"][field_name] = field_layout

                    # Em caso de erro ao configurar os campos.
                    except:
                        
                        # Desabilita o objeto para uso.
                        self.status = False
                        
                        # Mensagem para o suporte.
                        self.logger.warning("Não foi possível criar regras de layout para o campo '%s.%s'", record_name, field_name)

                        break

                # Caso nome do campo não seja FIELD, ignorar regras específicas.
                else:
                    
                    new_record[field_name] = field_data

            # Caso haja erro de configuração dos campos no loop, não proceder.
            if not self.status:
                
                # Mensagem para o suporte.
                self.logger.error("Não foi possível carregar o arquivo do layout!")

                break
        

class Parameters(object):
    '''
    Classe responsável pelas seguintes operações:
    PROC-1: Carregar o arquivo de parâmetros solicitado.
    PROC-2: Padronizar o ID do registro para encaixe no layout.
    PROC-3: Padronizar o arquivo de registros para encaixe no layout.
    '''

    def __init__(self, name, path, settings, custom_settings={}):

        # Sistema de logging configurado.
        self.logger = logging.getLogger("TreeData.Parameters")

        # Nome fantasia padrão.
        self.name = Path(name).stem

        # Nome do arquivo.
        self.file_name = name

        # Caminho completo do arquivo.
        self.path = os.path.join( path, name )

        # Caminho do diretório.
        self.folder_path = path

        # Referência às configurações da aplicação.
        self.settings = settings

        # O status do objeto indica se ele está apto para uso.
        self.status = True
        
        # Regras carregadas.
        self.rules = None

        # Dados externos mapeados.
        self.dictionary = None

        # Funções externas mapeadas.
        self.Plugins = Plugins()

        # API de conexão.
        self.LinkClass = None

        # Estrutura dos dados.
        self.StructureClass = None

        # TAGGED
        # Inicializa configuração do parametrizador.
        self.initialize(custom_settings)


    def initialize(self, settings={}):

        # Carrega o arquivo de configurações principal.
        self._load_configuration(settings)

        # Necessita do arquivo de regras carregado para continuar.
        if not self.rules:

            # Não está apto para uso.
            self.status = False

            return None

        # Configuração do nome fantasia.
        self.name = self.rules.get('name', self.name)

        # Carrega o arquivo de dicionário dos valores.
        self._load_dictionary()

        # Mapeia os elementos construtores.
        self._map_constructors()

        # Mapeia o caminho absoluto das tarefas.
        self._map_tasks()

        # Carrega os plugins externos.
        self._load_plugins()
        

    # TAGGED: Adicionei esse parâmetro settings na gambiarra.
    def _load_configuration(self, settings={}):
        
        # Caminho absoluto para o arquivo de regras solicitado.
        rules_path = self.path

        # Tenta abrir o arquivo.
        try:
            
            with open( rules_path, encoding="utf-8" ) as file:

                # Salva os dados carregados.
                self.rules = json.load( file )

            # TAGGED
            # Mescla os arquivos de parâmetros.
            FunctionService.update(self.rules, settings)

            # Caso seja solicitada a extensão dos parâmetros.
            rules_extension = self.rules.get('@extends', False)

            if rules_extension:

                # Caminho completo do arquivo de extensão.
                rules2_path = os.path.join(self.folder_path, rules_extension)

                # Carrega o arquivo de extensão.
                with open( rules2_path, encoding="utf-8" ) as file:

                    # Salva os dados carregados.
                    rules2 = json.load( file )

                # Mescla os arquivos de parâmetros.
                FunctionService.update(self.rules, rules2)
            # Mensagem de suporte.
            self.logger.debug("O arquivo de regras '%s' foi carregado!", self.name)

        except Exception as error:
            
            # Desabilita o objeto para uso.
            self.status = False
            
            # Mensagem de suporte.
            self.logger.warning("Não foi possível carregar o arquivo de regras '%s'", self.name)
            
            print(rules_path, repr(error))

        return None

    def _load_dictionary(self):

        # Diretório de dicionários principal.
        dictionaries_folder = self.settings.get('paths').get('dictionaries')

        # Arquivo de dicionário do parametrizador.
        dictionary_file = self.rules['link']['settings'].get('field', {}).get('dictionary', False)

        if not dictionary_file:

            return None

        # Caminho completo do arquivo.
        dictionary_path = os.path.join(dictionaries_folder, dictionary_file)

        # Tenta abrir o arquivo.
        try:
            
            with open( dictionary_path, encoding="utf-8" ) as file:

                # Salva os dados carregados.
                self.dictionary = json.load( file )

                # Mensagem de suporte.
                self.logger.debug("O arquivo de dicionário '%s' foi carregado!", dictionary_file)

        except:

            # Mensagem de suporte.
            self.logger.warning("Não foi possível carregar o arquivo de dicionário '%s'!", dictionary_file)


    def _load_plugins(self):

        # Configurações dos plugins do parametrizador.
        parameters_plugins = self.rules.get('plugins', {})

        # Diretório de plugins principal.
        plugins_folder = self.settings.get('paths').get('plugins', '')

        # Diretório de plugins do parametrizador.
        par_plugins_folder = parameters_plugins.get('folder', '')

        # Caminho completo do diretório de plugins do parametrizador.
        par_plugins_path = os.path.join(plugins_folder, par_plugins_folder)

        # Delega a criação dos plugins.
        self.Plugins.load(par_plugins_path, parameters_plugins)

        return None


    def _map_tasks(self):

        # Configuração das tarefas.
        parameters_tasks = self.rules.get('task', {})

        # Diretório de tarefas principal.
        tasks_folder = self.settings.get('paths').get('tasks')

        # Diretório de tarefas do parametrizador.
        par_tasks_folder = parameters_tasks.get('folder', '')

        # TAGGED-IMPROVE
        
        # Atualiza o caminho principal do diretório das tarefas.
        parameters_tasks['folder'] = os.path.join(tasks_folder, par_tasks_folder)


    def _map_constructors(self):
        
        # Interface de conexão.
        parameter_API = self.rules.get('link', {}).get('DATA-API', "").upper()

        # Formato dos dados carregados.
        parameter_MAP = self.rules.get('link', {}).get('DATA-MAP', "").upper()

        # API de conexão.
        self.LinkClass = File

        # Estrutura dos dados.
        self.StructureClass = None

        # API de banco de dados.
        if parameter_API == "SQL":
                    
            # CRUD.
            self.LinkClass = SQLDatabase

        # API de REST.
        elif parameter_API == "REST":

            pass

        # Dados de formato CSV.
        if parameter_MAP == "TABLE":

            # Estrutura.
            self.StructureClass = StructureTable

            # API de arquivo.
            if parameter_API == "FILE":
                
                # CRUD.
                self.LinkClass = FileTable

        # Dados em dicionário.
        elif parameter_MAP == "JSON":

            # Estrutura.
            self.StructureClass = StructureJSON

        # Dados em secção.
        elif parameter_MAP == "INI":

            # Estrutura.
            self.StructureClass = StructureConfigParser

        # Dados em vetor.
        elif parameter_MAP == "LAYOUT":

            # Estrutura.
            self.StructureClass = StructureLayout

    
    def standardize_link(self, link):
        '''
        Padroniza o arquivo uso do layout.
        '''

        return link


    def standardize_recordID(self, record_ID):
        '''
        Padroniza o ID do regisro para uso do layout.
        '''
        # Solicitação de conversão.
        conversion = self.rules.get('link').get('settings').get("record").get("ID-conversion", None)
        
        if conversion == "decimal":

            record_ID = int(record_ID[0] , 16)

        return record_ID


    def pre_standardize_record(self, record):

        # Palavra-Chave do nome do registro no layout.
        if self.rules.get('link').get('settings').get("layout", None):
                
            name_keyword = self.rules['link']['settings']["layout"].get("name-keyword", False).lower()

            if name_keyword:
                
                # Altera o nome do registro para o nome customizado no layout.
                record.name = record.layout.get(name_keyword, record.name)

        # Parâmetros de configurações complexas.
        complex_rules = self.rules.get("complex.records", {})

        # Verifica se há configurações para o registro.
        if record.name not in complex_rules:

            return record

        # Configuração para o registro.
        record_rules = complex_rules[ record.name ]

        # Configuração do nome personalizado.
        record.name = record_rules.get("name", record.name)

        # Configuração da chave estrangeira.
        record.foreign_key = record_rules.get("foreign-key", None)

        # Configuração dos rótulos.
        record.labels = record_rules.get("tags", [])

        return record


    def post_standardize_record(self, record):

        # TAGGED-IMPROVE.
        # Nova customização do nome.
        new_name = self.rules['link']['settings'].get('record', {}).get('name', None)

        # Retorna o valor do campo.
        new_name = record.get(new_name, bydescription=True, value=True)

        # Associa caso tenha valor.
        if new_name: record.name = new_name

        # Parâmetros de configurações complexas.
        complex_rules = self.rules.get("complex.records", {})

        # Realiza a avaliação dos condicionais genéricos primeiro.
        if '*' in complex_rules:

            # Configurações genéricas para todos os registros.
            generic_rules = complex_rules['*']

            # Aplica.
            self.apply_conditionals(record, generic_rules)

        # Verifica se há configurações para o registro.
        if record.name in complex_rules:

            # Configurações específicas do registro.
            record_rules = complex_rules[record.name]

            # Aplica.
            self.apply_conditionals(record, record_rules)

            # Monta a chave única estrangeira.
            foreign_id_string = ""
                
            for foreign_key_name in record_rules.get("foreign-id", []):

                # Valor da chave estrangeira.
                foreign_key_value = record.get(foreign_key_name, value=True, byforeign_key=True)

                foreign_id_string = foreign_id_string + str(foreign_key_value)

            # Configuração da chave estrangeira única.
            record.foreign_id = foreign_id_string
            
        return record


    def standardize_field(self, field, settings={}):

        # Converte o valor do campo para a base.
        field.convert(field.base)

        # Parâmetros de configurações complexas.
        complex_rules = self.rules.get("complex.fields", {})
                
        # Verifica se há configuração para esse campo.
        if field.name not in complex_rules:

            return field

        # Parâmetros de configuração do campo.
        complex_rules = complex_rules.get(field.name, {})

        # Associação.
        field.this_rules = complex_rules

        # Configuração da chave estrangeira.
        field.foreign_key = complex_rules.get("foreign-key", None)

        #  Base de conversão cadastrada para o campo.
        conversion_base = complex_rules.get("conversion", None)

        if conversion_base:
            
            # Conversão de valor do campo.
            field.base = conversion_base
            
        # Converte o valor do campo para a base.
        field.convert(field.base)
                    
        # Nome do catálogo de dados externos.
        dictionary_key = complex_rules.get("dictionary-key", None)

        # Caso haja mapeamento externo para o valor do campo.
        if dictionary_key:

            self.apply_dictionary(field, dictionary_key, settings)

        return field


    def apply_dictionary(self, field, dictionary_key, settings):

        # Valor externo do campo.
        dictionary_value = None

        # Expressões encontradas na chave de dicionário.
        expression = ExpressionService.expressions(dictionary_key)

        if len(expression) and expression[0].get('value', False):

            # Referência do registro do campo.
            record = settings.get('record', {})

            # Chave estrangeira do campo a ser referênciado.
            sibling_field_FK = expression[0].get('value')

            # Valor do campo referenciado.
            siblind_field_value = record.get(sibling_field_FK, value=True, byforeign_key=True)

            # Chave do dicionário atual é o valor do campo referenciado.
            dictionary_key = siblind_field_value

        # Verifica se o catálogo está carregado.
        dictionary = self.dictionary.get(dictionary_key, None)

        if dictionary and field.value in dictionary:

            # Valor no dicionário em string.
            dictionary_value = str(dictionary[field.value])

        # Altera o valor externo deste campo para o valor encontrado.
        field.dictionary_value = dictionary_value

        
    def apply_conditionals(self, record, rules):
        
        # Configurações condicionais do registro.
        conditionals = rules.get('conditionals', [])

        for condition in conditionals:

            result = False

            condition_rule = condition.get('if', False)

            # Verifica se o condicional retorna valor verdadeiro e sem erros.
            try:    result = bool( eval(condition_rule) )
            except: result = False

            if result:

                # Configurações especiais para o registro.
                record.conditionals = condition

                return record

        return record


class Plugins:

    def __init__(self):

        # Controle de plugins.
        self.plugins = {}


    def load(self, path, rules):
        
        # Validação do caminho.
        if not path or not os.path.exists(path) or not os.listdir(path):

            return False

        # Configurações dos plugin a serem carregados.
        plugins_settings = rules.get('settings', {})

        # Lista os arquivos disponíveis no diretório de plugins.
        plugins_files = next(os.walk(path))[2]

        # Para cada arquivo de plugin.
        for plugin_file in plugins_files:

            # Nome do plugin deve estar incluído nas configurações.
            if plugin_file not in plugins_settings:

                continue

            # Configurações do plugin específico.
            plugin_settings = plugins_settings[plugin_file]

            # Mapeia o plugin no controle.
            self.plugins[plugin_file] = {
                'status': None,
                'module': None,
                'config': None
            }

            # Caminho completo do plugin.
            plugin_path = os.path.join(path, plugin_file)

            # Tenta carregar o conteúdo do plugin.
            try:

                # Especificação.
                spec = importlib.util.spec_from_file_location(plugin_file, plugin_path)

                # Módulo.
                module = importlib.util.module_from_spec(spec)

                # Execução do módulo no escopo.
                spec.loader.exec_module(module)
        
                # O plugin deve conter a classe exportável apropriada:
                if "Plugin" not in dir(module):

                    continue

                # Atualiza o plugin no controle.
                self.plugins[plugin_file]['status'] = True
                self.plugins[plugin_file]['module'] = module.Plugin
                self.plugins[plugin_file]['config'] = plugin_settings

            # Erro ao tentar carregar plugin.
            except:

                # Atualiza o plugin no controle.
                self.plugins[plugin_file]['status'] = False

        return True


    def post_standardize(self, treedata):

        # Para cada plugin do controle.
        for plugin_name, plugin in self.plugins.items():

            # Ignora plugins com falha.
            if not plugin.get('status'):

                continue

            # Tenta executar função apropriada.
            try:

                # Módulo do plugin.
                module = plugin.get('module')

                # Configuração do plugin.
                config = plugin.get('config')

                # Executa função apropriada.
                module.post_standardize(treedata, config)

            # Erro ao executar função.
            except Exception as error:

                # Mensagem para o suporte.
                print("ERRO AO EXECUTAR PLUGIN:", plugin_name)

                print(repr(error))

                continue


