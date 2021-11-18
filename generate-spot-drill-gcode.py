#!/usr/bin/python3

#
# This program takes a series of coordinates and generates the gcode for a cnc machine to spot drill
# at those coordinates. By default it starts at X=0, Y=0, Z=0. Functionality:
#
# GUI: One window with the following widgets...
#    Depth Input - specifies how deep to drill. Default .1 inch
#    Plunge Rate Input - specified how fast to move the z axis during the cuts. Default: 1.5 inches/minute
#    Open Button - pops up a file section box for the user to choose a file containing a list of coordinates.
#    Save Button - pops up a file selection box for the user to save the current coordinates in a file.
#    New Button - adds a line to the coordinate list to be filled in by the user.
#    Coordinate Inputs - arranged in rows of two each, this is where the user enters X and Y coordinates.
#        The user can enter a number (float), or an expression that evaluates to a number.
#    Generate Gcode Button - pops up a file selection box for the user to specify the gcode file, and writes
#        gcode to the file.
#    Inch/mm menu. Default Inch
#    Absolute/relative menu. Default Absolute
#    Exit Button - exits the program. Asks user to save
#
#      Depth        Plunge       [New]
#      __________  __________    [Open]
#          X          Y          [Save]
#      __________  __________    v Inch
#      __________  __________    v Absolute
#      __________  __________    [Gen Gcode]
#                                [Exit]


#
# To start, we will just read the coordinates from a file, but adding a fill in the blanks gui would make
# it easier to use and avoid syntax error issues.
#

import numexpr                       # for allowing numeric expressions in coordinate fields
from tkinter import *                # GUI stuff
from tkinter import ttk              # more widgets
from tkinter.scrolledtext import ScrolledText  # not sure why we need to import a module for scrolled text
from tkinter import filedialog
test = float(numexpr.evaluate('.5+1'))
print(test)
print(test*2.54)
print(type(test))

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
def OpenPressed():
    print("Open button")
def NewPressed():
    print("New button")
def SavePressed():
    print("Save button")
def GenGcodePressed():
    print("Gen Gcode button")
def ExitPressed():
    print("Exit button")
def AbsRelSelectVarChanged(*args):
    print("Absolute/Relative Menu Changed")
    print(absRelSelectVar.get())
def InchMmSelectVarChanged(*args):
    print("Inch/mm menu changed")
    print(inchMmSelectVar.get())

coordList = []

#coordList.append([])

gcodeFile = open(gcodeFileName, "w")

# set up the GUI
window = Tk()
s = ttk.Style()
#s.theme_use('xpnative')
#s.configure('window.TFrame', font=('Helvetica', 30))
#
# create and size the main window
#
window.title('Spot Drilling Tool')
#window.geometry("400x200")
xText = StringVar()
xLabel = Label(window, textvariable=xText, relief=SUNKEN).grid(row=0, column=0)
xText.set('    X    ')
yText = StringVar()
yLabel = Label(window, textvariable=yText, relief=SUNKEN).grid(row=0, column=1)
yText.set('    Y    ')
Button(window, text='New', command=NewPressed).grid(row=1,column=2,sticky=W, pady=4)
Button(window, text='Open', command=OpenPressed).grid(row=2,column=2,sticky=W, pady=4)
Button(window, text='Save', command=SavePressed).grid(row=3,column=2,sticky=W, pady=4)

inchMmSelectVar = StringVar(window)
inchMmSelectVar.set("Unit: Inches")
inchMmSelectMenu = OptionMenu(window, inchMmSelectVar, 'Unit: Inches', 'Unit: Millimeters').grid(row=4,column=2)
inchMmSelectVar.trace('w', InchMmSelectVarChanged)

absRelSelectVar = StringVar(window)
absRelSelectVar.set("Mode: Absolute")
absRelSelectmenu = OptionMenu(window, absRelSelectVar, 'Mode: Absolute', 'Mode: Relative').grid(row=5,column=2)
absRelSelectVar.trace('w', AbsRelSelectVarChanged)

Button(window, text='Gen Gcode', command=GenGcodePressed).grid(row=6,column=2,sticky=W, pady=4)
Button(window, text='Exit', command=ExitPressed).grid(row=7,column=2,sticky=W, pady=4)

# create a list for each coordinate pair consisting of the value of X, the value of Y, and two tk
# entry widgets. The widgets will be displayed in the GUI window. Each of these coordinate pair lists
# will be appended to the coordList, previously initialized as an empty list, resulting in a list of
# coordinate pair lists.
#
lineNumber=0
for line in coordsLines:
    coords = line.strip().split(' ')
    coordList.append([coords[XVALUE], coords[YVALUE], Entry(window), Entry(window)])
    coordList[lineNumber][XWIDGET].insert(END, coordList[lineNumber][XVALUE])
    coordList[lineNumber][YWIDGET].insert(END, coordList[lineNumber][YVALUE])
    lineNumber += 1


print(coordList)  # debug temp

#
# Place X and Y entry widgets in the window
#
i=0
for lineNumber in range(6):
    coordList[lineNumber][XWIDGET].grid(row=i+1,column=0)
    coordList[lineNumber][YWIDGET].grid(row=i+1,column=1)
    i = i + 1

#yEntry[0].grid(row=0,column=1)
#xEntry[1].grid(row=1,column=0)
#yEntry[1].grid(row=1,column=1)
window.mainloop()