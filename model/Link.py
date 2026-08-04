###############################################################################
#                                                                             #
#   Tree Data Manager                                                         #
#   Versão 1.0.0.0 (Beta)                                                     #
#   Leonardo Amaral de Souza                                                  #
#   Rio de Janeiro, 12/09/1997                                                #
#                                                                             #
###############################################################################


# Bibliotecas padrões.
import io
import re
import csv
import json
import pyodbc
import os.path
import logging
import binascii
import configparser


# Classe principal.
class File:
    """
    Creates the representation of a logical link to FILE connection.
    """

    def __init__(self, path=None, parameters=None, settings=None):
        """
        Creates variables used by the internal functions.
        Starts the processes responsible for configuring the application.

        1. Initiates the logging system.
        2. Validates file's existence.
        3. Opens file.
        4. Initiates the conversion process.

        PARAMETER 1: path: Complete file path.
        PARAMETER 2: parameter: <TreeData.Parameters> object.
        PARAMETER 3: settings: Main configurations.

        RETURNS: None.
        """

        # Sistema de logging configurado.
        self.logger = logging.getLogger("TreeData.File")

        # O status do objeto indica se ele está apto para uso.
        self.status = True

        # Referência às configurações da aplicação.
        self.settings = settings.get("file")

        # Nome e caminho completo do arquivo.
        self.path = path
        self.name = os.path.basename(path)
        
        # Arquivo carregado e base de conversão.
        self.file = None
        self.base = None

        # Modos de abertura e salvamento do arquivo.
        self.opening_mode = self.settings.get("default").get("mode")
        self.writing_mode = self.settings.get("default").get("saving-mode")

        # Configurações pertinentes ao metódo de carregamento.
        self.type = self.settings.get("default").get("name")

        # Conteúdo carregado do arquivo e modificador apropriado.
        self.content = None
        self.handler = None
        
        # Parametrizador do arquivo.
        self.parameters = parameters

        # Função conversora dos dados.
        self.converter = None

        # Caso o arquivo informado não exista, interromper o processo.
        if not os.path.exists(path):

            # Atualiza o status.
            self.status = False

            # Mensagem para o suporte.
            self.logger.error("Não foi possível encontrar o arquivo informado! \n'%s'", path)

            return None

        # Carrega o arquivo informado.
        self.open(self.path)

        # TAGGED-TEST.
        # Solicitação de conversão.
        conversion = self.parameters.rules['link']['settings'].get("file", {}).get("opening-conversion", None)
        
        # Converte os dados carregados caso necessário.
        self.convert(conversion)

        return None


    def save(self, settings={}):
        """
        Saves the <TreeData.Link> object's content to file.
        
        PARAMETER: settings: Custom configurations.
        
        RETURNS: <Boolean> Flag to inform the result of the process.
        """

        # Resultado do processo de salvamento dos dados.
        result = None

        # Tenta escrever os dados para o arquivo original.
        try:

            # Caminho completo para salvamento do arquivo.
            file_path = settings.get('path', self.path)

            # Conversor configurado para salvamento dos dados.
            converter = self.parameters.rules['link']['settings'].get('file', {}).get('closing-conversion', None)

            # Dados convertidos.
            converted_data = self.convert(converter, { 'dont_apply': True })

            if isinstance(self, FileTable):
                
                result = self._save(file_path, converted_data)

                return result
            
            # Abertura do arquivo.
            with open(file_path, self.writing_mode) as file:

                # Metódo de salvamento para arquivos de ConfigParser.
                if isinstance(self.handler, configparser.ConfigParser):

                    # Escreve para o arquivo usando metódo específico.
                    self.handler.write(file)
                    
                else:

                    # Escreve para o arquivo.
                    file.write(converted_data)

            # Resultado positivo no salvamento dos dados.
            result = True

        except:

            # Resultado negativo no salvamento dos dados.
            result = False

            # Mensagem para o suporte.
            self.logger.error("Não foi possível salvar dados para o arquivo! \n'%s'", file_path)

        return result
        

    # Carrega os dados do arquivo informado.
    def open(self, path):
        """
        Populates internal data while opening file's content.

        PARAMETER: path: Complete file path.

        1. Opens file while validating it's existence.
        2. Restarts the current data life-cycle.
        3. Sets the approprieate handler.

        RETURNS: None.
        """

        # Caso o arquivo informado não exista, interrompe o processo.
        if not os.path.exists(path):

            # Atualiza o status.
            self.status = False

            # Mensagem para o suporte.
            self.logger.error("Não foi possível encontrar o arquivo informado! \n'%s'", path)

            return None
        
        # Detecção de arquivo por extensão.
        for regex, base in self.settings.items():

            # Expressão regular da extensão.
            regex = re.compile(regex, re.IGNORECASE)

            if re.match(regex, self.name):

                # Tipo de arquivo (Decimal, binário, etc.).
                self.type = base.get("type")

                # Modos de abertura e salvamento do arquivo.
                self.opening_mode = base.get("mode")
                self.writing_mode = base.get("saving-mode")

                break

        # Limpa o vetor de códigos trabalhados e dados carregados.
        self.clear()
            
        # Tenta abrir o arquivo para leitura.
        try:
            
            # Abre o arquivo informado.
            with open(self.path, mode=self.opening_mode) as file:

                # Referência ao arquivo original.
                self.file = file

                # Carrega o conteúdo do arquivo.
                self.content = file.read()
                
            # Aponta o manipulador de dados para o próprio conteúdo carregado.
            self.handler = self.content

            # Atualiza o caminho do arquivo.
            self.path = path

            # Atualiza o nome do arquivo.
            self.name = os.path.basename(path)

        except:
            
            # Atualiza o status.
            self.status = False

            # Mensagem para o suporte.
            self.logger.error("Não foi possível abrir o arquivo informado para leitura! \n'%s'", self.path)

        return None

        
    # Converte os dados carregados para a base solicitada.
    def convert(self, converter, settings={}):
        """
        Converts the loaded data with it's appropriate converter function.

        PARAMETER 1: converter: Converter function.
        PARAMETER 2: settings: Custom configuration.

        1. Opens file while validating it's existence.
        2. Sets the internal status of the link.
        3. Sets the approprieate handler.

        RETURNS: None.
        """
                
        # Caso a base a seja atual ou nulo, retornar o conteudo inalterado.
        if converter in (self.converter, None):
            
            return self.content

        # Tenta converter os dados carregados para a base solicitada.
        try:

            # Encontra o nome da função conversora.
            regex = r'(\w+)\(.*\)'
            match = re.match(regex, converter)

            # A base do arquivo é nome da própria função.
            new_base = match.group(1)

            # Retorna a função da classe conversora.
            function = getattr(Converter, new_base)

            # Nos argumentos para o eval, temos os dados do arquivo por padrão.
            arguments = dict(code=self.handler, data=self.content, file=self.file)

            # O nome da função conversora catalogada.
            arguments[new_base] = function

            # Interpreta o código externo com segurança.
            new_data = eval(converter, arguments)

            if settings.get('dont_apply', False):
                
                return new_data

            # Atualiza o conteúdo carregado e modificador padrão.
            self.content = new_data
            self.handler = new_data

            # Atualiza o nome da base pós conversão.
            self.base = new_base

            # Salva o texto do código conversor.
            self.converter = converter
            

        # Erro ao converter os dados para a base.
        except:
            
            # Atualiza o status.
            self.status = False

            # Mensagem para o suporte.
            self.logger.error("Não foi possível converter os dados do arquivo informado para a base! \n'%s'", base)

        return None


    # TAGGED: Trabalhar no código.
    def clear(self, keep_data=False):
        """
        Clears the loaded content and resets it's control variables.

        PARAMETER keep_data: If true, keeps the content loaded.

        RETURNS: None.
        """
        
        # TAGGED-IMPROVE: 
        # Vetor de códigos trabalhado.
        #self.handler = None

        # Remove os dados brutos do arquivo.
        if not keep_data:
            
            self.content = None

        return None


class FileTable(File):
    """
    Creates the representation of a logical link to FILE.TABLE connection.
    """
    
    def __init__(self, *args, **kwargs):
        """
        Creates variables used by the internal functions.
        Starts the processes responsible for configuring the application.

        RETURNS: None.
        """
        # Invoca o inicializador da classe principal.
        File.__init__(self, *args, **kwargs)

        # Inicialização específica da classe.
        self.initialize()

        return None


    def initialize(self):
        """
        Initiates the configuration of the table link.
        
        RETURNS: None
        """

        # Colunas.
        self.columns = []

        # O nome das colunas é a primeira linha do conteúdo.
        if len(self.content):
            
            self.columns = self.content.pop(0)

        return None


    # TAGGED: Trabalhar no código.
    def _save(self, file_path, converted_data):
        """
        Saves the <TreeData.Link> object's content to file.
        
        PARAMETER 1: file_path: Caminho completo do arquivo a ser salvo.
        PARAMETER 2: converted_data: ?
        
        RETURNS: <Boolean> Flag to inform the result of the process.
        """
        
        # Abertura do arquivo.
        with open(file_path, self.writing_mode, newline='') as file:

            # Objeto modificador do arquivo.
            writer = csv.writer(file, delimiter=',')

            # Escreve colunas.
            writer.writerows([self.columns])

            # Escreve dados.
            writer.writerows(self.handler)

        return True

    
class SQLDatabase:
    """
    Creates the representation of a logical link to database connection.
    """
    
    #'''
    #Classe responsável pelos seguintes procedimentos:
    #PROC-1: Validar a existência da fonte da dados informada.
    #PROC-2: Carregar o conteúdo de dados
    #PROC-3: Salvar as variáveis de propriedades do link e operações realizadas.
    #PROC-4: Converter os dados da base original para a base de destino informada.
    #PROC-5: Proporcionar metódos para a manipulação da fonte de dados original.
    #'''

    def __init__(self, server=None, parameters=None, settings=None):
        """
        Creates variables used by the internal functions.
        Starts the processes responsible for configuring the application.

        RETURNS: None.
        """
        
        # Sistema de logging configurado.
        self.logger = logging.getLogger("TreeData.SQLDatabase")

        # O status do objeto indica se ele está apto para uso.
        self.status = True

        # Dados.
        self.vector = self.handler = []

        # Configurações da conexão do banco de dados.
        self.driver    = None
        self.server    = server
        self.user      = None
        self.password  = None
        self.database  = None

        # Parametrizador do arquivo.
        self.parameters = parameters

        # Credenciais.
        self.credentials = self.parameters.rules.get('sql')

        # Tabela ativa e colunas.
        self.table   = None
        self.columns = None

        # Nome das tabelas do banco de dados.
        self.table_names = []

        # Conexão com o servidor de banco de dados.
        self.connect(self.server, self.credentials)

        # Atualiza as tabelas.
        self.tables(online=True)
        
        # Caso a conexão informada não exista, interromper o processo.
        if not self.connection:

            # Atualiza o status.
            self.status = False

            # Mensagem para o suporte.
            self.logger.info("Não foi possível realizar conexão com o banco de dados '{database}'".format(database=database))

            return None


    @staticmethod
    def _connect(server, credentials=None, parameters=None):
        """
        Main function responsible for stablishing database connections.

        PARAMETER 1: credentials: Credentials used to auth the connection.
        PARAMETER 2: parameter: <TreeData.Parameters> object.
        
        RETURNS 1: <PYODBC> connection.
        RETURNS 2: None if error while connecting.
        """
        
        if not credentials:

            # Credencial pré configurada.
            credentials = parameters.rules.get('sql')

        # Credencial padrão.
        default_credentials = {
            'driver':       '{SQL SERVER}',
            'server':       '',
            'database':     '',
            'username':     '',
            'password':     '',
            'trusted-connection': 'no'
        }

        # Padronização das credenciais informadas.
        for key in ['trusted-connection']:

            if credentials.get(key, False):

                credentials[key] = 'yes'
            else:

                credentials[key] = 'no'

        # Configuração das credenciais.
        default_credentials.update(credentials)

        # O servidor deve ser persistente.
        default_credentials['server'] = server
        
        # Realiza a conexão com o do banco de dados.
        query = "DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password};Trusted_Connection={trusted-connection};"

        # Formatação da query.
        query = query.format(**default_credentials)

        # Tentativa de conexão.
        try:    connection = pyodbc.connect(query)
        except: connection = None

        return connection



    def connect(self, server, credentials=None, test=False):
        """
        Populates internal data while connecting the link to database source.

        PARAMETER 1: server: Name of the database server.
        PARAMETER 1: credentials: Credentials used to auth the connection.
        PARAMETER 2: test: If true, does not restart internal data life-cycle.
        
        RETURNS 1: <PYODBC> connection.
        RETURNS 2: None if error while connecting.
        """
        
        # Conexão com o banco de dados.
        connection = SQLDatabase._connect(server, credentials, parameters=self.parameters)

        if not test:

            self.connection = connection
            self.clear()
            self.tables(online=True)
        
        return connection

    def disconnect(self):
        """
        Disconnects the link from the database source.

        1. Disconnects the database.
        2. Restarts the current data life-cycle.
        
        RETURNS: None.
        """
        
        #
        try:

            # Conectar.
            cursor = self.connection.cursor()

            # Tabela atual.
            self.table = None

            # Esvazia os dados internos.
            self.clear()

            # Desconectar.
            cursor.close()
            self.connection.close()

        except:
            
            # Atualiza o status.
            self.status = False

        return None
        
        
    def tables(self, online=True):

        if online:

            cursor = self.connection.cursor()

            tables = cursor.tables(tableType='TABLE')

            tables = [ table[2] for table in list(tables) ]

            self.table_names = tables


        tables = self.table_names

        return tables


    # Carrega os dados do arquivo informado.
    def select(self, table, limit=None):

        # Limpa o vetor de códigos trabalhados e dados carregados.
        self.clear()
        
        # Tenta abrir o arquivo para leitura.
        try:

            query = 'SELECT * FROM {table}'
            query = query.format(table=table)
            
            cursor = self.connection.cursor()
            cursor.execute(query)

            # Atualiza as variáveis de controle.
            self.table = table

            # Esvazia os dados da tabela.
            self.clear()

            # Atualiza os dados da tabela.
            self.vector.extend( list(cursor) )

            # Atualiza os dados das colunas da tabela.
            self.columns.extend( map(lambda x: x[0], cursor.description) )

        except:
            
            # Atualiza o status.
            self.status = False

            # Mensagem para o suporte.
            self.logger.error("Não foi possível carregar os dados da tabela! \n'%s'", table)
        
        
    # Limpa todos os dados internos carregados.
    def clear(self, keep_data=False):

        # Vetor de códigos trabalhado.
        self.vector  = self.handler = []
        self.columns = []




class Converter:
    '''
    Classe responsável pelos seguintes procedimentos:
    PROC-1: Validar a existência do arquivo informado.
    PROC-2: Carregar o conteúdo e converter os dados da base original para hexadecimal.
    PROC-3: Proporcionar metódos para a manipulação do arquivo original.
    PROC-4: Proporcionar metódos para a manipulação dos dados carregados.
    '''

    @staticmethod
    def replace(data, *args, **kwargs):
        
        code = data.replace(*args, **kwargs)

        return code

    @staticmethod
    def csv(data, *args, **kwargs):

        # Permite ler string como se fosse um arquivo.
        data = io.StringIO(data)

        # Leitor CSV dos dados.
        csv_reader = csv.reader(data, delimiter=',')

        # Cria lista de dados usada no sistema.
        csv_result = list(csv_reader)

        return csv_result


    @staticmethod
    def json(data, *args, **kwargs):

        # Converte string para JSON.
        json_data = json.loads(data)

        return json_data


    @staticmethod
    def csv_to_string(data, *args, **kwargs):

        pass


    @staticmethod
    def configparser(data, *args, **kwargs):

        configner = configparser.ConfigParser(interpolation=None, allow_no_value=True)
        configner.optionxform = str

        configner.read_string(data)

        return configner

    @staticmethod
    def binascii(code):

        code = "".join(code)
        code = binascii.unhexlify(code)

        return code


    @staticmethod
    def hexadecimal(data):

        code = []

        # Converte cada char de dado para hexadecimal
        for char in data:

            char = hex(char)[2:].upper()

            if len(char) < 2:
                char = "0" + char

            # Salva os dados convertidos para o vetor de códigos trabalhados.
            code.append(char)

        # Retorna o código convertido e base.
        return code
        
