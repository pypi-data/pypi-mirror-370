from enum import Enum


class LogType(Enum):
    INFO = 'INFO'
    WARNING = 'WARNING'
    DEBUG = 'DEBUG'
    ERROR = 'ERROR'
    EXEC = 'EXEC'

    # Método para obter o valor string
    def __str__(self):
        return self.value