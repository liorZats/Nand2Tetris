# Nand2Tetris - Project 07: VM I - Stack Arithmetic
## Project Overview
In this project, I implemented a VM translator that handles stack-based arithmetic and memory access commands. This is a key step in bridging high-level languages and low-level hardware.

The translator takes VM commands (written in a simple stack-based language) and generates Hack assembly code that can run on the Hack computer.

## Supported Command Types:
Arithmetic Commands:

add, sub, neg, eq, gt, lt, and, or, not

Memory Access Commands:

push segment index

pop segment index

Supports the following segments: local, argument, this, that, constant, static, temp, pointer

## How to Run
1. Run the translator script:

bash
Copy
Edit
python VMTranslator.py path/to/VMFile.vm
2. The script will generate an .asm file with the translated Hack assembly code.

3. Load the .asm file into the Nand2Tetris CPU Emulator to run and verify the program.

