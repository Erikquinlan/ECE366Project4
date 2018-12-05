input_file = open("i_mem.txt", "r")
output_file = open("d_mem_output.txt","w")
print("add, sub, xor, addi, beq, bne, slt, lw, sw")
instList = []
count = 0
for code in input_file:
    line = code.replace("\t", "")
    line = line.replace(" ","")     # remove spaces anywhere in line
    if (line == "\n"):              # empty lines ignored
        continue
    line = line.replace("\n","")
    line = format(int(line,16),"032b")
    instList.append(line)
    
input_file.close()
mem_size = 1024
memList = [0 for i in range(mem_size)]
r = [0,0,0,0,0,0,0,0]
pc = 0
threeCC = 0;    fourCC = 0;        fiveCC = 0                                                           #Variables used for P2 A
flushStall = 0; waitStall = 0;     waitStallChk = -1;   debug = -1                                      #Variables used for P2 B
dm1Block1 = -1; dm1Block2 = -1;    hitA = 0;            missA = 0                                       #Varibales used for P3 A
dm2Block1 = -1; dm2Block2 = -1;    dm2Block3 = -1;      dm2Block4 = -1;    hitB = 0;   missB = 0;       #Variables used for P3 B
faBlockSet = [-1,-1,-1,-1];        hitC = 0;   missC = 0;   nextBlock = 0;                              #Variables used for P3 C
saBlockSet1 = [-1,-1];  saBlockSet2 = [-1,-1];  saBlockSet3 = [-1,-1];  saBlockSet4 = [-1,-1]; 
nxt1 = 0;   nxt2 = 0;   nxt3 = 0;   nxt4 = 0;   hitD = 0;   missD = 0;                                  #Variables used for P3 D
       

while(pc < len(instList)):
    
    waitStallChk = debug
    debug = -1
    
    line = instList[pc]
    if(line == '00010000000000001111111111111111'):
        break;
    
    #r-type
    if(line[0:6] == '000000'):
        fourCC = fourCC + 1;
        if(waitStallChk == line[6:11] or waitStallChk == line[11:16]):
            waitStall = waitStall + 1
        #add
        if(line[26:32] == '100000'):
            #rd = rs + rt
            r[int(line[16:21],2)] = r[int(line[6:11],2)] + r[int(line[11:16],2)]
            pc = pc + 1
        #sub
        elif(line[26:32] == '100010'):
            #rd = rs - rt
            r[int(line[16:21],2)] = r[int(line[6:11],2)] - r[int(line[11:16],2)]
            pc = pc + 1
        #xor
        elif(line[26:32] == '100110'):
            #rd = rs ^ rt
            r[int(line[16:21],2)] = r[int(line[6:11],2)] ^ r[int(line[11:16],2)]
            pc = pc + 1
        #slt
        elif(line[26:32] == '101010'):
            #rd = 1 if(rs < rt)
            if (r[int(line[6:11],2)] < r[int(line[11:16],2)]):
                r[int(line[16:21],2)] = 1
            else:
                r[int(line[16:21],2)] = 0
            pc = pc + 1
                
    #addi
    elif(line[0:6] == '001000'):
        #rt = rs + imm
        fourCC = fourCC + 1
        if(waitStallChk == line[6:11]):
            waitStall = waitStall + 1
        if(int(line[16:32],2) < 30000):
            r[int(line[11:16],2)] = r[int(line[6:11],2)] + int(line[16:32],2)
        else:
            r[int(line[11:16],2)] = r[int(line[6:11],2)] - 4
        pc = pc + 1
        
    #beq
    elif(line[0:6] == '000100'):
        #if(rs == rt) then pc = imm + pc
        threeCC = threeCC + 1
        if(waitStallChk == line[6:11] or waitStallChk == line[11:16]):
            waitStall = waitStall + 1
        if(r[int(line[6:11],2)] is r[int(line[11:16],2)]):
            flushStall = flushStall + 1
            if(int(line[16:32],2) > 32768):
                pc = pc - 65535 + int(line[16:32],2)
            else:   
                pc = pc + int(line[16:32],2) + 1
        else:
            pc = pc + 1
            
    #bne
    elif(line[0:6] == '000101'):
        #if(rs != rt) then pc = imm + pc
        threeCC = threeCC + 1
        if(waitStallChk == line[6:11] or waitStallChk == line[11:16]):
            waitStall = waitStall + 1
        if(r[int(line[6:11],2)] != r[int(line[11:16],2)]):
            flushStall = flushStall + 1
            if(int(line[16:32],2) > 32768):
                pc = pc - 65535 + int(line[16:32],2)
            else:   
                pc = pc + int(line[16:32],2) + 1
        else:
            pc = pc + 1
            
    #lw
    elif(line[0:6] == '100011'):
        #rt = MEM[rs + imm]
        fiveCC = fiveCC + 1
        debug = line[11:16]
        offset = r[int(line[6:11],2)] + int(line[17:32],2) - 8192
        r[int(line[11:16],2)] = memList[offset]
        pc = pc + 1
        
        if(offset // 16 % 2 == 0):
            if(offset // 16 == dm1Block1):
                hitA = hitA + 1
            else:
                missA = missA + 1
                dm1Block1 = offset // 16
        elif(offset // 16 % 2 == 1):
            if(offset // 16 == dm1Block2):
                hitA = hitA + 1
            else:
                missA = missA + 1   
                dm1Block2 = offset // 16
                
        
        if(offset // 8 % 4 == 0):
            if(offset // 8 == dm2Block1):
                hitB = hitB + 1
            else:
                missB = missB + 1
                dm2Block1 = offset // 8
        elif(offset // 8 % 4 == 1):
            if(offset // 8 == dm2Block2):
                hitB = hitB + 1
            else:
                missB = missB + 1   
                dm2Block2 = offset // 8
        elif(offset // 8 % 4 == 2):
            if(offset // 8 == dm2Block3):
                hitB = hitB + 1
            else:
                missB = missB + 1
                dm2Block3 = offset // 8
        elif(offset // 8 % 4 == 3):
            if(offset // 8 == dm2Block4):
                hitB = hitB + 1
            else:
                missB = missB + 1   
                dm2Block4 = offset // 8
                
        if(offset // 8 == faBlockSet[0] or offset // 8 == faBlockSet[1] or offset // 8 == faBlockSet[2] or offset // 8 == faBlockSet[3]):
            hitC = hitC + 1
        else:
            faBlockSet[nextBlock] = offset // 8
            missC = missC + 1
            if(nextBlock < 3):
                nextBlock = nextBlock + 1
            else:
                nextBlock = 0
                
        if(offset // 8 % 4 == 0):
            if(offset // 8 == saBlockSet1[0] or offset // 8 == saBlockSet1[1]):
                hitD = hitD + 1
            else:
                missD = missD + 1
                saBlockSet1[nxt1] = offset // 8
                if(nxt1 == 1):
                    nxt1 = 0
                else:
                    nxt1 = 1
        if(offset // 8 % 4 == 1):
            if(offset // 8 == saBlockSet2[0] or offset // 8 == saBlockSet2[1]):
                hitD = hitD + 1
            else:
                missD = missD + 1
                saBlockSet2[nxt2] = offset // 8
                if(nxt2 == 1):
                    nxt2 = 0
                else:
                    nxt2 = 1
        if(offset // 8 % 4 == 2):
            if(offset // 8 == saBlockSet3[0] or offset // 8 == saBlockSet3[1]):
                hitD = hitD + 1
            else:
                missD = missD + 1
                saBlockSet3[nxt3] = offset // 8
                if(nxt3 == 1):
                    nxt3 = 0
                else:
                    nxt3 = 1
        if(offset // 8 % 4 == 3):
            if(offset // 8 == saBlockSet4[0] or offset // 8 == saBlockSet4[1]):
                hitD = hitD + 1
            else:
                missD = missD + 1
                saBlockSet4[nxt4] = offset // 8
                if(nxt4 == 1):
                    nxt4 = 0
                else:
                    nxt4 = 1
                
                
        
            
        
        
        
    #sw
    elif(line[0:6] == '101011'):
        #MEM[rs + imm] = rt
        fourCC = fourCC + 1
        if(waitStallChk == line[6:11]):
            waitStall = waitStall + 1
        offset = r[int(line[6:11],2)] + int(line[17:32],2) - 8192
        memList[offset] = r[int(line[11:16],2)]
        pc = pc + 1  
        
    else:
        print("Unknown instruction:"+ line)
        break;

    count = count + 1
    

multiCycleCount = threeCC * 3 + fourCC * 4 + fiveCC * 5

pipeCycleCount = 4 + waitStall + flushStall + count

hitRateA = hitA / (hitA + missA)
hitRateB = hitB / (hitB + missB)
hitRateC = hitC / (hitC + missC)
hitRateD = hitD / (hitD + missD)


for j in memList:
    j = format(j, '016b')
    output_file.write(j + '\n')
    
output_stats = open("stat_mem.txt","w")
r[0] = repr(r[0])
r[1] = repr(r[1])
r[2] = repr(r[2])
r[3] = repr(r[3])
r[4] = repr(r[4])
r[5] = repr(r[5])
r[6] = repr(r[6])
r[7] = repr(r[7])
multiCycleCount = repr(multiCycleCount)
waitStall = repr(waitStall)
flushStall = repr(flushStall)
pipeCycleCount = repr(pipeCycleCount)
hitA = repr(hitA)
missA = repr(missA)
hitB = repr(hitB)
missB = repr(missB)
hitC = repr(hitC)
missC = repr(missC)
hitD = repr(hitD)
missD = repr(missD)
hitRateA = repr(hitRateA)
hitRateB = repr(hitRateB)
hitRateC = repr(hitRateC)
hitRateD = repr(hitRateD)
output_stats.write("r0 = " + r[0] + '\n')
output_stats.write("r1 = " + r[1] + '\n')
output_stats.write("r2 = " + r[2] + '\n')
output_stats.write("r3 = " + r[3] + '\n')
output_stats.write("r4 = " + r[4] + '\n')
output_stats.write("r5 = " + r[5] + '\n')
output_stats.write("r6 = " + r[6] + '\n')
output_stats.write("r7 = " + r[7] + '\n\n')

output_stats.write("multicycle cycle count = " + multiCycleCount + '\n')
output_stats.write("pipeline LW hazard stalls = " + waitStall + '\n')
output_stats.write("pipeline Branch flush stalls = " + flushStall + '\n')
output_stats.write("pipeline cycle count = " + pipeCycleCount + '\n\n')

output_stats.write("hitA = " + hitA + '\n')
output_stats.write("missA = " + missA + '\n')
output_stats.write("hitRateA = " + hitRateA + '\n')
output_stats.write("hitB = " + hitB + '\n')
output_stats.write("missB = " + missB + '\n')
output_stats.write("hitRateB = " + hitRateB + '\n')
output_stats.write("hitC = " + hitC + '\n')
output_stats.write("missC = " + missC + '\n')
output_stats.write("hitRateC = " + hitRateC + '\n')
output_stats.write("hitD = " + hitD + '\n')
output_stats.write("missD = " + missD + '\n')
output_stats.write("hitRateD = " + hitRateD + '\n\n')

output_stats.write("DIC count = " + repr(count) + '\n')
output_stats.close()   
print("Final DIC count is: {}".format(count))
input_file.close()
output_file.close()
