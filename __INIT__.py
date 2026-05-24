from treedata.app import TreeData
from treedata.view.interface import TreeView

# Sistema de logging configurado.
TreeData.logger = TreeData.configure_logger()

# Carrega o arquivo de configurações.
TreeData.settings =  TreeData.configure()