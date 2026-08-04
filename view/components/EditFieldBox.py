#   Tree Data
#   Versão 1.0.0.0 (Beta)
#   Leonardo Amaral de Souza
#   Rio de Janeiro, 12/09/1997

import ast

from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox

from treedata.model import Bases
from treedata.model.Field  import FieldLayout


class EditFieldBox():

    def __init__(self, top_window, field, result, settings={}):

        # Cria subjanela da aplicação principal.        
        window = Toplevel(top_window)

        # Dados princpais da janela.
        self.window = window
        self.window.title('Editar Campo')
        self.window.geometry("450x275")
        self.window.resizable(False, False)

        # Tree Field.
        self.field = field
        
        # Resultado da janela.
        self.result = result

        # Configurações da janela.
        self.settings = settings

        # Inicializa a aplicação.
        self.initialize()

        # A jnela principal deve aguardar o resultado da subjanela.
        self.window.grab_set()
        self.window.focus_force()
        top_window.wait_window(window)

        return None


    def initialize(self):

        # Renderiza a janela.
        self.render()

        # Mapeia as teclas do teclado aos comandos.
        self.bind_shortcuts()

        # Verifica possibilidade de conversão dos dados.
        #if not isinstance(self.field, FieldLayout):

            # Desabilita a conversão dos dados.
            #self.checkbox_conversion.set(0)

        # Invoca o reconfigurador.
        self.toggle_conversion()

        return None


    def convert(self, value):

        # Remove espaços em branco do texto.
        value = value.replace(" ", "").rstrip()

        # Vetor de códigos criado.
        vector = list(value)

        # Converte o vetor de códigos para amostra.
        converted_value = Bases.convert_base(self.field.base, vector, parameters=self.field.parameters.rules, type1=self.field.type, reverse=False)

        return converted_value


    def onclick_button_convert(self):

        # Verifica se está habilitada a conversão.
        if self.checkbox_conversion.get() == 0:

            return None

        # Valor para o campo.
        value = self.entry_value.get("1.0", END)

        # Converte o valor.
        converted_value = self.convert(value)
        
        # Seta o valor convertido na entrada.
        self.entry_converted_value.delete("1.0", END)
        self.entry_converted_value.insert("1.0", converted_value)

        return converted_value


    def onclick_button_apply(self, event=None):
        
        # Valor para o campo.
        value = self.entry_value.get("1.0", END)

        # Remove as quebras de linhas.
        value = value.rstrip()

        # Seta o valor desejado no campo.
        self.field.set(value)

        # Informa a aplicação para atualizar a interface.
        self.result.update_gui = True
        
        # Encerra a janela.
        self.window.destroy()

        return None


    def render(self):

        # Valor original do campo.
        field_value = self.field.get(raw=True)

        # Valor convertido do campo.
        converted_value = self.field.value

        # Caso especificado valor padrão para a entrada.
        if self.settings.get("default", False):

            # Altera o valor padrão do campo
            field_value = self.settings.get("default")

            # Altera o valor padrão da conversão.
            converted_value = field_value
        
        # Renderiza o menu da janela.
        self.render_menu()
    
        # Caixa de rôtulo principal.
        label_frame = LabelFrame(self.window, text="Valor / Conversão", padx=10, pady=10)

        # Renderiza a caixa de rótulo.
        label_frame.grid(row=0, column=0, padx=10, pady=5, columnspan=3)

        # Entrada para mostrar os dados convertidos.
        self.entry_value = Text(label_frame, height=4, width=50, relief="groove", borderwidth=2)

        # Renderiza a entrada na interface.
        self.entry_value.grid(row=0, column=0, columnspan=2, pady=(0,10))

        # Esvazia a entrada.
        self.entry_value.delete("1.0", END)
        
        # Seta valor para a entrada.
        self.entry_value.insert("1.0", field_value)

        # Entrada para o valor final.
        self.entry_converted_value = Text(label_frame, height=4, width=50, relief="groove", borderwidth=2)

        # Renderiza a entrada na interface.
        self.entry_converted_value.grid(row=2, column=0, columnspan=2)

        # Esvazia a entrada.
        self.entry_converted_value.delete("1.0", END)

        # Seta valor para a entrada.
        self.entry_converted_value.insert("1.0", converted_value)
        
        # O valor convertido é alterado exclusivamente pelo sistema.
        self.entry_converted_value.bind("<Key>", lambda e: "break")
        
        # Variável para habilitar o buffer.
        self.enable_buffer = IntVar()

        # Caixa de seleção.
        checkbox_buffer = Checkbutton(self.window, text='Habilitar buffer', command=None, variable=self.enable_buffer, onvalue=1, offvalue=0)

        # Renderiza a caixa de seleção na interface.
        checkbox_buffer.grid(row=1, column=0, pady=0, sticky=W, padx=(5,0))

        # Variável para habilitar a conversão.
        self.checkbox_conversion = IntVar()

        # "Habilitada por padrão."
        self.checkbox_conversion.set(1)
        
        # Caixa de seleção.
        checkbox_conversion = Checkbutton(self.window, text='Habilitar conversão', command=self.toggle_conversion, variable=self.checkbox_conversion, onvalue=1, offvalue=0)

        # Renderiza a caixa de seleção na interface.
        checkbox_conversion.grid(row=1, column=1, columnspan=2, pady=0, sticky=E, padx=(0,50))

        # Botões.
        self.button1 = Button(self.window, text="CANCELAR",  command=self.window.destroy,         borderwidth=2, relief="groove", width=10, height=1, background="#EEE")
        self.button2 = Button(self.window, text="CONVERTER", command=self.onclick_button_convert, borderwidth=2, relief="groove", width=10, height=1, background="lightgray")
        self.button3 = Button(self.window, text="APLICAR",   command=self.onclick_button_apply,   borderwidth=2, relief="groove", width=10, height=1, foreground="white", background="DodgerBlue3")

        # Renderiza os botões na interface.
        self.button1.grid(row=2, column=0, pady=10, sticky=W, padx=(10,0))
        self.button2.grid(row=2, column=1, pady=10, sticky=E, padx=(150,0))
        self.button3.grid(row=2, column=2, pady=10, sticky=E, padx=(0,10))

        return None


    def render_menu(self):
        
        # Barra do menu.
        menubar = Menu(self.window)

        # Menus
        main_menu = Menu(menubar, tearoff=0)
        size_menu = Menu(menubar, tearoff=0)

        # Adiciona comandos dos menus.
        main_menu.add_command(label='Regras',     command=None)
        main_menu.add_command(label='Dicionário', command=None)

        size_menu.add_command(label='Grande',  command=lambda: self.do_resize('450x275', 4, 50))
        size_menu.add_command(label='Normal',  command=None)
        size_menu.add_command(label='Pequena', command=lambda: self.do_resize('260x250', 3, 26))

        # Adiciona os menus na barra.
        menubar.add_cascade(menu=main_menu, label="Menu")
        menubar.add_cascade(menu=size_menu, label="Janela")

        # Adiciona comando da barra de menu.
        menubar.add_command(label='Tarefa', command=None)
        
        # TAGGED-IMPROVE.
        menubar.entryconfig('Menu', state=DISABLED)
        menubar.entryconfig('Janela', state=DISABLED)
        menubar.entryconfig('Tarefa', state=DISABLED)
        
        # Configura o menu.
        self.window.config(menu=menubar)

        return None


    def do_resize(self, window_size, entry_height, entry_width):

        # Modifica o tamanho da janela.
        self.window.geometry(window_size)

        # Modifica altura e largura dos elementos de entrada.
        self.entry_value.config(height=entry_height, width=entry_width)
        self.entry_converted_value.config(height=entry_height, width=entry_width)

        return None


    def bind_shortcuts(self):

        # Aplica alterações de valor ao campo.
        self.window.bind("<Return>", self.onclick_button_apply)

        # Encerra a janela.
        self.window.bind("<Escape>", lambda event: self.window.destroy() )

        return None


    def toggle_conversion(self):

        print('AAAAAAAAAA')

        # Configuração padrão da entrada de conversão.
        this_state = NORMAL
        background = 'white'
        
        # Desabilitar a caixa de seleção.
        if self.checkbox_conversion.get() == 0:

            # Configuração para entrada desabilitada.
            edit_state = DISABLED
            background = '#EBEBE4'

            # Esvazia a entrada.
            self.entry_converted_value.delete("1.0", END)

        # Reconfigura a entrada.
        self.entry_converted_value.config(state=this_state, background=background)

        # Reconfigura o botão.
        self.button2.config(state=this_state)

        return None



class EditFieldList():

    def __init__(self, top_window, field, result, settings={}):

        # Cria subjanela da aplicação principal.        
        window = Toplevel(top_window)

        # Dados princpais da janela.
        self.window = window
        self.window.title('Editar Campo (LISTA)')
        self.window.geometry("450x360")
        self.window.resizable(False, False)

        # Tree Field.
        self.field = field
        
        # Resultado da janela.
        self.result = result

        # Configurações da janela.
        self.settings = settings

        # Controle do indice ativo.
        self.active_index = None

        # Inicializa a aplicação.
        self.initialize()

        # A jnela principal deve aguardar o resultado da subjanela.
        self.window.grab_set()
        self.window.focus_force()
        top_window.wait_window(window)

        return None


    def initialize(self):

        # Renderiza a janela.
        self.render()

        # Mapeia as teclas do teclado aos comandos.
        self.bind_shortcuts()

        return None


    def onclick_button_apply(self, event=None):
        
        # Novos valores para o campo.
        values = list(self.list_values.get(0, END))

        # Conversão dos valores
        values = str(values)

        # TAGGED-IMPROVA
        values = values.replace("'", "")

        print(values)

        # Seta o valor desejado no campo.
        self.field.set(values)

        # Informa a aplicação para atualizar a interface.
        self.result.update_gui = True
        
        # Encerra a janela.
        self.window.destroy()

        return None


    def render(self):

        # Valor original do campo.
        field_value = self.field.get(raw=True)

        # Valor convertido do campo.
        converted_value = self.field.value

        # Caso especificado valor padrão para a entrada.
        if self.settings.get("default", False):

            # Altera o valor padrão do campo
            field_value = self.settings.get("default")

            # Altera o valor padrão da conversão.
            converted_value = field_value
        
        # Renderiza o menu da janela.
        self.render_menu()


    
        # Caixa de rôtulo principal.
        label_frame = LabelFrame(self.window, text="> <", padx=10, pady=10, borderwidth=2)

        # Renderiza a caixa de rôtulo.
        label_frame.grid(row=0, column=0, padx=(6,0), pady=5)

        # Entrada para mostrar os dados convertidos.
        self.entry_value = Text(label_frame, height=1, width=20, relief="groove", borderwidth=2)

        # Renderiza a entrada na interface.
        self.entry_value.grid(row=0, column=0, pady=(0,10), ipadx=5, columnspan=3)

        # Esvazia a entrada.
        self.entry_value.delete("1.0", END)
        
        # Seta valor para a entrada.
        self.entry_value.insert("1.0", "")

        # Botões.
        self.button_set  = Button(label_frame, text="=", command=self.onclick_set, borderwidth=2, relief="groove", width=8, height=1, background="lightgray")
        self.button_add  = Button(label_frame, text="+", command=self.onclick_add, borderwidth=2, relief="groove", width=3, height=1, background="lightgray")
        self.button_del = Button(label_frame, text="-",  command=self.onclick_del, borderwidth=2, relief="groove", width=3, height=1, background="#EEE")

        self.button_import = Button(label_frame, text="IMPORTAR", state=DISABLED, command=None, borderwidth=2, relief="groove", width=8, height=1, background="lightgray")
        self.button_empty  = Button(label_frame, text="ESVAZIAR", state=DISABLED, command=None, borderwidth=2, relief="groove", width=8, height=1, background="#EEE")

        # Renderiza os botões na interface.
        self.button_set.grid(row=1, column=0, pady=5, sticky=W)
        self.button_add.grid(row=1, column=1, pady=5, sticky=E, padx=(38,0))
        self.button_del.grid(row=1, column=2, pady=5, sticky=E)
        
        self.button_import.grid(row=2, column=0, pady=(108,0), sticky=W)
        self.button_empty .grid(row=2, column=1, pady=(108,0), sticky=E, columnspan=2)
        



        # Caixa de rôtulo principal.
        label_frame = LabelFrame(self.window, text="> <", padx=10, pady=10)

        # Renderiza a caixa de rôtulo.
        label_frame.grid(row=0, column=1, padx=5, pady=5)

        # Entrada para o valor final.
        self.list_values = Listbox(label_frame, height=10, width=25, relief="groove", borderwidth=2)

        # Renderiza a entrada na interface.
        self.list_values.grid(row=0, column=0, ipadx=15)

        # Seta valor para a entrada.
        for index, item in enumerate(self.field.original):

            if type(item) is str: item = "'" + item + "'"
            
            self.list_values.insert(index, item)
        
        # 
        self.list_values.bind("<<ListboxSelect>>", self.onclick_listbox)

        self.button_sort = Button(label_frame, text="ORDERNAR", command=None, borderwidth=2, relief="groove", width=25, height=1, background="lightgray")
        self.button_sort.grid(row=1, column=0, pady=(10,0))



        # Caixa de rôtulo principal.
        label_frame = LabelFrame(self.window, text="> <", padx=10, pady=10)

        # Renderiza a caixa de rôtulo.
        label_frame.grid(row=1, column=0, padx=10, pady=4, columnspan=2)
        
        # Variável para habilitar o buffer.
        self.enable_buffer = IntVar()

        # Caixa de seleção.
        checkbox_buffer = Checkbutton(label_frame, text='Habilitar buffer', command=None, variable=self.enable_buffer, onvalue=1, offvalue=0)

        # Renderiza a caixa de seleção na interface.
        checkbox_buffer.grid(row=0, column=0, pady=(0,5), sticky=W, padx=0)

        # Botões.
        self.button1 = Button(label_frame, text="CANCELAR",  command=self.window.destroy,         borderwidth=2, relief="groove", width=10, height=1, background="#EEE")
        self.button2 = Button(label_frame, text="VALIDAR", command=None, borderwidth=2, relief="groove", width=10, height=1, background="lightgray")
        self.button3 = Button(label_frame, text="APLICAR",   command=self.onclick_button_apply,   borderwidth=2, relief="groove", width=10, height=1, foreground="white", background="DodgerBlue3")

        # Renderiza os botões na interface.
        self.button1.grid(row=1, column=0, pady=0, sticky=W, padx=(3,150))
        self.button2.grid(row=1, column=1, pady=0, sticky=E, padx=(0,10))
        self.button3.grid(row=1, column=2, pady=0, sticky=E, padx=(0,0))

        return None


    def render_menu(self):
        
        # Barra do menu.
        menubar = Menu(self.window)

        # Menus
        main_menu = Menu(menubar, tearoff=0)
        size_menu = Menu(menubar, tearoff=0)

        # Adiciona comandos dos menus.
        main_menu.add_command(label='Regras',     command=None)
        main_menu.add_command(label='Dicionário', command=None)

        size_menu.add_command(label='Grande',  command=lambda: self.do_resize('450x275', 4, 50))
        size_menu.add_command(label='Normal',  command=None)
        size_menu.add_command(label='Pequena', command=lambda: self.do_resize('260x250', 3, 26))

        # Adiciona os menus na barra.
        menubar.add_cascade(menu=main_menu, label="Menu")
        menubar.add_cascade(menu=size_menu, label="Janela")

        # Adiciona comando da barra de menu.
        menubar.add_command(label='Tarefa', command=None)
        
        # TAGGED-IMPROVE.
        menubar.entryconfig('Menu', state=DISABLED)
        menubar.entryconfig('Janela', state=DISABLED)
        menubar.entryconfig('Tarefa', state=DISABLED)
        
        # Configura o menu.
        self.window.config(menu=menubar)

        return None


    def onclick_listbox(self, event):

        # Indice selecionado.
        index = event.widget.curselection()

        if not index: return None

        # Valor do indice.
        value = event.widget.get(index)

        if value is str:

            # Remove as quebras de linhas.
            value = value.rstrip()
        
        # Esvazia a entrada.
        self.entry_value.delete("1.0", END)
        
        # Seta valor para a entrada.
        self.entry_value.insert("1.0", value)

        # Atualiza o controle de indice ativo.
        self.active_index = index


    def onclick_set(self):

        # Verifica o indice ativo.
        if not self.active_index: return None

        # Novo valor do item.
        new_value = self.entry_value.get("1.0", END)

        # Remove as quebras de linhas.
        new_value = new_value.rstrip()

        # Deleta o item antigo da lista de valores.
        self.list_values.delete(self.active_index)

        # Adiciona o item novo.
        self.list_values.insert(self.active_index, new_value)


    def onclick_del(self):

        # Verifica o indice ativo.
        if not self.active_index: return None

        # Deleta o item antigo da lista de valores.
        self.list_values.delete(self.active_index)

        # Esvazia a entrada.
        self.entry_value.delete("1.0", END)

        # Remove o controle de indice ativo.
        self.active_index = None

        # Remove o destadaque da seleção.
        self.list_values.selection_clear(0, END)


    def onclick_add(self):

        # Novo valor do item.
        new_value = self.entry_value.get("1.0", END)

        # Remove as quebras de linhas.
        new_value = new_value.rstrip()

        if not len(new_value): return None

        # Converte para o valor apropriado.
        new_value = ast.literal_eval(new_value)

        # Adiciona o item novo.
        self.list_values.insert(END, new_value)

        # Atualiza o controle de indice ativo.
        self.active_index = self.list_values.size() - 1
        

    def do_resize(self, window_size, entry_height, entry_width):

        # Modifica o tamanho da janela.
        self.window.geometry(window_size)

        # Modifica altura e largura dos elementos de entrada.
        self.entry_value.config(height=entry_height, width=entry_width)
        self.entry_converted_value.config(height=entry_height, width=entry_width)

        return None


    def bind_shortcuts(self):

        # Aplica alterações de valor ao campo.
        self.window.bind("<Return>", self.onclick_button_apply)

        # Encerra a janela.
        self.window.bind("<Escape>", lambda event: self.window.destroy() )

        return None


if __name__ == "__main__":

    class Field:

        def __init__(self):

            self.original = ["FOO", "BAR", "NER"]
            self.value = '["FOO", "BAR", "NER"]'


        def get(self, raw=False):

            return self.value


    window = Tk()
    field = Field()


    EditFieldList(window, field, {}, {})


    window.mainloop()




