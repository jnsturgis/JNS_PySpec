#!/usr/bin/env python3
## @program PySpec
#  Documentation for the pyspec project
#
#   More details: Initial toy application can read a file and display a spectrum in a window, it can even
#   save the resulting figure in different formats (thanks to matplotlib).
#
#   First project represents a PySpec viewer and converter.
#   TODO Form for spectrum properties to allow creation of PySpec format
#   TODO Parsers for different commonly found filetypes.
#   TODO Abstractions of current objects Dataset, Window, App
#   TODO Documentation of program pydoc and doxygen and Github wiki

from PyQt5 import QtWidgets
import sys
import os

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

def TestComment(my_string):
    return (my_string[0]=='#')

class Dataset:
    '''A dataset class, datasets should know how to fill themselves from a file, write themselves, draw themselves and so on'''
    # This class should not really know much about the GUI or OS
    x_values = []
    y_values = []
    x_label = "Wavelength (nm)"
    y_label = "Absorption"
    filename = None
    filetype = None
    
    def __init__(self, source=None,  name=None,  type='xy' ):
        
        self.valInit()
        self.filename = name
        self.filetype = type
        
        if source :                                        # If there is a source then use it to read the data
                                                                # This section should really switch on the filetype
                                                                # and check the filetype declared corresponds to
                                                                # the declaration.
            lineNumber = 0
            for line in source:
                lineNumber+= 1
                if TestComment(line):               # Ignore comments that start with a '#'
                    continue
                else:
                    # Read in the data
                    words = line.split()
                    if len(words)==0:               # Ignore blank lines too
                        continue
                    elif (len(words)!=2):
                        if self.fileReadError(lineNumber, "2 numbers"):
                            break
                        else:
                            continue
                    else:       # xy pair all is well (if they are numbers)
                        try:
                            self.x_values.append(float(words[0]))
                            self.y_values.append(float(words[1]))
                        except:
                            if self.fileReadError(lineNumber, "2 numbers"):
                                break
                            else:
                                continue

    def fileReadError(self, lineNumber, expected):
        msg = QtWidgets.QMessageBox.question(None,"Error", "Error reading file!\nLine #"+str(lineNumber)+"does not contain"+expected, QtWidgets.QMessageBox.Ignore | QtWidgets.QMessageBox.Abort)
        if msg == QtWidgets.QMessageBox.Abort:
            self.valInit()
            return True
        else:
            return False

    def valInit(self):
        '''Initialize the values of the instance'''
        while len(self.x_values):               # Empty class variables I do not really see why it is necessary.
            self.x_values.pop()                     # Since I did not intend to reuse the same instance each time.
        while len(self.y_values):               # But it is probably good form to make sure we know where things
            self.y_values.pop()                     # start.
        self.x_label = "Wavelength (nm)"
        self.y_label = "Absorption"
        self.filename = None
        self.filetype = "xy"
        
    def write(self,  dest=None,  type=None):
        '''Write the datastructure to the destination using the syntax associated with the type'''
        # If type is none use saved type or if there is none xy format (for the moment).
        if dest:
            dest.write('# File written by PySpec in xy format\n')
            for i in range(len(self.x_values))  :
                dest.write(str(self.x_values[i])+'\t'+str(self.y_values[i])+'\n')
    
    def plot(self, axis): 
        # plot data
        axis.plot(self.x_values, self.y_values )
        if self.filename:
            axis.set(xlabel=self.x_label, ylabel=self.y_label, Title=self.filename)
        else:
            axis.set(xlabel=self.x_label, ylabel=self.y_label, Title="No Data")

class Window(QtWidgets.QDialog):
    '''The main window for the application'''
    data = Dataset()
    
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

        # Create some buttons connected to action methods
        # An open button `plot` method
        self.OpenButton = QtWidgets.QPushButton('New data')
        self.OpenButton.clicked.connect(self.open)
        self.SaveButton = QtWidgets.QPushButton('Save')
        self.SaveButton.clicked.connect(self.save)
        self.SaveAsButton = QtWidgets.QPushButton('Save As')
        self.SaveAsButton.clicked.connect(self.saveAs)
        self.EditButton = QtWidgets.QPushButton('Edit')
        self.EditButton.clicked.connect(self.edit)
        # Put the buttons in a box
        self.buttonLayout = QtWidgets.QHBoxLayout()
        self.buttonLayout.addWidget(self.OpenButton)
        self.buttonLayout.addWidget(self.SaveButton)
        self.buttonLayout.addWidget(self.SaveAsButton)
        self.buttonLayout.addWidget(self.EditButton)
        self.buttonBox = QtWidgets.QGroupBox()
        self.buttonBox.setLayout(self.buttonLayout)
        
        # set the layout
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)
        layout.addWidget(self.buttonBox)
        self.setLayout(layout)
        self.open()

    def open(self):
        # Ask for a name and read in a new file
        ''' Plot a new spectrum '''
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        filename, filetype = QtWidgets.QFileDialog.getOpenFileName(None, "Open Data File", "", "All files (*);;csv files (*.csv)")
        if filename :
            my_file = open(filename, "r+")
            self.data = Dataset(my_file,  os.path.basename(filename),  os.path.splitext(os.path.basename(filename))[1])
            my_file.close()
        self.plot()
    
    def plot(self):
        ''' Plot the current spectrum in the window'''
        
        ax = self.figure.add_subplot(111)       # create an axis
        ax.clear()                  # discards the old graph
        self.data.plot(ax)
        self.canvas.draw()

    def save(self):
        if self.data.filename:
            my_file = open(self.data.filename, "w")
            self.data.write(my_file)
            my_file.close()
        else:
            self.saveAs()

    def saveAs(self):
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        filename, _ = QtWidgets.QFileDialog.getSaveFileName(None,"Save File As","","All Files (*);;xy Files (*.xy)", options=options)
        
        if filename:
            filetype = os.path.splitext(os.path.basename(filename))[1]
            # Check have info to save validly as chosen type.
            my_file = open(filename, "w")
            self.data.write(my_file, filetype)
            my_file.close()
            self.data.filename = os.path.basename(filename)
            self.data.filetype = filetype
            self.plot()
    
    def edit(self):
        print ("  Filename :" + self.data.filename)
        print ("  Filetype :" + self.data.filetype)
        print ("Datapoints :" + str(len(self.data.x_values)))
        print ("   X label :" + self.data.x_label)
        print ("   Y label :" + self.data.y_label)
        #if OK pressed copy to data and replot
        self.plot()
    
if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)

    main = Window()
    main.show()

    sys.exit(app.exec_())
