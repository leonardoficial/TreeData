#   Tree Data
#   Versão 1.0.0.0 (Beta)
#   Leonardo Amaral de Souza
#   Rio de Janeiro, 12/09/1997


# Bibliotecas padrões para interfaces gráficas.
from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox


# Classe principal.
class SearchBox:


    def __init__(self, top_window, treedata, settings={}):

        # Janela da aplicação.
        self.top_window = top_window
        
        # Subjanela da aplicação.        
        self.window = Toplevel(top_window)

        # Tree Data.
        self.treedata = treedata

        # Configurações.
        self.settings = settings

        # Status da operação.
        self.status = None

        # Resultado da operação.
        self.output = []

        # Variáveis das opções.
        self.variable_regex = BooleanVar()
        self.variable_window = BooleanVar()
        self.variable_persist = BooleanVar()
        self.variable_highlight = BooleanVar()

        # Valores padrões das entradas.
        default_entry1 = settings.get('entry1', "")
        default_entry2 = settings.get('entry2', "")

        # Variavéis das entradas.
        self.variable_entry1 = StringVar(value=default_entry1)
        self.variable_entry2 = StringVar(value=default_entry2)
        
        # Valores selecionados das caixas.
        self.variable_option1 = ""
        self.variable_option2 = ""
                
        # Renderiza a janela.
        self.render()

        # Configuração mais complexa de valores padrões.
        self.configure_defaults()

        # Configuração da janela.
        self.initialize_window()
        
        return None


    def initialize_window(self):
        """
        Initializes the main Window object used in the graphical interface.

        1. Configures it's title, size, appearence and behavior.
        
        RETURNS: None.
        """

        # Título.
        self.window.title('Pesquisa')

        # Tamanho.
        self.window.geometry("260x315")

        # Redimensionamento.
        self.window.resizable(False, False)

        # ENTER: Pesquisar.
        self.window.bind("<Return>", lambda event: self.onclick_button() )

        # ESC: Encerrar a janela de pesquisa.
        self.window.bind("<Escape>", lambda event: self.window.destroy() )

        # Ativa a captura de eventos.
        self.window.grab_set()

        # Força o foco para a subjanela.
        self.window.focus_force()

        # A jnela principal deve aguardar o resultado da subjanela.
        self.top_window.wait_window(self.window)

        return None


    def configure_defaults(self):

        # Opções de seleção padrão.
        default_option1 = self.settings.get('option1', None)
        default_option2 = self.settings.get('option2', None)

        # Valida existência do valor de seleção.
        if not default_option1 or default_option1 not in self.combobox1['values']:

            return None

        # Seta o valor.
        self.combobox1.set(default_option1)

        # Valida existência do valor de seleção.
        if not default_option2 or default_option2 not in self.combobox2['values']:

            return None

        # Popula os valores da segunda caixa de seleção.
        self.onchange_combobox1()

        # Seta o valor.
        self.combobox2.set(default_option2)

        return None
    
        
    def onchange_combobox1(self, event=None):
        
        # Valor do registro selecionado.
        value = self.combobox1.get()

        # Caso esteja vazio, não fazer nada.
        if not value:
            
            return None

        # Atualiza variável de valor selecionado.
        self.variable_option1 = value

        # Configuração dos campos no Combobox 2.
        self.combobox2["values"] = list(self.treedata.structure.records_groups[value][0].fields_names.keys())

        # Limpa a seleção atual do Combobox 2.
        self.combobox2.set("")

        return None
        

    def onchange_combobox2(self, event=None):
        
        # Valor do registro selecionado.
        value = self.combobox2.get()

        # Caso esteja vazio, não fazer nada.
        if not value:
            
            return None

        # Atualiza variável de valor selecionado.
        self.variable_option2 = value

        return None

    
    def onclick_button(self):
        
        # Valores das opções.
        self.option1 = value1 = self.combobox1.get()
        self.option2 = value2 = self.combobox2.get()

        # Valores atuais das entradas.
        entry1 = self.entry1.get()
        entry2 = self.entry2.get()

        # Caso ambos estejam vazios, não fazer nada.
        if value1 == "" and value2 == "":
            
            return None

        # Valor vazio pendente é substituido pelo preenchido.
        if entry1 == "": entry1 = entry2
        if entry2 == "": entry2 = entry1

        # Busca de registros dentro do filtro.
        for records_group_name, records in self.treedata.structure.records_groups.items():

            # Cas não seja igual ao grupo de registros selecionado, pular.
            if value1 != records_group_name:
                
                continue

            # Procura o valor no campo de cada registro.
            for record in records:

                # Valor do campo.
                field_value = record.get(value2, bydescription=True)

                # Caso valor do campo seja igual ao valor inputado.
                if field_value >= entry1 and field_value <= entry2:
                    
                    # Salva o registro no controle.
                    self.output.append(record)


        # Quantidade de registros encontrados.
        records_length = len(self.output)
        
        # Caso sejam encontrados valores na pesquisa.
        if records_length:
            
            # Mensagem de resultado.
            messagetxt ="{length} Registros Encontrados!".format( length=records_length )
            messagebox.showinfo(title="Resultado da Pesquisa", message=messagetxt)

        # Fecha a janela.
        self.window.destroy()

        # Atualiza o status.
        self.status = True

        return None
                            

    def render(self):

        # Label Frame (Caixas de Seleção).
        label_frame = LabelFrame(self.window, text="Registro / Campo", padx=10, pady=10)

        # Renderização.
        label_frame.grid(row=0, column=0, columnspan=2, padx=10, pady=10)

        # Estilo das caixas de seleção.
        combobox_style = dict(width=32, state="readonly")
        
        # Caixas de seleção.
        self.combobox1 = ttk.Combobox(label_frame, textvariable=self.variable_option1, **combobox_style)
        self.combobox2 = ttk.Combobox(label_frame, textvariable=self.variable_option2, **combobox_style)

        # Valores.
        self.combobox1["values"] = list(self.treedata.structure.records_groups.keys())
        self.combobox2["values"] = None

        # Eventos.
        self.combobox1.bind("<<ComboboxSelected>>", self.onchange_combobox1)
        self.combobox2.bind("<<ComboboxSelected>>", self.onchange_combobox2)

        # Renderização.
        self.combobox1.pack() 
        self.combobox2.pack(pady=(10,0))

        # Label Frame (Valor).
        label_frame = LabelFrame(self.window, text="Valor", padx=10, pady=10)
        label_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=(0,10))

        # Estilo das entradas.
        entry_style = dict(width=16, relief="groove", borderwidth=2)

        # Entradas.
        self.entry1 = Entry(label_frame, textvariable=self.variable_entry1, **entry_style)
        self.entry2 = Entry(label_frame, textvariable=self.variable_entry2, **entry_style)

        # Renderização.
        self.entry1.grid(row=0, column=0, ipadx=0, padx=(0,11))
        self.entry2.grid(row=0, column=1, ipadx=0)

        # Label Frame 3.
        label_frame = LabelFrame(self.window, text="Opções", padx=0, pady=10)
        label_frame.grid(row=2, column=0, columnspan=2, padx=10, pady=0, ipadx=6)

        # Opções
        checkbox1 = Checkbutton(label_frame, text="RegEx", onvalue=1, offvalue=0, variable=self.variable_regex)
        checkbox2 = Checkbutton(label_frame, text="Destacar", onvalue=1, offvalue=0,  variable=self.variable_highlight)
        checkbox3 = Checkbutton(label_frame, text="Abrir Filtro", onvalue=1, offvalue=0, variable=self.variable_window)
        checkbox4 = Checkbutton(label_frame, text="Manter", onvalue=1, offvalue=0, variable=self.variable_persist)
        
        checkbox1.grid(row=0, column=0, sticky=W, padx=(7,0))
        checkbox2.grid(row=0, column=1, sticky=W)
        checkbox3.grid(row=0, column=2, sticky=W)

        checkbox4.grid(row=1, column=0, sticky=W, padx=(7,0), columnspan=3)

        # Botão de Execução e Cancelamento.
        button1 = Button(self.window, text="CANCELAR", borderwidth=2, relief="groove", width=15, height=1, background="#EEE", command=self.window.destroy)
        button2 = Button(self.window, text="EXECUTAR", borderwidth=2, relief="groove", width=15, height=1, foreground="white", background="DodgerBlue3", command=self.onclick_button)

        button2.grid(row=3, column=1, pady=10, sticky=W, padx=0)
        button1.grid(row=3, column=0, pady=10, sticky=W, padx=(9,0))

        return None
