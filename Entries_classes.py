import os
from math import ceil,pow 

# // Global variables for sizes (they are stored as log base 2)
logical_address_space,ram_size,page_size,tlb_size=0,0,0,0
# // For storing PIDs, as PIDs can be random, simply storing in array doesn't work

class TLBE:
    def __init__(self,ppn,valid,present,at,rt):
        #self.virtual_address=virtual_address
        self.ppn=ppn
        self.valid = valid
        self.present=present
        self.arrival_time=at # //useful for FIFO replacement policy
        self.recent_usage_time=rt# //useful for LRU implementation

class PTE:
    def __init__(self,ppn,valid,present,at,rt):
        self.ppn = ppn
        self.valid = valid
        self.present=present
        self.arrival_time = at
        self.recent_usage_time = rt
#storing KEY-(pid,vpn) --> VALUE-(TLBE) in TLB level table
#storing KEY-(pid) --> VALUE-[dict key - vpn --->  VALUE - list(PTE)] in RAM level table
#storing KEY -pid --> VALUE -list(starting of page_block)
