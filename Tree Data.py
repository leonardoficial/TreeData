###############################################################################
#                                                                             #
#   Tree Data Manager                                                         #
#   Versão 1.0.0.0 (Beta)                                                     #
#   Leonardo Amaral de Souza                                                  #
#   Rio de Janeiro, 12/09/1997                                                #
#                                                                             #
###############################################################################


# Bibliotecas padrões para serviço.
import sys

# Bibliotecas padrões para interfaces gráficas.
from tkinter import messagebox

# Bibliotecas próprias para o projeto.
from treedata import TreeData

# Bibliotecas próprias para interfaces gráficas.
from treedata.view.interface import TreeView


# Caso executado com argumentos.
if len(sys.argv) > 1:

    try:
        # Caminho completo do arquivo.
        file_path = sys.argv[1]

        # Objeto TreeData.
        treedata = TreeData(file_path)

        # Verifica se o arquivo está apto para uso.
        if not treedata.status:

            # Cancelar importação.
            raise Exception

        # Objeto da interface gráfica.
        interface = TreeView()

        # Abre a interface gráfica principal.
        interface.open(treedata)

    except:
        
        # Mensagem para suporte.
        messagebox.showwarning(title="Aviso!", message="Importação cancelada!")

# Caso executado diretamente.
else:

    try:

        # Objeto da interface gráfica.
        interface = TreeView()

        # Abre a interface gráfica principal.
        interface.open()
        
    except:

        print("ERRO")
        
        pass
