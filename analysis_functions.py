import os
import glob
from PySide2 import QtWidgets, QtGui
import zipfile
import shutil
import lxml.etree as ET
import time

import classes as cl
import gui_functions as gf



def select_gml(self):
    """func to selecet single .gml or .xml or .zip file"""
    tup = QtWidgets.QFileDialog.getOpenFileName(self, 'Select file', self.tr("*.gml;*.xml"))            # starts file selection dialog
    path = tup[0]
    if path.endswith('.gml') or path.endswith('.xml') or path.endswith('.zip'):                         # checks if valid file has been selected
        self.textbox_gml.setText(path)                                                                  # displaying path 
        self.btn_reset.setEnabled(True)
        self.btn_run_analysis.setEnabled(True)
        self.btn_select_folder.setEnabled(False)
        dirpath = os.path.dirname(path)
        return path, dirpath
        
    else:
        self.textbox_gml.setText('')                                                                    # resetting textbox for path
        gf.messageBox(self, 'Important','Please select a valid .gml or .xml file')                      # message-box informing about unsuccessful selection
        return '',''



def select_folder(self):
    """func to select directory"""
    path = QtWidgets.QFileDialog.getExistingDirectory(self, 'Select Directory')                         # starts directory selection dialog
    if path:                                                                                            # checks if valid directory has been selected
        self.textbox_gml_folder.setText(path)                                                           # displaying path
        self.btn_reset.setEnabled(True)
        self.btn_run_analysis.setEnabled(True)
        self.btn_select_file.setEnabled(False)
        return path
    else:
        self.textbox_gml_folder.setText('')                                                             # resetting textbox for path
        gf.messageBox(self, 'Important', 'Valid Folder not selected')                                   # message-box informing about unsuccessful selection
    return ''



def tableClean(self):
    """func for cleaning table of all contents"""
    while self.table.rowCount() > 0:                    # deletes rows in table
        self.table.removeRow(0) 
    while self.table.columnCount() > 0:                 # deletes columns in table
        self.table.removeColumn(0)



def run_analysis(self, gmlpath, dirpath, pypath, app):
    """checking which kind of analysis is required; start needed one"""    
    self.completed = 0                                                                          # reseting value of progress bar
    tableClean(self)                                                                            # reseting table to default
    self.flagStop = False                                                                       # flag to stop current analysis
    
    if self.running == False:                                                                   # if analysis function not running
        self.running = True                                                                     # updating flag to running
        self.btn_run_analysis.setText('Cancel')
        # file analysis
        if gmlpath.endswith('.gml') or gmlpath.endswith('.xml'):                                # if single .gml or .xml file has been selected
            fileNames = [gmlpath]                                                               # list of files / for determining results
            data = [analysis(gmlpath)]                                                          # running analysis
            gf.progress(self, 100)                                                              # updating progressbar
        # zip analysis
        elif gmlpath.endswith('.zip'):                                                          # if single .zip file has been selected
            dirpath = os.path.dirname(gmlpath)                                                  # getting direcotry of file
            archive = zipfile.ZipFile(gmlpath, 'r')                                             # reading archive
            zippath = os.path.join(pypath + r'''zipExport''')                                   # path to export temporarily
            archive.extractall(zippath, archive.namelist())                                     # extracting all files
            fileNames = glob.glob(os.path.join(zippath, '*.gml'))                               # searching for .gml files in folder
            fileNames.extend(glob.glob(os.path.join(dirpath, '*.xml')))                         # searching for .xml files in folder
            data = []                                                                           # creating empty array for analysis resutls
            choice = QtWidgets.QMessageBox.question(self, '', "Do you want to extract the zipped files?",
                                                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
            if choice == QtWidgets.QMessageBox.Yes:                                                 # if user wants to keep extracted files
                try:
                    os.mkdir(gmlpath.replace('.zip',''))                                        # creating new directory, in the same directory as the file, with the same name as the file
                except:
                    gf.messageBox(self, 'Warning!', 'Error creating directory')
            for number, fileName in enumerate(fileNames):                                       # looping through all .gml and .xml files
                data.append(analysis(fileName))                                                 # calling analysis function
                if choice == QtWidgets.QMessageBox.Yes:                                             # if user wants to keep extracted files
                    try:                                                                        # try moving files to new directory
                        shutil.move(fileName, os.path.join(gmlpath.replace('.zip',''),
                                                           os.path.basename(fileName)))   
                    except:
                        gf.messageBox(self, 'Failed to move', str(fileName))                    # showing error to console
                gf.progress(self, (number + 1)/len(fileNames)*100)                              # updating progress bar
            shutil.rmtree(zippath)                                                              # deleting temporary directory
        # folder analysis
        elif dirpath:                                                                           # if directory has been selected
            fileNames = glob.glob(os.path.join(dirpath, "*.gml")) + glob.glob(os.path.join(dirpath, "*.xml"))   # searching for .gml/.xml files in directory
            data = []                                                                           # creating empty array for analysis resuls
            for number, fileName in enumerate(fileNames):                                       # loop to start analysis for single files
                app.processEvents()
                if self.flagStop == False:                                                      # checks if task has been canceled
                    data.append(analysis(fileName))                                             # calling analysis function
                    gf.progress(self, (number + 1) / len(fileNames) * 100)                      # updating progress bar
                else:
                    print('exit, because of Flag')
                    break                                                                       # breaking out of loop   
        else:
            gf.messageBox(self, 'Warning', "Couldnot find analysable content")
        # checks if .gml files have been found
        if len(fileNames) > 0:
            if self.flagStop == False:                                  # calling messageBox of successful computation
                title = 'Analysis'
                msg = 'Complete!'
            else:                                                       # signlas if run has been interupted by user
                title = 'Interrupted'
                msg = 'Only partial results!'
            self.btn_save.setEnabled(True)
        else:                                                           # info about no analysable content
            title = 'Important'
            msg = 'No .gml or .xml file present in given directory!'
        self.flagStop = False                                           # resetting flag to normal
        self.running = False
        self.btn_run_analysis.setText('Run Analysis')
        return data, title, msg
    else:                                                               # if button has been pressed to interupt current run
        self.flagStop = True                                            # updating flag
        return [], 'Warning!', 'Instant stop!'



def display(self, data):
    """adding data to table widget"""
    import header
    c = len(data[0])                                                    # getting column count
    r = len(data)                                                       # getting row count
    self.table.setColumnCount(c)
    self.table.setRowCount(r)
    
    for n in range(c):                                                  # loop for columns
        for m in range(r):                                              # loop for rows
            newitem = QtWidgets.QTableWidgetItem(str(data [m] [n]))         # creating widget item
            self.table.setItem(m, n, newitem)                           # adding item to table

    self.table.setHorizontalHeaderLabels(header.analysisTable)          # arranging headers
    self.table.verticalHeader().hide()
    
    # adjusting size of Table
    for i in range(0, self.table.columnCount()):
        self.table.horizontalHeader().setSectionResizeMode(i, QtWidgets.QHeaderView.ResizeToContents)
    self.table.horizontalHeader().setSectionResizeMode(3, QtWidgets.QHeaderView.Stretch)




def analysis (fileName):
    """func to analyse transfered file"""
    # setting defaults and counters
    lods = []
    results = {
        "file_name": os.path.basename(fileName),
        "gml_name": 'N/D',
        "gml_version": 'N/D',
        "crs": 'N/D',
        "gml_lod": 'N/D',
        "ade": 'none',
        "number_of_buildings": 0,
        "number_of_cityobject_members": 0,
        "number_of_buildingParts": 0,
        "size": 'N/D'
    }

    # getting file size
    size = os.path.getsize(fileName)
    suffixes=['B','KB','MB','GB','TB']
    suffixIndex = 0
    while size > 1024:
        suffixIndex += 1
        size = size/1024.0

    results["size"] = '%d %s' %(size, (suffixes[suffixIndex]))
    
    tree = ET.parse(fileName)
    root = tree.getroot()
    nss = root.nsmap

    # getting CityGML version by core element
    try:
        if nss['core'] == cl.CGML1.core:
            results["gml_version"] = 'CityGML 1.0'
        elif nss['core'] == cl.CGML2.core:
            results["gml_version"] = 'CityGML 2.0'
    except Exception as e:
        print(repr(e))
        return list(results.values())

    # checking for ADEs
    if 'energy' in nss:
        if nss['energy'] == cl.CGML2_energy_ADE.energy:
            results["ade"] = 'energyADE'

    name = root.find('gml:name', nss)
    results["gml_name"] = name.text
        
    # getting CRS
    try:
        envelope_E = root.find('./gml:boundedBy/gml:Envelope', nss)
        if envelope_E != None:
            results["crs"]= envelope_E.attrib['srsName']
    except Exception as e:
        print(repr(e))


    # counting cityObjectMembers
    cityObjectMembers = root.findall('core:cityObjectMember', nss)
    results["number_of_cityobject_members"] = len(cityObjectMembers)

    # counting buildings and buildingparts
    buildings_in_file = root.findall('core:cityObjectMember/bldg:Building', nss)
    results["number_of_buildings"] = len(buildings_in_file)

    for building_E in buildings_in_file:
        
        BPs_in_bldg = building_E.findall('./bldg:consistsOfBuildingPart', nss)
        results["number_of_buildingParts"] += len(BPs_in_bldg)

        # searching for LoDs
        for elem in building_E.iter():
            if elem.tag.split("}")[1].startswith('lod'):
                lods.append(elem.tag.split('}')[1][3])
            
    if lods != []:                                                                          # bringing LoDs in ascending order
        lods = list(set(lods))
        lods.sort()
        results["gml_lod"] = ', '.join(lods)

    return list(results.values())                                                 # returning data as list



def new_search(self):
    """resetting data and gui"""
    # resetting gui
    self.textbox_gml.setText('')
    self.textbox_gml_folder.setText('')
    tableClean(self)
    # resetting progress bar
    self.completed = 0
    self.progress_bar.setValue(self.completed)
    # en/disabling buttons
    self.btn_run_analysis.setEnabled(False)
    self.btn_select_file.setEnabled(True)
    self.btn_select_folder.setEnabled(True)
    self.btn_save.setEnabled(False)
    self.btn_reset.setEnabled(False)



def data_transfer(self, data, gmlpath, dirpath, search_info, analyseSearch, validationFilenames, analyseValidation):
    """checks for files (/flags) to analyse from validation or search or displays existing analysis-results"""
    if analyseSearch:                                                           # checks flag for analysis of 'searched'-file
        self.completed = 0                                                      # startvalue for progressbar
        data = []                                                               # creating empty array for analysis resutls
        filenames = [a[0] for a in search_info[5]]
        for number, fileName in enumerate(filenames):                           # looping through all files from the 'search'-window
            data.append(analysis(os.path.join(dirpath, fileName)))              # running analysis for file and adding it to array
            gf.progress(self, (number + 1) / len(filenames) * 100)              # updating progess bar
        analyseSearch = False                                                   # updating flag
        gf.messageBox(self, 'Analysis', 'Complete!')
        
    elif analyseValidation:                                                     # checks flag for analysis of validated files
        self.completed = 0                                                      # startvalue for progressbar
        data = []                                                               # creating empty array for analysis results
        for number, fileName in enumerate(validationFilenames):                 # looping through all validated files
            data.append(analysis(os.path.join(dirpath, fileName)))              # running analysis for file and adding it to array
            gf.progress(self, (number + 1) / len(validationFilenames) * 100)    # updating progress bar
        analyseValidation = False                                               # updating flag
        gf.messageBox(self, 'Analysis', 'Complete!')
        
    elif gmlpath:                                                               # checks for single file path
        self.textbox_gml.setText(gmlpath)                                       # displaying path
        self.btn_select_folder.setEnabled(False)
        self.btn_reset.setEnabled(True)
        self.btn_run_analysis.setEnabled(True)
        
    elif dirpath:                                                               # checks for directory path
        self.textbox_gml_folder.setText(dirpath)                                # displaying path
        self.btn_select_file.setEnabled(False)
        self.btn_reset.setEnabled(True)
        self.btn_run_analysis.setEnabled(True)
        
    if data != []:                                                              # checks for data from prior analyses
        display(self, data)                                                     # displays data
        self.btn_save.setEnabled(True)
        self.btn_reset.setEnabled(True)
        
    return data, analyseSearch, analyseValidation                               # returning analysis results and updated flags