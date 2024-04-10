// This file is part of nand2tetris, as taught in The Hebrew University, and
// was written by Aviv Yaish. It is an extension to the specifications given
// [here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
// as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
// Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).

// The program should swap between the max. and min. elements of an array.
// Assumptions:
// - The array's start address is stored in R14, and R15 contains its length
// - Each array value x is between -16384 < x < 16384
// - The address in R14 is at least >= 2048
// - R14 + R15 <= 16383
//
// Requirements:
// - Changing R14, R15 is not allowed.

// Put your code here.
// Initialize the counter varibale i
	@i
	M=0
// Represents the current address.
	@R14
	D=M
	@cur
	M=D
// Initialize min and max variables with the first member of the array
// They both has the address of the matching array memeber. 
	@cur
	D=M
	@min
	M=D
	@max
	M=D
(LOOP)
	//if we reached the end of the array jump to END
	@i
	D=M
	@R15
	D=M-D
	@SWAP
	D;JLE	
	//else check for mins and maxs
	@cur
	A=M
	D=M // has the value of the current's address content
	// have we found new max?
	@max
	A=M
	D=D-M
	// has the address of max memeber
	@NEWMAX
	D;JGT
	//have we found new min?
	@cur
	A=M
	D=M
	@min
	A=M
	D=D-M
	@NEWMIN
	D;JLT
	
	@LOOPPROG
	0;JMP	
(NEWMAX)
	@cur
	D=M
	@max
	M=D
	@LOOPPROG
	0;JMP
(NEWMIN)
	@cur
	D=M
	@min
	M=D
	@LOOP
	0;JMP
	
(LOOPPROG)
	@i
	M=M+1
	@cur
	M=M+1
	@LOOP
	0;JMP

(SWAP)
	@max
	A=M // address of max member
	D=M // max member
	@tempmax
	M=D
	@min
	A=M
	D=M // min number
	@max
	A=M
	M=D // max index now has min value
	@tempmax
	D=M // max number
	@min
	A=M
	M=D // min index now has max value
(END)
	@END
	0;JMP
	

