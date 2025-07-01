# Nand2Tetris - Project 11: Compiler II - Code Generation
## Project Overview

In this project, I extended the Jack compiler to translate Jack source code directly into VM code that can run on the Hack computer.
The compiler now handles the entire process:
From tokenization ➜ to syntax analysis ➜ to VM code generation.

This project enables the compilation and execution of high-level Jack programs on the Hack platform.

## Supported Features:
Memory management (local, argument, this, that, static, field)

Arithmetic and logical operations

Branching and function calls

Array handling and object construction

Control structures: loops, conditionals, and returns

## How to Run:
1. Compile a Jack file or an entire directory:

bash
Copy
Edit
python JackAnalyzer.py path/to/FileOrDirectory

2. The compiler will generate .vm files for each Jack source file.

3. Load the generated .vm files into the VM Emulator to run and test the compiled program.




