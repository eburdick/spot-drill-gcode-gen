#!/usr/bin/python3

# This program takes a series of coordinates and generates the gcode for a cnc machine to spot drill
# at those coordinates. By default it starts at X=0, Y=0, Z=0. Functionality:
#
# GUI: One window with the following widgets...
# Window menu bar with...
#     File menu
#         New
#             Erases everything and presents an empty GUI for creating a new set of points
#             Warning popup to and ask to save.
#         Open
#             Erases everything and populates from a file. After this, changes can be made,
#             including adding and removing points, and modifying depth and plunge rate.
#         Save
#             Save current state to the original file that was opened. If there is no original
#             file, this becomes a save as.
#         Save as
#             Prompt the user for a new file to save current state. If the file exists, a warning
#             box pops up.
#         Write GCode
#             Generates gcode and writes to a file. User is prompted to specify file. If file
#             exists, a warning box pops up.
#         Exit
#             Exits program. If there are unsaved changes, a warning box pops up, giving user
#             the option to save or save as.
#     Edit menu
#         add point
#             Adds a point at the end of the list
#         add point before
#             Add a point before the selected point line
#         add point after
#             Add a point after the selected point line
#         delete
#             Deletes the selected point line
#         move up
#             Moves selected point line above the line above it
#         move down
#             Move the selected point line below the line following it
#     Depth Input
#         specifies how deep to drill. Default .1 inch
#     Plunge Rate Input
#         specified how fast to move the z axis during the cuts. Default: 1.5 inches/minute
#     Add Point
#         adds coordinate input row with blank values.
#     Coordinate Inputs
#         arranged in rows of two each, this is where the user enters X and Y coordinates.
#         The user can enter a number (float), or an expression that evaluates to a number.
#         Each point line has a check button next to it. If this is checked, then an edit
#         command, insert before, insert after, delete, move up or move down will apply to
#         the corresponding point line.
#     Inch/mm menu.
#         Defaults to Inch. If it is changed while there are points in place, they are converted.
#         For example, 1 inch becomes 25.4 mm when switching from inch to mm
#     Absolute/relative menu.
#         Default Absolute. When Relative is active, the first point is absolute and all
#         others are relative to that. For example, if the first point is a 1,1, and the second point is at
#         2,2, absolute mode with show 2,2 for that point, and relative with show 1,1 for that point. If
#         points are already in place, switching between the two will make the appropriate changes.
#         !!! consider having a relative mode where each point is relative to the previous point !!!
#
#           Depth     Plunge Rate [Add Point]
#         __________  ___________ [Unit: Inches -]
#             X            Y      [Mode: Absolute -]
#         __________  ___________ [ ]
#         __________  ___________ [ ]
#         __________  ___________ [ ]
#         __________  ___________ [ ]
#
# Usage Models...
#     Edit existing points list
#         Points lists can be saved to a file. To edit an existing one, user opens the file, which
#         will populate the GUI, deleting anything that was there before. User that modifies it in
#         the GUI.
#     Create new point list
#         User fills in values in the GUI using the editing features. At any point, the GUI content
#         can be saved to a file.
#     Editing
#         Points can be added, deleted and moved. To keep things simple in the GUI, I am doing this
#         by allowing the user to put a check mark on one point at a time, and then pick the
#         desired edit operation for that point, so, for example, to delete a point, you check the
#         box for that line and pick delete from the edit menu. If an edit operation results in
#         a line being gone, the check mark goes away, too. If an edit results in a line being
#         moved, the check mark moves with it. If an edit is impossible, like moving the top line
#         up, it just does not happen. If an edit results in a new point being created, the check
#         mark for the new item is active.
#
# Error checking...
#     The main error we care about is text in the point coordinates that does not represent a
#     number. This is checked at least whenever we process the entire list, including when we
#     save to a file and when we process into a gcode file. We could also check when an entry
#     widget loses focus, like when we hit tab to go to the next field.
#
# Revison History:
#
# ----2021-11-28 10AM
# Starting this history after lots of experiments. Just removed StringVars for entry widgets, because
# they are not really necessary for this application. I will just carry the values in the widgets and
# retrieve them as needed, checking for syntax errors at that point. Syntax errors can also be checked
# When focus moves from numeric fields. We can also check for range errors at that point.
#
# ----2021-11-29 4pm
# In the middle of implementing the selection mechanism.
#
# ----2021-12-2 11:30 pm
# Added number error checking to all of the input widgets on losing focus (<FocusOut>). Still need
# to finish the selection mechanism. Also need to set up number error checking before any function
# that uses the values in the input widgets, because just looking at <FocusOut> events will
# not catch everything.
#
# Implementation notes...
#
# At this point, the selection state is
# in the PointsList class in the form of a member variable row_selected to indicate which
# row is selected. 0 means none. The check button widget for each point lives in the point data
# structure, which is a list of widgets. The value changed callback for those check box widgets
# lives outside of the class, but it is just a utility routine, so that seems fine. An alternative
# would be to just have the check button widgets live in a parallel array in the gui, but having
# all of the state in the class feels cleaner.
#
# Selection actions...
# * select a line - click on the line's check button, changing its state from unchecked to checked.
# This will call the check_select_change(row) callback, which will check the new state of the widget.
# If the new state is "checked" then it will change the row_selected state to the number of the row
# and then force all of the other check box widgets to be unchecked.
# * unselect a line - click on the line's check button, changing its state from checked to unchecked.
# This will call the check_select_change(row) callback, which will
# If the new state is "unchecked" then it will set the row_selected state to 0, because at this
# point, none of the boxes will be checked.
#
# ----2021-12-4 10 PM
# Cleaned up the row indexing stuff. I was starting the row numbers at 1 instead of 0, which was
# getting confusing. Changed the row numbers to start at zero, so they match the list element
# index. The only thing that is off by one is now point_count in the points list class. Also
# removed old code that is no longer needed and got rid of triple quote comment blocks, which
# are documentation strings, not comment blocks. Discovered PyCharm ctrl+/ for doing mass
# commenting. Next, get back to selection stuff.
#
# ----2021-12-10 5:30 pm
# Finished selection stuff. To carry the state of selection of each point, added a BooleanVar
# to each point to carry the state of the selection check button. Added deselect_row method to
# the pointslist class.
#
# ---- 11 pm
# Added code for edit menu with tearoff, including add point and delete point. Delete point
# needs to be updated to re-create all of the check buttons beyond the deleted one so that
# the callback gets the right index for selection. Otherwise everything is off by one after
# a delete because the pragma remembers its original index.

import numexpr                       # for allowing numeric expressions in coordinate fields
from tkinter import *                # GUI stuff
from tkinter import ttk              # more widgets
# from tkinter.scrolledtext import ScrolledText  # not sure why we need to import a module for scrolled text
from tkinter import filedialog
from tkinter import messagebox as mb

# Point index constants. A point is a list of values with indices defined by these constants.
POINTNUMBER = 0
XWIDGET = 1
YWIDGET = 2
CHECKBUTTON = 3
SELECTED = 4

NONESELECTED = -1

XCOLUMN = 0
YCOLUMN = 1
SELECTBOXCOLUMN = 2

POINTROWOFFSET = 3  # starting row of points list in the gui
BASEDIRECTORY = 'C:/development/python/PycharmProjects/spot-drill-gcode-gen'
window = Tk()
 
 

#
# Check that the text in an input widget is a number. If not, turn the widget
# background red and raise a message box.
#
def check_if_num(event):
    widget = event.widget
    #
    # attempt to convert the string to a number. If it fails, it will throw a ValueError
    # exception, which we catch to inform the user by setting the corresponding widget's 
    # background to red
    #
    try:
        float(widget.get())
        widget.config(bg="WHITE")
    except ValueError:
        widget.config(bg="RED")
        mb.showerror("error", widget.get() + " is not a number")


class PointsList:
    #
    # The list of points in the application and methods for creating, deleting, etc.
    #
    points = []
    point_count = 0
    row_selected = NONESELECTED  # NONESELECTED is none selected.

    #
    # Constructor initializes the points list and the points count
    #
    def __init__(self):
        self.points = []
        self.point_count = 0
        self.row_selected = NONESELECTED
    #
    # Clear the object back to its initial state. Effectively remove all points
    #
    def clear(self):
        self.points = []
        self.point_count = 0

    #
    # append_point adds a point at the end of the list and adds a row to the gui point display.
    # The GUI includes a selection check button on each line. That is added to each list element.
    #
    def append_point(self, x, y):
        self.point_count += 1
        index = self.point_count-1
        #
        # Create the entry widgets for this point
        #
        xentry = Entry(window)
        xentry.insert(0, x)
        yentry = Entry(window)
        yentry.insert(0, y)
        checkvar = BooleanVar()
        # create the check button for this point. Its state change callback passes the index
        # of this point, which will be used in the selection code.
        # This is implemented as an inline (lambda) function that calls the callback
        # with the argument.
        check_button = Checkbutton(window, variable=checkvar, command=lambda: check_select_change(index, checkvar))

        #
        # append the point as a list to the end of the points list
        #
        self.points.append([index,
                            xentry,
                            yentry,
                            check_button,
                            checkvar])
        #
        # place entry widgets and check button on the grid
        #
        self.points[index][XWIDGET].grid(row=self.point_count+POINTROWOFFSET, column=XCOLUMN, padx=4, pady=0)
        self.points[index][YWIDGET].grid(row=self.point_count+POINTROWOFFSET, column=YCOLUMN, padx=4, pady=0)
        self.points[index][CHECKBUTTON].grid(row=self.point_count+POINTROWOFFSET, column=SELECTBOXCOLUMN, sticky=W)
        #
        # set up event callback for entry widget loss of focus. This is so we can check whether the text
        # in the widget is a valid number
        #
        self.points[index][XWIDGET].bind('<FocusOut>', check_if_num)
        self.points[index][YWIDGET].bind('<FocusOut>', check_if_num)
        #
        # set up even callback for
        #
        return self.point_count
    
    # select_row mainly sets member variable row_selected to the specified row number. But it also
    # unchecks the rest of the check buttons. This could be done by just forcing the existing check
    # button to be unchecked, but to make sure we don't miss one, we just uncheck all buttons except
    # the target one.
    def select_row(self, row):
        #
        # deselect all points except the one in the target row.
        #
        print("row being selected" + str(row))
        print("old row selected " + str(self.row_selected))
        self.row_selected = NONESELECTED  # preset for the case that no row is selected
        for pt in self.points:
            if self.points.index(pt) != row:
                pt[CHECKBUTTON].deselect()
        self.row_selected = row
        print("new row selected " + str(self.row_selected))

    def deselect_row(self, row):
        #
        # The user has unchecked a checkbox. This should result in no boxes checked,
        # so we just set row_selected to NONESELECTED
        #
        print("old row selected " + str(self.row_selected))
        print("row being deslected " + str(row))
        self.row_selected = NONESELECTED
        print("new row selected " + str(self.row_selected))

    def delete_point(self, ptnum):
        #
        # Clear the points display from the gui
        #
        self.clear_points_from_grid()
        #
        # loop through the points until the point number to be removed is encountered. At that point,
        # the point is removed from the points list, and point_count is deleted. Also, the line number
        # offset is set to -1 so that all following points will be numbered one less.
        #
        line_number_offset = 0
        i = 0
        while i < len(self.points):
            if self.points[i][POINTNUMBER] == ptnum:
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
        #
        # Now, with the target point gone, we re-display the remaining points.
        #
        self.place_points_on_grid()
        #if line_number_offset == -1:
        #    return 0
        #else:
        #    return 1

    def read_point(self, ptnum):
        values = (self.points[ptnum][POINTNUMBER],
                  self.points[ptnum][XWIDGET].get(),
                  self.points[ptnum][YWIDGET].get(),
                  self.points[ptnum][SELECTED].get())
        return values

    def clear_points_from_grid(self):
        for clrpoint in self.points:
            clrpoint[XWIDGET].grid_remove()
            clrpoint[YWIDGET].grid_remove()
            clrpoint[CHECKBUTTON].grid_remove()

    def place_points_on_grid(self):
        for placeindex in range(0, len(self.points)):
            self.points[placeindex][XWIDGET].grid(row=placeindex + POINTROWOFFSET, column=XCOLUMN, padx=4, pady=0)
            self.points[placeindex][YWIDGET].grid(row=placeindex + POINTROWOFFSET, column=YCOLUMN, padx=4, pady=0)
            self.points[placeindex][CHECKBUTTON].grid(row=placeindex + POINTROWOFFSET, column=SELECTBOXCOLUMN, sticky=W)
        self.row_selected = NONESELECTED


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
    print(plist.points.index(point))
    print(point)

# print('deleting first point')
# myid = plist.delete_point(0)
# for point in plist.points:
#     print(point)
# print('deleting last point')
# myid = plist.delete_point(2)
# for point in plist.points:
#     print(point)

# end of class PointsList test code

# test code for type conversion
test = float(numexpr.evaluate('.5+1'))
print(test)
print(test*2.54)
print(type(test))
# end type conversion test code



def check_select_change(line, val):
    print("check select changed...index: " + str(line))
    print("checkbutton state: " + str(val.get()))
    if val.get():
        plist.select_row(line)
    else:
        plist.deselect_row(line)
    # for idx in range(0, len(plist.points)):
    #     print(plist.read_point(idx))

def open_pressed():
    # Open means read a coordinates file and make the points in that file the current points in 
    # the application. That file also has values for depth and plunge rate. 
    print("Open button")
    open_file = filedialog.askopenfilename(title='Open File', initialdir=BASEDIRECTORY)
    print(open_file)
    mb.askyesno('are you sure?')
    # open the coordinates file. This is just a pair of numbers on each line, x, then y, separated by a single
    # space. The readLines method creates a list of lines from this file, then we split each line into the two
    # fields (split()) and remove the end of line (strip())
    coords_file = open(open_file, "r")
    coords_lines = coords_file.readlines()

    for line in coords_lines:
        coords = line.strip().split(' ')
        # just print the coords value for now.
        print(coords)
        
    line_number = 0
    for line in coords_lines:
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
def display_points(lst=PointsList):
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


def addpoint_pressed():
    print("Add Point button")


def deletepoint_pressed():
    plist.delete_point(plist.row_selected)
    print("Delete Point button")


def gen_gcode_pressed():
    print("Points for GCode")
    print("row_selected: " + str(plist.row_selected))
    for ptindex in range(0, len(plist.points)):
        print(plist.read_point(ptindex))


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


coord_list = []

# coord_list.append([])

# gcodeFile = open(gcodeFileName, "w")

# set up the GUI

s = ttk.Style()
s.theme_use('xpnative')
s.configure('window.TFrame', font=('Helvetica', 30))
#
# create and size the main window
#
window.title('Spot Drilling Tool')

menu_bar = Menu(window)
filemenu = Menu(menu_bar, tearoff=1)
filemenu.add_command(label="New", command=new_pressed)
filemenu.add_command(label="Open", command=open_pressed)
filemenu.add_command(label="Save", command=save_pressed)
filemenu.add_command(label="Save as...", command=save_as_pressed)
filemenu.add_command(label="Write GCode", command=gen_gcode_pressed)
filemenu.add_command(label="Exit", command=exit_pressed)
menu_bar.add_cascade(label="File", menu=filemenu)
editmenu = Menu(menu_bar, tearoff=1)
editmenu.add_command(label="Add Point", command=addpoint_pressed)
editmenu.add_command(label="Delete Point", command=deletepoint_pressed)
menu_bar.add_cascade(label="Edit", menu=editmenu)

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


x_text = StringVar()
x_label = Label(window, textvariable=x_text, font=('Helvetica', 12))
x_text.set('    X    ')

y_text = StringVar()
y_label = Label(window, textvariable=y_text, font='Helvetica, 12')
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
inch_mm_select_menu.grid(row=1, column=2, padx=4, pady=4, sticky=W)
abs_rel_select_menu.grid(row=2, column=2, padx=4, pady=4, sticky=W)

# create a list for each coordinate pair consisting of the value of X, the value of Y, and two tk
# entry widgets. The widgets will be displayed in the GUI window. Each of these coordinate pair lists
# will be appended to the coord_list, previously initialized as an empty list, resulting in a list of
# coordinate pair lists.
#

# print(coord_list)  # debug temp


# Start the GUI main loop
window.config(menu=menu_bar)

window.protocol("WM_DELETE_WINDOW", on_closing)

window.mainloop()
