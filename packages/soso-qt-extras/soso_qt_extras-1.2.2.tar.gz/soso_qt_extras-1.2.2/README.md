# qt_extras

Provides various extras for PyQt, including menu_button, list_button,
list_layouts, autofit, SigBlock, ShutUpQT, WidgetDisabler and DevilBox


## Classes:

### SigBlock:

A context manager which blocks widgets from generating signals.

### ShutUpQT(object):

A context manager for temporarily supressing DEBUG level messages.
Primarily used when loading a Qt graphical user interface using uic.

### WidgetDisabler:

A context manager that disables every widget in a window.

### DevilBox(QMessageBox):

Quick and dirty error message dialog.


## Sub-modules:

### menu_button:

Pushbutton with an integrated pop-aside menu.

### list_button:

Pushbutton with an integrated drop-down list containing text and data.

### list_layouts:

"Collection" layouts which act like lists.

### autofit

Abbreviates widget text to fit inside a widget.

### info:

A command-line tool which accepts a PyQT class name and provides a list of all
class members or an import statement.


