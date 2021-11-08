from multiprocessing.pool import ThreadPool 
from itertools import repeat
import logging, subprocess, time

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
                index = message.rfind("min/avg/max/")
                RTT = message[index:].split("/")[-3]
                out_fp.write(f"{ip}@pingCheck, {RTT}, type:RTT@timestamp:{time.time()}\n")
                logging.debug(f"{ip}@pingCheck, {RTT}, type:RTT@timestamp:{time.time()}")

    except Exception as exp:
        logging.error(exp)

def starmap_wraper(func, arg, kwargs):
    return func(arg, **kwargs)

def multi_ip_ping(ips, out_fp = None, timeout=10, poolsize = 16):
    outList = set()
    pool = ThreadPool(poolsize)
    kwargs = {"outList":outList, "out_fp":out_fp, "timeout":timeout}
    pool.starmap(starmap_wraper, zip(repeat(ping), ips, repeat(kwargs)))    
    pool.close()
    pool.join() 
    return outList



