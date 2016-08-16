import xml.etree.ElementTree as ET
from xml.etree.ElementTree import SubElement, Element
import csv
import codecs

def csv_row_to_mods(csv_row,csv_defs,dest,date):
    """csv_row->List(String) a single row read in from a csv reader
       csv_defs->List(String) the first row from a csv file to give the dict keys
       dest->(String) Path to folder where MODS.xml will be saved
       date->(Stirng) DateCaptured YYYY-MM-DD from scandata

       the following keys are currently in use:
        title
        role
        dateCaptured
        dateQualifier
        dateCreated
        noteOnDateCreated
        description
        identifierLocal
        form
        extent
        note
        language
        topic
        continent
        country
        province
        state
        county
        city
        coordinates
        source

        
        Create a mods file from a csv row (already processed in lists) """

    meta = dict(zip(csv_defs,csv_row))

    xmlns_uris = ['http://www.loc.gov/mods/v3', 'http://www.loc.gov/mods/v3','http://www.w3.org/2001/XMLSchema-instance','http://www.w3.org/1999/xlink']
    
    mods = Element("mods")
    mods.attrib['xmlns'] = xmlns_uris[0]
    mods.attrib['xmlns:mods'] = xmlns_uris[1]
    mods.attrib['xmlns:xsi'] = xmlns_uris[2]
    mods.attrib['xmlns:xlink'] = xmlns_uris[3]

    titleinfo = SubElement(mods,'titleInfo')
    title = SubElement(titleinfo,'title')
    if("title" in meta):
        title.text = meta['title']


    name = SubElement(mods,'name')
    name.attrib['type'] = "personal" # Hardcoded
    namepartname = SubElement(name,'namePart')
    namepartname.text = "Spiller, Harley J."
    namepartdate = SubElement(name,'namePart')
    namepartdate.attrib['type']='date'
    namepartdate.text = "1959-"

    role = SubElement(name,'role')
    rolepart = SubElement(role,'roleTerm')
    if("role" in meta):
        rolepart.text = meta['role']
    rolepart.attrib['authority'] = "marcrelator"
    rolepart.attrib['type'] = "text"

    typeofresource= SubElement(mods,'typeOfResource')
    typeofresource.text = "text"

    genre = SubElement(mods,'genre')
    genre.text = "menu"

    origininfo = SubElement(mods,'originInfo')
    datecaptured = SubElement(origininfo,'dateCaptured')
    datecaptured.text = date
    datecreated = SubElement(origininfo, 'dateCreated')
    if("dateQualifier" in meta):
        datecreated.attrib['qualifier'] = meta['dateQualifier']
    if("dateCreated" in meta):
        datecreated.text = meta['dateCreated']

    datenote = SubElement(mods,'note')
    datenote.attrib['ID'] = "datenote"
    if("dateNote" in meta):
        datenote.text = meta['dateNote']

    description = SubElement(mods,'abstract')
    if("description" in meta):
        description.text = meta['description']

    identifier= SubElement(mods,'identifier')
    identifier.attrib['type'] = "local"
    if("identifierLocal" in meta):
        identifier.text = meta['identifierLocal']


    physicaldesc = SubElement(mods,'physicalDescription')
    form = SubElement(physicaldesc,'form')
    form.attrib['authority'] = "marcform"
    if("form" in meta):
        form.text = meta['form']
    extent = SubElement(physicaldesc,'extent')
    if("extent" in meta):
        extent.text = meta['extent']

    note = SubElement(mods,'note')
    if("note" in meta):
        note.text = meta['note']

    language = SubElement(mods,'language')
    languageterm = SubElement(mods,'languageTerm')
    languageterm.attrib['authority'] = "iso639-2b"
    languageterm.attrib['type'] = "code"
    if("language" in meta):
        language.text = meta['language']

    subject = SubElement(mods,'subject')
    topic = SubElement(subject,'topic')
    topic.attrib['authority'] = "lcsh"
    if("topic" in meta):
        topic.text = meta['topic']
    geographic = SubElement(subject,'geographic') # TODO blank?
    temporal = SubElement(subject,'temporal') # TODO blank?
    hierarchicalgeographic = SubElement(subject,'hierarchicalGeographic')
    continent = SubElement(hierarchicalgeographic,'continent')
    if("continent" in meta):
        continent.text = meta['continent']
    country = SubElement(hierarchicalgeographic,'country')
    if("country" in meta):
        country.text = meta['country']
    province = SubElement(hierarchicalgeographic,'province')
    if("province" in meta):
        province.text = meta['province']
    state = SubElement(hierarchicalgeographic,'state')
    if("state" in meta):
        state.text = meta['state']
    region = SubElement(hierarchicalgeographic,'region') 
    county = SubElement(hierarchicalgeographic,'county') 
    if("county" in meta):
        county.text = meta['county'] 
    city = SubElement(hierarchicalgeographic,'city') 
    if("city" in meta):
        city.text = meta['city'] 
    citysection= SubElement(hierarchicalgeographic,'citySection') 
    cartographics = SubElement(subject,'cartographics')
    coordinates = SubElement(cartographics,'coordinates')
    if("coordinates" in meta):
        coordinates.text = meta['coordinates']


    location = SubElement(mods,'location')
    holdinginstitution = SubElement(location,'physicalLocation')
    holdinginstitution.attrib['type'] = "holdingInstitution"
    holdinginstitution.text = "University of Toronto Scarborough Library, Archives & Special Collections"
    source = SubElement(location,'physicalLocation')
    source.attrib['type'] = "source"
    if("source" in meta):
        source.text = meta['source']
    
    accesscondition = SubElement(mods,'accessCondition') # Rights
    accesscondition.text = "Digital files found on the Digital Scholarship Unit site are meant for research and private study used in compliance with copyright legislation. Access to digital images and text found on this website and the technical capacity to download or copy it does not imply permission to re-use. Prior written permission to publish, or otherwise use images and text found on the website must be obtained from copyright holder. Please contact holding institution for further information."


    tree = ET.ElementTree(mods)
    tree.write(dest,encoding='utf-8',xml_declaration=True)


if __name__ == "__main__":

#    row = ['a','b']
#    defs = ['k1','k2']
#    dest = "."
    dest = "testarchive/MODS.xml"
    reader = csv.reader(codecs.open("006-1-4-5-1test.csv",encoding="utf-8")) # TODO TEXT ENCODING
    read_defs = False
    defs = []
    for row in reader:
        if not read_defs:
            defs = row
            read_defs = True
        else:
            csv_row_to_mods(row,defs,dest)
