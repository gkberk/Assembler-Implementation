# This is the executor of our cpu230
# You can find the details in our report and comments below :)
# Sabri Gökberk Yılmaz - Şefika Akman
# 2017400144-2017400192

import sys
memory = []
for i in range(2**16):  # memory is initiated here by "00"s
    memory.append("00")
inputdir = sys.argv[1]
dotind = inputdir.find(".")
outputdir = inputdir[0:dotind] + ".txt"
f = open(inputdir)
output = open(outputdir, "w")

lines = []
for ind, line in enumerate(f):  # instructions are stored into memory here
    x = line.split()
    lines.append(line)
    line = line.split()[0]
    memory[ind*3] = line[4:]
    memory[ind*3+1] = line[2:4]
    memory[ind*3+2] = line[0:2]

A, B, C, D, E, PC = 0, 0, 0, 0, 0, 0
S = 2**16-1  # Stack pointer initiated here, at the highest memory address
ZF, CF, SF = 0, 0, 0  # ZF, CF, SF are initiated here
Halt = False  # Halt is the boolean that represents if the halt command is invoked


registers = {"0001": "A", "0002": "B", "0003": "C", "0004": "D", "0005": "E", "0006": "S"}
# registers are mapped with their binary codes


# it returns the negated version of hex string in binary
def not_helper(hexa):
    result = ""
    dec = int(hexa, base=16)
    binar = bin(dec)
    binar = adjust_digits(binar, 16)
    for ch in binar:
        if ch == "0":
            result += "1"
        elif ch == "1":
            result += "0"
    return result


# it adds 0s in front of a string unless it is not of the desired size and
# it cuts 0b or 0x from hex and binary numbers' string versions
def adjust_digits(str, size):
    if str[0:2] == "0x" or str[0:2] == "0b":
        str = str[2:]
    while len(str) < size:
        str = "0" + str
    return str


# when halt is called, sets the global Halt variable
def halt_command():  # 1
    global Halt
    Halt = True


# when load is called
def load_command(address_mode, operand):  # 2
    global A, B, C, D, E, S, memory
    if address_mode == "00":  # if immediate
        A = int(operand, base=16)
    elif address_mode == "01":  # if register
        if operand == "0002":
            A = B
        elif operand == "0003":
            A = C
        elif operand == "0004":
            A = D
        elif operand == "0005":
            A = E
        elif operand == "0006":
            A = S
    elif address_mode == "10":  # if address in register
        if operand == "0002":
            hexA = memory[B+1] + memory[B]
            A = int(hexA, base=16)
        elif operand == "0003":
            hexA = memory[C+1] + memory[C]
            A = int(hexA, base=16)
        elif operand == "0004":
            hexA = memory[D+1] + memory[D]
            A = int(hexA, base=16)
        elif operand == "0005":
            hexA = memory[E+1] + memory[E]
            A = int(hexA, base=16)
        elif operand == "0006":
            A = memory[S+1] + memory[S]
    elif address_mode == "11":  # if address
        hexversion = memory[int(operand, base=16)+1] + memory[int(operand, base=16)]
        A = int(hexversion)


# when store is called, stores the operand into A
def store_command(address_mode, operand):  # 3
    global memory, A
    if address_mode == "01":  # if register
        regname = registers[operand]
        globals()[regname] = A
    elif address_mode == "10":  # if address in register
        regname = registers[operand]
        address = globals()[regname]
        hexA = adjust_digits(hex(A), 4)
        memory[address+1] = hexA[:2]
        memory[address] = hexA[2:]
    elif address_mode == "11":  # if address
        address = int(operand, base=16)
        hexA = adjust_digits(hex(A), 4)
        memory[address+1] = hexA[:2]
        memory[address] = hexA[2:]


# when add is called, stores the result into A
def add_command(address_mode, operand):  # 4
    global A, ZF, CF, SF, memory
    if address_mode == "00":  # if immediate
        opr = int(operand, base=16)
    elif address_mode == "01":  # if register
        regname = registers[operand]
        opr = globals()[regname]
    elif address_mode == "10":  # if address in register
        regname = registers[operand]
        address = globals()[regname]
        opr = int(memory[address+1]+memory[address],base=16)
    elif address_mode == "11":  # if address
        address = int(operand, base=16)
        opr = int(memory[address+1]+memory[address], base=16)

    decresult = A + opr
    strbinresult = str(bin(decresult))[2:]

    if len(strbinresult) == 17:
        CF = 1
        strbinresult = strbinresult[1:]
    else:
        CF = 0
        strbinresult = adjust_digits(strbinresult, 16)

    if int(strbinresult, base=2) == 0:
        ZF = 1
    else:
        ZF = 0

    if strbinresult[0] == "1":
        SF = 1
    else:
        SF = 0
    A = int(strbinresult, base=2)


# when sub is called, it uses not_helper, adds 1 and then calls add function stores the result into A
def sub_command(address_mode, operand):  # 5
    global memory, A
    if address_mode == "00":
        opr = int(operand, base=16)
    elif address_mode == "01":
        regname = registers[operand]
        opr = globals()[regname]
    elif address_mode == "10":
        regname = registers[operand]
        address = globals()[regname]
        opr = int(memory[address+1]+memory[address], base=16)
    elif address_mode == "11":
        address = int(operand, base=16)
        opr = int(memory[address+1]+memory[address])
    negatedopr = not_helper(hex(opr))
    decopr = int(negatedopr, base=2)+1
    hexopr = hex(decopr)
    add_command("00", str(hexopr)[2:])


# when inc is called, increments it
def inc_command(address_mode, operand):  # 6
    global memory, ZF, CF, SF
    result = 0
    if address_mode == "00":
        decopr = int(operand, base=16)
        decopr +=1
        result = decopr
    elif address_mode == "01":
        regname = registers[operand]
        opr = globals()[regname]
        opr += 1
        globals()[regname]=opr
        result = opr
    elif address_mode == "10":
        regname = registers[operand]
        address = globals()[regname]
        opr = int(memory[address+1] + memory[address], base=16)
        opr += 1
        hexopr = hex(opr)[2:]
        memory[address] = hexopr[2:]
        memory[address+1] = hexopr[:2]
        result = opr
    elif address_mode == "11":
        address = int(operand, base=16)
        opr = int(memory[address+1] + memory[address], base=16)
        opr += 1
        hexopr = hex(opr)[2:]
        memory[address] = hexopr[2:]
        memory[address+1] = hexopr[:2]
        result = opr
    if result == 0:
        ZF = 1
    else:
        ZF = 0

    result = str(bin(result)[2:])
    if len(result) == 17:
        CF = 1
        result = result[1:]
    else:
        CF = 0

    if result[0] == "1":
        SF = 1
    else:
        SF = 0


# when dec is called, decrements it
def dec_command(address_mode, operand):  # 7
    global memory, ZF, CF, SF, A
    result = 0
    if address_mode == "00":
        opr = int(operand, base=16)
        tmp = A
        A = opr
        add_command("00", "FFFF")
        result = A
        A = tmp
    elif address_mode == "01":
        regname = registers[operand]
        opr = globals()[regname]
        tmp = A
        A = opr
        add_command("00", "FFFF")
        opr = A
        A = tmp
        globals()[regname] = opr
        result = opr
    elif address_mode == "10":
        regname = registers[operand]
        address = globals()[regname]
        opr = int(memory[address+1] + memory[address], base=16)
        tmp = A
        A = opr
        add_command("00", "FFFF")
        opr = A
        A = tmp
        hexopr = hex(opr)[2:]
        memory[address] = hexopr[2:]
        memory[address + 1] = hexopr[:2]
        result = opr
    elif address_mode == "11":
        address = int(operand, base=16)
        opr = int(memory[address+1] + memory[address], base=16)
        tmp = A
        A = opr
        add_command("00", "FFFF")
        opr = A
        A = tmp
        hexopr = hex(opr)[2:]
        memory[address] = hexopr[2:]
        memory[address + 1] = hexopr[:2]
        result = opr

    if result == 0:
        ZF = 1
    else:
        ZF = 0

    result = str(bin(result)[2:])
    if len(result) == 17:
        CF = 1
        result = result[1:]
    else:
        CF = 0

    if result[0] == "1":
        SF = 1
    else:
        SF = 0


# it returns the XORed binary result of A's binary value and the hexa's binary value
def xor_helper(hexa):
    global A
    result = ""
    binaryA = adjust_digits(bin(A), 16)
    decversion = int(hexa, base=16)
    binar = bin(decversion)
    binaryOperand = adjust_digits(binar, 16)
    for i in range(len(binaryOperand)):
        if binaryA[i] == binaryOperand[i]:
            result += "0"
        elif binaryA[i] != binaryOperand[i]:
            result += "1"
    return result


# when xor is called, it uses xor_helper
def xor_command(address_mode, operand): # 8
    global A, ZF, SF, memory
    xored = ""
    if address_mode == "00":
        xored = xor_helper(operand)
    elif address_mode == "01":
        regname = registers[operand]
        opr = globals()[regname]
        xored = xor_helper(hex(opr))
    elif address_mode == "10":
        regname = registers[operand]
        address = globals()[regname]
        opr = memory[address+1] + memory[address]
        xored = xor_helper(opr)
    elif address_mode == "11":
        address = int(operand, base=16)
        opr = memory[address+1] + memory[address]
        xored = xor_helper(opr)
    A = int(xored, base=2)
    if A == 0:
        ZF = 1
    else:
        ZF = 0

    if xored[0] == "1":
        SF = 1
    else:
        SF = 0


# it returns bitwise and operation between two operands' binary representations
def bit_and(opr1, opr2):
    opr1 = adjust_digits(opr1, 16)
    opr2 = adjust_digits(opr2, 16)
    result = ""
    for i in range(len(opr1)):
        if opr1[i] == "1" and opr2[i] == "1":
            result += "1"
        else:
            result += "0"
    return result


# when and is called
def and_command(address_mode, operand): # 9
    result = ""
    global A, memory, SF, ZF
    if address_mode == "00":
        decversion = int(operand, base=16)
        binversion = bin(decversion)
        binA = bin(int(A))
        result = bit_and(binA, binversion)
    elif address_mode == "01":
        regname = registers[operand]
        opr = globals()[regname]
        decopr = int(opr, base=16)
        binopr = bin(decopr)
        binA = bin(int(A))
        result = bit_and(binA, binopr)
    elif address_mode == "10":
        regname = registers[operand]
        address = globals()[regname]
        opr = memory[address+1] + memory[address]
        decopr = int(opr, base=16)
        binopr = bin(decopr)
        binA = bin(int(A))
        result = bit_and(binA, binopr)
    elif address_mode == "11":
        address = int(operand, base=16)
        opr = memory[address+1] + memory[address]
        binA = bin(int(A))
        decopr = int(opr, base=16)
        binopr = bin(decopr)
        result = bit_and(binA, binopr)
    A = int(result, base=2)
    if A == 0:
        ZF = 1
    else:
        ZF = 0

    if result[0] == "1":
        SF = 1
    else:
        SF = 0


# it returns bitwise or operation between A register's binary value and operand
def or_helper(operand):
    global A
    result = ""
    binA = bin(A)
    binA = adjust_digits(binA,16)
    decopr = int(operand, base=16)
    binopr = bin(decopr)
    binopr = adjust_digits(binopr,16)
    for i in range(len(binopr)):
        if binopr[i] == "1" or binA[i] == "1":
            result += "1"
        else:
            result += "0"
    return result


# when or is called
def or_command(address_mode, operand):  # A
    global A, memory, ZF, SF
    if address_mode == "00":
        result = or_helper(operand)
    elif address_mode == "01":
        regname = registers[operand]
        decopr = globals()[regname]
        result = or_helper(hex(decopr))
    elif address_mode == "10":
        regname = registers[operand]
        address = globals()[regname]
        opr = memory[address+1] + memory[address]
        result = or_helper(opr)
    elif address_mode == "11":
        address = int(operand, base=16)
        opr = memory[address+1] + memory[address]
        result = or_helper(opr)
    A = int(result, base=2)

    if A == 0:
        ZF = 1
    else:
        ZF = 0

    if result[0] == "1":
        SF = 1
    else:
        SF = 0


# when not is called
def not_command(address_mode, operand): # B
    result = 0
    global ZF, SF, memory, A
    if address_mode == "00":
        result = not_helper(operand)
    elif address_mode == "01":
        regname = registers[operand]
        opr = globals()[regname]
        result = not_helper(hex(opr))
    elif address_mode == "10":
        regname = registers[operand]
        address = globals()[regname]
        opr = memory[address+1] + memory[address]
        result = not_helper(opr)
    elif address_mode == "11":
        adr = int(operand, base=16)
        opr = memory[adr+1] + memory[adr]
        result = not_helper(opr)
    A = int(result)
    if A == 0:
        ZF = 1
    else:
        ZF = 0
    if result[0] == "1":
        SF = 1
    else:
        SF = 0


# when shl is called
def shl_command(operand):  # C, register only
    global A,B,C,D, ZF, CF, SF
    regname = registers[operand]
    opr = globals()[regname]
    opr = adjust_digits(str(bin(opr)), 16)
    opr += "0"
    if opr[0] == "1":
        CF = 1
    else:
        CF = 0
    opr = opr[1:]
    if int(opr, base=2) == 0:
        ZF = 1
    else:
        ZF = 0
    if opr[0] == "1":
        SF = 1
    else:
        SF = 0
    globals()[regname] = int(opr, base=2)


# when shr is called
def shr_command(operand):  # D, register only
    global ZF, SF
    regname = registers[operand]
    val = globals()[regname]
    val = val // 2
    if val == 0:
        ZF = 1
    else:
        ZF = 0
    binval = adjust_digits(bin(val),16)
    if binval[0] == "1":
        SF = 1
    else:
        SF = 0
    globals()[regname] = val


# when push is called, it pushes the value in register to stack decreases S
def push_command(operand):  # F
    global S, memory
    regname = registers[operand]
    val = globals()[regname]
    val = adjust_digits(hex(val), 4)
    memory[S] = val[0:2]
    memory[S-1] = val[2:4]
    S -= 2


# when pop is called, it pops from stack and puts into register, increases S
def pop_command(operand): # 10
    global S, memory
    part1 = memory[S+2]
    part2 = memory[S+1]
    regname = registers[operand]
    globals()[regname] = int(part1+part2, base=16)
    S += 2


# when cmp is called, it compares operand with A and sets the flags accordingly
def cmp_command(address_mode, operand): # 11
    global A, memory, PC
    if address_mode == "00":
        opr = int(operand, base=16)
    elif address_mode == "01":
        regname = registers[operand]
        opr = globals()[regname]
    elif address_mode == "10":
        regname = registers[operand]
        address = globals()[regname]
        opr = int(memory[address+1]+memory[address], base=16)
    elif address_mode == "11":
        address = int(operand, base=16)
        opr = int(memory[address+1]+memory[address], base=16)
    tmp = A
    sub_command("00", str(hex(opr))[2:])
    A = tmp


# when jmp is called, sets the PC no matter what
def jmp_command(operand): # 12
    global PC
    address = int(operand, base=16)
    PC = address


# when jmp is called, sets the PC when ZF is 1
def jz_je_command(operand):  # 13
    global ZF, PC
    if ZF == 1:
        PC = int(operand, base=16)
    else:
        PC += 3


# when jmp is called, sets the PC when ZF is 0
def jnz_jne_command(operand):  # 14
    global ZF, PC
    if ZF == 0:
        PC = int(operand, base=16)
    else:
        PC += 3


# when jmp is called, sets the PC when CF is 1
def jc_command(operand): # 15
    global CF, PC
    if CF == 1:
        PC = int(operand, base=16)
    else:
        PC += 3


# when jmp is called, sets the PC when CF is 0
def jnc_command(operand): # 16
    global CF, PC
    if CF == 0:
        PC = int(operand, base=16)
    else:
        PC += 3


# when jmp is called, sets the PC when SF is 0
def ja_command(operand):  # 17
    global SF, PC
    if SF == 0:
        PC = int(operand, base=16)
    else:
        PC += 3


# when jmp is called, sets the PC when SA is 0 or ZF is 1
def jae_command(operand): # 18
    global ZF, SF, PC
    if SF == 0 or ZF == 1:
        PC = int(operand, base=16)
    else:
        PC += 3


# when jmp is called, sets the PC when SF is 1
def jb_command(operand): # 19
    global SF, PC
    if SF == 1:
        PC = int(operand, base=16)
    else:
        PC += 3


# when jmp is called, sets the PC when SF is 1 or ZF is 1
def jbe_command(operand): # 1A
    global SF, PC, ZF
    if SF == 1 or ZF == 1:
        PC = int(operand, base=16)
    else:
        PC += 3


# it reads from user when read is called
def read_command(address_mode, operand):  # 1B
    global memory
    x = input("Enter an ASCII character: ")
    val = ord(x)
    if address_mode == "01":
        regname = registers[operand]
        globals()[regname] = val
    elif address_mode == "10":
        regname = registers[operand]
        address = globals()[regname]
        y = adjust_digits(hex(val),2)
        memory[address] = y
    elif address_mode == "11":
        address = int(operand, base=16)
        y = adjust_digits(hex(val), 2)
        memory[address] = y


# it prints the char value according to ASCII table, converts number to ASCII when print is called
def print_command(address_mode, operand): # 1C
    global memory, output
    if address_mode == "00":
        val = int(operand, base=16)
    elif address_mode == "01":
        regname = registers[operand]
        val = globals()[regname]
    elif address_mode == "10":
        regname = registers[operand]
        address = globals()[regname]
        val = int(memory[address], base=16)
    elif address_mode == "11":
        address = int(operand, base=16)
        val = int(memory[address], base=16)
    asc = chr(val)
    output.write(asc + "\n")


# it analyzes the line and returns opcode, address mode and operand seperately
def line_analyze(line):
    first = line[:2]
    second = line[2:]
    intversion = int(first, base=16)
    binversion = bin(intversion)
    strversion = adjust_digits(str(binversion),8)
    opcode = strversion[:6]
    opcode = int(opcode, base=2)
    opcode = adjust_digits(str(hex(opcode)), 2)
    address_mode = strversion[6:]

    if len(second) == 5 and second[0] == "0":
        second = second[1:]
    operand = second

    return opcode, address_mode, operand


# it runs the program by first analyzing the line then calling the relevant function according to opcode with address
# mode and operand, it is called for every line in .asm folder
def program_runner():
    global PC, memory, counter
    instruction = memory[PC+2] + memory[PC+1] + memory[PC]
    opcode, address_mode, operand = line_analyze(instruction)
    if opcode == "01":
        halt_command()
        PC += 3
    elif opcode == "02":
        load_command(address_mode, operand)
        PC += 3
    elif opcode == "03":
        store_command(address_mode, operand)
        PC += 3
    elif opcode == "04":
        add_command(address_mode, operand)
        PC += 3
    elif opcode == "05":
        sub_command(address_mode, operand)
        PC += 3
    elif opcode == "06":
        inc_command(address_mode, operand)
        PC += 3
    elif opcode == "07":
        dec_command(address_mode, operand)
        PC += 3
    elif opcode == "08":
        xor_command(address_mode, operand)
        PC += 3
    elif opcode == "09":
        and_command(address_mode, operand)
        PC += 3
    elif opcode == "0A" or opcode == "0a":
        or_command(address_mode, operand)
        PC += 3
    elif opcode == "0B" or opcode == "0b":
        not_command(address_mode, operand)
        PC += 3
    elif opcode == "0C" or opcode == "0c":
        shl_command(operand)
        PC += 3
    elif opcode == "0D" or opcode == "0d":
        shr_command(operand)
        PC += 3
    elif opcode == "0E" or opcode == "0e":
        PC += 3
    elif opcode == "0F" or opcode == "0f":
        push_command(operand)
        PC += 3
    elif opcode == "10":
        pop_command(operand)
        PC += 3
    elif opcode == "11":
        cmp_command(address_mode, operand)
        PC += 3
    elif opcode == "12":
        jmp_command(operand)
    elif opcode == "13":
        jz_je_command(operand)
    elif opcode == "14":
        jnz_jne_command(operand)
    elif opcode == "15":
        jc_command(operand)
    elif opcode == "16":
        jnc_command(operand)
    elif opcode == "17":
        ja_command(operand)
    elif opcode == "18":
        jae_command(operand)
    elif opcode == "19":
        jb_command(operand)
    elif opcode == "1A" or opcode == "1a":
        jbe_command(operand)
    elif opcode == "1B" or opcode == "1b":
        read_command(address_mode, operand)
        PC += 3
    elif opcode == "1C" or opcode == "1c":
        print_command(address_mode, operand)
        PC += 3


# this loop runs the program actually, as long as the Halt is not set True or PC is not at the end of instructions.
while not Halt and PC <= len(lines)*3:
    program_runner()



