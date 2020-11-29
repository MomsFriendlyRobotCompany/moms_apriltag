#!/usr/bin/env python3
##############################################
# The MIT License (MIT)
# Copyright (c) 2020 Kevin Walchko
# see LICENSE for full details
##############################################
import apriltag_gen as apt
import numpy as np
import argparse
import imageio



def main():
    parser = argparse.ArgumentParser(description="Generate an AprilTag calibration board")
    parser.add_argument("-f", "--family", type=str, help="tag family, either tag16h5, tag25h9, tag36h10, or tag36h11; default is tag36h11", default="tag36h11")
    parser.add_argument("-n", "--filename", type=str, help="set output file name", default="board.png")
    parser.add_argument("-s", "--size", nargs=2, type=int, help="board size: 9 6", default=[4,5])
    parser.add_argument('-v', '--version', action='version', version=apt.__version__)
    args = parser.parse_args()
    args = vars(args)


    xx = apt.target.board(args["size"], args["family"])
    imageio.imwrite(args["filename"], xx)



if __name__ == '__main__':
    main()
