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
#
# ----2021-12-22 11 pm
# debugging the delete line function. The problem is that the command functions in the checkboxes
# beyond the deleted line have the wrong index. I tried creating a new checkbox for each of
# these, but it is not working. It dawned on me that what I really need to do is move all of
# these checkboxes down one position in the list, then they will be in the correct physical
# position. For example, if I delete line 1, then the new line 1 will now have a checkbox
# that thinks it is in line 2. If I copy the line 1 checkbox to line 2, it should be right.
# but I have to do this before I actually delete line 1. But the old line 2 checkbox also
# has to be copied to the old line 3, and so on, so this copy should be done backward order
# from the last line to the line after the deleted one. Maybe the whole operation should be
# done in this order and stopped when the target line is deleted. I'll look at this when I get
# back to this.
#
# ----2021-12-24 10 pm
# finished re-doing delete line function. The new approach was actually easy. Also added a test
# to do nothing if nothing is selected. Implemented add point gui function. Just one line of
# code added. Researched binding keys to the entry widgets, especially the <Return> key. Not sure
# what I am going to do here, but probably make <Return> do the same thing as tab within the
# coordinate entry area. Tab progression is based on "stacking Order," which can apparently
# be changed using the lift() method to move a widget up in the stack. Definately need to do
# this to get the points in the right order for the tab key. Another thing to explore
# is <<next window>> and event_generate
#
# ----2021-12-25 11:30 pm
# Added move up and move down buttons with tooltips. To get the tooltips, I had to import the
# tkinter.tix module to get the Balloon object, but that broke the option menu calls, because
# tix has and incompatible object of the same name. Some reading told me that importing
# tkinter with from tkinter import * is not really the right way to do it, and it is better
# to use "import tkinter as tk," and "import tkinter.tix as tix." The allows you to specify which
# module you want to use for each object. That meant I had to prefix all tkinter stuff with tk.,
# and all tix stuff with tix., but that was not hard. I found some wierdness with the grid
# geometry manager that caused widgets to move around as other widgets were removed and added
# from the grid, and it resulted in doing an add point operation placing the line in a visually
# wrong place. I fixed this by creating a frame for the buttons and option menues on the right
# side, so they use that frame's grid instead of the main window's grid. The frame is placed with
# as rowspan so that it takes up multiple grid positions on the main window grid.
#
# Next, implement the move up and move down keys, which just involves swapping X and Y values.
# pretty simple. Also, I want to move Add Point and Delete Point to the button frame so they
# are easily accessible without the pulldown. After that, I need to implement all of the file
# stuff, including gcode generation.

import numexpr                       # for allowing numeric expressions in coordinate fields
import tkinter as tk
import tkinter.tix as tix
#from tkinter import *                # GUI stuff
from tkinter import ttk              # more widgets
from tkinter import filedialog
from tkinter import messagebox as mb
from tkinter import font

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
window = tix.Tk()
 
fonts = sorted(list(font.families()))
print(fonts)

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
        xentry = tk.Entry(window)
        xentry.insert(0, x)
        yentry = tk.Entry(window)
        yentry.insert(0, y)
        checkvar = tk.BooleanVar()
        # create the check button for this point. Its state change callback passes the index
        # of this point, which will be used in the selection code.
        # This is implemented as an inline (lambda) function that calls the callback
        # with the argument.
        check_button = tk.Checkbutton(window, variable=checkvar, command=lambda: check_select_change(index, checkvar))

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
        print("placing point. Row = " + str(self.point_count+POINTROWOFFSET))

        self.points[index][XWIDGET].grid(row=self.point_count+POINTROWOFFSET, column=XCOLUMN, padx=4, pady=0)
        self.points[index][YWIDGET].grid(row=self.point_count+POINTROWOFFSET, column=YCOLUMN, padx=4, pady=0)
        self.points[index][CHECKBUTTON].grid(row=self.point_count+POINTROWOFFSET, column=SELECTBOXCOLUMN, sticky=tk.W)
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
        # Check if any points are selected. If not, then return without doing anything
        #
        if self.row_selected == NONESELECTED:
            return
        #
        # Clear the points display from the gui
        #
        self.clear_points_from_grid()
        #
        # Since we are deleting a point, all points after it need to appear one lower in the list, thus
        # higher in the physical window. This means we want to change the index number of those points
        # to be one less, and associate the selection check button for each physical row with the point
        # that moves to that row. In the code, the easiest way to do this is to start at the end of the
        # list and work backward until we reach the point to be deleted. A special case is when the last
        # point is the one being deleted, in which case we just delete that point and return.
        #
        # Traverse the points list in reverse
        for pt in reversed(self.points):
            # If this point is the point to be deleted, just delete it and decrement the point count.
            # after this, we are done, so we break out of the loop.
            if ptnum == pt[POINTNUMBER]:
                del self.points[ptnum]
                self.point_count -= 1
                break
            # If this point is not the point to be deleted, move the checkbutton from the adjacent
            # lower point to this one, and decrement the point number so that it is right after
            # a lower point is deleted.
            else:
                idx = pt[POINTNUMBER]
                self.points[idx][CHECKBUTTON] = self.points[idx-1][CHECKBUTTON]
                self.points[idx][POINTNUMBER] = idx-1
                pt[CHECKBUTTON].deselect()
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
            self.points[placeindex][CHECKBUTTON].grid(row=placeindex + POINTROWOFFSET, column=SELECTBOXCOLUMN, sticky=tk.W)
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
    print(point)

# end of class PointsList test code



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


def new_pressed():
    print("New button")


def save_pressed():
    print("Save button")
    save_file = filedialog.asksaveasfile(title='Open File')
    print(save_file)


def save_as_pressed():
    print("Save As button")

#
# when Add Point is pressed, we add a point at the end of the points list by calling
#
def addpoint_pressed():
    print("Add Point button")
    myid = plist.append_point('', '')


def deletepoint_pressed():
    print("Delete Point button, row_selected = " + str(plist.row_selected))
    plist.delete_point(plist.row_selected)
    for point in plist.points:
        print(point)


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

def up_button_pressed():
    print("up button pressed")

def down_button_pressed():
    print("down button pressed")

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

menu_bar = tk.Menu(window)
filemenu = tk.Menu(menu_bar, tearoff=1)
filemenu.add_command(label="New", command=new_pressed)
filemenu.add_command(label="Open", command=open_pressed)
filemenu.add_command(label="Save", command=save_pressed)
filemenu.add_command(label="Save as...", command=save_as_pressed)
filemenu.add_command(label="Write GCode", command=gen_gcode_pressed)
filemenu.add_command(label="Exit", command=exit_pressed)
menu_bar.add_cascade(label="File", menu=filemenu)
editmenu = tk.Menu(menu_bar, tearoff=1)
editmenu.add_command(label="Add Point", command=addpoint_pressed)
editmenu.add_command(label="Delete Point", command=deletepoint_pressed)
menu_bar.add_cascade(label="Edit", menu=editmenu)

#
# Create the GUI widgets
#
button_frame = ttk.Frame(window)
depth_text = tk.StringVar()
depth_label = tk.Label(window, textvariable=depth_text, font=('Helvetica', 12))
depth_text.set('Depth')

plunge_text = tk.StringVar()
plunge_label = tk.Label(window, textvariable=plunge_text, font=('Helvetica', 12))
plunge_text.set('Plunge Rate')

depth_entry = tk.Entry(window)
depth_entry.bind('<FocusOut>', check_if_num)

plunge_entry = tk.Entry(window)
plunge_entry.bind('<FocusOut>', check_if_num)


x_text = tk.StringVar()
x_label = tk.Label(window, textvariable=x_text, font=('Helvetica', 12))
x_text.set('    X    ')

# code for sampling fonts
# up_button = Button(window, text="abcdefghijklmnopqrstuvwxyz0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ", font='tt-icon-font 12', command=up_button_pressed)

up_tip = tix.Balloon(window)
up_button = tk.Button(button_frame, text="  k  ", font='tt-icon-font 12', command=up_button_pressed)
up_tip.bind_widget(up_button,balloonmsg="Swap selected point with the one above it")

down_tip = tix.Balloon(window)
down_button = tk.Button(button_frame, text="  c  ", font='tt-icon-font 12', command=down_button_pressed)
down_tip.bind_widget(down_button,balloonmsg="Swap selected point with the one below it")

y_text = tk.StringVar()
y_label = tk.Label(window, textvariable=y_text, font='Helvetica, 12')
y_text.set('    Y    ')

inch_mm_select_var = tk.StringVar(button_frame)
inch_mm_select_var.set("Unit: Inches")
inch_mm_select_menu = tk.OptionMenu(button_frame, inch_mm_select_var, 'Unit: Inches', 'Unit: Millimeters')
inch_mm_select_var.trace('w', inch_mm_select_var_changed)

abs_rel_select_var = tk.StringVar(button_frame)
abs_rel_select_var.set("Mode: Absolute")
abs_rel_select_menu = tk.OptionMenu(button_frame, abs_rel_select_var, 'Mode: Absolute', 'Mode: Relative')
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
button_frame.grid(       row=0, column=3, rowspan=6)
inch_mm_select_menu.grid(row=0, column=0, padx=0, pady=4, sticky=tk.W)
abs_rel_select_menu.grid(row=1, column=0, padx=0, pady=4, sticky=tk.W)
up_button.grid          (row=2, column=0, padx=0, pady=0, sticky=tk.W)
down_button.grid        (row=3, column=0, padx=0, pady=0, sticky=tk.W)

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
