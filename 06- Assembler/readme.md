# Nand2Tetris - Project 06: Assembler
## Project Overview
The goal of this project is to bridge the gap between low-level human-readable assembly code and binary machine code that can be executed by the Hack computer built in Project 05.

I implemented an assembler that:

Parses Hack assembly files (.asm).

Resolves symbols and variable addresses.

Generates the corresponding binary machine code (.hack files).

## Features
Symbol Handling: Supports predefined symbols, labels, and user-defined variables.

Two-Pass Structure:

First Pass: Identifies and maps labels to ROM addresses.

Second Pass: Translates A-instructions and C-instructions to binary code.

Full Hack Assembly Language Support: Handles A-instructions, C-instructions, jumps, computation, and memory addressing.

## How to Run
1. Run the assembler script on a Hack assembly file:

bash
Copy
Edit
python Assembler.py Prog.asm

2. The assembler will generate Prog.hack with the translated binary machine code.

3. Load the .hack file into the Nand2Tetris CPU Emulator to execute and verify the program.


