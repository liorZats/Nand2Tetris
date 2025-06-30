Projects for Nand2Teris

Nand2Tetris website: http://nand2tetris.org/
#Overview
This repository contains my work from the Nand2Tetris course, where I built a fully functional computer system from the ground up, starting from basic logic gates and progressing to a complete computer capable of running high-level programs.
The project covers all levels of abstraction, from hardware design in HDL to low-level assembly and high-level programming in a custom-built languag

#Project Highlights
###Hardware Design:
Designed logic gates, multiplexers, ALU, registers, RAM, and the full Hack CPU using HDL.

###Assembler Implementation:
Developed a two-pass assembler in Python to translate Hack assembly language into machine code.

###Virtual Machine:
Implemented a stack-based virtual machine (VM) translator that converts VM commands into Hack assembly.

###High-Level Language Support:
Built a Jack compiler to translate high-level Jack programs into VM code.

###Operating System:
Developed basic OS-level services in Jack, including memory management, string handling, and simple I/O.

###End-to-End System:
Fully integrated hardware, assembler, VM, compiler, and OS to run high-level programs on the Hack computer.
##How to Run
Use the Hardware Simulator and CPU Emulator provided by the Nand2Tetris course to test HDL and assembly files.
For the assembler and VM, Python scripts can be executed directly to generate Hack machine code.
Use the Jack Compiler and run Jack programs end-to-end on the Hack platform.

##Notes
The tools folder includes all simulation tools provided by the course.
For detailed instructions and project explanations, please refer to the official Nand2Tetris website.
