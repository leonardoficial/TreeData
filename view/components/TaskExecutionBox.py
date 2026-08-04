#   Tree Data
#   Versão 1.0.0.0 (Beta)
#   Leonardo Amaral de Souza
#   Rio de Janeiro, 12/09/1997


import ast, time

from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox

from treedata.view.builtin.WindowManager import StandardResult

from issabox.graphics.ProgressbarFactory import ProgressbarFactory

class TaskExecutionBox:

    def __init__(self, top_window, task, result, settings={}):

        # Cria subjanela da aplicação principal.        
        window = Toplevel(top_window)

        # Dados princpais da janela.
        self.window = window
        self.window.title('Execução da Tarefa')
        self.window.geometry("450x250")
        self.window.resizable(False, False)

        # Objeto administrável da tarefa.
        self.task = task

        # Barra de progresso.
        self.Progressbar = None

        # Total do progresso.
        self.total_progress = None
        
        # Resultado da janela.
        self.result = result

        # Bandeira para indicar cancelamento da tarefa.
        self.result.cancel = False

        # Configurações da janela.
        self.settings = settings

        # Protocolo de encerramento da janela.
        self.window.protocol("WM_DELETE_WINDOW", self.destroy)

        # A jnela principal deve aguardar o resultado da subjanela.
        self.window.grab_set()
        self.window.focus_force()


    def open(self, settings):

        # Total do progresso.
        self.total_progress = settings.get('total_progress', 100)

        # Renderiza a janela.
        self.render()

        # Mapeia as teclas do teclado aos comandos.
        self.bind_shortcuts()

        return None


    def close(self):

        # Destrói a janela renderizada.
        self.window.destroy()


    def destroy(self):

        # Atualiza a bandeira de cancelamento.
        self.result.cancel = True

        # Destrói a janela renderizada.
        self.close()


    def render(self):

        # Console de entrada e saída.
        self.render_console()

        # Barra de progresso da execução.
        self.render_progress()

        # Butões de ação.
        self.render_buttons()

        return None


    def render_console(self):

        # Texto para o console.
        console_text = "Executando a tarefa..."
    
        # Caixa de rôtulo principal.
        label_frame = LabelFrame(self.window, text=" Console ", padx=10, pady=10)

        # Renderiza a caixa de rótulo.
        label_frame.grid(row=0, column=0, padx=10, pady=5, columnspan=3)

        # Entrada para mostrar textos do console.
        self.entry_console = Text(label_frame, height=4, width=50, relief="groove", borderwidth=2)

        # Renderiza a entrada na interface.
        self.entry_console.grid(row=0, column=0, columnspan=2, pady=(0,10))

        # Atualiza o texto do console.
        self.update_console(console_text)

        return None


    def render_progress(self):

        # Caixa de rôtulo principal.
        label_frame = LabelFrame(self.window, text=" Progresso ", padx=10, pady=10)

        # Renderiza a caixa de rótulo.
        label_frame.grid(row=1, column=0, padx=10, pady=5, columnspan=3)

        # Barra de progresso.
        self.Progressbar = ProgressbarFactory(label_frame,
            packing={
                'fill':   X,
                'anchor': S,
                'expand': True
            },
            settings={
                'orient': 'horizontal',
                'mode':   'determinate',
                'length': 406
            }
        )

        # Abre a barra de progresso.
        self.Progressbar.start()

        return None


    def render_buttons(self):

        # Botões.
        self.button1 = Button(self.window, text="CANCELAR",  command=self.onclick_button_cancel,  borderwidth=2, relief="groove", width=10, height=1, background="#EEE")
        self.button3 = Button(self.window, text="APLICAR",   command=self.onclick_button_apply,   borderwidth=2, relief="groove", width=10, height=1, foreground="white", background="DodgerBlue3")

        # Renderiza os botões na interface.
        self.button1.grid(row=2, column=0, pady=10, sticky=W, padx=(10,0))
        self.button3.grid(row=2, column=2, pady=10, sticky=E, padx=(0,10))

        return None


    def onclick_button_apply(self, event=None):
        
        # Valor para o campo.
        value = self.entry_value.get("1.0", END)

        # Remove as quebras de linhas.
        value = value.rstrip()

        # Seta o valor desejado no campo.
        self.task.set(value)

        # Informa a aplicação para atualizar a interface.
        self.result.update_gui = True
        
        # Encerra a janela.
        self.window.destroy()

        return None


    def onclick_button_cancel(self, event=None):

        # Bandeira para indicar cancelamento da tarefa.
        self.result.cancel = True
        
        # Mensagem de suporte.
        messagebox.showinfo(title="Aviso!", message="A execução da tarefa foi cancelada!")
        
        # Encerra a janela.
        self.window.destroy()

        return None


    def progress(self, value):
        
        # Informa o progresso da execução.
        self.Progressbar.set({
            "total": self.total_progress,
            "value": value
        })


    def finish(self):

        # Completa a barra de tarefas.
        self.progress(self.total_progress)

        # Atualiza o console.
        self.update_console('Tarefa concluída!')


    def update_console(self, text):

        # Esvazia a entrada.
        self.entry_console.delete("1.0", END)
        
        # Seta valor para a entrada.
        self.entry_console.insert("1.0", text)

        return None


    def bind_shortcuts(self):

        # Aplica alterações de valor ao campo.
        self.window.bind("<Return>", self.onclick_button_apply)

        # Encerra a janela.
        self.window.bind("<Escape>", lambda event: self.window.destroy() )

        return None



if __name__ == "__main__":

    # Classe mock.
    class Task:

        def __init__(self):

            self.console = ''


        def get(self, raw=False):

            return self.value


    # Janela principal de teste.
    window = Tk()
    
    # Esconde a janela principal.
    window.withdraw()
    
    # Objeto mock.
    task = Task()

    # Resultado padrão.
    result = StandardResult()

    # Inicializa renderização do componente.
    TaskExecutionBox(window, task, {}, {
        "total_progress": 100
    })



