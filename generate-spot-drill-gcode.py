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
#
# User data inputs...
#     Depth Input
#         specifies how deep to drill. Default .1 inch
#     Plunge Rate Input
#         specified how fast to move the z axis during the cuts. Default: 1.5 inches/minute
#     Coordinate Inputs
#         arranged in rows of two each, this is where the user enters X and Y coordinates.
#         The user can enter a number (float), or an expression that evaluates to a number.
#         Each point line has a radio box style check button next to it. If a line is checked,
#         then delete, move up or move down will apply to the corresponding point row.
#
# Data control buttons and menus...
#     Inch/mm menu.
#         Defaults to Inch. If it is changed while there are points in place, they are converted.
#         For example, 1 inch becomes 25.4 mm when switching from inch to mm
#     Absolute/relative menu.
#         Default Absolute. When Relative is active, the first point is absolute and all
#         others are relative to that. For example, if the first point is a 1,1, and the second point is at
#         2,2, absolute mode with show 2,2 for that point, and relative with show 1,1 for that point. If
#         points are already in place, switching between the two will make the appropriate changes.
#         !!! consider having a relative mode where each point is relative to the previous point !!!
#     Add Point
#         Adds a blank point line at the end of the list
#     ^ (move up)
#         Moves selected point line up, and the line above it down (swap lines). Selection stays
#         with the moved line.
#     v (move down)
#         Move the selected point down, and the line below it up   (swap lines). Selection stays
#         with the moved line.
#     Delete Point
#         Deletes the selected point line
#
# Window layout...
#         File
#            ----------
#            New
#            Open
#            Save
#            Save as...
#            Write GCode
#            Exit
#
#           Depth     Plunge Rate
#         __________  ___________     [Unit: Inches -]
#             X            Y          [Mode: Absolute -]
#         __________  ___________ [ ] [Add Point]
#         __________  ___________ [ ] [    ^    ]
#         __________  ___________ [ ] [    v    ]
#         __________  ___________ [ ] [Delete Point]
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
# File formats...
#     config file
#         line 1: default path
#         line 2: last file name as name.ext
#
#     data file
#         line 1: coordinate mode abs, rel, relpt1
#             abs means absolute values relative to the origin
#             rel means each point is relative to the previous point
#             relpt1 means the first point is absolute and all others are relative to it.
#         line 2: units mm, inch
#             This just sets the units in the gcode
#         line 3: plunge rate inches per minute or mm per minute, depending on units
#         line 4: hole depth in selected units
#         line 5 to end: coordinate pairs X Y. Floating point in selected units.
#
#      gcode file (ext = .nc)
#         TBD
#
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
# row is selected. -1 means none. The check button widget for each point lives in the point data
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
#
# ----2021-12-26 10 PM
# Moved Add Point and Delete Point to the button frame and removed the Edit dropdown menu.
# Revamped the way I specified fonts by using the font class with decent names. Made all label,
# button, and selection menus use the same font, called helv12bold in the code. Implemented up
# and down keys, adding methods to the Pointslist class to do the real work. Modified select_row
# to force selection of the checkbutton instead of depending on the user click for it. This is
# needed for moving the selection with the points being moved by the up/down keys.  Modifed
# # append_point method to select the new point.
# This completes the basic gui and it is time to move on to functionality, which will probably drive
# some gui tweaks.
#
# Stuff to do:
#     File/Save: write the current points list to a file. Having a default directory and recording
#     the current path will have to happen, probably saving in a file for continuity between
#     program sessions.
#
#     File/Save-as: same as save, but prompt for a new file and update current path
#
#     Open: Pick a file in the current path, maybe defaulting to the last file opened.
#
#     New: Clear the gui and the current file so the user can start a new project.
#
# Starting with a config file in the program directory. Check to see if there is one, and if
# there is none, create it. Defined first cut file formats for config and data files, in initial
# comment block above
#
# ----2021/12/29 12:13 AM
#
# Added code for reading/creating the config file. Started on code for SaveAs, which uses the config
# file. The initial path stuff is not working right. Probably something about the backslashes having
# to be doubled. Need to figure that out. Brute force would be to turn them all into forward slashes
# which Python should deal with fine.
#
# ----2022/1/4 11 PM
#
# Finished save, save as and open functions, starting with just writing stuff into a simple file with
# two numbers on each line, but changed to XML format, which cleaned up a lot of stuff, and was not
# that hard with the Python XML stuff available. Saving and restoring null tags was a problem, so I
# convert those to a single space on save, which saves a lot of trouble. Also did things like trying
# to read non-xml formatted files and writing to files without write permission. Made a lot of use of
# try-except to catch these. Things to work out: relative mode if we want it. converting between inch
# and mm on the fly? Defaults for depth and plunge rates? Come up with a name for the application?
# Generate Gcode. I'll run across other stuff, I'm sure.


import numexpr as ne  # for allowing numeric expressions in coordinate fields
import tkinter as tk
import tkinter.tix as tix
from tkinter import ttk  # more widgets
from tkinter import filedialog
from tkinter import messagebox as mb
from tkinter import font
import os
import os.path
import xml.etree.ElementTree as Et
import xml

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
config_path = os.getcwd() + "/config"  # getcwd returns the current program working directory

# set default file names. These will go into the configuration file
DEFAULTDATAFILENAME = "generate_spot_drill_data_file"
DEFAULTGCODEFILENAME = "gcode.nc"

# configuration information that reflects state that is saved between sessions. This information
# is stored in a file and updated. This dictionary is used code in this program to access this data.
config = {'default_data_path': '', 'default_data_file': '', 'default_gcode_path': '', 'default_gcode_file': ''}

# code for finding and exploring fonts.
# fonts = sorted(list(font.families()))
# print(fonts)


# the PointsList class is the main working data structure for this program.
class PointsList:
    #
    # The list of points in the application and methods for creating, deleting, etc.
    #
    points = []
    point_count = 0
    row_selected = NONESELECTED  # NONESELECTED is none selected.

    #
    # Constructor initializes the points list to empty and the points count to zero
    #
    def __init__(self):
        self.points = []
        self.point_count = 0
        self.row_selected = NONESELECTED

    #
    # Clear the object back to its initial state. Effectively remove all points
    #
    def clear(self):
        self.clear_points_from_grid()
        self.points = []
        self.point_count = 0

    #
    # append_point adds a point at the end of the list and adds a row to the gui point display.
    # The GUI includes a selection check button on each line. That is added to each list element.
    #
    def append_point(self, x, y):
        self.point_count += 1
        index = self.point_count - 1  # The first point is point zero.
        #
        # Create the entry widgets for this point
        #
        xentry = tk.Entry(window)
        xentry.delete(0, tk.END)
        xentry.insert(0, x)
        yentry = tk.Entry(window)
        yentry.delete(0, tk.END)
        yentry.insert(0, y)
        #
        # create a booleanvariable to carry the information in the checkbutton used for selection.
        checkvar = tk.BooleanVar()
        # create the check button for this point. Its state change callback passes the index
        # of this point, which will be used in the selection code.
        # This is implemented as an inline (lambda) function that calls the callback
        # with the argument.
        check_button = tk.Checkbutton(window, variable=checkvar, command=lambda: check_select_change(index, checkvar))
        #
        # append these elements of the new point as a list to the end of the points list
        self.points.append([index,
                            xentry,
                            yentry,
                            check_button,
                            checkvar])
        #
        # place the entry widgets and check button on the grid. POINTROWOFFSET is the number of the
        # grid row where we want the first point displayed. We are placing this point at the end
        # of the existing set of rows.
        self.points[index][XWIDGET].grid(row=self.point_count + POINTROWOFFSET, column=XCOLUMN, padx=4, pady=0)
        self.points[index][YWIDGET].grid(row=self.point_count + POINTROWOFFSET, column=YCOLUMN, padx=4, pady=0)
        self.points[index][CHECKBUTTON].grid(row=self.point_count + POINTROWOFFSET, column=SELECTBOXCOLUMN, sticky=tk.W)
        #
        # set up event callback for entry widget loss of focus. This is so we can check whether the text
        # in the widget is a valid number
        self.points[index][XWIDGET].bind('<FocusOut>', check_if_num)
        self.points[index][YWIDGET].bind('<FocusOut>', check_if_num)
        #
        # Select the new line so we can move it right away if desired
        self.select_row(index)

    # select_row mainly sets member variable row_selected to the specified row number. But it also
    # unchecks the rest of the check buttons and checks the current one. This could be done by just
    # forcing the existing check button to be unchecked, but to make sure we don't miss one, we just
    # uncheck all buttons except the target one.
    def select_row(self, row):
        #
        # deselect all points except the one in the target row.
        #
        print("row being selected" + str(row))
        print("old row selected " + str(self.row_selected))
        self.row_selected = NONESELECTED  # preset for the case that no row is selected
        for pt in self.points:
            if self.points.index(pt) == row:
                pt[CHECKBUTTON].select()
            else:
                pt[CHECKBUTTON].deselect()
        self.row_selected = row

    def deselect_row(self, row):
        #
        # The user has unchecked a checkbox. This should result in no boxes checked,
        # so we just set row_selected to NONESELECTED
        self.row_selected = NONESELECTED

    def delete_point(self, ptnum):
        #
        # Check if any points are selected. If not, then return without doing anything.
        if self.row_selected == NONESELECTED:
            return
        #
        # Clear the points display from the gui. We will add them back after the point
        # is deleted and the other points are adjusted to fill the gap.
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
                self.points[idx][CHECKBUTTON] = self.points[idx - 1][CHECKBUTTON]
                self.points[idx][POINTNUMBER] = idx - 1
                pt[CHECKBUTTON].deselect()
        #
        # Now, with the target point gone, and the other points adjusted, we re-display the remaining points.
        self.place_points_on_grid()

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
            self.points[placeindex][XWIDGET].grid(row=placeindex + POINTROWOFFSET,
                                                  column=XCOLUMN,
                                                  padx=4,
                                                  pady=0)
            self.points[placeindex][YWIDGET].grid(row=placeindex + POINTROWOFFSET,
                                                  column=YCOLUMN,
                                                  padx=4,
                                                  pady=0)
            self.points[placeindex][CHECKBUTTON].grid(row=placeindex + POINTROWOFFSET,
                                                      column=SELECTBOXCOLUMN,
                                                      sticky=tk.W)
        self.row_selected = NONESELECTED

    def move_point_forward(self, ptnum):
        #
        # Move the target point x and y entry widgets forward in the points list by swapping with the next
        # point in the list, then select the destination line. This makes it possible to repeatedly move these
        # values down the list. If this point is already the last one in the list, do nothing
        #
        if ptnum == self.point_count-1:
            return
        # remove the point lines from the grid
        self.clear_points_from_grid()
        # take a snapshot of the x and y widgets on this point
        xtemp = self.points[ptnum][XWIDGET]
        ytemp = self.points[ptnum][YWIDGET]
        # copy the x and y widgets of the next point
        self.points[ptnum][XWIDGET] = self.points[ptnum+1][XWIDGET]
        self.points[ptnum][YWIDGET] = self.points[ptnum+1][YWIDGET]
        # replace the x and y widgets of the next point by the snapshots
        self.points[ptnum+1][XWIDGET] = xtemp
        self.points[ptnum+1][YWIDGET] = ytemp
        # re-display the point lines
        self.place_points_on_grid()
        # move the selection to the new position of the moved point
        self.select_row(ptnum+1)

    def move_point_backward(self, ptnum):
        #
        # Move the target point x and y entry widgets backward in the points list by swapping with the previous
        # point in the list, then select the destination line. This makes it possible to repeatedly move these
        # values up the list. If this point is already the first one in the list, do nothing
        if ptnum == 0:
            return
        # remove the point lines from the grid
        self.clear_points_from_grid()
        # take a snapshot of the x and y widgets on this point
        xtemp = self.points[ptnum][XWIDGET]
        ytemp = self.points[ptnum][YWIDGET]
        # copy the x and y widgets of the previous point
        self.points[ptnum][XWIDGET] = self.points[ptnum-1][XWIDGET]
        self.points[ptnum][YWIDGET] = self.points[ptnum-1][YWIDGET]
        # replace the x and y widgets of the previous point by the snapshots
        self.points[ptnum-1][XWIDGET] = xtemp
        self.points[ptnum-1][YWIDGET] = ytemp
        # re-display the point lines
        self.place_points_on_grid()
        # move the selection to the new position of the moved point
        self.select_row(ptnum-1)
# end of PointList class


# utility functions
#
# Check that the text in an input widget is an expression that evaluates to a number. If not, turn the widget
# background red and raise a message box.
#
# noinspection PyUnboundLocalVariable
def check_if_num(event):
    widget = event.widget
    #
    # attempt to evaluate the string as a python language numeric expression. If it fails, it
    # will throw one of a number of exceptions, which we catch and inform the user, setting
    # the widget background color to red.
    #
    # Note: the ne.evaluate function compiles the argument as a Python language expression,
    # and can encounter a number of errors during compilation or execution of that code. It executes
    # the expression as written, so it will execute, for example, 1000**100 differently from 1000.**100,
    # where the integer expression will overflow, and the floating point one will not. Practically,
    # though, the expressions used in this application will be simple ones that don't generate such
    # huge numbers.
    #
    try:
        widget_value = str(widget.get()).strip()
        exprval = ne.evaluate(widget_value)
        exprval = float(exprval)
        print(exprval)
        widget.config(bg="WHITE")
    except KeyError:
        widget.config(bg="RED")
        mb.showerror("error", widget_value + " does not evaluate to a number")
    except SyntaxError:
        widget.config(bg="RED")
        mb.showerror("error", widget_value + " does not evaluate to a number")
    except ZeroDivisionError:
        widget.config(bg="RED")
        mb.showerror("error", widget_value + " has a divide by zero error")
    except OverflowError:
        widget.config(bg="RED")
        mb.showerror("error", widget_value + " overflows")
    except TypeError:
        widget.config(bg="RED")
        mb.showerror("error", widget_value + " is an invalid expression")

# Gui callbacks (command functions)


def check_select_change(line, val):
    print("check select changed...index: " + str(line))
    print("checkbutton state: " + str(val.get()))
    if val.get():
        plist.select_row(line)
    else:
        plist.deselect_row(line)


def open_pressed():
    # Open means read a coordinates file and make the points in that file the current points in 
    # the application. That file also has values for depth and plunge rate.
    if not mb.askyesno("Are you sure?", "Current data will be deleted."):
        return
    else:
        open_file = filedialog.askopenfilename(title='Open File', initialdir=config['default_data_path'])
        # update window title
        window.title('Spot Drilling Tool: ' + open_file)
        # update the configuration dictionary with the returned path and file name
        path_file = os.path.split(open_file)
        config['default_data_path'] = path_file[0]
        config['default_data_file'] = path_file[1]
        update_config_file()
        # open the coordinates file. This is just a pair of expressions on each line, x, then y, separated by a comma
        # For parsing, we just use the split(',') string method. Not much error checking here. If the file does
        # not have the right number of tokens in each line, things will break. The assumption is that the program
        # only reads files it creates, and that these are right. More stuff can be added, but we just bail if
        # there is a problem.

        # The data file is in XML format. We read and parse it with the Python XML parser, then
        # do "find" operations on the resulting data tree to get the data fields.
        # Open and parse the file, catching any xml parse error.
        try:

            xmltree = Et.parse(open_file)

        except xml.etree.ElementTree.ParseError:
            mb.showerror("Data file XML Syntax Error", "Data File XML Syntax Error")
            return

        # Get the root of the data tree
        xmltree_root = xmltree.getroot()

        # the unit selection and mode selection menu values are at the top level of children, so we can
        # just find them in the root and set the values in the GUI.
        unitsel = xmltree_root.find('unitsel')
        inch_mm_select_var.set(unitsel.text)
        modesel = xmltree_root.find('modesel')
        abs_rel_select_var.set(modesel.text)

        # The depth and plunge values are also at the top level
        depthexpr = xmltree_root.find('depthexpr')
        depth_entry.delete(0, tk.END)
        depth_entry.insert(0, depthexpr.text)
        plungeexpr = xmltree_root.find('plungeexpr')
        plunge_entry.delete(0, tk.END)
        plunge_entry.insert(0, plungeexpr.text)

        # find the points tag, then iterate through the points and find the x and y expressions for each.
        #
        plist.clear()  # clear the existing points list
        points = xmltree_root.find('points')  # find the points tag in the XML root.
        for point in points.findall('point'):  # find each point tag in the points tag.
            # For each point, find the x and y expressions and append them to the plist.
            x = point.find('xexpr')
            y = point.find('yexpr')
            # xval = x.text
            # if not xval:
            #     xval = ' '
            # print(x.text, ',', y.text)
            # if x.text == none:

            plist.append_point(point.find('xexpr').text, point.find('yexpr').text)


def new_pressed():

    # Create an XML element tree from the data we want to save. The .text and .tail white space
    # values are for making the file easier to read. They have no impact on the actual
    # data. A .text string is added after an opening tag. Here we use it after <spotdrill> and
    # <points> to start and indent a new line. A .tail string is added after a closing tag. Here
    # we use it for starting new lines after single line tags to start and indent the next line.
    root = Et.Element("spotdrill")
    root.text = "\n  "

    unitsel = Et.SubElement(root, "unitsel")
    unitsel.text = "Unit: Inches"
    unitsel.tail = "\n  "

    modesel = Et.SubElement(root, "modesel")
    modesel.text = "Mode: Absolute"
    modesel.tail = "\n  "

    depthexpr = Et.SubElement(root, "depthexpr")
    depthexpr.text = ".1 + 1"
    depthexpr.tail = "\n  "

    plungeexpr = Et.SubElement(root,"plungeexpr")
    plungeexpr.text = "100"
    plungeexpr.tail = "\n  "

    points = Et.SubElement(root, "points")
    points.text = "\n    "  # double indent next line

    xmlpoint = Et.SubElement(points, "point")
    x = Et.SubElement(xmlpoint, "xexpr")
    x.text = "3.14"
    y = Et.SubElement(xmlpoint, "yexpr")
    y.text = ".001592"
    xmlpoint.tail = "\n    "  # double indent next line

    xmlpoint = Et.SubElement(points, "point")
    x = Et.SubElement(xmlpoint, "xexpr")
    x.text = "456"
    y = Et.SubElement(xmlpoint, "yexpr")
    y.text = "123"
    xmlpoint.tail = "\n    "  # double indent next line

    xmlpoint = Et.SubElement(points, "point")
    x = Et.SubElement(xmlpoint, "xexpr")
    x.text = "3.0"
    y = Et.SubElement(xmlpoint, "yexpr")
    y.text = ".141592"
    xmlpoint.tail = "\n  "  # single indent next line because this is the end of the last point, going back to points.

    points.tail = "\n"  # no indent because this is the end of points, going back to root

    tree = Et.ElementTree(root)

    tree.write("C:/Users/ed/Documents/CNC/testwrite_file_xml")










def save_data(file_path):

    # Create an XML element tree from the data we want to save. The .text and .tail white space
    # values are for making the file easier to read. They have no impact on the actual
    # data. A .text string is added after an opening tag. Here we use it after <spotdrill> and
    # <points> to start and indent a new line. A .tail string is added after a closing tag. Here
    # we use it for starting new lines after single line tags to start and indent the next line.
    # note we allow saving of the application state even when fields have not been filled. This
    # can result in null strings in the entry widgets, which creates null tags in the XML file,
    # and reading these into the XML tree from a file causes problems. To fix this, we just save
    # a blank instead of a null string, which is handled in expression evaluation
    root = Et.Element("spotdrill")
    root.text = "\n  "

    unitsel = Et.SubElement(root, "unitsel")
    unitsel.text = inch_mm_select_var.get()
    unitsel.tail = "\n  "

    modesel = Et.SubElement(root, "modesel")
    modesel.text = abs_rel_select_var.get()
    modesel.tail = "\n  "

    depthexpr = Et.SubElement(root, "depthexpr")
    if depth_entry.get() == '':
        depthexpr.text = ' '
    else:
        depthexpr.text = depth_entry.get()
    depthexpr.tail = "\n  "

    plungeexpr = Et.SubElement(root, "plungeexpr")
    if plunge_entry.get() == '':
        plungeexpr.text = ' '
    else:
        plungeexpr.text = plunge_entry.get()
    plungeexpr.tail = "\n  "

    points = Et.SubElement(root, "points")
    points.text = "\n    "  # double indent next line

    # Add the points to the XML tree. Note xmlpoint, x, and y just serve as temporary variables
    # that reference tree items on each time around the loop.
    for i in range(0, plist.point_count):
        point = plist.read_point(i)  # read point from point list object
        # Create the point and x and y subelements in the XML tree. Note we do not
        # save null x or y values to the xml file because it causes problems on read.
        xmlpoint = Et.SubElement(points, "point")
        x = Et.SubElement(xmlpoint, "xexpr")
        if point[XWIDGET] == '':
            x.text = ' '
        else:
            x.text = point[XWIDGET]
        y = Et.SubElement(xmlpoint, "yexpr")
        if point[YWIDGET] == '':
            y.text = ' '
        else:
            y.text = point[YWIDGET]
        if i == plist.point_count-1:
            xmlpoint.tail = "\n  "  # last point...single indent next line
        else:
            xmlpoint.tail = "\n    "  # double indent next point line

    points.tail = "\n"  # new line, but no indent because this is the end of points, going back to root

    # create and save the tree. Error handler in case we try to write an illegal file
    tree = Et.ElementTree(root)
    try:
        tree.write(file_path)

        # update the default save path
        path_file = os.path.split(file_path)
        # update window title
        window.title('Spot Drilling Tool: ' + file_path)
        # update the configuration dictionary with the returned path and file name
        path_file_list = os.path.split(file_path)
        config['default_data_path'] = path_file_list[0]
        config['default_data_file'] = path_file_list[1]
        update_config_file()
    except PermissionError:
        mb.showerror("Permission Error", "No permission to write this file")


# save button callback. Save the program data to the default data file path stored in the
# config dictionary.
#
def save_pressed():
    save_path = config['default_data_path'] + '/' + config['default_data_file']
    print(save_path)
    save_data(save_path)


#
# save as button callback. Prompt user for a file to which to save, save the program data
# there, and update the default path and file in the config dictionary and the config file.
# Also, update the title of the window to reflect this change.
#
def save_as_pressed():
    save_file = filedialog.asksaveasfilename(
        title='Save As...', initialdir=config['default_data_path'], initialfile=config['default_data_file'])
    save_data(save_file)



#
# when Add Point is pressed, we add a point at the end of the points list by calling
#
def addpoint_pressed():
    print("Add Point button")
    plist.append_point('', '')


def deletepoint_pressed():
    print("Delete Point button, row_selected = " + str(plist.row_selected))
    plist.delete_point(plist.row_selected)
    for delpoint in plist.points:
        print(delpoint)


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
    plist.move_point_backward(plist.row_selected)


def down_button_pressed():
    print("down button pressed")
    plist.move_point_forward(plist.row_selected)


def clean_up_and_exit():
    print("cleanup and exit called")
    window.destroy()


def on_closing():
    print("on_closing called")
    if mb.askokcancel("Quit", "Do you want to quit?"):
        clean_up_and_exit()


#
# configuration stuff...
#
# The configuration data is stored in a file, config, which lives with the program
#
def init_config():
    global config
    #
    # The config file lives in the same file as the python source code, and it is
    # called config. This code checks to see if it exists. If so, it reads it into
    # a list of lines called config_file_lines. If it does not exist, a default one
    # is created, setting the starting data file path to the user's home directory
    # (in windows, %HOMEDRIVE%%HOMEPATH%) and the data file name to DEFAULTDATAFILENAME
    # and the gcode file name to DEFAULTGCODEFILENAME.
    if os.path.exists(config_path):
        # config file exists. Read it.
        config_file = open(config_path, "r")
        config_file_lines = config_file.readlines()
        config_file.close()
    else:
        # config file does not exist. Create a default one.
        user_home_path = os.path.expanduser("~").replace("\\", "/") # set path to user home
        print(user_home_path)
        config_file_lines = [user_home_path + "\n",
                             DEFAULTDATAFILENAME + "\n",
                             user_home_path + "\n",
                             DEFAULTGCODEFILENAME]  # create the config file lines
        config_file = open(config_path, "w")
        config_file.writelines(config_file_lines)
        config_file.close()
    # Put all config data into the global config dictionary
    config["default_data_path"] = config_file_lines[0].rstrip("\n")
    config["default_data_file"] = config_file_lines[1].rstrip("\n")
    config["default_gcode_path"] = config_file_lines[2].rstrip("\n")
    config["default_gcode_file"] = config_file_lines[3].rstrip("\n")
    print(config)


def update_config_file():
    # config file is assumed to exist because init_config() was called before.
    # update the config file with new default save path and file.
    #     config_file = open(
    user_home_path = os.path.expanduser("~").replace("\\", "/")  # set path to user home
    config_file_lines = [config["default_data_path"] + "\n",
                         config["default_data_file"] + "\n",
                         config["default_gcode_path"] + "\n",
                         config["default_gcode_path"]]
    config_file = open(config_path, "w")
    config_file.writelines(config_file_lines)
    config_file.close()
# end def update_config_file

# Start up code


# create global working points list object
plist = PointsList()

#
init_config()
# default_save_path = config_list[0]
# default_save_file = config_list[1]
print(config)
# gcodeFile = open(gcodeFileName, "w")

# set up the GUI
window = tix.Tk()
s = ttk.Style()
s.theme_use('xpnative')
s.configure('window.TFrame', font=('Helvetica', 30))
#
# create and size the main window
#
window.title('Spot Drilling Tool')
# Test code for PointList class and initial points for testing.
# print('initial point list')
# for point in plist.points:
#     print(point)
# print('appending point')
# plist.append_point('', 2.0)
# for point in plist.points:
#     print(point)
# print('appending point')
# plist.append_point(3.0, 4.0)
# for point in plist.points:
#     print(point)
# print('appending point')
# plist.append_point(5.0, 6.0)
# for point in plist.points:
#     print(point)
# print('appending point')
# plist.append_point(7.0, 8.0)
# for point in plist.points:
#     print(point)
# end of class PointsList test code

menu_bar = tk.Menu(window)
filemenu = tk.Menu(menu_bar, tearoff=1)
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
helv12bold = tk.font.Font(family='Helvetica', size=12, weight='bold')
arrowfont = tk.font.Font(family='tt-icon-font', size=12, weight='bold')

button_frame = ttk.Frame(window)
depth_text = tk.StringVar()
depth_label = tk.Label(window, textvariable=depth_text, font=helv12bold)
depth_text.set('Depth')

plunge_text = tk.StringVar()
plunge_label = tk.Label(window, textvariable=plunge_text, font=helv12bold)
plunge_text.set('Plunge Rate')

depth_entry = tk.Entry(window)
depth_entry.bind('<FocusOut>', check_if_num)

plunge_entry = tk.Entry(window)
plunge_entry.bind('<FocusOut>', check_if_num)

# code for sampling fonts up_button = Button(window,
# text="abcdefghijklmnopqrstuvwxyz0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ", font='tt-icon-font 12',
# command=up_button_pressed)

up_tip = tix.Balloon(button_frame)
up_button = tk.Button(button_frame, text="  k  ", font=arrowfont, command=up_button_pressed)
up_tip.bind_widget(up_button, balloonmsg="Swap selected point with the one above it")

down_tip = tix.Balloon(button_frame)
down_button = tk.Button(button_frame, text="  c  ", font=arrowfont, command=down_button_pressed)
down_tip.bind_widget(down_button, balloonmsg="Swap selected point with the one below it")

addpoint_tip = tix.Balloon(button_frame)
addpoint_button = tk.Button(button_frame, text="Add Point", font=helv12bold, command=addpoint_pressed)
addpoint_tip.bind_widget(addpoint_button, balloonmsg="Add a point at the end")

delpoint_tip = tix.Balloon(button_frame)
delpoint_button = tk.Button(button_frame, text="Delete Point", font=helv12bold, command=deletepoint_pressed)
delpoint_tip.bind_widget(delpoint_button, balloonmsg="Delete selected point")

x_text = tk.StringVar()
x_label = tk.Label(window, textvariable=x_text, font=helv12bold)
x_text.set('    X    ')

y_text = tk.StringVar()
y_label = tk.Label(window, textvariable=y_text, font=helv12bold)
y_text.set('    Y    ')

inch_mm_select_var = tk.StringVar(button_frame)
inch_mm_select_var.set("Unit: Inches")
inch_mm_select_menu = tk.OptionMenu(button_frame, inch_mm_select_var, 'Unit: Inches', 'Unit: Millimeters')
inch_mm_select_menu.config(font=helv12bold)
inch_mm_select_var.trace('w', inch_mm_select_var_changed)

abs_rel_select_var = tk.StringVar(button_frame)
abs_rel_select_var.set("Mode: Absolute")
abs_rel_select_menu = tk.OptionMenu(button_frame, abs_rel_select_var, 'Mode: Absolute', 'Mode: Relative')
abs_rel_select_menu.config(font=helv12bold)
abs_rel_select_var.trace('w', abs_rel_select_var_changed)

#
# Place the widgets in the window
#
depth_label.grid(row=0, column=0, padx=4, pady=0)
plunge_label.grid(row=0, column=1, padx=4, pady=4)
depth_entry.grid(row=1, column=0, padx=4, pady=0)
plunge_entry.grid(row=1, column=1, padx=4, pady=0)
x_label.grid(row=2, column=0, padx=4, pady=0)
y_label.grid(row=2, column=1, padx=4, pady=0)
button_frame.grid(row=0, column=3, rowspan=10)
inch_mm_select_menu.grid(row=0, column=0, padx=0, pady=4, sticky=tk.W)
abs_rel_select_menu.grid(row=1, column=0, padx=0, pady=4, sticky=tk.W)
addpoint_button.grid(row=2, column=0, sticky=tk.W)
up_button.grid(row=3, column=0, sticky=tk.W)
down_button.grid(row=4, column=0, sticky=tk.W)
delpoint_button.grid(row=5, column=0, sticky=tk.W)

# set up a window menu
window.config(menu=menu_bar)

# bind window manager delete window to the on_closing function
window.protocol("WM_DELETE_WINDOW", on_closing)

# Start the GUI main look
window.mainloop()
