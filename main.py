#!/usr/bin/env python3
## @program PySpec
#  Documentation for the pyspec project
#
#  More details: Initial toy application can read a file and display a spectrum in a window, it can even
#  save the resulting figure in different formats (thanks to matplotlib).
#
#  First project represents a PySpec viewer and converter.
#  TODO Avoid concatenating files with new one (not really sure why this happens).
#  TODO Handle cancel on fileselector
#  TODO Handle file parsing problems and other error handling
#  TODO Form for spectrum properties to allow creation of PySpec format
#  TODO Parsers for different commonly found filetypes.
#  TODO Abstractions of current objects Dataset, Window, App
#  TODO Documentation of program pydoc and doxygen and Github wiki
#  TODO Save and SaveAs dialogs to write as different formats.
#
import sys
from PyQt5 import QtWidgets

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

import random

def TestComment(my_string):
    return (my_string[0]=='#')

class Dataset:
    x_values = []
    y_values = []

    def __init__(self, source=sys.stdin):
        for line in source:
            if TestComment(line):
                pass
            else:
                # Read in the data
                self.x_values.append(float(line.split()[0]))
                self.y_values.append(float(line.split()[1]))

class Window(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(Window, self).__init__(parent)

        # a figure instance to plot on
        self.figure = Figure()

        # this is the Canvas Widget that displays the `figure`
        # it takes the `figure` instance as a parameter to __init__
        self.canvas = FigureCanvas(self.figure)

        # this is the Navigation widget
        # it takes the Canvas widget and a parent
        self.toolbar = NavigationToolbar(self.canvas, self)

        # Just some button connected to `plot` method
        self.button = QtWidgets.QPushButton('New data')
        self.button.clicked.connect(self.plot)

        # set the layout
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)
        layout.addWidget(self.button)
        self.setLayout(layout)
        self.plot()

    def plot(self):
        ''' Plot a new spectrum '''
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        filename, _ = QtWidgets.QFileDialog.getOpenFileName(None, "Open Data File", "", "All files (*);;csv files (*.csv)")

        my_file = open(filename, "r+")
        data = Dataset(my_file)
        my_file.close()
        # create an axis
        ax = self.figure.add_subplot(111)
        # discards the old graph
        ax.clear()
        # plot data
        ax.plot(data.x_values, data.y_values )
        ax.set(xlabel='Wavelength (nm)', ylabel="Absorption", Title="Dataset"+str(len(data.x_values)))
        # refresh canvas
        self.canvas.draw()

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)

    main = Window()
    main.show()

    sys.exit(app.exec_())
