from math import ceil,pow ,floor
from Entries_classes import TLBE,PTE
from ReplacementPolicy import replacement_PT,replacement_TLB
TIME_STAMP=0
HDD_STORAGE,RAM_STORAGE,SWAP_STORAGE=[],[],[]
HDD_MAP,PT_MAP,TLB_MAP,SWAP_MAP,FIRST_TIME={},{},{},{},{}
hdd_size,swap_size,ram_size,page_size,tlb_size,replace_policy=1024,256,64,4,4,1
page_frame_LIMIT=ram_size//page_size
page_block_LIMIT=hdd_size//page_size
swap_limit=swap_size//page_size

tlb_hit_summary,tlb_miss_summary,page_fault_summary={},{},{}
page_faults,tlb_misses,tlb_hits=0,0,0

def TakeInput():    
    global  hdd_size,swap_size,ram_size,page_size,tlb_size,replace_policy,page_frame_LIMIT,page_block_LIMIT
    print("Enter the following 6 parameter. Example [1024 256 64 16 5 1] meaning [1MB 256KB 64KB 16KB 5 FIFO]")
    print(  "   1.  Size of HDD in KB"  )
    print(  "   2.  Size of Swap size in KB"  )
    print(  "   3.  Size of ram in KB")
    print(  "   4.  Page size in KB"  )
    print(  "   5.  Number of tlb entries"  )
    print(  "   6.  Replacement policy [0 => LRU ; 1 => FIFO ; 2 =>OPT]" )
    INPUT=list(map(int,input().split()))
    hdd_size,swap_size, ram_size,page_size, tlb_size,replace_policy=INPUT[0],INPUT[1],INPUT[2],INPUT[3],INPUT[4],INPUT[5]
    page_frame_LIMIT=ram_size//page_size
    Page_block_LIMIT=hdd_size//page_size
    swap_limit=swap_size//page_size

def Initializing():
    global HDD_STORAGE,RAM_STORAGE,HDD_MAP,PT_MAP,TLB_MAP
    global  hdd_size,swap_size,ram_size,page_size,tlb_size,replace_policy,page_frame_LIMIT,page_block_LIMIT
    HDD_STORAGE=["*"]*hdd_size

def Allocate_Memory(file_name):
    global HDD_STORAGE,RAM_STORAGE,HDD_MAP,PT_MAP,TLB_MAP
    global  hdd_size,swap_size,ram_size,page_size,tlb_size,replace_policy,page_frame_LIMIT,page_block_LIMIT
    free_pointer=0 #points to next free page_block in HDD
    f=open(file_name,'r')
    lines=f.readlines()
    for line in lines:
        line=line.strip().split(" ")
        pid,req_Memory=int(line[0]),int(line[1])
        #filling data in HDD
        req_pages=req_Memory//page_size
        if(req_Memory > (req_Memory//page_size)*page_size):
            req_pages+=1
        for i in range(free_pointer,free_pointer+req_Memory):
            HDD_STORAGE[i]=i-free_pointer
        #updating HDD_MAP
        HDD_MAP[pid]=[]
        for i in range(req_pages):
            HDD_MAP[pid].append(free_pointer+i*page_size)
        free_pointer+=req_pages*page_size
    f.close()
    # print(HDD_STORAGE)
    # print(HDD_MAP)
    

def Accese_Memory(file_name):
    global HDD_STORAGE,RAM_STORAGE,HDD_MAP,PT_MAP,TLB_MAP,TIME_STAMP,SWAP_MAP,SWAP_STORAGE
    global  hdd_size,swap_size,ram_size,page_size,tlb_size,replace_policy,page_frame_LIMIT,page_block_LIMIT,swap_limit    
    global tlb_hit_summary,tlb_miss_summary,page_fault_summary,page_faults,tlb_misses,tlb_hits

    #initializing summary varible
    for i in HDD_MAP.keys():
        page_fault_summary[i],tlb_hit_summary[i],tlb_miss_summary[i]=0,0,0

    f=open(file_name,'r')
    lines=f.readlines()
    for line in lines:
        TIME_STAMP+=1
        line=line.strip().split(" ")
        pid,V_Address=int(line[0]),int(line[1])
        vpn=V_Address//page_size
        offset=V_Address-vpn*page_size

        if(pid not in HDD_MAP):
            print("INVALID PID")
            continue
        if(vpn>=len(HDD_MAP[pid])):
            print("INVALID ADDRESS")
            continue

        #Searching in TLB
        if pid not in FIRST_TIME:
            FIRST_TIME[pid]=TIME_STAMP
            print("PID: "+str(pid)+"    |   V_Address     "+str(V_Address)+"   |   PROCESS AWOKE")
            count=page_frame_LIMIT-len(RAM_STORAGE)
            count1=swap_limit-len(SWAP_STORAGE)
            req_pages=len(HDD_MAP[pid])
            print("NEEDED : "+str(req_pages)+"      RAM SPACE: "+str(count)+" / "+str(page_frame_LIMIT))
            print("NEEDED : "+str(req_pages)+"      SWAP SPACE: "+str(count1)+" / "+str(swap_limit))

            if(count>0):
                print("---------------- Flooding RAM -------------")        
                if(count>=req_pages):
                    PT_MAP[pid]={}
                    print("RAM IS ENOGH     |       Required    "+ str(req_pages)+"     |       Available       "+str(count)+"\n")
                    for i in range(req_pages):
                        ppn=HDD_MAP[pid][i]
                        Data=HDD_STORAGE[ppn:ppn+page_size]
                        RAM_STORAGE.append(Data)
                        ppn=len(RAM_STORAGE)-1
                        if(i==vpn):
                            newPTE= PTE(ppn,valid=True,present=True,at=TIME_STAMP,rt=TIME_STAMP)
                        else:
                            newPTE= PTE(ppn,valid=True,present=True,at=-1,rt=-1)
                        PT_MAP[pid][i]=newPTE
                else:
                    print("RAM IS NOT ENOGH     |       Required    "+ str(req_pages)+"     |       Available       "+str(count)+"\n")
                    PT_MAP[pid]={}
                    SWAP_MAP[pid]={}
                    curr=-1
                    for i in range(count):
                        ppn=HDD_MAP[pid][i]
                        Data=HDD_STORAGE[ppn:ppn+page_size]
                        RAM_STORAGE.append(Data)
                        ppn=len(RAM_STORAGE)-1
                        if(i==vpn):
                            newPTE= PTE(ppn,valid=True,present=True,at=TIME_STAMP,rt=TIME_STAMP)
                        else:
                            newPTE= PTE(ppn,valid=True,present=True,at=-1,rt=-1)
                        PT_MAP[pid][i]=newPTE
                        curr=i
                    print("FILLING REST IN SWAP")
                    for i in range(curr+1,req_pages,1):
                        ppn=HDD_MAP[pid][i]
                        Data=HDD_STORAGE[ppn:ppn+page_size]
                        SWAP_STORAGE.append(Data)
                        ppn=len(SWAP_STORAGE)-1
                        newPTE= PTE(ppn,valid=True,present=True,at=TIME_STAMP,rt=TIME_STAMP)
                        SWAP_MAP[pid][i]=newPTE
            else:
                print("--------------------NO Flooding in RAM: --------------")
                if(req_pages>swap_limit-len(SWAP_STORAGE)):
                    print("SYSTEM ERROR ---> CRASHED")
                    break
                else:
                    print("FILLING ALL IN SWAP\n")
                    SWAP_MAP[pid]={}
                    for i in range(req_pages):
                        ppn=HDD_MAP[pid][i]
                        Data=HDD_STORAGE[ppn:ppn+page_size]
                        SWAP_STORAGE.append(Data)
                        ppn=len(SWAP_STORAGE)-1
                        newPTE= PTE(ppn,valid=True,present=True,at=TIME_STAMP,rt=TIME_STAMP)
                        SWAP_MAP[pid][i]=newPTE
        

                



        if (pid,vpn) in TLB_MAP:
            tlb_hits,tlb_hit_summary[pid]=tlb_hits+1,tlb_hit_summary[pid]+1
            if(TLB_MAP[(pid,vpn)].present==False):
                page_faults,page_fault_summary[pid]=page_faults+1,page_fault_summary[pid]+1
                print("PID: "+str(pid)+"    |   V_Address     "+str(V_Address)+"   |   TLB MISS[PB]     --->    RAM MISS[PB]")
                Page_fault_handler(pid,vpn)
                TLB_Miss_handler(pid,vpn)
            else:
                print("PID: "+str(pid)+"    |   V_Address     "+str(V_Address)+"   |   TLB HIT[DONE]")
                TLB_MAP[(pid,vpn)].recent_usage_time=TIME_STAMP
                PT_MAP[pid][vpn].recent_usage_time=TIME_STAMP
                if(PT_MAP[pid][vpn].arrival_time==-1):
                    PT_MAP[pid][vpn].arrival_time=TIME_STAMP
        else:
            tlb_misses ,tlb_miss_summary[pid]=tlb_misses+1, tlb_miss_summary[pid]+1
            #searching in RAM
            if((pid in PT_MAP) and len(PT_MAP[pid])>vpn):
                if(PT_MAP[pid][vpn].present==False):
                    page_faults,page_fault_summary[pid]=page_faults+1,page_fault_summary[pid]+1
                    print("PID: "+str(pid)+"    |   V_Address     "+str(V_Address)+"   |   TLB MISS     --->    RAM MISS[PB]")
                    Page_fault_handler(pid,vpn)
                    TLB_Miss_handler(pid,vpn)
                else:
                    print("PID: "+str(pid)+"    |   V_Address     "+str(V_Address)+"   |   TLB MISS     --->    RAM HIT[DONE]")
                    TLB_Miss_handler(pid,vpn)
                    PT_MAP[pid][vpn].recent_usage_time=TIME_STAMP
                    if(PT_MAP[pid][vpn].arrival_time==-1):
                        PT_MAP[pid][vpn].arrival_time=TIME_STAMP
            else:
                page_faults,page_fault_summary[pid]=page_faults+1,page_fault_summary[pid]+1
                print("PID: "+str(pid)+"    |   V_Address     "+str(V_Address)+"   |   TLB MISS     --->    RAM MISS")
                #Fetch from HDD
                Page_fault_handler(pid,vpn)
                TLB_Miss_handler(pid,vpn)
        # print("Data present: "+ str(RAM_STORAGE[TLB_MAP[(pid,vpn)].ppn][offset]))
        print("---------------------------TLB---------------------------------\n")
        print_TLB()
        print("---------------------------RAM---------------------------------\n")
        print(RAM_STORAGE)
        print("---------------------------RAM - PT---------------------------------\n")
        print_PT()
        print("---------------------------SWAP---------------------------------\n")
        print(SWAP_STORAGE)
        print("---------------------------SWAP - PT---------------------------------\n")
        print_SWAP()
        print("\n\n\n\n")
        # print("-------------------------------------------------------------------------------------------------------------------------\n\n\n")
def print_TLB():
    st="{"
    for key in TLB_MAP.keys():
        st+=str(key)+" : <"
        st+=str(TLB_MAP[key].ppn)+" "+str(TLB_MAP[key].valid)+" "+str(TLB_MAP[key].present)+" "+str(TLB_MAP[key].arrival_time)+" "+str(TLB_MAP[key].recent_usage_time)+"> "
    print(st+"}")
def print_PT():
    st="{"
    for pid in PT_MAP.keys():
        st+=str(pid)+" : ["
        for vpn in PT_MAP[pid].keys():
            st+="{" +str(vpn)+" :<"
            st+=str(PT_MAP[pid][vpn].ppn)+" "+str(PT_MAP[pid][vpn].valid)+" "+str(PT_MAP[pid][vpn].present)+" "+str(PT_MAP[pid][vpn].arrival_time)+" "+str(PT_MAP[pid][vpn].recent_usage_time)+">} "
        st+="] "
    print(st+"}")
def print_SWAP():
    st="{"
    for pid in SWAP_MAP.keys():
        st+=str(pid)+" : ["
        for vpn in SWAP_MAP[pid].keys():
            st+="{" +str(vpn)+" :<"
            st+=str(SWAP_MAP[pid][vpn].ppn)+" "+str(SWAP_MAP[pid][vpn].valid)+" "+str(SWAP_MAP[pid][vpn].present)+" "+str(SWAP_MAP[pid][vpn].arrival_time)+" "+str(SWAP_MAP[pid][vpn].recent_usage_time)+">} "
        st+="] "
    print(st+"}")

def get_info(idx,PT_MAP ):
    for pid in PT_MAP:
        for vpn in PT_MAP[pid]:
            if(idx==PT_MAP[pid][vpn].ppn ):
                return (pid,vpn)
def Page_fault_handler(pid,vpn):
    global HDD_STORAGE,RAM_STORAGE,HDD_MAP,PT_MAP,TLB_MAP,TIME_STAMP
    global  hdd_size,swap_size,ram_size,page_size,tlb_size,replace_policy,page_frame_LIMIT,page_block_LIMIT
    ppn=SWAP_MAP[pid][vpn].ppn
    Data=list(SWAP_STORAGE[ppn])
    SWAP_STORAGE.pop(ppn)
    del SWAP_MAP[pid][vpn]
    if(len(SWAP_MAP[pid])==0):
        del SWAP_MAP[pid]

    #-------------------------------TODO [RAPLACEMENT IN RAM]-----------------------------
    idx=replacement_PT(PT_MAP,TLB_MAP,RAM_STORAGE,page_frame_LIMIT,replace_policy,TIME_STAMP,page_size)
    # if(idx==-1):
    #     RAM_STORAGE.append(Data)
    # else:

    R_Data=list(RAM_STORAGE[idx])
    SWAP_STORAGE.append(R_Data)
    pid1,vpn1=get_info(idx,PT_MAP)
    if(pid1 not in SWAP_MAP):
        SWAP_MAP[pid1]={}
    ppn=len(SWAP_STORAGE)-1
    newPTE= PTE(ppn,valid=True,present=True,at=TIME_STAMP,rt=TIME_STAMP)
    SWAP_MAP[pid1][vpn1]=newPTE

    for k in range(page_size):
        RAM_STORAGE[idx][k]=Data[k]

    #updating PT_MAP
    # if(idx==-1):
    #     ppn=len(RAM_STORAGE)-1
    # else:
    ppn=idx
    if pid in PT_MAP:
        if vpn in PT_MAP[pid]:
            PT_MAP[pid][vpn].ppn=ppn
            PT_MAP[pid][vpn].present=True
            PT_MAP[pid][vpn].recent_usage_time=TIME_STAMP
            PT_MAP[pid][vpn].arrival_time=TIME_STAMP
            
        else:
            newPTE= PTE(ppn,valid=True,present=True,at=TIME_STAMP,rt=TIME_STAMP)
            PT_MAP[pid][vpn]=newPTE
    else:
        PT_MAP[pid]={}
        newPTE= PTE(ppn,valid=True,present=True,at=TIME_STAMP,rt=TIME_STAMP)
        PT_MAP[pid][vpn]=newPTE



def TLB_Miss_handler(pid,vpn):
    global HDD_STORAGE,RAM_STORAGE,HDD_MAP,PT_MAP,TLB_MAP,TIME_STAMP
    global  hdd_size,swap_size,ram_size,page_size,tlb_size,replace_policy,page_frame_LIMIT,page_block_LIMIT
    
    #updating PT_MAP
    if (pid,vpn) in PT_MAP:
        TLB_MAP[(pid,vpn)].ppn=PT_MAP[pid][vpn].ppn
        TLB_MAP[(pid,vpn)].present=True
        TLB_MAP[(pid,vpn)].recent_usage_time=TIME_STAMP
    else:
        ppn=PT_MAP[pid][vpn].ppn
        #-------------------------------TODO [RAPLACEMENT IN TLB]-----------------------------
        replacement_TLB(TLB_MAP,tlb_size,replace_policy,TIME_STAMP,page_size)    
        newTLBE= TLBE(ppn,valid=True,present=True,at=TIME_STAMP,rt=TIME_STAMP)
        TLB_MAP[(pid,vpn)]=(newTLBE)

def PrintSummary():    
    global HDD_STORAGE,RAM_STORAGE,HDD_MAP,PT_MAP,TLB_MAP,TIME_STAMP
    global tlb_hit_summary,tlb_miss_summary,page_fault_summary,page_faults,tlb_misses,tlb_hits

    print("------------------SUMMARY----------------\n")
    print("Total Number of TLB Misses  : "+str(tlb_misses)+"\n")
    # print("Total Number of TLB Hits    : "+str( tlb_hits)+"\n")
    print("Total number of page faults : "+str(page_faults)+"\n")

    for i in HDD_MAP.keys():
        print("pid : "+str(i)+"  | tlbMisses : "+str(tlb_miss_summary[i])+"  | tlbHits : "+str(tlb_hit_summary[i])+"  | pageFaults : "+str(page_fault_summary[i])+"   \n")

# TakeInput()
Initializing()
Allocate_Memory("sample inputfile1.txt")
Accese_Memory("sample inputfile2.txt")
PrintSummary()