"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing


class Parser:
    """
    # Parser
    
    Handles the parsing of a single .vm file, and encapsulates access to the
    input code. It reads VM commands, parses them, and provides convenient 
    access to their components. 
    In addition, it removes all white space and comments.

    ## VM Language Specification

    A .vm file is a stream of characters. If the file represents a
    valid program, it can be translated into a stream of valid assembly 
    commands. VM commands may be separated by an arbitrary number of whitespace
    characters and comments, which are ignored. Comments begin with "//" and
    last until the lines end.
    The different parts of each VM command may also be separated by an arbitrary
    number of non-newline whitespace characters.

    - Arithmetic commands:
      - add, sub, and, or, eq, gt, lt
      - neg, not, shiftleft, shiftright
    - Memory segment manipulation:
      - push <segment> <number>
      - pop <segment wthat is not constant> <number>
      - <segment> can be any of: argument, local, static, constant, this, that, 
                                 pointer, temp
    - Branching (only relevant for project 8):
      - label <label-name>
      - if-goto <label-name>
      - goto <label-name>
      - <label-name> can be any combination of non-whitespace characters.
    - Functions (only relevant for project 8):
      - call <function-name> <n-args>
      - function <function-name> <n-vars>
      - return
    """

    def __init__(self, input_file: typing.TextIO) -> None:
        """Gets ready to parse the input file.

        Args:
            input_file (typing.TextIO): input file.
        """
        input_lines = input_file.read().splitlines()
        # remove comment lines
        input_lines = [line for line in input_lines if not line.startswith('//')]
        # remove blank lines
        input_lines = [s.strip() for s in input_lines if s.strip()]
        # remove inline comments
        for i in range(len(input_lines)):
            comment_index = input_lines[i].find('//')
            if comment_index != -1:
                input_lines[i] = input_lines[i][:comment_index].rstrip()
        self.commands = input_lines
        self.commandsAmount = len(input_lines)
        self.curCommandCount = 0
        self.curCommand = input_lines[0]

    def has_more_commands(self) -> bool:
        """Are there more commands in the input?
        Returns:
            bool: True if there are more commands, False otherwise.
        """
        return self.commandsAmount > self.curCommandCount

    def advance(self) -> None:
        """Reads the next command from the input and makes it the current 
        command. Should be called only if has_more_commands() is true. Initially
        there is no current command.
        """
        if self.has_more_commands():
            self.curCommand = self.commands[self.curCommandCount]
        self.curCommandCount += 1

    def command_type(self) -> str:
        """
        Returns:
            str: the type of the current VM command.
            "C_ARITHMETIC" is returned for all arithmetic commands.
            For other commands, can return:
            "C_PUSH", "C_POP", "C_LABEL", "C_GOTO", "C_IF", "C_FUNCTION",
            "C_RETURN", "C_CALL".
        """
        command_split = self.curCommand.split()
        first_word_not_stripped = command_split[0]
        first_word = first_word_not_stripped.strip()  # remove whitspaces
        if first_word:
            if first_word == "push":
                return "C_PUSH"
            elif first_word == "pop":
                return "C_POP"
            elif first_word == "label":
                return "C_LABEL"
            elif first_word == "goto":
                return "C_GOTO"
            elif first_word == "if-goto":
                return "C_IF"
            elif first_word == "function":
                return "C_FUNCTION"
            elif first_word == "return":
                return "C_RETURN"
            elif first_word == "call":
                return "C_CALL"
        return "C_ARITHMETIC"

    def arg1(self) -> str:
        """
        Returns:
            str: the first argument of the current command. In case of 
            "C_ARITHMETIC", the command itself (add, sub, etc.) is returned. 
            Should not be called if the current command is "C_RETURN".
        """
        command_split = self.curCommand.split()
        if self.command_type() == "C_ARITHMETIC":
            return command_split[0]
        elif self.command_type() == "C_RETURN":
            pass
        return command_split[1]

    def arg2(self) -> int:
        """
        Returns:
            int: the second argument of the current command. Should be
            called only if the current command is "C_PUSH", "C_POP", 
            "C_FUNCTION" or "C_CALL".
        """
        if self.command_type() not in ["C_PUSH", "C_POP", "C_FUNCTION", "C_CALL"]:
            pass
        command_split = self.curCommand.split()
        return int(command_split[2])
