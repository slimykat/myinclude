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