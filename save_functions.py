# import of libraries
from PySide2 import QtWidgets, QtGui
import os
import time
import pandas as pd
from io import StringIO
import lxml.etree as ET

import CityATB.gui_functions as gf
import CityATB.classes as cl





def folder(self):
    """func to select folder"""
    self.output_foldername = str(QtWidgets.QFileDialog.getExistingDirectory(self, "Select Directory"))
    if self.output_foldername:
        self.textbox_output_folder.setText(self.output_foldername)
        self.btn_open_dir.setEnabled(True)



def reset(self):
    """resets window to default"""
    for checkbox in self.checkboxes_AV + self.checkboxes_DT:
        checkbox.setChecked(False)
    self.textbox_output_folder.setText('')
    self.textbox_output_name.setText('')
    self.output_foldername = ''
    self.progress_bar.setValue(0)
    self.btn_open_dir.setEnabled(False)
    self.list.clear()



def openfolder(self, dirpath):
    """open output directory"""
    if self.textbox_output_folder.text():
        os.startfile(self.textbox_output_folder.text())
    else:
        os.startfile(os.path.join(dirpath + '/output/'))



def save (self, data, validata, search_info, dirpath):
    """func to export data"""
    import header
    # checks if a filetype has been selected
    if ((self.checkbox_analysis.isChecked() and data != []) or (self.checkbox_validation.isChecked() and validata != []) or 
        (self.checkbox_search.isChecked() and search_info != []) or (self.checkbox_cgml.isChecked() and search_info != [])):
        if (self.checkbox_csv.isChecked() or self.checkbox_json.isChecked() or 
            self.checkbox_text.isChecked() or self.checkbox_xml.isChecked() or
            (self.checkbox_cgml.isChecked() and search_info != [])):
            # setting exportfolder
            if self.textbox_output_folder.text() =='':
                exppath = dirpath + '/output/'    
            else:
                exppath = self.output_foldername
            try:
                os.mkdir(exppath)
            except:
                print(exppath, 'is already present\ncontinuing')
            # setting exportname
            if self.textbox_output_name.text() == '':   
                nameAnalysis = time.strftime('CityGML Analysis %Y-%m-%d')
                nameVali = time.strftime('CityGML Validation %Y-%m-%d')
                nameSearch = time.strftime('CityGML Search %Y-%m-%d')
                nameCGML = time.strftime('CityGML NewFile %Y-%m-%d')
            else:
                name = self.textbox_output_name.text()
                if sum([self.checkbox_analysis.isChecked(), self.checkbox_validation.isChecked(), self.checkbox_search.isChecked(), self.checkbox_cgml.isChecked()]) == 1:
                    nameAnalysis = name
                    nameVali = name
                    nameSearch = name
                    nameCGML = name
                else:
                    nameAnalysis = name + ' Analysis'
                    nameVali = name + ' Validation'
                    nameSearch = name + ' Search'
                    nameCGML = name +' CityGML'
            # counting number of files to export for progressbar
            self.runner = 0
            self.completed = 0
            AV = 0
            DT = 0
            if self.checkbox_analysis.isChecked() and data != []:
                AV += 1
            if self.checkbox_validation.isChecked() and validata != []:
                AV += 1
            if self.checkbox_search.isChecked() and search_info != []:
                AV += 1
            for checkbox in self.checkboxes_DT:
                if checkbox.isChecked():
                    DT += 1
            self.EX = AV * DT
            if self.checkbox_cgml.isChecked() and search_info != []:
                self.EX += 1           
            # place to call writer
            if self.checkbox_analysis.isChecked() and data != []:
                writer(self, data, nameAnalysis, header.analysis, header.analysisXml, 'analysis', exppath)
            if self.checkbox_validation.isChecked() and validata != []:
                writer(self, validata, nameVali, header.vali, header.valiXml, 'validation', exppath)
            if self.checkbox_search.isChecked() and search_info != []:
                writer(self, search_info[5], nameSearch, header.search, header.searchXml, 'search', exppath, search_info)
            if self.checkbox_cgml.isChecked() and search_info != []:
                cityGML_writer(self, search_info, nameCGML, exppath)
                pass
            self.btn_open_dir.setEnabled(True)
        else:
            gf.messageBox(self, "Important", "Please select a format!")
    else:
        gf.messageBox(self, "Important", "Please select data to export!")



def writer(self, data, name, header, headerXml, form, exppath, additional = False):
    """func to write the export files"""
    # export to .txt
    if self.checkbox_text.isChecked():
        if form == 'search':
            complete = []
            for file in data:
                if file [1] != []:
                    for building in file [1]:
                        complete.append([file [0], building])
                else:
                    complete.append([file [0], 'N/D'])
            df = pd.DataFrame(complete, columns = header, dtype=str)
        else:
            df = pd.DataFrame(data, columns = header, dtype=str)
        with open(os.path.join(exppath, name+".txt"), 'w', encoding="utf-8") as f:        
            f.write(df.to_string())
        self.list.addItem(os.path.join(exppath, name+".txt"))
        progress(self)
    # export to .csv
    if self.checkbox_csv.isChecked():
        complete = []
        first_line = ['filename']
        for title in headerXml:
            first_line.append(title)
        complete.append(','.join(first_line))
        for file in data:
            if type(file[1]) is list and file[1] != []:
                if len(file) == 2:
                    for clone in file[1]:
                        line = []
                        line.append('%s,%s' %(file[0], clone))
                        complete.append(','.join(line))
                else:
                    print('error transposing')
            elif file[1] == []:
                line = []
                line.append(file[0])
                line.append('N/D')
                complete.append(','.join(line))
            else:
                line = []
                for content in file:
                    line.append(str(content))
                complete.append(','.join(line))
        with open(os.path.join(exppath, name+".csv"), 'w', encoding="utf-8") as f:
            f.write('\n'.join(complete))
        self.list.addItem(os.path.join(exppath, name+".csv"))
        progress(self)
    # export to .json
    if self.checkbox_json.isChecked():
        text3 = []
        text = ['{']                                # main textbody
        text.append('\t"CGML-ATB %s":{' %(form))
        if additional:                              # for search parameters
            text.append('\t\t"searchParameters":{')
            add_inten = []                          # additional_intended textbody
            if additional[3][1]:
                add_inten.append('%s%s%s' %('\t\t\t"crs": "', additional[3][0], '"'))
                i = 0
                for x, y in additional[3][1]:
                    add_inten.append('%s%s%s%s%s%s' %('\t\t\t"coordinate', i, '": "', x, y, '"'))
                    i -=- 1
            if additional[1]:
                add_inten.append('%s%s%s' %('\t\t\t"value": "', additional[1], '"'))
            text.append(',\n'.join(add_inten))
            text.append('\t\t},')
        for i, file in enumerate(data):             # for main info
            text1 = []
            text2 = []
            for j, content in enumerate(data [i]):
                if j == 0:
                    text1.append('\t\t"%s":{' %(content))
                elif type(content) is list:
                    y = 0
                    for value in content:
                        text2.append('\t\t\t"%s%s": "%s"' %(headerXml [j-1], y, value))
                        y -=- 1
                else:
                    text2.append('\t\t\t"%s": "%s"' %(headerXml [j-1], content))
                if j+1 == len(data [i]):
                    text1.append(',\n'.join(text2))
                    text1.append('\t\t}')
                    text3.append('\n'.join(text1))
        text.append(',\n'.join(text3))
        text.append('\t}')
        text.append('}')
        with open(os.path.join(exppath, name+".json"), 'w', encoding="utf-8") as f:
            f.write('\n'.join(text))
        self.list.addItem(os.path.join(exppath, name+".json"))
        progress(self)
    # export to .xml
    if self.checkbox_xml.isChecked():
        text = ['<?xml version="1.0" encoding="UTF-8"?>']
        text.append('%s%s%s' %('<cgml-atb type="', form, '">'))
        if additional:
            text.append('\t<searchParameters>')
            if additional[3][1]:
                text.append('%s%s%s' %('\t\t<boundingCoordinates CRS="', additional[3][0], '">'))
                for x, y in additional[3][1]:
                    text.append('%s%s %s%s' %('\t\t\t<point>', x, y, '</point>'))
                text.append('\t\t</boundingCoordinates>')
            if additional[1]:
                text.append('%s%s%s' %('\t\t<value text="', additional[1], '"/>'))
            text.append('\t</searchParameters>')
        for i, file in enumerate(data):
            for j, content in enumerate(data [i]):
                if j == 0:
                    text.append('\t<file name="%s">' %(content))
                elif type(content) is list:
                    for value in content:
                        text.append('\t\t<%s>%s</%s>' %(headerXml [j-1], value, headerXml [j-1]))
                else:
                    text.append('\t\t<%s>%s</%s>' %(headerXml [j-1], str(content), headerXml [j-1]))                        
            text.append('\t</file>')
        text.append('</cgml-atb>')
        with open(os.path.join(exppath, name+".xml"), 'w', encoding="utf-8") as f:
            f.write('\n'.join(text))
        self.list.addItem(os.path.join(exppath, name+".xml"))
        progress(self)



def progress(self):
    """to update the progress bar"""
    self.runner += 1
    while self.completed < (self.runner / self.EX * 100):
        self.completed += 0.01
        self.progress_bar.setValue(self.completed)



def cityGML_writer(self, search_info, name, exppath):
    """to write new CityGML file with name 'name' and dir 'exppath'"""
    
    # getting info from search_info
    path = search_info [0]
    results = search_info[5]
    minimum = [str(a) for a in search_info [4] [0]]
    maximum = [str(a) for a in search_info [4] [1]]
    crs = search_info [3] [0]
    print('crs from search:', crs)

    # warning for files with large area sizes
    area = ((float(maximum[0])-float(minimum[0]))**2 + (float(maximum[1])-float(minimum[1]))**2) / 2
    numberOfBuildings = sum( [ len(listElem[1]) for listElem in results])

    if area > 1000000 or numberOfBuildings > 2000:
        gf.messageBox(self, "Important", "Writing large file. This might take some time")
        print('the area is roughly:', round(area, 2), 'sqm\nthat is rougly', round(0.0001 * area, 2), 'ha')
        print('num of buildings', numberOfBuildings)

    # version of newly created file
    version = 0

    # buildings for new file
    listOfBuildings = []

    # test for namespaces and ADEs
    namespacing = {}

    for filename, buildings in results:
        # parsing file, getting root and namespace map
        tree = ET.parse(os.path.join(path, filename))
        root = tree.getroot()
        nss = root.nsmap
        namespacing = {**nss, **namespacing}

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
                print(filename, 'compatibility issue with file ')
                continue
        elif version == 2:
            if nss['core'] == cl.CGML2.core:
                print('probably also 2')
            else:
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
            elif ncrs.split(':')[3].split('*')[0] == crs:
                print('same srs split in ', filename)
                pass
            else:
                print('no matching srs\nskipping file ', filename)
                pass

        else:
            print('/nenvelope not found\nskipping file ', filename)
            ### here maybe question to continue or abort
            continue

        ### here checking and then adding building
        cityObjectMembers = root.findall('core:cityObjectMember', namespaces=nss)
        for cityObjectMember_E in cityObjectMembers:
            building_E = cityObjectMember_E.find('bldg:Building', nss)
            if building_E.attrib['{http://www.opengis.net/gml}id'] in buildings:
                listOfBuildings.append(cityObjectMember_E)

    # creating new namespacemap with default namespaces and namespaces from files
    newNSmap = {**nss, **{'core': nsClass.core, 'gen' : nsClass.gen, 'grp' : nsClass.grp, 'app': nsClass.app, 'bldg' : nsClass.bldg, 'gml': nsClass.gml,
                          'xal' : nsClass.xal, 'xlink' : nsClass.xlink, 'xsi' : nsClass.xsi}}



    # creating new root element
    nroot = ET.Element(ET.QName(nsClass.core, 'CityModel'), nsmap= newNSmap)
    
    # creating name element
    name_E = ET.SubElement(nroot, ET.QName(nsClass.gml, 'name'), nsmap={'gml': nsClass.gml})
    name_E.text = name

    # creating gml enevelope
    if crs != '':
        bound_E = ET.SubElement(nroot, ET.QName(nsClass.gml, 'boundedBy'))
        envelope = ET.SubElement(bound_E, ET.QName(nsClass.gml, 'Envelope'), srsName= crs)
        try:
            lcorner = ET.SubElement(envelope, ET.QName(nsClass.gml, 'lowerCorner'), srsDimension= str(len(minimum)))
            lcorner.text = ' '.join(map(str, minimum))
            ucorner = ET.SubElement(envelope, ET.QName(nsClass.gml, 'upperCorner'), srsDimension= str(len(maximum)))
            ucorner.text = ' '.join(map(str, maximum))
        except:
            print('error finding necessary coordinates for bounding box')
    else:
        print('error finding crs')

    listOfBuildings.reverse()

    # appending buildings to new root
    for building in listOfBuildings:
        nroot.insert(nroot.index(name_E)+2, building)
        building.tail = None

    # creating tree from elements
    tree = ET.ElementTree(nroot)
    

    # writing file
    print('writing file')
    tree.write(os.path.join(exppath, name + ".gml"), pretty_print = True, xml_declaration=True, 
                encoding='utf-8', standalone='yes', method="xml")
    
    self.list.addItem(os.path.join(exppath, name + ".gml"))
    progress(self)
    print('created new CityGML file')