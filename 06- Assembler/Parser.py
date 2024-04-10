"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing


class Parser:
    """Encapsulates access to the input code. Reads an assembly program
    by reading each command line-by-line, parses the current command,
    and provides convenient access to the commands components (fields
    and symbols). In addition, removes all white space and comments.
    """

    def __init__(self, input_file: typing.TextIO) -> None:
        """Opens the input file and gets ready to parse it.
        Args:
            input_file (typing.TextIO): input file.
        """
        # Your code goes here!
        # reads all the lines from the file
        # TODO is it removing blank spaces?
        # TODO a comment can start at the end of the command at the same line
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
        self.commandsNum = len(input_lines)
        self.curCommandCount = 0
        self.curCommand = input_lines[0]

    def has_more_commands(self) -> bool:
        """Are there more commands in the input?
        Returns:
            bool: True if there are more commands, False otherwise.
        """
        return self.commandsNum > self.curCommandCount

    def advance(self) -> None:
        """Reads the next command from the input and makes it the current command.
        Should be called only if has_more_commands() is true.
        """
        self.curCommandCount += 1
        if self.has_more_commands():
            self.curCommand = self.commands[self.curCommandCount]

    def command_type(self) -> str:
        """
        Returns:
            str: the type of the current command:
            "A_COMMAND" for @Xxx where Xxx is either a symbol or a decimal number
            "C_COMMAND" for dest=comp;jump
            "L_COMMAND" (actually, pseudo-command) for (Xxx) where Xxx is a symbol
        """
        if self.curCommand[0] == '@':
            return "A_COMMAND"
        elif self.curCommand[0] == '(':
            return "L_COMMAND"
        return "C_COMMAND"

    def symbol(self) -> str:
        """
        Returns:
            str: the symbol or decimal Xxx of the current command @Xxx or
            (Xxx). Should be called only when command_type() is "A_COMMAND" or 
            "L_COMMAND".
        """
        command_type = self.command_type()
        if command_type == "L_COMMAND":
            return self.curCommand[1:-1]
        return self.curCommand[1:]

    def dest(self) -> str:
        """
        Returns:
            str: the dest mnemonic in the current C-command. Should be called 
            only when commandType() is "C_COMMAND".
        """
        equal = '='
        if equal in self.curCommand:
            index_equal = self.curCommand.index(equal)
            return self.curCommand[0:index_equal]
        return "null"

    def comp(self) -> str:
        """
        Returns:
            str: the comp mnemonic in the current C-command. Should be called 
            only when commandType() is "C_COMMAND".
        """
        equal = '='
        semicolon = ';'
        start_comp = 0
        end_comp = len(self.curCommand)
        if equal in self.curCommand:
            start_comp = self.curCommand.index(equal) + 1
        if semicolon in self.curCommand:
            end_comp = self.curCommand.index(semicolon)
        return self.curCommand[start_comp:end_comp]

    def jump(self) -> str:
        """
        Returns:
            str: the jump mnemonic in the current C-command. Should be called 
            only when commandType() is "C_COMMAND".
        """
        semicolon = ';'
        if semicolon in self.curCommand:
            start_jmp = self.curCommand.index(semicolon) + 1
            return self.curCommand[start_jmp:]
        return "null"
