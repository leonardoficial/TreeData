#   Tree Data
#   Versão 1.0.0.0 (Beta)
#   Leonardo Amaral de Souza
#   Rio de Janeiro, 12/09/1997

import csv, datetime, json, os

from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox

from treedata import TreeData

class SelectTable():

    def __init__(self, top_window, treedata, result):

        # Cria subjanela da aplicação principal.        
        window = Toplevel(top_window)

        # Dados princpais da janela.
        self.window = window
        self.window.title('Selecão')
        self.window.geometry("260x130")
        self.window.resizable(False, False)

        # Tree Data.
        self.treedata = treedata
        
        # Resultado da janela.
        self.result = result

        # Configuração das categorias no Combobox 1.
        self.tables = self.treedata.structure.link.tables()

        # Renderiza a janela.
        self.render()

        # Atalhos do teclado.
        self.window.bind("<Return>", lambda event: self.onclick_button() )
        self.window.bind("<Escape>", lambda event: self.window.destroy() )

        # A jnela principal deve aguardar o resultado da subjanela.
        self.window.grab_set()
        self.window.focus_force()
        top_window.wait_window(window)


    def onclick_button(self):
        
        # Valores dos Combobox.
        value1 = self.combobox1.get()

        # Caso algum esteja vazio, não fazer nada.
        if value1 == "":
            
            return None

        # Caminho completo do script a ser executado.
        self.result.table = value1

        # Solicita a renderização.
        self.result.restart_gui = True
        
        # Fecha a janela.
        self.window.destroy()
                            

    def render(self):
        

        # Label Frame.
        label_frame = LabelFrame(self.window, text="Tabelas", padx=10, pady=10)
        label_frame.grid(row=0, column=0, columnspan=2, padx=10, pady=10)

        # Tabelas.
        self.combobox1 = ttk.Combobox(label_frame, width=32, state="readonly")
        
        self.combobox1["values"] = self.tables

        self.combobox1.pack()

        # Botão de Execução e Cancelamento.
        button1 = Button(self.window, text="CANCELAR", borderwidth=2, relief="groove", width=15, height=1, background="#EEE", command=self.window.destroy)
        button2 = Button(self.window, text="EXECUTAR", borderwidth=2, relief="groove", width=15, height=1, foreground="white", background="DodgerBlue3", command=self.onclick_button)

        button2.grid(row=2, column=1, pady=10, sticky=W, padx=0)
        button1.grid(row=2, column=0, pady=10, sticky=W, padx=(10,0))



