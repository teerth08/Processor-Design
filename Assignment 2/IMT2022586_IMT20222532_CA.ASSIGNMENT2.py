import math

IF_ID = []  # [Address of Instruction in decimal, 32 bit Binary Instruction]
ID_Ex = []  # [Control Signal, rs, rt, rd, imm, MemRead, MemWrite, MemtoReg, RegWrite]
Ex_Mem = []  # [ALU Result, MemRead, MemWrite, MemtoReg, RegWrite]
Mem_WB = []  # [


def CalculateStalls(DependentInstructionNo, InstructionNo):
    # print("Dependent Instruction No. = ", DependentInstructionNo)
    global InstructionStalls
    temp_stalls = 4 - abs(InstructionNo - DependentInstructionNo)
    if - InstructionStalls[InstructionNo] + temp_stalls > 0:
        x = - InstructionStalls[InstructionNo] + temp_stalls
    else:
        x = 0
    if DependentInstructionNo < len(InstructionStalls):
        for k in range(DependentInstructionNo):
            InstructionStalls[k] += x

    return x


def getRegValue(RegNumber):
    global Register_File
    for j in Register_File:
        if j[0] == RegNumber:
            return j[2]


def setRegValue(RegNumber, Value):
    global Register_File
    for j in Register_File:
        if j[0] == RegNumber:
            j[2] = Value


def getDataMemValue(MemAddress):
    global Data_Memory
    for j in Data_Memory:
        if j[0] == MemAddress:
            return j[1]


def setDataMemValue(MemAddress, Value):
    global Data_Memory
    for j in Data_Memory:
        if j[0] == MemAddress:
            j[1] = Value


def BinaryToDecimal(imm):
    decimal_value = int(imm, 2)
    if decimal_value & 0x8000:
        decimal_value = -((1 << 16) - decimal_value)
    return decimal_value


def IF(Ipointer):
    global Instruction_Memory
    if Ipointer >= len(Instruction_Memory):
        return []
    else:
        return Instruction_Memory[Ipointer]


def ID(Instruction, Tval):
    if Tval:
        Opcode = Instruction[0:6]
        if Opcode == "000000" or Opcode == "011100":  # R-Format
            # Accessing all the fields of R-Type Instruction
            rs = Instruction[6:11]
            rt = Instruction[11:16]
            rd = Instruction[16:21]
            shamt = Instruction[21:26]
            funct = Instruction[26:]

            # add
            if funct == "100000":
                rs = getRegValue(rs)
                rt = getRegValue(rt)
                CSadd = "010"

                return CSadd, rs, rt, rd, None, 0, 0, 0, 1  # CSadd, rs, rt, rd, imm, MemRead, MemWrite, MemtoReg, RegWrite

            # sub
            elif funct == "100010":
                rs = getRegValue(rs)
                rt = getRegValue(rt)
                CSsub = "011"
                return CSsub, rs, rt, rd, None, 0, 0, 0, 1

            # mul
            elif funct == "000010":
                rs = getRegValue(rs)
                rt = getRegValue(rt)
                CSmul = "000"
                return CSmul, rs, rt, rd, None, 0, 0, 0, 1

        elif Opcode == "000010":
            JumpAddress = Instruction[6:32]

        elif Opcode == "000011":
            JumpAddress = Instruction[6:32]

        else:
            # Accessing all fields for I-Type Instruction
            rs = Instruction[6:11]
            rt = Instruction[11:16]
            imm = Instruction[16:32]

            # For lw
            if Opcode == "100011":
                rs = getRegValue(rs)
                CSadd = "010"
                return CSadd, rs, rt, None, imm, 1, 0, 1, 1

            # For sw
            elif Opcode == "101011":
                rs = getRegValue(rs)
                rt = getRegValue(rt)
                CSadd = "010"
                return CSadd, rs, rt, None, imm, 0, 1, 0, 0

            # addi
            elif Opcode == "001000":
                rs = getRegValue(rs)
                CSadd = "010"
                return CSadd, rs, rt, None, imm, 0, 0, 0, 1

            # For beq
            elif Opcode == "000100" or Opcode == "000111":
                rs = getRegValue(rs)
                rt = getRegValue(rt)
                CSBranch = "111"
                return CSBranch, rs, rt, None, imm, 0, 0, 0, 0

            elif Opcode == "000101":
                rs = getRegValue(rs)
                rt = getRegValue(rt)
                CSBranch = "110"
                return CSBranch, rs, rt, None, imm, 0, 0, 0, 0

    else:
        return []


def Ex(CS, rs, rt, rd, imm, MemRead, MemWrite, MemtoReg, RegWrite):
    if rd:
        if CS == "010":
            z = rs + rt
        elif CS == "011":
            z = rs - rt
        elif CS == "000":
            z = rs * rt
        # imm has no job
        return z, CS, rs, rt, rd, imm, MemRead, MemWrite, MemtoReg, RegWrite  # (Value to return, MemCS, RegCS)

    elif imm:
        # for lw, sw, addi
        if CS == "010":
            imm = BinaryToDecimal(imm)
            z = imm + rs

            return z, CS, rs, rt, rd, imm, MemRead, MemWrite, MemtoReg, RegWrite  # z---> Address rt--->Value

        # For beq, bgtz
        elif CS == "111":
            z = rs - rt
            if z == 0:
                return BinaryToDecimal(imm), CS, rs, rt, rd, imm, MemRead, MemWrite, MemtoReg, RegWrite
            else:
                return 0, CS, rs, rt, rd, imm, MemRead, MemWrite, MemtoReg, RegWrite

        elif CS == "110":
            z = rs - rt
            if z != 0:
                return BinaryToDecimal(imm), CS, rs, rt, rd, imm, MemRead, MemWrite, MemtoReg, RegWrite
            else:
                return 0, CS, rs, rt, rd, imm, MemRead, MemWrite, MemtoReg, RegWrite

    else:
        return []


# rt & imm are not needed
def Mem(Address, CS, rs, rt, rd, imm, Value, MemRead, MemWrite, MemtoReg, RegWrite):
    global Data_Memory
    if MemRead == 1:
        x = getDataMemValue(Address)  # Address--->z--->Ex_Mem[0]
        return x, CS, rs, rt, rd, imm, Address, MemtoReg, RegWrite
    elif MemWrite == 1:
        setDataMemValue(Address, Value)  # Value--->rt--->Ex_Mem[3] Address--->z--->Ex_Mem[0]
        return Value, CS, rs, rt, rd, imm, Address, MemtoReg, RegWrite  # Returning These values just for convinience
    else:
        return Address, CS, rs, rt, rd, imm, Value, MemtoReg, RegWrite  # Value--->z--->Ex_Mem[0], Address--->None   Here Address is Value and Value is Address (For add,addi,sub,etc)


def WB(Value, rt, rd, RegWrite):
    if RegWrite == 1:
        if rd:
            setRegValue(rd, Value)
            print("Writeback Phase", rd, getRegValue(rd))
        else:
            setRegValue(rt, Value)
            print("Writeback Phase", rt,  getRegValue(rt))
    else:
        return


def BreakInstruction(Instruction):
    Opcode = Instruction[0:6]

    # For R-Type
    if Opcode == "000000" or Opcode == "011100":
        rs = Instruction[6:11]
        rt = Instruction[11:16]
        rd = Instruction[16:21]
        return 0, rs, rt, rd

    # For j, jal, jr
    elif Opcode == "000011" or Opcode == "000010":
        return 1,

    # For I-Type
    else:
        rs = Instruction[6:11]
        rt = Instruction[11:16]

        # For addi and lw
        if Opcode == "100011" or Opcode == "001000":
            return 2, rs, rt

        # For sw and beq and bne
        elif Opcode == "101011" or Opcode == "000100" or Opcode == "000101":
            return 3, rs, rt
        else:
            return 4,


def flush():
    global IF_ID
    global ID_Ex
    global Ex_Mem

    IF_ID = []
    ID_Ex = []
    Ex_Mem = []

    return


# Preprocessing

Instruction_Memory = []  # Instruction Memory Format ----> [ Address, Instruction ]
Data_Memory = []  # Data Memory Format ----> [ Address, Data ]

RegModification = {"00000": -1,
                   "00001": -1,
                   "00010": -1,
                   "00011": -1,
                   "00100": -1,
                   "00101": -1,
                   "00110": -1,
                   "00111": -1,
                   "01000": -1,
                   "01001": -1,
                   "01010": -1,
                   "01011": -1,
                   "01100": -1,
                   "01101": -1,
                   "01110": -1,
                   "01111": -1,
                   "10000": -1,
                   "10001": -1,
                   "10010": -1,
                   "10011": -1,
                   "10100": -1,
                   "10101": -1,
                   "10110": -1,
                   "10111": -1,
                   "11000": -1,
                   "11001": -1,
                   "11010": -1,
                   "11011": -1,
                   "11100": -1,
                   "11101": -1,
                   "11110": -1,
                   "11111": -1}
Dependencies = []

# Register File Format ----> [ Register Number, Register Name, Value Stored in Register ]
Register_File = [["00000", "$zero", 0],
                 ["00001", "$at", 0],
                 ["00010", "$v0", 0],
                 ["00011", "$v1", 0],
                 ["00100", "$a0", 0],
                 ["00101", "$a1", 0],
                 ["00110", "$a2", 0],
                 ["00111", "$a3", 0],
                 ["01000", "$t0", 0],
                 ["01001", "$t1", 0],
                 ["01010", "$t2", 0],
                 ["01011", "$t3", 0],
                 ["01100", "$t4", 0],
                 ["01101", "$t5", 0],
                 ["01110", "$t6", 0],
                 ["01111", "$t7", 0],
                 ["10000", "$s0", 0],
                 ["10001", "$s1", 0],
                 ["10010", "$s2", 0],
                 ["10011", "$s3", 0],
                 ["10100", "$s4", 0],
                 ["10101", "$s5", 0],
                 ["10110", "$s6", 0],
                 ["10111", "$s7", 0],
                 ["11000", "$t8", 0],
                 ["11001", "$t9", 0],
                 ["11010", "$k0", 0],
                 ["11011", "$k1", 0],
                 ["11100", "$gp", 0],
                 ["11101", "$sp", 0],
                 ["11110", "$pf", 0],
                 ["11111", "$ra", 0]]

Machine_Code = '''00100000000011100000000000000000
00100001010011110000000000000000
00100001011110000000000000000000
10001101010011000000000000000000
00100001110011100000000000000001
00100000000011010000000000000001
00010001100000000000000000000110
01110001101011000110100000000010
00100001100011001111111111111111
00010101100000001111111111111101
10101101011011010000000000000000
00100001010010100000000000000100
00100001011010110000000000000100
00100001100011000000000000000001
10101101011011000000000000000000
00010101110010011111111111110011
00100001111010100000000000000000
00100011000010110000000000000000'''

Machine_Code = Machine_Code.split("\n")

InstructionStalls = []  # Calculates the number of stalls after a particular instruction

for i in range(len(Machine_Code)):
    InstructionStalls.append(0)

for i in Machine_Code:
    Values = BreakInstruction(i)
    if Values[0] == 0:
        if RegModification[Values[1]] != -1:
            Dependencies.append([Machine_Code.index(i), RegModification[Values[1]], Values[1]])

        if RegModification[Values[2]] != -1:
            Dependencies.append([Machine_Code.index(i), RegModification[Values[2]], Values[2]])

        RegModification[Values[3]] = Machine_Code.index(i)

    elif Values[0] == 2:
        if RegModification[Values[1]] != -1:
            Dependencies.append([Machine_Code.index(i), RegModification[Values[1]], Values[1]])

        RegModification[Values[2]] = Machine_Code.index(i)

    elif Values[0] == 3:
        # print(Values[1], Values[2])
        if RegModification[Values[1]] != -1:
            Dependencies.append([Machine_Code.index(i), RegModification[Values[1]], Values[1]])

        if RegModification[Values[2]] != -1:
            Dependencies.append([Machine_Code.index(i), RegModification[Values[2]], Values[2]])
    # print(RegModification)

New_Dependencies = []  # ---> [ Dependent Instruction, Instruction on which it depends, Which Register it Depends on]
for i in range(len(Dependencies)):
    if 1 <= abs(Dependencies[i][0] - Dependencies[i][1]) <= 3:
        New_Dependencies.append(Dependencies[i])
Temp = []
New_Dependencies1 = []
# print(New_Dependencies)
for i in range(len(New_Dependencies)):
    for j in range(i+1, len(New_Dependencies)):
        if New_Dependencies[i][0] == New_Dependencies[j][0]:
            Temp.append(i)

for i in range(len(New_Dependencies)):
    if i not in Temp:
        New_Dependencies1.append(New_Dependencies[i])

print(Dependencies)
print(New_Dependencies1)


# print(RegModification)


# Non Pipelined Part
while len(Machine_Code) != 0:
    Starting_Address = int(input("Enter Starting Address of Instruction"))
    N = int(input("Enter Number of instructions"))
    for i in range(N):
        Instruction_Memory.append([Starting_Address, Machine_Code[0]])
        Starting_Address += 4
        del Machine_Code[0]

for i in Instruction_Memory:
    print(i)

# Completing the setup before the main execution
PC = int(input("Enter Starting address"))
Ending_Address = int(input("Enter the ending address of this code"))
pointer = 0  # Keeps track of the instruction to be executed
flag = True

# Setting up the data memory

Starting_AddressIN = int(input("Enter Starting Address of Inputs"))
setRegValue("01010", Starting_AddressIN)
N = int(input("Enter number of Inputs"))
for i in range(N):
    input_temp = int(input("Enter the number"))
    Data_Memory.append([Starting_AddressIN, input_temp])
    Starting_AddressIN += 4

Starting_AddressOUT = int(input("Enter Starting Address of Output)"))
setRegValue("01011", Starting_AddressOUT)
for i in range(N):
    Data_Memory.append([Starting_AddressOUT, 0])
    Starting_AddressOUT += 4
# print(Data_Memory)
# Setting up the register file

# Non - Pipelined Part Ended

setRegValue("01001", N)


def findDependencies(Ipointer):
    global New_Dependencies1
    for k in New_Dependencies1:
        # print("find Dependencies function", k[0])
        if k[0] == Ipointer:
            temp = k
            # New_Dependencies1.remove(k)
            return temp[1], temp[2]
    return


def updateStalls(currentPointer,destinationPointer):
    global InstructionStalls
    a = min(currentPointer, destinationPointer)
    b = max(currentPointer, destinationPointer)
    for k in range(len(InstructionStalls)):
        if k > a:
            InstructionStalls[k] = 0


pointer = 0
IF_Tval = True
ID_Tval = True
stalls = 0
TotalStalls = 0
FetchedInstruction = []
DecodedInstruction = []
ExecutedResult = []
Memory = []
DependedInstruction = None

# print(getRegValue("01001"))
# setRegValue("01000", 4)
# setRegValue("01100", 4)

while pointer <= len(Instruction_Memory) + 8:

    DependedInstruction = None  # Made None So as not to retain the previous Value
    print("Pointer Value = ", pointer)
    # print(New_Dependencies1, IF_Tval)
    # DecodedInstruction -----> ID -----> Control Signals
    FetchedInstruction = IF(pointer)
    print("FetchedInstruction", FetchedInstruction)
    if IF_Tval:
        DependedInstruction = findDependencies(pointer)
        print("Dependend Instruction", DependedInstruction)

    if DependedInstruction:
        stalls = CalculateStalls(pointer, DependedInstruction[0])
        print("Stalls=", stalls)
        TotalStalls += stalls

    if len(IF_ID) != 0:
        DecodedInstruction = ID(IF_ID[1], ID_Tval)  # 3  This generates all the control signals
        print("Decoded Instruction", DecodedInstruction)
    if len(ID_Ex) != 0:
        ExecutedResult = Ex(ID_Ex[0], ID_Ex[1], ID_Ex[2], ID_Ex[3], ID_Ex[4], ID_Ex[5], ID_Ex[6], ID_Ex[7], ID_Ex[8])
        print("Execution Stage", ExecutedResult)
    else:
        ExecutedResult = []

    # Ex/Mem
    if len(Ex_Mem) != 0:
        Memory = Mem(Ex_Mem[0], Ex_Mem[1], Ex_Mem[2], Ex_Mem[3], Ex_Mem[4], Ex_Mem[5], Ex_Mem[3], Ex_Mem[6], Ex_Mem[7],
                     Ex_Mem[8], Ex_Mem[9])
        print("Memory", Memory)

        # Pointer Update
        if Memory[1] == "111" or Memory[1] == "110":
            if Memory[0] != 0:

                # Updating Stalls correctly
                current_pointer = pointer
                destination_pointer = pointer + Memory[0] - 2
                print("Updating Stalls", current_pointer, destination_pointer)
                print(InstructionStalls)
                updateStalls(current_pointer, destination_pointer)
                print(InstructionStalls)

                pointer += Memory[0] - 3
                print("Jumping", Memory[0], "instructions")
                print("Flushing the functions")
                flush()
                print(FetchedInstruction, DecodedInstruction, ExecutedResult)
                print("After Flush", IF_ID, ID_Ex, Ex_Mem)
                FetchedInstruction = []
                DependedInstruction = []
                ExecutedResult = []
            else:
                print("Flushing Not Done")

    # WB
    if len(Mem_WB):
        WB(Mem_WB[0], Mem_WB[3], Mem_WB[4], Mem_WB[8])

    IF_ID = FetchedInstruction
    ID_Ex = DecodedInstruction
    Ex_Mem = ExecutedResult  # 2
    Mem_WB = Memory

    if stalls:
        IF_Tval = False
        ID_Tval = False
        stalls -= 1
    else:
        IF_Tval = True
        ID_Tval = True

    if IF_Tval:  # If IF_Tval is true only then fetch the next instruction. Else keep fetching the same instruction
        # print("Pointer Value 2 = ",pointer)
        pointer += 1

    # print("Last Line", IF_ID)

for i in Register_File:
    print(i)

# print(InstructionStalls)

print(Data_Memory)