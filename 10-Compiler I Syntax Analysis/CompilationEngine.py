"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing

from JackTokenizer import JackTokenizer


class CompilationEngine:
    """Gets input from a JackTokenizer and emits its parsed structure into an
    output stream.
    """
    statements = ["if", "do", "while", "return", "let"]
    ops = ["+", "-", "*", "/", "&", "|", "<", ">", "="]
    unary_ops = ['-', '~']
    arithmetics = ['-', '/', '+', '*']

    def __init__(self, input_stream: JackTokenizer, output_stream) -> None:
        """
        Creates a new compilation engine with the given input and output. The
        next routine called must be compileClass()
        :param input_stream: The input stream.
        :param output_stream: The output stream.
        """
        self.tokenizer = input_stream
        self.tokens = input_stream.tokens
        self.tokens_count = len(self.tokens)
        self.cur_token_index = 0
        self.output_stream = output_stream


    def compile_class(self) -> None:
        """Compiles a complete class."""
        # self.tokenizer.print_tokens()
        self.write_opening_tag("class")
        self.compile_from_tokens(3)  # class className {
        while self.more_vars_to_declare():
            self.compile_class_var_dec()
        while self.more_subroutines_to_declare():
            self.compile_subroutine()
        #  while() for subroutines
        self.write_closing_tag("class")

    def compile_class_var_dec(self) -> None:
        """Compiles a static declaration or a field declaration."""
        self.write_opening_tag("classVarDec")
        while not self.end_of_line():
            self.compile_from_tokens()
        self.compile_from_tokens()  # for ;
        self.write_closing_tag("classVarDec")

    def compile_subroutine(self) -> None:
        """
        Compiles a complete method, function, or constructor.
        You can assume that classes with constructors have at least one field,
        you will understand why this is necessary in project 11.
        """
        # Subroutine declaration
        self.write_opening_tag("subroutineDec")
        while not self.left_bracket_reached():
            self.compile_from_tokens()
        self.compile_from_tokens()  # for (
        self.compile_parameter_list()
        self.compile_from_tokens()  # for )
        # Subroutine body
        self.write_opening_tag("subroutineBody")
        self.compile_from_tokens()  # for {
        while self.more_vars_to_declare():
            self.compile_vars_dec()
        while self.more_statements():
            self.compile_statements()
        self.compile_from_tokens()  # for }
        self.write_closing_tag("subroutineBody")
        self.write_closing_tag("subroutineDec")
        if self.right_curley_bracket_reached():
            self.compile_from_tokens()  # for }

    def compile_parameter_list(self) -> None:
        """Compiles a (possibly empty) parameter list, not including the 
        enclosing "()".
        """
        self.write_opening_tag("parameterList")
        while not self.right_bracket_reached():
            self.compile_from_tokens()
        self.write_closing_tag("parameterList")

    def compile_var_dec(self) -> None:
        """Compiles a var declaration."""
        self.write_opening_tag("varDec")
        while not self.end_of_line():
            self.compile_from_tokens()
        self.compile_from_tokens()  # for ;
        self.write_closing_tag("varDec")

    def compile_statements(self) -> None:
        """Compiles a sequence of statements, not including the enclosing
        "{}".
        """
        self.write_opening_tag("statements")
        while self.more_statements():
            statement = self.tokenizer.cur_token
            if statement == "do":
                self.compile_do()
            if statement == "while":
                self.compile_while()
            if statement == "if":
                self.compile_if()
            if statement == "return":
                self.compile_return()
            if statement == "let":
                self.compile_let()
        self.write_closing_tag("statements")

    def compile_do(self) -> None:
        """Compiles a do statement."""
        self.write_opening_tag("doStatement")
        while not self.left_bracket_reached():
            self.compile_from_tokens()
        self.compile_from_tokens()  # for (
        self.compile_expression_list()
        self.compile_from_tokens()  # for )
        self.compile_from_tokens()  # for ;
        self.write_closing_tag("doStatement")

    def compile_let(self) -> None:
        """Compiles a let statement."""
        self.write_opening_tag("letStatement")
        while not self.equal_sign_reached() and not self.end_of_line():
            if self.left_square_bracket_reached():
                self.compile_from_tokens()
                self.compile_expression()
            else:
                self.compile_from_tokens()
        if not self.end_of_line():
            self.compile_from_tokens()  # for =
            self.compile_expression()
        self.compile_from_tokens()  # for ;
        self.write_closing_tag("letStatement")

    def compile_while(self) -> None:
        """Compiles a while statement."""
        self.write_opening_tag("whileStatement")
        self.compile_loop_or_condition()
        self.compile_statements()  # for empty loops
        while not self.right_curley_bracket_reached():
            self.compile_statements()
        self.compile_from_tokens()  # for }
        self.write_closing_tag("whileStatement")
        pass

    def compile_return(self) -> None:
        """Compiles a return statement."""
        self.write_opening_tag("returnStatement")
        self.compile_from_tokens()
        if not self.end_of_line():
            self.compile_expression()
        self.compile_from_tokens()  # for ;
        self.write_closing_tag("returnStatement")

    def compile_if(self) -> None:
        """Compiles an if statement, possibly with a trailing else clause."""
        self.write_opening_tag("ifStatement")
        self.compile_loop_or_condition()
        self.compile_statements()
        while not self.right_curley_bracket_reached():
            self.compile_statements()
        self.compile_from_tokens()  # for }
        self.compile_else()
        self.write_closing_tag("ifStatement")

    def compile_expression(self) -> None:
        """Compiles an expression."""
        self.write_opening_tag("expression")
        if self.tokenizer.cur_token in self.unary_ops:  # case: var = -value
            self.compile_term()
        while self.continue_expression():
            if self.tokenizer.cur_token in self.arithmetics:
                self.compile_from_tokens()
            self.compile_term()
        self.write_closing_tag("expression")
        if self.advance_after_expression():
            self.compile_from_tokens()

    def compile_term(self) -> None:
        """Compiles a term. 
        This routine is faced with a slight difficulty when
        trying to decide between some of the alternative parsing rules.
        Specifically, if the current token is an identifier, the routing must
        distinguish between a variable, an array entry, and a subroutine call.
        A single look-ahead token, which may be one of "[", "(", or "." suffices
        to distinguish between the three possibilities. Any other token is not
        part of this term and should not be advanced over.
        """
        pre_term = self.tokenizer.prev_token()
        self.write_opening_tag("term")
        while self.cur_token_is_term() and not self.right_bracket_reached():
            if self.left_bracket_reached():  # subroutineCall or (value)
                prev = self.tokenizer.prev_token()
                prev_type = self.tokenizer.prev_token_type()
                self.left_bracket_reached_in_term()
                if prev == "," or self.tokenizer.next_token() in self.arithmetics or \
                        self.tokenizer.cur_token in self.arithmetics:
                    # in case () reached in Expression list where : (someExp, (SomeExp))
                    if prev_type != "identifier":
                        # preventing cases like funcCall(Exp) - x printing arithmetics inside term
                        self.compile_from_tokens()
                    break
            elif self.tokenizer.cur_token in self.unary_ops:  # case (-/~ var)
                self.compile_from_tokens()
                self.compile_term()
            else:
                self.compile_from_tokens()
            if self.left_square_bracket_reached():  # Varname[]
                self.compile_from_tokens()  # for [
                self.compile_expression()
                if not self.end_of_line() and not self.comma_is_reached() and not self.right_bracket_reached() and \
                        self.tokenizer.next_token() in self.arithmetics:  # case not ']' handled by expression
                    self.compile_from_tokens()  # for ]
        self.write_closing_tag("term")
        if self.arithmetic_operation() and (
                pre_term not in self.unary_ops):  # for ops excluded the cases of ~/-(exp) |\&
            self.compile_from_tokens()
            self.compile_term()

    def compile_expression_list(self) -> None:
        """Compiles a (possibly empty) comma-separated list of expressions."""
        self.write_opening_tag("expressionList")
        while not self.right_bracket_reached() and not self.end_of_line():
            if self.left_bracket_reached() and self.tokenizer.prev_token_type() == "identifier":  # subroutineCall
                self.compile_subroutine_call()
            self.compile_expression()
        self.write_closing_tag("expressionList")

    ########################## END OF API ############################
    ###################### custom functions ##########################
    def get_current_token(self):
        """Returns current token"""
        return self.tokens[self.cur_token_index]

    def write_opening_tag(self, val: str):
        """
        Writes an opening XML tag with the specified value.
        """
        self.output_stream.write("<" + val + ">\n")

    def write_closing_tag(self, val: str):
        """
        Writes a closing XML tag with the specified value.
        """
        self.output_stream.write("</" + val + ">\n")

    def write_inline_opening_tag(self, val: str):
        """
        Writes an inline opening XML tag with the specified value.
        """
        self.output_stream.write("<" + val + ">")

    def compile_from_tokens(self, amount=0):
        """Writes in the output stream (amount) times"""
        if not amount:
            self.compile_token(self.tokenizer.cur_token, self.tokenizer.token_type())
            self.tokenizer.advance()
            return
        for i in range(amount):
            self.compile_token(self.tokenizer.cur_token, self.tokenizer.token_type())
            self.tokenizer.advance()

    def more_vars_to_declare(self):
        """
        Checks if there are more class variable declarations to compile.
        """
        cur_token = self.tokenizer.cur_token
        return self.tokenizer.token_type() == "keyword" and (
                cur_token == "static" or cur_token == "var" or cur_token == "field")

    def more_subroutines_to_declare(self):
        """
        Checks if there are more subroutines to declare within a class.
        """
        cur_token = self.tokenizer.cur_token
        return self.tokenizer.token_type() == "keyword" and (
                cur_token == "function" or cur_token == "constructor" or cur_token == "method")

    def end_of_line(self):
        """
        Checks if the end of a line has been reached.
        """
        return self.tokenizer.cur_token == ";" and self.tokenizer.token_type() == "symbol"

    def cur_token_is_symbol(self):
        """
        Checks if the current token is a symbol.
        """
        return self.tokenizer.token_type() == "symbol"

    def left_bracket_reached(self):
        """
        Checks if a left bracket has been reached.
        """
        return self.tokenizer.cur_token == "(" and self.tokenizer.token_type() == "symbol"

    def right_bracket_reached(self):
        """
        Checks if a right bracket has been reached.
        """
        return self.tokenizer.cur_token == ")" and self.tokenizer.token_type() == "symbol"

    def right_curley_bracket_reached(self):
        """
        Checks if a right curly bracket has been reached.
        """
        return self.tokenizer.cur_token == "}" and self.tokenizer.token_type() == "symbol"

    def left_curley_bracket_reached(self):
        """
         Checks if a left curly bracket has been reached.
         """
        return self.tokenizer.cur_token == "{" and self.tokenizer.token_type() == "symbol"

    def equal_sign_reached(self):
        """
        Checks if an equal sign has been reached.
        """
        return self.tokenizer.cur_token == "=" and self.tokenizer.token_type() == "symbol"

    def right_square_bracket_reached(self):
        """
        Checks if a right square bracket has been reached.
        """
        return self.tokenizer.cur_token == "]" and self.tokenizer.token_type() == "symbol"

    def left_square_bracket_reached(self):
        """
        Checks if a left square bracket has been reached.
        """
        return self.tokenizer.cur_token == "[" and self.tokenizer.token_type() == "symbol"

    def comma_is_reached(self):
        """
        Checks if a comma has been reached.
        """
        return self.tokenizer.cur_token == "," and self.tokenizer.token_type() == "symbol"

    def more_statements(self):
        """
        Checks if there are more statements to compile.
        """
        return self.tokenizer.cur_token in self.statements

    def compile_vars_dec(self):
        """
        Compiles variable declarations within a method or function.
        """
        while self.more_vars_to_declare():
            self.compile_var_dec()

    def compile_else(self):
        """In case an else statement is reached - compiles it"""
        if not self.tokenizer.cur_token == "else":
            return
        self.compile_from_tokens()  # else
        self.compile_from_tokens()  # {
        self.compile_statements()
        while not self.right_curley_bracket_reached():
            self.compile_statements()
        self.compile_from_tokens()  # for }

    def compile_token(self, cur_token, tag):
        """Writes to outputfile <tag> cur_token </tag>"""
        if tag == "symbol":
            cur_token = self.tokenizer.symbol()
        if tag == "stringConstant":
            cur_token = self.tokenizer.string_val()
        self.write_inline_opening_tag(tag)
        self.output_stream.write(" " + cur_token + " ")
        self.write_closing_tag(tag)

    def cur_token_is_term(self):
        """
         Checks if the current token is a term.
         """
        return (not self.end_of_line()) and (self.tokenizer.token_type() != "symbol" or self.tokenizer.cur_token == "."
                                             or self.left_square_bracket_reached() or self.tokenizer.cur_token == "("
                                             or (self.tokenizer.cur_token in self.unary_ops
                                                 and (self.tokenizer.prev_token_type() == "symbol" or
                                                      self.tokenizer.prev_token_type() == "keyword")))

    def compile_subroutine_call(self):
        """Prints ( expressionList )"""
        self.compile_from_tokens()  # for (
        self.compile_expression_list()
        self.compile_from_tokens()  # for )

    def left_bracket_reached_in_term(self):
        """
        Handles cases when a left bracket is reached within a term.
        """
        prev = self.tokenizer.prev_token()
        if self.tokenizer.prev_token_type() == "symbol":
            self.compile_from_tokens()  # for (
            self.compile_expression()
            if prev != "," and self.tokenizer.next_token() not in self.arithmetics:
                self.compile_from_tokens()  # for )
        elif self.tokenizer.prev_token_type() == "identifier":
            self.compile_subroutine_call()

    def continue_expression(self):
        """
        Checks if the expression parsing should continue.
        """
        return not self.end_of_line() and not self.right_bracket_reached() and not self.right_square_bracket_reached() \
               and not self.comma_is_reached()

    def advance_after_expression(self):
        """
        Checks if advancement is necessary after parsing an expression.
        """
        return self.right_square_bracket_reached() or self.comma_is_reached()

    def arithmetic_operation(self):
        """
        Checks if an arithmetic operation is encountered.
        """
        return self.tokenizer.cur_token in self.arithmetics or \
               (self.tokenizer.cur_token in self.ops and (self.tokenizer.prev_token_type() == "identifier" or
                                                          self.tokenizer.prev_token() == ")"
                                                          or self.tokenizer.prev_token_type() == "integerConstant" or
                                                          self.tokenizer.prev_token_type() == "stringConstant"))

    def compile_loop_or_condition(self):
        """
        Compiles a loop or a condition.
        """
        self.compile_from_tokens()  # if / while
        self.compile_from_tokens()  # (
        self.compile_expression()
        self.compile_from_tokens()  # )
        self.compile_from_tokens()  # {
