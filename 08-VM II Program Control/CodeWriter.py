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
    label_count = 0
    call_count = 0

    def __init__(self, output_stream: typing.TextIO) -> None:
        """Initializes the CodeWriter.
        Args:
            output_stream (typing.TextIO): output stream.
        """
        self.output_stream = output_stream
        self.current_function = "Sys.init"
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
        self.regA_as_last_stack_member_index()
        if command == "add":
            self.write("M=D+M")
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

    def write_label(self, label: str) -> None:
        """Writes assembly code that affects the label command. 
        Let "Xxx.foo" be a function within the file Xxx.vm. The handling of
        each "label bar" command within "Xxx.foo" generates and injects the symbol
        "Xxx.foo$bar" into the assembly code stream.
        When translating "goto bar" and "if-goto bar" commands within "foo",
        the label "Xxx.foo$bar" must be used instead of "bar".

        Args:
            label (str): the label to write.
        """
        # TODO:: filename.function (should i do a global var with current_scope?)
        self.write_pretty_function_label(label, None)

    def write_goto(self, label: str) -> None:
        """Writes assembly code that affects the goto command.

        Args:
            label (str): the label to go to.
        """
        self.regA_as_function_label(label, None)
        self.write("0;JMP")

    def write_if(self, label: str) -> None:
        """Writes assembly code that affects the if-goto command. 

        Args:
            label (str): the label to go to.
        """
        self.write_pop()  # Pops from stack to D
        self.regA_as_label(self.current_function + "$" + label, None)
        # jumps if d is not 0
        self.write("D;JNE")  # false is 0 true is anything but 0

    def write_function(self, function_name: str, n_vars: int) -> None:
        """Writes assembly code that affects the function command. 
        The handling of each "function Xxx.foo" command within the file Xxx.vm
        generates and injects a symbol "Xxx.foo" into the assembly code stream,
        that labels the entry-point to the function's code.
        In the subsequent assembly process, the assembler translates this 
        symbol into the physical address where the function code starts.

        Args:
            function_name (str): the name of the function.
            n_vars (int): the number of local variables of the function.
        """
        # The pseudo-code of "function function_name n_vars" is:
        # (function_name)       // injects a function entry label into the code
        # Updates the current function name
        self.write_pretty_label(function_name, None)
        self.current_function = function_name
        # repeat n_vars times:  // n_vars = number of local variables
        #   push constant 0     // initializes the local variables to 0
        for i in range(n_vars):
            self.write_push_false()

    def write_call(self, function_name: str, n_args: int) -> None:
        """Writes assembly code that affects the call command. 
        Let "Xxx.foo" be a function within the file Xxx.vm.
        The handling of each "call" command within Xxx.foo's code generates and
        injects a symbol "Xxx.foo$ret.i" into the assembly code stream, where
        "i" is a running integer (one such symbol is generated for each "call"
        command within "Xxx.foo").
        This symbol is used to mark the return address within the caller's 
        code. In the subsequent assembly process, the assembler translates this
        symbol into the physical memory address of the command immediately
        following the "call" command.

        Args:
            function_name (str): the name of the function to call.
            n_args (int): the number of arguments of the function.
        """
        # The pseudo-code of "call function_name n_args" is:
        # push return_address   // generates a label and pushes it to the stack
        CodeWriter.call_count += 1
        self.regA_as_function_label("ret", CodeWriter.call_count)
        self.write("D=A")
        self.write_push()
        # push LCL              // saves LCL of the caller
        self.write_push_val("LCL")
        # push ARG              // saves ARG of the caller
        self.write_push_val("ARG")
        # push THIS             // saves THIS of the caller
        self.write_push_val("THIS")
        # push THAT             // saves THAT of the caller
        self.write_push_val("THAT")
        # ARG = SP-5-n_args     // repositions ARG
        delta_args = 5 + n_args
        self.write("@" + str(delta_args))
        self.write("D=A")
        self.write("@SP")
        self.write("D=M-D")
        self.write("@ARG")
        self.write("M=D")
        # LCL = SP              // repositions LCL
        self.write("@SP")
        self.write("D=M")
        self.write("@LCL")
        self.write("M=D")
        # goto function_name    // transfers control to the callee
        self.write("@" + function_name)
        self.write("0;JMP")
        # (return_address)      // injects the return address label into the code
        self.write_pretty_function_label("ret", CodeWriter.call_count)

    def write_return(self) -> None:
        """Writes assembly code that affects the return command."""
        # frame = LCL                   // frame is a temporary variable
        self.write("@LCL")
        self.write("D=M")
        self.write("@R15")  # R15 would operate as the endFrame variable
        self.write("M=D")
        # return_address = *(frame-5)   // puts the return address in a temp var
        self.write("@5")
        self.write("D=A")
        self.write("@R15")
        self.write("A=M-D")
        self.write("D=M")  # gets the actual return address
        self.d_to_temp()  # puts in R13
        # *ARG = pop()                  // repositions the return value for the caller
        self.write_pop()
        self.write("@ARG")
        self.write("A=M")
        self.write("M=D")
        # SP = ARG + 1                  // repositions SP for the caller
        self.write("@ARG")
        self.write("D=M+1")
        self.write("@SP")
        self.write("M=D")
        # THAT = *(frame-1)             // restores THAT for the caller
        self.field_to_prefunction_address("THAT", 1)
        # THIS = *(frame-2)             // restores THIS for the caller
        self.field_to_prefunction_address("THIS", 2)
        # ARG = *(frame-3)              // restores ARG for the caller
        self.field_to_prefunction_address("ARG", 3)
        # LCL = *(frame-4)              // restores LCL for the caller
        self.field_to_prefunction_address("LCL", 4)
        # goto return_address           // go to the return address
        self.d_from_temp()
        self.write("A=D")
        self.write("0;JMP")
        pass

    def write_bootstrap(self):
        self.write("@256")
        self.write("D=A")
        self.write("@SP")
        self.write("M=D")
        self.write_call("Sys.init", 0)

    ########################## END OF API ############################
    ###################### custom functions ##########################
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

    def field_to_prefunction_address(self, field: str, delta: int):
        """Sets a given field(ARG/THIS/THAT/LCL) with the right address from
        LCL assuming its address is at @R15. and calculating it's place with given delta"""
        self.write("@" + str(delta))
        self.write("D=A")
        self.write("@R15")
        self.write("D=M-D")
        self.write("A=D")
        self.write("D=M")
        self.write("@" + field)
        self.write("M=D")

    def get_destination(self):
        """Sets A register to destination"""
        self.write("@R14")
        self.write("A=M")

    def regA_as_last_stack_member_index(self):
        """Sets A register as the address of the last stack member"""
        self.write("@SP")
        self.write("A=M-1")  # gets the last member index

    def write_compare(self, command: str):
        """Manages the writing of eq gt lt"""
        CodeWriter.label_count += 1
        self.write_pre_compare(command)
        self.write_pretty_label("unresolved", CodeWriter.label_count)  # jumps here if pre compare couldn't determine
        # pre_compare popd x and y. to subtract successfully in case unresolved, we should add 2 to SP.
        self.advance_sp()
        self.advance_sp()
        self.write_arithmetic("sub")
        self.retreat_sp()  # arithmetic advanced
        self.write("A=M")
        self.write("D=M")
        self.regA_as_label("TRUE", CodeWriter.label_count)
        if command == "eq":
            self.write("D;JEQ")
        elif command == "lt":
            self.write("D;JLT")
        elif command == "gt":
            self.write("D;JGT")
        self.regA_as_label("FALSE", CodeWriter.label_count)
        self.write("0;JMP")  # jumps over TRUE label section
        self.write_pretty_label("TRUE", CodeWriter.label_count)
        self.write_push_true()
        self.regA_as_label("CONTINUE", CodeWriter.label_count)
        self.write("0;JMP")
        self.write_pretty_label("FALSE", CodeWriter.label_count)
        self.write_push_false()
        self.write_pretty_label("CONTINUE", CodeWriter.label_count)

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
        """Writes a pretty label in form of : (text.label_num)"""
        if label_num:
            self.write("(" + text + "." + str(label_num) + ")")
        else:
            self.write("(" + text + ")")

    def write_pretty_function_label(self, text: str, label_num: int):
        """Writes a pretty label in form of : (function$label)"""
        if label_num:
            self.write_pretty_label(self.current_function + "$" + text, label_num)
        else:
            self.write_pretty_label(self.current_function + "$" + text, None)

    def regA_as_label(self, text: str, label_num: int):
        """"Sets A register to be the label in form of : @text.label_num"""
        if label_num:
            self.write("@" + text + "." + str(label_num))
        else:
            self.write("@" + text)

    def regA_as_function_label(self, text: str, label_num: int):
        if label_num:
            self.regA_as_label(self.current_function + "$" + text, label_num)
        else:
            self.regA_as_label(self.current_function + "$" + text, None)

    def write_push_true(self):
        """Pushes -1 to the stack"""
        self.write_push_pop("C_PUSH", "constant", -1)

    def write_push_false(self):
        """Pushes 0 to the stack"""
        self.write_push_pop("C_PUSH", "constant", 0)

    def write_push_val(self, val: str):
        """Pushes val to stack"""
        self.write("@" + val)
        self.write("D=M")
        self.write_push()

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
        cur_label = CodeWriter.label_count
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
        self.write_pretty_label("yGT0", CodeWriter.label_count)
        self.write_pop()  # pops x from stack to D
        # y>0 and x=0?
        self.regA_as_label("yGTx", CodeWriter.label_count)
        self.write("D;JEQ")
        # y>0 and x<0 ?
        self.regA_as_label("yGTx", CodeWriter.label_count)
        self.write("D;JLT")
        # y>0 and x>0
        self.jump_to("unresolved", CodeWriter.label_count)

        self.write_pretty_label("yEQx", CodeWriter.label_count)
        if command == "eq":
            self.jump_to("TRUE", CodeWriter.label_count)
        else:
            self.jump_to("FALSE", CodeWriter.label_count)

        self.write_pretty_label("yGTx", CodeWriter.label_count)
        if command == "lt":
            self.jump_to("TRUE", CodeWriter.label_count)
        else:
            self.jump_to("FALSE", CodeWriter.label_count)

        self.write_pretty_label("yLTx", CodeWriter.label_count)
        if command == "gt":
            self.jump_to("TRUE", CodeWriter.label_count)
        else:
            self.jump_to("FALSE", CodeWriter.label_count)
