from PyQt4 import QtGui, QtCore
import os
import glob



def select_gml(self):
    """func to select file"""
    path = QtGui.QFileDialog.getOpenFileName(self, 'Select XML file')
    if path.endswith('.gml') or path.endswith('.xml'):
        self.textbox_gml.setText(path)
        dirpath = os.path.dirname
        checkCheck(self, dirpath, path)
        self.btn_new_check.setEnabled(True)
        self.btn_one.setEnabled(True)
        self.btn_two.setEnabled(True)
        self.btn_twoplusenergy.setEnabled(True)
        self.btn_oneandtwo.setEnabled(True)
        self.btn_select_folder.setEnabled(False)
        return path, dirpath
    else:
        self.textbox_gml.setText('')  
        self.message_file = QtGui.QMessageBox.information(self, "Important", "Valid File not selected")
        return 0, 0



def select_folder(self):
    """func to select folder"""
    dirpath = QtGui.QFileDialog.getExistingDirectory(self, "Select Directory")
    if dirpath:
        self.btn_new_check.setEnabled(True)
        self.textbox_folder.setText(dirpath)
        self.btn_select_gml.setEnabled(False)
        self.btn_one.setEnabled(True)
        self.btn_two.setEnabled(True)
        self.btn_twoplusenergy.setEnabled(True)
        self.btn_oneandtwo.setEnabled(True)
        checkCheck(self, dirpath)
        return dirpath
    else:
        self.textbox_folder.setText('')
        self.message_folder = QtGui.QMessageBox.information(self, "Important", "Valid Folder not selected")



def select_xsd(self, gmlpath, dirpath):
    """func to select .xsd"""
    self.filename_xsd = QtGui.QFileDialog.getOpenFileName(self, 'Select XSD file')
    if self.filename_xsd.endswith('.xsd'):
        self.textbox_xsd.setText(self.filename_xsd)
        checkCheck(self, dirpath, gmlpath)
        self.btn_new_check.setEnabled(True)
    else:
        self.textbox_xsd.setText('')  
        self.message_file = QtGui.QMessageBox.information(self, "Important", "Valid File not selected")



def progress(self, max):
    """setting up progress bar"""
    while self.completed < max:
        self.completed += 0.0001
        self.progress_bar.setValue(self.completed)



def start_validation(self, xsd, button, buttonText, gmlpath, dirpath, app, validata, xsd_help, validationFilenames):
    """intizializing analysis"""
    if self.running == False:
        self.running = True                                                                         # updating flag
        names = []                                                                                  # for displaying schema names in window title
        for name in xsd:
            names.append(os.path.basename(name))
        self.setWindowTitle('validation against: '+ ', '.join(names))
        self.completed = 0                                                                          # reseting progressbar
        self.progress_bar.setValue(0)
        for nbutton in self.buttons:                                                                # disabeling other buttons
            nbutton.setEnabled(False)
        button.setEnabled(True)                                                                     # refunctioning start button to stop button
        button.setText('Cancel')
        if gmlpath:                                                                                 # for single files
            dirpath = os.path.dirname(gmlpath)
            for i, schema in enumerate(xsd):
                validata, xsd_help, validationFilenames = validate_file(
                    self, gmlpath, schema, validata, xsd_help, validationFilenames)
                self.progress_bar.setValue((i+1)/len(xsd)*100)
            
        elif dirpath:
            fileNames = glob.glob(os.path.join(dirpath, '*.gml')) + glob.glob(os.path.join(dirpath, '*.xml'))
            if len(fileNames) > 0:
                for i, fileName in enumerate(fileNames):
                    app.processEvents()
                    if self.flagStop == False:
                        for schema in xsd:
                            validata, xsd_help, validationFilenames = validate_file(
                                self, fileName, schema, validata, xsd_help, validationFilenames)
                        progress(self, (i + 1) / len(fileNames) * 100)
                        
                    else:
                        self.flagStop = False
                        break
                    
            else:
                self.message_file = QtGui.QMessageBox.information(self, "Important", 'no files have been found in given directory')
                
        else:
            self.message_file = QtGui.QMessageBox.information(self, "Important", 'error, neither a directory or .gml/.xml path were given')
        
        for nbutton in self.buttons:                                        # enabeling all buttons again
            nbutton.setEnabled(True)
            
        if self.progress_bar.value != 0:
            self.btn_save.setEnabled(True)
            self.btn_analyze.setEnabled(True)
        
        checkCheck(self, dirpath, gmlpath)
            
        button.setText(buttonText)
        
        self.setWindowTitle("CityGML ATB - validation")
        self.running = False
        return validata, validationFilenames, xsd_help
            
    # if a button is pressed while an anlysis is running -> stopping validation
    elif self.running == True:
        self.flagStop = True



def validate_file(self, fileName, schemaFile, validata, xsd_help, validationFilenames):         # validata = list of 
    """func to validate single file against schema"""
    from lxml import etree
    xml = etree.parse(fileName)
    # checks if given schema has already been used 
    if schemaFile in xsd_help [0]:
        for i, name in enumerate(xsd_help [0]):
            if name == schemaFile:
                xsd = xsd_help [1] [i]
                xmlschema = xsd_help [2] [i]
                break
    else:
        xsd = etree.parse(schemaFile)
        xmlschema = etree.XMLSchema(xsd)
        xsd_help [0].append(schemaFile)
        xsd_help [1].append(xsd)
        xsd_help [2].append(xmlschema)
    valid = xml.xmlschema(xsd)
    if valid == True:
        status = "Valid!"
        error = 'None'
    else:
        try:
            xmlschema.assert_(xml)
        except etree.XMLSyntaxError as e:
            status = 'PARSING ERROR'
            error = e
        except AssertionError as e:
            status = 'INVALID DOCUMENT'
            error = e
    validata.append([os.path.basename(fileName), os.path.basename(schemaFile), status, error])
    if fileName in validationFilenames:
        pass
    else:
        validationFilenames.append(fileName)
    display(self, validata)
    return validata, xsd_help, validationFilenames



def display(self, validata):
    """to display data"""
    self.table.horizontalHeader().show()
    rowPosition = self.table.rowCount()
    self.table.insertRow(rowPosition)
    for i in range(3):
        if i <= 1:
            print(os.path.basename(validata[rowPosition] [i]))
            newitem = QtGui.QTableWidgetItem(os.path.basename(validata[rowPosition] [i]))
            self.table.setItem(rowPosition, i, newitem)
        else:
            print(validata[rowPosition] [i])
            newitem = QtGui.QTableWidgetItem(validata[rowPosition] [i])
            self.table.setItem(rowPosition, i, newitem)
            if validata[rowPosition] [i] == 'Valid!':
                self.table.item(rowPosition, 2).setBackground(QtGui.QColor(85, 190, 30))
            else: 
                self.table.item(rowPosition, 2).setBackground(QtGui.QColor(230, 30, 30))



def displaysetup(self, validata):
    """setting defaults for table"""
    import header
    self.table.setColumnCount(3)
    self.table.setHorizontalHeaderLabels(header.vali)                                        # arranging headers
    self.table.verticalHeader().hide()
    self.table.horizontalHeader().hide()
    self.table.horizontalHeader().setResizeMode(0, QtGui.QHeaderView.Stretch)               # adjusting resizing of table
    for i in range(1, self.table.columnCount()):
        self.table.horizontalHeader().setResizeMode(i, QtGui.QHeaderView.ResizeToContents)
    if validata != []:                                                                      # displaying already present data
        for i in range(len(validata)):
            display(self, validata)
        self.btn_analyze.setEnabled(True)
        self.btn_save.setEnabled(True)



def checkCheck(self, dirpath, gmlpath = ''):
    """checks if files and schema are given and dis/enbles save-btn accordingly"""
    if (gmlpath.endswith('.gml') or gmlpath.endswith('.xml') or dirpath) and self.filename_xsd.endswith('.xsd'):
        self.btn_validation.setEnabled(True)
    else:
        self.btn_validation.setEnabled(False)



def new_check(self, validata):
    """resets window to defaults"""
    self.textbox_gml.setText('')
    self.textbox_folder.setText('')
    self.textbox_xsd.setText('')
    # clearing table
    while self.table.rowCount() > 0:
        self.table.removeRow(0)
    while self.table.columnCount() > 0:
        self.table.removeColumn(0)
    # reseting variables
    displaysetup(self, validata)
    self.progress_bar.setValue(0)
    # dis/enabeling buttons
    self.btn_validation.setEnabled(False)
    self.btn_one.setEnabled(False)
    self.btn_two.setEnabled(False)
    self.btn_twoplusenergy.setEnabled(False)
    self.btn_oneandtwo.setEnabled(False)
    self.btn_select_gml.setEnabled(True)
    self.btn_select_folder.setEnabled(True)
    self.btn_new_check.setEnabled(False)
    self.btn_save.setEnabled(False)
    self.btn_analyze.setEnabled(False)



def data_transfer(self, gmlpath, dirpath):
    """checks if data to analyze has already been selected"""
    if gmlpath or dirpath:                                                                  # checks for already selected files
        if gmlpath.endswith('.gml') or gmlpath.endswith('.xml'):
            self.textbox_gml.setText(gmlpath)
            self.btn_select_folder.setEnabled(False)
        elif dirpath:
            self.textbox_folder.setText(dirpath)
            self.btn_select_gml.setEnabled(False)
        self.btn_new_check.setEnabled(True)
        self.btn_one.setEnabled(True)
        self.btn_two.setEnabled(True)
        self.btn_twoplusenergy.setEnabled(True)
        self.btn_oneandtwo.setEnabled(True)