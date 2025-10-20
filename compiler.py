import os
import sys

mains = [".main"]
includes = []

numbers = []
for i in range(9):
    numbers.append(str(i))

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
    "read": "functions/read",
    ".bss": "functions/.bss",
    "dynamicInt": "functions/dynamicInt",
    ".new": "functions/.new",
    "run": "functions/run",
    "ret": "functions/ret",
    "addition": "functions/addition",
    "subtraction": "functions/subtraction",
    "intEqual": "functions/intEqual",
    "else": "functions/else",
    "changeResVarInt": "functions/changeResVarInt",
    "goto": "functions/goto",
    "match": "functions/match",
    "callMatch": "functions/callMatch",
    "int": "functions/int",
    "user": "functions/user",
    "application": "functions/application",
    "bcopy": "functions/bcopy",
    "byteEqual": "functions/byteEqual",
    "setUvar": "functions/setUvar",
    "resByte": "functions/resByte",
    "changeResVarByte": "functions/changeResVarByte",
    "resString": "functions/resString",
    "byte": "functions/byte"
}

_function_cache =  {}

order = [
    ".data",
    ".bss",
    ".text",
    "main",
    "exit",
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

def mergeStacks():
    finalStack = {}

    for key in currentStack.keys():
        finalStack[key] = currentStack[key]

    for key in applicationStack.keys():
        finalStack["application"] += applicationStack[key]+"\n\n"

    return finalStack

def stackToData(stack={}):
    dataToReturn = ""

    for i in order:
        if i in stack:
            dataToReturn += stack[i]+"\n\n"
        stack.pop(i, None)

    for key in stack.keys():
        if key != "application":
            dataToReturn += stack[key]+"\n\n"
    
    dataToReturn += stack["application"]+"\n\n"

    return dataToReturn

currentStack = {
    ".text": getFunction(".text")+"\n"+getFunction("forOutput")+"\n"+getFunction("forInput")+"\n",
    "main": getFunction("main")+"\n"+getFunction("consoleHandle", indents=1)+"\n"+getFunction("inputHandle", indents=1)+"\n"+getFunction("goto", {"FUNCTION_NAME": "application.main"}, indents=1),
    "application": getFunction("application")+"\n",
}

applicationStack = {
    ".main": getFunction(".new", {"NAME": "main"})+"\n"
}

variables = {
    "str": [],
    "int": [],
    "byte": []
}
userVariables = {
    "str": {},
    "int": {},
    "byte": {}
}

buildFile = sys.argv[1]

def parseLine(parts:list, line:str, baseLine:str, lines:list, indents:int, main:str, embededParse:bool):
    global userVariables, variables, currentStack, currentMain, lastMain, mains
    if parts == [] or parts == [""]:
        pass
    
    elif parts[0] == "output":
        if len(parts)-1 >= 1:
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
                # print(userVariables)
                # strName = userVariables["str"].keys()[list(userVariables["str"].values()).index(parts[1].replace("::", ""))]
                # lenName = userVariables["int"].keys()[list(userVariables["int"].values()).index("len"+parts[1].replace("::", ""))]

                strName = userVariables["str"][parts[1].replace("::", "")]
                lenName = userVariables["int"]["len"+parts[1].replace("::", "")]
                lenName = f"[rel {lenName}]"

            if embededParse:
                currentStack[main] += "\n\n"+getFunction("output", {
                    "STR_NAME": strName, 
                    "LEN_NAME": lenName
                }, indents)+"\n"
            else:
                applicationStack[main] += "\n\n"+getFunction("output", {
                    "STR_NAME": strName, 
                    "LEN_NAME": lenName
                }, indents)+"\n"

            if "-lkernel32" not in includes:
                includes.append("-lkernel32")
        else:
            print(f"WARN -- \"{parts[0]}\" expected 1 or more arguments, but only got {len(parts)-1} arguments on line {lines.index[baseLine]+1}")
            sys.exit()

    elif parts[0] == "uvar":
        parts = line.strip().split(" ")
        match parts[1]:

            case "string":

                if len(parts)-1 >= 3:
                    if ".data" not in currentStack:
                        currentStack[".data"] = getFunction(".data")+"\n"

                    strName = "str_"+str(len(variables["str"]))
                    lenName = "int_"+str(len(variables["int"]))
                    variables["str"].append(strName)
                    variables["int"].append(lenName)

                    currentStack[".data"] += getFunction("undefinedString", {"NAME": strName, "BYTES": parts[2], "BYTES_NAME": lenName}, indents)+"\n"
                    userVariables["str"][parts[3]] = strName
                    userVariables["int"]["len"+parts[3]] = lenName

                    # strName = "str_"+str(len(variables["str"]))
                    # lenName = "int_"+str(len(variables["int"]))
                    
                    # currentStack[".data"] += getFunction("string", {"STR_NAME": strName, "LEN_NAME": lenName})
                else:
                    print(f"WARN -- \"{parts[0]}\" expected 3 or more arguments, but only got {len(parts)-1} arguments on line {lines.index[baseLine]+1}")
                    sys.exit()
            
            case _:

                print(f"WARN -- \"{parts[0]}\" got unexpected TYPINPG argument \"{parts[1]}\" on line {lines.index(baseLine)+1}")
                sys.exit()

    elif parts[0] == "set":
        parts = line.strip().split(" ")
        typing = parts[1]

        match typing:
            case "uvar":
                if len(parts)-1 >= 4:
                    variable = parts[2]
                    value = f"\"{parts[3]}\""

                    variable = userVariables["str"][variable]

                    if embededParse:
                        currentStack[main] += getFunction("setUvar", {"VARIABLE_NAME": variable, "VALUE": value})+"\n"
                    else:
                        applicationStack[main] += getFunction("setUvar", {"VARIABLE_NAME": variable, "VALUE": value})+"\n"
                else:
                    print(f"WARN -- \"{parts[0]}\" expected 4 or more arguments, but only got {len(parts)} arguments on line {lines.index[baseLine]+1}")
                    sys.exit()
            
            case "resvar":
                if len(parts)-1 >= 4:
                    typing2 = parts[2]
                    variable = parts[3]
                    value = f"'{parts[4]}'"

                    if typing2 == "byte":
                        variable = userVariables["byte"][variable]
                        if embededParse:
                            currentStack[main] += getFunction("changeResVarByte", {"BYTE_NAME": variable, "NEW_VALUE": value})+"\n"
                        else:
                            applicationStack[main] += getFunction("changeResVarByte", {"BYTE_NAME": variable, "NEW_VALUE": value})+"\n"

                    elif typing2 == "string":
                        value = f"\"{parts[4]}\""

                        variable = userVariables["str"][variable]
                        if embededParse:
                            currentStack[main] += getFunction("setUvar", {"VARIABLE_NAME": variable, "NEW_VALUE": value})+"\n"
                        else:
                            applicationStack[main] += getFunction("setUvar", {"VARIABLE_NAME": variable, "NEW_VALUE": value})+"\n"
                else:
                    print(f"WARN -- \"{parts[0]}\" expected 4 or more arguments, but only got {len(parts)} arguments on line {lines.index[baseLine]+1}")
                    sys.exit()


            case _:
                print(f"WARN -- \"{parts[0]}\" got unexpected TYPINPG argument \"{parts[1]}\" on line {lines.index(baseLine)+1}")
                sys.exit()

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
                    print(f"WARN -- \"{parts[0]}\" expected 3 or more arguments, but only got {len(parts)} arguments on line {lines.index[baseLine]+1}")
                    sys.exit()
            
            case "int":
                    if len(parts)-1 >= 3:
                        if ".data" not in currentStack:
                            currentStack[".data"] = getFunction(".data")+"\n"

                        intName = "int_"+str(len(variables["int"]))

                        variables["int"].append(intName)

                        currentStack[".data"] += getFunction("int", {"INT_NAME": intName, "VALUE": parts[3]}, indents)+"\n"

                        userVariables["int"][parts[2]] = intName
                    else:
                        print(f"WARN -- \"{parts[0]}\" expected 3 or more arguments, but only got {len(parts)} arguments on line {lines.index[baseLine]+1}")
                        sys.exit()

            case _:

                print(f"WARN -- \"{parts[0]}\" got unexpected TYPINPG argument \"{parts[1]}\" on line {lines.index(baseLine)+1}")
                sys.exit()
    
    elif parts[0] == "read":
        parts = line.strip().split(" ")

        if len(parts)-1 >= 1:
            if embededParse:
                currentStack[main] += getFunction("read", {"BUFFER_NAME": userVariables["str"][parts[1]], "BYTES_NAME": userVariables["int"]["len"+parts[1]]}, indents)+"\n"
            else:
                applicationStack[main] += getFunction("read", {"BUFFER_NAME": userVariables["str"][parts[1]], "BYTES_NAME": userVariables["int"]["len"+parts[1]]}, indents)+"\n"
        else:
            print(f"WARN -- \"{parts[0]}\" expected 2 or more arguments, but only got {len(parts)} arguments on line {lines.index(baseLine)}")
            sys.exit()

    elif parts[0] == "resvar":
        parts = line.strip().split(" ")
        if len(parts)-1 >= 2:
            match parts[1]:
                case "int":
                    if not ".bss" in currentStack:
                        currentStack[".bss"] = getFunction(".bss")+"\n"

                    intName = "int_"+str(len(variables["int"]))
                    variables["int"].append(intName)
                    
                    userVariables["int"][parts[2]] = intName

                    currentStack[".bss"] += getFunction("dynamicInt", {"NAME": intName}, indents)+"\n"
                    applicationStack[main] += getFunction("changeResVarInt", {"INT_NAME": intName, "NEW_VALUE": parts[3]}, indents)+"\n"
                
                case "byte":
                    if not ".bss" in currentStack:
                        currentStack[".bss"] = getFunction(".bss")+"\n"

                    byteName = "byte_"+str(len(variables["byte"]))
                    variables["byte"].append(byteName)

                    userVariables["byte"][parts[2]] = byteName

                    currentStack[".bss"] += getFunction("resByte", {"BYTE_NAME": byteName})+"\n"

                case "string":
                    if not ".bss" in currentStack:
                        currentStack[".bss"] = getFunction(".bss")+"\n"

                    stringName = "str_"+str(len(variables["str"]))
                    variables["str"].append(stringName)
                    
                    valueBytes = parts[3]

                    userVariables["str"][parts[2]] = stringName

                    currentStack[".bss"] += getFunction("resString", {"STRING_NAME": stringName, "BYTES": valueBytes})+"\n"

                case _:
                    print(f"WARN -- \"{parts[0]}\" go unexpected TYPING argument \"{parts[1]}\" on line {lines.index(baseLine)}")
        else:
            print(f"WARN -- \"{parts[0]}\" expected 2 or more arguments, but only got {len(parts)} arguments on line {lines.index(baseLine)}")
            sys.exit()

    elif parts[0] == "cresvar":
        parts = line.strip().split(" ")
        if len(parts)-1 >= 2:
            intName = userVariables[parts[1]]
            applicationStack[main] += getFunction("changeResVarInt", {"INT_NAME": intName, "NEW_VALUE": parts[2]}, indents)+"\n"
        else:
            print(f"WARN -- \"{parts[0]}\" expected 2 or more arguments, but only got {len(parts)} arguments on line {lines.index(baseLine)}")
            sys.exit()

    elif parts[0] == "bcopy":
        parts = line.strip().split(" ")
        if len(parts)-1 >= 3:
            if embededParse:
                sourceVariable = parts[1]

                if sourceVariable in userVariables["str"]:
                    sourceVariable = userVariables["str"][parts[2]]
                elif sourceVariable in userVariables["byte"]:
                    sourceVariable = userVariables["byte"][parts[2]]
                else:
                    print(f"WARN -- \"{parts[0]}\" expected either byte or string but got neither on line {lines.index(baseLine)+1}")
                    sys.exit()

                destinationVariable = userVariables["byte"][parts[1]]
                offset = userVariables["int"][parts[3]]

                currentStack[main] += getFunction("bcopy", {
                    "SOURCE_NAME": sourceVariable, 
                    "DESTINTION_NAME": destinationVariable, 
                    "OFFSET": offset
                }, indents)+"\n"
            else:

                sourceVariable = parts[1]

                if sourceVariable in userVariables["str"]:
                    sourceVariable = userVariables["str"][parts[2]]
                elif sourceVariable in userVariables["byte"]:
                    sourceVariable = userVariables["byte"][parts[2]]
                else:
                    print(f"WARN -- \"{parts[0]}\" expected either byte or string but got \"{parts[1]}\" on line {lines.index(baseLine)+1}")
                    sys.exit()
                
                destinationVariable = userVariables["byte"][parts[1]]
                offset = userVariables["int"][parts[3]]

                applicationStack[main] += getFunction("bcopy", {
                    "SOURCE_NAME": sourceVariable, 
                    "DESTINTION_NAME": destinationVariable, 
                    "OFFSET": offset
                }, indents)+"\n"
        else:
            print(f"WARN -- \"{parts[0]}\" expected 3 or more arguments, but only got {len(parts)} arguments on line {lines.index(baseLine)}")
            sys.exit() 

    elif parts[0] == "subroutine":
        parts = line.strip().split(" ")
        if len(parts)-1 >= 1:
            currentStack[parts[1]] = getFunction(".new", {"NAME": parts[1]})+"\n"
        else:
            print(f"WARN -- \"{parts[0]}\" expected 2 or more arguments, but only got {len(parts)} arguments on line {lines.index(baseLine)}")
            sys.exit()

    elif parts[0] == "if":
        parts = line.strip().split(" ")
        # print(parts)

        value1 = parts[1]
        operator = parts[2]
        value2 = parts[3]
        subroutine = parts[4]

        match operator:
            case "i==":
                if not value1 in numbers:
                    value1 = f"[rel {userVariables["int"][value1]}]"
                
                if not value2 in numbers:
                    value2 = f"[rel {userVariables["int"][value2]}]"

                if embededParse:
                    currentStack[main] += getFunction("intEqual", {
                        "INT_NAME1": value1,
                        "INT_NAME2": value2,
                        "SUBROUTINE_NAME": f".{subroutine}"
                    })+"\n"
                else:
                    applicationStack[main] += getFunction("intEqual", {
                        "INT_NAME1": value1,
                        "INT_NAME2": value2,
                        "SUBROUTINE_NAME": "main."+subroutine
                    })+"\n"

                subroutineName = f"after_{subroutine}"

                applicationStack["."+subroutineName] = getFunction(".new", {"NAME": subroutineName})+"\n"
                mains.append("."+subroutineName)
            
            case "b==":
                value1 = userVariables["byte"][value1]
                value2 = userVariables["byte"][value2]

                if embededParse:
                    currentStack[main] += getFunction("byteEqual", {
                        "BYTE_NAME1": value1, 
                        "BYTE_NAME2": value2, 
                        "SUBROUTINE_NAME": f".{subroutine}"
                    })+"\n"
                else:
                    applicationStack[main] += getFunction("byteEqual", {
                        "BYTE_NAME1": value1, 
                        "BYTE_NAME2": value2, 
                        "SUBROUTINE_NAME": f"main.{subroutine}"
                    })+"\n"
                
                subroutineName = f"after_{subroutine}"

                applicationStack["."+subroutineName] = getFunction(".new", {"NAME": subroutineName})+"\n"
                mains.append("."+subroutineName)

    elif parts[0] == "finish":
        currentStack[main] += getFunction("run", {"FUNCTION_NAME": "application"+mains[-1]}, indents)+"\n"

    elif parts[0] == "ret":
        if embededParse:
            currentStack[main] += getFunction("ret", {}, indents)+"\n"
        else:
            applicationStack[main] += getFunction("ret", {}, indents)+"\n"

    elif parts[0] == ";":
        pass

    elif parts[0] == "exit":
        if embededParse:
            currentStack[main] += getFunction("exit", indents=indents)+"\n"
        else:
            applicationStack[main] += getFunction("exit", indents=indents)+"\n"
    
    elif parts[0] == "end":
        currentStack[main] += getFunction("ret", indents=indents)+"\n"

    elif parts[0] == "add":
        parts = line.strip().split(" ")
        if len(parts)-1 >= 2:
            # print(userVariables)
            intName1 = userVariables["int"][parts[1]]
            intName2 = userVariables["int"][parts[2]]
            if embededParse:
                currentStack[main] += getFunction("addition", {"INT_NAME1": intName1, "INT_NAME2": intName2}, indents)+"\n"
            else:
                applicationStack[main] += getFunction("addition", {"INT_NAME1": intName1, "INT_NAME2": intName2}, indents)+"\n"
        else:
            print(f"WARN -- \"{parts[0]}\" expected 2 or more arguments, but only got {len(parts)} arguments on line {lines.index(baseLine)}")
            sys.exit()
    
    elif parts[0] == "sub":
        if len(parts)-1 >= 2:
            if embededParse:
                currentStack[main] += getFunction("subtraction", {"INT_NAME1": intName1, "INT_NAME2": intName2}, indents)+"\n"
            else:
                applicationStack[main] += getFunction("subtraction", {"INT_NAME1": intName1, "INT_NAME2": intName2}, indents)+"\n"
        else:
            print(f"WARN -- \"{parts[0]}\" expected 2 or more arguments, but only got {len(parts)} arguments on line {lines.index(baseLine)}")
            sys.exit()

    elif parts[0] == "inc":
        if len(parts)-1 >= 1:
            match parts[1]:
                case "booleans":
                    if not ".data" in currentStack:
                        currentStack[".data"] = getFunction(".data")+"\n"
                    
                    currentStack[".data"] += getFunction("int", {"INT_NAME": "true", "VALUE": "1"}, 1)+"\n"
                    currentStack[".data"] += getFunction("int", {"INT_NAME": "false", "VALUE": "0"}, 1)+"\n"

                    currentStack[".data"] += getFunction("byte", {"BYTE_NAME": "btrue", "VALUE": "1"}, 1)+"\n"
                    currentStack[".data"] += getFunction("byte", {"BYTE_NAME": "bfalse", "VALUE": "0"}, 1)+"\n"

                    userVariables["int"]["true"] = "true"
                    userVariables["int"]["false"] = "false"

                    userVariables["byte"]["btrue"] = "btrue"
                    userVariables["byte"]["bfalse"] = "bfalse"

                case "null":
                    if not ".data" in currentStack:
                        currentStack[".data"] = getFunction(".data")+"\n"

                    currentStack[".data"] += getFunction("byte", {"BYTE_NAME": "null", "VALUE": "0"}, 1)+"\n"

                    userVariables["byte"]["null"] = "null"

                case _:
                    print(f"WARN -- \"{parts[1]}\" is not a valid option of \"{parts[0]}\". occured on line {lines.index(baseLine)}")
                    sys.exit()
        else:
            print(f"WARN -- \"{parts[0]}\" expected 1 or more arguments, but only got {len(parts)} arguments on line {lines.index(baseLine)}")
            sys.exit()

    elif parts[0] == "goto":
        parts = line.strip().split(" ")
        if len(parts)-1 >= 1:
            functionName = f".{parts[1]}"

            if embededParse:
                currentStack[main] += getFunction("goto", {"FUNCTION_NAME": functionName})
            else:
                functionName = f"main{functionName}"
                applicationStack[main] += getFunction("goto", {"FUNCTION_NAME": functionName})
        else:
            print(f"WARN -- \"{parts[0]}\" expected 1 or more arguments, but only got {len(parts)} arguments on line {lines.index(baseLine)}")
            sys.exit()

    elif parts[0] in currentStack:
        parts = line.strip().split(" ", maxsplit=2)

        if parts[1] == "<<":
            parseLine(parts[2].strip().split(" ", maxsplit=1), line.replace(f"{parts[0]} << ", ""), baseLine, lines, 1, parts[0], True)
        elif parts[1] == "run":
            if len(parts)-1 >= 1:
                if embededParse:
                    currentStack[main] += getFunction("run", {"FUNCTION_NAME": "."+parts[0]}, indents)+"\n"
                else:
                    applicationStack[main] += getFunction("run", {"FUNCTION_NAME": "main."+parts[0]}, indents)+"\n"
            else:
                print(f"WARN -- \"{parts[0]}\" expected 2 or more arguments, but only got {len(parts)} arguments on line {lines.index(baseLine)}")
                sys.exit() 
        else:
            print(f"WARN -- Unknown action \"{parts[1]}\" to \"{parts[0]}\" on line {lines.index(baseLine)}")
            sys.exit()

    else:
        print(f"WARN -- \"{parts[0]}\" on line {lines.index(baseLine)+1} does not match any existing syntax.")
        sys.exit()

with open(buildFile+".pok", "r") as file:
    lines = file.readlines()

    for line in lines:
        baseLine = line
        line = line.replace("\n", "")
        #print("Processing line: ", line)


        parts = line.split(" ")
        indents = 0
        if "-" in parts[0]:
            indents = parts[0].count("-")
            parts.pop(0)
        line = " ".join(parts)

        parts = line.strip().split(" ", maxsplit=1)
        parseLine(parts, line, baseLine, lines, indents, mains[-1], False)

finalStack = mergeStacks()
finalStackData = stackToData(finalStack)

writeASM(buildFile, finalStackData)
print("SUCCESS -- Initial pok code converted to assembly")
build(buildFile, " ".join(includes))
print("SUCCESS -- Build process complete")
# input()
