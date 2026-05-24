
#   Issabox Services
#   Versão 1.0.0.0 [Demo]
#   Leonardo Amaral de Souza
#   Rio de Janeiro, 01/01/2020


import collections.abc


class FunctionService:

    def __init__(self):
        
        pass

    @staticmethod
    def update(destiny, source):

        for key, value in source.items():

            if isinstance(value, collections.abc.Mapping):

                destiny[key] = FunctionService.update(destiny.get(key, {}), value)

            else:
                            
                destiny[key] = value

        return destiny
