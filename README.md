# POK Coding Language - Closer to the Core

pok (Primitive Operations Kit) is a simple, lightweight coding language made for the development of console based applications!

Although pok is similar to ASM, that doesnt mean you have to lose your sanity, when using it. pok manages the moving of bytes in order to run operations, but is flexible enough for high levels of control over meomry. pok, unlike most coding languages, does not include many high level function. There is no native way to check if two strings match. But thats the beauty, you can code your own arithmatic functions, logical checks, your own everything! Nothing is set in stone and everything can be done your own way.


## Overview



###### How does pok work?

The compiler.py file, tokenizes your .pok code. Then, it translates the tokenized code into 64-bit ASM code and creates an .obj file using NASM. To build the final product into an exe, GCC is used as the linker. This only works on Windows.



###### Dependencies

NASM 64-bit compatible, GCC 64-bit compatible, Python 1.14+ (python will be removed in favour of a fully POK based compiler, in the future)



## My Goal

Originally, this was just a project where I could mess about with ASM, but it has turned into so much more than that. I am reaching a point with the language where few things are missing for the development of a full compiler made solely of POK code. Thats the goal. Make a simple, yet robust, language with the control of ASM but readability of any other low-level language.




