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
#      Depth        Plunge       [Add Point]
#      __________  __________    [Open]
#          X          Y          [Save]
#      __________  __________    v Inch
#      __________  __________    v Absolute
#      __________  __________    [Gen Gcode]
#                                        [Exit]


#
# To start, we will just read the coordinates from a file, but adding a fill in the blanks gui would make
# it easier to use and avoid syntax error issues.
#

import numexpr                       # for allowing numeric expressions in coordinate fields
from tkinter import *                # GUI stuff
from tkinter import ttk              # more widgets
from tkinter.scrolledtext import ScrolledText  # not sure why we need to import a module for scrolled text
from tkinter import filedialog

baseDirectory = 'C:\development\python\PycharmProjects\spot-drill-gcode-gen'

test = float(numexpr.evaluate('.5+1'))
print(test)
print(test*2.54)
print(type(test))

XVALUE = 0;
YVALUE = 1;
XWIDGET = 2;
YWIDGET = 3;

# temporary code to open working files. This will be replaced by a file selection box later
#coordsFileName = "test_coords.txt"
#gcodeFileName = "test_gcode.nc"


#
# Data structures
#
# Coordinate list...
#
# Coordinates are stored in a list. Each coordinate pair is stored as a list containing the value,
# the gui widgets for displaying them, and the string variables needed for communication with the
# gui widgets.
#
# [
#     [X value, Y value, X entry widget, Y entry widget, X StringVar, Y StringVar]
#     [...]...
# ]
#
# Coordinate list functions...
#
# class CoordPair
#
# The main object type used by this application is a coordinate pair, and X and Y value that determines
# the physical location of a hole in the workpiece. A CoordPair can come from an input file, or be added
# by the user by clicking the Add button. CoordPairs are kept in a list that the gcode generation code
# uses, or the Save functionality writes to a file.
#
# CoordPair members:
#
# X value
# Y value
# X Entry widget
# Y Entry widget
# member functions set x, set y (maybe set value, including x and y)
# member functions get x, get y (maybe get value, including x and y)
#
# creating a CoordPair instance called x looks like x.CoordPair, which will call the __init__() function in
# the class definition
#
# Reading CoordPairs from a file:
#    Open the file
#    create a lines list from the file
#    parse each into an x and y
#    create a CoordPair from these values
#       set x value and y value
#       create X Entry widget and Y Entry widget
#       populate X Entry widget and Y Entry widget with X and Y values
#       place X Entry widget and Y Entry widget in the GUI grid
#
# Creating CoordPairs with the Gui:
#    The Add button creates a new CoordPair with null values in X and Y.
#    User adds values in Entry widgets

# The main data structure for the program is a list of lists, structured like this...
#
# [[x, y, entry widget for x, entry widget for y]...]
#
# Example with two coordinates: [[.5, .5, xEntry, yEntry],[.5, 1.0, xEntry, yEntry]]
#
# I think I want to break this up some so I can deal with values in the coordinate list
# separately.
#

#
# program state
#
def open_pressed():
    # Open means read a coordinates file and make the points in that file the current points in 
    # the application. That file also has values for depth and plunge rate. 
    print("Open button")
    openFile = filedialog.askopenfilename(title='Open File',initialdir=baseDirectory)
    print(openFile)
    # open the coordinates file. This is just a pair of numbers on each line, x, then y, separated by a single
    # space. The readLines method creates a list of lines from this file, then we split each line into the two
    # fields (split()) and remove the end of line (strip())
    coordsFile = open(openFile, "r")
    coordsLines = coordsFile.readlines()

    for line in coordsLines:
        coords = line.strip().split(' ')
        # just print the coords value for now.
        print(coords)
        
    line_number=0
    for line in coordsLines:
        coords = line.strip().split(' ')
        coordList.append([coords[XVALUE], coords[YVALUE], Entry(window), Entry(window), StringVar(), StringVar()])
        coordList[line_number][XWIDGET].insert(END, coordList[line_number][XVALUE])
        coordList[line_number][YWIDGET].insert(END, coordList[line_number][YVALUE])
        line_number += 1
        
def new_pressed():
    print("New button")
def save_pressed():
    print("Save button")
    saveFile = filedialog.asksaveasfile(title='Open File')
    print(saveFile)

def save_as_pressed():
    print("Save As button")


def gen_gcode_pressed():
    print("Gen Gcode button")


def exit_pressed():
    print("Exit button")


def abs_rel_select_var_changed(*args):
    print("Absolute/Relative Menu Changed")
    print(abs_rel_select_var.get())


def inch_mm_select_var_changed(*args):
    print("Inch/mm menu changed")
    print(inch_mm_select_var.get())


def add_button_pressed():
    print("Add Point button")


coordList = []

# coordList.append([])

# gcodeFile = open(gcodeFileName, "w")

# set up the GUI
window = Tk()
s = ttk.Style()
# s.theme_use('xpnative')
# s.configure('window.TFrame', font=('Helvetica', 30))
#
# create and size the main window
#
window.title('Spot Drilling Tool')

menu_bar = Menu(window)
filemenu = Menu(menu_bar, tearoff=0)
filemenu.add_command(label="New", command=new_pressed)
filemenu.add_command(label="Open", command=open_pressed)
filemenu.add_command(label="Save", command=save_pressed)
filemenu.add_command(label="Save as...", command=save_as_pressed)
filemenu.add_command(label="Write GCode", command=gen_gcode_pressed)
filemenu.add_command(label="Exit", command=exit_pressed)
menu_bar.add_cascade(label="File", menu=filemenu)

#
# Create the GUI widgets
#
depth_text = StringVar()
depth_label = Label(window, textvariable=depth_text, font=('Helvetica', 12))
depth_text.set('Depth')

plunge_text = StringVar()
plunge_label = Label(window, textvariable=plunge_text, font=('Helvetica', 12))
plunge_text.set('Plunge Rate')

depth_entry = Entry(window)
plunge_entry = Entry(window)

add_button = Button(window, text = "Add Point", command = add_button_pressed)

x_text = StringVar()
x_label = Label(window, textvariable=x_text, font=('Helvetica', 12))
x_text.set('    X    ')

y_text = StringVar()
y_label = Label(window, textvariable=y_text, font=('Helvetica, 12'))
y_text.set('    Y    ')

inch_mm_select_var = StringVar(window)
inch_mm_select_var.set("Unit: Inches")
inch_mm_select_menu = OptionMenu(window, inch_mm_select_var, 'Unit: Inches', 'Unit: Millimeters')
inch_mm_select_var.trace('w', inch_mm_select_var_changed)

abs_rel_select_var = StringVar(window)
abs_rel_select_var.set("Mode: Absolute")
abs_rel_select_menu = OptionMenu(window, abs_rel_select_var, 'Mode: Absolute', 'Mode: Relative')
abs_rel_select_var.trace('w', abs_rel_select_var_changed)

#
# Place the widgets in the window
#
depth_label.grid(        row=0, column=0, padx=4, pady=0)
plunge_label.grid(       row=0, column=1, padx=4, pady=4)
depth_entry.grid(        row=1, column=0, padx=4, pady=0)
plunge_entry.grid(       row=1, column=1, padx=4, pady=0)
x_label.grid(            row=2, column=0, padx=4, pady=0)
y_label.grid(            row=2, column=1, padx=4, pady=0)
add_button.grid(         row=0, column=2, padx=4, pady=4)
inch_mm_select_menu.grid(row=1, column=2, padx=4, pady=4, sticky=W)
abs_rel_select_menu.grid(row=2, column=2, padx=4, pady=4, sticky=W)

# create a list for each coordinate pair consisting of the value of X, the value of Y, and two tk
# entry widgets. The widgets will be displayed in the GUI window. Each of these coordinate pair lists
# will be appended to the coordList, previously initialized as an empty list, resulting in a list of
# coordinate pair lists.
#

print(coordList)  # debug temp

#
# Place X and Y entry widgets in the window
#
gridrow = 3
for line_number in range(6):
    coordList[line_number][XWIDGET].grid(row=gridrow,column=0, pady=4, padx=4)
    coordList[line_number][YWIDGET].grid(row=gridrow,column=1, pady=4, padx=4)
    gridrow += 1

# Start the GUI main loop
window.config(menu=menu_bar)
window.mainloop()