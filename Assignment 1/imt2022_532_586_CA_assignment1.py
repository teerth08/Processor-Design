import re  # The re module is used to split the instructions into tokens

# The dictionary contains opcodes of various functions used in the code
# the memory location of each label , the number of all the various registers used and
# the binary representation of some immediate fields used in the code.
dictionary = {"addi": "001000", "beq": "000100", "jal": "000011",
              "add": "000000", "lw": "100011", "j": "000010",
              "sw": "101011", "bgtz": "000111",
              "sub": "000000", 
                
              "move1": "00000100000000000000010111",
              "moveend": "0000000000000110", "calc_i": "00000100000000000001101010",
              "calc_j": "00000100000000000001110000","loopend2":"0000000000001000", 
              "sort1": "00000100000000000000100010","sort2": "00000100000000000000101000",
              "loopend1": "0000000000010000","swap":"000000000000000110000",
              
              "4": "0000000000000100", "0": "0000000000000000", "1": "0000000000000001",
              "$s1": "10001", "$s2": "10010", "$s4": "10100", "$s5": "10101", "$s7": "10111",
              "$t1": "01001", "$t2": "01010", "$t3": "01011", "$t4": "01100", "$t5": "01101", "$t7": "01111",
              "$t8": "11000",
              "$0": "00000"
              }
# s is the assembly code
# We are assuming the fact that the compiler during compilation has already stored the location of the various labels
# and the immediate fields in functions like beq. These values are stored in the dictionary.
s = '''addi $s1,$0,0
addi $s2,$0,0
addi $t7,$t2,0
addi $t8,$t3,0
beq $s1,$t1,moveend
lw $s7,0($t2)
sw $s7,0($t3)
addi $t2,$t2,4
addi $t3,$t3,4
addi $s1,$s1,1
j move1
addi $t2,$t7,0
addi $t3,$t8,0
addi $s7,$0,0
addi $s1,$0,0
beq $s1,$t1,loopend1
addi $s2,$s1,1
jal calc_i
addi $t8,$t3,0
add $t8,$t8,$t4
lw $s4,0($t8)
beq $s2,$t1,loopend2
jal calc_j
addi $t8,$t3,0
add $t8,$t8,$t5
lw $s5,0($t8)
sub $s7,$s4,$s5
bgtz $s7 swap
addi $s2,$s2,1
j sort2
addi $s1,$s1,1
j sort1
addi $s7,$0,0
addi $t7,$s4,0
addi $s4,$s5,0
addi $s5,$t7,0
addi $t8,$t3,0
add $t8,$t8,$t4
sw $s4,0($t8)
addi $t8,$t3,0
add $t8,$t8,$t5
sw $s5,0($t8)
addi $s2,$s2,1
j sort2
addi $t4,$0,0
add $t4,$t4,$s1
add $t4,$t4,$s1
add $t4,$t4,$s1
add $t4,$t4,$s1
jr $ra
addi $t5,$0,0
add $t5,$t5,$s2
add $t5,$t5,$s2
add $t5,$t5,$s2
add $t5,$t5,$s2
jr $ra'''

# Splitting the assembly code into instructions
l = s.split('\n')
machine_code = ""  # machine_code holds the entire binary code
for i in range(len(l)):
    machine_temp = ""  # machine_temp holds the binary value of each instruction
    delimeters = r'[ (),]'  # Specifying the delimiters according to which each instruction is split into token
    instruction = re.split(delimeters, l[i])
    instruction = list(filter(lambda x: x != '', instruction))
    # print(instruction)
    if (instruction[0] == "addi"):
        machine_temp += dictionary[instruction[0]] + dictionary[instruction[2]] + dictionary[instruction[1]] + dictionary[instruction[3]]

    elif(instruction[0] == "add"):
        machine_temp += dictionary[instruction[0]] + dictionary[instruction[2]] + dictionary[instruction[3]] +  dictionary[instruction[1]] + "00000100000"   # The last field of the add instruction includes the shamt(00000) and function field

    elif (instruction[0] == "lw"):
        machine_temp += dictionary[instruction[0]] + dictionary[instruction[3]] + dictionary[instruction[1]] + dictionary[instruction[2]]


    elif (instruction[0] == "sw"):
        machine_temp += dictionary[instruction[0]] + dictionary[instruction[3]] + dictionary[instruction[1]] + dictionary[instruction[2]]

    elif (instruction[0] == "sub"):
        machine_temp += dictionary[instruction[0]] + dictionary[instruction[2]] + dictionary[instruction[3]] + dictionary[instruction[1]] + "00000100010" #the last field of the sub instruction includes the shtamt and funct field

    elif (instruction[0] == "jal"):
        machine_temp += dictionary[instruction[0]] + dictionary[instruction[1]]

    elif (instruction[0] == "jr"):
        machine_temp += "00000011111000000000000000001000"  #the "jr $ra" function has the same machine code every time.

    elif (instruction[0] == "j"):
        machine_temp += dictionary[instruction[0]] + dictionary[instruction[1]]

    elif (instruction[0] == "beq"):
        machine_temp += dictionary[instruction[0]] + dictionary[instruction[1]] + dictionary[instruction[2]] + dictionary[instruction[3]]

    elif (instruction[0] == "bgtz"):
        machine_temp += dictionary[instruction[0]] + dictionary[instruction[1]] + dictionary[instruction[2]]

    machine_code += machine_temp
count=0
for i in range(0, len(machine_code), 32):
    count=count+1
    ans = machine_code[i:i + 32]
    print(ans)
    print(count)
