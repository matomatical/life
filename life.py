#!python3

import time
import curses

import numpy as np
import scipy.signal as signal

# # #
# Display Configuration
# 

CELL_CHAR  = b"O"

CELL_COLOR = curses.COLOR_MAGENTA
BORN_COLOR = curses.COLOR_WHITE
DIED_COLOR = curses.COLOR_BLACK

FRAMES_SEC = 12
SLEEP_TIME = 1 / FRAMES_SEC

# TODO: animated characters?

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
        self.b = np.zeros_like(self.a)
    def update(self):
        self.b = self.a
        counts = signal.convolve2d(
            self.b,
            KERNEL,
            mode='same',
            boundary='wrap',
        )
        self.a = (self.b & (counts == 2)) | (counts == 3)
    def status(self):
        return self.a
    def status_color(self):
        return self.b + 2*self.a


def main(stdscr):
    # curses setup
    curses.curs_set(False)
    stdscr.nodelay(True)
    # prepare colors
    attr_map = prepare_colors()
    # start life
    game = Game(
        height=curses.LINES,
        width=curses.COLS,
    )
    # enter main loop
    while stdscr.getch() < 0:
        # paint screen
        stdscr.clear()
        a = game.status_color()
        for i, j, in np.transpose(np.where(a > 0)):
            stdscr.insch(i, j, CELL_CHAR, attr_map[a[i, j]])
        stdscr.refresh()
        # update life
        game.update()
        time.sleep(SLEEP_TIME)


def prepare_colors():
    curses.use_default_colors()
    curses.init_pair(1, CELL_COLOR, -1)
    curses.init_pair(2, BORN_COLOR, -1)
    curses.init_pair(3, DIED_COLOR, -1)
    return (
        0,
        curses.color_pair(3) | curses.A_BOLD,
        curses.color_pair(2) | curses.A_BOLD,
        curses.color_pair(1) | curses.A_BOLD,
    )


if __name__ == "__main__":
    try:
        curses.wrapper(main)
    except KeyboardInterrupt:
        pass
