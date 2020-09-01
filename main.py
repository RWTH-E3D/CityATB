# -*- coding: utf-8 -*-
"""
The CityGML Analysis Toolbox (CGML ATB) was developed by members of the  "Institute of Energy Efficiency and Sustainable Building (e3D), RWTH Aachen University" using Python 3.5+.
This tool can be used for the analysis of CityGML datasets and searching of building(s) and city quarters using user defined coordinates and attributes. 
The CityATB also allows the users to validate datasets according to the predefined and also the user defined CityGML XML Schema Definiton (XSD) schema(s). 
The results of different functions of the CityATB can also be stored into TXTs, CSVs, XMLs and JSONs. This Toolbox is available under the MIT License.


Contact:
M.Sc. Avichal Malhotra: malhotra@e3d.rwth-aachen.de
Simon Raming           


www.e3d.rwth-aachen.de
Mathieustr. 30
52074 Aachen
"""

# import of libaries
import os
import sys
import PySide2
from PySide2 import QtWidgets, QtGui
import time

# import of functions
import gui_functions as gf
import analysis_functions as af
import search_functions as sf
import validation_functions as vf
import save_functions as save_f


dirname = os.path.dirname(PySide2.__file__)
plugin_path = os.path.join(dirname, 'plugins', 'platforms')
os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = plugin_path


# generall variables
gmlpath = ''                                # path of file
dirpath = ''                                # path of directory

# variables for analysis
data = []                                   # data from analysis

# variables for search
inputCoor = []                              # coordinates in entered CRS
outputCoor = []                             # coordinates in transformed CRS
scaledCoor = []                             # coordinates scaled by user
analyseSearch = False                       # flag for analysing search_data
search_info = []                            # [path, value, [iCRS, [iCoor]], [oCRS, [oCoor], [min(), max()]], search_data]
CRS = ['', '']


# variables for validation
xsd_help = [[],[],[]]
validata = []                               # data from validation
validationFilenames = []                    # files, that have been validated
analyseValidation = False                   # flag for analysing validationFilenames

# positions and dimensions of window
posx = 275
posy = 100
width = 800
height = 800
sizefactor = 0
sizer = True

pypath = os.path.dirname(os.path.realpath(__file__))        # path of script


class mainWindow(QtWidgets.QWidget):
    def __init__(self):
        #initiate the parent
        super(mainWindow,self).__init__()
        self.initUI()

    def initUI(self):
        global posx, posy, width, height, sizefactor, sizer

        # setup of gui / layout
        if sizer:
            posx, posy, width, height, sizefactor = gf.screenSizer(self, posx, posy, width, height, app)
            sizer = False
        gf.windowSetup(self, posx, posy, width, height, pypath, 'CityATB - CityGML Analysis Toolbox')

        self.vbox = QtWidgets.QVBoxLayout(self)
        self.setLayout(self.vbox)

        gf.load_banner(self, os.path.join(pypath, r'pictures\e3dHeader.png'), sizefactor)

        self.uGrid = QtWidgets.QGridLayout()

        # setup of buttons
        button_height = 0.2

        self.btn_search_building = QtWidgets.QPushButton('Search buildings')
        self.uGrid.addWidget(self.btn_search_building, 0, 0, 1, 2)

        self.lbl_search = QtWidgets.QLabel("     Search for values by coordinates or for\n     value(s)(sep = '&')\n")
        self.uGrid.addWidget(self.lbl_search, 2, 0, 1, 2)

        self.btn_convert = QtWidgets.QPushButton('Convert files')
        self.uGrid.addWidget(self.btn_convert, 0, 2, 1, 2)
        self.btn_convert.setEnabled(False)

        self.lbl_convert = QtWidgets.QLabel('      Change the version of CityGML files\n\n')
        self.uGrid.addWidget(self.lbl_convert, 2, 2, 1, 2)

        self.btn_analysis = QtWidgets.QPushButton('Analyse files')
        self.uGrid.addWidget(self.btn_analysis, 4, 0, 1, 2)

        self.lbl_analysis = QtWidgets.QLabel('      Analyse files or folders on version, LoD,\n     #ofB, # ofBP...\n')
        self.uGrid.addWidget(self.lbl_analysis, 6, 0, 1, 2)

        self.btn_validation = QtWidgets.QPushButton('Validate files')
        self.uGrid.addWidget(self.btn_validation, 4, 2, 1, 2)

        self.lbl_validation = QtWidgets.QLabel('      Validate .gml (and .xml) files according\n      to .xsd schemas\n')
        self.uGrid.addWidget(self.lbl_validation, 6, 2, 1, 2)

        self.btn_about = QtWidgets.QPushButton('About the toolbox')
        self.uGrid.addWidget(self.btn_about, 8, 0, 1, 2)

        self.btn_exit = QtWidgets.QPushButton('Exit')
        self.uGrid.addWidget(self.btn_exit, 8, 2, 1, 2)

        listOfButtons = [self.btn_search_building, self.btn_convert, self.btn_analysis, self.btn_validation, self.btn_about, self.btn_exit]
        listOfLabels = [self.lbl_search, self.lbl_convert, self.lbl_analysis, self.lbl_validation]

        for button in listOfButtons:
            button.setStyleSheet("QPushButton {font-size: 16pt;}")
            button.setMinimumHeight(button_height * self.btn_search_building.height())

        for label in listOfLabels:
            label.setStyleSheet("QLabel {font-size: 14pt;}")

        self.vbox.addLayout(self.uGrid)

        # setup of bottom image
        gf.load_banner(self, os.path.join(pypath, r'pictures\e3dbig.png'), sizefactor)

        # binding buttons to functions
        self.btn_search_building.clicked.connect(self.open_search)
        self.btn_analysis.clicked.connect(self.open_analysis)
        self.btn_validation.clicked.connect(self.open_validation)
        self.btn_about.clicked.connect(self.open_about)
        self.btn_exit.clicked.connect(self.func_exit)

    def open_search(self):
        global posx, posy
        posx, posy = gf.dimensions(self)
        gf.next_window(self, search())

    def open_analysis(self):
        global posx, posy
        posx, posy = gf.dimensions(self)
        gf.next_window(self, analysis())

    def open_validation(self):
        global posx, posy
        posx, posy = gf.dimensions(self)
        gf.next_window(self, validation())

    def open_about(self):
        global posx, posy
        posx, posy = gf.dimensions(self)
        gf.next_window(self, about(), False)

    def func_exit(self):
        gf.close_application(self)




class search(QtWidgets.QWidget):
    def __init__(self):
        #initiate the parent
        super(search,self).__init__()
        self.initUI()

    def initUI(self):
        global posx, posy, width, height, sizefactor, sizer
        gf.windowSetup(self, posx, posy, width, height, pypath, 'CityATB - Search Building(s)/City Quarter(s)')

        self.vbox_value = QtWidgets.QVBoxLayout(self)
        self.setLayout(self.vbox_value)

        coordinateReferenceSystems = ['', 'EPSG:2056', 'EPSG:2263', 'EPSG:25830', 'EPSG:25832', 'EPSG:25833', 'EPSG:27700', 'EPSG:28992', 'EPSG:2979', 'EPSG:31256', 'EPSG:31370', 'EPSG:31467', 'EPSG:32118', 'EPSG:32626', 'EPSG:32627', 'EPSG:32628', 'EPSG:3879', 'EPSG:4326', 'EPSG:4979']

        self.uGrid = QtWidgets.QGridLayout()

        # setup of buttons
        self.btn_select_folder = QtWidgets.QPushButton('Select folder', self)
        self.uGrid.addWidget(self.btn_select_folder, 0, 0, 1, 1)
        
        self.textbox_folder = QtWidgets.QLineEdit('')
        self.textbox_folder.setReadOnly(True)
        self.textbox_folder.setPlaceholderText('directory path')
        self.uGrid.addWidget(self.textbox_folder, 0, 1, 1, 4)

        self.lbl_spcr = QtWidgets.QLabel('')
        self.uGrid.addWidget(self.lbl_spcr, 0, 5, 1, 1)
        
        self.lbl_value = QtWidgets.QLabel('Value:')
        self.uGrid.addWidget(self.lbl_value, 0, 6, 1, 1)
        
        self.textbox_value = QtWidgets.QLineEdit('', self)
        self.textbox_value.setPlaceholderText('enter your value here')
        self.uGrid.addWidget(self.textbox_value, 0, 7, 1, 4)

        self.vbox_value.addLayout(self.uGrid)

        self.groupbox = QtWidgets.QGroupBox(' Coordinate search ')
        self.vbox_value.addWidget(self.groupbox)
        self.groupbox.setStyleSheet("QGroupBox {border: 1px solid rgb(90,90,90);margin-top: 20px;} QGroupBox::title {bottom: 6px; left: 5px;}")

        self.mGrid = QtWidgets.QGridLayout()
        self.groupbox.setLayout(self.mGrid)

        self.lbl_iCRS = QtWidgets.QLabel('Input CRS:')
        self.mGrid.addWidget(self.lbl_iCRS, 1, 0, 1, 1)
        
        self.combobox_input = QtWidgets.QComboBox()
        self.combobox_input.addItems(coordinateReferenceSystems)
        self.mGrid.addWidget(self.combobox_input, 1, 1, 1, 3)
        
        self.lbl_oCRS = QtWidgets.QLabel('Output CRS:')
        self.mGrid.addWidget(self.lbl_oCRS, 1, 5, 1, 1)
        
        self.combobox_output = QtWidgets.QComboBox()
        self.combobox_output.addItems(coordinateReferenceSystems)
        self.mGrid.addWidget(self.combobox_output, 1, 6, 1, 3)

        self.btn_load_crs = QtWidgets.QPushButton('load .csv', self)
        self.mGrid.addWidget(self.btn_load_crs, 1, 10, 1, 3)
        self.btn_load_crs.setEnabled(False)

        self.lbl_CRS1 = QtWidgets.QLabel('')
        self.mGrid.addWidget(self.lbl_CRS1, 2, 0, 1, 12)
        
        self.lbl_x = QtWidgets.QLabel('Longitude:')
        self.mGrid.addWidget(self.lbl_x, 4, 0, 1, 1)
                
        self.QL_x = QtWidgets.QLineEdit('')
        self.mGrid.addWidget(self.QL_x, 4, 1, 1, 3)
        self.QL_x.setPlaceholderText('enter longitude')
        
        self.lbl_y = QtWidgets.QLabel('Latitude:')
        self.mGrid.addWidget(self.lbl_y, 4, 5, 1, 1)
        
        self.QL_y = QtWidgets.QLineEdit('')
        self.mGrid.addWidget(self.QL_y, 4, 6, 1, 3)
        self.QL_y.setPlaceholderText('enter latitude')

        self.btn_apoint = QtWidgets.QPushButton('add Point', self)
        self.mGrid.addWidget(self.btn_apoint, 4, 10, 1, 3)
        
        self.btn_rpoint = QtWidgets.QPushButton('remove last Point', self)
        self.mGrid.addWidget(self.btn_rpoint, 5, 6, 1, 3)
        self.btn_rpoint.setEnabled(False)

        self.sb_scale = QtWidgets.QSpinBox(self)
        self.sb_scale.setRange(100, 200)
        self.mGrid.addWidget(self.sb_scale, 5, 10, 1, 2)
        self.sb_scale.setSuffix('%')
        self.sb_scale.setSingleStep(10)

        self.btn_scale = QtWidgets.QPushButton('Scale', self)
        self.mGrid.addWidget(self.btn_scale, 5, 12, 1, 1)
        self.btn_scale.setEnabled(False)
        
        self.tbl_coor = QtWidgets.QTableWidget(self)
        self.tbl_coor.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.mGrid.addWidget(self.tbl_coor, 6, 0, 1, 13)

        self.rGrid = QtWidgets.QGridLayout()


        self.btn_run = QtWidgets.QPushButton('Run', self)
        self.btn_run.setEnabled(False)
        self.rGrid.addWidget(self.btn_run, 0, 0, 1, 1)

        self.progress_bar = QtWidgets.QProgressBar(self)
        self.rGrid.addWidget(self.progress_bar, 0, 1, 1, 4)

        self.label_result = QtWidgets.QLabel('Results:')
        self.rGrid.addWidget(self.label_result, 1, 0, 1, 2)
        
        self.table = QtWidgets.QTableWidget()
        self.table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.rGrid.addWidget(self.table, 2, 0, 1, 5)

        self.vbox_value.addLayout(self.rGrid)


        self.lGrid = QtWidgets.QGridLayout()
        
        self.btn_new = QtWidgets.QPushButton('New Search')
        self.btn_new.setEnabled(False)
        self.lGrid.addWidget(self.btn_new, 0, 0, 1, 1)
        
        self.btn_file_analysis = QtWidgets.QPushButton('Analyse files')
        self.btn_file_analysis.setEnabled(False)
        self.lGrid.addWidget(self.btn_file_analysis, 0, 1, 1, 1)
        
        self.btn_save = QtWidgets.QPushButton('Save results')
        self.btn_save.setEnabled(False)
        self.lGrid.addWidget(self.btn_save, 1, 0, 1, 1)
        
        self.btn_exit = QtWidgets.QPushButton('Main Window')
        self.lGrid.addWidget(self.btn_exit, 1, 1, 1, 1)
        
        self.vbox_value.addLayout(self.lGrid)

        # binding buttons to functions
        self.btn_select_folder.clicked.connect(self.folder)
        self.btn_apoint.clicked.connect(self.add)
        self.btn_rpoint.clicked.connect(self.remove)
        self.btn_scale.clicked.connect(self.scale_area)
        self.btn_run.clicked.connect(self.run_search)
        self.btn_new.clicked.connect(self.new)
        self.btn_file_analysis.clicked.connect(self.analyse_search)
        self.btn_save.clicked.connect(self.save_window)
        self.btn_exit.clicked.connect(self.main_winodw)

        self.flagStop = False                                               # flag to signal stop to search func
        self.running = False                                                # shows wether search is running or not
        self.completed = 0                                                  # value of progressbar

        # finishing gui
        sf.displaysetup(self)
        sf.data_transfer(self, dirpath, inputCoor, outputCoor, CRS)


    def folder(self):
        global dirpath
        dirpath = sf.select_folder(self)

    def add(self):
        global inputCoor, outputCoor, scaledCoor, CRS
        CRS = [self.combobox_input.currentText(), self.combobox_output.currentText()]
        inputCoor, outputCoor, scaledCoor = sf.add_point(self, inputCoor, outputCoor, scaledCoor)

    def remove(self):
        global inputCoor, outputCoor, scaledCoor, CRS
        inputCoor, outputCoor, scaledCoor = sf.remove_last(self, inputCoor, outputCoor, scaledCoor)
        if self.tbl_coor.rowCount() == 0:
            CRS = ['', '']

    def scale_area(self):
        global inputCoor, outputCoor, scaledCoor
        inputCoor, outputCoor, scaledCoor = sf.scale_outset(self, inputCoor, outputCoor, scaledCoor)

    def run_search(self):
        global inputCoor, outputCoor, search_info, scaledCoor
        inputCoor, outputCoor, search_info = sf.search(self, dirpath, inputCoor, outputCoor, scaledCoor, self.sb_scale.value(), app)
        

    def new(self):
        global dirpath, inputCoor, outputCoor, scaledCoor, CRS, posx, posy
        dirpath = ''                                            # clearing directorypath
        inputCoor = []                                          # clearing list of input coordinates
        outputCoor = []                                         # clearing list of output coordinates
        scaledCoor = []
        CRS = ['', '']
        posx, posy = gf.dimensions(self)
        gf.next_window(self, search())

    def analyse_search(self):
        global analyseSearch, posx, posy
        analyseSearch = True
        posx, posy = gf.dimensions(self)
        gf.next_window(self, analysis())

    def save_window(self):
        global posx, posy
        posx, posy = gf.dimensions(self)
        gf.next_window(self, saveResults())

    def main_winodw(self):
        global posx, posy
        posx, posy = gf.dimensions(self)
        gf.next_window(self, mainWindow())




class analysis(QtWidgets.QWidget):
    def __init__(self):
        #initiate the parent
        super(analysis,self).__init__()
        self.initUI()

    def initUI(self):
        global posx, posy, width, height, sizefactor, data, gmlpath, dirpath, analyseSearch, validationFilenames, analyseValidation
        gf.windowSetup(self, posx, posy, width, height, pypath, 'CityATB CityGML Analysis')

        # setup of gui / layout
        self.vbox = QtWidgets.QVBoxLayout(self)
        self.setLayout(self.vbox)   
        
        # setup of header image
        gf.load_banner(self, os.path.join(pypath, r'pictures\e3dHeader.png'), sizefactor)

        self.uGrid = QtWidgets.QGridLayout()
        
        self.btn_select_file = QtWidgets.QPushButton('Select CityGML file', self)                       # btn to select single .gml / .xml file or .zip folder
        self.uGrid.addWidget(self.btn_select_file, 0, 0, 1, 1)
        
        self.textbox_gml = QtWidgets.QLineEdit('')                                                      # textbox to display single file path
        self.textbox_gml.setReadOnly(True)
        self.textbox_gml.setPlaceholderText('.gml path')
        self.uGrid.addWidget(self.textbox_gml, 0, 1, 1, 3)
        
        self.btn_select_folder = QtWidgets.QPushButton('Select folder for multiple files', self)        # btn to select directory of .gml / .xml files 
        self.uGrid.addWidget(self.btn_select_folder, 1, 0, 1, 1)
        
        self.textbox_gml_folder = QtWidgets.QLineEdit('')                                               # textbox to display directory path
        self.textbox_gml_folder.setReadOnly(True)
        self.textbox_gml_folder.setPlaceholderText('directory path')
        self.uGrid.addWidget(self.textbox_gml_folder, 1, 1, 1, 3)
        
        self.btn_run_analysis = QtWidgets.QPushButton('Run Analysis', self)                             # btn to start analysis
        self.uGrid.addWidget(self.btn_run_analysis, 2, 0, 1, 1)

        self.progress_bar = QtWidgets.QProgressBar(self)                                                # progress bar displays computational progress
        self.uGrid.addWidget(self.progress_bar, 2, 1, 1, 3)

        self.vbox.addLayout(self.uGrid)                                                             # adding sub-layout to main-layout
        
        self.table = QtWidgets.QTableWidget(self)                                                       # table to display analysis results
        self.vbox.addWidget(self.table)
        self.table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)

        self.lGrid = QtWidgets.QGridLayout()
        
        self.btn_reset = QtWidgets.QPushButton('Reset window',self)                                     # btn to reset window to defaults
        self.lGrid.addWidget(self.btn_reset, 0, 0, 1, 3)
        
        self.btn_save = QtWidgets.QPushButton('Save results',self)                                      # btn to jump to 'save' window
        self.lGrid.addWidget(self.btn_save, 0, 3, 1, 3)
        
        self.btn_search = QtWidgets.QPushButton('Search for buildings', self)                           # btn to jump to 'search' window
        self.lGrid.addWidget(self.btn_search, 1, 0, 1, 3)

        self.btn_validation = QtWidgets.QPushButton('Validation',self)                                  # btn to jump to 'validation' window
        self.lGrid.addWidget(self.btn_validation, 1, 3, 1, 3)
    
        self.btn_about = QtWidgets.QPushButton('About',self)                                            # btn to jump to 'about' window
        self.lGrid.addWidget(self.btn_about, 2, 0, 1, 3)
        
        self.btn_mainWindow = QtWidgets.QPushButton('Main Window',self)                                 # btn to close programme
        self.lGrid.addWidget(self.btn_mainWindow, 2, 3, 1, 3)

        self.vbox.addLayout(self.lGrid)                                                             # adding sub-layout to main-layout

        # en/disabling buttons
        self.btn_save.setEnabled(False)
        self.btn_run_analysis.setEnabled(False)
        self.btn_reset.setEnabled(False)

        # binding buttons to functions
        self.btn_select_file.clicked.connect(self.func_select_file)
        self.btn_select_folder.clicked.connect(self.func_select_folder)
        self.btn_run_analysis.clicked.connect(self.func_start_analysis)
        self.btn_reset.clicked.connect(self.func_new_search)
        self.btn_save.clicked.connect(self.open_save)
        self.btn_search.clicked.connect(self.open_search)
        self.btn_validation.clicked.connect(self.open_vali)
        self.btn_about.clicked.connect(self.open_about)
        self.btn_mainWindow.clicked.connect(self.open_mainWindow)

        self.running = False                                            # flag displaying if analysis is running

        # checking for paths
        data, analyseSearch, analyseValidation = af.data_transfer(self, data, gmlpath, dirpath, search_info,
                                                                  analyseSearch, validationFilenames, 
                                                                  analyseValidation)

    def func_select_file(self):
        global gmlpath, dirpath
        gmlpath, dirpath = af.select_gml(self)

    def func_select_folder(self):
        global dirpath
        dirpath = af.select_folder(self)

    def func_start_analysis(self):
        global data
        data, title, msg = af.run_analysis(self, gmlpath, dirpath, pypath, app)
        if data != []:
            af.display(self, data)
            gf.messageBox(self, title, msg)

    def func_new_search(self):
        global gmlpath, dirpath, data
        af.new_search(self)
        gmlpath = ''
        dirpath = ''
        data = []
    
    def open_save(self):
        global posx, posy
        posx, posy = gf.dimensions(self)
        gf.next_window(self, saveResults())

    def open_search(self):
        global posx, posy
        posx, posy = gf.dimensions(self)
        gf.next_window(self, search())

    def open_vali(self):
        global posx, posy
        posx, posy = gf.dimensions(self)
        gf.next_window(self, validation())

    def open_about(self):
        global posx, posy
        posx, posy = gf.dimensions(self)
        gf.next_window(self, about(), False)
    
    def open_mainWindow(self):
        global posx, posy
        posx, posy = gf.dimensions(self)
        gf.next_window(self, mainWindow())




class validation(QtWidgets.QWidget):
    def __init__(self):
        #initiate the parent
        super(validation,self).__init__()
        self.initUI()

    def initUI(self):
        global posx, posy, width, height, sizefactor, sizer
        gf.windowSetup(self, posx, posy, width, height, pypath, 'CityATB - Schema specific validation')

        # setup of gui / layout
        self.vbox_validation = QtWidgets.QVBoxLayout()
        self.setLayout(self.vbox_validation) 
        
        self.uGrid = QtWidgets.QGridLayout()

        self.lGrid = QtWidgets.QGridLayout()

        # setup of buttons
        self.btn_select_gml = QtWidgets.QPushButton('Select a GML file', self)
        self.uGrid.addWidget(self.btn_select_gml, 0, 0, 1, 1)
                
        self.textbox_gml = QtWidgets.QLineEdit('')
        self.textbox_gml.setReadOnly(True)
        self.textbox_gml.setPlaceholderText('.gml path')
        self.uGrid.addWidget(self.textbox_gml, 0, 1, 1, 3)
        
        self.btn_select_folder = QtWidgets.QPushButton('Selecet a folder', self)
        self.uGrid.addWidget(self.btn_select_folder, 1, 0, 1, 1)
                
        self.textbox_folder = QtWidgets.QLineEdit('')
        self.textbox_folder.setReadOnly(True)
        self.textbox_folder.setPlaceholderText('directory path')
        self.uGrid.addWidget(self.textbox_folder, 1, 1, 1, 3)
        
        self.btn_select_xsd = QtWidgets.QPushButton('Selecet an xsd schema', self)
        self.uGrid.addWidget(self.btn_select_xsd, 2, 0, 1, 1)
                 
        self.textbox_xsd = QtWidgets.QLineEdit('')
        self.textbox_xsd.setReadOnly(True)
        self.textbox_xsd.setPlaceholderText('.xsd path')
        self.uGrid.addWidget(self.textbox_xsd, 2, 1, 1, 3)
        
        self.btn_validation = QtWidgets.QPushButton("Start validation",self)
        self.uGrid.addWidget(self.btn_validation, 3, 0, 1, 1)
        self.btn_validation.setEnabled(False)
        
        self.progress_bar = QtWidgets.QProgressBar(self)
        self.uGrid.addWidget(self.progress_bar, 3, 1, 1, 3)
        self.progress_bar.setValue(0)
        
        self.table = QtWidgets.QTableWidget(self)
        self.uGrid.addWidget(self.table, 4, 0, 1, 4)
        self.table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        
        self.vbox_validation.addLayout(self.uGrid)


        self.btn_one = QtWidgets.QPushButton("CityGML 1.0",self)
        self.lGrid.addWidget(self.btn_one, 0, 0, 1, 3)
        self.btn_one.setEnabled(False)
        
        self.btn_two = QtWidgets.QPushButton("CityGML 2.0",self)
        self.lGrid.addWidget(self.btn_two, 0, 3, 1, 3)
        self.btn_two.setEnabled(False)
     
        self.btn_twoplusenergy = QtWidgets.QPushButton('CityGML 2.0+ energy ADE 1.0',self)
        self.lGrid.addWidget(self.btn_twoplusenergy, 0, 6, 1, 3)
        self.btn_twoplusenergy.setEnabled(False)
        
        self.btn_oneandtwo = QtWidgets.QPushButton('CityGML 1.0 + 2.0',self)
        self.lGrid.addWidget(self.btn_oneandtwo, 0, 9, 1, 3)
        self.btn_oneandtwo.setEnabled(False)
        
        self.btn_new_check = QtWidgets.QPushButton("New check",self)
        self.lGrid.addWidget(self.btn_new_check, 1, 0, 1, 3)
        self.btn_new_check.setEnabled(False)
        
        self.btn_analyze = QtWidgets.QPushButton("Analyse files",self)
        self.lGrid.addWidget(self.btn_analyze, 1, 3, 1, 3)
        self.btn_analyze.setEnabled(False)
        
        self.btn_save = QtWidgets.QPushButton("Save results", self)
        self.lGrid.addWidget(self.btn_save, 1, 6, 1, 3)
        self.btn_save.setEnabled(False)
        
        self.btn_main_window = QtWidgets.QPushButton("Main Window",self)
        self.lGrid.addWidget(self.btn_main_window, 1, 9, 1, 3)
        
        self.vbox_validation.addLayout(self.lGrid)

        # setting local variables
        self.filename_xsd = ''
        self.running = False
        self.flagStop = False

        self.buttons = [self.btn_validation, self.btn_one, self.btn_two, self.btn_twoplusenergy, self.btn_oneandtwo]            # list of buttons


        # binding buttons to functions
        self.btn_select_gml.clicked.connect(self.xmlfile)
        self.btn_select_folder.clicked.connect(self.folder)
        self.btn_select_xsd.clicked.connect(self.xsdfile)
        self.btn_validation.clicked.connect(self.default)
        self.btn_one.clicked.connect(self.one)
        self.btn_two.clicked.connect(self.two)
        self.btn_twoplusenergy.clicked.connect(self.twoplusenergy)
        self.btn_oneandtwo.clicked.connect(self.oneandtwo)
        self.btn_new_check.clicked.connect(self.reset_window)
        self.btn_analyze.clicked.connect(self.analyse_validation)
        self.btn_save.clicked.connect(self.open_save)
        self.btn_main_window.clicked.connect(self.main_window)

        # finishing gui
        vf.data_transfer(self, gmlpath, dirpath)
        vf.displaysetup(self, validata)

    def xmlfile(self):
        global gmlpath, dirpath
        gmlpath, dirpath = vf.select_gml(self)

    def folder(self):
        global dirpath
        dirpath = vf.select_folder(self)

    def xsdfile(self):
        global gmlpath, dirpath
        vf.select_xsd(self, gmlpath, dirpath)
        
    def default(self):
        global validata, validationFilenames, xsd_help, gmlpath, dirpath
        validata, validationFilenames, xsd_help = vf.start_validation(
            self, [self.filename_xsd], self.btn_validation, 'Start validation', gmlpath, dirpath, app, validata, xsd_help, validationFilenames)

    def one(self):
        global validata, validationFilenames, xsd_help, gmlpath, dirpath
        validata, validationFilenames, xsd_help = vf.start_validation(
            self, [os.path.join(pypath, r'schemas\v1.0\CityGML1.0.xsd')], self.btn_one, 'CityGML 1.0', gmlpath, dirpath, app, validata, xsd_help, validationFilenames)

    def two(self):
        global validata, validationFilenames, xsd_help, gmlpath, dirpath
        validata, validationFilenames, xsd_help = vf.start_validation(
            self, [os.path.join(pypath, r'schemas\v2.0\CityGML2.0.xsd')], self.btn_two, 'CityGML 2.0', gmlpath, dirpath, app, validata, xsd_help, validationFilenames)

    def twoplusenergy(self):
        global validata, validationFilenames, xsd_help, gmlpath, dirpath
        validata, validationFilenames, xsd_help = vf.start_validation(
            self, [os.path.join(pypath, r'schemas\v2.0+EnergyADE\cityGML+energyADE.xsd')], self.btn_twoplusenergy, 'CityGML 2.0+ energy ADE 1.0', gmlpath, dirpath, app, validata, xsd_help, validationFilenames)

    def oneandtwo(self):
        global validata, validationFilenames, xsd_help, gmlpath, dirpath
        validata, validationFilenames, xsd_help = vf.start_validation(
            self, [os.path.join(pypath, r'schemas\v1.0\CityGML1.0.xsd'), os.path.join(pypath, r'schemas\v2.0\CityGML2.0.xsd')], self.btn_oneandtwo, 'CityGML 1.0 + 2.0', gmlpath, dirpath, app, validata, xsd_help, validationFilenames)

    def reset_window(self):
        global validata, gmlpath, dirpath, validationFilenames
        validata = []
        validationFilenames = []
        gmlpath = ''
        dirpath = ''
        vf.new_check(self, validata)

    def analyse_validation(self):
        global analyseValidation, posx, posy
        analyseValidation = True
        posx, posy = gf.dimensions(self)
        gf.next_window(self, analysis())

    def open_save(self):
        global posx, posy
        posx, posy = gf.dimensions(self)
        gf.next_window(self, saveResults())

    def main_window(self):
        global posx, posy
        posx, posy = gf.dimensions(self)
        gf.next_window(self, mainWindow())
        


class about(QtWidgets.QWidget):
    def __init__(self):
        #initiate the parent
        super(about,self).__init__()
        self.initUI()

    def initUI(self):
        global posx, posy, width, height, sizefactor, sizer

        gf.windowSetup(self, posx, posy, width, height, pypath, 'CityATB About')

        # creating main layout
        self.vbox = QtWidgets.QVBoxLayout(self)
        self.setLayout(self.vbox)

        # setup of header image
        gf.load_banner(self, os.path.join(pypath, r'pictures\e3dHeader.png'), sizefactor)

        self.textwidget = QtWidgets.QTextBrowser()
        self.vbox.addWidget(self.textwidget)
        self.textwidget.setFontPointSize(14)
        with open(os.path.join(pypath, 'about/about.txt'), 'r') as file:
            text = file.read()
        self.textwidget.setText(text)




class saveResults(QtWidgets.QWidget):
    def __init__(self):
        #initiate the parent
        super(saveResults,self).__init__()
        self.initUI()

    def initUI(self):
        global posx, posy, width, height, sizefactor, sizer
        gf.windowSetup(self, posx, posy, width, height, pypath, 'CityATB - Export results')

        # setup of gui / layout
        self.vbox_save_results = QtWidgets.QVBoxLayout(self)
        self.setLayout(self.vbox_save_results)      
        self.uGrid = QtWidgets.QGridLayout()
        
        
        # setup of buttons
        self.lbl_output_name = QtWidgets.QLabel('Enter name for output file:', self)
        self.uGrid.addWidget(self.lbl_output_name, 0, 0, 1, 1)
        
        self.textbox_output_name = QtWidgets.QLineEdit('')
        self.textbox_output_name.setPlaceholderText(time.strftime('CityGML Export %Y-%m-%d'))
        self.uGrid.addWidget(self.textbox_output_name, 0, 1, 1, 3)
        
        self.btn_output_folder = QtWidgets.QPushButton('Select folder')
        self.uGrid.addWidget(self.btn_output_folder, 1, 0, 1, 1)
        
        self.textbox_output_folder = QtWidgets.QLineEdit('')
        self.textbox_output_folder.setReadOnly(True)
        self.textbox_output_folder.setPlaceholderText(dirpath + r'''\output\ ''')
        self.uGrid.addWidget(self.textbox_output_folder, 1, 1, 1, 3)
        
        self.vbox_save_results.addLayout(self.uGrid)


        self.gb_data = QtWidgets.QGroupBox(' Select data for export ')
        self.vbox_save_results.addWidget(self.gb_data)
        
        self.mGrid = QtWidgets.QGridLayout()
        self.gb_data.setLayout(self.mGrid)
        
        self.checkbox_analysis = QtWidgets.QCheckBox('Analysis', self)
        self.mGrid.addWidget(self.checkbox_analysis, 0, 0, 1, 1)
        
        self.checkbox_validation = QtWidgets.QCheckBox('Validation', self)
        self.mGrid.addWidget(self.checkbox_validation, 0, 1, 1, 1)
        
        self.checkbox_search = QtWidgets.QCheckBox('Search', self)
        self.mGrid.addWidget(self.checkbox_search, 0, 2, 1, 1)

        self.checkbox_cgml = QtWidgets.QCheckBox('to CityGML', self)
        self.mGrid.addWidget(self.checkbox_cgml, 0, 3, 1, 1)
        

        self.gb_format = QtWidgets.QGroupBox(' Select format to save results: ')
        self.vbox_save_results.addWidget(self.gb_format)
        
        self.lGrid = QtWidgets.QGridLayout()
        self.gb_format.setLayout(self.lGrid)

        
        self.checkbox_text = QtWidgets.QCheckBox('Text (.txt)', self)
        self.lGrid.addWidget(self.checkbox_text, 1, 0, 1, 2)
        
        self.checkbox_csv = QtWidgets.QCheckBox('CSV (.csv)', self)
        self.lGrid.addWidget(self.checkbox_csv, 1, 2, 1, 2)
        
        self.checkbox_json = QtWidgets.QCheckBox('JSON (.json)', self)
        self.lGrid.addWidget(self.checkbox_json, 2, 0, 1, 2)
        
        self.checkbox_xml = QtWidgets.QCheckBox('XML (.xml)', self)
        self.lGrid.addWidget(self.checkbox_xml, 2, 2, 1, 2)


        self.bGrid = QtWidgets.QGridLayout()
        
        self.btn_save_conform = QtWidgets.QPushButton('Save', self)
        self.bGrid.addWidget(self.btn_save_conform, 3, 0, 1, 1)
        
        self.progress_bar = QtWidgets.QProgressBar(self)
        self.bGrid.addWidget(self.progress_bar, 3, 1, 1, 3)
        
        
        self.list = QtWidgets.QListWidget(self)
        self.bGrid.addWidget(self.list, 4, 0, 1, 4)
        self.list.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        
        self.btn_reset = QtWidgets.QPushButton("Reset",self)
        self.bGrid.addWidget(self.btn_reset, 5, 0, 1, 2)
        
        self.btn_open_dir = QtWidgets.QPushButton("Open Output dir",self)
        self.bGrid.addWidget(self.btn_open_dir, 5, 2, 1, 2)
        self.btn_open_dir.setEnabled(False)
        
        self.btn_quit = QtWidgets.QPushButton("Exit",self)
        self.bGrid.addWidget(self.btn_quit, 6, 0, 1, 2)
        
        self.btn_main_window = QtWidgets.QPushButton("Main window",self)
        self.bGrid.addWidget(self.btn_main_window, 6, 2, 1, 2)
        
        self.vbox_save_results.addLayout(self.bGrid)

        # binding buttons to functions
        self.btn_main_window.clicked.connect(self.main_window)
        self.btn_output_folder.clicked.connect(self.get_output_data_folder)
        self.btn_save_conform.clicked.connect(self.save)
        self.btn_quit.clicked.connect(self.exit)
        self.btn_reset.clicked.connect(self.reset)
        self.btn_open_dir.clicked.connect(self.openfolder)
        

        # en/disabling
        self.checkbox_analysis.setEnabled(data != [])
        self.checkbox_validation.setEnabled(validata != [])
        self.checkbox_search.setEnabled(search_info != [])
        self.checkbox_cgml.setEnabled(search_info != [])
        
        self.checkboxes_AV = [self.checkbox_analysis, self.checkbox_validation]                                 # checkboxes data
        self.checkboxes_DT = [self.checkbox_csv, self.checkbox_json, self.checkbox_text, self.checkbox_xml]     # checkboxes export type



    def get_output_data_folder(self):
        save_f.folder(self)

    def save(self):
        save_f.save(self, data, validata, search_info, dirpath)

    def openfolder(self):
        save_f.openfolder(self, dirpath)

    def reset(self):
        save_f.reset(self)

    def main_window(self):
        global posx, posy
        posx, posy = gf.dimensions(self)
        gf.next_window(self, mainWindow())

    def exit(self):
        gf.close_application(self)





if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle('Fusion')
    widget = mainWindow()
    widget.show()
    sys.exit(app.exec_())