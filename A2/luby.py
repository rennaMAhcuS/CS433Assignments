#!/usr/bin/env python3
import math

import matplotlib.pyplot as plt

n = 7
luby = [0 for i in range(0, n)]

i = 0
while 2**i < n:
    twop = 2**i
    luby[twop - 1] = twop // 2
    for j in range(twop, 2 * twop - 1):
        if j >= n:
            break
        luby[j] = luby[j - twop + 1]
    i += 1

plt.plot(luby)
plt.show()
