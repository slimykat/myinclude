from itertools import product

#expand ipRange into list
def ipRange_to_list(ipRange:str):
    ipv4 = ipRange.split(".")   # split into list of integers
    if len(ipv4) != 4 : # bad input format
        logging.critical(f"{ipRange} is not ipv4 format")
        return False

    for i in range(len(ipv4)):
        addr = ipv4[i]  # extract each number
        if '-' in addr: # range
            start, end = addr.split('-')
            ipv4[i] = [str(c) for c in range(int(start), 1+int(end))]
            # convert string upper bond and lower bond
            # to list of integers

        else:           # not range, wrap in list for iteration perpose
            ipv4[i] = [ipv4[i]]

    return [".".join(addr) for addr in product(*ipv4)] 
            # join the numbers with dot for each combination 


def ipdecode(ip:int):
    addr=[]
    for _ in range(4):
        addr.append(str(ip&255))
        ip = ip >> 8
    return ".".join(addr[-1::-1]);
def ipencode(ip:str):
    addr = zip(ip.split("."),(24,16,8,0))
    return sum([int(a[0])<<a[1] for a in addr]);
def ip_compare(A:str, B:str, mask:int=4294967295):
    assert(0 <= mask <= 4294967295)
    A = ipencode(A)
    B = ipencode(B)
    return mask & (A ^ B);

