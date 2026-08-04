#   Tree Data
#   Versão 1.0.0.0 (Beta)
#   Leonardo Amaral de Souza
#   Rio de Janeiro, 12/09/1997

from tkinter import *
from tkinter import ttk

class FilterBox():

    def __init__(self, top_window, treedata, result):

        # Cria subjanela da aplicação principal.        
        window = Toplevel(top_window)

        # Configuração da subjanela.
        self.window = window
        self.window.title('Filtro')
        self.window.geometry("260x165")
        self.window.resizable(False, False)

        # Tree Data.
        self.treedata = treedata
        
        # Resultado da janela.
        self.result = result

        # Renderiza a janela.
        self.render()

        self.window.bind("<Return>", lambda event: self.onclick_button() )
        self.window.bind("<Escape>", lambda event: self.window.destroy() )

        # A jnela principal deve aguardar o resultado da subjanela.
        self.window.grab_set()
        self.window.focus_force()
        top_window.wait_window(window)


    def onchange_combobox1(self, event):
        
        # Valor do filtro selecionado.
        value = self.combobox1.get()

        # Caso esteja vazio, não fazer nada.
        if not value:
            return None

        # Dicionário onde a busca será realizada.
        self.filter_dictionary = None

        if value == "Rótulos":
            self.filter_dictionary = self.treedata.structure.records_labels

        elif value == "Registros":
            self.filter_dictionary = self.treedata.structure.records_groups
            
        elif value == "Chaves Estrangeiras":
            self.filter_dictionary = self.treedata.structure.records_foreign_keys 

        # Configuração dos nomes no Combobox 2.
        self.combobox2["values"] = list(self.filter_dictionary.keys())
        
        # Limpa a seleção atual do Combobox 2.
        self.combobox2.set("")
        

    def onclick_button(self):

        # Valores dos Combobox.
        value1 = self.combobox1.get()
        value2 = self.combobox2.get()

        # Caso algum esteja vazio, não fazer nada.
        if "" in (value1, value2):
            
            return None

        # Busca de registros dentro do filtro.
        for record in self.filter_dictionary[value2]:

            # Salva o registro no controle.
            self.result.records.append(record)

        # Fecha a janela.
        self.window.destroy()
                            

    def render(self):

        # Label Frame.
        label_frame = LabelFrame(self.window, text="Filtro / Nome", padx=10, pady=10)
        label_frame.grid(row=0, column=0, columnspan=2, padx=10, pady=10)

        # Filtros e Nomes.
        self.combobox1 = ttk.Combobox(label_frame, width=32, state="readonly")
        self.combobox2 = ttk.Combobox(label_frame, width=32, state="readonly")

        self.combobox1["values"] = ("Rótulos",  "Registros", "Chaves Estrangeiras")
        self.combobox2["values"] = None
        
        self.combobox1.bind("<<ComboboxSelected>>", self.onchange_combobox1)
        self.combobox2.bind("<<ComboboxSelected>>", None)

        self.combobox1.pack()
        self.combobox2.pack(pady=(15,0))
        
        self.combobox1.current()
        self.combobox2.current()

        # Botão de Execução e Cancelamento.
        button1 = Button(self.window, text="CANCELAR", borderwidth=2, relief="groove", width=15, height=1, background="#EEE", command=self.window.destroy)
        button2 = Button(self.window, text="EXECUTAR", borderwidth=2, relief="groove", width=15, height=1, foreground="white", background="DodgerBlue3", command=self.onclick_button)

        button2.grid(row=2, column=1, pady=10, sticky=W, padx=0)
        button1.grid(row=2, column=0, pady=10, sticky=W, padx=(10,0))


