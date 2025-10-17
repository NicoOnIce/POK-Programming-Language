# pok-Coding-Language

pok is a simple, lightweight coding language made for quick development of simple console based applications!



###### How does pok work?

The compiler.py file, tokenizes the .pok file, which has been input to the application. After this, it translates the tokenized code into 64-bit ASM code and creates an .obj file of it using nasm. To build the final product into an exe, GCC is used as the linker.



###### Dependencies

NASM 64-bit compatible, GCC 64-bit compatible

