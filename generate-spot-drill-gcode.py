#!/usr/bin/python3

#
# This program takes a series of coordinates and generates the gcode for a cnc machine to spot drill
# at those coordinates. By default it starts at X=0, Y=0, Z=0.
#
# To start, we will just read the coordinates from a file, but adding a fill in the blanks gui would make
# it easier to use and avoid syntax error issues.
#

import os
from tkinter import *                # GUI stuff
from tkinter import ttk              # more widgets
from tkinter.scrolledtext import ScrolledText  # not sure why we need to import a module for scrolled text
from tkinter import filedialog

# constants for list index values
XVALUE = 0;
YVALUE = 1;
XWIDGET = 2;
YWIDGET = 3;

# temporary code to open working files. This will be replaced by a file selection box later
coordsFileName = "test_coords.txt"
gcodeFileName = "test_gcode.nc"

# open the coordinates file. This is just a pair of numbers on each line, x, then y, separated by a single
# space. The readLines method creates a list of lines from this file, then we split each line into the two
# fields (split()) and remove the end of line (strip())
coordsFile = open(coordsFileName, "r")
coordsLines = coordsFile.readlines()
for line in coordsLines:
    coords = line.strip().split(' ')
    # just print the coords value for now.
    print(coords)
#    print(line.strip())  # line.strip() removes end of line characters

#
# The main data structure for the program is a list of lists, structured like this...
#
# [[x, y, entry widget for x, entry widget for y]...]
#
# Example with two coordinates: [[.5, .5, xEntry, yEntry],[.5, 1.0, xEntry, yEntry]]
#
# I think I want to break this up some so I can deal with values in the coordinate list
# separately.
#
coordList = []

#coordList.append([])

gcodeFile = open(gcodeFileName, "w")

# set up the GUI
window = Tk()
s = ttk.Style()
s.theme_use('xpnative')
s.configure('window.TFrame', font=('Helvetica', 20))
#
# create and size the main window
#
window.title('Spot Drilling Tool')
window.geometry("400x600")

#
# create a list for each coordinate pair consisting of the value of X, the value of Y, and two tk
# entry widgets. The widgets will be displayed in the GUI window. Each of these coordinate pair lists
# will be appended to the coordList, previously initialized as an empty list, resulting in a list of
# coordinate pair lists.
#
i=0
for line in coordsLines:
    coords = line.strip().split(' ')
    coordList.append([coords[XVALUE], coords[YVALUE], Entry(window), Entry(window)])
    coordList[i][XWIDGET].insert(END,coordList[i][XVALUE])
    coordList[i][YWIDGET].insert(END,coordList[i][YVALUE])
    i = i + 1


print(coordList)  # debug temp

#
# Place X and Y entry widgets in the window
#
i=0
for lineNumber in range(4):
    coordList[lineNumber][XWIDGET].grid(row=i,column=0)
    coordList[lineNumber][YWIDGET].grid(row=i,column=1)
    i = i + 1

#yEntry[0].grid(row=0,column=1)
#xEntry[1].grid(row=1,column=0)
#yEntry[1].grid(row=1,column=1)
window.mainloop()