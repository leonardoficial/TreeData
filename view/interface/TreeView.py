###############################################################################
#                                                                             #
#   Tree Data Manager                                                         #
#   Versão 1.0.0.0 (Beta)                                                     #
#   Leonardo Amaral de Souza                                                  #
#   Rio de Janeiro, 12/09/1997                                                #
#                                                                             #
###############################################################################


# Bibliotecas padrões.
import os, logging, time

# Bibliotecas próprias para serviços.
from issabox.services import StandardData

# Bibliotecas padrões para interfaces gráficas.
from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox

# Bibliotecas próprias para interfaces gráficas.
from issabox.graphics import (
    
    ProgressbarFactory,
    TreeviewBuilder,
    ConnectDatabase
    
)

from issabox.graphics.components import (

    EditValueBox, EditComboBox
)

from issabox.views.StructureView import JSONViewer

# Bibliotecas próprias para o projeto.
from treedata              import TreeData
from treedata.model        import File, FileTable, SQLDatabase
from treedata.model        import Bases
from treedata.controller   import Middleware

from treedata.view.components import (
    
    FilterBox,          GotoBox,            SearchBox,
    TaskSelectionBox,   TaskExecutionBox,
    SelectTable
)

from treedata.view.builtin.TreeManager import TreeManager


# Classe principal.
class TreeView(TreeManager, TreeviewBuilder):
    """
    Creates the representation of a tree view graphical interface.

    SUPER 1: Class responsible for managing the <TreeData> object life-cycle.
    SUPER 2: Class responsible for managing the GUI components of the tree view.
    """

    #'''
    #1. Visualizar a estrutura de dados do objeto.
    #2. Proporcionar metódos para a manipulação do link original.
    #3. Proporcionar metódos para a manipulação dos dados carregados.
    #4. Proporcionar metódos auxiliares para a renderização dos componentes.
    #'''
    
    def __init__(self, *args, **kwargs):
        """
        Creates variables used by the internal functions.
        Starts the processes responsible for configuring the application.

        RETURNS: None.
        """

        super(TreeView, self).__init__(*args, **kwargs)

        # Sistema de logging configurado.
        self.logger = logging.getLogger("TreeData.TreeView")

        # Intermediador entre lógica da aplicação e regras de negócios.
        self.middleware = Middleware(TreeData.settings)

        # Configuração da interface.
        self.settings = {}
        
        # Janela para a interface.
        self.initialize_window()

        # Árvore.
        self.Treeview = None

        # Barra de progresso.
        self.Progressbar = None

        # Rodapé.
        self.footer = Label(self.window)

        # Estilização da janela.
        self.style = ttk.Style()

        # Construtor de árvore da janela principal.
        self.TreeviewFactory = self.NewTreeview(self.window, self.style, {
            'full-version': True
        })

        return None


    def open(self, treedata=None):
        """
        Resets the current data and graphical interface life-cycle while
        initiating the rendering of the provided <TreeData> object.

        1. Binds the current GUI with the provided <TreeData> object.
        2. Initiates the rendering of the progress bar.
        3. Initiates the rendering of the menu.
        4. Initiates the rendering of the tree view.
        
        PARAMETER 1: treedata: <TreeData> object.
        
        RETURNS: None.
        """
    
        # Atualiza o objeto da interface.
        self.replace_treedata(treedata)

        # Menu principal.
        self.menu = WindowMenu(self, self.window)

        # Inicializa o controle de elementos.
        self.initialize_elements()

        # Barra de progresso.
        self.Progressbar = ProgressbarFactory(self.window,
            packing={
                'fill':   X,
                'anchor': S,
                'expand': True
            },
            settings={
                'orient': "horizontal",
                'mode':   "determinate"
            }
        )

        # Mensagem de suporte.
        self.logger.debug("A abertura da GUI foi solicitada!")

        # Inicializa a renderização da interface gráfica.
        self.render()

        return None


    def initialize_window(self):
        """
        Initializes the main Window object used in the graphical interface.

        1. Creates a brand new <Tk> window object.
        2. Configures it's title, size and appearence.
        
        RETURNS: None.
        """
        
        # Janela da aplicação.
        self.window = Tk()

        # Título.
        self.window.title("Gerenciador de Dados")

        # Tamanho.
        self.window.geometry("570x570")

        # Redimensionamento.
        self.window.resizable(False, False)
        
        # Ícone.
        icon_path = os.path.join( TreeData.settings.get("paths").get("icons"), "app-prod.ico")
        
        self.window.iconbitmap( icon_path )
    
        return None


    def initialize_elements(self):
        """
        Creates/resets the control variables of the elements.
        
        RETURNS: None.
        """

        # Referências aos elementos da interface.
        self.elements = dict(bases={}, entry={}, labels={}, buttons={})

        return None


    def render(self):
        """
        Initiates the main rendering process of the graphical interface.

        1. Updates the footer label.
        2. Initiates the rendering of the progress bar.
        3. Initiates the rendering of the tree view elements.
        4. Binds the keyboard to events.
        5. Initiates the processing of the startup tasks.
        
        RETURNS: None.
        """
        
        # Mensagem de suporte.
        self.logger.debug("Início da renderização!")

        # Valida se o objeto está apto para uso.
        if not self.treedata or not self.treedata.status:

            self.window.mainloop()

            return None

        # Renderização.
        self.footer.pack(anchor=W, side="bottom")

        # Atualiza o rodapé.
        self.footer.configure(text=r"Renderizando...")

        # Abre a barra de progresso.
        self.Progressbar.start()

        # Árvore.
        self.Treeview = self.TreeviewFactory.Treeview()

        # Quantidade total de registros a serem renderizados.
        records_length = len(self.treedata.structure.records)
        
        # Indica se o registro deve ser criado aberto.
        record_open = self.treedata.parameters.rules.get('view', {}).get('record', {}).get('start-opened', False)
        
        # 
        # Constrói a árvore de elementos (Registros).
        for record_index, record in enumerate(self.treedata.structure.records):

            # Representação do valor do registro.
            record_value = record.parameters.rules['link']['settings'].get('record', {}).get('representation', "")

            # Sem representação, aparece como vazio.
            if record_value == "":
                
                pass
            
            # Representação em códigos do vetor.
            elif record_value == "vector":

                # Junta vetor de códigos em um texto.
                record_value = " ".join( record.vector )

            # Representação com valor de campo específico.
            else:

                # Valor extraido do campo especificado.
                record_value = record.get(record_value, bydescription=True)

                # Caso campo não exista, aparece como vazio.
                if not record_value:

                    # Sem representação.
                    record_value = ""

            # Widget ID gerado na criação do registro.
            record_widget = self.TreeviewFactory.Record(record.name, settings={
                'ID':        record.id,
                'value':     record_value,
                'fonts':     record.conditionals.get('font', ''),
                'reference': record,
                'open':      record_open
            })

            # Informa o progresso da renderização dos registros.
            self.Progressbar.set({
                "total": records_length,
                "value": record_index
            })

            # Constrói a árvore de elementos (Campos).
            for field in record.fields:

                # Referência ao campo.
                field = record.get(field, value=False)

                # Valor original.
                field_original = field.original

                # Detalhes do valor do campo.
                field_details = field.get(details=True)

                # Representação.
                field_value = field_details['value']

                # Fontes externas.
                field_class = field_details['class']
                
                if field.type == "DICT":

                    field_class = "dictionary"
                    field_value = "{ ... }"
                
                # Widget ID gerado na criação campo.
                field_widget = self.TreeviewFactory.Field(field.name, {
                    'ID':        field.id,
                    'value':     field_value,
                    'fonts':     field_class, #field.conditionals.get('font', ''),
                    'class':     field_class,
                    'parent':    record_widget,
                    'reference': field
                })

   
        # Finaliza a barra de progresso.
        self.Progressbar.finish()
        
        # Nome do link de dados.
        link_name = self.treedata.link.name
        
        # Nome do parâmetro de configuração.
        parameter_name = self.treedata.parameters.name

        # Atualiza o texto do rodapé.
        self.footer.configure(text=r" {parameter}  \  {link}".format(parameter=parameter_name, link=link_name))

        # Renderização da árvore.
        self.TreeviewFactory.pack(fill=BOTH, side="top", expand=True)

        # Mensagem para suporte.
        self.logger.debug("Fim da renderização!")

        # Inicializa os processos internos.
        self.startup()

        # Aguarda a finalização da janela.
        self.window.mainloop()

        return None


    def close(self, kill=False):
        """
        Finishes the current data and graphical interface life-cycle.

        1. Deletes the associated <TreeData> object. *
        2. Resets the control variables of the elements.
        3. Destroyes the rendered elements.

        PARAMETER 1: kill: Flag to determine whether destroys <TreeData> object or not.

        RETURNS: None.
        """

        # Remove os dados do objeto atual.
        if self.treedata:

            # Atualiza os controladores internos
            self.initialize_elements()

            # Reseta as variáveis de rastreamento do objeto.
            self.reset_treedata_tracking()

            # Remove a referência do objeto.
            if kill:
            
                self.treedata = None

        # Remove a árvore gráfica atual caso renderizada.
        if self.Treeview:
            
            self.TreeviewFactory.destroy()

        # Remove a barra lateral caso renderizada.
        if self.Progressbar:

            self.Progressbar.finish()
            
        # Esconde o rodapé caso renderizado.
        if self.footer:

            self.footer.pack_forget()

        # Mensagem de suporte.
        self.logger.debug("O link renderizado foi fechado!")

        return None


    def restart(self):
        """
        Restarts the current data and graphical interface life-cycle.

        1. Resets the control variables of the elements.
        2. Resets the control variables of the TreeData object.
        3. Initiates the rendering of the tree view.

        RETURNS: None.
        """
        
        # Atualiza os controladores internos
        self.initialize_elements()
        
        # Reseta as variáveis de rastreamento do objeto.
        self.reset_treedata_tracking()

        # Renderiza os elementos da interface.
        self.render()

        # Mensagem de suporte.
        self.logger.debug("O restart da aplicação foi realizado!")

        return None


    # TAGGED: Melhorar o inglês desta descrição.
    def startup(self):
        """
        Starts the required processes of the life-cycle boot.
        
        1. Executes startup tasks specified by the parameters.

        RETURNS: None.
        """

        # Parâmetros de configuração.
        rules = self.treedata.parameters.rules

        # Tarefas executadas ao iniciar a aplicação.
        tasks = rules.get('task', {}).get('run-on', {}).get('startup', [])

        if len(tasks):

            # Caminho do diretório de tarefas.
            tasks_folder = self.treedata.settings.get('paths', {}).get('tasks')

            # Para cada tarefa.
            for task in tasks:

                # Caminho completo da tarefa.
                task_path = os.path.join(tasks_folder, rules.get('task').get('folder'), task.get('folder', ''), task.get('name', ''))

                # Dados para a nova janela.
                data = StandardData()

                # Executa a tarefa.
                self.do_execute_task(task_path, data)

        return None


    def do_goto(self, widget):
        """
        Scrolls the treeview to the specified widget's position.

        PARAMETER 1: widget: <Widget> object.

        RETURNS: None.
        """

        # Scroll para o topo.
        self.Treeview.yview_moveto(0)

        # Foco no elemento.
        self.Treeview.focus(widget.iid)

        # Seleção no elemento.
        self.Treeview.selection_set(widget.iid)

        # Scroll até o elemento.
        self.Treeview.yview_scroll(widget.index, "units")

        return None


    def do_remove(self, record):
        """
        Removes the <TreeData.Record> object from the current structure.
        This method is required by the TreeViewBuilder!
        
        PARAMETER 1: widget: <TreeData.Record> object.

        RETURNS: None.
        """

        # Deleta o registro da estrutura.
        self.treedata.structure.delete(record)

        return None


    # TAGGED: Melhorar o código.
    def do_edit_field(self, event=None, field_widget=None, clipboard=None):
        """
        Edits the <TreeData.Field> object's value.
        This method is required by the TreeViewBuilder!
        
        PARAMETER 1: event: <Event> object that called the function.
        PARAMETER 2: field_widget: <Widget> object of the field element.
        PARAMETER 3: clipboard: If true, gets field's value from the clipboard.

        RETURNS: None.
        """
        
        if field_widget:

            # Objeto do campo.
            field = field_widget.reference

            # Valor do campo.
            value = field.get(raw=True)

            # Área de transferência.
            if clipboard:

                # Valor padrão extraído da área de transferência.
                value = self.window.clipboard_get()

            # GUI de edição.
            EditFieldClass = EditValueBox

            # GUI personalizada para listas.
            #if field.type == 'LIST':

                #EditFieldClass = EditFieldList

            if field.clss == "LAYOUT":

                  value = "".join(field.vector)
            
            # Configuração da visualização.
            view_settings = self.treedata.parameters.rules.get('view', {})

            # Editor GUI do campo.
            field_editor = field.this_rules.get('editor', None)

            # Configurações do editor.
            editor_settings = {
                'value': value,
                'fonts': "dictionary",
                'values': ["TESTE", "BAR"],
                'disable-conversion': not view_settings.get('field', {}).get('enable-conversion', False),
                'function-convert': lambda value: self.do_convert_field(value, field)
            }

            if field.type == "DICT":

                viewer = JSONViewer(self.window)

                dict_settings = {}
                dict_settings[field.name] = field.original

                viewer.open(dict_settings)

                if not viewer.status:

                    return None

                #
                field.join(viewer.data[field.name], {'update-value': True})

                # TAGGED: A class IssaBox.Treeview deveria executar esse tramite.
                # Atualiza o valor do campo na árvore.
                field_widget.value = "{ ... }"

                return True

            # GUI personalizada para listas.
            if field_editor == "combobox":

                # Editor pertinente.
                EditFieldClass = EditComboBox

                # Opções de valores
                editor_settings['values'] = field.this_rules.get('values', [])

                editor_settings['disable-conversion'] = None
                        
            # Janela de edição.
            edition_result = EditFieldClass(self.window, editor_settings)

            # Renderização da janela.
            edition_result.open()

            # Cancelamento da edição.
            if edition_result.cancel:

                return None

            
            # Atualiza o valor do campo da aplicação.
            field_result = field.set(edition_result.value)
            
            # Falha na edição.
            if not field_result:

                return False

            # Atualiza o valor do campo na árvore.
            field_widget.value = edition_result.converted_value 
            
        return True


    def do_convert_field(self, value, field):
        """
        Initiates the process of value converting of the field.
        
        PARAMETER 1: value: Text to be converted.
        PARAMETER 2: field: <TreeData.Field> object of the element.

        RETURNS: Converted text value.
        """
        
        # Remove as quebras de linhas.
        value = value.rstrip()

        # Remove espaços em branco do texto.
        value = value.replace(" ", "").rstrip()

        # Vetor de códigos criado.
        vector = list(value)

        # Converte o vetor de códigos para amostra.
        converted_value = Bases.convert_base(field.base, vector, parameters=field.parameters.rules, type1=field.type, reverse=False)

        return converted_value
    

    #TAGGED: A função aceita qualquer texto como padrão, exceto "dictionary".
    def do_display(self, widget, value_class="default"):
        """
        Returns the specified object's value representation.
        
        PARAMETER 1: widget: <Widget> object of the field.
        PARAMETER 2: value_class: Type of wanted representation.
        which may include the following list of options:
        * default: Default value.
        * dictionary: Dictionary value.

        RETURNS 1: Required <TreeData.Field> object's value.
        RETURNS 2: None.
        """

        # Objeto do campo.
        field = widget.reference

        # Valor padrão.
        field_value = field.value

        # Caso valor de dicionário seja solicitado.
        if value_class == "dictionary":

            # Verificar se existe dicionário associado ao campo.
            if field.dictionary_value:

                # Caso exista, utilizar o seu valor mapeado.
                field_value = field.dictionary_value

            # Caso não exista, retornar nada.
            else:

                return None

        return field_value


    # TAGGED: Metódo legado a ser melhorado.
    def do_execute_task(self, path, results={}):
        """
        Initiates the execution of the script provided by path.
        
        PARAMETER 1: path: The complete path to the script.
        PARAMETER 2: results: Data transfered between this function and script.

        RETURNS: <Boolean> Flag to inform the result of the execution.
        """

        # Caixa de execução da tarefa.
        #taskExectutionBox = TaskExecutionBox(self.window, self, results, { "total_progress": 100 })

        import csv
        
        # Resultado da execução da tarefa.
        task_result = self.middleware.execute(self.treedata, path, globals(), {
            "RESULTS":    results,
            "messagebox": messagebox,
            "filedialog": filedialog,
            "os":         os,
            'len': len,
            'csv': csv,
            "TaskExecutionBox": None #taskExectutionBox
       })

        # Ações padrões em caso de resultado.
        #if len(results.records_DIFF):
            
            #SubTreeview(self.window, results.records_DIFF, "error", {'heading': ''})

        # Caso seja necessário restartar a GUI.
        if results and results.restart_gui:

            # Restart a GUI da janela.
            self.close()
            self.render()


class SubTreeview(TreeviewBuilder):
    """
    Creates the representation of a sub tree view graphical interface.

    SUPER 1: Class responsible for managing the GUI components of the tree view.
    """
        
    def __init__(self, top_window, records, tags=None, settings=None):
        """
        Creates variables used by the internal functions.
        Starts the processes responsible for configuring the tree view.

        PARAMETER 1: window: Upper window.
        PARAMETER 2: records: <TreeData.Record> objects to be rendered.
        PARAMETER 3: tags: Fonts used by the elements.
        PARAMETER 4: settings: Main configurations.

        RETURNS: None.
        """

        # Janela da aplicação.
        self.top_window = top_window
        
        # Subjanela da aplicação. 
        self.window = Toplevel(top_window)
        
        # Eventos do teclado.
        #self.window.bind("<Escape>", lambda event: self.window.destroy())

        # Estilização da janela.
        self.style = ttk.Style()

        # Configurações da janela.
        self.settings = settings

        # Construtor de árvore da janela principal.
        self.TreeviewFactory = self.NewTreeview(self.window, self.style, settings)
        
        # Renderização da janela.
        self.render(records, tags)

        # Janela para a interface.
        self.initialize_window()

        return None


    def initialize_window(self):
        """
        Initializes the main Window object used in the graphical interface.

        1. Creates brand new <Tk Window> object.
        2. Configures it's title, size and appearence.
        
        RETURNS: None.
        """
        
        # Título.
        self.window.title("Tree Data (Filtro)")

        # Tamanho.
        self.window.geometry("570x325")

        # Redimensionamento.
        self.window.resizable(False, False)

        # Ícone.
        self.window.iconbitmap( TreeData.settings.get("paths").get("icon") )

        #TAGGED: Não funcionando!
        # Cor de fundo.
        #self.window.configure(background="black")

        # Ativa a captura de eventos.
        self.window.grab_set()

        # Força o foco para a subjanela.
        self.window.focus_force()

        # A jnela principal deve aguardar o resultado da subjanela.
        self.top_window.wait_window(self.window)
        
        return None


    def render(self, records, tags=None):
        """
        Initiates the rendering process of the graphical interface.

        PARAMETER 1: records: <TreeData.Record> objects to be rendered.
        PARAMETER 2: tags: Fonts used by the elements.
        
        RETURNS: None.
        """
        
        # Árvore de registros e campos.
        self.Treeview = self.TreeviewFactory.Treeview()

        # Constroi a arvore de elementos (Registros).
        for record in records:

            # Representação do valor do registro.
            record_value = record.parameters.rules['link']['settings'].get('record', {}).get('representation', "")

            # Sem representação, aparece como vazio.
            if record_value == "":
                
                pass
            
            # Representação em códigos do vetor.
            elif record_value == "vector":

                # Junta vetor de códigos em um texto.
                record_value = " ".join( record.vector )

            # Representação com valor de campo específico.
            else:

                # Valor extraido do campo especificado.
                record_value = record.get(record_value, bydescription=True)

                # Caso campo não exista, aparece como vazio.
                if not record_value:

                    # Sem representação.
                    record_value = ""
                    
            # Widget ID gerado na criação.
            record_widget = self.TreeviewFactory.Record(record.name, {
                'value': record_value
            })
            
            # Configura a fonte no widget.
            self.Treeview.item(record_widget, tags=("default", tags))
        
            # Constroi a arvore de elementos (Campos).
            for field in record.fields:

                # Objeto campo.
                field = record.get(field, value=False)

                # Detalhes do valor do campo.
                field_details = field.get(details=True)

                # Widget ID gerado na criação.
                field_widget = self.TreeviewFactory.Field(field.name, {
                    'parent': record_widget,
                    'value':  field_details['value'],
                    'fonts':  field_details['class']
                })

        # Renderização.
        self.TreeviewFactory.pack(fill=BOTH, expand=True)

        return None


# TAGGED: Melhorar a descrição.
class WindowMenu(Menu):
    """
    Creates the representation of a GUI menu.

    SUPER 1: Class responsible for managing the Tk Menu elements.
    """

    def __init__(self, application, window):
        """
        Creates variables used by the internal functions.
        Starts the processes responsible for configuring the menu.

        PARAMETER 1: application: <TreeView> object.
        PARAMETER 2: window: Upper window.

        RETURNS: None.
        """

        # Inicialização da classe do menu.
        Menu.__init__(self, window)

        # Mapeia a janela principal.
        self.window = window

        # Mapeia a interface principal.
        self.application = application

        # Barra de menu principal.
        menubar = self.menubar = Menu(self.window)

        # Eventos do teclado.
        window.bind("<Control-s>",      lambda event: self.on_save_file() )
        window.bind("<Control-f>",      lambda event: self.on_filter() )
        window.bind("<Control-i>",      lambda event: self.on_goto() )
        window.bind("<Control-p>",      lambda event: self.on_search() )
        window.bind("<Control-t>",      lambda event: self.on_select_task() )
        window.bind("<Escape><Escape>", lambda event: self.window.destroy() )
        
        # Criação dos menus paralelos.
        files_menu = self.files_menu = Menu(menubar, tearoff=0)
        explo_menu = self.explo_menu = Menu(menubar, tearoff=0)
        datab_menu = self.datab_menu = Menu(menubar, tearoff=0)
        https_menu = self.https_menu = Menu(menubar, tearoff=0)
        tools_menu = self.tools_menu = Menu(menubar, tearoff=0)
        advan_menu = self.advan_menu = Menu(menubar, tearoff=0)
        confg_menu = self.confg_menu = Menu(menubar, tearoff=0)

        # Configuração dos menus paralelos.
        menubar.add_cascade(label='Arquivo',       menu=files_menu)
        menubar.add_cascade(label='Explorador'    ,menu=explo_menu)
        menubar.add_cascade(label='Banco de Dados',menu=datab_menu)
        menubar.add_cascade(label='HTTP',          menu=https_menu)
        menubar.add_cascade(label='Ferramentas',   menu=tools_menu)
        menubar.add_cascade(label='Avançado',      menu=advan_menu)
        menubar.add_cascade(label='Configurações', menu=confg_menu)
        
        # Menu (Arquivo).
        files_menu.add_command(label='Abrir',       command=self.on_open_file)
        files_menu.add_separator()
        files_menu.add_command(label='Salvar',      command=self.on_save_file,    state='disabled')
        files_menu.add_command(label='Salvar Como', command=self.on_save_file_as, state='disabled')
        files_menu.add_separator()
        files_menu.add_command(label='Fechar',      command=self.on_close_file,  state='disabled')
        files_menu.add_command(label='Encerrar',    command=self.window.destroy, state='normal')

        # Menu (Explorador).
        explo_menu.add_command(label="Conectar",    command=None, state="disabled")
        explo_menu.add_separator()
        explo_menu.add_command(label="Desconectar", command=None, state='disabled')
        explo_menu.add_command(label="Encerrar",    command=None, state="disabled")

        # Menu (Banco de Dados).
        datab_menu.add_command(label="Conectar",    command=self.on_connect_database)
        datab_menu.add_separator()
        datab_menu.add_command(label="Mudar Tabela",command=self.on_change_table, state='disabled')
        datab_menu.add_separator()
        datab_menu.add_command(label="Salvar",      command=None,  state='disabled')
        datab_menu.add_separator()
        datab_menu.add_command(label="Desconectar", command=self.on_disconnect_database, state='disabled')
        datab_menu.add_command(label="Encerrar",    command=self.destroy_with_sql)

        # Menu (HTTPS).
        https_menu.add_command(label="Conectar",    command=None, state="disabled")
        https_menu.add_separator()
        https_menu.add_command(label="Desconectar", command=None, state='disabled')
        https_menu.add_command(label="Encerrar",    command=None, state="disabled")
        
        # Menu (Ferramentas).
        tools_menu.add_command(label="Filtrar",              command=self.on_filter)
        tools_menu.add_command(label="Ir Para",              command=self.on_goto)
        tools_menu.add_command(label="Ordenar",              command=None, state='disabled')
        tools_menu.add_command(label="Exportar",             command=None, state='disabled')
        tools_menu.add_command(label="Pesquisar",            command=self.on_search)
        
        tools_menu.add_separator()
        tools_menu.add_command(label="Executar Tarefa",      command=self.on_select_task)
        tools_menu.add_command(label="Visualizar Histórico", command=None, state='disabled')
        tools_menu.add_separator()
        tools_menu.add_command(label="Fechar Itens Abertos",    command=self.on_collapse_all)
        tools_menu.add_command(label="Limpar Itens Destacados", command=self.on_clear)

        # Menu (Avançado).
        advan_menu.add_command(label="Para Cada ƒ(x)",          command=None, state="disabled")
        advan_menu.add_command(label="Pesquisa Detalhada",      command=None, state="disabled")
        advan_menu.add_separator()
        advan_menu.add_command(label="Importação de Registros", command=None, state="disabled")
        advan_menu.add_command(label="Comparação de Arquivos",  command=None, state="disabled")
        advan_menu.add_separator()
        advan_menu.add_command(label="Console de Comandos",     command=None, state="disabled")
        advan_menu.add_command(label="Conversor Hexadecimal",   command=None, state="disabled")

        # Menu (Configurações).
        confg_menu.add_command(label="Painel de Recursos",           command=None, state="disabled")
        confg_menu.add_separator()
        confg_menu.add_command(label="Configuração da Interface",    command=None, state="disabled")
        confg_menu.add_command(label="Configuração da Aplicação",    command=None, state="disabled")
        confg_menu.add_separator()
        confg_menu.add_command(label="Configuração dos Layouts",     command=None, state="disabled")
        confg_menu.add_command(label="Configuração dos Parâmetros",  command=self.display_configure_parameters, state="normal")
        confg_menu.add_command(label="Configuração dos Dicionários", command=None, state="disabled")
        confg_menu.add_separator()
        confg_menu.add_command(label="Atualização",                  command=None, state="disabled")
        confg_menu.add_command(label="Suporte",                      command=None)

        # Configura a barra de menu na janela.
        self.window.configure(menu=menubar)
        
        # Atualiza as configurações iniciais do menu.
        self.initialize_menu()

        #self.update_menu()


    # TAGGED: Dá pra melhorar bastante essa função.
    def initialize_menu(self):
        """
        Configures the menu according to the current <TreeData> object and status.
        
        RETURNS: None.
        """

        # Configurações dos parâmetros.
        settings = self.application.settings

        # Configurações do menu.
        menu_settings = settings.get('menu', {})

        # Condicionais do Menu (Arquivo).
        file_saving    = "disabled" if menu_settings.get('disable-file-saving',    False) else "normal"
        file_saving_as = "disabled" if menu_settings.get('disable-file-saving-as', False) else "normal"

        # Condicionais do menus principais.
        hide_menu_database = menu_settings.get('hide-database', False)
        hide_menu_explorer = menu_settings.get('hide-explorer', False)
        hide_menu_http     = menu_settings.get('hide-http',     False)
        hide_menu_tools    = menu_settings.get('hide-tools',    False)
        
        tool_task   = "disabled" if menu_settings.get('disable-task',   False) else "normal"
        tool_goto   = "disabled" if menu_settings.get('disable-goto',   False) else "normal"
        tool_filter = "disabled" if menu_settings.get('disable-filter', False) else "normal"
        tool_search = "disabled" if menu_settings.get('disable-search', False) else "normal"

        # Condicionais do Menu (Avançado).
        hide_menu_advanced = menu_settings.get('hide-advanced', False)
        
        # Condicionais do Menu (Configurações).
        hide_menu_settings = menu_settings.get('hide-settings', False)

        # Condicionais dos Registros.      
        enable_removal = "disabled" if self.application.settings.get('disable-record-removal') else "normal"

        # Condicionais dos Campos.
        #field_edition = "disabled" if self.application.settings.get('field', {}).get('disable-editing') else "normal"

        # Menu do campo.
        #self.application.Treeview.field_menu.entryconfig('Editar', state="disabled")

        #print(self.application.TreeviewFactory.field_menu)
        
        # Estrutura para regras dos menus.
        menu_rules = {
            'File': {
                # Variáveis internas do menu.
                '@name': 'Arquivo',
                '@reff': self.files_menu,
                '@class': File,
                # Comandos.
                'Abrir':       { 'online': 'disabled',      'offline': 'normal'   },
                'Salvar':      { 'online': file_saving,     'offline': 'disabled' },
                'Salvar Como': { 'online': file_saving_as,  'offline': 'disabled' },
                'Fechar':      { 'online': 'normal',        'offline': 'disabled' },
                'Encerrar':    { 'online': 'normal',        'offline': 'normal'   }
            },
            'SQLDatabase': {
                # Variáveis internas do menu.
                '@name': 'Banco de Dados',
                '@reff': self.datab_menu,
                '@stat': "disabled",
                '@hide': hide_menu_database,
                '@class': None,
                # Comandos.
                'Conectar':     { 'online': 'disabled', 'offline': 'normal'   },
                'Mudar Tabela': { 'online': 'normal',   'offline': 'disabled' },
                'Salvar':       { 'online': 'normal',   'offline': 'disabled' },
                'Desconectar':  { 'online': 'normal',   'offline': 'disabled' },
                'Encerrar':     { 'online': 'normal',   'offline': 'normal'   }
            },
            'Explorador': {
                # Variáveis internas do menu.
                '@name': "Explorador",
                '@reff': self.explo_menu,
                '@stat': "disabled",
                '@hide': hide_menu_explorer,
                '@class': None
            },
            'HTTP': {
                # Variáveis internas do menu.
                '@name': "HTTP",
                '@reff': self.https_menu,
                '@stat': "disabled",
                '@hide': hide_menu_http,
                '@class': None
            },
            'Tools': {
                # Variáveis internas do menu.
                '@name': "Ferramentas",
                '@reff': self.tools_menu,
                '@hide': hide_menu_tools,
                '@class': None,
                '@skip': True,
                # Comandos.
                'Filtrar':          { 'online': tool_filter,    'offline': "disabled" },
                'Ir Para':          { 'online': tool_goto,      'offline': "disabled" },
                'Pesquisar':        { 'online': tool_search,    'offline': "disabled" },
                'Executar Tarefa':  { 'online': tool_task,      'offline': "disabled" },
                
                'Fechar Itens Abertos':     { 'online': "normal",   'offline': "disabled" },
                'Limpar Itens Destacados':  { 'online': "normal",   'offline': "disabled" }
            },
            'Advanced': {
                # Variáveis internas do menu.
                '@name': "Avançado",
                '@reff': self.advan_menu,
                '@stat': "disabled",
                '@hide': hide_menu_advanced,
                '@class': None
            },
            'Settings': {
                # Variáveis internas do menu.
                '@name': "Configurações",
                '@reff': self.confg_menu,
                '@hide': hide_menu_settings,
                '@skip': True,
                '@class': None
            }
        }

        # Indica a existência da conexão do objeto com a interface.
        connection = 'online' if (self.application.treedata and self.application.treedata.link) else 'offline'
        
        # Configurações do menu para objetos online.
        for class_name, menu_rules in menu_rules.items():

            # Nome e referência do menu apresentado na interface.
            menu_name = menu_rules.get('@name')
            menu_reff = menu_rules.get('@reff')
            menu_stat = menu_rules.get('@stat', "normal")
            menu_hide = menu_rules.get('@hide', False)
            menu_clss = menu_rules.get('@class')
            menu_skip = menu_rules.get('@skip', False)
            
            # Validação.
            if menu_hide:

                # Remove o menu.
                self.menubar.delete(menu_name)

                continue

            # Configurações do menu para casos de objeto offline.
            if connection == 'offline' or (menu_clss and isinstance(self.application.treedata.link, menu_clss)) or menu_skip:

                # Configuração padrão dos menus.
                self.menubar.entryconfig(menu_name, state=menu_stat)

                # Configura o estado dos comandos de acordo com a conexão.
                for command_name, command_rules in menu_rules.items():

                    # Pula as variáveis internas.
                    if command_name in ['@name', '@reff', '@class', '@skip', '@stat', '@hide']:
                            
                        continue

                    # Status de acordo com as regras.
                    command_state = command_rules.get(connection)

                    # Configura o comando.
                    menu_reff.entryconfig(command_name, state=command_state)
     
            # Configurações nos menus paralelos.
            else:

                if menu_skip:

                    continue

                # Desabilita o menu paralelo.
                self.menubar.entryconfig(menu_name, state='disabled')

        return None


    # TAGGED: Melhorar o nome dessa função.
    def update_menu(self):
        """
        Configures the menu according to the parameters.
        
        RETURNS: None.
        """

        #return None
        

        
        # Menu (Arquivo).
        #self.files_menu.entryconfig("Salvar",      state=enable_saving)
        #self.files_menu.entryconfig("Salvar Como", state=enable_saving_as)
        
        # Menu (Banco de Dados).
        #self.datab_menu.entryconfig("Salvar", state=enable_saving)

        # Menu (Ferramentas).
        #self.tools_menu.entryconfig("Executar Tarefa", state='disabled')

        # Menu do registro.
        #self.record_menu.entryconfig('Remover', state=enable_removal)

        

        return None


    # TAGGED: Aprimorar o nome da função.
    # TAGGED: Trabalhar no código e descrição.
    def configure_menu(self, state=None, settings=None):
        '''
        Método responsável pelas seguintes operações:
        1. Configurar o estado dos menus informados.
        '''
        
        for option, menu in settings.items():

            menu.entryconfig(option, state=state)

        return None


    # TAGGED: Trabalhar no código da função.        
    def on_connect_database(self, event=None):
        """
        Initiates the processes required to connect to database by GUI.

        1. Initiates the GUI component responsible for the database connection interface.
        2. Handles the gap between the GUI results and the creation of the <TreeData> object.
        3. Updates the menu.
        
        PARAMETER: event: <Event> object that called the function.
        
        RETURNS: None.
        """
        
        # Interoperabilidade.
        data = StandardData()

        # Credenciais de acesso.
        data.credentials = {}

        # Resultado da autenticação.
        data.auth = False

        # Conexão com o banco de dados.
        data.connection = None

        # Objeto da interface atual.
        treedata = self.application.treedata

        # Janela de ação.
        ConnectDatabase(self.window, data, {
            'connections': {
                'RptGar': {
                    "server":             "127.0.0.1\\RIOCARD2022",
                    "username":           "sa",
                    "password":           "Riocard@01",
                    "default-database":   "db_mercury",
                    "trusted-connection": False,
                    "remember-access":    False
                }
            }
        })

        # Caso não seja possível de autenticação.
        if not data.auth:

            return None

        if not treedata :

            # Cria novo objeto Tree Data.
            new_treedata = TreeData(data.credentials.get('server'), data.connection_name, settings={"initialize": True})

            # Substitui o objeto na aplicação.
            self.application.replace_treedata(new_treedata)

        # Caso seja necessário restartar a GUI.
        if data and data.restart_gui:

            # Desabilita os menus paralelos.
            self.initialize_menu()

            # Atualiza o menu com os parâmetros de configuração do objeto.
            #self.update_menu()

            # Solicita a tabela a ser renderizada.
            self.on_change_table()

        return None


    def on_disconnect_database(self, event=None):
        """
        Disconnects the database by GUI.

        1. Closes the opened connection to database.
        2. Deletes the associated <TreeData> object.
        3. Updates the main graphical interface.
        4. Updates the menu.
        
        PARAMETER: event: <Event> object that called the function.
        
        RETURNS: None.
        """
        
        if self.application.treedata:

            # Reseta o link utilizado na conexão.
            self.application.treedata.link.disconnect()

            # Encerra a interface gráfica.
            self.application.close(kill=True)

            # Habilita os menus paralelos.
            self.initialize_menu()

        return None


    def destroy_with_sql(self, event=None):
        """
        Disconnects the database while destroying the GUI.
        
        PARAMETER: event: <Event> object that called the function.
        
        RETURNS: None.
        """

        # Desconecta do banco de dados.
        self.on_disconnect_database()

        # Destrói a janela principal.
        self.window.destroy()

        return None

    
    def on_change_table(self, event=None):
        """
        Initiates the processes required to change the table by GUI.

        1. Initiates the GUI component responsible for selecting table options.
        2. Changes the <TreeData> object pool of data while selecting a new table source.
        3. Updates the main graphical interface.
        
        PARAMETER: event: <Event> object that called the function.
        
        RETURNS: None.
        """
        
        # Dados para a janela.
        data = StandardData()

        # Nome da tabela.
        data.table = None

        # Janela de ação.
        SelectTable(self.window, self.application.treedata, data)

        # Caso não seja selecionado o nome,
        if not data.table:

            return None

        # Modifica a tabela do link.
        self.application.treedata.structure.link.select(data.table)

        # Reseta as configurações.
        self.application.treedata.structure.restart()

        # Caso seja necessário restartar a GUI.
        if data and data.restart_gui:

            # Restart a GUI da janela.
            self.application.close()
            self.application.render()

        return None
    

    def on_save_file(self, settings={}):
        """
        Saves the <TreeData> object's content to file.
        
        PARAMETER: settings: Custom configurations.
        
        RETURNS: None.
        """

        # Mensagem de confirmação.
        confirmation = messagebox.askquestion(title="Salvar?", message="Deseja salvar o arquivo?")

        if confirmation == 'no':

            return None

        # Tenta salvar os dados de maneira persistente.
        result = self.application.treedata.save(persistent=True, settings=settings)

        if result:

            # Mensagem de suporte.
            messagebox.showinfo(title="Aviso!", message="Arquivo salvo!")
            
        else:
            
            # Mensagem de suporte.
            messagebox.showerror(title="Erro!", message="Não foi possível escrever para o arquivo!")

        return None

    
    def on_save_file_as(self):
        """
        Saves the <TreeData> object's content to new file.
        
        PARAMETER: settings: Custom configurations.
        
        RETURNS: None.
        """
        
        # Caminho completo para o novo arquivo.
        new_path = filedialog.asksaveasfilename(initialfile = self.application.treedata.link.name, title="Salvar arquivo", filetypes=(
            ("Todos os arquivos", "*.*"),
            ("Arquivos binarios", "*.BIN")
        ))

        # O caminho necessita ser válido.
        if not new_path:

            return None

        # Delega o salvamento do arquivo.
        self.on_save_file({ 'path': new_path })

        return None
    
    
    def on_open_file(self):
        """
        Initiates the main process for opening files while creating <TreeData> object.

        1. Opens Tkinter file dialog asking for path while validating it's existence.
        2. Updates the footer label.
        3. Initiates the rendering of the progress bar.
        4. Restarts the current data and graphical interface life-cycle
        5. Initiates the rendering of the tree view elements.
        6. It may prompts error if not able to complete the process.

        RETURNS: None.
        """
        
        # Caminho do arquivo a ser importado.
        path = filedialog.askopenfilename(
            filetypes=(
                ("Todos os arquivos",    "*.*"),
                ("Arquivos de texto",    "*.txt"),
                ("Arquivos de binarios", "*.bin"),
                ("Arquivos de CSV",      "*.csv"),
                ("Arquivos de JSON",     "*.json")
            )
        )

        try:
            
            # Valida existência do caminho.
            if not os.path.exists(path):

                print("CAMINHO NAO EXISTE")

                raise Exception

            # Mostra o rodapé.
            self.application.footer.pack(anchor=W, side="bottom")

            # Atualiza o texto do rodapé.
            self.application.footer.config(text=r"Processando...")

            # Renderiza a barra de progresso.
            self.application.Progressbar.start()

            # Cria novo objeto com  a atualização da barra de progresso como callback.
            new_treedata = self.application.create_treedata(path, settings={
                'callback.progress': self.application.Progressbar.set
            })

            # Restaura a janela para a posição de destaque.
            self.window.deiconify()

            # Caso arquivo importado não esteja apto, não fazer nada!
            if not new_treedata.status:

                raise Exception

            # Fecha a renderização atual.
            self.application.close()

            # Atualiza o novo treedata no controle interno.
            self.application.replace_treedata(new_treedata)

            # Desabilita os menus paralelos.
            self.initialize_menu()

            # Atualiza o menu.
            #self.update_menu()
            
            # Renderiza a aplicação.
            self.application.render()

        except:

            print("IMPORTACAO CANCELADA")

            # Mensagem de suporte.
            messagebox.showwarning(title="Aviso!", message="Importação cancelada!")
            
            # Fecha a renderização atual.
            self.application.close()

        return None

    
    @TreeManager.validate_treedata
    def on_goto(self):
        """
        Initiates the processes required to go to specific position in the GUI.

        1. Initiates the GUI component responsible for selecting records.
        
        RETURNS: None.
        """
        
        # Dados para a janela.
        data = StandardData()

        # Abertura do registro.
        #

        # Janela de pesquisa.
        GotoBox(self.window, self.application, data)

        return None


    def on_select_task(self):
        """
        Initiates the processes required to execute script tasks.

        1. Initiates the GUI component responsible for selecting task.
        2. Calls function responsible for executing the selected task.
        3. May creates sub tree view with the results of the execution.
        4. May restarts the current data and graphical interface life-cycle.
        
        RETURNS: None.
        """
        
        # Dados para a janela.
        data = StandardData()

        # Registros encontrados com diferença.
        data.records_DIFF = []

        # Parâmetro de configuração para as tarefas.
        settings = self.application.treedata.parameters.rules.get('task')

        # Configura o caminho principal das tarefas.
        data.path = settings.get('folder')

        # Bandeira de cancelamento da tarefa.
        data.cancel = False
        
        # Janela de tarefa.
        TaskSelectionBox(self.window, self.application.treedata, data, settings)

        # Executa a tarefa informada.
        self.application.do_execute_task(data.task_path, data)

        # Ações padrões em caso de resultado.
        if len(data.records):
            
            SubTreeview(self.window, data.records, "okay", {'heading': ''})

        # Ações padrões em caso de resultado.
        if len(data.records_DIFF):
            
            SubTreeview(self.window, data.records_DIFF, "error", {'heading': ''})

        # Caso seja necessário restartar a GUI.
        if data and data.restart_gui:

            # Restart a GUI da janela.
            self.application.close()
            self.application.render()

        return None

        
    def on_close_file(self):
        """
        Closes file while finishing the current data and graphical interface life-cycle.

        1. Initiates the process of finishing the main application.
        2. Updates the menu.
        
        RETURNS: None.
        """


        # TAGGED
        # Condicionais do Menu (Arquivo).
        #conditional = self.application.settings.get('view', {}).get('destroy-on-close', False)

        #if conditional:

            #self.window.destroy()

            #return None
            
        # Fecha a interface gráfica renderizada.
        self.application.close(kill=True)

        # Habilita os menus paralelos.
        self.initialize_menu()
        
        return None


    def on_clear(self):
        """
        Removes the colored fonts from the highlighted elements.
        
        RETURNS: None.
        """
        
        self.application.TreeviewFactory.do_remove_fonts()

        return None


    def on_collapse_all(self):
        """
        Collapses all the opened elements.
        
        RETURNS: None.
        """
       
        self.application.TreeviewFactory.do_collapse_all()

        return None

    @TreeManager.validate_treedata
    def on_search(self, settings={}):
        """
        Initiates the processes required to execute script tasks.

        1. Initiates the GUI component responsible for searching.
        2. May creates sub tree view with the results of the execution.
        3. May highlights the returned elements by the result in the GUI.

        RETURNS: None.
        """
        
        # Janela de pesquisa.
        searchBox = SearchBox(self.window, self.application.treedata, settings)

        # Status da operação.
        if searchBox.status == False:

            return None

        # Registros encontrados na operação.
        records = searchBox.output

        # Destacar os registros?
        if searchBox.variable_highlight.get():

            # Para cada registro.
            for record in records:

                # Elemento no catálogo.
                widget = self.application.TreeviewFactory.get_widget(name=record.id, by='ID')

                # Destaca o elemento.
                self.application.TreeviewFactory.do_highlight(widget.iid, font='highlight')
                
        # Abrir a janela de resultados?
        if searchBox.variable_window.get():

            records_length = len(records)

            # Janela de resultados.
            SubTreeview(self.window, records, None, {
                'heading': "Total: {length}".format(length=records_length)
            })

        # Reabrir a janela de pesquisa?
        if searchBox.variable_persist.get():

            self.on_search({
                'entry1': searchBox.variable_entry1.get(),
                'entry2': searchBox.variable_entry2.get(),
                'option1': searchBox.variable_option1 #'"203 - CHANGE LINE"'
            })

        return None


    @TreeManager.validate_treedata
    def on_filter(self):
        """
        Initiates the processes required to execute script tasks.

        1. Initiates the GUI component responsible for filtering.
        3. May creates sub tree view with the results of the execution.

        RETURNS: None.
        """
        
       # Dados para a janela.
        data = StandardData()

        # Janela da GUI.
        FilterBox(self.window, self.application.treedata, data)

        # Quantidade de registros encontrados no filtro.
        records_length = len(data.records)

        # Ações padrões em caso de resultado.
        if records_length:

            # Configurações da janela de filtro.
            settings = {
                "heading": "Total: {length}".format(length=records_length)
            }

            # Janela de filtro.
            SubTreeview(self.window, data.records, None, settings)

        return None


    def display_configure_parameters(self, event=None):

        # Caminho completo do arquivo de parâmetros.
        path = self.application.treedata.parameters.path

        # Objeto Tree Data para auxiliar na configuração.
        tree = TreeData(path, "configure-parameter.json")

        # Interface gráfica.
        view = TreeView()

        # Renderização.
        view.open(tree)

        return None
