"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import os
import sys
import typing
from SymbolTable import SymbolTable
from Parser import Parser
from Code import Code


def deci_to_bin(deci: str):
    """Translates decimal to binary
        Args:
            command string of decimal address/command etc
            return string for the binary representation
    """
    a = int(deci)
    bin_out = ""
    for i in range(14, -1, -1):
        b = pow(2, i)
        if b <= a:
            bin_out += "1"
            a = a - b
        else:
            bin_out += "0"
    return bin_out

def assemble_file(
        input_file: typing.TextIO, output_file: typing.TextIO) -> None:
    """Assembles a single file.

    Args:
        input_file (typing.TextIO): the file to assemble.
        output_file (typing.TextIO): writes all output to this file.
    """
    parser_l_seeker = Parser(input_file)
    symbols = SymbolTable()
    line_count = 0
    rom = 16
    # first pass - filling the symbol table
    while parser_l_seeker.has_more_commands():
        cur_instruction_type = parser_l_seeker.command_type()
        if cur_instruction_type == "L_COMMAND":
            l_command = parser_l_seeker.symbol()
            symbols.add_entry(l_command, line_count)
        else:
            line_count += 1
        parser_l_seeker.advance()
    # second pass - commands handle
    input_file.seek(0)
    parser_commands_handler = Parser(input_file)
    while parser_commands_handler.has_more_commands():
        cur_instruction_type = parser_commands_handler.command_type()
        # handle @xxx can be @123 or @counter
        if cur_instruction_type == "A_COMMAND":
            command = "0"
            cur_symbol = parser_commands_handler.symbol()
            # @counter
            if not cur_symbol.isnumeric():
                if symbols.contains(cur_symbol):
                    address = symbols.get_address(cur_symbol)
                    command += deci_to_bin(address)
                else:
                    symbols.add_entry(cur_symbol, rom)
                    command += deci_to_bin(rom)
                    rom += 1
            # @1234
            else:
                command += deci_to_bin(cur_symbol)
        elif cur_instruction_type == "C_COMMAND":
            comp = Code.comp(parser_commands_handler.comp())
            dest = Code.dest(parser_commands_handler.dest())
            jmp = Code.jump(parser_commands_handler.jump())
            if len(comp) > 7:  # shift is called
                command = comp + dest + jmp
            else:
                command = "111" + comp + dest + jmp
        else:
            parser_commands_handler.advance()
            continue
        output_file.write(command + '\n')
        parser_commands_handler.advance()


if "__main__" == __name__:
    # Parses the input path and calls assemble_file on each input file.
    # This opens both the input and the output files!
    # Both are closed automatically when the code finishes running.
    # If the output file does not exist, it is created automatically in the
    # correct path, using the correct filename.
    if not len(sys.argv) == 2:
        sys.exit("Invalid usage, please use: Assembler <input path>")
    argument_path = os.path.abspath(sys.argv[1])
    if os.path.isdir(argument_path):
        files_to_assemble = [
            os.path.join(argument_path, filename)
            for filename in os.listdir(argument_path)]
    else:
        files_to_assemble = [argument_path]
    for input_path in files_to_assemble:
        filename, extension = os.path.splitext(input_path)
        if extension.lower() != ".asm":
            continue
        output_path = filename + ".hack"
        with open(input_path, 'r') as input_file, \
                open(output_path, 'w') as output_file:
            assemble_file(input_file, output_file)
