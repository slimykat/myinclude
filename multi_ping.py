from multiprocessing.pool import ThreadPool 
from itertools import repeat
import logging, subprocess, time
#logging.getLogger().setLevel(20)
#import ping3
THREAD_LIMIT = 8

# ping protocal requires sudo privilage for process to send by it self
# since ping package doesnot guarantee better perforance, I just simply use Popen method here
#
def ping(ip, outList:dict, timeout = 10):
    try:
        r = subprocess.Popen(["ping", "-c", "1", "-W", str(timeout), str(ip)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # popen to call ping, since ping protocal is not safe in process layer

        out = r.communicate()    # read from pipe
        message = out[0].decode("utf-8") # decode
        if r.returncode:         # return status > 0
            logging.info(f"pingCheck_Failed {ip}... return {r.returncode}")
            RTT = None
        else:
            logging.debug(f"{ip} alive")
            # parse out RTT information, this is tested on CentOS 6
            index = message.rfind("min/avg/max")
            RTT = message[index:].split("/")[-3]

        outList[ip] = (r.returncode, RTT) # return in pair
    except Exception as exp:
        logging.error(exp)

def handler(IPiter):
    try:
        while(True):
            arg = next(IPiter)  # 從迭代器取出一個IP，避免跟其他thread取到同樣的IP
            ping(*arg)         
    except StopIteration:       # 正常結束
        pass
    except Exception as e:
        logging.error(f"push tasks failed\n{e}")

def iterator(ips, *args):
    for ip in ips:
        yield (ip, *args) # 將參數映射到所以IP

def multi_ip_ping(ips, outList:dict, timeout=4 , size:int = 8):
    IPiter = iterator(ips, outList, timeout) # 將List組成迭代器，提供複數thread共用
    if size > THREAD_LIMIT:    #寫死的上限，不會創造超過這個數量的thread
        size = THREAD_LIMIT
    if size <= 1:   # 如果size只有一，不用開啟thread pool
        handler(IPiter)
    else:
        with ThreadPool(size) as pool:
            pool.map(handler, [IPiter for _ in range(size)])
            # 將物件指標提供給所有thread



#multi_ip_ping([f"172.16.1.{i+1}" for i in range(244)])
"""
def ping3(ip, outList:set = None, out_fp = None, timeout = 10):
    try:
        RTT = ping3.ping(ip, timeout=timeout)
        if RTT:
            logging.debug(f"{ip} alive")
            if outList != None:
                outList.add(ip)
        elif RTT == None:
            logging.info(f"pingCheck_Failed {ip}... Timeout no reply")
        elif RTT == False:
            logging.info(f"pingCheck_Failed {ip}... Unkown host")
        else:
            logging.info(f"pingCheck_Failed {ip}... unkown error {RTT}")
        if out_fp:
            result = isinstance(RTT, (int, float))
            if result:
                out_fp.write(f"{ip}@pingCheck, {RTT}, type:RTT@timestamp:{time.time()}\n")
                logging.debug(f"{ip}@pingCheck, {RTT}, type:RTT@timestamp:{time.time()}")
                result = bool(result > 0)
            out_fp.write(f"{ip}@pingCheck, {not result}, type:alive@timestamp:{time.time()}\n")
            logging.debug(f"{ip}@pingCheck, {not result}, type:alive@timestamp:{time.time()}")
                
    except Exception as exp:
        logging.error(exp)

def starmap_wraper(func, arg, kwargs):
    return func(arg, **kwargs)
"""

