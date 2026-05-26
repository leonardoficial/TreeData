###############################################################################
#                                                                             #
#   Tree Data Manager                                                         #
#   Versão 1.0.0.0 (Beta)                                                     #
#   Leonardo Amaral de Souza                                                  #
#   Rio de Janeiro, 12/09/1997                                                #
#                                                                             #
###############################################################################


# Bibliotecas padrões.
import json
import logging

# Parametrização das regras personalizadas.
from treedata.controller import Middleware

# Interface para diferentes fontes de dados.
from treedata.model import (
    File,
    SQLDatabase
)

# Interfaces para diferentes tipos de campos.
from treedata.model.Field import (
    Field,
    FieldJSON,
    FieldLayout
)

# Interfaces para diferentes tipos de registros.
from treedata.model.Record import (
    Record, 
    RecordJSON,
    RecordTable,
    RecordLayout,
    RecordConfigParser
)


# Classe principal.
class Structure:
    """
    Provides an unique interface for building 
    and managing the <TreeData.*> object models.
    """


    def __init__(self, link=None, parameters=None, settings={}):
        """
        Creates variables used by the internal functions.
        Starts the processes responsible for configuring the application.

        PARAMETER 1: link: <TreeData.Link> object.
        PARAMETER 2: parameter: <TreeData.Parameters> object.
        PARAMETER 3: settings: Main configuration of the application.

        RETURNS: None.
        """
        
        # Sistema de logging configurado.
        self.logger = logging.getLogger("TreeData.Structure")

        # Fonte de dados administrável.
        self.link = link

        # Referência do Middleware intermediador.
        self.middleware = Middleware.Middleware()

        # Parametrizador administrável.
        self.parameters = parameters
        
        # Regras de configuração.
        self.rules = self.parameters.rules

        # Variáveis de controle dos registros.
        self.records = []
        self.records_ids = {}
        self.records_groups = {}
        self.records_labels = {}
        self.records_foreign_ids = {}
        self.records_foreign_keys = {}

        # Callback para informar o progresso da criação dos registros.
        callback = settings.get('callback.progress', lambda data: None)

        # Configuração dos callbacks.
        self._callback_progress = callback

        # Inicializa o processamento de dados.
        if settings.get('initialize', True):

            # Mensagem de suporte.
            self.logger.debug("Início da criação do objeto TreeData!")
            
            self.initialize()

        return None


    def initialize(self, *args, **kwargs):
        """
        Starts the required processes of the life-cycle boot.
        * This method should be overriden for better implementation.
        
        1. Builds the structure of the <TreeData> Record and Fields objects.
        2. Standardizes the objects according to the <TreeData.Parameters>.

        RETURNS: None.
        """
        
        return None


    def callback_progress(self, data):
        """
        Informs the creation progress to the registered callback function.

        PARAMETER: data: <Dict> object with "total" and "value" keys.

        RETURNS: None.
        """
        
        # Invoca o callback de progresso do carregamento.
        self._callback_progress(data)

        return None


    def reset(self):
        """
        Resets the control variables of the records.

        RETURNS: None.
        """

        # Esvazia a lista por íncide.
        self.records.clear()

        # Esvazia a lista por ID.
        self.records_ids.clear()

        # Esvazia a lista por grupos de nomes.
        self.records_groups.clear()

        # Esvazia a lista por rótulos.
        self.records_labels.clear()

        # Esvazia a lista por ID estrangeiro.
        self.records_foreign_ids.clear()

        # Esvazia a lista por chave estrangeira.
        self.records_foreign_keys.clear()

        return None


    def restart(self):
        """
        Restarts the current system life-cycle.

        RETURNS: None.
        """

        # Remove os dados internos.
        self.reset()

        # Inicializa o processamento dos dados.
        self.initialize()

        return None
    

    def delete(self, record):
        """
        Removes the <TreeData.Record> object from the structure.

        PARAMETER: record: <TreeData.Record> object.

        RETURNS: None.
        """
        
        # Remove as referências gerais.
        self.records.remove(record)
        self.records_groups[record.name].remove(record)

        # Remove as referências por ID.
        del self.records_ids[record.id]

        # Remove as referências por ID estrangeiro.
        if record.foreign_id:
            
            del self.records_foreign_ids[record.foreign_id]

        # Remove as referências por chave estrangeira.
        if record.foreign_key:
            
            self.records_foreign_keys[record.foreign_key].remove(record)

        # Remove as referências dos rótulos.
        for label in record.labels:

            if record in self.records_labels[label]:
                
                self.records_labels[label].remove(record)

        return None


    def save(self):
        """
        Updates the <TreeData.Structure> while iterating over it's records.
        * This method should be overriden for better implementation.
        
        RETURNS: <Boolean> Flag to inform the result of the saving.
        """
        
        return None


    @staticmethod
    def _save(function):
        """
        Standardizes the logging outputs related to the saving methods.
        
        RETURNS: Function wrapper.
        """
        
        def wrapper(self, *args, **kwargs):

            # Executa a função.
            result = function(self, *args, **kwargs)

            # Sucesso.
            if result:
                
                # Mensagem para o suporte.
                self.logger.debug("A estrutura principal do objeto Tree Data foi atualizada!")

            # Falha.
            else:
                
                # Mensagem para o suporte.
                self.logger.debug("Não foi possível atualizar a estrutura principal do objeto Tree Data!")
            
        return wrapper

    
    def map_references(self, record):
        """
        Maps the <TreeData.Record> object to the internal controle variables.
        
        PARAMETER: record: <TreeData.Record> object.
        """

        # Controle geral.
        self.records.append(record)

        # Controle por ID
        self.records_ids[record.id] = record

        # Controle por ID estrangeiro.
        self.records_foreign_ids[record.foreign_id] = record

        # Controle por chave estrangeira.
        if record.foreign_key:

            if record.foreign_key not in self.records_foreign_keys:

                # Cria grupo de referências por chave estrangeira.
                self.records_foreign_keys[record.foreign_key] = []

            # Controle por chave estrangeira.
            self.records_foreign_keys[record.foreign_key].append(record)

        # Configuração do grupo auxiliar de registros.
        if record.name not in self.records_groups:

            # Cria o registro no grupo auxiliar.
            self.records_groups[record.name] = []

        # Controle por grupo de nomes.
        self.records_groups[record.name].append(record)

        # Controle por rótulos.
        if len(record.labels):

            # Para cada rótulo.
            for record_label in record.labels:
            
                if record_label not in self.records_labels:

                    # Cria grupo de referências por rótulo.
                    self.records_labels[record_label] = []
                        
                # Controle por rótulos.
                self.records_labels[record_label].append(record)

        return None


class StructureConfigParser(Structure):
    """
    Interface for building and managing the <TreeData.*> object models.
    Used exclusively for structured CONFIGURATION PARSER data.
    
    SUPER 1: Manages the <TreeData.Structure> object life-cycle.
    """


    def __init__(self, *args, **kwargs):
        """
        Creates variables used by the internal functions.
        Starts the processes responsible for configuring the application.

        RETURNS: None.
        """
       
        # Invoca o inicializador da classe principal.
        Structure.__init__(self, *args, **kwargs)

        return None


    def save(self):
        """
        Updates the <TreeData.Structure> while iterating over it's records.
        
        RETURNS: <Boolean> Flag to inform the result of the saving.
        """
        
        # Referência ao modificador ConfigParser.
        configparser = self.link.handler

        # Para cada seção.
        for record in self.records:

            # Para cada propriedade da seção.
            for field in record.fields:

                # Valor da propriedade.
                field = record.get(field, value=False)

                # Atualiza a mudança do valor no modifificador.
                configparser.set(record.name, field.name, field.value)

        return None

        
    def initialize(self):
        """
        Starts the required processes of the life-cycle boot.
        
        1. Builds the structure of <TreeData> Records Fields objects.
        2. Standardizes the objects according to the <TreeData.parameters>.

        RETURNS: None.
        """
        
        # Referência ao modificador ConfigParser.
        configparser = self.link.handler

        # Para cada seção.
        for section_name in configparser.sections():

            # Delega a criação do registro.
            record = RecordConfigParser(section_name, {}, self.parameters, None)

            # Por padrão, o nome do registro é igual ao nome da seção.
            record.name = section_name

            # Mapeia a referência do ConfigParser original.
            record.configparser = self.link.handler

            # Regras de configuração específicas do registro.
            record_settings = self.rules.get("record")

            # Permite que o Middleware realize tratativas no registro antes do preenchimento.
            record = self.parameters.pre_standardize_record(record)

            # Para cada propriedade da seção.
            for field_key, field_value in configparser.items(section_name):

                # Delega a criação do campo.
                field = Field(record, field_value, {}, self.parameters, None)

                # Nome do campo é a própria chave.
                field.name = field_key
                
                # Tipo de dado.
                field.type = "NONE"
                
                # Classe do dado.
                field.clss = RecordConfigParser.DATA_TYPE

                # Permite que o Middleware realize tratativas e consultas no campo criado.
                field = self.parameters.standardize_field(field)

                # Adiciona o campo criado ao controle.
                record.fields[field.name] = field

                # Adiciona referência as variáveis auxiliares.
                record.fields_names[field.name] = field

                if field.foreign_key:
                    
                    record.fields_foreign_keys[field.foreign_key] = field

            # Permite que o Middleware realize tratativas no registro criado.
            self.parameters.post_standardize_record(record)

            # Mapeia as referências nos controles internos.
            self.map_references(record)

        return None


class StructureTable(Structure):
    """
    Provides an interface for building and managing the <TreeData.*> object models.
    Used exclusively for structured TABLE data.
    
    SUPER 1: Class responsible for managing the <TreeData.Structure> object life-cycle.
    """

    def __init__(self, *args, **kwargs):
        """
        Creates variables used by the internal functions.
        Starts the processes responsible for configuring the application.

        RETURNS: None.
        """
       
        # Invoca o inicializador da classe principal.
        Structure.__init__(self, *args, **kwargs)

        return None


    def initialize(self):
        """
        Starts the required processes of the life-cycle boot.
        
        1. Builds the structure of <TreeData.Records> and <TreeData.Fields> objects.
        2. Standardizes the created objects according to the <TreeData.parameters>.

        RETURNS: None.
        """

        # Para cada linha.
        for record_index, record_vector in enumerate(self.link.handler):

            # Delega a criação do registro.
            record = RecordTable(record_vector, {}, self.parameters, None)

            # O nome do registro é o índice do vetor.
            record.name = str(record_index)

            # TAGGED-IMPROVE.
            record.index = record_index

            # Regras de configuração específicas do registro.
            record_settings = self.rules.get("record")

            # Para cada coluna da linha.
            for index, field_value in enumerate(record_vector):

                # Delega a criação do campo.
                field = Field(record, field_value, {}, self.parameters, None)

                # Nome do campo e a coluna associada.
                field.name = self.link.columns[index]

                # Tipo de dados.
                field.type = "NONE"

                # Classe do dado.
                field.clss = RecordConfigParser.DATA_TYPE

                # TAGGED-IMPROVE,
                field.index = index

                # Permite que o Middleware realize tratativas e consultas no campo criado.
                field = self.parameters.standardize_field(field)

                # Adiciona o campo criado ao controle.
                record.fields[field.name] = field

                # Adiciona referência as variáveis auxiliares.
                record.fields_names[field.name] = field

                # Adiciona mapemamento da chave estrangeira.
                if field.foreign_key:
                    
                    record.fields_foreign_keys[field.foreign_key] = field

            # TAGGED-IMPROVE - Mover essa função para antes do preenchimento.
            # Obs.: É necessário verificar o que foi feito nos parâmetros de configuração.
            # Permite que o Middleware realize tratativas no registro antes do preenchimento.
            record = self.parameters.pre_standardize_record(record)

            # Permite que o Middleware realize tratativas no registro criado.
            self.parameters.post_standardize_record(record)

            # Mapeia as referências nos controles internos.
            self.map_references(record)

        return None


    def save(self):
        """
        Updates the <TreeData.Structure> while iterating over it's records.
        
        RETURNS: <Boolean> Flag to inform the result of the saving.
        """
        
        # Limpa o vetor de códigos atual.
        del self.link.handler[:]

        # Atualiza o vetor de códigos com os dados salvos nos registros.
        for record in self.records:
            
            self.link.handler.append(record.vector)

        return None


class StructureJSON(Structure):
    """
    Provides an interface for building and managing the <TreeData.*> object models.
    Used exclusively for structured JSON data.
    
    SUPER 1: Class responsible for managing the <TreeData.Structure> object life-cycle.
    """

    def __init__(self, *args, **kwargs):
        """
        Creates variables used by the internal functions.
        Starts the processes responsible for configuring the application.

        RETURNS: None.
        """
        
        # Invoca o inicializador da classe principal.
        Structure.__init__(self, *args, **kwargs)

        return None


    def initialize(self):
        """
        Starts the required processes of the life-cycle boot.
        
        1. Builds the structure of <TreeData.Records> and <TreeData.Fields> objects.
        2. Standardizes the created objects according to the <TreeData.parameters>.

        RETURNS: None.
        """

        # TAGGED-IMPROVE
        # Contagem de registros.
        record_index = 0

        # Para cada chave do dicionário.
        for record_name, record_dictionary in self.link.handler.items():

            # Delega a criação do registro.
            record = RecordJSON(record_dictionary, {}, self.parameters, None)

            # Nome do registro.
            record.name = str(record_name)

            # TAGGED-IMPROVE.
            record.index = record_index

            record_index = record_index + 1

            # Regras de configuração específicas do registro.
            record_settings = self.rules.get("record")

            # TAGGED-IMPROVE
            # Contagem de campos.
            field_index = 0

            if not isinstance(record_dictionary, dict):
                
                value = record_dictionary

                record_dictionary = {
                    "value": value
                }

            # Para cada coluna da linha.
            for field_name, field_value in record_dictionary.items():

                FieldClass = Field

                if type(field_value).__name__.upper() == "DICT":

                    FieldClass = FieldJSON

                # Delega a criação do campo.
                field = FieldClass(record, field_value, {}, self.parameters, None)
                
                # Nome do campo é a própria chave.
                field.name = field_name

                # Tipo de dado.
                field.type = type(field_value).__name__.upper()

                # Classe do dado.
                field.clss = RecordJSON.DATA_TYPE

                # TAGGED-IMPROVE.
                field.index = field_index

                field_index = field_index + 1

                # Permite que o Middleware realize tratativas e consultas no campo criado.
                field = self.parameters.standardize_field(field)

                # Adiciona o campo criado ao controle.
                record.fields[field.name] = field

                # Adiciona referência as variáveis auxiliares.
                record.fields_names[field.name] = field

                # Adiciona mapemamento da chave estrangeira.
                if field.foreign_key:
                    
                    record.fields_foreign_keys[field.foreign_key] = field

            # TAGGED-IMPROVE - Mover essa função para antes do preenchimento.
            # Obs.: É necessário verificar o que foi feito nos parâmetros de configuração.
            # Permite que o Middleware realize tratativas no registro antes do preenchimento.
            record = self.parameters.pre_standardize_record(record)

            # Permite que o Middleware realize tratativas no registro criado.
            self.parameters.post_standardize_record(record)

            # Mapeia as referências nos controles internos.
            self.map_references(record)

        return None


    def save(self):
        """
        Updates the <TreeData.Structure> while iterating over it's records.
        
        RETURNS: <Boolean> Flag to inform the result of the saving.
        """
        
        # Novo modificador de dados do link.
        self.link.handler = {}

        # Nível de indentação.
        indent = self.rules.get('link').get('settings').get('file').get('indent', 4)
        
        # Para cada registro.
        for record in self.records:

            # Associa o dicionário atualizado ao novo modificador.
            self.link.handler[record.name] = record.dictionary

        # Atualiza o string representativo do link.
        self.link.content = json.dumps(self.link.handler, indent=indent)

        return None


class StructureLayout(Structure):
    """
    Provides an interface for building and managing the <TreeData.*> object models.
    Used exclusively for structured LAYOUT data.
    
    SUPER 1: Class responsible for managing the <TreeData.Structure> object life-cycle.
    """

    def __init__(self, *args, **kwargs):
        """
        Creates variables used by the internal functions.
        Starts the processes responsible for configuring the application.

        RETURNS: None.
        """
        
        # Invoca o inicializador da classe principal.
        Structure.__init__(self, *args, **kwargs)

        # Regras de configuração da fonte de dados.
        link_settings = self.rules.get('link').get('settings')

        # Regras de configuração do layout.
        layout_settings = link_settings.get('layout')

        # Regras de configuração do registro.        
        record_settings = link_settings.get('record')
        
        # Nome do arquivo de layout associado.
        self.layout_name = layout_settings.get('file')

        # Layout apropriado.
        self.layout = self.middleware.layout(self.layout_name, self.parameters)

        # Palavra-Chave do registro no layout.
        self.layout_keyword = record_settings.get('ID-prefix')
        
        # Tamanho de corte do identificador do registro.
        self.record_ID_size = record_settings.get('ID-bytes', None)

        # Corte adicional no offset do registro.
        self.record_extra_offset = record_settings.get('extra-offset', 0)
        
        # Indica os bytes iniciais a serem ignorados.
        self.skip_first_bytes = record_settings.get('skip-first-bytes', 0)

        return None


    @Structure._save
    def save(self):
        """
        Updates the <TreeData.Structure> while iterating over it's records.
        
        RETURNS: <Boolean> Flag to inform the result of the saving.
        """
        
        # Limpa o vetor de códigos atual.
        del self.link.handler[:]

        # Atualiza o vetor de códigos com os dados salvos nos registros.
        for record in self.records:
            
            self.link.handler.extend(record.vector)

        return True

        
    def initialize(self):
        """
        Starts the required processes of the life-cycle boot.
        
        1. Builds the structure of <TreeData> Records and Fields objects.
        2. Standardizes the objects according to the <TreeData.parameters>.

        RETURNS: None.
        """
        
        # Vetor de códigos extraídos do arquivo.
        looping_vector = self.link.handler

        # Tamanho total do vetor de códigos extraído.
        vector_length = len(self.link.handler)

        # Função recursiva criadora de registros.
        def build(record_keyword, looping_vector, runtime_settings=None):
            
            # Layout específico do registro.
            record_layout = self.layout.records[record_keyword]

            # Indica até onde deve ser cortado o vetor de códigos.
            record_offset = record_layout['offset']
            
            # Offset total do vetor de códigos.
            offset = record_offset + self.record_extra_offset

            # Extração do vetor de códigos do registro catalogado.
            record_vector = looping_vector[0: offset]

            # FEATURE-IMPROVE (Testes de uma parada ai. Vou consertar logo mais).
            if runtime_settings:

                # O registro consome TODO o vetor de códigos para encerrar o looping nesta iteração.
                record_vector = looping_vector[:]

            # Delega a criação do registro.
            record = RecordLayout(record_vector, record_layout, self.parameters, runtime_settings)

            # Permite que o Middleware realize tratativas no registro antes do preenchimento.
            record = self.parameters.pre_standardize_record(record)
            
            # Vetor contendo o código dos campos a serem usados pelos campos.
            working_vector = looping_vector[self.skip_first_bytes:] 
            
            # Para cada campo catalogado no layout.
            for name in record.layout['fields']:

                # Layout do campo.
                field_layout = record.layout['fields'][name]

                # Indica até onde deve ser cortado o vetor de códigos.
                field_bytes = field_layout['bytes']

                # Vetor de códigos do campo catalogado.
                field_vector = working_vector[:field_bytes]

                # FEATURE-IMPROVE (Testes de uma parada ai. Vou consertar logo mais).
                if runtime_settings:

                    # O campo consome TODO o vetor de códigos do registro para encerrar o looping nesta iteração.
                    field_vector = working_vector[:]

                # Delega a criação do campo.
                field = FieldLayout(record, field_vector, field_layout, self.parameters, runtime_settings)

                # Nome associado no layout.
                field.name = field_layout['name']

                # Tipo de dado.
                field.type = field_layout['type']
        
                # Classe do dado.
                field.clss = RecordLayout.DATA_TYPE

                # FEATURE-IMPROVE (Template de formatação do dado).
                field.template = field_layout['template']
                
                # Permite que o Middleware realize tratativas no campo criado.
                field = self.parameters.standardize_field(field, settings={
                    'record': record
                })

                # Adiciona o campo criado ao controle.
                record.fields[name] = field

                # Adiciona referência as variáveis auxiliares.
                record.fields_names[field.name] = field

                # Chave estrangeira.
                if field.foreign_key:

                    # Adiciona ao controle
                    record.fields_foreign_keys[field.foreign_key] = field

                # Remove o código trabalhado do vetor para continuar a recursão.
                working_vector = working_vector[field_bytes:]

            # Informa o progresso da criação dos registros.
            self.callback_progress({
                "total": vector_length,
                "value": vector_length - len(looping_vector)
            })

            # Permite que o Middleware realize tratativas no registro criado.
            self.parameters.post_standardize_record(record)

            # Mapeia as referências nos controles internos.
            self.map_references(record)

            # Remove o código trabalhado do vetor para continuar a recursão.
            return looping_vector[offset:]

        # Para cada registro.
        while True:

            # O processo termina com sucesso ao limpar o vetor de códigos do lopping.
            if len(looping_vector) == 0:

                self.logger.debug("O vetor de códigos foi zerado por completo!")
                
                break

            # Identificador do registro nos códigos.
            record_ID = looping_vector[:self.record_ID_size]
            
            # Chave identificadora do registro.
            record_keyword = self.layout_keyword

            # Padroniza o identificador de acordo com os parâmetros.
            if self.record_ID_size:

                # Identificador padronizado.
                record_ID = self.parameters.standardize_recordID(record_ID)

                # Identificador completo do registro.
                record_keyword = self.layout_keyword + str(record_ID)

            # Aplicação das regras ao registro catalogado no layout.
            if record_keyword in self.layout.records:

                # Função recursiva.
                looping_vector = build(record_keyword, looping_vector)
                
            # FEATURE-IMPROVE (Caso o registro não esteja conforme o layout).
            else:

                # Em caso de erros controlados.
                if record_settings.get('on-error', False):

                    # FEATURE-IMPROVE (Configurações para criação de registro em tempo real).
                    runtime_settings = None

                    # Nome e tamanho do registro de erro.
                    record_keyword = record_settings.get('on-error').get('fulfill-record')
                    record_tobytes = record_settings.get('on-error').get('bytes', None)

                    # Caso o tamanho não seja específicado, consome todo o restante do vetor.
                    if not record_tobytes:

                        # Tamanho do vetor de códigos restantes.
                        record_tobytes = len(looping_vector)

                        # Configuração em tempo real.
                        runtime_settings = dict(fields={ 'dynamic-offeset': record_tobytes })

                    # Constrói o registro de erro.
                    looping_vector = build(record_keyword, looping_vector, runtime_settings)

                # Em caso de erros não controlados.
                else:

                    # Mensagem de suporte.
                    self.logger.critical("Não foi possível encontrar layout para o registro '%s'", record_keyword)

                    break

        return None

