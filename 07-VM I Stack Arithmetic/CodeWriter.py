"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing


class CodeWriter:
    """Translates VM commands into Hack assembly code."""

    def __init__(self, output_stream: typing.TextIO) -> None:
        """Initializes the CodeWriter.
        Args:
            output_stream (typing.TextIO): output stream.
        """
        self.output_stream = output_stream
        self.label_count = 0
        self.file_name = ""

    def set_file_name(self, filename: str) -> None:
        """Informs the code writer that the translation of a new VM file is 
        started.

        Args:
            filename (str): The name of the VM file.
        """
        # This function is useful when translating code that handles the
        # static segment. For example, in order to prevent collisions between two
        # .vm files which push/pop to the static segment, one can use the current
        # file's name in the assembly variable's name and thus differentiate between
        # static variables belonging to different files.
        # To avoid problems with Linux/Windows/MacOS differences with regards
        # to filenames and paths, you are advised to parse the filename in
        # the function "translate_file" in Main.py using python's os library,
        # For example, using code similar to:
        # input_filename, input_extension = os.path.splitext(os.path.basename(input_file.name))
        self.file_name = filename.replace('.vm', '').split('/')[-1]

    def write_arithmetic(self, command: str) -> None:
        """Writes assembly code that is the translation of the given 
        arithmetic command. For the commands' eq, lt, gt, you should correctly
        compare between all numbers our computer supports, and we define the
        value "true" to be -1, and "false" to be 0.

        Args:
            command (str): an arithmetic command.
        """
        if command not in ["neg", "not", "shiftLeft", "shiftRight"]:
            self.write_pop()  # pops *((@sp)-1) to D register
        self.regA_as_last_stack_member()
        if command == "add":
            self.write("M=M+D")
        elif command == "sub":
            self.write("M=M-D")
        elif command == "neg":
            self.write("M=-M")
        elif command == "and":
            self.write("M=M&D")
        elif command == "or":
            self.write("M=M|D")
        elif command == "not":
            self.write("M=!M")
        elif command == "shiftLeft":
            self.write("M=<<M")
        elif command == "shiftRight":
            self.write("M=>>M")
        else:  # eq, lt, gt
            self.write_compare(command)

    def write_push_pop(self, command: str, segment: str, index: int) -> None:
        """Writes assembly code that is the translation of the given 
        command, where command is either C_PUSH or C_POP.

        Args:
            command (str): "C_PUSH" or "C_POP".
            segment (str): the memory segment to operate on.
            index (int): the index in the memory segment.
        """
        # Note: each reference to "static i" appearing in the file Xxx.vm should
        # be translated to the assembly symbol "Xxx.i". In the subsequent
        # assembly process, the Hack assembler will allocate these symbolic
        # variables to the RAM, starting at address 16.
        if command == "C_PUSH":
            self.write_get_src_or_dest(segment, index, command)  # sets D reg with the right data
            self.write_push()  # pushes to stack from D reg
        elif command == "C_POP":
            self.write_pop()  # sets D reg to last stack member
            self.write_get_src_or_dest(segment, index, command)  # sets the destination to D's value

    # END OF API #
    # custom functions #
    def write(self, command):
        """
        writes the command in a file output stream.
        Adds \n in EOL
        """
        self.output_stream.write(command + '\n')

    def write_push(self):
        """Pushes to stack whatever in D"""
        self.write("@SP")
        self.write("A=M")
        self.write("M=D")
        self.advance_sp()

    def write_pop(self):
        """Pops from stack to D"""
        self.write("@SP")
        self.write("A=M-1")
        self.write("D=M")
        self.retreat_sp()

    def advance_sp(self):
        """@sp++"""
        self.write("@SP")
        self.write("M=M+1")

    def retreat_sp(self):
        """@sp--"""
        self.write("@SP")
        self.write("M=M-1")

    def write_get_src_or_dest(self, segment: str, index: int, command):
        """Gets the right address from segment and index and based on command type
        C_PUSH: sets D register with the right data to push
        C:POP: sets the value of an address with the content of D register"""
        segments = {"local": "LCL", "this": "THIS", "that": "THAT", "argument": "ARG"}
        if segment == "pointer":
            self.pointer_handler(index, command)
            return
        if segment == "constant":
            if index == -1:  # for true value
                self.write("D=-1")
            else:
                self.write("@" + str(index))
                self.write("D=A")
            return
        if command == "C_POP":
            self.d_to_temp()
        self.set_destination(segment, index)
        if command == "C_PUSH":
            self.get_destination()
            self.write("D=M")
        else:
            self.d_from_temp()
            self.get_destination()
            self.write("M=D")

    def set_destination(self, segment: str, index: int):
        """Makes an address called @destination==@R14 and sets it with the right address"""
        segments = {"local": "LCL", "this": "THIS", "that": "THAT", "argument": "ARG"}
        if segment == "static":
            self.regA_as_label(self.file_name, index)
            self.write("D=A")
            self.write("@R14")
            self.write("M=D")
            return
        self.write("@" + str(index))
        self.write("D=A")
        if segment == "temp":
            self.write("@R5")
            self.write("D=D+A")
        elif segment in segments.keys():  # segment is local/this/that/arg
            self.write("@" + segments.get(segment))
            self.write("D=D+M")
        self.write("@R14")
        self.write("M=D")

    def get_destination(self):
        """Sets A register to destination"""
        self.write("@R14")
        self.write("A=M")

    def regA_as_last_stack_member(self):
        """Sets A register as the address of the last stack member"""
        self.write("@SP")
        self.write("A=M-1")  # gets the last member index

    def write_compare(self, command: str):
        """Manages the writing of eq gt lt"""
        self.label_count += 1
        self.write_pre_compare(command)
        self.write_pretty_label("unresolved", self.label_count)  # jumps here if pre compare couldn't determine
        # pre_compare popd x and y. to subtract successfully in case unresolved, we should add 2 to SP.
        self.advance_sp()
        self.advance_sp()
        self.write_arithmetic("sub")
        self.retreat_sp()  # arithmetic advanced
        self.write("A=M")
        self.write("D=M")
        self.regA_as_label("TRUE", self.label_count)
        if command == "eq":
            self.write("D;JEQ")
        elif command == "lt":
            self.write("D;JLT")
        elif command == "gt":
            self.write("D;JGT")
        self.regA_as_label("FALSE", self.label_count)
        self.write("0;JMP")  # jumps over TRUE label section
        self.write_pretty_label("TRUE", self.label_count)
        self.write_push_true()
        self.regA_as_label("CONTINUE", self.label_count)
        self.write("0;JMP")
        self.write_pretty_label("FALSE", self.label_count)
        self.write_push_false()
        self.write_pretty_label("CONTINUE", self.label_count)

    def pointer_handler(self, index: int, command: str):
        if index == 0:
            self.write("@THIS")
        else:
            self.write("@THAT")
        if command == "C_POP":
            self.write("M=D")
        if command == "C_PUSH":
            self.write("D=M")

    def write_pretty_label(self, text: str, label_num: int):
        """write a pretty label in form of : (text.label_num)"""
        self.write("(" + text + "." + str(label_num) + ")")

    def regA_as_label(self, text: str, label_num: int):
        """"Sets A register to be the label in form of : @text.label_num"""
        self.write("@" + text + "." + str(label_num))

    def write_push_true(self):
        self.write_push_pop("C_PUSH", "constant", -1)

    def write_push_false(self):
        self.write_push_pop("C_PUSH", "constant", 0)

    def d_to_temp(self):
        """Saves D register to a temporary segment"""
        self.write("@R13")
        self.write("M=D")

    def d_from_temp(self):
        """Gets D register from a temporary segment"""
        self.write("@R13")
        self.write("D=M")

    def jump_to(self, text: str, label_num: int):
        """writing a jump command to @text.label_num"""
        self.regA_as_label(text, label_num)
        self.write("0;JMP")

    def write_pre_compare(self, command: str):
        """Checks if we're able to determine the command output based on x and y sign """
        cur_label = self.label_count
        # y is popd from stack to D
        # y=0 ?
        self.regA_as_label("yEQ0", cur_label)
        self.write("D;JEQ")
        # y>0 ?
        self.regA_as_label("yGT0", cur_label)
        self.write("D;JGT")

        # y<0
        self.write_pop()  # pops x from stack to D
        # y<0 and x=0?
        self.regA_as_label("yGTx", cur_label)
        self.write("D;JEQ")
        # y<0 and x>0 ?
        self.regA_as_label("yLTx", cur_label)
        self.write("D;JGT")
        # y<0 and x<0
        self.jump_to("unresolved", cur_label)

        # y=0
        self.write_pretty_label("yEQ0", cur_label)
        # y=0 and x=0?
        self.write_pop()  # pops x from stack to D
        self.regA_as_label("yEQx", cur_label)
        self.write("D;JEQ")
        # y=0 and x<0 or x>0
        self.regA_as_label("yGTx", cur_label)
        self.write("D;JLT")  # x<0
        self.regA_as_label("yLTx", cur_label)
        self.write("D;JGT")  # x>0

        # y>0
        self.write_pretty_label("yGT0", self.label_count)
        self.write_pop()  # pops x from stack to D
        # y>0 and x=0?
        self.regA_as_label("yGTx", self.label_count)
        self.write("D;JEQ")
        # y>0 and x<0 ?
        self.regA_as_label("yGTx", self.label_count)
        self.write("D;JLT")
        # y>0 and x>0
        self.jump_to("unresolved", self.label_count)

        self.write_pretty_label("yEQx", self.label_count)
        if command == "eq":
            self.jump_to("TRUE", self.label_count)
        else:
            self.jump_to("FALSE", self.label_count)

        self.write_pretty_label("yGTx", self.label_count)
        if command == "lt":
            self.jump_to("TRUE", self.label_count)
        else:
            self.jump_to("FALSE", self.label_count)

        self.write_pretty_label("yLTx", self.label_count)
        if command == "gt":
            self.jump_to("TRUE", self.label_count)
        else:
            self.jump_to("FALSE", self.label_count)
