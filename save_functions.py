from PySide2 import QtWidgets, QtGui
import os
import time
import pandas as pd
import xml.etree.ElementTree as ET
from io import StringIO

import gui_functions as gf



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



def cityGML_writer(self, search_info, name, exppath):
    """func for writing new CityGML file from list of buildings and files"""
    path = search_info [0]
    results = search_info[5]
    mininimum = [str(a) for a in search_info [4] [0]]
    maximum = [str(a) for a in search_info [4] [1]]
    crs = search_info [3] [0]

    # warning for files with large area sizes
    area = ((float(maximum[0])-float(mininimum[0]))**2 + (float(maximum[1])-float(mininimum[1]))**2) / 2
    numberOfBuildings = sum( [ len(listElem[1]) for listElem in results])

    if area > 1000000 or numberOfBuildings > 2000:
        gf.messageBox(self, "Important", "Writing large file. This might take some time")
        print('the area is roughly:', round(area, 2), 'sqm\nthat is rougly', round(0.0001 * area, 2), 'ha')
        print('num of buildings', numberOfBuildings)

    regSt2ff = [('', 'http://www.opengis.net/citygml/profiles/base/2.0'), ('core', 'http://www.opengis.net/citygml/2.0'), ('gen', 'http://www.opengis.net/citygml/generics/2.0'), ('grp', 'http://www.opengis.net/citygml/cityobjectgroup/2.0'),
                ('app', 'http://www.opengis.net/citygml/appearance/2.0'), ('bldg', 'http://www.opengis.net/citygml/building/2.0'), ('gml', 'http://www.opengis.net/gml'), ('xal', 'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'),
                ('xlink', 'http://www.w3.org/1999/xlink'), ('xsi', 'http://www.w3.org/2001/XMLSchema-instance')]

    nucleus = []

    ns = []

    for filename, buildings in results:
        f = open(os.path.join(path, filename), "r")
        xml_data = f.read()
        my_namespaces = [node for _, node in ET.iterparse(StringIO(xml_data), events=['start-ns'])]
        ns.extend(my_namespaces)
        for prefix, link in my_namespaces:
            ET.register_namespace(prefix, link)
        tree = ET.parse(os.path.join(path, filename))
        root = tree.getroot()
        for children in root.iter():
            if (children.tag.split("}")[1]) == "cityObjectMember":
                for child in children:
                    if (child.tag.split("}")[1]) == "Building":
                        if child.attrib['{http://www.opengis.net/gml}id'] in buildings:
                            atrb2stay = []
                            elemn = [ET.tostring(i, encoding= 'unicode') for i in children]
                            [front, back] = elemn[0].split('>', 1)
                            frunk = front.split()[1:]
                            for bag in frunk:
                                if bag.startswith('xmlns:'):
                                    pAL = bag.split('xmlns:')[1]        # prefixAndLocation
                                    p_a_l = pAL.split('=', 1)           # prefix_and_location
                                    if (p_a_l[0], p_a_l[1][1:-1]) in my_namespaces: # if prefix with same location is already present -> skips
                                        continue
                                atrb2stay.append(bag)
                            nucleus.append('  <core:cityObjectMember>')
                            nucleus.append('    <bldg:Building ' + ' '.join(atrb2stay) + '>')
                            nucleus.append(back[1::].rsplit('>', 1)[0] + '>')
                            nucleus.append('  </core:cityObjectMember>')
    
    ns = list(set(ns))

    prfxs = [i[0] for i in ns]                                          # list of all prefixes
    dup = list(set([x for x in prfxs if prfxs.count(x) > 1]))           # list of all prefix duplicates
    for dplct in dup:
        prob = index_2d(ns, dplct) #getting all namespaces of prefix
        longest = max([i[1] for i in prob], key=len)    # getting longest namespace
        for link in prob:                               # removing all duplicated prefixes
            ns.remove((dplct, link[1]))
        ns.append((dplct, longest))                     # adding prefix with longest namespace

    haupt = []

    header1 = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<core:CityModel xmlns="http://www.opengis.net/citygml/profiles/base/2.0"\nxmlns:core="http://www.opengis.net/citygml/2.0"\nxmlns:gen="http://www.opengis.net/citygml/generics/2.0"\nxmlns:grp="http://www.opengis.net/citygml/cityobjectgroup/2.0"\nxmlns:app="http://www.opengis.net/citygml/appearance/2.0"\nxmlns:bldg="http://www.opengis.net/citygml/building/2.0"\nxmlns:gml="http://www.opengis.net/gml"\nxmlns:xal="urn:oasis:names:tc:ciq:xsdschema:xAL:2.0"\nxmlns:xlink="http://www.w3.org/1999/xlink"\nxmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"'
    haupt.append(header1)

    for prefix, link in ns:
        existing  = [i[0] for i in regSt2ff]
        if prefix in existing:
            continue
        else:
            test = 'xmlns:' + prefix + '="' + link + '"'
            haupt.append(test)

    header2 = 'xsi:schemaLocation="http://www.opengis.net/citygml/2.0 http://schemas.opengis.net/citygml/2.0/cityGMLBase.xsd  http://www.opengis.net/citygml/appearance/2.0 http://schemas.opengis.net/citygml/appearance/2.0/appearance.xsd http://www.opengis.net/citygml/building/2.0 http://schemas.opengis.net/citygml/building/2.0/building.xsd http://www.opengis.net/citygml/generics/2.0 http://schemas.opengis.net/citygml/generics/2.0/generics.xsd">'
    haupt.append(header2)


    envelope = '  <gml:name>' + time.strftime('e3D_export_%Y_%m_%d') + '</gml:name>\n  <gml:boundedBy>\n    <gml:Envelope srsName="' + crs + '">\n      <gml:lowerCorner srsDimension="3">' + ' '.join(mininimum) + '</gml:lowerCorner>\n      <gml:upperCorner srsDimension="3">' + ' '.join(maximum) + '</gml:upperCorner>\n    </gml:Envelope>\n  </gml:boundedBy>'
    haupt.append(envelope)

    haupt.extend(nucleus)

    closingTag = '</core:CityModel>'
    haupt.append(closingTag)

    # unifying intendation
    string = '\n'.join(haupt)
    import xml.dom.minidom
    pretty_print = lambda data: '\n'.join([line for line in xml.dom.minidom.parseString(data).toprettyxml(indent=' '*4).split('\n') if line.strip()])
    prettyxml = pretty_print(string)

    with open(os.path.join(exppath, name + ".gml"), 'w', encoding="utf-8") as f:
        f.write(prettyxml)
        f.close()

    self.list.addItem(os.path.join(exppath, name+".gml"))
    progress(self)



def writer(self, data, name, header, headerXml, form, exppath, additional = False):
    """func to write the export files"""
    # export to .txt
    if self.checkbox_text.isChecked():
        if form == 'search':
            complete = []
            print(data)
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



def index_2d(myList, v):
    """func to get all namespaces of list ([[prefix, namepsace]..[,]]) and returning all namespaces of prefix v"""
    res = []
    for i, x in enumerate(myList):
        if v in x:
            res.append([i, x[1]])
    return res