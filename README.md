# pok-Coding-Language

pok is a simple, lightweight coding language made for quick development of simple console based applications!


## Overview



###### How does pok work?

The compiler.py file, tokenizes the .pok file, which has been input to the application. After this, it translates the tokenized code into 64-bit ASM code and creates an .obj file of it using nasm. To build the final product into an exe, GCC is used as the linker.



###### Dependencies

NASM 64-bit compatible, GCC 64-bit compatible



## My Goal

Originally, this started out as a project meant to help me learn some 64-bit ASM, but it has become more than just that to me now. When the language is finished, I hope to code a compiler for the language... in the language! If this goes well, in the further future, I hope to make a simple operating system with it (Mainly just mess about with making my own I/O).
