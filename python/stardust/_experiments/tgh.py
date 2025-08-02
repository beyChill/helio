import math

from time import perf_counter
import timeit

from stardust import parse_streamer_name
from stardust.utils.general import chk_streamer_name
# import timeit
# g=sum_as_string(4,5)
# t=get_env_data()
# print(t)
# print(g)
uname = "g,9897(@67t"
times = 3
t1 = 0

# hh= parse_streamer_name(uname)
# print(hh)

# r = format_streamer_name(uname)
# print(type(r))
# print(r)
# try:
#     m=parse_streamer_name(uname)
#     # print(type(m))
#     print(m)
# except NameLengthError as e:
#     print(e)

# # 



def parse(uname=uname):
    runs = []
    start = perf_counter()
    for _ in range(times):
        t1=0
        m=chk_streamer_name(uname)
        # print(type(m))
        # print(m)
        t1 = perf_counter() - start
        # print(t1)
        runs.append(t1)
    # print("time:", round((sum(runs)) / len(runs),5))
    # print(f"total time {round(sum(runs),5)} {len(runs)}")

def parse2(uname=uname):
    a=0
    runs2 = []
    start = perf_counter()
    for _ in range(times):
        t2=0
        r = parse_streamer_name(uname)
        # print(type(m))
        # print(m)
        t2 = perf_counter() - start
        runs2.append(t2)
        # a+=1
        # print(a)
    # print("time2:", round((sum(runs2)) / len(runs2),5))
    # print(f"total time2 {round(sum(runs2),5)} {len(runs2)}")
# setup="from __main__ import test"

def parse3(uname=uname):
    a=0
    runs2 = []
    start = perf_counter()
    for _ in range(times):
        t2=0
        r = format_streamer_name(uname)
        # print(type(m))
        # print(m)
        t2 = perf_counter() - start
        runs2.append(t2)
        # a+=1
        # print(a)
    # print("time2:", round((sum(runs2)) / len(runs2),5))
    # print(f"total time2 {round(sum(runs2),5)} {len(runs2)}")
# setup="from __main__ import test"



if __name__=="__main__":
    try:
        # parse(uname)
        # parse2(uname)
        # parse3(uname)
        # print(f"python: {timeit.timeit("parse()",number=60000, globals=globals() )}")
        # print(f"rust: {timeit.timeit("parse2()",number=60000, globals=globals() )}")
        # print(f"rust2: {timeit.timeit("parse3()",number=1, globals=globals() )}")


        # if parse_streamer_name(uname):
        #     print(uname)
        # else:
        #     print("noot")
        w= "sweetlikestrawberrywine"
        print(len(w))

    except Exception as e:
        print(e)