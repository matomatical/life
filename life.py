#!python3

import time
import curses

import numpy as np
import scipy.signal as signal

# # #
# Display Configuration
# 

CELL_CHAR  = b"O"
CELL_COLOR = curses.COLOR_GREEN

SLEEP_TIME = 0.07 # seconds


# # #
# Conway's Game of Life
# 

KERNEL = np.array([
    [1, 1, 1],
    [1, 0, 1],
    [1, 1, 1],
])

class Game:
    def __init__(self, height, width):
        self.h = height
        self.w = width
        self.seed()
    def seed(self):
        self.a = np.random.choice(
            [False, True],
            (self.h, self.w),
            p=[0.75, 0.25],
        )
    def update(self):
        counts = signal.convolve2d(
            self.a,
            KERNEL,
            mode='same',
            boundary='wrap',
        )
        self.a = (self.a & (counts == 2)) | (counts == 3)
    def status(self):
        return self.a


def main(stdscr):
    # curses setup
    curses.curs_set(False)
    stdscr.nodelay(True)
    # prepare colors
    curses.use_default_colors()
    curses.init_pair(1, CELL_COLOR, -1) # -1: transparent background
    cell_attr = curses.color_pair(1) | curses.A_BOLD
    # start life
    game = Game(
        height=curses.LINES,
        width=curses.COLS,
    )
    # enter main loop
    while stdscr.getch() < 0:
        # paint screen
        stdscr.clear()
        for i, j in np.transpose(np.where(game.status())):
            stdscr.insch(i, j, CELL_CHAR, cell_attr)
        stdscr.refresh()
        # update life
        game.update()
        time.sleep(SLEEP_TIME)




if __name__ == "__main__":
    try:
        curses.wrapper(main)
    except KeyboardInterrupt:
        pass
