#!/usr/bin/python3

#
# This program takes a series of coordinates and generates the gcode for a cnc machine to spot drill
# at those coordinates. By default it starts at X=0, Y=0, Z=0. Functionality:
#
# GUI: One window with the following widgets...
#    Window menu bar with...
#        File menu
#            New
#                Erases everything and presents an empty GUI for creating a new set of points
#                Warning popup to and ask to save.
#            Open
#                Erases everything and populates from a file. After this, changes can be made,
#                including adding and removing points, and modifying depth and plunge rate.
#            Save
#                Save current state to the original file that was opened. If there is no original
#                file, this becomes a save as.
#            Save as
#                Prompt the user for a new file to save current state. If the file exists, a warning
#                box pops up.
#            Write GCode
#                Generates gcode and writes to a file. User is prompted to specify file. If file
#                exists, a warning box pops up.
#            Exit
#                Exits program. If there are unsaved changes, a warning box pops up, giving user
#                the option to save or save as.
#    Depth Input - specifies how deep to drill. Default .1 inch
#    Plunge Rate Input - specified how fast to move the z axis during the cuts. Default: 1.5 inches/minute
#    Add Point - adds coordinate input row with blank values.
#    Coordinate Inputs - arranged in rows of two each, this is where the user enters X and Y coordinates.
#        The user can enter a number (float), or an expression that evaluates to a number.
#    Inch/mm menu. Defaults to Inch. If it is changed while there are points in place, they are converted.
#        For example, 1 inch becomes 25.4 mm when switching from inch to mm
#    Absolute/relative menu. Default Absolute. When Relative is active, the first point is absolute and all
#        others are relative to that. For example, if the first point is a 1,1, and the second point is at
#        2,2, absolute mode with show 2,2 for that point, and relative with show 1,1 for that point. If
#        points are already in place, switching between the two will make the appropriate changes.
#        !!! consider having a relative mode where each point is relative to the previous point !!!
#
#      Depth       Plunge Rate     [Add Point]
#      __________  __________    [Unit: Inches -]
#          X          Y          [Mode: Absolute -]
#      __________  __________
#      __________  __________
#      __________  __________
#      __________  __________
#


#
# To start, we will just read the coordinates from a file, but adding a fill in the blanks gui would make
# it easier to use and avoid syntax error issues.
#

import numexpr                       # for allowing numeric expressions in coordinate fields
from tkinter import *                # GUI stuff
from tkinter import ttk              # more widgets
from tkinter.scrolledtext import ScrolledText  # not sure why we need to import a module for scrolled text
from tkinter import filedialog
from tkinter import messagebox as mb

# Point index constants. A point is a list of values with indices defined by these constants.
POINTNUMBER = 0
XVALUE = 1
YVALUE = 2
XWIDGET = 3
YWIDGET = 4
XSTRINGVAR = 5
YSTRINGVAR = 6
point_row_offset = 3
baseDirectory = 'C:\development\python\PycharmProjects\spot-drill-gcode-gen'
window = Tk()


def xcallback(sv):
    print("x="+sv.get())

def ycallback(sv):
    print("y="+sv.get())






class PointsList:
    #
    # The list of points in the application and methods for creating, deleting, etc.
    #
    points = []
    point_count = 0;

    def __init__(self):
        self.points = []
        self.point_count = 0;

    def clear(self):
        self.points = []
        self.point_count = 0;

# append_point adds a point at the end of the list and adds a row to the gui point display.
    def append_point(self, x, y):
        self.point_count += 1
        # create StringVar objects and assign values to them
        x_stringvar = StringVar(window)
        x_stringvar.set(x)
        y_stringvar = StringVar(window)
        y_stringvar.set(y)
        # set up a callback for capturing user changes to the widgets. Probably don't need this, though
        x_stringvar.trace("w", lambda name, index, mode, sv=x_stringvar: xcallback(sv))
        y_stringvar.trace("w", lambda name, index, mode, sv=y_stringvar: ycallback(sv))
        self.points.append([self.point_count,
                            x,
                            y,
                            Entry(window, textvariable=x_stringvar),
                            Entry(window, textvariable=y_stringvar),
                            x_stringvar,
                            y_stringvar])
    # place entry widgets on the grid
        self.points[self.point_count-1][XWIDGET].grid(row=self.point_count+point_row_offset, column=0, padx=4, pady=0)
        self.points[self.point_count-1][YWIDGET].grid(row=self.point_count+point_row_offset, column=1, padx=4, pady=0)


        return self.point_count


    def delete_point(self, ptnum):
        # print("PointsList delete_point call: Point #" + str(ptnum))
        line_number_offset = 0
        i = 0
        while i < len(self.points):
            if self.points[i][POINTNUMBER] == ptnum:
                # print("PointsList deleting point at index " + str(i))
                # The point number of the point in the list matches the target point number. Delete the
                # point and set the index_offset to -1. The will be be used to decrement the line number
                # of subsequent lines. We do not increment the list index here because the next point will
                # take the place of this one after it is deleted.
                del self.points[i]
                self.point_count -= 1
                line_number_offset = -1
            else:
                # The point number of the point in the list does not match the target point number.
                # Adjust the line number by adding line_number_offset, which starts at zero and gets
                # set to -1 after the target point is deleted.
                self.points[i][POINTNUMBER] += line_number_offset
                i += 1
        if line_number_offset == -1:
            return 0
        else:
            return 1


# Test code for PointList class
plist = PointsList()
print('initial point list')
for point in plist.points:
    print(point)
print('appending point')
myid = plist.append_point(1.0, 2.0)
for point in plist.points:
    print(point)
print('appending point')
myid = plist.append_point(3.0, 4.0)
for point in plist.points:
    print(point)
print('appending point')
myid = plist.append_point(5.0, 6.0)
for point in plist.points:
    print(point)
print('appending point')
myid = plist.append_point(7.0, 8.0)
for point in plist.points:
    print(point)
print('deleting first point')
myid = plist.delete_point(1)
for point in plist.points:
    print(point)
print('deleting last point')
myid = plist.delete_point(3)
for point in plist.points:
    print(point)
# end of class PointsList test code

# test code for type conversion
test = float(numexpr.evaluate('.5+1'))
print(test)
print(test*2.54)
print(type(test))
# end type conversion test code



"""
# temporary code to open working files. This will be replaced by a file selection box later
coordsFileName = "test_coords.txt"
gcodeFileName = "test_gcode.nc"
"""

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
    mb.askyesno('are you sure?')
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
#        coordList.append([coords[XVALUE], coords[YVALUE], Entry(window), Entry(window), StringVar(), StringVar()])
#       coordList[line_number][XWIDGET].insert(END, coordList[line_number][XVALUE])
#       coordList[line_number][YWIDGET].insert(END, coordList[line_number]
        line_number += 1

#
# display_points takes the list of points in a PointsList object and displays them in the GUI. The display is a
# column of pairs of Entry widgets with a line for each list element. To start, we delete all of the Entry
# widgets already there. This just keeps things clean, because we create new ones every time we display a
# new point list.
#
def display_points(lst = PointsList):
    # !!! placeholder code. Replace with gui placement code
    for thing in lst.points:
        print(thing)


def new_pressed():
    print("New button")


def save_pressed():
    print("Save button")
    save_file = filedialog.asksaveasfile(title='Open File')
    print(save_file)

def save_as_pressed():
    print("Save As button")


def gen_gcode_pressed():
    print("Gen Gcode button")


def exit_pressed():
    print("Exit button. Clean up has to happen here.")
    clean_up_and_exit()

def abs_rel_select_var_changed(*args):
    print("Absolute/Relative Menu Changed")
    print(abs_rel_select_var.get())


def inch_mm_select_var_changed(*args):
    print("Inch/mm menu changed")
    print(inch_mm_select_var.get())


def add_button_pressed():
    print("Add Point button")


def clean_up_and_exit():
    print("cleanup and exit called")
    window.destroy()

def on_closing():
    print("on_closing called")
    if mb.askokcancel("Quit", "Do you want to quit?"):
        clean_up_and_exit()

coordList = []

# coordList.append([])

# gcodeFile = open(gcodeFileName, "w")

# set up the GUI

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

# print(coordList)  # debug temp

#
# Place X and Y entry widgets in the window
#
"""
gridrow = 3
for line_number in range(6):
    coordList[line_number][XWIDGET].grid(row=gridrow,column=0, pady=4, padx=4)
    coordList[line_number][YWIDGET].grid(row=gridrow,column=1, pady=4, padx=4)
    gridrow += 1
"""
# Start the GUI main loop
window.config(menu=menu_bar)



window.protocol("WM_DELETE_WINDOW", on_closing)

window.mainloop()