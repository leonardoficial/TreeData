#   Tree Data
#   Versão 1.0.0.0 (Beta)
#   Leonardo Amaral de Souza
#   Rio de Janeiro, 12/09/1997


import csv
import datetime
import json
import os

from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox

from treedata.view.builtin.WindowManager import StandardResult


class TaskSelectionBox():


    def __init__(self, top_window, treedata, result, settings={}):

        # Cria subjanela da aplicação principal.        
        window = Toplevel(top_window)

        # Dados princpais da janela.
        self.window = window
        self.window.title('Executar Tarefa')
        self.window.geometry("260x190")
        self.window.resizable(False, False)

        # Tree Data.
        self.treedata = treedata
        
        # Resultado da janela.
        self.result = result

        # Caminho completo da tarefa.
        self.result.task_path = None

        # Bandeira para indicar cancelamento da tarefa.
        self.result.cancel = False

        # Configuração das váriaveis de retorno.
        self.result.set_boolean('safe-mode', overwrite=False)
        self.result.set_boolean('dont-close-window', overwrite=False)

        # Configuração.
        self.settings = settings

        # Configuração das categorias na caixa de seleção.
        self.tasks_categories = os.walk(self.result.path)
        self.tasks_categories = next(self.tasks_categories)[1]
        self.tasks_categories = sorted(self.tasks_categories, key=str.lower)

        # Renderiza a janela.
        self.render()

        # Mapeia os eventos ao teclado.
        self.window.bind("<Return>",    lambda event: self.onclick_execute() )
        self.window.bind("<Escape>",    lambda event: self.onclick_cancel() )
        self.window.bind("<Control-d>", lambda event: self.configure_default() )

        # Protocolo de encerramento da janela.
        self.window.protocol("WM_DELETE_WINDOW", self.destroy)
        
        # A janela principal deve aguardar o resultado da subjanela.
        self.window.grab_set()
        self.window.focus_force()
        top_window.wait_window(window)


    def destroy(self):

        # Atualiza a bandeira de cancelamento.
        self.result.cancel = True

        # Destrói a janela renderizada.
        self.window.destroy()


    def configure_default(self):

        # Tarefa padrão informada.
        default = self.settings.get('run-on', {}).get('default', None)

        if not default:

            return None

        # Configuração da caixa de seleção da categoria.
        self.combobox_category.set( default.get('folder') )

        # Configuração da caixa de seleção do script.
        self.combobox_script.set( default.get('name') )
        

    def onchange_combobox_category(self, event):
        
        # Valor da categoria selecionada.
        value = self.combobox_category.get()

        # Caso esteja vazio, não fazer nada.
        if not value:
            
            return None

        # Caminho completo do diretório das tarefas.
        path_selection = os.path.join(self.result.path, value)

        # Limpa a seleção atual da caixa de seleção de scripts.
        self.combobox_script.set("")

        # Configuração dos scripts no Combobox 2.
        tasks_scripts = [ file for file in os.listdir( path_selection ) if os.path.isfile( os.path.join(path_selection, file) ) ]
        tasks_scripts = sorted(tasks_scripts, key=str.lower)

        # Configura scripts disponíveis na caixa de seleção.
        self.combobox_script["values"] = tasks_scripts


    def onclick_execute(self):
        
        # Categoria.
        category = self.combobox_category.get()

        # Tarefa.
        script = self.combobox_script.get()

        # Caso algum esteja vazio, não fazer nada.
        if "" in (category, script):
            
            return None

        # Caminho completo do script a ser executado.
        self.result.task_path = os.path.join(self.result.path, category, script)

        # Executa o callback.
        self.settings.get('callback', lambda x: x)(self.result)

        # Fecha a janela.
        if not self.result.get('dont-close-window').get():
            
            self.window.destroy()


    def onclick_cancel(self):

        # Bandeira para indicar cancelamento da tarefa.
        self.result.cancel = True

        # Fecha a janela.
        self.window.destroy()
                            

    def render(self):

        # Renderização do menu.
        self.render_menu()

        # Caixa de rótulo.
        label_frame = LabelFrame(self.window, text="Categoria / Tarefa", padx=10, pady=10)
        label_frame.grid(row=0, column=0, columnspan=2, padx=10, pady=10)

        # Caixas de seleção das categorias e tarefas.
        self.combobox_category = ttk.Combobox(label_frame, width=32, state="readonly")
        self.combobox_script = ttk.Combobox(label_frame, width=32, state="readonly")

        # Configuração dos valores.
        self.combobox_category["values"] = self.tasks_categories
        self.combobox_script["values"] = None

        # Configuração dos eventos.
        self.combobox_category.bind("<<ComboboxSelected>>", self.onchange_combobox_category)
        self.combobox_script.bind("<<ComboboxSelected>>", None)

        # Renderização dos elementos.
        self.combobox_category.pack()
        self.combobox_script.pack(pady=(15,0))

        # Configuração inicial.
        self.combobox_category.current()
        self.combobox_script.current()

        # Opções.
        checkbox1 = Checkbutton(self.window, text="Modo Seguro", variable=self.result.get('safe-mode'),    onvalue=1, offvalue=0)
        checkbox2 = Checkbutton(self.window, text="Não Fechar",  variable=self.result.get('dont-close-window'), onvalue=1, offvalue=0)
        
        checkbox1.grid(row=1, column=0, sticky=W, padx=(10,5))
        checkbox2.grid(row=1, column=1, sticky=W)

        # Desabilitado até a implementação.
        checkbox1.config(state="disabled")

        # Botões de execução e cancelamento.
        button1 = Button(self.window, text="CANCELAR", command=self.onclick_cancel,  borderwidth=2, relief="groove", width=15, height=1, background="#EEE")
        button2 = Button(self.window, text="EXECUTAR", command=self.onclick_execute, borderwidth=2, relief="groove", width=15, height=1, background="DodgerBlue3", foreground="white")

        # Renderização dos elementos.
        button2.grid(row=2, column=1, pady=10, sticky=W, padx=0)
        button1.grid(row=2, column=0, pady=10, sticky=W, padx=(10,0))


    def render_menu(self):
        
        # Menu.
        menubar = Menu(self.window)
        self.window.config(menu=menubar)
        
        # Configuração dos menus acoplados.
        menu = Menu(menubar, tearoff=0)
        
        menu.add_command(label="Fila",               command=None, state='disabled')
        menu.add_command(label="Tarefa Padrão",      command=self.configure_default)
        menu.add_command(label="Execução ao Abrir",  command=None, state='disabled')
        menu.add_command(label="Execução ao Fechar", command=None, state='disabled')
        
        menubar.add_cascade(label="Menu", menu=menu)


if __name__ == "__main__":

    # Classe mock.
    class Mock:

        def __init__(self):

            self.original = ["FOO", "BAR", "NER"]
            self.value = '["FOO", "BAR", "NER"]'


        def get(self, raw=False):

            return self.value


    # Janela principal de teste.
    window = Tk()

    # Esconde a janela principal.
    window.withdraw()

    # Objeto mock.
    mock = Mock()

    # Resultado padrão.
    result = StandardResult()

    # Diretório do caminho das tarefas
    result.path = r"C:\DEV\Tree Data (HML)\treedata\controller\tasks\EKS.TEST.MOCK.TASK"
    
    # Inicializa renderização do componente.
    TaskSelectionBox(window, mock, result, {})


