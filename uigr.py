'''UIGR - User Interface General Recommendation

This module provides the components of a general user interface in a
way that can be rendered at different resolutions and both as
a GUI and a TUI.
'''

# The basic structure is
#
#   An application can have multiple windows
#   A window's parent is an application or another window
#   Within a window there are various UI elements
#
# Hints can be given to the layout engines
#
# Specific types of UI element
#   Menu = a tree of records
#   Button = a labelled boolean
#   Text = an optionally scrollable ro or rw string with parameters
#   Table = a potentially scrollable sequence of rows
#
# Attributes
#   Choice = choose N (e.g. 1) from several
#   Skip A and put focus on B
#
# Hints
#   Keep together
#   Sizes: min, target, max
#   Box one or more items
#
# Events
#

import sys

# Explicit choice of import, although rest of code is not portable
if sys.version_info.major < 3:
  import Tkinter as tk
  import ttk
else:
  import tkinter as tk
  from tkinter import ttk


#******************************************************************************
#
# App class
#
#******************************************************************************

class App(object):
  'An application. A collector for active windows'

  def __init__(self):
    self._root = None
    self._windows = []

  def window_add(self, window):
    if window not in self._windows:
      self._windows.append(window)
    else:
      raise ValueError, 'App already has window %s' % window

  def window_remove(self, window):
    try:
      self._windows.remove(window)
    except ValueError:
      raise ValueError, 'App does not have window %s' % window
    if len(self._windows) == 0:
      self._root.destroy()

  def implement(self):
    'Implement this app in the chosen UI toolkit'
    self._root = tk.Tk()
    self._root.wm_title('Default window')
    self._root.withdraw()  # Don't use the default window
    for window in self._windows:
      window.implement(self)

  def interact(self):
    'Process the windows and widgets and their callbacks'
    if not self._root:
      self.implement()
    self._root.mainloop()
    # App has closed. Nothing to pass back to caller


#******************************************************************************
#
# Window class
#
#******************************************************************************

class Window(object):
  def __init__(self, title = ''):
    self._title = title
    self._menus = []
    self._impl = None  # Implementation
    self._parent = None

  def destroy(self):
    if self._impl:
      self._impl.destroy()
    if self._parent:
      self._parent.window_remove(self)

  def menu_add(self, menu):
    self._menus.append(menu)

  def implement(self, parent):
    'Implement the elements of the window'
    self._parent = parent
    self._impl = tk.Toplevel()
    self._impl.wm_title(self._title)
    self._impl.protocol(name = 'WM_DELETE_WINDOW', func = self.destroy)

    if len(self._menus) > 1:
      raise ValueError, 'Have %s menus instead or 0 or 1.' % len(self._menus)

    if len(self._menus) == 1:
#      print ' _menus[0] =', self._menus[0]
      menubar = self._menus[0].make()  # Just the first menu
      self._impl.config(menu = menubar)


#******************************************************************************
#
# Action class
#
#******************************************************************************

class Action(object):
  'An action that a UI element can cause'

  def __init__(self, label, selector_offset,
       desc = '', action = None, parms = None, icon = None):
    self.label  = label
    self.seloff = selector_offset
    self.desc   = desc
    self.action = action
    self.parms  = parms
    self.icon   = icon


#******************************************************************************
#
# Menu class
#
#******************************************************************************

class Menu(object):
  def __init__(self, label, selector_offset, desc=''):
    self.label    = label
    self._seloff   = selector_offset
    self.desc = desc
    self._entries  = []

  def action_add(self, action):
    self._entries.append(('a', action))

  def menu_add(self, menu):
    self._entries.append(('m', menu))

  def make(self):
    print ' menumake', self.label, '##', self._entries
    menu = tk.Menu(tearoff=False)
    for entry in self._entries:
      if len(entry) != 2:
        raise ValueError, \
           'Internal error: entry %r has to be two elements' % entry
      etype, submenu = entry
      if etype == 'm':  # Another menu
        menu.add_cascade(label=submenu.label, menu=submenu.make())
      elif etype == 'a':  # Action
        menu.add_command(label=submenu.label, command=submenu.action)
      else:
        raise ValueError, \
           'Internal error: entry type %r not recognised' % etype
    return menu

#    dummy = tk.Menu()
#    filemenu = tk.Menu(tearoff=False)
#    filemenu.add_command(label = 'No menu')
#    dummy.add_cascade(label='File', menu=filemenu)
#    return dummy


#******************************************************************************
#
# Main routine
#
#******************************************************************************

if __name__ == '__main__':

  # Make a name for the module so we can use the same form as when imported
  ui = sys.modules[__name__]

  # Set up the app's actions
  new_action   = ui.Action('New',   -1, desc = 'Create a new document')
  close_action = ui.Action('Close', -1, desc = 'Close this window')
  exit_action  = ui.Action('Exit',  -1, desc = 'Quit the application',
      action=quit)
  cut_action   = ui.Action('Cut',   -1, desc = 'Cut to clipboard')
  copy_action  = ui.Action('Copy',  -1, desc = 'Copy to clipboard')
  paste_action = ui.Action('Paste', -1, desc = 'Paste from clipboard')

  # Create the file menu
  file_menu = ui.Menu('File', -1, desc='File and application controls')
  file_menu.action_add(new_action)
  file_menu.action_add(exit_action)

  # Create the edit menu
  edit_menu = ui.Menu('Edit', -1)
  edit_menu.action_add(cut_action)
  edit_menu.action_add(copy_action)
  edit_menu.action_add(paste_action)

  # Create the window menu
  window_menu = ui.Menu('', -1)
  window_menu.menu_add(file_menu)
  window_menu.menu_add(edit_menu)

  # Add the content to a new window
  win0 = ui.Window(title = 'win0')
  win0.menu_add(window_menu)

  # Add the window to a new app
  app = ui.App()
  app.window_add(win0)

  # Make the UI real
  app.implement()

  # Pass control to the windowing system
  response = app.interact()
