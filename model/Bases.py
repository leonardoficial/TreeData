import re, locale, sys

from datetime import datetime, timedelta

# CONFIGURAÇÕES UNIVERSAIS
locale.setlocale(locale.LC_ALL, '')

julian_initial = datetime(2002, 12, 31)
epoch_initial  = datetime(1900, 1, 1)

class Bases:

    available_bases = [ "juliancurrency", "original", "decimal", "currency", "ascii", "enum", "datetime", "date", "time", "time_from_seconds", "juliandate", "juliantime", "juliandatetime_teste"]

    @classmethod
    def convert_base(cls, base, value, type1=None, reverse=None, parameters={}):
        
        # Deve ser lista
        if not type(base) is list:
            bases=[base]
        else:
            bases=base

        # Converter o valor para decimal caso necessário.
        conversion = parameters['link']['settings'].get("field", {}).get("conversion", None)

        if conversion == "hexadecimal":
            
            # Vetor a ser convertido
            value = valuecopy = "".join(value)

            # Converte para a base decimal
            value =  int(value, 16)

        base_newvalue=value

        # Função correspondente a base catalogada.
        for base in bases:

            base = base.lower()
            
            # Somente aceitar base catalogada.
            if base not in cls.available_bases:
                return None

            base_function = getattr(cls, base)
            base_newvalue = base_function(base_newvalue, type1, reverse, parameters)

        return base_newvalue

    @staticmethod
    def original(value, type1=None, reverse=False, settings={}):

        return value


    @staticmethod
    def decimal(value, type1=None, reverse=False, settings={}):

        return int(value)

    @staticmethod
    def format_hexadecimal(value, bytes):

        value  = value.zfill(bytes)
        vector = [value[i:i+2] for i in range(0, len(value), 2)]

        return vector


    @classmethod
    def date(cls, value, type1=None, reverse=False, settings={}):

        #print("value:", value)

        # Usar o valor decimal para a operação
        value = cls.decimal(value)

        #print("value decimal:", value)

        # Usar o valor Unix Time para a operação.
        value = datetime.utcfromtimestamp(value)

        #print("value decimal unix", value)

        value = value.strftime("%d/%m/%Y")

        return value

    @classmethod
    def juliandate(cls, value, type1=None, reverse=False, settings={}):

        # Usar o valor decimal para a operação
        value = cls.decimal(value)

        # Usar o valor Unix Time para a operação.
        value = julian_initial + timedelta(days=value)
        value = value.strftime("%d/%m/%Y")

        return value

    @classmethod
    def juliantime(cls, value, type1=None, reverse=False, settings={}):

        # Usar o valor decimal para a operação
        value = cls.decimal(value)

        # Usar o valor Unix Time para a operação.
        value = julian_initial + timedelta(minutes=value)

        value = value.strftime("%H:%M")

        return value

    @classmethod
    def juliandatetime_teste(cls, value, type1=None, reverse=False, settings={}):

        # Usar o valor decimal para a operação
        value = cls.decimal(value)

        # Usar o valor Unix Time para a operação.
        value = julian_initial + timedelta(seconds=value)

        value = value.strftime("%d/%m/%y %H:%M:%S")

        return value


    @classmethod
    def time_from_seconds(cls, value, type1=None, reverse=False, settings={}):

        # Usar o valor decimal para a operação
        value = cls.decimal(value)
        value = julian_initial + timedelta(seconds=value)
        value = value.strftime("%H:%M")

        return value


    @classmethod
    def datetime(cls, value, type1=None, reverse=False, settings={}):

        # Usar o valor decimal para a operação.
        value = cls.decimal(value)

        # Usar o valor Unix Time para a operação.
        value = datetime.utcfromtimestamp(value)
        value = value.strftime("%d/%m/%y %H:%M:%S")

        return value


    @classmethod
    def time(cls, value, type1=None, reverse=False, settings={}):
        #
        # if type1 == "STRING":
        #     value = "".join(value)
        #     value = bytearray.fromhex(value).decode()
        #     print(value)

        # Usar o valor decimal para a operação.

        value = cls.decimal(value)

        # Extrai apenas horas e minutos.
        value = timedelta(seconds=value)
        value = str(value)[2:]

        return value


    @classmethod
    def ascii(cls, value, type1=None, reverse=False, settings={}):

        # Converte a lista hexadecimal para string.
        #value = "".join(value)

        value = cls.decimal(value)

        value = bytearray( value.to_bytes(32, sys.byteorder) )

        value.reverse()

        value = value.decode().strip('\x00')

        return value

    @classmethod
    def enum(cls, value, type1=None, reverse=False, settings={}):

        value = cls.decimal(value)
        value = int(value)

        return value


    @classmethod
    def juliancurrency(cls, value, type1=None, reverse=False, settings={}):

        # Usar o valor decimal para a operação.
        value = cls.decimal(value)

        # Valor monetário para o cálculo.
        value = value - 4096

        # Formatação para caso de duas casas decimais.
        if value > 99:

            value = str(value)

            # Notas e centavos.
            bills = value[:-2]
            coins = value[-2:]

            value = float(bills + "." + coins)

        # Moeda local configurada.
        value = locale.currency(value, grouping=True, symbol=None)

        value = str(value)

        return value


    @classmethod
    def currency(cls, value, type1=None, reverse=False, settings={}):

        # Usar o valor decimal para a operação.
        value = cls.decimal(value)

        # Valor monetário para o cálculo.
        #value = value - 4096

        # Formatação para caso de duas casas decimais.
        if value > 99:

            value = str(value)

            # Notas e centavos.
            bills = value[:-2]
            coins = value[-2:]

            value = float(bills + "." + coins)

        # Moeda local configurada.
        value = locale.currency(value, grouping=True, symbol=None)

        value = str(value)

        return value


    @staticmethod
    def raw_from_currency(value, type1=None, reverse=False, settings={}):

        value = locale.atof(value)

        return value
