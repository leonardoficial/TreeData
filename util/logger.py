import logging

class CustomFormatter(logging.Formatter):

    # Código das cores
    red =       "\x1b[31;20m"
    grey =      "\x1b[38;20m"
    bold_grey = "\x1b[38;1m"
    bold_red =  "\x1b[31;1m"
    yellow =    "\x1b[33;20m"

    # Fina de linha da formatação de cor
    end_of_line = "\x1b[0m"

    # Formatação padrão.
    formatter_string = "(%(levelname)s) %(name)s: %(message)s"
    
    FORMATS = {
        logging.DEBUG: bold_grey    + formatter_string + end_of_line,
        logging.INFO: grey          + formatter_string + end_of_line,
        logging.WARNING: yellow     + formatter_string + end_of_line,
        logging.ERROR: red          + formatter_string + end_of_line,
        logging.CRITICAL: bold_red  + formatter_string + end_of_line
    }

    def format(self, record):

        # Template formatado.
        color_string = self.FORMATS.get(record.levelno)

        # Formato final
        formatter = logging.Formatter(color_string)
        
        return formatter.format(record)
