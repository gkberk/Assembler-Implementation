# This is the assembler of our cpu230
# You can find the details in our report and comments below :)
# Sabri Gökberk Yılmaz - Şefika Akman
# 2017400144-2017400192

import sys
instruction_dict = {  # instructions are mapped with their hex values
        "HALT": "1",
        "LOAD": "2",
        "STORE": "3",
        "ADD": "4",
        "SUB": "5",
        "INC": "6",
        "DEC": "7",
        "XOR": "8",
        "AND": "9",
        "OR": "A",
        "NOT": "B",
        "SHL": "C",
        "SHR": "D",
        "NOP": "E",
        "PUSH": "F",
        "POP": "10",
        "CMP": "11",
        "JMP": "12",
        "JZ": "13",
        "JE": "13",
        "JNZ": "14",
        "JNE": "14",
        "JC": "15",
        "JNC": "16",
        "JA": "17",
        "JAE": "18",
        "JB": "19",
        "JBE": "1A",
        "READ": "1B",
        "PRINT": "1C"
    }


def is_a_label(line):  # returns true if the line is a label's beginning
    if line[-1] == ":" and line[-2] != " " and line[-2] != "\t":
        if line[0].isalpha():
            for c in line[1:-1]:
                if not c.isalnum():
                    break
                return True
    return False


def is_register(x):  # returns code of the register if x is a register
    bracbegin = x.find("[")
    bracend = x.find("]")
    if bracbegin>=0 and bracend > 0:
        x = x[bracbegin+1:bracend]
        if x == "0001" or x == "0002" or x == "0003" or x == "0004" or x == "0005" or x == "0006" or x == "0000":
            return x
    regs = {'A':"0001", 'B':"0002", 'C':"0003", 'D':"0004", 'E':"0005", 'S':"0006", "PC":"0000"}
    if x == 'A' or x == 'B' or x =='C' or x =='D' or x == 'E' or x == 'S' or x == 'PC':
        return regs[x]
    else:
        return False


def addressing_mode(operand):  # returns addressing mode of the operand
    braceopen = operand.find("[")
    braceclose = operand.find("]")
    if braceopen >= 0 and braceclose > 0:
        opr = operand[braceopen+1:braceclose]
        r = is_register(opr)
        if r:
            return "10"
        elif len(opr)==4 and opr.isdigit():
            return "11"
    else:
        r = is_register(operand)
        if r:
            return "01"
        else:
            return "00"


def adjust_hex(stri, size):  # it adds 0s in front of a string unless it is not of the desired size and
    # it cuts 0b or 0x from hex and binary numbers' string versions
    if stri[0:2] == "0x":
        stri = stri[2:]
    if size == 4 and len(stri) == 5 and stri[0] == "0":
        stri = stri[1:]
    while len(stri) < size:
        stri = "0" + stri
    return stri


def convert_to_hex(line):  # it converts the given line to hex coding of cpu230
    parsed = line.split()
    instr = parsed[0]
    if instr == "HALT":
        return "040000"
    elif instr == "NOP":
        return "380000"
    operand = parsed[1]
    instr_hex = instruction_dict[instr]
    address_mode = addressing_mode(operand)

    if address_mode == "00":  # if it is immediate
        operand = operand.upper()
        if operand in labels:
            tmp = labels[operand]*3
            oprnum = hex(tmp)
            opr = str(oprnum)
        elif len(operand) == 3 and operand[0] == "\'" and operand[2] == "\'":
            ch = operand[1]
            asci = ord(ch)
            opr = hex(asci)
        else:
            opr = str(operand)
    elif address_mode == "01":  # if it is register
        r = is_register(operand)
        opr = r
    elif address_mode == "10":  # if it is memory address in register
        r = is_register(operand)
        opr = r
    elif address_mode == "11":  # if it is memory address
        bracbegin = operand.find("[")
        bracend = operand.find("]")
        opr = operand[bracbegin+1:bracend]
    tmp1 = int(instr_hex,base=16)  # convert string hex to decimal
    tmp2 = bin(tmp1)  # convert decimal to binary
    tmp3 = str(tmp2) + address_mode  # concatenate binary address mode and opcode
    instr_address = int(tmp3,base=2)  # decimal version of instr_address
    x = hex(instr_address)  # hex version of instr_address

    leftside = adjust_hex(x, 2)
    rigtside = adjust_hex(opr, 4)
    final_version = leftside + rigtside
    return final_version

inputdir = sys.argv[1]
f = open(inputdir, "r")
lines = []
for line in f:  # lines are appended to list after being read from file
    if line[-1] != "\n":
        lines.append(line)
    else:
        lines.append(line[:-1])  # put the lines into a list and cut \n from the end


empty_and_label_count = 0
labels = {}
statements = []
for ind, line in enumerate(lines):  # disregards empty lines, keeps index of labels
    parsed = line.split()
    if parsed == []:  # if it is empty line
        empty_and_label_count += 1
        continue
    elif is_a_label(parsed[0]):  # if it is label
        y = line
        labelname = parsed[0][:-1].upper()
        labels[labelname] = ind - empty_and_label_count
        empty_and_label_count += 1
    else:
        x = line
        line = line.upper()
        statements.append(line)

outputs = []
ind = inputdir.find(".")
outputdir = inputdir[0:ind] + ".bin"
output = open(outputdir, "w")
for op in statements:  # statements are converted to hex, note that labels and empty lines are not in statements
    x = convert_to_hex(op)
    x = x.upper() + "\n"
    outputs.append(x)
    output.write(x)