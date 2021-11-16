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

coordsFileName = "test_coords.txt"
gcodeFileName = "test_gcode.nc"

coordsFile = open(coordsFileName, "r")
coordsLines = coordsFile.readlines()
for line in coordsLines:
    coords = line.strip().split(' ')
    print(coords)
#    print(line.strip())  # line.strip() removes end of line characters

#
# The main data structure for the program is a list of lists, structured like this...
#
# [[x, y, entry widget for x, entry widget for y]...]
#
# Example with two coordinates: [[.5, .5, xEntry, yEntry],[.5, 1.0, xEntry, yEntry]]
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

i=0
for line in coordsLines:
    coords = line.strip().split(' ')
    coordList.append([coords[0], coords[1], Entry(window, coords[0]), Entry(window, coords[1])])


print(coordList)
#
# X and Y entry widgets
#

coordList[0][2].grid(row=0,column=0)
coordList[0][3].grid(row=0,column=1)
coordList
#yEntry[0].grid(row=0,column=1)
#xEntry[1].grid(row=1,column=0)
#yEntry[1].grid(row=1,column=1)
window.mainloop()