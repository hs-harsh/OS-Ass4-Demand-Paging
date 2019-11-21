# Demand Paging Memory Management System

Write a simulator for a demand paging memory management system. The fol-
lowing will be input parameters for your program:

• a file containing a list of processes and their sizes
• a file containing a sequence of memory accesses in the following form:
< pid >< logical address >
• page replacement algorithms (implement FIFO, Optimal and LRU)
• amount of RAM and swap available
• number of TLB entries
Your simulator should have data structures for per-process page tables, and the
kernel frame table. The simulator’s output should report TLB hits/misses, and
page faults for each process.
