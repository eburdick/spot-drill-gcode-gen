#!/usr/bin/python3
"""

This program takes a series of coordinates and generates the gcode for a cnc machine to spot drill
at those coordinates. By default it starts at X=0, Y=0, Z=0. Functionality:

GUI: One window with the following widgets...
Window menu bar with...
    File menu
        New
            Erases everything and presents an empty GUI for creating a new set of points
            Warning popup to and ask to save.
        Open
            Erases everything and populates from a file. After this, changes can be made,
            including adding and removing points, and modifying depth and plunge rate.
        Save
            Save current state to the original file that was opened. If there is no original
            file, this becomes a save as.
        Save as
            Prompt the user for a new file to save current state. If the file exists, a warning
            box pops up.
        Write GCode
            Generates gcode and writes to a file. User is prompted to specify file. If file
            exists, a warning box pops up.
        Exit
            Exits program. If there are unsaved changes, a warning box pops up, giving user
            the option to save or save as.
    Edit menu
        add point
            Adds a point at the end of the list
        add point before
            Add a point before the selected point line
        add point after
            Add a point after the selected point line
        delete
            Deletes the selected point line
        move up
            Moves selected point line above the line above it
        move down
            Move the selected point line below the line following it
    Depth Input
        specifies how deep to drill. Default .1 inch
    Plunge Rate Input
        specified how fast to move the z axis during the cuts. Default: 1.5 inches/minute
    Add Point
        adds coordinate input row with blank values.
    Coordinate Inputs
        arranged in rows of two each, this is where the user enters X and Y coordinates.
        The user can enter a number (float), or an expression that evaluates to a number.
        Each point line has a check button next to it. If this is checked, then an edit
        command, insert before, insert after, delete, move up or move down will apply to
        the corresponding point line.
    Inch/mm menu.
        Defaults to Inch. If it is changed while there are points in place, they are converted.
        For example, 1 inch becomes 25.4 mm when switching from inch to mm
    Absolute/relative menu.
        Default Absolute. When Relative is active, the first point is absolute and all
        others are relative to that. For example, if the first point is a 1,1, and the second point is at
        2,2, absolute mode with show 2,2 for that point, and relative with show 1,1 for that point. If
        points are already in place, switching between the two will make the appropriate changes.
        !!! consider having a relative mode where each point is relative to the previous point !!!

          Depth     Plunge Rate [Add Point]
        __________  ___________ [Unit: Inches -]
            X            Y      [Mode: Absolute -]
        __________  ___________ [ ]
        __________  ___________ [ ]
        __________  ___________ [ ]
        __________  ___________ [ ]

Usage Models...
    Edit existing points list
        Points lists can be saved to a file. To edit an existing one, user opens the file, which
        will populate the GUI, deleting anything that was there before. User that modifies it in
        the GUI.
    Create new point list
        User fills in values in the GUI using the editing features. At any point, the GUI content
        can be saved to a file.
    Editing
        Points can be added, deleted and moved. To keep things simple in the GUI, I am doing this
        by allowing the user to put a check mark on one point at a time, and then pick the
        desired edit operation for that point, so, for example, to delete a point, you check the
        box for that line and pick delete from the edit menu. If an edit operation results in
        a line being gone, the check mark goes away, too. If an edit results in a line being
        moved, the check mark moves with it. If an edit is impossible, like moving the top line
        up, it just does not happen. If an edit results in a new point being created, the check
        mark for the new item is active.

Error checking...
    The main error we care about is text in the point coordinates that does not represent a
    number. This is checked at least whenever we process the entire list, including when we
    save to a file and when we process into a gcode file. We could also check when an entry
    widget loses focus, like when we hit tab to go to the next field.

Revison History:

2021-11-28 10AM
Starting this history after lots of experiments. Just removed StringVars for entry widgets, because
they are not really necessary for this application. I will just carry the values in the widgets and
retrieve them as needed, checking for syntax errors at that point. Syntax errors can also be checked
When focus moves from numeric fields. We can also check for range errors at that point.

2021-11-29 4pm
In the middle of implementing the selection mechanism.

2021-12-2 11:30 pm
Added number error checking to all of the input widgets on losing focus (<FocusOut>). Still need
to finish the selection mechanism. Also need to set up number error checking before any function
that uses the values in the input widgets, because just looking at <FocusOut> events will
not catch everything.

Implementation notes...

At this point, the selection state is
in the PointsList class in the form of a member variable row_selected to indicate which
row is selected. 0 means none. The check button widget for each point lives in the point data
structure, which is a list of widgets. The value changed callback for those check box widgets
lives outside of the class, but it is just a utility routine, so that seems fine. An alternative
would be to just have the check button widgets live in a parallel array in the gui, but having
all of the state in the class feels cleaner.

Selection actions...
* select a line - click on the line's check button, changing its state from unchecked to checked.
This will call the check_state_change(row) callback, which will check the new state of the widget.
If the new state is "checked" then it will change the row_selected state to the number of the row
and then force all of the other check box widgets to be unchecked.
* unselect a line - click on the line's check button, changing its state from checked to unchecked.
This will call the check_state_change(row) callback, which will check the new state of the widget.
If the new state is "unchecked" then it will set the row_selected state to 0, because at this
point, none of the boxes will be checked.


"""

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
XWIDGET = 1
YWIDGET = 2
CHECKBUTTON = 3

point_row_offset = 3  # starting row of points list in the gui
baseDirectory = 'C:\development\python\PycharmProjects\spot-drill-gcode-gen'
window = Tk()

def check_state_change(line):
    print("check state changed...index: " + str(line))

#
# Check that the text in an input widget is a number. If not, turn the widget
# background red and raise a message box.
#
def check_if_num(event):
    widget = event.widget
    #
    # attempt to convert the string to a number. If it fails, it will throw a ValueError
    # exception, which we catch to inform the user.
    #
    try:
        float(widget.get())
        widget.config(bg="WHITE")
    except ValueError:
        widget.config(bg="RED")
        mb.showerror("error", widget.get() + " is not a number")

class PointsList:    #
    # The list of points in the application and methods for creating, deleting, etc.
    #
    points = []
    point_count = 0
    row_selected = 0  # 0 is none selected. Note row numbers are one bigger that the corresponding index

    def __init__(self):
        self.points = []
        self.point_count = 0

    def clear(self):
        self.points = []
        self.point_count = 0

# append_point adds a point at the end of the list and adds a row to the gui point display.
    def append_point(self, x, y):
        self.point_count += 1
        line = self.point_count
        #
        # Create the entry widgets and check button for this point
        #
        xentry = Entry(window)
        xentry.insert(0, x)
        yentry = Entry(window)
        yentry.insert(0, y)
        # check button state change callback passes the line number of this point.
        # This is implemented as an inline (lambda) function that calls the callback
        # with the argument.
        check_button = Checkbutton(window, command=lambda: check_state_change(line))
        #
        # append the point t0 the end of the points list
        #
        self.points.append([self.point_count,
                            xentry,
                            yentry,
                            check_button])
        # place entry widgets and check button on the grid
        self.points[self.point_count-1][XWIDGET].grid(row=self.point_count+point_row_offset, column=0, padx=4, pady=0)
        self.points[self.point_count-1][YWIDGET].grid(row=self.point_count+point_row_offset, column=1, padx=4, pady=0)
        self.points[self.point_count-1][CHECKBUTTON].grid(row=self.point_count+point_row_offset, column=2, sticky=W)
        # set up event callback for entry widget loss of focus. This is so we can check whether the text
        # in the widget is a valid number
        self.points[self.point_count-1][XWIDGET].bind('<FocusOut>', check_if_num)
        self.points[self.point_count-1][YWIDGET].bind('<FocusOut>', check_if_num)
        return self.point_count

    #
    def select_row(self, row):
        #
        # deselect the existing selected row, if any, then set the target row as row_selected. Note this
        # will be called from the GUI, which will have already set the widget as being selected.
        #
        print("row selected" + str(self.row_selected))
        if self.row_selected >= 0:
            self.points[self.row_selected-1][CHECKBUTTON].deselect()
        row_selected = row

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

    def read_point(self, ptnum):
        values = (self.points[ptnum][XWIDGET].get(), self.points[ptnum][YWIDGET].get())
        return values


# Test code for PointList class
plist = PointsList()
print('initial point list')
for point in plist.points:
    print(point)
print('appending point')
myid = plist.append_point('', 2.0)
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
"""
print('deleting first point')
myid = plist.delete_point(1)
for point in plist.points:
    print(point)
print('deleting last point')
myid = plist.delete_point(3)
for point in plist.points:
    print(point)
    """
# end of class PointsList test code

# test code for type conversion
test = float(numexpr.evaluate('.5+1'))
print(test)
print(test*2.54)
print(type(test))
# end type conversion test code

# test reading entry widgets without StringVar
print("   reading points...")
print(plist.read_point(0))
print(plist.read_point(1))
# test reading entry widgets without StringVar


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

def check_state_change(line):
    print("check state changed")
    print("index: " + str(line))
    plist.select_row(line)


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
depth_entry.bind('<FocusOut>', check_if_num)

plunge_entry = Entry(window)
plunge_entry.bind('<FocusOut>', check_if_num)

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