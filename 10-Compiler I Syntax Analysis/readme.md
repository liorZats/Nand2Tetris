# Nand2Tetris - Project 10: Compiler I - Syntax Analysis
## Project Overview

In this project, I developed a syntax analyzer (parser) for the Jack programming language.
The syntax analyzer processes Jack source files and generates structured XML representations that describe the program’s syntax tree.

## Key Components:
Tokenizer: Breaks the input Jack source code into a stream of tokens.

Compilation Engine: Applies the Jack grammar to the token stream and outputs an XML syntax tree.

This is the foundational step in building a complete compiler that can later generate executable VM code.

## How to Run
1. Run the compiler on a single .jack file or a directory:

bash
Copy
Edit
python JackAnalyzer.py path/to/FileOrDirectory
2. The tokenizer will generate a T.xml file and the parser will generate a parse tree .xml file.

3. Use the provided TextComparer tool from Nand2Tetris to verify your XML outputs.

