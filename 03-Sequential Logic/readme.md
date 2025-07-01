# Nand2Tetris - Project 03: Sequential Logic
## Project Overview
Unlike combinational circuits that output results based solely on current inputs, sequential circuits have memory: their outputs depend on both current inputs and past states.

In this project, I constructed the basic memory units that enable computers to store and process data over time.

## Implemented Components
The following sequential logic chips were implemented:

Bit: A single-bit storage element that can load and hold a value.

Register: A 16-bit storage unit composed of multiple Bits.

RAM8: Memory with 8 registers (each 16-bit).

RAM64: Memory with 64 registers.

RAM512: Memory with 512 registers.

RAM4K: Memory with 4,096 registers.

RAM16K: Memory with 16,384 registers.

PC (Program Counter): A special-purpose register that can increment, reset, or load a value, used for instruction sequencing.

Each component was built on top of the previous ones, forming a hierarchical memory system.

