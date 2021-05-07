# Mensajes de error.

class LexerError(Exception):
    pass

class InvalidTokenError(LexerError):
    def __init__(self, char):
        if char != ' ' and char != '\n':
            self.char = char
        elif char == ' ':
            self.char = "Espacio"
        else:
            self.char = "Salto de línea."

        self.message = "Símbolo inválido: " + self.char + "\n"

class EOFScanning(LexerError):
    def __init__(self):
        self.message = "Se llegó al final del archivo durante escaneo.\n"

class FileNameError(LexerError):
    def __init__(self, filename):
        self.filename = filename
        self.message = "Nombre de programa inválido: " + self.filename + "\n"

class NewlineError(LexerError):
    def __init__(self):
        self.message = "Se esperaba un ';' y un salto de línea.\n"


class ParserException(Exception):
    pass

class InvalidSyntax(ParserException):
    def __init__(self, sentence):
        self.sentence = sentence
        self.message = "Sintaxis incorrecta: " + self.sentence + "\n"

class ParenthesisError(ParserException):
    def __init__(self, sentence):
        self.sentence = sentence
        self.message = "Error en paréntesis de la expresión.\n"
