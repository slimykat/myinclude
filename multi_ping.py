from multiprocessing.pool import ThreadPool 
from itertools import repeat
import logging, subprocess, time

def ping(ip, outList:set = None, out_fp = None, timeout = 10):
    try:
        r = subprocess.Popen(["ping", "-c", "1", "-W", str(timeout), str(ip)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out = r.communicate()
        #Sessions[key][1] = r.returncode
        if r.returncode:
            message = out[0].decode("utf-8")
            logging.info(f"pingCheck_Failed {ip}... return {r.returncode}")
            #logging.debug(f"{ip} : \n{message}")
        elif outList != None:
            #logging.debug(f"aliveList.add({ip})")
            outList.add(ip)
        if out_fp:
            out_fp.write(f"{ip}@pingCheck, {r.returncode}, type:alive@timestamp:{time.time()}\n")
        logging.debug(f"{ip}@pingCheck, {r.returncode}, type:alive@timestamp:{time.time()}\n")
    except Exception as exp:
        logging.error(exp)

def starmap_wraper(func, arg, kwargs):
    return func(arg, **kwargs)

def multi_ip_ping(ips, poolsize = 15, out_fp = None, timeout=10):
    outList = set()
    pool = ThreadPool(poolsize)
    kwargs = {"outList":outList, "out_fp":out_fp, "timeout":timeout}
    pool.starmap(starmap_wraper, zip(repeat(ping), ips, repeat(kwargs)))
    return outList



