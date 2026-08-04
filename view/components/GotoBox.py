#   Tree Data
#   Versão 1.0.0.0 (Beta)
#   Leonardo Amaral de Souza
#   Rio de Janeiro, 12/09/1997


# Bibliotecas padrões para interfaces gráficas.
from tkinter import *
from tkinter import ttk


# Classe principal.
class GotoBox:
    '''
    Classe responsável pelas seguintes operações:
    1.
    2.
    3.
    '''

    def __init__(self, top_window=None, application=None, result=None):


        # Janela atual.
        self.window = None

        # Janela superior.
        self.top_window = top_window

        # Tree Data.
        self.treedata = application.treedata
        
        # Referência a aplicação de interface gráfica.
        self.application = application
        
        # Resultado da janela.
        self.result = result

        # Controle de itens ativos.
        self.active_records = []
        self.active_indexes = []

        # Execução dos processos.
        self.boot()


    def boot(self):

        # Configuração da janela.
        self.configure_window()

        # Mapeia atalhos do teclado.
        self.map_shortcuts()

        # Renderiza a janela.
        self.render()

        # Interface inicializada.
        #self.window.mainloop()

        return None


    def configure_window(self):
        
        if not self.top_window:

            # Inicializa como janela principal.
            self.window = Tk()
            
        else:

            # Inicializa como subjanela da janela principal.        
            self.window = Toplevel(self.top_window)

        # Título.
        self.window.title("Ir Para")

        # Tamanho.
        self.window.geometry("305x153")

        # Redimensionável
        self.window.resizable(False, False)

        # Associa eventos a janela atual.
        #self.window.grab_set()

        #if self.top_window:

            # A janela principal deve aguardar a subjanela.
            #self.top_window.wait_window(self.window)

        # Protocolo de encerramento da janela.
        #self.window.protocol("WM_DELETE_WINDOW", self.destroy)

        return None


    def map_shortcuts(self):

        # Tecla ENTER.
        #self.window.bind("<Return>", lambda event: self.onclick_button() )

        # Tecla ESC.
        self.window.bind("<Escape>", lambda event: self.window.destroy() )

        return None


    def destroy(self):

        # Finaliza o looping de renderização.
        self.window.quit()

        # Finaliza a janela atual.
        self.window.destroy()

        return None

    
    def get_indexes(self, records, byID=False):

        indexes = []
        
        for record in records:

            # Widget do registro.
            if byID:

                widget = self.application.TreeviewFactory.get_widget("treeview.records", record.id, by='ID')

            else:

                widget = self.application.TreeviewFactory.get_widget("treeview.records", record)
                
            # Adiciona o índice do registro na listagem.
            indexes.append(widget.index)

        return indexes


    def onchange_combobox1(self, event):
        
        # Valor do registro selecionado.
        value = self.combobox_name.get()

        # Caso esteja vazio, não fazer nada.
        if not value:
            
            return None

        # Registros do grupo selecionado.
        records = self.treedata.structure.records_groups[value]
                    
        # Atualiza a lista no controle interno.
        self.active_records = records
        
        # Indíces de cada registro do grupo selecionado.
        indexes = self.get_indexes(records, byID=True)

        # Configura os valores no combox de campos.
        self.combobox_index["values"] = indexes

        # Atualiza a lista no controle interno.
        self.active_indexes = indexes

        # Limpa a seleção atual do combox de campos.
        self.combobox_index.set("")


    def onclick_button1(self, index=None, byHighlighting=False):

        # Nome do registro selecionado.
        value1 = self.combobox_name.get()

        # Índice do registro selecionado.
        value2 = self.combobox_index.get()

        if not value1 and not byHighlighting:
            return None

        if not value2:
            value2 = self.active_indexes[0]

        if index:
            value2 = index

        # Item selecionado.
        widget = self.application.TreeviewFactory.get_widget(section="treeview.records", name=int(value2), by='index')
        
        # Somente interagir com registros destacados.
        if self.result.variable_boolean.get():

            # Lista de registros destacados na interface.
            highlighted_records = self.application.tracking.get("highlighting", [])

            # Verifica se o registro está destacado.
            if widget.name in highlighted_records:
                pass

            # Caso não seja, buscar o primeiro registro destacado.
            else:
                pass

        
        self.combobox_index.set(value2)

        # Solicita a direcionamento até o item.
        self.application.do_goto(widget)

        # Verifica se o item deve ser expandido.
        self.expand_widget(widget)

        
        

    def onclick_button2(self):

        # Valor do índice atual selecionado.
        index = self.combobox_index.get()

        if not index:
            
            return None

        # Conversão.
        index = int( index )

        # Índice da lista interna.
        current_index = self.active_indexes.index(index)

        # Índice anterior.
        previous_index = current_index - 1

        # Valida se o indíce anterior está no controle.
        if previous_index < 0:
            
            return None

        # Fecha o item atual.
        self.collapse_widget(index)

        # Valor do indíce anterior.
        previous_value2 = self.active_indexes[previous_index]

        # Ir para o indíce anterior.
        self.onclick_button1(previous_value2)        


    def onclick_button3(self):
        
        # Valor do indíce atual selecionado.
        index = self.combobox_index.get()

        if not index:
            return None

        # Conversão.
        index = int( index )

        # Indíce da lista interna.
        current_index = self.active_indexes.index(index)

        # Próximo indíce.
        next_index = current_index + 1

        # Valida se o próximo indíce está no controle.
        if next_index >= len(self.active_indexes):
            return None
    
        # Fecha o item atual.
        self.collapse_widget(index)
        
        # Valor do próximo indíce.
        next_value2 = self.active_indexes[next_index]

        # Ir para o próximo indíce.
        self.onclick_button1(next_value2)


    def expand_widget(self, widget):

        # Bandeira de indicação.
        flag = self.result.variable_boolean.get()

        # Caso desmarcada, não expandirá.
        if not flag:

            return None
        
        # Solicita a expansão do item.
        self.application.TreeviewFactory.do_expand(widget)

                  
    def collapse_widget(self, index):

        # Item.
        widget = self.application.TreeviewFactory.get_widget(section="treeview.records", name=int(index), by='index')
        
        if not widget:

            return None
        
        # Solicita o fechametno do item.
        self.application.TreeviewFactory.do_collapse(widget)

        
    def render(self):

        # Label Frame.
        label_frame = LabelFrame(self.window, text="Registro / Index", padx=10, pady=10)
        label_frame.grid(row=0, column=0, columnspan=3, padx=10, pady=10)

        # Registro e índice.
        self.combobox_name  = ttk.Combobox(label_frame, width=32, state="readonly")
        self.combobox_index = ttk.Combobox(label_frame, width=3,  state="readonly")
        
        self.combobox_name["values"] = list(self.treedata.structure.records_groups.keys())
        self.combobox_index["values"] = None

        self.combobox_name.bind("<<ComboboxSelected>>", self.onchange_combobox1)
        self.combobox_index.bind("<<ComboboxSelected>>", None)

        self.combobox_name.grid(row=0, column=0, columnspan=2) 
        self.combobox_index.grid(row=0, column=2, padx=(5,0))

        self.combobox_name.current()
        self.combobox_index.current()
        

        # Opções.
        # TAGGED-IMPROVE
        self.checkbox_open = Checkbutton(label_frame, text="Abrir", variable=self.result.variable_boolean, onvalue=1, offvalue=0, command=None)
        self.checkbox_open.grid(row=1, column=0, pady=(12,0), sticky=W)


        # Opções.
        checkbox2 = Checkbutton(label_frame, text="Registros Destacados", variable=None, onvalue=1, offvalue=0, command=None)        
        checkbox2.grid(row=1, column=1, columnspan=2, pady=(12,0))

        # Desabilitado até a implementação.
        checkbox2.config(state="disabled")

        
        # Botões.
        button1 = Button(self.window, text="Buscar", borderwidth=2, relief="groove", width=7, height=1, foreground="white", background="DodgerBlue3", command=self.onclick_button1)
        button2 = Button(self.window, text="Anterior", borderwidth=2, relief="groove", width=10, height=1, background="#eee", command=self.onclick_button2)
        button3 = Button(self.window, text="Próximo", borderwidth=2, relief="groove", width=10, height=1, background="#eee", command=self.onclick_button3)

        button1.grid(row=2, column=0, sticky=W, ipadx=1, pady=0, padx=10)
        button2.grid(row=2, column=1, sticky=E, ipadx=1, pady=0, padx=0)
        button3.grid(row=2, column=2, sticky=E, ipadx=1, pady=0, padx=(0,10))




