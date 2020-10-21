from PySide2 import QtWidgets, QtGui
import os
import glob
import lxml.etree as ET
from io import StringIO
import time
import math


import header
import classes as cl
import gui_functions as gf
import save_functions as save_f



def select_gml(self):
    """func to select file"""
    tup = QtWidgets.QFileDialog.getOpenFileName(self, 'Select .gml or .xml file', self.tr("*.gml;*.xml"))
    path = tup[0]
    if path.endswith('.gml') or path.endswith('.xml'):
        self.textbox_gml.setText(path)
        dirpath = os.path.dirname(path)
        self.btn_new_check.setEnabled(True)
        self.btn_convert.setEnabled(True)
        self.btn_select_folder.setEnabled(False)
        default_exppath(self, dirpath)
        return path, dirpath
    else:
        self.textbox_gml.setText('')  
        gf.messageBox(self, "Important", "Valid File not selected")
        return 0, 0



def select_folder(self):
    """func to select folder"""
    dirpath = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Directory")
    if dirpath:
        self.btn_new_check.setEnabled(True)
        self.textbox_folder.setText(dirpath)
        self.btn_select_gml.setEnabled(False)
        self.btn_convert.setEnabled(True)
        self.btn_combine.setEnabled(True)
        default_exppath(self, dirpath)
        return dirpath
    else:
        self.textbox_folder.setText('')
        gf.messageBox(self, "Important", "Valid Folder not selected")



def default_exppath(self, dirpath):
    """func to select default exppath"""
    if self.exppath == '':                  # if exppath has not been selected
        self.exppath = os.path.join(dirpath, 'converted or combined')
        self.textbox_exppath.setText(self.exppath)
    else:
        pass



def select_exppath(self):
    """func to select folder"""
    path = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Directory")
    if path:
        self.exppath = path
        self.textbox_exppath.setText(self.exppath)
    else:
        gf.messageBox(self, "Important", "Valid Exportfolder not selected")



def displaysetup(self):
    """function for initial setup of table"""
    self.table.setColumnCount(len(header.conversion))
    self.table.setHorizontalHeaderLabels(header.conversion)
    self.table.verticalHeader().hide()
    self.table.horizontalHeader().hide()
    for i in range(0, self.table.columnCount()):
        self.table.horizontalHeader().setSectionResizeMode(i, QtWidgets.QHeaderView.Stretch)



def display(self, data):
    """function to add data to header"""
    self.table.horizontalHeader().show()
    rowPos = self.table.rowCount()
    self.table.insertRow(rowPos)
    for i in range(len(header.conversion)):
        if i < 1:
            text = os.path.basename(str(data[i]))
        else:
            text = str(data[i])
        newItem = QtWidgets.QTableWidgetItem(text)
        self.table.setItem(rowPos, i, newItem)
        if i == len(data)-1:
            if data[i] == 'Converted' or data[i] == 'Combined':
                color = QtGui.QColor(85, 190, 30)
            else:
                color = QtGui.QColor(235, 30, 30)
            self.table.item(rowPos, i).setBackground(color)





def data_transfer(self, gmlpath, dirpath):
    """checks if data to analyze has already been selected"""
    if gmlpath or dirpath:                                                                  # checks for already selected files
        if gmlpath.endswith('.gml') or gmlpath.endswith('.xml'):
            self.textbox_gml.setText(gmlpath)
            self.btn_select_folder.setEnabled(False)
        elif dirpath:
            self.textbox_folder.setText(dirpath)
            self.btn_select_gml.setEnabled(False)
            self.btn_combine.setEnabled(True)
        self.btn_new_check.setEnabled(True)
        self.btn_convert.setEnabled(True)



def start_conversion(self, gmlpath, dirpath, app):
    """function to convert files from CityGML 1.0 to CityGML 2.0"""
    self.flagStop = False

    if self.running == False:
        self.running = True
        if gmlpath or dirpath:
            self.btn_convert.setText('Cancel')
            self.btn_combine.setEnabled(False)
            self.completed = 0
            #setting default title and message
            title = 'Important'
            msg = 'Conversion complete!'
            if gmlpath:         # for single selected file
                try:
                    convert_file(self, gmlpath)
                    gf.progress(self, 100)
                    result = [gmlpath, 'Converted']
                except:
                    result = [gmlpath, 'Error']
                display(self, result)
                gf.progress(self, 100)
            elif dirpath:       # for selected folder
                fileNames = glob.glob(os.path.join(dirpath, "*.gml")) + glob.glob(os.path.join(dirpath, "*.xml"))
                if fileNames != 0:
                    for number, fileName in enumerate(fileNames):
                        app.processEvents()
                        if self.flagStop == False:
                            try:
                                convert_file(self, fileName)
                                result = [fileName, 'Converted']
                            except:
                                result = [fileName, 'Error']
                            display(self, result)
                            gf.progress(self, (number + 1) / len(fileNames) * 100)
                        else:
                            # break because of flagStop
                            break
                else:
                    title = 'Error'
                    msg = 'Please select a folder containing GML files'
            # resetting buttons to defaults
            self.btn_convert.setText('Start conversion')
            self.btn_combine.setEnabled(True)
            self.running = False
            self.flagStop = False
            return title, msg
        else:
            return 'Attention!', 'Please select file or folder first.'
    else:
        print('run has been interrupted')
        self.flagStop = True



def convert_file(self, filename):
    """function to convert file to CityGML 2.0 and save to exppath"""
    content = open(filename, 'r').read()
    old = ['http://www.opengis.net/citygml/1.0', 'http://www.opengis.net/citygml/generics/1.0', 'http://www.opengis.net/citygml/cityobjectgroup/1.0', 'http://www.opengis.net/citygml/appearance/1.0', 'http://www.opengis.net/citygml/building/1.0']
    new = ['http://www.opengis.net/citygml/2.0', 'http://www.opengis.net/citygml/generics/2.0', 'http://www.opengis.net/citygml/cityobjectgroup/2.0', 'http://www.opengis.net/citygml/appearance/2.0', 'http://www.opengis.net/citygml/building/2.0']

    # replacing old URIs with new ones
    for i in range(0, len(new)):
        content = content.replace(old[i], new[i])

    # writing new file
    with open(os.path.join(self.exppath, os.path.basename(filename)), 'w', encoding='utf-8') as f:
        f.write(content)
        f.close()



def combine_files(self, dirpath, app):
    """func for writing new CityGML file from list of buildings and files"""
    self.flagStop = False

    if self.running == False:
        self.running = True

        filenames = glob.glob(os.path.join(dirpath, "*.gml")) + glob.glob(os.path.join(dirpath, "*.xml"))
        if len(filenames) > 1:
            self.btn_combine.setText('Cancel')
            self.btn_convert.setEnabled(False)

            self.completed = 0

            # name of created file
            name ='e3D_combined'
            # buildings for new file
            listOfBuildings = []
            # crs and minimum and maximum coordinates of created file
            crs = ''
            minimum = [math.inf, math.inf, math.inf]
            maximum = [-math.inf, -math.inf, -math.inf]
            # version of newly created file
            version = 0

            for i, filename in enumerate(filenames):
                app.processEvents()
                if self.flagStop == False:
                    # parsing file, getting root and namespace map
                    tree = ET.parse(filename)
                    root = tree.getroot()
                    nss = root.nsmap
                    # checking for version and intercompatibilty between input files
                    print('checking CGML version')
                    if version == 0:
                        if nss['core'] == cl.CGML1.core:
                            print(filename, 'probably 1')
                            nsClass = cl.CGML1
                            version = 1
                        elif nss['core'] == cl.CGML2.core:
                            print(filename, 'probably 2')
                            nsClass = cl.CGML2
                            version = 2
                        else:
                            display(self, [filename, 'core declaration not found'])
                            print('unable to find matching core declaration')
                            print('skipping file ', filename)
                            continue
                    elif version == 1:
                        if nss['core'] == cl.CGML1.core:
                            print(filename, 'probably also 1')
                        elif nss['core'] == cl.CGML2.core:
                            print(filename, 'probably 2\nchanging to version 2')
                            
                            nsClass = cl.CGML2
                            version = 2
                        else:
                            display(self, [filename, 'compatibility issue with file'])
                            print(filename, 'compatibility issue with file ')
                            continue
                    elif version == 2:
                        if nss['core'] == cl.CGML2.core:
                            print('probably also 2')
                        else:
                            display(self, [filename, 'compatibility issue with file'])
                            print('compatibility issue with file ', filename)
                            continue

                    # finding gml envelope with srs declaration and bounding coordinates
                    envelope_E = root.find('.//gml:Envelope', namespaces= nss)
                    if envelope_E != None:
                        # new srs
                        ncrs = envelope_E.attrib['srsName']
                        if crs == '':
                            crs = ncrs
                            print('set new srs to', crs, '\nfrom', filename)
                        elif ncrs == crs:
                            print('same srs in', filename)
                            pass
                        else:
                            display(self, [filename, 'SRS not matching'])
                            print('no matching srs in', filename)
                            ### here maybe question to continue or abort
                            pass
                        # getting bounding coordinates
                        try:
                            lowerCorner = envelope_E.find('./gml:lowerCorner', nss).text.split(' ')
                            for i, coor in enumerate(lowerCorner):
                                if float(coor) < minimum[i]:
                                    minimum[i] = float(coor)
                            upperCorner = envelope_E.find('./gml:upperCorner', nss).text.split(' ')
                            for i, coor in enumerate(upperCorner):
                                if float(coor) > maximum[i]:
                                    maximum[i] = float(coor)
                        except:
                            display(self, [filename, 'error finding lower or upper corner'])
                            print('error within gml:envelope in file: ', filename)

                    else:
                        display(self, [filename, 'Envelope not found'])
                        print('envelope not found\nskipping file ', filename)
                        ### here maybe question to continue or abort
                        continue
                    # extending list of cityObjectMembers, which wil be transfered to new file
                    listOfBuildings.extend(root.findall('.//core:cityObjectMember', namespaces=nss))
                    gf.progress(self, (i) / len(filenames) * 100)
                
                else:
                    display(self, [filename, 'Run interrupted'])
                    print('Run interrupted at file', filename)
                print('\n\n')

            # creating new root element
            nroot = ET.Element(ET.QName(nsClass.core, 'CityModel'), nsmap= {'core': nsClass.core, 'gen' : nsClass.gen, 'grp' : nsClass.grp,
                                                                            'app': nsClass.app, 'bldg' : nsClass.bldg, 'gml': nsClass.gml, 'xal' : nsClass.xal,
                                                                            'xlink' : nsClass.xlink, 'xsi' : nsClass.xsi})
            
            # creating name element
            name_E = ET.SubElement(nroot, ET.QName(nsClass.gml, 'name'), nsmap={'gml': nsClass.gml})
            name_E.text = 'created by the CGML-ATB of the e3D'

            # creating gml enevelope
            if crs != '':
                bound = ET.SubElement(nroot, ET.QName(nsClass.gml, 'boundedBy'))
                envelope = ET.SubElement(bound, ET.QName(nsClass.gml, 'Envelope'), srsName= crs)
                if all([x != math.inf for x in minimum]) and all([x != -math.inf for x in maximum]):
                    lcorner = ET.SubElement(envelope, ET.QName(nsClass.gml, 'lowerCorner'), srsDimension= str(len(minimum)))
                    lcorner.text = ' '.join(map(str, minimum))
                    ucorner = ET.SubElement(envelope, ET.QName(nsClass.gml, 'upperCorner'), srsDimension= str(len(maximum)))
                    ucorner.text = ' '.join(map(str, maximum))
                else:
                    display(self, [os.path.join(self.exppath, name + ".gml"), 'error in creation of new envelope'])
                    print('error finding necessary coordinates for bounding box')
            else:
                return 'error', 'no SRS found'

            # appending buildings to new root
            for building in listOfBuildings:
                nroot.insert(nroot.index(name_E)+2, building)
                building.tail = None

            # creating tree from elements
            tree = ET.ElementTree(nroot)
            
            # trying to create export directory
            try:
                os.mkdir(self.exppath)
            except:
                print(self.exppath, 'is already present\ncontinuing')

            # writing file
            print('writing file')
            tree.write(os.path.join(self.exppath, name + ".gml"), pretty_print = True, xml_declaration=True, 
                        encoding='utf-8', standalone='yes', method="xml")
            gf.progress(self, 100)
            display(self, [os.path.join(self.exppath, name + ".gml"), 'Combined'])

            self.btn_combine.setText("Start combining")
            self.btn_convert.setEnabled(True)
            self.running = False
            self.flagStop = False
            return 'Important', 'Combining complete'
        else:
            return 'Error', 'Please select folder with 2 or more files'
    else:
        print('trying to interrupt run')
        self.flagStop = True