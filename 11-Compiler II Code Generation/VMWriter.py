"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing


class VMWriter:
    """
    Writes VM commands into a file. Encapsulates the VM command syntax.
    """

    def __init__(self, output_stream: typing.TextIO) -> None:
        """Creates a new file and prepares it for writing VM commands."""
        self.vm_file = output_stream

    def segment_determine(self, segment: str):
        """
        Args:
            segment: the string by which the segment is determined

        Returns: string of the right segment to write

        """
        if segment == "CONST":
            return "constant"
        elif segment == "ARG":
            return "argument"
        else:
            return segment.lower()

    def write_push(self, segment: str, index: int) -> None:
        """Writes a VM push command.
        Args:
            segment (str): the segment to push to, can be "CONST", "ARG", 
            "LOCAL", "STATIC", "THIS", "THAT", "POINTER", "TEMP"
            index (int): the index to push to.
        """
        segment_to_write = self.segment_determine(segment)
        self.vm_file.write('push ' + segment_to_write + " " + str(index) + "\n")

    def write_pop(self, segment: str, index: int) -> None:
        """Writes a VM pop command.

        Args:
            segment (str): the segment to pop from, can be "CONST", "ARG", 
            "LOCAL", "STATIC", "THIS", "THAT", "POINTER", "TEMP".
            index (int): the index to pop from.
        """
        segment_to_write = self.segment_determine(segment)
        if segment_to_write == 'var':
            segment_to_write = 'local'
        elif segment_to_write == 'field':
            segment_to_write = 'local'
        self.vm_file.write('pop ' + segment_to_write + " " + str(index) + "\n")

    def write_arithmetic(self, command: str) -> None:
        """Writes a VM arithmetic command.

        Args:
            command (str): the command to write, can be "ADD", "SUB", "NEG", 
            "EQ", "GT", "LT", "AND", "OR", "NOT", "SHIFTLEFT", "SHIFTRIGHT".
        """
        self.vm_file.write(command + " \n")

    def write_label(self, label: str) -> None:
        """Writes a VM label command.

        Args:
            label (str): the label to write.
        """
        self.vm_file.write("label " + label + " \n")

    def write_goto(self, label: str) -> None:
        """Writes a VM goto command.

        Args:
            label (str): the label to go to.
        """
        self.vm_file.write("goto " + label + " \n")

    def write_if(self, label: str) -> None:
        """Writes a VM if-goto command.

        Args:
            label (str): the label to go to.
        """
        self.vm_file.write("if-goto " + label + " \n")

    def write_call(self, class_name: str, name: str, n_args: int) -> None:
        """Writes a VM call command.
        Args:
            class_name:
            name (str): the name of the function to call.
            n_args (int): the number of arguments the function receives.
        """
        self.vm_file.write("call " + class_name + "." + name + " " + str(n_args) + " \n")

    def write_function(self, name: str, n_locals: int) -> None:
        """Writes a VM function command.
        Args:
            name (str): the name of the function.
            n_locals (int): the number of local variables the function uses.
        """
        self.vm_file.write("function " + name + " " + str(n_locals) + " \n")

    def write_return(self) -> None:
        """Writes a VM return command."""
        self.vm_file.write('return \n')

    def write(self, text):
        """Write anything in VM"""
        self.vm_file.write(text + ' \n')
