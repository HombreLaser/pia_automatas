from tokens import TokenType, Token
from execution_exceptions import *

NEWLINE = ";\n"
WHITESPACE = " \t"


class Lexer:
    def __init__(self, text):
        """
        Superclase de los analizadores
        sintácticos.
        """
        self.text = text
        self.pointer = -1
        self.next_char()

    def next_char(self, advance=1):
        self.pointer += advance

        try:
            self.current = self.text[self.pointer]
        except IndexError:
            self.current = None

    def generate_tokens(self):
        pass


class ProgramLexer(Lexer):
    """
    Analizador léxico del código fuente 
    de algún programa.
    """
    def __init__(self, text):
            super().__init__(text)

    def generate_tokens(self):
        while self.current is not None:
            if self.current in NEWLINE and self.text[self.pointer - 1] != '\n':
                self.next_char()
            elif self.current.islower() or self.current == ' ':
                # Checamos primero las palabras
                # reservadas.
                if self.text[self.pointer:self.pointer + len("programa ")] == "programa ":
                    self.next_char(advance=len("programa "))
                    yield Token(TokenType.NAME_FIELD)
                    yield self.generate_name()
                    self.check_newline()
                elif self.text[self.pointer:self.pointer + len("iniciar")] == "iniciar":
                    self.next_char(advance=len("iniciar"))
                    yield Token(TokenType.START)
                elif self.text[self.pointer:self.pointer + len("leer ")] == "leer ":
                    self.next_char(advance=len("leer "))
                    yield Token(TokenType.READ)
                elif self.text[self.pointer:self.pointer + len("imprimir ")] == "imprimir ":
                    self.next_char(advance=len("imprimir "))
                    yield Token(TokenType.PRINT)
                elif self.text[self.pointer:self.pointer + len("terminar.")] == "terminar.":
                    self.next_char(advance=len("terminar."))
                    yield Token(TokenType.END)
                elif self.text[self.pointer:self.pointer + len(" := ")] == " := ":
                    self.next_char(advance=len(" := "))
                    yield Token(TokenType.EQUALS)
                    yield self.generate_expr()
                    self.check_newline()
                else:
                    # Entonces es un identificador.
                    yield self.generate_id()
            else:
                raise InvalidTokenError(self.current)

    def generate_expr(self):
        expression = ""

        while self.current not in NEWLINE and self.current is not None:
            expression += self.current
            self.next_char()

        if self.current is None:
            raise EOFScanning()
            
        return Token(TokenType.EXPR, expression)

    def generate_name(self):
        if self.current.isalpha() and not self.current.isupper():
            name = self.current
            self.next_char()
        else:
            raise FileNameError(name + self.current)

        while (self.current is not None and self.current not in NEWLINE and
               self.current.islower() or self.current.isnumeric()):
            name += self.current
            self.next_char()

        if self.current is None or self.current.isupper():
            raise FileNameError(name + self.current)
            
        return Token(TokenType.NAME, name)

    def generate_id(self):
        id = ""

        while (self.current not in NEWLINE and self.current != ' ' and self.current is not None):
            # Checamos que el caracter no sea una mayúscula.
            if self.current.isupper() or not self.current.isalnum():
                raise InvalidTokenError(self.current)

            id += self.current
            self.next_char()

        if self.current == ' ':
            if (next_c := self.text[self.pointer + 1]) == ' ' or next_c in NEWLINE:
                raise InvalidTokenError(self.current)

        if self.current in NEWLINE:
            self.check_newline()

        return Token(TokenType.ID, id)


    def check_newline(self):
        if self.text[self.pointer:self.pointer + 2] != ";\n":
            raise NewlineError()


class ArithmeticLexer(Lexer):
    """
    Analizador léxico de expresiones 
    aritméticas.
    """
    operators = {'-', '+', '*', '/', '^', '(', ')'}
    
    def __init__(self, expr):
        super().__init__(expr)

    def generate_tokens(self):
        while self.current is not None:
            if self.current.isalpha() and self.current not in self.operators:

                if self.current.isupper() or self.current == ' ':
                    raise InvalidTokenError(self.current)
    
                yield self.generate_id()
            elif self.current.isnumeric():
                yield self.generate_number()
            elif self.current == '+':
                self.next_char()
                yield Token(TokenType.SUM)
            elif self.current == '-':  # Habrá que checar si es negación o resta.
                self.next_char()
                yield Token(TokenType.SUBSTRACTION)
            elif self.current == '*':
                self.next_char()
                yield Token(TokenType.MULTIPLY)
            elif self.current == '/':
                self.next_char()
                yield Token(TokenType.DIVIDE)
            elif self.current == '^':
                self.next_char()
                yield Token(TokenType.POWER)
            elif self.current == '(':
                self.next_char()
                yield Token(TokenType.LEF_PARENS)
            elif self.current == ')':
                self.next_char()
                yield Token(TokenType.RIGHT_PARENS)
            else:
                raise InvalidTokenError(self.current)

    def generate_number(self):
        number = ""
        
        while self.current is not None and self.current.isnumeric():
            # Checamos que no haya números de la forma 012, 003, etc.
            if number:
                if number[0] == "0":
                    raise InvalidTokenError(number + self.current)

            number += self.current
            self.next_char()

        return Token(TokenType.NUMBER, number)

    def generate_id(self):
        identifier = ""

        while self.current is not None and self.current not in self.operators:
            identifier += self.current
            self.next_char()

        return Token(TokenType.ID, identifier)
