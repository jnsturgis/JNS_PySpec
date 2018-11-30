#!/usr/bin/env python3
## @program PySpec
#  Documentation for the PySpec project
#
#   More details: Initial toy application can read a file and display a spectrum in a window, it can even
#   save the resulting figure in different formats (thanks to matplotlib).
#
#   Version 0.0 First project represents a PySpec Spectrum viewer
#
#   GUI based on PyQt5
#   Plotting based on matplotlib
#
from PyQt5 import QtWidgets
import sys
import os
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

#
#   A Dataset class that holds and manipulates data.
#   This class provides the following methods and values:
#       TODO npoints: the number of points in the datasets
#       x_values[]: a list of values for the independant variable TODO of length npoints
#       y_values[]: a list of values for the dependant variable TODO of length npoints
#       x_label: a string describing the independant variable TODO from a list?
#       y_label: a string describing the dependant variable TODO from a list?
#       filename: name of the file (without path or TODO extension)
#       filetype: name for the filetype, TODO and the filename extension
#	Dataset(source=None,  name=None,  type='xy' ): Read a new dataset from source, with name and type.
#       ... the rest I need to work on a bit with a view to scripting
class Dataset:
    '''A dataset class, datasets should know how to fill themselves from a file, 
       write themselves, draw themselves and so on'''
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
                if self.TestComment(line):               # Ignore comments that start with a '#'
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

    def TestComment(self, my_string):
        return (my_string[0]=='#')

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

#
#   The user interface parts start here...
#
#   This class collection and file provides the following top level methods and values:
#       batchMode: The program is running in batch mode i.e. not from the main program interface.
#       withGUI:   The program has initiated the GUI allowing the use of internal dialogs even 
#                  when running in batchMode.
#       SpecDialog(): The dialog for manually editing the passed dataset.
#       Window():  The main program window.
#
#   SpecDialog class to handle the edit metadata/data dialog
#
class SpecDialog(QtWidgets.QDialog):  
    '''The dialog for displaying and editing spectrum data'''
    def __init__(self, data):
        super(SpecDialog,  self).__init__()                         # What does this do?
        
        #
        # Would be good if the edit dialog also had a tab for the data spreadsheet.
        # Beyond the metadata information in the first tab...
        #
        
        self.data = []
        self.le1 = QtWidgets.QLineEdit(data.filename)
        self.le2 = QtWidgets.QLineEdit(data.filetype)
        self.le3 = QtWidgets.QLineEdit(data.x_label)
        self.le4 = QtWidgets.QLineEdit(data.y_label)
        
        self.formGroupBox = QtWidgets.QGroupBox("Dataset Info")
        layout = QtWidgets.QFormLayout()
        layout.addRow(QtWidgets.QLabel("Filename:"), self.le1)
        layout.addRow(QtWidgets.QLabel("Filetype:"), self.le2)
        layout.addRow(QtWidgets.QLabel("X label:"), self.le3)
        layout.addRow(QtWidgets.QLabel("Y label:"), self.le4)
        layout.addRow(QtWidgets.QLabel("Datapoints:"), QtWidgets.QLabel(str(len(data.x_values))))
        self.formGroupBox.setLayout(layout)
        
        buttonBox = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        buttonBox.accepted.connect(self.resultOK)
        buttonBox.rejected.connect(self.resultCancel)
        
        mainLayout = QtWidgets.QVBoxLayout()
        mainLayout.addWidget(self.formGroupBox)
        mainLayout.addWidget(buttonBox)
        
        self.setLayout(mainLayout)
        self.setWindowTitle("PySpec: Edit info")
        self.open() 

    def resultOK(self):
        self.data.append(self.le1.text())
        self.data.append(self.le2.text())
        self.data.append(self.le3.text())
        self.data.append(self.le4.text())
        self.accept()
        
    def resultCancel(self):
        self.reject()

#
#   Window class to handle the main application window and associated methods.
# 
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
        self.ExitButton = QtWidgets.QPushButton('Done')
        self.ExitButton.clicked.connect(self.exit)
        
        # Put the buttons in a box
        self.buttonLayout = QtWidgets.QHBoxLayout()
        self.buttonLayout.addWidget(self.OpenButton)
        self.buttonLayout.addWidget(self.SaveButton)
        self.buttonLayout.addWidget(self.SaveAsButton)
        self.buttonLayout.addWidget(self.EditButton)
        self.buttonLayout.addWidget(self.ExitButton)
        self.buttonBox = QtWidgets.QGroupBox()
        self.buttonBox.setLayout(self.buttonLayout)
        
        # set the layout
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)
        layout.addWidget(self.buttonBox)
        self.setLayout(layout)
        self.open()

    def exit(self):
        self.accept()

    def open(self):
        # Ask for a name and read in a new file
        ''' Plot a new spectrum '''
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        filename, filetype = QtWidgets.QFileDialog.getOpenFileName(None, "Open Data File", "", "All files (*);;csv files (*.csv)")
        if filename :
            my_file = open(filename, "r+")
            names = os.path.splitext(os.path.basename(filename))
            self.data = Dataset(my_file,  names[0],  names[1][1:])
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
            fullname = self.data.filename + '.' + self.data.filetype
            my_file = open(fullname, "w")
            self.data.write(my_file)
            my_file.close()
        else:
            self.saveAs()

    def saveAs(self):
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        filename, _ = QtWidgets.QFileDialog.getSaveFileName(None,"Save File As","","All Files (*);;xy Files (*.xy)", options=options)
        
        if filename:
            # Check have info to save validly as chosen type.
            my_file = open(filename, "w")
            names = os.path.splitext(os.path.basename(filename))
            filetype = names[1][1:]
            self.data.write(my_file, filetype)
            my_file.close()
            self.data.filename = names[0]
            self.data.filetype = filetype
            self.plot()
    
    def edit(self):
        dialog = SpecDialog(self.data)
        dialog.exec_()
        if dialog.result():  # OK button was clicked so recover the data...
            self.data.filename = dialog.data[0]
            self.data.filetype = dialog.data[1]
            self.data.x_label = dialog.data[2]
            self.data.y_label = dialog.data[3]
            self.plot()         # Redraw ideally only on OK button (true)

def initGUI(argv):
    withGUI = True
    return QtWidgets.QApplication(argv)
#
#   The main part that is executed on load depending on if the file is called as a
#   program (__name__ == '__main__') or not.
# 
if __name__ == '__main__':
    app = initGUI(sys.argv)

    main = Window()
    main.show()

    sys.exit(app.exec_())
else:
    batchMode = True
    withGUI = False

