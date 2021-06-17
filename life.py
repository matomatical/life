#!python3

import time
import curses

import numpy as np
import scipy.signal as signal

# # #
# Display Configuration
# 

CELL_COLOR = curses.COLOR_MAGENTA

FRAMES_SEC = 12
SLEEP_TIME = 1 / FRAMES_SEC

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
    stdscr.bkgd(' ', prepare_colors())
    # start life
    game = Game(
        height=curses.LINES * 4,
        width=curses.COLS * 2,
    )
    # enter main loop
    while stdscr.getch() < 0:
        # paint screen
        stdscr.clear()
        a = game.status()
        b = braille_cells(a)
        for i, j, in np.transpose(np.where(b > 0)):
            stdscr.insstr(i, j, chr(0x2800+b[i, j]))
        stdscr.refresh()
        # update life
        game.update()
        time.sleep(SLEEP_TIME)


def braille_cells(a):
    """
    Turns a HxW array of booleans into a (H//4)x(W//2) array of braille
    binary codes (suitable for specifying unicode codepoints, just add
    0x2800).
    
    braille symbol:                 binary digit representation:
                    0-o o-1
                    2-o o-3   ---->     0 b  0 0  0 0 0  0 0 0
                    4-o o-5                  | |  | | |  | | |
                    6-o o-7                  7 6  5 3 1  4 2 0

    """
    H, W = a.shape
    h, w = (H // 4, W // 2)
    c = (   a
            .reshape(h, 4, w, 2)     # split rows into 4s and cols into 2s
            .transpose([1, 3, 0, 2]) # put the 4x2s in the first two dims
            .reshape(8, h, w)        # collapse them into one dimension
        )
    # pack the numbers into an array of bytes
    b = ( c[0]      | c[1] << 3 
        | c[2] << 1 | c[3] << 4 
        | c[4] << 2 | c[5] << 5 
        | c[6] << 6 | c[7] << 7
        )
    return b

def prepare_colors():
    curses.use_default_colors()
    curses.init_pair(1, CELL_COLOR, -1)
    return curses.color_pair(1) | curses.A_BOLD


if __name__ == "__main__":
    try:
        curses.wrapper(main)
    except KeyboardInterrupt:
        pass
