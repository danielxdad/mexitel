# -*- coding: utf-8 -*-
import curses
import time
import numpy as np


window = curses.initscr()
times = []
try:
    while True:
        x = window.getch()
        times.append(time.time())
        if x == 10:
            break
except KeyboardInterrupt:
    curses.endwin()
    exit(0)
else:
    curses.endwin()

if len(times) >= 3:
    times = np.diff(times)
    print('MIN:', np.min(times))
    print('MAX:', np.max(times))
    print('AVG:', np.average(times))
    print('STD:', np.std(times))
