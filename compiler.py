import os

includes = []

functions = {
    "output": "functions/output",
    ".data": "functions/.data",
    ".text": "functions/.text",
    "consoleHandle": "functions/consoleHandle",
    "forOutput": "functions/forOutput",
    "main": "functions/main",
    "output": "functions/output",
    "string": "functions/string",
    "exit": "functions/exit",
    "undefinedString": "functions/undefinedString",
    "forInput": "functions/forInput",
    "inputHandle": "functions/inputHandle",
    "write": "functions/write"
}

_function_cache =  {}

order = [
    ".data",
    ".text",
    "main",
    "exit"
]

def getFunction(function, arguments={}, indents=0):
    if function not in _function_cache:
        with open(functions[function], "r") as f:
            _function_cache[function] = f.read()
    data = _function_cache[function]

    for key, value in arguments.items():
        data = data.replace("{" + key + "}", value)

    lines = data.split("\n")
    finalLines = []

    #print(indents)

    for line in lines:
        line = "    "*indents + line
        finalLines.append(line)
        #print(line)

    data = "\n".join(finalLines)
    #print(data)

    return data

def build(buildFile, include):
    os.system(f"nasm -f win64 {buildFile}.asm -o {buildFile}.obj")
    os.system(f"gcc {buildFile}.obj -o {buildFile}.exe {include}")

    #os.system(f"del {buildFile}.asm")
    os.system(f"del {buildFile}.obj")

def writeASM(file, data):
    with open(f"{file}.asm", "w") as file:
        file.write(data)

def stackToData(stack={}):
    dataToReturn = ""

    for i in order:
        if i in stack:
            dataToReturn += "\n\n"+stack[i]

    return dataToReturn

currentStack = {
    ".text": getFunction(".text")+"\n"+getFunction("forOutput")+"\n"+getFunction("forInput")+"\n",
    "main": getFunction("main")+"\n"+getFunction("consoleHandle", indents=1)+"\n"+getFunction("inputHandle", indents=1)+"\n",
    "exit": getFunction("exit", indents=1)+"\n"
}
variables = {
    "str": [],
    "int": []
}
userVariables = {
    "str": {},
    "int": {}
}

buildFile = input("File name > ")

with open(buildFile+".pok", "r") as file:
    lines = file.readlines()

    for line in lines:
        baseLine = line
        line = line.replace("\n", "")
        #print("Processing line: ", line)


        parts = line.split(" ")
        if "-" in parts[0]:
            indents = parts[0].count("-")
            parts.pop(0)
        line = " ".join(parts)

        parts = line.strip().split(" ", maxsplit=1)
        if parts == []:
            pass
        
        elif parts[0] == "output":
            output = parts[1]

            if ".data" not in currentStack:
                currentStack[".data"] = getFunction(".data")+"\n"

            strName = ""
            lenName = ""

            if not "::" in parts[1]:
                strName = "str_"+str(len(variables["str"]))
                lenName = "int_"+str(len(variables["int"]))
            
                currentStack[".data"] += getFunction("string", {
                    "STR_NAME": strName, 
                    "VALUE": output,
                    "LEN_NAME": lenName
                }, 1)+"\n"

                variables["str"].append(strName)
                variables["int"].append(lenName)

            else:
                print(userVariables)
                # strName = userVariables["str"].keys()[list(userVariables["str"].values()).index(parts[1].replace("::", ""))]
                # lenName = userVariables["int"].keys()[list(userVariables["int"].values()).index("len"+parts[1].replace("::", ""))]

                strName = userVariables["str"][parts[1].replace("::", "")]
                lenName = userVariables["int"]["len"+parts[1].replace("::", "")]

            currentStack["main"] += "\n\n"+getFunction("output", {
                "STR_NAME": strName, 
                "LEN_NAME": lenName
            }, indents)+"\n"

            if "-lkernel32" not in includes:
                includes.append("-lkernel32")

        elif parts[0] == "uvar":
            parts = line.strip().split(" ")
            match parts[1]:

                case "string":

                    if len(parts)-1 >= 3:
                        if ".data" not in currentStack:
                            currentStack[".data"] = getFunction(".data")+"\n"

                        strName = "str_"+str(len(variables["str"]))
                        variables["str"].append(strName)

                        currentStack[".data"] += getFunction("undefinedString", {"NAME": parts[3], "BYTES": parts[2]}, indents)+"\n"
                        userVariables["str"][parts[3]] = strName

                        # strName = "str_"+str(len(variables["str"]))
                        # lenName = "int_"+str(len(variables["int"]))
                        
                        # currentStack[".data"] += getFunction("string", {"STR_NAME": strName, "LEN_NAME": lenName})
                    else:
                        print(f"WARN -- \"{parts[0]}\" expected 3 or more arguments, but only got {len(parts)-1} arguments on line {lines.index[baseLine]+1}")
                        input("ENTER > ")
                
                case _:

                    print(f"WARN -- \"{parts[0]}\" got unexpected TYPINPG argument \"{parts[1]}\" on line {lines.index(baseLine)+1}")
                    input("ENTER > ")

        elif parts[0] == "var":
            parts = line.strip().split(" ")
            match parts[1]:

                case "string":

                    if len(parts)-1 >= 3:
                        if ".data" not in currentStack:
                            currentStack[".data"] = getFunction(".data")+"\n"

                        strName = "str_"+str(len(variables["str"]))
                        lenName = "int_"+str(len(variables["int"]))
                        value = line.strip().split(" ", maxsplit=3)[3]

                        variables["str"].append(strName)
                        variables["int"].append(lenName)

                        currentStack[".data"] += getFunction("string", {"STR_NAME": strName, "VALUE": value, "LEN_NAME":lenName}, indents)+"\n"

                        userVariables["str"][parts[2]] = strName
                        userVariables["int"]["len"+parts[2]] = lenName
                    else:
                        print(f"WARN -- \"{parts[0]}\" expected 3 or more arguments, but only got {len(parts)-1} arguments on line {lines.index[baseLine]+1}")
                        input("ENTER > ")
                
                case _:

                    print(f"WARN -- \"{parts[0]}\" got unexpected TYPINPG argument \"{parts[1]}\" on line {lines.index(baseLine)+1}")
                    input("ENTER > ")


        elif parts[0] == ";":
            pass

        else:
            print(f"WARN -- \"{parts[0]}\" on line {lines.index(baseLine)+1} does not match any existing syntax.")
            input("ENTER > ")

writeASM("mycode", stackToData(currentStack))
print("SUCCESS -- Initial pok code converted to assembly")
build(buildFile, " ".join(includes))
print("SUCCESS -- Build process complete")
