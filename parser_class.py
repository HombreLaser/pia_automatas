from execution_exceptions import *
from tokens import TokenType, Token
from lexer import ArithmeticLexer

# Mensajes de error misceláneos.
UNEXPECTED = "Se encontró un elemento inesperado."


class Parser:
    """
    Superclase parser. Los atributos que comparten todos los
    parsers son la salida del análisis y los tokens del texto de entrada. 
    Los método que todos los parsers comparten es el de pedir el próximo token,
    el de analizar el token identificador y el de hacer un log de fallos.
    """
    def __init__(self, tokens):
        self.output = ""
        self.symbol_table = []
        self.tokens = iter(tokens)
        self.next_token()

    # Para checar que no haya errores en el lexer.
    def check_token(self):
        if self.current_token is None:
            return False

        return True
    
    def next_token(self):
        try:
            self.current_token = next(self.tokens)
        except StopIteration:
            
            self.current_token = None
        # Cualquier otro error en el lexer.
        except (EOFScanning, FileNameError, NewlineError, InvalidTokenError) as e:
            self.output += e.message
            self.current_token = None

    def parse_id(self):
        if self.current_token is None or self.current_token.type != TokenType.ID:
            raise InvalidSyntax(self.error_log())
        # Este en cambio, sí, pero no amerita detener la ejecución del
        # análisis.
        if self.current_token.value not in self.symbol_table:
            self.output += f"Aviso: uso de variable sin inicializar: {self.current_token.value}.\n"

    # Pequeña función para regresar en que símbolo falló el parser.
    def error_log(self):
        types = {TokenType.READ: "leer", TokenType.PRINT:"imprimir", TokenType.END:"terminar.",
                 TokenType.START:"iniciar", TokenType.NAME_FIELD:"programa"}

        if self.current_token.type in types:
            return types[self.current_token.type]

        return self.current_token.value


# Inicio de la clase ProgramParser.
# La mayoría de los errores posibles son escapables:
# excepto la falta de los saltos de línea.
class ProgramParser(Parser):
    """
    La clase de nuestro analizador sintáctico. Tiene como 
    variables globales los operadores y como atributos
    la salida del análisis, la tabla de símbolos donde
    se encuentran las variables inicializadas y una lista
    ordenada de tokens junto a la posición del token actual.
    """

    def __init__(self, tokens):
        super().__init__(tokens)

    # Inicio del análisis sintáctico.
    def parse(self):
        # Si el token actual es None, ocurrió un error
        # durante el análisis léxico.
        if not self.check_token():
            return self.output
        
        if self.current_token.type == TokenType.NAME_FIELD:
            self.next_token()
            
            if not self.check_token():
                raise InvalidSyntax(UNEXPECTED)

            if self.current_token.type != TokenType.NAME:
                raise InvalidSyntax(self.error_log())

            self.next_token()

            if not self.check_token():
                raise InvalidSyntax(UNEXPECTED)

            if self.current_token.type == TokenType.START:
                try:
                    self.next_token()
                    self.parse_sentence()
                except (InvalidSyntax, EOFScanning) as e:
                    self.output += e.message
                    return self.output
            else:
                raise InvalidSyntax(self.error_log())

            if self.current_token.type == TokenType.END:
                self.next_token()

                # Se supone que ya debimos haber consumido
                # todos los tokens en caso de que la entrada
                # sea correcta.
                if self.current_token is None:
                    return self.output

                return f"Sintaxis inválida: {self.error_log()}\n"
        else:
            return f"Sintaxis inválida: {self.error_log()}\n"

    def parse_expr(self, expr):
        lexer = ArithmeticLexer(expr)

        try:
            tokens = lexer.generate_tokens()
        except InvalidTokenError as e:
            self.output += e.message
            return False

        expr_parser = ArithmeticParser(expr, self.symbol_table, tokens)

        try:
            self.output += expr_parser.parse()
        except (InvalidSyntax) as e:
            self.output += e.message

    def parse_sentence(self):
        while self.current_token is not None and self.current_token.type != TokenType.END:
            if self.current_token.type == TokenType.READ:
                self.next_token()

                if not self.check_token():
                    raise InvalidSyntax("Errores en lectura de tokens.")
                    
                if self.current_token.type == TokenType.ID:
                    # Agregamos a la tabla de símbolos el
                    # identificador inicializado.
                    self.symbol_table.append(self.current_token.value)
                    self.next_token()
                else:
                    raise InvalidSyntax(self.error_log())
            elif self.current_token.type == TokenType.PRINT:
                self.next_token()
                self.parse_id()
                self.next_token()
            elif self.current_token.type == TokenType.ID:
                self.symbol_table.append(self.current_token.value)
                self.next_token()

                if self.current_token.type == TokenType.EQUALS:
                    self.next_token()

                    if self.current_token.type != TokenType.EXPR:
                        raise InvalidSyntax(self.current_token.value)
                    else:
                        self.parse_expr(self.current_token.value)
                        self.next_token()
                else:
                    raise InvalidSyntax(self.error_log())
            else:
                raise InvalidSyntax(self.error_log())

        if self.current_token is None:
            raise EOFScanning()


class ArithmeticParser(Parser):
    """
    Clase para el analizador sintáctico de expresiones
    aritméticas. Gramática:
    E --> TE'
    E' --> (+|-)TE'| épsilon
    T --> PT'
    T' --> (*|/)PT'| épsilon
    P --> FP'
    P' --> ^FP' | épsilon
    F --> -E | (E) | id
    """
    # El atributo expr sólo es para mostrar
    # mensajes de error más concisos.
    def __init__(self, expr, symbol_table, tokens):
        super().__init__(tokens)
        self.symbol_table = symbol_table
        self.expr = expr

    def parse(self):
        if self.current_token is None:
            return self.output

        try:
            self.parse_expr()
        except InvalidSyntax as e:
            self.output += e.message

        # Si no se consumieron todos los tokens
        # de la expresión hubo errores.
        if self.current_token is not None:
            raise InvalidSyntax(self.expr)

        return self.output

    def parse_expr(self):
        if not self.parse_term() or not self.parse_prime_expr():
            raise InvalidSyntax(self.expr)

        return True

    def parse_prime_expr(self):
        if self.current_token is not None:
            if self.current_token.type == TokenType.SUM or self.current_token.type == TokenType.SUBSTRACTION:
                self.next_token()

                if not self.parse_term() or not self.parse_prime_expr():
                    return False

        return True

    def parse_term(self):
        if not self.parse_power() or not self.parse_prime_term():
            return False

        return True

    def parse_prime_term(self):
        if self.current_token is not None:
            if ((is_division := (self.current_token.type == TokenType.DIVIDE)) or
                self.current_token.type == TokenType.MULTIPLY):
                self.next_token()

                # Ocurrió un error.
                if self.current_token is None:
                    return False

                if is_division and self.current_token.value == '0':
                    self.output += "Aviso: División entre cero.\n"
                if not self.parse_power():
                    return False
                
                if not self.parse_prime_term():
                    return False

        return True

    def parse_power(self):
        try:
            if not self.parse_factor():
                return False
        except ParenthesisError as e:
            self.output += e.message
            return False

        if not self.parse_prime_power():
            return False

        return True

    def parse_prime_power(self):
        if self.current_token is not None:
            if self.current_token.type == TokenType.POWER:
                self.next_token()

                try:
                    if not self.parse_factor():
                        return False
                except ParenthesisError as e:
                    self.output += e.message
                    return False

                if not self.parse_prime_power():
                    return False

        return True

    def parse_factor(self):
        # Si el token es None en este punto significa que se quedó
        # esperando un factor, pero no hay nada. Expresiones de la
        # forma a+
        if self.current_token is None:
            return False
        
        if self.current_token.type == TokenType.SUBSTRACTION:
            self.next_token()

            if not self.parse_expr():
                return False

            return True
        elif self.current_token.type == TokenType.LEF_PARENS:
            self.next_token()

            try:
                self.parse_expr()
            except InvalidSyntax as e:
                return False

            # Si el token actual es nulo por fallo en el
            # análisis léxico, lo detectaremos y retornaremos false.
            try:
                if self.current_token.type != TokenType.RIGHT_PARENS:
                    raise ParenthesisError(self.text)
            except AttributeError:
                return False

            self.next_token()

            return True
        elif ((is_id := (self.current_token.type == TokenType.ID))
              or self.current_token.type == TokenType.NUMBER):

            if is_id:
                self.parse_id()
                
            self.next_token()

            return True
        else:
            raise InvalidSyntax(self.expr)
