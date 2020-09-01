from PyQt4 import QtGui, QtCore
import pyproj
import math
import time
import glob
import os
import lxml.etree as ET
import matplotlib.path as mpl
import numpy as np
import csv

 

def select_folder(self):
    """func to select folder"""
    dirpath = QtGui.QFileDialog.getExistingDirectory(self, "Select Directory")
    if dirpath:
        self.textbox_folder.setText(dirpath)
        self.btn_run.setEnabled(True)
        self.btn_new.setEnabled(True)
        return dirpath
    else:
        pass



def displaysetup(self):
    """preparing tbl_coor in gui"""
    self.tbl_coor.setColumnCount(4)
    self.tbl_coor.setHorizontalHeaderLabels(['Input Longitude', 'Input Latitude', 'Output Longitude', 'Output Latitude', 'scaled Long', 'scaled Lat'])          ### arranging headers
    self.tbl_coor.verticalHeader().hide()
    self.tbl_coor.horizontalHeader().hide()
    self.tbl_coor.horizontalHeader().setResizeMode(0, QtGui.QHeaderView.ResizeToContents)    ### adjusting size of table
    self.tbl_coor.horizontalHeader().setResizeMode(1, QtGui.QHeaderView.ResizeToContents)    
    self.tbl_coor.horizontalHeader().setResizeMode(2, QtGui.QHeaderView.Stretch)
    self.tbl_coor.horizontalHeader().setResizeMode(3, QtGui.QHeaderView.Stretch)



def del_scale(self):
    """to remove old scaled when removing or adding new oCoor"""
    while self.tbl_coor.columnCount() > 4:
        self.tbl_coor.removeColumn(4)
    self.tbl_coor.horizontalHeader().setResizeMode(3, QtGui.QHeaderView.Stretch)
    self.sb_scale.setValue(100)



def add_point(self, inputCoor, outputCoor, scaledCoor):
    """add point to list of coordinates"""
    if self.combobox_input.currentText() != '' and self.combobox_output.currentText() != '':        # checking if input and output CRS are selected
        if self.QL_x.text():                                                                        # trying to convert longitude
            try:
                X = float(self.QL_x.text())
                if self.QL_y.text():                                                                # trying to convert latitude
                    try:
                        Y = float(self.QL_y.text())
                    except:
                        msg = 'Could not convert ' + self.QL_y.text() + ' to float'
                        self.message_complete = QtGui.QMessageBox.information(self, 'Warning!', msg)
                        return inputCoor, outputCoor, scaledCoor
                else:
                    self.message_complete = QtGui.QMessageBox.information(self, 'Warning!', 'Please enter a Latitude')
                    return inputCoor, outputCoor, scaledCoor
            except:
                msg = 'Could not convert ' + self.QL_x.text() + ' to float'
                self.message_complete = QtGui.QMessageBox.information(self, 'Warning!', msg)
                return inputCoor, outputCoor, scaledCoor
        else:
            self.message_complete = QtGui.QMessageBox.information(self, 'Warning!', 'Please enter a Longitude')
            return inputCoor, outputCoor, scaledCoor
        if X and Y:
            if (X, Y) not in inputCoor:                                                             # checks if point is already present
                input_pr=pyproj.Proj(self.combobox_input.currentText())                             # getting input CRS
                output_pr = pyproj.Proj(self.combobox_output.currentText())                         # getting output CRS
                x, y = pyproj.transform(input_pr,output_pr, X, Y, always_xy = True)                 # transfroming point
                if x == math.inf or y == math.inf or x == -math.inf or y == -math.inf:              # checking if values are reasonable
                    self.message_complete = QtGui.QMessageBox.information(self, 'Warning!', 'Could not convert area because of too large values.')
                    return inputCoor, outputCoor, scaledCoor
                if len(outputCoor) == 2:                        # checks if the first 3 given coordinates create an area - might change to check for min area
                    area = (outputCoor[0][0] * (outputCoor[1][1] - y) + outputCoor[1][0] *(y - outputCoor[0][1]) + x * (outputCoor[0][1] - outputCoor[1][1])) * 0.5
                    if area == 0:
                        self.message_complete = QtGui.QMessageBox.information(self, 'Warning!', 'Given coordinates do not create an area!')
                        return inputCoor, outputCoor, scaledCoor
                    self.btn_scale.setEnabled(True)
                inputCoor.append((X, Y))                        # appends coordinates
                outputCoor.append((x, y))
                point_to_table(self, [X, Y, x, y])
                self.btn_rpoint.setEnabled(True)
                self.btn_new.setEnabled(True)
                self.combobox_input.setEnabled(False)
                self.combobox_output.setEnabled(False)
                self.QL_x.setText('')
                self.QL_y.setText('')
                del_scale(self)
                return inputCoor, outputCoor, []
            else:
                QtGui.QMessageBox.information(self, "Important", "This point already exists")
    else:
        self.message_complete = QtGui.QMessageBox.information(self, 'Warning!', 'Please select input and output CRS!')
    return inputCoor, outputCoor, scaledCoor



def point_to_table(self, coordinates):
    """adding point to table - coordinates = [x, y, X, Y]"""
    self.tbl_coor.horizontalHeader().show()
    rowPosition = self.tbl_coor.rowCount()
    self.tbl_coor.insertRow(rowPosition)
    for i in range(4):
        newitem = QtGui.QTableWidgetItem(str(coordinates[i]))
        self.tbl_coor.setItem(rowPosition, i, newitem)
    self.tbl_coor.horizontalHeader().show()



def remove_last(self, inputCoor, outputCoor, scaledCoor):
    """ remove point from  polygon"""
    self.tbl_coor.removeRow(self.tbl_coor.rowCount()-1)
    inputCoor.remove(inputCoor[len(inputCoor)-1])           # removing point in input
    outputCoor.remove(outputCoor[len(outputCoor)-1])        # removing point in output
    if self.tbl_coor.rowCount() == 0:
        self.btn_rpoint.setEnabled(False)
        self.btn_new.setEnabled(False)
        self.tbl_coor.horizontalHeader().hide()
        self.combobox_input.setEnabled(True)
        self.combobox_output.setEnabled(True)
    del_scale(self)
    return inputCoor, outputCoor, []



def new_search(self):
    """reseting window to defaults"""
    self.textbox_folder.setText('')
    self.textbox_value.setText('')
    self.completed = 0
    self.progress_bar.setValue(0)
    self.btn_run.setEnabled(False)
    self.btn_new.setEnabled(False)
    self.btn_save.setEnabled(False)
    self.btn_file_analysis.setEnabled(False)
    self.btn_rpoint.setEnabled(False)
    self.QL_x.setText('')
    self.QL_y.setText('')
    self.combobox_input.setEnabled(True)
    self.combobox_output.setEnabled(True)
    self.sb_scale.setValue(100)
    self.btn_scale.setEnabled(False)
    self.combobox_input.setCurrentIndex(0)
    self.combobox_output.setCurrentIndex(0)
    while self.table.rowCount() > 0:                        # clearing result table
        self.table.removeRow(0)
    while self.table.columnCount() > 0:
        self.table.removeColumn(0)
    while self.tbl_coor.rowCount() > 0:                     # clearing coordinate table
        self.tbl_coor.removeRow(0)
    while self.tbl_coor.columnCount() > 0:
        self.tbl_coor.removeColumn(0)



def progress(self, max):
    """increassing value of progress bar until max is reached"""
    while self.completed < max:
        self.completed += 0.0001
        self.progress_bar.setValue(self.completed)



def value(self, fileNames, factor, app, startvalue = 0):
    """searching for a value in fileNames"""
    if self.flagStop == False:
        search_data = []
        noF = len(fileNames)
        crs = ''
        se_min = [math.inf, math.inf, math.inf]             # bounding coordinates for gml envelope
        se_max = [-math.inf, -math.inf, -math.inf]
        values = self.textbox_value.text().split('&')       # spliting content of QLineEdit by sepereator


        for i, file in enumerate(fileNames):
            app.processEvents()
            afb = []                            # help array
            if self.flagStop == False:
                tree = ET.parse(file[0])        # parsing file
                root = tree.getroot()           # getting root
                namespace = root.nsmap                                              # maping namespaces
                # searching for envelope
                envelope_E = root.find('./gml:boundedBy/gml:Envelope', namespace)
                if envelope_E != None:
                    try:
                        crs = envelope_E.attrib['srsName']
                    except:
                        print('error getting srs')
                buildings_in_file = root.findall('core:cityObjectMember/bldg:Building', namespace)      # gets buildings within file
                for building_E in buildings_in_file:                                                    # checking buildings and building parts
                    if file[1] == [] or (building_E.attrib['{http://www.opengis.net/gml}id'] in file[1]):
                        bs = building_E.getiterator()
                        bs = [b.text for b in bs]
                        if set(values).issubset(set(bs)):                                               # checks values of elements contain searched for values
                            afb.append(building_E.attrib['{http://www.opengis.net/gml}id'])
                            se_min, se_max = search_for_coordinates(building_E, namespace, se_min, se_max)
                            for BP in building_E.findall('./bldg:consistsOfBuildingPart', namespace):
                                se_min, se_max = search_for_coordinates(BP, namespace, se_min, se_max, building_E)
                progress(self, (i + 1) / noF * factor * 100 + startvalue)
            else:
                break
            if afb != []:
                search_data.append([os.path.basename(file[0]), list(set(afb))])
        return search_data, [se_min, se_max], crs



def coordinates(self, fileNames, factor, outputCoor, app, startvalue=0):
    """searching for area of outputCoor in fileNames"""
    if self.flagStop == False:
        #creating border
        border = mpl.Path(np.array(outputCoor))
        # surroding coordinates
        list_pol = outputCoor
        
        noF = len(fileNames)                        # number of files
        search_data = []                            # regular results

        # surrounding northed square
        se_min = [math.inf, math.inf, math.inf]     # lower corner
        se_max = [-math.inf, -math.inf, -math.inf]  # upper corner

        # oCoor_list = []                             # declaring list for coordinates from files
        for i, file in enumerate(fileNames):
            app.processEvents()
            fcheck = True
            building_list = []                      # buildings found in file
            # bounding coordinates
            x1 = False                              
            y1 = False
            x2 = False
            y2 = False
            if self.flagStop == False:              # checking if run has been interrupted
                tree = ET.parse(file)               # parsing file
                root = tree.getroot()               # getting root
                namespace = root.nsmap                                              # maping namespaces
                # searching for envelope
                envelope_E = root.find('./gml:boundedBy/gml:Envelope', namespace)
                if envelope_E != None:
                    try:
                        # srs = envelope.attrib['srsName'] currently not needed
                        lowerCorner = envelope_E.find('./gml:lowerCorner', namespace).text.split(' ')
                        x1 = float(lowerCorner[0])
                        y1 = float(lowerCorner[1])
                        upperCorner = envelope_E.find('./gml:upperCorner', namespace).text.split(' ')
                        x2 = float(upperCorner[0])
                        y2 = float(upperCorner[1])
                    except:
                        print('error within gml:envelope in file: ', file)
                if x1 and x2 and y1 and y2:                                         # checking if all coordinates are present
                    fcoor = [(x1, y1), (x2, y1), (x2, y2), (x1, y2)]
                    fcheck = border_check(border, list_pol, fcoor)
                if fcheck == True:                                                  # checks if it is necessary to search within file
                    buildings_in_file = root.findall('core:cityObjectMember/bldg:Building', namespace)      # gets buildings within file
                    for building_E in buildings_in_file:                                                    # checking buildings and building parts
                        building_list, se_min, se_max = search_element(border, outputCoor, building_list, se_min, se_max, building_E, namespace)

                        BPs_in_bldg = building_E.findall('./bldg:consistsOfBuildingPart', namespace)
                        for BP_E in BPs_in_bldg:
                            building_list, se_min, se_max = search_element(border, outputCoor, building_list, se_min, se_max, BP_E, namespace, building_E)

                progress(self, startvalue + (i + 1)/ noF * factor * 100)    # updating progressbar
            else:
                self.flagStop = False
                break
            if building_list != []:         # appending buildings to search data
                search_data.append([os.path.basename(file), list(set(building_list))])

        return search_data, [se_min, se_max]
    else:
        print('stoped form start (coor)')



def display(self, search_data):
    """displaying results in table"""
    self.table.setColumnCount(2)
    self.table.setRowCount(0)
    self.table.horizontalHeader().show()
    self.table.setHorizontalHeaderLabels(['File', 'Building'])
    self.table.verticalHeader().hide()
    m = 0
    for [file, buildings] in search_data:
        for j, building in enumerate(buildings):
            if j == 0:
                self.table.insertRow(m)
                newitem = QtGui.QTableWidgetItem(str(file))
                self.table.setItem(m, 0, newitem)
                newitem = QtGui.QTableWidgetItem(str(building))
                self.table.setItem(m, 1, newitem)
                m += 1
            else:
                self.table.insertRow(m)
                newitem = QtGui.QTableWidgetItem(str(building))
                self.table.setItem(m, 1, newitem)
                m += 1
    self.table.horizontalHeader().setResizeMode(0, QtGui.QHeaderView.Stretch)
    self.table.horizontalHeader().setResizeMode(1, QtGui.QHeaderView.Stretch)



def search(self, dirpath, inputCoor, outputCoor, scaledCoor, scale, app):
    """ deciding which algorithm to use for search"""
    self.flagStop = False
    if self.running == False:           # checks if search is already running
        self.running = True             # updating running flag
        self.completed = 0
        search_data = []
        search_info = []
        se_min_max = []
        crs = ''
        if scaledCoor != []:            # searching for scaled coordinates if they are present
            searchCoor = scaledCoor
        else:
            searchCoor = outputCoor
        fileNames = (glob.glob(os.path.join(dirpath, '*.gml')) + glob.glob(os.path.join(dirpath, '*.xml')))
        if fileNames:
            while self.table.rowCount() > 0:                        # clearing result table
                self.table.removeRow(0)
            while self.table.columnCount() > 0:
                self.table.removeColumn(0) 
            if len(inputCoor) == 2:                                 # checking number of coordinates
                choice = QtGui.QMessageBox.question(self, 'Attention!', "Not enough Coordinates! Do you want to form a square from the entered ones?",
                                QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
                if choice == QtGui.QMessageBox.Yes:
                    inputCoor, outputCoor = two_p_to_square(self, inputCoor, outputCoor)
                else:
                    pass
            if 0 < len(outputCoor) < 3:
                choice = QtGui.QMessageBox.question(self, 'Attention!', "Not enough Coordinates to form a polygon! Continue?",
                                QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
                if choice == QtGui.QMessageBox.Yes:
                    pass
                else:
                    self.running = False
                    return
            if self.textbox_value.text() or len(outputCoor) >= 3:   # checking if there is something to search for
                if self.textbox_value.text() and len(outputCoor) >= 3:              # searching for both
                    inputCoor, outputCoor = sorter(inputCoor, outputCoor, self)     # sorting coordinates
                    search_data, se_min_max, = coordinates(self, fileNames, 0.5, searchCoor, app)   # searching for coordinates
                    if search_data != []:                                           # if results are present seraching for value(s)
                        for w in search_data:
                            w[0] = os.path.join(dirpath, w[0])
                        search_data, se_min_max, crs = value(self, search_data, 0.5, app, 50)
                    else:
                        progress(self, 100)
                elif self.textbox_value.text():                     # searching for value
                    fileNames = [[x, []] for x in fileNames]
                    search_data, se_min_max, crs = value(self, fileNames, 1, app)
                elif len(outputCoor) >= 3:                          # seaching for coordinates
                    inputCoor, outputCoor = sorter(inputCoor, outputCoor, self)
                    search_data, se_min_max, = coordinates(self, fileNames, 1, searchCoor, app)
                    crs = ''
                else:
                    QtGui.QMessageBox.information(self, "Error", 'Could not decide for search algorithm')
                if search_data != []:
                    iCRS = [self.combobox_input.currentText(), inputCoor]
                    oCRS = [self.combobox_output.currentText(), searchCoor]
                    if crs != '':
                        oCRS[0] = crs
                    search_info = [dirpath, self.textbox_value.text(), iCRS, oCRS, se_min_max, search_data]
                    display(self, search_data)
                    self.btn_file_analysis.setEnabled(True)
                else:
                    QtGui.QMessageBox.information(self, "Important", 'No matching files have been found')
            else:
                QtGui.QMessageBox.information(self, "Error", 'No arguments for search')
        else:
            QtGui.QMessageBox.information(self, "Important", 'No files found in given directory')
            
        self.running = False                    # updating flags
        self.flagStop = False
        if search_data != []:
            self.btn_save.setEnabled(True)
        return inputCoor, outputCoor, search_info
    else:
        self.flagStop = True



def data_transfer(self, dirpath, iCoor, oCoor, CRS):
    """checking if a dir is already selected"""
    if dirpath != '':
        self.textbox_folder.setText(dirpath)
        self.btn_run.setEnabled(True)
        self.btn_new.setEnabled(True)
    if iCoor != [] and oCoor != [] and len(iCoor) == len(oCoor) and CRS != ['', '']:
        self.btn_new.setEnabled(True)
        self.combobox_input.setCurrentIndex(self.combobox_input.findText(CRS[0], QtCore.Qt.MatchFixedString))
        self.combobox_output.setCurrentIndex(self.combobox_output.findText(CRS[1], QtCore.Qt.MatchFixedString))
        self.combobox_input.setEnabled(False)
        self.combobox_output.setEnabled(False)
        self.btn_rpoint.setEnabled(True)
        for index in range(len(iCoor)):
            point_to_table(self, [iCoor[index][0], iCoor[index][1], oCoor[index][0], oCoor[index][1]])
            if len(oCoor) > 2:
                self.btn_scale.setEnabled(True)



def sorter(iCoor, oCoor, self, sort=False):
    """sorting coordinates to avoid wrong order"""
    pp = oCoor.copy()
    cent = (sum([p[0] for p in pp])/len(pp), sum([p[1] for p in pp])/len(pp))   # compute centroid
    pp.sort(key=lambda p: math.atan2(p[1]-cent[1], p[0]-cent[0]))               # sort by polar angle
    # checking for all possible sequences
    if oCoor == pp:
        return iCoor, oCoor
    elif oCoor == list(reversed(pp)):
        return iCoor, oCoor
    lang = pp + pp                                      # for different starting point
    lang_r = list(reversed(pp)) + list(reversed(pp))    # for differnet starting point and reversed order
    for i, short in enumerate(lang):
        if i == len(oCoor):
            break
        if short == oCoor[0]:
            if lang[i:i+len(oCoor)] == oCoor:
                return iCoor, oCoor
    for i, short in enumerate(lang_r):
        if i == len(oCoor):
            break
        if short == oCoor[0]:
            if lang_r[i:i+len(oCoor)] == oCoor:
                return iCoor, oCoor
    # pop up for comparing coordinates, suggested vs input
    if sort == False:
        msg = str('CityGML ATB suggests an alternative order.\n' + ','.join([str(p) for p in pp]) + '\nDo you want to use the suggested order?')
        choice = QtGui.QMessageBox.question(self, 'Attention!', msg, QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
        if choice == QtGui.QMessageBox.No:
            return iCoor, oCoor
    while self.tbl_coor.rowCount() > 0:                 # deleting old coordinates in table
        self.tbl_coor.removeRow(0)
    temp = []
    for i, p in enumerate(pp):                          # resorting input and Cooridnates and re-displaying coordinates
        index = oCoor.index(p)
        point_to_table(self, [iCoor[index][0], iCoor[index][1], oCoor[index][0], oCoor[index][1]])
        temp.append(iCoor[index])
    iCoor = temp
    return iCoor, pp
        
    

def AREA(oCoor):
    """calculates the area of polygon (input as 1D array of tuples)"""
    x = [i[0]for i in oCoor]
    y = [i[1]for i in oCoor]
    return 0.5*np.abs(np.dot(x, np.roll(y, 1))-np.dot(y, np.roll(x, 1)))



def stretch_poly(oCoor, x, y, scale):
    """to stretch a polygon by given factor, x and y presenting center around which the poly is steched"""
    stretched = []
    [stretched.append(((scale * (p[0] - x)) + x, (scale * (p[1] - y)) + y)) for p in oCoor]
    return stretched



def interpol_scale(inputCoor, p_old, scale, self, mode = 'sum'):
    """interpolating new coordinates for new scaled area"""
    inputCoor, p_old = sorter(inputCoor, p_old, self)           # sorting by polar angle
    a_shall = AREA(p_old) * (scale)                             # calculating user wanted area
    # calculating center of mass based on mode
    x_old = [i[0]for i in p_old]
    y_old = [i[1]for i in p_old]
    if mode == 'sum':
        x_mid = sum(x_old) / len(x_old)
        y_mid = sum(y_old) / len(y_old)
    else:
        x_mid = (max(x_old) + min(x_old)) * 0.5
        y_mid = (max(y_old) + min(y_old)) * 0.5
    # setting lower bound for interpolation
    s_low = 0
    a_low = 0
    # setting upper bound for interpolation
    s_high = 100
    a_high = AREA(stretch_poly(p_old, x_mid, y_mid, 100))
    
    i = 0                                                           # counter
    max_runs = 1000                                                 # max number of runs

    for i in range(max_runs):
        if a_low < a_shall < a_high:                                # checking if areas are suitable for interpolation
            s_new = (s_high+s_low)*0.5                              # calculating new scale
            a_new = AREA(stretch_poly(p_old, x_mid, y_mid, s_new))  # calculating new area
            if a_new == a_shall:                                    # break condition for exact match
                break
            elif a_new > a_shall:                                   # setting new higher bound
                a_high = a_new
                s_high = s_new
            elif a_new < a_shall:                                   # setting new lower bound
                a_low = a_new
                s_low = s_new
            else:
                print('error with bounds of new area')
        else:
            print('error while searching for interpolation bounds')
            return ['error with interpolation bounds']
        i -= - 1
    p_new = stretch_poly(p_old, x_mid, y_mid, s_new)
    return inputCoor, p_old, p_new



def border_check(border, list_of_border, list_of_coordinates):
    """ checks for area vice verca"""
    for point in list_of_coordinates:
        if border.contains_point(point):
            return True
    n_border = mpl.Path(np.array(list_of_coordinates))
    for point in list_of_border:
        if n_border.contains_point(point):
            return True
    return False



def scale_outset(self, iCoor, oCoor, sCoor):
    """starts scaling of coordinates"""
    if self.sb_scale.value() != 100 and len(oCoor) > 2:     # checks requirements
        iCoor, oCoor, sCoor = interpol_scale( iCoor, oCoor, self.sb_scale.value()/100, self, 'sum')     # interpolating
        self.tbl_coor.setColumnCount(6)
        for i, oriCoor in enumerate(sCoor):                         # adding scaled coordinates to table
            for n, coordinate in enumerate(oriCoor):
                newitem = QtGui.QTableWidgetItem(str(coordinate))
                self.tbl_coor.setItem(i, 4 + n, newitem)
        self.tbl_coor.setHorizontalHeaderLabels(['Input Longitude', 'Input Latitude', 'Output Longitude', 'Output Latitude', 'scaled Long', 'scaled Lat'])          # arranging headers
    elif self.sb_scale.value() == 100:      # removing scaled coordinates
        sCoor = []
        del_scale(self)
    else:
        QtGui.QMessageBox.information(self, "Error", 'Please change scale and make sure you entered enough coordinates')
    return iCoor, oCoor, sCoor



def new_min_max(new_values, old_min=[math.inf, math.inf, math.inf], old_max=[-math.inf, -math.inf, -math.inf]):
    """calculates new min and max values for search info (envelope)"""
    new_min = [min(new_values[0::3]), min(new_values[1::3]), min(new_values[2::3])]
    for i, value in enumerate(new_min):
        if value < old_min[i]:
            old_min[i] = value
    new_max = [max(new_values[0::3]), max(new_values[1::3]), max(new_values[2::3])]
    for i, value in enumerate(new_max):
        if value > old_max[i]:
            old_max[i] = value
    return old_min, old_max



def two_p_to_square(self, iCoor, oCoor):
    """calculates two coordinates to square, transforms coordinates and sorts list"""
    X1, Y1 = iCoor[0]                   # getting coordinates of first point
    X2, Y2 = iCoor[1]                   # getting coordinates of second point

    # calculating interim results
    Xc = (X1 + X2)/2                    # xCenter
    Yc = (Y1 + Y2)/2                    # yCenter
    Xd = (X1 - X2)/2                    # xDistance
    Yd = (Y1 - Y2)/2                    # yDistance

    # calculating new points
    X3 = round(Xc - Yd, 8)
    Y3 = round(Yc + Xd, 8)
    X4 = round(Xc + Yd, 8)
    Y4 = round(Yc - Xd, 8)

    # getting input and output CRS
    input_pr=pyproj.Proj(self.combobox_input.currentText())
    output_pr = pyproj.Proj(self.combobox_output.currentText())
    
    # transforming coordinates
    x3, y3 = pyproj.transform(input_pr,output_pr, X3, Y3, always_xy = True)
    x4, y4 = pyproj.transform(input_pr,output_pr, X4, Y4, always_xy = True)

    # adding new coordiantes to list
    iCoor = iCoor + [(X3, Y3),(X4, Y4)]
    oCoor = oCoor + [(x3, y3), (x4, y4)]
    
    # sorting coordinates
    iCoor, oCoor = sorter(iCoor, oCoor, self, True)
    
    return iCoor, oCoor



def prepSTR(text):
    """converts str from gml:posList element to needed lists"""
    oCoor_list = [float(x) for x in text.split()]
    min_max_list = oCoor_list.copy()
    del oCoor_list[2::3]                                                # delete every 3rd entry (height)
    oCoor_list = [ x for x in zip(oCoor_list[0::2], oCoor_list[1::2])]  # creating tuples of coordinates
    return oCoor_list, min_max_list



def search_element(border, outputCoor, building_list, se_min, se_max, searched_E, namespace, building_E=None):       # (element to check, map of namespaces, building to get building id)
    """searches for coordinates in given element"""
    if building_E == None:
        building_E = searched_E
    minim = [math.inf, math.inf, math.inf]
    maxim = [-math.inf, -math.inf, -math.inf]
    all_poylgons = []

    groundSurface_E = searched_E.find('.//bldg:boundedBy/bldg:GroundSurface', namespace)
    if groundSurface_E != None:                                             # checking for groundsurface in building/buildingpart
        posList_E = groundSurface_E.find('.//gml:posList', namespace)       # searching for list of coordinates
        if posList_E != None:           # case aachen lod2
            coor_list, min_max_list = prepSTR(posList_E.text)
            result, building_list, se_min, se_max = poly_check(border, outputCoor, building_list, se_min, se_max, coor_list, min_max_list, building_E)

        else:           # case hamburg lod2 2020
            pos_Es = groundSurface_E.findall('.//gml:pos', namespace)
            polygon = []
            for pos_E in pos_Es:
                polygon.append(pos_E.text)
            polyStr = ' '.join(polygon)
            coor, min_max = prepSTR(polyStr)
            all_poylgons.append(coor)
            minim, maxim = new_min_max(min_max, minim, maxim)
            min_max_list = minim + maxim
            result, building_list, se_min, se_max = poly_check(border, outputCoor, building_list, se_min, se_max, coor, min_max_list, building_E)

    else:               # case for lod1 files 
        poly_Es = searched_E.findall('.//gml:Polygon', namespace)
        all_poylgons = []
        for poly_E in poly_Es:
            polygon = []
            posList_E = searched_E.find('.//gml:posList', namespace)    # searching for list of coordinates
            if posList_E != None:
                polyStr = posList_E.text
            else:
                pos_Es = poly_E.findall('.//gml:pos', namespace)        # searching for individual coordinates in polygon
                for pos_E in pos_Es:
                    polygon.append(pos_E.text)
                polyStr = ' '.join(polygon)
            coor, min_max = prepSTR(polyStr)
            all_poylgons.append(coor)
            minim, maxim = new_min_max(min_max, minim, maxim)
        min_max_list = minim + maxim
        for polygon in all_poylgons:
            result, building_list, se_min, se_max = poly_check(border, outputCoor, building_list, se_min, se_max, polygon, min_max_list, building_E)
            if result:
                break
    return building_list, se_min, se_max



def search_for_coordinates(searched_E, namespace, se_min, se_max, building_E=None):
    if building_E == None:
        building_E = searched_E
    minim = [math.inf, math.inf, math.inf]
    maxim = [-math.inf, -math.inf, -math.inf]
    groundSurface_E = searched_E.find('.//bldg:boundedBy/bldg:GroundSurface', namespace)
    if groundSurface_E != None:                                             # checking for groundsurface in building/buildingpart
        posList_E = groundSurface_E.find('.//gml:posList', namespace)       # searching for list of coordinates
        if posList_E != None:           # case aachen lod2
            min_max_list = prepSTR(posList_E.text)[1]
            # hier sind coordinaten
            se_min, se_max = new_min_max(min_max_list, se_min, se_max)

        else:           # case hamburg lod2 2020
            pos_Es = groundSurface_E.findall('.//gml:pos', namespace)
            polygon = []
            for pos_E in pos_Es:
                polygon.append(pos_E.text)
            polyStr = ' '.join(polygon)
            min_max = prepSTR(polyStr)[1]
            minim, maxim = new_min_max(min_max, minim, maxim)
            min_max_list = minim + maxim
            se_min, se_max = new_min_max(min_max_list, se_min, se_max)

    else:               # case for lod1 files 
        poly_Es = searched_E.findall('.//gml:Polygon', namespace)
        for poly_E in poly_Es:
            polygon = []
            posList_E = searched_E.find('.//gml:posList', namespace)    # searching for list of coordinates
            if posList_E != None:
                polyStr = posList_E.text
            else:
                pos_Es = poly_E.findall('.//gml:pos', namespace)        # searching for individual coordinates in polygon
                for pos_E in pos_Es:
                    polygon.append(pos_E.text)
                polyStr = ' '.join(polygon)
            min_max = prepSTR(polyStr)[1]
            minim, maxim = new_min_max(min_max, minim, maxim)
        min_max_list = minim + maxim
        se_min, se_max = new_min_max(min_max_list, se_min, se_max)
    
    return se_min, se_max




def poly_check(border, borderList, building_list, se_min, se_max, toCheckList, min_max_list, building_E):
    """calls border check and updates min and max if needed"""
    result = border_check(border, borderList, toCheckList)
    if result:
        building_list.append(building_E.attrib['{http://www.opengis.net/gml}id'])
        se_min, se_max = new_min_max(min_max_list, se_min, se_max)
    return result, building_list, se_min, se_max