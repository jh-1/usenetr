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


class App(object):
  'An application. A collector for active windows'

  def __init__(self):
    self._root = tk.Tk()
    self._root.wm_title('Default window')
    self._root.withdraw()
    self._children = []
    self._nchildren = 0 # Ignoring the default (withdrawn) window

  def act(self):
    'Process the windows and widgets and their callbacks'
    for child in self._children:
      child.implement()
    self._root.mainloop()

  def child_new(self, child):
    'Add a new child'
    if child not in self._children:
      self._children.append(child)
      self._nchildren += 1
    else:
      raise KeyError, 'Child %s already present' % child

  def child_killed(self, child):
    'Delete an existing child'
    for i in range(self._nchildren):
      if self._children[i] == child:
        del self._children[i]
        self._nchildren -= 1
        if self._nchildren == 0:
          self._root.destroy()
        break
    else:
      raise KeyError, 'Child %s not present' % child

class Action(object):
  'An action that a UI element can cause'

  def __init__(self, label = '', desc = '', action = None, icon = None):
    self.label  = label
    self.desc   = desc
    self.action = action
    self.icon   = icon

class Master_window(object):
  def __init__(self, parent = None, title = ''):
    ptype = type(parent)
    if ptype != App:
      raise ValueError, \
         'Parent of a master window must be an app, not %s' % ptype
    parent.child_new(self)
    self._parent = parent
    self._title = title
    self.menus = []

  def killed(self):
    self._real.destroy()
    self._parent.child_killed(self)

  def implement(self):
    'Implement the elements of the window'
    self._real = tk.Toplevel()
    self._real.wm_title(self._title)
    self._real.protocol(name = 'WM_DELETE_WINDOW', func = self.killed)

    # Implement the menu, if present
    if self.menus:
      for m in self.menus:
        print ' menu:', m
        for v in m:
          print ' ', v

#      menubar = tk.Menu(self)


class Slave_window(object):
  def __init__(self, parent = None, title = ''):
    ptype = type(parent)
    if ptype == Master_window or ptype == Slave_window:
      self._real = tk.Toplevel()
      self._real.wm_title(title)
      parent.child_new(self)
      self._real.protocol(name = 'WM_DELETE_WINDOW', func = self.killed)

  def killed(self):
    self._real.destroy()
    self._parent.child_killed(self)


class Element(object): pass


class Menu(object):
  def __init__(self, value = []):
    self._value = value


class Button(object):
  def __init__(self, parent, text = ''):
    self._parent = parent
    self._text = text


class Text(object): pass
class Table(object): pass


if __name__ == '__main__':

  # Make a name for the module so we can use the same form as when imported
  ui = sys.modules[__name__]

  # Create a new UI application
  app = ui.App()

  # Create windows
  win0 = ui.Master_window(title = 'win0')
  win1 = ui.Master_window(title = 'win1')

  # Associate windows with the app
  app.window_add(win0)
  app.window_add(win1)

  # Set up the app's actions
  new_action   = ui.Action('New',   -1, desc = 'Create a new document')
  close_action = ui.Action('Close', -1, desc = 'Close this window')
  exit_action  = ui.Action('Exit',  -1, desc = 'Quit the application')
  cut_action   = ui.Action('Cut',   -1, desc = 'Cut to clipboard')
  copy_action  = ui.Action('Copy',  -1, desc = 'Copy to clipboard')
  paste_action = ui.Action('Paste', -1, desc = 'Paste from clipboard')

  # Create the file menu
  file_menu = ui.Menu('File', -1)
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

  # Associate the menu with the window
  win0.menu_add(window_menu)

  # Make the UI real
  win0.effect()

  # Handle user interations
  response = app.act()
  print 'App response: %r', response
