"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing


class JackTokenizer:
    """Removes all comments from the input stream and breaks it
    into Jack language tokens, as specified by the Jack grammar.
    
    # Jack Language Grammar

    A Jack file is a stream of characters. If the file represents a
    valid program, it can be tokenized into a stream of valid tokens. The
    tokens may be separated by an arbitrary number of whitespace characters, 
    and comments, which are ignored. There are three possible comment formats: 
    /* comment until closing */ , /** API comment until closing */ , and 
    // comment until the line’s end.

    - ‘xxx’: quotes are used for tokens that appear verbatim (‘terminals’).
    - xxx: regular typeface is used for names of language constructs 
           (‘non-terminals’).
    - (): parentheses are used for grouping of language constructs.
    - x | y: indicates that either x or y can appear.
    - x?: indicates that x appears 0 or 1 times.
    - x*: indicates that x appears 0 or more times.

    ## Lexical Elements

    The Jack language includes five types of terminal elements (tokens).

    - keyword: 'class' | 'constructor' | 'function' | 'method' | 'field' | 
               'static' | 'var' | 'int' | 'char' | 'boolean' | 'void' | 'true' |
               'false' | 'null' | 'this' | 'let' | 'do' | 'if' | 'else' | 
               'while' | 'return'
    - symbol: '{' | '}' | '(' | ')' | '[' | ']' | '.' | ',' | ';' | '+' | 
              '-' | '*' | '/' | '&' | '|' | '<' | '>' | '=' | '~' | '^' | '#'
    - integerConstant: A decimal number in the range 0-32767.
    - StringConstant: '"' A sequence of Unicode characters not including 
                      double quote or newline '"'
    - identifier: A sequence of letters, digits, and underscore ('_') not 
                  starting with a digit. You can assume keywords cannot be
                  identifiers, so 'self' cannot be an identifier, etc'.

    ## Program Structure

    A Jack program is a collection of classes, each appearing in a separate 
    file. A compilation unit is a single class. A class is a sequence of tokens 
    structured according to the following context free syntax:
    
    - class: 'class' className '{' classVarDec* subroutineDec* '}'
    - classVarDec: ('static' | 'field') type varName (',' varName)* ';'
    - type: 'int' | 'char' | 'boolean' | className
    - subroutineDec: ('constructor' | 'function' | 'method') ('void' | type) 
    - subroutineName '(' parameterList ')' subroutineBody
    - parameterList: ((type varName) (',' type varName)*)?
    - subroutineBody: '{' varDec* statements '}'
    - varDec: 'var' type varName (',' varName)* ';'
    - className: identifier
    - subroutineName: identifier
    - varName: identifier

    ## Statements

    - statements: statement*
    - statement: letStatement | ifStatement | whileStatement | doStatement | 
                 returnStatement
    - letStatement: 'let' varName ('[' expression ']')? '=' expression ';'
    - ifStatement: 'if' '(' expression ')' '{' statements '}' ('else' '{' 
                   statements '}')?
    - whileStatement: 'while' '(' 'expression' ')' '{' statements '}'
    - doStatement: 'do' subroutineCall ';'
    - returnStatement: 'return' expression? ';'

    ## Expressions
    
    - expression: term (op term)*
    - term: integerConstant | stringConstant | keywordConstant | varName | 
            varName '['expression']' | subroutineCall | '(' expression ')' | 
            unaryOp term
    - subroutineCall: subroutineName '(' expressionList ')' | (className | 
                      varName) '.' subroutineName '(' expressionList ')'
    - expressionList: (expression (',' expression)* )?
    - op: '+' | '-' | '*' | '/' | '&' | '|' | '<' | '>' | '='
    - unaryOp: '-' | '~' | '^' | '#'
    - keywordConstant: 'true' | 'false' | 'null' | 'this'
    
    Note that ^, # correspond to shiftleft and shiftright, respectively.
    """
    keyword_list = ['class', 'constructor', 'function', 'method', 'field',
                    'static', 'var', 'int', 'char', 'boolean', 'void', 'true',
                    'false', 'null', 'this', 'let', 'do', 'if', 'else',
                    'while', 'return']
    symbol_list = ['{', '}', '(', ')', '[', ']', '.', ',', ';', '+',
                   '-', '*', '/', '&', '|', '<', '>', '=', '~', '^', '#']

    def __init__(self, input_stream: typing.TextIO) -> None:
        """Opens the input stream and gets ready to tokenize it.

        Args:
            input_stream (typing.TextIO): input stream.
        """
        input_lines = input_stream.read().splitlines()
        lines = []
        # remove blank lines
        input_lines = [s.strip() for s in input_lines if s.strip()]
        # remove lines start with '//'
        input_lines = [line for line in input_lines if not line.startswith('//')]
        lines_without_comments = self.clean_inline_comments(input_lines)
        lines = self.clean_comment_blocks(lines_without_comments)
        # Fields initialization
        self.tokens = self.tokenize_lines(lines)
        self.tokensAmount = len(self.tokens)
        self.cur_token_count = 0
        self.cur_token = self.tokens[0]

    def has_more_tokens(self) -> bool:
        """Do we have more tokens in the input?

        Returns:
            bool: True if there are more tokens, False otherwise.
        """
        return self.tokensAmount > self.cur_token_count

    def advance(self) -> None:
        """Gets the next token from the input and makes it the current token. 
        This method should be called if has_more_tokens() is true. 
        Initially there is no current token.
        """
        self.cur_token_count += 1
        if self.has_more_tokens():
            self.cur_token = self.tokens[self.cur_token_count]
        # print(self.cur_token)

    def token_type(self) -> str:
        """
        Returns:
            str: the type of the current token, can be
            "KEYWORD", "SYMBOL", "IDENTIFIER", "INT_CONST", "STRING_CONST"
        """
        if self.cur_token in self.keyword_list:
            return "keyword"
        elif self.cur_token in self.symbol_list:
            return "symbol"
        elif self.cur_token.isdigit():
            return "integerConstant"
        elif self.cur_token[0] == '"':
            return "stringConstant"
        else:
            return "identifier"

    def keyword(self) -> str:
        """
        Returns:
            str: the keyword which is the current token.
            Should be called only when token_type() is "KEYWORD".
            Can return "CLASS", "METHOD", "FUNCTION", "CONSTRUCTOR", "INT", 
            "BOOLEAN", "CHAR", "VOID", "VAR", "STATIC", "FIELD", "LET", "DO", 
            "IF", "ELSE", "WHILE", "RETURN", "TRUE", "FALSE", "NULL", "THIS"
        """
        return self.cur_token.upper()

    def symbol(self) -> str:
        """
        Returns:
            str: the character which is the current token.
            Should be called only when token_type() is "SYMBOL".
            Recall that symbol was defined in the grammar like so:
            symbol: '{' | '}' | '(' | ')' | '[' | ']' | '.' | ',' | ';' | '+' | 
              '-' | '*' | '/' | '&' | '|' | '<' | '>' | '=' | '~' | '^' | '#'
        """
        if self.cur_token == "<":
            return "&lt;"
        elif self.cur_token == ">":
            return "&gt;"
        elif self.cur_token == "&":
            return "&amp;"
        elif self.cur_token == '"':
            return "&quot;"
        return self.cur_token

    def identifier(self) -> str:
        """
        Returns:
            str: the identifier which is the current token.
            Should be called only when token_type() is "IDENTIFIER".
            Recall that identifiers were defined in the grammar like so:
            identifier: A sequence of letters, digits, and underscore ('_') not 
                  starting with a digit. You can assume keywords cannot be
                  identifiers, so 'self' cannot be an identifier, etc'.
        """
        return self.cur_token

    def int_val(self) -> int:
        """
        Returns:
            str: the integer value of the current token.
            Should be called only when token_type() is "INT_CONST".
            Recall that integerConstant was defined in the grammar like so:
            integerConstant: A decimal number in the range 0-32767.
        """
        if 0 <= int(self.cur_token) < 32768:
            return int(self.cur_token)

    def string_val(self) -> str:
        """
        Returns:
            str: the string value of the current token, without the double 
            quotes. Should be called only when token_type() is "STRING_CONST".
            Recall that StringConstant was defined in the grammar like so:
            StringConstant: '"' A sequence of Unicode characters not including 
                      double quote or newline '"'
        """
        return self.cur_token.strip('"')

    ########################## END OF API ############################
    ###################### custom functions ##########################
    def clean_comment_blocks(self, input_lines):
        """" remove blocks start with /* or /** and end with */ """
        in_comment_block = False
        in_string = False
        lines = []
        for line in input_lines:
            new_line = ''
            i = 0
            while i < len(line):
                if line[i] == '"':
                    in_string = not in_string
                if not in_comment_block and not in_string and line[i:i + 2] == '/*':
                    in_comment_block = True
                    i += 2
                elif in_comment_block and line[i:i + 2] == '*/':
                    in_comment_block = False
                    i += 2
                elif not in_comment_block:
                    new_line += line[i]
                    i += 1
                else:
                    i += 1
            if not in_comment_block and new_line.strip() != '':
                lines.append(new_line)
        return lines

    def clean_inline_comments(self, input_lines):
        """Removes inline comments from @param input lines"""
        in_comment = False
        in_string = False
        lines = []
        for line in input_lines:
            new_line = ''
            i = 0
            while i < len(line):
                if line[i] == '"':
                    in_string = not in_string
                if not in_string and line[i:i + 2] == '//':
                    break
                else:
                    new_line += line[i]
                    i += 1
            if new_line.strip() != '':
                lines.append(new_line)
        return lines

    def tokenize_lines(self, lines):
        """returns list of tokens from a given lines array"""
        tokens = []
        for line in lines:
            current_token = ''
            is_string_literal = False
            for char in line:
                if char == '"':
                    if is_string_literal:
                        tokens.append(current_token + char)
                        current_token = ''
                        is_string_literal = False
                    else:
                        is_string_literal = True
                        current_token = '"'
                elif (char.isspace() or char in self.symbol_list) and not is_string_literal:
                    if current_token:
                        tokens.append(current_token)
                        current_token = ''
                    if char in self.symbol_list:
                        tokens.append(char)
                else:
                    current_token += char
            if current_token and (current_token != ";" or current_token != "{"):
                tokens.append(current_token)
        return tokens

    def prev_token_type(self) -> str:
        """
        Returns:
            str: the type of the prev token, can be
            "KEYWORD", "SYMBOL", "IDENTIFIER", "INT_CONST", "STRING_CONST"
        """
        prev = self.tokens[self.cur_token_count - 1]
        if prev in self.keyword_list:
            return "keyword"
        elif prev in self.symbol_list:
            return "symbol"
        elif prev.isdigit():
            return "integerConstant"
        elif prev[0] == '"':
            return "stringConstant"
        else:
            return "identifier"

    def next_token_type(self) -> str:
        """
        Returns:
            str: the type of the prev token, can be
            "KEYWORD", "SYMBOL", "IDENTIFIER", "INT_CONST", "STRING_CONST"
        """
        prev = self.tokens[self.cur_token_count + 1]
        if prev in self.keyword_list:
            return "keyword"
        elif prev in self.symbol_list:
            return "symbol"
        elif prev.isdigit():
            return "integerConstant"
        elif prev[0] == '"':
            return "stringConstant"
        else:
            return "identifier"

    def prev_token(self) -> str:
        """
        Returns prev token
        """
        return self.tokens[self.cur_token_count - 1]

    def next_token(self) -> str:
        """
        Returns prev token
        """
        return self.tokens[self.cur_token_count + 1]

    def print_tokens(self):
        for token in self.tokens:
            print(token)
