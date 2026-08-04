
#   Issabox Services
#   Versão 1.0.0.0 [Demo]
#   Leonardo Amaral de Souza
#   Rio de Janeiro, 01/01/2020


import re

class ExpressionService:

    def __init__(self):
        pass

    @classmethod
    def expressions(cls, text, interpret=True):

        # Precisa ser do tipo string.
        text = str(text)

        # EXPRESSÕES ENCONTRADAS NO TEXTO
        expressions = re.findall(r"(\{\{.*?\}\})", text)
        # REQUISIÇÕES INTERPRETADAS DAS EXPRESSÕES
        requisitons = []

        # CASO DESEJE INTERPRETAR EXPRESSÕES
        if interpret == True:

            for expression in expressions:
                #
                requisiton = cls.data(expression)
                requisitons.append(requisiton)

            # RETONAR REQUISIÇÕES
            return requisitons

        # CASO NÃO DESEJE INTERPRETAR, RETORNAR EXPRESSÕES CRUAS
        return expressions

    @classmethod
    def data(cls, expression):

        # PACOTE E SCHEMA REQUISITADO NA EXPRESSÃO
        original = expression
        package  = None
        value    = None

        # REMOVE ESPAÇOS E CHAVETAS DA EXPRESSÃO
        expression = "".join( expression.split() )
        expression = expression.replace( "{", "" )
        expression = expression.replace( "}", "" )

        # CASO NÃO HAJA NENHUM DADO PARA INTERPRETAR
        if len(expression) == 0:
            return None

        # CASO HAJA ATRIBUTOS GLOBAIS NA EXPRESSÃO
        expression = expression.split(":")

        # SE HOUVER MAIS DE DUAS OCORRÊNCIAS, RETORNAR PACKAGE E SCHEMA REQUISITADOS
        if len(expression) >= 2:
            package = expression[0]
            value   = expression[1]
        # CASO CONTRÁRIO, APENAS RETORNAR SCHEMA REQUISITADO.
        else:
            value = expression[0]

        # CONSTROI OBJETO DE RETORNO
        requisition = { "expression": original, "package": package, "value": value }

        return requisition


#expression = "{{SYNDICATE:value}}"
#requisiton = ExpressionService.expressions(expression)

#print(requisiton)
