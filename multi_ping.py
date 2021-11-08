from multiprocessing.pool import ThreadPool 
from itertools import repeat
import logging, subprocess, time
logging.getLogger().setLevel(20)
#import ping3

def ping(ip, outList:set = None, out_fp = None, timeout = 10):
    try:
        r = subprocess.Popen(["ping", "-c", "1", "-W", str(timeout), str(ip)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out = r.communicate()
        message = out[0].decode("utf-8")
        if r.returncode:
            logging.info(f"pingCheck_Failed {ip}... return {r.returncode}")
            if r.returncode != 1: logging.debug(f"{ip} : \n{message}")
        else:
            logging.debug(f"{ip} alive")
            if outList != None:
                outList.add(ip)
        if out_fp:
            out_fp.write(f"{ip}@pingCheck, {r.returncode}, type:alive@timestamp:{time.time()}\n")
            logging.debug(f"{ip}@pingCheck, {r.returncode}, type:alive@timestamp:{time.time()}")
            if r.returncode == 0:
                index = message.rfind("min/avg/max")
                RTT = message[index:].split("/")[-3]
                out_fp.write(f"{ip}@pingCheck, {RTT}, type:RTT@timestamp:{time.time()}\n")
                logging.debug(f"{ip}@pingCheck, {RTT}, type:RTT@timestamp:{time.time()}")
    except Exception as exp:
        logging.error(exp)


def handler(IPiter):
    try:
        while(True):
            arg = next(IPiter)
            ping(*arg)
    except StopIteration:
        pass
    except Exception as e:
        logging.error(f"push tasks failed\n{e}")

def iterator(ips, outList, out_fp, timeout):
    for ip in ips:
        yield ip, outList, out_fp, timeout

def multi_ip_ping(ips, out_fp = None, timeout=4):
    outList = set()
    with ThreadPool(16) as pool:
        IPiter = iterator(ips, outList, out_fp, timeout)
        pool.map(handler, [IPiter for _ in range(16)])
        #pool.starmap(starmap_wraper, zip(repeat(ping3), ips, repeat(kwargs)))    
    return outList

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

