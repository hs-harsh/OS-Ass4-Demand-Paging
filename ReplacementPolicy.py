def emptyCheck_TLB(TLB_MAP,tlb_size):
    if(len(TLB_MAP)<tlb_size):
        return 1
    return -1

            
def replacement_PT(PT_MAP,TLB_MAP,RAM_STORAGE,page_frame_LIMIT,replace_policy,TIME_STAMP,page_size):
    # if(len(RAM_STORAGE)<page_frame_LIMIT):
    #     return -1
    Lru,Fifo="",""
    min_at,min_rt=float('inf'),float('inf')
    for pid in PT_MAP:
        for vpn in (PT_MAP[pid]):
            if(PT_MAP[pid][vpn].present==True):
                if(PT_MAP[pid][vpn].arrival_time < min_at):
                    Fifo=pid,vpn
                    min_at=PT_MAP[pid][vpn].arrival_time
                if(PT_MAP[pid][vpn].recent_usage_time < min_rt):
                    Lru=pid,vpn
                    min_rt=PT_MAP[pid][vpn].recent_usage_time
    if(replace_policy==0):
        PT_MAP[Lru[0]][Lru[1]].present=False
        if (Lru[0],Lru[1]) in TLB_MAP:
            TLB_MAP[(Lru[0],Lru[1])].present=False
        return PT_MAP[Lru[0]][Lru[1]].ppn
    elif(replace_policy==1):
        PT_MAP[Fifo[0]][Fifo[1]].present=False
        if (Fifo[0],Fifo[1]) in TLB_MAP:
            TLB_MAP[(Fifo[0],Fifo[1])].present=False
        return PT_MAP[Fifo[0]][Fifo[1]].ppn
    elif (replace_policy==2):
        Next_Access={} #to map (pid,vpn) to the next time it's being accessed
        for pid in PT_MAP:
            for vpn in (PT_MAP[pid]):
                if(PT_MAP[pid][vpn].present==True):
                    Next_Access[pid]=float('inf')
            
        f=open("sample inputfile2.txt",'r')
        lines=f.readlines()
        time=0
        for line in lines:
            time+=1
            if(time>=TIME_STAMP):
                line=line.strip().split(" ")
                pid,V_Address=int(line[0]),int(line[1])
                vpn=V_Address//page_size
                if pid in Next_Access:
                    if(Next_Access[(pid)]==float('inf')):
                        Next_Access[(pid)]=time
        mx_delay=-float('inf')
        OPT=""
        for pid in Next_Access:
            if(Next_Access[pid]>mx_delay):
                OPT=pid
                mx_delay=Next_Access[pid]

        for v in PT_MAP[OPT]:
            if(PT_MAP[OPT][v].present):
                OPT=(OPT,v)
                break
        PT_MAP[OPT[0]][OPT[1]].present=False
        if (OPT[0],OPT[1]) in TLB_MAP:
            TLB_MAP[(OPT[0],OPT[1])].present=False
        return PT_MAP[OPT[0]][OPT[1]].ppn
    else:
        print("-------------------------Invalid Policy_nuber---------------------------------------\n")


def replacement_TLB(TLB_MAP,tlb_size,replace_policy,TIME_STAMP,page_size):
    if(emptyCheck_TLB(TLB_MAP,tlb_size)==1):
        return

    Tlbe_Lru,Tlbe_Fifo="",""
    min_at,min_rt=float('inf'),float('inf')
    for (pid,vpn) in TLB_MAP:
        if(TLB_MAP[(pid,vpn)].arrival_time < min_at):
            Tlbe_Fifo=(pid,vpn)
            min_at=TLB_MAP[Tlbe_Fifo].arrival_time
        if(TLB_MAP[(pid,vpn)].recent_usage_time < min_rt):
            Tlbe_Lru=(pid,vpn)
            min_rt=TLB_MAP[Tlbe_Lru].recent_usage_time
            
    if(replace_policy==0):
        del TLB_MAP[Tlbe_Lru]
    elif(replace_policy==1):
        del TLB_MAP[Tlbe_Fifo]
    elif (replace_policy==2):
        Next_Access={} #to map (pid,vpn) to the next time it's being accessed
        for (pid,vpn) in TLB_MAP:
            Next_Access[pid]=float('inf')
        f=open("sample inputfile2.txt",'r')
        lines=f.readlines()
        time=0
        for line in lines:
            time+=1
            if(time>=TIME_STAMP):
                line=line.strip().split(" ")
                pid,V_Address=int(line[0]),int(line[1])
                vpn=V_Address//page_size
                offset=V_Address-vpn*page_size
                if pid in Next_Access:
                    if(Next_Access[pid]==float('inf')):
                        Next_Access[pid]=time
        mx_delay=-float('inf')
        Tlbe_OPT=""
        for pid in Next_Access:
            if(Next_Access[pid]>mx_delay):
                Tlbe_OPT=pid
                mx_delay=Next_Access[pid]
        # print(Next_Access)
        
        for p,v in TLB_MAP:
            if(TLB_MAP[p,v].present and p==Tlbe_OPT):
                Tlbe_OPT=(Tlbe_OPT,v)
                break

        del TLB_MAP[Tlbe_OPT]

    else:
        print("-------------------------Invalid Policy_nuber---------------------------------------\n")


