# Nand2Tetris - Project 08: VM II - Program Control
## Project Overview
Building on the stack arithmetic translator from Project 07, this project adds support for:

Conditional and unconditional program flow commands.

Function declarations, calls, and returns.

This step is essential for supporting multi-function programs, recursive calls, and the control flow structures of high-level languages.

## Supported Command Types
Program Control Commands:

label labelName

goto labelName

if-goto labelName

Function Commands:

function functionName nVars

call functionName nArgs

return

## How to Run

1. Run the translator script:

bash
Copy
Edit
python VMTranslator.py path/to/VMFile.vm
Or for directories (if supported):

bash
Copy
Edit
python VMTranslator.py path/to/Directory

2. The translator will generate an .asm file.

3. Load the .asm file into the Nand2Tetris CPU Emulator to run and verify the program.

