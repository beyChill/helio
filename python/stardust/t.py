import math
from stardust import get_env_data, sum_as_string, format_streamer_name,parse_streamer_name
from time import perf_counter
import timeit
# import timeit
# g=sum_as_string(4,5)
# t=get_env_data()
# print(t)
# print(g)
uname = "?"
times = 5000000
t1 = 0

# hh= parse_streamer_name(uname)
# print(hh)

r = format_streamer_name(uname)
print(type(r))
print(r)

# m=parse_streamer_name(uname)
# print(type(m))
# print(m)





def parse(uname=uname):
    runs = []
    start = perf_counter()
    for _ in range(times):
        t1=0
        m=parse_streamer_name(uname)
        # print(type(m))
        # print(m)
        t1 = perf_counter() - start
        # print(t1)
        runs.append(t1)
    print("time:", round((sum(runs)) / len(runs),5))
    print(f"total time {round(sum(runs),5)} {len(runs)}")

def parse2(uname=uname):
    
    runs2 = []
    start = perf_counter()
    for _ in range(times):
        t2=0
        r = format_streamer_name(uname)
        # print(type(m))
        # print(m)
        t2 = perf_counter() - start
        runs2.append(t2)
    print("time2:", round((sum(runs2)) / len(runs2),5))
    print(f"total time2 {round(sum(runs2),5)} {len(runs2)}")
# setup="from __main__ import test"

# parse(uname)
# parse2(uname)
# print(timeit.timeit("parse()",number=40000, globals=globals() ))
# print(timeit.timeit("parse2()",number=40000, globals=globals() ))