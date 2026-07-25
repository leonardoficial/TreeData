###############################################################################
#                                                                             #
#   Tree Data Manager                                                         #
#   Versão 1.0.0.0 (Beta)                                                     #
#   Leonardo Amaral de Souza                                                  #
#   Rio de Janeiro, 12/09/1997                                                #
#                                                                             #
###############################################################################

# TESTE DA NOVA IDE


# Bibliotecas padrões.
import ast
import uuid
import logging

# Bibliotecas próprias para serviços.
from treedata.model import Bases


# Classe principal.
class Field:
    """
    Creates the representation of a logical field.
    """

    
    def __init__(self, record, value, layout, parameters, settings=None):
        """
        Creates variables used by the internal functions.
        Starts the processes responsible for configuring the application.

        PARAMETER 1: record: Related <TreeData.Record> object.
        PARAMETER 2: value: Value.
        PARAMETER 3: layout: Layout used to fabricate the field.
        PARAMETER 4: parameter: <TreeData.Parameters> object.
        PARAMETER 5: settings: Custom configuration.

        RETURNS: None.
        """
        
        # Sistema de logging configurado.
        self.logger = logging.getLogger("TreeData.Structure.Record.Field")

        # Layout do campo.
        self.layout = layout

        # Parametrizador administrável.
        self.parameters = parameters

        # Regras gerais do parametrizador.
        self.rules = self.parameters.rules

        # Regras específicas deste campo.
        self.this_rules = {}

        # Configurações.
        self.settings = {} if settings is None else settings

        # Condicionais.
        self.conditionals = {}

        # Referência ao registro criador do campo.
        self.record = record

        # Variáveis internas de controle.
        self.value = value
        self.vector = value
        self.original = value

        # Nome, tipo e classe do campo.
        self.name = None
        self.type = None
        self.clss = None

        # Função conversora padrão.
        self.converter = ast.literal_eval

        # Nome da chave estrangeira do campo.
        self.foreign_key = None

        # Valor representativo.
        self.dictionary_value = None

        # Gera um ID único de controle para o campo.
        self.id = uuid.uuid4()

        # Inicializa a criação do campo.
        self.initialize()

        return None


    def initialize(self):
        """
        Initiates the configuration of the field.
        
        RETURNS: Value of the field.
        """
        
        # Base padrão do campo.
        self.base = "original"
        
        # O valor do campo deve ser do tipo string por padrão.
        self.value = str( self.value )

        return self.value


    def convert(self, base=None):
        """
        Initiates the process responsible for converting the field's value.
        * This method should be overriden for better implementation.
        
        RETURNS: None.
        """
        
        # TAGGED-IMPROVE
        # Identifica a função conversora responsável.
        if self.type == 'STR': self.converter = str

        #print(self.value)

        #self.original = self.value 

        # Função conversora responsável.
        #self.original = self.converter(self.value)

        return None


    # TAGGED: Melhorar o inglês da descrição.
    def validate(self, value):
        """
        Validates the value with specific metrics.
        * This method should be overriden for better implementation.

        PARAMETER: value: Value to be validated.
        
        RETURNS: <Boolean> flag to indicate the field's value confiability.
        """
        
        return True


    # TAGGED: Improve english of the description.
    def get(self, raw=False, details=False):
        """
        Returns the field's value with details if wanted.

        PARAMETER 1: raw: if true, returns the "raw value" of the field. *
        PARAMETER 2: details: If true, returns <Dict> object with details
        which may include the following keys: value and class.

        * raw value = Value neither converted nor modified of the field.
        
        RETURNS: Field's value.
        """
        
        value = self.value

        if raw:

            value = self.raw()

        if details:

            value = {
                'value': value,
                'class': "default"
            }

            if self.dictionary_value:

                value['value'] = self.dictionary_value
                value['class'] = "dictionary"
            

        return value

    # TAGGED: Improve english of the description.
    def raw(self):
        """
        Returns the field's value neither converted nor modified.
        
        RETURNS: Field's value.
        """
        
        return self.value


    def _set(self, new_value, settings=None):
        """
        Main hidden method to set the field's value.

        PARAMETER 1: new_value: New value.
        PARAMETER 2: settings: Custom configurations which may include:
        buffer = If true, changes the value without affecting <TreeData.Structure>
        
        RETURNS: <Boolean> flag to indicate the result of the process.
        """

        settings = {} if settings is None else settings
        
        self.value = new_value

        return True


    def set(self, new_value, settings=None):
        """
        Custom method to set the field's value.

        1. Sets the field's value.
        2. Standardizes the value according to the <TreeData.parameters>.

        PARAMETER 1: new_value: New value.
        PARAMETER 2: settings: Custom configurations which may include:
        buffer = If true, changes the value without affecting <TreeData.Structure>
        
        RETURNS: Field's value.
        """

        settings = {} if settings is None else settings
        
        # Invoca o método interno responsável pela configuração adequada.
        edition_result = self._set(new_value, settings)

        # TAGGED-IMPROVE:
        self.original = new_value

        # Permite que o Middleware realize tratativas no campo modificado.
        self.parameters.standardize_field(self)
        
        # Informa o registro criador sobre a mudança no campo.
        if not settings.get('buffer', False):
            
            self.record.update({ 'field': self, 'event': "change" })

        return edition_result


class FieldJSON(Field):
    """
    Creates the representation of a logical layout field.
    """
    
    def __init__(self, *args, **kwargs):
        """
        Creates variables used by the internal functions.
        Starts the processes responsible for configuring the application.

        RETURNS: None.
        """

        # Invoca o inicializador da classe principal.
        Field.__init__(self, *args, **kwargs)

        # Dicionário original.
        self.dictionary = self.original

        # Valor em texto.
        self.value = str(self.value)

        return None


    def convert(self, base=None):
        """
        Initiates the process responsible for converting the field's value.
        * This method should be overriden for better implementation.
        
        RETURNS: None.
        """
        
        # TAGGED-IMPROVE
        # Identifica a função conversora responsável.
        #self.converter = str

        #print(self.value)

        #self.original = self.value 

        # Função conversora responsável.
        #self.original = self.converter(self.value)

        return None


    def set(self, new_value, settings=None):
        """
        Custom method to set the field's value.

        1. Sets the field's value.
        2. Standardizes the value according to the <TreeData.parameters>.

        PARAMETER 1: new_value: New value.
        PARAMETER 2: settings: Custom configurations which may include:
        buffer = If true, changes the value without affecting <TreeData.Structure>
        
        RETURNS: Field's value.
        """

        # Configurações.
        settings = {} if settings is None else settings
        
        # Invoca o método interno responsável pela configuração adequada.
        edition_result = self._set(str(new_value), settings)
        
        # Permite que o Middleware realize tratativas no campo modificado.
        self.parameters.standardize_field(self)
        
        # Informa o registro criador sobre a mudança no campo.
        if not settings.get('buffer', False):
            
            self.record.update({ 'field': self, 'event': "change" })

        # Não atualizar o dicionário interno.
        if settings.get('update-dictionary', True):

            self.join(new_value, {'update-value': False})

        return edition_result
    
    
    # TAGGED: Não cria novas chaves! Apenas atualiza as existentes.
    def join(self, dictionary, settings=None):

        # Configurações.
        settings = {} if settings is None else settings

        for key, value in dictionary.items():

            if key in self.dictionary:

                #print(key, value, type(value))

                # Função conversora de valor.
                converter = type(self.dictionary[key])

                # TAGGED: avaliar o risco dessa operação.
                # Mantém o tipo de original.
                self.dictionary[key] = converter(eval(str(value)))

                
        if settings.get('update-value', False):

            # Atualização.
            self.set(self.dictionary, {'update-dictionary': False})

        #print(self.dictionary)

        return None


    def raw(self):
        """
        Returns the field's value neither converted nor modified.
        
        RETURNS: Field's value.
        """
        
        return self.dictionary


class FieldLayout(Field):
    """
    Creates the representation of a logical layout field.
    """
    
    def __init__(self, *args, **kwargs):
        """
        Creates variables used by the internal functions.
        Starts the processes responsible for configuring the application.

        RETURNS: None.
        """

        # Invoca o inicializador da classe principal.
        Field.__init__(self, *args, **kwargs)

        # Configura o novo valor.
        #self.value = "".join(self.vector)

        return None


    # TAGGED: Validar o inglês da descrição.
    def validate(self, value):
        """
        Validates the value with specific metrics.

        1. Value must by of type <List>.
        2. Value must have the size specified by the layout.

        PARAMETER: value: Value to be validated.
        
        RETURNS: <Boolean> flag to indicate the field's value confiability.
        """
        
        # Bytes requeridos para preenchimento do campo.
        layout_bytes = self.layout.get('bytes')

        # O valor novo informado deve ser somente do tipo lista.
        if not isinstance(value, list):
            
            return False

        # O novo valor informado deve ser do mesmo tamanho do requerido pelo layout.
        if len(value) != layout_bytes:

            # Mensagem para o suporte.
            self.logger.error("O novo valor para o campo '%s' deve ter o comprimento igual a %s.", self.name, layout_bytes)

            return False

        return True


    def convert(self, base=None):
        """
        Initiates the process responsible for converting the field's value.
        
        RETURNS: Field's value.
        """
        
        # É necessário informar a base de conversão.
        if not base or self.settings:
            
            return None

        # Tenta realizar a conversão de valor do campo.
        try:
            self.value = Bases.convert_base(base, self.vector, parameters=self.parameters.rules, type1=self.type, reverse=False)

            # Tratamento para campos do tipo ENUM.
            if self.type.upper() == "ENUM":

                # Vetor com as opções de valores.
                values = self.template.split(" ")

                # Seta o valor de acordo com o indicado.
                self.dictionary_value = values[self.value]
                
        except:
            
            self.logger.error("Não foi possível converter o campo '%s' para %s", self.name, self.base)

        # O valor do campo deve ser do tipo string por padrão.
        self.value = str( self.value )
        
        return self.value


    def raw(self):
        """
        Returns the field's value in original vector format.
        
        RETURNS: Field's value.
        """
        
        # Deve retornar o valor original no link de dados.
        return self.vector


    # TAGGED: Melhorar o inglês.
    def _set(self, new_vector, settings={}):
        """
        Custom method to set the field's value.

        1. Checkes the provided new value for consistency.
        2. Validates the value.
        3. Sets the new value.

        PARAMETER 1: new_vector: New value in vector.
        PARAMETER 2: settings: Custom configurations which may include:
        +buffer = If true, changes the value without affecting <TreeData.Structure>
        
        RETURNS: <Boolean> flag to indicate the result of the process.
        """
        
        # Caso argumento fornecido para valor seja do tipo texto.
        if type(new_vector) is str:

            # Remove espaços em branco.
            new_vector = new_vector.replace(" ", "")

            # Tamanho de saltos no corte.
            length = 2

            # Vetor de códigos criado.
            new_vector = list(new_vector[0+i:length+i] for i in range(0, len(new_vector), length))
        
        # Valida se o valor está apto para ser usado para o campo.
        validation = self.validate(new_vector)

        if not validation:

            return False

        # Configura o novo valor.
        self.value = "".join(new_vector)

        # Configura o novo vetor.
        self.vector = new_vector

        # Mensagem para o suporte.
        self.logger.info("O novo valor para o campo '%s' foi configurado com sucesso!", self.name)

        return True