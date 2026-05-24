###############################################################################
#                                                                             #
#   Tree Data Manager                                                         #
#   Versão 1.0.0.0 (Beta)                                                     #
#   Leonardo Amaral de Souza                                                  #
#   Rio de Janeiro, 12/09/1997                                                #
#                                                                             #
###############################################################################


# Bibliotecas padrões.
import uuid, logging


# Classe principal.
class Record:
    """
    Creates the representation of a logical record.
    """


    DATA_TYPE = "BASIC"
    

    def __init__(self, vector, layout, parameters, settings):
        """
        Creates variables used by the internal functions.
        Starts the processes responsible for configuring the application.

        PARAMETER 1: vector: Raw list of data to be converted into fields.
        PARAMETER 2: layout: Layout used to fabricate the record.
        PARAMETER 3: parameter: <TreeData.Parameters> object.
        PARAMETER 4: settings: Custom configuration.

        RETURNS: None.
        """
        
        # Sistema de logging configurado.
        self.logger = logging.getLogger("TreeData.Structure.Record")

        # Layout do registro.
        self.layout = layout

        # Nome padrão do registro (TESTE).
        self.name = self.layout.get("name")

        # Parametrizador administrável.
        self.parameters = parameters

        # Regras dos dados.
        self.rules = self.parameters.rules['link']['settings'].get("record")

        # Configurações do objeto.
        self.settings = settings

        # Condicionais.
        self.conditionals = {}

        # Variáveis internas de controle.
        self.vector = vector
        self.fields = {}

        # Chave e ID estrangeiro.
        self.foreign_key = None
        self.foreign_id = None

        # Rótulos dinâmicos.
        self.labels = []

        # Variáveis auxiliares.
        self.fields_names = {}
        self.fields_foreign_keys = {}

        # Gera um ID único de controle para o registro.
        self.id = uuid.uuid4()

        # Inicializa a criação do registro.
        self.initialize()

        return None


    def update(self, settings={}):
        """
        Custom method to updates the record's structure of fields.

        PARAMETER 1: settings: Custom configurations.
        
        RETURNS: None.
        """
        
        self._update(settings)

        return None


    def _update(self, settings={}):
        """
        Main hidden method to updates the record's structure of fields.

        PARAMETER 1: settings: Custom configurations.
        
        RETURNS: None.
        """
        
        return None

        
    def initialize(self):
        """
        Initiates the configuration of the record.
        
        RETURNS: None
        """
        
        return None


    # TAGGED: Aprimorar o código e descrição.
    def get(self, name, value=True, default=None, bydescription=False, byforeign_key=False, byforeign_id=False):
        """
        Returns the record's field by value reference.

        PARAMETER 1: name:
        PARAMETER 2: value:
        PARAMETER 3: default:
        PARAMETER 2: bydescription:
        PARAMETER 2: byforeign_key:
        PARAMETER 2: byforeign_id:
        
        RETURNS: Field's value.
        """
        
        # Onde procurar o valor.
        fields = self.fields

        # Caso nome seja a descrição, procurar neste objeto.
        if bydescription:
            
            fields = self.fields_names

        if byforeign_key:

            fields = self.fields_foreign_keys

        if byforeign_id:

            fields = self.fields_foreign_ids

        #print(name, fields)

        # CASO FIELD NÃO EXISTA, RETORNAR VALOR PADRÃO
        if name not in fields: return default

        field = fields[name]

        # CASO DESEJE RETORNAR APENAS VALOR DO FIELD
        if value == True: field = field.value

        return field


class RecordJSON(Record):
    """
    Creates the representation of a logical JSON record.
    """

    
    DATA_TYPE = "JSON"


    def __init__(self, *args, **kwargs):
        """
        Creates variables used by the internal functions.
        Starts the processes responsible for configuring the application.

        RETURNS: None.
        """
        
        # Invoca o inicializador da classe principal.
        Record.__init__(self, *args, **kwargs)

        # Modificador de dados do registro.
        self.dictionary = self.vector

        return None

    def dump(self, dictionary):

        print(self.dictionary)

        return None

        for key, value in dictionary.items():

            print(key)

            field = self.get(key, value=False, bydescription=True)

            print(field)

        return None

    def _update(self, settings={}):
        """
        Main hidden method to updates the record's structure of fields.

        PARAMETER 1: settings: Custom configurations.
        
        RETURNS: None.
        """
        
        # Campo modificado.
        field = settings.get('field')

        # TAGGED
        if isinstance(self.dictionary, dict):

            # Atualiza o modificador de dados.
            self.dictionary[field.name] = field.original

        else:

            self.dictionary = field.original

        return None

        
class RecordTable(Record):
    """
    Creates the representation of a logical table record.
    """

    
    DATA_TYPE = "TABLE"


    def __init__(self, *args, **kwargs):
        """
        Creates variables used by the internal functions.
        Starts the processes responsible for configuring the application.

        RETURNS: None.
        """
          
        # Invoca o inicializador da classe principal.
        Record.__init__(self, *args, **kwargs)

        # Modificador original da fonte de dados (atualizado em tempo de execução).
        self.configparser = None

        return None


    def _update(self, settings={}):
        """
        Main hidden method to updates the record's structure of fields.

        PARAMETER 1: settings: Custom configurations.
        
        RETURNS: None.
        """
        
        # Campo modificado.
        field = settings.get('field')

        self.vector[field.index] = field.value

        return None

    
class RecordConfigParser(Record):
    """
    Creates the representation of a logical ConfigParser record.
    """

    
    DATA_TYPE = "CONFIGPARSER"


    def __init__(self, *args, **kwargs):
        """
        Creates variables used by the internal functions.
        Starts the processes responsible for configuring the application.

        RETURNS: None.
        """
        
        # Invoca o inicializador da classe principal.
        Record.__init__(self, *args, **kwargs)

        # Modificador original da fonte de dados (atualizado em tempo de execução).
        self.configparser = None

        return None


    def _update(self, settings={}):
        """
        Main hidden method to updates the record's structure of fields.

        PARAMETER 1: settings: Custom configurations.
        
        RETURNS: None.
        """
        
        # Campo modificado.
        field = settings.get('field')

        # Altera o valor no ConfigParser interno.
        self.configparser.set(self.name, field.name, field.value)

        return None


class RecordLayout(Record):
    """
    Creates the representation of a logical layout record.
    """

    
    DATA_TYPE = "LAYOUT"


    def __init__(self, *args, **kwargs):
        """
        Creates variables used by the internal functions.
        Starts the processes responsible for configuring the application.

        RETURNS: None.
        """
        
        # Invoca o inicializador da classe principal.
        Record.__init__(self, *args, **kwargs)

        return None


    def _update(self, settings={}):
        """
        Main hidden method to updates the record's structure of fields.

        1. Checkes for initial bytes to be skipped from the trim.
        2. Updates the record's structure while iterating over it's fields.

        PARAMETER 1: settings: Custom configurations.
        
        RETURNS: None.
        """
        
        # Novo vetor de códigos atualizados a ser configurado.
        new_vector = []

        # Indica os bytes iniciais a serem ignorados.
        skip_first_bytes = self.rules.get('skip-first-bytes', 0)
        
        # Vetor contendo o código de identificação do campo caso apartado na inicialização.
        record_id_vector = self.vector[:skip_first_bytes]

        # Adiciona o código de identificação primeiro.
        new_vector.extend(record_id_vector)

        # Verifica o vetor de cada campo.
        for field_name, field in self.fields.items():

            # Insere o código do campo no novo vetor para o registro.
            new_vector.extend(field.vector)

        # Atualiza o vetor original do registro.
        self.vector = new_vector
    
        return None
